#!/usr/bin/env python3
"""
Weekly Briefing Skill Invoker

This script allows Claude Code to invoke the weekly-briefing skill.

Usage:
    python invoke.py "Generate CEO briefing for this week"
    python invoke.py "Create Monday morning briefing"
    python invoke.py "Audit business performance"

Returns:
    JSON output with status, file_path, and summary
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the briefing generator
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from generate_ceo_briefing import WeeklyBriefingGenerator


def invoke_briefing(task: str, vault_path: str = None) -> dict:
    """
    Invoke the weekly briefing skill.

    Args:
        task: Natural language task description
        vault_path: Path to Obsidian vault

    Returns:
        dict: Result with status, file_path, summary, and error if any
    """
    try:
        # Determine vault path
        if vault_path is None:
            vault_path = project_root / "AI_Employee_Vault"
        else:
            vault_path = Path(vault_path)  # Convert string to Path

        # Check if task is requesting a briefing
        task_lower = task.lower()
        keywords = ["briefing", "ceo", "audit", "business", "performance", "week", "monday"]

        if not any(keyword in task_lower for keyword in keywords):
            return {
                "status": "error",
                "error": "Task not recognized. Use keywords like: 'briefing', 'CEO', 'audit', 'business performance'",
                "file_path": None,
                "summary": None
            }

        # Generate briefing
        print(f"[*] Generating CEO briefing...", file=sys.stderr)

        generator = WeeklyBriefingGenerator(str(vault_path))
        briefing_file = generator.save_briefing()

        # Read the briefing content for summary
        briefing_content = briefing_file.read_text()

        # Extract summary (first 500 chars)
        summary = briefing_content.split("\n\n")[0][:500] + "..."

        print(f"[✅] Briefing generated: {briefing_file.name}", file=sys.stderr)

        return {
            "status": "success",
            "file_path": str(briefing_file),
            "summary": summary,
            "action": "CEO briefing generated and saved to vault",
            "error": None
        }

    except Exception as e:
        print(f"[✗] Error: {e}", file=sys.stderr)
        return {
            "status": "error",
            "error": str(e),
            "file_path": None,
            "summary": None
        }


def main():
    """Main entry point for skill invocation."""
    parser = argparse.ArgumentParser(
        description="Invoke weekly-briefing skill"
    )
    parser.add_argument(
        "task",
        help="Task description (e.g., 'Generate CEO briefing')"
    )
    parser.add_argument(
        "--vault",
        help="Path to Obsidian vault",
        default=None
    )

    args = parser.parse_args()

    # Invoke the skill
    result = invoke_briefing(args.task, args.vault)

    # Output as JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
