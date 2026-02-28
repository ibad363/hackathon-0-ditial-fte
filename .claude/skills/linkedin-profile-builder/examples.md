# LinkedIn Profile Builder - Usage Examples

This document provides practical examples of using the LinkedIn Profile Builder skill.

---

## Example 1: Generate Complete Profile Improvements

```python
from skills.linkedin_profile_builder import LinkedInProfileBuilder
import asyncio

async def generate_improvements():
    builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")

    # Generate all improvement drafts
    drafts = await builder.generate_improvement_drafts(
        profile_id="hamdan-mohammad-922486374",
        target_role="Senior AI Engineer",
        tone="professional",
        include_seo=True
    )

    # Print summary
    print(f"Generated improvements for {drafts.profile_id}")
    print(f"Target Role: {drafts.target_role}")
    print(f"\nSuggested Headline:\n{drafts.headline.suggested}")
    print(f"\nAbout Section: {drafts.about.word_count} words")
    print(f"Experience Updates: {len(drafts.experiences)}")
    print(f"Skills to Add: {len(drafts.skills_recommendations)}")

    # Save drafts
    output_path = builder.save_drafts(
        drafts,
        "AI_Employee_Vault/Needs_Action/LINKEDIN_PROFILE_DRAFT_improvements.md",
        format="markdown"
    )
    print(f"\nDrafts saved to: {output_path}")

asyncio.run(generate_improvements())
```

---

## Example 2: Generate Headline Only

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
from skills.linkedin_profile_builder import LinkedInProfileBuilder
import asyncio

async def generate_headline():
    # Extract current profile
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")
    profile_data = await accessor.extract_profile_data("profile-id")

    # Generate headline
    builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")
    headline_draft = builder.generate_headline_draft(
        profile_data=profile_data,
        target_role="Senior Data Scientist",
        tone="professional"
    )

    # Display options
    print("Current Headline:")
    print(f"  {headline_draft.current}")
    print(f"\nSuggested Headline:")
    print(f"  {headline_draft.suggested}")
    print(f"\nCharacter Count: {headline_draft.character_count}/220")
    print(f"\nReasoning:")
    print(f"  {headline_draft.reasoning}")
    print(f"\nSEO Keywords: {', '.join(headline_draft.seo_keywords)}")

    # Show alternative options
    print(f"\nAlternative Options:")
    for i, option in enumerate(headline_draft.options, 1):
        print(f"  {i}. {option}")

asyncio.run(generate_headline())
```

---

## Example 3: Generate About Section

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
from skills.linkedin_profile_builder import LinkedInProfileBuilder
import asyncio

async def generate_about():
    # Extract current profile
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")
    profile_data = await accessor.extract_profile_data("profile-id")

    # Generate about section
    builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")

    # Try different tones
    for tone in ["professional", "confident", "casual"]:
        about_draft = builder.generate_about_draft(
            profile_data=profile_data,
            target_role="Product Manager",
            tone=tone,
            target_length=300
        )

        print(f"\n=== {tone.title()} Tone ===")
        print(f"Word Count: {about_draft.word_count}")
        print(f"\n{about_draft.suggested}")

asyncio.run(generate_about())
```

---

## Example 4: Enhance Experience Descriptions

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
from skills.linkedin_profile_builder import LinkedInProfileBuilder
import asyncio

async def enhance_experience():
    # Extract current profile
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")
    profile_data = await accessor.extract_profile_data("profile-id")

    # Generate enhanced experiences
    builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")
    experience_drafts = builder.generate_experience_updates(
        profile_data=profile_data,
        target_role="Senior Software Engineer"
    )

    # Display enhancements
    for exp_draft in experience_drafts:
        print(f"\n{'='*60}")
        print(f"{exp_draft.title} at {exp_draft.company}")
        print(f"{'='*60}")

        print(f"\nBEFORE:")
        print(f"  {exp_draft.current_description or '(No description)'}")

        print(f"\nAFTER:")
        print(f"  {exp_draft.enhanced_description}")

        print(f"\nIMPROVEMENTS:")
        for improvement in exp_draft.improvements:
            print(f"  • {improvement}")

        print(f"\nScore Improvement: +{exp_draft.score_improvement} points")

