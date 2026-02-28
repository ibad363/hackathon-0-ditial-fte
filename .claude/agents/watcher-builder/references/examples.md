---
name: watcher-builder
description: Complete examples demonstrating how to use the Watcher Builder skill
license: MIT
---

# Watcher Builder Examples

Complete examples demonstrating how to use the Watcher Builder skill.

---

## Example 1: Slack Watcher

A complete walkthrough of creating a Slack watcher with OAuth authentication.

### Scenario

You want to monitor Slack for:
- Direct messages to your bot
- Messages in specific channels
- Messages mentioning your bot

### Step 1: Describe Requirements

```
I need a Slack watcher that:
- Uses OAuth 2.0 authentication
- Monitors for DMs and channel messages
- Checks for mentions: @bot
- Polls every 60 seconds
- Creates action files in Needs_Action/
```

### Step 2: Configuration

The watcher builder generates this configuration:

```yaml
service_name: "slack"
auth_type: "oauth"
oauth_config:
  auth_uri: "https://slack.com/oauth/v2/authorize"
  token_uri: "https://slack.com/api/oauth.v2.access"
  scopes:
    - "channels:history"
    - "im:history"
    - "mpim:history"
    - "groups:history"
  client_id_var: "SLACK_CLIENT_ID"
  client_secret_var: "SLACK_CLIENT_SECRET"
check_interval: 60
filter_criteria:
  - type: "direct_message"
  - type: "mention"
    pattern: "@bot"
  - type: "channel"
    channels: ["#general", "#alerts"]
```

### Step 3: Generated Watcher Code

**File:** `watchers/slack_watcher.py`

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from watchers.base_watcher import BaseWatcher
from pathlib import Path
import json
import logging
from datetime import datetime
import re

