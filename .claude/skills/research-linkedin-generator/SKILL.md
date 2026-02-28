# Auto-Research LinkedIn Generator Skill

## Overview

This skill enables the AI Employee to autonomously research any topic and generate professional LinkedIn posts through a multi-stage process with human-in-the-loop approval.

## What's New in v2.0

### 🔬 Deep Research Mode
- **3-Level Research Methodology**: Surface articles → Documentation → Library/Package analysis
- **GitHub Repository Analysis**: Extracts stars, forks, language, topics for code libraries
- **Package Manager Integration**: Analyzes PyPI, NPM, crates.io packages
- **Technology Stack Detection**: Identifies frameworks, libraries, and tools
- **Enhanced Content**: Posts include library insights and technical context

### Bug Fixes
- Added UTF-8 encoding to all file operations
- Added `from __future__ import annotations` for type hints
- Fixed type hints throughout codebase
- Added proper error handling for JSON parsing
- Fixed division by zero issues

## Skill Metadata

```yaml
name: research-linkedin-generator
version: 2.0.0
author: AI Employee
description: Multi-level research and generate professional LinkedIn posts with approval workflow
```

---

## Instruction for Claude Code

You are the **Research & LinkedIn Content Generator** for the AI Employee system. Your task is to transform any research topic into a professional, well-sourced LinkedIn post.

## Workflow Overview

```
User Request → Research (3 Levels) → Extract → Analyze → Draft → Approval → Post
```

### Phase 1: Research (Browser Automation)

**Input**: Topic/term from user
**Tool**: `playwright` (mcp__playwright__*)

**Steps**:
1. Navigate to Google Search: `mcp__playwright__browser_navigate(url="https://google.com")`
2. Search for topic: `mcp__playwright__browser_type` the search query
3. Wait for results: `mcp__playwright__browser_wait_for` selector to load
4. Take snapshot: `mcp__playwright__browser_snapshot`
5. Extract top 8-10 results from snapshot (look for result links)

**Output**: Save research to `AI_Employee_Vault/Plans/RESEARCH_{topic}_{timestamp}.md`

```markdown
---
type: research
topic: {topic}
status: research_complete
created: {timestamp}
---

# Research Results for: {topic}

## Sources Found
1. [{Title}]({URL}) - {Domain} - {Snippet}
2. [{Title}]({URL}) - {Domain} - {Snippet}
...

## Next Steps
- [ ] Visit each source
- [ ] Extract content
- [ ] Analyze findings
- [ ] Generate LinkedIn post
```

### Phase 2: Content Extraction

**For each source URL**:

1. Navigate to URL: `mcp__playwright__browser_navigate(url={source_url})`
2. Wait for page load: `mcp__playwright__browser_wait_for(time=3)`
3. Get page text: `mcp__playwright__browser_evaluate(function="() => document.body.innerText")`
4. Check for paywalls: Look for "subscribe", "premium", "paywall" in text
5. Extract main content:
   - Remove navigation, footer, ads
   - Extract article body (look for `<article>`, `main`, or content divs)
   - Get author, date, headline

**Quality Checks**:
- Content length > 500 words?
- Paywall detected? → Skip to next source
- Language is English? → Continue, else skip
- Ads < 5% of content? → Continue

**Update research file** with extracted content.

### Phase 3: Analysis & Synthesis

**Read all extracted content** from research file and:

1. **Identify Common Themes**: What do 3+ sources agree on?
2. **Extract Statistics**: Numbers, percentages with exact quotes
3. **Find Expert Quotes**: Verbatim quotes with author names
4. **Note Contradictions**: Where do sources disagree?
5. **Assess Credibility**: Cross-reference claims

**Create summary** in research file:

```markdown
## Key Insights
- {Theme 1} (Source A, B, C agree)
- {Theme 2} (Source A, D agree)
- {Theme 3} (Source B disagrees)

## Statistics Found
- "{Stat}" — {Source}, {Date}
- "{Stat}" — {Source}, {Date}

## Expert Quotes
> "{Quote}" — {Author}, {Publication}

## Credibility Assessment
- {Overall assessment}
```

