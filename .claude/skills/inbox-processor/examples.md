# Inbox Processor - Examples

## Example 1: Processing an Urgent Email

**Input:** `/Inbox/urgent_client_request.txt`

```
From: client@company.com
Subject: URGENT: Deadline change needed
We need to move the deadline from Friday to Wednesday. Please confirm.
```

**Processing Steps:**

1. **Scan** - Detect keyword "URGENT" and "deadline"
2. **Classify** - Type: email, Category: action_required, Priority: high
3. **Route** - Move to `/Needs_Action/EMAIL_client_deadline_20260110.md`
4. **Log** - Record in daily processing log

**Result:** Item moved, Dashboard updated, flagged for review

---

## Example 2: Processing a Payment Request

**Input:** `/Inbox/invoice_1234.pdf`

**Processing Steps:**

1. **Scan** - Detect "invoice" and financial nature
2. **Classify** - Type: financial, Category: approval_required, Priority: critical
3. **Route** - Move to `/Pending_Approval/PAYMENT_invoice_1234.md`
4. **Create** approval request file

**Result:** Item routed for human approval before any action

---

## Example 3: Processing Reference Material

**Input:** `/Inbox/article_to_read.html`

**Processing Steps:**

1. **Scan** - No action required, reference material
2. **Classify** - Type: reference, Category: archive, Priority: low
3. **Route** - Move to `/Done/REFERENCE_article_20260110.md`
4. **Tag** - Add tag: #reading-list

**Result:** Archived for later reference, no action needed

---

## Example 4: Batch Processing Multiple Items

**Scenario:** `/Inbox/` contains 5 items after weekend

**Processing Workflow:**

```bash
# Using Claude Code
claude --cwd .

# Prompt: "Process all items in /Inbox using the inbox-processor skill"
```

**Steps:**
1. List all items in `/Inbox/`
2. Process each item individually using categorization form
3. Create processing summary at `/Logs/inbox_processing_YYYY-MM-DD.md`
4. Update Dashboard with counts
5. Report summary to user

---

## Example 5: Integration with Watcher

**Scenario:** Gmail watcher creates new email file

**Flow:**

1. `gmail_watcher.py` detects unread email
2. **Creates** `/Needs_Action/EMAIL_urgent_20260110.md`
3. `inbox-processor` skill **reviews** on next cycle
4. **Confirms** correct categorization
5. **Updates** Dashboard with urgent count

**Result:** Seamless handoff between watcher and processor

---

## Example Commands for Claude Code

```
"Process all items in /Inbox and categorize them"

"Review the new email in Needs_Action and suggest next actions"

"Move processed items from Inbox and update the Dashboard"

"Create a summary of today's inbox processing"
```
