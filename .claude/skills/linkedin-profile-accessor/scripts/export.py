"""
Export Utilities for LinkedIn Profile Data

Provides export functionality in multiple formats:
- HTML: Professional web reports with CSS styling
- PDF: Printable PDF reports
- Markdown: Enhanced markdown with tables and formatting
"""

import json
import base64
from pathlib import Path
from typing import Any, Optional, List, Dict
from datetime import datetime
from dataclasses import dataclass, field


class HTMLExporter:
    """
    Export LinkedIn profile data to HTML format.

    Usage:
        exporter = HTMLExporter(theme="professional")

        html = exporter.export_profile_analysis(profile_data, analysis)

        # Save to file
        Path("report.html").write_text(html, encoding="utf-8")
    """

    THEMES = {
        "professional": {
            "primary": "#0a66c2",
            "secondary": "#004182",
            "background": "#f8f9fa",
            "text": "#333333",
            "accent": "#00a0dc",
            "success": "#057a55",
            "warning": "#9f6000",
            "danger": "#c53030"
        },
        "modern": {
            "primary": "#6366f1",
            "secondary": "#4f46e5",
            "background": "#ffffff",
            "text": "#1f2937",
            "accent": "#8b5cf6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444"
        },
        "minimal": {
            "primary": "#000000",
            "secondary": "#333333",
            "background": "#ffffff",
            "text": "#000000",
            "accent": "#666666",
            "success": "#22c55e",
            "warning": "#eab308",
            "danger": "#ef4444"
        }
    }

    def __init__(self, include_styles: bool = True, theme: str = "professional"):
        """
        Initialize HTML exporter.

        Args:
            include_styles: Whether to include CSS styles
            theme: Color theme (professional, modern, minimal)
        """
        self.include_styles = include_styles
        self.theme = self.THEMES.get(theme, self.THEMES["professional"])

    def export_profile_analysis(
        self,
        profile_data: Any,
        analysis: Any,
        include_network: bool = False
    ) -> str:
        """
        Export profile analysis to HTML.

        Args:
            profile_data: ProfileData instance
            analysis: AnalysisReport instance
            include_network: Whether to include network insights

        Returns:
            HTML string
        """
        colors = self.theme

        html_parts = [
            self._get_html_start(),
            self._get_styles() if self.include_styles else "",
            f"""
    <body>
        <div class="container">
            <header class="header">
                <h1 class="title">LinkedIn Profile Analysis</h1>
                <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </header>

            <div class="profile-overview">
                <h2>Profile Overview</h2>
                <div class="profile-card">
                    <div class="profile-header">
                        <h3>{self._escape(profile_data.name)}</h3>
                        <p class="headline">{self._escape(profile_data.headline)}</p>
                        <p class="location">{self._escape(profile_data.location or 'Not specified')}</p>
                    </div>
                    <div class="profile-stats">
                        <div class="stat">
                            <span class="stat-label">Completeness Score</span>
                            <span class="stat-value {self._get_score_class(analysis.completeness_score.score)}">{analysis.completeness_score.score}/100</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Experience</span>
                            <span class="stat-value">{len(profile_data.experience)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Education</span>
                            <span class="stat-value">{len(profile_data.education)}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Skills</span>
                            <span class="stat-value">{len(profile_data.skills)}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Completeness Analysis</h2>
                {self._render_completeness_breakdown(analysis.completeness_score)}
            </div>

            <div class="section">
                <h2>Strengths</h2>
                <ul class="strength-list">
                    {"".join(f'<li class="strength-item">{self._escape(s)}</li>' for s in analysis.strengths)}
                </ul>
            </div>

            <div class="section">
                <h2>Areas for Improvement</h2>
                <ul class="improvement-list">
                    {"".join(f'<li class="improvement-item">{self._escape(i)}</li>' for i in analysis.weaknesses)}
                </ul>
            </div>

            <div class="section">
                <h2>Recommended Actions</h2>
                <div class="action-list">
                    {"".join(self._render_suggestion(s) for s in analysis.suggestions)}
                </div>
            </div>
""",
            self._render_experience_section(profile_data.experience),
            self._render_education_section(profile_data.education),
            self._render_skills_section(profile_data.skills),
            self._get_html_end()
        ]

        return "".join(html_parts)

    def export_profile_drafts(self, drafts: Any) -> str:
        """
        Export profile improvement drafts to HTML.

        Args:
            drafts: ProfileDrafts instance

        Returns:
            HTML string
        """
        html_parts = [
            self._get_html_start(),
            self._get_styles() if self.include_styles else "",
            f"""
    <body>
        <div class="container">
            <header class="header">
                <h1 class="title">LinkedIn Profile Improvement Drafts</h1>
                <p class="subtitle">Target Role: {self._escape(drafts.target_role)}</p>
                <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </header>

            <div class="section">
                <h2>Professional Headline</h2>
                <div class="draft-card">
                    <div class="draft-current">
                        <h3>Suggested Headline</h3>
                        <p class="draft-content">{self._escape(drafts.headline.suggested)}</p>
                        <div class="draft-meta">
                            <span class="meta-item">Characters: {drafts.headline.character_count}/220</span>
                        </div>
                    </div>
                    <div class="draft-alternatives">
                        <h4>Alternative Options</h4>
                        <ol class="alternatives-list">
                            {"".join(f'<li>{self._escape(opt)}</li>' for opt in drafts.headline.options[:5])}
                        </ol>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>About Section</h2>
                <div class="draft-card">
                    <div class="draft-content">
                        {self._markdown_to_html(drafts.about.suggested)}
                    </div>
                    <div class="draft-meta">
                        <span class="meta-item">Word Count: {drafts.about.word_count}</span>
                    </div>
                </div>
            </div>
""",
            self._render_experience_drafts(drafts.experiences),
            self._render_skills_recommendations(drafts.skills_recommendations),
            self._render_seo_keywords(drafts.seo_keywords),
            self._get_html_end()
        ]

        return "".join(html_parts)

    def _get_html_start(self) -> str:
        """Get HTML document start."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Profile Report</title>
</head>
"""

    def _get_html_end(self) -> str:
        """Get HTML document end."""
        return """
        </div>
    </body>
</html>
"""

    def _get_styles(self) -> str:
        """Get CSS styles for HTML export."""
        colors = self.theme
        return f"""
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background-color: {colors['background']};
            color: {colors['text']};
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .title {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}

        .section {{
            padding: 30px 40px;
            border-bottom: 1px solid #e5e7eb;
        }}

        .section:last-child {{
            border-bottom: none;
        }}

        .section h2 {{
            color: {colors['primary']};
            font-size: 24px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}

        .section h2::before {{
            content: '';
            display: inline-block;
            width: 4px;
            height: 24px;
            background: {colors['accent']};
            margin-right: 12px;
            border-radius: 2px;
        }}

        .profile-card {{
            background: {colors['background']};
            border-radius: 8px;
            padding: 24px;
        }}

        .profile-header h3 {{
            font-size: 24px;
            margin-bottom: 8px;
        }}

        .headline {{
            color: {colors['primary']};
            font-weight: 600;
            margin-bottom: 4px;
        }}

        .location {{
            color: #6b7280;
            font-size: 14px;
        }}

        .profile-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }}

        .stat {{
            text-align: center;
            padding: 16px;
            background: white;
            border-radius: 8px;
        }}

        .stat-label {{
            display: block;
            font-size: 12px;
            color: #6b7280;
            margin-bottom: 4px;
        }}

        .stat-value {{
            display: block;
            font-size: 28px;
            font-weight: 700;
            color: {colors['primary']};
        }}

        .stat-value.excellent {{ color: {colors['success']}; }}
        .stat-value.good {{ color: {colors['accent']}; }}
        .stat-value.fair {{ color: {colors['warning']}; }}
        .stat-value.poor {{ color: {colors['danger']}; }}

        .strength-list {{
            list-style: none;
        }}

        .strength-item {{
            padding: 12px 16px;
            background: #f0fdf4;
            border-left: 4px solid {colors['success']};
            margin-bottom: 8px;
            border-radius: 4px;
        }}

        .improvement-list {{
            list-style: none;
        }}

        .improvement-item {{
            padding: 12px 16px;
            background: #fffbeb;
            border-left: 4px solid {colors['warning']};
            margin-bottom: 8px;
            border-radius: 4px;
        }}

        .action-list {{
            display: grid;
            gap: 12px;
        }}

        .action-card {{
            padding: 16px;
            background: {colors['background']};
            border-radius: 8px;
            border-left: 4px solid {colors['primary']};
        }}

        .action-priority {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
        }}

        .priority-high {{ background: #fee2e2; color: #991b1b; }}
        .priority-medium {{ background: #fef3c7; color: #92400e; }}
        .priority-low {{ background: #dbeafe; color: #1e40af; }}

        .draft-card {{
            background: {colors['background']};
            border-radius: 8px;
            padding: 24px;
        }}

        .draft-current {{
            margin-bottom: 20px;
        }}

        .draft-content {{
            font-size: 16px;
            line-height: 1.8;
            white-space: pre-wrap;
        }}

        .draft-meta {{
            margin-top: 16px;
            display: flex;
            gap: 20px;
        }}

        .meta-item {{
            font-size: 14px;
            color: #6b7280;
        }}

        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
        }}

        .skill-item {{
            padding: 12px;
            background: {colors['background']};
            border-radius: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .skill-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {colors['accent']};
        }}

        .keyword-tag {{
            display: inline-block;
            padding: 6px 12px;
            background: {colors['background']};
            border-radius: 16px;
            margin: 4px;
            font-size: 14px;
        }}

        .keyword-primary {{
            background: #dbeafe;
            color: #1e40af;
        }}

        .keyword-secondary {{
            background: #e5e7eb;
            color: #374151;
        }}

        @media print {{
            body {{ padding: 0; }}
            .container {{ box-shadow: none; }}
            .section {{ page-break-inside: avoid; }}
        }}

        @media (max-width: 600px) {{
            .profile-stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .section {{
                padding: 20px;
            }}
        }}
    </style>
"""

    def _get_score_class(self, score: int) -> str:
        """Get CSS class for score color."""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        return "poor"

    def _escape(self, text: str) -> str:
        """Escape HTML special characters."""
        return (str(text)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#x27;"))

    def _markdown_to_html(self, markdown: str) -> str:
        """Convert simple markdown to HTML."""
        lines = markdown.split("\n")
        html = []
        in_list = False

        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    html.append("</ul>")
                    in_list = False
                continue

            if line.startswith("# "):
                html.append(f"<h3>{self._escape(line[2:])}</h3>")
            elif line.startswith("## "):
                html.append(f"<h4>{self._escape(line[3:])}</h4>")
            elif line.startswith("- "):
                if not in_list:
                    html.append("<ul>")
                    in_list = True
                html.append(f"<li>{self._escape(line[2:])}</li>")
            elif line.startswith("**") and line.endswith("**"):
                html.append(f"<p><strong>{self._escape(line[2:-2])}</strong></p>")
            else:
                html.append(f"<p>{self._escape(line)}</p>")

        if in_list:
            html.append("</ul>")

        return "\n".join(html)

    def _render_completeness_breakdown(self, completeness: Any) -> str:
        """Render completeness score breakdown."""
        items = []
        for section, score in completeness.breakdown.items():
            percentage = int(score)
            items.append(f"""
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span>{section.title()}</span>
                        <span>{percentage}%</span>
                    </div>
                    <div style="height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden;">
                        <div style="height: 100%; background: {self.theme['primary']}; width: {percentage}%;"></div>
                    </div>
                </div>
            """)
        return f"<div class='completeness-breakdown'>{''.join(items)}</div>"

    def _render_suggestion(self, suggestion: Any) -> str:
        """Render a suggestion card."""
        priority_class = f"priority-{suggestion.priority.lower()}"
        return f"""
            <div class="action-card">
                <span class="action-priority {priority_class}">{suggestion.priority.upper()}</span>
                <h4 style="margin-bottom: 8px;">{self._escape(suggestion.title)}</h4>
                <p style="color: #6b7280;">{self._escape(suggestion.description)}</p>
            </div>
        """

    def _render_experience_section(self, experiences: List[Any]) -> str:
        """Render experience section."""
        if not experiences:
            return ""

        items = []
        for exp in experiences[:5]:
            items.append(f"""
                <div class="section">
                    <h2>Experience</h2>
                    <div class="experience-item">
                        <h3>{self._escape(exp.title)} at {self._escape(exp.company)}</h3>
                        <p style="color: #6b7280; font-size: 14px;">
                            {exp.start_date} - {exp.end_date or 'Present'}
                        </p>
                        <p style="margin-top: 12px;">{self._escape(exp.description or '')}</p>
                    </div>
                </div>
            """)

        return "".join(items)

    def _render_education_section(self, education: List[Any]) -> str:
        """Render education section."""
        if not education:
            return ""

        items = []
        for edu in education:
            items.append(f"""
                <div class="education-item" style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                    <h4 style="margin-bottom: 4px;">{self._escape(edu.school)}</h4>
                    <p style="color: #6b7280;">{self._escape(edu.degree)}{f" in {edu.field_of_study}" if edu.field_of_study else ""}</p>
                </div>
            """)

        return f'<div class="section"><h2>Education</h2>{"".join(items)}</div>'

    def _render_skills_section(self, skills: List[str]) -> str:
        """Render skills section."""
        skill_items = [f'<div class="skill-item"><div class="skill-dot"></div>{self._escape(skill)}</div>' for skill in skills[:20]]
        return f'''
            <div class="section">
                <h2>Skills</h2>
                <div class="skills-grid">
                    {"".join(skill_items)}
                </div>
            </div>
        '''

    def _render_experience_drafts(self, experiences: List[Any]) -> str:
        """Render experience draft suggestions."""
        if not experiences:
            return ""

        items = []
        for exp in experiences[:3]:
            items.append(f"""
                <div class="draft-card" style="margin-bottom: 16px;">
                    <h4 style="margin-bottom: 8px;">{self._escape(exp.title)} at {self._escape(exp.company)}</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <h5 style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Current</h5>
                            <p style="font-size: 14px; opacity: 0.7;">{self._escape(exp.current_description or 'No description')}</p>
                        </div>
                        <div>
                            <h5 style="font-size: 12px; color: {self.theme['success']}; margin-bottom: 4px;">Enhanced</h5>
                            <p style="font-size: 14px;">{self._escape(exp.enhanced_description)}</p>
                        </div>
                    </div>
                </div>
            """)

        return f'<div class="section"><h2>Experience Updates</h2>{"".join(items)}</div>'

    def _render_skills_recommendations(self, skills: List[Any]) -> str:
        """Render skills recommendations."""
        items = [f'<span class="keyword-tag keyword-primary">{self._escape(skill.name)}</span>' for skill in skills[:15]]
        return f'<div class="section"><h2>Recommended Skills</h2><div>{"".join(items)}</div></div>'

    def _render_seo_keywords(self, keywords: Any) -> str:
        """Render SEO keywords section."""
        primary = [f'<span class="keyword-tag keyword-primary">{self._escape(kw)}</span>' for kw in keywords.primary[:10]]
        secondary = [f'<span class="keyword-tag keyword-secondary">{self._escape(kw)}</span>' for kw in keywords.secondary[:10]]

        return f'''
            <div class="section">
                <h2>SEO Keywords</h2>
                <h3 style="font-size: 16px; margin-bottom: 12px;">Primary Keywords</h3>
                <div style="margin-bottom: 20px;">{"".join(primary)}</div>
                <h3 style="font-size: 16px; margin-bottom: 12px;">Secondary Keywords</h3>
                <div>{"".join(secondary)}</div>
            </div>
        '''


class PDFExporter:
    """
    Export LinkedIn profile data to PDF format.

    Usage:
        exporter = PDFExporter()

        # Generate PDF from profile data
        pdf_bytes = exporter.export_profile_analysis(profile_data, analysis)

        # Save to file
        Path("report.pdf").write_bytes(pdf_bytes)
    """

    def __init__(self, html_exporter: Optional[HTMLExporter] = None):
        """
        Initialize PDF exporter.

        Args:
            html_exporter: HTMLExporter instance (uses default if not provided)
        """
        self.html_exporter = html_exporter or HTMLExporter()

    def export_profile_analysis(
        self,
        profile_data: Any,
        analysis: Any,
        include_network: bool = False
    ) -> bytes:
        """
        Export profile analysis to PDF.

        Args:
            profile_data: ProfileData instance
            analysis: AnalysisReport instance
            include_network: Whether to include network insights

        Returns:
            PDF bytes
        """
        # Generate HTML first
        html = self.html_exporter.export_profile_analysis(
            profile_data, analysis, include_network
        )

        # Convert to PDF
        return self._html_to_pdf(html)

    def export_profile_drafts(self, drafts: Any) -> bytes:
        """
        Export profile drafts to PDF.

        Args:
            drafts: ProfileDrafts instance

        Returns:
            PDF bytes
        """
        html = self.html_exporter.export_profile_drafts(drafts)
        return self._html_to_pdf(html)

    def _html_to_pdf(self, html: str) -> bytes:
        """
        Convert HTML to PDF.

        Attempts multiple libraries in order of preference.

        Args:
            html: HTML string

        Returns:
            PDF bytes
        """
        # Try weasyprint first (best quality)
        try:
            from weasyprint import HTML
            from io import BytesIO

            buffer = BytesIO()
            HTML(string=html).write_pdf(buffer)
            return buffer.getvalue()
        except ImportError:
            pass

        # Try pdfkit (wkhtmltopdf wrapper)
        try:
            import pdfkit
            return pdfkit.from_string(html, False)
        except ImportError:
            pass

        # Try reportlab
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from io import BytesIO

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Add title
            title = Paragraph("LinkedIn Profile Report", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 0.2 * inch))

            # Add content as paragraphs
            from html.parser import HTMLParser

            class TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text_parts = []

                def handle_data(self, data):
                    self.text_parts.append(data.strip())

            parser = TextExtractor()
            parser.feed(html)

            for line in parser.text_parts:
                if line:
                    para = Paragraph(line, styles['BodyText'])
                    story.append(para)
                    story.append(Spacer(1, 0.1 * inch))

            doc.build(story)
            return buffer.getvalue()
        except ImportError:
            pass

        # Fallback: Return HTML as bytes with warning
        error_msg = b"""
        WARNING: PDF generation requires one of these libraries:
        - weasyprint (pip install weasyprint)
        - pdfkit (pip install pdfkit)
        - reportlab (pip install reportlab)

        HTML content included below. Save as .html and open in browser.
        """

        return error_msg + html.encode('utf-8')


