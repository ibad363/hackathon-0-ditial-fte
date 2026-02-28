"""
LinkedIn Content Generator - AI Content Generation Module

Generates AI-optimized LinkedIn profile content using GLM API.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

import requests


class LinkedInContentGenerator:
    """
    Generates LinkedIn profile content using AI.

    Usage:
        generator = LinkedInContentGenerator(api_key="your-api-key")
        headline = generator.generate_headline(context)
        about = generator.generate_about(context, target_length=300)
    """

    # API Configuration
    API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    DEFAULT_MODEL = "glm-4"
    DEFAULT_TIMEOUT = 30

    # Tone prompts
    TONE_PROMPTS = {
        "professional": "Professional, business-oriented, and polished",
        "confident": "Bold, assertive, and achievement-focused",
        "casual": "Conversational, approachable, and authentic",
        "technical": "Precise, detailed, and technical"
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize the content generator.

        Args:
            api_key: GLM API key (default: from ZHIPU_API_KEY env var)
            model: Model name (default: "glm-4")
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GLM API key not found. Set ZHIPU_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.model = model
        self.timeout = timeout

    def generate_headline(self, context: Dict) -> str:
        """
        Generate an optimized LinkedIn headline.

        Context Keys:
            - current_role: Current job title
            - target_role: Target job title
            - industry: Industry
            - expertise: List of expertise areas
            - achievements: Key achievements
            - tone: Content tone

        Args:
            context: Generation context

        Returns:
            Generated headline (max 220 characters)
        """
        tone = context.get("tone", "professional")
        tone_desc = self.TONE_PROMPTS.get(tone, tone)

        prompt = self._build_headline_prompt(context, tone_desc)

        response = self._call_api(prompt)
        headline = self._extract_headline(response)

        # Ensure character limit
        if len(headline) > 220:
            headline = headline[:217] + "..."

        return headline

    def generate_about(
        self,
        context: Dict,
        target_length: int = 300
    ) -> str:
        """
        Generate an optimized LinkedIn about section.

        Context Keys:
            - current_role: Job title
            - years_experience: Years of experience
            - industry: Industry
            - expertise: Key skills
            - achievements: Notable achievements
            - passion: What drives you
            - tone: Content tone

        Args:
            context: Generation context
            target_length: Target word count

        Returns:
            Generated about section
        """
        tone = context.get("tone", "professional")
        tone_desc = self.TONE_PROMPTS.get(tone, tone)

        prompt = self._build_about_prompt(context, tone_desc, target_length)

        response = self._call_api(prompt)
        about = self._extract_about(response)

        return about

    def generate_experience_description(
        self,
        role: str,
        company: str,
        context: Dict
    ) -> str:
        """
        Generate an enhanced experience description.

        Context Keys:
            - duration: Time in role
            - achievements: List of achievements
            - responsibilities: Key responsibilities
            - team_size: Team size managed
            - tools: Tools/technologies used
            - tone: Content tone

        Args:
            role: Job title
            company: Company name
            context: Experience context

        Returns:
            Generated experience description
        """
        tone = context.get("tone", "professional")
        tone_desc = self.TONE_PROMPTS.get(tone, tone)

        prompt = self._build_experience_prompt(
            role, company, context, tone_desc
        )

        response = self._call_api(prompt)
        description = self._extract_description(response)

        return description

    def _build_headline_prompt(self, context: Dict, tone_desc: str) -> str:
        """Build prompt for headline generation."""
        current_role = context.get("current_role", "")
        target_role = context.get("target_role", current_role)
        industry = context.get("industry", "")
        expertise = context.get("expertise", [])
        achievements = context.get("achievements", [])

        expertise_str = ", ".join(expertise[:5]) if expertise else ""
        achievements_str = "; ".join(achievements[:2]) if achievements else ""

        prompt = f"""Generate a professional LinkedIn headline for a {target_role} in the {industry} industry.

Current Role: {current_role}
Expertise: {expertise_str}
Key Achievement: {achievements_str}

Requirements:
- Maximum 220 characters
- Format: Role | Key Skills | Achievement/Impact
- Use {tone_desc} tone
- Include 2-3 relevant keywords for SEO
- Make it compelling and specific

Generate only the headline text, nothing else."""

        return prompt

    def _build_about_prompt(
        self,
        context: Dict,
        tone_desc: str,
        target_length: int
    ) -> str:
        """Build prompt for about section generation."""
        current_role = context.get("current_role", "")
        years_experience = context.get("years_experience", 5)
        industry = context.get("industry", "")
        expertise = context.get("expertise", [])
        achievements = context.get("achievements", [])
        passion = context.get("passion", "solving complex problems")

        expertise_str = ", ".join(expertise[:8]) if expertise else ""
        achievements_str = "; ".join(achievements[:3]) if achievements else ""

        prompt = f"""Generate a compelling LinkedIn about section for a {current_role} with {years_experience}+ years of experience in the {industry} industry.

Key Details:
- Role: {current_role}
- Expertise: {expertise_str}
- Key Achievements: {achievements_str}
- Passion: {passion}

Requirements:
- Target length: {target_length} words (±50 words)
- Use {tone_desc} tone
- Include these sections:
  1. Hook - Who you are and what you do
  2. Story - Your journey and passion
  3. Skills - Key expertise areas
  4. Impact - What you've achieved
  5. Call to action - Connect or reach out
