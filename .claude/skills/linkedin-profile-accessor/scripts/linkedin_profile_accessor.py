"""
LinkedIn Profile Accessor - Core Module

Extracts LinkedIn profile data using Chrome DevTools Protocol.

This module provides the main LinkedInProfileAccessor class for extracting
profile data, posts, and network information from LinkedIn.
"""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

from .profile_data_models import (
    ProfileData,
    ExperienceItem,
    EducationItem,
    SkillItem,
    PostItem,
    ConnectionItem,
    RecommendationItem
)
from .linkedin_selectors import (
    PROFILE_SELECTORS,
    SECTION_SELECTORS,
    EXPERIENCE_SELECTORS,
    EDUCATION_SELECTORS,
    SKILLS_SELECTORS,
    POST_SELECTORS,
    CONNECTION_SELECTORS,
    LOGIN_INDICATORS
)
from .linkedin_helpers import (
    extract_text_with_fallbacks,
    extract_list_with_fallbacks,
    extract_attribute_with_fallbacks,
    human_delay,
    wait_for_load_state,
    clean_text,
    count_words,
    parse_connections_count,
    is_logged_in,
    take_screenshot,
    build_profile_url,
    extract_date_range,
    validate_profile_id,
    extract_numbers
)


class LinkedInProfileAccessor:
    """
    Extracts LinkedIn profile data using Chrome CDP.

    Usage:
        accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")
        profile_data = await accessor.extract_profile_data("profile-id")
    """

    def __init__(
        self,
        vault_path: str | Path = "AI_Employee_Vault",
        cdp_endpoint: str = "http://127.0.0.1:9222",
        timeout: int = 30000,
        headless: bool = False
    ):
        """
        Initialize the accessor.

        Args:
            vault_path: Path to the Obsidian vault
            cdp_endpoint: Chrome DevTools Protocol endpoint
            timeout: Page load timeout in milliseconds
            headless: Whether to run headless (not recommended for LinkedIn)
        """
        self.vault_path = Path(vault_path)
        self.cdp_endpoint = cdp_endpoint
        self.timeout = timeout
        self.headless = headless
        self.browser: Optional[Browser] = None

        # Log access
        self._log_audit_action("accessor_init", {
            "cdp_endpoint": cdp_endpoint,
            "timeout": timeout
        })

    async def connect_to_chrome(self) -> Browser:
        """
        Connect to Chrome via CDP.

        Returns:
            Playwright Browser instance

        Raises:
            ConnectionError: If Chrome is not running on port 9222
        """
        if self.browser:
            return self.browser

        playwright = await async_playwright().start()

        try:
            # Connect to existing Chrome session via CDP
            self.browser = await playwright.chromium.connect_over_cdp(self.cdp_endpoint)

            self._log_audit_action("chrome_connected", {"endpoint": self.cdp_endpoint})
            return self.browser

        except Exception as e:
            self._log_audit_action("chrome_connection_failed", {"error": str(e)}, result="error")
            raise ConnectionError(
                f"Could not connect to Chrome on {self.cdp_endpoint}. "
                f"Make sure Chrome is running with CDP enabled. "
                f"Use: scripts/social-media/START_AUTOMATION_CHROME.bat"
            ) from e

    async def _get_page(self) -> Page:
        """Get or create a page."""
        browser = await self.connect_to_chrome()

        # Get existing context and page or create new
        contexts = browser.contexts
        if contexts:
            context = contexts[0]
        else:
            context = await browser.new_context()

        pages = context.pages
        if pages:
            page = pages[0]
        else:
            page = await context.new_page()

        # Set default timeout
        page.set_default_timeout(self.timeout)

        return page

    async def navigate_to_profile(self, profile_id: str, page: Optional[Page] = None) -> Page:
        """
        Navigate to a LinkedIn profile.

        Args:
            profile_id: LinkedIn profile ID (e.g., "hamdan-mohammad-922486374")
            page: Playwright Page instance (optional, will create if not provided)

        Returns:
            Playwright Page instance on the profile page

        Raises:
            ValueError: If profile_id is invalid
            TimeoutError: If page fails to load
        """
        if not validate_profile_id(profile_id):
            raise ValueError(f"Invalid profile ID: {profile_id}")

        if page is None:
            page = await self._get_page()

        # Build profile URL
        profile_url = build_profile_url(profile_id)

        self._log_audit_action("navigate_to_profile", {"profile_id": profile_id, "url": profile_url})

        try:
            # Navigate to profile
            await page.goto(profile_url, wait_until="domcontentloaded", timeout=self.timeout)

            # Wait for page to load
            await wait_for_load_state(page, "domcontentloaded")

            # Check if logged in
            if not is_logged_in(page):
                self._log_audit_action("not_logged_in", {"profile_id": profile_id}, result="error")
                raise PermissionError(
                    "Not logged into LinkedIn. Please log in via the Chrome automation window."
                )

            # Small delay to ensure dynamic content loads
            await asyncio.sleep(2)

            return page

        except PlaywrightTimeoutError as e:
            self._log_audit_action("navigation_timeout", {"profile_id": profile_id}, result="error")
            raise TimeoutError(f"Timeout loading profile: {profile_id}") from e

    async def extract_profile_data(
        self,
        profile_id: str,
        include_posts: bool = True,
        post_limit: int = 10,
        include_network: bool = False,
        network_limit: int = 50,
        capture_screenshot: bool = False
    ) -> ProfileData:
        """
        Extract all available profile data.

        Args:
            profile_id: LinkedIn profile ID
            include_posts: Whether to extract recent posts
            post_limit: Maximum number of posts to extract
            include_network: Whether to extract network data (slower)
            network_limit: Maximum number of network connections to extract
            capture_screenshot: Whether to capture a screenshot

        Returns:
            ProfileData object with all extracted information
        """
        page = await self.navigate_to_profile(profile_id)

        # Extract basic profile info
        name = await self._extract_name(page)
        headline = await self._extract_headline(page)
        location = await self._extract_location(page)
        connections_count = await self._extract_connections_count(page)
        profile_url = build_profile_url(profile_id)

        # Check for profile photo
        photo_url = await self._extract_profile_photo_url(page)
        has_photo = bool(photo_url)

        # Extract about section
        about = await self._extract_about(page)
        about_word_count = count_words(about) if about else 0

        # Extract experience
        experience = await self._extract_experience(page)

        # Extract education
        education = await self._extract_education(page)

        # Extract skills
        skills = await self._extract_skills(page)

        # Extract recommendations
        recommendations = await self._extract_recommendations(page)

        # Extract posts if requested
        posts = []
        if include_posts:
            posts = await self._extract_posts(page, limit=post_limit)

        # Extract network if requested
        network = None
        if include_network:
            network = await self._extract_network(page, limit=network_limit)

        # Capture screenshot if requested
        screenshot_path = None
        if capture_screenshot:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = await take_screenshot(
                page,
                f"profile_{profile_id}_{timestamp}.png"
            )

        # Create ProfileData object
        profile_data = ProfileData(
            profile_id=profile_id,
            name=name or "Unknown",
            headline=headline or "",
            location=location,
            about=about,
            about_word_count=about_word_count,
            experience=experience,
            education=education,
            skills=skills,
            posts=posts,
            recommendations=recommendations,
            connections_count=connections_count,
            profile_url=profile_url,
            profile_photo_url=photo_url,
            has_photo=has_photo,
            extracted_at=datetime.now(),
            screenshot_path=screenshot_path
        )

        self._log_audit_action("profile_extracted", {
            "profile_id": profile_id,
            "name": name,
            "experience_count": len(experience),
            "skills_count": len(skills)
        })

        return profile_data

    async def _extract_name(self, page: Page) -> Optional[str]:
        """Extract profile name."""
        return await extract_text_with_fallbacks(page, PROFILE_SELECTORS['name'])

    async def _extract_headline(self, page: Page) -> Optional[str]:
        """Extract professional headline."""
        return await extract_text_with_fallbacks(page, PROFILE_SELECTORS['headline'])

    async def _extract_location(self, page: Page) -> Optional[str]:
        """Extract location."""
        return await extract_text_with_fallbacks(page, PROFILE_SELECTORS['location'])

    async def _extract_connections_count(self, page: Page) -> Optional[int]:
        """Extract connection count."""
        text = await extract_text_with_fallbacks(page, PROFILE_SELECTORS['connections'])
        if text:
            return parse_connections_count(text)
        return None

    async def _extract_profile_photo_url(self, page: Page) -> Optional[str]:
        """Extract profile photo URL."""
        return await extract_attribute_with_fallbacks(
            page,
            PROFILE_SELECTORS['profile_photo'],
            'src'
        )

    async def _extract_about(self, page: Page) -> Optional[str]:
        """Extract about section."""
        # Try to find and click "About" section to expand it
        try:
            about_button = await page.query_selector('button[aria-label="Expand about section"]')
            if about_button:
                await about_button.click()
                await asyncio.sleep(0.5)
        except Exception:
            pass

        return await extract_text_with_fallbacks(page, PROFILE_SELECTORS['about'])

    async def _extract_experience(self, page: Page) -> List[ExperienceItem]:
        """Extract work experience."""
        experiences = []

        try:
            # Scroll to experience section
            await page.evaluate('window.scrollTo(0, 4000)')
            await asyncio.sleep(1)

            # Find all experience containers
            containers = await page.query_selector_all(EXPERIENCE_SELECTORS['container'][0])

            for container in containers[:10]:  # Limit to 10 experiences
                try:
                    # Extract title
                    title_elem = await container.query_selector(EXPERIENCE_SELECTORS['title'][0])
                    title = await title_elem.inner_text() if title_elem else ""

                    # Extract company
                    company_elem = await container.query_selector(EXPERIENCE_SELECTORS['company'][0])
                    company = await company_elem.inner_text() if company_elem else ""

                    # Extract date range
                    date_elem = await container.query_selector(EXPERIENCE_SELECTORS['date_range'][0])
                    date_text = await date_elem.inner_text() if date_elem else ""
                    start_date, end_date = extract_date_range(date_text)

                    # Extract description
                    desc_elem = await container.query_selector(EXPERIENCE_SELECTORS['description'][0])
                    description = await desc_elem.inner_text() if desc_elem else None

                    if title or company:
                        experiences.append(ExperienceItem(
                            title=clean_text(title),
                            company=clean_text(company),
                            start_date=start_date or "",
                            end_date=end_date,
                            description=clean_text(description) if description else None
                        ))
                except Exception:
                    continue

        except Exception:
            pass

        return experiences

    async def _extract_education(self, page: Page) -> List[EducationItem]:
        """Extract education."""
        education_list = []

        try:
            # Find all education containers
            containers = await page.query_selector_all(EDUCATION_SELECTORS['container'][0])

            for container in containers[:5]:  # Limit to 5 entries
                try:
                    # Extract school
                    school_elem = await container.query_selector(EDUCATION_SELECTORS['school'][0])
                    school = await school_elem.inner_text() if school_elem else ""

                    # Extract degree
                    degree_elem = await container.query_selector(EDUCATION_SELECTORS['degree'][0])
                    degree = await degree_elem.inner_text() if degree_elem else ""

                    # Extract years
                    years_elem = await container.query_selector(EDUCATION_SELECTORS['years'][0])
                    years_text = await years_elem.inner_text() if years_elem else ""
                    years = extract_numbers(years_text)
                    grad_year = years[-1] if years else None

                    if school or degree:
                        education_list.append(EducationItem(
                            school=clean_text(school),
                            degree=clean_text(degree),
                            graduation_year=grad_year
                        ))
                except Exception:
                    continue

        except Exception:
            pass

        return education_list

    async def _extract_skills(self, page: Page) -> List[SkillItem]:
        """Extract skills."""
        skills = []

        try:
            # Find all skill containers
            containers = await page.query_selector_all(SKILLS_SELECTORS['container'][0])

            for container in containers[:50]:  # Limit to 50 skills
                try:
                    # Extract skill name
                    name_elem = await container.query_selector(SKILLS_SELECTORS['name'][0])
                    name = await name_elem.inner_text() if name_elem else ""

                    # Extract endorsement count
                    endorsements_elem = await container.query_selector(SKILLS_SELECTORS['endorsements'][0])
                    endorsements_text = await endorsements_elem.inner_text() if endorsements_elem else ""
                    endorsements = extract_numbers(endorsements_text)
                    endorsement_count = endorsements[0] if endorsements else 0

                    if name:
                        skills.append(SkillItem(
                            name=clean_text(name),
                            endorsements=endorsement_count
                        ))
                except Exception:
                    continue

        except Exception:
            pass

        return skills

    async def _extract_recommendations(self, page: Page) -> List[RecommendationItem]:
        """Extract recommendations."""
        recommendations = []

        try:
            # Navigate to recommendations section if exists
            rec_section = await page.query_selector(SECTION_SELECTORS['recommendations'][0])
            if not rec_section:
                return recommendations

            # Scroll to recommendations
            await rec_section.scroll_into_view_if_needed()
            await asyncio.sleep(1)

            # Extract recommendation items
            rec_items = await rec_section.query_selector_all('.pv-recommendation-entity')

            for item in rec_items[:5]:
                try:
                    # Author info
                    author_elem = await item.query_selector('.pv-recommendation-entity__author-profile-name')
                    author_name = await author_elem.inner_text() if author_elem else ""

                    # Recommendation text
                    text_elem = await item.query_selector('.pv-recommendation-entity__recommendation-text')
                    text = await text_elem.inner_text() if text_elem else ""

                    if author_name or text:
                        recommendations.append(RecommendationItem(
                            author_name=clean_text(author_name),
                            author_title="",
                            author_company="",
                            text=clean_text(text),
                            date=""
                        ))
                except Exception:
                    continue

        except Exception:
            pass

        return recommendations

    async def _extract_posts(self, page: Page, limit: int = 10) -> List[PostItem]:
        """Extract recent posts."""
        posts = []

        try:
            # Scroll to activity section
            await page.evaluate('window.scrollTo(0, 6000)')
            await asyncio.sleep(1)

            # Find post containers
            post_containers = await page.query_selector_all(POST_SELECTORS['container'][0])

            for container in post_containers[:limit]:
                try:
                    # Extract post text
                    text_elem = await container.query_selector(POST_SELECTORS['text'][0])
                    text = await text_elem.inner_text() if text_elem else ""

                    # Extract reactions count
                    reactions_elem = await container.query_selector(POST_SELECTORS['reactions'][0])
                    reactions_text = await reactions_elem.inner_text() if reactions_elem else ""
                    reactions = extract_numbers(reactions_text)
                    reaction_count = reactions[0] if reactions else 0

                    # Extract comments count
                    comments_elem = await container.query_selector(POST_SELECTORS['comments'][0])
                    comments_text = await comments_elem.inner_text() if comments_elem else ""
                    comments = extract_numbers(comments_text)
                    comment_count = comments[0] if comments else 0

                    # Extract date
                    date_elem = await container.query_selector(POST_SELECTORS['date'][0])
                    date = await date_elem.inner_text() if date_elem else ""

                    if text:
                        posts.append(PostItem(
                            text=clean_text(text),
                            date=clean_text(date),
                            reactions=reaction_count,
                            comments=comment_count
                        ))
                except Exception:
                    continue

        except Exception:
            pass

        return posts

    async def _extract_network(self, page: Page, limit: int = 50) -> Dict[str, Any]:
        """
        Extract network information (connections, people you may know).

        Args:
            page: Playwright Page object
            limit: Maximum number of connections to extract

        Returns:
            Dictionary with network statistics and sample connections
        """
        network_info = {
            "total_connections": 0,
            "connections_sample": [],
            "people_you_may_know_count": 0
        }

        try:
            # Navigate to network page
            network_url = f"{build_profile_url(self.current_profile_id)}/network/"
            await page.goto(network_url)
            await wait_for_load_state(page, "networkidle")
            await human_delay()

            # Extract total connections count
            try:
                connections_elem = await page.query_selector('.t-14')
                if connections_elem:
                    connections_text = await connections_elem.inner_text()
                    # Extract numbers from text like "500+ connections"
                    numbers = extract_numbers(connections_text)
                    if numbers:
                        network_info["total_connections"] = numbers[0]
            except Exception:
                pass

            # Scroll to load more connections
            await page.evaluate('window.scrollTo(0, 1000)')
            await asyncio.sleep(1)

            # Extract connection cards
            connection_cards = await page.query_selector_all('.mn-discovererperson-card')

            for card in connection_cards[:limit]:
                try:
                    # Extract profile link
                    link_elem = await card.query_selector('a')
                    profile_link = await link_elem.get_attribute('href') if link_elem else ""

                    # Extract name
                    name_elem = await card.query_selector('.t-14, .t-16')
                    name = await name_elem.inner_text() if name_elem else ""

                    # Extract headline/title
                    headline_elem = await card.query_selector('.t-12')
                    headline = await headline_elem.inner_text() if headline_elem else ""

                    # Extract connection degree (1st, 2nd, 3rd+)
                    degree_elem = await card.query_selector('.t-black--light')
                    degree = await degree_elem.inner_text() if degree_elem else ""

                    if name:
                        network_info["connections_sample"].append({
                            "name": clean_text(name),
                            "headline": clean_text(headline),
                            "degree": clean_text(degree),
                            "profile_link": profile_link
                        })
                except Exception:
                    continue

            # Try to get "People You May Know" count
            try:
                pymk_section = await page.query_selector('text:("People You May Know")')
                if pymk_section:
                    parent = pymk_section.closest('section')
                    if parent:
                        count_text = await parent.inner_text()
                        numbers = extract_numbers(count_text)
                        if numbers:
                            network_info["people_you_may_know_count"] = numbers[0]
            except Exception:
                pass

        except Exception as e:
            self.logger.warning(f"Error extracting network info: {e}")

        return network_info

    def save_profile_report(
        self,
        profile_data: ProfileData,
        output_path: str | Path,
        format: str = "markdown"
    ) -> Path:
        """
        Save profile data to a report file.

        Args:
            profile_data: ProfileData instance
            output_path: Output file path
            format: Output format ("markdown", "json", or "csv")

        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            self._save_json_report(profile_data, output_path)
        elif format == "csv":
            self._save_csv_report(profile_data, output_path)
        else:  # markdown
            self._save_markdown_report(profile_data, output_path)

        self._log_audit_action("report_saved", {
            "path": str(output_path),
            "format": format
        })

        return output_path

    def _save_json_report(self, profile_data: ProfileData, output_path: Path) -> None:
        """Save as JSON."""
        import json
        from dataclasses import asdict

        # Convert to dict
        data = asdict(profile_data)

        # Handle datetime
        data['extracted_at'] = profile_data.extracted_at.isoformat()

        # Write file
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _save_csv_report(self, profile_data: ProfileData, output_path: Path) -> None:
        """Save as CSV."""
        import csv

        with output_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Basic info
            writer.writerow(["Field", "Value"])
            writer.writerow(["Name", profile_data.name])
            writer.writerow(["Headline", profile_data.headline])
            writer.writerow(["Location", profile_data.location])
            writer.writerow(["About", profile_data.about])
            writer.writerow(["Connections", profile_data.connections_count])

            # Experience
            writer.writerow([])
            writer.writerow(["Experience"])
            for exp in profile_data.experience:
                writer.writerow([f"{exp.title} at {exp.company}", f"{exp.start_date} - {exp.end_date or 'Present'}"])

            # Skills
            writer.writerow([])
            writer.writerow(["Skills", "Endorsements"])
            for skill in profile_data.skills:
                writer.writerow([skill.name, skill.endorsements])

    def _save_markdown_report(self, profile_data: ProfileData, output_path: Path) -> None:
        """Save as Markdown."""
        content = f"""# LinkedIn Profile: {profile_data.name}

