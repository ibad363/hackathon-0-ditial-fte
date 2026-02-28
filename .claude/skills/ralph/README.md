# Ralph Wiggum - AI Employee Implementation

**Status:** ✅ **Implemented and Ready**
**Last Updated:** 2026-01-12
**Version:** 1.0 for AI Employee

---

## 🎯 What is Ralph?

Ralph Wiggum is an **autonomous agent loop** that:
- Executes multi-step business tasks automatically
- Runs iterations until all tasks are complete
- Maintains human oversight (approval required for external actions)
- Persists memory via files and vault

This is the **final 5%** to reach **100% Gold Tier**!

---

## 📁 Files

### Core Ralph Files

| File | Purpose |
|------|---------|
| `ralph-claude.sh` | Main autonomous loop script |
| `prompt-ai-employee.md` | Instructions for Claude Code |
| `prd.json` | Task list (YOUR tasks go here) |
| `progress.txt` | Learnings log (auto-generated) |
| `prd.json.example` | Example task format (reference) |

### Helper Scripts

| Script | Purpose |
|--------|---------|
| `scripts/start-ralph.sh` | Start Ralph loop |
| `scripts/check-ralph-status.sh` | Check Ralph progress |

---

## 🚀 Quick Start

### 1. Create Your Task List

Edit `ralph/prd.json` with your tasks:

```json
{
  "project": "AI Employee",
  "branchName": "my-task-name",
  "description": "Brief description of what you're accomplishing",
  "userStories": [
    {
      "id": "TASK-001",
      "title": "Send email to client",
      "description": "Send follow-up email to client about invoice",
      "acceptanceCriteria": ["Email sent", "Logged to Logs/"],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### 2. Check Your Tasks

```bash
./scripts/check-ralph-status.sh
```

### 3. Start Ralph

```bash
./scripts/start-ralph.sh 10
```

Ralph will:
1. Pick highest priority task
2. Execute it autonomously
3. Request approval for external actions
4. Wait for your approval
5. Complete task
6. Continue to next task
7. Repeat until all tasks done

---

## 📊 Examples

### Example 1: Monday Morning CEO Briefing (Hackathon Standout Feature)

**File:** `.claude/skills/ralph/prd_monday_ceo_briefing.json`

This is the **standout feature** mentioned in hackathon0.md - the "Monday Morning CEO Briefing" where AI autonomously prepares weekly business summary for CEO review.

**Task Breakdown:**
1. Check Gmail for urgent weekend messages
2. Check Calendar for upcoming events
3. Review business performance from logs
4. Check business goals and targets
5. Generate proactive suggestions
6. Format and finalize CEO briefing
7. Create follow-up action list

**Total tasks:** 7
**Estimated time:** 10-15 minutes (with approvals)
**Manual time would be:** 30-60 minutes
**Demonstrates:** All AI Employee capabilities working together

---

### Example 2: Client Onboarding (Original Example)

The `ralph/prd.json` file contains a complete example for client onboarding with 6 tasks:
1. Send welcome email
2. Create client folders
3. Create setup invoice
4. Schedule kickoff meeting
5. Create project plan
6. Add to Slack

**Total tasks:** 6
**Estimated time:** 10-15 minutes (with approvals)
**Manual time would be:** 30-45 minutes

---

## 🔄 How Ralph Works

### Per Iteration

```
┌─────────────────────────────────────────────┐
│ 1. LOAD STATE                              │
│    - Read prd.json (tasks)                 │
│    - Read progress.txt (learnings)          │
│    - Check Plans/ (previous work)           │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ 2. PICK NEXT TASK                          │
│    - Find highest priority with passes: false│
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ 3. EXECUTE (Claude Code)                   │
│    - Create plan in Plans/                  │
│    - Execute using MCPs/skills               │
│    - Create approval request                │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ 4. WAIT FOR APPROVAL                       │
│    - You review Pending_Approval/ file     │
│    - Move to Approved/ when ready            │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ 5. VERIFY & COMPLETE                       │
│    - Monitor executes action                │
│    - Moves to Done/                        │
│    - Update prd.json (passes: true)         │
│    - Log progress to progress.txt            │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│ 6. CHECK COMPLETE?                          │
│    - All tasks pass? → TASK_COMPLETE        │
│    - More tasks? → Next iteration           │
└─────────────────────────────────────────────┘
```

### Memory Between Iterations

Each iteration starts with **fresh context** but remembers via:

- **`prd.json`** - Which tasks are done/pending
- **`progress.txt`** - Learnings from previous work
- **`Plans/`**** - Previous execution plans
- **`Logs/`**** - Audit trail of all actions
- **Vault files**** - Client data, communications, etc.

---

## 🎯 Task Sizing Rules

**✅ Good (One session):**
- Send one email
- Create one folder structure
- Generate one invoice
- Schedule one meeting
- Post one social media update

**❌ Too Large (split these):**
- "Complete client onboarding" → 6 tasks
- "Handle all emails" → One task per email
- "Weekly review" → Split into 4-5 tasks

---

## 🛑 Stopping Ralph

### Safe Stop (After Current Task)

```bash
# Ralph will complete current iteration and stop
# Press Ctrl+C when waiting for approval
```

### Immediate Stop

```bash
# Find and kill Ralph process
pkill -INT ralph-claude.sh
```

### Check Status

```bash
./scripts/check-ralph-status.sh
```

---

## 📊 Monitoring Progress

### View Task Status

```bash
./scripts/check-ralph-status.sh
```

Output shows:
- Running status (PID if active)
- Task completion overview
- List of pending tasks
- List of completed tasks
- Recent progress log

### View Progress Log

```bash
cat ralph/progress.txt
```

Shows:
- Codebase patterns discovered
- Task-by-task progress
- Learnings for future iterations
- Files changed

---

## 🔧 Customization

### Edit Task List

```bash
# View current tasks
cat ralph/prd.json | jq '.userStories[]'

