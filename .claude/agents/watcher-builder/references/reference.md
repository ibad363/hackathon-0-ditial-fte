---
name: watcher-builder
description: Technical reference for building watchers that integrate with the AI Employee system
license: MIT
---

# Watcher Builder Reference

Technical reference for building watchers that integrate with the AI Employee system.

---

## BaseWatcher API

All watchers must inherit from `BaseWatcher` class defined in `watchers/base_watcher.py`.

### Class Definition

```python
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
import json
import logging

class BaseWatcher(ABC):
    """Base class for all watcher scripts"""

    def __init__(self, vault_path: str, check_interval: int = 60, dry_run: bool = False):
        """
        Initialize watcher.

        Args:
            vault_path: Path to AI_Employee_Vault folder
            check_interval: Seconds between checks (default: 60)
            dry_run: If True, don't create action files (default: False)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        self.dry_run = dry_run
        self.processed_ids = set()

        # Create folders
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new updates from external service.

        Returns:
            List of new items (any type)
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create markdown action file in Needs_Action folder.

        Args:
            item: Item object from check_for_updates()

        Returns:
            Path to created file
        """
        pass

    @abstractmethod
    def get_item_id(self, item) -> str:
        """
        Get unique identifier for item (for deduplication).

        Args:
            item: Item object

        Returns:
            Unique ID string
        """
        pass

    def log_action(self, action_type: str, details: dict):
        """Log action to JSONL file"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "watcher": self.__class__.__name__,
            "action_type": action_type,
            "details": details
        }

        log_file = self.logs / f"{datetime.utcnow().strftime('%Y-%m-%d')}.json"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
```

---

## Abstract Methods Implementation

### check_for_updates()

**Purpose:** Poll external service for new items

**Requirements:**
- Return list of items (any type)
- Handle API errors gracefully
- Implement rate limiting if needed
- Return empty list if no updates

**Example:**

```python
def check_for_updates(self) -> list:
    try:
        response = self.client.get('/messages', params={
            'since': self.last_check
        })
        response.raise_for_status()
        return response.json()['messages']
    except Exception as e:
        self.logger.error(f"Failed to check for updates: {e}")
        return []
```

---

### create_action_file()

**Purpose:** Create markdown action file in Needs_Action folder

**Requirements:**
- Create structured markdown with YAML frontmatter
- Use descriptive filename
- Return Path object
- Handle file creation errors

**File Naming Pattern:**
```
{TYPE}_{YYYYMMDD_HHMMSS}_{sanitized_title}.md
```

**Example:**

```python
def create_action_file(self, message) -> Path:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_title = re.sub(r'[^\w-]', '_', message['subject'][:50])
    filename = f"EMAIL_{timestamp}_{safe_title}.md"

    filepath = self.needs_action / filename

    content = f'''---
type: email
service: gmail
from: {message['from']}
subject: {message['subject']}
received: {datetime.utcnow().isoformat()}
priority: high
status: pending
---

# Email: {message['subject']}

**From:** {message['from']}
**Received:** {message['date']}

## Content

{message['snippet']}

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward if needed
- [ ] Archive after processing
'''

    filepath.write_text(content)
    self.log_action('created_action_file', {
        'filename': filename,
        'type': 'email',
        'from': message['from']
    })

    return filepath
```

---

### get_item_id()

**Purpose:** Return unique identifier for deduplication

**Requirements:**
- Return unique string for each item
- Consistent across checks
- Handle missing IDs gracefully

**Example:**

```python
def get_item_id(self, message) -> str:
    # Prefer explicit ID
    if 'id' in message:
        return message['id']

    # Fallback to hash of content
    content_hash = hashlib.md5(
        str(message).encode()
    ).hexdigest()
    return f"hash_{content_hash}"
```

---

## Logging Format

### JSONL Structure

Every action logs to `AI_Employee_Vault/Logs/YYYY-MM-DD.json`:

```json
{"timestamp": "2026-01-12T10:30:00Z", "watcher": "GmailWatcher", "action_type": "created_action_file", "details": {"filename": "EMAIL_20260112_103000_invoice.md", "type": "email"}}
{"timestamp": "2026-01-12T10:31:00Z", "watcher": "GmailWatcher", "action_type": "error", "details": {"error": "Connection timeout"}}
{"timestamp": "2026-01-12T10:32:00Z", "watcher": "GmailWatcher", "action_type": "detected", "details": {"count": 3, "new": 1}}
```

