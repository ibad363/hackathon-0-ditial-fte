#!/usr/bin/env python3
"""
Inbox Processor Utility Script

Automatically processes items in the /Inbox folder and routes them
to appropriate destinations based on content analysis.

Usage:
    python process_inbox.py [--vault PATH] [--dry-run]
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import re
import shutil

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class InboxProcessor:
    """Process and route inbox items to appropriate destinations."""

    # Keywords that indicate urgency
    URGENT_KEYWORDS = ["urgent", "asap", "emergency", "deadline", "immediately"]

    # Keywords that indicate financial content
    FINANCIAL_KEYWORDS = ["invoice", "payment", "contract", "quote", "estimate"]

    # Keywords that indicate approval needed
    APPROVAL_KEYWORDS = ["approve", "approval", "authorize", "confirm"]

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.done_path = self.vault_path / "Done"
        self.logs_path = self.vault_path / "Logs"
        self.dry_run = dry_run

        # Ensure folders exist
        self.needs_action_path.mkdir(parents=True, exist_ok=True)
        self.pending_approval_path.mkdir(parents=True, exist_ok=True)
        self.done_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

    def analyze_item(self, filepath: Path) -> dict:
        """
        Analyze an inbox item and determine routing.

        Returns:
            dict with keys: category, priority, destination, reason
        """
        content = filepath.read_text(errors="ignore").lower()
        filename = filepath.stem.lower()

        combined_text = f"{filename} {content}"

        # Check for urgent keywords
        is_urgent = any(kw in combined_text for kw in self.URGENT_KEYWORDS)

        # Check for financial keywords
        is_financial = any(kw in combined_text for kw in self.FINANCIAL_KEYWORDS)

        # Check for approval keywords
        needs_approval = any(kw in combined_text for kw in self.APPROVAL_KEYWORDS)

        # Determine routing
        if is_financial or needs_approval:
            return {
                "category": "approval_required",
                "priority": "critical" if is_urgent else "high",
                "destination": self.pending_approval_path,
                "reason": "Financial or approval required",
            }
        elif is_urgent:
            return {
                "category": "action_required",
                "priority": "high",
                "destination": self.needs_action_path,
                "reason": "Urgent keywords detected",
            }
        elif any(kw in combined_text for kw in ["task", "todo", "follow up", "action"]):
            return {
                "category": "action_required",
                "priority": "normal",
                "destination": self.needs_action_path,
                "reason": "Action item detected",
            }
        else:
            return {
                "category": "archive",
                "priority": "low",
                "destination": self.done_path,
                "reason": "Reference or information only",
            }

    def add_metadata_header(self, source_file: Path, analysis: dict) -> str:
        """Add metadata header to file content."""
        content = source_file.read_text(encoding="utf-8", errors="ignore")

        metadata = f"""---
type: {analysis['category']}
source: inbox
category: {analysis['category']}
priority: {analysis['priority']}
processed_date: {datetime.now().isoformat()}
original_location: /Inbox/{source_file.name}
destination: {analysis['destination'].name}/
---

"""
        return metadata + content

    def process_item(self, filepath: Path) -> dict:
        """Process a single inbox item."""
        logger.info(f"Processing: {filepath.name}")

        # Analyze the item
        analysis = self.analyze_item(filepath)

        # Determine new filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{analysis['category']}_{timestamp}_{filepath.name}"
        dest_path = analysis['destination'] / new_filename

        if not self.dry_run:
            # Add metadata header
            content = self.add_metadata_header(filepath, analysis)
            dest_path.write_text(content, encoding="utf-8")
            # Remove from inbox
            filepath.unlink()
            logger.info(f"  -> Moved to {analysis['destination'].name}/{new_filename}")
        else:
            logger.info(f"  [DRY RUN] Would move to {analysis['destination'].name}/{new_filename}")

        return {
            "original_file": filepath.name,
            "destination": str(analysis['destination'].name),
            "new_filename": new_filename,
            "category": analysis['category'],
            "priority": analysis['priority'],
            "reason": analysis['reason']
        }

    def process_all(self) -> list:
        """Process all items in the inbox."""
        items = list(self.inbox_path.glob("*"))
        items = [i for i in items if i.is_file()]

        if not items:
            logger.info("No items in /Inbox to process")
            return []

        logger.info(f"Found {len(items)} items in /Inbox")

        results = []
        for item in items:
            try:
                result = self.process_item(item)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {item.name}: {e}")

        # Log summary
        self.log_processing_summary(results)

        return results

    def log_processing_summary(self, results: list) -> None:
        """Create a processing summary log."""
        log_path = self.logs_path / f"inbox_processing_{datetime.now().strftime('%Y-%m-%d')}.md"

        summary = f"""# Inbox Processing Log - {datetime.now().strftime('%Y-%m-%d')}

## Summary
- Items Processed: {len(results)}
- Routed to Needs_Action: {sum(1 for r in results if r['destination'] == 'Needs_Action')}
- Routed to Pending_Approval: {sum(1 for r in results if r['destination'] == 'Pending_Approval')}
- Archived: {sum(1 for r in results if r['destination'] == 'Done')}

## Items Processed
"""

        for result in results:
            summary += f"\n### [{result['priority'].upper()}] {result['original_file']}\n"
            summary += f"- **Destination**: {result['destination']}\n"
            summary += f"- **Category**: {result['category']}\n"
            summary += f"- **Reason**: {result['reason']}\n"

        if not self.dry_run:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(summary + "\n")
            logger.info(f"Logged summary to {log_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Process items in /Inbox folder")
    parser.add_argument(
        "--vault",
        default=".",
        help="Path to vault (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze without moving files"
    )

    args = parser.parse_args()

    processor = InboxProcessor(args.vault, args.dry_run)
    results = processor.process_all()

    print(f"\nProcessed {len(results)} items")


if __name__ == "__main__":
    main()
