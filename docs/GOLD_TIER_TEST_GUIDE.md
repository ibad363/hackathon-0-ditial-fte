# Gold Tier Test Guide

How to test every Gold Tier feature manually. Run from project root:
`D:/Ibad Coding/hackathon-0-ditial-fte/`

---

## Test 1: Silver Tier Still Works

Create a test file in drop folder:
```
copy NUL drop_folder\test_silver.txt
```

Start the file watcher:
```
uv run main.py --watcher
```
Wait 5 seconds, press Ctrl+C.

Check file moved to Inbox:
```
dir AI_Employee_Vault\Inbox\test_silver.txt
```

PASS: File appears in Inbox folder.

---

## Test 2: Odoo Accounting Integration

Test connection (will fail without real creds, that's expected):
```
uv run main.py --odoo
```

Check error was saved properly:
```
dir AI_Employee_Vault\Error_Queue\odoo_error_*
```

Test all 5 functions exist:
```
uv run python -c "from mcp_server.odoo_mcp import test_connection, create_invoice, get_pending_invoices, get_monthly_revenue, mark_invoice_paid; print('All 5 Odoo functions OK')"
```

PASS: Prints "All 5 Odoo functions OK". Error file saved in Error_Queue.

---

## Test 3: Facebook + Instagram Drafts

```
uv run python -c "from mcp_server.facebook_playwright import FacebookPoster; from mcp_server.instagram_playwright import InstagramPoster; FacebookPoster().create_post_draft('Test FB post', topic='Gold Test'); InstagramPoster().create_post_draft('Test IG post', topic='Gold Test', image_path='assets/default_post_image.png'); print('FB + IG drafts created')"
```

Check drafts exist:
```
dir AI_Employee_Vault\Pending_Approval\FACEBOOK_DRAFT_*
dir AI_Employee_Vault\Pending_Approval\INSTAGRAM_DRAFT_*
```

PASS: Both draft files appear in Pending_Approval.

---

## Test 4: Twitter Integration

```
uv run python -c "from mcp_server.twitter_playwright import TwitterPoster; TwitterPoster().create_post_draft('Test tweet for Gold Tier testing', topic='Gold Test'); print('Twitter draft created')"
```

Check:
```
dir AI_Employee_Vault\Pending_Approval\TWITTER_DRAFT_*
```

PASS: Twitter draft file in Pending_Approval.

---

## Test 5: Social Media Manager (All 3 at Once)

```
uv run python -c "from services.social_media_manager import create_all_drafts; create_all_drafts('Excited about our new project! #AI #Business', topic='Project Launch')"
```

PASS: 3 draft files created (FACEBOOK_DRAFT, INSTAGRAM_DRAFT, TWITTER_DRAFT).

---

## Test 6: Approval Workflow (Block Unapproved Posts)

Try posting with nothing approved:
```
uv run python -c "from services.social_media_manager import post_all_approved; r = post_all_approved(); print('Result:', r)"
```

PASS: Prints empty list or "No approved social media drafts found."

---

## Test 7: Approval Workflow (Session Check)

Move a draft to Approved:
```
move AI_Employee_Vault\Pending_Approval\FACEBOOK_DRAFT_Gold_Test_*.md AI_Employee_Vault\Approved\
```

Try posting:
```
uv run python -c "from services.social_media_manager import post_all_approved; r = post_all_approved(); print(r)"
```

PASS: Says "No session for Facebook. Run: python main.py --setup" (because no browser session yet). This proves the guard works.

---

## Test 8: All MCP Servers Import

```
uv run python -c "from mcp_server.email_server import send_email; from mcp_server.odoo_mcp import test_connection; from mcp_server.social_playwright_base import SocialPlaywrightBase; from mcp_server.facebook_playwright import FacebookPoster; from mcp_server.instagram_playwright import InstagramPoster; from mcp_server.twitter_playwright import TwitterPoster; print('All 6 MCP servers OK')"
```

PASS: Prints "All 6 MCP servers OK".

---

## Test 9: Error Recovery + Graceful Degradation

Create a fake error file. Save this as `AI_Employee_Vault/Error_Queue/test_error_20260303_120000.md`:
```
# Test Error
**Time:** 2026-03-03
**Context:** test_service
**Error:** Simulated connection timeout
```

Run audit:
```
uv run main.py --audit
```

PASS: Error gets processed (recovered). All 6 services show OK status. Dashboard updated.

---

## Test 10: Audit Logging

```
uv run python -c "from services.audit_logger import log_action; log_action('test_gold', 'tester', 'system', {'test': True}, 'success', 'N/A'); print('Audit entry saved')"
```

Verify the JSON file:
```
uv run python -c "import json; from pathlib import Path; from datetime import date; f = Path(f'AI_Employee_Vault/Logs/Audit/{date.today()}.json'); data = json.loads(f.read_text()); print(f'Entries today: {len(data)}'); print('Latest:', data[-1]['action_type'])"
```

PASS: Shows entry count and latest action is "test_gold".

---

## Test 11: Ralph Loop

Create 3 test files in `AI_Employee_Vault/Needs_Action/`:

File 1 - `payment_reminder.md`:
```
# Payment Reminder
Client billing overdue. Invoice #1234 payment pending.
```

File 2 - `server_crash.md`:
```
# Server Alert
Application error: database connection failed at 3:00 AM.
Exception thrown in production.
```

File 3 - `team_update.md`:
```
# Team Update
Sprint retrospective notes. Everything going well.
```

Run Ralph:
```
uv run main.py --ralph
```

Check routing:
- `payment_reminder.md` should be in `Pending_Approval/` (financial keyword)
- `server_crash.md` should be in `Error_Queue/` (error keyword)
- `team_update.md` should be in `Done/` (general)

```
dir AI_Employee_Vault\Pending_Approval\payment_reminder.md
dir AI_Employee_Vault\Error_Queue\server_crash.md
dir AI_Employee_Vault\Done\team_update.md
```

Check Ralph log:
```
type AI_Employee_Vault\Logs\ralph_log.md
```

PASS: All 3 files routed correctly. Log shows iteration details.

---

## Test 12: Weekly Social Summary

```
uv run python -c "from services.social_media_manager import get_weekly_summary; get_weekly_summary()"
```

PASS: Prints summary for Facebook, Instagram, Twitter with log entry counts.

---

## Test 13: Session Manager

```
uv run main.py --sessions
```

PASS: Shows status for all 3 platforms (Facebook, Instagram, Twitter). All show "No session" since setup hasn't been run.

---

## Test 14: Scheduler Has All Gold Schedules

```
uv run python -c "from services.scheduler import gold_monday_briefing, social_post_all, error_queue_check, ralph_loop_if_needed, sunday_revenue; print('gold_monday_briefing:', gold_monday_briefing.__doc__); print('social_post_all:', social_post_all.__doc__); print('error_queue_check:', error_queue_check.__doc__); print('ralph_loop_if_needed:', ralph_loop_if_needed.__doc__); print('sunday_revenue:', sunday_revenue.__doc__)"
```

PASS: All 5 Gold scheduler functions print their descriptions.

---

## Test 15: All Skills Installed

```
uv run python -c "from pathlib import Path; skills = sorted([d.name for d in Path('.claude/skills').iterdir() if d.is_dir()]); print(f'Total skills: {len(skills)}'); [print(f'  - {s}') for s in skills]"
```

PASS: Shows all installed skills.

---

## Test 16: Documentation Exists

```
uv run python -c "c = open('docs/GOLD_TIER_ARCHITECTURE.md').read(); sections = ['System Overview','Architecture Diagram','File Reference','Setup Instructions','Approval Workflow','Troubleshooting','Lessons Learned']; [print(f'  PASS: {s}' if s in c else f'  FAIL: {s}') for s in sections]"
```

PASS: All 7 sections show PASS.

---

## Test 17: Placeholder Image

```
uv run python scripts/create_placeholder.py
dir assets\default_post_image.png
```

PASS: File exists at `assets/default_post_image.png`.

---

## Test 18: Full Gold Mode (Final Test)

```
uv run main.py --gold
```

You should see:
- Filesystem watcher started
- Gmail watcher started
- Session status for all platforms
- All Silver + Gold schedules listed (9 total)
- "Running... Press Ctrl+C to stop"

Let it run 2 minutes, then Ctrl+C.

PASS: No crashes, all services start, all schedules listed.

---

## Quick Results Table

| # | Feature | Command | Expected |
|---|---------|---------|----------|
| 1 | File watcher | --watcher | File moves to Inbox |
| 2 | Odoo integration | --odoo | Error saved gracefully |
| 3 | FB + IG drafts | python -c | 2 drafts in Pending_Approval |
| 4 | Twitter drafts | python -c | 1 draft in Pending_Approval |
| 5 | All drafts at once | python -c | 3 drafts created |
| 6 | Block unapproved | python -c | Empty result |
| 7 | Session guard | python -c | "No session" message |
| 8 | MCP servers | python -c | All 6 import OK |
| 9 | Error recovery | --audit | Error recovered, 6 services OK |
| 10 | Audit logging | python -c | JSON entry saved |
| 11 | Ralph loop | --ralph | 3 files routed correctly |
| 12 | Weekly summary | python -c | Summary printed |
| 13 | Session check | --sessions | 3 platforms listed |
| 14 | Gold schedules | python -c | 5 functions exist |
| 15 | Skills installed | python -c | All skills listed |
| 16 | Documentation | python -c | 7 sections found |
| 17 | Placeholder image | scripts/ | PNG file created |
| 18 | Gold mode | --gold | All services start |
