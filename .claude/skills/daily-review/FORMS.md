# Daily Review - Forms and Templates

## Daily Plan Template

**Create** daily plans at `/Plans/daily_YYYY-MM-DD.md`:

```markdown
---
date: YYYY-MM-DD
created: YYYY-MM-DDTHH:MM:SSZ
total_items: 0
urgent_count: 0
high_priority_count: 0
---

# Daily Plan - YYYY-MM-DD

## 🔴 Critical (Do Now)
- [ ] Item requiring immediate attention

## 🟠 High Priority (Today)
- [ ] Task due today
- [ ] Meeting preparation needed

## 🟡 Medium Priority (This Week)
- [ ] Task with upcoming deadline

## 🟢 Low Priority (Backlog)
- [ ] Nice to have item

## Calendar Today
| Time | Event | Preparation Needed |
|------|-------|-------------------|
| 09:00 | Team standup | Review agenda |
| 14:00 | Client call | Prepare notes |

## Pending Approvals
| Item | Waiting For | Action |
|------|-------------|--------|
| Payment | Human approval | Review and approve |

## Notes
[Additional context for the day]
```

## Priority Assessment Matrix

| Urgency \ Importance | High | Medium | Low |
|---------------------|------|--------|-----|
| **Today** | 🔴 Critical | 🟠 High | 🟡 Medium |
| **This Week** | 🟠 High | 🟡 Medium | 🟢 Low |
| **Later** | 🟡 Medium | 🟢 Low | 🟢 Low |

## Quick Review Checklist

```
□ Check /Needs_Action/ for new items
□ Review /Pending_Approval/ for blocked items
□ Scan today's calendar events
□ Check for deadlines due today/tomorrow
□ Review Company_Handbook for any rule updates
□ Update Dashboard with today's focus
```

## Dashboard Update Template

Update these sections in `Dashboard.md`:

```markdown
## Today's Focus

### Urgent
- [ ] Item 1
- [ ] Item 2

### In Progress
- [ ] Item 3

### Upcoming Deadlines
| Task | Due | Priority |
|------|-----|----------|
| Task 1 | Today | Critical |
```
