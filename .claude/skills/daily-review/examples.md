# Daily Review - Examples

## Example 1: Morning Review with 5 Items

**Scenario:** Monday morning, 5 items in `/Needs_Action/`

**Items Found:**
1. `EMAIL_urgent_client_20250110.md` - marked urgent
2. `EVENT_meeting_20250110.md` - meeting at 2pm
3. `EMAIL_invoice_question_20250110.md` - normal priority
4. `TASK_review_document_20250110.md` - due Friday
5. `EMAIL_newsletter_20250110.md` - reference only

**Processing:**

1. **Classify** each item using priority matrix
2. **Generate** daily plan at `/Plans/daily_2025-01-10.md`

**Output Plan:**

```markdown
## 🔴 Critical (Do Now)
- [ ] Respond to urgent client email

## 🟠 High Priority (Today)
- [ ] Prepare for 2pm meeting

## 🟡 Medium Priority (This Week)
- [ ] Answer invoice question
- [ ] Review document (due Friday)

## 🟢 Low Priority
- [ ] Archive newsletter
```

---

## Example 2: Handling Blocked Items

**Scenario:** 2 items stuck in `/Pending_Approval/`

**Items:**
1. `PAYMENT_vendor_20250108.md` - waiting 2 days
2. `EMAIL_new_client_reply_20250109.md` - waiting 1 day

**Action:**
1. **Flag** blocked items in daily plan
2. **Surface** for human attention
3. **Note** aging items

**Output:**

```markdown
## Pending Approvals
| Item | Waiting Since | Action |
|------|---------------|--------|
| PAYMENT_vendor | 2 days | ⚠️ Follow up |
| EMAIL_new_client | 1 day | Review today |
```

---

## Example 3: Light Day with Calendar Focus

**Scenario:** 3 items in Needs_Action, 4 calendar events

**Processing:**

1. **Review** items - all low priority
2. **Focus** shifts to calendar preparation
3. **Generate** meeting prep checklist

**Output:**

```markdown
## 🔴 Critical
- [ ] None

## 🟠 High Priority (Today)
- [ ] Prepare for 9am standup
- [ ] Prep materials for 2pm client call
- [ ] Review agenda for 4pm planning

## Calendar Today
| Time | Event | Prep Needed |
|------|-------|-------------|
| 09:00 | Team Standup | Review updates |
| 11:00 | 1:1 with Manager | Prepare talking points |
| 14:00 | Client Call | Open project notes |
| 16:00 | Planning Session | Review roadmap |
```

---

## Example 4: End-of-Day Review

**Scenario:** 5pm, checking what's done

**Action:**
1. **Check** `/Plans/daily_2025-01-10.md`
2. **Move** completed items to `/Done/`
3. **Carry over** incomplete items to tomorrow
5. **Update** Dashboard

**Output:**

```markdown
## Today's Summary
✅ Completed: 3 items
⏳ Carried over: 2 items
📊 Productivity: 60%

## Carried to Tomorrow
- [ ] Review document (moved from today)
```

---

## Example Commands for Claude Code

```
"Run daily review and create today's plan"

"What's my focus for today? Check Needs_Action and calendar"

"Review pending approvals and flag anything waiting over 24 hours"

"Update the Dashboard with today's priorities"

"Create a daily plan and highlight anything due today"
```
