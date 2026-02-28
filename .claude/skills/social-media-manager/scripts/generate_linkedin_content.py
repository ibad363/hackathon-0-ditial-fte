#!/usr/bin/env python3
"""
LinkedIn Content Generator

Generates business-focused LinkedIn content and creates approval requests.
This is part of the social-media-manager agent skill.

Usage:
    python generate_linkedin_content.py --vault . --topic automation
    python generate_linkedin_content.py --vault . --random
"""

import sys
import json
import random
import argparse
from pathlib import Path
from datetime import datetime


# Business-focused content templates
CONTENT_TEMPLATES = {
    "insight": [
        {
            "template": "Just discovered something powerful about {topic}: {insight}. The key insight? {takeaway}. #Automation #Productivity",
            "insights": [
                "automating repetitive tasks frees up mental bandwidth for strategic thinking",
                "the best systems are the ones you don't have to think about",
                "consistency beats intensity every single time",
                "measuring what matters is half the battle",
                "the right tool at the right time changes everything"
            ],
            "takeaways": [
                "Start small, automate one task this week",
                "Build systems that scale without your direct involvement",
                "Focus on the 20% of work that drives 80% of results",
                "Track your metrics before you try to improve them",
                "Choose tools that integrate with your existing workflow"
            ]
        },
        {
            "template": "Hot take: {hot_take}. {elaboration}. {question} #BusinessInsights",
            "hot_takes": [
                "Most businesses overcomplicate their tech stack",
                "The best automation feels invisible",
                "Your time is worth more than you think",
                "Manual processes are silently killing your productivity",
                "The future of work is already here"
            ],
            "elaborations": [
                "More tools ≠ more productivity. Integration is key",
                "When it works seamlessly, you forget it's even there",
                "Calculate your hourly rate and delegate everything below it",
                "Every manual step is an opportunity for automation",
                "Those adapting to AI and automation are already winning"
            ],
            "questions": [
                "What's one process you should automate this month?",
                "Where are you losing time to manual work?",
                "What would you do with an extra 10 hours per week?",
                "Which repetitive task can you eliminate today?",
                "Are you building systems or just fighting fires?"
            ]
        }
    ],

    "achievement": [
        {
            "template": "🎯 {achievement}\n\n{details}\n\n{reflection}\n\n#Milestone #Growth #Entrepreneurship",
            "achievements": [
                "Just hit a major milestone!",
                "Excited to share some progress",
                "This week's win",
                "Breaking through barriers",
                "Celebrating the small wins"
            ],
            "details": [
                "Completed a project that's been months in the making. The journey taught me that persistence matters more than perfection.",
                "Automated a workflow that was consuming hours every week. Already seeing the impact on productivity.",
                "Landed a new client who found value in our services. Validation that we're solving real problems.",
                "Solved a technical challenge that had been blocking progress. Sometimes you just need to step back and rethink.",
                "Launched a new service offering. The market response has been incredibly encouraging."
            ],
            "reflections": [
                "The key? Showing up every day, even when progress felt slow.",
                "Lesson learned: The best time to automate was yesterday. The second best time is now.",
                "Grateful for the trust clients place in us. We deliver results.",
                "Technical skills are important. Problem-solving mindset is everything.",
                "Innovation isn't just about ideas. It's about execution."
            ]
        }
    ],

    "educational": [
        {
            "template": "📚 {topic} 101:\n\n{point_1}\n{point_2}\n{point_3}\n\n{cta}\n\n#Tips #Learning #Knowledge",
            "topics": [
                "Business Automation",
                "Productivity Hacks",
                "Scaling Your Business",
                "Digital Transformation",
                "Smart Workflows"
            ],
            "points": [
                [
                    "Start by auditing your current processes - you can't improve what you don't measure",
                    "Identify repetitive tasks that don't require human judgment",
                    "Implement and iterate - perfect is the enemy of good"
                ],
                [
                    "Time-block your most important work first thing in the morning",
                    "Batch similar tasks together to maintain focus",
                    "Use tools that work for you, not against you"
                ],
                [
                    "Document your processes before you scale them",
                    "Hire for attitude, train for skill",
                    "Build systems that can run without you"
                ],
                [
                    "Assess your current tech stack and eliminate redundancies",
                    "Choose tools that integrate with each other",
                    "Train your team properly on new systems"
                ],
                [
                    "Map out your entire workflow from start to finish",
                    "Identify bottlenecks and friction points",
                    "Use automation to smooth out the rough edges"
                ]
            ],
            "ctas": [
                "What's your best productivity tip? Share in the comments!",
                "Which of these resonates most with you?",
                "What would you add to this list?",
                "How are you implementing these in your work?",
                "Drop a 👍 if this was helpful!"
            ]
        }
    ],

    "promotion": [
        {
            "template": "{headline}\n\n{problem}\n\n{solution}\n\n{result}\n\n{cta}\n\n#Services #BusinessGrowth",
            "headlines": [
                "Struggling to keep up with your business operations?",
                "Feeling overwhelmed by manual processes?",
                "Your time is too valuable for repetitive tasks",
                "Ready to scale your business without burnout?",
                "The bottleneck in your business might be manual workflows"
            ],
            "problems": [
                "You're wearing too many hats and can't focus on growth",
                "Administrative tasks are eating up your productive hours",
                "Your business is growing but your systems haven't kept up",
                "You're working IN your business instead of ON your business",
                "Important tasks are falling through the cracks"
            ],
            "solutions": [
                "Automated workflows that handle the repetitive work for you",
                "Smart systems that scale with your business needs",
                "Custom solutions designed for your specific challenges",
                "Technology that works while you sleep",
                "Streamlined processes that free up your time"
            ],
            "results": [
                "Our clients typically save 10+ hours per week",
                "Proven results across multiple industries",
                "Scalable solutions that grow with you",
                "Focus on what you do best - we'll handle the rest",
                "Transform your operations in 30 days or less"
            ],
            "ctas": [
                "DM me 'AUTOMATE' to learn how we can help",
                "Ready to reclaim your time? Let's talk",
                "Comment 'INTERESTED' below and I'll reach out",
                "Link in bio to schedule a free consultation",
                "What's holding you back from automating?"
            ]
        }
    ],

    "story": [
        {
            "template": "{hook}\n\n{story}\n\n{lesson}\n\n{engagement}\n\n#StoryTime #Business #Entrepreneurship",
            "hooks": [
                "I almost gave up on automation...",
                "Here's something I learned the hard way",
                "A client told me something that changed my perspective",
                "The moment everything clicked",
                "I used to think that... until I realized"
            ],
            "stories": [
                "I tried to automate everything at once. Failed miserably. Then I started small - one process at a time. Now I have systems that run 24/7. The lesson? Progress over perfection.",
                "Thought I needed expensive tools to be productive. Turns out, simple workflows beat complex systems every time. Focus on what actually moves the needle.",
                "They said automation would make things impersonal. Instead, it freed up time for genuine human connections with clients. The irony?",
                "Spent months building the 'perfect' system. It was too complicated. Threw it out, started simple. That simple version? Still running today.",
                "Tried to convince clients to automate. Showed them results instead. Words are good. Proof is better. Now they come to me."
            ],
            "lessons": [
                "Build in public, fail fast, iterate faster",
                "Complexity isn't a feature - it's often a bug",
                "The goal isn't less work - it's more impact",
                "Sometimes the old ways are the best ways",
                "Results speak louder than any sales pitch"
            ],
            "engagements": [
                "What's a lesson you learned the hard way?",
                "Ever had a moment that changed your perspective?",
                "Who else has been there?",
                "What would you do differently?",
                "Drop your story in the comments 👇"
            ]
        }
    ]
}

