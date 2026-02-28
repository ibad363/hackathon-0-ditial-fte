"""
LinkedIn Profile Accessor - Data Models

Defines all data models used for LinkedIn profile data extraction and analysis.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum


class Priority(Enum):
    """Suggestion priority levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class ExperienceItem:
    """Represents a work experience entry."""
    title: str
    company: str
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    company_url: Optional[str] = None

    def __post_init__(self):
        """Clean up dates."""
        if self.end_date == "Present":
            self.end_date = None


@dataclass
class EducationItem:
    """Represents an education entry."""
    school: str
    degree: str
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    graduation_year: Optional[int] = None
    description: Optional[str] = None


@dataclass
class SkillItem:
    """Represents a skill with endorsements."""
    name: str
    endorsements: int = 0


@dataclass
class PostItem:
    """Represents a LinkedIn post."""
    text: str
    date: str
    reactions: int = 0
    comments: int = 0
    reposts: int = 0
    url: Optional[str] = None


@dataclass
class ConnectionItem:
    """Represents a LinkedIn connection."""
    name: str
    headline: str
    company: Optional[str] = None
    mutual: int = 0
    url: Optional[str] = None


@dataclass
class RecommendationItem:
    """Represents a recommendation."""
    author_name: str
    author_title: str
    author_company: str
    text: str
    date: str
    url: Optional[str] = None


@dataclass
class ProfileData:
    """Complete LinkedIn profile data."""
    profile_id: str
    name: str
    headline: str
    location: Optional[str] = None
    about: Optional[str] = None
    about_word_count: int = 0
    experience: List[ExperienceItem] = field(default_factory=list)
    education: List[EducationItem] = field(default_factory=list)
    skills: List[SkillItem] = field(default_factory=list)
    posts: List[PostItem] = field(default_factory=list)
    recommendations: List[RecommendationItem] = field(default_factory=list)
    connections_count: Optional[int] = None
    profile_url: str = ""
    profile_photo_url: Optional[str] = None
    has_photo: bool = False
    extracted_at: datetime = field(default_factory=datetime.now)
    completeness_score: Optional[int] = None
    screenshot_path: Optional[str] = None

    def get_primary_keywords(self) -> List[str]:
        """Extract primary keywords from headline and skills."""
        keywords = set()

        # From headline
        if self.headline:
            words = self.headline.replace("|", " ").replace(",", " ").split()
            keywords.update([w for w in words if len(w) > 3])

        # From skills
        keywords.update([skill.name.lower() for skill in self.skills[:10]])

        return sorted(list(keywords))

    def get_experience_years(self) -> int:
        """Calculate total years of experience."""
        if not self.experience:
            return 0

        total_years = 0
        for exp in self.experience:
            start_year = int(exp.start_date.split()[-1]) if exp.start_date else 0
            if exp.end_date:
                end_year = int(exp.end_date.split()[-1])
            else:
                end_year = datetime.now().year
            total_years += max(0, end_year - start_year)

        return total_years


@dataclass
class CompletenessScore:
    """Profile completeness analysis."""
    total_score: int
    breakdown: dict = field(default_factory=dict)
    missing_sections: List[str] = field(default_factory=list)

    def get_grade(self) -> str:
        """Get letter grade for score."""
        if self.total_score >= 90:
            return "A"
        elif self.total_score >= 80:
            return "B"
        elif self.total_score >= 70:
            return "C"
        elif self.total_score >= 60:
            return "D"
        else:
            return "F"


@dataclass
class Suggestion:
    """Improvement suggestion."""
    priority: str
    title: str
    description: str
    impact: str


@dataclass
class AnalysisReport:
    """Complete profile analysis report."""
    profile_data: ProfileData
    completeness: CompletenessScore
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    suggestions: List[Suggestion] = field(default_factory=list)
    primary_keywords: List[str] = field(default_factory=list)
    secondary_keywords: List[str] = field(default_factory=list)


@dataclass
class NetworkInsights:
    """Network analysis results."""
    total_connections: int
    mutual_connections: int
    industry_breakdown: dict = field(default_factory=dict)
    company_breakdown: dict = field(default_factory=dict)
    seniority_breakdown: dict = field(default_factory=dict)
    top_connections: List[ConnectionItem] = field(default_factory=list)


@dataclass
class ActivityReport:
    """Activity pattern analysis."""
    posts_per_week: float
    best_day: str
    best_time: str
    engagement_rate: float
    avg_reactions: float
    avg_comments: float
