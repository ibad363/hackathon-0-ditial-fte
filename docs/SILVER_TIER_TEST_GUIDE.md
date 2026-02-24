# Silver Tier — Complete Test Guide

This guide walks you through testing every Silver Tier feature with one realistic end-to-end scenario.

---

## The Scenario

> **"You receive a client email asking about a project. Your AI Employee reads it, drafts a reply, you approve it, and the email gets sent. Meanwhile, your LinkedIn post for the week gets drafted, approved, and published automatically."**

---

## Prerequisites

1. `.env` file configured with Gmail and LinkedIn credentials
2. `python main.py` is running (or start it now)
3. Obsidian vault open at `AI_Employee_Vault/`

---

## Test 1 — Gmail Watcher (Automatic Email Detection)

**What it tests:** Gmail watcher reads incoming emails and creates vault files.

### Steps:
1. From any email account, send an email to your Gmail (`MY_EMAIL`) with:
   - **Subject:** `Invoice Request - Project Alpha`
   - **Body:** `Hi, please send me the invoice for Project Alpha. Total amount should be $500. Urgent.`

2. Wait up to 2 minutes (watcher polls every 2 min)

3. Check `AI_Employee_Vault/Needs_Action/` — you should see:
   ```
   EMAIL_Invoice_Request_Project_Alpha_[id].md
   ```

4. Open the file — it should contain the sender, subject, priority (HIGH due to "invoice" + "urgent"), and email preview.

**Expected result:** File appears automatically, no manual action needed.

---

## Test 2 — File Drop Watcher (Task from File)

**What it tests:** Filesystem watcher detects dropped files and creates tasks.

### Steps:
1. Create a text file anywhere on your computer:
   ```
   client_brief.txt
   ---
   Client: Ahmed Corp
   Task: Review and respond to contract proposal
   Deadline: End of week
   ```

2. Copy/move it into `drop_folder/`

3. Within seconds, check `AI_Employee_Vault/Needs_Action/` — you should see:
   ```
   FILE_client_brief.txt
   FILE_client_brief_metadata.md
   ```

**Expected result:** Files appear instantly (watchdog is real-time).

---

## Test 3 — Process Emails Skill (Claude Intelligence)

**What it tests:** Claude reads EMAIL files, assesses priority, drafts a reply, creates approval request.

### Steps:
1. In Claude Code terminal, run:
   ```
   /process-emails
   ```

2. Claude will:
   - Read `EMAIL_Invoice_Request_Project_Alpha_*.md`
   - Assess it as HIGH priority (invoice + urgent)
   - Draft a reply
   - Create an approval request (financial commitment > $100)

3. Check `AI_Employee_Vault/Pending_Approval/` — you should see:
   ```
   REPLY_Invoice_Request_Project_Alpha.md
   APPROVAL_Invoice_Request_Project_Alpha.md
   ```

4. Check `AI_Employee_Vault/Done/` — the original EMAIL file should be moved there.

5. Check `AI_Employee_Vault/Dashboard.md.md` — should show a new Recent Activity entry.

**Expected result:** 2 files in Pending_Approval, email moved to Done, Dashboard updated.

---

## Test 4 — Human-in-the-Loop Approval (The Safety Net)

**What it tests:** Nothing gets sent without your explicit approval.

### Steps:
1. Open `Pending_Approval/REPLY_Invoice_Request_Project_Alpha.md` in Obsidian
2. Read the drafted reply — edit it if you want
3. To **approve**: move the file to `AI_Employee_Vault/Approved/`
   ```bash
   # In file explorer or terminal:
   mv "AI_Employee_Vault/Pending_Approval/REPLY_Invoice_Request_Project_Alpha.md" "AI_Employee_Vault/Approved/"
   ```
4. To **reject**: move it to `AI_Employee_Vault/Rejected/` — nothing will be sent

**Expected result:** File sits in Pending_Approval until YOU take action. System is completely paused.

---

## Test 5 — MCP Email Server (Send Email)

**What it tests:** Claude calls the MCP `send_email` tool to actually send the approved reply.

### Steps:
1. Run this directly to simulate what Claude does after approval:
   ```bash
   python -c "
   from mcp_server.email_server import send_email
   result = send_email(
       to='your-test-email@gmail.com',
       subject='Re: Invoice Request - Project Alpha',
       body='Thank you for reaching out. I have received your invoice request for Project Alpha (\$500). I will prepare and send the invoice within 24 hours.\n\nBest regards,\nAI Employee'
   )
   print(result)
   "
   ```

2. Check the target inbox — email should arrive within 1 minute.

3. Check `AI_Employee_Vault/Logs/email_log.md` — should show the send event.

**Expected result:** `{'success': True, 'to': '...', 'subject': '...'}` and email in inbox.

