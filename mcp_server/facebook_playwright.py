# facebook_playwright.py - Facebook posting via Playwright
# Extends SocialPlaywrightBase
# Login + post flow for facebook.com

import os
from pathlib import Path
from dotenv import load_dotenv
from mcp_server.social_playwright_base import SocialPlaywrightBase, _human_delay, _log, SESSIONS_ROOT

load_dotenv()

FACEBOOK_EMAIL    = os.getenv('FACEBOOK_EMAIL', '')
FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD', '')


class FacebookPoster(SocialPlaywrightBase):
    PLATFORM    = 'Facebook'
    SESSION_DIR = SESSIONS_ROOT / 'facebook'

    def _do_login(self, page):
        """Login to Facebook."""
        _log(self.PLATFORM, 'INFO', 'Navigating to Facebook login...')
        page.goto('https://www.facebook.com/', wait_until='domcontentloaded')
        _human_delay()

        # Accept cookies popup if present
        try:
            cookies_btn = page.locator('[data-cookiebanner="accept_button"]')
            if cookies_btn.is_visible(timeout=3000):
                cookies_btn.click()
                _human_delay()
        except Exception:
            pass

        page.fill('input#email', FACEBOOK_EMAIL)
        _human_delay(0.5, 1.5)
        page.fill('input#pass', FACEBOOK_PASSWORD)
        _human_delay(0.5, 1.0)
        page.click('button[name="login"]')
        _human_delay(3, 5)

        # Wait for feed to confirm login
        page.wait_for_url('**/facebook.com/**', timeout=30000)
        _log(self.PLATFORM, 'INFO', 'Login successful.')

    def _do_post(self, page, content: str, image_path: str = None) -> str:
        """Create a new Facebook post."""
        _log(self.PLATFORM, 'INFO', 'Navigating to feed...')
        page.goto('https://www.facebook.com/', wait_until='domcontentloaded')
        _human_delay(2, 4)

        # Click "What's on your mind?" to open composer
        try:
            composer = page.locator('[aria-label="Create a post"], '
                                    '[aria-label="What\'s on your mind"]')
            composer.first.click()
            _human_delay(2, 3)
        except Exception:
            # Fallback: look for the role=button with "What's on your mind"
            page.locator('div[role="button"]:has-text("What\'s on your mind")').first.click()
            _human_delay(2, 3)

        # Type content into the post box
        editor = page.locator('[aria-label="What\'s on your mind?"], '
                              '[contenteditable="true"][role="textbox"]')
        editor.first.click()
        _human_delay(0.5, 1)
        editor.first.fill(content)
        _human_delay(1, 2)

        # Attach image if provided
        if image_path and Path(image_path).exists():
            try:
                photo_btn = page.locator('[aria-label="Photo/video"], '
                                         '[aria-label="Photo/Video"]')
                photo_btn.first.click()
                _human_delay(1, 2)
                file_input = page.locator('input[type="file"][accept*="image"]')
                file_input.first.set_input_files(image_path)
                _human_delay(2, 3)
            except Exception as e:
                _log(self.PLATFORM, 'WARN', f"Image upload skipped: {e}")

        # Dismiss any overlays (e.g. "Fewer than 1000 posts" popup)
        try:
            page.keyboard.press('Escape')
            _human_delay(0.5, 1)
        except Exception:
            pass

        # Click Post button (force=True to bypass any remaining overlays)
        post_btn = page.locator('[aria-label="Post"], button:has-text("Post")')
        post_btn.first.click(force=True)
        _human_delay(3, 5)

        _log(self.PLATFORM, 'INFO', 'Post submitted.')
        return ''
