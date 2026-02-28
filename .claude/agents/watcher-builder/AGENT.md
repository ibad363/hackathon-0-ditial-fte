---
name: watcher-builder
description: Generate complete watcher scripts that inherit from BaseWatcher with PM2 configuration, authentication code, and test harness. Use when you need to create a new watcher for any service (Slack, Telegram, Jira, etc.).
---

# Watcher Builder Agent

Rapidly scaffold complete, production-ready watcher scripts for the AI Employee system.

## When to Use This Agent

Use this agent when you need to:
- Create a new watcher for an external service (API, webhook, polling)
- Add monitoring for a new data source (database, message queue, etc.)
- Generate a watcher with proper error handling and logging
- Create a watcher that integrates with the PM2 process manager
- Build watchers with OAuth, token-based, or session authentication

## What This Agent Does

Watcher Builder generates complete, production-ready watcher scripts including:

1. **Full Watcher Class** - Inherits from `BaseWatcher` with all required methods
2. **Authentication Code** - OAuth 2.0, API tokens, or session management
3. **PM2 Configuration** - Ready-to-use process manager configuration
4. **Credential Setup** - Step-by-step setup instructions
5. **Test Harness** - Unit tests and integration test template
6. **Error Handling** - Comprehensive error recovery and logging
7. **Documentation** - Auto-generated README and usage examples

## Quick Start

### Basic Usage

```
Create a watcher for Slack API with OAuth authentication:
- Service: Slack
- Auth type: OAuth 2.0
- Check interval: 60 seconds
- Important events: mentions, DMs, messages in monitored channels
```

### Advanced Usage

```
Create a Telegram watcher with:
- Bot token authentication
- Polling for updates via getUpdates API
- Filter for commands and keywords
- Webhook fallback support
- Rate limiting handling
```

## Workflow

1. **Specify Service Details**
   - Service name (e.g., "slack", "telegram", "jira")
   - API endpoints or documentation
   - Authentication type (OAuth, token, session)

2. **Define Event Filtering**
   - What events are important?
   - Filtering criteria (keywords, priorities, labels)
   - Action file naming pattern

3. **Generate Watcher**
   - Creates complete watcher class
   - Generates authentication code
   - Adds PM2 configuration
   - Creates credential templates

4. **Customize & Test**
   - Review generated code
   - Adjust filtering logic
   - Run test harness
   - Deploy with PM2

## Output Structure

```
watchers/
├── slack_watcher.py           ← Generated watcher
├── .slack_token.json          ← Token storage
└── slack_credentials.json     ← API credentials

process-manager/
└── pm2.config.js              ← Updated with new watcher

.claude/agents/watcher-builder/
└── outputs/
    ├── slack_test.py          ← Test harness
    └── slack_README.md        ← Documentation
```

## Authentication Types

### OAuth 2.0
For services like Gmail, Slack, Jira, Notion:
- Token refresh logic
- Authorization URL generation
- Callback handling
- Persistent token storage

### API Token
For services like Telegram, Discord, Stripe:
- Header-based authentication
- Token validation
- Expiry handling
- Secure storage patterns

### Session-Based
For services like WhatsApp Web:
- Browser session persistence
- QR code authentication
- Cookie management
- Session recovery

## Watcher Features

### BaseWatcher Interface

All generated watchers implement:

```python
class [Service]Watcher(BaseWatcher):
    def check_for_updates(self) -> list:
        """Return list of new items to process"""

    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""

    def get_item_id(self, item) -> str:
        """Return unique identifier for deduplication"""
```

### Included Features

- ✅ JSONL logging to `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- ✅ Item deduplication using `processed_ids` set
- ✅ Configurable check intervals
- ✅ Dry run mode for testing
- ✅ Graceful error handling
- ✅ PM2 process management
- ✅ Automatic folder creation
- ✅ Token refresh logic (OAuth)

## Templates

See `references/FORMS.md` for:
- OAuth watcher template
- Token-based watcher template
- Session-based watcher template
- Action file templates
- Test harness templates

## Reference

See `references/reference.md` for:
- BaseWatcher API documentation
- PM2 configuration options
- Error handling patterns
- Logging formats
- Credential security best practices

## Examples

See `references/examples.md` for:
- Complete Slack watcher walkthrough
- Telegram bot watcher example
- Jira issue watcher case study
- Testing and deployment guides

---

**Next:** Use the watcher-builder agent to generate your first watcher!
