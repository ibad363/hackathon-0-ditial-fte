# Social Media Manager - Examples

## Example 1: Scheduling Approved LinkedIn Post

**Input:** Content Generator created LinkedIn post, human approved

**File:** `/Approved/POST_linkedin_ai_tips_20260110.md`

**Processing:**

```bash
python .claude/skills/social-media-manager/scripts/generate_content_calendar.py --vault .
```

**Output:**

```markdown
# Content Calendar: Week of January 13

## LinkedIn

| Day | Topic | Status | Scheduled Time |
|----|-------|--------|-----------------|
| Mon | "5 AI tools that save 10+ hours/week" | Scheduled | 2026-01-13 8:00 AM |
| Wed | "How I failed at setting up AI assistant (lessons learned)" | Scheduled | 2026-01-15 12:00 PM |
| Fri | "The future of AI in small business" | Scheduled | 2026-01-17 5:00 PM |
```

**Posting:**

1. Social Media Manager monitors `/Approved/`
2. Detects approved LinkedIn post
3. Posts via LinkedIn MCP server at scheduled time
4. Logs activity to `/Logs/2026-01-13.json`
5. Moves file to `/Social_Media/`

---

## Example 2: Weekly Performance Report

**Input:** Weekly briefing generation

**Processing:**

```bash
python .claude/skills/social-media-manager/scripts/analyze_performance.py --vault . --week 2026-02
```

**Output:**

```markdown
# Social Media Performance: Week of February 5-9

## Overview

| Platform | Posts | Impressions | Engagement | Engagement Rate |
|----------|-------|-------------|-------------|----------------|
| LinkedIn | 3 | 4,500 | 125 | 2.8% ✓ |
| Twitter | 15 | 2,100 | 95 | 4.5% ✓ |
| Instagram | 3 stories, 1 post | 2,800 | 56 | 2% ✓ |
| Facebook | 4 | 8,200 | 42 | 0.5% |

## Top Performing Posts

### LinkedIn
**Post:** "5 AI tools that save 10+ hours/week"
- Impressions: 2,100
- Engagement: 89 (42 likes, 47 comments)
- Shares: 12
- **Engagement Rate:** 4.2% (excellent!)

### Twitter/X
**Tweet:** Thread on AI prompt engineering
- Impressions: 850
- Engagement: 38 (18 likes, 8 retweets, 12 replies)
- **Engagement Rate:** 4.5% (very good)

## Platform Growth

### LinkedIn
| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Followers | 1,250 | 1,220 | +30 (+2.5%) |

### Twitter/X
| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Followers | 845 | 820 | +25 (+3%) |

### Instagram
| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Followers | 620 | 595 | +25 (+4%) |

## Insights

### What Worked
- LinkedIn posts with "How-to" content got 2x engagement
- Twitter threads performed well (4.5% rate)
- Instagram Stories posted on weekends got 2x views

### What Didn't Work
- Facebook posts without images got low engagement
- LinkedIn posts on Friday evening got less reach
- Generic content performed worse than specific

### Recommendations
- Create more "How-to" content for LinkedIn
- Continue Twitter threads that worked well
- Always include images in Facebook posts
- Avoid Friday evening LinkedIn posts

## Action Items
- [ ] Draft next week's content calendar
- [] Create more Twitter thread ideas
- [] Test different posting times on Instagram
- [] Review Facebook posting strategy

## Performance Summary
**Total Posts:** 25
**Total Impressions:** 17,500
**Total Engagement:** 318
**Average Engagement Rate:** 2.7%
**Follower Growth:** +80 across all platforms
```

---

## Example 3: Content Calendar Generation

**Input:**

```
Generate a social media content calendar for the week of January 13-17
Focus: Building personal brand as AI consultant
Platforms: LinkedIn, Twitter/X
```

**Processing:**

```bash
python .claude/skills/social-media-manager/scripts/generate_content_calendar.py --vault . --week 2026-01-13 --platforms LinkedIn,Twitter
```

**Output:**

```markdown
# Content Calendar: Week of January 13-17

## LinkedIn

| Day | Topic | Type | Status | Scheduled Time |
|----|-------|------|--------|----------------|
| Mon | "5 AI tools that save 10+ hours/week" | Educational | Draft | 2026-01-13 8:00 AM |
| Wed | "How I failed at setting up AI assistant" | Personal story | Draft | 2026-01-15 12:00 PM |
| Fri | "The future of AI in small business" | Industry insight | Draft | 2026-01-17 5:00 PM |

## Twitter/X

| Day | Topic | Type | Status | Scheduled Time |
|----|-------|------|--------|-----------------|
| Mon | "Top 5 automation mistakes to avoid" | Educational | Draft | 2026-01-13 12:00 PM |
| Tue | "My favorite AI tool for coding" | Reply to tweet | Draft | 2026-01-14 2:00 PM |
| Wed | "Common AI misconceptions" | Thread | Draft | 2026-01-15 3:00 PM |
| Thu | "Quick tip: Better prompting" | Tweet | Draft | 202---- |

## Themes
- **Monday:** Productivity tips
- **Wednesday:** Personal experience
- **Friday:** Industry predictions

## Goals
- **Engagement:** 2%+ on LinkedIn posts
- **Growth:** +20 new LinkedIn connections
- **Visibility:** +50 Twitter followers
```

---

## Example 4: Post-Performance Analysis

**Input:** Weekly briefing includes social media metrics

