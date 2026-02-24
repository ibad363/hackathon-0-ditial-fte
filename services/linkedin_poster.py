# linkedin_poster.py - Create drafts and post to LinkedIn using Playwright (browser automation)
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

VAULT_PATH = Path('D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault')
PENDING_APPROVAL = VAULT_PATH / 'Pending_Approval'
APPROVED = VAULT_PATH / 'Approved'
LOGS = VAULT_PATH / 'Logs'
SESSION_FILE = Path('D:/Ibad Coding/hackathon-0-ditial-fte/linkedin_session.json')

LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')


def create_linkedin_draft(content, topic="General"):
    """Save a LinkedIn post draft to Pending_Approval folder. Never posts directly."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in topic)
    safe_topic = safe_topic.strip().replace(' ', '_')[:40]

    filename = f'LINKEDIN_DRAFT_{safe_topic}_{timestamp}.md'
    filepath = PENDING_APPROVAL / filename

    draft_content = f'''---
type: linkedin_draft
topic: {topic}
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
status: pending_approval
approved: false
---

## LinkedIn Post Draft

### Topic: {topic}

### Content
{content}

---

## Approval Section
- [ ] Content reviewed by human
- [ ] Approved for posting

> **Instructions:** Move this file to /Approved folder to authorize posting.
> The system will NEVER post without your explicit approval.
'''
    filepath.write_text(draft_content, encoding='utf-8')
    print(f"[LinkedIn] Draft saved: {filename}")
    print(f"[LinkedIn] Review it in: {PENDING_APPROVAL}")
    print(f"[LinkedIn] Move to /Approved when ready to post")

    log_action(f"LinkedIn draft created: {filename} | Topic: {topic}")
    return filepath


def _get_browser_and_context(playwright):
    """Launch browser, load saved session if available."""
    browser = playwright.chromium.launch(headless=False)  # headless=False so you can see/debug

    if SESSION_FILE.exists():
        print("[LinkedIn] Loading saved session...")
        storage_state = json.loads(SESSION_FILE.read_text(encoding='utf-8'))
        context = browser.new_context(storage_state=storage_state)
    else:
        context = browser.new_context()

    return browser, context


def _save_session(context):
    """Save browser cookies/storage so we don't need to re-login next time."""
    storage_state = context.storage_state()
    SESSION_FILE.write_text(json.dumps(storage_state), encoding='utf-8')
    print("[LinkedIn] Session saved to linkedin_session.json")


def _login_if_needed(page):
    """Check if we're logged in; if not, perform login."""
    page.goto("https://www.linkedin.com/feed/", timeout=30000)
    time.sleep(2)

    # If redirected to login page, we need to authenticate
    if "login" in page.url or "authwall" in page.url:
        print("[LinkedIn] Not logged in. Logging in now...")

        if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
            raise ValueError(
                "Missing LINKEDIN_EMAIL or LINKEDIN_PASSWORD in .env file.\n"
                "Add these to your .env:\n"
                "  LINKEDIN_EMAIL=your@email.com\n"
                "  LINKEDIN_PASSWORD=yourpassword"
            )

        page.goto("https://www.linkedin.com/login", timeout=30000)
        time.sleep(1)

        page.fill('#username', LINKEDIN_EMAIL)
        page.fill('#password', LINKEDIN_PASSWORD)
        page.click('button[type="submit"]')
        time.sleep(4)

        # Check if login succeeded
        if "feed" in page.url or "mynetwork" in page.url or "jobs" in page.url:
            print("[LinkedIn] Login successful!")
        elif "checkpoint" in page.url or "challenge" in page.url:
            print("[LinkedIn] Security check required!")
            print("[LinkedIn] Please complete the verification in the browser window.")
            print("[LinkedIn] Waiting up to 60 seconds for you to verify...")
            # Wait for user to complete captcha/2FA
            page.wait_for_url("**/feed/**", timeout=60000)
            print("[LinkedIn] Verification complete, continuing...")
        else:
            raise RuntimeError(f"[LinkedIn] Login failed. Current URL: {page.url}")
    else:
        print("[LinkedIn] Already logged in via saved session.")