# Edit tasks
nano ralph/prd.json
# OR
code ralph/prd.json
```

### Change Priority

Edit `priority` field in prd.json (lower number = higher priority).

### Mark Task Complete

Edit `passes: false` → `passes: true` for completed task.

### Reset All Tasks

Set all `passes: false` to start over.

---

## 📝 Task Format Reference

### prd.json Structure

```json
{
  "project": "AI Employee",
  "branchName": "task-identifier",
  "description": "Brief description of overall goal",
  "userStories": [
    {
      "id": "TASK-XXX",
      "title": "Task title",
      "description": "As a [role], I want [feature] so that [benefit]",
      "acceptanceCriteria": [
        "Specific verifiable criterion 1",
        "Specific verifiable criterion 2",
        "Logged to Logs/YYYY-MM-DD.json"
      ],
      "priority": 1,
      "passes": false,
      "notes": "Optional context or dependencies"
    }
  ]
}
```

### Required Fields

- `id` - Unique task identifier (TASK-001, TASK-002, etc.)
- `title` - Short descriptive title
- `description` - What the task does
- `acceptanceCriteria` - Array of verifiable criteria
- `priority` - Execution order (1 = highest)
- `passes` - false (pending) or true (complete)
- `notes` - Optional additional context

---

## 🎓 Examples

### Example 1: Simple Email Task

```json
{
  "id": "TASK-001",
  "title": "Send follow-up email",
  "description": "Send follow-up email to client about overdue invoice",
  "acceptanceCriteria": [
    "Email sent to client@example.com",
    "Email includes invoice #123 details",
    "Logged to Logs/YYYY-MM-DD.json"
  ],
  "priority": 1,
  "passes": false,
  "notes": ""
}
```

### Example 2: Multi-Step Calendar Task

```json
{
  "id": "TASK-005",
  "title": "Schedule project review meeting",
  "description": "Schedule 1-hour project review with stakeholders",
  "acceptanceCriteria": [
    "Calendar invite sent to all participants",
    "Meeting scheduled within next 3 business days",
    "Meeting duration: 60 minutes",
    "Agenda attached to invite",
    "Logged to Calendar/ or Briefings/",
    "Logged to Logs/YYYY-MM-DD.json"
  ],
  "priority": 5,
  "passes": false,
  "notes": "Depends on TASK-001, TASK-002, TASK-003"
}
```

---

## 🐛 Troubleshooting

### Ralph Not Starting

**Problem:** Script doesn't run
```bash
# Check permissions
ls -la ralph/ralph-claude.sh

