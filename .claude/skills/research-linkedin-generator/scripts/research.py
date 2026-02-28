#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Research LinkedIn Generator - AI Employee Skill

Automatically research topics and generate professional LinkedIn posts.
Integrates with the AI Employee approval workflow.
"""

from __future__ import annotations

import sys
import os

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
import argparse
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

# Load .env file if it exists
env_path = Path(__file__).parent.parent.parent.parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# Add project root to path (go up 5 levels: scripts/ -> skill/ -> skills/ -> .claude/ -> root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Try to use trafilatura, fall back to simple extractor
try:
    from utils.content_extractor import ContentExtractor
except ImportError:
    from utils.content_extractor_simple import ContentExtractor

from utils.research_analyzer import ResearchAnalyzer

# Import deep research capabilities
try:
    from utils.deep_research import DeepResearcher, DocumentationFinder, LibraryAnalyzer
    HAS_DEEP_RESEARCH = True
except ImportError:
    HAS_DEEP_RESEARCH = False
    print("[WARNING] Deep research module not available. Install: pip install requests beautifulsoup4")


class ResearchLinkedInGenerator:
    """Research topics and generate LinkedIn posts"""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.plans_path = self.vault_path / "Plans"
        self.pending_path = self.vault_path / "Pending_Approval"
        self.done_path = self.vault_path / "Done"

        # Initialize utilities
        self.content_extractor = ContentExtractor()
        self.research_analyzer = ResearchAnalyzer()

        # Initialize deep research if available
        if HAS_DEEP_RESEARCH:
            self.deep_researcher = DeepResearcher(cache_dir=self.vault_path / ".cache" / "research")
            self.doc_finder = DocumentationFinder()
            self.lib_analyzer = LibraryAnalyzer()
        else:
            self.deep_researcher = None
            self.doc_finder = None
            self.lib_analyzer = None

        # MCP server path
        self.playwright_mcp = Path(__file__).parent.parent.parent.parent / "mcp-servers" / "playwright-mcp"

    def create_research_request(self, topic: str, urls: List[str] = None) -> Path:
        """Create a research request file in Inbox"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = topic.lower().replace(" ", "_")[:50]
        filename = f"RESEARCH_REQUEST_{timestamp}_{slug}.md"

        request_file = self.inbox_path / filename

        urls_section = ""
        if urls:
            urls_section = "\n## Source URLs (provided)\n" + "\n".join(f"- {url}" for url in urls)

        content = f"""---
type: research_request
action: research_and_linkedin_post
topic: {topic}
created: {datetime.now().isoformat()}
---

# Research Request: {topic}

Please research this topic and create a professional LinkedIn post.
{urls_section}
## Research Requirements
- Search for recent articles (past 30 days) if URLs not provided
- Analyze 8-10 relevant sources
- Extract key insights, statistics, and quotes
- Generate a 1,000-2,000 character LinkedIn post
- Cite all sources for statistics and quotes

## Output Format
- Professional tone
- Include hook, body, call-to-action
- Add 5-10 relevant hashtags
- Cite sources inline

## Approval
The generated post will require approval before posting.
"""

        request_file.parent.mkdir(parents=True, exist_ok=True)
        request_file.write_text(content, encoding="utf-8")

        print(f"✓ Research request created: {request_file}")
        return request_file

    def process_inbox_requests(self):
        """Process all research requests in Inbox"""
        requests = list(self.inbox_path.glob("RESEARCH_REQUEST_*.md"))

        if not requests:
            print("No research requests found in Inbox")
            return

        print(f"Found {len(requests)} research request(s)")

        for request_file in requests:
            print(f"\nProcessing: {request_file.name}")

            # Parse request
            content = request_file.read_text()
            topic = self._extract_topic(content)

            if topic:
                self._process_research(topic, request_file)
            else:
                print(f"  ✗ Could not extract topic from request")

    def process_daily_research(self):
        """Process daily research with pre-configured topics"""
        import json
        from datetime import datetime

        # Load daily topics config
        config_path = Path(__file__).parent.parent / "daily_topics.json"

        if not config_path.exists():
            print(f"Config file not found: {config_path}")
            return

        with open(config_path) as f:
            config = json.load(f)

        # Get today's topic based on day of week
        today = datetime.now().strftime("%A").lower()
        topics = config.get("daily_topics", [])

        if not topics:
            print("No topics configured")
            return

        # Select topic for today (rotate through topics)
        topics_per_day = config.get("schedule", {}).get("topics_per_day", 1)
        day_index = (datetime.now().weekday()) % len(topics)

        print(f"Daily Research Run - {today}")
        print(f"=" * 50)

        for i in range(topics_per_day):
            topic_index = (day_index + i) % len(topics)
            topic_config = topics[topic_index]

            print(f"\nProcessing: {topic_config['topic']}")
            print("-" * 40)

            try:
                self._process_research_with_urls(
                    topic_config['topic'],
                    topic_config['sources']
                )
            except Exception as e:
                print(f"  ✗ Error: {e}")

        print("\n" + "=" * 50)
        print("Daily research complete!")

    def _extract_topic(self, content: str) -> str:
        """Extract topic from request file"""
        for line in content.split('\n'):
            if line.startswith('topic: '):
                return line.split(':', 1)[1].strip()
        return None

    def _process_research_with_urls(self, topic: str, source_urls: List[str]):
        """Process research for a topic with provided URLs - for cloud VM"""
        print(f"  Topic: {topic}")
        print(f"  URLs: {len(source_urls)} provided")

        try:
            # Skip search, use provided URLs
            print("  → Step 1: Using provided URLs...")

            # Step 2: Extract content from URLs
            print("  → Step 2: Extracting content...")
            articles = self.content_extractor.extract_multiple(source_urls)

            if not articles:
                print("  ✗ No content could be extracted")
                return

            print(f"  ✓ Extracted content from {len(articles)} sources")

            # Step 3: Analyze research with GLM-4.7
            print("  → Step 3: Analyzing research...")
            analysis = self.research_analyzer.analyze_research(topic, articles)
            print(f"  ✓ Analysis complete: {analysis.get('sources_analyzed', 0)} sources analyzed")

            # Step 4: Generate LinkedIn post
            print("  → Step 4: Generating LinkedIn post...")
            linkedin_post = self.research_analyzer.generate_linkedin_post(topic, analysis)
            print(f"  ✓ Generated {len(linkedin_post)} character post")

            # Step 5: Create approval file
            print("  → Step 5: Creating approval file...")
            approval_file = self._create_approval_file(topic, analysis, linkedin_post, source_urls)
            print(f"  ✓ Created: {approval_file.name}")

            print("\n  === SUMMARY ===")
            print(f"  Post length: {len(linkedin_post)} chars")
            print(f"  Sources used: {len(articles)}")
            print(f"  Review at: {approval_file}")

        except Exception as e:
            print(f"  ✗ Error processing research: {e}")
            import traceback
            traceback.print_exc()

    def _process_research(self, topic: str, request_file: Path):
        """Process research for a topic - full workflow implementation"""
        print(f"  Topic: {topic}")

        try:
            # Step 1: Search Google for the topic
            print("  → Step 1: Searching Google...")
            source_urls = self._search_google(topic)

            if not source_urls:
                print("  ✗ No search results found")
                return

            print(f"  ✓ Found {len(source_urls)} sources")

            # Step 2: Extract content from URLs
            print("  → Step 2: Extracting content...")
            articles = self.content_extractor.extract_multiple(source_urls)

            if not articles:
                print("  ✗ No content could be extracted")
                return

            print(f"  ✓ Extracted content from {len(articles)} sources")

            # Step 3: Analyze research with GLM-4.7
            print("  → Step 3: Analyzing research...")
            analysis = self.research_analyzer.analyze_research(topic, articles)
            print(f"  ✓ Analysis complete: {analysis.get('sources_analyzed', 0)} sources analyzed")

            # Step 4: Generate LinkedIn post
            print("  → Step 4: Generating LinkedIn post...")
            linkedin_post = self.research_analyzer.generate_linkedin_post(topic, analysis)
            print(f"  ✓ Generated {len(linkedin_post)} character post")

            # Step 5: Create approval file
            print("  → Step 5: Creating approval file...")
            approval_file = self._create_approval_file(topic, analysis, linkedin_post, source_urls)
            print(f"  ✓ Created: {approval_file.name}")

            # Move request to Plans
            plan_file = self.plans_path / request_file.name.replace("REQUEST", "")
            request_file.rename(plan_file)
            print(f"  ✓ Moved request to Plans/")

            print("\n  === SUMMARY ===")
            print(f"  Post length: {len(linkedin_post)} chars")
            print(f"  Sources used: {len(articles)}")
            print(f"  Review at: {approval_file}")

        except Exception as e:
            print(f"  ✗ Error processing research: {e}")
            import traceback
            traceback.print_exc()

    def _search_google(self, topic: str, max_results: int = 10) -> List[str]:
        """
        Search for articles about a topic.
        For cloud VM: Uses DuckDuckGo HTML (more permissive than Google).
        Falls back to trafilatura's built-in search if available.
        """
        try:
            import requests
            from html.parser import HTMLParser

            # Use DuckDuckGo HTML search (more permissive for headless/cloud)
            search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(topic)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=30)
            response.raise_for_status()

            # Parse results using regex
            url_pattern = r'class="result__url"[^>]*><a[^>]*href="(https?://[^"]+)"'
            matches = re.findall(url_pattern, response.text)

            # DuckDuckGo redirects, so we need to resolve the actual URLs
            urls = []
            for match in matches[:max_results * 2]:  # Get more to filter
                # Remove DuckDuckGo redirect prefix if present
                clean_url = match
                if 'uddg=' in match:
                    clean_url = re.sub(r'^https?://[^/]*//uddg=', '', match)
                    # URL decode
                    from urllib.parse import unquote
                    try:
                        clean_url = unquote(clean_url)
                    except:
                        pass

                # Filter quality domains
                if self._is_quality_url(clean_url):
                    urls.append(clean_url)
                    if len(urls) >= max_results:
                        break

            if urls:
                print(f"  ✓ Found {len(urls)} URLs via DuckDuckGo")
                return urls
            else:
                print("  ⚠ No URLs found, using fallback")
                return self._fallback_urls(topic)

        except Exception as e:
            print(f"  ⚠ Search error ({e}), using fallback")
            return self._fallback_urls(topic)

    def _is_quality_url(self, url: str) -> bool:
        """Check if URL is from a quality source"""
        exclude_patterns = [
            'google.', 'youtube.', 'facebook.', 'twitter.', 'linkedin.',
            'instagram.', 'pinterest.', 'reddit.', 'amazon.', 'ebay.',
            'duckduckgo', 'yandex.', 'bing.'
        ]

        url_lower = url.lower()

        # Exclude low-quality sources
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False

        # Include good sources
        good_patterns = [
            '.com/', '.org/', '.edu/', '.net/', '.io/', '.co/',
            'blog.', 'news.', 'tech.', 'medium.com', 'dev.to'
        ]

        return any(pattern in url_lower for pattern in good_patterns)

    def _extract_urls_from_search_result(self, result_text: str) -> List[str]:
        """Extract URLs from search result (legacy, for Playwright MCP compatibility)"""
        urls = []
        url_pattern = r'https?://[^\s\)"\'\>]+'
        matches = re.findall(url_pattern, result_text)

        for url in matches:
            if self._is_quality_url(url):
                urls.append(url)

        return urls[:10]

    def _fallback_urls(self, topic: str) -> List[str]:
        """
        Fallback: Use a few reputable tech/news sources with topic in URL.
        This is a simple heuristic for when search fails.
        """
        # Generate likely search URLs based on topic keywords
        keywords = topic.lower().split()[:3]
        fallback_urls = []

        # Common tech news domains
        domains = [
            'techcrunch.com',
            'theverge.com',
            'wired.com',
            'arstechnica.com',
            'news.ycombinator.com'
        ]

        # This is just a placeholder - in real use you'd want proper search
        # For now return empty to signal that proper URLs should be provided
        print("  ℹ No search results available. Please provide URLs manually.")
        return []

    def _create_approval_file(self, topic: str, analysis: Dict, post: str, sources: List[str]) -> Path:
        """Create approval file in Pending_Approval/"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = topic.lower().replace(" ", "_")[:30]
        filename = f"LINKEDIN_POST_RESEARCH_{timestamp}_{slug}.md"

        approval_file = self.pending_path / filename

        # Format sources list
        sources_text = "\n".join(f"{i+1}. {url}" for i, url in enumerate(sources[:8]))

        # Format analysis
        themes_text = "\n".join(f"  - {t}" for t in analysis.get("themes", [])[:5])
        stats_text = "\n".join(f"  - {s}" for s in analysis.get("key_statistics", [])[:5])

        content = f"""---
