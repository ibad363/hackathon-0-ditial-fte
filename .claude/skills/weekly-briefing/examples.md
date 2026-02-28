# Weekly Briefing - Examples

## Example 1: Standard Week - On Track

**Scenario:** Week of Jan 6-10, revenue on track, normal activity

**Analysis:**
- Revenue: $2,450 (45% of $5,400 monthly goal)
- Tasks completed: 12
- No significant bottlenecks

**Executive Summary Output:**

```markdown
## Executive Summary
Strong week with revenue ahead of target pace. All major deliverables
completed on schedule. One minor bottleneck with Client B proposal
(+2 days) - root cause identified as waiting for assets. Focus this week:
close Project Alpha and respond to 3 new client inquiries.
```

---

## Example 2: Week with Cost Concerns

**Scenario:** Week with subscription creep detected

**Analysis of `/Accounting/` reveals:**
- Notion: $15/month - last activity 45 days ago
- Slack: $8/month - price increased from $6/month (33% increase)
- Adobe: $54/month - duplicate with Canva ($12/month)

**Proactive Suggestions Output:**

```markdown
### Cost Optimization

⚠️ **Notion**: $15/month - No team activity in 45 days
- **Action**: Cancel or downgrade?
- **Savings**: $180/year

⚠️ **Adobe Creative Cloud**: $54/month
- **Observation**: Duplicate functionality with Canva ($12/month)
- **Savings**: $504/year if cancelled

⚠️ **Slack**: Price increased 33% (from $6 to $8/month)
- **Action**: Review if workspace features justify increase
- **Savings**: Consider alternatives or negotiate

**Potential Annual Savings: $684**
```

---

## Example 3: Week with Bottlenecks

**Scenario:** Week with delayed deliverables

**Analysis from `/Done/` and `/Plans/`:**

| Task | Planned | Actual | Delay |
|------|---------|--------|-------|
| Client A proposal | 2 days | 5 days | +3 |
| Website updates | 1 day | 4 days | +3 |
| Invoice processing | Same day | 2 days | +2 |

**Root Cause Analysis:**

```markdown
## Bottlenecks

| Task | Expected | Actual | Delay | Root Cause |
|------|----------|--------|-------|------------|
| Client A proposal | 2 days | 5 days | +3 | Waiting for client assets |
| Website updates | 1 day | 4 days | +3 | API documentation unclear |
| Invoice processing | Same day | 2 days | +2 | Manual data entry |

### Pattern Identified
3 delays this week all relate to **external dependencies** and **documentation**.

### Recommendations
1. Create asset checklist for client onboarding
2. Request API documentation update from vendor
3. Consider invoice automation (Silver tier feature)
```

---

## Example 4: Week with Revenue Alert

**Scenario:** Month-end approaching, revenue below target

**Data:**
- MTD Revenue: $3,200 (32% of $10,000 goal)
- Days remaining: 5
- Outstanding invoices: $2,100

**Output:**

```markdown
## Revenue

### This Week
| Metric | Amount | Change vs Last Week |
|--------|--------|-------------------|
| Revenue | $850 | -15% ↓ |
| Invoices Sent | 2 | -1 |
| Invoices Paid | 1 | -2 |

### Month to Date
| Metric | MTD | Goal | Progress |
|--------|-----|------|----------|
| Revenue | $3,200 | $10,000 | ⚠️ 32% |
| Days Remaining | 5 | - | - |

⚠️ **ALERT**: Revenue tracking 18% behind pace to meet $10,000 goal.

### Immediate Actions Required
1. Follow up on $2,100 outstanding invoices
2. Accelerate proposal for hot lead
3. Consider offering rush fee for expedited work
```

---

## Example Commands for Claude Code

```
"Generate weekly CEO briefing"

"Create Monday briefing and check if we're on track for goals"

"Analyze last week's performance and identify any bottlenecks"

"Review subscriptions and flag any costs to optimize"

"Compare this week to last week and highlight changes"
```

---

## Example 5: Full Briefing Generation

**Input to Claude Code:**

```
Use the weekly-briefing skill to generate a comprehensive CEO briefing
for the period 2026-01-06 to 2026-01-10. Check Business_Goals.md for
targets, Accounting/ for financial data, and Done/ for completed work.
```

**Processing Steps:**

1. **Read** `/Business_Goals.md` → Extract revenue goal: $10,000/month
2. **Parse** `/Accounting/2026-01.md` → Sum transactions
3. **Scan** `/Done/` → Count completed tasks, analyze timing
4. **Check** `/Needs_Action/` → Identify pending items
5. **Review** `/Logs/*.json` → Extract activity metrics
6. **Generate** `/Briefings/2026-01-06_Monday_Briefing.md`

**Result:** Complete 3-page executive briefing
