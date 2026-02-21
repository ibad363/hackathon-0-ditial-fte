# Silver Tier - Setup & Testing Guide

## Prerequisites
- Python 3.12+
- pip (or uv)
- A Gmail account
- (Optional) LinkedIn Developer account for posting

---

## STEP 1: Install Dependencies

```bash
cd "D:/Ibad Coding/hackathon-0-ditial-fte"
pip install -r requirements.txt
```

Or if using uv:
```bash
uv pip install -r requirements.txt
```

Verify installs:
```bash
python -c "import watchdog, schedule, dotenv, googleapiclient; print('All packages installed OK')"
```

---

## STEP 2: Setup Environment File

```bash
copy .env.example .env
```

Open `.env` and fill in your values:
```
MY_EMAIL=your_real_gmail@gmail.com
MY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_PERSON_ID=your_id
```

> LinkedIn credentials are optional for now. Gmail is the priority.

---

## STEP 3: Setup Gmail OAuth2

This is the most involved step. Follow carefully:

### 3a. Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Click **Select a Project** > **New Project**
3. Name it: `AI Employee` > Create
4. Select the new project

### 3b. Enable Gmail API
1. Go to **APIs & Services** > **Library**
2. Search for **Gmail API**
3. Click **Enable**

### 3c. Create OAuth Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. If prompted, configure the **OAuth consent screen** first:
   - User type: **External** > Create
   - App name: `AI Employee`
   - User support email: your email
   - Developer contact: your email
   - Click **Save and Continue** through all steps
   - Add your Gmail as a **Test User**
4. Now create the credential:
   - Application type: **Desktop app**
   - Name: `AI Employee Desktop`
   - Click **Create**
5. Click **Download JSON**
6. Save the downloaded file as `credentials.json` in the project root:
   ```
   D:/Ibad Coding/hackathon-0-ditial-fte/credentials.json
   ```

### 3d. First-Time Authorization
```bash
python watchers/gmail_watcher.py
```

- A browser window will open asking you to sign in
- Sign in with your Gmail account
- Click **Allow** to grant read-only access
- The terminal will show: `[Gmail] Token saved for future use`
- A `token.json` file is created (auto-refreshes, no need to repeat)
- Press `Ctrl+C` to stop after you see it checking for emails

---

## STEP 4: Verify Each Component

Run each test one by one.

### Test 1: Filesystem Watcher
Open **Terminal 1**:
```bash
python main.py --watcher
```

Open **Terminal 2** — create a test file:
```bash
echo "Test task from client" > "D:/Ibad Coding/hackathon-0-ditial-fte/drop_folder/test_task.txt"
```

**Expected result:**
- Terminal 1 shows: `Copied: test_task.txt`
- Check `AI_Employee_Vault/Needs_Action/` — should have `FILE_test_task.txt` and `FILE_test_task.md`

Press `Ctrl+C` to stop.

### Test 2: Gmail Watcher
```bash
python main.py --gmail
```

**Expected result:**
- Shows `[Gmail Watcher] Starting up...`
- Shows `[Gmail] Successfully connected to Gmail API`
- Every 2 minutes checks for unread important emails
- If you have unread important emails, creates `EMAIL_*.md` files in `Needs_Action/`

Send yourself an important email and mark it as important (the star/flag) to test.
Press `Ctrl+C` to stop.

### Test 3: LinkedIn Draft (No credentials needed)
```bash
python main.py --linkedin
```

Choose option `1` to create a test draft.

**Expected result:**
- Shows `[LinkedIn] Draft saved: LINKEDIN_DRAFT_*.md`
- Check `AI_Employee_Vault/Pending_Approval/` — should have the draft file
- Open it in Obsidian to see the formatted post

### Test 4: Scheduler
```bash
python main.py --scheduler
```

**Expected result:**
- Shows all scheduled tasks with times
- Shows `[Scheduler] Running... Press Ctrl+C to stop`
- Check `AI_Employee_Vault/Logs/scheduler_log.md` — should show `Scheduler started`

Press `Ctrl+C` to stop.

### Test 5: Full System
```bash
python main.py
```

**Expected result:**
- Filesystem watcher thread starts
- Gmail watcher thread starts
- Scheduler runs on main thread
- All three running simultaneously

Press `Ctrl+C` to stop all.

---

## STEP 5: Test Approval Workflow

This tests the core Silver Tier feature — nothing posts without your approval.

### 5a. Create a LinkedIn Draft
```bash
python main.py --linkedin
```
Choose option `1`.

