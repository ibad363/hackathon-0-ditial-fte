---
name: watcher-builder
description: Templates for generating different types of watchers
license: MIT
---

# Watcher Builder Templates

This document contains templates for generating different types of watchers.

---

## OAuth 2.0 Watcher Template

**Use for:** Gmail, Slack, Jira, Notion, and services with OAuth 2.0

### Configuration Form

```yaml
service_name: "slack"
auth_type: "oauth"
oauth_config:
  auth_uri: "https://slack.com/oauth/v2/authorize"
  token_uri: "https://slack.com/api/oauth.v2.access"
  scopes: ["channels:read", "chat:read", "im:read", "groups:read"]
  client_id_var: "SLACK_CLIENT_ID"
  client_secret_var: "SLACK_CLIENT_SECRET"
check_interval: 60
filter_criteria:
  - "messages mentioning @bot"
  - "direct messages"
  - "messages in monitored channels"
```

### Generated Code Structure

```python
class SlackWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 60):
        super().__init__(vault_path, check_interval)
        self.credentials_path = Path(credentials_path)
        self.token_path = self.credentials_path.parent / '.slack_token.json'
        self.client = None

    def _authenticate(self):
        # OAuth flow with token refresh
        pass

    def check_for_updates(self) -> list:
        # Poll for new messages
        pass

    def create_action_file(self, item) -> Path:
        # Create action file in Needs_Action
        pass
```

---

## Token-Based Watcher Template

**Use for:** Telegram, Discord, Stripe, and services with API tokens

### Configuration Form

```yaml
service_name: "telegram"
auth_type: "token"
token_config:
  token_var: "TELEGRAM_BOT_TOKEN"
  token_location: ".env"  # or "parameter_store" or "vault"
check_interval: 30
api_endpoint: "https://api.telegram.org/bot{token}/"
filter_criteria:
  - "bot commands (/start, /help, etc.)"
  - "keywords: urgent, invoice, payment"
  - "private messages only"
```

### Generated Code Structure

```python
class TelegramWatcher(BaseWatcher):
    def __init__(self, vault_path: str, token: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.token = token
        self.api_base = f"https://api.telegram.org/bot{token}/"
        self.offset = 0  # For polling

    def _make_request(self, method: str, params: dict = None):
        # Authenticated API requests
        pass

    def check_for_updates(self) -> list:
        # Poll getUpdates endpoint
        pass
```

---

## Session-Based Watcher Template

**Use for:** WhatsApp Web, and services requiring browser sessions

### Configuration Form

```yaml
service_name: "whatsapp"
auth_type: "session"
session_config:
  session_path: "./whatsapp_session"
  browser: "chromium"
  headless: true
check_interval: 30
filter_criteria:
  - "unread messages"
  - "keywords: urgent, asap, invoice, payment, help"
```

### Generated Code Structure

```python
from playwright.sync_api import sync_playwright

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path)
        self.playwright = None

    def _get_browser_context(self):
        # Persistent browser context with session
        pass

    def check_for_updates(self) -> list:
        # Navigate to WhatsApp Web and check for messages
        pass
```

---

## Action File Templates

### Email/Message Action File

```markdown
---
type: message
service: slack
from: "john@company.com"
channel: "#general"
timestamp: "2026-01-12T10:30:00Z"
priority: high
status: pending
---

# Message Content

@bot Can you send me the invoice for last month?

## Suggested Actions

- [ ] Reply to acknowledge request
- [ ] Check if invoice exists
- [ ] Generate invoice if needed
- [ ] Send invoice via email
- [ ] Archive after processing
```

### Issue/Ticket Action File

```markdown
---
type: issue
service: jira
project: "PROJ"
key: "PROJ-123"
priority: "high"
status: "open"
assignee: "unassigned"
---

# Issue Summary

**Title:** Database connection fails in production

**Description:**
Getting connection timeout errors when trying to connect to the production database.

**Reporter:** alice@company.com
**Created:** 2026-01-12T09:15:00Z

## Suggested Actions

- [ ] Check database status
- [ ] Review connection string
- [ ] Check network connectivity
- [ ] Assign to DBA team
- [ ] Update ticket with findings
```

### Event/Webhook Action File

```markdown
---
type: event
service: stripe
event_type: "invoice.payment_failed"
customer: "cust_1234"
amount: 500.00
currency: "USD"
timestamp: "2026-01-12T08:00:00Z"
priority: urgent
---

# Payment Failed Event

Customer **cust_1234** failed to pay invoice **INV-0042** for **$500.00**.

**Reason:** Card declined - insufficient funds

## Suggested Actions

- [ ] Notify customer of failed payment
- [ ] Update payment method
- [ ] Retry payment in 3 days
- [ ] Flag account for review
- [ ] Update customer record
```

---

## PM2 Configuration Template

```javascript
{
  name: "{service_name}-watcher",
  "script": "python -m watchers.{service_name}_watcher --vault AI_Employee_Vault --credentials {credentials_file}",
  "interpreter": "python3",
  "exec_mode": "fork",
  "autorestart": true,
  "watch": false,
  "max_restarts": 10,
  "max_memory_restart": "500M",
  "env": {
    "PYTHONUNBUFFERED": "1",
    "VAULT_PATH": "AI_Employee_Vault",
    "{SERVICE_UPPER}_TOKEN": "${path:./.{service}_token.json}"
  }
}
```

---

## Test Harness Template

```python
import unittest
from unittest.mock import Mock, patch
from watchers.slack_watcher import SlackWatcher

class TestSlackWatcher(unittest.TestCase):
    def setUp(self):
        self.watcher = SlackWatcher(
            vault_path="test_vault",
            credentials_path="test_creds.json",
            check_interval=1  # Fast for testing
        )

    def test_check_for_updates(self):
        """Test that watcher detects new messages"""
        # Mock API response
        # Verify items returned
        pass

    def test_create_action_file(self):
        """Test action file creation"""
        # Mock item
        # Verify file created in Needs_Action
        pass

    def test_item_deduplication(self):
        """Test that duplicates are filtered"""
        # Add same item twice
        # Verify only one action file created
        pass

if __name__ == '__main__':
    unittest.main()
```

---

## Credential Setup Instructions Template

### OAuth 2.0 Setup

1. **Create OAuth App**
   - Go to service developer console
   - Create new OAuth app
   - Set redirect URI: `http://localhost:8080/callback`
   - Note client ID and secret

2. **Configure Environment**
   ```bash
   export SERVICE_CLIENT_ID="your_client_id"
   export SERVICE_CLIENT_SECRET="your_client_secret"
   ```

3. **Run Authentication Flow**
   ```bash
   python -m watchers.service_watcher --auth
   # Opens browser for OAuth approval
   ```

4. **Verify Token Saved**
   ```bash
   cat .service_token.json
   ```

### Token-Based Setup

1. **Generate API Token**
   - Go to service developer settings
   - Generate new bot token
   - Copy token securely

2. **Configure Environment**
   ```bash
   # Add to .env file (NEVER commit)
   echo "SERVICE_BOT_TOKEN='your_token_here'" >> .env
   ```

3. **Test Token**
   ```bash
   python -m watchers.service_watcher --test-token
   ```

### Session-Based Setup

1. **First-Time Setup**
   ```bash
   python -m watchers.whatsapp_watcher --setup
   # Opens browser with QR code
   # Scan QR code with mobile app
   ```

2. **Session Saved**
   - Browser session saved to `./whatsapp_session/`
   - Reuses session on subsequent runs

3. **Test Session**
   ```bash
   python -m watchers.whatsapp_watcher --test-session
   ```