type: linkedin_post
action: post_to_linkedin
platform: linkedin
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=7)).isoformat()}
status: pending
research_topic: {topic}
sources_count: {len(sources)}
char_count: {len(post)}
---

# LinkedIn Post: {topic}

## Research Summary
{analysis.get('summary', '')}

## Key Themes
{themes_text}

## Key Statistics
{stats_text}

## LinkedIn Post
{post}

## Sources
{sources_text}

---
*This post was auto-generated from research on {len(sources)} sources.*
*Review for accuracy and tone before approving.*
"""

        approval_file.parent.mkdir(parents=True, exist_ok=True)
        approval_file.write_text(content, encoding='utf-8')

        return approval_file

    def process_deep_research(self, topic: str, max_depth: int = 3) -> Optional[Path]:
        """
        Perform deep multi-level research on a topic.

        Research Levels:
        1. Surface: Article content extraction
        2. Documentation: Official docs, guides, references
        3. Libraries: GitHub repos, package info, dependencies

        Args:
            topic: Research topic
            max_depth: Maximum research depth (1-3)

        Returns:
            Path to approval file if successful, None otherwise
        """
        if not HAS_DEEP_RESEARCH:
            print("  ⚠ Deep research not available. Using standard research.")
            return None

        print(f"  🔬 Deep Research: {topic}")
        print(f"  Max Depth: {max_depth}")
        print("-" * 50)

        try:
            # Phase 1: Multi-level research
            print("  → Phase 1: Multi-level research...")
            deep_results = self.deep_researcher.research_topic(topic, max_depth)

            # Phase 2: Compile articles from all levels
            all_articles = []

            # Level 1: Surface articles
            for source in deep_results["levels"]["surface"]:
                if "url" in source:
                    all_articles.append(source)

            # Level 2: Documentation
            for doc in deep_results["levels"]["documentation"]:
                if "url" in doc:
                    all_articles.append({
                        "url": doc["url"],
                        "title": doc.get("title", "Documentation"),
                        "domain": urlparse(doc["url"]).netloc,
                        "text": f"Official documentation for {doc.get('tech', topic)}",
                        "word_count": 500
                    })

            # Level 3: Libraries
            for lib in deep_results["levels"]["libraries"]:
                if lib.get("type") == "github_repo":
                    all_articles.append({
                        "url": lib["url"],
                        "title": f"{lib.get('name', 'Repository')} - GitHub",
                        "domain": "github.com",
                        "text": self._format_github_repo_info(lib),
                        "word_count": 500
                    })
                elif lib.get("type") in ["pypi_package", "npm_package", "crate"]:
                    all_articles.append({
                        "url": lib["url"],
                        "title": f"{lib.get('name', 'Package')} - {lib.get('manager', 'Package')}",
                        "domain": urlparse(lib["url"]).netloc,
                        "text": self._format_package_info(lib),
                        "word_count": 300
                    })

            if not all_articles:
                print("  ✗ No sources found in deep research")
                return None

            print(f"  ✓ Found {len(all_articles)} sources across {max_depth} levels")

            # Phase 3: Enhanced analysis with library insights
            print("  → Phase 2: Enhanced analysis...")
            analysis = self._create_enhanced_analysis(topic, deep_results, all_articles)
            print(f"  ✓ Analysis: {analysis.get('sources_analyzed', 0)} sources")

            # Phase 4: Generate LinkedIn post with library context
            print("  → Phase 3: Generating LinkedIn post...")
            linkedin_post = self._generate_deep_post(topic, analysis, deep_results)
            print(f"  ✓ Generated {len(linkedin_post)} character post")

            # Phase 5: Create approval file with deep research metadata
            print("  → Phase 4: Creating approval file...")
            approval_file = self._create_deep_approval_file(topic, analysis, linkedin_post, deep_results)
            print(f"  ✓ Created: {approval_file.name}")

            print("\n  === DEEP RESEARCH SUMMARY ===")
            print(f"  Research Depth: {max_depth} levels")
            print(f"  Total Sources: {len(all_articles)}")
            print(f"  Technologies Found: {len(deep_results['insights']['technologies'])}")
            print(f"  Libraries Analyzed: {len(deep_results['levels']['libraries'])}")
            print(f"  Post Length: {len(linkedin_post)} chars")
            print(f"  Review at: {approval_file}")

            return approval_file

        except Exception as e:
            print(f"  ✗ Deep research failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _format_github_repo_info(self, lib: Dict[str, Any]) -> str:
        """Format GitHub repository information as text."""
        info = [
            f"Repository: {lib.get('name', 'N/A')}",
            f"Description: {lib.get('description', 'No description')}",
            f"Language: {lib.get('language', 'N/A')}",
            f"Stars: {lib.get('stars', 0):,}",
            f"Forks: {lib.get('forks', 0):,}",
        ]
        return " | ".join(info)

    def _format_package_info(self, pkg: Dict[str, Any]) -> str:
        """Format package information as text."""
        info = [
            f"Package: {pkg.get('name', 'N/A')}",
            f"Version: {pkg.get('version', 'N/A')}",
            f"Manager: {pkg.get('manager', 'N/A')}",
        ]
        if pkg.get('author'):
            info.append(f"Author: {pkg['author']}")
        return " | ".join(info)

    def _create_enhanced_analysis(self, topic: str, deep_results: Dict, articles: List[Dict]) -> Dict[str, Any]:
        """Create enhanced analysis with library insights."""
        # Use the research analyzer for basic analysis
        basic_analysis = self.research_analyzer.analyze_research(topic, articles)

        # Add deep research insights
        enhanced = dict(basic_analysis)

        # Add technology stack insights
        enhanced["technology_stack"] = deep_results["insights"]

        # Add library analysis
        if deep_results["levels"]["libraries"]:
            enhanced["library_analysis"] = {
                "github_repos": [lib for lib in deep_results["levels"]["libraries"] if lib.get("type") == "github_repo"],
                "packages": [lib for lib in deep_results["levels"]["libraries"] if lib.get("type") in ["pypi_package", "npm_package", "crate"]],
                "total_repos": len([lib for lib in deep_results["levels"]["libraries"] if lib.get("type") == "github_repo"]),
                "total_packages": len([lib for lib in deep_results["levels"]["libraries"] if lib.get("type") in ["pypi_package", "npm_package", "crate"]])
            }

        return enhanced

    def _generate_deep_post(self, topic: str, analysis: Dict, deep_results: Dict) -> str:
        """Generate LinkedIn post with deep research context."""
        # Build context with library insights
        tech_stack = analysis.get("technology_stack", {})
        lib_analysis = analysis.get("library_analysis", {})

        # Create enhanced prompt
        tech_list = ", ".join(tech_stack.get("technologies", [])[:5])
        frameworks = ", ".join(tech_stack.get("frameworks", [])[:3])

        context_addition = ""
        if lib_analysis.get("total_repos", 0) > 0:
            repo_names = [lib.get("name", "repo") for lib in lib_analysis.get("github_repos", [])[:3]]
            context_addition = f"\n\n# GitHub Repositories Analyzed\n{', '.join(repo_names)}"
        if frameworks:
            context_addition += f"\n\n# Key Frameworks\n{frameworks}"

        base_post = self.research_analyzer.generate_linkedin_post(topic, analysis)

        # Enhance with library context if available
        if context_addition:
            enhanced_post = f"""{base_post}

