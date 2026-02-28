# LinkedIn Profile Accessor - Technical Reference

This document provides detailed technical information about the LinkedIn Profile Accessor skill.

---

## API Reference

### LinkedInProfileAccessor Class

**Location:** `scripts/linkedin_profile_accessor.py`

#### Constructor

```python
LinkedInProfileAccessor(
    vault_path: str | Path = "AI_Employee_Vault",
    cdp_endpoint: str = "http://127.0.0.1:9222",
    timeout: int = 30000,
    headless: bool = False
)
```

**Parameters:**
- `vault_path`: Path to the Obsidian vault (default: "AI_Employee_Vault")
- `cdp_endpoint`: Chrome DevTools Protocol endpoint (default: "http://127.0.0.1:9222")
- `timeout`: Page load timeout in milliseconds (default: 30000)
- `headless`: Whether to run headless (default: False)

**Example:**
```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor

accessor = LinkedInProfileAccessor(
    vault_path="AI_Employee_Vault",
    cdp_endpoint="http://127.0.0.1:9222"
)
```

#### Methods

##### connect_to_chrome()

```python
async def connect_to_chrome(self) -> Browser
```

Connects to Chrome via CDP and returns a Browser instance.

**Returns:** `playwright.async_api.Browser`

**Raises:**
- `ConnectionError`: If Chrome is not running on port 9222

**Example:**
```python
browser = await accessor.connect_to_chrome()
```

##### navigate_to_profile()

```python
async def navigate_to_profile(self, profile_id: str, page: Page) -> None
```

Navigates to a LinkedIn profile page.

**Parameters:**
- `profile_id`: LinkedIn profile ID (e.g., "hamdan-mohammad-922486374")
- `page`: Playwright Page instance

**Example:**
```python
await accessor.navigate_to_profile("hamdan-mohammad-922486374", page)
```

##### extract_profile_data()

```python
async def extract_profile_data(
    self,
    profile_id: str,
    include_posts: bool = True,
    post_limit: int = 10,
    include_network: bool = False
) -> ProfileData
```

Extracts all available profile data.

**Parameters:**
- `profile_id`: LinkedIn profile ID
- `include_posts`: Whether to extract recent posts (default: True)
- `post_limit`: Maximum number of posts to extract (default: 10)
- `include_network`: Whether to extract network data (default: False)

**Returns:** `ProfileData` dataclass

**Example:**
```python
data = await accessor.extract_profile_data(
    "hamdan-mohammad-922486374",
    include_posts=True,
    post_limit=10,
    include_network=False
)
print(f"Name: {data.name}")
print(f"Headline: {data.headline}")
```

##### extract_posts()

```python
async def extract_posts(self, page: Page, limit: int = 10) -> list[PostItem]
```

Extracts recent posts from the profile activity section.

**Parameters:**
- `page`: Playwright Page instance (must be on profile page)
- `limit`: Maximum number of posts to extract

**Returns:** List of `PostItem` dataclass instances

##### extract_connections()

```python
async def extract_connections(self, page: Page, limit: int = 100) -> list[ConnectionItem]
```

Extracts connection data from the network page.

**Parameters:**
- `page`: Playwright Page instance (must be on network page)
- `limit`: Maximum number of connections to extract

**Returns:** List of `ConnectionItem` dataclass instances

##### save_profile_report()

```python
def save_profile_report(
    self,
    profile_data: ProfileData,
    output_path: str | Path,
    format: str = "markdown"
) -> Path
```

Saves profile data to a report file.

**Parameters:**
- `profile_data`: ProfileData instance from extract_profile_data()
- `output_path`: Output file path
- `format`: Output format ("markdown", "json", or "csv")

**Returns:** Path to saved file

**Example:**
```python
data = await accessor.extract_profile_data("profile-id")
report_path = accessor.save_profile_report(
    data,
    "AI_Employee_Vault/Needs_Action/LINKEDIN_PROFILE_ANALYSIS_test.md",
    format="markdown"
)
```

---

### LinkedInProfileAnalyzer Class

**Location:** `scripts/linkedin_profile_analyzer.py`

#### Constructor

```python
LinkedInProfileAnalyzer(vault_path: str | Path = "AI_Employee_Vault")
```

#### Methods

##### analyze_completeness()

```python
def analyze_completeness(self, profile_data: ProfileData) -> CompletenessScore
```

Calculates profile completeness score (0-100).

**Returns:** `CompletenessScore` dataclass with:
- `total_score`: Overall score (0-100)
- `breakdown`: Dictionary of section scores
- `missing_sections`: List of missing sections

**Scoring Breakdown:**
- Professional headline: 10 points
- About section (300+ words): 20 points
- Profile photo: 10 points
- 3+ positions: 25 points
- Education entry: 10 points
- 10+ skills: 15 points
- 2+ recommendations: 10 points