class MarkdownExporter:
    """
    Export LinkedIn profile data to enhanced markdown format.

    Usage:
        exporter = MarkdownExporter()

        md = exporter.export_profile_analysis(profile_data, analysis)

        # Save to file
        Path("report.md").write_text(md, encoding="utf-8")
    """

    def __init__(self, include_toc: bool = True):
        """
        Initialize markdown exporter.

        Args:
            include_toc: Whether to include table of contents
        """
        self.include_toc = include_toc

    def export_profile_analysis(
        self,
        profile_data: Any,
        analysis: Any,
        include_network: bool = False
    ) -> str:
        """
        Export profile analysis to markdown.

        Args:
            profile_data: ProfileData instance
            analysis: AnalysisReport instance
            include_network: Whether to include network insights

        Returns:
            Markdown string
        """
        parts = [
            self._get_frontmatter(profile_data),
            "",
            "# LinkedIn Profile Analysis",
            "",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"**Profile:** [{profile_data.name}]({profile_data.profile_url})",
            "",
            "---",
            "",
        ]

        if self.include_toc:
            parts.extend([
                "## Table of Contents",
                "",
                "- [Profile Overview](#profile-overview)",
                "- [Completeness Analysis](#completeness-analysis)",
                "- [Strengths](#strengths)",
                "- [Weaknesses](#weaknesses)",
                "- [Recommendations](#recommendations)",
                "- [Experience](#experience)",
                "- [Education](#education)",
                "- [Skills](#skills)",
                "",
            ])

        # Overview
        parts.extend([
            "## Profile Overview",
            "",
            f"### {profile_data.name}",
            "",
            f"**{profile_data.headline}**",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| **Completeness Score** | **{analysis.completeness_score.score}/100** |",
            f"| Experience | {len(profile_data.experience)} positions |",
            f"| Education | {len(profile_data.education)} entries |",
            f"| Skills | {len(profile_data.skills)} skills |",
            "",
            "---",
            "",
        ])

        # Completeness
        parts.extend([
            "## Completeness Analysis",
            "",
            f"**Overall Score:** {analysis.completeness_score.score}/100",
            "",
            "| Section | Score |",
            "|---------|-------|",
        ])

        for section, score in analysis.completeness_score.breakdown.items():
            percentage = int(score)
            status = "✅" if percentage >= 80 else "⚠️" if percentage >= 50 else "❌"
            parts.append(f"| {section.title()} | {percentage}% {status} |")

        parts.extend(["", "---", ""])

        # Strengths
        parts.extend([
            "## Strengths",
            "",
        ])
        for strength in analysis.strengths:
            parts.append(f"- ✅ {strength}")

        parts.extend(["", "---", ""])

        # Weaknesses
        parts.extend([
            "## Areas for Improvement",
            "",
        ])
        for weakness in analysis.weaknesses:
            parts.append(f"- ⚠️ {weakness}")

        parts.extend(["", "---", ""])

        # Recommendations
        parts.extend([
            "## Recommendations",
            "",
        ])
        for suggestion in analysis.suggestions:
            priority_emoji = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(suggestion.priority, "⚪")

            parts.extend([
                f"### {priority_emoji} {suggestion.title}",
                "",
                f"{suggestion.description}",
                "",
                f"**Priority:** {suggestion.priority.upper()}",
                "",
            ])

        parts.extend(["---", ""])

        # Experience
        if profile_data.experience:
            parts.extend([
                "## Experience",
                "",
            ])
            for exp in profile_data.experience[:5]:
                parts.extend([
                    f"### {exp.title} at {exp.company}",
                    "",
                    f"**Dates:** {exp.start_date} - {exp.end_date or 'Present'}",
                    "",
                    exp.description or "No description provided.",
                    "",
                ])

        # Education
        if profile_data.education:
            parts.extend([
                "---",
                "",
                "## Education",
                "",
            ])
            for edu in profile_data.education:
                parts.extend([
                    f"### {edu.school}",
                    "",
                    f"**Degree:** {edu.degree}",
                    f"**Field:** {edu.field_of_study or 'N/A'}",
                    f"**Years:** {edu.start_year} - {edu.end_year or 'Present'}",
                    "",
                ])

        # Skills
        parts.extend([
            "---",
            "",
            "## Skills",
            "",
        ])

        for i, skill in enumerate(profile_data.skills[:30], 1):
            parts.append(f"{i}. {skill}")

        parts.append("")
        parts.extend([
            "---",
            "",
            f"*Report generated by LinkedIn Profile Accessor*",
            f"*{datetime.now().isoformat()}*",
            ""
        ])

        return "\n".join(parts)

    def export_profile_drafts(self, drafts: Any) -> str:
        """
        Export profile drafts to markdown.

        Args:
            drafts: ProfileDrafts instance

        Returns:
            Markdown string
        """
        parts = [
            self._get_frontmatter(drafts),
            "",
            "# LinkedIn Profile Improvement Drafts",
            "",
            f"**Target Role:** {drafts.target_role}",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
            "---",
            "",
            "## Professional Headline",
            "",
            f"**Suggested:**",
            f"> {drafts.headline.suggested}",
            "",
            f"**Character Count:** {drafts.headline.character_count}/220",
            "",
            "**Alternatives:**",
            "",
        ]

        for i, option in enumerate(drafts.headline.options[:5], 1):
            parts.append(f"{i}. {option}")

        parts.extend([
            "",
            "---",
            "",
            "## About Section",
            "",
            drafts.about.suggested,
            "",
            f"**Word Count:** {drafts.about.word_count}",
            "",
            "---",
            "",
            "## Experience Updates",
            "",
        ])

        for exp in drafts.experiences[:3]:
            parts.extend([
                f"### {exp.title} at {exp.company}",
                "",
                "**Current:**",
                f"> {exp.current_description or 'No description'}",
                "",
                "**Enhanced:**",
                f"> {exp.enhanced_description}",
                "",
                "**Improvements:**",
                "",
            ])
            for improvement in exp.improvements[:5]:
                parts.append(f"- {improvement}")

            parts.append("")

        parts.extend([
            "---",
            "",
            "## Skills Recommendations",
            "",
        ])

        for skill in drafts.skills_recommendations[:15]:
            parts.append(f"- **{skill.name}** - {skill.reason}")

        parts.extend([
            "",
            "---",
            "",
            "## SEO Keywords",
            "",
            "### Primary Keywords",
            "",
        ])

        for keyword in drafts.seo_keywords.primary[:10]:
            parts.append(f"- `{keyword}`")

        parts.extend([
            "",
            "### Secondary Keywords",
            "",
        ])

        for keyword in drafts.seo_keywords.secondary[:10]:
            parts.append(f"- `{keyword}`")

        parts.extend([
            "",
            "---",
            "",
            "## Application Instructions",
            "",
            "1. Review each section carefully",
            "2. Edit to match your voice and experience",
            "3. Verify all facts and figures",
            "4. Apply to LinkedIn profile",
            "5. View profile as public to verify",
            "",
            "---",
            "",
            f"*Generated by LinkedIn Profile Builder*",
            f"*Target Role: {drafts.target_role}*",
            ""
        ])

        return "\n".join(parts)

    def export_comparison_report(
        self,
        before: Any,
        after: Any,
        profile_id: str
    ) -> str:
        """
        Export before/after comparison report.

        Args:
            before: Original profile data
            after: Improved drafts
            profile_id: Profile identifier

        Returns:
            Markdown string
        """
        parts = [
            "# LinkedIn Profile Before & After",
            "",
            f"**Profile ID:** {profile_id}",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
            "---",
            "",
            "## Headline Comparison",
            "",
            "**Before:**",
            f"> {before.headline}",
            "",
            "**After:**",
            f"> {after.headline.suggested}",
            "",
            "**Improvements:**",
            f"- More SEO keywords",
            f"- Clearer value proposition",
            f"- Better keyword placement",
            "",
            "---",
            "",
            "## About Section Comparison",
            "",
            "**Before:**",
            f"> {before.about or '(Empty)'}",
            "",
            "**After:**",
            f"> {after.about.suggested}",
            "",
            "**Improvements:**",
            f"- {after.about.word_count} words (vs {len(before.about.split()) if before.about else 0})",
            f"- Professional structure",
            f"- Key achievements highlighted",
            "",
            "",
        ]

        return "\n".join(parts)

    def _get_frontmatter(self, data: Any) -> str:
        """Generate YAML frontmatter."""
        frontmatter = {
            "type": "linkedin_profile_export",
            "generated": datetime.now().isoformat(),
        }

        if hasattr(data, "profile_id"):
            frontmatter["profile_id"] = data.profile_id
        if hasattr(data, "target_role"):
            frontmatter["target_role"] = data.target_role

        lines = ["---"]
        for key, value in frontmatter.items():
            lines.append(f"{key}: {value}")
        lines.append("---")

        return "\n".join(lines)