---

📚 Deep Research Insights{context_addition}

#TechnicalResearch #AIEmployee #TechInsights"""

            return enhanced_post

        return base_post

    def _create_deep_approval_file(self, topic: str, analysis: Dict, post: str, deep_results: Dict) -> Path:
        """Create approval file with deep research metadata."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = topic.lower().replace(" ", "_")[:30]
        filename = f"LINKEDIN_POST_DEEP_RESEARCH_{timestamp}_{slug}.md"

        approval_file = self.pending_path / filename

        # Format technology insights
        tech_stack = analysis.get("technology_stack", {})
        tech_text = "\n".join(f"  - {t}" for t in tech_stack.get("technologies", [])[:10])
        frameworks_text = "\n".join(f"  - {f}" for f in tech_stack.get("frameworks", [])[:5])
        libraries_text = "\n".join(f"  - {l}" for l in tech_stack.get("libraries", [])[:5])

        # Format library analysis
        lib_analysis = analysis.get("library_analysis", {})
        repos_section = ""
        if lib_analysis.get("github_repos"):
            repos = lib_analysis["github_repos"][:5]
            repos_section = "\n".join(
                f"  - [{lib.get('name', 'N/A')}]({lib.get('url', '')}) - "
                f"{lib.get('stars', 0)} ⭐, {lib.get('language', 'N/A')}"
                for lib in repos
            )

        packages_section = ""
        if lib_analysis.get("packages"):
            packages = lib_analysis["packages"][:5]
            packages_section = "\n".join(
                f"  - [{pkg.get('name', 'N/A')}]({pkg.get('url', '')}) - "
                f"{pkg.get('manager', 'N/A')}"
                for pkg in packages
            )

        content = f"""---
