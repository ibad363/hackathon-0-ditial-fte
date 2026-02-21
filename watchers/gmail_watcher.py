# gmail_watcher.py - Monitors Gmail for unread important emails
import os
import json
import time
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail API scope - read-only access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

VAULT_PATH = Path('D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault')
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'
PROCESSED_IDS_FILE = Path('D:/Ibad Coding/hackathon-0-ditial-fte/watchers/processed_emails.json')
CHECK_INTERVAL = 120  # 2 minutes


def get_gmail_service():
    """Authenticate with Gmail using OAuth2 and return the service."""
    creds = None
    token_path = Path('D:/Ibad Coding/hackathon-0-ditial-fte/token.json')
    credentials_path = Path('D:/Ibad Coding/hackathon-0-ditial-fte/credentials.json')

    # Load existing token if available
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[Gmail] Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                print("[Gmail] ERROR: credentials.json not found!")
                print("[Gmail] Download it from Google Cloud Console > APIs > Credentials")
                print("[Gmail] Save it as: credentials.json in project root")
                return None
            print("[Gmail] Starting OAuth2 authorization flow...")
            print("[Gmail] A browser window will open - sign in with your Gmail account")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future runs
        token_path.write_text(creds.to_json())
        print("[Gmail] Token saved for future use")

    service = build('gmail', 'v1', credentials=creds)
    print("[Gmail] Successfully connected to Gmail API")
    return service


def load_processed_ids():
    """Load set of already-processed email IDs from disk."""
    if PROCESSED_IDS_FILE.exists():
        data = json.loads(PROCESSED_IDS_FILE.read_text())
        return set(data)
    return set()


def save_processed_ids(processed_ids):
    """Save processed email IDs to disk."""
    PROCESSED_IDS_FILE.write_text(json.dumps(list(processed_ids)))


def create_email_action_file(service, msg_id, headers, snippet):
    """Create a .md file in Needs_Action for a new email."""
    sender = headers.get('From', 'Unknown')
    subject = headers.get('Subject', 'No Subject')
    date = headers.get('Date', datetime.now().isoformat())

    # Clean subject for filename (remove special chars)
    safe_subject = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in subject)
    safe_subject = safe_subject.strip().replace(' ', '_')[:50]

    filename = f'EMAIL_{safe_subject}_{msg_id[:8]}.md'
    filepath = NEEDS_ACTION / filename

    content = f'''---
type: email
from: {sender}
subject: {subject}
received: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
original_date: {date}
gmail_id: {msg_id}
priority: high
status: pending
---

## Email Preview
{snippet}

## Sender Info
- **From:** {sender}
- **Subject:** {subject}
- **Date:** {date}

## Suggested Actions
- [ ] Read full email and assess priority
- [ ] Draft reply if needed
- [ ] Create approval request if involves money/commitments
- [ ] Update Dashboard.md
- [ ] Move to /Done after processing
'''
    filepath.write_text(content, encoding='utf-8')
    print(f"  [Gmail] Created action file: {filename}")
    return filepath


def check_for_new_emails(service, processed_ids):
    """Check Gmail for unread important emails and create action files."""
    try:
        results = service.users().messages().list(
            userId='me',
            q='is:unread is:important',
            maxResults=10
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            print(f"[Gmail] No new unread important emails found")
            return processed_ids

        new_count = 0
        for msg_ref in messages:
            msg_id = msg_ref['id']

            if msg_id in processed_ids:
                continue

            # Fetch full message details
            msg = service.users().messages().get(
                userId='me', id=msg_id, format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()

            headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
            snippet = msg.get('snippet', '')

            create_email_action_file(service, msg_id, headers, snippet)
            processed_ids.add(msg_id)
            new_count += 1

        if new_count > 0:
            print(f"[Gmail] Processed {new_count} new email(s)")
            save_processed_ids(processed_ids)
        else:
            print(f"[Gmail] All emails already processed")

        return processed_ids

    except Exception as e:
        print(f"[Gmail] Error checking emails: {e}")
        return processed_ids


def run():
    """Main loop - check Gmail every 2 minutes."""
    print("=" * 50)
    print("[Gmail Watcher] Starting up...")
    print(f"[Gmail] Check interval: {CHECK_INTERVAL} seconds")
    print(f"[Gmail] Action folder: {NEEDS_ACTION}")
    print("=" * 50)

    service = get_gmail_service()
    if not service:
        print("[Gmail] Failed to connect. Exiting.")
        return

    processed_ids = load_processed_ids()
    print(f"[Gmail] Loaded {len(processed_ids)} previously processed email IDs")

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[Gmail] [{timestamp}] Checking for new emails...")
        processed_ids = check_for_new_emails(service, processed_ids)
        print(f"[Gmail] Next check in {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    run()