def post_approved_linkedin(approval_file):
    """Post to LinkedIn via Playwright ONLY after the file has been moved to /Approved."""
    from playwright.sync_api import sync_playwright

    filepath = Path(approval_file)

    # Safety check: file MUST be in Approved folder
    if APPROVED.name not in filepath.parts:
        print("[LinkedIn] BLOCKED: File is not in /Approved folder!")
        print("[LinkedIn] Move the draft to /Approved first to authorize posting.")
        return False

    if not filepath.exists():
        print(f"[LinkedIn] ERROR: File not found: {filepath}")
        return False

    # Extract content from the markdown file
    file_text = filepath.read_text(encoding='utf-8')
    content = extract_post_content(file_text)

    if not content:
        print("[LinkedIn] ERROR: Could not extract post content from file")
        return False

    print(f"[LinkedIn] Posting via Playwright browser automation...")
    print(f"[LinkedIn] Content preview: {content[:80]}...")

    try:
        with sync_playwright() as p:
            browser, context = _get_browser_and_context(p)
            page = context.new_page()

            # Login if needed
            _login_if_needed(page)

            # Save session after successful login
            _save_session(context)

            # Navigate to LinkedIn feed to create a post
            page.goto("https://www.linkedin.com/feed/", timeout=30000)
            time.sleep(2)

            # Debug: print the page title so we can confirm we're on the right page
            print(f"[LinkedIn] Page title: {page.title()}")

            # Click "Start a post" — try multiple selectors in order of reliability
            print("[LinkedIn] Looking for 'Start a post' button...")
            start_post_btn = page.locator(
                '[aria-label="Start a post"], '
                '[placeholder="Start a post"], '
                'button:has-text("Start a post")'
            ).first
            start_post_btn.wait_for(state="visible", timeout=15000)
            start_post_btn.click()
            time.sleep(2)

            # Type the post content — the modal editor is a contenteditable div
            print("[LinkedIn] Typing post content...")
            post_editor = page.locator(
                'div.ql-editor[contenteditable="true"], '
                'div[role="textbox"][contenteditable="true"]'
            ).first
            post_editor.wait_for(state="visible", timeout=15000)
            post_editor.click()
            post_editor.type(content, delay=20)
            time.sleep(1)

            # Screenshot before clicking Post — so we can verify the modal looked right
            screenshot_path = Path('D:/Ibad Coding/hackathon-0-ditial-fte/linkedin_debug_before_post.png')
            page.screenshot(path=str(screenshot_path))
            print(f"[LinkedIn] Screenshot saved: {screenshot_path}")

            # Click the submit Post button (confirmed selector from DOM inspection)
            print("[LinkedIn] Clicking Post button...")
            post_btn = page.locator('button.share-actions__primary-action').first
            post_btn.wait_for(state="visible", timeout=15000)
            print(f"[LinkedIn] Post button text: '{post_btn.inner_text().strip()}'")
            print(f"[LinkedIn] Post button disabled: {post_btn.is_disabled()}")
            post_btn.click()

            # Wait for the modal to close — confirms the post was submitted
            print("[LinkedIn] Waiting for modal to close...")
            page.wait_for_selector('div[role="dialog"]', state="hidden", timeout=15000)
            time.sleep(2)

            # Screenshot after — confirms feed returned
            screenshot_after = Path('D:/Ibad Coding/hackathon-0-ditial-fte/linkedin_debug_after_post.png')
            page.screenshot(path=str(screenshot_after))
            print(f"[LinkedIn] Screenshot after post: {screenshot_after}")

            print("[LinkedIn] Post submitted successfully!")
            log_action(f"LinkedIn post published via Playwright: {filepath.name}")

            browser.close()
            return True

    except Exception as e:
        print(f"[LinkedIn] Playwright error: {e}")
        log_action(f"LinkedIn post FAILED: {str(e)[:200]} | {filepath.name}")
        return False


def extract_post_content(file_text):
    """Extract the post content from between ### Content and the next ---."""
    lines = file_text.split('\n')
    capture = False
    content_lines = []

    for line in lines:
        if line.strip() == '### Content':
            capture = True
            continue
        if capture and line.strip() == '---':
            break
        if capture:
            content_lines.append(line)

    return '\n'.join(content_lines).strip()


def check_approved_posts():
    """Scan /Approved folder for LinkedIn drafts ready to post."""
    approved_files = list(APPROVED.glob('LINKEDIN_DRAFT_*.md'))

    if not approved_files:
        print("[LinkedIn] No approved posts found in /Approved")
        return

    for filepath in approved_files:
        print(f"[LinkedIn] Found approved post: {filepath.name}")
        success = post_approved_linkedin(filepath)
        if success:
            # Move to Done after successful posting
            done_path = VAULT_PATH / 'Done' / filepath.name
            filepath.rename(done_path)
            print(f"[LinkedIn] Moved to /Done: {filepath.name}")


def save_session_manually():
    """Open browser for manual login and save the session. Run once to set up."""
    from playwright.sync_api import sync_playwright

    print("[LinkedIn] Opening browser for manual login...")
    print("[LinkedIn] Log in to LinkedIn in the browser window, then press Enter here.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.linkedin.com/login", timeout=30000)

        input("[LinkedIn] Press Enter AFTER you have logged in successfully in the browser...")

        _save_session(context)
        print("[LinkedIn] Session saved! Future runs will use this session.")
        browser.close()


def log_action(message):
    """Append action to LinkedIn log."""
    log_file = LOGS / 'linkedin_log.md'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not log_file.exists():
        log_file.write_text("# LinkedIn Activity Log\n\n", encoding='utf-8')

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"- [{timestamp}] {message}\n")


if __name__ == '__main__':
    print("=" * 50)
    print("[LinkedIn Poster] Playwright Mode")
    print("=" * 50)
    print("\nOptions:")
    print("1. Create a test draft")
    print("2. Check and post approved drafts")
    print("3. Save session manually (run once to set up login)")

    choice = input("\nEnter choice (1/2/3): ").strip()

    if choice == '1':
        test_content = """Excited to share our latest project update!

We've been building an AI-powered personal employee system that automates daily tasks like email processing, scheduling, and content creation.

The key insight? AI works best when it has clear guardrails and human approval loops.

#AI #Automation #Productivity #TechInnovation #BuildInPublic"""
        create_linkedin_draft(test_content, topic="AI Employee Project Update")

    elif choice == '2':
        check_approved_posts()

    elif choice == '3':
        save_session_manually()

    else:
        print("Invalid choice")
