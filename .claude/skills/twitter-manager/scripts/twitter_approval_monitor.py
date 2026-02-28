#!/usr/bin/env python3
"""
Twitter (X) Approval Monitor

Watches the /Approved/ folder for approved Twitter posts and publishes them
to Twitter (X) using the stealth automation approach.

This is the human-in-the-loop component - it only posts after you approve.

Usage:
    python twitter_approval_monitor.py --vault .
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


class TwitterApprovalMonitor:
    """
    Monitors the Approved/ folder for Twitter posts using polling.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / "Approved"
        self.done_folder = self.vault_path / "Done"
        self.logs_folder = self.vault_path / "Logs"
        # Check TWITTER_DRY_RUN environment variable, default to dry_run parameter
        env_dry_run = os.getenv('TWITTER_DRY_RUN', 'true').lower() == 'true'
        self.dry_run = dry_run or env_dry_run
        self._is_running = False
        self.processed_files = set()

        # Ensure folders exist
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def check_for_updates(self) -> list:
        """Check for newly approved Twitter posts."""
        updates = []

        if not self._is_running:
            return updates

        # Get list of markdown files in Approved/
        patterns = ["TWITTER_POST_", "TWEET_", "X_POST_"]
        files = []
        for pattern in patterns:
            files.extend(self.approved_folder.glob(f"{pattern}*.md"))

        for filepath in files:
            # Skip files we've already processed
            if str(filepath) in self.processed_files:
                continue

            print(f"\n[OK] Detected approved Twitter post: {filepath.name}")
            self.process_approved_post(filepath)
            self.processed_files.add(str(filepath))
            updates.append(filepath)

        return updates

    def process_approved_post(self, filepath: Path):
        """
        Process an approved Twitter post.

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
            print(f"TWITTER POST DETAILS:")
            print(f"{'='*60}")
            print(f"Content:\n{post_details.get('content', '')[:280]}...")
            reply_to = post_details.get('reply_to')
            if reply_to:
                print(f"Reply To: @{reply_to}")
            print(f"{'='*60}\n")

            # Log the action
            self._log_action("twitter_post_approved", {
                "file": filepath.name,
                "content_length": len(post_details.get('content', '')),
                "reply_to": reply_to,
                "timestamp": datetime.now().isoformat()
            })

            if self.dry_run:
                print("[DRY RUN] Would post to Twitter")
                self._move_to_done(filepath)
                return

            # Publish to Twitter
            print("[INFO] Publishing to Twitter (X)...")
            success = self._publish_to_twitter(post_details)

            if success:
                print("[OK] Successfully published to Twitter!")
                self._log_action("twitter_post_published", {
                    "file": filepath.name,
                    "reply_to": reply_to,
                    "timestamp": datetime.now().isoformat(),
                    "result": "success"
                })

                # Generate summary
                self._generate_summary(post_details)

                self._move_to_done(filepath)
            else:
                print("[ERROR] Failed to publish to Twitter")
                self._log_action("twitter_post_failed", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "failed"
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_action("twitter_post_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_post_details(self, content: str) -> dict:
        """
        Extract post details from approval file.

        Returns:
            Dictionary with 'content', 'reply_to' keys
        """
        details = {}

        # Extract reply_to if present
        reply_match = re.search(r'reply_to:\s*(.+)', content)
        if reply_match:
            details['reply_to'] = reply_match.group(1).strip().strip('@')

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

    def _publish_to_twitter(self, post_details: dict) -> bool:
        """
        Publish content to Twitter using the Twitter MCP server wrapper.

        Args:
            post_details: Dictionary with content and optional reply_to

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the MCP wrapper script path
            vault_root = self.vault_path.parent if self.vault_path.name == "AI_Employee_Vault" else self.vault_path
            mcp_wrapper = vault_root / "mcp-servers" / "twitter-mcp" / "call_post_tool.js"

            if not mcp_wrapper.exists():
                print(f"[ERROR] Twitter MCP wrapper not found: {mcp_wrapper}")
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
            # Pass through TWITTER_DRY_RUN setting
            if self.dry_run:
                env['TWITTER_DRY_RUN'] = 'true'
            else:
                env['TWITTER_DRY_RUN'] = 'false'

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
                    print(f"[MCP] {response.get('message', 'Posted to Twitter')}")
                except json.JSONDecodeError:
                    print(result.stdout)

            if result.stderr:
                for line in result.stderr.split('\n'):
                    if line.strip():
                        print(f"[MCP] {line}")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("[ERROR] Twitter MCP call timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Error calling Twitter MCP: {e}")
            return False

    def _generate_summary(self, post_details: dict):
        """
        Generate a summary of the published tweet.

        Creates a summary markdown file in Briefings/ folder.
        """
        try:
            briefings_folder = self.vault_path / "Briefings"
            briefings_folder.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = briefings_folder / f"Twitter_Post_Summary_{timestamp}.md"

            content = post_details.get('content', '')
            content_preview = content[:280]  # Twitter character limit

            reply_to = post_details.get('reply_to', '')

            summary_content = f"""---
type: twitter_post_summary
created: {datetime.now().isoformat()}
---

# Twitter Post Summary

## Published At
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Post Type
{'Reply to @' + reply_to if reply_to else 'New Tweet'}

## Content
{content_preview}

## Character Count
{len(content)} / 280

## Status
Successfully published to Twitter (X)

## Next Steps
- [ ] Monitor engagement (likes, retweets, replies)
- [ ] Respond to mentions within 24 hours
- [ ] Analyze performance after 7 days
- [ ] Update content strategy based on results

---

*Generated by Twitter Approval Monitor*
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
            "component": "twitter_approval_monitor",
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
                        print("[INFO] Waiting for approved Twitter posts...")

                except Exception as e:
                    print(f"[ERROR] Error in main loop: {e}")

        except KeyboardInterrupt:
            print("\n\n[INFO] Stopping Twitter approval monitor...")
            self._is_running = False
            print("[OK] Monitor stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor /Approved/ folder and publish Twitter posts"
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
    monitor = TwitterApprovalMonitor(args.vault, args.dry_run)

    print("=" * 60)
    print("Twitter (X) Approval Monitor")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Watching: {approved_folder}")
    print(f"Mode: {'DRY RUN' if monitor.dry_run else 'LIVE'}")
    print("Polling interval: 30 seconds")
    print("=" * 60)
    print("\n[INFO] Waiting for approved posts...")
    print("[INFO] Press Ctrl+C to stop\n")

    # Run continuous polling
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n[OK] Monitor stopped")


if __name__ == "__main__":
    main()
