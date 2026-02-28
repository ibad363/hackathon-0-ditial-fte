"""
Pytest Configuration for LinkedIn Profile Builder

Shared fixtures and configuration for builder tests.
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def industry_templates():
    """Load industry templates for testing."""
    templates_path = Path(__file__).parent.parent / "templates" / "industry_about_templates.json"

    if templates_path.exists():
        return json.loads(templates_path.read_text())

    # Fallback minimal templates
    return {
        "technology": {
            "headline": "{role} | {skills1} | {skills2}",
            "about": "# {role}\n\nI'm a {role} with expertise in {skills1}."
        },
        "finance": {
            "headline": "{role} | {focus_area} | Finance",
            "about": "# Financial {role}\n\nExperienced {role} specializing in {focus_area}."
        }
    }


@pytest.fixture
def seo_keywords():
    """Load SEO keywords for testing."""
    keywords_path = Path(__file__).parent.parent / "keywords" / "seo_keywords.json"

    if keywords_path.exists():
        return json.loads(keywords_path.read_text())

    # Fallback minimal keywords
    return {
        "software_engineer": {
            "primary": ["Python", "JavaScript", "AWS"],
            "secondary": ["Docker", "Kubernetes", "CI/CD"],
            "long_tail": ["Cloud Computing", "System Design"]
        }
    }


@pytest.fixture
def target_roles():
    """Sample target roles for testing."""
    return [
        "Senior Software Engineer",
        "Data Scientist",
        "Product Manager",
        "DevOps Engineer",
        "Full Stack Developer",
        "AI Engineer",
        "ML Engineer"
    ]


@pytest.fixture
def tone_options():
    """Available tone options."""
    return ["professional", "confident", "casual", "technical"]


@pytest.fixture
def sample_draft_data():
    """Sample draft data for testing."""
    from datetime import datetime

    return {
        "profile_id": "draft-test-123",
        "target_role": "Senior Software Engineer",
        "generated_at": datetime.now().isoformat(),
        "headline": {
            "current": "Software Engineer",
            "suggested": "Senior Software Engineer | Python | AWS | Cloud Architecture",
            "character_count": 58,
            "seo_keywords": ["Python", "AWS", "Cloud"],
            "options": [
                "Senior Software Engineer | Python | AWS",
                "Software Engineer | Cloud Architecture"
            ],
            "improvements": [
                "Added seniority level",
                "Included key skills",
                "Added specialization"
            ]
        },
        "about": {
            "current": "I am a software engineer.",
            "suggested": "# Senior Software Engineer\n\nExperienced software engineer...",
            "word_count": 250,
            "seo_keywords": ["Python", "AWS", "Cloud Computing"],
            "improvements": [
                "Professional structure",
                "Key achievements highlighted",
                "SEO optimized"
            ]
        },
        "experiences": [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "current_description": "Built software",
                "enhanced_description": "• Developed microservices architecture\n• Improved API performance by 40%\n• Led team of 3 developers",
                "improvements": [
                    "Added specific achievements",
                    "Included metrics",
                    "Used action verbs"
                ]
            }
        ],
        "skills_recommendations": [
            {
                "name": "Kubernetes",
                "reason": "Highly requested for senior roles",
                "priority": "high"
            },
            {
                "name": "Terraform",
                "reason": "Infrastructure as Code skill",
                "priority": "medium"
            }
        ],
        "seo_keywords": {
            "primary": ["Python", "AWS", "Cloud Computing"],
            "secondary": ["Docker", "Kubernetes", "CI/CD"],
            "long_tail": ["Microservices Architecture", "System Design"]
        }
    }


# Mock GLM API responses
@pytest.fixture
def mock_glm_headline_response():
    """Mock GLM API response for headline generation."""
    return {
        "choices": [{
            "message": {
                "content": "Senior Software Engineer | Python | AWS | Cloud Architecture"
            }
        }]
    }


@pytest.fixture
def mock_glm_about_response():
    """Mock GLM API response for about generation."""
    return {
        "choices": [{
            "message": {
                "content": """# Senior Software Engineer

I'm a senior software engineer with 5+ years of experience building scalable cloud solutions. I specialize in Python development and AWS infrastructure.

## Key Achievements
• Led development of microservices architecture serving 1M+ users
• Reduced API latency by 40% through optimization
• Mentored junior developers and conducted code reviews

## Technical Expertise
• Languages: Python, JavaScript, TypeScript
• Cloud: AWS, Azure, GCP
• DevOps: Docker, Kubernetes, CI/CD

I'm passionate about building robust, scalable systems and mentoring the next generation of engineers."""
            }
        }]
    }


@pytest.fixture
def mock_glm_experience_response():
    """Mock GLM API response for experience enhancement."""
    return {
        "choices": [{
            "message": {
                "content": """• Led development of microservices architecture using Python and AWS
• Designed and implemented RESTful APIs serving 1M+ daily requests
• Reduced API response time by 40% through caching and optimization
• Collaborated with cross-functional teams to deliver features on time
• Mentored 3 junior developers, conducting code reviews and pair programming sessions"""
            }
        }]
    }


# Test helper functions
def create_mock_experience(title: str = "Software Engineer",
                          company: str = "Tech Corp",
                          description: str = "Built software"):
    """Create a mock experience item."""
    from datetime import datetime
    from scripts.profile_data_models import ExperienceItem

    return ExperienceItem(
        title=title,
        company=company,
        start_date="2020-01",
        end_date=None,
        description=description
    )


def create_mock_education(school: str = "University",
                         degree: str = "BS"):
    """Create a mock education item."""
    from scripts.profile_data_models import EducationItem

    return EducationItem(
        school=school,
        degree=degree,
        field_of_study="Computer Science",
        start_year=2016,
        end_year=2020
    )


# Skip conditions for tests
def pytest_configure(config):
    """Configure test markers."""
    config.addinivalue_line(
        "markers", "generator: mark test as content generation test"
    )
    config.addinivalue_line(
        "markers", "template: mark test as template test"
    )
    config.addinivalue_line(
        "markers", "seo: mark test as SEO test"
    )
