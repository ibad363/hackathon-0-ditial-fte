"""
LinkedIn Builder Monitor - Approval Workflow Monitor

Monitors the Approved/ folder for LinkedIn profile draft requests
and processes them when detected.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directories to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from utils.audit_logging import AuditLogger


class LinkedInBuilderMonitor:
    """
    Monitor for LinkedIn profile builder approval workflow.

    Watches the Approved/ folder for LINKEDIN_PROFILE_DRAFT_*.md files
    and processes them when detected.

    Usage:
        monitor = LinkedInBuilderMonitor(vault_path="AI_Employee_Vault")
        await monitor.run(check_interval=30)
    """

    def __init__(
        self,
        vault_path: str | Path = "AI_Employee_Vault",
        check_interval: int = 30
    ):
        """
        Initialize the monitor.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 30)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.approved_dir = self.vault_path / "Approved"
        self.done_dir = self.vault_path / "Done"
        self.audit_logger = AuditLogger(self.vault_path)

        # Track processed files
        self.processed_files = set()

        self._log_audit_action("monitor_init", {
            "check_interval": check_interval
        })

    def _log_audit_action(
        self,
        action_type: str,
        parameters: dict,
        result: str = "success"
    ) -> None:
        """Log action to audit log."""
        try:
            self.audit_logger.log_action(
                action_type=action_type,
                target="linkedin_builder_monitor",
                parameters=parameters,
                result=result
            )
        except Exception:
            pass

    async def check_for_approved_files(self) -> list[Path]:
        """
        Check for approved draft files.

        Returns:
            List of approved file paths
        """
        if not self.approved_dir.exists():
            return []

        # Find all LINKEDIN_PROFILE_DRAFT_*.md files in Approved/
        approved_files = list(self.approved_dir.glob("LINKEDIN_PROFILE_DRAFT_*.md"))

        # Filter out already processed files
        new_files = [f for f in approved_files if str(f) not in self.processed_files]

        return new_files

    async def process_approved_file(self, file_path: Path) -> bool:
        """
        Process an approved draft file.

        Args:
            file_path: Path to approved file

        Returns:
            True if processed successfully, False otherwise
        """
        try:
            self._log_audit_action("process_file", {
                "file": str(file_path)
            })

            # Read the approved file
            content = file_path.read_text(encoding="utf-8")

            # Parse frontmatter
            frontmatter = self._parse_frontmatter(content)

            if not frontmatter:
                self._log_audit_action("invalid_file", {
                    "file": str(file_path),
                    "error": "No frontmatter found"
                }, result="error")
                return False

            # Check file type
            file_type = frontmatter.get("type", "")
            if file_type != "linkedin_profile_draft":
                self._log_audit_action("wrong_type", {
                    "file": str(file_path),
                    "type": file_type
                }, result="error")
                return False

            # Get profile ID
            profile_id = frontmatter.get("profile_id")
            if not profile_id:
                self._log_audit_action("missing_profile_id", {
                    "file": str(file_path)
                }, result="error")
                return False

            # The file is a draft, so we just need to:
            # 1. Mark it as processed
            # 2. Move to Done/ with completion summary

            # Mark as processed
            self.processed_files.add(str(file_path))

            # Move to Done/
            await self._move_to_done(file_path, summary="Profile drafts approved and ready for application")

            self._log_audit_action("file_processed", {
                "file": str(file_path),
                "profile_id": profile_id
            })

            return True

        except Exception as e:
            self._log_audit_action("process_error", {
                "file": str(file_path),
                "error": str(e)
            }, result="error")
            return False

    def _parse_frontmatter(self, content: str) -> Optional[dict]:
        """
        Parse YAML frontmatter from markdown content.

        Args:
            content: Markdown file content

        Returns:
            Frontmatter dict or None
        """
        try:
            # Find frontmatter section
            if not content.startswith("---"):
                return None

            # Find end of frontmatter
            end_idx = content.find("\n---", 3)
            if end_idx == -1:
                return None

            # Extract frontmatter
            frontmatter_text = content[3:end_idx]

            # Parse simple key-value pairs
            frontmatter = {}
            for line in frontmatter_text.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()

            return frontmatter

        except Exception:
            return None

    async def _move_to_done(self, file_path: Path, summary: str = "") -> None:
        """
        Move file to Done/ with summary.

        Args:
            file_path: Path to file to move
            summary: Summary of what was done
        """
        # Ensure Done/ directory exists
        self.done_dir.mkdir(parents=True, exist_ok=True)

        # Read content
        content = file_path.read_text(encoding="utf-8")

        # Add completion summary at end
        if summary:
            content += f"\n\n---\n\n**Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{summary}\n"
            content += "\n## Next Steps\n\n"
            content += "1. Review each draft section\n"
            content += "2. Edit as needed for your voice\n"
            content += "3. Copy and paste to LinkedIn profile\n"
            content += "4. Save profile when complete\n"

        # Generate new filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = file_path.stem
        new_name = f"{original_name}_completed_{timestamp}.md"
        done_path = self.done_dir / new_name

        # Write to Done/
        done_path.write_text(content, encoding="utf-8")

        # Remove original
        file_path.unlink()

        self._log_audit_action("file_moved_to_done", {
            "from": str(file_path),
            "to": str(done_path)
        })

    async def run_once(self) -> int:
        """
        Run one check cycle.

        Returns:
            Number of files processed
        """
        # Check for approved files
        approved_files = await self.check_for_approved_files()

        processed_count = 0

        for file_path in approved_files:
            success = await self.process_approved_file(file_path)
            if success:
                processed_count += 1

            # Small delay between processing files
            await asyncio.sleep(1)

        return processed_count

    async def run(self) -> None:
        """
        Run the monitor continuously.

        Checks for approved files every check_interval seconds.
        """
        self._log_audit_action("monitor_started", {})

        print(f"LinkedIn Profile Builder Monitor started")
        print(f"Watching: {self.approved_dir}")
        print(f"Check interval: {self.check_interval} seconds")
        print("Press Ctrl+C to stop")

        try:
            while True:
                # Run one check cycle
                processed = await self.run_once()

                if processed > 0:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processed {processed} file(s)")

                # Wait before next check
                await asyncio.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\nMonitor stopped by user")
            self._log_audit_action("monitor_stopped", {"reason": "user_interrupt"})

        except Exception as e:
            print(f"\nMonitor error: {e}")
            self._log_audit_action("monitor_error", {"error": str(e)}, result="error")


# Main entry point
async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn Profile Builder Monitor")
    parser.add_argument("--vault", default="AI_Employee_Vault", help="Path to vault")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run once and exit")

    args = parser.parse_args()

    monitor = LinkedInBuilderMonitor(
        vault_path=args.vault,
        check_interval=args.interval
    )

    if args.once:
        # Run once
        processed = await monitor.run_once()
        print(f"Processed {processed} file(s)")
    else:
        # Run continuously
        await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
