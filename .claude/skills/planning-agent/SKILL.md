# Planning Agent

Break down complex tasks, create execution plans, identify dependencies, and generate structured workflows for achieving goals.

## Purpose

The Planning Agent skill **analyzes** complex objectives, **decomposes** them into manageable steps, **identifies** dependencies and risks, **estimates** effort and timeline, and **generates** actionable Plan.md files. This skill **transforms** vague goals into clear, executable roadmaps that humans can follow and AI can execute.

## Design Philosophy

- **Goal-Oriented**: Start with clear objective and success criteria
- **Decomposition**: Break complex tasks into simple, actionable steps
- **Dependency-Aware**: Identify prerequisites and blocking issues
- **Risk-Conscious**: Anticipate problems and create mitigation strategies
- **Trackable**: Each step has clear completion criteria

## Workflow

1. **Receive** goal or task from human or another system
2. **Analyze** requirements and constraints
3. **Decompose** into subtasks and milestones
4. **Identify** dependencies between tasks
5. **Estimate** effort and timeline for each step
6. **Assess** risks and create mitigation plans
7. **Generate** Plan.md file with checkboxes
8. **Update** plan status as progress is made
9. **Archive** completed plans to `/Done/`

## Modularity

Extensible with:
- Multiple planning methodologies (Agile, Waterfall, MVP)
- Resource allocation planning
- Risk assessment frameworks
- Priority scoring algorithms
- Integration with task management tools

---

*Planning Agent Skill v1.0*
