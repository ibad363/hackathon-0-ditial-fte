---
name: linkedin-profile-accessor
description: Extract and analyze LinkedIn profile data with completeness scoring, strengths/weaknesses analysis, and network insights
license: Apache-2.0
---

# LinkedIn Profile Accessor

## Overview

The LinkedIn Profile Accessor skill extracts comprehensive profile data from LinkedIn, provides AI-powered analysis of profile completeness, identifies strengths and weaknesses, and delivers network insights including connection patterns and mutual connections.

This skill operates in **read-only mode** - it never modifies profiles, only extracts and analyzes data for your review.

## Key Features

- **Profile Data Extraction**: Extract name, headline, about, experience, education, skills, posts, and more
- **Completeness Analysis**: Score profiles 0-100 based on LinkedIn best practices
- **Strengths Identification**: Analyze what makes a profile stand out
- **Weaknesses Detection**: Identify gaps and areas for improvement
- **Network Insights**: Extract connection data and analyze network patterns
- **Activity Analysis**: Track posting patterns and engagement
- **Multi-Format Output**: JSON, Markdown, and CSV export options

## Capabilities

### Profile Data Extraction

The accessor can extract the following data from any LinkedIn profile:

- **Basic Info**: Name, headline, location, profile URL, connection count
- **About Section**: Full text with word count analysis
- **Experience**: Current and past positions with dates, descriptions, companies
- **Education**: Degrees, institutions, graduation years
- **Skills**: All listed skills with endorsement counts
- **Activity**: Recent posts (up to 10) with engagement metrics
- **Recommendations**: Received and given recommendations

### Profile Analysis

The accessor provides comprehensive analysis:

- **Completeness Score** (0-100):
  - Professional headline (10 points)
  - About section 300+ words (20 points)
  - Profile photo (10 points)
  - 3+ positions (25 points)
  - Education entry (10 points)
  - 10+ skills (15 points)
  - 2+ recommendations (10 points)

- **Strengths Analysis**:
  - Strong keywords and phrases
  - Complete sections
  - High engagement posts
  - Quality recommendations
  - Diverse experience

- **Weaknesses Identification**:
  - Missing sections
  - Thin content
  - Poor keywords
  - Inconsistent formatting
  - Low engagement

### Network Insights

- **Connection List**: Extract up to 100 connections with names, headlines, companies
- **Mutual Connections**: Analyze mutual connections with any profile
- **Activity Patterns**: Posting frequency, best times to post, engagement rates
- **Network Growth**: Track connection growth over time

## When to Use This Skill

Use the LinkedIn Profile Accessor when you need to:

1. **Analyze your own profile** - Get a complete picture of your LinkedIn presence
2. **Research prospects** - Understand potential clients, partners, or hires
3. **Competitive analysis** - Compare your profile against industry leaders
4. **Recruiting** - Extract candidate data for review
5. **Network mapping** - Understand connection patterns and mutual contacts
6. **Profile audit** - Before making improvements, understand current state

## Quick Start

### Analyze Your Own Profile

```bash
# Using the skill directly
cd .claude/skills/linkedin-profile-accessor
python invoke.py "your-profile-id"

# Using as a module
python -c "
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
accessor = LinkedInProfileAccessor()
data = accessor.extract_profile_data('your-profile-id', include_network=True)
print(data.summary())
"
```

### Analyze Someone Else's Profile

```bash
python invoke.py "hamdan-mohammad-922486374"
```

### Export to Different Formats

```bash
# JSON export
python .claude/skills/linkedin-profile-accessor/scripts/linkedin_profile_accessor.py \
    --profile-id "hamdan-mohammad-922486374" \
    --output "profile_data.json" \
    --format json

# Markdown report
python .claude/skills/linkedin-profile-accessor/scripts/linkedin_profile_accessor.py \
    --profile-id "hamdan-mohammad-922486374" \
    --output "profile_report.md" \
    --format markdown

# CSV export (for bulk analysis)
python .claude/skills/linkedin-profile-accessor/scripts/linkedin_profile_accessor.py \
    --profile-id "hamdan-mohammad-922486374" \
    --output "profile_data.csv" \
    --format csv
```

