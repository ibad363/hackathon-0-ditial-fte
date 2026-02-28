---
name: twitter-manager
description: Manage Twitter (X) posting and engagement through stealth automation using Chrome DevTools Protocol (CDP). Generate, approve, and publish tweets with fast copy-paste method (100-200x faster).
license: Apache-2.0
---

# Twitter (X) Manager

## Overview

Manage Twitter (X) posting and engagement through stealth automation using Chrome DevTools Protocol (CDP). This skill enables you to generate, approve, and publish tweets to Twitter/X with fast copy-paste method (100-200x faster than typing).

## Key Features

- **Stealth Automation**: Human-like typing (0.05-0.18s per character) and hover delays (0.5-1.2s)
- **Approval Workflow**: Human-in-the-loop approval process for all posts
- **Reply Support**: Post replies to existing tweets
- **Thread Support**: Create and post tweet threads (future enhancement)
- **Dry Run Mode**: Test posts without actually publishing
- **Character Limit Enforcement**: Automatic checking against Twitter's 280 character limit

## Capabilities

### Generate Twitter Content
Create engaging tweet content with:
- Hashtags
- Mentions
- Thread structure
- Media attachments (future)
- Poll support (future)

### Approval Workflow
1. Generate content → Creates `TWITTER_POST_*.md` in `/Pending_Approval/`
2. Review and edit → Human reviews content
3. Move to `/Approved/` → Human approval
4. Auto-publish → `twitter_approval_monitor.py` detects and posts

### Publishing
- Posts to Twitter (X) via Chrome DevTools Protocol (CDP)
- Uses existing logged-in session
- Mimics human typing and clicking behavior
- Generates post-summary in `/Briefings/`

## When to Use This Skill

Use the **Twitter Manager** when:
- User mentions "post to Twitter", "tweet about", "share on X"
- User wants to engage with Twitter audience
- Content is short and concise (under 280 characters)
- Real-time updates or quick thoughts
- Behind-the-scenes content
- Industry insights and tips
- User mentions "Twitter", "X", "tweet"

## Quick Start

```bash
# 1. Start Chrome with remote debugging (first time only)
# Windows:
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"

# 2. Log in to Twitter (X) in the Chrome window
# 3. Test the poster
python scripts/social-media/twitter_poster.py "Test tweet" --dry-run

# 4. Start the approval monitor
python scripts/social-media/twitter_approval_monitor.py --vault .
```

## Workflow

### 1. Content Generation
```
User: "Create a tweet about our new feature launch"
↓
Claude: Generates content, creates TWITTER_POST_*.md in /Pending_Approval/
```

### 2. Human Review
```
User: Reviews /Pending_Approval/TWITTER_POST_*.md
↓
User: Edits if needed, then moves to /Approved/
```

### 3. Auto-Publish
```
twitter_approval_monitor.py: Detects file in /Approved/
↓
twitter_poster.py: Posts to Twitter (X)
↓
System: Generates summary in /Briefings/, moves file to /Done/
```

## Content Guidelines

### Best Practices for Twitter

1. **Keep it Short**: Aim for 200-240 characters (allows for retweets with comments)
2. **Use Hashtags Sparingly**: 1-3 relevant hashtags maximum
3. **Engage Early**: Best times: 8-9 AM, 12-1 PM, 5-6 PM
4. **Visual Content**: Use images/videos when possible
5. **Thread Strategy**: Break long content into threads (max 3-5 tweets)
6. **Reply to Mentions**: Engage with your audience within 24 hours

### What Works on Twitter

- **Tips & Advice**: Quick value-add content
- **Industry News**: Your take on current events
- **Behind the Scenes**: Show your process
- **Questions**: Engage your audience
- **Threadstorms**: Deep dives in threaded format
- **Visual Quotes**: Text on image backgrounds

### What to Avoid

- Over-posting (max 4-5 tweets per day)
- Over-hashtaging (looks spammy)
- Only self-promotion (share value 80% of the time)
- Negativity or controversial topics (unless strategic)
- URL shorteners (Twitter auto-shortens)

