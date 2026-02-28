# LinkedIn Profile Accessor - Usage Examples

This document provides practical examples of using the LinkedIn Profile Accessor skill.

---

## Example 1: Analyze Your Own Profile

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
import asyncio

async def analyze_my_profile():
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")

    # Extract profile data
    profile_data = await accessor.extract_profile_data(
        profile_id="hamdan-mohammad-922486374",
        include_posts=True,
        post_limit=10,
        include_network=False
    )

    # Print summary
    print(f"Name: {profile_data.name}")
    print(f"Headline: {profile_data.headline}")
    print(f"Completeness Score: {profile_data.completeness_score}/100")
    print(f"Connections: {profile_data.connections_count}")

    # Save report
    report_path = accessor.save_profile_report(
        profile_data,
        "AI_Employee_Vault/Needs_Action/LINKEDIN_PROFILE_ANALYSIS_my_profile.md",
        format="markdown"
    )
    print(f"Report saved to: {report_path}")

asyncio.run(analyze_my_profile())
```

---

## Example 2: Extract Profile Data as JSON

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
import asyncio
import json

async def export_profile_json():
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")

    # Extract data
    profile_data = await accessor.extract_profile_data("profile-id")

    # Convert to dictionary
    data_dict = {
        "name": profile_data.name,
        "headline": profile_data.headline,
        "location": profile_data.location,
        "about": profile_data.about,
        "experience": [
            {
                "title": exp.title,
                "company": exp.company,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "description": exp.description
            }
            for exp in profile_data.experience
        ],
        "skills": [skill.name for skill in profile_data.skills],
        "completeness_score": profile_data.completeness_score
    }

    # Save as JSON
    with open("profile_data.json", "w") as f:
        json.dump(data_dict, f, indent=2)

    print("Profile data exported to profile_data.json")

asyncio.run(export_profile_json())
```

---

## Example 3: Analyze Multiple Profiles

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
from skills.linkedin_profile_analyzer import LinkedInProfileAnalyzer
import asyncio

async def analyze_multiple_profiles():
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")
    analyzer = LinkedInProfileAnalyzer(vault_path="AI_Employee_Vault")

    profiles = [
        "profile-id-1",
        "profile-id-2",
        "profile-id-3"
    ]

    results = []

    for profile_id in profiles:
        # Extract data
        profile_data = await accessor.extract_profile_data(profile_id)

        # Analyze
        completeness = analyzer.analyze_completeness(profile_data)
        strengths = analyzer.identify_strengths(profile_data)
        weaknesses = analyzer.identify_weaknesses(profile_data)

        results.append({
            "profile_id": profile_id,
            "name": profile_data.name,
            "completeness_score": completeness.total_score,
            "strengths": strengths,
            "weaknesses": weaknesses
        })

        # Rate limiting delay
        await asyncio.sleep(3)

    # Print summary
    print("\nProfile Analysis Summary")
    print("=" * 50)
    for r in results:
        print(f"\n{r['name']} ({r['profile_id']})")
        print(f"  Score: {r['completeness_score']}/100")
        print(f"  Strengths: {len(r['strengths'])}")
        print(f"  Weaknesses: {len(r['weaknesses'])}")

asyncio.run(analyze_multiple_profiles())
```

---

## Example 4: Network Analysis

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
from skills.linkedin_network_analyzer import LinkedInNetworkAnalyzer
import asyncio

async def analyze_network():
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")
    network_analyzer = LinkedInNetworkAnalyzer(vault_path="AI_Employee_Vault")

    # Extract profile with network data
    profile_data = await accessor.extract_profile_data(
        "profile-id",
        include_network=True
    )

    # Analyze network
    connections = await network_analyzer.extract_connections("profile-id", limit=100)

    # Count by industry
    industry_count = {}
    for conn in connections:
        if conn.company:
            industry_count[conn.company] = industry_count.get(conn.company, 0) + 1

    # Print top industries
    print("Top Companies in Network:")
    sorted_companies = sorted(industry_count.items(), key=lambda x: x[1], reverse=True)
    for company, count in sorted_companies[:10]:
        print(f"  {company}: {count} connections")

    # Analyze activity patterns
    if profile_data.posts:
        activity = network_analyzer.analyze_activity_patterns(profile_data.posts)
        print(f"\nActivity Patterns:")
        print(f"  Posts per week: {activity.posts_per_week}")
        print(f"  Best day to post: {activity.best_day}")
        print(f"  Avg engagement: {activity.engagement_rate}%")

asyncio.run(analyze_network())
```

