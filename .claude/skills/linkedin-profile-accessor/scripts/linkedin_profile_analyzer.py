"""
LinkedIn Profile Analyzer - Profile Analysis Module

Analyzes LinkedIn profiles for completeness, strengths, weaknesses,
and generates improvement suggestions.
"""

import re
from pathlib import Path
from typing import List, Dict

from .profile_data_models import (
    ProfileData,
    CompletenessScore,
    Suggestion,
    AnalysisReport
)
from .linkedin_helpers import count_words, extract_keywords


class LinkedInProfileAnalyzer:
    """
    Analyzes LinkedIn profiles for completeness and improvement opportunities.

    Usage:
        analyzer = LinkedInProfileAnalyzer(vault_path="AI_Employee_Vault")
        score = analyzer.analyze_completeness(profile_data)
        strengths = analyzer.identify_strengths(profile_data)
        weaknesses = analyzer.identify_weaknesses(profile_data)
        suggestions = analyzer.generate_improvements(profile_data)
    """

    # Completeness scoring weights
    COMPLETENESS_WEIGHTS = {
        'headline': 10,       # Professional headline
        'about': 20,          # About section (300+ words)
        'photo': 10,          # Profile photo
        'experience': 25,     # At least 3 positions
        'education': 10,      # At least 1 entry
        'skills': 15,         # At least 10 skills
        'recommendations': 10  # At least 2 recommendations
    }

    # Thresholds for scoring
    ABOUT_WORD_COUNT_TARGET = 300
    EXPERIENCE_COUNT_TARGET = 3
    SKILLS_COUNT_TARGET = 10
    RECOMMENDATIONS_COUNT_TARGET = 2

    def __init__(self, vault_path: str | Path = "AI_Employee_Vault"):
        """
        Initialize the analyzer.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)

    def analyze_completeness(self, profile_data: ProfileData) -> CompletenessScore:
        """
        Calculate profile completeness score (0-100).

        Args:
            profile_data: ProfileData instance

        Returns:
            CompletenessScore with total score and breakdown
        """
        breakdown = {}
        missing_sections = []

        # Headline (10 points)
        if profile_data.headline and len(profile_data.headline) > 10:
            breakdown['headline'] = 10
        else:
            breakdown['headline'] = 0
            missing_sections.append('Professional headline')

        # About section (20 points)
        about_score = 0
        if profile_data.about_word_count >= self.ABOUT_WORD_COUNT_TARGET:
            about_score = 20
        elif profile_data.about_word_count >= 150:
            about_score = 15
        elif profile_data.about_word_count >= 50:
            about_score = 10
        elif profile_data.about_word_count > 0:
            about_score = 5
        else:
            missing_sections.append('About section')
        breakdown['about'] = about_score

        # Profile photo (10 points)
        breakdown['photo'] = 10 if profile_data.has_photo else 0
        if not profile_data.has_photo:
            missing_sections.append('Profile photo')

        # Experience (25 points)
        exp_count = len(profile_data.experience)
        if exp_count >= self.EXPERIENCE_COUNT_TARGET:
            breakdown['experience'] = 25
        elif exp_count >= 2:
            breakdown['experience'] = 15
        elif exp_count >= 1:
            breakdown['experience'] = 8
        else:
            breakdown['experience'] = 0
            missing_sections.append('Work experience')

        # Education (10 points)
        if len(profile_data.education) >= 1:
            breakdown['education'] = 10
        else:
            breakdown['education'] = 0
            missing_sections.append('Education')

        # Skills (15 points)
        skills_count = len(profile_data.skills)
        if skills_count >= self.SKILLS_COUNT_TARGET:
            breakdown['skills'] = 15
        elif skills_count >= 5:
            breakdown['skills'] = 10
        elif skills_count >= 1:
            breakdown['skills'] = 5
        else:
            breakdown['skills'] = 0
            missing_sections.append('Skills')

        # Recommendations (10 points)
        rec_count = len(profile_data.recommendations)
        if rec_count >= self.RECOMMENDATIONS_COUNT_TARGET:
            breakdown['recommendations'] = 10
        elif rec_count >= 1:
            breakdown['recommendations'] = 5
        else:
            breakdown['recommendations'] = 0
            missing_sections.append('Recommendations')

        # Calculate total score
        total_score = sum(breakdown.values())

        return CompletenessScore(
            total_score=total_score,
            breakdown=breakdown,
            missing_sections=missing_sections
        )

    def identify_strengths(self, profile_data: ProfileData) -> List[str]:
        """
        Identify profile strengths.

        Args:
            profile_data: ProfileData instance

        Returns:
            List of strength descriptions
        """
        strengths = []

        # Check for strong headline
        if profile_data.headline:
            headline_lower = profile_data.headline.lower()
            power_words = ['expert', 'senior', 'lead', 'manager', 'director', 'specialist', 'engineer']
            if any(word in headline_lower for word in power_words):
                strengths.append(f"Strong professional headline with clear role designation: '{profile_data.headline[:60]}...'")

            # Check for value proposition indicators
            if any(word in headline_lower for word in ['helping', 'driving', 'building', 'creating', 'delivering']):
                strengths.append("Headline communicates value proposition and impact")

        # Check about section
        if profile_data.about_word_count >= 300:
            strengths.append(f"Comprehensive about section ({profile_data.about_word_count} words) - exceeds best practice")
        elif profile_data.about_word_count >= 150:
            strengths.append(f"Well-developed about section ({profile_data.about_word_count} words)")

        # Check experience
        exp_count = len(profile_data.experience)
        if exp_count >= 5:
            strengths.append(f"Extensive work history with {exp_count} positions listed")
        elif exp_count >= 3:
            strengths.append(f"Solid work history with {exp_count} positions")

        # Check for experience progression
        if self._has_career_progression(profile_data.experience):
            strengths.append("Clear career progression with advancing titles")

        # Check skills
        skills_count = len(profile_data.skills)
        if skills_count >= 20:
            strengths.append(f"Extensive skill set with {skills_count} listed skills")
        elif skills_count >= 10:
            strengths.append(f"Good skill coverage with {skills_count} skills")

        # Check for skill endorsements
        high_endorsement_skills = [s for s in profile_data.skills if s.endorsements >= 10]
        if len(high_endorsement_skills) >= 5:
            strengths.append(f"{len(high_endorsement_skills)} skills with 10+ endorsements")

        # Check recommendations
        rec_count = len(profile_data.recommendations)
        if rec_count >= 3:
            strengths.append(f"Strong social proof with {rec_count} recommendations")

        # Check profile photo
        if profile_data.has_photo:
            strengths.append("Profile photo present (important for trust and engagement)")

        # Check recent activity
        if profile_data.posts:
            strengths.append(f"Active on LinkedIn with {len(profile_data.posts)} recent posts")

        # Check diverse experience
        companies = set(exp.company for exp in profile_data.experience if exp.company)
        if len(companies) >= 3:
            strengths.append(f"Diverse experience across {len(companies)} companies")

        return strengths

    def identify_weaknesses(self, profile_data: ProfileData) -> List[str]:
        """
        Identify profile weaknesses.

        Args:
            profile_data: ProfileData instance

        Returns:
            List of weakness descriptions
        """
        weaknesses = []

        # Check for missing headline
        if not profile_data.headline or len(profile_data.headline) < 10:
            weaknesses.append("Professional headline is missing or too short")

        # Check about section
        if not profile_data.about:
            weaknesses.append("No about section - critical for personal branding")
        elif profile_data.about_word_count < 100:
            weaknesses.append(f"About section is too short ({profile_data.about_word_count} words) - aim for 300+")

        # Check profile photo
        if not profile_data.has_photo:
            weaknesses.append("No profile photo - profiles with photos get 21x more views")

        # Check experience
        exp_count = len(profile_data.experience)
        if exp_count == 0:
            weaknesses.append("No work experience listed")
        elif exp_count < 3:
            weaknesses.append(f"Only {exp_count} position(s) listed - aim for at least 3")

        # Check for experience descriptions
        exp_without_desc = [exp for exp in profile_data.experience if not exp.description]
        if exp_without_desc:
            weaknesses.append(f"{len(exp_without_desc)} position(s) lack descriptions")

        # Check education
        if len(profile_data.education) == 0:
            weaknesses.append("No education listed")

        # Check skills
        skills_count = len(profile_data.skills)
        if skills_count == 0:
            weaknesses.append("No skills listed - critical for discoverability")
        elif skills_count < 10:
            weaknesses.append(f"Only {skills_count} skill(s) listed - aim for at least 10")

        # Check recommendations
        rec_count = len(profile_data.recommendations)
        if rec_count == 0:
            weaknesses.append("No recommendations - important for credibility")
        elif rec_count < 2:
            weaknesses.append("Only 1 recommendation - aim for at least 2-3")

        # Check for recent activity
        if not profile_data.posts:
            weaknesses.append("No recent posts - active engagement increases visibility")

        # Check for generic headline
        if profile_data.headline:
            generic_terms = ['looking for work', 'open to opportunities', 'aspiring']
            headline_lower = profile_data.headline.lower()
            if any(term in headline_lower for term in generic_terms):
                weaknesses.append("Headline contains generic terms - use specific role and value proposition")

        return weaknesses

    def generate_improvements(self, profile_data: ProfileData) -> List[Suggestion]:
        """
        Generate prioritized improvement suggestions.

        Args:
            profile_data: ProfileData instance

        Returns:
            List of Suggestion objects
        """
        suggestions = []

        # High priority suggestions
        if not profile_data.has_photo:
            suggestions.append(Suggestion(
                priority="High",
                title="Add a Professional Photo",
                description="Add a professional headshot. Profiles with photos receive up to 21x more profile views and 9x more connection requests. Ensure good lighting, professional attire, and a friendly expression.",
                impact="21x more profile views"
            ))

        if not profile_data.about or profile_data.about_word_count < 150:
            suggestions.append(Suggestion(
                priority="High",
                title="Expand About Section",
                description=f"Your about section is currently {profile_data.about_word_count} words. Expand to 300+ words covering: your unique value proposition, key achievements, work philosophy, and what drives you. Use storytelling to make it memorable.",
                impact="Increased connection requests and profile views"
            ))

        if len(profile_data.skills) < 10:
            needed = 10 - len(profile_data.skills)
            suggestions.append(Suggestion(
                priority="High",
                title=f"Add {needed}+ More Skills",
                description=f"You currently have {len(profile_data.skills)} skills. Add relevant technical and soft skills to improve discoverability in recruiter searches. Include both industry-standard tools and specialized expertise.",
                impact="Better search ranking and recruiter discovery"
            ))

        # Medium priority suggestions
        if not profile_data.headline or len(profile_data.headline) < 30:
            suggestions.append(Suggestion(
                priority="Medium",
                title="Optimize Professional Headline",
                description="Craft a compelling headline that communicates your role, expertise, and value. Format: 'Role | Specialization | Key Achievement'. Avoid generic terms like 'looking for work'.",
                impact="Improved first impression and searchability"
            ))

        exp_without_desc = [exp for exp in profile_data.experience if not exp.description]
        if exp_without_desc:
            suggestions.append(Suggestion(
                priority="Medium",
                title=f"Add Descriptions for {len(exp_without_desc)} Position(s)",
                description="Add bullet-point descriptions for each role highlighting achievements, responsibilities, and impact. Use numbers and metrics where possible (e.g., 'Increased sales by 40%', 'Led team of 5').",
                impact="Better demonstration of capabilities and impact"
            ))

        if len(profile_data.recommendations) < 2:
            suggestions.append(Suggestion(
                priority="Medium",
                title="Request Recommendations",
                description="Reach out to former colleagues, managers, or clients for recommendations. Aim for 2-3 strong recommendations that vouch for your work ethic, skills, and character. Offer to write one in return.",
                impact="Increased credibility and social proof"
            ))

        # Low priority suggestions
        if not profile_data.posts or len(profile_data.posts) < 3:
            suggestions.append(Suggestion(
                priority="Low",
                title="Increase Posting Activity",
                description="Share insights, articles, or updates 1-2 times per week. Consistent posting increases visibility, establishes thought leadership, and keeps your network engaged. Focus on value, not self-promotion.",
                impact="Increased engagement and network growth"
            ))

        if profile_data.headline and 'aspiring' in profile_data.headline.lower():
            suggestions.append(Suggestion(
                priority="Low",
                title="Remove 'Aspiring' from Headline",
                description="Replace 'aspiring' with confident language. Instead of 'Aspiring Data Scientist', use 'Data Scientist | Machine Learning | Python'. You are what you claim to be.",
                impact="More confident and professional impression"
            ))

        return suggestions

    def generate_analysis_report(self, profile_data: ProfileData) -> AnalysisReport:
        """
        Generate complete analysis report.

        Args:
            profile_data: ProfileData instance

        Returns:
            AnalysisReport with all analysis data
        """
        completeness = self.analyze_completeness(profile_data)
        strengths = self.identify_strengths(profile_data)
        weaknesses = self.identify_weaknesses(profile_data)
        suggestions = self.generate_improvements(profile_data)

        # Extract keywords
        text_parts = [
            profile_data.headline or "",
            profile_data.about or "",
            " ".join([skill.name for skill in profile_data.skills])
        ]
        combined_text = " ".join(text_parts)
        all_keywords = extract_keywords(combined_text)

        # Split into primary (top 10) and secondary (rest)
        primary_keywords = all_keywords[:10]
        secondary_keywords = all_keywords[10:30]

        return AnalysisReport(
            profile_data=profile_data,
            completeness=completeness,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            primary_keywords=primary_keywords,
            secondary_keywords=secondary_keywords
        )

    def _has_career_progression(self, experiences: List) -> bool:
        """Check if experience shows career progression."""
        if len(experiences) < 2:
            return False

        # Look for progression indicators
        progression_keywords = ['senior', 'lead', 'manager', 'director', 'head', 'chief', 'vp', 'principal']

        recent_titles = experiences[:2]
        older_titles = experiences[2:4] if len(experiences) > 2 else []

        recent_title_words = set()
        for exp in recent_titles:
            if exp.title:
                recent_title_words.update(exp.title.lower().split())

        older_title_words = set()
        for exp in older_titles:
            if exp.title:
                older_title_words.update(exp.title.lower().split())

        # Check if recent titles have progression indicators
        has_progression = any(
            keyword in " ".join(recent_title_words)
            for keyword in progression_keywords
        )

        return has_progression

    def get_missing_sections(self, profile_data: ProfileData) -> List[str]:
        """
        Get list of missing profile sections.

        Args:
            profile_data: ProfileData instance

        Returns:
            List of missing section names
        """
        completeness = self.analyze_completeness(profile_data)
        return completeness.missing_sections

    def get_section_scores(self, profile_data: ProfileData) -> Dict[str, int]:
        """
        Get scores for each profile section.

        Args:
            profile_data: ProfileData instance

        Returns:
            Dictionary of section names to scores
        """
        completeness = self.analyze_completeness(profile_data)
        return completeness.breakdown


# Convenience functions for backward compatibility
def analyze_profile_completeness(profile_data: ProfileData) -> CompletenessScore:
    """Analyze profile completeness score."""
    analyzer = LinkedInProfileAnalyzer()
    return analyzer.analyze_completeness(profile_data)


def get_profile_strengths(profile_data: ProfileData) -> List[str]:
    """Get list of profile strengths."""
    analyzer = LinkedInProfileAnalyzer()
    return analyzer.identify_strengths(profile_data)


def get_profile_weaknesses(profile_data: ProfileData) -> List[str]:
    """Get list of profile weaknesses."""
    analyzer = LinkedInProfileAnalyzer()
    return analyzer.identify_weaknesses(profile_data)


def get_improvement_suggestions(profile_data: ProfileData) -> List[Suggestion]:
    """Get improvement suggestions for profile."""
    analyzer = LinkedInProfileAnalyzer()
    return analyzer.generate_improvements(profile_data)