##### identify_strengths()

```python
def identify_strengths(self, profile_data: ProfileData) -> list[str]
```

Identifies profile strengths.

**Returns:** List of strength descriptions

**Example:**
```python
strengths = analyzer.identify_strengths(data)
# ["Strong professional headline with clear value proposition",
#  "Comprehensive experience section with 5+ positions",
#  "Well-written about section (450 words)"]
```

##### identify_weaknesses()

```python
def identify_weaknesses(self, profile_data: ProfileData) -> list[str]
```

Identifies profile weaknesses.

**Returns:** List of weakness descriptions

**Example:**
```python
weaknesses = analyzer.identify_weaknesses(data)
# ["No profile photo detected",
#  "Only 3 skills listed (recommend 10+)",
#  "No recommendations received"]
```

##### generate_improvements()

```python
def generate_improvements(self, profile_data: ProfileData) -> list[Suggestion]
```

Generates prioritized improvement suggestions.

**Returns:** List of `Suggestion` dataclass instances with:
- `priority`: "High", "Medium", or "Low"
- `title`: Short title
- `description`: Detailed description
- `impact`: Expected impact

##### generate_analysis_report()

```python
def generate_analysis_report(
    self,
    profile_data: ProfileData
) -> AnalysisReport
```

Generates complete analysis report.

**Returns:** `AnalysisReport` dataclass

---

### LinkedInNetworkAnalyzer Class

**Location:** `scripts/linkedin_network_analyzer.py`

#### Methods

##### extract_connections()

```python
async def extract_connections(
    self,
    profile_id: str,
    limit: int = 100
) -> list[ConnectionItem]
```

Extracts connection list from profile.

##### analyze_mutual_connections()

```python
def analyze_mutual_connections(
    self,
    connections: list[ConnectionItem],
    target_profile: str
) -> NetworkInsights
```

Analyzes mutual connections with a target profile.

##### analyze_activity_patterns()

```python
def analyze_activity_patterns(self, posts: list[PostItem]) -> ActivityReport
```

Analyzes posting patterns and engagement.

---

## Data Models

**Location:** `scripts/profile_data_models.py`

### ProfileData

```python
@dataclass
class ProfileData:
    profile_id: str
    name: str
    headline: str
    location: Optional[str] = None
    about: Optional[str] = None
    about_word_count: int = 0
    experience: list[ExperienceItem] = field(default_factory=list)
    education: list[EducationItem] = field(default_factory=list)
    skills: list[SkillItem] = field(default_factory=list)
    posts: list[PostItem] = field(default_factory=list)
    recommendations: list[RecommendationItem] = field(default_factory=list)
    connections_count: Optional[int] = None
    profile_url: str = ""
    profile_photo_url: Optional[str] = None
    has_photo: bool = False
    extracted_at: datetime = field(default_factory=datetime.now)
    completeness_score: Optional[int] = None
    screenshot_path: Optional[str] = None
```

### ExperienceItem

```python
@dataclass
class ExperienceItem:
    title: str
    company: str
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    company_url: Optional[str] = None
```

### EducationItem

```python
@dataclass
class EducationItem:
    school: str
    degree: str
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    graduation_year: Optional[int] = None
```

### SkillItem

```python
@dataclass
class SkillItem:
    name: str
    endorsements: int = 0
```

### PostItem

```python
@dataclass
class PostItem:
    text: str
    date: str
    reactions: int = 0
    comments: int = 0
    reposts: int = 0
    url: Optional[str] = None
```

### ConnectionItem

```python
@dataclass
class ConnectionItem:
    name: str
    headline: str
    company: Optional[str] = None
    mutual: int = 0
    url: Optional[str] = None
```

---

## LinkedIn Selectors

**Location:** `scripts/linkedin_selectors.py`

### Profile Selectors

```python
PROFILE_SELECTORS = {
    'name': [
        'h1.text-heading-xlarge',
        'h1',
        '[data-anonymize="person-name"]',
        '.pv-text-details__left-panel h1'
    ],
    'headline': [
        'div.text-body-medium.break-words',
        '.text-body-medium',
        '.headline',
        '.pv-text-details__left-panel .text-body-medium'
    ],
    'location': [
        'span.text-body-small.inline.t-black--light',
        '.pv-text-details__left-panel .text-body-small',
        '.mt2.relative .text-body-small'
    ],
    'about': [
        'div.display-flex.ph5.pv-about__summary-text',
        '.pv-about__summary-text',
        '.pv-about-section',
        '#about ~ div div'
    ],
    'connections': [
        'span.t-black--light',
        '.pv-top-card--list-bullet li span',
        '.pv-top-card--list-bullet li'
    ],
    'profile_photo': [
        'img.pv-top-card-profile-picture__image',
        '.pv-top-card-profile-picture img',
        'img.profile-photo-edit__preview'
    ]
}
```