# Topic-specific content
TOPIC_CONTENT = {
    "automation": {
        "hashtags": "#Automation #Productivity #BusinessAutomation #WorkSmarter",
        "themes": ["insight", "educational", "story"]
    },
    "productivity": {
        "hashtags": "#Productivity #TimeManagement #Efficiency #GrowthMindset",
        "themes": ["insight", "educational", "achievement"]
    },
    "business": {
        "hashtags": "#Business #Entrepreneurship #SmallBusiness #Growth",
        "themes": ["insight", "promotion", "story"]
    },
    "technology": {
        "hashtags": "#Tech #Innovation #DigitalTransformation #FutureOfWork",
        "themes": ["insight", "educational", "story"]
    },
    "leadership": {
        "hashtags": "#Leadership #Management #TeamBuilding #Culture",
        "themes": ["insight", "story", "achievement"]
    }
}


def generate_content(topic: str = None, content_type: str = None) -> str:
    """
    Generate LinkedIn content based on topic and type.

    Args:
        topic: Topic area (automation, productivity, business, technology, leadership)
        content_type: Type of content (insight, achievement, educational, promotion, story)

    Returns:
        Generated content string
    """
    # Select topic if not specified
    if not topic:
        topic = random.choice(list(TOPIC_CONTENT.keys()))
    elif topic not in TOPIC_CONTENT:
        topic = random.choice(list(TOPIC_CONTENT.keys()))

    topic_config = TOPIC_CONTENT[topic]

    # Select content type if not specified
    if not content_type:
        content_type = random.choice(topic_config["themes"])
    elif content_type not in CONTENT_TEMPLATES:
        content_type = random.choice(topic_config["themes"])

    # Get template for this content type
    template_group = random.choice(CONTENT_TEMPLATES[content_type])
    template = template_group["template"]

    # Fill in template
    content = template.format(**_get_template_fillers(template_group, topic))

    # Add topic-specific hashtags if not already present
    if topic_config["hashtags"] not in content:
        content += f"\n\n{topic_config['hashtags']}"

    return content


