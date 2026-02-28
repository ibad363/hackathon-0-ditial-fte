# Accounting Manager - Examples

## Example 1: Categorizing a New Expense

**Input:** New bank transaction detected
```
Amount: $54.00
Description: ADOBE *CREATIVE CLOUD
Date: 2026-01-10
```

**Processing Steps:**

1. **Detect** vendor: "Adobe" → Software category
2. **Sub-categorize**: "Creative Cloud" → Development tools
3. **Check** if recurring: Yes (monthly subscription)
4. **Update** `/Accounting/2026-01.md`:

```markdown
## Expenses
| Category | Amount | Vendor | Date |
|----------|--------|--------|------|
| Software/Development | $54 | Adobe | 2026-01-10 |
```

**Result:** Expense properly categorized and tracked

---

## Example 2: Invoice Payment Received

**Scenario:** Client pays invoice INV-001

**Processing:**

1. Xero Watcher detects payment
2. **Updates** invoice status from "Sent" to "Paid"
3. **Records** in `/Accounting/2026-01.md`:

```markdown
### Invoices Paid
| Invoice # | Client | Amount | Date Paid |
|-----------|--------|--------|-----------|
| INV-001 | Client A | $1,500 | 2026-01-15 |
```

3. **Updates** revenue total
4. **Celebrates** internally 🎉

**Result:** Revenue tracked, client notified if needed

---

## Example 3: Overdue Invoice Alert

**Scenario:** Invoice INV-003 is 25 days overdue

**Xero Watcher detects:**
```json
{
  "invoice_number": "INV-003",
  "amount": 2000,
  "days_overdue": 25,
  "contact": "Client C"
}
```

**Creates action file** at `/Needs_Action/INVOICE_OVERDUE_INV-003.md`:

```markdown
---
priority: high
status: pending
---

# Overdue Invoice Alert

**Invoice:** INV-003
**Client:** Client C
**Amount:** $2,000
**Days Overdue:** 25 days

## Suggested Actions
- [ ] Send payment reminder email
- [ ] Call client to discuss
- [ ] Consider payment plan
```

**Result:** Human follows up with client

---

## Example 4: Monthly Financial Summary

**Input:** End of month, generate summary

**Claude Code prompt:**
```
Use the accounting skill to generate a monthly financial summary
for January 2026. Include revenue, expenses, profit, and key insights.
```

**Processing:**

1. **Read** `/Accounting/2026-01.md`
2. **Sum** revenue from all sources
3. **Sum** expenses by category
4. **Calculate** profit/loss
5. **Compare** to goals in `Business_Goals.md`
6. **Generate** summary:

```markdown
# January 2026 Financial Summary

## Executive Summary
Strong month with revenue ahead of target. One client payment
delayed but now resolved. Software costs stable.

## Revenue
- **Total:** $12,500
- **Goal:** $10,000
- **Progress:** 125% ✅

### Top Clients
1. Client A: $5,000 (40%)
2. Client B: $3,500 (28%)
3. Client C: $2,500 (20%)
4. Other: $1,500 (12%)

## Expenses
- **Total:** $850
- **Budget:** $1,000
- **Under budget by:** $150 ✅

### By Category
- Software: $450 (53%)
- Marketing: $200 (24%)
- Office: $100 (12%)
- Travel: $100 (12%)

## Profit & Loss
- **Gross Revenue:** $12,500
- **Total Expenses:** ($850)
- **Net Profit:** $11,650

## Key Insights
1. Revenue 25% above target - excellent performance
2. Client A represents 40% of revenue - consider diversification
3. Software costs stable, no new subscriptions
4. Marketing ROI positive (generated $3,500 in leads)

## Action Items
- [ ] Send thank you note to top 3 clients
- [ ] Review Client A contract for renewal
- [ ] Plan marketing spend for February
```

**Result:** Complete financial overview for decision-making

---

## Example 5: CEO Briefing Integration

**Scenario:** Monday morning briefing generation

**Weekly Briefing includes accounting section:**

```markdown
## Revenue

### This Week
| Metric | Amount | Change vs Last Week |
|--------|--------|-------------------|
| Revenue | $2,450 | +15% ↑ |
| Invoices Sent | 2 | - |
| Invoices Paid | 3 | +1 |

### Month to Date
| Metric | MTD | Goal | Progress |
|--------|-----|------|----------|
| Revenue | $8,500 | $10,000 | 85% |
| Invoices Outstanding | $3,200 | - | 3 invoices |

## Proactive Suggestions

### Cost Optimization
⚠️ **Notion**: $15/month - No activity in 45 days
- **Action**: Cancel or downgrade?
- **Savings**: $180/year

### Revenue Opportunities
💡 **Client A**: Contract expiring in 30 days
- **Action**: Prepare renewal proposal
- **Potential**: $6,000 annual contract

### Cash Flow
📊 **Strong Position**: 85% of monthly goal reached
- **Confidence**: High
- **Recommendation**: Consider Q1 investment in tools
```

**Result:** Financial insights integrated into business overview

---

## Example Commands for Claude Code

```
"Categorize this expense: $150 for Adobe Creative Cloud"

"Track this payment: Client A paid $2,500 for INV-001"

"Generate monthly profit/loss report for January"

"Check for any overdue invoices that need follow-up"

"Compare this month's expenses to last month"

"Update the accounting file with today's revenue"

"Create an invoice for Client B: $3,000 for web development"

"Which subscriptions should we review this month?"

"What's our revenue vs goal for this quarter?"
```

---

## Example 6: Subscription Audit

**Scenario:** Quarterly subscription review

**Processing:**

1. **Extract** all software expenses from last 90 days
2. **Check** last usage date (from logs or manual tracking)
3. **Identify** candidates for cancellation:

```markdown
## Subscription Audit - Q1 2026

### Active Subscriptions
| Service | Cost/mo | Last Used | Recommendation |
|---------|---------|-----------|----------------|
| Adobe Creative Cloud | $54 | 2026-01-15 | ✅ Keep - Daily use |
| Slack | $8 | 2026-01-15 | ✅ Keep - Team comms |
| Notion | $15 | 2025-11-20 | ⚠️ Cancel - No activity |
| GitHub Copilot | $10 | 2026-01-14 | ✅ Keep - Daily use |
| Figma | $45 | 2026-01-10 | ✅ Keep - Active projects |

### Potential Savings
- **Notion**: $15/month = $180/year
- **Total Annual Savings**: $180

### Recommendations
1. Cancel Notion subscription
2. Consolidate tools where possible
3. Review Adobe plan (could downgrade?)
```

**Result:** $180/year in savings identified
