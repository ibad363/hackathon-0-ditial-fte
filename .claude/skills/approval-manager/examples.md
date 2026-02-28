# Approval Manager - Examples

## Example 1: Processing an Email Approval Request

**Input:** Gmail Watcher detects email to new contact, creates approval request

**File Created:** `/Pending_Approval/EMAIL_new_client_20260110.md`

```markdown
---
type: approval_request
action_type: email
priority: high
amount: null
recipient: john@prospect-company.com
created: 2026-01-10T14:30:00Z
expires: 2026-01-12T14:30:00Z
status: pending
---

# Approval Request: Send Cold Outreach Email

## Action Details
- **Type:** Email Send
- **To:** john@prospect-company.com
- **Subject:** Web Development Services
- **Due by:** 2026-01-11 5:00 PM

## Context
New prospect from LinkedIn conversation. Expressed interest in web development services for their e-commerce site.

## Email Draft

---

**Subject:** Your e-commerce project

Hi John,

Great connecting with you on LinkedIn! I enjoyed our conversation about your e-commerce platform plans.

I'd love to learn more about:
- Your current challenges
- Timeline for the project
- Budget range

Would you be available for a 15-minute call this week?

Best regards,
[Your Name]

---

## Risk Assessment
- **Financial Risk:** No - Zero cost
- **Reputation Risk:** Low - Professional outreach
- **Reversibility:** Easy - One email

## Information for Review
- Prospect: John Smith, CEO at Prospect Company
- Source: LinkedIn conversation
- Previous interactions: 1 (LinkedIn message)

## To Approve
Move this file to `/Approved/`

## To Reject
Move this file to `/Rejected/`
```

**Processing:**

1. Approval Manager monitors `/Pending_Approval/`
2. Detects new approval request
3. Tracks age of request
4. After 24 hours (not approved), sends reminder
5. Human reviews draft
6. Human moves to `/Approved/`
7. Email MCP server sends email
8. File archived to `/Done/`

---

## Example 2: Payment Approval with Escalation

**Input:** Xero Watcher detects invoice >$100 (requires approval)

**File Created:** `/Pending_Approval/PAYMENT_vendor_x_20260110.md`

```markdown
---
type: approval_request
action_type: payment
priority: critical
amount: 250.00
recipient: Vendor X (Acme Corp)
created: 2026-01-10T09:00:00Z
expires: 2026-01-10T17:00:00Z
status: pending
---

# Approval Request: Pay Vendor X Invoice

## Action Details
- **Type:** Payment
- **Amount:** $250.00
- **To:** Vendor X (Acme Corp)
- **Invoice:** #INV-2025-123
- **Due by:** 2026-01-10 5:00 PM

## Context
Monthly subscription for software tools. Vendor X has been reliable supplier for 6 months.

## Invoice Details
- **Description:** Software license - January 2026
- **Amount Due:** $250.00
- **Payment Terms:** Net 15
- **Due Date:** January 25, 2026

## Risk Assessment
- **Financial Risk:** Medium - $250
- **Reputation Risk:** None if paid on time
- **Reversibility:** Difficult - Hard to recall payment

## Budget Check
- **Category:** Software/Tools
- **Monthly Budget:** $400
- **Spent So Far:** $150
- **Remaining:** $250 ✓

## Information for Review
- Vendor: Acme Corp
- **Service:** Cloud productivity suite
- **Duration:** January 2026
- **Account Code:** EXP-001

## To Approve
Move this file to `/Approved/`

## To Reject
Move this file to `/Rejected/` and provide reason

---
*Created: 2026-01-10 09:00*
```

**Escalation (after 4 hours):**

```markdown
---
escalation_type: overdue_approval
action_type: payment
original_request: PAYMENT_vendor_x_20260110.md
waiting_since: 2026-01-10T09:00:00Z
urgency: critical
---

# 🔔 ESCALATION: Urgent Approval Required

## What Needs Approval
**Type:** Payment
**Title:** $250 payment to Vendor X
**Amount:** $250.00
**Waiting Since:** 4 hours (expired at 5:00 PM today)

## Why It's Urgent
- Payment is **4 hours overdue** (was due by 5:00 PM)
- Late payment may incur late fees
- Service disruption risk

## Consequence
If not paid today:
- ⚠️ Late fee: $25 (10%)
- ⚠️ Service interruption possible
- ⚠️ Good standing at risk

## Action Required
**REVIEW IMMEDIATELY**

Move to `/Approved/` to authorize payment or `/Rejected/` to cancel.

## Original Request
File: `PAYMENT_vendor_x_20260110.md`
```

---

## Example 3: Social Media Post Approval

