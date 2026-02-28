#!/usr/bin/env python3
"""
Daily Review Utility Script

Generates a prioritized daily plan by reviewing all action items,
calendar events, and pending approvals.

Usage:
    python generate_daily_plan.py [--vault PATH]
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class DailyReviewGenerator:
    """Generate daily review plans from vault content."""

    # Priority icons (ASCII-safe for Windows console)
    ICON_CRITICAL = "[!]"
    ICON_HIGH = "[^]"
    ICON_MEDIUM = "[-]"
    ICON_LOW = "[o]"

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.plans_path = self.vault_path / "Plans"
        self.done_path = self.vault_path / "Done"
        self.company_handbook_path = self.vault_path / "Company_Handbook.md"

        # Ensure Plans folder exists
        self.plans_path.mkdir(parents=True, exist_ok=True)

    def extract_priority_from_file(self, filepath: Path) -> tuple:
        """
        Extract priority from file frontmatter.

        Returns:
            tuple: (priority_level, icon, category)
        """
        content = filepath.read_text(encoding="utf-8", errors="ignore")

        # Check frontmatter for priority
        priority_match = re.search(r'priority:\s*(\w+)', content, re.IGNORECASE)
        if priority_match:
            priority = priority_match.group(1).lower()
        else:
            # Check for keywords in content
            content_lower = content.lower()
            if any(kw in content_lower for kw in ["urgent", "asap", "emergency"]):
                priority = "critical"
            elif any(kw in content_lower for kw in ["high", "important", "deadline"]):
                priority = "high"
            elif any(kw in content_lower for kw in ["medium", "normal"]):
                priority = "medium"
            else:
                priority = "low"

        # Map to icon
        icon_map = {
            "critical": self.ICON_CRITICAL,
            "high": self.ICON_HIGH,
            "medium": self.ICON_MEDIUM,
            "low": self.ICON_LOW,
        }

        return priority, icon_map.get(priority, self.ICON_LOW), self._categorize_file(filepath, content)

    def _categorize_file(self, filepath: Path, content: str) -> str:
        """Categorize file by type."""
        name_lower = filepath.name.lower()

        if "email" in name_lower:
            return "Email"
        elif "event" in name_lower or "calendar" in name_lower:
            return "Event"
        elif "payment" in name_lower or "invoice" in name_lower:
            return "Financial"
        elif "task" in name_lower:
            return "Task"
        else:
            return "Item"

    def get_items_from_folder(self, folder: Path) -> list:
        """Get all items from a folder with their priorities."""
        items = []

        if not folder.exists():
            return items

        for filepath in folder.glob("*.md"):
            try:
                priority, icon, category = self.extract_priority_from_file(filepath)
                items.append({
                    "filepath": filepath,
                    "filename": filepath.name,
                    "priority": priority,
                    "icon": icon,
                    "category": category,
                })
            except Exception as e:
                logger.warning(f"Error reading {filepath.name}: {e}")

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        items.sort(key=lambda x: priority_order.get(x["priority"], 4))

        return items

    def parse_calendar_events(self) -> list:
        """Parse calendar events from Needs_Action folder."""
        events = []

        for filepath in self.needs_action_path.glob("EVENT_*.md"):
            try:
                content = filepath.read_text(encoding="utf-8")
                # Extract event details
                title_match = re.search(r'# Event: (.+)', content)
                time_match = re.search(r'\*\*When:\*\*\s*(.+)', content)
                location_match = re.search(r'\*\*Where:\*\*\s*(.+)', content)

                events.append({
                    "title": title_match.group(1) if title_match else filepath.stem,
                    "time": time_match.group(1) if time_match else "TBD",
                    "location": location_match.group(1) if location_match else "TBD",
                    "filename": filepath.name,
                })
            except Exception as e:
                logger.warning(f"Error parsing event {filepath.name}: {e}")

        return events

    def generate_plan(self) -> str:
        """Generate the daily plan content."""
        today = datetime.now().strftime("%Y-%m-%d")

        # Collect items
        needs_action_items = self.get_items_from_folder(self.needs_action_path)
        pending_items = self.get_items_from_folder(self.pending_approval_path)
        calendar_events = self.parse_calendar_events()

        # Count items by priority
        urgent_count = sum(1 for i in needs_action_items if i["priority"] == "critical")
        high_count = sum(1 for i in needs_action_items if i["priority"] == "high")

        # Build the plan
        plan = f"""---
