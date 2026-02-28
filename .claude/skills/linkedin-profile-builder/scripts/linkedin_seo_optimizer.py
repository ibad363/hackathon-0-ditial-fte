"""
LinkedIn SEO Optimizer - SEO Optimization Module

Analyzes and optimizes LinkedIn profiles for search engine optimization
and recruiter discovery.
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import List, Dict, Optional

from .draft_models import Keywords


class LinkedInSEOOptimizer:
    """
    Optimizes LinkedIn profiles for SEO.

    Usage:
        optimizer = LinkedInSEOOptimizer(vault_path="AI_Employee_Vault")
        keywords = optimizer.suggest_keywords("Technology", "Software Engineer")
        gaps = optimizer.analyze_keyword_gaps(profile_data, "Senior Engineer")
    """

    def __init__(self, vault_path: str | Path = "AI_Employee_Vault"):
        """
        Initialize the SEO optimizer.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.keyword_database = self._load_keyword_database()

    def extract_keywords(self, profile_data: "ProfileData") -> Keywords:
        """
        Extract keywords from profile data.

        Args:
            profile_data: ProfileData instance

        Returns:
            Keywords object with categorized keywords
        """
        # Combine text from all profile sections
        text_parts = [
            profile_data.headline or "",
            profile_data.about or "",
            " ".join([skill.name for skill in profile_data.skills]),
            " ".join([exp.title + " " + (exp.description or "") for exp in profile_data.experience])
        ]

        combined_text = " ".join(text_parts).lower()

        # Extract keywords
        all_keywords = self._extract_keywords_from_text(combined_text)

        # Categorize by frequency
        keyword_counts = Counter(all_keywords)

        # Primary: top 10 most frequent
        primary = [kw for kw, _ in keyword_counts.most_common(10)]

        # Secondary: next 20
        secondary = [kw for kw, _ in keyword_counts.most_common(30)[10:]]

        # Long tail: remaining relevant keywords
        long_tail = [kw for kw, _ in keyword_counts.most_common(100)[30:]]

        return Keywords(
            primary=primary,
            secondary=secondary,
            long_tail=long_tail
        )

    def analyze_keyword_gaps(
        self,
        profile_data: "ProfileData",
        target_role: str
    ) -> List[str]:
        """
        Identify keywords missing from profile.

        Args:
            profile_data: ProfileData instance
            target_role: Target job role

        Returns:
            List of missing keywords
        """
        # Get current keywords
        current_keywords = set(self.extract_keywords(profile_data).primary)
        current_keywords.update(self.extract_keywords(profile_data).secondary)

        # Get expected keywords for role
        expected_keywords = self._get_keywords_for_role(target_role)
        expected_set = set(expected_keywords)

        # Find gaps
        gaps = expected_set - current_keywords

        return sorted(list(gaps))

    def suggest_keywords(
        self,
        industry: str,
        role: str
    ) -> Keywords:
        """
        Suggest keywords based on industry and role.

        Args:
            industry: Industry name
            role: Job role

        Returns:
            Keywords with suggestions
        """
        # Get keywords from database
        role_key = self._normalize_role_key(role)
        keywords_data = self.keyword_database.get(role_key, {})

        if keywords_data:
            return Keywords(
                primary=keywords_data.get("primary", []),
                secondary=keywords_data.get("secondary", []),
                long_tail=keywords_data.get("long_tail", [])
            )

        # Fallback: generate based on role name
        return self._generate_keywords_from_role(role)

    def optimize_content(
        self,
        content: str,
        keywords: List[str]
    ) -> str:
        """
        Optimize content by naturally integrating keywords.

        Args:
            content: Original content
            keywords: Keywords to integrate

        Returns:
            Optimized content
        """
        # This is a simple implementation
        # In production, you'd use more sophisticated NLP

        # For now, just return original content
        # Real implementation would:
        # 1. Identify natural insertion points
        # 2. Integrate keywords without disrupting flow
        # 3. Maintain original voice and tone

        return content

    def calculate_seo_score(
        self,
        profile_data: "ProfileData",
        target_role: str
    ) -> Dict:
        """
        Calculate SEO score for profile.

        Args:
            profile_data: ProfileData instance
            target_role: Target job role

        Returns:
            Dictionary with SEO score and breakdown
        """
        expected_keywords = self._get_keywords_for_role(target_role)
        current_keywords = self.extract_keywords(profile_data)

        # Check headline
        headline_score = self._score_section(
            profile_data.headline or "",
            expected_keywords
        )

        # Check about
        about_score = self._score_section(
            profile_data.about or "",
            expected_keywords
        )

        # Check skills
        skills_score = self._score_skills(
            profile_data.skills,
            expected_keywords
        )

        # Calculate overall score
        weights = {"headline": 0.3, "about": 0.4, "skills": 0.3}
        overall_score = (
            headline_score * weights["headline"] +
            about_score * weights["about"] +
            skills_score * weights["skills"]
        ) * 100

        return {
            "overall_score": round(overall_score),
            "headline_score": round(headline_score * 100),
            "about_score": round(about_score * 100),
            "skills_score": round(skills_score * 100),
            "keyword_coverage": self._calculate_coverage(
                current_keywords.primary,
                expected_keywords
            )
        }

    def _load_keyword_database(self) -> Dict:
        """Load SEO keyword database."""
        keywords_path = self.vault_path / ".claude" / "skills" / "linkedin-profile-builder" / "keywords" / "seo_keywords.json"

        # Try vault path first
        if not keywords_path.exists():
            # Try relative path
            keywords_path = Path(__file__).parent.parent / "keywords" / "seo_keywords.json"

        if keywords_path.exists():
            with open(keywords_path) as f:
                return json.load(f)

        # Return default database
        return self._get_default_database()

    def _get_default_database(self) -> Dict:
        """Get default keyword database."""
        return {
            "software_engineer": {
                "primary": [
                    "Python", "JavaScript", "Java", "C++", "TypeScript",
                    "AWS", "Azure", "GCP", "Kubernetes", "Docker"
                ],
                "secondary": [
                    "Microservices", "REST API", "CI/CD", "Git",
                    "React", "Node.js", "SQL", "NoSQL", "MongoDB", "PostgreSQL"
                ],
                "long_tail": [
                    "Serverless architecture", "Event-driven systems",
                    "Distributed computing", "Cloud-native development"
                ]
            },
            "data_scientist": {
                "primary": [
                    "Machine Learning", "Python", "SQL", "Statistics",
                    "TensorFlow", "PyTorch", "R", "Data Analysis"
                ],
                "secondary": [
                    "NLP", "Deep Learning", "Data Visualization",
                    "Tableau", "Power BI", "Jupyter", "Pandas", "NumPy"
                ],
                "long_tail": [
                    "Natural Language Processing", "Computer Vision",
                    "Predictive modeling", "A/B testing"
                ]
            },
            "product_manager": {
                "primary": [
                    "Product Management", "Agile", "Scrum", "Roadmapping",
                    "User Research", "Product Strategy", "Stakeholder Management"
                ],
                "secondary": [
                    "Jira", "Confluence", "SQL", "Data Analysis",
                    "A/B Testing", "User Stories", "Sprint Planning"
                ],
                "long_tail": [
                    "Product-led growth", "User experience design",
                    "Go-to-market strategy", "Product analytics"
                ]
            },
            "ui_ux_designer": {
                "primary": [
                    "UI/UX Design", "Figma", "Sketch", "User Research",
                    "Wireframing", "Prototyping", "Design Systems"
                ],
                "secondary": [
                    "Adobe XD", "InVision", "User Testing", "Information Architecture",
                    "Interaction Design", "Visual Design", "Usability"
                ],
                "long_tail": [
                    "Design thinking", "User-centered design",
                    "Mobile-first design", "Design sprint"
                ]
            },
            "devops_engineer": {
                "primary": [
                    "DevOps", "CI/CD", "Docker", "Kubernetes", "AWS",
                    "Terraform", "Ansible", "Jenkins", "GitOps"
                ],
                "secondary": [
                    "Linux", "Shell Scripting", "Python", "Monitoring",
                    "Prometheus", "Grafana", "ELK Stack", "CloudFormation"
                ],
                "long_tail": [
                    "Infrastructure as code", "Site reliability engineering",
                    "Continuous deployment", "Microservices architecture"
                ]
            }
        }

    def _normalize_role_key(self, role: str) -> str:
        """Normalize role name for database lookup."""
        role_lower = role.lower().replace(" ", "_").replace("-", "_")

        # Map common variations
        mappings = {
            "sr_software_engineer": "software_engineer",
            "senior_software_engineer": "software_engineer",
            "software_developer": "software_engineer",
            "full_stack_developer": "software_engineer",
            "backend_developer": "software_engineer",
            "frontend_developer": "software_engineer",
            "ml_engineer": "data_scientist",
            "machine_learning_engineer": "data_scientist",
            "data_analyst": "data_scientist",
            "ux_designer": "ui_ux_designer",
            "ui_designer": "ui_ux_designer",
            "product_owner": "product_manager",
            "senior_product_manager": "product_manager"
        }

        return mappings.get(role_lower, role_lower)

    def _get_keywords_for_role(self, role: str) -> List[str]:
        """Get expected keywords for a role."""
        role_key = self._normalize_role_key(role)
        role_data = self.keyword_database.get(role_key, {})

        keywords = []
        keywords.extend(role_data.get("primary", []))
        keywords.extend(role_data.get("secondary", []))

        return keywords

    def _generate_keywords_from_role(self, role: str) -> Keywords:
        """Generate keywords from role name."""
        # Extract potential keywords from role title
        words = re.findall(r'\b[A-Z][a-z]+\b', role)

        # Common technical terms
        tech_terms = [
            "Development", "Engineering", "Management", "Design",
            "Analysis", "Architecture", "Leadership", "Strategy"
        ]

        primary = [role] + [w for w in words if len(w) > 3]
        secondary = tech_terms[:10]
        long_tail = []

        return Keywords(
            primary=primary[:10],
            secondary=secondary,
            long_tail=long_tail
        )

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Remove common words
        stop_words = {
            "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
            "with", "a", "an", "is", "are", "was", "were", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "from", "by",
            "about", "as", "into", "through", "during", "before", "after"
        }

        # Tokenize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Filter stop words
        keywords = [w for w in words if w not in stop_words]

        return keywords

    def _score_section(self, text: str, keywords: List[str]) -> float:
        """Score a section for keyword presence."""
        if not text:
            return 0.0

        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)

        return min(matches / len(keywords), 1.0) if keywords else 0.0

    def _score_skills(self, skills: List, keywords: List[str]) -> float:
        """Score skills section."""
        if not skills:
            return 0.0

        skill_names = [s.name.lower() if hasattr(s, 'name') else str(s).lower() for s in skills]
        matches = sum(1 for kw in keywords if kw.lower() in skill_names)

        return min(matches / len(keywords), 1.0) if keywords else 0.0

    def _calculate_coverage(
        self,
        current_keywords: List[str],
        expected_keywords: List[str]
    ) -> Dict:
        """Calculate keyword coverage."""
        current_set = set(kw.lower() for kw in current_keywords)
        expected_set = set(kw.lower() for kw in expected_keywords)

        covered = current_set & expected_set
        missing = expected_set - current_set

        coverage_pct = (len(covered) / len(expected_set) * 100) if expected_set else 0

        return {
            "coverage_percent": round(coverage_pct),
            "covered_count": len(covered),
            "missing_count": len(missing),
            "missing_keywords": sorted(list(missing))[:10]
        }


# Convenience functions
def extract_keywords_sync(profile_data: "ProfileData") -> Keywords:
    """Synchronous wrapper for extract_keywords."""
    optimizer = LinkedInSEOOptimizer()
    return optimizer.extract_keywords(profile_data)


def suggest_keywords_sync(industry: str, role: str) -> Keywords:
    """Synchronous wrapper for suggest_keywords."""
    optimizer = LinkedInSEOOptimizer()
    return optimizer.suggest_keywords(industry, role)
