# Daily Review - Reference

## Key Files

| File | Purpose |
|------|---------|
| `/Needs_Action/*.md` | Items awaiting processing |
| `/Pending_Approval/*.md` | Items requiring human approval |
| `/Plans/daily_*.md` | Generated daily plans |
| `Dashboard.md` | Updated with today's focus |
| `Company_Handbook.md` | Rules for prioritization |

## Folder Structure

| Folder | Contents | Review Frequency |
|--------|----------|------------------|
| `/Needs_Action/` | Active items | Daily |
| `/Pending_Approval/` | Blocked items | Daily |
| `/Done/` | Completed items | Weekly (for briefing) |
| `/Plans/` | Active plans | Daily review/archive |

## Priority Levels

| Level | Icon | Response Time | Criteria |
|-------|------|---------------|----------|
| Critical | 🔴 | Immediate | Deadline today, urgent request |
| High | 🟠 | < 4 hours | Deadline this week, client request |
| Medium | 🟡 | < 24 hours | Normal task, upcoming event |
| Low | 🟢 | Backlog | Reference, nice to have |

## Item Categories

| Category | Source | Typical Action |
|----------|--------|----------------|
| Email | gmail_watcher | Reply, forward, or archive |
| Event | calendar_watcher | Prepare, attend, or decline |
| Task | Manual/dropbox | Execute, delegate, or schedule |
| Financial | watcher/manual | Approve payment, record |
| Reference | Manual | Archive for future use |

## Time Estimation Guidelines

| Complexity | Estimation | Examples |
|------------|------------|----------|
| Quick | 5-15 min | Reply to email, simple task |
| Moderate | 30-60 min | Draft document, research |
| Significant | 2+ hours | Deep work, creative output |

## Related Skills

- `inbox-processor` - Feeds items to Needs_Action
- `weekly-briefing` - Uses Done items for summary

## Scripts

### `scripts/generate_daily_plan.py`

Automated script to generate prioritized daily plans from all action items.

**Features:**
- Scans `/Needs_Action/` and `/Pending_Approval/` folders
- Extracts priority from file frontmatter or content keywords
- Parses calendar events for daily schedule
- Generates structured daily plan with icons and categories

**Usage:**
```bash
# Generate daily plan
python scripts/generate_daily_plan.py --vault .

# Print summary only (no file creation)
python scripts/generate_daily_plan.py --vault . --summary-only
```

**Output:**
- Daily plan file at `/Plans/daily_YYYY-MM-DD.md`
- Console summary of item counts
- Items organized by priority (Critical → High → Medium → Low)

**Plan Structure:**
- 🔴 Critical items (Do Now)
- 🟠 High Priority (Today)
- 🟡 Medium Priority (This Week)
- 🟢 Low Priority (Backlog)
- Calendar events table
- Pending approvals table
