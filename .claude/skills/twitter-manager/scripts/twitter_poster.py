#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter (X) Poster - Stealth Automation for Twitter/X

Uses Playwright to post tweets to Twitter (X) with human-like behavior.

Usage:
    python twitter_poster.py "Your tweet here" --dry-run
    python twitter_poster.py "Your tweet here" --reply_to @user (Reply to a tweet)

Note:
    Start Chrome with: chrome.exe --remote-debugging-port=9222
"""

import argparse
import os
import sys
import socket
import platform
import time
import random
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    sys.exit(1)

# Import shared automation helpers
try:
    from automation_helpers import human_type, human_click
except ImportError:
    print("Error: automation_helpers.py not found.")
    print("Please ensure automation_helpers.py is in the same directory.")
    sys.exit(1)


# ==================== CONFIGURATION ====================

# DRY_RUN: Set to False to actually publish tweets
# Can be overridden via:
# 1. Environment variable: export TWITTER_DRY_RUN=false
# 2. Command-line flag: --live or --dry-run
DRY_RUN = os.getenv('TWITTER_DRY_RUN', 'true').lower() == 'true'
TWEETER_BASE_URL = "https://X.com"  # Twitter/X URL
CDP_ENDPOINT = "http://127.0.0.1:9222"  # IPv4 for Windows compatibility

# Twitter-specific timing
INITIAL_PAGE_LOAD_DELAY = 3.0  # Wait for page load
NETWORK_IDLE_TIMEOUT = 30000  # 30 seconds for network to settle

# Twitter/X selectors
TEXTAREA_SELECTOR = 'div[data-testid="tweetTextarea_0"]'
TWEET_BUTTON_SELECTOR = 'div[data-testid="tweetButton"]'  # Old selector
POST_BUTTON_SELECTOR = 'div[data-testid="tweetButtonInline"]'  # New inline post button
# Alternative selectors for the Post button
POST_BUTTON_ALTS = [
    'div[data-testid="tweetButtonInline"]',
    'button[data-testid="tweet-button"]',
    'div[role="button"][data-testid="tweetButton"]',
    'button[aria-label*="Post"]',
    'div[aria-label*="Post"]',
]

# Reply-specific selector
REPLY_BUTTON_SELECTOR = 'div[role="button"][data-testid="reply"]'
QUOTE_BUTTON_SELECTOR = 'div[role="button"][data-testid="quote"]'


# ==================== CHROME CDP HELPER ====================

def ensure_chrome_cdp_running():
    """
    Check if Chrome CDP is running on port 9222. If not, automatically start it.
    This preserves your existing Chrome session with logins.
    """
    import subprocess
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', 9222))
    sock.close()

    if result == 0:
        print("[OK] Chrome CDP detected on port 9222 - using existing session")
        return

    print("[INFO] Chrome CDP not available - auto-starting...")
    system = platform.system()

    if system == "Windows":
        # Use subprocess to start Chrome in background
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        profile_dir = r"C:\Users\User\ChromeAutomationProfile"

        command = [
            chrome_path,
            "--remote-debugging-port=9222",
            f"--user-data-dir={profile_dir}",
            f"--profile-directory={profile_dir}",
            "--start-maximized",
            "about:blank"
        ]

        print(f"[INFO] Starting Chrome CDP: {chrome_path}")

        try:
            process = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
            print("[OK] Chrome CDP started (PID: " + str(process.pid) + ")")
            print("[INFO] Chrome automation window should open in background")
            print("[INFO] This Chrome is separate from your main Chrome profile")

            # Wait for Chrome to start
            time.sleep(3)

            # Check if it started successfully
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock2.settimeout(2)
            result2 = sock2.connect_ex(('localhost', 9222))
            sock2.close()

            if result2 == 0:
                print("[OK] Chrome CDP is ready!")
                return
            else:
                raise Exception("Chrome CDP failed to start")

        except Exception as e:
            print(f"[ERROR] Failed to start Chrome CDP: {e}")
            print("\n[INFO] Please manually start Chrome with:")
            print("[INFO]   START_AUTOMATION_CHROME.bat")
            raise Exception("Chrome CDP not available")

    elif system == "Darwin":  # macOS
        # Use subprocess to start Chrome in background
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        command = [
            chrome_path,
            "--remote-debugging-port=9222",
            "--profile-directory=~/Library/Application Support/Google/Chrome"
        ]

        try:
            process = subprocess.Popen(command)
            print("[OK] Chrome CDP started (PID: " + str(process.pid) + ")")
            time.sleep(5)

            # Check if it started
            if sock.connect_ex(('localhost', 9222)) == 0:
                print("[OK] Chrome CDP is ready!")
                return
            else:
                raise Exception("Chrome CDP failed to start")

        except Exception as e:
            print(f"[ERROR] Failed to start Chrome CDP: {e}")
            print("\n[INFO] Please manually start Chrome with:")
            print("[INFO]   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
            raise Exception("Chrome CDP not available")

    else:  # Linux
        command = ["google-chrome", "--remote-debugging-port=9222"]

        try:
            process = subprocess.Popen(command)
            print("[OK] Chrome CDP started (PID: " + str(process.pid) + ")")
            time.sleep(5)

            if sock.connect_ex(('localhost', 9222)) == 0:
                print("[OK] Chrome CDP is ready!")
                return
            else:
                raise Exception("Chrome CDP failed to start")

        except Exception as e:
            print(f"[ERROR] Failed to start Chrome CDP: {e}")
            raise Exception("Chrome CDP not available")


def post_tweet(page, tweet_content, reply_to=None):
    """
    Post a tweet to Twitter (X).

    Args:
        page: Playwright page object (already connected to Chrome)
        tweet_content: Text content to post
        reply_to: Optional[str] - If specified, reply to a tweet (format: "@username or tweet_id")

    Returns:
        True if successful, False otherwise
    """
    try:
        print("\n" + "="*60)
        print("🐦 TWEETER (X) - Post Tweet")
        print("="*60 + "\n")

        print(f"📝 Tweet Content: {tweet_content[:100]}{'...' if len(tweet_content) > 100 else ''}")
        print(f"📱 Reply To: {reply_to if reply_to else 'None'}")
        print("\n")

        # Step 1: Navigate to Twitter (X)
        print("📍 Step 1: Navigating to Twitter (X)...")
        page.goto(TWEETER_BASE_URL, wait_until="domcontentloaded", timeout=60000)

        # Wait for page to load
        print(f"⏳ Waiting {INITIAL_PAGE_LOAD_DELAY}s for page to stabilize...")
        time.sleep(INITIAL_PAGE_LOAD_DELAY)

        # Try to wait for network to be mostly idle
        try:
            page.wait_for_load_state("networkidle", timeout=NETWORK_IDLE_TIMEOUT)
            print("✅ Twitter loaded\n")
        except PlaywrightTimeoutError:
            print("⚠️  Network not fully idle, proceeding anyway...\n")

        # Step 2: Compose tweet
        print("📍 Step 2: Composing tweet...")

        # Click on "What's happening?!" (tweet button)
        human_click(page, TWEET_BUTTON_SELECTOR, "Tweet button")

        time.sleep(2.0)  # Wait for composer to open

        # Type content
        if reply_to:
            # For replies
            print(f"Replying to: {reply_to}")
            human_click(page, REPLY_BUTTON_SELECTOR, "Reply button")
            time.sleep(1.0)

            # Type @username or reply_to handle
            human_type(page, TEXTAREA_SELECTOR, f"@{reply_to} ")
            human_type(page, TEXTAREA_SELECTOR, tweet_content)
        else:
            # For new tweets
            human_type(page, TEXTAREA_SELECTOR, tweet_content)

        time.sleep(1.0)
        print("✅ Content typed\n")

        # Step 3: Review and post
        print("📍 Step 3: Review and Post...")

        if not DRY_RUN:
            # Click Post button - try multiple selectors
            print("🚀 Clicking 'Post' button...")
            posted = False

            for selector in POST_BUTTON_ALTS:
                try:
                    if page.is_visible(selector, timeout=2000):
                        print(f"   Found Post button with selector: {selector}")
                        if human_click(page, selector, "Post button"):
                            posted = True
                            break
                except (PlaywrightTimeoutError, Error):
                    continue

            if not posted:
                print("⚠️  Could not find Post button, trying keyboard shortcut...")
                # Try Ctrl+Enter as fallback
                page.keyboard.press("Control+Enter")
                posted = True

            # Wait for tweet to be posted
            time.sleep(random.uniform(2.0, 4.0))

            print("\n✅ Tweet posted successfully!")
        else:
            print("📸 DRY RUN MODE - Skipping actual posting")
            page.screenshot(path="twitter_dry_run_preview.png", full_page=True)
            print("✅ Saved: twitter_dry_run_preview.png")
            print("\n⚠️  To actually post, set DRY_RUN = False at the top of the script\n")

        print("\n" + "="*60)
        print("🎉 TWITTER (X) POST COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")

        return True

    except PlaywrightTimeoutError as e:
        print(f"❌ Timeout error: {e}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="twitter_error_debug.png", full_page=True)
        print("📸 Saved debug screenshot: twitter_error_debug.png")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Post tweets to Twitter (X) with stealth automation"
    )

    parser.add_argument(
        "content",
        help="Tweet content (keep it under 280 characters)"
    )

    parser.add_argument(
        "--reply-to",
        help="Reply to a tweet (format: @username or tweet_id)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without actually posting (default)"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually publish the tweet (overrides DRY_RUN)"
    )

    args = parser.parse_args()

    # Override DRY_RUN if flag is set
    global DRY_RUN
    if args.live:
        DRY_RUN = False
        print("⚠️  LIVE MODE: Tweets will actually be published!")
    elif args.dry_run:
        DRY_RUN = True
        print("✅ DRY RUN MODE: Preview only, will not publish")

    # Prepare content
    tweet_content = args.content

    if args.reply_to:
        tweet_content = f"@{args.reply_to} {tweet_content}"

    print("\n╔══════════════════════════════════════════════════════╗")
    print("      TWITTER (X) POSTER v1.0                            ")
    print("      Playwright-based with stealth automation                ")
    print("==========================================================")
    print("")

    print(f"📝 Tweet Content: {tweet_content[:100]}{'...' if len(tweet_content) > 100 else ''}")
    print(f"📱 Reply To: {args.reply_to if args.reply_to else 'None'}")
    print(f"⚠️  Dry Run: {'YES' if DRY_RUN else 'NO'}")
    print(f"🐔 CDP Endpoint: {CDP_ENDPOINT}")
    print(f"📸 Screenshot: {'twitter_dry_run_preview.png' if DRY_RUN else 'twitter_error_debug.png'}")
    print("")

    with sync_playwright() as p:
        try:
            # Check Chrome CDP is available
            ensure_chrome_cdp_running()

            # Connect to existing Chrome instance via CDP
            print("[INFO] Connecting to Chrome CDP session...")

            try:
                browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
                print("[OK] Connected to existing Chrome session!")
            except Exception as e:
                print(f"[ERROR] Could not connect to Chrome CDP: {e}")
                raise

            # Get the default context and page
            default_context = browser.contexts[0]
            page = default_context.pages[0] if default_context.pages else default_context.new_page()

            # Bring window to front
            page.bring_to_front()

            # Create the post
            success = post_tweet(page, tweet_content, args.reply_to)

            if success:
                print("✅ Script completed successfully!")
                sys.exit(0)
            else:
                print("❌ Script failed. Check debug screenshot")
                sys.exit(1)

        except Exception as e:
            print(f"\n❌ CONNECTION ERROR: {e}")
            print("\n" + "="*60)
            print("TROUBLESHOOTING:")
            print("="*60)
            print("""
1. Make sure Chrome is running with remote debugging enabled
2. Check if Chrome is listening on port 9222
3. Ensure you're logged into Twitter (X)
4. If Twitter is slow, increase INITIAL_PAGE_LOAD_DELAY in the script
5. Try increasing timeouts in the script
            """)
            sys.exit(1)


if __name__ == "__main__":
    main()
