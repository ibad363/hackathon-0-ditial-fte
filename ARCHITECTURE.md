# Architecture — AI Employee (Digital FTE, Gold Tier)

## Overview

This project is an autonomous AI Employee system that manages social media, email, file processing, accounting, and business intelligence — all with human-in-the-loop approval workflows. Built as a Gold Tier submission for the Digital FTE hackathon.

The system follows an **event-driven, file-based architecture** where the Obsidian Vault (`AI_Employee_Vault/`) acts as the central state store. Actions flow through a pipeline: **Inbox → Needs_Action → Pending_Approval → Approved → Done**, with errors routed to `Error_Queue/`.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRY POINTS                             │
│  main.py --gold    (all services)                               │
│  main.py --ralph   (autonomous loop)                            │
│  main.py --setup   (browser session setup)                      │
│  main.py --audit   (error recovery + degradation report)        │
│  main.py --post-social  (post approved drafts)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │   Watchers   │   │  Services   │   │ MCP Servers  │
   │ (Event Loop) │   │  (Logic)    │   │ (Automation) │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
              ┌──────────────────────────┐
              │    AI_Employee_Vault/     │
              │   (Obsidian State Store)  │
              │                          │
              │  Inbox/                  │
              │  Needs_Action/           │
              │  Pending_Approval/       │
              │  Approved/               │
              │  Done/                   │
              │  Error_Queue/            │
              │  Logs/Audit/             │
              │  Social/<Platform>/      │
              └──────────────────────────┘
```

---

## Directory Structure

```
hackathon-0-ditial-fte/
├── main.py                          # Entry point — all CLI modes
├── ARCHITECTURE.md                  # This file
│
├── mcp_server/                      # MCP servers (platform automation)
│   ├── social_playwright_base.py    # Base class for all social Playwright posters
│   ├── facebook_playwright.py       # Facebook posting via Playwright
│   ├── instagram_playwright.py      # Instagram posting via Playwright
│   ├── twitter_playwright.py        # Twitter/X posting via Playwright
│   ├── odoo_mcp.py                  # Odoo accounting integration (XML-RPC)
│   └── email_server.py              # Email MCP server
│
├── services/                        # Business logic layer
│   ├── social_media_manager.py      # Orchestrates all social platforms
│   ├── ralph_loop.py                # Ralph Wiggum autonomous processing loop
│   ├── audit_logger.py              # Structured JSON audit logging (90-day retention)
│   ├── error_handler.py             # Retry logic, error queue, graceful degradation
│   ├── session_manager.py           # Browser session management
│   ├── scheduler.py                 # Cron-like task scheduler
│   └── linkedin_poster.py           # LinkedIn posting (CDP-based)
│
├── watchers/                        # Event-driven watchers (daemon threads)
│   ├── base_watcher.py              # Base watcher class
│   ├── filesystem_watcher.py        # Drop folder monitor (watchdog)
│   ├── gmail_watcher.py             # Gmail inbox monitor (API)
│   └── whatsapp_watcher.py          # WhatsApp monitor (Playwright)
│
├── scripts/
│   └── setup_social_sessions.py     # One-time headed browser login for all platforms
│
├── sessions/                        # Saved browser sessions (cookies/storage)
│   ├── facebook/session.json
│   ├── instagram/session.json
│   └── twitter/session.json
│
├── assets/
│   └── default_post_image.png       # Default image for Instagram posts
│
├── .claude/skills/                  # Agent Skills (all AI as skills)
│   ├── ralph/                       # Ralph Wiggum autonomous loop skill
│   ├── social-media-manager/        # Social media orchestration skill
│   ├── facebook-instagram-manager/  # FB + IG content generation & posting
│   ├── twitter-manager/             # Twitter content generation & posting
│   ├── linkedin-manager/            # LinkedIn automation (CDP)
│   ├── email-manager/               # Gmail monitoring skill
│   ├── calendar-manager/            # Google Calendar monitoring skill
│   ├── whatsapp-manager/            # WhatsApp monitoring skill
│   ├── slack-manager/               # Slack monitoring skill
│   ├── odoo-manager/                # Odoo accounting skill
│   ├── weekly-briefing/             # CEO Briefing generation skill
│   ├── business-handover/           # Business audit skill
│   ├── approval-manager/            # Human-in-the-loop approval skill
│   ├── cross-domain-coordinator/    # Personal + Business domain routing
│   ├── docx-processor/              # Word doc → Markdown converter
│   ├── planning-agent/              # Task planning skill
│   ├── daily-review/                # Daily review generation
│   ├── inbox-processor/             # Inbox processing skill
│   ├── content-generator/           # Content generation skill
│   ├── accounting/                  # Accounting reports skill
│   └── skill-creator/               # Meta-skill for creating new skills
│
└── AI_Employee_Vault/               # Obsidian Vault (central state store)
    ├── Inbox/                       # Incoming items (emails, files, messages)
    ├── Needs_Action/                # Items requiring processing
    ├── Pending_Approval/            # Drafts awaiting human approval
    ├── Approved/                    # Human-approved items ready to execute
    ├── Done/                        # Completed/archived items
    ├── Rejected/                    # Human-rejected items
    ├── Error_Queue/                 # Failed items for retry/recovery
    ├── Plans/                       # Task plans
    ├── Accounting/                  # Odoo accounting data
    ├── Social/                      # Per-platform post logs & summaries
    │   ├── Facebook/
    │   ├── Instagram/
    │   ├── Twitter/
    │   └── LinkedIn/
    ├── Logs/
    │   ├── Audit/                   # JSON audit logs (per-day) + service logs
    │   └── screenshots/             # Debug screenshots from Playwright
    ├── Dashboard.md                 # System status dashboard
    ├── Business_Goals.md            # Business targets
    └── Company_Handbook.md          # Company reference
