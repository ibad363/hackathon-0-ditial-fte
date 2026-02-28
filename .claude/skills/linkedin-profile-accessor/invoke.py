#!/usr/bin/env python3
"""
LinkedIn Profile Accessor - Main Invocation Script

This script is invoked by Claude Code when the skill is called.
It extracts LinkedIn profile data and creates an approval file.

Usage:
    python invoke.py <profile_id> [options]

Options:
    --include-network    Include network analysis
    --include-posts      Include recent posts
    --post-limit N       Limit number of posts (default: 10)
    --output PATH        Custom output path
    --format FORMAT      Output format (markdown, json, csv)
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add scripts directory to path
scripts_dir = Path(__file__).parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Import modules from scripts directory
import importlib.util

# Import LinkedInProfileAccessor
spec = importlib.util.spec_from_file_location(
    "linkedin_profile_accessor",
    scripts_dir / "linkedin_profile_accessor.py"
)
linkedin_profile_accessor = importlib.util.module_from_spec(spec)
sys.modules["linkedin_profile_accessor"] = linkedin_profile_accessor
spec.loader.exec_module(linkedin_profile_accessor)

# Import LinkedInProfileAnalyzer
spec = importlib.util.spec_from_file_location(
    "linkedin_profile_analyzer",
    scripts_dir / "linkedin_profile_analyzer.py"
)
linkedin_profile_analyzer = importlib.util.module_from_spec(spec)
sys.modules["linkedin_profile_analyzer"] = linkedin_profile_analyzer
spec.loader.exec_module(linkedin_profile_analyzer)


def print_json_response(data: dict) -> None:
    """Print JSON response for Claude Code."""
    print(json.dumps(data, indent=2))


def create_approval_file(
    profile_data,
    vault_path: Path,
    analyzer
) -> Path:
    """Create approval file in Needs_Action/."""

    # Analyze profile
    completeness = analyzer.analyze_completeness(profile_data)
    strengths = analyzer.identify_strengths(profile_data)
    weaknesses = analyzer.identify_weaknesses(profile_data)
    suggestions = analyzer.generate_improvements(profile_data)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"LINKEDIN_PROFILE_ANALYSIS_{timestamp}.md"
    approval_file = vault_path / "Needs_Action" / filename

    # Generate markdown content
    content = generate_analysis_markdown(
        profile_data,
        completeness,
        strengths,
        weaknesses,
        suggestions
    )

    # Write file
    approval_file.parent.mkdir(parents=True, exist_ok=True)
    approval_file.write_text(content, encoding="utf-8")

    return approval_file


def generate_analysis_markdown(
    profile_data: "ProfileData",
    completeness: "CompletenessScore",
    strengths: list[str],
    weaknesses: list[str],
    suggestions: list["Suggestion"]
) -> str:
    """Generate markdown analysis report."""

    content = f"""---
type: linkedin_profile_analysis
profile_id: {profile_data.profile_id}
profile_url: {profile_data.profile_url}
created: {profile_data.extracted_at.isoformat()}
status: pending_approval
completeness_score: {completeness.total_score}
---

# LinkedIn Profile Analysis: {profile_data.name}

## Profile Overview

| Field | Value |
|-------|-------|
| **Name** | {profile_data.name} |
| **Headline** | {profile_data.headline} |
| **Location** | {profile_data.location or 'Not specified'} |
| **Connections** | {profile_data.connections_count or 'Unknown'} |
| **Profile URL** | {profile_data.profile_url} |

## Completeness Score: {completeness.total_score}/100

### Breakdown

| Section | Score | Status |
|---------|-------|--------|
| Professional Headline | {completeness.breakdown.get('headline', 0)}/10 | {'✅' if completeness.breakdown.get('headline', 0) == 10 else '❌'} |
| About Section ({profile_data.about_word_count} words) | {completeness.breakdown.get('about', 0)}/20 | {'✅' if completeness.breakdown.get('about', 0) >= 15 else '⚠️'} |
| Profile Photo | {completeness.breakdown.get('photo', 0)}/10 | {'✅' if profile_data.has_photo else '❌'} |
| Experience ({len(profile_data.experience)} positions) | {completeness.breakdown.get('experience', 0)}/25 | {'✅' if len(profile_data.experience) >= 3 else '⚠️'} |
| Education ({len(profile_data.education)} entries) | {completeness.breakdown.get('education', 0)}/10 | {'✅' if len(profile_data.education) >= 1 else '❌'} |
| Skills ({len(profile_data.skills)} skills) | {completeness.breakdown.get('skills', 0)}/15 | {'✅' if len(profile_data.skills) >= 10 else '⚠️'} |
| Recommendations ({len(profile_data.recommendations)}) | {completeness.breakdown.get('recommendations', 0)}/10 | {'✅' if len(profile_data.recommendations) >= 2 else '⚠️'} |

## Strengths

