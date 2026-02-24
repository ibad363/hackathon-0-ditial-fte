# AI Employee — What Is This Project?

## The Big Idea

This project is a **Digital Full-Time Employee (FTE)** — an AI-powered assistant that runs 24/7 on your computer, watches for incoming work (emails, dropped files), processes it intelligently using Claude AI, and takes action — but **never does anything sensitive without your approval first**.

Think of it as hiring an executive assistant that:
- Reads your emails and decides what needs attention
- Drafts replies for you to approve and send
- Posts on LinkedIn to build your brand (after you approve)
- Creates structured action plans from tasks
- Sends emails on your behalf via its own email tool
- Wakes up every morning at 8 AM and gives you a briefing

---

## The Core Loop (How It Works)

```
WORLD                    AI EMPLOYEE                   YOU
-----                    -----------                   ---
Gmail inbox    →→→  Gmail Watcher reads it      →→→  EMAIL_*.md appears
                         in Needs_Action/             in your Vault

Drop a file    →→→  File Watcher detects it     →→→  FILE_*.md appears
in drop_folder/          in Needs_Action/             in your Vault

                    Claude processes it:
                    - Assesses priority
                    - Drafts reply / plan
                    - Flags financial items      →→→  REPLY_*.md or
                    → saves to Pending_Approval/      APPROVAL_*.md
                                                      appear for you

YOU REVIEW:
Move file to   →→→  Scheduler detects it        →→→  Email is SENT
Approved/            hourly, triggers action          or post is PUBLISHED
                     via MCP server / Playwright

                    Everything logged to
                    Vault/Logs/ and Dashboard.md
```

---

## Project Components

### 1. Watchers (The Eyes)
| Component | File | What It Does |
|---|---|---|
| Gmail Watcher | `watchers/gmail_watcher.py` | Polls your Gmail every 2 minutes for unread+important emails. Creates `EMAIL_*.md` files in `Needs_Action/` |
| File Watcher | `watchers/filesystem_watcher.py` | Monitors `drop_folder/`. When you drop any file there, it creates a `FILE_*.md` task in `Needs_Action/` |

### 2. The Vault (The Brain/Memory)
An **Obsidian markdown vault** at `AI_Employee_Vault/` — this is where everything lives:

```
AI_Employee_Vault/
├── Needs_Action/       ← New tasks arrive here (emails, files)
├── Pending_Approval/   ← AI drafts waiting for your review
├── Approved/           ← You move things here to execute them
├── Done/               ← Completed/archived items
├── Plans/              ← Claude-generated action plans
├── Logs/               ← Full audit trail
├── Dashboard.md.md     ← Your executive summary
├── Business_Goals.md   ← Context Claude reads for every task
└── Company_Handbook.md ← Rules Claude follows
```

### 3. Agent Skills (The Intelligence)
Claude Code slash commands that process vault items:

| Command | When It Runs | What It Does |
|---|---|---|
| `/process-emails` | Daily 8 AM (+ manually) | Reads all EMAIL_*.md, assesses priority, drafts replies, creates approval requests |
| `/linkedin-post` | Wednesday 10 AM (+ manually) | Writes a CEO-style LinkedIn post, saves to Pending_Approval — never posts directly |
| `/create-plan` | Manually triggered | Reads a Needs_Action item and creates a structured PLAN_*.md |
| `/weekly-briefing` | Monday 7 AM | Aggregates all vault data into an executive summary |

### 4. Scheduler (The Clock)
`services/scheduler.py` — runs continuously, triggers Claude commands at set times:
- **8:00 AM daily** → `/process-emails`
- **Monday 7:00 AM** → `/weekly-briefing`
- **Wednesday 10:00 AM** → `/linkedin-post`
- **Every hour** → checks `Approved/` for LinkedIn posts to publish

### 5. MCP Server (The Hands — Email)
`mcp_server/email_server.py` — a JSON-RPC server that gives Claude a `send_email` tool. When Claude processes emails, it can call this tool to actually send replies via Gmail SMTP. Registered in `.claude/settings.json`.

### 6. LinkedIn Poster (The Hands — Social Media)
`services/linkedin_poster.py` — uses Playwright (browser automation) to log into LinkedIn and publish posts. Only activates when you move a draft from `Pending_Approval/` to `Approved/`.

### 7. Human-in-the-Loop (The Safety Net)
**Nothing sensitive happens without your approval.** The approval flow:
1. AI creates a draft in `Pending_Approval/`
2. You review it in Obsidian
3. You move it to `Approved/` → it executes
4. You move it to `Rejected/` → it gets archived, nothing happens

---

## What Silver Tier Delivers

| Capability | Status |
|---|---|
| Reads your Gmail automatically | Working |
| Monitors a drop folder for tasks | Working |
| Claude drafts email replies | Working |
| Claude creates action plans | Working |
| Weekly CEO briefing | Working |
| Sends emails via MCP server | Working |
| Posts to LinkedIn (Playwright) | Working |
| Human approval before any external action | Working |
| Scheduled automation (cron-style) | Working |
| Full audit trail in Obsidian vault | Working |

---

## How to Run It

```bash
# Start everything (watchers + scheduler)
python main.py

# Or start individual components
python main.py --gmail      # Gmail watcher only
python main.py --watcher    # File watcher only
python main.py --scheduler  # Scheduler only
```

Make sure `.env` has:
```
MY_EMAIL=your@gmail.com
MY_APP_PASSWORD=xxxx xxxx xxxx xxxx   # Gmail App Password
LINKEDIN_EMAIL=your@linkedin.com
LINKEDIN_PASSWORD=yourpassword
```
