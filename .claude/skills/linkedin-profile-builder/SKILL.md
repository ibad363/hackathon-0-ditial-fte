---
name: linkedin-profile-builder
description: Generate AI-optimized LinkedIn profile content drafts for headline, about, experience descriptions, and skills
license: Apache-2.0
---

# LinkedIn Profile Builder

## Overview

The LinkedIn Profile Builder skill generates AI-optimized content drafts to improve LinkedIn profiles. It analyzes your current profile, identifies gaps, and creates professional, SEO-optimized drafts for your headline, about section, experience descriptions, and more.

This skill operates in **draft mode** - it generates recommendations for you to review and apply manually. It never makes changes to your profile automatically.

## Key Features

- **AI-Powered Content**: Generate professional content using GLM API
- **SEO Optimization**: Optimize keywords for recruiter discovery and LinkedIn search
- **Draft Generation**: Create ready-to-use drafts for manual application
- **Profile Completion**: Identify and recommend content for missing sections
- **Industry Templates**: Use proven templates for various industries and roles
- **Tone Customization**: Adjust content tone (professional, casual, confident)

## Capabilities

### Headline Generation

Generate compelling headlines that:
- Communicate your role and expertise clearly
- Include SEO keywords for discoverability
- Showcase your unique value proposition
- Follow LinkedIn best practices (max 220 characters)

### About Section Creation

Create professional about sections that:
- Tell your professional story
- Highlight key achievements and skills
- Use SEO keywords naturally
- Range from 150-500 words (optimal 300 words)
- Engage readers with authentic voice

### Experience Descriptions

Enhance experience entries with:
- Achievement-focused bullet points
- Quantified results and metrics
- Action-oriented language
- Skills integration
- Career progression storytelling

### Skills Recommendations

Suggest relevant skills based on:
- Current industry standards
- Job market demands
- Your experience and goals
- LinkedIn search trends

### SEO Optimization

Optimize your profile with:
- Primary keywords for your target role
- Secondary keywords for broader discovery
- Keyword placement recommendations
- Competitor keyword analysis

## When to Use This Skill

Use the LinkedIn Profile Builder when you need to:

1. **Improve your profile** - Get AI-optimized content that stands out
2. **Job searching** - Optimize your profile for recruiter discovery
3. **Career transition** - Reposition your profile for a new industry
4. **Profile refresh** - Update outdated content with modern best practices
5. **SEO optimization** - Increase visibility in LinkedIn search results
6. **Complete missing sections** - Fill gaps in your profile effectively

## Quick Start

### Generate Profile Improvements

```bash
# Using the skill directly
cd .claude/skills/linkedin-profile-builder
python invoke.py "your-profile-id" "target-role"

# Example:
python invoke.py "hamdan-mohammad-922486374" "Senior AI Engineer"
```

### With Options

```bash
python invoke.py "profile-id" "target-role" \
    --tone professional \
    --include-seo \
    --about-length 300 \
    --output "drafts.md"
```

### Using as a Module

```python
from skills.linkedin_profile_builder import LinkedInProfileBuilder

builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")
drafts = await builder.generate_improvement_drafts(
    profile_id="profile-id",
    target_role="Senior Data Scientist",
    tone="professional",
    include_seo=True
)

# Save drafts
builder.save_drafts(drafts, "improvement_drafts.md")
```

## Workflow

### 1. Request Profile Improvements

Create an action file or invoke the skill directly:

```bash
# Direct invocation
python invoke.py "profile-id" "target-role"

# Via action file
cat > "AI_Employee_Vault/Needs_Action/LINKEDIN_PROFILE_DRAFT_request.md" << 'EOF'
---
type: linkedin_profile_draft
profile_id: hamdan-mohammad-922486374
target_role: Senior AI Engineer
tone: professional
include_seo: true
created: 2026-01-23T10:00:00Z
status: pending_approval
---
EOF
```

### 2. Profile Analysis

The builder:
- Uses the Accessor to extract current profile data
- Analyzes completeness and identifies gaps
- Extracts existing keywords and content
- Identifies improvement opportunities

