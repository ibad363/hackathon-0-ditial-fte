#!/usr/bin/env python3
"""
Meta (Facebook & Instagram) Approval Monitor

Watches the /Approved/ folder for approved Meta posts and publishes them
to Facebook and Instagram via Meta Business Suite.

This is the human-in-the-loop component - it only posts after you approve.

Usage:
    python meta_approval_monitor.py --vault .
"""

import sys
import time
import subprocess
import argparse
import os
import re
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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


class MetaApprovalHandler(FileSystemEventHandler):
    """
    Handles approved Meta (Facebook & Instagram) post files.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / "Approved"
        self.done_folder = self.vault_path / "Done"
        self.logs_folder = self.vault_path / "Logs"
        # Check for Facebook or Instagram DRY_RUN environment variables
        # This monitor handles both platforms, so check both
        facebook_dry_run = os.getenv('FACEBOOK_DRY_RUN', 'true').lower() == 'true'
        instagram_dry_run = os.getenv('INSTAGRAM_DRY_RUN', 'true').lower() == 'true'
        # Use dry_run parameter OR both platform settings
        env_dry_run = facebook_dry_run and instagram_dry_run
        self.dry_run = dry_run or env_dry_run

        # Ensure folders exist
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        """Called when a file is created in /Approved/ folder."""
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Only process Meta approval files
        if not filepath.name.startswith(("FACEBOOK_POST_", "INSTAGRAM_POST_", "META_POST_")):
            return

        if not filepath.suffix == ".md":
            return

        print(f"\n[OK] Detected approved Meta post: {filepath.name}")
        self.process_approved_post(filepath)

    def process_approved_post(self, filepath: Path):
        """
        Process an approved Meta post.

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
            print(f"METa POST DETAILS:")
            print(f"{'='*60}")
            print(f"Platforms: {post_details.get('platforms', 'Facebook, Instagram')}")
            print(f"Content:\n{post_details.get('content', '')[:200]}...")
            print(f"{'='*60}\n")

            # Log the action
            self._log_action("meta_post_approved", {
                "file": filepath.name,
                "platforms": post_details.get('platforms'),
                "content_length": len(post_details.get('content', '')),
                "timestamp": datetime.now().isoformat()
            })

            if self.dry_run:
                print("[DRY RUN] Would post to Meta Business Suite")
                self._move_to_done(filepath)
                return

            # Publish to Meta Business Suite
            print("[INFO] Publishing to Meta Business Suite...")
            success = self._publish_to_meta(post_details)

            if success:
                print("[OK] Successfully published to Meta!")
                self._log_action("meta_post_published", {
                    "file": filepath.name,
                    "platforms": post_details.get('platforms'),
                    "timestamp": datetime.now().isoformat(),
                    "result": "success"
                })

                # Generate summary
                self._generate_summary(post_details)

                self._move_to_done(filepath)
            else:
                print("[ERROR] Failed to publish to Meta")
                self._log_action("meta_post_failed", {
                    "file": filepath.name,
                    "timestamp": datetime.now().isoformat(),
                    "result": "failed"
                })

        except Exception as e:
            print(f"[ERROR] Error processing {filepath.name}: {e}")
            self._log_action("meta_post_error", {
                "file": filepath.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _extract_post_details(self, content: str) -> dict:
        """
        Extract post details from approval file.

        Returns:
            Dictionary with 'content', 'platforms', 'media' keys
        """
        details = {}

        # Extract platforms from frontmatter
        # Try platforms: [Instagram] format first
        platforms_match = re.search(r'platforms:\s*\[([^\]]+)\]', content)
        if platforms_match:
            platforms_str = platforms_match.group(1)
            details['platforms'] = [p.strip().strip('"\'') for p in platforms_str.split(',')]
        else:
            # Try platform: instagram (single value) format
            platform_match = re.search(r'platform:\s*(\w+)', content)
            if platform_match:
                platform = platform_match.group(1).strip()
                # Capitalize first letter
                platform = platform.capitalize()
                details['platforms'] = [platform]
            else:
                # Default to both platforms
                details['platforms'] = ['Facebook', 'Instagram']

        # Extract media if present
        media_match = re.search(r'media:\s*(.+)', content)
        if media_match:
            details['media'] = media_match.group(1).strip()

        # Extract content between ```
        content_match = re.search(r'```(.+?)```', content, re.DOTALL)
        if content_match:
            details['content'] = content_match.group(1).strip()
        else:
            # Fallback: try to find content after "## Content"
            fallback_match = re.search(r'## Content\s*\n+(.+?)(?=##|\Z)', content, re.DOTALL)
            if fallback_match:
                details['content'] = fallback_match.group(1).strip()
            else:
                return None

        return details

    def _publish_to_meta(self, post_details: dict) -> bool:
        """
        Publish content to Meta platforms using the appropriate poster script.

        Args:
            post_details: Dictionary with content and platforms

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the poster script path
            # The poster script is in the parent directory of the vault
            vault_root = self.vault_path.parent if self.vault_path.name == "AI_Employee_Vault" else self.vault_path

            # Route to appropriate poster based on platforms
            platforms = post_details.get('platforms', [])
            is_instagram_only = 'Instagram' in platforms and 'Facebook' not in platforms
            is_facebook_only = 'Facebook' in platforms and 'Instagram' not in platforms

            if is_instagram_only:
                poster_script = vault_root / "scripts" / "social-media" / "instagram_poster.py"
            elif is_facebook_only:
                poster_script = vault_root / "scripts" / "social-media" / "facebook_poster_v2.py"
            else:
                # Both platforms - use facebook_poster_v2.py (can be extended for both)
                poster_script = vault_root / "scripts" / "social-media" / "facebook_poster_v2.py"

            if not poster_script.exists():
                print(f"[ERROR] Poster script not found: {poster_script}")
                return False

            # Build command
            content = post_details.get('content', '')
            cmd = ["python", str(poster_script), content]

            # Add live flag if not in dry run mode
            if not self.dry_run:
                cmd.append("--live")

            # Call the meta_poster script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout (Meta Business Suite is slow)
            )

            # Print output for visibility
            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print(f"[STDERR] {result.stderr}")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("[ERROR] Meta poster timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Error running meta_poster: {e}")
            return False

    def _generate_summary(self, post_details: dict):
        """
        Generate a summary of the published post.

        Creates a summary markdown file in Briefings/ folder.
        """
        try:
            briefings_folder = self.vault_path / "Briefings"
            briefings_folder.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = briefings_folder / f"Meta_Post_Summary_{timestamp}.md"

            platforms = post_details.get('platforms', ['Facebook', 'Instagram'])
            content = post_details.get('content', '')
            content_preview = content[:200] + "..." if len(content) > 200 else content

            summary_content = f"""---
type: meta_post_summary
platforms: {', '.join(platforms)}
created: {datetime.now().isoformat()}
---

# Meta Post Summary

## Published At
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Platforms
{chr(10).join(f'- {p}' for p in platforms)}

## Content Preview
{content_preview}

## Full Content
{content}

## Status
✅ Successfully published

## Next Steps
- [ ] Monitor engagement (likes, comments, shares)
- [ ] Respond to comments within 24 hours
- [ ] Analyze performance after 7 days
- [ ] Update content strategy based on results

---

*Generated by Meta Approval Monitor*
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
            "component": "meta_approval_monitor",
            "action": action,
            "details": details
        }

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"[ERROR] Could not write to log: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor /Approved/ folder and publish Meta posts"
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

    # Create handler first to get the actual dry_run state (from env or args)
    event_handler = MetaApprovalHandler(args.vault, args.dry_run)

    print("=" * 60)
    print("Meta (Facebook & Instagram) Approval Monitor")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Watching: {approved_folder}")
    print(f"Mode: {'DRY RUN' if event_handler.dry_run else 'LIVE'}")
    print("=" * 60)
    print("\n[INFO] Waiting for approved posts...")
    print("[INFO] Press Ctrl+C to stop\n")

    observer = Observer()
    observer.schedule(event_handler, str(approved_folder), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Stopping monitor...")
        observer.stop()
    observer.join()

    print("[OK] Monitor stopped")


if __name__ == "__main__":
    main()
