# Twitter (X) Manager - Reference

## Key Files

### Core Scripts

| File | Purpose | Location |
|------|---------|----------|
| `twitter_poster.py` | Posts to Twitter (X) via Playwright | `scripts/social-media/` |
| `twitter_approval_monitor.py` | Watches /Approved/ for approved posts | `scripts/social-media/` |

### Agent Skill Files

| File | Purpose | Location |
|------|---------|----------|
| `SKILL.md` | Skill overview | `.claude/skills/twitter-manager/` |
| `FORMS.md` | Content templates & workflows | `.claude/skills/twitter-manager/` |
| `reference.md` | This file - API reference, configuration | `.claude/skills/twitter-manager/` |
| `examples.md` | Usage examples | `.claude/skills/twitter-manager/` |

## Command Reference

### Direct Posting

```bash
# Post a tweet
python scripts/social-media/twitter_poster.py "Your tweet here"

# Post a reply
python scripts/social-media/twitter_poster.py "Your reply here" --reply-to username

# Dry run (preview without posting)
python scripts/social-media/twitter_poster.py "Test tweet" --dry-run
```

### Approval Workflow

```bash
# Start twitter_approval_monitor (background process)
python scripts/social-media/twitter_approval_monitor.py --vault .

# Test in dry-run mode
python scripts/social-media/twitter_approval_monitor.py --vault . --dry-run
```

## Twitter Poster Configuration

### Browser Setup (First Time)

**Windows:**
```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
```

**Mac/Linux:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222
```

**Session Path:** `C:\ChromeDebug` or `../whatsapp_session/` (can be customized)

### Twitter (X) Login

1. Open https://X.com in the Chrome window
2. Log in with your Twitter account
3. Verify you can access your home timeline
4. The poster will use this existing session

## Data Structures

### Approval File Frontmatter

```yaml
---
type: twitter_post
source: twitter-manager
platforms: [Twitter]
priority: medium | high
status: pending_approval
created: 2026-01-11T18:00:00Z
reply_to: @[username]  # Optional: for replies
---
```

### Post Content Structure

```javascript
// Extract reply_to from frontmatter
const replyMatch = content.match(/reply_to:\s*(.+)/);
const replyTo = replyMatch ? replyMatch[1].strip().strip('@') : null;

// Extract content
const contentMatch = content.match(/```(.+?)```/s);
const content = contentMatch ? contentMatch[1].strip() : null;

// Check character limit
if (content.length > 280) {
    console.error('Tweet exceeds 280 character limit');
}
```

## API Reference

### Twitter (X) Web Interface

**Endpoint:** `https://X.com`

**Selectors Used:**
- Tweet composer: `div[data-testid="tweet"]`
- Tweet button: `div[role="button"][data-testid="tweet"]`
- Reply button: `div[role="button"][data-testid="reply"]`
- Quote button: `div[role="button"][data-testid="quote"]`

### Playwright Stealth Features

**Human-like typing:** 0.05-0.18s per character + occasional "thinking pauses" (15% chance)

**Human-like clicking:** Hover 0.5-1.2 seconds before clicking

**Timing parameters:**
```python
TYPING_MIN_DELAY = 0.05  # Minimum delay between keystrokes
TYPING_MAX_DELAY = 0.18  # Maximum delay
THINKING_PAUSE_PROBABILITY = 0.15  # 15% chance of a thinking pause
THINKING_PAUSE_DURATION = 0.5  # Duration of thinking pause
HOVER_MIN_DELAY = 0.5  # Minimum hover before click
HOVER_MAX_DELAY = 1.2  # Maximum hover before click
```

## Troubleshooting

### Common Issues

**Q: Chrome won't connect to CDP**
```bash
# Check if Chrome is running with debugging
netstat -ano | findstr :9222

# Restart Chrome with debugging
# Windows:
taskkill /F /IM chrome.exe
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
```

**Q: "Network did not fully idle"**
- This is normal - Twitter (X) is very dynamic
- The script continues after this warning
- Manual testing: Open X.com manually to verify login

