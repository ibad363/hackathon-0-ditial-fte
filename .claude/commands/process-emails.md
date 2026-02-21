# Process Emails Command

You are an AI Employee processing email action files. Follow these steps precisely:

## Step 1: Read Email Files
- Scan `/Needs_Action/` for files matching `EMAIL_*.md`
- Read each file's frontmatter (from, subject, priority, status)
- Read the email preview content

## Step 2: Assess Priority
- **HIGH:** Contains words like "urgent", "asap", "payment", "invoice", "deadline"
- **MEDIUM:** General business communication, meeting requests, follow-ups
- **LOW:** Newsletters, notifications, FYI messages

## Step 3: Draft Replies
- For HIGH priority: Draft an immediate reply acknowledging receipt and promising action
- For MEDIUM priority: Draft a professional response within context
- For LOW priority: Note it and archive
- Save reply drafts to `/Pending_Approval/REPLY_[subject].md`

## Step 4: Create Approval Requests
If the email involves any of these, create an approval request in `/Pending_Approval/`:
- Money or payments over $100
- Commitments or deadlines
- Sharing confidential information
- Agreeing to meetings on behalf of the CEO

## Step 5: Update Dashboard
Add a new entry to `Dashboard.md.md` under Recent Activity:
```
- [DATE] Processed email from [SENDER]: [SUBJECT] — [ACTION TAKEN]
```

## Step 6: Move Processed Files
- Move processed EMAIL files from `/Needs_Action/` to `/Done/`
- Log the action in `/Logs/log.md`

## Tone
- Professional, concise, and respectful
- Match the formality level of the sender
- When in doubt, be more formal
