#!/usr/bin/env python3
"""
Ralph Skill Invoker

This script allows Claude Code to invoke the Ralph autonomous execution skill.

Usage:
    python invoke.py "Complete these tasks: task1, task2"
    python invoke.py "Execute client onboarding plan"
    python invoke.py "Run autonomous task loop"

Returns:
    JSON output with status, progress, and results
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def invoke_ralph(task: str, vault_path: str = None, max_iterations: int = 10) -> dict:
    """
    Invoke the Ralph autonomous execution skill.

    Args:
        task: Natural language task description
        vault_path: Path to Obsidian vault
        max_iterations: Maximum number of iterations

    Returns:
        dict: Result with status, tasks_completed, and progress
    """
    try:
        # Determine vault path
        if vault_path is None:
            vault_path = project_root / "AI_Employee_Vault"
        else:
            vault_path = Path(vault_path)  # Convert string to Path

        # Check if Ralph is already running
        progress_file = vault_path / ".claude" / "skills" / "ralph" / "progress.txt"

        if progress_file.exists():
            current_progress = progress_file.read_text()
            return {
                "status": "running",
                "message": "Ralph is already running",
                "current_progress": current_progress,
                "action": "Check progress.txt or use /cancel-ralph to stop",
                "error": None
            }

        # Create Ralph task
        print(f"[*] Starting Ralph autonomous execution...", file=sys.stderr)

        # Create task file in Plans/
        plans_folder = vault_path / "Plans"
        plans_folder.mkdir(parents=True, exist_ok=True)

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_file = plans_folder / f"RALPH_TASK_{timestamp}.md"

        task_content = f"""---
type: ralph_task
status: pending
created: {datetime.now().isoformat()}
---

# Ralph Autonomous Task

## Task Description
{task}

## Instructions
Ralph will:
1. Break down this task into subtasks
2. Execute each subtask using available skills
3. Create approval requests for external actions
4. Continue until all tasks complete
5. Report results when done

## Progress
- Initial state: Task received
- Ralph will update this as it progresses
"""

        task_file.write_text(task_content)

        # Note: In a real implementation, this would trigger the Ralph loop
        # For now, we return instructions for starting Ralph

        return {
            "status": "success",
            "message": "Ralph task created",
            "task_file": str(task_file),
            "action": "Task created in Plans/ - Use /ralph-loop to execute",
            "next_steps": [
                "Review the task in Plans/",
                "Use: /ralph-loop to start autonomous execution",
                "Ralph will iterate through subtasks until complete"
            ],
            "error": None
        }

    except Exception as e:
        print(f"[✗] Error: {e}", file=sys.stderr)
        return {
            "status": "error",
            "error": str(e),
            "action": None
        }


def main():
    """Main entry point for skill invocation."""
    parser = argparse.ArgumentParser(
        description="Invoke Ralph skill for autonomous execution"
    )
    parser.add_argument(
        "task",
        help="Task description for Ralph to execute"
    )
    parser.add_argument(
        "--vault",
        help="Path to Obsidian vault",
        default=None
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum number of iterations"
    )

    args = parser.parse_args()

    # Invoke Ralph
    result = invoke_ralph(args.task, args.vault, args.max_iterations)

    # Output as JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
