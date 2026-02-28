# AI Employee Agent Skills Index

**Version:** 1.1.0
**Last Updated:** 2026-01-14
**Total Skills:** 21

---

## Quick Reference

| Skill | Purpose | Tier | Status |
|-------|---------|------|--------|
| [email-manager](#email-manager) | Monitor Gmail emails | Silver | ✅ |
| [calendar-manager](#calendar-manager) | Monitor Calendar events | Silver | ✅ |
| [slack-manager](#slack-manager) | Monitor Slack messages | Silver | ✅ |
| [whatsapp-manager](#whatsapp-manager) | Monitor WhatsApp messages | Gold | ✅ |
| [filesystem-manager](#filesystem-manager) | Monitor drop folder | Bronze | ✅ |
| [xero-manager](#xero-manager) | Monitor Xero accounting | Gold | ✅ |
| [linkedin-manager](#linkedin-manager) | Post to LinkedIn | Gold | ✅ |
| [twitter-manager](#twitter-manager) | Post to Twitter/X | Gold | ✅ |
| [facebook-instagram-manager](#facebook-instagram-manager) | Post to Facebook/Instagram | Gold | ✅ |
| [approval-manager](#approval-manager) | Manage approval workflow | Gold | ✅ |
| [weekly-briefing](#weekly-briefing) | Generate CEO briefing | Gold | ✅ |
| [daily-review](#daily-review) | Generate daily plan | Silver | ✅ |
| [ralph](#ralph) | Autonomous task execution | Gold | ✅ |
| [content-generator](#content-generator) | Generate content | Silver | ✅ |
| [planning-agent](#planning-agent) | Create execution plans | Silver | ✅ |
| [social-media-manager](#social-media-manager) | Coordinate social posts | Gold | ✅ |
| [inbox-processor](#inbox-processor) | Process inbox items | Silver | ✅ |
| [business-handover](#business-handover) | CEO business audit | Gold | ✅ |
| [accounting](#accounting) | Financial reporting | Gold | ✅ |
| [skill-creator](#skill-creator) | Create new skills | Meta | ✅ |
| [docx-processor](#docx-processor) | Convert DOCX to Markdown | Silver | ✅ |

---

## Watcher Skills (Perception Layer)

### email-manager

**Purpose:** Monitor, detect, and process Gmail emails automatically using the Gmail API.

**Tier:** Silver (Required)

**Description:** Scans inbox for important emails (unread, flagged, keyword matches) and creates action files in your Obsidian vault for processing.

**Key Features:**
- API-based monitoring via Gmail API
- OAuth2 authentication
- Keyword and flag filtering
- Incremental processing (tracks processed emails)
- Human-in-the-loop (creates action files, doesn't auto-respond)

**Output:** `Needs_Action/EMAIL_*.md` files with email content and suggested actions

**Related Skills:** approval-manager, content-generator, weekly-briefing

---

### calendar-manager

**Purpose:** Monitor Google Calendar for upcoming events and meetings.

**Tier:** Silver (Required)

**Description:** Tracks upcoming calendar events, identifies meetings requiring preparation, and creates action files for events needing attention.

**Key Features:**
- Google Calendar API integration
- OAuth2 authentication
- Event filtering (by type, duration, attendees)
- Preparation reminders
- Human-in-the-loop

**Output:** `Needs_Action/EVENT_*.md` files with event details

**Related Skills:** approval-manager, weekly-briefing

---

### slack-manager

**Purpose:** Monitor Slack channels for important messages and mentions.

**Tier:** Silver (Required)

**Description:** Watches specified Slack channels for keywords, mentions, and important messages, creating action files for items requiring attention.

**Key Features:**
- Slack Bot API integration
- Bot token authentication
- Channel filtering
- Keyword detection
- Human-in-the-loop

**Output:** `Needs_Action/SLACK_*.md` files with message content

**Related Skills:** approval-manager, content-generator

---

### whatsapp-manager

**Purpose:** Monitor WhatsApp for urgent messages via Playwright automation.

**Tier:** Gold (Required)

**Description:** Uses Playwright to scan WhatsApp Web chat list for keywords (urgent, asap, invoice, payment, help), creating action files for urgent messages.

**Key Features:**
- Playwright browser automation
- Persistent browser mode
- Chat list preview scanning (fast, no clicking)
- Keyword detection
- Human-in-the-loop

**Output:** `Needs_Action/WHATSAPP_*.md` files with message content

**Related Skills:** approval-manager, content-generator

**Implementation:** `watchers/whatsapp_watcher_playwright.py`

---

### filesystem-manager

**Purpose:** Monitor a drop folder for new files and automatically create action files.

**Tier:** Bronze (Required)

**Description:** Watches a specified folder for new files, automatically copying them to `Needs_Action/` with metadata files describing the content.

**Key Features:**
- File system monitoring
- Automatic metadata generation
- Support for all file types
- Human-in-the-loop

**Output:** `Needs_Action/FILE_*.md` files with file metadata

**Related Skills:** approval-manager, inbox-processor

---

### xero-manager

**Purpose:** Monitor Xero accounting system for financial events requiring action.

**Tier:** Gold (Required)

**Description:** Monitors Xero for invoices, payments, and unusual transactions via Xero MCP server, creating action files for financial review.

**Key Features:**
- Xero MCP server integration
- OAuth2 authentication
- Overdue invoice detection (>7 days)
- Unusual expense detection (>$500)
- Payment tracking
- Human-in-the-loop

**Output:** `Accounting/INVOICE_*.md` or `XERO_*.md` files with financial details

**Related Skills:** approval-manager, accounting, weekly-briefing

**Implementation:** `watchers/xero_watcher_mcp.py` (uses Xero MCP)

---

## Social Media Skills (Action Layer)

### linkedin-manager

**Purpose:** Manage LinkedIn posting and engagement through stealth automation using CDP.

**Tier:** Gold (Required)

**Description:** Generate, approve, and publish LinkedIn posts with professional business content using fast copy-paste method (100-200x faster).

**Key Features:**
- Chrome DevTools Protocol (CDP) automation
- Fast copy-paste method (0.3s vs 30-60s)
- Professional content support
- Approval workflow
- Character limit: 3,000
- Dry run mode

**Output:** Posts to LinkedIn, generates summary in `Briefings/`

**Related Skills:** content-generator, social-media-manager, approval-manager

**Implementation:** `scripts/social-media/linkedin_poster.py`, `scripts/social-media/linkedin_approval_monitor.py`

---

### twitter-manager

**Purpose:** Manage Twitter/X posting through browser automation.

**Tier:** Gold (Required)

**Description:** Generate, approve, and publish tweets with fast copy-paste method (100-200x faster).

**Key Features:**
- Chrome DevTools Protocol (CDP) automation
- Fast copy-paste method
- Character limit: 280
- Approval workflow
- Dry run mode

**Output:** Posts to Twitter/X, generates summary in `Briefings/`

**Related Skills:** content-generator, social-media-manager, approval-manager

**Implementation:** `scripts/social-media/twitter_poster.py`, `scripts/social-media/twitter_approval_monitor.py`

---

### facebook-instagram-manager

**Purpose:** Manage Facebook and Instagram posting through browser automation.

**Tier:** Gold (Required)

**Description:** Generate, approve, and publish posts to Facebook and Instagram. Instagram auto-generates professional images with 6 color themes.

**Key Features:**
- Chrome DevTools Protocol (CDP) automation
- Instagram: Professional image generation (1080x1080, 6 themes)
- Facebook: Direct content insertion
- Approval workflow
- Dry run mode

**Output:** Posts to Facebook/Instagram, generates summary in `Briefings/`

**Related Skills:** content-generator, social-media-manager, approval-manager

**Implementation:** `scripts/social-media/facebook_poster_v2.py`, `scripts/social-media/instagram_poster_v2.py`, `scripts/social-media/meta_approval_monitor.py`

---

### social-media-manager

**Purpose:** Coordinate social media posting across multiple platforms.

**Tier:** Gold (Required)

**Description:** Orchestrates content generation and posting across LinkedIn, Twitter, Facebook, and Instagram.

**Key Features:**
- Multi-platform coordination
- Content calendar generation
- Scheduling support
- Analytics tracking
- Cross-platform optimization

**Output:** Content calendar, scheduled posts

**Related Skills:** linkedin-manager, twitter-manager, facebook-instagram-manager, content-generator

---

## Core System Skills

### approval-manager

**Purpose:** Monitor, track, and manage the human-in-the-loop approval workflow for sensitive actions.

**Tier:** Gold (Required - Critical Security Component)

**Description:** Orchestrates approval workflow from detection to execution while maintaining security and compliance. No sensitive action can execute without human approval.

**Key Features:**
- No auto-approval (always requires human)
- Traceability (all decisions logged)
- Time-based escalation
- Risk-based categories
- Audit trail
- Expiration handling (24 hours)

**Approval Categories:**
- **Email:** New contacts, bulk sends, external comms
- **Social Media:** New posts, replies, controversial topics
- **Payments:** All payments to new payees, payments >$100
- **Calendar:** Meetings with external attendees, recurring events

**Output:** Logs to `Logs/YYYY-MM-DD.json`, moves files to `Done/` or `Rejected/`

**Related Skills:** All watcher and action skills

**Implementation:** `scripts/monitors/*_approval_monitor.py` (6 approval monitors)

---

### weekly-briefing (CEO Briefing)

**Purpose:** Generate comprehensive Monday Morning CEO Briefing with business audit, performance analysis, and proactive suggestions.

**Tier:** Gold (Required - Standout Feature)

**Description:** **The standout feature** of the AI Employee system. Aggregates data from across the vault, analyzes business performance against goals, identifies trends and bottlenecks, and presents actionable insights.

**Key Features:**
- Executive-level reporting
- Data-driven insights
- Proactive suggestions
- Ralph Wiggum integration (7-task autonomous workflow)
- Performance: 10-15 minutes (vs 30-60 manual)
- Speed: 3-6x faster than manual

**Report Sections:**
1. Executive Summary
2. Revenue (this week, MTD, vs target)
3. Completed Tasks
4. Bottlenecks
5. Upcoming Deadlines
6. Proactive Suggestions (cost optimization, process improvements, opportunities)
7. Email Summary
8. Calendar Summary
9. Action Items

**Output:** `Briefings/YYYY-MM-DD_Monday_Briefing.md`, `Briefings/YYYY-MM-DD_Monday_Actions.md`

**Related Skills:** ralph, accounting, xero-manager, email-manager, calendar-manager

**Implementation:** `.claude/skills/weekly-briefing/scripts/generate_ceo_briefing.py` (executed via Ralph)

---

### ralph (Ralph Wiggum)

**Purpose:** Autonomous task execution loop that iterates through task lists until complete.

**Tier:** Gold (Required - Core Autonomy Feature)

**Description:** **The core autonomy feature** of the AI Employee system. Ralph iterates through task lists, planning and executing each task while maintaining human oversight for external actions.

**Key Features:**
- Autonomous execution (continues until all tasks complete)
- Human-in-the-loop (external actions require approval)
- Fresh context (each iteration starts clean)
- Persistent memory (state maintained via files)
- Transparent (all progress logged and inspectable)

**Workflow:**
1. Load task list (JSON format)
2. Read progress file for learnings
3. Pick highest priority incomplete task
4. Plan execution in `Plans/` folder
5. Execute using available skills/MCPs
6. Create approval request in `Pending_Approval/`
7. Wait for human approval
8. Verify execution in logs
9. Update task list (mark complete)
10. Continue to next task

**Standout Use Case:** Monday Morning CEO Briefing (7 tasks, 10-15 minutes, 3-6x faster)

**Output:** Plans, approvals, logs, completion signal

**Related Skills:** weekly-briefing, approval-manager, all watcher and action skills

**Implementation:** `.claude/skills/ralph/`, `scripts/start-ralph.sh`

---

## Supporting Skills

### daily-review

**Purpose:** Generate daily plan and review pending items.

**Tier:** Silver (Required)

**Description:** Reviews `Needs_Action/`, `Done/`, and upcoming events to create a prioritized daily plan.

**Key Features:**
- Daily task prioritization
- Upcoming deadline alerts
- Inbox triage
- Schedule optimization

**Output:** `Plans/daily_YYYY-MM-DD.md`

**Related Skills:** planning-agent, inbox-processor

---

### content-generator

**Purpose:** Generate content for emails, social posts, and documents.

**Tier:** Silver (Required)

**Description:** Creates professional content for various channels using templates and AI generation.

**Key Features:**
- Email generation
- Social media content
- Document generation
- Template-based
- AI-assisted writing

**Output:** Content in appropriate vault folders

**Related Skills:** email-manager, linkedin-manager, twitter-manager, facebook-instagram-manager

---

### planning-agent

**Purpose:** Create execution plans for complex tasks.

**Tier:** Silver (Required)

**Description:** Analyzes task requirements and creates detailed step-by-step execution plans.

**Key Features:**
- Task breakdown
- Dependency analysis
- Resource estimation
- Risk identification

**Output:** `Plans/PLAN_*.md` files with execution steps

**Related Skills:** ralph, daily-review

---

### inbox-processor

**Purpose:** Process and organize items in the inbox.

**Tier:** Silver (Required)

**Description:** Triages incoming items, categorizes them, and routes to appropriate folders.

**Key Features:**
- Automated triage
- Categorization
- Routing
- Priority assessment

**Output:** Organized items in appropriate vault folders

**Related Skills:** filesystem-manager, daily-review

---

### business-handover

**Purpose:** Generate CEO business audit and handover document.

**Tier:** Gold (Required)

**Description:** Similar to weekly-briefing but focused on business continuity and executive handover.

**Key Features:**
- Executive summary
- Business performance
- Pending items
- Action items
- Risk assessment

**Output:** `Briefings/EXECUTIVE_SUMMARY_*.md`

**Related Skills:** weekly-briefing, ralph

---

### accounting

**Purpose:** Process financial reports and accounting data.

**Tier:** Gold (Required)

**Description:** Aggregates financial data from Xero and other sources to generate reports.

**Key Features:**
- Financial aggregation
- Report generation
- Invoice tracking
- Payment monitoring

**Output:** `Accounting/` reports

**Related Skills:** xero-manager, weekly-briefing

---

### docx-processor

**Purpose:** Convert Word documents (.docx) to Markdown format.

**Tier:** Silver (Utility)

**Description:** Converts `.docx` files into clean Markdown, preserving headings, tables, bold/italic formatting, headers, and footers. Handles large documents (50+ pages).

**Key Features:**
- Full document structure preservation (headings H1-H6, tables, formatting)
- Large document support (50+ pages)
- Nested table handling
- Header/footer extraction
- Zero configuration

**Output:** `.md` files with converted content

**Related Skills:** filesystem-manager, inbox-processor, content-generator

**Implementation:** `.claude/skills/docx-processor/scripts/convert_docx_to_md.py`

---

### skill-creator

**Purpose:** Guide for creating new agent skills.

**Tier:** Meta (Tool)

**Description:** Provides instructions and templates for creating new agent skills to extend AI Employee capabilities.

**Key Features:**
- Skill creation guide
- Templates
- Best practices
- Examples

**Output:** New skill directories with SKILL.md

**Related Skills:** All skills (creates them)

---

## Skill Tier Requirements

### Bronze Tier (Minimum Viable)

**Required Skills:**
- filesystem-manager
- At least one of: email-manager, calendar-manager, slack-manager

**Capability:** Basic monitoring and action file creation

---

### Silver Tier (Functional Assistant)

**Required Skills (All Bronze plus):**
- email-manager
- calendar-manager
- At least two social media: linkedin-manager OR twitter-manager OR facebook-instagram-manager
- approval-manager
- daily-review
- content-generator
- planning-agent

**Capability:** Full monitoring, social posting, approval workflow, planning

---

### Gold Tier (Autonomous Employee)

**Required Skills (All Silver plus):**
- whatsapp-manager
- xero-manager
- linkedin-manager
- twitter-manager
- facebook-instagram-manager
- social-media-manager
- weekly-briefing
- ralph
- business-handover
- accounting

**Capability:** Cross-domain integration, full social media, accounting, CEO briefings, autonomous execution

---

## Skill Development

### Creating New Skills

1. Use the skill-creator skill for guidance
2. Create directory: `.claude/skills/your-skill/`
3. Create `SKILL.md` with YAML frontmatter
4. Optionally add: `FORMS.md`, `reference.md`, `examples.md`
5. Optionally add: `scripts/` subdirectory

### Skill SKILL.md Format

```yaml
---
name: your-skill
description: Brief description of what this skill does
license: Apache-2.0
---

# Your Skill Name

## Purpose
**Action verbs** what the skill does and why it matters.

## Design Philosophy
- Core principles
- Architecture
- Modularity

## Workflow
Step-by-step breakdown

## Integration Points
- Input sources
- Output destinations
- Related skills
```

---

## Skill Invocation

### Via Claude Code

```
# List available skills
/skills

# Invoke a skill
/skill skill-name "task description"

# Use Ralph for autonomous execution
/ralph-loop "Generate Monday CEO Briefing"
```

### Via CLI

```bash
# Run Ralph (autonomous task execution)
./scripts/start-ralph.sh 10

# Check Ralph status
./scripts/check-ralph-status.sh

# Cancel Ralph
/cancel-ralph
```

---

## Related Documentation

- **Hackathon0.md:** Overall project architecture and requirements
- **docs/ARCHITECTURE.md:** Detailed system architecture
- **CLAUDE.md:** Project instructions and usage
- **docs/RALPH_USER_GUIDE.md:** Ralph Wiggum user guide
- **docs/SOCIAL_MEDIA_GUIDE.md:** Social media posting guide

---

*AI Employee Agent Skills Index v1.1.0*
*Last Updated: 2026-01-14*
*Gold Tier 100% Complete - All 20 Skills Operational*