class CSVExporter:
    """
    Export LinkedIn profile data to CSV format for bulk analysis.

    Usage:
        exporter = CSVExporter()

        csv_data = exporter.export_profiles([profile1, profile2, profile3])

        Path("analysis.csv").write_text(csv_data, encoding="utf-8")
    """

    def export_profiles(self, profiles: List[Any]) -> str:
        """
        Export multiple profiles to CSV.

        Args:
            profiles: List of ProfileData instances

        Returns:
            CSV string
        """
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Profile ID",
            "Name",
            "Headline",
            "Location",
            "Experience Count",
            "Education Count",
            "Skills Count",
            "Connections",
            "Profile URL",
            "Extracted At"
        ])

        # Data rows
        for profile in profiles:
            writer.writerow([
                profile.profile_id,
                profile.name,
                profile.headline,
                profile.location,
                len(profile.experience),
                len(profile.education),
                len(profile.skills),
                getattr(profile, "connections_count", "N/A"),
                profile.profile_url,
                profile.extracted_at.isoformat()
            ])

        return output.getvalue()

    def export_analysis_comparison(
        self,
        analyses: List[tuple[Any, Any]]
    ) -> str:
        """
        Export multiple analyses for comparison.

        Args:
            analyses: List of (profile_data, analysis) tuples

        Returns:
            CSV string
        """
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Profile ID",
            "Name",
            "Completeness Score",
            "Strengths Count",
            "Weaknesses Count",
            "Suggestions Count",
            "Experience Count",
            "Education Count",
            "Skills Count"
        ])

        # Data rows
        for profile, analysis in analyses:
            writer.writerow([
                profile.profile_id,
                profile.name,
                analysis.completeness_score.score,
                len(analysis.strengths),
                len(analysis.weaknesses),
                len(analysis.suggestions),
                len(profile.experience),
                len(profile.education),
                len(profile.skills)
            ])

        return output.getvalue()