```

---

## Core Components

### 1. Social Media Automation (Playwright)

All social media posting uses Playwright browser automation with a shared base class pattern:

```
SocialPlaywrightBase (ABC)
├── FacebookPoster
├── InstagramPoster
└── TwitterPoster
```

**Key design decisions:**
- **Session persistence** — First login opens headed browser, saves cookies to `sessions/<platform>/session.json`. Subsequent runs use headless mode with saved session.
- **`keyboard.type()` over `fill()`** — Avoids overlay interception issues on Twitter/Instagram where background mask divs block pointer events.
- **JavaScript `evaluate('el => el.click()')` for buttons** — Bypasses Twitter's overlay div that intercepts Playwright's native click even with `force=True`.
- **User-Agent spoofing on Twitter** — Custom user-agent string to reduce headless detection. Twitter is more aggressive at detecting automation than Facebook/Instagram.
- **Debug screenshots** — Saved at each step (`before_caption`, `before_share`, `after_share`) for diagnosing failures without visual access.

### 2. Approval Workflow (Human-in-the-Loop)

Every action that affects external systems requires explicit human approval:

```
Content Generated → Pending_Approval/ → [Human moves file] → Approved/ → Execute
```

- Drafts are Markdown files with YAML frontmatter (platform, topic, timestamp, status)
- The system **never** posts without finding the matching file in `Approved/`
- Approval is checked by filename match — simple, auditable, no database needed

### 3. Ralph Wiggum Loop (Autonomous Processing)

The Ralph loop (`services/ralph_loop.py`) is the autonomous task executor:

```
LOOP (max N iterations):
  1. Count Needs_Action/ files
  2. Count Error_Queue/ files
  3. If both empty → EXIT (nothing to do)
  4. Route Needs_Action files (invoice→Pending, error→Error_Queue, other→Done)
  5. Process Error_Queue (archive transient, flag unrecoverable)
  6. Log iteration to ralph_log.md
  HARD STOP at max_iterations → alert human