class SlackWatcher(BaseWatcher):
    """Watch Slack for important messages"""

    def __init__(self, vault_path: str, credentials_path: str,
                 check_interval: int = 60):
        super().__init__(vault_path, check_interval)
        self.credentials_path = Path(credentials_path)
        self.token_path = self.credentials_path.parent / '.slack_token.json'
        self.client = None
        self.bot_user_id = None

        # Authenticate on init
        self._authenticate()

        # Filter config
        self.monitored_channels = []
        self.mention_pattern = re.compile(r'<@(\w+)>')

    def _authenticate(self):
        """Load or refresh OAuth token"""
        if not self.token_path.exists():
            raise FileNotFoundError(
                f"Token file not found: {self.token_path}\n"
                "Run authentication flow first: "
                "python -m watchers.slack_watcher --auth"
            )

        with open(self.token_path) as f:
            token_data = json.load(f)

        access_token = token_data.get('access_token')
        if not access_token:
            raise ValueError("Invalid token file format")

        self.client = WebClient(token=access_token)

        # Get bot user ID for mention detection
        auth_info = self.client.auth_test()
        self.bot_user_id = auth_info['user_id']

        self.log_action('authenticated', {'bot_id': self.bot_user_id})

    def check_for_updates(self) -> list:
        """Check for new messages"""
        new_items = []

        try:
            # 1. Check DMs
            ims = self._check_direct_messages()
            new_items.extend(ims)

            # 2. Check mentions in channels
            mentions = self._check_mentions()
            new_items.extend(mentions)

            # 3. Check monitored channels
            channel_msgs = self._check_monitored_channels()
            new_items.extend(channel_msgs)

        except SlackApiError as e:
            self.logger.error(f"Slack API error: {e}")
            self.log_action('api_error', {'error': str(e)})
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.log_action('error', {'error': str(e)})

        return new_items

    def _check_direct_messages(self) -> list:
        """Check for new DMs"""
        # List all DM conversations
        conversations = self.client.conversations_list(
            types='im,mpim'
        )['channels']

        messages = []
        for conv in conversations:
            # Get conversation history
            history = self.client.conversations_history(
                channel=conv['id'],
                limit=10
            )

            for msg in history['messages']:
                # Skip messages from bot
                if msg.get('user') == self.bot_user_id:
                    continue

                item_id = self.get_item_id(msg)
                if item_id in self.processed_ids:
                    continue

                messages.append({
                    'type': 'direct_message',
                    'channel_id': conv['id'],
                    'channel_name': conv.get('name', 'DM'),
                    'message': msg
                })

        return messages

    def _check_mentions(self) -> list:
        """Check for bot mentions in public channels"""
        # Search messages containing bot mention
        # Implementation depends on Slack search API
        return []

    def _check_monitored_channels(self) -> list:
        """Check monitored channels for new messages"""
        messages = []

        for channel in self.monitored_channels:
            history = self.client.conversations_history(
                channel=channel['id'],
                limit=10
            )

            for msg in history['messages']:
                if msg.get('user') == self.bot_user_id:
                    continue

                item_id = self.get_item_id(msg)
                if item_id in self.processed_ids:
                    continue

                messages.append({
                    'type': 'channel_message',
                    'channel_id': channel['id'],
                    'channel_name': channel['name'],
                    'message': msg
                })

        return messages

    def get_item_id(self, item) -> str:
        """Get unique message ID"""
        return f"slack_{item['message']['ts']}"

    def create_action_file(self, item) -> Path:
        """Create action file for message"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        msg_type = item['type']
        channel = item['channel_name']

        filename = f"SLACK_{timestamp}_{msg_type}_{channel}.md"
        filepath = self.needs_action / filename

        msg = item['message']
        user = msg.get('user', 'Unknown')
        text = msg.get('text', '')

        content = f'''---
type: slack_message
service: slack
message_type: {msg_type}
channel: {item['channel_name']}
channel_id: {item['channel_id']}
user: {user}
timestamp: {datetime.utcnow().isoformat()}
priority: high
status: pending
---

# Slack Message from {channel}

**From User:** {user}
**Channel:** {item['channel_name']}
**Type:** {msg_type}

## Message Content

{text}

## Suggested Actions

- [ ] Reply to message
- [ ] Create task if action needed
- [ ] Archive after processing
'''

        filepath.write_text(content)
        self.log_action('created_action_file', {
            'filename': filename,
            'type': msg_type,
            'channel': channel
        })

        return filepath

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--vault', default='AI_Employee_Vault')
    parser.add_argument('--credentials', default='.slack_credentials.json')
    parser.add_argument('--interval', type=int, default=60)
    parser.add_argument('--auth', action='store_true',
                       help='Run OAuth flow')
    parser.add_argument('--dry-run', action='store_true')

    args = parser.parse_args()

    if args.auth:
        # Run OAuth flow
        print("Starting OAuth flow...")
        # OAuth implementation here
    else:
        # Run watcher
        watcher = SlackWatcher(
            vault_path=args.vault,
            credentials_path=args.credentials,
            check_interval=args.interval
        )
        watcher.run()
```

### Step 4: PM2 Configuration

**Add to `process-manager/pm2.config.js`:**

```javascript
{
  name: "slack-watcher",
  "script": "python -m watchers.slack_watcher --vault AI_Employee_Vault --credentials .slack_credentials.json",
  "interpreter": "python3",
  "exec_mode": "fork",
  "autorestart": true,
  "watch": false,
  "max_restarts": 10,
  "max_memory_restart": "500M",
  "env": {
    "PYTHONUNBUFFERED": "1",
    "VAULT_PATH": "AI_Employee_Vault"
  }
}
```

### Step 5: Credential Setup

**Create `.slack_credentials.json`:**

```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "redirect_uri": "http://localhost:8080/callback"
}
```

**Run OAuth flow:**

```bash
python -m watchers.slack_watcher --auth
# Opens browser for Slack OAuth approval
# Token saved to .slack_token.json
```

### Step 6: Test

```bash
# Test watcher (dry run)
python -m watchers.slack_watcher --vault AI_Employee_Vault --dry-run

# Start with PM2
pm2 restart process-manager/pm2.config.js

# Check logs
pm2 logs slack-watcher

# Verify action files created
ls AI_Employee_Vault/Needs_Action/
```

---

## Example 2: Telegram Bot Watcher

Creating a Telegram bot watcher with token-based authentication.

### Requirements

```
Telegram bot watcher:
- Bot token authentication
- Polls for updates via getUpdates API
- Monitors for bot commands (/start, /help, etc.)
- Monitors for keywords: urgent, invoice, payment
- Checks every 30 seconds
```

### Generated Code

**File:** `watchers/telegram_watcher.py`

```python
import requests
from watchers.base_watcher import BaseWatcher
from pathlib import Path
import logging
from datetime import datetime

class TelegramWatcher(BaseWatcher):
    """Watch Telegram for bot commands and keywords"""

    def __init__(self, vault_path: str, token: str,
                 check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.token = token
        self.api_base = f"https://api.telegram.org/bot{token}/"
        self.offset = 0

        # Keywords to monitor
        self.keywords = ['urgent', 'invoice', 'payment', 'help']

    def _make_request(self, method: str, params: dict = None):
        """Make authenticated API request"""
        url = self.api_base + method
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def check_for_updates(self) -> list:
        """Poll for new updates"""
        try:
            result = self._make_request('getUpdates', {
                'offset': self.offset,
                'timeout': 0,
                'limit': 100
            })

            if not result.get('ok'):
                self.logger.error(f"API error: {result}")
                return []

            updates = result.get('result', [])
            new_items = []

            for update in updates:
                # Update offset for next poll
                self.offset = update['update_id'] + 1

                # Check if message
                if 'message' not in update:
                    continue

                message = update['message']
                item_id = self.get_item_id(update)

                if item_id in self.processed_ids:
                    continue

                # Check if important
                if self._is_important(message):
                    new_items.append({
                        'update': update,
                        'message': message
                    })

            return new_items

        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return []

    def _is_important(self, message) -> bool:
        """Check if message is important"""
        # Bot commands are always important
        if 'text' in message:
            text = message['text'].lower()

            # Check for bot command
            if text.startswith('/'):
                return True

            # Check for keywords
            for keyword in self.keywords:
                if keyword in text:
                    return True

        return False

    def get_item_id(self, item) -> str:
        """Get unique update ID"""
        return f"telegram_{item['update']['update_id']}"

    def create_action_file(self, item) -> Path:
        """Create action file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        message = item['message']
        chat_id = message['chat']['id']
        chat_name = message['chat'].get('title',
                       message['chat'].get('first_name',
                       'Unknown'))

        filename = f"TELEGRAM_{timestamp}_{chat_id}.md"
        filepath = self.needs_action / filename

        text = message.get('text', '')
        from_user = message.get('from', {}).get('first_name', 'Unknown')

        content = f'''---
type: telegram_message
service: telegram
chat_id: {chat_id}
chat_name: {chat_name}
from: {from_user}
timestamp: {datetime.utcnow().isoformat()}
priority: high
status: pending
---

# Telegram Message

**From:** {from_user}
**Chat:** {chat_name}
**Chat ID:** {chat_id}

## Message Content

{text}

## Suggested Actions

- [ ] Reply via Telegram
- [ ] Forward to relevant person
- [ ] Create task if action needed
- [ ] Archive after processing
'''

        filepath.write_text(content)
        self.log_action('created_action_file', {
            'filename': filename,
            'chat_id': chat_id
        })

        return filepath