def _get_template_fillers(template_group: dict, topic: str) -> dict:
    """Get filler values for template placeholders."""
    import re

    fillers = {}

    # Get template string
    template = template_group.get("template", "")

    # Extract all placeholder names from template
    placeholders = re.findall(r'\{(\w+)\}', template)

    # Fill each placeholder from template_group data
    for placeholder in placeholders:
        # Direct match first
        if placeholder in template_group:
            if isinstance(template_group[placeholder], list):
                if placeholder == "points":
                    # Special handling for points array
                    selected_points = random.choice(template_group[placeholder])
                    fillers["point_1"] = f"• {selected_points[0]}"
                    fillers["point_2"] = f"• {selected_points[1]}"
                    fillers["point_3"] = f"• {selected_points[2]}"
                else:
                    fillers[placeholder] = random.choice(template_group[placeholder])
            else:
                fillers[placeholder] = template_group[placeholder]
            continue

        # Try singular/plural variations
        plural_key = placeholder + "s"
        if plural_key in template_group:
            if isinstance(template_group[plural_key], list):
                fillers[placeholder] = random.choice(template_group[plural_key])
            else:
                fillers[placeholder] = template_group[plural_key]
            continue

    # Add topic if needed
    if "topic" in placeholders and "topic" not in fillers:
        fillers["topic"] = topic.replace("_", " ").title()

    # Add defaults for any remaining placeholders
    defaults = {
        "headline": "💡 Business Insight",
        "problem": "Many businesses struggle with inefficiency",
        "solution": "Automation and smart workflows can help",
        "result": "Save time and scale operations",
        "cta": "DM me to learn how",
        "hook": "Here's something I learned recently",
        "story": "Building systems takes time but pays off",
        "lesson": "Consistency beats intensity",
        "engagement": "What's your experience?",
        "hot_take": "Most businesses overcomplicate their tech stack",
        "elaboration": "More tools ≠ more productivity. Integration is key",
        "question": "What's one process you should automate this month?",
        "achievement": "Just hit a major milestone!",
        "details": "Completed a challenging project successfully",
        "reflection": "Persistence matters more than perfection",
        "insight": "automating repetitive tasks frees up mental bandwidth",
        "takeaway": "Start small, automate one task this week",
        "point_1": "• Start by auditing your current processes",
        "point_2": "• Identify repetitive tasks that don't require judgment",
        "point_3": "• Implement and iterate - perfect is the enemy of good",
    }

    for placeholder in placeholders:
        if placeholder not in fillers and placeholder in defaults:
            fillers[placeholder] = defaults[placeholder]

    return fillers


def create_approval_request(content: str, vault_path: str) -> Path:
    """
    Create an approval request file for LinkedIn post.

    Args:
        content: The post content
        vault_path: Path to vault

    Returns:
        Path to approval request file
    """
    vault = Path(vault_path)
    pending_folder = vault / "Pending_Approval"
    pending_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"LINKEDIN_POST_{timestamp}.md"
    filepath = pending_folder / filename

    approval_content = f"""---
type: linkedin_post
source: social_media_manager
priority: medium
status: pending
created: {datetime.now().isoformat()}
expires: {datetime.now().replace(hour=23, minute=59, second=59).isoformat()}
---

# LinkedIn Post Approval Request

## Post Content

```
{content}
```

## Metadata

- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Platform:** LinkedIn
- **Character Count:** {len(content)}
- **Hashtags:** {len([w for w in content.split() if w.startswith('#')])} tags

## To Approve

1. Review the post content above
2. Edit this file if you want to make changes
3. Move this file to `/Approved/` folder to post

## To Reject

1. Add your reasoning below
2. Move this file to `/Rejected/` folder

---

*Generated by Social Media Manager - v1.0*
"""

    filepath.write_text(approval_content, encoding='utf-8')
    print(f"[OK] Created approval request: {filepath}")
    return filepath


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate LinkedIn content and create approval request"
    )

    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--topic",
        choices=list(TOPIC_CONTENT.keys()) + ["random"],
        help="Content topic area"
    )

    parser.add_argument(
        "--type",
        choices=["insight", "achievement", "educational", "promotion", "story", "random"],
        help="Content type"
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview content without creating approval file"
    )

    parser.add_argument(
        "--bulk",
        type=int,
        help="Generate N posts at once"
    )

    args = parser.parse_args()

    if args.topic == "random":
        args.topic = None

    if args.type == "random":
        args.type = None

    if args.bulk:
        # Bulk generate posts
        print(f"Generating {args.bulk} LinkedIn posts...")
        for i in range(args.bulk):
            content = generate_content(args.topic, args.type)
            filepath = create_approval_request(content, args.vault)
            print(f"[{i+1}/{args.bulk}] {filepath.name}")
        print(f"\n[OK] Generated {args.bulk} posts in /Pending_Approval/")
    else:
        # Single post
        content = generate_content(args.topic, args.type)

        if args.preview:
            print("=" * 60)
            print("LINKEDIN POST PREVIEW")
            print("=" * 60)
            print(content)
            print("=" * 60)
            print(f"\nCharacter Count: {len(content)}")
        else:
            filepath = create_approval_request(content, args.vault)
            print(f"\n[INFO] Review the post in: {filepath}")
            print(f"[INFO] Move to /Approved/ to publish")


if __name__ == "__main__":
    main()
