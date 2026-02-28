# Gold Tier Architecture - AI Employee Digital FTE

## System Overview

The AI Employee is a personal digital full-time employee that monitors your Gmail, file drops, and business systems, then takes action with human approval. Silver Tier handles email, files, LinkedIn, and scheduling. Gold Tier adds Odoo ERP accounting, multi-platform social media (Facebook, Instagram, Twitter), autonomous error recovery (Ralph Loop), structured audit logging, and a unified scheduler that ties everything together.

Every action that affects the outside world (posting, invoicing, payments) requires a human approval file in the Approved/ folder before the system will execute it. Nothing goes out without your sign-off.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         main.py (Entry Point)                     │
│  --watcher | --gmail | --scheduler | --linkedin | --odoo          │
│  --setup | --social | --post-social | --sessions                  │
│  --ralph | --audit | --gold (all Gold services)                   │
└────────────┬─────────────────────────────────────────────────────┘
             │
     ┌───────┴────────────────────────────────────────────┐
     │                                                     │
┌────▼─────────────┐  ┌──────────────────┐  ┌─────────────▼──────────┐
│    WATCHERS       │  │   MCP SERVERS     │  │      SERVICES           │
│                   │  │                   │  │                         │
│ filesystem_watcher│  │ email_server.py   │  │ scheduler.py            │
│ gmail_watcher.py  │  │ odoo_mcp.py       │  │ linkedin_poster.py      │
│ whatsapp_watcher  │  │ social_pw_base.py │  │ social_media_manager.py │
│ base_watcher.py   │  │ facebook_pw.py    │  │ session_manager.py      │
│                   │  │ instagram_pw.py   │  │ error_handler.py        │
│                   │  │ twitter_pw.py     │  │ audit_logger.py         │
│                   │  │                   │  │ ralph_loop.py           │
└────────┬──────────┘  └────────┬──────────┘  └────────┬──────────────┘
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   AI_Employee_Vault/   │
                    │                       │
                    │  Inbox/               │
                    │  Needs_Action/        │
                    │  Pending_Approval/    │
                    │  Approved/            │
                    │  Done/                │
                    │  Rejected/            │
                    │  Plans/               │
                    │  Error_Queue/         │
                    │  Accounting/          │
                    │  │ Invoices/          │
                    │  │ Payments/          │
                    │  │ Monthly_Reports/   │
                    │  Social/              │
                    │  │ Facebook/          │
                    │  │ Instagram/         │
                    │  │ Twitter/           │
                    │  Logs/                │
                    │  │ Audit/             │
                    │  │ screenshots/       │
                    │  Dashboard.md         │
                    └───────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  APPROVAL FLOW:                                                   │
│  Draft created → Pending_Approval/ → Human reviews →              │
│    Approved/ (to post) OR Rejected/ (to discard)                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  RALPH LOOP (Autonomous Recovery):                                │
│  Check Needs_Action + Error_Queue → Route files → Process errors  │
│  → Repeat until empty or max 20 iterations → Alert if stuck       │
└──────────────────────────────────────────────────────────────────┘
```

## File Reference

### Root
| File | Purpose |
|---|---|
| `main.py` | Single entry point with CLI flags for every feature |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for all required environment variables |
| `.gitignore` | Keeps secrets, sessions, and assets out of git |

### watchers/
| File | Purpose |
|---|---|
| `base_watcher.py` | Base class for all file/event watchers |
| `filesystem_watcher.py` | Monitors drop_folder/ for new files, routes to vault |
| `gmail_watcher.py` | Monitors Gmail inbox via OAuth, creates action files |
| `whatsapp_watcher.py` | Monitors WhatsApp Web via Playwright |

### mcp_server/
| File | Purpose |
|---|---|
| `email_server.py` | MCP server for sending emails via Gmail SMTP |
| `odoo_mcp.py` | Odoo ERP integration: invoices, payments, revenue via XML-RPC |
| `social_playwright_base.py` | Base class for all social media Playwright automation |
| `facebook_playwright.py` | Facebook login + post flow |
| `instagram_playwright.py` | Instagram login + post flow (requires image) |
| `twitter_playwright.py` | Twitter/X login + post flow (auto-truncate 280 chars) |

### services/
| File | Purpose |
|---|---|
| `scheduler.py` | Unified Silver+Gold scheduler with all timed tasks |
| `linkedin_poster.py` | LinkedIn draft creation and approval-based posting |
| `social_media_manager.py` | Orchestrates drafts and posting across FB/IG/Twitter |
| `session_manager.py` | Check, refresh, and validate browser sessions |
| `error_handler.py` | Retry with escalation, error queue processing, health checks |
| `audit_logger.py` | Structured JSON audit logs with 90-day retention |
| `ralph_loop.py` | Autonomous loop: routes Needs_Action, processes errors |

### scripts/
| File | Purpose |
|---|---|
| `create_placeholder.py` | Generate default 1080x1080 placeholder image |
| `setup_social_sessions.py` | One-time headed browser login for all platforms |

## Setup Instructions

1. **Clone and install dependencies**
   ```
   git clone <repo>
   cd hackathon-0-ditial-fte
   pip install -r requirements.txt
   playwright install
   ```

2. **Configure environment**
   ```
   cp .env.example .env
   # Edit .env with your real credentials
   ```

3. **Gmail OAuth setup**
   - Download `credentials.json` from Google Cloud Console
   - Run `python main.py --gmail` once to complete OAuth flow
   - `token.json` will be saved automatically

4. **Generate placeholder image**
   ```
   python scripts/create_placeholder.py
   ```

5. **Setup social media sessions**
   ```
   python main.py --setup
   # Login manually to each platform in the browser that opens
   # Press ENTER after each login
   ```

6. **Test Odoo connection** (if using Odoo)
   ```
   python main.py --odoo
   ```

7. **Verify everything**
   ```
   python main.py --sessions    # Check browser sessions
   python main.py --audit       # Check service health
   ```

8. **Run Gold mode**
   ```
   python main.py --gold        # All services + Gold scheduler
   ```

## Approval Workflow

The system **never** takes external action without human approval:

1. **Draft created** — System writes a markdown file to `Pending_Approval/`
2. **Human reviews** — Open the file, read the content, check it's correct
3. **Approve** — Move the file to `Approved/` folder
4. **Reject** — Move the file to `Rejected/` folder
5. **System acts** — Scheduler or manual command picks up approved files and executes
6. **Logged** — Every action is recorded in `Logs/Audit/` as structured JSON

Financial actions (Odoo invoices, payments) have an additional check:
- An approval file named `Approved/odoo_<action>.md` must exist before the action runs

## Troubleshooting

| Problem | Solution |
|---|---|
| `playwright not installed` | Run `pip install playwright && playwright install` |
| `Odoo connection failed` | Check ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD in .env |
| `No session for <platform>` | Run `python main.py --setup` to login manually |
| `Session expired / login failed` | Delete `sessions/<platform>/session.json` and re-run --setup |
| `Error queue growing` | Run `python main.py --audit` to see what's failing |
| `Ralph loop hit max iterations` | Check Dashboard.md for alert, review Needs_Action/ manually |
| `Gmail OAuth error` | Delete `token.json` and re-run `python main.py --gmail` |
| `Screenshot errors` | Check `AI_Employee_Vault/Logs/screenshots/` for visual clues |
| `Import errors` | Make sure you run from project root: `D:/Ibad Coding/hackathon-0-ditial-fte/` |
| `Missing .env variables` | Compare your .env against .env.example for missing keys |

## Lessons Learned

_(To be filled in after deployment and usage)_