### Log Action Types

- `created_action_file` - New action file created
- `error` - Error occurred
- `detected` - New items detected
- `authenticated` - Authentication successful
- `refreshed_token` - OAuth token refreshed
- `rate_limited` - API rate limit hit

---

## PM2 Configuration

### Configuration Schema

```javascript
{
  name: string,              // Unique process name
  script: string,            // Command to run
  interpreter: string,       // "python3" for Python scripts
  exec_mode: string,         // "fork" or "watchdog"
  autorestart: boolean,      // Auto-restart on crash
  watch: boolean|string[],   // Watch files and restart on change
  max_restarts: number,      // Max restarts before stopping
  max_memory_restart: string // Restart if memory exceeds
  cron: string,              // Cron schedule (optional)
  env: {
    PYTHONUNBUFFERED: "1",   // Disable Python output buffering
    VAULT_PATH: string,      // Path to vault
    DRY_RUN: "false"         // Dry run mode
  }
}
```

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `VAULT_PATH` | Path to AI_Employee_Vault | `AI_Employee_Vault` |
| `PYTHONUNBUFFERED` | Disable output buffering | `1` |
| `DRY_RUN` | Enable dry run mode | `true` or `false` |
| `LOG_LEVEL` | Logging verbosity | `DEBUG`, `INFO`, `WARNING` |

### Process Management

```bash
# Start all watchers
pm2 start process-manager/pm2.config.js

# List running processes
pm2 list

# View logs
pm2 logs gmail-watcher

# Restart a watcher
pm2 restart gmail-watcher

# Stop a watcher
pm2 stop gmail-watcher

# Stop all
pm2 stop all

# Monitor in real-time
pm2 monit
```

---

## Error Handling Patterns

### Exponential Backoff

```python
import time

def fetch_with_retry(self, url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            delay = 2 ** attempt  # 1s, 2s, 4s
            self.logger.warning(
                f"Attempt {attempt + 1} failed, "
                f"retrying in {delay}s: {e}"
            )
            time.sleep(delay)
```

### Graceful Degradation

```python
def check_for_updates(self) -> list:
    try:
        items = self._fetch_items()
        return items
    except AuthenticationError:
        # Auth error - don't retry
        self.logger.error("Authentication failed, stopping")
        self.log_action('auth_error', {'error': 'Invalid credentials'})
        raise  # Re-raise to stop process
    except RateLimitError:
        # Rate limited - return empty and retry later
        self.logger.warning("Rate limited, waiting until next check")
        return []
    except TransientError:
        # Network error - return empty and retry
        self.logger.warning("Transient error, will retry")
        return []
```

---

## Credential Security

### Principles

1. **Never commit credentials** - Add `.env` and `*_token.json` to `.gitignore`
2. **Use environment variables** - Store sensitive data in environment
3. **Token encryption** - Encrypt tokens at rest for production
4. **Minimal permissions** - Request only required API scopes
5. **Token rotation** - Support token refresh and rotation

### .gitignore Pattern

```gitignore
# Credentials
.env
*_token.json
*_credentials.json
.client_secret.json

# Sessions
*whatsapp_session/
.playwright/
```

### Environment Variable Loading

```python
import os
from dotenv import load_dotenv

class SlackWatcher(BaseWatcher):
    def __init__(self, vault_path: str, check_interval: int = 60):
        super().__init__(vault_path, check_interval)

        # Load .env file
        load_dotenv()

        # Get credentials from environment
        self.client_id = os.getenv('SLACK_CLIENT_ID')
        self.client_secret = os.getenv('SLACK_CLIENT_SECRET')

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "SLACK_CLIENT_ID and SLACK_CLIENT_SECRET "
                "must be set in environment"
            )
```

---

## Rate Limiting

