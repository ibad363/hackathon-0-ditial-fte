# LinkedIn Profile Builder - Technical Reference

This document provides detailed technical information about the LinkedIn Profile Builder skill.

---

## API Reference

### LinkedInProfileBuilder Class

**Location:** `scripts/linkedin_profile_builder.py`

#### Constructor

```python
LinkedInProfileBuilder(
    vault_path: str | Path = "AI_Employee_Vault",
    api_key: str | None = None,
    model: str = "glm-4"
)
```

**Parameters:**
- `vault_path`: Path to the Obsidian vault (default: "AI_Employee_Vault")
- `api_key`: GLM API key (default: from ZHIPU_API_KEY env var)
- `model`: GLM model to use (default: "glm-4")

**Example:**
```python
from skills.linkedin_profile_builder import LinkedInProfileBuilder

builder = LinkedInProfileBuilder(
    vault_path="AI_Employee_Vault",
    api_key=os.getenv("ZHIPU_API_KEY")
)
```

#### Methods

##### analyze_current_profile()

```python
async def analyze_current_profile(self, profile_id: str) -> ProfileAnalysis
```

Analyzes the current LinkedIn profile.

**Parameters:**
- `profile_id`: LinkedIn profile ID

**Returns:** `ProfileAnalysis` object with:
- Current profile data
- Completeness score
- Strengths and weaknesses
- Improvement opportunities

##### generate_headline_draft()

```python
def generate_headline_draft(
    self,
    profile_data: ProfileData,
    target_role: str,
    tone: str = "professional"
) -> HeadlineDraft
```

Generates optimized headline.

**Parameters:**
- `profile_data`: Current profile data
- `target_role`: Target job role
- `tone`: Content tone (professional, confident, casual, technical)

**Returns:** `HeadlineDraft` with:
- Suggested headline
- Reasoning
- Character count
- SEO keywords

**Example:**
```python
draft = builder.generate_headline_draft(
    profile_data,
    "Senior AI Engineer",
    tone="professional"
)
print(draft.headline)
# "Senior AI Engineer | Machine Learning | NLP | Building AI products at scale"
```

##### generate_about_draft()

```python
def generate_about_draft(
    self,
    profile_data: ProfileData,
    target_role: str,
    tone: str = "professional",
    target_length: int = 300
) -> AboutDraft
```

Generates optimized about section.

**Parameters:**
- `profile_data`: Current profile data
- `target_role`: Target job role
- `tone`: Content tone
- `target_length`: Target word count (default: 300)

**Returns:** `AboutDraft` with:
- Suggested about text
- Word count
- SEO keywords
- Improvement reasoning

##### generate_experience_updates()

```python
def generate_experience_updates(
    self,
    profile_data: ProfileData,
    target_role: str
) -> list[ExperienceDraft]
```

Generates enhanced experience descriptions.

**Parameters:**
- `profile_data`: Current profile data
- `target_role`: Target job role

**Returns:** List of `ExperienceDraft` objects with:
- Enhanced descriptions
- Improvement notes
- Before/after comparison

##### identify_missing_sections()

```python
def identify_missing_sections(
    self,
    profile_data: ProfileData,
    target_role: str
) -> list[MissingSection]
```

Identifies missing or incomplete profile sections.

**Returns:** List of `MissingSection` objects with:
- Section name
- Why it's missing
- Recommended content

##### generate_improvement_drafts()

```python
async def generate_improvement_drafts(
    self,
    profile_id: str,
    target_role: str,
    tone: str = "professional",
    include_seo: bool = True
) -> ProfileDrafts
```

Generates complete set of improvement drafts.

**Parameters:**
- `profile_id`: LinkedIn profile ID
- `target_role`: Target job role
- `tone`: Content tone
- `include_seo`: Whether to include SEO optimization

**Returns:** `ProfileDrafts` object with:
- Headline draft
- About draft
- Experience drafts
- Skills recommendations
- SEO keywords

##### save_drafts()

```python
def save_drafts(
    self,
    drafts: ProfileDrafts,
    output_path: str | Path,
    format: str = "markdown"
) -> Path
```