### Phase 4: LinkedIn Post Generation

**Generate post** following this structure:

```markdown
{Hook - Question or surprising statistic}

{Paragraph 1: Context - what's happening and why it matters}

{Paragraph 2: Key insight or data point with source}

{Paragraph 3: Actionable takeaway or recommendation}

{Call to Action: Question to engage audience}

{Hashtags - 5-10 relevant tags}
```

**Post Requirements**:
- Length: 1,000-2,000 characters
- Tone: Professional, conversational, authoritative
- Grade level: 8-12 (Flesch-Kincaid)
- No filler words: "very", "really", "just"
- Statistics must have inline citations: `According to {Source}...`
- Quotes use blockquotes with attribution
- 0-2 emojis maximum (for professional tone)
- Hashtags mix: `#BroadTopic #SpecificTerm`

### Phase 5: Approval Workflow

**Create approval file** with `status: pending` (auto-approver will route to `Pending_Approval/`):

```markdown
---
type: linkedin_post
action: post_to_linkedin
platform: linkedin
created: {timestamp}
expires: {expires_24h_later}
status: pending
topic: {topic}
research_sources: {count}
---

# LinkedIn Post: {Topic}

## Post Content
{Full generated post}

## Research Summary
**Sources Analyzed**: {count}
**Key Themes**: {theme1}, {theme2}, {theme3}
**Statistics Cited**: {count}

## Sources
1. [{Title}]({URL}) - {Domain}
2. [{Title}]({URL}) - {Domain}

## Approval Required
This post will be published to LinkedIn when approved.

**To Approve**: Move this file to `AI_Employee_Vault/Approved/`

**To Reject**: Move this file to `AI_Employee_Vault/Rejected/`

**To Edit**: Edit content above, then move to `Approved/`
```

**Workflow**: File created → Auto-approver moves to `Pending_Approval/` → User reviews → Move to `Approved/` → Posted

**Notify user**: "LinkedIn post ready for review. Check `Pending_Approval/` folder."

---

## Vault Integration

### Folder Structure

```
AI_Employee_Vault/
├── Inbox/
│   └── RESEARCH_REQUEST_{topic}.md          # User requests
├── Plans/
│   └── RESEARCH_{topic}_{timestamp}.md       # Research data
├── Needs_Action/
│   └── LINKEDIN_POST_{timestamp}_{slug}.md  # Initial creation (status: pending)
├── Pending_Approval/
│   └── LINKEDIN_POST_{timestamp}_{slug}.md  # Auto-approver moves here
├── Approved/
│   └── LINKEDIN_POST_{timestamp}_{slug}.md  # Ready to post
├── Rejected/
│   └── LINKEDIN_POST_{timestamp}_{slug}.md  # Declined posts
└── Done/
    ├── LINKEDIN_POST_{timestamp}_{slug}.md  # Completed
    └── LINKEDIN_POST_SUMMARY_{timestamp}.md # Post analytics
```

### File Naming Convention

- Research requests: `RESEARCH_REQUEST_{YYYYMMDD}_{topic_slug}.md`
- Research data: `RESEARCH_{topic_slug}_{YYYYMMDD_HHMMSS}.md`
- Posts: `LINKEDIN_POST_{YYYYMMDD_HHMMSS}_{topic_slug}.md`
- Summaries: `LINKEDIN_POST_SUMMARY_{YYYYMMDD_HHMMSS}.md`

---

## MCP Tools Available

### Browser (Playwright)
- `mcp__playwright__browser_navigate(url)` - Navigate to URL
- `mcp__playwright__browser_type(element, text)` - Type text
- `mcp__playwright__browser_click(element, ref)` - Click element
- `mcp__playwright__browser_snapshot(filename)` - Get page snapshot
- `mcp__playwright__browser_evaluate(function)` - Run JavaScript
- `mcp__playwright__browser_wait_for(time)` - Wait for time