## File Structure

```
.claude/skills/twitter-manager/
├── SKILL.md              # This file
├── FORMS.md              # Content templates and workflows
├── reference.md          # API reference and configuration
├── examples.md           # Usage examples
└── scripts/
    └── generate_twitter_content.py   # Content generation script
```

## Integration with Other Skills

### Complementary Skills

- **content-generator**: Generate blog posts → convert to Twitter threads
- **social-media-manager**: Coordinate across platforms (Facebook, Instagram, LinkedIn)
- **weekly-briefing**: Include Twitter metrics in weekly reports
- **approval-manager**: Centralized approval workflows

### Data Flow

```
content-generator → Twitter Manager (convert to thread)
                              ↓
                        twitter_approval_monitor
                              ↓
                        twitter_poster (X)
                              ↓
                   Briefings/Twitter_Post_Summary_*.md
                              ↓
                        weekly-briefing (include metrics)
```

## Technical Details

### Browser Automation

**Tool**: Playwright (sync API)
**Connection**: Chrome DevTools Protocol (CDP)
**Endpoint**: `http://localhost:9222`

**Why CDP?**
- Uses your existing logged-in session
- No need to handle authentication
- Preserves cookies and session data
- Avoids bot detection

### Stealth Features

```python
# Human-like typing
TYPING_MIN_DELAY = 0.05  # 50ms per keystroke
TYPING_MAX_DELAY = 0.18  # 180ms per keystroke
THINKING_PAUSE_PROBABILITY = 0.15  # 15% chance of pause

# Human-like clicking
HOVER_MIN_DELAY = 0.5  # Hover 500ms before clicking
HOVER_MAX_DELAY = 1.2  # Hover 1200ms before clicking

# Network timing
INITIAL_PAGE_LOAD_DELAY = 3.0  # Wait 3s for page to stabilize
NETWORK_IDLE_TIMEOUT = 30000  # Wait up to 30s for network to settle
```

### Selectors Used

```javascript
// Tweet composer
TEXTAREA_SELECTOR = 'div[data-testid="tweet"]'

// Post button
TWEET_BUTTON_SELECTOR = 'div[role="button"][data-testid="tweet"]'

// Reply button (for replies)
REPLY_BUTTON_SELECTOR = 'div[role="button"][data-testid="reply"]'
```

## Troubleshooting

### Chrome Won't Connect

**Problem**: `Could not connect to chrome`

**Solution**:
```bash
# Make sure Chrome is running with debugging
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"

# On Mac/Linux:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222
```

### Page Timeout

**Problem**: `Timeout waiting for selector`

**Solution**:
- Twitter (X) can be slow, increase `INITIAL_PAGE_LOAD_DELAY` in `twitter_poster.py`
- Check your internet connection
- Try a different network

### Character Limit

**Problem**: Tweet exceeds 280 characters

**Solution**:
- Split into a thread (use thread template in FORMS.md)
- Shorten the content
- Remove unnecessary hashtags or mentions

## Security Considerations

### CDP Security

- **Port 9222 is localhost only** - not exposed to network
- **User data directory**: `C:\ChromeDebug` or custom path
- **No credentials stored in code** - uses existing session

### Action Safeguards

- **DRY_RUN mode** for testing
- **Approval workflow** prevents accidental posts
- **Audit logging** of all actions
- **Summary generation** for review

## Future Enhancements

- [ ] Thread support (multi-tweet posts)
- [ ] Media attachments (images, videos)
- [ ] Poll creation
- [ ] Quote tweets
- [ ] Scheduled posting
- [ ] Analytics integration
- [ ] Reply monitoring
- [ ] Mention tracking

## Related Documentation

- **FORMS.md**: Content templates and workflows
- **reference.md**: Technical reference and configuration
- **examples.md**: Real-world usage examples
- **Hackathon0.md**: Overall project architecture

---

*Last Updated: 2026-01-11*
