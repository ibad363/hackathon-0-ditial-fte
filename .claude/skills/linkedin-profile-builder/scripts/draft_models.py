"""
LinkedIn Profile Builder - Data Models

Defines all data models used for LinkedIn profile draft generation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Any
from enum import Enum


class Priority(Enum):
    """Priority levels for recommendations."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Tone(Enum):
    """Content tone options."""
    PROFESSIONAL = "professional"
    CONFIDENT = "confident"
    CASUAL = "casual"
    TECHNICAL = "technical"


@dataclass
class HeadlineDraft:
    """Generated headline draft."""
    current: str
    suggested: str
    reasoning: str
    character_count: int
    seo_keywords: List[str] = field(default_factory=list)
    options: List[str] = field(default_factory=list)
    score: int = 0  # Quality score 0-100


@dataclass
class AboutDraft:
    """Generated about section draft."""
    current: str
    suggested: str
    reasoning: str
    word_count: int
    seo_keywords: List[str] = field(default_factory=list)
    options: List[str] = field(default_factory=list)
    score: int = 0  # Quality score 0-100


@dataclass
class ExperienceDraft:
    """Generated experience description draft."""
    title: str
    company: str
    current_description: str
    enhanced_description: str
    improvements: List[str] = field(default_factory=list)
    current_score: int = 0
    enhanced_score: int = 0
    score_improvement: int = 0


@dataclass
class SkillsRecommendation:
    """Skill recommendation."""
    name: str
    reason: str
    priority: str  # high, medium, low
    demand: str = "medium"  # high, medium, low


@dataclass
class MissingSection:
    """Missing profile section."""
    section_name: str
    why_missing: str
    recommended_content: str
    priority: str = "medium"


@dataclass
class Keywords:
    """SEO keywords categorized by importance."""
    primary: List[str] = field(default_factory=list)    # Top 10
    secondary: List[str] = field(default_factory=list)  # Next 20
    long_tail: List[str] = field(default_factory=list)  # Niche keywords


@dataclass
class ProfileDrafts:
    """Complete set of profile improvement drafts."""
    profile_id: str
    target_role: str
    headline: HeadlineDraft
    about: AboutDraft
    experiences: List[ExperienceDraft] = field(default_factory=list)
    skills_recommendations: List[SkillsRecommendation] = field(default_factory=list)
    missing_sections: List[MissingSection] = field(default_factory=list)
    seo_keywords: Keywords = field(default_factory=Keywords)
    generated_at: datetime = field(default_factory=datetime.now)
    tone: str = "professional"
    include_seo: bool = True

    def get_summary(self) -> dict:
        """Get summary of drafts."""
        return {
            "profile_id": self.profile_id,
            "target_role": self.target_role,
            "headline_character_count": self.headline.character_count,
            "about_word_count": self.about.word_count,
            "experience_count": len(self.experiences),
            "skills_count": len(self.skills_recommendations),
            "primary_keywords_count": len(self.seo_keywords.primary),
            "generated_at": self.generated_at.isoformat()
        }


@dataclass
class ProfileAnalysis:
    """Result of profile analysis."""
    profile_data: "ProfileData"
    completeness_score: int
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    missing_sections: List[str] = field(default_factory=list)
    current_keywords: List[str] = field(default_factory=list)


@dataclass
class GenerationRequest:
    """Request for content generation."""
    profile_id: str
    target_role: str
    tone: str = "professional"
    include_seo: bool = True
    about_length: int = 300
    generate_headline: bool = True
    generate_about: bool = True
    generate_experiences: bool = True
    generate_skills: bool = True


@dataclass
class GenerationResult:
    """Result of content generation."""
    success: bool
    drafts: Optional[ProfileDrafts] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "drafts": self.drafts.get_summary() if self.drafts else None,
            "error": self.error,
            "warnings": self.warnings
        }