asyncio.run(enhance_experience())
```

---

## Example 5: Get Skills Recommendations

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
from skills.linkedin_profile_builder import LinkedInProfileBuilder
import asyncio

async def get_skills_recommendations():
    # Extract current profile
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")
    profile_data = await accessor.extract_profile_data("profile-id")

    # Get skills recommendations
    builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")
    recommendations = builder.identify_missing_sections(
        profile_data=profile_data,
        target_role="Machine Learning Engineer"
    )

    # Display recommendations by priority
    print("Skills Recommendations:")
    print("=" * 50)

    high_priority = [r for r in recommendations if r.priority == "high"]
    medium_priority = [r for r in recommendations if r.priority == "medium"]
    low_priority = [r for r in recommendations if r.priority == "low"]

    print(f"\nHIGH PRIORITY ({len(high_priority)}):")
    for rec in high_priority:
        print(f"  • {rec.name}")
        print(f"    Reason: {rec.reason}")

    print(f"\nMEDIUM PRIORITY ({len(medium_priority)}):")
    for rec in medium_priority:
        print(f"  • {rec.name}")

    print(f"\nLOW PRIORITY ({len(low_priority)}):")
    for rec in low_priority:
        print(f"  • {rec.name}")

asyncio.run(get_skills_recommendations())
```

---

## Example 6: SEO Optimization

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
from skills.linkedin_profile_builder import LinkedInProfileBuilder, LinkedInSEOOptimizer
import asyncio

async def optimize_seo():
    # Extract current profile
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")
    profile_data = await accessor.extract_profile_data("profile-id")

    # Get SEO optimizer
    builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")
    seo_optimizer = LinkedInSEOOptimizer(vault_path="AI_Employee_Vault")

    # Analyze keywords
    current_keywords = seo_optimizer.extract_keywords(profile_data)
    print("Current Keywords:")
    print(f"  Primary: {', '.join(current_keywords.primary[:10])}")

    # Get keyword suggestions for target role
    suggested_keywords = seo_optimizer.suggest_keywords(
        industry="Technology",
        role="Senior Software Engineer"
    )
    print(f"\nSuggested Keywords:")
    print(f"  Primary: {', '.join(suggested_keywords.primary)}")
    print(f"  Secondary: {', '.join(suggested_keywords.secondary[:10])}")

    # Find keyword gaps
    gaps = seo_optimizer.analyze_keyword_gaps(
        profile_data=profile_data,
        target_role="Senior Software Engineer"
    )
    print(f"\nMissing Keywords:")
    for gap in gaps:
        print(f"  • {gap}")

    # Generate SEO-optimized headline
    drafts = await builder.generate_improvement_drafts(
        profile_id="profile-id",
        target_role="Senior Software Engineer",
        include_seo=True
    )
    print(f"\nSEO-Optimized Headline:")
    print(f"  {drafts.headline.suggested}")
    print(f"\nSEO Keywords Used:")
    for keyword in drafts.headline.seo_keywords:
        print(f"  • {keyword}")

asyncio.run(optimize_seo())
```

---

## Example 7: Using the Invoke Script

```bash
# Basic usage
cd .claude/skills/linkedin-profile-builder
python invoke.py "hamdan-mohammad-922486374" "Senior AI Engineer"

# With custom tone
python invoke.py "profile-id" "target-role" --tone confident

# With SEO optimization
python invoke.py "profile-id" "target-role" --include-seo

# Custom output path
python invoke.py "profile-id" "target-role" --output "my_drafts.md"

# Specify about section length
python invoke.py "profile-id" "target-role" --about-length 400
```

---

## Example 8: Standalone Script Usage

```bash
# Run directly
python .claude/skills/linkedin-profile-builder/scripts/linkedin_profile_builder.py \
    --profile-id "hamdan-mohammad-922486374" \
    --target-role "Senior AI Engineer" \
    --tone professional \
    --include-seo \
    --output "drafts.md"

# Dry run (no file output)
python .claude/skills/linkedin-profile-builder/scripts/linkedin_profile_builder.py \
    --profile-id "profile-id" \
    --target-role "Software Engineer" \
    --dry-run
```

---

## Example 9: Multiple Role Options

```python
from skills.linkedin_profile_builder import LinkedInProfileBuilder
import asyncio

async def compare_roles():
    builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")

    roles = [
        "Senior Software Engineer",
        "Engineering Manager",
        "Solutions Architect",
        "Principal Engineer"
    ]

    for role in roles:
        drafts = await builder.generate_improvement_drafts(
            profile_id="profile-id",
            target_role=role,
            tone="professional"
        )

        print(f"\n{'='*60}")
        print(f"Role: {role}")
        print(f"{'='*60}")
        print(f"\nHeadline:\n{drafts.headline.suggested}\n")

asyncio.run(compare_roles())
```

---

## Example 10: Integration with Approval Workflow

```python
from pathlib import Path
from skills.linkedin_profile_builder import LinkedInProfileBuilder
import asyncio
import json

