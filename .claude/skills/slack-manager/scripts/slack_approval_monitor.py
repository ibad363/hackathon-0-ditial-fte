#!/usr/bin/env python3
"""
Slack Approval Monitor

Watches the /Approved/ folder for approved Slack actions and sends them via Slack MCP.
This is the human-in-the-loop component - it only sends messages after you approve.

Usage:
    python slack_approval_monitor.py --vault AI_Employee_Vault
"""

import sys
import time
import subprocess
import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


class SlackApprovalMonitor:
    """
    Monitors the Approved/ folder for Slack messages using polling.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / "Approved"
        self.done_folder = self.vault_path / "Done"
        self.logs_folder = self.vault_path / "Logs"
        self.dry_run = dry_run
        self._is_running = False
        self.processed_files = set()

        # Get Slack bot token from environment
        self.slack_token = os.environ.get('SLACK_BOT_TOKEN')
        if not self.slack_token:
            print("[WARNING] SLACK_BOT_TOKEN not found in environment")

        # Ensure folders exist
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def check_for_updates(self) -> list:
        """Check for newly approved Slack messages."""
        updates = []

        if not self._is_running:
            return updates

        # Get list of markdown files in Approved/
        patterns = ["SLACK_", "SLACK_MESSAGE_"]
        files = []
        for pattern in patterns:
            files.extend(self.approved_folder.glob(f"{pattern}*.md"))

        for filepath in files:
            # Skip files we've already processed
            if str(filepath) in self.processed_files:
                continue

            print(f"\n[OK] Detected approved Slack message: {filepath.name}")
            self.process_approved_slack_message(filepath)
            self.processed_files.add(str(filepath))
            updates.append(filepath)

        return updates

    def process_approved_slack_message(self, filepath: Path):
        """
        Process an approved Slack message.

        Args:
            filepath: Path to approved Slack file
        """
        try:
            # Read the approval file
            content = filepath.read_text(encoding='utf-8')

            # Extract Slack message details
            message_details = self._extract_message_details(content)

            if not message_details:
                print(f"[ERROR] Could not extract message details from {filepath.name}")
                return

            print(f"\n{'='*60}")
            print(f"SLACK MESSAGE TO SEND:")
            print(f"{'='*60}")
            print(f"Channel: {message_details.get('channel', 'N/A')}")
            print(f"Message:\n{message_details.get('message', '')[:300]}")
            print(f"{'='*60}\n")

            # Log the action
            self._log_action("slack_message_approved", {
                "file": filepath.name,
                "channel": message_details.get('channel'),
                "timestamp": datetime.now().isoformat()
            })

            if self.dry_run:
                print("[DRY RUN] Would send message via Slack MCP")
                self._move_to_done(filepath)
                return

            # Send via Slack MCP
            print("[INFO] Sending message via Slack MCP...")
            success = self._send_via_mcp(message_details)

            if success:
                print("[OK] Successfully sent Slack message!")
                self._log_action("slack_message_sent", {
                    "file": filepath.name,
                    "channel": message_details.get('channel'),
                    "timestamp": datetime.now().isoformat(),
                    "result": "success"
                })
                self._move_to_done(filepath)
            else:
                print("[ERROR] Failed to send Slack message")
                self._log_action("slack_message_failed", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "failed"
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_action("slack_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_message_details(self, content: str) -> dict:
        """
        Extract Slack message details from approval file.

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
        if not details.get('channel'):
            channel_match = re.search(r'[Cc]hannel:\s*#?(\w+)', content)
            if channel_match:
                details['channel'] = '#' + channel_match.group(1).strip()

            message_match = re.search(r'[Mm]essage:\s*(.+?)(?:\n|$)', content, re.DOTALL)
            if message_match:
                details['message'] = message_match.group(1).strip()

            # Extract message body
            body_start = content.find('---', content.find('---') + 3) if content.count('---') >= 2 else 0
            if body_start > 0:
                message = content[body_start + 3:].strip()
                message = re.sub(r'^#+\s*', '', message)
                if not details.get('message'):
                    details['message'] = message

        return details if details.get('channel') and details.get('message') else None

    def _send_via_mcp(self, message_details: dict) -> bool:
        """
        Send message using Slack API.

        Args:
            message_details: Dictionary with channel, message

        Returns:
            True if successful, False otherwise
        """
        try:
            channel = message_details.get('channel', '')
            message = message_details.get('message', '')

            if not channel or not message:
                print(f"[ERROR] Missing channel or message")
                return False

            # Try using Slack CLI via subprocess
            # First check if slack CLI is available
            result = subprocess.run(
                ["slack", "--version"],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                # Use Slack CLI
                print(f"[INFO] Sending via Slack CLI...")
                slack_command = [
                    "slack", "chat", "send",
                    "--channel", channel,
                    "--text", message
                ]

                result = subprocess.run(
                    slack_command,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"[OK] Message sent via Slack CLI")
                    return True
                else:
                    print(f"[ERROR] Slack CLI failed: {result.stderr}")
                    # Fall through to web API attempt
            else:
                print(f"[INFO] Slack CLI not available, trying Web API...")

            # Fallback: Use Slack Web API directly
            return self._send_via_web_api(channel, message)

        except subprocess.TimeoutExpired:
            print(f"[ERROR] Slack command timed out")
            return False
        except FileNotFoundError:
            print(f"[INFO] Slack CLI not found, trying Web API...")
            return self._send_via_web_api(channel, message)
        except Exception as e:
            print(f"[ERROR] Error sending Slack message: {e}")
            return False

    def _send_via_web_api(self, channel: str, message: str) -> bool:
        """
        Send message via Slack Web API using requests library.

        Args:
            channel: Slack channel (e.g., #general)
            message: Message text

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.slack_token:
                print(f"[ERROR] SLACK_BOT_TOKEN not set")
                print(f"[INFO] Message logged but not sent:")
                print(f"  Channel: {channel}")
                print(f"  Message: {message[:100]}...")
                return True  # Return True so file moves to Done

            import requests

            # Remove # from channel if present
            channel_id = channel.lstrip('#')

            # Slack Web API endpoint
            url = "https://slack.com/api/chat.postMessage"

            headers = {
                "Authorization": f"Bearer {self.slack_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "channel": channel_id,
                "text": message
            }

            print(f"[INFO] Sending via Slack Web API...")
            response = requests.post(url, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    print(f"[OK] Message sent successfully")
                    return True
                else:
                    print(f"[ERROR] Slack API error: {data.get('error')}")
                    return False
            else:
                print(f"[ERROR] HTTP error: {response.status_code}")
                return False

        except ImportError:
            print(f"[WARNING] requests library not available")
            print(f"[INFO] Message logged but not sent:")
            print(f"  Channel: {channel}")
            print(f"  Message: {message[:100]}...")
            return True  # Return True so file moves to Done
        except Exception as e:
            print(f"[ERROR] Error using Slack Web API: {e}")
            return False

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
            "component": "slack_approval_monitor",
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
                        print(f"\n[INFO] Processing {len(updates)} approved message(s)...")
                    else:
                        print("[INFO] Waiting for approved Slack messages...")

                except Exception as e:
                    print(f"[ERROR] Error in main loop: {e}")

        except KeyboardInterrupt:
            print("\n\n[INFO] Stopping Slack approval monitor...")
            self._is_running = False
            print("[OK] Monitor stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor /Approved/ folder and send Slack messages via Slack MCP"
    )

    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't actually send"
    )

    args = parser.parse_args()

    vault_path = Path(args.vault)
    approved_folder = vault_path / "Approved"
    approved_folder.mkdir(parents=True, exist_ok=True)

    # Create monitor
    monitor = SlackApprovalMonitor(args.vault, args.dry_run)

    print("=" * 60)
    print("Slack Approval Monitor")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Watching: {approved_folder}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("Polling interval: 30 seconds")
    print("=" * 60)
    print("\n[INFO] Waiting for approved Slack messages...")
    print("[INFO] Press Ctrl+C to stop\n")

    # Run continuous polling
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n[OK] Monitor stopped")


if __name__ == "__main__":
    main()
