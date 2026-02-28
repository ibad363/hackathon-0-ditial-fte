# Inbox Processor - Reference

## Folder Structure

| Path | Purpose |
|------|---------|
| `/Inbox/` | Drop zone for all incoming items |
| `/Needs_Action/` | Items requiring processing |
| `/Pending_Approval/` | Items awaiting human approval |
| `/Done/` | Completed and archived items |
| `/Logs/` | Processing logs and audit trail |

## Key Files

| File | Purpose |
|------|---------|
| `Company_Handbook.md` | Rules for handling different item types |
| `Dashboard.md` | Updated after processing |
| `orchestrator.py` | Can trigger automated processing |

## Watcher Integration

Watchers **create** files that this skill **processes**:

| Watcher | Creates | Location |
|---------|---------|----------|
| `gmail_watcher.py` | Email action files | `/Needs_Action/` |
| `calendar_watcher.py` | Event action files | `/Needs_Action/` |

## Processing Rules

1. **Financial items** (payment, invoice, contract) → `/Pending_Approval/`
2. **Client communications** → `/Needs_Action/` (priority: high)
3. **Calendar events < 24 hours** → `/Needs_Action/` (priority: high)
4. **General tasks** → `/Needs_Action/` (priority: normal)
5. **Reference material** → `/Done/`
6. **Processed items** → Original deleted from `/Inbox/`

## Priority Levels

| Level | Response Time | Example |
|-------|---------------|---------|
| Critical | Immediate | Security alert, urgent client issue |
| High | < 4 hours | Client inquiry, today's deadline |
| Medium | < 24 hours | Normal task, upcoming meeting |
| Low | > 24 hours | Reference, backlog item |

## Related Skills

- `daily-review` - Reviews processed items
- `weekly-briefing` - Summarizes weekly activity

## Scripts

### `scripts/process_inbox.py`

Automated script to process and route items from `/Inbox/` to appropriate destinations.

**Features:**
- Analyzes file content for keywords (urgent, financial, approval)
- Routes items based on detected category
- Adds metadata headers to processed files
- Creates processing logs

**Usage:**
```bash
# Process all items in /Inbox
python scripts/process_inbox.py --vault .

# Dry run (analyze without moving)
python scripts/process_inbox.py --vault . --dry-run
```

**Output:**
- Items moved to `/Needs_Action/`, `/Pending_Approval/`, or `/Done/`
- Processing log at `/Logs/inbox_processing_YYYY-MM-DD.md`
- Console summary of actions taken
