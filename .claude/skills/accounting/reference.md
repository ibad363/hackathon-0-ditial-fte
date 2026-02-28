# Accounting Manager - Reference

## Key Files

| File | Purpose |
|------|---------|
| `/Accounting/YYYY-MM.md` | Monthly accounting summary |
| `/Accounting/invoices.md` | Invoice tracking master list |
| `/Accounting/expenses.md` | Expense categories and vendors |
| `/Accounting/revenue.md` | Revenue by source and client |
| `Business_Goals.md` | Revenue targets and budget |
| `Company_Handbook.md` | Financial approval thresholds |

## Folder Structure

| Folder | Contents | Update Frequency |
|--------|----------|------------------|
| `/Accounting/` | Monthly files, reports | Daily/Weekly |
| `/Pending_Approval/` | Invoices awaiting approval | As created |
| `/Approved/` | Approved invoices/transactions | As approved |
| `/Done/` | Completed financial items | As completed |

## Xero Integration

| Component | Purpose | Location |
|-----------|---------|----------|
| `xero_watcher.py` | Monitor transactions & invoices | `watchers/` |
| `xero-mcp/` | Create invoices, send reminders | `mcp-servers/` |
| `.xero_credentials.json` | OAuth credentials | Vault root (gitignored) |
| `.xero_token.json` | Access token | Vault root (gitignored) |

## Approval Thresholds (from Company_Handbook)

| Action | Auto-Approve | Always Require |
|--------|--------------|---------------|
| Expense <$50 | Recurring only | New vendor |
| Expense $50-$100 | No | Always |
| Expense >$100 | No | Always |
| Invoice creation | No | Always |
| Payment send | No | Always |

## Expense Categories

### Software
- **Development**: IDEs, tools, APIs
- **Office**: Productivity, communication
- **Design**: Creative tools

### Operations
- **Marketing**: Ads, promotion
- **Travel**: Transportation, lodging
- **Office**: Supplies, equipment
- **Professional Services**: Legal, accounting

### One-Time
- **Hardware**: Computers, equipment
- **Training**: Courses, books
- **Startup**: Initial setup costs

## Invoice Status Flow

```
DRAFT → PENDING_APPROVAL → APPROVED → SENT → PAID → DONE
                                              ↓
                                         OVERDUE
```

## Related Skills

- `weekly-briefing` - Uses financial data for CEO Briefing
- `inbox-processor` - Routes financial items to Pending_Approval
- `approval-manager` - Manages approval workflow

## Scripts

### `scripts/generate_report.py`

Generate profit/loss statements and financial summaries from monthly accounting files.

**Features:**
- Parse accounting data from `/Accounting/YYYY-MM.md`
- Calculate revenue by source
- Summarize expenses by category
- Generate profit/loss statement
- Calculate profit margins

**Usage:**
```bash
# Generate report for current month
python scripts/generate_report.py --vault .

# Generate report for specific month
python scripts/generate_report.py --vault . --month 2026-01

# Specify custom output path
python scripts/generate_report.py --vault . --month 2026-01 --output /path/to/report.md
```

**Output:**
- Report saved to `/Accounting/report_YYYY-MM.md`
- Sections: Executive Summary, Revenue, Expenses, Profit/Loss, Top Expenses
- Formatted as markdown for easy viewing

**Report Sections:**
1. Executive Summary (profitability overview)
2. Revenue Breakdown (by source)
3. Expense Breakdown (by category)
4. Profit & Loss Statement
5. Top 5 Expenses

### `scripts/track_revenue.py`

Track revenue progress against monthly goals (TODO).

### `scripts/categorize_expenses.py`

Automatically categorize expenses using keyword matching (TODO).
