# Daily Review

Conduct comprehensive daily review of all action items, tasks, and calendar events to prioritize and plan the day.

## Purpose

The Daily Review skill **aggregates** all pending items across the vault, **assesses** their urgency and priority, **generates** a focused daily action plan, and **updates** the Dashboard with current status. This skill **ensures** nothing falls through the cracks while **enabling** focus on what matters most.

## Design Philosophy

- **Single Source of Truth**: All items reviewed in one place
- **Priority-Driven**: Important items surfaced first
- **Action-Oriented**: Output is a concrete plan, not just a list
- **Time-Boxed**: Review completes in under 5 minutes

## Workflow

1. **Collect** all items from `/Needs_Action/`
2. **Retrieve** today's calendar events
3. **Check** `/Pending_Approval/` for blocked items
4. **Assess** each item's urgency and priority
5. **Identify** time-sensitive items (deadlines today)
6. **Generate** prioritized daily plan
7. **Update** Dashboard with today's focus
8. **Create** plan file at `/Plans/daily_YYYY-MM-DD.md`

## Modularity

Extensible with:
- Custom priority scoring algorithms
- Integration with task management tools
- Automated time estimates
- Deadline tracking alerts

---

*Daily Review Skill v1.0*
