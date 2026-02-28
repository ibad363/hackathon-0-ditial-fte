# Ralph Wiggum - Autonomous Task Execution Loop

**Gold Tier Requirement**: Execute multi-step business tasks autonomously while maintaining human oversight and approval for all external actions.

## Purpose

The Ralph Wiggum skill **iterates** through a task list until all items are complete, **maintains** state between iterations via files, **requests** approval for external actions, and **persists** progress for transparency and recovery. This skill **transforms** a list of tasks into a fully-executed workflow with minimal human supervision.

**Standout Feature**: Monday Morning CEO Briefing (7-task autonomous workflow that generates comprehensive business audit, performance analysis, and proactive suggestions).

## Design Philosophy

- **Autonomous Execution**: Continues until all tasks complete (no manual intervention)
- **Human-in-the-Loop**: Every external action requires approval
- **Fresh Context**: Each iteration starts clean (no memory buildup)
- **Persistent Memory**: State maintained via files (not conversation)
- **Transparent**: All progress logged and inspectable
- **Gold Tier**: Multi-step workflows for complex business operations

## Workflow

1. **Load** `ralph/prd.json` task list (or custom path)
2. **Read** `ralph/progress.txt` for learnings from previous iterations
3. **Pick** highest priority task where `passes: false`
4. **Plan** execution in `Plans/` folder
5. **Execute** using available AI Employee capabilities (MCPs, skills)
6. **Create** approval request in `Pending_Approval/`
7. **Wait** for human to move file to `Approved/`
8. **Verify** execution in `Logs/YYYY-MM-DD.json`
9. **Update** `prd.json` to mark task complete (`passes: true`)
10. **Log** progress to `progress.txt`
11. **Check** if all tasks complete → Output `<promise>TASK_COMPLETE</promise>`
12. **Continue** to next iteration

## Modularity

Extensible with:
- Custom task list formats (JSON, YAML)
- Custom approval workflows
- Custom completion signals
- Custom progress tracking
- Integration with any skill/MCP

## Inputs

- **Task List**: JSON file with `userStories` array
- **Progress File**: Text file with learnings
- **Vault Path**: Path to AI_Employee_Vault

## Outputs

- **Plans**: Execution plans in `Plans/` folder
- **Approvals**: Request files in `Pending_Approval/`
- **Logs**: Action logs in `Logs/YYYY-MM-DD.json`
- **Completion Signal**: `<promise>TASK_COMPLETE</promise>`

## Usage

```bash
# Start Ralph with default task list (ralph/prd.json)
claude --cwd AI_Employee_Vault < ralph/prompt-ai-employee.md

# Or use the convenience script
./scripts/start-ralph.sh 10

# Check status
./scripts/check-ralph-status.sh
```

## Task List Format

```json
{
  "project": "Project Name",
  "branchName": "feature-identifier",
  "description": "Brief description of what you're accomplishing",
  "userStories": [
    {
      "id": "TASK-001",
      "title": "Task title",
      "description": "As a [role], I want [feature] so that [benefit]",
      "acceptanceCriteria": [
        "Verifiable criterion 1",
        "Verifiable criterion 2",
        "Logged to Logs/YYYY-MM-DD.json"
      ],
      "priority": 1,
      "passes": false,
      "notes": "Optional context"
    }
  ]
}
```

## Task Sizing Rules

**✅ Good (One Claude Code session):**
- Send one email
- Create one folder structure
- Generate one invoice
- Schedule one meeting
- Post one social media update
- Read and summarize emails

**❌ Too Large (split these):**
- "Complete client onboarding" → Split into individual tasks
- "Handle all urgent emails" → One task per email
- "Weekly business review" → Split into 4-5 tasks

## Error Handling

- **Max Iterations**: Stops after N iterations to prevent infinite loops
- **Progress Tracking**: All actions logged to progress.txt
- **State Persistence**: prd.json updated after each task
- **Graceful Degradation**: Continues on error, logs issues

## Examples

See `ralph/prd.json` for example client onboarding workflow with 6 tasks.

## Dependencies

- BaseWatcher (for file monitoring)
- AI Employee vault structure
- PM2 (for process management, optional)
- Claude Code CLI

## See Also

- `ralph/README.md` - Complete Ralph guide
- `ralph/prompt-ai-employee.md` - Instructions for Claude Code
- `docs/RALPH_USER_GUIDE.md` - Ralph user guide (updated v1.1)
- `docs/PROCESS_CONTROL_GUIDE.md` - PM2 process management
- `ralph/prd_monday_ceo_briefing.json` - Monday CEO Briefing task list (7 tasks)
- `.claude/skills/business-handover/SKILL.md` - CEO Briefing skill

