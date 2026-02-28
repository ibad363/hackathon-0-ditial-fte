---
name: approval-manager
description: Monitor, track, and manage the human-in-the-loop approval workflow for sensitive actions, ensuring proper oversight and audit trails.
license: Apache-2.0
---

# Approval Manager

Monitor, track, and manage the human-in-the-loop approval workflow for sensitive actions, ensuring proper oversight and audit trails.

## Purpose

The Approval Manager skill **monitors** approval queues, **tracks** pending items, **escalates** overdue approvals, **maintains** audit logs, and **ensures** proper human oversight for all sensitive actions. This skill **orchestrates** the decision flow from detection to execution while **maintaining** security and compliance.

This is a **critical security component** of the AI Employee system - no sensitive action (email sending, social posting, payments) can execute without human approval.

## Design Philosophy

### Core Principles

1. **Smart Auto-Approval**: AI-powered approval decisions for safe actions
2. **Human-in-the-Loop**: Sensitive actions always require human review
3. **Traceability**: Every approval decision is logged with timestamp
4. **Time-Aware**: Escalate overdue items automatically
5. **Risk-Based**: Approval requirements match action risk level
6. **Transparent**: Clear status tracking for all items
7. **Audit-First**: Complete audit trail for compliance

### Architecture

```
External System (Gmail/LinkedIn/Xero/etc)
      ↓
Watcher Detects Event
      ↓
Creates Action File in Needs_Action/
      ↓
AI Auto-Approver Analyzes (runs every 2 min)
      ↓
┌─────────────────────────────────────────┐
│ Claude 3 Haiku AI Decision:             │
│ - approve → Safe actions (file ops,     │
│              known contacts, Slack/WhatsApp) │
│ - reject → Dangerous (scams, phishing)  │
│ - manual → Needs human review (social   │
│             media, payments, new contacts) │
└─────────────────────────────────────────┘
      ↓
┌──────────────┬──────────────┬──────────────┐
│ Approved/    │ Rejected/    │ Pending_     │
│ (auto)       │ (auto)       │ Approval/    │
│              │              │ (manual)     │
└──────────────┴──────────────┴──────────────┘
      ↓              ↓              ↓
Approval Monitor     Discard       Human Reviews
Executes Action                      ↓
                              Moves to Approved/
                              ↓
                              Approval Monitor
                              Detects & Executes
                              ↓
Logs/ YYYY-MM-DD.json
                              ↓
Moves to Done/ (or Rejected/)
```

### Modularity

- **Separation of Concerns**: Detection → AI Approval → Human Review → Execution → Logging
- **Risk-Based Categories**: High/Medium/Low priority actions
- **Time-Based Escalation**: Auto-escalate overdue approvals
- **Integration Points**: Works with all watchers and action scripts
- **AI-First Approach**: Smart auto-approval reduces manual review burden

### AI Auto-Approver

The AI Auto-Approver (`scripts/auto_approver.py`) uses **Claude 3 Haiku** to make intelligent approval decisions, dramatically reducing the manual review burden while maintaining security.

**How It Works:**

1. **Scans** `Needs_Action/` and `Inbox/` every 2 minutes
2. **Reads** each action file's content and metadata
3. **Loads** Company_Handbook.md for context and rules
4. **Calls** Claude 3 Haiku API with:
   - Action type and service
   - Content (first 2000 chars)
   - Company rules (first 3000 chars)
   - Request for single-word decision: approve/reject/manual

5. **Claude decides:**
   - **approve** → Safe to auto-approve (file ops, known contacts, Slack/WhatsApp)
   - **reject** → Dangerous (scams, phishing, payment requests)
   - **manual** → Needs human review (social media, payments, new contacts)

6. **Files moved to:**
   - `Approved/` → Auto-approved actions (executed by monitors)
   - `Rejected/` → Rejected as unsafe
   - `Pending_Approval/` → Requires human review

**AI Decision Examples:**

```
[INPUT] Slack message from team: "Meeting at 3pm"
[AI] approve → Moves to Approved/ → Auto-executed

[INPUT] Email: "URGENT: Send $5000 wire transfer now!!!"
[AI] reject → Moves to Rejected/ → Blocked

[INPUT] LinkedIn post: "Check out our new product"
[AI] manual → Moves to Pending_Approval/ → Human reviews

[INPUT] File drop in Inbox/
[AI] approve → Moves to Approved/ → Auto-processed

[INPUT] Email from known contact "mom@gmail.com"
[AI] manual → Moves to Pending_Approval/ → Human reviews (not in known contacts)
```

**Safety Features:**

- **Fallback Rules**: If Claude API unavailable, uses rule-based fallback
- **Conservative Default**: When uncertain, defaults to "manual" review
- **Audit Trail**: All AI decisions logged with "approved_by": "AI (Claude)"
- **Context Awareness**: Reads Company_Handbook.md for business-specific rules