async def create_approval_request():
    builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")

    # Generate drafts
    drafts = await builder.generate_improvement_drafts(
        profile_id="profile-id",
        target_role="Senior AI Engineer",
        tone="professional",
        include_seo=True
    )

    # Create approval file
    vault_path = Path("AI_Employee_Vault")
    timestamp = drafts.generated_at.strftime("%Y%m%d_%H%M%S")

    approval_file = vault_path / "Needs_Action" / f"LINKEDIN_PROFILE_DRAFT_{timestamp}.md"

    # Generate markdown content
    content = f"""---
type: linkedin_profile_draft
profile_id: {drafts.profile_id}
target_role: {drafts.target_role}
created: {drafts.generated_at.isoformat()}
status: pending_approval
---

# LinkedIn Profile Improvement Drafts

## Suggested Headline

```
{drafts.headline.suggested}
```

**Character Count:** {drafts.headline.character_count}/220

## About Section

```
{drafts.about.suggested}
```

**Word Count:** {drafts.about.word_count}

## Next Steps

1. Review each draft section
2. Edit as needed
3. Copy and paste to LinkedIn profile
4. Save profile when complete
"""

    # Write file
    approval_file.write_text(content)
    print(f"Approval file created: {approval_file}")

    # Print JSON for Claude Code
    print(json.dumps({
        "status": "success",
        "profile_id": drafts.profile_id,
        "target_role": drafts.target_role,
        "draft_file": str(approval_file),
        "next_steps": [
            f"Review drafts at: {approval_file}",
            "Edit as needed",
            "Apply to LinkedIn profile manually"
        ]
    }))

asyncio.run(create_approval_request())
```

---

## Example 11: Custom Tone Options

```python
from skills.linkedin_profile_builder import LinkedInProfileBuilder
import asyncio

async def compare_tones():
    builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")

    tones = ["professional", "confident", "casual", "technical"]

    for tone in tones:
        drafts = await builder.generate_improvement_drafts(
            profile_id="profile-id",
            target_role="Senior Engineer",
            tone=tone
        )

        print(f"\n{'='*60}")
        print(f"Tone: {tone.title()}")
        print(f"{'='*60}")
        print(f"\nHeadline:\n{drafts.headline.suggested}\n")
        print(f"About Preview:\n{drafts.about.suggested[:200]}...\n")

asyncio.run(compare_tones())
```

---

## Example 12: Batch Processing

```python
from skills.linkedin_profile_builder import LinkedInProfileBuilder
import asyncio

async def batch_generate():
    builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")

    profiles = [
        ("profile-id-1", "Senior Software Engineer"),
        ("profile-id-2", "Product Manager"),
        ("profile-id-3", "Data Scientist")
    ]

    results = []

    for profile_id, target_role in profiles:
        try:
            drafts = await builder.generate_improvement_drafts(
                profile_id=profile_id,
                target_role=target_role,
                tone="professional"
            )

            results.append({
                "profile_id": profile_id,
                "target_role": target_role,
                "status": "success",
                "headline": drafts.headline.suggested
            })

            # Rate limiting
            await asyncio.sleep(2)

        except Exception as e:
            results.append({
                "profile_id": profile_id,
                "target_role": target_role,
                "status": "error",
                "error": str(e)
            })

    # Print summary
    print("\nBatch Processing Summary:")
    print("=" * 50)
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {result['profile_id']} - {result['target_role']}")

asyncio.run(batch_generate())
```

---

## Common Patterns

### Pattern 1: Analyze Then Build

```python
# First analyze with Accessor
accessor = LinkedInProfileAccessor()
profile_data = await accessor.extract_profile_data("profile-id")

# Then build with Builder
builder = LinkedInProfileBuilder()
drafts = await builder.generate_improvement_drafts(
    profile_id="profile-id",
    target_role="Senior Engineer"
)
```

### Pattern 2: Iterate on Content

```python
builder = LinkedInProfileBuilder()

# Generate first version
drafts = await builder.generate_improvement_drafts("profile-id", "role-1")

# Generate alternative version
drafts_alt = await builder.generate_improvement_drafts(
    "profile-id",
    "role-1",
    tone="confident"  # Different tone
)
```

### Pattern 3: Compare Multiple Options

```python
builder = LinkedInProfileBuilder()

# Generate for different roles
for role in ["role-1", "role-2", "role-3"]:
    drafts = await builder.generate_improvement_drafts("profile-id", role)
    print(f"{role}: {drafts.headline.suggested}")
```

---

*Last Updated: 2026-01-23*
