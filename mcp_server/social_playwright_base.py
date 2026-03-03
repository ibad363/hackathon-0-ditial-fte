# social_playwright_base.py - Base class for all social media Playwright automation
#
# Subclasses override: PLATFORM, SESSION_DIR, _do_login(), _do_post()
# All posts require an approval file in AI_Employee_Vault/Approved/
# Screenshots saved to AI_Employee_Vault/Logs/screenshots/ on error
# Post summaries saved to AI_Employee_Vault/Social/<Platform>/

import json
import time
import random
import os
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH       = Path('D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault')
APPROVED_DIR     = VAULT_PATH / 'Approved'
PENDING_DIR      = VAULT_PATH / 'Pending_Approval'
ERROR_QUEUE      = VAULT_PATH / 'Error_Queue'
SCREENSHOTS_DIR  = VAULT_PATH / 'Logs' / 'screenshots'
SESSIONS_ROOT    = Path('D:/Ibad Coding/hackathon-0-ditial-fte/sessions')

# Ensure shared dirs exist
for _d in [APPROVED_DIR, PENDING_DIR, ERROR_QUEUE, SCREENSHOTS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _human_delay(min_s: float = 1.0, max_s: float = 3.0):
    """Sleep a random human-like delay between min_s and max_s seconds."""
    time.sleep(random.uniform(min_s, max_s))


def _log(platform: str, level: str, message: str):
    log_file = VAULT_PATH / 'Social' / platform / f'{platform.lower()}_log.md'
    log_file.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")
    print(f"[{platform}] [{level}] {message}")


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class SocialPlaywrightBase(ABC):
    """
    Abstract base for social media Playwright posters.

    Subclasses must set:
        PLATFORM   : str   — e.g. 'Facebook'
        SESSION_DIR: Path  — sessions/facebook/

    Subclasses must implement:
        _do_login(page)    — perform login flow on already-open page
        _do_post(page, content, image_path) — perform post flow
    """

    PLATFORM: str = ''
    SESSION_DIR: Path = None

    # ------------------------------------------------------------------ #
    #  Browser / session management                                        #
    # ------------------------------------------------------------------ #

    def _session_file(self) -> Path:
        return self.SESSION_DIR / 'session.json'

    def _session_exists(self) -> bool:
        sf = self._session_file()
        return sf.exists() and sf.stat().st_size > 10

    def get_browser(self, playwright, force_headed: bool = False):
        """
        Launch Chromium.
        headless=False when no session exists (first run) or force_headed=True.
        headless=True after session is saved.
        """
        headless = self._session_exists() and not force_headed
        browser = playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled'],
        )
        _log(self.PLATFORM, 'INFO',
             f"Browser launched (headless={headless})")
        return browser

    def _load_context(self, browser):
        """Create browser context, loading saved session if available."""
        if self._session_exists():
            _log(self.PLATFORM, 'INFO', "Loading saved session...")
            state = json.loads(self._session_file().read_text(encoding='utf-8'))
            return browser.new_context(
                storage_state=state,
                viewport={'width': 1280, 'height': 900},
            )
        return browser.new_context(viewport={'width': 1280, 'height': 900})

    def _save_session(self, context):
        """Persist cookies/storage to sessions/<platform>/session.json."""
        self.SESSION_DIR.mkdir(parents=True, exist_ok=True)
        state = context.storage_state()
        self._session_file().write_text(
            json.dumps(state, indent=2), encoding='utf-8'
        )
        _log(self.PLATFORM, 'INFO',
             f"Session saved: {self._session_file()}")

    # ------------------------------------------------------------------ #
    #  Approval guard                                                      #
    # ------------------------------------------------------------------ #

    def _check_approval(self, draft_filename: str) -> bool:
        """Return True only if matching approval file exists in Approved/."""
        approval = APPROVED_DIR / draft_filename
        if approval.exists():
            _log(self.PLATFORM, 'INFO',
                 f"Approval confirmed: {draft_filename}")
            return True
        _log(self.PLATFORM, 'WARN',
             f"No approval file found for '{draft_filename}'. "
             f"Move it to {APPROVED_DIR} to allow posting.")
        return False

    # ------------------------------------------------------------------ #
    #  Error handling                                                      #
    # ------------------------------------------------------------------ #

    def handle_error(self, page, context: str, error: Exception):
        """Screenshot + error file + log on any exception."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Screenshot
        try:
            shot_path = SCREENSHOTS_DIR / f"{self.PLATFORM.lower()}_error_{timestamp}.png"
            page.screenshot(path=str(shot_path))
            _log(self.PLATFORM, 'ERROR',
                 f"Screenshot saved: {shot_path.name}")
        except Exception:
            pass

        # Error file
        err_file = ERROR_QUEUE / f"{self.PLATFORM.lower()}_error_{timestamp}.md"
        err_file.write_text(
            f"# {self.PLATFORM} Error\n\n"
            f"**Time:** {datetime.now()}\n"
            f"**Context:** {context}\n"
            f"**Error:** {error}\n",
            encoding='utf-8',
        )
        _log(self.PLATFORM, 'ERROR', f"{context}: {error}")

    # ------------------------------------------------------------------ #
    #  Draft creation                                                      #
    # ------------------------------------------------------------------ #

    def create_post_draft(self, content: str, topic: str = 'General',
                          image_path: str = None) -> Path:
        """
        Save a post draft to Pending_Approval/.
        Returns the draft file path.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        safe_topic = ''.join(
            c if c.isalnum() or c in (' ', '-', '_') else ''
            for c in topic
        ).strip().replace(' ', '_')[:40]

        filename = f"{self.PLATFORM.upper()}_DRAFT_{safe_topic}_{timestamp}.md"
        filepath = PENDING_DIR / filename

        image_line = f"image: {image_path}" if image_path else "image: none"

        draft = (
            f"---\n"
            f"platform: {self.PLATFORM.lower()}\n"
            f"topic: {topic}\n"
            f"created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"status: pending_approval\n"
            f"approved: false\n"
            f"{image_line}\n"
            f"---\n\n"
            f"## {self.PLATFORM} Post Draft\n\n"
            f"### Topic: {topic}\n\n"
            f"### Content\n{content}\n\n"
            f"---\n\n"
            f"## Approval\n"
            f"- [ ] Content reviewed\n"
            f"- [ ] Approved for posting\n\n"
            f"> Move this file to /Approved to authorise posting.\n"
            f"> The system will NEVER post without your explicit approval.\n"
        )
        filepath.write_text(draft, encoding='utf-8')
        _log(self.PLATFORM, 'INFO',
             f"Draft saved: {filename} -> review in {PENDING_DIR}")
        return filepath

    # ------------------------------------------------------------------ #
    #  Post summary                                                        #
    # ------------------------------------------------------------------ #

    def save_post_summary(self, content: str, status: str, post_url: str = ''):
        """Append a post summary to Social/<Platform>/<platform>_posts.md."""
        summary_file = VAULT_PATH / 'Social' / self.PLATFORM / f"{self.PLATFORM.lower()}_posts.md"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = (
            f"\n---\n"
            f"**Posted:** {timestamp}  \n"
            f"**Status:** {status}  \n"
            f"**URL:** {post_url or 'N/A'}  \n"
            f"**Content:**\n{content[:300]}{'...' if len(content) > 300 else ''}\n"
        )
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        _log(self.PLATFORM, 'INFO', f"Post summary saved.")

    # ------------------------------------------------------------------ #
    #  Abstract methods — implemented by each platform subclass           #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def _do_login(self, page):
        """Perform platform login. Called only when no session exists."""

    @abstractmethod
    def _do_post(self, page, content: str, image_path: str = None):
        """Perform the actual post action. Return post URL string or ''."""

    # ------------------------------------------------------------------ #
    #  High-level public API                                               #
    # ------------------------------------------------------------------ #

    def post_approved_content(self, draft_filename: str,
                              content: str, image_path: str = None) -> dict:
        """
        Check approval, login if needed, post content.
        Returns { success, message, post_url }
        """
        if not self._check_approval(draft_filename):
            return {
                'success': False,
                'message': f"Approval required: move {draft_filename} to Approved/",
                'post_url': '',
            }

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                'success': False,
                'message': "playwright not installed. Run: pip install playwright && playwright install",
                'post_url': '',
            }

        if not self._session_exists():
            msg = (f"No session for {self.PLATFORM}. "
                   f"Run: python main.py --setup")
            _log(self.PLATFORM, 'WARN', msg)
            return {'success': False, 'message': msg, 'post_url': ''}

        post_url = ''
        page = None
        try:
            with sync_playwright() as pw:
                browser = self.get_browser(pw)
                context = self._load_context(browser)
                page    = context.new_page()

                # Login if session is fresh/missing
                if not self._session_exists():
                    _log(self.PLATFORM, 'INFO', "No session -- running login flow...")
                    self._do_login(page)
                    self._save_session(context)
                    _human_delay(1, 2)

                _log(self.PLATFORM, 'INFO', "Starting post flow...")
                post_url = self._do_post(page, content, image_path) or ''

                # Refresh saved session after successful post
                self._save_session(context)
                browser.close()

            self.save_post_summary(content, 'posted', post_url)
            _log(self.PLATFORM, 'INFO', f"Post successful. URL: {post_url or 'N/A'}")
            return {'success': True, 'message': 'Posted successfully.', 'post_url': post_url}

        except Exception as e:
            err_msg = str(e).encode('ascii', 'replace').decode('ascii')
            if page is not None:
                try:
                    self.handle_error(page, 'post_approved_content', e)
                except Exception:
                    pass
            _log(self.PLATFORM, 'ERROR', f"post_approved_content failed: {err_msg}")
            self.save_post_summary(content, f'FAILED: {err_msg}', '')
            return {'success': False, 'message': err_msg, 'post_url': ''}
