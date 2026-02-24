# LinkedIn Playwright Setup

No API keys or developer apps needed. Uses browser automation (Playwright) to post just like a human would.

---

## 1. Install Playwright

Run these commands in the project directory:

```bash
.venv/Scripts/pip install playwright
.venv/Scripts/playwright install chromium
```

---

## 2. Add credentials to `.env`

Open your `.env` file and add:

```
LINKEDIN_EMAIL=your_linkedin@email.com
LINKEDIN_PASSWORD=yourpassword
```

---

## 3. Save your LinkedIn session (run once)

This opens a browser window so you can log in manually. The session gets saved to `linkedin_session.json` so you won't need to log in again.

```bash
.venv/Scripts/python services/linkedin_poster.py
```

Choose option **3** → A Chromium browser window opens → Log in to LinkedIn → Come back to terminal and press **Enter**.

> After this, `linkedin_session.json` is saved. Future runs skip the login step entirely.

---

## 4. Test posting an approved draft

1. Run the script and choose **1** to create a test draft in `/Pending_Approval`
2. Move that `.md` file to `/Approved` folder
3. Run the script and choose **2** to post it

Or from main.py:
```bash
.venv/Scripts/python main.py --linkedin
```

---

## How it works

```
Draft created → saved to /Pending_Approval
       ↓
You review & move file to /Approved
       ↓
check_approved_posts() runs (every hour via scheduler)
       ↓
Playwright opens Chromium browser
       ↓
Loads saved session (no login needed)
       ↓
Navigates to LinkedIn feed
       ↓
Clicks "Start a post" → types content → clicks "Post"
       ↓
File moved to /Done
```

---

## Security notes

- `linkedin_session.json` contains your login cookies — keep it private, it's already in `.gitignore`
- The system **never posts without a file in /Approved** — that's the human approval gate
- `headless=False` means you can see what the browser is doing