```

---

## Example 3: Testing Your Watcher

### Unit Test Example

**File:** `tests/test_slack_watcher.py`

```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from watchers.slack_watcher import SlackWatcher
import json
from pathlib import Path

class TestSlackWatcher(unittest.TestCase):
    def setUp(self):
        self.vault_path = Path("test_vault")
        self.vault_path.mkdir(exist_ok=True)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)

        # Create test token file
        self.token_path = self.vault_path / ".slack_token.json"
        self.token_path.write_text(json.dumps({
            'access_token': 'test_token'
        }))

        self.watcher = SlackWatcher(
            vault_path=str(self.vault_path),
            credentials_path=str(self.token_path),
            check_interval=1  # Fast for testing
        )

    def tearDown(self):
        # Cleanup test files
        import shutil
        if self.vault_path.exists():
            shutil.rmtree(self.vault_path)

    @patch('watchers.slack_watcher.WebClient')
    def test_check_for_updates(self, mock_client):
        """Test that watcher detects new messages"""
        # Mock Slack client
        mock_api = MagicMock()
        mock_client.return_value = mock_api

        # Mock auth test response
        mock_api.auth_test.return_value = {'user_id': 'U123BOT'}

        # Mock conversations list
        mock_api.conversations_list.return_value = {
            'channels': [
                {'id': 'D123', 'name': 'dm_channel'}
            ]
        }

        # Mock conversation history
        mock_api.conversations_history.return_value = {
            'messages': [
                {
                    'ts': '1234567890.123456',
                    'user': 'U999',
                    'text': 'Hello bot!'
                }
            ]
        }

        # Reinitialize to trigger auth
        self.watcher._authenticate()

        # Check for updates
        items = self.watcher.check_for_updates()

        # Assert
        self.assertGreater(len(items), 0)
        self.assertEqual(items[0]['type'], 'direct_message')

    def test_create_action_file(self):
        """Test action file creation"""
        item = {
            'type': 'direct_message',
            'channel_id': 'D123',
            'channel_name': 'DM',
            'message': {
                'ts': '1234567890.123456',
                'user': 'U999',
                'text': 'Test message'
            }
        }

        filepath = self.watcher.create_action_file(item)

        # Verify file exists
        self.assertTrue(filepath.exists())

        # Verify content
        content = filepath.read_text()
        self.assertIn('type: slack_message', content)
        self.assertIn('Test message', content)

    def test_item_deduplication(self):
        """Test that duplicates are filtered"""
        item = {'message': {'ts': '1234567890.123456'}}

        # Get ID twice
        id1 = self.watcher.get_item_id(item)
        id2 = self.watcher.get_item_id(item)

        # Should be same
        self.assertEqual(id1, id2)

        # After processing, should be in set
        self.watcher.processed_ids.add(id1)
        self.assertIn(id1, self.watcher.processed_ids)

