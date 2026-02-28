#!/usr/bin/env python3
"""
LinkedIn Content Calendar Generator

Generates a batch of LinkedIn content for approval.
Designed to be run periodically (e.g., weekly) to create a content queue.

Usage:
    python generate_content_calendar.py --vault . --count 5
    python generate_content_calendar.py --vault . --schedule weekly
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding issue
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path to import generate_linkedin_content
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Import the content generator
import importlib.util
spec = importlib.util.spec_from_file_location(
    "generate_linkedin_content",
    Path(__file__).parent.parent.parent.parent.parent / ".claude" / "skills" / "social-media-manager" / "scripts" / "generate_linkedin_content.py"
)
linkedin_gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(linkedin_gen)


# Content mix strategy
CONTENT_MIX = {
    "weekly": {
        "total": 5,
        "distribution": {
            "insight": 2,      # 2 insight posts
            "educational": 1,  # 1 educational post
            "story": 1,        # 1 story post
            "promotion": 1     # 1 promotional post
        },
        "topics": ["automation", "productivity", "business", "technology"]
    }
}


def generate_content_batch(vault_path: str, schedule: str = "weekly", count: int = None) -> int:
    """
    Generate a batch of LinkedIn content based on schedule strategy.

    Args:
        vault_path: Path to vault
        schedule: Schedule type (weekly, monthly)
        count: Override count (optional)

    Returns:
        Number of posts generated
    """
    vault = Path(vault_path)

    # Get strategy
    if schedule not in CONTENT_MIX:
        print(f"[WARNING] Unknown schedule '{schedule}', using 'weekly'")
        schedule = "weekly"

    strategy = CONTENT_MIX[schedule]
    total_posts = count or strategy["total"]
    distribution = strategy["distribution"]
    topics = strategy["topics"]

    print(f"\n{'='*60}")
    print(f"LinkedIn Content Calendar Generator")
    print(f"{'='*60}")
    print(f"Schedule: {schedule}")
    print(f"Posts to generate: {total_posts}")
    print(f"Topics: {', '.join(topics)}")
    print(f"{'='*60}\n")

    generated = 0
    topic_index = 0

    # Generate content based on distribution
    for content_type, quantity in distribution.items():
        for i in range(quantity):
            if generated >= total_posts:
                break

            topic = topics[topic_index % len(topics)]

            print(f"[{generated+1}/{total_posts}] Generating {content_type} post about {topic}...")

            content = linkedin_gen.generate_content(topic=topic, content_type=content_type)
            filepath = linkedin_gen.create_approval_request(content, vault_path)

            print(f"     -> Created: {filepath.name}\n")
            generated += 1
            topic_index += 1

    # Generate any remaining posts with random types
    while generated < total_posts:
        topic = topics[generated % len(topics)]

        print(f"[{generated+1}/{total_posts}] Generating random post about {topic}...")

        content = linkedin_gen.generate_content(topic=topic, content_type=None)
        filepath = linkedin_gen.create_approval_request(content, vault_path)

        print(f"     -> Created: {filepath.name}\n")
        generated += 1

    print(f"{'='*60}")
    print(f"[OK] Generated {generated} LinkedIn posts in /Pending_Approval/")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"1. Review the posts in /Pending_Approval/")
    print(f"2. Edit as needed")
    print(f"3. Move approved posts to /Approved/")
    print(f"4. The approval monitor will automatically publish them")
    print(f"\n")

    # Create summary file
    create_summary(vault_path, generated, schedule)

    return generated


def create_summary(vault_path: str, count: int, schedule: str):
    """Create a summary of the generated content batch."""
    vault = Path(vault_path)
    pending_folder = vault / "Pending_Approval"

    summary_path = pending_folder / f"CONTENT_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    # Get all LinkedIn post files
    linkedin_files = sorted(pending_folder.glob("LINKEDIN_POST_*.md"))

    summary_content = f"""---
type: content_summary
generated: {datetime.now().isoformat()}
schedule: {schedule}
---

# LinkedIn Content Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Schedule:** {schedule}
**Total Posts:** {count}

## Posts Awaiting Approval

"""

    for i, filepath in enumerate(linkedin_files[-count:], 1):
        summary_content += f"{i}. **{filepath.name}**\n"

    summary_content += f"""

## Approval Process

1. Review each post in /Pending_Approval/
2. Edit the content if needed
3. Move to /Approved/ to schedule for publishing
4. Posts will be automatically published by the approval monitor

## Content Mix

- **Insight posts:** Share thoughts and perspectives
- **Educational posts:** Teach valuable lessons
- **Story posts:** Build connection through storytelling
- **Promotional posts:** Highlight services and offerings

---

*Generated by LinkedIn Content Calendar Generator*
"""

    summary_path.write_text(summary_content, encoding='utf-8')
    print(f"[OK] Created summary: {summary_path.name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate LinkedIn content calendar"
    )

    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--schedule",
        choices=["weekly", "monthly"],
        default="weekly",
        help="Content schedule type"
    )

    parser.add_argument(
        "--count",
        type=int,
        help="Number of posts to generate (overrides schedule default)"
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview strategy without generating"
    )

    args = parser.parse_args()

    if args.preview:
        # Show what would be generated
        strategy = CONTENT_MIX[args.schedule]
        print(f"\nStrategy: {args.schedule}")
        print(f"Total posts: {strategy['total']}")
        print(f"\nDistribution:")
        for content_type, quantity in strategy['distribution'].items():
            print(f"  - {content_type}: {quantity}")
        print(f"\nTopics: {', '.join(strategy['topics'])}")
        return

    # Generate content
    count = generate_content_batch(
        vault_path=args.vault,
        schedule=args.schedule,
        count=args.count
    )

    return 0 if count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
