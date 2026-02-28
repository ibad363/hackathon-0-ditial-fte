# Facebook & Instagram Manager - Reference

## Key Files

### Core Scripts

| File | Purpose | Location |
|------|---------|----------|
| `meta_poster.py` | Posts to FB + Instagram via Meta Business Suite | Root |
| `meta_approval_monitor.py` | Watches /Approved/ for approved posts | `scripts/social-media/` |

### Agent Skill Files

| File | Purpose | Location |
|------|---------|----------|
| `SKILL.md` | Skill overview | `.claude/skills/facebook-instagram-manager/` |
| `FORMS.md` | Content templates & workflows | `.claude/skills/facebook-instagram-manager/` |
| `reference.md` | This file - API reference, configuration | `.claude/skills/facebook-instagram-manager/` |
| `examples.md` | Usage examples | `.claude/skills/facebook-instagram-manager/` |
| `scripts/generate_fb_content.py` | Generate Facebook post content | `.claude/skills/facebook-instagram-manager/scripts/` |
| `scripts/generate_insta_content.py` | Generate Instagram post content | `.claude/skills/facebook-instagram-manager/scripts/` |

## Command Reference

### Content Generation

```bash
# Generate Facebook post
python -m .claude.skills.facebook-instagram-manager.scripts.generate_fb_content.py \
    --vault . \
    --topic "New feature launch" \
    --tone professional

# Generate Instagram post
python -m .claude.skills.facebook-instagram-manager.scripts.generate_insta_content.py \
    --vault . \
    --topic "Behind the scenes at our office" \
    --tone engaging \
    --image ./images/office.jpg
```

### Approval Workflow

```bash
# Start meta_approval_monitor (background process)
python scripts/social-media/meta_approval_monitor.py --vault .

# Test in dry-run mode
python scripts/social-media/meta_approval_monitor.py --vault . --dry-run
```

## Meta Poster Configuration

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

**Session Path:** `../whatsapp_session/` (can be customized)

### Meta Business Suite Login

1. Open https://business.facebook.com in the Chrome window
2. Log in with your Facebook account
3. Navigate to Business Suite
4. Connect your Instagram business account
5. Verify both platforms appear in the composer

### Platform Selection

Available flags:
```bash
# Default: Both platforms
python meta_poster.py "Your post here"

# Facebook only
python meta_poster.py "Your post here" --facebook-only

# Instagram only
python meta_poster.py "Your post here" --instagram-only
```

## Data Structures

### Approval File Frontmatter

```yaml
---
type: meta_post
source: facebook-instagram-manager
platforms: [Facebook, Instagram]  # or just one
priority: medium | high
status: pending_approval
created: 2026-01-11T18:00:00Z
---
```

### Post Content Structure

```javascript
// Extract platforms from frontmatter
const platformsMatch = content.match(/platforms:\s*\[([^\]]+)\]/);
const platforms = platformsMatch ? platformsMatch[1].split(',').map(p => p.trim().strip('"\'')) : ['Facebook', 'Instagram'];

// Extract content
const contentMatch = content.match(/```(.+?)```/s);
const content = contentMatch ? contentMatch[1].strip() : null;
```

## API Reference

### Meta Business Suite API

**Endpoint:** `https://business.facebook.com/latest/composer`

**Selectors Used:**
- Text areas: `div[contenteditable="true"][role="textbox"]`
- Facebook checkbox: `input[value="facebook"]` or `div[role="checkbox"][aria-label*="Facebook"]`
- Instagram checkbox: `input[value="instagram"]` or `div[role="checkbox"][aria-label*="Instagram"]`
- Publish button: `button[aria-label="Publish"]` or `button:has-text("Publish")`

### Playwright Stealth Features

**Human-like typing:** 0.05-0.18s per character + occasional "thinking pauses" (15% chance)

**Human-like clicking:** Hover 0.5-1.2 seconds before clicking