if __name__ == '__main__':
    unittest.main()
```

### Run Tests

```bash
python -m pytest tests/test_slack_watcher.py -v
```

---

## Example 4: Deployment Checklist

### Pre-Deployment

- [ ] Watcher code written and tested
- [ ] Unit tests passing
- [ ] Authentication configured
- [ ] PM2 config updated
- [ ] Environment variables set
- [ ] .gitignore excludes credentials

### Deployment Steps

1. **Install dependencies**
   ```bash
   pip install slack-sdk
   ```

2. **Configure credentials**
   ```bash
   export SLACK_CLIENT_ID="your_id"
   export SLACK_CLIENT_SECRET="your_secret"
   ```

3. **Run authentication**
   ```bash
   python -m watchers.slack_watcher --auth
   ```

4. **Test locally**
   ```bash
   python -m watchers.slack_watcher --vault AI_Employee_Vault --dry-run
   ```

5. **Start with PM2**
   ```bash
   pm2 start process-manager/pm2.config.js
   pm2 list
   ```

6. **Monitor**
   ```bash
   pm2 logs slack-watcher
   ```

7. **Verify**
   ```bash
   ls AI_Employee_Vault/Needs_Action/
   cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | tail -5
   ```

---

## Common Pitfalls

### 1. Forgetting to inherit from BaseWatcher

❌ **Wrong:**
```python
class SlackWatcher:
    pass
```

✅ **Right:**
```python
from watchers.base_watcher import BaseWatcher

class SlackWatcher(BaseWatcher):
    pass
```

### 2. Not implementing abstract methods

❌ **Missing:**
```python
class SlackWatcher(BaseWatcher):
    pass  # Missing abstract methods
```

✅ **Implemented:**
```python
class SlackWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        return []

    def create_action_file(self, item) -> Path:
        return Path("test.md")

    def get_item_id(self, item) -> str:
        return "id"
```

### 3. Committing credentials

❌ **Wrong:**
```gitignore
# Missing credential files
```

✅ **Right:**
```gitignore
# Credentials
*_token.json
*_credentials.json
.env
.client_secret.json
```

---

**Next:** Try building your own watcher using `/watcher-builder`!