**Configuration:**

```bash
# Run once (for testing)
python scripts/auto_approver.py --vault AI_Employee_Vault --once

# Run continuously (PM2 manages this)
pm2 start auto-approver

# Set API key
export ANTHROPIC_API_KEY="your-api-key"
pm2 restart auto-approver --update-env
```

**Cost & Performance:**

- **Model**: Claude 3 Haiku (fastest, cheapest)
- **Cost**: ~$0.00025 per decision (1M tokens/$0.25)
- **Speed**: ~1-2 seconds per decision
- **Frequency**: Every 2 minutes
- **Monthly Cost**: ~$5-10 for moderate usage

**Monitoring:**

```bash
# Check AI approval logs
pm2 logs auto-approver --lines 50

# View recent decisions
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.component == "auto_approver")'

# Check approval stats
ls AI_Employee_Vault/Approved/ | wc -l  # Auto-approved
ls AI_Employee_Vault/Pending_Approval/ | wc -l  # Manual review
ls AI_Employee_Vault/Rejected/ | wc -l  # Rejected
```

## Workflow

### 1. Detection Phase

**Watcher creates approval request**:
```markdown
---
type: approval_request
action: send_email
priority: high
created: 2026-01-11T17:00:00Z
expires: 2026-01-12T17:00:00Z
status: pending_approval
---

# Approval Required: Send Email to Client

## Details
- **To:** client@example.com
- **Subject:** Invoice #1234 - $1,500.00
- **Body:** [Draft email content]

## Risk Assessment
- **Risk Level:** Medium
- **Reversible:** Yes (can send follow-up correction)
- **Requires Approval:** Yes (external communication)

## To Approve
Move this file to `/Approved/` folder.

## To Reject
Move this file to `/Rejected/` folder.

---
*Generated by Gmail Watcher*
```

### 2. Monitoring Phase

**Approval Manager monitors** `/Pending_Approval/`:
- Tracks new approval requests
- Assesses priority and risk level
- Categorizes by action type
- Monitors age of pending approvals

**Priority Assessment**:
- **High**: Payments >$100, new payees, bulk emails
- **Medium**: Routine emails, social posts, calendar changes
- **Low**: Internal notifications, file organization

### 3. Escalation Phase

**Time-based escalation** (per Company_Handbook rules):
- **0-2 hours old**: Normal priority
- **2-6 hours old**: Medium priority (send reminder)
- **6-12 hours old**: High priority (urgent notification)
- **12+ hours old**: Critical (escalate to human)

**Escalation Actions**:
- Create reminder in `/Needs_Action/`
- Send notification (if configured)
- Flag in Dashboard
- Alert via Slack/WhatsApp

### 4. Decision Phase

**Human reviews and decides**:

**Approve**: Move to `/Approved/`
```bash
mv "Pending_Approval/EMAIL_client_20260111.md" "Approved/"
```

**Reject**: Move to `/Rejected/`
```bash
mv "Pending_Approval/EMAIL_client_20260111.md" "Rejected/"
```

**Modify**: Edit file, then move to `/Approved/`
```bash
# Edit file to change content
vim "Pending_Approval/EMAIL_client_20260111.md"
mv "Pending_Approval/EMAIL_client_20260111.md" "Approved/"
```

### 5. Execution Phase

**Approval monitor detects** file in `/Approved/`:
- Reads approval request metadata
- Validates approval is recent (not expired)
- Executes action via appropriate script
- Logs result to audit log
- Moves file to `/Done/` (success) or keeps in `/Approved/` (failure)

### 6. Audit Phase

**All actions logged** to `Logs/YYYY-MM-DD.json`:
```json
{
  "timestamp": "2026-01-11T17:30:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "parameters": {
    "subject": "Invoice #1234",
    "approval_file": "EMAIL_client_20260111.md"
  },
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success"
}
```

## Approval Categories

### Email Actions

**AI Auto-Approves** (low risk):
- Replies to known contacts (in whitelist)
- Internal team communications
- Status updates from trusted sources

**AI Requires Manual Review** (medium/high risk):
- Unknown senders
- Bulk sends (>5 recipients)
- External communications
- Attachments
- Financial keywords (invoice, payment, urgent)

### Social Media Actions

**AI Requires Manual Review** (always):
- **All** social media posts (LinkedIn, Twitter, Instagram, Facebook)
- Replies/DMs
- Scheduled posts

**Rationale**: Public-facing content always needs human review, regardless of pre-scheduling.

### Payment Actions

**AI Auto-Rejects** (always):
- Payment requests
- Invoice processing
- Wire transfer requests
- "Urgent" financial requests