---

## Test 6 — LinkedIn Post Draft (AI Content Creation)

**What it tests:** Claude writes a professional LinkedIn post and saves it for approval — never posts directly.

### Steps:
1. In Claude Code terminal, run:
   ```
   /linkedin-post
   ```

2. Claude will write a CEO-style post based on `Business_Goals.md` context.

3. Check `AI_Employee_Vault/Pending_Approval/` — you should see:
   ```
   LINKEDIN_DRAFT_[topic]_[date].md
   ```

4. Verify it did NOT post to LinkedIn — the post only exists as a file.

**Expected result:** Draft file created, LinkedIn untouched.

---

## Test 7 — LinkedIn Approval & Auto-Post (Full Loop)

**What it tests:** Moving a LinkedIn draft to Approved triggers Playwright to publish it.

### Steps:
1. Open the `LINKEDIN_DRAFT_*.md` file, review the content
2. Move it to `Approved/`:
   ```bash
   mv "AI_Employee_Vault/Pending_Approval/LINKEDIN_DRAFT_*.md" "AI_Employee_Vault/Approved/"
   ```
3. Either wait for the hourly scheduler check, or trigger it manually:
   ```bash
   python -c "
   import sys; sys.path.insert(0, 'services')
   from linkedin_poster import check_approved_posts
   check_approved_posts()
   "
   ```
4. Playwright will open a browser (headless), log into LinkedIn, and publish the post.

5. Check `AI_Employee_Vault/Logs/linkedin_log.md` — should show `SUCCESS: Post published`

6. Check `AI_Employee_Vault/Done/` — the draft should be moved there after posting.

**Expected result:** Post appears on your LinkedIn profile, file moves to Done.

---

## Test 8 — Create Plan Skill (Structured Action Plans)

**What it tests:** Claude reads a task and creates a detailed action plan.

### Steps:
1. In Claude Code terminal, run:
   ```
   /create-plan
   ```
   (Claude will look at items in Needs_Action — use the `FILE_client_brief.txt` from Test 2)

2. Check `AI_Employee_Vault/Plans/` — you should see:
   ```
   PLAN_client_brief_[date].md
   ```

3. Open it — should contain: objective, action steps, priority level, estimated effort, and a Dashboard log entry.

**Expected result:** Structured plan file created in Plans/.

---

## Test 9 — Scheduler Fires Automatically

**What it tests:** The scheduler correctly finds and launches Claude CLI at scheduled times.

### Steps:
1. Start the scheduler:
   ```bash
   python main.py --scheduler
   ```

2. Check `AI_Employee_Vault/Logs/scheduler_log.md` — should show `Scheduler started`

3. The scheduler checks every 60 seconds. To verify it can find Claude without waiting for 8 AM, check the log shows it started cleanly without "Claude CLI not found" errors.

4. To do a quick forced test, temporarily run:
   ```bash
   python -c "
   import sys; sys.path.insert(0, 'services')
   from scheduler import morning_briefing
   morning_briefing()
   "
   ```
   (Run this OUTSIDE of a Claude Code session — open a regular terminal)

**Expected result:** Scheduler log shows TRIGGERED → COMPLETED entries.

---

## Test 10 — Weekly Briefing (Executive Summary)

**What it tests:** Claude aggregates all vault activity into an executive summary.

### Steps:
1. In Claude Code terminal, run:
   ```
   /weekly-briefing
   ```

2. Check `AI_Employee_Vault/Plans/` — you should see:
   ```
   Briefing_[date].md
   ```

3. Open it — should summarize: emails processed, plans created, LinkedIn posts, pending approvals, and business metrics.

**Expected result:** Comprehensive briefing document created.

---

## Full Silver Tier Checklist

| # | Feature | Test | Pass? |
|---|---|---|---|
| 1 | Gmail Watcher | Send email → check Needs_Action/ | |
| 2 | File Drop Watcher | Drop file → check Needs_Action/ | |
| 3 | Process Emails Skill | /process-emails → check Pending_Approval/ | |
| 4 | Human-in-the-Loop | Draft stays in Pending_Approval until YOU move it | |
| 5 | MCP Email Server | python send_email() → email received in inbox | |
| 6 | LinkedIn Post Draft | /linkedin-post → draft in Pending_Approval, not posted | |
| 7 | LinkedIn Auto-Post | Move to Approved/ → Playwright posts it | |
| 8 | Create Plan Skill | /create-plan → PLAN_*.md in Plans/ | |
| 9 | Scheduler | python main.py --scheduler → logs show started | |
| 10 | Weekly Briefing | /weekly-briefing → Briefing_*.md in Plans/ | |

All 10 pass = Silver Tier complete.