- Naturally integrate keywords from expertise
- Make it authentic and engaging

Generate the complete about section text."""

        return prompt

    def _build_experience_prompt(
        self,
        role: str,
        company: str,
        context: Dict,
        tone_desc: str
    ) -> str:
        """Build prompt for experience description generation."""
        duration = context.get("duration", "")
        achievements = context.get("achievements", [])
        responsibilities = context.get("responsibilities", [])
        team_size = context.get("team_size", "")
        tools = context.get("tools", [])

        achievements_str = "\n".join([f"- {a}" for a in achievements[:5]])
        responsibilities_str = "\n".join([f"- {r}" for r in responsibilities[:5]])
        tools_str = ", ".join(tools[:10]) if tools else ""

        prompt = f"""Generate an enhanced LinkedIn experience description for:

Role: {role}
Company: {company}
Duration: {duration}

Current Details:
Responsibilities:
{responsibilities_str}

Achievements:
{achievements_str}

Tools/Technologies: {tools_str}
Team Size: {team_size}

Requirements:
- Use {tone_desc} tone
- Format as bullet points
- Focus on achievements and impact
- Use action verbs (Built, Led, Developed, Increased, etc.)
- Include numbers and metrics where possible
- Naturally integrate relevant skills/tools
- 3-6 bullet points maximum

Generate the complete experience description."""

        return prompt

    def _call_api(self, prompt: str) -> str:
        """Call GLM API and return response."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert LinkedIn profile optimizer. Generate professional, compelling content that helps people stand out."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            return content

        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"API call failed: {e}") from e

    def _extract_headline(self, response: str) -> str:
        """Extract headline from API response."""
        # Clean up response
        headline = response.strip()

        # Remove common prefixes
        for prefix in ["Headline:", "LinkedIn:", "Result:", "Output:"]:
            if headline.startswith(prefix):
                headline = headline[len(prefix):].strip()

        # Remove quotes if present
        if headline.startswith('"') and headline.endswith('"'):
            headline = headline[1:-1]
        elif headline.startswith("'") and headline.endswith("'"):
            headline = headline[1:-1]

        return headline

    def _extract_about(self, response: str) -> str:
        """Extract about section from API response."""
        about = response.strip()

        # Remove common prefixes
        for prefix in ["About:", "LinkedIn About:", "Result:", "Output:"]:
            if about.startswith(prefix):
                about = about[len(prefix):].strip()

        # Remove quotes if present
        if about.startswith('"') and about.endswith('"'):
            about = about[1:-1]
        elif about.startswith("'") and about.endswith("'"):
            about = about[1:-1]

        return about

    def _extract_description(self, response: str) -> str:
        """Extract experience description from API response."""
        description = response.strip()

        # Remove common prefixes
        for prefix in ["Description:", "Experience:", "Result:", "Output:"]:
            if description.startswith(prefix):
                description = description[len(prefix):].strip()

        # Remove quotes if present
        if description.startswith('"') and description.endswith('"'):
            description = description[1:-1]
        elif description.startswith("'") and description.endswith("'"):
            description = description[1:-1]

        return description


class APIConnectionError(Exception):
    """API connection error."""
    pass


class APIError(Exception):
    """API error."""
    pass


# Template-based generator (fallback when API unavailable)
class TemplateContentGenerator:
    """
    Generates content using templates (fallback).

    Usage:
        generator = TemplateContentGenerator()
        headline = generator.generate_headline(context)
    """

    def __init__(self):
        """Initialize the template generator."""
        # Load templates
        self.headline_templates = self._load_headline_templates()
        self.about_templates = self._load_about_templates()

    def generate_headline(self, context: Dict) -> str:
        """Generate headline from templates."""
        target_role = context.get("target_role", "")
        expertise = context.get("expertise", [])

        template = self.headline_templates.get("default")
        if not template:
            template = "{role} | {skills} | Building impact at scale"

        skills_str = " | ".join(expertise[:3]) if expertise else "Expert"

        return template.format(
            role=target_role,
            skills=skills_str
        )

    def generate_about(self, context: Dict, target_length: int = 300) -> str:
        """Generate about from templates."""
        current_role = context.get("current_role", "")
        years = context.get("years_experience", 5)
        industry = context.get("industry", "")

        template = self.about_templates.get("professional", "")
        if not template:
            template = "Passionate {role} with {years} years of experience in {industry}. Specialized in delivering results and driving innovation."

        return template.format(
            role=current_role,
            years=years,
            industry=industry
        )

    def _load_headline_templates(self) -> Dict:
        """Load headline templates."""
        templates_path = Path(__file__).parent.parent / "templates" / "headline_templates.json"

        if templates_path.exists():
            try:
                with open(templates_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                # Log error and return empty templates
                print(f"Warning: Could not load headline templates: {e}")

        return {}

    def _load_about_templates(self) -> Dict:
        """Load about templates."""
        templates_path = Path(__file__).parent.parent / "templates" / "about_templates.json"

        if templates_path.exists():
            try:
                with open(templates_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                # Log error and return empty templates
                print(f"Warning: Could not load about templates: {e}")

        return {}