```

**Safety:** Hard iteration cap prevents infinite loops. Unrecoverable errors are flagged, not deleted.

### 4. Error Recovery & Graceful Degradation

`services/error_handler.py` provides:

- **Retry with backoff** — `wrap_with_retry()`: 1min → 5min → 30min delays, max 3 attempts
- **Error queue processing** — Transient errors (timeouts, network) are archived. Unrecoverable errors remain for human review.
- **Degradation report** — Checks service health, updates `Dashboard.md` with status per service

### 5. Audit Logging

`services/audit_logger.py` provides structured JSON audit logs:

- One JSON file per day: `Logs/Audit/YYYY-MM-DD.json`
- Each entry: `{ timestamp, action_type, actor, target, parameters, result, approval_status }`
- 90-day auto-retention (old logs cleaned on each write)
- Separate text logs per service (error_handler, odoo, social platforms)

### 6. MCP Servers

Multiple MCP servers for different action types:

| Server | Protocol | Purpose |
|--------|----------|---------|
| `social_playwright_base.py` | Playwright | Social media posting (FB, IG, Twitter) |
| `odoo_mcp.py` | XML-RPC | Odoo accounting (invoices, payments, reports) |
| `email_server.py` | Gmail API | Email processing |

### 7. Agent Skills

All AI functionality is implemented as Agent Skills in `.claude/skills/`. Each skill has:
- `invoke.py` — Entry point
- `scripts/` — Implementation scripts
- Skill definition file — Describes triggers, capabilities, workflow

---

## Data Flow Examples

### Social Media Post Flow
```
1. Content generated (by skill or manually)
2. Draft created → Pending_Approval/TWITTER_DRAFT_topic_timestamp.md
3. Human reviews, moves to Approved/
4. post_all_approved() scans Approved/
5. Finds matching draft → calls TwitterPoster.post_approved_content()
6. Playwright opens headless browser → loads session → navigates to x.com
7. Types content via keyboard → clicks Post via JS evaluate
8. Screenshots saved → post summary logged → session refreshed
9. Draft moved to Done/
```

### Ralph Autonomous Loop
```
1. Gmail watcher detects email → creates action file in Needs_Action/
2. Ralph loop picks it up → reads content → routes:
   - Invoice mention → Pending_Approval/ (needs human sign-off)
   - Error mention → Error_Queue/ (needs investigation)
   - General → Done/ (acknowledged)
3. Error queue processed → transient errors archived, unrecoverable flagged
4. All actions logged to ralph_log.md + Audit JSON
```

---

## Lessons Learned

1. **Twitter is the hardest to automate** — Aggressive bot detection, overlay divs blocking clicks, session expiry. Solution: user-agent spoofing, JS-level clicks, `keyboard.type()`.

2. **File-based state > database for this scale** — Markdown files in Obsidian are human-readable, editable, version-controlled, and require zero infrastructure. The approval workflow is just moving a file.

3. **Session management is critical** — Playwright sessions expire. The system needs clear error messages ("session expired, re-login") rather than cryptic timeouts.

4. **`force=True` doesn't truly force** — Playwright's `force=True` skips actionability checks but still goes through the click engine. For overlays that intercept pointer events, only `evaluate('el => el.click()')` works.

5. **Debug screenshots are essential** — Without visual access to headless browsers, screenshots at each step are the only way to diagnose failures. Save them liberally.

6. **Human-in-the-loop is non-negotiable** — Every external action (post, email, payment) goes through explicit file-based approval. This makes the system auditable and safe to run autonomously.

7. **Ralph loop needs a hard cap** — Autonomous loops must have `max_iterations` to prevent runaway processing. When max is reached, alert the human immediately.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12+ |
| Package Manager | uv |
| Browser Automation | Playwright (Chromium) |
| Vault / State Store | Obsidian (Markdown files) |
| Email | Gmail API |
| Accounting | Odoo 19 Community (XML-RPC) |
| Social Media | Facebook, Instagram, Twitter via Playwright |
| LinkedIn | Chrome DevTools Protocol (CDP) |
| Scheduling | APScheduler |
| File Watching | watchdog |
| AI Framework | Claude Code with Agent Skills |
| Environment | dotenv (.env) |

---

## Running the System

```bash
# First-time setup — login to all social platforms (headed browser)
python main.py --setup

# Run everything (Gold mode)
python main.py --gold

# Individual components
python main.py --ralph          # Autonomous processing loop
python main.py --audit          # Error recovery + degradation report
python main.py --post-social    # Post all approved social drafts
python main.py --sessions       # Check browser session status
python main.py --odoo           # Test Odoo connection
```
