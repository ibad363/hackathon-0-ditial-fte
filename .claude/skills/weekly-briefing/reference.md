# Weekly Briefing - Reference

## Key Files

| File | Purpose |
|------|---------|
| `/Business_Goals.md` | Revenue targets, metrics, active projects |
| `/Accounting/*.md` | Financial transactions, invoices |
| `/Done/*.md` | Completed work for the week |
| `/Needs_Action/*.md` | Pending items, backlog |
| `/Logs/YYYY-MM-DD.json` | Activity logs for metrics |
| `Dashboard.md` | Updated with weekly summary |

## Data Sources

| Source | Data Extracted | Processing |
|--------|----------------|------------|
| `/Accounting/` | Revenue, expenses, invoices | Sum totals, categorize |
| `/Done/` | Completed tasks | Count, categorize, analyze timing |
| `/Needs_Action/` | Pending work | Count, assess age, identify delays |
| `/Logs/` | Activity patterns | Parse JSON, extract metrics |
| `/Briefings/` | Previous briefings | Compare week-over-week |

## Subscription Detection

**Patterns** to detect in transaction descriptions:
- `netflix.com` → Netflix
- `spotify.com` → Spotify
- `adobe.com` → Adobe Creative Cloud
- `notion.so` → Notion
- `slack.com` → Slack
- `openai.com` → OpenAI/ChatGPT
- `google.com` → Google services

**Alert** if:
- No login/activity in 30 days
- Price increased >20%
- Duplicate functionality detected

## Bottleneck Detection

**Indicators** to analyze:
- Task spent >3 days in Needs_Action
- Same task type consistently delayed
- Tasks moved from Plans back to Needs_Action
- Deadline dates in past

## Related Skills

- `daily-review` - Provides daily completion data
- `inbox-processor` - Feeds items to Needs_Action

## Scheduling

**Run weekly briefing:**
- **Day**: Monday morning
- **Frequency**: Weekly
- **Trigger**: Cron/scheduler or manual
- **Prerequisite**: At least 7 days of log data

## Scripts

### `scripts/generate_ceo_briefing.py`

Automated script to generate comprehensive Monday Morning CEO Briefing.

**Features:**
- Analyzes `/Business_Goals.md` for revenue targets
- Scans `/Accounting/` for financial data (placeholder)
- Parses `/Done/` folder for completed work
- Analyzes `/Logs/` for activity metrics
- Detects bottlenecks in `/Needs_Action/`
- Generates executive summary with insights

**Usage:**
```bash
# Generate briefing for last 1 week
python scripts/generate_ceo_briefing.py --vault .

# Generate for last 4 weeks
python scripts/generate_ceo_briefing.py --vault . --weeks 4

# Output to stdout (no file creation)
python scripts/generate_ceo_briefing.py --vault . --stdout
```

**Output:**
- Briefing file at `/Briefings/YYYY-MM-DD_Monday_Briefing.md`
- Console confirmation of saved location
- Structured sections: Executive Summary, Revenue, Completed Work, Bottlenecks, Activity Summary

**Briefing Sections:**
1. Executive Summary (AI-generated overview)
2. Revenue (weekly and MTD vs goals)
3. Completed Work (by category)
4. Bottlenecks (items stuck >3 days)
5. Activity Summary (actions logged by type)
6. Focus for This Week (action items)
