# Social Media Manager - Forms and Templates

## Post Schedule Template

```markdown
---
platform: [LinkedIn|Twitter|Instagram|Facebook]
content_id: [identifier]
scheduled_date: YYYY-MM-DD
scheduled_time: HH:MM
timezone: [timezone]
status: [scheduled|posted|failed]
---

# Post: [Title]

## Content
[Content preview or summary]

## Target Audience
- **Demographics:** [age, location, industry]
- **Interests:** [topics they care about]

## Goals
- [ ] Engagement target (likes, comments, shares)
- [ ] Conversion goal (clicks, signups)
- [ ] Brand awareness

## Posting Details
- **Date:** YYYY-MM-DD
- **Time:** HH:MM [Timezone]
- **Platform:** [Platform]
- **Format:** [Text, Image, Video, Link]

## Performance Targets
- **Engagement Rate:** >5%
- **Click-Through Rate:** >2%
- **Shares:** >10

## Post-Engagement Plan
- [ ] Respond to all comments within 24 hours
- [ ] Thank people for shares
- [ ] Answer questions
```

## Engagement Tracking Template

```markdown
---
post_id: [identifier]
platform: [platform]
posted_date: YYYY-MM-DD
days_since_posting: [number]
---

# Engagement Report: [Post Title]

## Metrics (as of [Time])
- **Impressions:** [number]
- **Likes/Reactions:** [number]
- **Comments:** [number]
- **Shares:** [number]
- **Clicks:** [number]

## Engagement Rate
- **Total Engagement:** [number]
- **Engagement Rate:** [percentage]
- **vs. Average:** [above/below]

## Top Comments
1. [Comment 1]
   - **Author:** [Name]
   - **Likes:** [number]
   - **Sentiment:** [positive/negative/neutral]

2. [Comment 2]
   - **Author:** [Name]
   - **Likes:** [number]
   - **Sentiment:** [positive/negative/neutral]

## Action Items
- [ ] Respond to question from [User]
- [ ] Thank [User] for sharing
- [ ] Follow up on [topic]

## Insights
- [ ] What worked well
- [ ] What didn't work
- [ ] Ideas for future content
```

## Content Calendar Template

```markdown
# Content Calendar: Week of [Date]

## LinkedIn

| Day | Topic | Type | Status | Scheduled Time |
|----|-------|------|--------|----------------|
| Mon | [Topic] | [Type] | Scheduled | 8:00 AM EST |
| Wed | [Topic] | [Type] | Scheduled | 12:00 PM EST |
| Fri | [Topic] | [Type] | Scheduled | 5:00 PM EST |

## Twitter/X

| Day | Topic | Type | Status | Scheduled Time |
|----|-------|------|--------|----------------|
| Mon-Wed | [Topic] | Thread | Scheduled | 12-3 PM EST |
| Thu | [Topic] | Tweet | Scheduled | 2:00 PM EST |
| Fri | [Topic] | Tweet | Scheduled | 4:00 PM EST |

## Instagram

| Day | Topic | Format | Status | Scheduled Time |
|----|-------|--------|--------|----------------|
| Tue | [Topic] | [Format] | Scheduled | 6:00 PM EST |
| Thu | [Topic] | [Format] | Scheduled | 7:30 PM EST |
| Sat | [Topic] | Story | Scheduled | 10:00 AM EST |

## Facebook

| Day | Topic | Type | Status | Scheduled Time |
|----|-------|------|--------|----------------|
| Mon | [Topic] | Post | Scheduled | 9:00 AM EST |
| Wed | [Topic] | Share | Scheduled | 12:00 PM EST |
| Fri | [Topic] | Post | Scheduled | 4:00 PM EST |
```

## Platform Best Practices

### LinkedIn
- **Optimal Times:** Tuesday-Thursday, 8-10am or 5-6pm
- **Content Length:** 1,300-3,000 characters
- **Hashtags:** 3-5 relevant tags
- **Media:** Images, PDFs, documents, videos
- **Engagement:** Questions, polls, mentions
- **Frequency:** 2-3 posts per week

### Twitter/X
- **Optimal Times:** Weekdays 12-3pm, evenings 7-9pm
- **Content Length:** 280 characters (25,000 premium)
- **Hashtags:** 1-2 tags
- **Media:** Images, GIFs, short videos
- **Engagement:** Threads, quotes, retweets
- **Frequency:** 3-5 tweets per day

### Instagram
- **Optimal Times:** Monday-Friday, 6-9pm, weekends 10am-2pm
- **Content Types:** Stories (daily), Feed posts (3-4/week)
- **Hashtags:** 5-10 relevant tags + location
- **Media:** High-quality images, carousels, videos
- **Engagement:** Stories stickers, replies, DMs
- **Frequency:** 1 story daily, 1-2 feed posts/week

### Facebook
- **Optimal Times:** Thursday-Sunday, 1-4pm
- **Content Types:** Posts, shares, stories
- **Hashtags:** 2-4 tags
- **Media:** Images, videos, links
- **Engagement:** Comments, reactions, shares
- **Frequency:** 3-5 posts per week

## Posting Workflow

### Manual Posting (Current)
```
1. Content Generator creates draft → `/Pending_Approval/`
2. Human reviews and moves to `/Approved/`
3. Social Media Manager schedules the post
4. Human manually posts at scheduled time
```

### Automated Posting (Future - with MCP Servers)
```
1. Content Generator creates draft → `/Pending_Approval/`
2. Human reviews and moves to `/Approved/`
3. Social Media Manager schedules in content calendar
4. At scheduled time:
   - Social Media Manager triggers MCP server
   - MCP server posts to platform
   - Confirmation logged to `/Logs/`
   - File moved to `/Done/`
```

## Performance Metrics

### Engagement Metrics
| Metric | Good Performance | Needs Improvement |
|--------|-----------------|-------------------|
| LinkedIn Engagement Rate | >2% on posts | <1% on posts |
| Twitter Likes (per tweet) | >5% | <2% |
| Instagram Story Views | >5% of followers | <2% |
| Facebook Post Reach | >10% of page likes | <5% |

### Growth Metrics
| Metric | Target | Tracking |
|--------|--------|---------|
| Followers | +10% per month | Weekly check |
| Connections | +25 per month | Weekly check |
| Engagement Rate | Improving trend | Weekly check |
| Profile Views | Increasing | Weekly check |

## Hashtag Strategy

### By Platform

**LinkedIn:**
- Primary: #[Industry] #[Specialization]
- Secondary: #[Trend] #[ValueProp]

**Twitter/X:**
- Primary: #[Topic] #[Niche]
- Secondary: #[Community] #[Chat]

**Instagram:**
- Primary: #[Niche] #[Location] #[Aesthetic]
- Secondary: #[Trending] #[Inspiration]

**Facebook:**
- Primary: #[Topic] #[Local]
- Secondary: #[Community] #[Event]
