#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Approval Monitor

Watches the /Approved/ folder for approved WhatsApp responses and sends them.
This is the human-in-the-loop component - it only sends messages after you approve.

Usage:
    python whatsapp_approval_monitor.py --vault .
"""

import sys
import time
import subprocess
import argparse
import os
import re
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    # Save original print before overriding
    _original_print = print

    # Create a safe print function that handles Unicode encoding errors
    def safe_print(*args, **kwargs):
        """Print function that safely handles Unicode characters on Windows."""
        # Convert all args to strings safely
        safe_args = []
        for arg in args:
            try:
                # Try to encode as ASCII with replacement for unsupported chars
                safe_args.append(str(arg).encode('ascii', 'replace').decode('ascii'))
            except:
                safe_args.append(str(arg))
        _original_print(*safe_args, **kwargs)

    # Override print for this module
    print = safe_print


class WhatsAppApprovalMonitor:
    """
    Monitors the Approved/ folder for WhatsApp responses using polling.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / "Approved"
        self.done_folder = self.vault_path / "Done"
        self.logs_folder = self.vault_path / "Logs"
        # Check WHATSAPP_DRY_RUN environment variable, default to dry_run parameter
        env_dry_run = os.getenv('WHATSAPP_DRY_RUN', 'true').lower() == 'true'
        self.dry_run = dry_run or env_dry_run
        self._is_running = False
        self.processed_files = set()

        # Ensure folders exist
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def check_for_updates(self) -> list:
        """Check for newly approved WhatsApp responses."""
        updates = []

        if not self._is_running:
            return updates

        # Get list of markdown files in Approved/
        files = list(self.approved_folder.glob("WHATSAPP_*.md"))

        for filepath in files:
            # Skip files we've already processed
            if str(filepath) in self.processed_files:
                continue

            print(f"\n[OK] Detected approved WhatsApp response: {filepath.name}")
            self.process_approved_response(filepath)
            self.processed_files.add(str(filepath))
            updates.append(filepath)

        return updates

    def process_approved_response(self, filepath: Path):
        """
        Process an approved WhatsApp response.

        Args:
            filepath: Path to approved response file
        """
        try:
            # Read the approval file
            content = filepath.read_text(encoding='utf-8')

            # Extract response details
            response_details = self._extract_response_details(content)

            if not response_details:
                print(f"[ERROR] Could not extract response details from {filepath.name}")
                return

            contact = response_details.get('contact', '')
            message = response_details.get('message', '')

            print(f"\n{'='*60}")
            print(f"WHATSAPP RESPONSE DETAILS:")
            print(f"{'='*60}")
            print(f"To: {contact}")
            print(f"Message:\n{message}")
            print(f"{'='*60}\n")

            # Log the action
            self._log_action("whatsapp_response_approved", {
                "file": filepath.name,
                "contact": contact,
                "message_length": len(message),
                "timestamp": datetime.now().isoformat()
            })

            if self.dry_run:
                print("[DRY RUN] Would send WhatsApp message")
                self._move_to_done(filepath)
                return

            # Send via WhatsApp
            print("[INFO] Sending WhatsApp message...")
            success = self._send_whatsapp_message(response_details)

            if success:
                print("[OK] Successfully sent WhatsApp message!")
                self._log_action("whatsapp_message_sent", {
                    "file": filepath.name,
                    "contact": contact,
                    "timestamp": datetime.now().isoformat(),
                    "result": "success"
                })

                # Generate summary
                self._generate_summary(response_details)

                self._move_to_done(filepath)
            else:
                print("[ERROR] Failed to send WhatsApp message")
                self._log_action("whatsapp_message_failed", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "failed"
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_action("whatsapp_response_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_response_details(self, content: str) -> dict:
        """
        Extract response details from approval file.

        Returns:
            Dictionary with 'contact', 'message' keys
        """
        details = {}

        # First, try to extract from frontmatter
        contact_match = re.search(r'contact:\s*(.+)', content, re.IGNORECASE)
        if contact_match:
            details['contact'] = contact_match.group(1).strip()

        # Extract message between ```
        content_match = re.search(r'```(.+?)```', content, re.DOTALL)
        if content_match:
            details['message'] = content_match.group(1).strip()
        else:
            # Fallback: extract content after frontmatter, stopping at metadata
            parts = content.split('---')
            if len(parts) >= 3:
                content_section = '---'.join(parts[2:]).strip()

                # Stop at metadata sections
                lines = content_section.split('\n')
                content_lines = []

                for line in lines:
                    # Stop at metadata sections
                    if line.startswith('## Metadata') or line.startswith('## Approval Required') or line.startswith('## To Reject'):
                        break
                    if line.strip() == '---':
                        break
                    content_lines.append(line)

                result = '\n'.join(content_lines).strip()
                # Remove ## Content header if present
                result = re.sub(r'^## Content\s*\n', '', result)
                result = result.strip()

                if result:
                    details['message'] = result
                else:
                    return None
            else:
                return None

        # If contact not in frontmatter, try to extract from message content
        if 'contact' not in details:
            # Look for patterns like "To: John" or "@John" at the start of message
            message = details.get('message', '')
            to_match = re.search(r'^(?:To:\s*|@)(.+?)\n', message, re.IGNORECASE)
            if to_match:
                details['contact'] = to_match.group(1).strip()
                # Remove the "To:" line from the message
                details['message'] = re.sub(r'^(?:To:\s*|@).+?\n', '', message, flags=re.IGNORECASE).strip()
            else:
                # No contact found - mark as error
                print("[ERROR] No contact specified in WhatsApp response")
                return None

        return details

    def _send_whatsapp_message(self, response_details: dict) -> bool:
        """
        Send message via WhatsApp using the WhatsApp MCP server.

        Args:
            response_details: Dictionary with contact and message

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the MCP wrapper script path
            vault_root = self.vault_path.parent if self.vault_path.name == "AI_Employee_Vault" else self.vault_path
            mcp_wrapper = vault_root / "mcp-servers" / "whatsapp-mcp" / "call_send_tool.js"

            if not mcp_wrapper.exists():
                print(f"[ERROR] WhatsApp MCP wrapper not found: {mcp_wrapper}")
                return False

            contact = response_details.get('contact', '')
            message = response_details.get('message', '')

            # Call the MCP wrapper via Node.js
            env = os.environ.copy()
            # Pass through WHATSAPP_DRY_RUN setting
            if self.dry_run:
                env['WHATSAPP_DRY_RUN'] = 'true'
            else:
                env['WHATSAPP_DRY_RUN'] = 'false'

            result = subprocess.run(
                ["node", str(mcp_wrapper), contact, message],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                timeout=180  # 3 minutes timeout
            )

            # Print output for visibility
            if result.stdout:
                try:
                    import json
                    response = json.loads(result.stdout.strip())
                    print(f"[MCP] {response.get('message', 'Sent via WhatsApp')}")
                except json.JSONDecodeError:
                    print(result.stdout)

            if result.stderr:
                for line in result.stderr.split('\n'):
                    if line.strip():
                        print(f"[MCP] {line}")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("[ERROR] WhatsApp MCP call timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Error calling WhatsApp MCP: {e}")
            return False

    def _generate_summary(self, response_details: dict):
        """
        Generate a summary of the sent WhatsApp message.

        Creates a summary markdown file in Briefings/ folder.
        """
        try:
            briefings_folder = self.vault_path / "Briefings"
            briefings_folder.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = briefings_folder / f"WhatsApp_Message_Summary_{timestamp}.md"

            contact = response_details.get('contact', '')
            message = response_details.get('message', '')
            message_preview = message[:200] + "..." if len(message) > 200 else message

            summary_content = f"""---
type: whatsapp_message_summary
platform: WhatsApp
created: {datetime.now().isoformat()}
---

# WhatsApp Message Summary

## Sent At
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Platform
- WhatsApp (Messaging)

## Recipient
{contact}

## Message Preview
{message_preview}

## Full Message
{message}

## Character Count
{len(message)} characters

## Status
Successfully sent via WhatsApp

## Next Steps
- [ ] Wait for response
- [ ] Follow up if no response within 24 hours
- [ ] Archive conversation if resolved

---
*Generated by WhatsApp Approval Monitor*
"""

            summary_file.write_text(summary_content, encoding='utf-8')
            print(f"[OK] Generated summary: {summary_file.name}")

        except Exception as e:
            print(f"[ERROR] Could not generate summary: {e}")

    def _move_to_done(self, filepath: Path):
        """Move processed file to Done folder."""
        try:
            done_path = self.done_folder / filepath.name
            filepath.rename(done_path)
            print(f"[OK] Moved to Done: {done_path.name}")
        except Exception as e:
            print(f"[ERROR] Could not move to Done: {e}")

    def _log_action(self, action: str, details: dict):
        """Log action to daily log file."""
        log_file = self.logs_folder / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        import json

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": "whatsapp_approval_monitor",
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
                        print(f"\n[INFO] Processing {len(updates)} approved response(s)...")
                    else:
                        print("[INFO] Waiting for approved WhatsApp responses...")

                except Exception as e:
                    print(f"[ERROR] Error in main loop: {e}")

        except KeyboardInterrupt:
            print("\n\n[INFO] Stopping WhatsApp approval monitor...")
            self._is_running = False
            print("[OK] Monitor stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor /Approved/ folder and send WhatsApp messages"
    )

    parser.add_argument(
        "--vault",
        default=".",
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
    monitor = WhatsAppApprovalMonitor(args.vault, args.dry_run)

    print("=" * 60)
    print("WhatsApp Approval Monitor")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Watching: {approved_folder}")
    print(f"Mode: {'DRY RUN' if monitor.dry_run else 'LIVE'}")
    print("Polling interval: 30 seconds")
    print("=" * 60)
    print("\n[INFO] Waiting for approved responses...")
    print("[INFO] Press Ctrl+C to stop\n")

    # Run continuous polling
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n[OK] Monitor stopped")


if __name__ == "__main__":
    main()