"""

    for strength in strengths:
        content += f"- {strength}\n"

    content += "\n## Weaknesses\n\n"
    for weakness in weaknesses:
        content += f"- {weakness}\n"

    content += "\n## Improvement Suggestions\n\n"
    for suggestion in suggestions:
        content += f"### {suggestion.priority} Priority: {suggestion.title}\n\n"
        content += f"{suggestion.description}\n\n"
        content += f"**Impact:** {suggestion.impact}\n\n"

    # Add detailed sections
    content += "## Detailed Profile Data\n\n"

    # About section
    if profile_data.about:
        content += f"### About Section\n\n{profile_data.about}\n\n"
        content += f"*Word Count: {profile_data.about_word_count}*\n\n"
    else:
        content += "### About Section\n\n*No about section found.*\n\n"

    # Experience
    if profile_data.experience:
        content += "### Experience\n\n"
        for exp in profile_data.experience:
            content += f"#### {exp.title} at {exp.company}\n"
            content += f"*{exp.start_date} - {exp.end_date or 'Present'}*\n\n"
            if exp.description:
                content += f"{exp.description}\n\n"

    # Education
    if profile_data.education:
        content += "### Education\n\n"
        for edu in profile_data.education:
            content += f"#### {edu.degree} from {edu.school}\n"
            if edu.graduation_year:
                content += f"*Graduated: {edu.graduation_year}*\n"
            content += "\n"

    # Skills
    if profile_data.skills:
        content += "### Skills\n\n"
        for skill in profile_data.skills[:20]:
            endorsements = f" ({skill.endorsements} endorsements)" if skill.endorsements > 0 else ""
            content += f"- {skill.name}{endorsements}\n"
        if len(profile_data.skills) > 20:
            content += f"\n*... and {len(profile_data.skills) - 20} more skills*\n"

    # Recent posts
    if profile_data.posts:
        content += "\n### Recent Activity\n\n"
        for post in profile_data.posts[:5]:
            content += f"- **{post.date}**: {post.text[:100]}... "
            content += f"({post.reactions} reactions, {post.comments} comments)\n"

    # Next steps
    content += """
## Next Steps

1. **Review this analysis** - Check for accuracy and completeness
2. **Move to Approved/** - To trigger LinkedIn Profile Builder for improvements
3. **Apply improvements** - Use the Builder skill to generate optimized content

```bash
# To approve and generate improvements:
mv AI_Employee_Vault/Needs_Action/{filename} \\
   AI_Employee_Vault/Approved/

# Then invoke the builder:
cd .claude/skills/linkedin-profile-builder
python invoke.py "{profile_id}" "target-role"
```

---
*Generated by LinkedIn Profile Accessor*
*Extraction Date: {profile_data.extracted_at.strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return content


async def main():
    """Main entry point."""

    # Parse arguments
    args = parse_arguments()

    # Initialize
    vault_path = Path(args.get("vault", "AI_Employee_Vault"))
    profile_id = args.get("profile_id")

    if not profile_id:
        print_json_response({
            "status": "error",
            "error": "No profile_id provided",
            "usage": "python invoke.py <profile_id> [options]"
        })
        sys.exit(1)

    # Create accessor using dynamically imported modules
    accessor = linkedin_profile_accessor.LinkedInProfileAccessor(vault_path=vault_path)
    analyzer = linkedin_profile_analyzer.LinkedInProfileAnalyzer(vault_path=vault_path)

    try:
        # Extract profile data
        profile_data = await accessor.extract_profile_data(
            profile_id=profile_id,
            include_posts=args.get("include_posts", True),
            post_limit=args.get("post_limit", 10),
            include_network=args.get("include_network", False)
        )

        # Create approval file
        approval_file = create_approval_file(profile_data, vault_path, analyzer)

        # Print success response
        print_json_response({
            "status": "success",
            "profile_id": profile_id,
            "name": profile_data.name,
            "completeness_score": profile_data.completeness_score,
            "action_file": str(approval_file),
            "next_steps": [
                f"Review analysis at: {approval_file}",
                "Move to Approved/ to generate improvements",
                "Use LinkedIn Profile Builder to create optimized content"
            ]
        })

    except ConnectionError as e:
        print_json_response({
            "status": "error",
            "error": "Could not connect to Chrome",
            "details": str(e),
            "solution": "Start Chrome with CDP: scripts/social-media/START_AUTOMATION_CHROME.bat"
        })
        sys.exit(1)

    except Exception as e:
        print_json_response({
            "status": "error",
            "error": str(e),
            "profile_id": profile_id
        })
        sys.exit(1)


def parse_arguments() -> dict:
    """Parse command line arguments."""

    args = {
        "profile_id": None,
        "include_network": False,
        "include_posts": True,
        "post_limit": 10,
        "vault": "AI_Employee_Vault",
        "output": None,
        "format": "markdown"
    }

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg.startswith("--"):
            key = arg[2:].replace("-", "_")
            if key in args:
                i += 1
                if i < len(sys.argv) and not sys.argv[i].startswith("--"):
                    value = sys.argv[i]
                    # Convert to appropriate type
                    if key in ["include_network", "include_posts"]:
                        args[key] = value.lower() in ["true", "1", "yes"]
                    elif key in ["post_limit"]:
                        args[key] = int(value)
                    else:
                        args[key] = value
        else:
            args["profile_id"] = arg

        i += 1

    return args


if __name__ == "__main__":
    asyncio.run(main())