## Monday Morning CEO Briefing (Standout Feature)

### Overview
The Monday Morning CEO Briefing is the **standout feature** of the AI Employee system. It autonomously audits the business, analyzes performance, and generates actionable insights.

### Task List (7 Tasks)

```json
{
  "project": "Monday Morning CEO Briefing",
  "branchName": "ceo-briefing",
  "description": "Generate comprehensive Monday Morning CEO Briefing with business audit, performance analysis, and proactive suggestions",
  "userStories": [
    {
      "id": "TASK-001",
      "title": "Check Gmail for Urgent Weekend Messages",
      "description": "Scan AI_Employee_Vault/Needs_Action/EMAIL_*.md for urgent weekend messages requiring immediate attention",
      "acceptanceCriteria": [
        "All weekend emails reviewed",
        "Urgent items identified",
        "Findings documented in briefing"
      ],
      "priority": 1,
      "passes": false
    },
    {
      "id": "TASK-002",
      "title": "Review Calendar for Updated Events",
      "description": "Scan AI_Employee_Vault/Needs_Action/EVENT_*.md for upcoming events and meetings",
      "acceptanceCriteria": [
        "All upcoming events reviewed",
        "Schedule changes identified",
        "Calendar summary included in briefing"
      ],
      "priority": 2,
      "passes": false
    },
    {
      "id": "TASK-003",
      "title": "Analyze Business Performance from Logs",
      "description": "Scan AI_Employee_Vault/Logs/YYYY-MM-DD.json for business activity patterns and performance metrics",
      "acceptanceCriteria": [
        "All relevant logs analyzed",
        "Key metrics extracted",
        "Performance trends identified"
      ],
      "priority": 3,
      "passes": false
    },
    {
      "id": "TASK-004",
      "title": "Compare Progress to Business Targets",
      "description": "Read AI_Employee_Vault/Business_Goals.md and compare actual performance to targets",
      "acceptanceCriteria": [
        "Business goals reviewed",
        "Actual vs. target comparison complete",
        "Gaps and opportunities identified"
      ],
      "priority": 4,
      "passes": false
    },
    {
      "id": "TASK-005",
      "title": "Generate Proactive Optimization Suggestions",
      "description": "Identify cost savings, process improvements, and business opportunities",
      "acceptanceCriteria": [
        "Cost optimization opportunities identified",
        "Process improvements suggested",
        "New opportunities surfaced"
      ],
      "priority": 5,
      "passes": false
    },
    {
      "id": "TASK-006",
      "title": "Create Professional CEO Briefing Document",
      "description": "Generate comprehensive briefing document at AI_Employee_Vault/Briefings/YYYY-MM-DD_Monday_Briefing.md",
      "acceptanceCriteria": [
        "Briefing document created",
        "All sections complete",
        "Format matches template"
      ],
      "priority": 6,
      "passes": false
    },
    {
      "id": "TASK-007",
      "title": "Create Prioritized Action List for the Week",
      "description": "Generate prioritized action list at AI_Employee_Vault/Briefings/YYYY-MM-DD_Monday_Actions.md",
      "acceptanceCriteria": [
        "Action list created",
        "Tasks prioritized by importance",
        "Due dates and owners assigned"
      ],
      "priority": 7,
      "passes": false
    }
  ]
}
```

### Execution Performance

| Metric | Ralph (Autonomous) | Manual |
|--------|-------------------|--------|
| **Time** | 10-15 minutes | 30-60 minutes |
| **Speed** | 3-6x faster | Baseline |
| **Consistency** | 99%+ | Variable |
| **Coverage** | Complete | Often incomplete |

### Output Files

```
AI_Employee_Vault/Briefings/
├── YYYY-MM-DD_Monday_Briefing.md    # CEO briefing document
└── YYYY-MM-DD_Monday_Actions.md     # Prioritized action list
```

### PM2 Cron Schedule

```javascript
{
  name: "daily-briefing",
  script: ".claude/skills/ralph/scripts/run_ceo_briefing.sh",
  cron_schedule: "0 7 * * 1",  // Every Monday at 7:00 AM
  exec_mode: "fork"
}
```

---

*Ralph Wiggum Skill v1.1 - Gold Tier Autonomous Task Execution*
*Standout Feature: Monday Morning CEO Briefing (7 tasks, 3-6x faster than manual)*
