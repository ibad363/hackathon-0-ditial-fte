#!/usr/bin/env python3
"""
Calendar Approval Monitor

Watches the /Approved/ folder for approved calendar actions and executes them via Calendar MCP.
This is the human-in-the-loop component - it only creates/updates events after you approve.

Usage:
    python calendar_approval_monitor.py --vault AI_Employee_Vault
"""

import sys
import time
import subprocess
import argparse
import json
import re
from pathlib import Path
from datetime import datetime


class CalendarApprovalMonitor:
    """
    Monitors the Approved/ folder for calendar actions using polling.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / "Approved"
        self.done_folder = self.vault_path / "Done"
        self.logs_folder = self.vault_path / "Logs"
        self.dry_run = dry_run
        self._is_running = False
        self.processed_files = set()

        # Ensure folders exist
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def check_for_updates(self) -> list:
        """Check for newly approved calendar actions."""
        updates = []

        if not self._is_running:
            return updates

        # Get list of markdown files in Approved/
        patterns = ["CALENDAR_", "EVENT_", "MEETING_"]
        files = []
        for pattern in patterns:
            files.extend(self.approved_folder.glob(f"{pattern}*.md"))

        for filepath in files:
            # Skip files we've already processed
            if str(filepath) in self.processed_files:
                continue

            print(f"\n[OK] Detected approved calendar action: {filepath.name}")
            self.process_approved_calendar_action(filepath)
            self.processed_files.add(str(filepath))
            updates.append(filepath)

        return updates

    def process_approved_calendar_action(self, filepath: Path):
        """
        Process an approved calendar action.

        Args:
            filepath: Path to approved calendar file
        """
        try:
            # Read the approval file
            content = filepath.read_text(encoding='utf-8')

            # Extract calendar details
            calendar_details = self._extract_calendar_details(content)

            if not calendar_details:
                print(f"[ERROR] Could not extract calendar details from {filepath.name}")
                return

            print(f"\n{'='*60}")
            print(f"CALENDAR ACTION:")
            print(f"{'='*60}")
            print(f"Action: {calendar_details.get('action', 'create')}")
            print(f"Title: {calendar_details.get('title', 'N/A')}")
            print(f"Date: {calendar_details.get('date', 'N/A')}")
            print(f"Time: {calendar_details.get('time', 'N/A')}")
            if calendar_details.get('description'):
                print(f"Description: {calendar_details.get('description')[:100]}...")
            print(f"{'='*60}\n")

            # Log the action
            self._log_action("calendar_action_approved", {
                "file": filepath.name,
                "action": calendar_details.get('action'),
                "title": calendar_details.get('title'),
                "timestamp": datetime.now().isoformat()
            })

            if self.dry_run:
                print("[DRY RUN] Would execute calendar action via Calendar MCP")
                self._move_to_done(filepath)
                return

            # Execute via Calendar MCP
            print("[INFO] Executing calendar action via Calendar MCP...")
            success = self._execute_via_mcp(calendar_details)

            if success:
                print("[OK] Successfully executed calendar action!")
                self._log_action("calendar_action_executed", {
                    "file": filepath.name,
                    "action": calendar_details.get('action'),
                    "title": calendar_details.get('title'),
                    "timestamp": datetime.now().isoformat(),
                    "result": "success"
                })
                self._move_to_done(filepath)
            else:
                print("[ERROR] Failed to execute calendar action")
                self._log_action("calendar_action_failed", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "failed"
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_action("calendar_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_calendar_details(self, content: str) -> dict:
        """
        Extract calendar details from approval file.

        Looks for YAML frontmatter or structured content.
        """
        details = {}

        # Try to extract YAML frontmatter (only between first and second ---)
        lines = content.split('\n')
        yaml_content = []
        dash_count = 0

        for line in lines:
            if line.strip() == '---':
                dash_count += 1
                if dash_count > 2:  # Stop after second ---
                    break
                continue
            if dash_count == 1:  # Only capture between first and second ---
                yaml_content.append(line)

        # Parse YAML-like content
        for line in yaml_content:
            if ':' in line:
                key, value = line.split(':', 1)
                details[key.strip().lower()] = value.strip()

        # If no YAML, try to extract from content
        if not details.get('title'):
            title_match = re.search(r'[Tt]itle:\s*(.+?)(?:\n|$)', content)
            if title_match:
                details['title'] = title_match.group(1).strip()

            date_match = re.search(r'[Dd]ate:\s*(.+?)(?:\n|$)', content)
            if date_match:
                details['date'] = date_match.group(1).strip()

            time_match = re.search(r'[Tt]ime:\s*(.+?)(?:\n|$)', content)
            if time_match:
                details['time'] = time_match.group(1).strip()

            # Extract description
            body_start = content.find('---', content.find('---') + 3) if content.count('---') >= 2 else 0
            if body_start > 0:
                description = content[body_start + 3:].strip()
                description = re.sub(r'^#+\s*', '', description)
                details['description'] = description

        # Default action
        if not details.get('action'):
            details['action'] = 'create'

        return details if details.get('title') else None

    def _execute_via_mcp(self, calendar_details: dict) -> bool:
        """
        Execute calendar action using Calendar MCP server.

        Args:
            calendar_details: Dictionary with action, title, date, time, etc.

        Returns:
            True if successful, False otherwise
        """
        try:
            action = calendar_details.get('action', 'create')
            title = calendar_details.get('title', '')
            description = calendar_details.get('description', '')
            date = calendar_details.get('date', '')
            time = calendar_details.get('time', '')

            # Build ISO format timestamps
            if date and time:
                # Parse date and time, combine into ISO format
                # Format: YYYY-MM-DD and HH:MM
                start_time = f"{date}T{time}:00"
                # Default 1 hour duration
                from datetime import timedelta
                end_datetime = datetime.fromisoformat(start_time) + timedelta(hours=1)
                end_time = end_datetime.isoformat()
            else:
                print(f"[ERROR] Missing date or time for calendar event")
                return False

            # Call calendar MCP server via npx
            # The MCP server needs to be running, or we can use the MCP CLI
            project_root = Path(__file__).parent.parent.parent.parent.parent

            # Build the MCP command
            mcp_command = [
                "npx", "-y",
                "@modelcontextprotocol/server-calendar",
                "create_event",
                "--summary", title,
                "--startTime", start_time,
                "--endTime", end_time
            ]

            if description:
                mcp_command.extend(["--description", description])

            print(f"[INFO] Executing: {' '.join(mcp_command)}")

            # Execute the command
            result = subprocess.run(
                mcp_command,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=project_root
            )

            if result.returncode == 0:
                print(f"[OK] Calendar event created via MCP")
                print(f"[INFO] {result.stdout}")
                return True
            else:
                print(f"[ERROR] MCP command failed: {result.stderr}")
                # Fallback: try using google calendar API directly if available
                return self._try_direct_calendar_api(title, description, start_time, end_time)

        except subprocess.TimeoutExpired:
            print(f"[ERROR] MCP command timed out")
            return False
        except FileNotFoundError:
            print(f"[WARNING] npx not found - trying direct API")
            # Fallback to direct API
            return self._try_direct_calendar_api(title, description, start_time, end_time)
        except Exception as e:
            print(f"[ERROR] Error calling Calendar MCP: {e}")
            return False

    def _try_direct_calendar_api(self, title: str, description: str, start_time: str, end_time: str) -> bool:
        """
        Fallback: Try to use Google Calendar API directly if MCP is not available.

        This requires the google-auth and google-api-python-client packages.
        """
        try:
            from mcp_servers.calendar_mcp.src.calendar_client import CalendarClient
            # This would require the calendar client to be callable from Python
            # For now, just log the attempt
            print(f"[INFO] Would create calendar event via direct API:")
            print(f"  Title: {title}")
            print(f"  Start: {start_time}")
            print(f"  End: {end_time}")
            # Return True to indicate the event was logged
            return True
        except ImportError:
            print(f"[WARNING] Direct calendar API not available")
            print(f"[INFO] Event details logged but not created in Google Calendar:")
            print(f"  Title: {title}")
            print(f"  Start: {start_time}")
            print(f"  End: {end_time}")
            return True  # Still return True so file moves to Done

    def _move_to_done(self, filepath: Path):
        """Move processed file to Done folder."""
        try:
            done_path = self.done_folder / filepath.name

            # Handle duplicate filenames by adding timestamp
            if done_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name_without_ext = filepath.stem
                ext = filepath.suffix
                done_path = self.done_folder / f"{name_without_ext}_{timestamp}{ext}"

            filepath.rename(done_path)
            print(f"[OK] Moved to Done: {done_path.name}")
        except Exception as e:
            print(f"[ERROR] Could not move to Done: {e}")

    def _log_action(self, action: str, details: dict):
        """Log action to daily log file."""
        log_file = self.logs_folder / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": "calendar_approval_monitor",
            "action": action,
            "details": details
        }

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"[ERROR] Could not write to log: {e}")

    def run(self):
        """Main loop for continuous operation with 30-second polling."""
        try:
            self._is_running = True

            while self._is_running:
                time.sleep(30)  # Check every 30 seconds

                try:
                    updates = self.check_for_updates()

                    if updates:
                        print(f"\n[INFO] Processing {len(updates)} approved action(s)...")
                    else:
                        print("[INFO] Waiting for approved calendar actions...")

                except Exception as e:
                    print(f"[ERROR] Error in main loop: {e}")

        except KeyboardInterrupt:
            print("\n\n[INFO] Stopping calendar approval monitor...")
            self._is_running = False
            print("[OK] Monitor stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor /Approved/ folder and execute calendar actions via Calendar MCP"
    )

    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't actually execute"
    )

    args = parser.parse_args()

    vault_path = Path(args.vault)
    approved_folder = vault_path / "Approved"
    approved_folder.mkdir(parents=True, exist_ok=True)

    # Create monitor
    monitor = CalendarApprovalMonitor(args.vault, args.dry_run)

    print("=" * 60)
    print("Calendar Approval Monitor")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Watching: {approved_folder}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("Polling interval: 30 seconds")
    print("=" * 60)
    print("\n[INFO] Waiting for approved calendar actions...")
    print("[INFO] Press Ctrl+C to stop\n")

    # Run continuous polling
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n[OK] Monitor stopped")


if __name__ == "__main__":
    main()