**Timing parameters:**
```python
TYPING_MIN_DELAY = 0.05  # Minimum delay between keystrokes
TYPING_MAX_DELAY = 0.18  # Maximum delay
THINKING_PAUSE_PROBABILITY = 0.15  # 15% chance of a thinking pause
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
- This is normal - Meta Business Suite is very heavy
- The script continues after this warning
- Manual testing: Open Meta Business Suite manually to verify login

**Q: "Could not find text area"**
- Check if Meta Business Suite is loaded (wait 5-10 seconds)
- Verify you're logged in
- Try different text area selectors

**Q: "Could not find enabled 'Publish' button"**
- Make sure you've typed some content first
- The Publish button only enables after typing
- Check if button is visible (check zoom level)

## Dependencies

### Python

```bash
# Required packages
pip install playwright watchdog

# Install Chromium
playwright install chromium
```

### Node.js (MCP Servers)

```bash
# For Xero MCP Server
cd mcp-servers/xero-mcp
npm install
npm run authenticate
npm start
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
- Agent skill scripts (generate_fb_content.py)

### Processing
- `meta_approval_monitor.py` watches `/Approved/` folder
- Extracts post details and platforms
- Calls `meta_poster.py` via subprocess

### Output
- Posts to Facebook and Instagram
- Creates summary in `Briefings/Meta_Post_Summary_*.md`
- Moves files to `/Done/` after posting

## Performance

### Scan Speed
- Startup: 5-10 seconds (browser launch)
- Page load: 5-15 seconds (heavy page)
- Typing: 0.5-2 seconds per 100 characters (human-like)
- Total: ~15-30 seconds per post

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

- **social-media-manager** - General social media management
- **content-generator** - Content creation templates
- **approval-manager** - Approval workflow management
- **weekly-briefing** - Include social media in weekly briefings

## Extension Points

### Adding New Keywords

**Location**: `.claude/skills/facebook-instagram-manager/scripts/generate_fb_content.py`

```python
# Add to keywords list
keywords = ['promote', 'launch', 'announcement', 'behind scenes', 'testimonial', 'company news']
```

### Custom Tones

**Location**: `.claude/skills/facebook-instagram-manager/scripts/generate_fb_content.py`

Add new tone in the `TONES` dictionary in `main()`:

```python
TONES = {
    'professional': {
        'tone': 'Professional, informative',
        'style': 'Formal, credible'
    },
    'casual': {
        'tone': 'Friendly, conversational',
        'style': 'Relatable, authentic'
    },
    'excited': {
        'tone': 'Energetic, enthusiastic',
        'style': 'High energy, emoji-heavy'
    },
    'engaging': {
        'tone': 'Interactive, question-based',
        'style': 'Stimulates discussion'
    },
    # Add your custom tone here
}
```

### Custom Post Templates

**Location**: `.claude/skills/facebook-instagram-manager/scripts/generate_fb_content.py`

```python
def generate_template_post(topic, tone='professional'):
    """Generate a template post from a topic."""
    # Your custom template logic here
    pass
```

## Best Practices

### Content Quality

1. **Always proofread** before creating approval file
2. **Test in dry-run mode** first: `--dry-run` flag
3. **Review the output** before moving to `/Approved/`
4. **Check image paths** if media attachments
5. **Verify platform selection** (Facebook vs Instagram vs both)

### Timing Strategy

**Facebook:**
- Best times: 9-10 AM, 2-3 PM, 7-8 PM
- Frequency: 2-3 posts per day

**Instagram:**
- Best times: 11 AM-1 PM, 7-10 PM
- Stories: 3-5 per day
- Posts: 1-2 per day

### Engagement Tips

**Facebook:**
- Ask questions to encourage comments
- Share links to drive traffic
- Use analytics to refine strategy
- Respond to all comments within 24 hours

**Instagram:**
- Use story stickers for interaction
- Post consistently (daily stories)
- Use 10-30 relevant hashtags
- Respond to all DMs within 24 hours
- Use "Link in bio" for external links

---

*Last Updated: 2026-01-11*