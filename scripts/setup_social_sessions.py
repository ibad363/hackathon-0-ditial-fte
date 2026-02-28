# setup_social_sessions.py - One-time manual setup for social media browser sessions
#
# Opens a headed browser for each platform so you can login manually.
# After login, sessions are saved to sessions/<platform>/session.json.
# Usage: python scripts/setup_social_sessions.py

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp_server.facebook_playwright import FacebookPoster
from mcp_server.instagram_playwright import InstagramPoster
from mcp_server.twitter_playwright import TwitterPoster
from mcp_server.social_playwright_base import _log

PLATFORMS = [
    ('Facebook',  'https://www.facebook.com/',                  FacebookPoster()),
    ('Instagram', 'https://www.instagram.com/accounts/login/',  InstagramPoster()),
    ('Twitter',   'https://x.com/i/flow/login',                TwitterPoster()),
]


def setup_sessions():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[Setup] playwright not installed. Run:")
        print("  pip install playwright && playwright install")
        return

    print("=" * 60)
    print("  Social Media Session Setup")
    print("  Login manually to each platform. Sessions will be saved.")
    print("=" * 60)
    print()

    with sync_playwright() as pw:
        for name, url, poster in PLATFORMS:
            print(f"\n--- {name} ---")
            print(f"Opening {url}")
            print("Login manually, then press ENTER here when done.\n")

            browser = pw.chromium.launch(
                headless=False,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled'],
            )
            context = browser.new_context(viewport={'width': 1280, 'height': 900})
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded')

            input(f"  >> Press ENTER after logging into {name}... ")

            poster._save_session(context)
            browser.close()
            print(f"  [OK] {name} session saved.\n")

    print("=" * 60)
    print("  All sessions saved. You can now use headless mode.")
    print("=" * 60)


if __name__ == '__main__':
    setup_sessions()
