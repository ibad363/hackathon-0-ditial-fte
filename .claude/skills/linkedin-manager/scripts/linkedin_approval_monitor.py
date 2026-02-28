#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Approval Monitor

Watches the /Approved/ folder for approved LinkedIn posts and publishes them.
This is the human-in-the-loop component - it only posts after you approve.

Usage:
    python linkedin_approval_monitor.py --vault .
"""

import sys
import time
import subprocess
import argparse
import os
import re
from pathlib import Path
from datetime import datetime

# Import Chrome CDP helper
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "scripts"))
from chrome_cdp_helper import ensure_chrome_cdp

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


class LinkedInApprovalMonitor:
    """
    Monitors the Approved/ folder for LinkedIn posts using polling.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / "Approved"
        self.done_folder = self.vault_path / "Done"
        self.logs_folder = self.vault_path / "Logs"
        # Check LINKEDIN_DRY_RUN environment variable, default to dry_run parameter
        env_dry_run = os.getenv('LINKEDIN_DRY_RUN', 'true').lower() == 'true'
        self.dry_run = dry_run or env_dry_run
        self._is_running = False
        self.processed_files = set()

        # Ensure folders exist
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def check_for_updates(self) -> list:
        """Check for newly approved LinkedIn posts."""
        updates = []

        if not self._is_running:
            return updates

        # Get list of markdown files in Approved/
        files = list(self.approved_folder.glob("LINKEDIN_POST_*.md"))

        for filepath in files:
            # Skip files we've already processed
            if str(filepath) in self.processed_files:
                continue

            print(f"\n[OK] Detected approved post: {filepath.name}")
            self.process_approved_post(filepath)
            self.processed_files.add(str(filepath))
            updates.append(filepath)

        return updates

    def process_approved_post(self, filepath: Path):
        """
        Process an approved LinkedIn post.

        Args:
            filepath: Path to approved post file
        """
        try:
            # Read the approval file
            content = filepath.read_text(encoding='utf-8')

            # Extract the post content from between the ```
            post_content = self._extract_post_content(content)

            if not post_content:
                print(f"[ERROR] Could not extract post content from {filepath.name}")
                return

            print(f"\n{'='*60}")
            print(f"POST CONTENT TO PUBLISH:")
            print(f"{'='*60}")
            print(post_content)  # safe_print handles encoding
            print(f"{'='*60}\n")

            # Log the action
            self._log_action("linkedin_post_approved", {
                "file": filepath.name,
                "content_length": len(post_content),
                "timestamp": datetime.now().isoformat()
            })

            if self.dry_run:
                print("[DRY RUN] Would post to LinkedIn")
                self._move_to_done(filepath)
                return

            # Publish to LinkedIn
            print("[INFO] Publishing to LinkedIn...")
            success = self._publish_to_linkedin(post_content)

            if success:
                print("[OK] Successfully published to LinkedIn!")
                self._log_action("linkedin_post_published", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "success"
                })

                # Generate summary
                self._generate_summary(post_content)

                self._move_to_done(filepath)
            else:
                print("[ERROR] Failed to publish to LinkedIn")
                self._log_action("linkedin_post_failed", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "failed"
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_action("linkedin_post_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_post_content(self, content: str) -> str:
        """Extract post content from approval file."""
        # First, try to find content between code blocks (```...```)
        match = re.search(r'```(.+?)```', content, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Look for ## LinkedIn Post section (for research-generated posts)
        linkedin_post_match = re.search(r'## LinkedIn Post\s*\n+(.+?)(?=\n##|\n#|$)', content, re.DOTALL)
        if linkedin_post_match:
            post_text = linkedin_post_match.group(1).strip()
            # Remove the title line if present (e.g., "# LinkedIn Post: topic")
            post_text = re.sub(r'^# LinkedIn Post:.+\n?', '', post_text)
            # Clean up any trailing metadata
            # Remove everything after first hashtag line (sources section usually follows)
            lines = post_text.split('\n')
            content_lines = []
            for line in lines:
                # Stop at sources section
                if line.startswith('## Sources') or line.startswith('## Sources:'):
                    break
                content_lines.append(line)
            return '\n'.join(content_lines).strip()

        # If no code blocks, look for content after the frontmatter
        # Split by "---" to get the content section after frontmatter
        parts = content.split('---')
        if len(parts) >= 3:
            # Everything after the second "---" is content
            content_section = '---'.join(parts[2:]).strip()

            # Remove metadata sections by stopping at certain headers
            # Stop at: ## Metadata, ## Approval Required, ## To Reject, ## Sources, ---
            lines = content_section.split('\n')
            content_lines = []

            for line in lines:
                # Stop at metadata sections
                if line.startswith('## Metadata') or line.startswith('## Approval Required') or line.startswith('## To Reject') or line.startswith('## Sources'):
                    break
                # Stop at another frontmatter
                if line.strip() == '---':
                    break

                content_lines.append(line)

            # Join and clean up
            result = '\n'.join(content_lines).strip()

            # Remove leading/trailing empty lines and the ## Content header if present
            result = re.sub(r'^## Content\s*\n', '', result)
            result = result.strip()

            if result:
                return result

        return None

    def _publish_to_linkedin(self, content: str) -> bool:
        """
        Publish content to LinkedIn using the LinkedIn MCP server wrapper.

        Args:
            content: Post content

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the MCP wrapper script path
            vault_root = self.vault_path.parent if self.vault_path.name == "AI_Employee_Vault" else self.vault_path
            mcp_wrapper = vault_root / "mcp-servers" / "linkedin-mcp" / "call_post_tool.js"

            if not mcp_wrapper.exists():
                print(f"[ERROR] LinkedIn MCP wrapper not found: {mcp_wrapper}")
                return False

            # Add extra space after hashtags for better formatting
            if content and content.endswith('#'):
                # Already has trailing space after hashtag
                pass
            elif content:
                # Check if content ends with hashtags and add space
                # Match hashtags at the end of content
                hashtag_pattern = r'(?:\s*#[\w]+)+\s*$'
                if re.search(hashtag_pattern, content):
                    # Content ends with hashtags, add extra space
                    content = content.rstrip() + '  '

            # Call the MCP wrapper via Node.js
            env = os.environ.copy()
            # Pass through LINKEDIN_DRY_RUN setting
            if self.dry_run:
                env['LINKEDIN_DRY_RUN'] = 'true'
            else:
                env['LINKEDIN_DRY_RUN'] = 'false'

            result = subprocess.run(
                ["node", str(mcp_wrapper), content],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                timeout=180  # 3 minutes timeout
            )

            # Print output for visibility
            # The wrapper outputs JSON to stdout, logs to stderr
            if result.stdout:
                # Parse JSON result
                try:
                    import json
                    response = json.loads(result.stdout.strip())
                    print(f"[MCP] {response.get('message', 'Posted to LinkedIn')}")
                except json.JSONDecodeError:
                    print(result.stdout)

            if result.stderr:
                # MCP server logs to stderr
                for line in result.stderr.split('\n'):
                    if line.strip():
                        print(f"[MCP] {line}")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("[ERROR] LinkedIn MCP call timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Error calling LinkedIn MCP: {e}")
            return False

    def _generate_summary(self, post_content: str):
        """
        Generate a summary of the published LinkedIn post.

        Creates a summary markdown file in Briefings/ folder.
        """
        try:
            briefings_folder = self.vault_path / "Briefings"
            briefings_folder.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = briefings_folder / f"LinkedIn_Post_Summary_{timestamp}.md"

            content_preview = post_content[:200] + "..." if len(post_content) > 200 else post_content

            # Count hashtags
            hashtag_count = post_content.count('#')

            summary_content = f"""---
type: linkedin_post_summary
platform: LinkedIn
created: {datetime.now().isoformat()}
---

# LinkedIn Post Summary

## Published At
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Platform
- LinkedIn (Professional Network)

## Content Preview
{content_preview}

## Full Content
{post_content}

## Character Count
{len(post_content)} characters

## Hashtags
{hashtag_count} hashtags detected

## Status
Successfully published to LinkedIn

## Next Steps
- [ ] Monitor engagement (likes, comments, shares)
- [ ] Respond to comments within 24 hours
- [ ] Analyze performance after 7 days
- [ ] Update content strategy based on results

## Professional Metrics
Track these metrics over time:
- Connection views
- Post impressions
- Engagement rate
- Comment sentiment
- Share count

---

*Generated by LinkedIn Approval Monitor*
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
            "component": "linkedin_approval_monitor",
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
                        print("[INFO] Waiting for approved LinkedIn posts...")

                except Exception as e:
                    print(f"[ERROR] Error in main loop: {e}")

        except KeyboardInterrupt:
            print("\n\n[INFO] Stopping LinkedIn approval monitor...")
            self._is_running = False
            print("[OK] Monitor stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor /Approved/ folder and publish LinkedIn posts"
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
    monitor = LinkedInApprovalMonitor(args.vault, args.dry_run)

    print("=" * 60)
    print("LinkedIn Approval Monitor")
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
