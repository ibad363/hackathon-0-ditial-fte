# twitter_playwright.py - Twitter/X posting via Playwright
# Extends SocialPlaywrightBase
# Login + post flow for x.com. Auto-truncates to 280 chars.

import os
from pathlib import Path
from dotenv import load_dotenv
from mcp_server.social_playwright_base import SocialPlaywrightBase, _human_delay, _log, SESSIONS_ROOT

load_dotenv()

TWITTER_USERNAME = os.getenv('TWITTER_USERNAME', '')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD', '')

MAX_TWEET_LENGTH = 280


class TwitterPoster(SocialPlaywrightBase):
    PLATFORM    = 'Twitter'
    SESSION_DIR = SESSIONS_ROOT / 'twitter'

    @staticmethod
    def _truncate(text: str) -> str:
        """Truncate text to 280 chars, appending '...' if needed."""
        if len(text) <= MAX_TWEET_LENGTH:
            return text
        return text[:277] + '...'

    def _do_login(self, page):
        """Login to X (Twitter)."""
        _log(self.PLATFORM, 'INFO', 'Navigating to X login...')
        page.goto('https://x.com/i/flow/login', wait_until='domcontentloaded')
        _human_delay(3, 5)

        # Enter username
        username_input = page.locator('input[autocomplete="username"], '
                                      'input[name="text"]')
        username_input.first.fill(TWITTER_USERNAME)
        _human_delay(0.5, 1.5)
        page.locator('button:has-text("Next"), [role="button"]:has-text("Next")').first.click()
        _human_delay(2, 3)

        # Enter password
        password_input = page.locator('input[name="password"], '
                                      'input[type="password"]')
        password_input.first.fill(TWITTER_PASSWORD)
        _human_delay(0.5, 1.0)
        page.locator('button:has-text("Log in"), [data-testid="LoginForm_Login_Button"]').first.click()
        _human_delay(4, 6)

        page.wait_for_url('**/x.com/**', timeout=30000)
        _log(self.PLATFORM, 'INFO', 'Login successful.')

    def _do_post(self, page, content: str, image_path: str = None) -> str:
        """Create a new tweet. Content auto-truncated to 280 chars."""
        text = self._truncate(content)

        _log(self.PLATFORM, 'INFO', f"Posting tweet ({len(text)} chars)...")
        page.goto('https://x.com/compose/post', wait_until='domcontentloaded')
        _human_delay(2, 3)

        # Type into tweet compose box
        editor = page.locator('[data-testid="tweetTextarea_0"], '
                              '[aria-label="Post text"], '
                              '[contenteditable="true"][role="textbox"]')
        editor.first.click()
        _human_delay(0.5, 1)
        editor.first.fill(text)
        _human_delay(1, 2)

        # Attach image if provided
        if image_path and Path(image_path).exists():
            try:
                file_input = page.locator('input[type="file"][accept*="image"]')
                file_input.first.set_input_files(image_path)
                _human_delay(2, 3)
            except Exception as e:
                _log(self.PLATFORM, 'WARN', f"Image upload skipped: {e}")

        # Click Post button
        post_btn = page.locator('[data-testid="tweetButton"], '
                                'button:has-text("Post")')
        post_btn.first.click()
        _human_delay(3, 5)

        _log(self.PLATFORM, 'INFO', 'Tweet submitted.')
        return ''