### Filesystem
- `mcp__playwright__filesystem.write_file(path, content)` - Write file
- `mcp__playwright__filesystem.read_file(path)` - Read file
- `mcp__playwright__filesystem.list_directory(path)` - List folder

---

## Execution Commands

### Start Research
```bash
User: "Research 'generative AI in healthcare' and create a LinkedIn post"

AI responds by:
1. Creating research request in Inbox/
2. Starting browser automation
3. Visiting Google and extracting results
4. Processing each source
5. Generating LinkedIn post
6. Creating approval file in Pending_Approval/
```

### Manual Trigger
```bash
# Create research request manually
cat > "AI_Employee_Vault/Inbox/RESEARCH_REQUEST_$(date +%Y%m%d).md" << 'EOF'
---
type: research_request
action: research_and_linkedin_post
topic: AI trends 2024
created: $(date -Iseconds)
---

Please research this topic and create a professional LinkedIn post.
EOF
```

---

## Quality Standards

### Research Phase
- Minimum 5 relevant sources found
- Maximum 2 sources skipped (paywalls, low quality)
- All sources from past 30 days (unless specified otherwise)
- Domain authority check (prioritize .edu, reputable news)

### Content Extraction
- Clean text without HTML tags
- Author names extracted
- Publication dates identified
- Main content separated from navigation/ads

### Post Generation
- No hallucinated statistics (all cited)
- No copyrighted text reproduced verbatim
- Professional tone maintained
- Readability score 60+ (Flesch-Kincaid)
- Character count 1,000-2,000
- Hashtag relevance to topic

### Approval Workflow
- File created in Pending_Approval/
- Contains full post + research metadata
- Expires after 24 hours
- Clear approval instructions included

---

## Error Handling

| Error | Action |
|-------|--------|
| Google blocked | Wait 60s, retry with different queries |
| Paywall detected | Skip source, log in research file |
| Low content quality | Skip source, continue to next |
| No results found | Broaden search query, try again |
| Browser crash | Restart browser, resume from last source |
| Generation timeout | Save progress, notify user for manual review |

---

## Example Session

```
USER: Research "Claude Code" and make a LinkedIn post

AI: I'll research "Claude Code" and create a professional LinkedIn post.

[Phase 1: Research]
✓ Navigated to Google
✓ Searched for "Claude Code"
✓ Found 8 relevant sources
✓ Saved to Plans/RESEARCH_claude_code_20260120.md

[Phase 2: Extraction]
✓ Extracted content from anthropic.com (1,247 words)
✓ Extracted content from medium.com (892 words)
✓ Skipped paywalled article on wsj.com
✓ Extracted content from dev.to (1,102 words)
... (processing all sources)

[Phase 3: Analysis]
✓ Identified 3 common themes
✓ Extracted 5 statistics
✓ Found 2 expert quotes

[Phase 4: Post Generation]
✓ Generated 1,847 character LinkedIn post
✓ Added 7 hashtags
✓ Cited 3 sources

[Phase 5: Approval]
✓ Created approval file
→ Pending_Approval/LINKEDIN_POST_20260120_143000_claude_code.md

📋 LinkedIn post ready for review!

The post includes:
- Hook: "Did you know AI pair programming is now a reality?"
- Key insights from 8 sources
- 2 statistics with citations
- 7 relevant hashtags
- Call to action for comments

Check Pending_Approval/ folder to approve, edit, or reject.

USER: [Moves file to Approved/]

MONITOR: [Detects approved file, posts to LinkedIn]

✓ Posted successfully to LinkedIn!
✓ Moved to Done/
✓ Created summary: Done/LINKEDIN_POST_SUMMARY_20260120_143105.md
```

---

## Configuration

```yaml
research:
  max_sources: 10
  min_content_length: 500
  date_filter_days: 30
  skip_domains:
    - ads.*
    - *.sponsored
  preferred_domains:
    - medium.com
    - dev.to
    - towardsdatascience.com
    - anthropic.com

post:
  min_characters: 1000
  max_characters: 2000
  min_hashtags: 5
  max_hashtags: 10
  max_emojis: 2
  tone: professional_conversational

approval:
  expires_hours: 24
  auto_approve: false  # Always require human review
  edit_allowed: true
```