# Make executable
chmod +x ralph/ralph-claude.sh
chmod +x scripts/start-ralph.sh
```

### Tasks Not Completing

**Problem:** Ralph runs but tasks stay incomplete

```bash
# Check progress log
cat ralph/progress.txt

# Check for pending approvals
ls AI_Employee_Vault/Pending_Approval/
ls AI_Employee_Vault/Approved/

# Check if monitors are running
pm2 status
```

### No Tasks Found

**Problem:** "No task list found (prd.json)"

```bash
# Check if prd.json exists
ls ralph/prd.json

# View example format
cat ralph/prd.json.example

# Create from example
cp ralph/prd.json.example ralph/prd.json
# Then edit with your tasks
```

---

## 📚 Documentation

- **Full Guide:** `docs/RALPH_IMPLEMENTATION_GUIDE.md`
- **System Status:** `docs/STATUS.md`
- **Quick Reference:** `docs/QUICK_REFERENCE.md`
- **Architecture:** `docs/ARCHITECTURE.md`

---

## 🎉 Benefits

1. **Autonomous Multi-Step Execution**
   - Complete workflows without supervision
   - 5-10 related tasks automated

2. **Human Control Maintained**
   - Every external action requires approval
   - Can edit/stop at any point

3. **Clean Context**
   - Each iteration starts fresh
   - No context buildup

4. **Persistent Memory**
   - Progress log tracks learnings
   - Vault maintains state
   - Logs provide audit trail

---

## 🚀 Ready to Use

Your Ralph implementation is ready!

**To start:**
1. Edit `ralph/prd.json` with your tasks
2. Run: `./scripts/check-ralph-status.sh` to verify
3. Run: `./scripts/start-ralph.sh 10` to start

**Ralph will autonomously:**
- Execute all tasks in priority order
- Request approval for external actions
- Wait for your review and approval
- Continue until all tasks complete

**You achieve:**
- ✅ 100% Gold Tier
- ✅ Autonomous multi-step workflows
- ✅ Human-in-the-loop maintained
- ✅ Complete business automation

---

## 🏆 Hackathon Requirements Alignment

Ralph directly addresses **Gold Tier Requirements** from hackathon0.md:

| Requirement | How Ralph Fulfills It |
|------------|----------------------|
| **Monday Morning CEO Briefing** (Standout Feature) | Autonomous 7-task briefing generator using Gmail, Calendar, Logs, Business_Goals, and weekly-briefing skill |
| **Full cross-domain integration (Personal + Business)** | Can execute tasks across Gmail (personal) and Calendar/Slack/Xero (business) in a single workflow |
| **Multiple MCP servers for different action types** | Uses email-mcp, calendar-mcp, slack-mcp, xero-mcp servers through skills and approval monitors |
| **Error recovery and graceful degradation** | @with_retry decorator on all watchers, error_recovery module, Ralph continues even if individual tasks fail |
| **Comprehensive audit logging** | Every Ralph iteration logs to Logs/YYYY-MM-DD.json via audit_logging module |
| **Ralph Wiggum loop** | Autonomous multi-step task completion (7 tasks autonomously completed with human approval for external actions) |
| **Documentation of architecture and lessons learned** | Complete Ralph implementation with README, SKILL.md, examples, and this guide |

---

**Ralph Wiggum for AI Employee - Ready for Production!**
*Last Updated: 2026-01-14*
*Version: 1.1 for AI Employee - Gold Tier Complete*
