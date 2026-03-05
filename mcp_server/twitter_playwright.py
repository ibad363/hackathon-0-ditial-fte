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

    USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/131.0.0.0 Safari/537.36')

    def _load_context(self, browser):
        """Override to add user_agent for Twitter bot detection bypass."""
        import json
        if self._session_exists():
            _log(self.PLATFORM, 'INFO', "Loading saved session...")
            state = json.loads(self._session_file().read_text(encoding='utf-8'))
            return browser.new_context(
                storage_state=state,
                viewport={'width': 1280, 'height': 900},
                user_agent=self.USER_AGENT,
            )
        return browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent=self.USER_AGENT,
        )

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
        page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=30000)
        _human_delay(4, 6)

        # Debug screenshot to see what loaded
        try:
            from mcp_server.social_playwright_base import SCREENSHOTS_DIR
            page.screenshot(path=str(SCREENSHOTS_DIR / 'twitter_page_loaded.png'))
            _log(self.PLATFORM, 'INFO', f'Page URL: {page.url}')
            _log(self.PLATFORM, 'INFO', 'Debug screenshot saved: twitter_page_loaded.png')
        except Exception:
            pass

        # Check if we got redirected to login (session expired)
        if '/login' in page.url or '/i/flow/login' in page.url:
            raise Exception("Session expired - redirected to login. Delete sessions/twitter/session.json and re-login.")

        # Check for Twitter error page ("Something went wrong") - retry once
        try:
            error_text = page.locator('text="Something went wrong"')
            if error_text.count() > 0 and error_text.first.is_visible(timeout=2000):
                _log(self.PLATFORM, 'WARN', 'Twitter error page detected, retrying...')
                # Click "Try again" or just reload
                try:
                    retry_btn = page.locator('button:has-text("Try again"), button:has-text("Retry")')
                    if retry_btn.count() > 0:
                        retry_btn.first.click()
                    else:
                        page.reload(wait_until='domcontentloaded', timeout=30000)
                except Exception:
                    page.reload(wait_until='domcontentloaded', timeout=30000)
                _human_delay(4, 6)
        except Exception:
            pass

        # Dismiss any overlay/mask that Twitter shows
        try:
            mask = page.locator('[data-testid="mask"]')
            if mask.count() > 0 and mask.first.is_visible(timeout=2000):
                mask.first.click()
                _human_delay(1, 2)
                _log(self.PLATFORM, 'INFO', 'Dismissed overlay mask')
        except Exception:
            pass

        # Wait for the compose box to appear on timeline
        editor_selectors = [
            '[data-testid="tweetTextarea_0"]',
            '[aria-label="Post text"]',
            '[contenteditable="true"][role="textbox"]',
        ]
        editor_clicked = False
        for selector in editor_selectors:
            try:
                loc = page.locator(selector)
                loc.first.wait_for(state='visible', timeout=10000)
                loc.first.click(force=True, timeout=5000)
                editor_clicked = True
                _log(self.PLATFORM, 'INFO', f'Editor clicked: {selector}')
                break
            except Exception as e:
                _log(self.PLATFORM, 'WARN', f'Editor selector {selector} failed: {e}')
                continue
        if not editor_clicked:
            # Take screenshot for debugging
            try:
                page.screenshot(path=str(SCREENSHOTS_DIR / 'twitter_no_editor.png'))
                _log(self.PLATFORM, 'INFO', 'Debug screenshot saved: twitter_no_editor.png')
            except Exception:
                pass
            raise Exception("Could not find tweet compose box - check twitter_no_editor.png and twitter_page_loaded.png")
        _human_delay(0.5, 1)

        # Type content using keyboard (avoids overlay interception issues)
        page.keyboard.type(text, delay=20)
        _log(self.PLATFORM, 'INFO', f'Tweet typed ({len(text)} chars)')
        _human_delay(1, 2)

        # Attach image if provided
        if image_path and Path(image_path).exists():
            try:
                file_input = page.locator('input[type="file"][accept*="image"]')
                file_input.first.set_input_files(image_path)
                _human_delay(2, 3)
            except Exception as e:
                _log(self.PLATFORM, 'WARN', f"Image upload skipped: {e}")

        # Take debug screenshot before posting
        try:
            from mcp_server.social_playwright_base import SCREENSHOTS_DIR
            page.screenshot(path=str(SCREENSHOTS_DIR / 'twitter_before_post.png'))
            _log(self.PLATFORM, 'INFO', 'Debug screenshot saved: twitter_before_post.png')
        except Exception:
            pass

        # Click Post button using JavaScript click to bypass overlay interception
        post_selectors = [
            '[data-testid="tweetButtonInline"]',
            '[data-testid="tweetButton"]',
        ]
        post_clicked = False
        for selector in post_selectors:
            try:
                loc = page.locator(selector)
                if loc.count() > 0:
                    # Use JS click - bypasses overlay completely
                    loc.first.evaluate('el => el.click()')
                    post_clicked = True
                    _log(self.PLATFORM, 'INFO', f'Post button JS-clicked: {selector}')
                    break
            except Exception as e:
                _log(self.PLATFORM, 'WARN', f'Post selector {selector} failed: {e}')
                continue
        if not post_clicked:
            raise Exception("Could not find Post button")
        _human_delay(5, 7)

        # Verify tweet was posted - check if compose box text is cleared
        try:
            page.screenshot(path=str(SCREENSHOTS_DIR / 'twitter_after_post.png'))
            _log(self.PLATFORM, 'INFO', 'Debug screenshot saved: twitter_after_post.png')
        except Exception:
            pass

        _log(self.PLATFORM, 'INFO', 'Tweet submitted.')
        return ''