**Processing:**

```bash
python .claudeskills/social-media-manager/scripts/optimize_schedule.py --vault . --platform LinkedIn --month 2026-01
```

**Output:**

```markdown
# LinkedIn Performance Analysis: January 2026

## Posting Schedule Results

| Time Slot | Avg Engagement Rate | Optimal For |
|------------|----------------------|-------------|
| 8-10 AM | 3.2% | Educational content |
| 12-2 PM | 1.8% | Behind-the-scenes |
| 5-6 PM | 2.7% | Personal stories |

### Recommendations

**Best Day:** Tuesday (3.5% avg engagement)
**Worst Day:** Friday (1.2% avg engagement)
**Best Time:** 8:00 AM (3.8% engagement)

## Content Performance by Type

| Content Type | Avg Engagement Rate | Best Day | Best Time |
|---------------|---------------------|----------|-----------|
| How-to | 4.2% | Tuesday | 8-10 AM |
| Personal story | 3.5% | Wednesday | 12-2 PM |
| Industry insight | 2.9% | Thursday | 5-6 PM |
| Promotional | 1.8% | Friday | 12-2 PM |

## Optimization Suggestions

### High Impact
1. **Shift promotional posts** to Tuesday 8-10 AM (4.2% vs 1.8%)
2. **Stop posting on Friday** (1.2% - worst day)
3. **Create more how-to content** (4.2% best performer)

### Medium Impact
1. **Post at 8:00 AM** instead of 5:00 PM (3.8% vs 2.7%)
2. **Use numbers in headlines** (+20% engagement)
3. **Include questions in posts** (+40% comments)

## A/B Test Results

### Test: Including questions in posts
| With Questions | Without Questions |
|----------------|---------------------|
| Comments per post: 8 | Comments per post: 3 |

### Test: Number-focused headlines
| Number in Headline | Avg Engagement Rate |
|-------------------|----------------------|
| 5 AI tools... | 4.2% |
| Tips for... | 2.1% |
| Things I learned... | 3.5% |

## Next Steps
Based on this analysis, the content calendar for next month will:
1. Focus on how-to content (best performer at 4.2% engagement)
2. Move promotional posts to Tuesday mornings
3. Pause Friday posting (low engagement)
4. Always include questions in posts
5. Test video content (not tested yet)

```

---

## Example 5: Tracking Engagement

**Input:** Daily check of social media metrics

**Processing:**

```bash
python .claude/skills/social-media-manager/scripts/track_engagement.py --vault . --platform LinkedIn
```

**Output:**

```markdown
# LinkedIn Engagement Report: January 10, 2026

## Overview

| Metric | Value | vs Yesterday | vs Last Week |
|--------|-----|-------------|--------------|
| Impressions | 450 | +50 (+12%) | +350 (+350%) |
| Engagement | 12 | +3 (+33%) | +8 (+200%) |
| Engagement Rate | 2.7% | +0.3% | +1.5% |

## Top Performing Post

**Post:** "5 AI tools that save 10+ hours/week"
- **Impressions:** 1,800
- **Engagement:** 89
- **Engagement Rate:** 4.9%
- **Time Since Posting:** 24 hours
- **Performance:** Excellent (benchmark is 2%)

## Comments Breakdown

| Comment Type | Count | % of Total |
|-------------|-------|-------------|
| Questions | 6 | 50% |
| Praise | 3 | 25% |
| Opinions | 3 | 25% |

## Notifications
| Type | Count | Action Required |
|------|-------|------------------|
| Questions to answer | 6 | Reply within 24 hours |
| Connection requests | 3 | Review profiles, accept connections |

## Recommendations
1. **Reply to:** 6 comments awaiting response
2. **Engage with:** 3 people who praised your post
3. **Share:** Share to 2-3 relevant people via DM
4. **Create follow-up content:** Deep dive into top-performing topic
```

---

## Example 6: Approval Workflow Integration

**Scenario:** Content Generator creates post → Approval Manager reviews → Social Media Manager schedules

**Step 1:** Content Generator creates draft

**File:** `/Pending_Approval/POST_linkedin_tips_20260110.md`

**Step 2:** Approval Manager reviews and escalates if needed

**Status:** Approved → Moved to `/Approved/`

**Step 3:** Social Media Manager schedules the post

```markdown
---
platform: LinkedIn
content_id: POST_linkedin_tips_20260110
scheduled_date: 2026-01-13
scheduled_time: 08:00
timezone: US/Eastern
status: scheduled
---

# Post: 5 AI tools that save 10+ hours/week

## Content Preview
[Content preview...]

## Scheduled
**Date:** Monday, January 13, 2026
**Time:** 8:00 AM EST
**Platform:** LinkedIn
```

**Step 4:** Post published via LinkedIn MCP server

**File:** `/Social_Media/POST_linkedin_tips_20260110_published.md`

**Tracking:** Engagement tracked and logged to `Dashboard.md`

---

## Example Commands for Claude Code

```
"Generate a content calendar for next week for LinkedIn and Twitter"

"What were the top 3 performing posts last month and why?"

"Schedule this LinkedIn post for Tuesday at 8am and add to content calendar"

"Generate a monthly social media performance report for January"

"Analyze the engagement on Twitter posts containing "#AI" and provide insights"

"What's the best time to post on LinkedIn based on historical data?"

"Track engagement on all posts from the last 7 days and summarize insights"
```