---

## Example 5: Compare Two Profiles

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
from skills.linkedin_profile_analyzer import LinkedInProfileAnalyzer
import asyncio

async def compare_profiles():
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")
    analyzer = LinkedInProfileAnalyzer(vault_path="AI_Employee_Vault")

    # Extract both profiles
    profile_a = await accessor.extract_profile_data("profile-id-a")
    profile_b = await accessor.extract_profile_data("profile-id-b")

    # Analyze both
    score_a = analyzer.analyze_completeness(profile_a)
    score_b = analyzer.analyze_completeness(profile_b)

    # Compare
    print(f"\nProfile Comparison")
    print("=" * 50)
    print(f"\n{profile_a.name} vs {profile_b.name}")
    print(f"\nCompleteness Score:")
    print(f"  {profile_a.name}: {score_a.total_score}/100")
    print(f"  {profile_b.name}: {score_b.total_score}/100")

    # Compare sections
    sections = ["headline", "about", "experience", "skills"]
    print(f"\nSection Breakdown:")
    for section in sections:
        score_a_section = score_a.breakdown.get(section, 0)
        score_b_section = score_b.breakdown.get(section, 0)
        winner = profile_a.name if score_a_section > score_b_section else profile_b.name
        print(f"  {section.title()}: {score_a_section} vs {score_b_section} (Winner: {winner})")

asyncio.run(compare_profiles())
```

---

## Example 6: Generate Improvement Suggestions

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
from skills.linkedin_profile_analyzer import LinkedInProfileAnalyzer
import asyncio

async def get_improvement_suggestions():
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")
    analyzer = LinkedInProfileAnalyzer(vault_path="AI_Employee_Vault")

    # Extract and analyze
    profile_data = await accessor.extract_profile_data("profile-id")

    # Generate suggestions
    suggestions = analyzer.generate_improvements(profile_data)

    # Print suggestions by priority
    print(f"\nImprovement Suggestions for {profile_data.name}")
    print("=" * 60)

    for priority in ["High", "Medium", "Low"]:
        priority_suggestions = [s for s in suggestions if s.priority == priority]
        if priority_suggestions:
            print(f"\n{priority} Priority:")
            for s in priority_suggestions:
                print(f"\n  {s.title}")
                print(f"  {s.description}")
                print(f"  Impact: {s.impact}")

asyncio.run(get_improvement_suggestions())
```

---

## Example 7: Export to CSV

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
import asyncio
import csv

async def export_to_csv():
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")

    # Extract data
    profile_data = await accessor.extract_profile_data("profile-id")

    # Write to CSV
    with open("profile_export.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Field", "Value"])

        writer.writerow(["Name", profile_data.name])
        writer.writerow(["Headline", profile_data.headline])
        writer.writerow(["Location", profile_data.location])
        writer.writerow(["About", profile_data.about])
        writer.writerow(["Connections", profile_data.connections_count])
        writer.writerow(["Completeness Score", profile_data.completeness_score])

        writer.writerow([])
        writer.writerow(["Experience"])

        for exp in profile_data.experience:
            writer.writerow([
                f"  {exp.title} at {exp.company}",
                f"{exp.start_date} - {exp.end_date or 'Present'}"
            ])

        writer.writerow([])
        writer.writerow(["Skills"])

        for skill in profile_data.skills:
            writer.writerow(["  " + skill.name, skill.endorsements])

    print("Profile exported to profile_export.csv")

asyncio.run(export_to_csv())
```

---

## Example 8: Using the Invoke Script

```bash
# Basic usage - analyze a profile
cd .claude/skills/linkedin-profile-accessor
python invoke.py "hamdan-mohammad-922486374"