## Profile Overview

| Field | Value |
|-------|-------|
| **Name** | {profile_data.name} |
| **Headline** | {profile_data.headline} |
| **Location** | {profile_data.location or 'Not specified'} |
| **Connections** | {profile_data.connections_count or 'Unknown'} |
| **Profile URL** | {profile_data.profile_url} |

## About

{profile_data.about or '*No about section*'}

## Experience

{chr(10).join([f"### {exp.title} at {exp.company}\n*{exp.start_date} - {exp.end_date or 'Present'}*\n\n{exp.description or ''}\n" for exp in profile_data.experience])}

## Education

{chr(10).join([f"### {edu.degree} from {edu.school}\n" for edu in profile_data.education])}

## Skills

{chr(10).join([f"- {skill.name} ({skill.endorsements} endorsements)" for skill in profile_data.skills[:20]])}

## Recent Posts

{chr(10).join([f"- **{post.date}**: {post.text[:100]}... ({post.reactions} reactions, {post.comments} comments)" for post in profile_data.posts[:5]])}

---
*Extracted: {profile_data.extracted_at.strftime('%Y-%m-%d %H:%M:%S')}*
"""
        output_path.write_text(content, encoding="utf-8")

    def _log_audit_action(
        self,
        action_type: str,
        parameters: dict,
        result: str = "success"
    ) -> None:
        """Log action to audit log."""
        try:
            from utils.audit_logging import AuditLogger

            audit_logger = AuditLogger(self.vault_path)
            audit_logger.log_action(
                action_type=action_type,
                target="linkedin_profile_accessor",
                parameters=parameters,
                result=result
            )
        except Exception:
            # Don't fail if audit logging fails
            pass

    def close(self) -> None:
        """Close browser connection synchronously."""
        if self.browser:
            # Try to get running event loop
            try:
                loop = asyncio.get_running_loop()
                # If there's a running loop, we can't close asynchronously
                # Schedule the close as a task but don't wait
                loop.create_task(self.browser.close())
            except RuntimeError:
                # No running loop, run in new loop
                asyncio.run(self.browser.close())
            self.browser = None

    async def aclose(self) -> None:
        """Close browser connection asynchronously."""
        if self.browser:
            await self.browser.close()
            self.browser = None


# Synchronous wrapper for easier use
def extract_profile_data_sync(
    profile_id: str,
    vault_path: str | Path = "AI_Employee_Vault",
    **kwargs
) -> ProfileData:
    """
    Synchronous wrapper for extract_profile_data.

    Args:
        profile_id: LinkedIn profile ID
        vault_path: Path to vault
        **kwargs: Additional arguments for extract_profile_data

    Returns:
        ProfileData object
    """
    async def _extract():
        accessor = LinkedInProfileAccessor(vault_path=vault_path)
        return await accessor.extract_profile_data(profile_id, **kwargs)

    return asyncio.run(_extract())
