# Accounting Manager - Forms and Templates

## Monthly Accounting File Template

`/Accounting/YYYY-MM.md`:

```markdown
---
month: YYYY-MM
period_start: YYYY-MM-01
period_end: YYYY-MM-30
status: open
---

# Accounting: YYYY-MM

## Revenue
| Source | Amount | Invoices | Notes |
|--------|--------|----------|-------|
| Client A | $2,500 | 3 | Web development |
| Client B | $1,800 | 2 | Consulting |

**Total Revenue:** $4,300

## Expenses
| Category | Amount | Vendor | Date |
|----------|--------|--------|------|
| Software | $150 | Adobe | 2026-01-05 |
| Software | $25 | Slack | 2026-01-05 |
| Office | $50 | Supplies | 2026-01-10 |

**Total Expenses:** $225

## Invoices

### Sent
| Invoice # | Client | Amount | Date | Status |
|-----------|--------|--------|------|--------|
| INV-001 | Client A | $1,500 | Jan 5 | Paid |
| INV-002 | Client B | $800 | Jan 10 | Sent |

### Overdue
| Invoice # | Client | Amount | Due Date | Days Overdue |
|-----------|--------|--------|----------|-------------|
| INV-003 | Client C | $2,000 | Dec 15 | 25 days |

## Profit & Loss
- **Revenue:** $4,300
- **Expenses:** ($225)
- **Net Profit:** $4,075

## Subscription Audit
| Service | Cost | Last Used | Action |
|---------|------|-----------|--------|
| Adobe | $54/month | 2026-01-05 | Keep |
| Notion | $15/month | 2025-11-20 | Review - No activity |

## Notes
- All invoices paid on time except INV-003 (followed up)
- Software costs stable
- Ready to send Q1 invoices

---

*Last updated: YYYY-MM-DD*
```

## Expense Categorization Form

Use this decision tree for every expense:

```
Is it software/subscription?
├── YES → Development tools or Office tools?
│   ├── Development → /Software/Development/
│   └── Office → /Software/Office/
└── NO → Is it travel?
    ├── YES → /Travel/
    └── NO → Is it marketing?
        ├── YES → /Marketing/
        └── NO → /Office Expenses/
```

## Expense Categories

| Category | Description | Examples |
|----------|-------------|----------|
| Software/Development | Development tools, IDEs | Adobe, GitHub, Copilot |
| Software/Office | Productivity, communication | Slack, Notion, Office 365 |
| Marketing | Advertising, promotion | Google Ads, social media |
| Travel | Transportation, lodging | Flights, hotels, meals |
| Office Expenses | Supplies, equipment | Desk, chair, printer |
| Professional Services | Legal, accounting, consulting | Lawyer, accountant |
| Hardware | Computers, equipment | Laptop, monitor, phone |

## Invoice Workflow

```
1. Work Completed
   ↓
2. Create Invoice Draft
   - Invoice number
   - Client details
   - Line items
   - Amount
   - Due date
   ↓
3. Save to /Pending_Approval/
   ↓
4. Human Review
   ↓
5. Move to /Approved/
   ↓
6. Xero MCP creates invoice in Xero
   ↓
7. Send to client
   ↓
8. Track payment status
   ↓
9. Move to /Done/ when paid
```

## Payment Reminder Templates

### 7 Days Before Due
```
Subject: Friendly Reminder: Invoice #INV-001 Due Soon

Hi [Client Name],

Just a friendly note that invoice #INV-001 for $[Amount] is due on [Due Date].

Please let us know if you have any questions.

Best regards
```

### Overdue (1-7 days)
```
Subject: Payment Overdue: Invoice #INV-001

Hi [Client Name],

Invoice #INV-001 for $[Amount] is now [X] days overdue.

Please arrange payment at your earliest convenience.

If you have any questions or need an updated copy, please let me know.

Best regards
```

### Seriously Overdue (14+ days)
```
Subject: URGENT: Invoice #INV-001 - [X] Days Overdue

Hi [Client Name],

Invoice #INV-001 for $[Amount] is now [X] days overdue.

Please contact us immediately to arrange payment or discuss a payment plan.

If we don't hear from you by [Date], we may need to pause work on your project.

Best regards
```

## Financial Health Indicators

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Revenue vs Goal | >80% | 50-80% | <50% |
| Invoice Payment Rate | >90% | 70-90% | <70% |
| Average Payment Time | <14 days | 14-30 days | >30 days |
| Overdue Invoices | 0 | 1-2 | 3+ |
| Expense Run Rate | Stable | <20% increase | >20% increase |