### 5b. Review in Obsidian
Open your vault in Obsidian. Go to `Pending_Approval/` folder.
Read the draft. Edit if needed.

### 5c. Approve by Moving
Move the file from `Pending_Approval/` to `Approved/` (drag in Obsidian or File Explorer).

### 5d. Post It (requires LinkedIn credentials in .env)
```bash
python main.py --linkedin
```
Choose option `2` to check and post approved drafts.

### 5e. Reject Instead
If you don't like a draft, move it to `Rejected/` instead.

---

## STEP 6: Test Agent Commands

These work with Claude Code CLI.

```bash
# Process any emails sitting in Needs_Action
claude /process-emails

# Create a plan from a task
claude /create-plan

# Draft a LinkedIn post
claude /linkedin-post

# Generate a weekly briefing
claude /weekly-briefing
```

---

## STEP 7: LinkedIn Setup (Optional)

Only needed if you want to actually post to LinkedIn.

### 7a. Create LinkedIn App
1. Go to https://www.linkedin.com/developers/apps
2. Click **Create App**
3. Fill in app details, associate with a LinkedIn page
4. Under **Auth** tab, note your **Client ID** and **Client Secret**

### 7b. Get Access Token
1. Under **Auth** tab, add redirect URL: `https://localhost:8080/callback`
2. Under **Products** tab, request access to **Share on LinkedIn**
3. Use the OAuth 2.0 flow to get an access token
4. Quick way — use the LinkedIn Token Generator in developer portal

### 7c. Get Your Person ID
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" "https://api.linkedin.com/v2/me"
```
Copy the `id` field from the response.

### 7d. Update .env
```
LINKEDIN_ACCESS_TOKEN=your_actual_token
LINKEDIN_PERSON_ID=your_actual_id
```

---

## Folder Structure Reference

```
project-root/
├── .claude/commands/           # Agent skill commands
│   ├── process-emails.md
│   ├── create-plan.md
│   ├── linkedin-post.md
│   └── weekly-briefing.md
├── services/                   # Business logic
│   ├── linkedin_poster.py
│   └── scheduler.py
├── watchers/                   # Input channel monitors
│   ├── base_watcher.py
│   ├── filesystem_watcher.py
│   ├── gmail_watcher.py
│   └── whatsapp_watcher.py
├── docs/                       # Documentation
│   └── SILVER_TIER_SETUP.md
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Needs_Action/           # New tasks queue
│   ├── Pending_Approval/       # Drafts awaiting human review
│   ├── Approved/               # Human-approved items
│   ├── Rejected/               # Declined items
│   ├── Done/                   # Completed tasks
│   ├── Plans/                  # Action plans & briefings
│   ├── Logs/                   # Audit trail
│   ├── Inbox/                  # Staging area
│   ├── Dashboard.md.md
│   ├── Company_Handbook.md.md
│   └── Business_Goals.md
├── drop_folder/                # File drop input
├── main.py                     # Entry point
├── requirements.txt
├── .env.example
├── .env                        # Your secrets (git-ignored)
├── credentials.json            # Gmail OAuth (git-ignored)
└── token.json                  # Gmail token (git-ignored)
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'watchdog'` | Run `pip install -r requirements.txt` |
| `[Gmail] ERROR: credentials.json not found` | Download from Google Cloud Console (Step 3c) |
| `[Gmail] Token expired` | Delete `token.json` and re-run gmail watcher to re-auth |
| `[LinkedIn] ERROR: Missing credentials` | Fill in LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID in `.env` |
| `[LinkedIn] BLOCKED: File is not in /Approved` | Move draft from Pending_Approval to Approved first |
| `ImportError: cannot import from services` | Make sure `services/__init__.py` exists |
| Gmail says "App not verified" | Click **Advanced** > **Go to AI Employee (unsafe)** — this is normal for test users |

---

## Quick Verification Checklist

- [ ] `pip install -r requirements.txt` — no errors
- [ ] `python main.py --watcher` — starts and watches drop_folder
- [ ] Drop a file — appears in Needs_Action with FILE_ prefix
- [ ] `python main.py --gmail` — connects to Gmail (needs credentials.json)
- [ ] `python main.py --linkedin` option 1 — draft appears in Pending_Approval
- [ ] `python main.py --scheduler` — shows schedule and starts running
- [ ] `python main.py` — all three services run together
- [ ] Move a draft from Pending_Approval to Approved — approval workflow works
- [ ] Agent commands work: `claude /process-emails`
