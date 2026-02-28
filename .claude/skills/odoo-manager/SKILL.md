---
name: odoo-manager
description: Monitor Odoo Community Edition accounting system for events requiring attention. Tracks invoices, payments, vendor bills, and overdue accounts via XML-RPC API.
license: Apache-2.0
author: AI Employee System
version: 1.0.0
category: watcher
tags: [accounting, odoo, erp, finance, invoices, payments]
---

# Odoo Manager

Monitor Odoo Community Edition for accounting events and financial data.

## Purpose

The Odoo Manager watches your Odoo accounting system and:

- **Detects new draft invoices** that need to be sent
- **Tracks payments received** from customers
- **Monitors overdue invoices** for follow-up
- **Creates monthly accounting files** with revenue/expense summaries
- **Generates action files** for events requiring human attention

## Integration

**Platform:** Odoo Community Edition (XML-RPC API)

**Connection Method:** Direct XML-RPC to Odoo server

**Credentials Required:**
- `ODOO_URL` - Odoo server URL (default: `http://localhost:8069`)
- `ODOO_DB` - Database name (default: `odoo`)
- `ODOO_USERNAME` - Admin username (default: `admin`)
- `ODOO_PASSWORD` - Admin password (default: `admin`)

## Usage

### Via PM2 (Continuous)

```bash
pm2 start odoo-watcher
```

The watcher runs continuously, checking every 5 minutes (300 seconds) for new accounting events.

### Manual Execution

```bash
# Run once for testing
python -m watchers.odoo_watcher --vault AI_Employee_Vault --once

# With custom Odoo credentials
python -m watchers.odoo_watcher \
  --vault AI_Employee_Vault \
  --odoo-url https://your-odoo-server.com \
  --odoo-db your_database \
  --odoo-username your_username \
  --odoo-password your_password \
  --once
```

## Events Detected

### Invoice Events

**Type:** `invoice`

Created when:
- New draft invoice detected
- Invoice needs to be sent to customer
- Invoice requires review

**Action File Format:**
```markdown
---
type: odoo_invoice
service: odoo
priority: high|medium|low
status: pending
created: 2026-01-19T10:30:00Z
odoo_id: INV/2026/0001
odoo_type: invoice
---

# Odoo Invoice: INV/2026/0001

**Partner:** Acme Corporation
**Amount:** $2,500.00
**Date:** 2026-01-19
**Status:** Draft

## Customer Invoice

**Due Date:** 2026-02-19

### Suggested Actions:
- [ ] Review invoice details
- [ ] Send to customer if not already sent
- [ ] Record payment when received
- [ ] Reconcile with bank statement

### Priority: Medium
```

### Payment Events

**Type:** `payment`

Created when:
- New payment received from customer
- Payment needs reconciliation

### Overdue Events

**Type:** `overdue_invoice`

Created when:
- Invoice is past due date
- Payment not received
- Follow-up required

## Accounting Files

The watcher creates monthly accounting files at:

```
AI_Employee_Vault/Accounting/YYYY-MM.md
```

**Contents:**
- Revenue summary (total from customer invoices)
- Expense summary (total from vendor bills)
- Invoice list (sent and overdue)
- Payments received
- Profit & Loss calculation

**Example:**
```markdown
---
month: 2026-01
period_start: 2026-01-01
period_end: 2026-01-31
status: open
updated: 2026-01-19T10:30:00Z
source: odoo_watcher
odoo_connected: true
---

# Accounting: January 2026

## Revenue
| Source | Amount | Invoices | Notes |
|--------|--------|----------|-------|
| Customer Invoices | $15,250.00 | 8 | Odoo Live Data |

**Total Revenue:** $15,250.00

## Expenses
| Category | Amount | Vendor |
|----------|--------|--------|
| Vendor Bills | $4,320.00 | 5 vendors |

**Total Expenses:** $4,320.00

## Profit & Loss
- **Revenue:** $15,250.00
- **Expenses:** ($4,320.00)
- **Net Profit:** $10,930.00
```

## Configuration

### PM2 Environment Variables

```javascript
{
  name: "odoo-watcher",
  script: ".claude/skills/odoo-manager/scripts/run_odoo_watcher.py",
  args: "--vault AI_Employee_Vault --interval 300",
  env: {
    "ODOO_URL": "http://localhost:8069",
    "ODOO_DB": "your_database",
    "ODOO_USERNAME": "your_username",
    "ODOO_PASSWORD": "your_password",
    "PYTHONUNBUFFERED": "1"
  }
}
```

### Priority Rules

**High Priority:**
- Payments received (requires reconciliation)
- Invoices over $5,000
- Overdue invoices

**Medium Priority:**
- Invoices over $1,000
- Vendor bills

**Low Priority:**
- Invoices under $1,000
- Routine accounting events

## Error Handling

**Connection Failures:**
- Odoo not available → Graceful degradation, uses placeholder data
- Authentication failed → Logs error, continues monitoring

**Data Fetch Failures:**
- API errors → Logs error, returns empty event list
- Invalid data → Skips malformed records

**State Persistence:**
- Last check time saved to `.odoo_watcher_state.json`
- Survives PM2 restarts
- Prevents duplicate event detection

## Troubleshooting

### Odoo Not Connecting

```bash
# Test connection manually
python -c "from utils.odoo_client import OdooClient; client = OdooClient('http://localhost:8069', 'odoo', 'admin', 'admin'); client.connect(); print('Connected!')"
```

### No Events Detected

Check:
1. Odoo server is running
2. Credentials are correct
3. Database has invoices/payments
4. Watcher state file (`.odoo_watcher_state.json`) for last check time

### Accounting File Not Updating

```bash
# Force update with --once flag
python -m watchers.odoo_watcher --vault AI_Employee_Vault --once

# Check accounting folder exists
ls AI_Employee_Vault/Accounting/
```

## Dependencies

- `utils/odoo_client.py` - Odoo XML-RPC client
- `watchers/base_watcher.py` - Base watcher class
- `watchers/error_recovery.py` - Retry logic with exponential backoff
- `utils/audit_logging.py` - Audit trail logging

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              ODOO WATCHER                          │
│                                                      │
│  Every 5 minutes:                                   │
│  1. Connect to Odoo via XML-RPC                    │
│  2. Fetch new invoices, payments, overdue          │
│  3. Create action files in Needs_Action/            │
│  4. Update accounting file in Accounting/           │
│  5. Save state to .odoo_watcher_state.json          │
└─────────────────────────────────────────────────────┘
```

## Security Notes

- **Credentials stored in environment variables** - Never in code
- **XML-RPC over HTTP** - Use HTTPS for production
- **Local-first architecture** - Data never leaves your network
- **Audit trail** - All events logged to `Logs/YYYY-MM-DD.json`

## License

Apache License 2.0
