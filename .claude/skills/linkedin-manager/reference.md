# LinkedIn Manager - Technical Reference

This document provides technical details for the LinkedIn Manager skill.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LinkedIn Manager                      │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   Content    │ -> │  Approval    │ -> │  Posting  │ │
│  │  Generation  │    │   Workflow   │    │   (CDP)   │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Content Generation
- **Location**: `.claude/skills/linkedin-manager/`
- **Purpose**: Generate LinkedIn post content
- **Output**: `/Pending_Approval/LINKEDIN_POST_*.md`

### 2. Approval Monitor
- **Location**: `scripts/social-media/linkedin_approval_monitor.py`
- **Purpose**: Watch `/Approved/` for approved posts
- **Action**: Trigger poster when file detected
- **PM2 Process**: `linkedin-approval-monitor`

### 3. LinkedIn Poster
- **Location**: `scripts/social-media/linkedin_poster.py`
- **Purpose**: Post content to LinkedIn
- **Method**: Chrome DevTools Protocol (CDP)
- **Speed**: 100-200x faster than typing (fast copy-paste)

## File Paths

```
AI_EMPLOYEE_APP/
├── .claude/skills/linkedin-manager/
│   ├── SKILL.md                    # This skill documentation
│   ├── FORMS.md                    # Content templates
│   ├── reference.md                # This file
│   └── examples.md                 # Usage examples
│
├── scripts/social-media/
│   ├── linkedin_poster.py          # LinkedIn posting script
│   ├── linkedin_approval_monitor.py# Approval monitor
│   └── START_AUTOMATION_CHROME.bat # Start Chrome CDP
│
└── AI_Employee_Vault/
    ├── Pending_Approval/           # Awaiting approval
    ├── Approved/                   # Ready to post
    ├── Done/                       # Completed posts
    └── Briefings/                  # Post summaries
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `LINKEDIN_DRY_RUN` | Enable/disable posting | `false` |
| `CHROME_CDP_PORT` | Chrome CDP port | `9222` |
| `CHROME_USER_DATA` | Chrome profile dir | `C:\ChromeDebug` |

## PM2 Configuration

```javascript
{
  name: "linkedin-approval-monitor",
  script: "scripts/social-media/linkedin_approval_monitor.py",
  args: "--vault AI_Employee_Vault",
  interpreter: "python",
  exec_mode: "fork",
  autorestart: true,
  max_restarts: 10,
  max_memory_restart: "300M",
  env: {
    "LINKEDIN_DRY_RUN": "false",
    "PYTHONUNBUFFERED": "1"
  }
}
```

## Chrome DevTools Protocol (CDP)

### Setup

**Windows:**
```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
```

**Mac/Linux:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222
```

### CDP Connection

```python
import pycdp

# Connect to Chrome
cdp.connect(url='http://localhost:9222')

# Get target tab
tab = cdp.target.get_targets()[0]

# Create session
session = cdp.connect_session(tab)

# Navigate to LinkedIn
session.send('Page.navigate', url='https://linkedin.com')
```

### Fast Copy-Paste Method

**Old Method (Character-by-Character Typing)**:
```python
# Slow: 1000 chars = 30-60 seconds
for char in text:
    page.type(char)
    time.sleep(random.uniform(0.05, 0.18))
```

**New Method (Fast Copy-Paste)**:
```python
# Fast: 1000 chars = ~0.3 seconds (100-200x faster)
# 1. Copy to clipboard using JavaScript
page.evaluate(f"navigator.clipboard.writeText({escape_json(content)})")

# 2. Paste with Ctrl+V
keyboard_down('Control')
key_down('v')
key_up('v')
keyboard_up('Control')

# Speed improvement: 100-200x faster
```

## LinkedIn Page Selectors

### Post Box
```javascript
// Main post composer
'div[contenteditable="true"]'

// Specific selector
'div[role="textbox"]'
```

### Post Button
```javascript
// Post button (changes based on state)
'button[aria-label^="Post"]'
'button[aria-label="Post now"]'

// Alternative selector
'div[data-control-name="share.post"]'
```

### Navigation
```javascript
// Home feed
'https://linkedin.com/feed/'

// Profile
'https://linkedin.com/in/[username]'

// Company page
'https://linkedin.com/company/[company-id]'
```

## Error Handling

### Common Errors

**Error: `Could not connect to chrome`**
- **Cause**: Chrome not running with CDP
- **Solution**: Start Chrome with `--remote-debugging-port=9222`

**Error: `Timeout waiting for selector`**
- **Cause**: LinkedIn slow, page not loaded
- **Solution**: Increase `PAGE_LOAD_DELAY`

**Error: `Element not interactable`**
- **Cause**: Modal or dialog blocking interaction
- **Solution**: Close modal with ESC key or close button

**Error: `Clipboard write failed`**
- **Cause**: Permission denied or special characters
- **Solution**: Escape special characters (`\``, `$`, `\`)

### Retry Logic

```python
@with_retry(max_attempts=3, base_delay=1, max_delay=60)
def post_to_linkedin(content):
    # Posting logic
    pass
```

## Audit Logging

All LinkedIn posts are logged to `AI_Employee_Vault/Logs/YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-01-14T10:30:00Z",
  "action_type": "linkedin_post",
  "platform": "linkedin",
  "content_preview": "First 100 chars...",
  "character_count": 1250,
  "hashtags": ["#Innovation", "#Technology"],
  "result": "success",
  "post_url": "https://linkedin.com/posts/..."
}
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| **Posting Speed** | 0.3s per 1000 chars (fast paste) |
| **Old Speed** | 30-60s per 1000 chars (typing) |
| **Improvement** | 100-200x faster |
| **Success Rate** | > 95% (with retry logic) |
| **Memory Usage** | ~300MB (approval monitor) |
| **CPU Usage** | < 5% (idle), < 20% (posting) |

## Troubleshooting Commands

```bash
# Check Chrome is running
netstat -ano | findstr :9222

# Check PM2 process status
pm2 status linkedin-approval-monitor

# View approval monitor logs
pm2 logs linkedin-approval-monitor --lines 50

# Restart approval monitor
pm2 restart linkedin-approval-monitor

# Test poster manually
python scripts/social-media/linkedin_poster.py "Test post" --dry-run
```

## Security Considerations

### CDP Security
- **Port 9222** - localhost only (not exposed to network)
- **User Data Dir** - `C:\ChromeDebug` (separate from main Chrome)
- **Session Persistence** - No credentials stored in code

### Data Handling
- **No Credentials** - Uses existing LinkedIn session
- **No API Keys** - CDP uses browser cookies
- **Local Only** - All data stays on local machine

### Action Safeguards
- **DRY_RUN Mode** - Test without posting
- **Approval Workflow** - Human review required
- **Audit Logging** - All actions logged
- **Summary Generation** - Post-summary in Briefings/

## Version History

- **v1.1** (2026-01-14): Fast copy-paste method (100-200x faster)
- **v1.0** (2026-01-11): Initial release with character-by-character typing

---

*Last Updated: 2026-01-14*
