---
name: linkedin-manager
description: Manage LinkedIn posting and engagement through stealth automation using Chrome DevTools Protocol (CDP). Generate, approve, and publish professional LinkedIn posts with fast copy-paste method (100-200x faster).
license: Apache-2.0
---

# LinkedIn Manager

## Overview

Manage LinkedIn posting and engagement through stealth automation using Chrome DevTools Protocol (CDP). This skill enables you to generate, approve, and publish LinkedIn posts with professional business content and fast copy-paste method (100-200x faster).

## Key Features

- **Fast Copy-Paste Method**: 100-200x faster posting (0.3s vs 30-60s before)
- **Professional Content**: Business-focused posts with full formatting support
- **Approval Workflow**: Human-in-the-loop approval process for all posts
- **Document Support**: Post with documents, images, and links (future)
- **Dry Run Mode**: Test posts without actually publishing
- **Character Limit**: LinkedIn supports up to 3,000 characters

## Capabilities

### Generate LinkedIn Content
Create professional LinkedIn posts with:
- Hashtags
- Mentions
- Links
- Documents (future)
- Images (future)

### Approval Workflow
1. Generate content → Creates `LINKEDIN_POST_*.md` in `/Pending_Approval/`
2. Review and edit → Human reviews content
3. Move to `/Approved/` → Human approval
4. Auto-publish → `linkedin_approval_monitor.py` detects and posts

### Publishing
- Posts to LinkedIn via Chrome DevTools Protocol (CDP)
- Uses existing logged-in session
- Fast copy-paste method (100-200x faster than typing)
- Generates post-summary in `/Briefings/`

## When to Use This Skill

Use the **LinkedIn Manager** when:
- User mentions "post to LinkedIn", "share on LinkedIn", "LinkedIn post"
- User wants to engage with professional network
- Content is business-focused or professional
- Industry insights and thought leadership
- Company updates and announcements
- User mentions "LinkedIn", "professional network"

## Quick Start

```bash
# 1. Start Chrome with remote debugging (first time only)
# Windows:
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"

# 2. Log in to LinkedIn in the Chrome window
# 3. Test the poster
python scripts/social-media/linkedin_poster.py "Test post" --dry-run

# 4. Start the approval monitor
python scripts/social-media/linkedin_approval_monitor.py --vault .
```

## Workflow

### 1. Content Generation
```
User: "Create a LinkedIn post about our new feature launch"
↓
Claude: Generates content, creates LINKEDIN_POST_*.md in /Pending_Approval/
```

### 2. Human Review
```
User: Reviews /Pending_Approval/LINKEDIN_POST_*.md
↓
User: Edits if needed, then moves to /Approved/
```

### 3. Auto-Publish
```
linkedin_approval_monitor.py: Detects file in /Approved/
↓
linkedin_poster.py: Posts to LinkedIn
↓
System: Generates summary in /Briefings/, moves file to /Done/
```

## Content Guidelines

### Best Practices for LinkedIn

1. **Professional Tone**: Maintain business-appropriate language
2. **Value-First**: Share insights, not just promotions (80/20 rule)
3. **Engage Early**: Best times: 8-10 AM, 12-1 PM, 5-6 PM on weekdays
4. **Use Visuals**: Posts with images get 2x more engagement
5. **Hashtag Strategy**: 3-5 relevant hashtags maximum
6. **Mention Thoughtfully**: Tag people/companies when relevant
7. **Long-Form Content**: LinkedIn supports up to 3,000 characters

### What Works on LinkedIn

- **Industry Insights**: Your professional perspective
- **Company Updates**: Behind-the-scenes and milestones
- **Thought Leadership**: Original ideas and analysis
- **Case Studies**: Real-world examples and results
- **Professional Tips**: Value-add advice
- **Event Recaps**: Conference and meeting takeaways

### What to Avoid

- Over-posting (max 1-2 posts per day)
- Overly promotional content (mix value with promotion)
- Personal or controversial topics (unless strategic)
- Poor formatting (use line breaks and structure)
- Ignoring comments (respond within 24 hours)

## File Structure

```
.claude/skills/linkedin-manager/
├── SKILL.md              # This file
├── FORMS.md              # Content templates and workflows
├── reference.md          # API reference and configuration
├── examples.md           # Usage examples
└── scripts/
    └── generate_linkedin_content.py   # Content generation script
```

## Integration with Other Skills

### Complementary Skills

- **content-generator**: Generate blog posts → convert to LinkedIn posts
- **social-media-manager**: Coordinate across platforms (Twitter, Facebook, Instagram)
- **weekly-briefing**: Include LinkedIn metrics in weekly reports
- **approval-manager**: Centralized approval workflows

### Data Flow

```
content-generator → LinkedIn Manager (convert to post)
                              ↓
                        linkedin_approval_monitor
                              ↓
                        linkedin_poster (CDP)
                              ↓
                   Briefings/LinkedIn_Post_Summary_*.md
                              ↓
                        weekly-briefing (include metrics)
```

## Technical Details

### Browser Automation

**Tool**: Chrome DevTools Protocol (CDP) via PyCDP
**Connection**: Chrome DevTools Protocol
**Endpoint**: `http://localhost:9222`

**Why CDP?**
- Uses your existing logged-in session
- No need to handle authentication
- Preserves cookies and session data
- Avoids bot detection
- Fast copy-paste method (100-200x faster)

### Fast Copy-Paste Method

```python
# Fast method (100-200x faster)
# Copy text to clipboard using JavaScript
page.evaluate(f"navigator.clipboard.writeText({escape_json(content)})")

# Paste with Ctrl+V
keyboard_down('Control')
key_down('v')
key_up('v')
keyboard_up('Control')

# Speed: 1000 characters in ~0.3 seconds
```

### Selectors Used

```javascript
// Post composer box
POST_BOX_SELECTOR = 'div[contenteditable="true"]'

// Post button
POST_BUTTON_SELECTOR = 'button[aria-label^="Post"]'

// Close button (for closing modal)
CLOSE_BUTTON_SELECTOR = 'button[aria-label="Close"]'
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
- LinkedIn can be slow, increase `PAGE_LOAD_DELAY` in `linkedin_poster.py`
- Check your internet connection
- Try a different network
- Verify you're logged in to LinkedIn

### Character Limit

**Problem**: Post exceeds 3,000 characters

**Solution**:
- Shorten the content
- Split into multiple posts
- Remove unnecessary hashtags or mentions
- Use a linked article for long-form content

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

- [ ] Document attachments (PDF, presentations)
- [ ] Image posts with professional overlays
- [ ] Video posts
- [ ] Poll creation
- [ ] Scheduled posting
- [ ] Analytics integration
- [ ] Comment monitoring
- [ ] Mention tracking

## Related Documentation

- **FORMS.md**: Content templates and workflows
- **reference.md**: Technical reference and configuration
- **examples.md**: Real-world usage examples
- **Hackathon0.md**: Overall project architecture

---

*Last Updated: 2026-01-14*
*LinkedIn Manager Skill v1.1*
*Fast Copy-Paste Method - 100-200x Faster Posting*