### Pattern: Token Bucket

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, rate: int, per: int):
        """
        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()

    def can_request(self) -> bool:
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current

        self.allowance += time_passed * (self.rate / self.per)

        if self.allowance > self.rate:
            self.allowance = self.rate

        if self.allowance < 1:
            return False

        self.allowance -= 1
        return True

# Usage in watcher
class SlackWatcher(BaseWatcher):
    def __init__(self, vault_path: str, check_interval: int = 60):
        super().__init__(vault_path, check_interval)
        self.rate_limiter = RateLimiter(rate=20, per=1)  # 20 req/sec

    def _make_request(self, endpoint: str):
        while not self.rate_limiter.can_request():
            time.sleep(0.1)  # Wait until we can make request

        return self.client.get(endpoint)
```

---

## Testing Strategy

### Unit Tests

```python
import unittest
from unittest.mock import Mock, patch
from watchers.slack_watcher import SlackWatcher

class TestSlackWatcher(unittest.TestCase):
    def setUp(self):
        self.watcher = SlackWatcher(
            vault_path="test_vault",
            token="test_token",
            check_interval=1
        )

    @patch('watchers.slack_watcher.SlackWatcher._make_request')
    def test_check_for_updates(self, mock_request):
        # Mock API response
        mock_request.return_value = {
            'messages': [
                {'id': '1', 'text': 'Test message'},
                {'id': '2', 'text': 'Another message'}
            ]
        }

        items = self.watcher.check_for_updates()

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['id'], '1')
```

### Integration Tests

```python
def test_end_to_end_flow():
    # 1. Start watcher
    watcher = GmailWatcher(vault_path="test_vault")
    watcher.dry_run = True  # Don't actually create files

    # 2. Check for updates
    items = watcher.check_for_updates()

    # 3. Verify items detected
    assert len(items) > 0

    # 4. Create action file
    filepath = watcher.create_action_file(items[0])

    # 5. Verify file created
    assert filepath.exists()

    # 6. Verify file content
    content = filepath.read_text()
    assert 'type: email' in content
```

---

## Watcher Performance Guidelines

### Memory Management

- Use `processed_ids` set for deduplication
- Periodically clean old IDs (> 7 days)
- Limit set size to 10,000 items max

### Check Intervals

| Service Type | Recommended Interval |
|--------------|---------------------|
| Email (Gmail) | 120 seconds (2 min) |
| Instant Message (Slack) | 30 seconds |
| SMS (WhatsApp) | 30 seconds |
| Project Management (Jira) | 300 seconds (5 min) |
| Finance (Xero) | 600 seconds (10 min) |

### CPU Usage

- Use async I/O where possible
- Implement exponential backoff
- Avoid busy-wait loops
- Use generator expressions instead of lists for large datasets

---

## Common Patterns

### Pagination

```python
def check_for_updates(self) -> list:
    all_items = []
    page = 1

    while True:
        response = self.client.get('/items', params={'page': page})
        items = response.json()['items']

        if not items:
            break

        all_items.extend(items)
        page += 1

        # Check if last page
        if response.json()['page'] >= response.json()['total_pages']:
            break

    return all_items
```

### Webhook Fallback

```python
class SlackWatcher(BaseWatcher):
    def __init__(self, vault_path: str, check_interval: int = 60, use_webhook: bool = False):
        super().__init__(vault_path, check_interval)
        self.use_webhook = use_webhook

    def check_for_updates(self) -> list:
        if self.use_webhook:
            # Webhook mode - return items from webhook queue
            return self._get_webhook_items()
        else:
            # Polling mode
            return self._poll_api()
```

---

## Troubleshooting

### Issue: Watcher stops detecting new items

**Diagnosis:**
1. Check `processed_ids` set size - might be too large
2. Verify API token hasn't expired
3. Check rate limits in logs

**Solution:**
```python
# Periodically clean processed_ids
if len(self.processed_ids) > 10000:
    # Remove IDs older than 7 days
    cutoff = datetime.utcnow() - timedelta(days=7)
    # Filter based on timestamp...
```

### Issue: High memory usage

**Diagnosis:**
1. `processed_ids` set growing too large
2. Response objects not being garbage collected

**Solution:**
```python
# Store only IDs, not full objects
item_ids = {item['id'] for item in items}
```

### Issue: PM2 watcher exits with code 0

**Diagnosis:**
1. Unhandled exception
2. Authentication failure

**Solution:**
```bash
# Check PM2 logs
pm2 logs --err

# Common fixes:
# - Refresh OAuth tokens
# - Check credentials in .env
# - Verify API scopes
```
