# Content Generator

Generate, refine, and optimize content for various platforms including LinkedIn, blog posts, email campaigns, and social media updates.

## Purpose

The Content Generator skill **creates** engaging content tailored to specific platforms, **optimizes** for audience engagement, **maintains** brand voice consistency, and **scales** content production across multiple channels. This skill **leverages** AI to transform rough ideas into polished, platform-ready content.

## Design Philosophy

- **Platform-Specific**: Each platform has unique conventions, length limits, and audience expectations
- **Brand-Consistent**: Maintains tone and style guidelines from Company_Handbook
- **Engagement-Focused**: Optimizes for likes, shares, comments, and conversions
- **Data-Informed**: Uses analytics from previous posts to improve performance
- **Approval-Required**: All content requires human review before posting

## Workflow

1. **Review** brief or topic from human
2. **Analyze** platform requirements and best practices
3. **Generate** content following platform-specific templates
4. **Optimize** for engagement (headlines, hashtags, calls-to-action)
5. **Review** against Company_Handbook guidelines
6. **Create** draft in `/Pending_Approval/`
7. **Human** reviews and moves to `/Approved/`
8. **MCP Server** posts to platform

## Modularity

Extensible with:
- Custom platform templates
- Brand voice style guides
- A/B testing frameworks
- Analytics integration
- Content calendar management

---

*Content Generator Skill v1.0*
