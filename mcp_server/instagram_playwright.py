# instagram_playwright.py - Instagram posting via Playwright
# Extends SocialPlaywrightBase
# Login + post flow for instagram.com (requires image)

import os
from pathlib import Path
from dotenv import load_dotenv
from mcp_server.social_playwright_base import SocialPlaywrightBase, _human_delay, _log, SESSIONS_ROOT

load_dotenv()

INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '')

DEFAULT_IMAGE = Path('D:/Ibad Coding/hackathon-0-ditial-fte/assets/default_post_image.png')


class InstagramPoster(SocialPlaywrightBase):
    PLATFORM    = 'Instagram'
    SESSION_DIR = SESSIONS_ROOT / 'instagram'

    def _do_login(self, page):
        """Login to Instagram."""
        _log(self.PLATFORM, 'INFO', 'Navigating to Instagram login...')
        page.goto('https://www.instagram.com/accounts/login/', wait_until='domcontentloaded')
        _human_delay(2, 4)

        # Accept cookies if present
        try:
            btn = page.locator('button:has-text("Allow"), button:has-text("Accept")')
            if btn.first.is_visible(timeout=3000):
                btn.first.click()
                _human_delay()
        except Exception:
            pass

        page.fill('input[name="username"]', INSTAGRAM_USERNAME)
        _human_delay(0.5, 1.5)
        page.fill('input[name="password"]', INSTAGRAM_PASSWORD)
        _human_delay(0.5, 1.0)
        page.click('button[type="submit"]')
        _human_delay(4, 6)

        # Handle "Save Login Info" and notification prompts
        for btn_text in ['Not Now', 'Not now']:
            try:
                not_now = page.locator(f'button:has-text("{btn_text}")')
                if not_now.first.is_visible(timeout=3000):
                    not_now.first.click()
                    _human_delay()
            except Exception:
                pass

        page.wait_for_url('**/instagram.com/**', timeout=30000)
        _log(self.PLATFORM, 'INFO', 'Login successful.')

    def _do_post(self, page, content: str, image_path: str = None) -> str:
        """Create a new Instagram post (image required)."""
        # Use default placeholder if no image provided
        img = image_path if image_path and Path(image_path).exists() else str(DEFAULT_IMAGE)

        if not Path(img).exists():
            raise FileNotFoundError(
                f"No image found at {img}. Run: python scripts/create_placeholder.py"
            )

        _log(self.PLATFORM, 'INFO', 'Starting new post flow...')
        page.goto('https://www.instagram.com/', wait_until='domcontentloaded')
        _human_delay(2, 3)

        # Click the "New post" / "Create" button (plus icon in nav)
        try:
            create_btn = page.locator('[aria-label="New post"], '
                                      '[aria-label="Create"],'
                                      'svg[aria-label="New post"]')
            create_btn.first.click()
            _human_delay(2, 3)
        except Exception:
            page.locator('a[href="/create/"]').first.click()
            _human_delay(2, 3)

        # Upload image via hidden file input
        file_input = page.locator('input[type="file"][accept*="image"]')
        file_input.first.set_input_files(img)
        _human_delay(3, 5)

        # Click Next / Arrow through crop / filter screens
        for _ in range(2):
            try:
                next_btn = page.locator('button:has-text("Next"), '
                                        '[aria-label="Next"]')
                next_btn.first.click()
                _human_delay(2, 3)
            except Exception:
                pass

        # Write caption
        try:
            caption_box = page.locator('[aria-label="Write a caption..."], '
                                       'textarea[aria-label="Write a caption..."]')
            caption_box.first.click()
            _human_delay(0.5, 1)
            caption_box.first.fill(content)
            _human_delay(1, 2)
        except Exception as e:
            _log(self.PLATFORM, 'WARN', f"Caption input skipped: {e}")

        # Share (force=True to bypass any overlays)
        share_btn = page.locator('button:has-text("Share"), '
                                 '[aria-label="Share"]')
        share_btn.first.click(force=True)
        _human_delay(4, 6)

        _log(self.PLATFORM, 'INFO', 'Post submitted.')
        return ''
