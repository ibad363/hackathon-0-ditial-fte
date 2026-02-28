#!/usr/bin/env python3
"""
Email Approval Monitor - Monitors Approved/ folder for email actions.

Processes approved email requests and sends them via Gmail MCP.

Usage:
    python email_approval_monitor.py --vault AI_Employee_Vault
"""

import os
import sys
import yaml
import re
import subprocess
from datetime import datetime
import time
import shutil
import json
from pathlib import Path

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path for imports
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Import MCP HTTP client
try:
    from utils.mcp_http_client import EmailMCPClient
except ImportError:
    print("[WARNING] MCP HTTP client not available. Email sending will not work.")
    EmailMCPClient = None

try:
    from watchers.base_watcher import BaseWatcher
except ImportError:
    # Fallback for direct script execution
    script_dir = Path(__file__).parent
    watchers_dir = script_dir.parent.parent.parent.parent / "watchers"
    sys.path.insert(0, str(watchers_dir))
    from base_watcher import BaseWatcher

class EmailApprovalMonitor(BaseWatcher):
    """Monitor the Approved/ folder and send emails."""

    def __init__(self, vault_path: str):
        """
        Initialize the email approval monitor.

        Args:
            vault_path: Path to Obsidian vault
        """
        super().__init__(vault_path)

        self.vault_path = Path(vault_path)
        self.approved = self.vault_path / "Approved"
        self.needs_action = self.vault_path / "Needs_Action"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.done = self.vault_path / "Done"

        # Ensure folders exist
        for folder in [self.approved, self.needs_action, self.pending_approval, self.done]:
            folder.mkdir(parents=True, exist_ok=True)

        # Watch for new files
        self._is_running = False
        self.processed_files = []

    def check_for_updates(self) -> list:
        """Check for newly approved emails to send."""
        updates = []

        if not self._is_running:
            return []

        # Get list of markdown files in Approved/
        files = sorted(self.approved.glob("*.md"), key=lambda x: x.stat().st_mtime)

        # Get last processed file ID (for resume capability)
        last_id = self._get_last_processed_id()

        for filepath in files:
            # Skip files we've already processed
            item_id = self._get_item_id(filepath)
            if item_id == last_id:
                continue

            # Only process approved emails
            try:
                content = filepath.read_text(encoding='utf-8')
                frontmatter = self._extract_frontmatter(content)

                # Check if it's an email and approved
                if frontmatter.get("type") == "email" and frontmatter.get("status") == "approved":
                    self.process_approved_email(filepath)
                    updates.append({"id": item_id, "filepath": filepath})
                    self._save_last_processed_id(item_id)

            except Exception as e:
                print(f"[ERROR] Error processing {filepath.name}: {e}")
                self._log_audit_action("email_error", {
                    "file": filepath.name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

        return updates

    def _get_last_processed_id(self) -> str:
        """Get the last processed file ID."""
        last_id_file = self.vault_path / ".email_last_id.txt"
        if last_id_file.exists():
            return last_id_file.read_text().strip()
        return ""

    def _save_last_processed_id(self, item_id: str):
        """Save the last processed file ID."""
        last_id_file = self.vault_path / ".email_last_id.txt"
        with open(last_id_file, "w") as f:
            f.write(item_id)

    def _get_item_id(self, filepath: Path) -> str:
        """Get unique ID for a file."""
        return f"email_{filepath.stat().st_mtime}_{filepath.stem}"

    # BaseWatcher abstract methods (approval monitors don't use these)
    def get_item_id(self, item) -> str:
        """Generate unique ID for item (not used by approval monitors)."""
        return f"email_{datetime.now().timestamp()}"

    def create_action_file(self, item):
        """Create action file (not used by approval monitors - they only process)."""
        pass

    def process_approved_email(self, filepath: Path):
        """
        Process an approved email action - sends the email via MCP.

        Args:
            filepath: Path to approved email file
        """
        try:
            # Read the approval file
            content = filepath.read_text(encoding='utf-8')

            # Extract email details from YAML frontmatter
            email_details = self._extract_email_details_from_frontmatter(content)

            if not email_details or not email_details.get('to'):
                print(f"[ERROR] Could not extract email details from {filepath.name}")
                return

            print(f"\n{'='*60}")
            print(f"EMAIL TO SEND:")
            print(f"{'='*60}")
            print(f"To: {email_details.get('to', 'N/A')}")
            print(f"Subject: {email_details.get('subject', 'N/A')}")
            if email_details.get('body'):
                print(f"Body:\n{email_details.get('body')[:200]}...")
            print(f"{'='*60}\n")

            # Check if MCP client is available
            if EmailMCPClient is None:
                print("[WARNING] MCP client not available. Email will not be sent.")
                print("[INFO] Keeping file in Approved/ for retry when MCP is available.")
                return

            # Get MCP server URL from environment or use default
            mcp_url = os.getenv('EMAIL_MCP_URL', 'http://localhost:3000')

            # Initialize MCP client
            try:
                mcp_client = EmailMCPClient(base_url=mcp_url)

                # Check MCP server health
                if not mcp_client.health_check():
                    print(f"[ERROR] Email MCP server not reachable at {mcp_url}")
                    print("[INFO] Keeping file in Approved/ for retry when MCP server is available.")
                    return

                # Send email via MCP
                print(f"[INFO] Sending email to {email_details.get('to')} via MCP...")
                result = mcp_client.send_email(
                    to=email_details.get('to'),
                    subject=email_details.get('subject'),
                    body=email_details.get('body', ''),
                    cc=email_details.get('cc'),
                    bcc=email_details.get('bcc')
                )

                # Log success
                message_id = result.get('messageId', 'unknown')
                print(f"[SUCCESS] Email sent successfully! Message ID: {message_id}")

                # Log the action
                self._log_audit_action("email_sent_via_mcp", {
                    "file": filepath.name,
                    "to": email_details.get("to"),
                    "subject": email_details.get("subject"),
                    "message_id": message_id,
                    "timestamp": datetime.now().isoformat()
                })

                # Move to Done only after successful send
                self._move_to_done(filepath, success_message=f"Email sent via MCP. Message ID: {message_id}")

            except Exception as mcp_error:
                print(f"[ERROR] Failed to send email via MCP: {mcp_error}")
                print("[INFO] Keeping file in Approved/ for retry on next check.")
                self._log_audit_action("email_mcp_send_failed", {
                    "file": filepath.name,
                    "error": str(mcp_error),
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_audit_action("email_approval_monitor_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_frontmatter(self, content: str) -> dict:
        """Extract YAML frontmatter from email file."""
        if content.startswith('---'):
            try:
                # Find second ---
                end_pos = content.find('---', 3)  # Start from index 3 (after first ---)
                yaml_content = content[3:end_pos]

                # Remove smart quotes and special characters
                yaml_content = yaml_content.replace('“', '').replace('”', '').replace('‘', '').replace('’', '')

                # Parse YAML with safe_load
                data = yaml.safe_load(yaml_content)
                if data:
                    return data
            except Exception as e:
                print(f"[DEBUG] YAML parsing failed: {e}")

        # Fallback: Return empty dict
        return {}

    def _extract_email_details_from_frontmatter(self, content: str) -> dict:
        """
        Extract email details from YAML frontmatter.

        Handles emails with smart quotes and special characters.
        Also handles draft_content from AI-generated drafts.
        Falls back to regex parsing if YAML fails.
        """
        details = {}

        # Extract from YAML frontmatter (should work for most emails)
        try:
            pattern = r'---\n(.*?)\n---'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                yaml_content = match.group(1)

                # Remove smart quotes
                yaml_content = yaml_content.replace('""', '').replace('""', '').replace(''', '').replace(''', '')

                # Parse YAML
                data = yaml.safe_load(yaml_content)
                if data:
                    # Extract to, subject, from fields
                    details['to'] = data.get('to', data.get('to_email', ''))
                    details['subject'] = data.get('subject', '')
                    details['from'] = data.get('from', '')

                    # Check for AI-generated draft first
                    if 'draft_content' in data:
                        details['body'] = data.get('draft_content')
                        details['has_draft'] = True
                        details['draft_generated_at'] = data.get('draft_generated_at', '')
                    else:
                        details['body'] = data.get('body', '')
                        details['has_draft'] = False

                    # Clean up extracted values
                    for key in ['to', 'subject', 'from']:
                        if details.get(key):
                            details[key] = details[key].strip().strip('"\'')  # Remove quotes

                    # Extract body if not in YAML and no draft
                    if not details.get('body') or not details['has_draft']:
                        # Extract from email body content
                        body_match = re.search(r'^# Email:.*?\n\n(.*)$', content, re.MULTILINE | re.DOTALL)
                        if body_match:
                            details['body'] = body_match.group(1).strip()
                            details['has_draft'] = False

                    return details if details.get('to') and details.get('subject') else None
        except Exception as e:
            print(f"[DEBUG] YAML parsing failed: {e}")

        # Fallback: Use regex-based parsing for problematic YAML
        print("[INFO] Using fallback regex parsing for email details...")
        try:
            # Extract key-value pairs using regex
            yaml_part = content[content.find('---')+3:content.find('---', 3)]

            # Extract common fields using regex
            patterns = {
                'to': r'to:\s*(.+?)(?:\n|$)',
                'from': r'from:\s*(.+?)(?:\n|$)',
                'subject': r'subject:\s*(.+?)(?:\n|$)',
                'message_id': r'message_id:\s*(.+?)(?:\n|$)',
                'thread_id': r'thread_id:\s*(.+?)(?:\n|$)',
                'status': r'status:\s*(.+?)(?:\n|$)',
                'draft_content': r'draft_content:\s*(.+?)(?:\n---|\Z)',
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, yaml_part, re.MULTILINE | re.DOTALL)
                if match:
                    value = match.group(1).strip()
                    # Remove quotes if present
                    value = value.strip('"\'').strip()
                    # Clean up trailing whitespace
                    value = value.rstrip()
                    details[key] = value

            # Extract body from email content if not in frontmatter
            if not details.get('draft_content'):
                body_match = re.search(r'^# Email:.*?\n\n(.*)', content, re.MULTILINE | re.DOTALL)
                if body_match:
                    details['body'] = body_match.group(1).strip()
                    details['has_draft'] = False
                else:
                    details['has_draft'] = True if 'draft_content' in details else False

            return details if details.get('to') and details.get('subject') else None
        except Exception as e:
            print(f"[ERROR] Regex parsing also failed: {e}")

        return None

    def _move_to_done(self, filepath: Path, success_message: str = "Processed"):
        """
        Move completed files to Done/ folder.

        Args:
            filepath: Path to file to move
            success_message: Optional success message to log
        """
        done_folder = self.vault_path / "Done"
        done_folder.mkdir(parents=True, exist_ok=True)

        # Move file to Done/
        dest = done_folder / filepath.name
        shutil.move(str(filepath), str(dest))

        print(f"[SUCCESS] Moved {filepath.name} to Done/ - {success_message}")

    def _log_audit_action(self, action_type: str, data: dict):
        """Log action to audit log."""
        try:
            log_dir = self.vault_path / "Logs" / datetime.now().strftime("%Y-%m-%d") / "audit_log.csv"

            # Create folder if doesn't exist
            log_dir.mkdir(parents=True, exist_ok=True)

            # Append to CSV log
            log_file = log_dir / "audit_log.csv"

            with open(log_file, "a", encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()},{action_type},{json.dumps(data)}\n")

        except Exception as e:
            print(f"[WARNING] Could not write to audit log: {e}")

    def run_once(self):
        """Process all approved emails once (for manual testing)."""
        self._is_running = True

        updates = self.check_for_updates()

        if updates:
            print(f"\nProcessing {len(updates)} approved email(s)...")
            for update in updates:
                print(f"  - {update['filepath'].name}")

        print(f"\n✅ Processed {len(updates)} email(s)!")

        self._is_running = False

    def run(self):
        """Main loop for continuous operation."""
        try:
            self._is_running = True

            while self._is_running:
                time.sleep(30)  # Check every 30 seconds

                try:
                    updates = self.check_for_updates()

                    if updates:
                        print(f"\nProcessing {len(updates)} approved email(s)...")
                        for update in updates:
                            print(f"  - {update['filepath'].name}")

                    else:
                        print("[INFO] Waiting for approved emails...")

                except Exception as e:
                    print(f"[ERROR] Error in main loop: {e}")

        except KeyboardInterrupt:
            print("\n\nStopping email approval monitor...")
            self._is_running = False
            print(f"Files processed: {len(self.processed_files)}")
            print("Email approval monitor stopped.")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor Approved/ for new emails to send"
    )

    parser.add_argument("--vault", default="AI_Employee_Vault", help="Path to vault")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Don't actually send emails (just print what would be sent)")

    args = parser.parse_args()

    # Run email approval monitor
    monitor = EmailApprovalMonitor(args.vault)
    monitor.dry_run = args.dry_run

    print("\n" + "="*60)
    print("EMAIL APPROVAL MONITOR")
    print("="*60)
    print(f"Vault: {args.vault}")
    print("Watching: AI_Employee_Vault/Approved/")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("Press Ctrl+C to stop\n")

    # Run continuously
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\nEmail approval monitor stopped.")


if __name__ == "__main__":
    main()