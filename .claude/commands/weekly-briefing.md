# Weekly Briefing Command

You are an AI Employee preparing the Monday morning CEO briefing. Follow this precisely:

## Step 1: Gather Data
Read these files to build the briefing:
- `Business_Goals.md` — Current company objectives
- `Dashboard.md.md` — Status and metrics
- All files in `/Done/` — Completed tasks from the past week
- All files in `/Plans/` — Active and pending plans
- All files in `/Needs_Action/` — Unprocessed items
- All files in `/Pending_Approval/` — Items waiting for CEO decision
- `/Logs/log.md` — Activity log for the week

## Step 2: Create Briefing
Save to `/Plans/Briefing_[YYYY-MM-DD].md` with this format:

```markdown
---
type: weekly_briefing
date: [Monday's date]
created: [timestamp]
status: delivered
---

# Weekly Briefing — [Date]

## Executive Summary
[2-3 sentences: Overall status, biggest win, biggest concern]

## Completed This Week
- [List all items moved to /Done with dates]
- Total tasks completed: [N]

## In Progress
- [List active plans with status]

## Pending Your Approval
- [List items in /Pending_Approval that need CEO decision]
- **Action needed on [N] items**

## Upcoming This Week
- [Scheduled tasks, deadlines, follow-ups]

## Bottlenecks & Risks
- [Anything stuck, overdue, or at risk]
- [Resource constraints or blockers]

## Key Metrics
- Tasks completed: [N]
- Tasks pending: [N]
- Approval queue: [N]
- Average response time: [if trackable]

## Recommendations
- [1-3 suggestions for the CEO's attention]
```

## Step 3: Update Dashboard
Replace the Executive Summary section in Dashboard.md.md with fresh data.

## Step 4: Log It
Append to `/Logs/log.md`:
```
- [DATE] Weekly briefing delivered: Briefing_[DATE].md
```
