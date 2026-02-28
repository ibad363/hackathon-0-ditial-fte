# Approval Manager - Reference

## Key Files

| File | Purpose |
|------|---------|
| `/Pending_Approval/` | Items awaiting human review |
| `/Approved/` | Approved items ready for execution |
| `/Rejected/` | Declined items |
| `/Logs/YYYY-MM-DD.json` | Approval audit trail |
| `Company_Handbook.md` | Approval thresholds and rules |
| `Dashboard.md` | Approval status summary |

## Approval Categories

### By Action Type

| Type | Description | Approval Criteria |
|------|-------------|-------------------|
| **Email** | Sending emails | Known contacts: Auto for routine; Manual for new/sensitive |
| **Payment** | Financial transactions | <$50 recurring: Sometimes; All new payees: Always |
| **Social Media** | Posting content | Scheduled: Sometimes; Replies/DMs: Always |
| **Calendar** | Creating events | Personal: Sometimes; Professional: Always |
| **File Operations** | Moving/deleting files | Within vault: Sometimes; Outside: Always |

### By Priority

| Priority | Response Time | Examples |
|----------|---------------|----------|
| **Critical** | < 4 hours | Urgent payments, client emergencies |
| **High** | < 24 hours | Client emails, important posts |
| **Medium** | < 3 days | Standard emails, scheduled posts |
| **Low** | < 7 days | Reference materials, nice-to-have |

## Approval Metrics

### Key Performance Indicators

| Metric | Target | How to Measure |
|--------|--------|-----------------|
| Response Time | < 24 hours avg | Time from pending → approved/rejected |
| Overdue Approvals | < 5% | Items past SLA |
| Approval Rate | > 80% | Approved vs. rejected ratio |
| Escalations | < 10% | Items needing escalation |

### Dashboard Summary

```markdown
## Approval Status (This Week)

| Metric | Count |
|--------|-------|
| Pending | 3 |
| Approved | 5 |
| Rejected | 1 |
| Avg Response Time | 18 hours |

## Overdue Approvals

| Action | Age | Action |
|--------|-----|--------|
| Payment to Vendor | 5 days | Escalate |
| Email to New Client | 2 days | Send reminder |
```

## Related Skills

- `inbox-processor` - Routes items to Pending_Approval
- `social-media-manager` - Posts approved content
- `weekly-briefing` - Reports on approval metrics
- `planning-agent` - Creates approval workflows within plans

## Scripts

### `scripts/check_pending_approvals.py`

Scan `/Pending_Approval/` for items needing attention or escalation.

### `scripts/generate_approval_summary.py`

Generate daily summary of pending approvals for Dashboard.

### `scripts/escalate_overdue.py`

Send reminders for overdue approval requests.

## Approval Triggers

### Automatic Triggers

Watchers create approval requests when:

1. **Gmail Watcher** detects email to new contact
2. **Xero Watcher** detects invoice needing payment
3. **Calendar Watcher** detects event with attendees
4. **Planning Agent** creates plan with sensitive actions

### Manual Triggers

Human can create approval requests by:
1. Creating file in `/Pending_Approval/`
2. Using approval template from FORMS.md
3. Claude suggesting action that requires approval

## File Naming Conventions

```
EMAIL_[recipient]_[date].md
PAYMENT_[vendor]_[amount]_[date].md
POST_[platform]_[topic]_[date].md
CALENDAR_[event]_[date].md
FILE_[action]_[date].md
```