Saves drafts to file.

**Parameters:**
- `drafts`: ProfileDrafts object
- `output_path`: Output file path
- `format`: Output format ("markdown" or "json")

**Returns:** Path to saved file

---

### LinkedInContentGenerator Class

**Location:** `scripts/linkedin_content_generator.py`

#### Constructor

```python
LinkedInContentGenerator(
    api_key: str,
    model: str = "glm-4",
    timeout: int = 30
)
```

**Parameters:**
- `api_key`: GLM API key
- `model`: Model name (default: "glm-4")
- `timeout`: Request timeout in seconds (default: 30)

#### Methods

##### generate_headline()

```python
def generate_headline(self, context: dict) -> str
```

Generates headline using AI.

**Context Keys:**
- `current_role`: Current job title
- `target_role`: Target job title
- `industry`: Industry
- `expertise`: List of expertise areas
- `achievements`: Key achievements
- `tone`: Content tone

##### generate_about()

```python
def generate_about(self, context: dict, target_length: int = 300) -> str
```

Generates about section using AI.

**Context Keys:**
- `current_role`: Job title
- `years_experience`: Years of experience
- `industry`: Industry
- `expertise`: Key skills
- `achievements`: Notable achievements
- `passion`: What drives you
- `tone`: Content tone
- `target_length`: Target word count

##### generate_experience_description()

```python
def generate_experience_description(
    self,
    role: str,
    company: str,
    context: dict
) -> str
```

Generates experience description using AI.

**Context Keys:**
- `duration`: Time in role
- `achievements`: List of achievements
- `responsibilities`: Key responsibilities
- `team_size`: Team size managed
- `tools`: Tools/technologies used

---

### LinkedInSEOOptimizer Class

**Location:** `scripts/linkedin_seo_optimizer.py`

#### Methods

##### extract_keywords()

```python
def extract_keywords(self, profile_data: ProfileData) -> list[Keyword]
```

Extracts keywords from profile.

##### analyze_keyword_gaps()

```python
def analyze_keyword_gaps(
    self,
    profile_data: ProfileData,
    target_role: str
) -> list[str]
```

Identifies missing keywords for target role.

##### suggest_keywords()

```python
def suggest_keywords(
    self,
    industry: str,
    role: str
) -> Keywords
```

Suggests keywords based on industry and role.

##### optimize_content()

```python
def optimize_content(
    self,
    content: str,
    keywords: list[str]
) -> str
```

Optimizes content by naturally integrating keywords.

---

## Data Models

**Location:** `scripts/draft_models.py`

### HeadlineDraft

```python
@dataclass
class HeadlineDraft:
    current: str
    suggested: str
    reasoning: str
    character_count: int
    seo_keywords: list[str]
    options: list[str]  # Alternative options
```

### AboutDraft

```python
@dataclass
class AboutDraft:
    current: str
    suggested: str
    reasoning: str
    word_count: int
    seo_keywords: list[str]
    options: list[str]  # Alternative versions
```

### ExperienceDraft

```python
@dataclass
class ExperienceDraft:
    title: str
    company: str
    current_description: str
    enhanced_description: str
    improvements: list[str]
    score_improvement: int
```

### SkillsRecommendation

```python
@dataclass
class SkillsRecommendation:
    name: str
    reason: str
    priority: str  # high, medium, low
    demand: str  # high, medium, low
```

### ProfileDrafts

```python
@dataclass
class ProfileDrafts:
    profile_id: str
    target_role: str
    headline: HeadlineDraft
    about: AboutDraft
    experiences: list[ExperienceDraft]
    skills_recommendations: list[SkillsRecommendation]
    missing_sections: list[str]
    seo_keywords: Keywords
    generated_at: datetime
```

### Keywords

```python
@dataclass
class Keywords:
    primary: list[str]      # Top 10 most important
    secondary: list[str]    # Next 20
    long_tail: list[str]    # Niche keywords
```

---

## GLM API Integration

### Request Format

