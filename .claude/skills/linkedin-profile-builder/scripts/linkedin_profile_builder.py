"""
LinkedIn Profile Builder - Core Module

Generates AI-optimized LinkedIn profile content drafts.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, TYPE_CHECKING, Any

# Add parent skills directory to path for cross-skill imports
_skill_root = Path(__file__).parent.parent.parent
if str(_skill_root) not in sys.path:
    sys.path.insert(0, str(_skill_root))

from .draft_models import (
    HeadlineDraft,
    AboutDraft,
    ExperienceDraft,
    SkillsRecommendation,
    ProfileDrafts,
    Keywords,
    MissingSection,
    ProfileAnalysis
)
from .linkedin_content_generator import LinkedInContentGenerator, TemplateContentGenerator
from .linkedin_seo_optimizer import LinkedInSEOOptimizer

# Use TYPE_CHECKING for forward references
if TYPE_CHECKING:
    # Import ProfileData only during type checking
    try:
        from ..linkedin_profile_accessor.scripts.profile_data_models import ProfileData
    except ImportError:
        ProfileData = Any  # Fallback to Any if import fails
else:
    # Runtime - use Any type to avoid circular import
    ProfileData = Any


class LinkedInProfileBuilder:
    """
    Generates AI-optimized LinkedIn profile content.

    Usage:
        builder = LinkedInProfileBuilder(vault_path="AI_Employee_Vault")
        drafts = await builder.generate_improvement_drafts(
            profile_id="profile-id",
            target_role="Senior AI Engineer"
        )
        builder.save_drafts(drafts, "output.md")
    """

    def __init__(
        self,
        vault_path: str | Path = "AI_Employee_Vault",
        api_key: Optional[str] = None,
        model: str = "glm-4"
    ):
        """
        Initialize the builder.

        Args:
            vault_path: Path to the Obsidian vault
            api_key: GLM API key (default: from ZHIPU_API_KEY env var)
            model: GLM model to use
        """
        self.vault_path = Path(vault_path)
        self.model = model

        # Initialize content generator
        try:
            self.content_generator = LinkedInContentGenerator(
                api_key=api_key,
                model=model
            )
        except Exception:
            # Fallback to template generator
            self.content_generator = TemplateContentGenerator()

        # Initialize SEO optimizer
        self.seo_optimizer = LinkedInSEOOptimizer(vault_path=vault_path)

    async def analyze_current_profile(self, profile_id: str) -> ProfileAnalysis:
        """
        Analyze the current LinkedIn profile.

        Args:
            profile_id: LinkedIn profile ID

        Returns:
            ProfileAnalysis with current state

        Raises:
            ImportError: If accessor modules cannot be imported
            Exception: If profile extraction or analysis fails
        """
        # Lazy import to avoid circular dependency
        try:
            from linkedin_profile_accessor.scripts.linkedin_profile_accessor import LinkedInProfileAccessor
            from linkedin_profile_accessor.scripts.linkedin_profile_analyzer import LinkedInProfileAnalyzer
        except ImportError as e:
            raise ImportError(
                "Could not import linkedin-profile-accessor modules. "
                "Ensure that skill is in the skills directory."
            ) from e

        # Extract profile data
        accessor = LinkedInProfileAccessor(vault_path=self.vault_path)
        profile_data = await accessor.extract_profile_data(profile_id)

        # Analyze
        analyzer = LinkedInProfileAnalyzer(vault_path=self.vault_path)
        completeness = analyzer.analyze_completeness(profile_data)
        strengths = analyzer.identify_strengths(profile_data)
        weaknesses = analyzer.identify_weaknesses(profile_data)
        missing = analyzer.get_missing_sections(profile_data)

        # Extract keywords
        keywords = self.seo_optimizer.extract_keywords(profile_data)

        return ProfileAnalysis(
            profile_data=profile_data,
            completeness_score=completeness.total_score,
            strengths=strengths,
            weaknesses=weaknesses,
            missing_sections=missing,
            current_keywords=keywords.primary
        )

    def generate_headline_draft(
        self,
        profile_data: Any,  # ProfileData from accessor
        target_role: str,
        tone: str = "professional"
    ) -> HeadlineDraft:
        """
        Generate optimized headline.

        Args:
            profile_data: Current profile data
            target_role: Target job role
            tone: Content tone

        Returns:
            HeadlineDraft with suggestions
        """
        # Build context
        context = {
            "current_role": profile_data.headline or "",
            "target_role": target_role,
            "industry": self._extract_industry(profile_data),
            "expertise": [s.name for s in profile_data.skills[:10]],
            "achievements": self._extract_achievements(profile_data),
            "tone": tone
        }

        # Generate using AI
        suggested = self.content_generator.generate_headline(context)

        # Get SEO keywords
        keywords = self.seo_optimizer.suggest_keywords(
            self._extract_industry(profile_data),
            target_role
        )

        # Generate alternatives
        options = self._generate_headline_alternatives(
            profile_data,
            target_role,
            keywords
        )

        return HeadlineDraft(
            current=profile_data.headline or "",
            suggested=suggested,
            reasoning=self._headline_reasoning(profile_data, suggested),
            character_count=len(suggested),
            seo_keywords=keywords.primary[:5],
            options=options[:5],
            score=self._score_headline(suggested, keywords)
        )

    def generate_about_draft(
        self,
        profile_data: Any,
        target_role: str,
        tone: str = "professional",
        target_length: int = 300
    ) -> AboutDraft:
        """
        Generate optimized about section.

        Args:
            profile_data: Current profile data
            target_role: Target job role
            tone: Content tone
            target_length: Target word count

        Returns:
            AboutDraft with suggestions
        """
        # Build context
        context = {
            "current_role": target_role,
            "years_experience": profile_data.get_experience_years(),
            "industry": self._extract_industry(profile_data),
            "expertise": [s.name for s in profile_data.skills[:10]],
            "achievements": self._extract_achievements(profile_data),
            "passion": "delivering impactful results",
            "tone": tone
        }

        # Generate using AI
        suggested = self.content_generator.generate_about(context, target_length)

        # Count words
        word_count = len(suggested.split())

        # Get SEO keywords
        keywords = self.seo_optimizer.suggest_keywords(
            self._extract_industry(profile_data),
            target_role
        )

        # Generate alternatives
        options = self._generate_about_alternatives(
            profile_data,
            target_role,
            tone
        )

        return AboutDraft(
            current=profile_data.about or "",
            suggested=suggested,
            reasoning=self._about_reasoning(profile_data, suggested),
            word_count=word_count,
            seo_keywords=keywords.primary[:7],
            options=options[:3],
            score=self._score_about(suggested, keywords)
        )

    def generate_experience_updates(
        self,
        profile_data: Any,
        target_role: str
    ) -> List[ExperienceDraft]:
        """
        Generate enhanced experience descriptions.

        Args:
            profile_data: Current profile data
            target_role: Target job role

        Returns:
            List of ExperienceDraft objects
        """
        drafts = []

        for exp in profile_data.experience:
            # Build context
            context = {
                "duration": f"{exp.start_date} - {exp.end_date or 'Present'}",
                "achievements": self._parse_achievements(exp.description),
                "responsibilities": self._parse_responsibilities(exp.description),
                "team_size": "",
                "tools": [s.name for s in profile_data.skills if s.name],
                "tone": "professional"
            }

            # Generate enhanced description
            try:
                enhanced = self.content_generator.generate_experience_description(
                    exp.title,
                    exp.company,
                    context
                )
            except Exception:
                # Fallback to original
                enhanced = exp.description or ""

            # Score improvement
            current_score = self._score_experience_description(exp.description or "")
            enhanced_score = self._score_experience_description(enhanced)

            draft = ExperienceDraft(
                title=exp.title,
                company=exp.company,
                current_description=exp.description or "",
                enhanced_description=enhanced,
                improvements=self._identify_improvements(exp.description or "", enhanced),
                current_score=current_score,
                enhanced_score=enhanced_score,
                score_improvement=enhanced_score - current_score
            )

            drafts.append(draft)

        return drafts

    def identify_missing_sections(
        self,
        profile_data: Any,
        target_role: str
    ) -> List[MissingSection]:
        """
        Identify missing profile sections.

        Args:
            profile_data: Current profile data
            target_role: Target job role

        Returns:
            List of MissingSection objects
        """
        missing = []
        keywords = self.seo_optimizer.suggest_keywords(
            self._extract_industry(profile_data),
            target_role
        )

        # Check about
        if not profile_data.about or len(profile_data.about) < 100:
            missing.append(MissingSection(
                section_name="About",
                why_missing="Too short or missing",
                recommended_content="Add 300-word about section with your story, skills, and achievements",
                priority="high"
            ))

        # Check experience descriptions
        exp_without_desc = [exp for exp in profile_data.experience if not exp.description]
        if exp_without_desc:
            missing.append(MissingSection(
                section_name="Experience Descriptions",
                why_missing=f"{len(exp_without_desc)} positions lack descriptions",
                recommended_content="Add achievement-focused descriptions for each position",
                priority="medium"
            ))

        # Check skills
        if len(profile_data.skills) < 15:
            needed = 15 - len(profile_data.skills)
            missing.append(MissingSection(
                section_name="Skills",
                why_missing=f"Only {len(profile_data.skills)} skills (recommend 15+)",
                recommended_content=f"Add these skills: {', '.join(keywords.primary[:needed])}",
                priority="high"
            ))

        return missing

    async def generate_improvement_drafts(
        self,
        profile_id: str,
        target_role: str,
        tone: str = "professional",
        include_seo: bool = True
    ) -> ProfileDrafts:
        """
        Generate complete set of improvement drafts.

        Args:
            profile_id: LinkedIn profile ID
            target_role: Target job role
            tone: Content tone
            include_seo: Whether to include SEO optimization

        Returns:
            ProfileDrafts with all improvements
        """
        # Analyze current profile
        analysis = await self.analyze_current_profile(profile_id)
        profile_data = analysis.profile_data

        # Generate headline
        headline = self.generate_headline_draft(profile_data, target_role, tone)

        # Generate about
        about = self.generate_about_draft(profile_data, target_role, tone)

        # Generate experience updates
        experiences = self.generate_experience_updates(profile_data, target_role)

        # Generate skills recommendations
        skills_recs = self._generate_skills_recommendations(
            profile_data,
            target_role
        )

        # Identify missing sections
        missing_sections = self.identify_missing_sections(profile_data, target_role)

        # Get SEO keywords
        seo_keywords = Keywords()
        if include_seo:
            seo_keywords = self.seo_optimizer.suggest_keywords(
                self._extract_industry(profile_data),
                target_role
            )

        return ProfileDrafts(
            profile_id=profile_id,
            target_role=target_role,
            headline=headline,
            about=about,
            experiences=experiences,
            skills_recommendations=skills_recs,
            missing_sections=missing_sections,
            seo_keywords=seo_keywords,
            generated_at=datetime.now(),
            tone=tone,
            include_seo=include_seo
        )

    def save_drafts(
        self,
        drafts: ProfileDrafts,
        output_path: str | Path,
        format: str = "markdown"
    ) -> Path:
        """
        Save drafts to file.

        Args:
            drafts: ProfileDrafts object
            output_path: Output file path
            format: Output format

        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            self._save_json(drafts, output_path)
        else:
            self._save_markdown(drafts, output_path)

        return output_path

    def _save_json(self, drafts: ProfileDrafts, output_path: Path) -> None:
        """Save as JSON."""
        import json
        from dataclasses import asdict

        data = asdict(drafts)
        data["generated_at"] = drafts.generated_at.isoformat()

        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _save_markdown(self, drafts: ProfileDrafts, output_path: Path) -> None:
        """Save as Markdown."""
        # Generate markdown content
        content = self._generate_markdown(drafts)
        output_path.write_text(content, encoding="utf-8")

    def _generate_markdown(self, drafts: ProfileDrafts) -> str:
        """Generate markdown from drafts."""
        content = f"""# LinkedIn Profile Improvement Drafts

## Profile Overview
- **Profile ID:** {drafts.profile_id}
- **Target Role:** {drafts.target_role}
- **Generated:** {drafts.generated_at.strftime('%Y-%m-%d %H:%M:%S')}

## 1. Headline

**Suggested:**
```
{drafts.headline.suggested}
```

## 2. About Section

**Suggested:**
```
{drafts.about.suggested}
```

## 3. Experience Updates

"""
        for exp in drafts.experiences:
            content += f"### {exp.title} at {exp.company}\n\n"
            content += f"**Enhanced:**\n```\n{exp.enhanced_description}\n```\n\n"

        content += f"""## 4. Skills Recommendations

"""
        for skill in drafts.skills_recommendations[:10]:
            content += f"- **{skill.name}** - {skill.reason}\n"

        return content

    # Helper methods
    def _extract_industry(self, profile_data: Any) -> str:
        """Extract industry from profile."""
        headline_lower = profile_data.headline.lower() if profile_data.headline else ""

        industry_map = {
            "software": "Technology",
            "engineer": "Technology",
            "developer": "Technology",
            "data": "Technology",
            "product": "Product",
            "design": "Design",
            "marketing": "Marketing",
            "sales": "Sales"
        }

        for key, industry in industry_map.items():
            if key in headline_lower:
                return industry

        return "Business"

    def _extract_achievements(self, profile_data: Any) -> List[str]:
        """Extract achievements from profile."""
        achievements = []

        # From experience
        for exp in profile_data.experience[:3]:
            if exp.description:
                # Look for achievement indicators
                desc_lower = exp.description.lower()
                if any(word in desc_lower for word in ["led", "built", "developed", "increased", "reduced"]):
                    achievements.append(f"{exp.title} at {exp.company}")

        return achievements[:5]

    def _generate_headline_alternatives(
        self,
        profile_data: Any,
        target_role: str,
        keywords: Keywords
    ) -> List[str]:
        """Generate alternative headline options."""
        alternatives = []

        # Option 1: Role + Skills
        skills_str = " | ".join(keywords.primary[:3])
        alternatives.append(f"{target_role} | {skills_str}")

        # Option 2: Achievement focused
        if profile_data.experience:
            company = profile_data.experience[0].company
            alternatives.append(f"{target_role} at {company} | Building impact at scale")

        # Option 3: Minimal
        alternatives.append(f"{target_role} | {keywords.primary[0]}")

        return alternatives

    def _generate_about_alternatives(
        self,
        profile_data: Any,
        target_role: str,
        tone: str
    ) -> List[str]:
        """Generate alternative about sections."""
        alternatives = []

        # Would generate different versions based on tone
        # For now, return empty list
        return alternatives

    def _generate_skills_recommendations(
        self,
        profile_data: Any,
        target_role: str
    ) -> List[SkillsRecommendation]:
        """Generate skills recommendations."""
        keywords = self.seo_optimizer.suggest_keywords(
            self._extract_industry(profile_data),
            target_role
        )

        current_skills = set(s.name.lower() for s in profile_data.skills)
        recommendations = []

        for keyword in keywords.primary[:20]:
            if keyword.lower() not in current_skills:
                recommendations.append(SkillsRecommendation(
                    name=keyword,
                    reason=f"In-demand skill for {target_role} roles",
                    priority="high" if keyword in keywords.primary[:5] else "medium",
                    demand="high"
                ))

        return recommendations[:15]

    def _headline_reasoning(self, profile_data: Any, suggested: str) -> str:
        """Generate reasoning for headline suggestion."""
        reasons = [
            "Uses specific role title for clarity",
            "Includes key skills for discoverability",
            "Adds value proposition or achievement",
            "Follows LinkedIn best practices for length"
        ]
        return "; ".join(reasons)

    def _about_reasoning(self, profile_data: Any, suggested: str) -> str:
        """Generate reasoning for about suggestion."""
        word_count = len(suggested.split())
        reasons = [
            f"Optimal length ({word_count} words)",
            "Professional storytelling structure",
            "Keywords naturally integrated",
            "Authentic and engaging voice"
        ]
        return "; ".join(reasons)

    def _score_headline(self, headline: str, keywords: Keywords) -> int:
        """Score headline quality (0-100)."""
        score = 0

        # Length check
        if 100 <= len(headline) <= 220:
            score += 30

        # Keywords check
        keyword_count = sum(1 for kw in keywords.primary if kw.lower() in headline.lower())
        score += min(keyword_count * 15, 50)

        # Structure check (has separators)
        if "|" in headline or "•" in headline:
            score += 20

        return min(score, 100)

    def _score_about(self, about: str, keywords: Keywords) -> int:
        """Score about quality (0-100)."""
        score = 0

        # Length check
        word_count = len(about.split())
        if 200 <= word_count <= 400:
            score += 30
        elif word_count >= 150:
            score += 20

        # Keywords check
        keyword_count = sum(1 for kw in keywords.primary if kw.lower() in about.lower())
        score += min(keyword_count * 5, 40)

        # Structure check
        if any(about.lower().startswith(word) for word in ["i am", "i'm a", "passionate"]):
            score += 15

        # Engaging language
        engaging_words = ["passionate", "driven", "focused", "dedicated", "love"]
        if any(word in about.lower() for word in engaging_words):
            score += 15

        return min(score, 100)

    def _score_experience_description(self, description: str) -> int:
        """Score experience description (0-100)."""
        if not description:
            return 0

        score = 0

        # Length check
        if len(description) >= 50:
            score += 20

        # Action verbs
        action_verbs = ["led", "built", "developed", "created", "managed", "increased", "reduced"]
        if any(verb in description.lower() for verb in action_verbs):
            score += 40

        # Numbers/metrics
        if any(char.isdigit() for char in description):
            score += 40

        return min(score, 100)

    def _parse_achievements(self, description: Optional[str]) -> List[str]:
        """Parse achievements from description."""
        if not description:
            return []

        # Split by common delimiters
        achievements = []
        for delimiter in ["\n", "•", "-", "*"]:
            if delimiter in description:
                achievements = [a.strip() for a in description.split(delimiter) if a.strip()]
                break

        return achievements[:5]

    def _parse_responsibilities(self, description: Optional[str]) -> List[str]:
        """Parse responsibilities from description."""
        return self._parse_achievements(description)

    def _identify_improvements(self, current: str, enhanced: str) -> List[str]:
        """Identify improvements made."""
        improvements = []

        if len(enhanced) > len(current):
            improvements.append("Expanded content with more details")

        # Check for action verbs
        action_verbs = ["led", "built", "developed", "created", "managed"]
        if any(verb in enhanced.lower() for verb in action_verbs):
            improvements.append("Added action-oriented language")

        # Check for numbers
        if any(char.isdigit() for char in enhanced) and not any(char.isdigit() for char in current):
            improvements.append("Added quantifiable metrics")

        return improvements


# Synchronous wrappers
def generate_headline_sync(
    profile_data: Any,
    target_role: str,
    tone: str = "professional"
) -> HeadlineDraft:
    """Synchronous wrapper for generate_headline_draft."""
    builder = LinkedInProfileBuilder()
    return builder.generate_headline_draft(profile_data, target_role, tone)


def generate_about_sync(
    profile_data: Any,
    target_role: str,
    tone: str = "professional",
    target_length: int = 300
) -> AboutDraft:
    """Synchronous wrapper for generate_about_draft."""
    builder = LinkedInProfileBuilder()
    return builder.generate_about_draft(profile_data, target_role, tone, target_length)
