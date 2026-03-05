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

        # Click the "New post" / "Create" button - try multiple selectors
        create_selectors = [
            'div[role="button"]:has-text("Create")',
            'svg[aria-label="New post"]',
            'a[aria-label="New post"]',
            '[aria-label="Create"]',
        ]
        for selector in create_selectors:
            try:
                loc = page.locator(selector)
                if loc.count() > 0:
                    loc.first.click(timeout=5000)
                    _log(self.PLATFORM, 'INFO', f'Create button clicked: {selector}')
                    break
            except Exception:
                continue
        _human_delay(2, 3)

        # Upload image via file input
        file_input = page.locator('input[type="file"]')
        file_input.first.set_input_files(img)
        _log(self.PLATFORM, 'INFO', 'Image uploaded.')
        _human_delay(3, 5)

        # Click Next buttons (crop -> filter -> caption screens)
        for step in range(2):
            next_selectors = [
                'div[role="button"]:has-text("Next")',
                'button:has-text("Next")',
                '[aria-label="Next"]',
            ]
            for selector in next_selectors:
                try:
                    loc = page.locator(selector)
                    if loc.count() > 0:
                        loc.first.click(timeout=5000)
                        _log(self.PLATFORM, 'INFO', f'Next clicked (step {step+1})')
                        break
                except Exception:
                    continue
            _human_delay(2, 3)

        # Take debug screenshot before caption
        try:
            from mcp_server.social_playwright_base import SCREENSHOTS_DIR
            page.screenshot(path=str(SCREENSHOTS_DIR / 'ig_before_caption.png'))
            _log(self.PLATFORM, 'INFO', 'Debug screenshot saved: ig_before_caption.png')
        except Exception:
            pass

        # Write caption - try multiple selectors, use keyboard typing
        caption_selectors = [
            'div[role="textbox"]',
            'div[contenteditable="true"]',
            '[aria-label="Write a caption..."]',
            'textarea[placeholder*="Write a caption"]',
        ]
        caption_typed = False
        for selector in caption_selectors:
            try:
                loc = page.locator(selector)
                if loc.count() > 0:
                    loc.first.click(timeout=5000)
                    _human_delay(0.3, 0.5)
                    # Use keyboard.type() - works in headless unlike clipboard
                    page.keyboard.type(content, delay=20)
                    caption_typed = True
                    _log(self.PLATFORM, 'INFO', f'Caption typed ({len(content)} chars)')
                    break
            except Exception as e:
                _log(self.PLATFORM, 'WARN', f'Caption selector {selector} failed: {e}')
                continue
        if not caption_typed:
            _log(self.PLATFORM, 'WARN', 'Caption input skipped - no matching selector')
        _human_delay(1, 2)

        # Take debug screenshot before share
        try:
            page.screenshot(path=str(SCREENSHOTS_DIR / 'ig_before_share.png'))
            _log(self.PLATFORM, 'INFO', 'Debug screenshot saved: ig_before_share.png')
        except Exception:
            pass

        # Click Share button - try multiple selectors
        share_selectors = [
            # Top-right Share text link (jo screenshot mein dikh raha hai)
            'div._acan._acap._acas._aj1-._ap30',   # Instagram internal class
            'div[role="button"] >> text=Share',
            'text=Share >> nth=-1',                 # Last "Share" element (top-right)
            '//div[text()="Share"]',               # XPath exact match
            '//span[text()="Share"]',
        ]
        share_clicked = False
        for selector in share_selectors:
            try:
                loc = page.locator(selector)
                if loc.count() > 0:
                    loc.first.click(force=True, timeout=5000)
                    share_clicked = True
                    _log(self.PLATFORM, 'INFO', f'Share clicked: {selector}')
                    break
            except Exception:
                continue
        if not share_clicked:
            raise Exception("Could not find Share button")
        _human_delay(5, 7)
        
        # ✅ ADD THIS - dialog band hone ka wait karo
        try:
            page.wait_for_selector('div:has-text("Create new post")', 
                                state='hidden', timeout=15000)
            _log(self.PLATFORM, 'INFO', '✅ Post dialog closed - post shared!')
        except Exception:
            page.screenshot(path=str(SCREENSHOTS_DIR / 'ig_share_failed.png'))
            raise Exception("Share button click nahi hua - dialog still open")

        # Take screenshot after share to verify
        try:
            page.screenshot(path=str(SCREENSHOTS_DIR / 'ig_after_share.png'))
            _log(self.PLATFORM, 'INFO', 'Debug screenshot saved: ig_after_share.png')
        except Exception:
            pass

        _log(self.PLATFORM, 'INFO', 'Post submitted.')
        return ''