**Q: "Could not find text area"**
- Check if Twitter (X) is loaded (wait 5-10 seconds)
- Verify you're logged in
- Try different text area selectors

**Q: Tweet exceeds character limit**
- Split into a thread (use thread template)
- Shorten the content
- Remove unnecessary hashtags or mentions

**Q: "Timeout waiting for selector"**
- Twitter (X) can be slow, increase `INITIAL_PAGE_LOAD_DELAY`
- Check your internet connection
- Try a different network

## Dependencies

### Python

```bash
# Required packages
pip install playwright watchdog

# Install Chromium
playwright install chromium
```

### Configuration Files

| File | Purpose |
|------|---------|
| `config/CLAUDE.md` | Project documentation |
| `config/Company_Handbook.md` | Business rules |
| `config/Business_Goals.md` | Strategic objectives |
| `pm2.config.js` | Process manager configuration |
| `.env` | Environment variables (gitignored) |
| `.gitignore` | Git ignore rules |

## Integration Points

### Input
- Claude Code prompts for content generation
- Manual creation in `/Pending_Approval/`
- Agent skill scripts (generate_twitter_content.py)

### Processing
- `twitter_approval_monitor.py` watches `/Approved/` folder
- Extracts tweet content and reply_to
- Calls `twitter_poster.py` via subprocess

### Output
- Posts to Twitter (X)
- Creates summary in `Briefings/Twitter_Post_Summary_*.md`
- Moves files to `/Done/` after posting

## Performance

### Scan Speed
- Startup: 5-10 seconds (browser launch)
- Page load: 3-10 seconds (Twitter is faster than Meta)
- Typing: 0.5-2 seconds per 100 characters (human-like)
- Total: ~10-20 seconds per post

### Resource Usage
- Memory: ~150-300MB (Chrome instance)
- CPU: Low (idle between posts)
- Network: Only during page load and posting

## Security Considerations

### CDP Security
- Uses `--remote-debugging-port=9222` (localhost only)
- User data directory: `C:\ChromeDebug` or `../whatsapp_session`
- **Port 9222 should NOT be exposed to network**

### Credential Security
- No credentials stored in code
- Uses existing Chrome session (already logged in)
- No passwords or API keys in code
- Human approval required for posting

### Action Safeguards
- **DRY_RUN mode** for testing
- Approval workflow prevents accidental posts
- Audit logging of all actions
- Summary generation for review

## Related Skills

- **facebook-instagram-manager** - Meta platform posting
- **linkedin-manager** - LinkedIn posting
- **social-media-manager** - General social media management
- **content-generator** - Content creation templates
- **weekly-briefing** - Include Twitter metrics in weekly briefings

## Extension Points

### Adding New Content Types

**Location**: `.claude/skills/twitter-manager/FORMS.md`

Add new template:
```markdown
### Poll Tweet Template

```markdown
---
type: twitter_poll
source: twitter-manager
---

## Question
[Your poll question]

## Options
1. [Option 1]
2. [Option 2]
3. [Option 3]
4. [Option 4]
```
```

### Custom Post Templates

**Location**: `.claude/skills/twitter-manager/scripts/generate_twitter_content.py`

```python
def generate_template_post(topic, tone='engaging'):
    """Generate a template post from a topic."""
    # Your custom template logic here
    pass
```

## Best Practices

### Content Quality

1. **Always proofread** before creating approval file
2. **Test in dry-run mode** first: `--dry-run` flag
3. **Review the output** before moving to `/Approved/`
4. **Check character count** (280 limit)
5. **Verify hashtags** are relevant

### Timing Strategy

**Best times:**
- 8-9 AM: Morning commute
- 12-1 PM: Lunch break
- 5-6 PM: After work
- 7-9 PM: Evening scrolling

**Frequency:**
- 3-5 tweets per day max
- Space out posts (2-3 hours apart)
- Engage with others between posts

### Engagement Tips

- **Reply to all mentions** within 24 hours
- **Retweet valuable content** from others
- **Use threads** for longer content
- **Ask questions** to boost engagement
- **Share value** 80% of the time
- **Be authentic** and conversational

---

*Last Updated: 2026-01-11*
