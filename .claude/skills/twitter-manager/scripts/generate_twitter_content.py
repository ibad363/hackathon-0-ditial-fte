#!/usr/bin/env python3
"""
Generate Twitter (X) Content

Generates Twitter-optimized content for a given topic and creates
an approval file in /Pending_Approval/.

Usage:
    python generate_twitter_content.py --vault . --topic "New product launch"
"""

import argparse
from pathlib import Path
from datetime import datetime
import json
import sys


# Add parent directory to path to import from utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "utils"))


def generate_twitter_content(topic: str, tone: str = "engaging") -> dict:
    """
    Generate Twitter-optimized content.

    Args:
        topic: Topic or key message
        tone: Tone of voice (engaging, professional, casual, excited)

    Returns:
        Dictionary with content, hashtags, and metadata
    """
    # Content templates based on tone
    templates = {
        "engaging": {
            "emoji": "🚀",
            "opening": "",
            "style": "question",
        },
        "professional": {
            "emoji": "💡",
            "opening": "Insight:",
            "style": "statement",
        },
        "casual": {
            "emoji": "✨",
            "opening": "Quick thought:",
            "style": "casual",
        },
        "excited": {
            "emoji": "🔥",
            "opening": "BIG NEWS:",
            "style": "announcement",
        }
    }

    template = templates.get(tone, templates["engaging"])

    # Hashtag suggestions based on common topics
    hashtag_suggestions = {
        "product": ["#ProductLaunch", "#NewFeatures", "#Innovation", "#Tech", "#StartupLife"],
        "company": ["#CompanyNews", "#BehindTheScenes", "#TeamWork", "#Business", "#Entrepreneur"],
        "tips": ["#ProTips", "#HowTo", "#BusinessTips", "#Advice", "#Productivity"],
        "event": ["#Event", "#JoinUs", "#MarkYourCalendar", "#Webinar", "#Networking"],
        "tech": ["#Tech", "#Coding", "#Development", "#Programming", "#Software"],
        "general": ["#Growth", "#Success", "#Business", "#Motivation", "#Leadership"]
    }

    # Detect topic category
    topic_lower = topic.lower()
    if any(word in topic_lower for word in ["launch", "product", "feature", "update"]):
        category = "product"
    elif any(word in topic_lower for word in ["team", "company", "news", "announcement"]):
        category = "company"
    elif any(word in topic_lower for word in ["tip", "guide", "how", "tutorial"]):
        category = "tips"
    elif any(word in topic_lower for word in ["event", "webinar", "workshop"]):
        category = "event"
    elif any(word in topic_lower for word in ["code", "dev", "tech", "api", "software"]):
        category = "tech"
    else:
        category = "general"

    hashtags = hashtag_suggestions.get(category, hashtag_suggestions["general"])

    # Generate content based on style
    if template["style"] == "question":
        content = f"""{template['emoji']} {topic}

What do you think? 👇

{' '.join(hashtags[:3])}"""
    elif template["style"] == "statement":
        content = f"""{template['emoji']} {template['opening']} {topic}

{' '.join(hashtags[:3])}"""
    elif template["style"] == "announcement":
        content = f"""{template['emoji']} {template['opening']}

{topic}

This is huge! 🎉

{' '.join(hashtags[:3])}"""
    else:  # casual
        content = f"""{template['emoji']} {template['opening']} {topic}

{' '.join(hashtags[:3])}"""

    # Check character count (Twitter limit is 280)
    char_count = len(content)
    if char_count > 280:
        # Trim hashtags if over limit
        words = content.split()
        hashtag_count = len([w for w in words if w.startswith('#')])
        if hashtag_count > 2:
            # Reduce to 2 hashtags
            content = ' '.join(words[:-1])
            content += ' ' + words[-2]
            char_count = len(content)

    return {
        "content": content,
        "hashtags": hashtags,
        "category": category,
        "tone": tone,
        "platform": "Twitter",
        "char_count": len(content),
        "within_limit": len(content) <= 280
    }


def create_approval_file(vault_path: Path, content_data: dict, topic: str) -> Path:
    """
    Create an approval file in /Pending_Approval/.

    Args:
        vault_path: Path to the vault
        content_data: Dictionary with generated content
        topic: Original topic

    Returns:
        Path to the created approval file
    """
    pending_folder = vault_path / "Pending_Approval"
    pending_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"TWITTER_POST_{timestamp}.md"
    filepath = pending_folder / filename

    # Create approval file content
    file_content = f"""---
type: twitter_post
platforms: [Twitter]
priority: medium
created: {datetime.now().isoformat()}
status: pending
tone: {content_data['tone']}
category: {content_data['category']}
char_count: {content_data['char_count']}
within_limit: {str(content_data['within_limit']).lower()}
---

# Twitter Post: {topic}

## Content
```
{content_data['content']}
```

## Character Count
{content_data['char_count']} / 280

{'✅ Within limit' if content_data['within_limit'] else '⚠️ OVER LIMIT - Edit before posting'}

## Hashtags Used
{', '.join(content_data['hashtags'][:3])}

## Scheduling
- **Best time to post:** 8-9 AM, 12-1 PM, or 5-6 PM
- **Best days:** Tuesday, Wednesday, Thursday

## Approval Required
Please review and move to `/Approved/` when ready to publish.

**To Approve:** Move this file to `/Approved/`
**To Reject:** Move this file to `/Rejected/`
**To Edit:** Edit this file, then move to `/Approved/`

---

*Generated by Twitter Manager Skill*
"""

    filepath.write_text(file_content, encoding='utf-8')
    return filepath


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Twitter content and create approval file"
    )

    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--topic",
        required=True,
        help="Topic or key message for the tweet"
    )

    parser.add_argument(
        "--tone",
        default="engaging",
        choices=["engaging", "professional", "casual", "excited"],
        help="Tone of voice (default: engaging)"
    )

    args = parser.parse_args()

    vault_path = Path(args.vault)

    # Generate content
    print("=" * 60)
    print("Twitter Content Generator")
    print("=" * 60)
    print(f"Topic: {args.topic}")
    print(f"Tone: {args.tone}")
    print("=" * 60)

    content_data = generate_twitter_content(args.topic, args.tone)

    print(f"\nGenerated Content:")
    print("-" * 60)
    print(content_data['content'])
    print("-" * 60)
    print(f"\nCharacter Count: {content_data['char_count']} / 280")
    print(f"Within Limit: {'Yes ✅' if content_data['within_limit'] else 'No ⚠️'}")

    # Create approval file
    filepath = create_approval_file(vault_path, content_data, args.topic)

    print(f"\n✅ Approval file created: {filepath}")
    print(f"📁 Location: /Pending_Approval/{filepath.name}")
    print("\nNext steps:")
    print("1. Review the content in the approval file")
    print("2. Edit if needed")
    print("3. Move to /Approved/ to queue for posting")
    print("4. The twitter_approval_monitor will handle the rest")


if __name__ == "__main__":
    main()
