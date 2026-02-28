# Inbox Processor - Forms and Templates

## Item Categorization Form

Use this decision tree for every incoming item:

```
Is it actionable?
├── YES → Does it require human approval?
│   ├── YES → Move to /Pending_Approval/
│   └── NO → Is it urgent?
│       ├── YES → Move to /Needs_Action/ (mark priority: high)
│       └── NO → Move to /Needs_Action/ (mark priority: normal)
└── NO → Is it reference material?
    ├── YES → Move to /Done/ with tag: reference
    └── NO → Move to /Done/ (archive)
```

## Processed Item Template

When processing an item, **create** this metadata header:

```yaml
---
type: [email|task|file|event]
source: [inbox|watcher|manual]
category: [action_required|information|delegate|archive]
priority: [critical|high|medium|low]
processed_date: YYYY-MM-DDTHH:MM:SSZ
original_location: /Inbox/filename.ext
destination: [folder]/filename.ext
---
```

## Daily Processing Log Template

**Create** daily logs at `/Logs/inbox_processing_YYYY-MM-DD.md`:

```markdown
# Inbox Processing Log - YYYY-MM-DD

## Summary
- Items Processed: 0
- Routed to Needs_Action: 0
- Routed to Pending_Approval: 0
- Archived: 0

## Items Processed
### [Time] - Item Name
- **Type**: [category]
- **Destination**: [folder]
- **Reason**: [why routed here]

## Notes
[Additional observations]
```

## Urgency Assessment Form

| Indicator | Critical | High | Medium | Low |
|-----------|----------|------|--------|-----|
| Time-sensitive (deadline today) | ✓ | | | |
| Contains "urgent/asap" | ✓ | | | |
| Financial/payment needed | ✓ | | | |
| Client inquiry | | ✓ | | |
| General task | | | ✓ | |
| Reference/info only | | | | ✓ |
