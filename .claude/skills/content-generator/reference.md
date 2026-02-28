# Content Generator - Reference

## Key Files

| File | Purpose |
|------|---------|
| `Company_Handbook.md` | Tone, style guidelines, approval thresholds |
| `/Pending_Approval/` | Draft content awaiting human review |
| `/Approved/` | Approved content ready for posting |
| `/Social_Media/` | Posted content archive and analytics |
| `Dashboard.md` | Content calendar and upcoming posts |

## Platform-Specific Resources

### LinkedIn
| Feature | Details |
|---------|---------|
| Character limit | 3,000 (optimal: 1,300) |
| Hashtags | 3-5 per post |
| Media types | Images, PDFs, documents, videos |
| Best posting times | Tue-Thu, 8-10am, 5-6pm |
| Engagement drivers | Questions, polls, mentions |

### Twitter/X
| Feature | Details |
|---------|---------|
| Character limit | 280 (25,000 premium) |
| Hashtags | 1-2 per tweet |
| Media types | Images, GIFs, videos |
| Best posting times | Weekdays 12-3pm |
| Engagement drivers | Threads, quotes, retweets |

### Email
| Feature | Details |
|---------|---------|
| Subject line | 30-50 characters |
| Preview text | First 80 characters |
| Body | 200-500 words |
| CTA | Single, clear action |

## Content Types

### Educational Content
- How-to guides
- Tips and best practices
- Industry insights
- Tool reviews
- Tutorials

### Promotional Content
- Product launches
- Service announcements
- Special offers
- Event promotions
- Case studies

### Engagement Content
- Questions
- Polls
- Behind-the-scenes
- Personal stories
- Industry predictions

## Content Calendar Structure

| Day | Platform | Topic | Type | Status |
|-----|----------|-------|------|--------|
| Mon | LinkedIn | Industry insight | Educational | Scheduled |
| Wed | LinkedIn | Product tip | Promotional | Draft |
| Fri | Twitter | Quick tip | Educational | Scheduled |
| etc. | | | | |

## Approval Workflow

1. **Generate** content using this skill
2. **Save** to `/Pending_Approval/`
3. **Human reviews** content
4. **Edit** based on feedback
5. **Move** to `/Approved/`
6. **MCP Server** posts to platform
7. **Archive** to `/Social_Media/` with analytics

## Related Skills

- `social-media-manager` - Posts generated content
- `approval-manager` - Manages approval workflow
- `weekly-briefing` - Reports on content performance

## Scripts

### `scripts/generate_linkedin_post.py`

Generate LinkedIn posts based on topic and goals.

### `scripts/generate_email_draft.py`

Generate email drafts for various purposes.

### `scripts/optimize_content.py`

Analyze and optimize content for engagement.