**Input:** Content Generator creates LinkedIn post

**File Created:** `/Pending_Approval/POST_linkedin_ai_tips_20260110.md`

```markdown
---
type: approval_request
action_type: social_post
platform: LinkedIn
priority: medium
amount: null
created: 2026-01-10T16:00:00Z
expires: 2026-01-12T16:00:00Z
status: pending
---

# Approval Request: LinkedIn Post - AI Productivity Tips

## Content Preview

**Platform:** LinkedIn
**Type:** Educational
**Character Count:** 1,245

---

Post Preview:

Most people use AI wrong.

They ask AI to "do everything" and get mediocre results.

Try this instead:

Be radically specific about the task.

❌ "Write a marketing email"
✅ "Write a 50-word email to marketing managers at digital agencies, promoting our new social scheduling tool"

The constraint is the quality control.

#AI #Productivity #TechTips

---

## Review Checklist
- [ ] On-brand tone and voice
- [ ] Accurate information
- [ ] Appropriate for target audience
- [ ] No controversial statements
- [ ] Links work correctly
- [ ] Hashtags are relevant
- [ ] Call to action is clear

## Posting Schedule
- **Target Date:** 2026-01-11 at 8:00 AM
- **Reasoning:** Tuesday morning optimal for engagement
- **Time Zone:** EST

## To Approve
1. Review content above
2. Make edits if needed
3. Move this file to `/Approved/`
4. LinkedIn MCP will post automatically

## To Reject
Move this file to `/Rejected/` and provide feedback
```

**Processing:**

Human reviews and makes minor edits:

```markdown
## Changes Made:
- Added specific example in second paragraph
- Changed one hashtag from #TechTips to #SaaS
- Added "Follow for more" to CTA
```

Moves to `/Approved/`

LinkedIn MCP server posts at scheduled time.

---

## Example 4: Dashboard Approval Summary

**Generated by:** `scripts/generate_approval_summary.py`

**Output:**

```markdown
# Approval Summary - Week of January 6

## Overview

| Metric | Value |
|--------|-------|
| Pending Approvals | 2 |
| Approved This Week | 8 |
| Rejected This Week | 1 |
| Average Response Time | 18 hours |
| Overdue (>24 hrs) | 0 |

## Pending Approvals

| Action | Priority | Age | Action Needed |
|--------|----------|-----|---------------|
| LinkedIn Post | Medium | 4 hours | Review content |
| Payment Invoice | Critical | 2 days | Approve immediately |

## Approval Rate by Type

| Type | Approved | Rejected | Pending |
|------|---------|---------|--------|
| Email | 4 | 0 | 1 |
| Payment | 2 | 0 | 1 |
| Social Post | 2 | 1 | 0 |

## Response Time Analysis

| Day | Avg Response Time |
|-----|-----------------|
| Mon | 12 hours |
| Tue | 8 hours |
| Wed | 24 hours |
| Thu | 16 hours |
| Fri | 6 hours |

**Weekly Average:** 18 hours

## Recommendations

✅ **Good:** Response times improving
⚠️ **Watch:** 1 payment approval is 2 days old
💡 **Tip:** Set up approval reminders for time-sensitive actions
```

---

## Example 5: Rejection with Feedback

**Scenario:** Human rejects approval request with feedback

**Original Request:** `EMAIL_cold_outreach_20260110.md`

**Decision:** Moved to `/Rejected/`

**Rejection Note:**

```markdown
---
rejected: 2026-01-10T15:00:00Z
rejected_by: [Human]
reason: Draft needs refinement
---

## Rejection Feedback

The email draft needs changes before sending:

### Issues:
- ❌ Too long - shorten to under 150 words
- ❌ Opening doesn't address specific pain point
- ❌ Missing clear call-to-action

### Suggested Improvements:
1. Start with a specific observation about their recent work
2. Focus on one clear value proposition
3. Make the CTA lower-friction (15-min call instead of generic "let's talk")

## Revised Draft Needed

Please revise and create new approval request.
```

**Processing:**

1. Approval Manager detects rejection
2. Logs rejection to `/Logs/2026-01-10.json`
3. Creates new task in `/Needs_Action/`: "Revise email draft based on feedback"
4. Content Generator creates new draft
5. New approval request created
6. Cycle repeats until approved

---

## Example Commands for Claude Code

```
"Review all pending approvals and summarize what needs attention"

"Check if any approvals are overdue and escalate them"

"Generate an approval summary report for this week"

"Create an approval request for sending a thank you email to Client Z for their recent payment"

"What's the average response time for approvals this month?"

"Which pending approvals are critical and need immediate attention?"
```
