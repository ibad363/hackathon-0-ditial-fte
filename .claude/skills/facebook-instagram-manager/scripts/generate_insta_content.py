#!/usr/bin/env python3
"""
Generate Instagram Content

Generates Instagram-optimized content for a given topic and creates
an approval file in /Pending_Approval/.

Usage:
    python generate_insta_content.py --vault . --topic "Behind the scenes"
"""

import argparse
from pathlib import Path
from datetime import datetime
import sys


def generate_instagram_content(topic: str, tone: str = "engaging") -> dict:
    """
    Generate Instagram-optimized content.

    Args:
        topic: Topic or key message
        tone: Tone of voice (engaging, inspirational, fun)

    Returns:
        Dictionary with content, hashtags, and metadata
    """
    # Content templates based on tone
    templates = {
        "engaging": {
            "emojis": ["✨", "🚀", "💡"],
            "opening": "New post alert!",
            "closing": "Link in bio to learn more! 🔗",
        },
        "inspirational": {
            "emojis": ["💪", "🌟", "🎯"],
            "opening": "Dream big, work hard:",
            "closing": "What's your goal? Share below! 👇",
        },
        "fun": {
            "emojis": ["😄", "🎉", "🔥"],
            "opening": "Guess what?!",
            "closing": "Tap the link in our bio for more! 📱",
        }
    }

    template = templates.get(tone, templates["engaging"])

    # Instagram hashtags (more than Facebook, mix of popular + niche)
    hashtag_sets = {
        "product": [
            "#ProductLaunch", "#NewFeatures", "#Innovation", "#ProductUpdate",
            "#TechNews", "#StartupLife", "#NewDrop", "#MustHave", "#TechTrends",
            "#InnovationLab", "#Productivity", "#TechTools", "#Startup",
            "#Entrepreneur", "#BusinessTools", "#LifeHacks"
        ],
        "company": [
            "#CompanyNews", "#BehindTheScenes", "#TeamWork", "#Business",
            "#OfficeLife", "#TeamCulture", "#CompanyCulture", "#WorkLife",
            "#DreamTeam", "#WorkGoals", "#SmallBusiness", "#BizLife",
            "#OfficeVibes", "#TeamBonding", "#CompanyGrowth"
        ],
        "tips": [
            "#ProTips", "#HowTo", "#BusinessTips", "#ExpertAdvice",
            "#LifeHacks", "#TipsAndTricks", "#ProductivityTips", "#SuccessTips",
            "#DailyTips", "#LearnSomethingNew", "#KnowledgeIsPower",
            "#Expertise", "#GrowthMindset", "#SelfImprovement"
        ],
        "general": [
            "#Growth", "#Success", "#Business", "#Entrepreneurship",
            "#Motivation", "#Inspiration", "#Goals", "#Grind",
            "#Hustle", "#Mindset", "#Vision", "#Ambition",
            "#BusinessOwner", "#Founder", "#CEO", "#Leadership"
        ]
    }

    # Detect topic category
    topic_lower = topic.lower()
    if any(word in topic_lower for word in ["launch", "product", "feature", "update"]):
        category = "product"
    elif any(word in topic_lower for word in ["team", "company", "news", "announcement"]):
        category = "company"
    elif any(word in topic_lower for word in ["tip", "guide", "how", "tutorial"]):
        category = "tips"
    else:
        category = "general"

    hashtags = hashtag_sets.get(category, hashtag_sets["general"])

    # Select emojis
    import random
    selected_emojis = random.sample(template["emojis"], 2)

    # Generate content (shorter, punchier than Facebook)
    content = f"""{selected_emojis[0]} {template['opening']}

{topic}

{template['closing']}

.
.
.
{' '.join(hashtags[:15])}"""

    return {
        "content": content,
        "hashtags": hashtags,
        "category": category,
        "tone": tone,
        "platform": "Instagram",
        "suggested_media": "High-quality image or video required"
    }


def create_approval_file(vault_path: str, topic: str, tone: str = "engaging",
                       image_path: str = None) -> Path:
    """
    Create an approval file in /Pending_Approval/.

    Args:
        vault_path: Path to Obsidian vault
        topic: Topic or key message
        tone: Tone of voice
        image_path: Optional path to image/video

    Returns:
        Path to created approval file
    """
    vault = Path(vault_path)
    pending_folder = vault / "Pending_Approval"
    pending_folder.mkdir(parents=True, exist_ok=True)

    # Generate content
    content_data = generate_instagram_content(topic, tone)

    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"INSTAGRAM_POST_{timestamp}.md"
    filepath = pending_folder / filename

    # Create approval file content
    approval_content = f"""---
type: meta_post
platforms: [Instagram]
priority: medium
created: {datetime.now().isoformat()}
status: pending
tone: {tone}
category: {content_data['category']}
image: {image_path or 'TBD'}
---

# Instagram Post: {topic}

## Content Preview
{content_data['content'][:150]}...

## Full Content
```
{content_data['content']}
```

## Platform Details
- **Platform:** Instagram
- **Tone:** {tone}
- **Length:** {len(content_data['content'])} characters
- **Optimal Length:** 50-150 characters ✅

## Image/Video Required
{"✅ Image specified: " + image_path if image_path else "⚠️  Please attach image before publishing"}

**Best practices:**
- High-resolution (1080x1080 or 1080x1350)
- Good lighting
- On-brand visuals
- Minimal text overlay

## Hashtags ({len(content_data['hashtags'])} suggested)
{chr(10).join(f"- {tag}" for tag in content_data['hashtags'][:10])}
... and {len(content_data['hashtags']) - 10} more

## Best Posting Time
- **Day:** Tuesday, Wednesday, Thursday
- **Time:** 11:00 AM - 1:00 PM or 7:00 PM - 9:00 PM
- **Reason:** Peak engagement times

## Stories Integration
Consider creating 3-5 Instagram Stories to accompany this post:
- [ ] Teaser story (2 hours before)
- [ ] Post announcement story
- [ ] Behind-the-scenes story
- [ ] Poll/question sticker story
- [ ] Link sticker to website

## Approval Required
Please review the content above.

**To Approve:** Move this file to `/Approved/`
**To Edit:** Edit this file, then move to `/Approved/`
**To Reject:** Move this file to `/Rejected/`

## Checklist Before Publishing
- [ ] Content is on-brand and accurate
- [ ] Image/video is high quality
- [ ] Hashtags are relevant (10-30 recommended)
- [ ] First line is attention-grabbing
- [ ] Call-to-action is clear
- [ ] Link in bio is updated (if applicable)

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
        description="Generate Instagram-optimized content"
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
        choices=["engaging", "inspirational", "fun"],
        default="engaging",
        help="Tone of voice (default: engaging)"
    )

    parser.add_argument(
        "--image",
        help="Path to image/video file"
    )

    parser.add_argument(
        "--output",
        help="Output folder (default: vault/Pending_Approval/)"
    )

    args = parser.parse_args()

    # Generate content
    print("\n" + "="*60)
    print("INSTAGRAM CONTENT GENERATOR")
    print("="*60)
    print(f"\nTopic: {args.topic}")
    print(f"Tone: {args.tone}")
    if args.image:
        print(f"Image: {args.image}")

    filepath = create_approval_file(args.vault, args.topic, args.tone, args.image)

    print(f"\n✅ Created approval file:")
    print(f"   {filepath}")
    print(f"\n📋 Next steps:")
    print(f"   1. Review the content in {filepath}")
    print(f"   2. Attach image if not specified")
    print(f"   3. Make edits if needed")
    print(f"   4. Move to /Approved/ to publish")
    print(f"\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
