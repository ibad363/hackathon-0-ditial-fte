#!/usr/bin/env python3
"""
Ralph Wiggum Orchestrator - Autonomous Task Loop

Implements the Stop hook pattern for autonomous multi-step task completion.
Ralph keeps iterating until all tasks in the PRD are complete.

The Pattern:
1. Read task list from prd.json
2. Find first incomplete task (passes: false)
3. Execute the task
4. Check completion
5. If not all done, loop back to step 2
6. Output <promise>TASK_COMPLETE</promise> when done

Usage:
    python ralph_orchestrator.py --vault AI_Employee_Vault --prd ralph/prd.json
    python ralph_orchestrator.py --once  # Single iteration for testing
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ralph_orchestrator")


class RalphOrchestrator:
    """
    Orchestrator for the Ralph Wiggum autonomous task loop.

    Manages:
    - Task list (PRD) loading and updating
    - Progress tracking
    - State persistence
    - Completion detection
    """

    def __init__(
        self,
        vault_path: str,
        prd_path: str = None,
        max_iterations: int = 10,
        check_interval: int = 30
    ):
        self.vault_path = Path(vault_path)
        self.prd_path = Path(prd_path) if prd_path else self.vault_path.parent / "ralph" / "prd.json"
        self.max_iterations = max_iterations
        self.check_interval = check_interval

        # State files
        self.state_file = self.vault_path.parent / "ralph" / "state.json"
        self.progress_file = self.vault_path.parent / "ralph" / "progress.txt"

        # Ensure ralph folder exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load state
        self.state = self._load_state()
        self.prd = self._load_prd()

    def _load_state(self) -> dict:
        """Load orchestrator state."""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except:
                pass
        return {
            "iteration": 0,
            "started_at": None,
            "current_task": None,
            "completed_tasks": [],
            "status": "idle"
        }

    def _save_state(self):
        """Save orchestrator state."""
        self.state_file.write_text(json.dumps(self.state, indent=2))

    def _load_prd(self) -> dict:
        """Load the Product Requirements Document (task list)."""
        if not self.prd_path.exists():
            logger.warning(f"PRD not found: {self.prd_path}")
            return {"userStories": []}

        try:
            return json.loads(self.prd_path.read_text())
        except json.JSONDecodeError as e:
            logger.error(f"Invalid PRD JSON: {e}")
            return {"userStories": []}

    def _save_prd(self):
        """Save the PRD with updated task states."""
        self.prd_path.write_text(json.dumps(self.prd, indent=2))

    def _log_progress(self, message: str):
        """Append to progress file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.progress_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")

    def get_next_task(self) -> dict:
        """Get the next incomplete task (highest priority first)."""
        stories = self.prd.get("userStories", [])

        # Sort by priority (lower number = higher priority)
        incomplete = [s for s in stories if not s.get("passes", False)]
        incomplete.sort(key=lambda x: x.get("priority", 999))

        return incomplete[0] if incomplete else None

    def get_all_incomplete(self) -> list:
        """Get all incomplete tasks."""
        stories = self.prd.get("userStories", [])
        return [s for s in stories if not s.get("passes", False)]

    def mark_task_complete(self, task_id: str):
        """Mark a task as complete in the PRD."""
        for story in self.prd.get("userStories", []):
            if story.get("id") == task_id:
                story["passes"] = True
                story["completed_at"] = datetime.now(timezone.utc).isoformat()
                break

        self._save_prd()
        self.state["completed_tasks"].append(task_id)
        self._save_state()
        self._log_progress(f"Task {task_id} marked complete")

    def check_all_complete(self) -> bool:
        """Check if all tasks are complete."""
        stories = self.prd.get("userStories", [])
        return all(s.get("passes", False) for s in stories)

    def check_approval_status(self, task: dict) -> str:
        """
        Check if a task's approval has been processed.

        Returns: "pending", "approved", "rejected", or "no_approval_needed"
        """
        task_id = task.get("id", "unknown")

        # Check Pending_Approval for this task
        pending = self.vault_path / "Pending_Approval"
        for f in pending.glob(f"*{task_id}*.md"):
            return "pending"

        # Check Approved
        approved = self.vault_path / "Approved"
        for f in approved.glob(f"*{task_id}*.md"):
            return "approved"

        # Check Rejected
        rejected = self.vault_path / "Rejected"
        for f in rejected.glob(f"*{task_id}*.md"):
            return "rejected"

        # Check Done (already processed)
        done = self.vault_path / "Done"
        for f in done.glob(f"*{task_id}*.md"):
            return "approved"

        return "no_approval_needed"

    def create_task_plan(self, task: dict) -> Path:
        """Create a plan file for the task."""
        task_id = task.get("id", "unknown")
        title = task.get("title", "Unknown Task")
        description = task.get("description", "")
        criteria = task.get("acceptanceCriteria", [])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_file = self.vault_path / "Plans" / f"PLAN_{task_id}_{timestamp}.md"
        plan_file.parent.mkdir(exist_ok=True)

        content = f"""---
type: ralph_plan
task_id: {task_id}
status: in_progress
created: {datetime.now(timezone.utc).isoformat()}
---

# Ralph Plan: {title}

## Task ID
{task_id}

## Description
{description}

## Acceptance Criteria
"""
        for criterion in criteria:
            content += f"- [ ] {criterion}\n"

        content += f"""

## Execution Steps

1. [ ] Analyze task requirements
2. [ ] Identify required skills/MCPs
3. [ ] Execute actions
4. [ ] Create approval request if needed
5. [ ] Verify completion
6. [ ] Mark task as done

## Notes

*This plan was auto-generated by Ralph Wiggum Orchestrator*
"""

        plan_file.write_text(content, encoding='utf-8')
        logger.info(f"Created plan: {plan_file}")
        return plan_file

    def execute_iteration(self) -> str:
        """
        Execute a single iteration of the Ralph loop.

        Returns: "continue", "complete", "waiting", or "error"
        """
        self.state["iteration"] += 1
        self._save_state()

        logger.info(f"=== Ralph Iteration {self.state['iteration']} ===")
        self._log_progress(f"Starting iteration {self.state['iteration']}")

        # Check if we've exceeded max iterations
        if self.state["iteration"] > self.max_iterations:
            logger.warning(f"Max iterations ({self.max_iterations}) reached")
            self._log_progress(f"STOPPED: Max iterations reached")
            return "error"

        # Get next task
        task = self.get_next_task()

        if task is None:
            # All tasks complete!
            logger.info("All tasks complete!")
            self._log_progress("ALL TASKS COMPLETE")
            self.state["status"] = "complete"
            self._save_state()
            return "complete"

        task_id = task.get("id", "unknown")
        title = task.get("title", "Unknown")

        logger.info(f"Working on task: {task_id} - {title}")
        self.state["current_task"] = task_id
        self._save_state()

        # Check approval status
        approval_status = self.check_approval_status(task)

        if approval_status == "pending":
            logger.info(f"Task {task_id} waiting for approval")
            self._log_progress(f"Task {task_id} waiting for human approval")
            return "waiting"

        elif approval_status == "rejected":
            logger.info(f"Task {task_id} was rejected - skipping")
            self._log_progress(f"Task {task_id} REJECTED - marking as skipped")
            # Mark as complete anyway (rejected = handled)
            self.mark_task_complete(task_id)
            return "continue"

        elif approval_status == "approved":
            logger.info(f"Task {task_id} approved - marking complete")
            self._log_progress(f"Task {task_id} APPROVED - completed")
            self.mark_task_complete(task_id)
            return "continue"

        else:
            # No approval needed yet - create plan and process
            logger.info(f"Processing task {task_id}")
            self.create_task_plan(task)
            self._log_progress(f"Created plan for task {task_id}")
            return "continue"

    def run(self) -> bool:
        """
        Run the full Ralph loop until completion or max iterations.

        Returns: True if all tasks completed, False otherwise
        """
        logger.info("Starting Ralph Wiggum autonomous loop")
        self.state["started_at"] = datetime.now(timezone.utc).isoformat()
        self.state["status"] = "running"
        self._save_state()
        self._log_progress("Ralph Wiggum loop started")

        try:
            while True:
                result = self.execute_iteration()

                if result == "complete":
                    # All tasks done!
                    print("\n<promise>TASK_COMPLETE</promise>\n")
                    return True

                elif result == "error":
                    logger.error("Ralph encountered an error")
                    self.state["status"] = "error"
                    self._save_state()
                    return False

                elif result == "waiting":
                    # Waiting for approval - check periodically
                    logger.info(f"Waiting {self.check_interval}s for approval...")
                    time.sleep(self.check_interval)

                else:
                    # Continue to next iteration with small delay
                    time.sleep(2)

        except KeyboardInterrupt:
            logger.info("Ralph interrupted by user")
            self.state["status"] = "interrupted"
            self._save_state()
            self._log_progress("Ralph interrupted by user")
            return False

    def run_once(self) -> str:
        """Run a single iteration (for testing)."""
        return self.execute_iteration()

    def get_status(self) -> dict:
        """Get current Ralph status."""
        return {
            "status": self.state.get("status", "unknown"),
            "iteration": self.state.get("iteration", 0),
            "current_task": self.state.get("current_task"),
            "completed_tasks": len(self.state.get("completed_tasks", [])),
            "remaining_tasks": len(self.get_all_incomplete()),
            "started_at": self.state.get("started_at")
        }

    def reset(self):
        """Reset Ralph state for a fresh start."""
        self.state = {
            "iteration": 0,
            "started_at": None,
            "current_task": None,
            "completed_tasks": [],
            "status": "idle"
        }
        self._save_state()

        # Clear progress file
        if self.progress_file.exists():
            self.progress_file.unlink()

        logger.info("Ralph state reset")


def main():
    parser = argparse.ArgumentParser(description="Ralph Wiggum Orchestrator")
    parser.add_argument(
        "--vault", "-v",
        default=os.getenv("VAULT_PATH", "AI_Employee_Vault"),
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--prd", "-p",
        default=None,
        help="Path to PRD (task list) JSON file"
    )
    parser.add_argument(
        "--max-iterations", "-m",
        type=int,
        default=10,
        help="Maximum iterations before stopping"
    )
    parser.add_argument(
        "--check-interval", "-i",
        type=int,
        default=30,
        help="Seconds to wait when checking for approvals"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run single iteration and exit"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current Ralph status and exit"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset Ralph state and exit"
    )

    args = parser.parse_args()

    ralph = RalphOrchestrator(
        vault_path=args.vault,
        prd_path=args.prd,
        max_iterations=args.max_iterations,
        check_interval=args.check_interval
    )

    if args.status:
        status = ralph.get_status()
        print(json.dumps(status, indent=2))
        return

    if args.reset:
        ralph.reset()
        print("Ralph state reset")
        return

    if args.once:
        result = ralph.run_once()
        print(f"Iteration result: {result}")
        return

    # Run full loop
    success = ralph.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