### 3. Content Generation

The builder generates:
- **Optimized headline** with SEO keywords
- **Professional about section** (300 words recommended)
- **Enhanced experience descriptions** with achievements
- **Skills recommendations** for your target role
- **SEO keyword list** for optimization

### 4. Draft Creation

Results are saved to:
- `Needs_Action/LINKEDIN_PROFILE_DRAFT_*.md` - For review
- `AI_Employee_Vault/Logs/YYYY-MM-DD.json` - Audit trail

### 5. Review and Apply

1. Review each draft section
2. Edit as needed for your voice
3. Copy and paste to LinkedIn profile
4. Save profile when complete

## Content Guidelines

### Headline Best Practices

- **Length**: 100-220 characters (optimal: 150)
- **Format**: Role | Specialization | Key Achievement
- **Keywords**: Include 2-3 primary keywords
- **Value**: Communicate what you do and your impact

**Good Example:**
```
Senior AI Engineer | Machine Learning | NLP | Building AI products that impact 100M+ users
```

**Bad Example:**
```
Looking for work | Aspiring engineer
```

### About Section Best Practices

- **Length**: 250-400 words (optimal: 300)
- **Structure**:
  1. Hook - Who you are and what you do
  2. Story - Your journey and passion
  3. Skills - Key expertise areas
  4. Impact - What you've achieved
  5. Call to action - Connect or reach out

- **Voice**: Authentic, professional, conversational
- **Keywords**: 5-7 primary keywords naturally integrated
- **Achievements**: Quantified results (numbers, percentages)

### Experience Description Best Practices

- **Format**: Bullet points for readability
- **Focus**: Achievements, not just responsibilities
- **Quantification**: Use numbers wherever possible
- **Action verbs**: Built, Led, Developed, Increased, etc.

**Good Example:**
```
Senior Software Engineer at TechCorp
• Led development of AI platform serving 10M+ daily users
• Improved system performance by 40% through optimization
• Managed team of 5 engineers across 2 time zones
• Reduced deployment time from 2 hours to 15 minutes
```

### Skills Best Practices

- **Quantity**: 15-30 skills (optimal: 20)
- **Mix**: Technical skills + soft skills + tools
- **Endorsements**: Focus on skills you can get endorsed for
- **Relevance**: Align with your target role

## File Structure

```
.claude/skills/linkedin-profile-builder/
├── SKILL.md                          # This file
├── FORMS.md                          # Draft templates
├── reference.md                      # Technical reference
├── examples.md                       # Usage examples
├── invoke.py                         # Main invocation script
└── scripts/
    ├── __init__.py
    ├── draft_models.py               # Dataclass definitions
    ├── linkedin_content_generator.py # AI content generation
    ├── linkedin_seo_optimizer.py     # SEO optimization
    ├── linkedin_profile_builder.py   # Core builder logic
    └── linkedin_builder_monitor.py   # Approval workflow monitor
templates/
    ├── headline_templates.json        # Headline templates by role
    └── about_templates.json           # About section templates
keywords/
    └── seo_keywords.json              # SEO keyword database
```

## Integration with Other Skills

### LinkedIn Profile Accessor
Use the Accessor skill first to analyze your current profile:

```bash
# Analyze first
cd .claude/skills/linkedin-profile-accessor
python invoke.py "your-profile-id"

# Then generate improvements
cd ../linkedin-profile-builder
python invoke.py "your-profile-id" "target-role"
```

### LinkedIn Manager
After applying improvements, post about them:

```bash
/skill linkedin-manager
```

### Research LinkedIn Generator
Combine with research for industry-specific content:

```bash
/skill research-linkedin-generator
```

## Technical Details

### GLM API Integration

The builder uses the GLM API (Zhipu AI) for content generation:

