# session_manager.py - Manage browser sessions for all social media platforms
#
# check_all_sessions()         → check if session files exist and are valid
# refresh_session(platform)    → re-login and save fresh session
# validate_session(platform)   → quick check if session can load a page

import json
from pathlib import Path
from datetime import datetime

from mcp_server.social_playwright_base import SESSIONS_ROOT, _log
from mcp_server.facebook_playwright import FacebookPoster
from mcp_server.instagram_playwright import InstagramPoster
from mcp_server.twitter_playwright import TwitterPoster

PLATFORMS = {
    'facebook':  FacebookPoster(),
    'instagram': InstagramPoster(),
    'twitter':   TwitterPoster(),
}

PLATFORM_URLS = {
    'facebook':  'https://www.facebook.com/',
    'instagram': 'https://www.instagram.com/',
    'twitter':   'https://x.com/home',
}


def check_all_sessions() -> dict:
    """
    Check all platform sessions.
    Returns { platform: { exists, file, size_bytes, modified } }
    """
    results = {}
    for name, poster in PLATFORMS.items():
        sf = poster._session_file()
        if sf.exists() and sf.stat().st_size > 10:
            mod_time = datetime.fromtimestamp(sf.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            results[name] = {
                'exists': True,
                'file': str(sf),
                'size_bytes': sf.stat().st_size,
                'modified': mod_time,
            }
            print(f"  [OK] {name:12s} — session saved ({mod_time})")
        else:
            results[name] = {'exists': False, 'file': str(sf)}
            print(f"  [--] {name:12s} — no session. Run: python main.py --setup")

    return results


def refresh_session(platform: str) -> bool:
    """
    Force re-login for a platform and save fresh session.
    Returns True on success.
    """
    poster = PLATFORMS.get(platform)
    if not poster:
        print(f"[Session] Unknown platform: {platform}")
        return False

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[Session] playwright not installed.")
        return False

    try:
        _log(poster.PLATFORM, 'INFO', 'Refreshing session (force login)...')
        with sync_playwright() as pw:
            browser = poster.get_browser(pw, force_headed=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 900})
            page = context.new_page()
            poster._do_login(page)
            poster._save_session(context)
            browser.close()
        _log(poster.PLATFORM, 'INFO', 'Session refreshed successfully.')
        return True
    except Exception as e:
        _log(poster.PLATFORM, 'ERROR', f"Session refresh failed: {e}")
        return False


def validate_session(platform: str) -> bool:
    """
    Quick check: load saved session and visit platform page.
    Returns True if we can access the authenticated page.
    """
    poster = PLATFORMS.get(platform)
    if not poster:
        print(f"[Session] Unknown platform: {platform}")
        return False

    if not poster._session_exists():
        print(f"[Session] No session for {platform}. Run --setup first.")
        return False

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[Session] playwright not installed.")
        return False

    try:
        with sync_playwright() as pw:
            browser = poster.get_browser(pw)
            context = poster._load_context(browser)
            page = context.new_page()
            url = PLATFORM_URLS.get(platform, '')
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            title = page.title()
            browser.close()

        _log(poster.PLATFORM, 'INFO', f"Session valid. Page title: {title}")
        print(f"  [OK] {platform} session valid — {title}")
        return True
    except Exception as e:
        _log(poster.PLATFORM, 'WARN', f"Session validation failed: {e}")
        print(f"  [FAIL] {platform} session invalid: {e}")
        return False