**Rationale**: Payments are too high-risk for AI approval.

### Calendar Actions

**AI Auto-Approves** (low risk):
- Personal calendar updates
- Tentative holds
- Meetings without attendees

**AI Requires Manual Review** (medium/high risk):
- Meetings with external attendees
- Recurring meeting creation
- Calendar invites to >5 people

### File Operations

**AI Auto-Approves** (safe operations):
- File drops in Inbox/
- File organization
- Task categorization
- Meeting preparation

**Rationale**: File operations within the vault are inherently safe.

### Messaging

**AI Auto-Approves** (notifications):
- Slack messages
- WhatsApp messages
- System notifications

**Rationale**: These are read-only notifications, not actions.

## Risk Assessment Matrix

| Action | Reversible | Impact | AI Decision | Review Required |
|--------|-----------|--------|-------------|----------------|
| Email to known contact | Yes | Low | Auto-approve | No |
| Email to unknown sender | Yes | Medium | Manual review | Yes |
| Payment request | Maybe | High | Auto-reject | N/A (blocked) |
| Social media post | Delete | Medium | Manual review | Yes (always) |
| Calendar (no attendees) | Cancel | Low | Auto-approve | No |
| Calendar (with attendees) | Cancel | Medium | Manual review | Yes |
| File drop in Inbox/ | Yes | Low | Auto-approve | No |
| Slack/WhatsApp message | Yes | Low | Auto-approve | No |
| Scam/Phishing attempt | N/A | High | Auto-reject | N/A (blocked) |

## Integration Points

### Input Sources

- **All Watchers**: Create approval requests
- **Ralph Wiggum**: Creates approval for multi-step tasks
- **Content Generator**: Creates approval for generated content
- **Scripts**: Manual approval request creation

### Output Destinations

- **Approved/**: Ready for execution
- **Rejected/**: Declined actions
- **Done/**: Completed actions
- **Logs/**: Audit trail

### Related Skills

- **All Manager Skills**: Create approval requests
- **All Approval Monitors**: Execute approved actions
- **Weekly Briefing**: Include approval metrics in reports
- **Dashboard**: Show approval queue status

## Security Considerations

### No Bypass Possible

- All approval monitors check `/Approved/` folder only
- No direct execution without file movement
- No environment variable bypass
- No command-line override

### Expiration Handling

- Approval requests expire after 24 hours (configurable)
- Expired requests moved to `/Rejected/` with reason
- Fresh approval required for expired requests

### Audit Trail

- All approvals logged with timestamp
- Human approver tracked (file system user)
- Approval reason preserved in file
- Decision audit trail maintained

## Troubleshooting

### Approval Not Executing

**Problem**: File in `/Approved/` but action not executed

**Solution**:
1. Check approval monitor is running: `pm2 status`
2. Check monitor logs: `pm2 logs email-approval-monitor`
3. Verify file format (YAML frontmatter required)
4. Check for expired approval (created >24 hours ago)

### File Not Moving to Done

**Problem**: Action executed but file stays in `/Approved/`

**Solution**:
1. Check Logs/YYYY-MM-DD.json for execution result
2. Look for error in monitor logs
3. Verify action script completed successfully
4. Manually move to `/Done/` if action succeeded

### Escalation Not Working

**Problem**: Overdue approvals not escalating

**Solution**:
1. Check Company_Handbook.md escalation rules
2. Verify approval monitor checking age
3. Check notification system (Slack/Email)
4. Manually flag in Dashboard if needed

## Usage

```bash
# Check pending approvals
ls AI_Employee_Vault/Pending_Approval/

# Approve an action
mv "Pending_Approval/EMAIL_*.md" "Approved/"

# Reject an action
mv "Pending_Approval/EMAIL_*.md" "Rejected/"

# Check approval status
pm2 status | grep approval

# View approval logs
pm2 logs email-approval-monitor --lines 50

# Check audit log
cat "AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json" | jq '.[] | select(.action_type == "email_send")'
```

## Future Enhancements

- [ ] Web-based approval UI
- [ ] Mobile approval app
- [ ] Multi-level approval chains
- [ ] Approval delegation
- [ ] Notification system (Slack/Email/SMS)
- [ ] Approval analytics dashboard
- [ ] Bulk approval actions
- [ ] Approval comments/feedback
- [ ] Approval withdrawal

## Related Documentation

- **Hackathon0.md**: Overall project architecture
- **docs/ARCHITECTURE.md**: System architecture details
- **CLAUDE.md**: Project instructions and usage
- **AI_Employee_Vault/Company_Handbook.md**: Approval rules and escalation

---

*Last Updated: 2026-01-17*
*Approval Manager Skill v1.2 - AI-Powered Auto-Approval*
*Now with Claude 3 Haiku integration for intelligent approval decisions*