```python
from linkedin_content_generator import LinkedInContentGenerator

generator = LinkedInContentGenerator(
    api_key=os.getenv("ZHIPU_API_KEY"),
    model="glm-4"
)

headline = generator.generate_headline({
    "current_role": "Senior Software Engineer",
    "industry": "Technology",
    "expertise": ["Python", "AI", "Cloud"],
    "target_companies": ["Google", "Microsoft"]
})
```

### SEO Keyword Database

The builder includes a local keyword database by industry and role:

```json
{
  "software_engineer": {
    "primary": ["Python", "JavaScript", "AWS", "Kubernetes", "CI/CD"],
    "secondary": ["Docker", "React", "Node.js", "Microservices", "API"]
  }
}
```

### Content Templates

Industry-specific templates ensure relevant, professional content:

```json
{
  "tech_headline": "{role} | {specializations} | {achievement}",
  "about_tech": "Passionate {role} with {years} years of experience..."
}
```

## Configuration

### Environment Variables

```bash
# Required for AI content generation
ZHIPU_API_KEY=your_api_key_here

# Optional model selection
LINKEDIN_BUILDER_MODEL=glm-4

# Optional tone default
LINKEDIN_BUILDER_TONE=professional
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
  "template_directory": ".claude/skills/linkedin-profile-builder/templates"
}
```

## Troubleshooting

### API Key Not Found

**Problem:** `Error: ZHIPU_API_KEY not found`

**Solution:**
```bash
# Set API key
export ZHIPU_API_KEY=your_api_key_here

# Or add to .env file
echo "ZHIPU_API_KEY=your_api_key_here" >> .env
```

### Generated Content Too Generic

**Problem:** Content feels generic or doesn't sound like you

**Solution:**
- Provide more specific context in your request
- Include your actual achievements and numbers
- Edit the generated drafts to add your voice
- Use different tone option (confident, casual)

### SEO Keywords Not Relevant

**Problem:** Suggested keywords don't match your industry

**Solution:**
- Specify your industry and target role explicitly
- Edit the SEO keyword list manually
- Add custom keywords to `keywords/seo_keywords.json`

### Profile Not Found

**Problem:** `Error: Profile not found or not accessible`

**Solution:**
- Verify profile ID is correct
- Make sure profile is public or you're connected
- Check Chrome automation is logged into LinkedIn

## Security Considerations

1. **Draft Mode Only**: Content is generated as drafts only - never auto-applied
2. **Manual Review**: All drafts require human review before application
3. **Local Storage**: All drafts stored locally in the vault
4. **Audit Logging**: All generation activities logged
5. **API Key Security**: API keys loaded from environment variables
6. **No Auto-Posting**: No automatic changes to LinkedIn profile

## Content Tone Options

### Professional
- Formal, business-oriented
- Best for: Executives, consultants, job seekers
- Example: "Results-driven leader with 15+ years of experience..."

### Confident
- Bold, assertive
- Best for: Senior roles, entrepreneurs
- Example: "I build products that users love. Scaling teams..."

### Casual
- Conversational, approachable
- Best for: Creative roles, startups
- Example: "Passionate about turning complex problems into simple solutions..."

### Technical
- Precise, detailed
- Best for: Engineers, researchers
- Example: "Specialized in distributed systems, ML pipelines..."

## Future Enhancements

- **A/B Testing**: Generate multiple versions for testing
- **Competitor Analysis**: Compare with top profiles in your field
- **Integration with Job Descriptions**: Tailor content to specific job postings
- **Multi-language Support**: Generate content in multiple languages
- **Video Scripts**: Generate video intro scripts for profile
- **Recommendation Requests**: Draft recommendation requests for others

## Related Documentation

- [LinkedIn Profile Accessor](.claude/skills/linkedin-profile-accessor/SKILL.md) - Analyze profiles
- [LinkedIn Manager](.claude/skills/linkedin-manager/SKILL.md) - Post to LinkedIn
- [Research Processor](research_processor/) - GLM API integration
- [SEO Keywords](.claude/skills/linkedin-profile-builder/keywords/seo_keywords.json) - Keyword database

---
*Last Updated: 2026-01-23*
*Version: 1.0.0*
