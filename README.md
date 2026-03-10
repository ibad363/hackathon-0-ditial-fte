# AI Employee — Personal Digital FTE (Gold Tier)

An autonomous AI-powered employee system that manages social media, email, file processing, accounting, and business intelligence — all with human-in-the-loop approval workflows. Built for the Digital FTE Hackathon (Gold Tier).

## What It Does

This system acts as a full-time digital employee that:

- **Posts to Facebook, Instagram, and Twitter/X** automatically via Playwright browser automation
- **Monitors Gmail** for important emails and creates action files
- **Watches a drop folder** for new files and routes them through the pipeline
- **Runs an autonomous processing loop** (Ralph Wiggum) that handles tasks, recovers from errors, and alerts humans when needed
- **Tracks everything** with structured audit logs, debug screenshots, and a dashboard
- **Never acts without approval** — every external action requires explicit human sign-off via a file-based approval workflow

## Architecture

```
Entry Points (main.py)
        │
   ┌────┼────┐
   ▼    ▼    ▼
Watchers  Services  MCP Servers
(Gmail,   (Ralph,   (Social Playwright,
 Files)    Audit,    Odoo XML-RPC,
           Schedule) Email)
        │
        ▼
 AI_Employee_Vault (Obsidian)
 ├── Inbox/
 ├── Needs_Action/
 ├── Pending_Approval/
 ├── Approved/
 ├── Done/
 ├── Error_Queue/
 ├── Logs/Audit/
 └── Social/<Platform>/
```

Items flow through the pipeline: **Inbox → Needs_Action → Pending_Approval → Approved → Done**, with errors routed to `Error_Queue/` for automatic retry or human review.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full technical deep-dive.

## Gold Tier Requirements — Status

| # | Requirement | Status |
|---|------------|--------|
| 1 | All Silver requirements | Done |
| 2 | Cross-domain integration (Personal + Business) | Done |
| 3 | Odoo accounting system + MCP server | Code ready, needs Odoo instance |
| 4 | Facebook + Instagram integration | Done |
| 5 | Twitter/X integration | Done |
| 6 | Multiple MCP servers | Done |
| 7 | Weekly CEO Briefing | Done |
| 8 | Error recovery & graceful degradation | Done |
| 9 | Comprehensive audit logging | Done |
| 10 | Ralph Wiggum autonomous loop | Done |
| 11 | Architecture documentation | Done |
| 12 | All AI as Agent Skills | Done (20+ skills) |

## Key Features

### Social Media Automation
- **3 platforms**: Facebook, Instagram, Twitter/X — all via Playwright
- Session persistence (login once, post headless forever)
- Debug screenshots at every step for diagnosing failures
- Twitter-specific: JS-level clicks to bypass overlay detection, user-agent spoofing

### Human-in-the-Loop Approval
- Every external action requires a file in `Approved/`
- Drafts created in `Pending_Approval/` as Markdown with YAML frontmatter
- Human reviews and moves file to approve — simple, auditable, no database

### Ralph Wiggum Loop
- Autonomous multi-step task processor
- Routes items: invoices → approval, errors → error queue, general → done
- Hard iteration cap to prevent runaway loops
- Processes error queue: archives transient errors, flags unrecoverable

### Error Recovery
- Retry with exponential backoff (1min → 5min → 30min)
- Transient errors auto-archived, unrecoverable flagged for human
- Graceful degradation report updates dashboard with service health

### Audit Logging
- Per-day JSON audit logs with 90-day retention
- Per-service text logs (social platforms, error handler, Odoo, Ralph)
- Screenshots saved for every Playwright action

### 20+ Agent Skills
All AI functionality implemented as Claude Code Agent Skills:
- Social media (Facebook, Instagram, Twitter, LinkedIn)
- Communication (Email, WhatsApp, Slack, Calendar)
- Business (CEO Briefing, Accounting, Approval Manager)
- Operations (Ralph Loop, Cross-domain Coordinator, Planning Agent)
- Utilities (Document Processor, Content Generator, Skill Creator)

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Playwright browsers: `playwright install chromium`

### Setup

1. Clone the repo and install dependencies:
```bash
uv sync
```

2. Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

3. Login to social media platforms (opens headed browser):
```bash
python main.py --setup
```

4. Run the system:
```bash
# Full Gold mode (all watchers + scheduler)
python main.py --gold

# Or run individual components:
python main.py --ralph          # Autonomous processing loop
python main.py --post-social    # Post all approved social drafts
python main.py --audit          # Error recovery + degradation report
python main.py --sessions       # Check browser session status
python main.py --odoo           # Test Odoo connection
```

### Posting Workflow

1. Create drafts:
```bash
python main.py --social
```

2. Review drafts in `AI_Employee_Vault/Pending_Approval/`

3. Move approved drafts to `AI_Employee_Vault/Approved/`

4. Post:
```bash
python main.py --post-social
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12+ |
| Package Manager | uv |
| Browser Automation | Playwright (Chromium) |
| State Store | Obsidian Vault (Markdown files) |
| Email | Gmail API (OAuth2) |
| Accounting | Odoo 19 Community (XML-RPC) |
| Social Media | Facebook, Instagram, Twitter — Playwright |
| LinkedIn | Chrome DevTools Protocol (CDP) |
| Scheduling | APScheduler |
| File Watching | watchdog |
| AI Framework | Claude Code with Agent Skills |

## Project Structure

```
├── main.py                    # Entry point (all CLI modes)
├── mcp_server/                # MCP servers (platform automation)
│   ├── social_playwright_base.py
│   ├── facebook_playwright.py
│   ├── instagram_playwright.py
│   ├── twitter_playwright.py
│   ├── odoo_mcp.py
│   └── email_server.py
├── services/                  # Business logic
│   ├── social_media_manager.py
│   ├── ralph_loop.py
│   ├── audit_logger.py
│   ├── error_handler.py
│   ├── scheduler.py
│   └── session_manager.py
├── watchers/                  # Event-driven monitors
│   ├── filesystem_watcher.py
│   ├── gmail_watcher.py
│   └── whatsapp_watcher.py
├── .claude/skills/            # 20+ Agent Skills
├── AI_Employee_Vault/         # Obsidian Vault (state store)
├── sessions/                  # Saved browser sessions (gitignored)
├── ARCHITECTURE.md            # Full technical architecture
└── .env.example               # Environment variable template
```

## Lessons Learned

1. **Twitter is the hardest to automate** — overlay divs block clicks, sessions expire fast, aggressive bot detection. Fix: JS-level clicks, user-agent spoofing, `keyboard.type()`.

2. **File-based state beats databases at this scale** — Markdown files are human-readable, editable, and need zero infrastructure.

3. **`force=True` doesn't truly force clicks** — Playwright's force mode still uses the click engine. Only `evaluate('el => el.click()')` bypasses overlay interception.

4. **Debug screenshots are essential** — Without visual access to headless browsers, screenshots at each step are the only way to diagnose failures.

5. **Human-in-the-loop is non-negotiable** — Every external action goes through file-based approval. Auditable, safe, simple.

## License

Hackathon project — built for the Digital FTE Hackathon.