# Convenience functions
def export_to_html(
    profile_data: Any,
    analysis: Any,
    output_path: Path,
    theme: str = "professional"
) -> Path:
    """
    Quick export to HTML.

    Args:
        profile_data: ProfileData instance
        analysis: AnalysisReport instance
        output_path: Output file path
        theme: Color theme

    Returns:
        Path to exported file
    """
    exporter = HTMLExporter(theme=theme)
    html = exporter.export_profile_analysis(profile_data, analysis)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def export_to_pdf(
    profile_data: Any,
    analysis: Any,
    output_path: Path
) -> Path:
    """
    Quick export to PDF.

    Args:
        profile_data: ProfileData instance
        analysis: AnalysisReport instance
        output_path: Output file path

    Returns:
        Path to exported file
    """
    exporter = PDFExporter()
    pdf_bytes = exporter.export_profile_analysis(profile_data, analysis)
    output_path.write_bytes(pdf_bytes)
    return output_path


def export_to_markdown(
    profile_data: Any,
    analysis: Any,
    output_path: Path
) -> Path:
    """
    Quick export to markdown.

    Args:
        profile_data: ProfileData instance
        analysis: AnalysisReport instance
        output_path: Output file path

    Returns:
        Path to exported file
    """
    exporter = MarkdownExporter()
    md = exporter.export_profile_analysis(profile_data, analysis)
    output_path.write_text(md, encoding="utf-8")
    return output_path
