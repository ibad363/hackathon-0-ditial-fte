#!/usr/bin/env python3
"""
Planning Agent Skill Invoker

Creates intelligent, context-aware execution plans using LLM reasoning.
Reads vault context (Business_Goals.md, Needs_Action items, Company_Handbook.md)
to generate relevant step-by-step plans.

Usage:
    python invoke.py "Create a plan for client onboarding"
    python invoke.py "Process all pending invoices" --vault AI_Employee_Vault
    python invoke.py "Prepare Q1 tax documents"

Returns:
    JSON output with status and plan details
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests as http_requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def _gather_vault_context(vault_path: Path) -> str:
    """Read relevant vault files to provide context for plan generation."""
    context_parts = []

    # Business Goals
    goals_file = vault_path / "Business_Goals.md"
    if goals_file.exists():
        content = goals_file.read_text(encoding='utf-8')[:2000]
        context_parts.append(f"## Business Goals\n{content}")

    # Company Handbook (rules)
    handbook_file = vault_path / "Company_Handbook.md"
    if handbook_file.exists():
        content = handbook_file.read_text(encoding='utf-8')[:2000]
        context_parts.append(f"## Company Handbook Rules\n{content}")

    # Pending items in Needs_Action
    needs_action = vault_path / "Needs_Action"
    if needs_action.exists():
        items = list(needs_action.glob("*.md"))
        if items:
            summaries = []
            for item in items[:10]:
                try:
                    first_lines = item.read_text(encoding='utf-8')[:300]
                    summaries.append(f"- {item.name}: {first_lines[:100]}...")
                except Exception:
                    summaries.append(f"- {item.name}")
            context_parts.append(
                f"## Pending Items in Needs_Action ({len(items)} total)\n"
                + "\n".join(summaries)
            )

    # Recent plans
    plans_dir = vault_path / "Plans"
    if plans_dir.exists():
        recent_plans = sorted(plans_dir.glob("*.md"), reverse=True)[:3]
        if recent_plans:
            plan_names = [f"- {p.name}" for p in recent_plans]
            context_parts.append(
                f"## Recent Plans\n" + "\n".join(plan_names)
            )

    return "\n\n".join(context_parts) if context_parts else "(No vault context available)"


def _call_llm(prompt: str) -> str | None:
    """Call LLM API (supports Anthropic, GLM, or any OpenAI-compatible endpoint)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    is_custom = base_url != "https://api.anthropic.com" and HAS_REQUESTS

    try:
        if is_custom:
            # OpenAI-compatible endpoint (GLM, etc.)
            api_url = base_url.rstrip('/') + '/chat/completions'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }
            payload = {
                'model': 'glm-4',
                'max_tokens': 1500,
                'temperature': 0.7,
                'messages': [{'role': 'user', 'content': prompt}],
            }
            response = http_requests.post(api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            if 'choices' in data and data['choices']:
                return data['choices'][0]['message']['content'].strip()
            return None
        else:
            # Standard Anthropic SDK
            import anthropic
            client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text.strip()
    except Exception as e:
        print(f"[WARNING] LLM call failed: {e}", file=sys.stderr)
        return None


def invoke_planning(task: str, vault_path: str = None) -> dict:
    """
    Invoke the planning agent skill.

    Args:
        task: Task or project to plan
        vault_path: Path to Obsidian vault

    Returns:
        dict: Result with status and plan details
    """
    try:
        if vault_path is None:
            vault_path = project_root / "AI_Employee_Vault"
        else:
            vault_path = Path(vault_path)

        objective = task

        # Gather vault context
        context = _gather_vault_context(vault_path)

        # Try LLM-powered plan generation
        llm_prompt = f"""You are a planning agent for an AI Employee system. Generate a detailed, actionable execution plan.

# VAULT CONTEXT
{context}

# OBJECTIVE
{objective}

# INSTRUCTIONS
Create a step-by-step plan with:
1. A brief analysis of what needs to be done
2. Specific phases with actionable checkbox items (use "- [ ]" format)
3. Required tools/skills (email, social media, file processing, etc.)
4. Risk considerations
5. Success criteria

Be specific and practical. Reference actual vault folders (Needs_Action/, Plans/, Pending_Approval/, Done/).
Keep the plan under 40 lines. Use markdown formatting.

Output ONLY the plan content (no preamble, no code blocks).
"""

        llm_plan = _call_llm(llm_prompt)

        # Create plan file
        plans_folder = vault_path / "Plans"
        plans_folder.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"PLAN_{timestamp}.md"
        filepath = plans_folder / filename

        if llm_plan:
            # AI-generated plan
            plan_content = f"""---
type: execution_plan
status: draft
created: {datetime.now().isoformat()}
objective: "{objective}"
generated_by: ai
---

# Execution Plan: {objective}

**Generated by:** Planning Agent (AI-powered)
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Objective
{objective}

{llm_plan}

---
*AI-generated plan. Review and adjust before executing.*
"""
        else:
            # Fallback: structured template (no LLM available)
            needs_action = vault_path / "Needs_Action"
            pending_count = len(list(needs_action.glob("*.md"))) if needs_action.exists() else 0

            plan_content = f"""---
type: execution_plan
status: draft
created: {datetime.now().isoformat()}
objective: "{objective}"
generated_by: template
---

# Execution Plan: {objective}

**Generated by:** Planning Agent (template mode - no API key configured)
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Objective
{objective}

## Current State
- Items in Needs_Action: {pending_count}

## Phase 1: Assessment
- [ ] Review relevant items in Needs_Action/
- [ ] Check Company_Handbook.md for applicable rules
- [ ] Identify required resources and skills
- [ ] Estimate time and risk

## Phase 2: Execution
- [ ] Process items related to: {objective}
- [ ] Create approval requests in Pending_Approval/ if needed
- [ ] Execute approved actions via MCP servers
- [ ] Log all actions to Logs/

## Phase 3: Completion
- [ ] Verify all objectives met
- [ ] Move completed items to Done/
- [ ] Update Dashboard.md with results

## Notes
- Set ANTHROPIC_API_KEY in .env for AI-powered plan generation
- Use approval workflow for sensitive actions

---
*Planning Agent Skill - Template Plan*
"""

        filepath.write_text(plan_content, encoding='utf-8')

        generation_type = "AI-powered" if llm_plan else "template"
        print(f"[*] Execution plan created ({generation_type}): {filename}", file=sys.stderr)

        return {
            "status": "success",
            "action": f"Execution plan created ({generation_type})",
            "file_path": str(filepath),
            "objective": objective,
            "generation_type": generation_type,
            "summary": f"Plan created for: {objective}",
            "next_steps": [
                f"Review plan at: {filepath}",
                "Adjust phases as needed",
                "Execute using Ralph or manual approach",
            ],
            "error": None,
        }

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return {
            "status": "error",
            "error": str(e),
            "action": None,
        }


def main():
    """Main entry point for skill invocation."""
    parser = argparse.ArgumentParser(
        description="Planning Agent - Creates intelligent execution plans"
    )
    parser.add_argument(
        "task",
        help="Task or project to create a plan for",
    )
    parser.add_argument(
        "--vault",
        help="Path to Obsidian vault",
        default=None,
    )

    args = parser.parse_args()
    result = invoke_planning(args.task, args.vault)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
