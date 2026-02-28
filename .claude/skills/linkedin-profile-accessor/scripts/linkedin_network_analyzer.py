"""
LinkedIn Network Analyzer - Network Insights Module

Analyzes LinkedIn network data including connections, mutual connections,
and activity patterns.
"""

import asyncio
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from playwright.async_api import Page

from .profile_data_models import (
    ProfileData,
    ConnectionItem,
    PostItem,
    NetworkInsights,
    ActivityReport
)
from .linkedin_selectors import CONNECTION_SELECTORS
from .linkedin_helpers import (
    extract_text_with_fallbacks,
    clean_text,
    build_profile_url
)


class LinkedInNetworkAnalyzer:
    """
    Analyzes LinkedIn network and activity patterns.

    Usage:
        analyzer = LinkedInNetworkAnalyzer(vault_path="AI_Employee_Vault")
        insights = await analyzer.analyze_network(profile_data)
        activity = analyzer.analyze_activity_patterns(posts)
    """

    def __init__(self, vault_path: str | Path = "AI_Employee_Vault"):
        """
        Initialize the network analyzer.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)

    async def extract_connections(
        self,
        page: Page,
        limit: int = 100
    ) -> List[ConnectionItem]:
        """
        Extract connection data from network page.

        Args:
            page: Playwright Page instance (should be on network page)
            limit: Maximum number of connections to extract

        Returns:
            List of ConnectionItem objects
        """
        connections = []

        try:
            # Find all connection cards
            containers = await page.query_selector_all(CONNECTION_SELECTORS['container'][0])

            for container in containers[:limit]:
                try:
                    # Extract name
                    name_elem = await container.query_selector(CONNECTION_SELECTORS['name'][0])
                    name = await name_elem.inner_text() if name_elem else ""

                    # Extract headline
                    headline_elem = await container.query_selector(CONNECTION_SELECTORS['headline'][0])
                    headline = await headline_elem.inner_text() if headline_elem else ""

                    # Extract company (if available)
                    company_elem = await container.query_selector(CONNECTION_SELECTORS['company'][0])
                    company = await company_elem.inner_text() if company_elem else None

                    # Extract mutual connections count
                    mutual_elem = await container.query_selector(CONNECTION_SELECTORS['mutual_connections'][0])
                    mutual_text = await mutual_elem.inner_text() if mutual_elem else ""
                    mutual_count = self._extract_mutual_count(mutual_text)

                    # Extract profile URL
                    link_elem = await container.query_selector('a[href*="/in/"]')
                    url = await link_elem.get_attribute('href') if link_elem else None

                    if name:
                        connections.append(ConnectionItem(
                            name=clean_text(name),
                            headline=clean_text(headline),
                            company=clean_text(company) if company else None,
                            mutual=mutual_count,
                            url=url
                        ))
                except Exception:
                    continue

        except Exception:
            pass

        return connections

    def analyze_connections(
        self,
        connections: List[ConnectionItem]
    ) -> NetworkInsights:
        """
        Analyze connection data for insights.

        Args:
            connections: List of ConnectionItem objects

        Returns:
            NetworkInsights object with analysis
        """
        if not connections:
            return NetworkInsights(total_connections=0, mutual_connections=0)

        # Industry breakdown (from headline keywords)
        industry_keywords = {
            'Technology': ['engineer', 'developer', 'software', 'data', 'product', 'tech'],
            'Finance': ['finance', 'investment', 'banking', 'analyst', 'trader', 'fund'],
            'Marketing': ['marketing', 'brand', 'growth', 'content', 'social media', 'seo'],
            'Sales': ['sales', 'business development', 'account manager', 'revenue'],
            'HR': ['hr', 'recruiter', 'talent', 'people', 'hiring'],
            'Operations': ['operations', 'supply chain', 'logistics', 'project manager'],
            'Consulting': ['consultant', 'advisor', 'strategy'],
            'Executive': ['ceo', 'cto', 'cfo', 'vp', 'director', 'head of'],
        }

        industry_breakdown = {}
        company_breakdown = Counter()

        for conn in connections:
            # Industry classification
            headline_lower = conn.headline.lower() if conn.headline else ""
            classified = False

            for industry, keywords in industry_keywords.items():
                if any(keyword in headline_lower for keyword in keywords):
                    industry_breakdown[industry] = industry_breakdown.get(industry, 0) + 1
                    classified = True
                    break

            if not classified:
                industry_breakdown['Other'] = industry_breakdown.get('Other', 0) + 1

            # Company tracking
            if conn.company:
                company_breakdown[conn.company] += 1

        # Convert to percentages
        total = len(connections)
        industry_breakdown_pct = {
            k: {'count': v, 'percentage': round(v / total * 100, 1)}
            for k, v in industry_breakdown.items()
        }

        # Top connections (most mutual connections)
        top_connections = sorted(
            connections,
            key=lambda c: c.mutual,
            reverse=True
        )[:10]

        return NetworkInsights(
            total_connections=len(connections),
            mutual_connections=sum(c.mutual for c in connections),
            industry_breakdown=industry_breakdown_pct,
            company_breakdown=dict(company_breakdown.most_common(10)),
            top_connections=top_connections
        )

    def analyze_activity_patterns(self, posts: List[PostItem]) -> ActivityReport:
        """
        Analyze posting patterns and engagement.

        Args:
            posts: List of PostItem objects

        Returns:
            ActivityReport with pattern analysis
        """
        if not posts:
            return ActivityReport(
                posts_per_week=0,
                best_day="N/A",
                best_time="N/A",
                engagement_rate=0,
                avg_reactions=0,
                avg_comments=0
            )

        # Calculate averages (with division by zero protection)
        total_reactions = sum(p.reactions for p in posts)
        total_comments = sum(p.comments for p in posts)

        num_posts = len(posts)
        avg_reactions = total_reactions / num_posts if num_posts > 0 else 0
        avg_comments = total_comments / num_posts if num_posts > 0 else 0

        # Engagement rate (reactions + comments) / total
        total_engagement = total_reactions + total_comments
        engagement_rate = (total_engagement / num_posts) * 100 if num_posts > 0 else 0

        # Post frequency (assuming posts are from last month)
        posts_per_week = num_posts / 4 if num_posts > 0 else 0  # Approximate

        # Best day (simplified - would need actual dates)
        # For now, use a heuristic based on common LinkedIn activity
        best_day = "Tuesday"  # Typically high engagement
        best_time = "8-10 AM"  # Typical business hours

        return ActivityReport(
            posts_per_week=round(posts_per_week, 2),
            best_day=best_day,
            best_time=best_time,
            engagement_rate=round(engagement_rate, 2),
            avg_reactions=round(avg_reactions, 2),
            avg_comments=round(avg_comments, 2)
        )

    def identify_network_gaps(
        self,
        profile_data: ProfileData,
        network_insights: NetworkInsights
    ) -> List[str]:
        """
        Identify gaps in network coverage.

        Args:
            profile_data: User's profile data
            network_insights: Network analysis results

        Returns:
            List of gap descriptions
        """
        gaps = []

        # Check if network is too small
        if network_insights.total_connections < 100:
            gaps.append(f"Small network size ({network_insights.total_connections}) - aim for 500+ connections")

        # Check industry diversity
        if len(network_insights.industry_breakdown) < 3:
            gaps.append("Limited industry diversity - connect with professionals in other sectors")

        # Check for executive connections
        has_executives = any(
            'executive' in industry.lower() or 'vp' in industry.lower()
            for industry in network_insights.industry_breakdown.keys()
        )
        if not has_executives:
            gaps.append("Few executive-level connections - consider connecting with senior leaders")

        # Check company diversity
        if len(network_insights.company_breakdown) < 5:
            gaps.append("Connections concentrated at few companies - expand network")

        return gaps

    def generate_connection_recommendations(
        self,
        profile_data: ProfileData
    ) -> List[str]:
        """
        Generate recommendations for network growth.

        Args:
            profile_data: User's profile data

        Returns:
            List of recommendations
        """
        recommendations = []

        # Based on experience
        if profile_data.experience and len(profile_data.experience) > 0:
            current_company = profile_data.experience[0].company
            if current_company:
                recommendations.append(
                    f"Connect with more colleagues at {current_company} - "
                    "aim for 50+ connections from your current company"
                )

        # Based on industry
        if profile_data.headline:
            headline_lower = profile_data.headline.lower()
            if 'engineer' in headline_lower or 'developer' in headline_lower:
                recommendations.append(
                    "Connect with engineers at target companies like Google, Microsoft, Amazon"
                )
            elif 'marketing' in headline_lower:
                recommendations.append(
                    "Join marketing groups and connect with other marketing professionals"
                )

        # General recommendations
        recommendations.extend([
            "Connect with alumni from your education institutions",
            "Attend virtual events and connect with speakers and attendees",
            "Engage with content from industry leaders to build connections"
        ])

        return recommendations[:5]

    def _extract_mutual_count(self, text: str) -> int:
        """Extract mutual connections count from text."""
        import re

        if not text:
            return 0

        # Look for patterns like "5 mutual", "5 mutual connections"
        match = re.search(r'(\d+)\s*mutual', text.lower())
        if match:
            return int(match.group(1))

        return 0

    async def navigate_to_network(self, page: Page, profile_id: str) -> None:
        """
        Navigate to network page for a profile.

        Args:
            page: Playwright Page instance
            profile_id: LinkedIn profile ID
        """
        from .linkedin_helpers import build_profile_url

        # Build network URL
        profile_url = build_profile_url(profile_id)
        network_url = profile_url.rstrip("/") + "/detail/network/"

        try:
            await page.goto(network_url, wait_until="domcontentloaded")
            await asyncio.sleep(2)
        except Exception:
            # Try alternative navigation
            await page.goto(profile_url)
            await asyncio.sleep(1)
            # Click network button if exists
            try:
                network_button = await page.query_selector('a[href*="network"]')
                if network_button:
                    await network_button.click()
                    await asyncio.sleep(2)
            except Exception:
                pass

    def get_network_quality_score(self, connections: List[ConnectionItem]) -> Dict[str, int]:
        """
        Calculate network quality metrics.

        Args:
            connections: List of ConnectionItem objects

        Returns:
            Dictionary with quality metrics
        """
        if not connections:
            return {
                'total': 0,
                'with_mutual': 0,
                'senior_level': 0,
                'same_industry': 0,
                'quality_score': 0
            }

        # Count connections with mutual connections
        with_mutual = sum(1 for c in connections if c.mutual > 0)

        # Count senior-level connections
        senior_keywords = ['ceo', 'cto', 'cfo', 'vp', 'director', 'head', 'manager', 'lead']
        senior_level = 0
        for conn in connections:
            headline_lower = conn.headline.lower() if conn.headline else ""
            if any(keyword in headline_lower for keyword in senior_keywords):
                senior_level += 1

        # Calculate quality score (0-100)
        quality_score = 0
        if len(connections) > 0:
            quality_score += min(with_mutual / len(connections) * 40, 40)  # Max 40 points
            quality_score += min(senior_level / len(connections) * 30, 30)  # Max 30 points
            quality_score += 30 if len(connections) >= 100 else len(connections) * 0.3  # Max 30 points

        return {
            'total': len(connections),
            'with_mutual': with_mutual,
            'senior_level': senior_level,
            'same_industry': 0,  # Would need user's industry to calculate
            'quality_score': round(quality_score)
        }


# Convenience functions
async def extract_connections_sync(page: Page, limit: int = 100) -> List[ConnectionItem]:
    """Synchronous wrapper for extract_connections."""
    analyzer = LinkedInNetworkAnalyzer()
    return await analyzer.extract_connections(page, limit)


def analyze_activity_patterns_sync(posts: List[PostItem]) -> ActivityReport:
    """Synchronous wrapper for analyze_activity_patterns."""
    analyzer = LinkedInNetworkAnalyzer()
    return analyzer.analyze_activity_patterns(posts)
