---
name: email-manager
description: Monitor, detect, and process Gmail emails automatically using the Gmail API. Scans inbox for important emails and creates action files for processing.
license: Apache-2.0
---

# Email Manager Agent Skill

## Purpose

**Monitor, Detect, and Process** Gmail emails automatically using the Gmail API. The Email Manager **scans** your inbox for important emails (unread, flagged, keyword matches) and **creates** action files in your Obsidian vault for processing.

This skill enables your AI Employee to **proactively monitor** email communications 24/7, **extract** email content and metadata, and **trigger** appropriate workflows without manual inbox checking.

## Design Philosophy

### Core Principles

1. **API-Based Monitoring**: Uses official Gmail API for reliable access
2. **Keyword and Flag Filtering**: Detects important emails via unread status, flags, and content keywords
3. **OAuth2 Authentication**: Secure token-based authentication (no password storage)
4. **Incremental Processing**: Tracks processed emails to avoid duplicates
5. **Human-in-the-Loop**: Creates action files for review rather than auto-responding

### Architecture

```
Gmail API (OAuth2)
      ↓
Query Messages
      ↓
Filter (unread/flags/keywords)
      ↓
Extract Content
      ↓
Create Action File (.md)
      ↓
Needs_Action/ Folder
      ↓
Claude Processes
```

### Modularity

- **Separation of Concerns**: Authentication → Query → Filter → Extract → Action
- **Configurable Filters**: Easy to customize keywords, flags, search queries
- **Token Management**: Secure credential storage and refresh
- **Watchdog Integration**: Can run continuously or on schedule

## Workflow

### 1. Authenticate Phase

**Setup OAuth2 credentials**:
- Create Google Cloud project
- Enable Gmail API
- Generate OAuth2 credentials
- Save token file locally (never committed)

**Token refresh**:
- Automatic token refresh on expiration
- Secure credential storage
- No password storage required

### 2. Query Phase

**Search for important emails**:
```python
# Query unread important emails
query = 'is:unread is:important'

# Add keyword filters
keywords = ['urgent', 'asap', 'invoice', 'payment', 'deadline']
```

**Gmail search syntax**:
- `is:unread` - Unread messages
- `is:important` - Marked as important
- `has:attachment` - Has attachments
- `from:sender@example.com` - From specific sender
- `subject:invoice` - Subject contains text

### 3. Extract Phase

**Parse email content**:
- From (sender)
- To (recipient)
- Subject
- Body (plain text and HTML)
- Timestamp
- Attachments list
- Thread ID

**Generate summary**:
- Key information extraction
- Priority assessment
- Action recommendations

### 4. Action Phase

**Generate** markdown action file:
```markdown
---
type: email
source: gmail_watcher
priority: high
status: pending
created: 2026-01-11T17:00:00Z
---

# Email from [Sender]

## Subject
[Email subject]

## From
[Sender email]

## Summary
[Extracted key points]

## Suggested Actions
- [ ] Review email content
- [ ] Check attachments
- [ ] Draft response or action plan
---
```

**Organize** in vault:
- Save to `Needs_Action/EMAIL_*.md`
- Track processed email IDs
- Ready for Claude processing

## Scalability

### Current Capabilities

- **Scans**: Up to 50 emails per batch
- **Filters**: Multiple filter criteria (unread, flags, keywords)
- **Keywords**: Configurable keyword list
- **Rate Limits**: Respects Gmail API quota

### Scaling Options

1. **Batch Processing**: Increase batch size (watchers/gmail_watcher.py)
2. **Continuous Monitoring**: Run watchdog every 5-10 minutes
3. **Advanced Filters**: Add Gmail search queries
4. **Label Management**: Auto-label processed emails
5. **Attachment Processing**: Download and analyze attachments

## Maintainability

### Key Configuration Points

```python
# Gmail watcher configuration
class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path, credentials_path, check_interval=120):
        self.credentials_path = credentials_path
        self.processed_ids = set()  # Track processed emails
        self.keywords = ['urgent', 'asap', 'invoice', 'payment']  # Keywords
```

### Error Handling

- **Token Expired**: Automatic refresh with retry
- **API Quota Exceeded**: Exponential backoff and retry
- **Network Timeout**: Graceful degradation and retry
- **Authentication Failed**: Clear instructions to re-authenticate

## Action-Driven Verbs

**Monitor** Gmail inbox for important emails
**Detect** unread and flagged messages
**Extract** email content and metadata
**Filter** by keywords and priority
**Create** action files for review
**Organize** emails by sender and subject
**Prioritize** urgent email responses
**Track** processed email IDs
**Log** all email detections
**Generate** email summaries
**Identify** action-required emails
**Aggregate** email metrics

## Integration Points

### Input Sources

- **Gmail API**: https://developers.google.com/gmail/api
- **OAuth2 Credentials**: Client ID and secret
- **Token File**: Stored locally (never committed)

### Output Destinations

- **Needs_Action/**: Email action files
- **Logs/**: Daily JSON logs of detected emails
- **Accounting/**: Invoice/payment emails

### Related Skills

- **Accounting**: Process invoice emails
- **Approval Manager**: Approve email responses
- **Content Generator**: Generate email replies
- **Daily Review**: Include emails in daily briefings
- **WhatsApp Manager**: Cross-reference with WhatsApp messages
