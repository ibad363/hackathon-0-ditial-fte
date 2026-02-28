# WhatsApp Manager - Reference

## Key Files

### Core Scripts

| File | Purpose | Location |
|------|---------|----------|
| `whatsapp_watcher_simple.py` | Main WhatsApp scanner | `watchers/` |
| `whatsapp_watcher_playwright.py` | Advanced scanner (clicks chats) | `watchers/` |
| `base_watcher.py` | Abstract base class | `watchers/` |

### Configuration

| File | Purpose | Key Settings |
|------|---------|--------------|
| `whatsapp_watcher_simple.py` | Keyword list | Line 35: `KEYWORDS` |
| Environment | Session path | `--session` argument |

## Command Reference

### Basic Usage

```bash
# One-time scan (current directory)
cd watchers
python whatsapp_watcher_simple.py --vault . --session ../whatsapp_session

# Custom vault location
python whatsapp_watcher_simple.py --vault /path/to/vault --session ../session

# Scan once only (default behavior)
python whatsapp_watcher_simple.py --vault . --session ../whatsapp_session
```

### Output

```
============================================================
SIMPLE WHATSAPP WATCHER
============================================================
Keywords: urgent, asap, invoice, payment, help, watch

[*] Opening WhatsApp Web...

[*] Scanning chat list for keywords...

[*] Found 23 messages with keywords

1. From: +92 300 2543640
   Keywords: help
   Preview: Help request from client...

============================================================
Done! Created 23 action files
============================================================
```

## Data Structures

### Action File Frontmatter

```yaml
---
type: whatsapp_message          # File type identifier
source: whatsapp_manager        # Source component
priority: high                  # Priority level
status: pending                 # Processing status
created: 2026-01-11T16:30:00Z   # ISO timestamp
---
```

### Message Object

```python
{
    'id': f"WHATSAPP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    'sender': '+92 300 2543640',           # Phone number or name
    'content': 'Message preview text...',   # First 200 chars
    'keywords': ['help'],                   # List of matched keywords
    'timestamp': datetime.now().isoformat() # Detection time
}
```

## Selectors and DOM Structure

### WhatsApp Web Chat List

**Selector**: `#side` (sidebar container)

**Chat item structure**:
```html
<div role="listitem" tabindex="0">
  <div>
    <span title="Contact Name">Contact Name</span>
    <div>Message preview text...</div>
  </div>
</div>
```

### Message Preview Detection

**JavaScript extraction**:
```javascript
// Scans all elements in sidebar
const side = document.querySelector('#side');
const allElements = Array.from(side.querySelectorAll('*'));

// Filters for keyword matches
const hasKeyword = keywords.some(kw =>
    textLower.includes(kw)
);
```

## API Reference

### Playwright API Used

| Method | Purpose | Parameters |
|--------|---------|------------|
| `chromium.launch_persistent_context()` | Open browser | user_data_dir, headless |
| `new_page()` / `pages[0]` | Get page object | - |
| `goto()` | Navigate to URL | url, timeout |
| `evaluate()` | Run JavaScript | script string |
| `screenshot()` | Capture page | path, full_page |

### Python Standard Library

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `pathlib.Path` | File paths | `resolve()`, `mkdir()`, `write_text()` |
| `datetime` | Timestamps | `now()`, `isoformat()`, `strftime()` |
| `hashlib` | Deduplication | Hash calculation for content |

## Troubleshooting

### Common Issues

**Issue**: "Chrome not running on port 9222"
```bash
# Solution: Start Chrome with debugging
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
```

**Issue**: "No chat elements found"
```bash
# Solution: Check WhatsApp Web is loaded
# Verify you see chat list in browser
# Check network connection
```

**Issue**: "Found 0 messages with keywords"
```bash
# Solution: Verify keywords exist in visible chats
# Check keyword list in script
# Ensure messages are recent (visible in chat list)
```

**Issue**: "Session not found"
```bash
# Solution: Re-scan QR code
# Delete old session folder
# Run watcher again to get new QR prompt
```

## Performance Characteristics

### Scan Speed

- **Startup**: 3-5 seconds (browser launch)
- **Page load**: 5-10 seconds (WhatsApp Web)
- **Scan**: 2-3 seconds (JavaScript execution)
- **Total**: ~15-20 seconds per scan

### Resource Usage

- **Memory**: ~150-300MB (Chrome headless)
- **CPU**: Minimal (idle between scans)
- **Network**: Only during page load

### Optimization Tips

1. **Reuse sessions**: Don't restart browser between scans
2. **Limit scan frequency**: Every 15-30 minutes is sufficient
3. **Keyword specificity**: More specific keywords = less noise
4. **Chat limit**: Limit to recent 20-30 chats for faster scans

## Dependencies

### Required Python Packages

```bash
pip install playwright
playwright install chromium
```

### Version Requirements

- **Python**: 3.8+
- **Playwright**: 1.40+
- **Chromium**: Bundled with Playwright

## Security Considerations

### Session Security

- **Session files**: Stored locally, never committed to git
- **QR codes**: One-time authentication, session persists
- **No credentials**: Script doesn't store passwords

### Privacy

- **Local only**: Data never leaves your machine
- **Read-only**: Script only reads, doesn't send messages
- **Preview only**: Only reads message previews, not full history

### Access Control

```bash
# Session folder permissions
chmod 700 whatsapp_session/

# Vault permissions
chmod 700 Needs_Action/
```

## Extension Points

### Adding New Keywords

**Location**: `watchers/whatsapp_watcher_simple.py:35`

```python
KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'watch',
            'meeting', 'contract']  # Add here
```

### Custom Output Format

**Location**: `watchers/whatsapp_watcher_simple.py:114-152`

Modify the `content` template in `create_action_file()`.

### Integration with Other Systems

**Example**: Send notifications
```python
# After creating action file
if send_notification:
    notify.send(f"New WhatsApp message from {sender}")
```

## Related Documentation

- **Hackathon0.md**: WhatsApp watcher specification (lines 291-324)
- **CLAUDE.md**: Project overview and architecture
- **FACEBOOK_INSTAGRAM_COMPLETE.md**: Similar social media integration pattern
