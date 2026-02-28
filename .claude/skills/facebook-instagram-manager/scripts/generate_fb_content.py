#!/usr/bin/env python3
"""
Generate Facebook Content

Generates Facebook-optimized content for a given topic and creates
an approval file in /Pending_Approval/.

Usage:
    python generate_fb_content.py --vault . --topic "New product launch"
"""

import argparse
from pathlib import Path
from datetime import datetime
import json
import sys


# Add parent directory to path to import from utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "utils"))


def generate_facebook_content(topic: str, tone: str = "professional") -> dict:
    """
    Generate Facebook-optimized content.

    Args:
        topic: Topic or key message
        tone: Tone of voice (professional, casual, excited)

    Returns:
        Dictionary with content, hashtags, and metadata
    """
    # Content templates based on tone
    templates = {
        "professional": {
            "emoji": "🚀",
            "opening": "We're excited to share",
            "closing": "Learn more in the link below.",
            "cta": "Let us know your thoughts in the comments!"
        },
        "casual": {
            "emoji": "✨",
            "opening": "Guess what?",
            "closing": "Check it out!",
            "cta": "What do you think? 👇"
        },
        "excited": {
            "emoji": "🎉",
            "opening": "BIG NEWS!",
            "closing": "This is huge!",
            "cta": "Who's excited? Drop a 🔥 below!"
        }
    }

    template = templates.get(tone, templates["professional"])

    # Hashtag suggestions based on common topics
    hashtag_suggestions = {
        "product": ["#ProductLaunch", "#NewFeatures", "#Innovation", "#ProductUpdate"],
        "company": ["#CompanyNews", "#BehindTheScenes", "#TeamWork", "#Business"],
        "tips": ["#ProTips", "#HowTo", "#BusinessTips", "#ExpertAdvice"],
        "event": ["#Event", "#JoinUs", "#MarkYourCalendar", "#DontMissOut"],
        "general": ["#Growth", "#Success", "#Business", "#Entrepreneurship"]
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
    else:
        category = "general"

    hashtags = hashtag_suggestions.get(category, hashtag_suggestions["general"])

    # Generate content
    content = f"""{template['emoji']} {template['opening']}...

{topic}

{template['closing']}

👉 [Link to website/blog post]

{template['cta']}

{' '.join(hashtags[:5])}"""

    return {
        "content": content,
        "hashtags": hashtags,
        "category": category,
        "tone": tone,
        "platform": "Facebook",
        "suggested_media": "Image or link preview will be auto-generated"
    }


def create_approval_file(vault_path: str, topic: str, tone: str = "professional") -> Path:
    """
    Create an approval file in /Pending_Approval/.

    Args:
        vault_path: Path to Obsidian vault
        topic: Topic or key message
        tone: Tone of voice

    Returns:
        Path to created approval file
    """
    vault = Path(vault_path)
    pending_folder = vault / "Pending_Approval"
    pending_folder.mkdir(parents=True, exist_ok=True)

    # Generate content
    content_data = generate_facebook_content(topic, tone)

    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"FACEBOOK_POST_{timestamp}.md"
    filepath = pending_folder / filename

    # Create approval file content
    approval_content = f"""---
type: meta_post
platforms: [Facebook]
priority: medium
created: {datetime.now().isoformat()}
status: pending
tone: {tone}
category: {content_data['category']}
---

# Facebook Post: {topic}

## Content Preview
{content_data['content'][:150]}...

## Full Content
```
{content_data['content']}
```

## Platform Details
- **Platform:** Facebook
- **Tone:** {tone}
- **Length:** {len(content_data['content'])} characters
- **Optimal Length:** 100-300 characters ✅

## Hashtags
{chr(10).join(f"- {tag}" for tag in content_data['hashtags'][:5])}

## Suggested Media
{content_data['suggested_media']}

## Best Posting Time
- **Day:** Tuesday, Wednesday, Thursday
- **Time:** 9:00 AM - 3:00 PM
- **Reason:** Highest engagement during business hours

## Approval Required
Please review the content above.

**To Approve:** Move this file to `/Approved/`
**To Edit:** Edit this file, then move to `/Approved/`
**To Reject:** Move this file to `/Rejected/`

## Checklist Before Publishing
- [ ] Content is on-brand and accurate
- [ ] Link is correct and working
- [ ] Spelling and grammar checked
- [ ] Hashtags are relevant
- [ ] Call-to-action is clear

---

*Generated by Facebook & Instagram Manager Skill*
*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

    # Write file
    filepath.write_text(approval_content, encoding='utf-8')
    return filepath


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Facebook-optimized content"
    )

    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--topic",
        required=True,
        help="Topic or key message for the post"
    )

    parser.add_argument(
        "--tone",
        choices=["professional", "casual", "excited"],
        default="professional",
        help="Tone of voice (default: professional)"
    )

    parser.add_argument(
        "--output",
        help="Output folder (default: vault/Pending_Approval/)"
    )

    args = parser.parse_args()

    # Generate content
    print("\n" + "="*60)
    print("FACEBOOK CONTENT GENERATOR")
    print("="*60)
    print(f"\nTopic: {args.topic}")
    print(f"Tone: {args.tone}")

    filepath = create_approval_file(args.vault, args.topic, args.tone)

    print(f"\n✅ Created approval file:")
    print(f"   {filepath}")
    print(f"\n📋 Next steps:")
    print(f"   1. Review the content in {filepath}")
    print(f"   2. Make edits if needed")
    print(f"   3. Move to /Approved/ to publish")
    print(f"\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