## Workflow

### 1. Request Profile Analysis
Create an action file or invoke the skill directly:

```bash
# Direct invocation
python invoke.py "profile-id"

# Via action file
cat > "AI_Employee_Vault/Needs_Action/LINKEDIN_PROFILE_ANALYSIS_request.md" << 'EOF'
---
type: linkedin_profile_analysis
profile_id: hamdan-mohammad-922486374
include_network: true
created: 2026-01-23T10:00:00Z
status: pending_approval
---
EOF
```

### 2. Data Extraction
The accessor:
- Connects to Chrome via CDP (port 9222)
- Navigates to the LinkedIn profile
- Extracts all visible data using multiple selector strategies
- Captures screenshots for verification

### 3. Analysis Generation
The analyzer:
- Calculates completeness score
- Identifies strengths and weaknesses
- Generates improvement suggestions
- Analyzes network patterns (if requested)

### 4. Report Creation
Results are saved to:
- `Needs_Action/LINKEDIN_PROFILE_ANALYSIS_*.md` - For review
- `AI_Employee_Vault/Logs/YYYY-MM-DD.json` - Audit trail

### 5. Review and Approve
Move to `Approved/` to trigger the builder skill for improvements:

```bash
mv AI_Employee_Vault/Needs_Action/LINKEDIN_PROFILE_ANALYSIS_*.md \
   AI_Employee_Vault/Approved/
```

## Content Guidelines

### Data Privacy

- All profile data stored locally in `AI_Employee_Vault/`
- Never share extracted data without permission
- Respect LinkedIn's Terms of Service
- Use rate limiting (3-5 second delays between requests)

### Usage Best Practices

1. **Start with your own profile** - Test the accessor on yourself first
2. **Use specific profile IDs** - Full LinkedIn profile IDs work best
3. **Enable network analysis sparingly** - It takes longer and uses more API calls
4. **Review screenshots** - Check captured screenshots for verification
5. **Keep audit logs** - All accesses are logged for compliance

## File Structure

```
.claude/skills/linkedin-profile-accessor/
├── SKILL.md                          # This file
├── FORMS.md                          # Report templates
├── reference.md                      # Technical API reference
├── examples.md                       # Usage examples
├── invoke.py                         # Main invocation script
└── scripts/
    ├── __init__.py
    ├── profile_data_models.py        # Dataclass definitions
    ├── linkedin_selectors.py         # LinkedIn CSS selectors
    ├── linkedin_helpers.py           # Utility functions
    ├── linkedin_profile_accessor.py  # Core accessor logic
    ├── linkedin_profile_analyzer.py  # Analysis engine
    ├── linkedin_network_analyzer.py  # Network insights
    └── linkedin_accessor_monitor.py  # Approval workflow monitor
```

## Integration with Other Skills

### LinkedIn Profile Builder
After analysis, use the Builder skill to generate improvements:

```bash
# The Builder uses the Accessor's analysis
cd .claude/skills/linkedin-profile-builder
python invoke.py "profile-id" "target-role"
```

### LinkedIn Manager
The existing LinkedIn Manager skill handles posting content:

```bash
# Post about your profile improvements
/skill linkedin-manager
```

### Research LinkedIn Generator
Combine with research to generate profile-optimized content:

```bash
/skill research-linkedin-generator
```

## Technical Details

### Chrome CDP Connection

The accessor uses Chrome DevTools Protocol on port 9222:

```python
CDP_ENDPOINT = "http://127.0.0.1:9222"

browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
context = browser.contexts[0]
page = context.pages[0]
```

**Prerequisites:**
- Chrome must be running with CDP enabled
- Use `START_AUTOMATION_CHROME.bat` or run:
  ```bash
  chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\User\ChromeAutomationProfile"
  ```
- User must be logged into LinkedIn in that Chrome session

### Selector Strategy

The accessor uses multiple selector fallbacks for robustness:

