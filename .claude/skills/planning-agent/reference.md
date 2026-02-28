# Planning Agent - Reference

## Key Files

| File | Purpose |
|------|---------|
| `/Plans/*.md` | Generated plan files |
| `/Needs_Action/` | Tasks that need planning |
| `Company_Handbook.md` | Planning guidelines and constraints |
| `Business_Goals.md` | Strategic objectives and targets |
| `Dashboard.md` | Active plans status |

## Planning Process

### Input Sources
- Human request ("Plan a project to...")
- Items from `/Needs_Action/` that are complex
- Business goals from `Business_Goals.md`
- Recurring tasks (weekly briefings, etc.)

### Output Destinations
- `/Plans/` - Generated plan files
- `/Pending_Approval/` - Plans requiring human review
- `/Approved/` - Approved plans ready for execution

## Plan States

| State | Description | Trigger |
|-------|-------------|--------|
| **Draft** | Initial plan created | Planning Agent generates |
| **Active** | Plan approved, being executed | Moved to `/Approved/` |
| **Completed** | All steps done | Last checkbox checked |
| **Cancelled** | Plan no longer relevant | Human decision |
| **On Hold** | Paused for some reason | External blocker |

## Complexity Indicators

### Low Complexity
- Single domain (technical, business, personal)
- 1-3 steps
- Clear requirements
- No external dependencies
- Familiar problem type

### Medium Complexity
- 2-3 domains
- 4-8 steps
- Some requirements ambiguity
- Some dependencies
- Similar to past work

### High Complexity
- 3+ domains
- 8+ steps
- Vague requirements
- Many dependencies
- Novel problem type

## Planning Methodologies

### Agile / Iterative
- Break into sprints
- Regular review cycles
- Adapt based on feedback
- Good for: Projects with changing requirements

### Waterfall / Sequential
- Detailed upfront planning
- Clear phases
- Document everything
- Good for: Well-defined projects

### MVP / Lean
- Start minimal
- Validate early
- Iterate based on data
- Good for: New products/features

### Work Breakdown Structure (WBS)
- Hierarchical decomposition
- Parent-child task relationships
- Clear deliverables
- Good for: Complex technical projects

## Related Skills

- `content-generator` - Generates content within plans
- `approval-manager` - Manages plan approval workflow
- `weekly-briefing` - Uses plan completion data for reports
- `daily-review` - Reviews plan progress daily

## Scripts

### `scripts/generate_plan.py`

Analyze a task or goal and generate a comprehensive Plan.md file.

### `scripts/update_plan.py`

Update an existing plan based on progress and changes.

### `scripts/assess_complexity.py`

Analyze a task and assess complexity, risks, and estimated effort.

## Quick Planning Templates

### Quick Task Plan (Simple)
```markdown
## Steps
- [ ] Task 1 (30 min)
- [ ] Task 2 (1 hour)
- [ ] Task 3 (30 min)

## Total Time: 2 hours
```

### Project Plan (Medium)
```markdown
## Phases
1. Research (4 hours)
2. Design (8 hours)
3. Implementation (16 hours)
4. Testing (4 hours)

## Total Time: 32 hours (~1 week)
```

### Complex Project Plan
```markdown
## Workstreams
1. Frontend (40 hours)
2. Backend (32 hours)
3. Infrastructure (16 hours)
4. Testing (16 hours)

## Dependencies
- Frontend ← Backend (API design)
- Infrastructure ← Backend (requirements)
- Testing ← All workstreams

## Timeline: 6-8 weeks
```
