# Approval Manager - Forms and Templates

## Approval Request File Template

```markdown
---
type: approval_request
action_type: [email|payment|post|calendar|file_op]
priority: [critical|high|medium|low]
amount: [amount or null]
recipient: [recipient or null]
created: YYYY-MM-DDTHH:MM:SSZ
expires: YYYY-MM-DDTHH:MM:SSZ
status: [pending|approved|rejected|expired]
---

# Approval Request: [Title]

## Action Details
- **Type:** [Email Send, Payment, Social Post, etc.]
- **Amount:** $XXX (if applicable)
- **Recipient:** [Name/Email]
- **Due by:** [Date/Time]

## Context
[Why this action is needed, background information]

## Risk Assessment
- **Financial Risk:** [Yes/No - explain]
- **Reputation Risk:** [Yes/No - explain]
- **Reversibility:** [Easy/Hard/Impossible]

## Information for Review
[Attach or link to relevant information:
- Email draft
- Invoice preview
- Post content
- File details]

## To Approve
Move this file to `/Approved/`

## To Reject
Move this file to `/Rejected/`

---
*Created: YYYY-MM-DD HH:MM*
*Expires: YYYY-MM-DD HH:MM*
```

## Approval Decision Log Template

```markdown
---
approval_id: [unique_id]
action_type: [type]
reviewed_by: [human]
reviewed_at: YYYY-MM-DDTHH:MM:SSZ
decision: [approved|rejected]
reason: [explanation]
confidence: [high|medium|low]
---

## Approval Details
**Original Request:** [Summary]

**Decision:** Approved/Rejected

**Rationale:**
[Human's reasoning for the decision]

**Changes Made:**
[Any modifications before approval]

**Conditions:**
[Any conditions placed on approval]

---
*Logged: YYYY-MM-DD HH:MM*
```

## Escalation Template

```markdown
---
escalation_type: [overdue_approval]
action_type: [type]
original_request: [title]
waiting_since: YYYY-MM-DDTHH:MM:SSZ
urgency: [high|critical]
---

# 🔔 ESCALATION: Approval Required

## What Needs Approval
**Type:** [Email/Payment/etc]
**Title:** [Brief description]
**Amount:** $XXX
**Waiting Since:** [Date]

## Why It's Urgent
- This approval is [X hours/days] overdue
- It's blocking [important outcome]
- [Consequences of delay]

## Action Required
Please review and move to:
- `/Approved/` to approve
- `/Rejected/` to decline

## Original Request
[Link to original approval file or summary]

---
*Escalated: YYYY-MM-DD HH:MM*
```

## Approval Types & Thresholds

### Email Actions
| Scenario | Auto-Approve | Manual Approval |
|----------|-------------|-----------------|
| Reply to known contact | Routine matters | New contacts |
| Routine reply | Yes | Sensitive topics |
| New contact outreach | No | Always |
| Bulk send | No (5+ recipients) | Always |

### Financial Actions
| Amount | Auto-Approve | Manual Approval |
|--------|-------------|-----------------|
| <$50 | Recurring only | Always |
| $50-$100 | No | Always |
| >$100 | No | Always |
| New payee | No | Always |

### Social Media Actions
| Platform | Auto-Approve | Manual Approval |
|----------|-------------|-----------------|
| Scheduled post | Yes | Replies/DMs |
| Reply/DM | No | Always |
| New connection | No | Always |

## Approval Workflow States

```
Pending → [Human Review] → Approved → [Action Executed] → Done
   ↓
Rejected → [Action Cancelled] → Archived

Pending → [Expired] → Escalated → [Urgent Review]
```

## Approval SLA (Service Level Agreement)

| Priority | Response Time | Escalation |
|----------|---------------|------------|
| Critical | 4 hours | After 4 hours |
| High | 24 hours | After 1 day |
| Medium | 3 days | After 3 days |
| Low | 7 days | After 7 days |

## Dashboard Integration

Update Dashboard.md with:

```markdown
## Pending Approvals

| Action | Priority | Waiting Since | Days Pending |
|--------|----------|---------------|---------------|
| Email to Client A | High | 2026-01-08 | 2 days |
| Payment to Vendor B | Critical | 2026-01-05 | 5 days |
| LinkedIn Post | Medium | 2026-01-10 | 1 day |

## Approval Status
- Pending: 3
- Approved this week: 5
- Rejected this week: 1
- Average response time: 18 hours
```

## Common Approval Patterns

### Email Approval Pattern
```
1. Draft created in Pending_Approval/
2. Human reviews draft
3. Edits made if needed
4. Moved to Approved/
5. Email MCP server sends email
6. File moved to Done/
```

### Payment Approval Pattern
```
1. Invoice created in Pending_Approval/
2. Human reviews:
   - Amount
   - Vendor
   - Due date
   - Budget availability
3. Moved to Approved/
4. Payment MCP executes
5. Receipt filed
6. File moved to Done/
```

### Social Media Approval Pattern
```
1. Post created in Pending_Approval/
2. Human reviews:
   - Content quality
   - Brand alignment
   - Timing
3. Moved to Approved/
4. Social Media MCP posts
5. Engagement tracking started
6. File moved to Done/
```