type: linkedin_post
action: post_to_linkedin
platform: linkedin
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=7)).isoformat()}
status: pending
research_topic: {topic}
research_type: deep_research
research_depth: 3
sources_count: {len(deep_results.get('sources', []))}
char_count: {len(post)}
---

# LinkedIn Post: {topic}
(Deep Research - 3 Levels)

## Technology Stack Identified

### Technologies
{tech_text if tech_text else "  - None identified"}

### Frameworks
{frameworks_text if frameworks_text else "  - None identified"}

### Libraries & Tools
{libraries_text if libraries_text else "  - None identified"}

## GitHub Repositories Analyzed
{repos_section if repos_section else "  - None analyzed"}

## Package References
{packages_section if packages_section else "  - None found"}

## LinkedIn Post
{post}

---

## Research Metadata
**Research Type:** Multi-level Deep Research
**Level 1 (Surface):** {len(deep_results.get('levels', {}).get('surface', []))} sources
**Level 2 (Documentation):** {len(deep_results.get('levels', {}).get('documentation', []))} sources
**Level 3 (Libraries):** {len(deep_results.get('levels', {}).get('libraries', []))} sources

**Total Sources Analyzed:** {len(deep_results.get('sources', []))}
**Technologies Identified:** {len(tech_stack.get('technologies', []))}
**Research Depth:** 3 levels (Surface → Documentation → Libraries)

