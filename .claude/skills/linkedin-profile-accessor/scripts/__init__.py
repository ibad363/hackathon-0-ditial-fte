"""
LinkedIn Profile Accessor - Scripts Package

This package contains all scripts for the LinkedIn Profile Accessor skill.
"""

__version__ = "1.0.0"

from .profile_data_models import (
    ProfileData,
    ExperienceItem,
    EducationItem,
    SkillItem,
    PostItem,
    ConnectionItem,
    RecommendationItem,
    CompletenessScore,
    Suggestion,
    AnalysisReport,
    NetworkInsights,
    ActivityReport
)

__all__ = [
    "ProfileData",
    "ExperienceItem",
    "EducationItem",
    "SkillItem",
    "PostItem",
    "ConnectionItem",
    "RecommendationItem",
    "CompletenessScore",
    "Suggestion",
    "AnalysisReport",
    "NetworkInsights",
    "ActivityReport"
]
