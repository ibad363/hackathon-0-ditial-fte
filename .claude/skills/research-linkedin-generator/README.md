# Research LinkedIn Generator - AI Employee Skill

Automatically research any topic and generate professional LinkedIn posts with full approval workflow.

## Quick Start

### Option 1: Direct Command
```
User: "Research 'AI in manufacturing 2024' and create a LinkedIn post"
```

### Option 2: Inbox Request
Create a file in `AI_Employee_Vault/Inbox/`:
```bash
cat > "AI_Employee_Vault/Inbox/RESEARCH_REQUEST_$(date +%Y%m%d_%H%M%S).md" << 'EOF'
---
type: research_request
action: research_and_linkedin_post
topic: Generative AI trends for small business
created: 2026-01-20T22:00:00Z
---

Research this topic and create a professional LinkedIn post summarizing key insights.
EOF
```

## Workflow

```
Request → Research (Google) → Extract (8-10 sources) → Analyze → Draft Post → Approval → Publish
```

## What Happens

1. **Research Phase** (2-3 min)
   - Opens Chrome (CDP on port 9222)
   - Searches Google for your topic
   - Filters by past 30 days
   - Extracts top 8-10 results

2. **Extraction Phase** (3-5 min)
   - Visits each source URL
   - Extracts clean text (no HTML)
   - Skips paywalls and low-quality content
   - Saves statistics, quotes, themes

3. **Analysis Phase** (30 sec)
   - Identifies common themes
   - Extracts statistics with citations
   - Finds expert quotes
   - Assesses credibility

4. **Post Generation** (30 sec)
   - Creates 1,000-2,000 character LinkedIn post
   - Includes hook, body, CTA, hashtags
   - Cites all sources

5. **Approval** (Manual)
   - File created with `status: pending` in `Needs_Action/`
   - Auto-approver moves to `Pending_Approval/` (marks as manual review)
   - You review, edit, or reject
   - Move to `Approved/` to publish

6. **Publishing** (Automatic)
   - linkedin-approval-monitor detects approved file
   - Posts to LinkedIn via Chrome automation
   - Moves to `Done/` with summary

## Output Example

**File**: `Pending_Approval/LINKEDIN_POST_20260120_143000_ai_manufacturing.md`

```markdown
---
type: linkedin_post
action: post_to_linkedin
platform: linkedin
created: 2026-01-20T14:30:00Z
expires: 2026-01-21T14:30:00Z
status: pending
topic: AI in manufacturing 2024
research_sources: 8
---

# LinkedIn Post: AI in Manufacturing 2024

## Post Content

🏭 Manufacturing is getting smarter thanks to AI.

A new McKinsey report shows 67% of manufacturers have implemented AI in at least one process, up from 45% last year. The shift is real.

**Key applications:**
• Predictive maintenance (reduces downtime by 35%)
• Quality control (defect detection 99.2% accurate)
• Supply chain optimization (inventory costs down 22%)

According to Deloitte's 2024 survey, manufacturers using AI report 15% higher productivity than competitors.

The opportunity? Start small with predictive maintenance—biggest ROI, lowest risk.

What's your experience with AI in manufacturing? 👇

#AI #Manufacturing #Industry40 #Automation #Innovation

## Research Summary
**Sources Analyzed**: 8
**Key Themes**: Predictive maintenance, quality control, ROI
**Statistics Cited**: 3

## Sources
1. [McKinsey: AI in Manufacturing 2024](mckinsey.com) - mckinsey.com
2. [Deloitte Manufacturing Survey](deloitte.com) - deloitte.com
3. [MIT Technology Review](technologyreview.com) - technologyreview.com
... (5 more sources)

## Approval Required
This post will be published to LinkedIn when approved.

**To Approve**: Move to `AI_Employee_Vault/Approved/`
**To Reject**: Move to `AI_Employee_Vault/Rejected/`
**To Edit**: Edit above, then move to `Approved/`
```

## Requirements

- **Chrome automation** must be running (`START_AUTOMATION_CHROME.bat`)
- **Linked in** to LinkedIn in the automation window
- **Playwright MCP** server configured in Claude Code
- **GLM-4.7** available for text generation

## Troubleshooting

**Browser fails to start**:
```bash
# Make sure Chrome automation is running
scripts/social-media/START_AUTOMATION_CHROME.bat
```

**No search results**:
- Try broader topic
- Remove quotes from search terms
- Check internet connection

**Extraction fails**:
- Paywalled content is automatically skipped
- Low-quality sources are skipped
- At least 3 good sources are required

**Post not generated**:
- Check GLM-4.7 API key is configured
- Ensure at least 500 words of content extracted
- Review research file in `Plans/`

## Files Created

| Phase | Folder | File Pattern |
|-------|--------|--------------|
| Request | Inbox/ | RESEARCH_REQUEST_*.md |
| Research | Plans/ | RESEARCH_{topic}_*.md |
| Initial | Needs_Action/ | LINKEDIN_POST_*.md (status: pending) |
| Approval | Pending_Approval/ | LINKEDIN_POST_*.md (after auto-approver) |
| Published | Done/ | LINKEDIN_POST_*.md |
| Summary | Done/ | LINKEDIN_POST_SUMMARY_*.md |

## Configuration

Edit skill settings in `SKILL.md`:

```yaml
research:
  max_sources: 10              # How many sources to analyze
  min_content_length: 500      # Min words per article
  date_filter_days: 30         # How recent articles

post:
  min_characters: 1000         # Min post length
  max_characters: 2000         # Max post length
  max_emojis: 2                # Professional tone
```