```python
PROFILE_SELECTORS = {
    'name': ['h1.text-heading-xlarge', 'h1', '[data-anonymize="person-name"]'],
    'headline': ['div.text-body-medium.break-words', '.text-body-medium', '.headline'],
    # ... more selectors with fallbacks
}
```

### Data Models

All extracted data uses Pydantic models for validation:

```python
@dataclass
class ProfileData:
    profile_id: str
    name: str
    headline: str
    location: Optional[str]
    about: Optional[str]
    experience: List[ExperienceItem]
    education: List[EducationItem]
    skills: List[SkillItem]
    posts: List[PostItem]
    connections_count: Optional[int]
    profile_url: str
    extracted_at: datetime
    completeness_score: Optional[int] = None
```

### Error Handling

The accessor uses the existing error recovery system:

```python
from watchers.error_recovery import with_retry, ErrorCategory

@with_retry(max_attempts=3, base_delay=2, max_delay=60, category=ErrorCategory.NETWORK)
def navigate_to_profile(self, profile_id: str) -> Page:
    # Retry with exponential backoff
    pass
```

### Audit Logging

All profile accesses are logged:

```python
from utils.audit_logging import AuditLogger, EventType

audit_logger = AuditLogger(self.vault_path)
audit_logger.log_action(
    action_type="profile_extraction",
    target=profile_id,
    parameters={"include_network": True},
    result="success"
)
```

## Troubleshooting

### Chrome Not Connected

**Problem:** `Error: Could not connect to Chrome on port 9222`

**Solution:**
```bash
# Start Chrome with CDP
scripts/social-media/START_AUTOMATION_CHROME.bat

# Or manually:
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\User\ChromeAutomationProfile"
```

### Not Logged Into LinkedIn

**Problem:** Extracted data is empty or contains "Sign in" text

**Solution:** Open the Chrome automation window and log into LinkedIn manually. The accessor uses your existing session.

### Selectors Not Found

**Problem:** `Error: Could not find element with selector`

**Solution:** LinkedIn frequently changes their selectors. The accessor uses multiple fallbacks, but you may need to update `linkedin_selectors.py` with new selectors.

### Rate Limiting

**Problem:** LinkedIn shows "You've reached the limit"

**Solution:** The accessor has built-in rate limiting (3-5 second delays). If you still hit limits, increase the delay in `linkedin_helpers.py`:

```python
PROFILE_ACCESS_DELAY = 5  # Increase to 10 or more
```

### Network Analysis Not Working

**Problem:** `include_network=True` but no connection data extracted

**Solution:** Network analysis requires additional navigation and may fail if:
- The profile has no connections visible
- You're not connected to the profile
- LinkedIn has restricted access

## Security Considerations

1. **Read-Only Access**: The accessor never modifies profiles, only reads data
2. **Local Storage**: All data stored locally in the vault
3. **Audit Trail**: All accesses logged to `Logs/YYYY-MM-DD.json`
4. **Rate Limiting**: Built-in delays to avoid LinkedIn rate limits
5. **CDP Localhost**: Chrome connection only on localhost:9222 (not exposed to network)
6. **Approval Required**: Actions require human approval via workflow

## Future Enhancements

- **Competitor Benchmarking**: Compare profiles against industry leaders
- **Bulk Profile Analysis**: Analyze multiple profiles at once
- **Historical Tracking**: Track profile changes over time
- **Skill Gap Analysis**: Identify missing skills for target roles
- **Salary Insights**: Estimate salary range based on profile
- **Job Matching**: Match profiles to job descriptions

## Related Documentation

- [LinkedIn Profile Builder](.claude/skills/linkedin-profile-builder/SKILL.md) - Generate profile improvements
- [LinkedIn Manager](.claude/skills/linkedin-manager/SKILL.md) - Post to LinkedIn
- [Chrome CDP Helper](scripts/chrome_cdp_helper.py) - Chrome automation utilities
- [Error Recovery](watchers/error_recovery.py) - Retry and circuit breaker patterns
- [Audit Logging](utils/audit_logging.py) - Logging system

---
*Last Updated: 2026-01-23*
*Version: 1.0.0*