```python
import requests
import os

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
API_KEY = os.getenv("ZHIPU_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "glm-4",
    "messages": [
        {
            "role": "system",
            "content": "You are a LinkedIn profile optimization expert."
        },
        {
            "role": "user",
            "content": "Generate a headline for a Senior AI Engineer..."
        }
    ],
    "temperature": 0.7,
    "max_tokens": 500
}

response = requests.post(API_URL, headers=headers, json=data)
result = response.json()
```

### Error Handling

```python
try:
    result = generate_headline(context)
except APIError as e:
    if e.status_code == 401:
        # Invalid API key
        print("Check your ZHIPU_API_KEY")
    elif e.status_code == 429:
        # Rate limit exceeded
        print("Rate limit exceeded. Wait and retry.")
    else:
        print(f"API error: {e}")
```

---

## Templates

### Headline Templates

**Location:** `templates/headline_templates.json`

```json
{
  "tech": "{role} | {specializations} | {achievement}",
  "executive": "{role} | {industry} Leader | {impact}",
  "creative": "{role} ✨ {specialization} | Creating {impact}",
  "minimal": "{role} | {top_skill}"
}
```

### About Templates

**Location:** `templates/about_templates.json`

```json
{
  "professional": "Passionate {role} with {years} years of experience in {industry}. Specialized in {specializations}...",
  "story": "My journey in {industry} started {years} years ago when...",
  "achievement": "Throughout my career, I've {major_achievement}. Currently focused on...",
  "concise": "{role} | {specializations} | {achievement}."
}
```

---

## SEO Keyword Database

**Location:** `keywords/seo_keywords.json`

```json
{
  "software_engineer": {
    "primary": ["Python", "JavaScript", "AWS", "Kubernetes", "CI/CD"],
    "secondary": ["Docker", "React", "Node.js", "Microservices", "API"],
    "long_tail": ["Serverless computing", "Event-driven architecture", "Distributed systems"]
  },
  "data_scientist": {
    "primary": ["Machine Learning", "Python", "SQL", "TensorFlow", "PyTorch"],
    "secondary": ["NLP", "Deep Learning", "Statistics", "R", "Tableau"],
    "long_tail": ["Natural Language Processing", "Computer Vision", "Reinforcement Learning"]
  }
}
```

---

## Configuration

### Environment Variables

```bash
# Required
ZHIPU_API_KEY=your_api_key_here

# Optional
LINKEDIN_BUILDER_MODEL=glm-4
LINKEDIN_BUILDER_TONE=professional
LINKEDIN_BUILDER_TIMEOUT=30
```

### Settings File

**Location:** `AI_Employee_Vault/.linkedin_builder_config.json`

```json
{
  "model": "glm-4",
  "default_tone": "professional",
  "about_length_target": 300,
  "headline_max_length": 220,
  "enable_seo": true,
  "template_directory": ".claude/skills/linkedin-profile-builder/templates",
  "keyword_database": ".claude/skills/linkedin-profile-builder/keywords/seo_keywords.json"
}
```

---

## Error Handling

### Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| `APIKeyError` | ZHIPU_API_KEY not set | Set environment variable |
| `APIConnectionError` | Cannot reach GLM API | Check internet connection |
| `RateLimitError` | Too many API requests | Wait and retry |
| `ProfileNotFoundError` | Profile ID invalid | Verify profile ID |
| `TemplateNotFoundError` | Template file missing | Create template file |

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_api_with_retry(prompt: str) -> str:
    # API call that may fail
    pass
```

---

## Testing

### Unit Tests

```python
# Test content generation
python -m pytest tests/test_linkedin_builder.py::test_generate_headline

# Test SEO optimizer
python -m pytest tests/test_seo_optimizer.py::test_keyword_extraction
```

### Integration Tests

```bash
# Test full pipeline
python .claude/skills/linkedin-profile-builder/scripts/linkedin_profile_builder.py \
    --profile-id "test-profile" \
    --target-role "Senior AI Engineer" \
    --dry-run
```

---

*Last Updated: 2026-01-23*