# Output will be saved to:
# AI_Employee_Vault/Needs_Action/LINKEDIN_PROFILE_ANALYSIS_YYYYMMDD_HHMMSS.md
```

---

## Example 9: Using as a Standalone Script

```bash
# Run directly with command-line arguments
python .claude/skills/linkedin-profile-accessor/scripts/linkedin_profile_accessor.py \
    --profile-id "hamdan-mohammad-922486374" \
    --output "my_analysis.json" \
    --format json \
    --include-posts \
    --post-limit 20

# Dry run (no file output)
python .claude/skills/linkedin-profile-accessor/scripts/linkedin_profile_accessor.py \
    --profile-id "hamdan-mohammad-922486374" \
    --dry-run
```

---

## Example 10: Integration with Approval Workflow

```python
from pathlib import Path
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
import asyncio
import json

async def create_approval_request():
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")

    # Extract data
    profile_data = await accessor.extract_profile_data("profile-id")

    # Create approval request file
    vault_path = Path("AI_Employee_Vault")
    timestamp = profile_data.extracted_at.strftime("%Y%m%d_%H%M%S")

    approval_file = vault_path / "Needs_Action" / f"LINKEDIN_PROFILE_ANALYSIS_{timestamp}.md"

    # Generate markdown content
    content = f"""---
type: linkedin_profile_analysis
profile_id: {profile_data.profile_id}
profile_url: {profile_data.profile_url}
created: {profile_data.extracted_at.isoformat()}
status: pending_approval
---

# LinkedIn Profile Analysis: {profile_data.name}

## Profile Overview

| Field | Value |
|-------|-------|
| **Name** | {profile_data.name} |
| **Headline** | {profile_data.headline} |
| **Location** | {profile_data.location} |
| **Connections** | {profile_data.connections_count} |

## Completeness Score: {profile_data.completeness_score}/100

## Next Steps

1. Review this analysis
2. Move to `Approved/` to trigger LinkedIn Profile Builder
3. Apply improvements manually to LinkedIn profile

---
*Generated by LinkedIn Profile Accessor*
"""

    # Write file
    approval_file.write_text(content)
    print(f"Approval request created: {approval_file}")

    # Print JSON for Claude Code
    print(json.dumps({
        "status": "success",
        "action_file": str(approval_file),
        "next_steps": "Move to Approved/ to generate improvements"
    }))

asyncio.run(create_approval_request())
```

---

## Example 11: Screenshot Capture

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
import asyncio

async def capture_profile_screenshot():
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")

    # Extract with screenshot
    profile_data = await accessor.extract_profile_data(
        "profile-id",
        capture_screenshot=True
    )

    if profile_data.screenshot_path:
        print(f"Screenshot saved to: {profile_data.screenshot_path}")

asyncio.run(capture_profile_screenshot())
```

---

## Example 12: Error Handling

```python
from skills.linkedin_profile_accessor import LinkedInProfileAccessor
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def safe_profile_extraction():
    accessor = LinkedInProfileAccessor(vault_path="AI_Employee_Vault")

    try:
        profile_data = await accessor.extract_profile_data("profile-id")
        print(f"Successfully extracted profile for {profile_data.name}")

    except ConnectionError as e:
        print(f"Chrome connection failed: {e}")
        print("Make sure Chrome is running with CDP enabled")

    except TimeoutError as e:
        print(f"Timeout waiting for profile: {e}")
        print("Try increasing timeout parameter")

    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Check LinkedIn selectors - they may have changed")

asyncio.run(safe_profile_extraction())
```

---

## Common Patterns

### Pattern 1: Extract and Analyze

```python
accessor = LinkedInProfileAccessor()
analyzer = LinkedInProfileAnalyzer()

data = await accessor.extract_profile_data("profile-id")
score = analyzer.analyze_completeness(data)
```

### Pattern 2: Export Multiple Formats

```python
data = await accessor.extract_profile_data("profile-id")

accessor.save_profile_report(data, "report.md", format="markdown")
accessor.save_profile_report(data, "data.json", format="json")
accessor.save_profile_report(data, "data.csv", format="csv")
```

### Pattern 3: Rate Limiting

```python
profiles = ["id1", "id2", "id3"]

for profile_id in profiles:
    data = await accessor.extract_profile_data(profile_id)
    # Process data...
    await asyncio.sleep(3)  # Rate limiting
```

---

*Last Updated: 2026-01-23*