---

## Dependencies

### Required
- Python playwright for browser automation
- trafilatura for content extraction
- GLM-4.7 for text generation
- MCP servers: playwright, filesystem

### Optional (for Deep Research Mode)
- requests: HTTP client for API calls
- beautifulsoup4: HTML parsing for documentation extraction
- json: For JSON parsing (built-in)

Install optional dependencies:
```bash
pip install requests beautifulsoup4
```

---

## Integration with AI Employee

This skill integrates with existing AI Employee components:

1. **Watchers**: None needed (manual trigger via Inbox)
2. **Approval Monitor**: linkedin-approval-monitor detects Approved/ files
3. **MCP Servers**: playwright (browser), filesystem (file ops)
4. **Vault**: Uses standard folder structure
5. **Human-in-the-Loop**: Pending_Approval workflow enforced

---

## 🔬 Deep Research Mode

### Overview

Deep Research Mode goes beyond surface-level article scraping to provide comprehensive multi-level research:

**Level 1: Surface Research**
- Extract content from articles and blog posts
- Get publication metadata (authors, dates, publications)
- Identify key themes and statistics

**Level 2: Documentation Research**
- Find official documentation sites
- Extract API references and guides
- Identify getting started materials
- Collect tutorial and guide content

**Level 3: Library/Package Research**
- Analyze GitHub repositories (stars, forks, language, topics)
- Extract package information (PyPI, NPM, crates.io, etc.)
- Identify dependencies and version history
- Assess community activity and code quality

### Technology Stack Detection

Deep research automatically identifies:
- **Programming Languages**: Python, JavaScript, Rust, Go, etc.
- **Frameworks**: React, Vue, Django, Flask, Express, etc.
- **Libraries**: pandas, numpy, tensorflow, etc.
- **Tools**: Docker, Kubernetes, Git, etc.

### Enhanced Post Generation

Posts created with Deep Research include:
- Standard article analysis
- GitHub repository insights (stars, language, activity)
- Package version information
- Technology stack overview
- Multiple source types (articles, docs, repos)

### Usage

#### Command Line

```bash
# Standard research
python scripts/research.py --topic "Rust programming" --process-topic

# Deep research (all 3 levels)
python scripts/research.py --topic "Rust programming" --deep-research --depth 3

# Deep research (documentation only - levels 1-2)
python scripts/research.py --topic "Rust programming" --deep-research --depth 2

# Deep research with provided URLs
python scripts/research.py --topic "Rust programming" --deep-research --urls "https://www.rust-lang.org/,https://github.com/rust-lang/rust"
```

#### From Python API

```python
from scripts.research import ResearchLinkedInGenerator

generator = ResearchLinkedInGenerator()

# Standard research
generator._process_research("AI in healthcare", None)

# Deep research
approval = generator.process_deep_research("Rust programming", max_depth=3)

if approval:
    print(f"Deep research complete! Review at: {approval}")
```

### Deep Research Output

Posts created with deep research have enhanced metadata:

```markdown
---
type: linkedin_post
research_type: deep_research
research_depth: 3
---

## Technology Stack Identified

### Technologies
  - rust
  - ownership
  - type-safety

### Frameworks
  - tokio
  - async-std

### Libraries & Tools
  - cargo
  - clippy

## GitHub Repositories Analyzed
  - [rust-lang/rust](https://github.com/rust-lang/rust) - 85000 ⭐, Rust
  - [tokio-rs/tokio](https://github.com/tokio-rs/tokio) - 23000 ⭐, Rust

## Package References
  - [serde](https://crates.io/crates/serde) - crates.io
  - [clippy](https://github.com/rust-lang/rust-clippy) - GitHub
```

---

## Success Metrics

- Research completes in <3 minutes
- At least 5 relevant sources found
- Post generation completes in <30 seconds
- Posts approved >80% of time
- Posts generate >5% engagement rate
- Zero copyright violations