### Section Selectors

```python
SECTION_SELECTORS = {
    'experience': [
        '#experience',
        '.pv-profile-section__card-item-v2',
        '[data-section="experience"]',
        'section[aria-labelledby="experience"]'
    ],
    'education': [
        '#education',
        '.pv-profile-section__card-item-v2',
        '[data-section="education"]',
        'section[aria-labelledby="education"]'
    ],
    'skills': [
        '#skills',
        '.pv-skill-category-entity__name',
        '[data-section="skills"]',
        'section[aria-labelledby="skills"]'
    ],
    'recommendations': [
        '#recommendations',
        '.pv-recommendation-entity',
        '[data-section="recommendations"]'
    ],
    'activity': [
        '#activity',
        '.occludable-update',
        '[data-section="activity"]',
        '.pv-recent-activity-section'
    ]
}
```

### Navigation Selectors

```python
NAVIGATION_SELECTORS = {
    'profile_tab': [
        '//nav//a[contains(text(), "Profile")]',
        '//a[@data-link-to="profile"]',
        '.global-nav__nav-item a[href*="/in/"]'
    ],
    'network_tab': [
        '//nav//a[contains(text(), "My Network")]',
        '//a[@data-link-to="network"]',
        '.global-nav__nav-item a[href*="/mynetwork/"]'
    ]
}
```

---

## Utility Functions

**Location:** `scripts/linkedin_helpers.py`

### extract_text_with_fallbacks()

```python
async def extract_text_with_fallbacks(
    page: Page,
    selectors: list[str],
    timeout: int = 5000
) -> Optional[str]
```

Tries multiple selectors and returns the first match.

### extract_list_with_fallbacks()

```python
async def extract_list_with_fallbacks(
    page: Page,
    selectors: list[str],
    timeout: int = 5000
) -> list[str]
```

Extracts multiple elements using selector fallbacks.

### wait_for_load_state()

```python
async def wait_for_load_state(
    page: Page,
    state: str = "domcontentloaded"
) -> None
```

Waits for page to finish loading.

### human_delay()

```python
def human_delay(min_sec: float = 1.0, max_sec: float = 3.0) -> None
```

Adds random delay to mimic human behavior.

### clean_text()

```python
def clean_text(text: str) -> str
```

Cleans and normalizes extracted text.

### count_words()

```python
def count_words(text: str) -> int
```

Counts words in text (handles multiple languages).

---

## Error Handling

### Retry Decorator

Uses the existing error recovery system:

```python
from watchers.error_recovery import with_retry, ErrorCategory

@with_retry(max_attempts=3, base_delay=2, max_delay=60, category=ErrorCategory.NETWORK)
async def navigate_to_profile(self, profile_id: str) -> None:
    # Retry with exponential backoff on network errors
    pass
```

### Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| `ConnectionError` | Chrome not running on port 9222 | Start Chrome with CDP enabled |
| `TimeoutError` | Page load timeout | Increase timeout parameter |
| `SelectorError` | LinkedIn selectors changed | Update linkedin_selectors.py |
| `NotLoggedInError` | Not logged into LinkedIn | Log in via Chrome automation window |
| `RateLimitError` | LinkedIn rate limit exceeded | Increase delays, wait before retry |

---

## Configuration

### Environment Variables

```bash
# Optional: Override default CDP endpoint
LINKEDIN_CDP_ENDPOINT=http://127.0.0.1:9222

# Optional: Set default timeout
LINKEDIN_TIMEOUT_MS=30000

# Optional: Enable debug mode
LINKEDIN_DEBUG=true
```

### Settings File

**Location:** `AI_Employee_Vault/.linkedin_accessor_config.json`

```json
{
  "cdp_endpoint": "http://127.0.0.1:9222",
  "timeout_ms": 30000,
  "default_post_limit": 10,
  "default_connection_limit": 100,
  "rate_limit_delay_sec": 3,
  "screenshot_enabled": true,
  "screenshot_dir": "AI_Employee_Vault/Screenshots/"
}
```

---

## Testing

### Unit Tests

```python
# Test profile extraction
python -m pytest tests/test_linkedin_accessor.py::test_extract_profile_data

# Test analyzer
python -m pytest tests/test_linkedin_analyzer.py::test_completeness_score
```

### Integration Tests

```python
# Test end-to-end
python .claude/skills/linkedin-profile-accessor/scripts/linkedin_profile_accessor.py \
    --profile-id "test-profile" \
    --dry-run
```

---

*Last Updated: 2026-01-23*
