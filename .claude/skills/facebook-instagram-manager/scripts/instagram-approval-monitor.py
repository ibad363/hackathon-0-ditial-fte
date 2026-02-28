#!/usr/bin/env python3
"""
Instagram Approval Monitor

Watches the /Approved/ folder for approved Instagram posts and publishes them.

This is the human-in-the-loop component - it only posts after you approve.

Usage:
    python instagram-approval-monitor.py --vault .
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
    _original_print = print

    def safe_print(*args, **kwargs):
        """Print function that safely handles Unicode characters on Windows."""
        safe_args = []
        for arg in args:
            try:
                safe_args.append(str(arg).encode('ascii', 'replace').decode('ascii'))
            except (UnicodeEncodeError, UnicodeDecodeError):
                safe_args.append(str(arg))
        _original_print(*safe_args, **kwargs)

    print = safe_print


class InstagramApprovalMonitor:
    """
    Monitors the Approved/ folder for Instagram posts using polling.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / "Approved"
        self.done_folder = self.vault_path / "Done"
        self.logs_folder = self.vault_path / "Logs"
        # Check INSTAGRAM_DRY_RUN environment variable, default to dry_run parameter
        env_dry_run = os.getenv('INSTAGRAM_DRY_RUN', 'true').lower() == 'true'
        self.dry_run = dry_run or env_dry_run
        self._is_running = False
        self.processed_files = set()

        # Ensure folders exist
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def check_for_updates(self) -> list:
        """Check for newly approved Instagram posts."""
        updates = []

        if not self._is_running:
            return updates

        # Get list of markdown files in Approved/
        files = list(self.approved_folder.glob("INSTAGRAM_POST_*.md"))

        for filepath in files:
            # Skip files we've already processed
            if str(filepath) in self.processed_files:
                continue

            print(f"\n[OK] Detected approved Instagram post: {filepath.name}")
            self.process_approved_post(filepath)
            self.processed_files.add(str(filepath))
            updates.append(filepath)

        return updates

    def process_approved_post(self, filepath: Path):
        """
        Process an approved Instagram post.

        Args:
            filepath: Path to approved post file
        """
        try:
            # Read the approval file
            content = filepath.read_text(encoding='utf-8')

            # Extract post details
            post_details = self._extract_post_details(content)

            if not post_details:
                print(f"[ERROR] Could not extract post details from {filepath.name}")
                return

            print(f"\n{'='*60}")
            print(f"INSTAGRAM POST DETAILS:")
            print(f"{'='*60}")
            print(f"Content:\n{post_details.get('content', '')[:200]}...")
            print(f"{'='*60}\n")

            # Log the action
            self._log_action("instagram_post_approved", {
                "file": filepath.name,
                "content_length": len(post_details.get('content', '')),
                "timestamp": datetime.now().isoformat()
            })

            if self.dry_run:
                print("[DRY RUN] Would post to Instagram")
                self._move_to_done(filepath)
                return

            # Publish to Instagram
            print("[INFO] Publishing to Instagram...")
            print("[ART] Generating professional image from text...")
            success = self._publish_to_instagram(post_details)

            if success:
                print("[OK] Successfully published to Instagram!")
                self._log_action("instagram_post_published", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "success"
                })

                # Generate summary
                self._generate_summary(post_details)

                self._move_to_done(filepath)
            else:
                print("[ERROR] Failed to publish to Instagram")
                self._log_action("instagram_post_failed", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "failed"
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_action("instagram_post_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_post_details(self, content: str) -> dict:
        """
        Extract post details from approval file.

        Returns:
            Dictionary with 'content' key
        """
        details = {}

        # Extract content between ```
        content_match = re.search(r'```(.+?)```', content, re.DOTALL)
        if content_match:
            details['content'] = content_match.group(1).strip()
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
                    details['content'] = result
                else:
                    return None
            else:
                return None

        return details

    def _publish_to_instagram(self, post_details: dict) -> bool:
        """
        Publish content to Instagram using the Instagram MCP server wrapper.

        Args:
            post_details: Dictionary with content

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the MCP wrapper script path
            vault_path_abs = self.vault_path.resolve()
            vault_root = vault_path_abs.parent if vault_path_abs.name == "AI_Employee_Vault" else vault_path_abs
            mcp_wrapper = vault_root / "mcp-servers" / "instagram-mcp" / "call_post_tool.js"

            if not mcp_wrapper.exists():
                print(f"[ERROR] Instagram MCP wrapper not found: {mcp_wrapper}")
                return False

            # Get content
            content = post_details.get('content', '')

            # Add extra space after hashtags for better formatting
            if content and content.endswith('#'):
                # Already has trailing space after hashtag
                pass
            elif content:
                # Check if content ends with hashtags and add space
                import re
                # Match hashtags at the end of content
                hashtag_pattern = r'(?:\s*#[\w]+)+\s*$'
                if re.search(hashtag_pattern, content):
                    # Content ends with hashtags, add extra space
                    content = content.rstrip() + '  '

            # Call the MCP wrapper via Node.js
            env = os.environ.copy()
            # Pass through INSTAGRAM_DRY_RUN setting
            if self.dry_run:
                env['INSTAGRAM_DRY_RUN'] = 'true'
            else:
                env['INSTAGRAM_DRY_RUN'] = 'false'

            result = subprocess.run(
                ["node", str(mcp_wrapper), content],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                timeout=180
            )

            # Print output for visibility
            if result.stdout:
                try:
                    import json
                    response = json.loads(result.stdout.strip())
                    print(f"[MCP] {response.get('message', 'Posted to Instagram')}")
                except json.JSONDecodeError:
                    print(result.stdout)

            if result.stderr:
                for line in result.stderr.split('\n'):
                    if line.strip():
                        print(f"[MCP] {line}")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("[ERROR] Instagram MCP call timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Error calling Instagram MCP: {e}")
            return False

    def _generate_summary(self, post_details: dict):
        """
        Generate a summary of the published Instagram post.

        Creates a summary markdown file in Briefings/ folder.
        """
        try:
            briefings_folder = self.vault_path / "Briefings"
            briefings_folder.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = briefings_folder / f"Instagram_Post_Summary_{timestamp}.md"

            content = post_details.get('content', '')
            content_preview = content[:200] + "..." if len(content) > 200 else content

            summary_content = f"""---
type: instagram_post_summary
platform: Instagram
created: {datetime.now().isoformat()}
---

# Instagram Post Summary

## Published At
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Platform
- Instagram

## Content Preview
{content_preview}

## Full Content
{content}

## Status
✅ Successfully published

## Next Steps
- [ ] Monitor engagement (likes, comments, saves)
- [ ] Respond to comments within 24 hours
- [ ] Analyze performance after 7 days
- [ ] Update content strategy based on results

## Hashtag Performance
Track which hashtags drove the most engagement.

---

*Generated by Instagram Approval Monitor*
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
            "component": "instagram_approval_monitor",
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
                        print(f"\n[INFO] Processing {len(updates)} approved post(s)...")
                    else:
                        print("[INFO] Waiting for approved Instagram posts...")

                except Exception as e:
                    print(f"[ERROR] Error in main loop: {e}")

        except KeyboardInterrupt:
            print("\n\n[INFO] Stopping Instagram approval monitor...")
            self._is_running = False
            print("[OK] Monitor stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor /Approved/ folder and publish Instagram posts"
    )

    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't actually post"
    )

    args = parser.parse_args()

    vault_path = Path(args.vault)
    approved_folder = vault_path / "Approved"
    approved_folder.mkdir(parents=True, exist_ok=True)

    # Create monitor
    monitor = InstagramApprovalMonitor(args.vault, args.dry_run)

    print("=" * 60)
    print("Instagram Approval Monitor")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Watching: {approved_folder}")
    print(f"Mode: {'DRY RUN' if monitor.dry_run else 'LIVE'}")
    print("Polling interval: 30 seconds")
    print("=" * 60)
    print("\n[INFO] Waiting for approved Instagram posts...")
    print("[INFO] Press Ctrl+C to stop\n")

    # Run continuous polling
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n[OK] Monitor stopped")


if __name__ == "__main__":
    main()
