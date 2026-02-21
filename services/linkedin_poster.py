# linkedin_poster.py - Create drafts and post to LinkedIn after approval
import os
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = Path('D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault')
PENDING_APPROVAL = VAULT_PATH / 'Pending_Approval'
APPROVED = VAULT_PATH / 'Approved'
LOGS = VAULT_PATH / 'Logs'

LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
LINKEDIN_PERSON_ID = os.getenv('LINKEDIN_PERSON_ID', '')


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


def post_approved_linkedin(approval_file):
    """Post to LinkedIn API ONLY after the file has been moved to /Approved."""
    filepath = Path(approval_file)

    # Safety check: file MUST be in Approved folder
    if APPROVED.name not in filepath.parts:
        print("[LinkedIn] BLOCKED: File is not in /Approved folder!")
        print("[LinkedIn] Move the draft to /Approved first to authorize posting.")
        return False

    if not filepath.exists():
        print(f"[LinkedIn] ERROR: File not found: {filepath}")
        return False

    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_ID:
        print("[LinkedIn] ERROR: Missing LinkedIn credentials in .env")
        print("[LinkedIn] Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID")
        return False

    # Extract content from the markdown file
    file_text = filepath.read_text(encoding='utf-8')
    content = extract_post_content(file_text)

    if not content:
        print("[LinkedIn] ERROR: Could not extract post content from file")
        return False

    # LinkedIn API v2 - Create a share
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    payload = {
        "author": f"urn:li:person:{LINKEDIN_PERSON_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            print("[LinkedIn] Post published successfully!")
            log_action(f"LinkedIn post published from: {filepath.name}")
            return True
        else:
            print(f"[LinkedIn] API Error {response.status_code}: {response.text}")
            log_action(f"LinkedIn post FAILED: {response.status_code} | {filepath.name}")
            return False
    except Exception as e:
        print(f"[LinkedIn] Request failed: {e}")
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


def log_action(message):
    """Append action to scheduler log."""
    log_file = LOGS / 'linkedin_log.md'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not log_file.exists():
        log_file.write_text("# LinkedIn Activity Log\n\n", encoding='utf-8')

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"- [{timestamp}] {message}\n")


if __name__ == '__main__':
    print("=" * 50)
    print("[LinkedIn Poster] Manual Mode")
    print("=" * 50)
    print("\nOptions:")
    print("1. Create a test draft")
    print("2. Check and post approved drafts")

    choice = input("\nEnter choice (1/2): ").strip()

    if choice == '1':
        test_content = """Excited to share our latest project update!

We've been building an AI-powered personal employee system that automates daily tasks like email processing, scheduling, and content creation.

The key insight? AI works best when it has clear guardrails and human approval loops.

#AI #Automation #Productivity #TechInnovation #BuildInPublic"""
        create_linkedin_draft(test_content, topic="AI Employee Project Update")

    elif choice == '2':
        check_approved_posts()
    else:
        print("Invalid choice")
