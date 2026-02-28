---
name: whatsapp-manager
description: Monitor, detect, and process WhatsApp messages automatically using Playwright web automation. Scans for important keywords and creates action files for processing.
license: Apache-2.0
---

# WhatsApp Manager Agent Skill

## Purpose

**Monitor, Detect, and Process** WhatsApp messages automatically using Playwright-based web automation. The WhatsApp Manager **scans** your WhatsApp Web chat list for important keywords (urgent, asap, invoice, payment, help, watch) and **creates** action files in your Obsidian vault for processing.

This skill enables your AI Employee to **proactively monitor** WhatsApp conversations 24/7, **extract** message previews containing critical keywords, and **trigger** appropriate workflows without manual checking.

## Design Philosophy

### Core Principles

1. **Non-Intrusive Monitoring**: Reads message previews from the chat list without marking messages as read
2. **Keyword-Driven Detection**: Filters messages by important keywords to reduce noise
3. **Session Persistence**: Uses persistent browser sessions to avoid repeated QR code scanning
4. **Human-in-the-Loop**: Creates action files for review rather than auto-responding

### Architecture

```
WhatsApp Web (Playwright)
         ↓
    Scan Chat List
         ↓
  Detect Keywords
         ↓
  Extract Message Preview
         ↓
Create Action File (.md)
         ↓
  Needs_Action/ Folder
         ↓
  Claude Processes
```

### Modularity

- **Separation of Concerns**: Detection (watcher) → Extraction (parser) → Action (file creation)
- **Configurable Keywords**: Easy to add/remove monitored keywords
- **Platform Independence**: Works on Windows, Mac, Linux via Playwright
- **Session Isolation**: Uses separate Chrome profile to avoid conflicts

## Workflow

### 1. Monitor Phase

**Launch** WhatsApp Web with persistent session:
- Connect to existing session or scan QR code (first time)
- Load chat list with recent conversations
- Parse visible message previews

**Detect** keyword matches:
- Scan all visible chat previews
- Match against keyword list (urgent, asap, invoice, payment, help, watch)
- Extract sender name, message text, timestamp

### 2. Extract Phase

**Parse** message context:
- Sender name/phone number
- Message preview (first 200 chars)
- Detected keywords (list of matches)
- Timestamp of detection

**Deduplicate** messages:
- Hash-based deduplication to avoid repeats
- Content hash: `hash(sender + content[:50])`
- Only create new files for unique messages

### 3. Action Phase

**Generate** markdown action file:
- Frontmatter with metadata (type, source, priority, status, created)
- Sender identification
- Message preview
- Detected keywords list
- Next steps suggestions

**Organize** in vault:
- Save to `Needs_Action/WHATSAPP_*.md`
- Ready for Claude processing
- Human review before response

## Scalability

### Current Capabilities

- **Scans**: Up to 50 recent chats in one pass
- **Processes**: All visible message previews
- **Keywords**: 6 default keywords (configurable)
- **Languages**: Works with any language (UTF-8)

### Scaling Options

1. **Increase Chat Coverage**: Modify scan limit in `whatsapp_watcher_simple.py`
2. **Add Keywords**: Update `KEYWORDS` list in script
3. **Continuous Monitoring**: Run on schedule (cron/Task Scheduler) every N minutes
4. **Message History**: Expand to click into chats and read full message history

## Maintainability

### Key Configuration Points

```python
# Keywords to monitor (line 35)
KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'watch']

# Vault path (command line argument)
--vault .  # Current directory

# Session path (command line argument)
--session ../whatsapp_session  # Browser session location
```

### Error Handling

- **Session Not Found**: Instructions to re-scan QR code
- **Network Timeout**: Retry with exponential backoff
- **Element Not Found**: Multiple selector fallbacks
- **Encoding Issues**: UTF-8 handling for international messages

## Action-Driven Verbs

**Detect** urgent messages from clients
**Extract** payment-related conversations
**Identify** help requests in WhatsApp
**Scan** chat list for invoice mentions
**Create** action files for follow-up
**Organize** messages by priority
**Prioritize** urgent responses
**Log** all detected messages
**Filter** noise from casual chats
**Generate** summaries of WhatsApp activity

## Integration Points

### Input Sources

- **WhatsApp Web**: https://web.whatsapp.com (via Playwright)
- **Browser Session**: Persistent Chrome profile
- **Chat List**: Visible message previews

### Output Destinations

- **Needs_Action/**: Action files for processing
- **Logs/**: Daily JSON logs of detected messages
- **Briefings/**: WhatsApp activity summaries

### Related Skills

- **Social Media Manager**: Handle social media mentions
- **Approval Manager**: Approve WhatsApp responses
- **Content Generator**: Generate reply templates
- **Daily Review**: Include WhatsApp in daily briefings
