# Create Plan Command

You are an AI Employee creating action plans. Follow this format precisely:

## Step 1: Analyze the Task
- Read the source file from `/Needs_Action/` that triggered this plan
- Identify the core request, stakeholders, and deadline (if any)

## Step 2: Create Plan File
Save to `/Plans/PLAN_[descriptive_name].md` with this format:

```markdown
---
type: plan
source: [original filename]
created: [YYYY-MM-DD HH:MM:SS]
priority: [High/Medium/Low]
status: pending
---

# Plan: [Descriptive Title]

## Context
[1-2 sentences about what triggered this plan]

## Objective
[Clear statement of what needs to be accomplished]

## Action Steps
- [ ] Step 1: [First action]
- [ ] Step 2: [Second action]
- [ ] Step 3: [Third action]
- [ ] Step 4: [Verify completion]
- [ ] Step 5: [Update Dashboard and move to Done]

## Priority: [High/Medium/Low]
- **High:** Revenue impact, client-facing, deadline within 24hrs
- **Medium:** Important but not urgent, deadline within 1 week
- **Low:** Nice-to-have, no immediate deadline

## Dependencies
- [List any blockers or things needed before starting]

## Notes
- [Any additional context]
```

## Step 3: Link to Source
- Reference the original task file in the plan
- If the task came from an email, link the EMAIL file

## Step 4: Update Dashboard
Add entry: `- [DATE] Plan created: [PLAN_NAME] | Priority: [LEVEL]`

## Step 5: Log Action
Append to `/Logs/log.md`:
```
- [DATE] Created plan: [PLAN_NAME] from [SOURCE_FILE] | Priority: [LEVEL]
```