date: {today}
created: {datetime.now().isoformat()}
total_items: {len(needs_action_items) + len(pending_items)}
urgent_count: {urgent_count}
high_priority_count: {high_count}
---

# Daily Plan - {today}

## {self.ICON_CRITICAL} Critical (Do Now)
"""

        # Critical items
        critical_items = [i for i in needs_action_items if i["priority"] == "critical"]
        if critical_items:
            for item in critical_items:
                plan += f"- [ ] [{item['category']}] {item['filename']}\n"
        else:
            plan += "- [ ] None\n"

        plan += f"\n## {self.ICON_HIGH} High Priority (Today)\n"

        # High priority items
        high_items = [i for i in needs_action_items if i["priority"] == "high"]
        if high_items:
            for item in high_items:
                plan += f"- [ ] [{item['category']}] {item['filename']}\n"
        else:
            plan += "- [ ] None\n"

        plan += f"\n## {self.ICON_MEDIUM} Medium Priority (This Week)\n"

        # Medium priority items
        medium_items = [i for i in needs_action_items if i["priority"] == "medium"]
        if medium_items:
            for item in medium_items:
                plan += f"- [ ] [{item['category']}] {item['filename']}\n"
        else:
            plan += "- [ ] None\n"

        plan += f"\n## {self.ICON_LOW} Low Priority (Backlog)\n"

        # Low priority items
        low_items = [i for i in needs_action_items if i["priority"] == "low"]
        if low_items:
            for item in low_items[:5]:  # Limit to 5
                plan += f"- [ ] [{item['category']}] {item['filename']}\n"
        else:
            plan += "- [ ] None\n"

        # Calendar events
        if calendar_events:
            plan += "\n## Calendar Today\n"
            plan += "| Time | Event | Location |\n"
            plan += "|------|-------|----------|\n"
            for event in calendar_events:
                plan += f"| {event['time']} | {event['title']} | {event['location']} |\n"

        # Pending approvals
        if pending_items:
            plan += "\n## Pending Approvals\n"
            plan += "| Item | Priority | Action |\n"
            plan += "|------|----------|--------|\n"
            for item in pending_items:
                plan += f"| {item['filename'][:30]} | {item['icon']} {item['priority']} | Review |\n"

        # Notes section
        plan += "\n## Notes\n"
        plan += "\n---\n"
        plan += f"\n*Generated by Personal AI Employee on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"

        return plan

    def save_plan(self) -> Path:
        """Generate and save the daily plan."""
        today = datetime.now().strftime("%Y-%m-%d")
        plan_content = self.generate_plan()
        plan_path = self.plans_path / f"daily_{today}.md"

        plan_path.write_text(plan_content, encoding="utf-8")
        logger.info(f"Daily plan saved to {plan_path}")

        return plan_path

    def print_summary(self) -> None:
        """Print a summary of today's items."""
        needs_action_items = self.get_items_from_folder(self.needs_action_path)
        pending_items = self.get_items_from_folder(self.pending_approval_path)

        print(f"\n{'='*60}")
        print(f"Daily Review - {datetime.now().strftime('%Y-%m-%d')}")
        print(f"{'='*60}")

        print(f"\nItems in Needs_Action: {len(needs_action_items)}")
        for item in needs_action_items[:5]:
            print(f"  {item['icon']} {item['priority']:8} - {item['filename']}")

        if len(needs_action_items) > 5:
            print(f"  ... and {len(needs_action_items) - 5} more")

        print(f"\nItems in Pending_Approval: {len(pending_items)}")
        for item in pending_items:
            print(f"  {item['icon']} {item['priority']:8} - {item['filename']}")

        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate daily review plan")
    parser.add_argument(
        "--vault",
        default=".",
        help="Path to vault (default: current directory)"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print summary without generating plan file"
    )

    args = parser.parse_args()

    generator = DailyReviewGenerator(args.vault)

    if args.summary_only:
        generator.print_summary()
    else:
        generator.print_summary()
        plan_path = generator.save_plan()
        print(f"Plan saved to: {plan_path}")


if __name__ == "__main__":
    main()