---
*This post was generated using deep research methodology.*
*Sources analyzed at multiple levels: articles, official docs, and package repositories.*
*Review for accuracy before approving.*
"""

        approval_file.parent.mkdir(parents=True, exist_ok=True)
        approval_file.write_text(content, encoding="utf-8")

        return approval_file


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Research LinkedIn Generator - AI Employee Skill"
    )
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--topic",
        help="Topic to research (creates request in Inbox)"
    )
    parser.add_argument(
        "--urls",
        help="Comma-separated URLs to use as sources (optional, for --topic or --process-topic)"
    )
    parser.add_argument(
        "--process-topic",
        help="Research topic directly and create approval file"
    )
    parser.add_argument(
        "--process",
        action="store_true",
        help="Process all requests in Inbox"
    )
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Run daily research with pre-configured topics"
    )
    parser.add_argument(
        "--deep-research",
        action="store_true",
        help="Use deep research methodology (3-level: articles → docs → libraries)"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=3,
        choices=[1, 2, 3],
        help="Research depth for --deep-research (1-3, default: 3)"
    )

    args = parser.parse_args()

    # Parse URLs if provided
    source_urls = None
    if args.urls:
        source_urls = [url.strip() for url in args.urls.split(",") if url.strip()]
        print(f"Using {len(source_urls)} provided source URLs")

    generator = ResearchLinkedInGenerator(args.vault)

    if args.topic:
        print(f"Creating research request for: {args.topic}")
        generator.create_research_request(args.topic, source_urls)
        print("\nNext steps:")
        print("1. Run with --process to handle all Inbox requests")
        print("2. Or run with --process-topic '{}' to process immediately".format(args.topic))
        print("3. Research will be saved to Plans/")
        print("4. LinkedIn post will be created in Pending_Approval/")
        print("5. Review and move to Approved/ to publish")

    elif args.process_topic:
        print(f"Processing research topic: {args.process_topic}\n")
        # Pass URLs directly if provided, otherwise search
        if source_urls:
            print(f"Using {len(source_urls)} provided URLs")
            generator._process_research_with_urls(args.process_topic, source_urls)
        else:
            generator._process_research(args.process_topic, None)
        print("\nNext steps:")
        print("1. Review the generated post in Pending_Approval/")
        print("2. Move to Approved/ to publish to LinkedIn")

    elif args.process:
        print("Processing research requests...")
        generator.process_inbox_requests()

    elif args.daily:
        print("Running daily research...")
        generator.process_daily_research()

    elif args.deep_research:
        # Use the provided topic or first daily topic
        research_topic = args.process_topic or "AI technology trends"

        print(f"🔬 Deep Research Mode: {research_topic}")
        print(f"Research Depth: {args.depth} levels")
        print("=" * 60)

        approval_file = generator.process_deep_research(research_topic, args.depth)

        if approval_file:
            print("\n✓ Deep research complete!")
            print(f"Review at: {approval_file}")
            print("\nTo approve, move file to Approved/")
        else:
            print("\n✗ Deep research failed. Falling back to standard research...")
            # Fallback to standard research
            generator._process_research(research_topic, None)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
