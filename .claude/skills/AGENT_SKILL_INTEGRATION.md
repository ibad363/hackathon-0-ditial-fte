# Agent Skill Integration Guide

**Purpose:** Enable Claude Code to discover and invoke Agent Skills

## Current Status

Skills are **documented** in `.claude/skills/` but **not directly invocable** by Claude Code via the Skill tool.

## Required Changes for Full Skill Integration

### 1. SKILL.md Format (Already Complete)

All skills have proper YAML frontmatter:

```yaml
---
name: skill-name
description: Brief description
license: Apache-2.0
---

# Skill Name

## Purpose
**Action verbs** what the skill does

## Design Philosophy
- Core principles

## Workflow
1. Step one
2. Step two

## Integration Points
- **Input:** Sources
- **Output:** Destinations
```

### 2. Skill Invocation Script (NEW - Needs Implementation)

Each skill needs an invocable script that Claude Code can call:

**File:** `.claude/skills/skill-name/invoke.py`

```python
#!/usr/bin/env python3
"""
Skill invocation wrapper for skill-name

Usage:
    python invoke.py "task description"
"""

import sys
import json
from pathlib import Path

def invoke_skill(task: str) -> dict:
    """
    Invoke the skill with a task description.

    Args:
        task: Natural language task description

    Returns:
        dict: Result with status, output, and any errors
    """
    try:
        # Import the main skill module
        from skill_module import main_function

        # Execute the skill
        result = main_function(task)

        return {
            "status": "success",
            "output": result,
            "error": None
        }
    except Exception as e:
        return {
            "status": "error",
            "output": None,
            "error": str(e)
        }

if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "help"
    result = invoke_skill(task)
    print(json.dumps(result, indent=2))
```

### 3. Skill Discovery (Already Working)

Claude Code automatically discovers skills in `.claude/skills/` that have SKILL.md files.

**Currently Discoverable Skills:**
- approval-manager
- business-handover
- calendar-manager
- content-generator
- daily-review
- facebook-instagram-manager
- filesystem-manager
- linkedin-manager
- planning-agent
- ralph
- skill-creator
- slack-manager
- social-media-manager
- twitter-manager
- weekly-briefing
- whatsapp-manager
- xero-manager

## How to Invoke Skills

### Via Claude Code (When Implemented)

```bash
# List available skills
/skills

# Invoke a skill
/skill linkedin-manager "Create a post about AI automation"

# Use Ralph for autonomous execution
/ralph-loop "Generate Monday CEO briefing"

# Cancel Ralph
/cancel-ralph
```

### Via PM2 (Current Method)

```bash
# All skills run as PM2 processes
pm2 status

# Check logs
pm2 logs gmail-watcher

# Restart a skill
pm2 restart linkedin-approval-monitor
```

## Implementation Priority

### Phase 1: Core Skills (High Priority)

Skills that need direct invocation:

1. **weekly-briefing** - Generate CEO briefing on demand
2. **daily-review** - Generate daily plan on demand
3. **ralph** - Autonomous task execution
4. **planning-agent** - Create execution plans

### Phase 2: Action Skills (Medium Priority)

Skills that execute actions:

5. **linkedin-manager** - Post to LinkedIn
6. **twitter-manager** - Post to Twitter
7. **facebook-instagram-manager** - Post to FB/IG
8. **email-manager** - Send emails

### Phase 3: Supporting Skills (Low Priority)

9. **approval-manager** - Manual approval workflow
10. **content-generator** - Generate content
11. **business-handover** - CEO handoff doc

## Example Implementation

### weekly-briefing Skill

**Current:** Runs as PM2 cron job (Mondays 7 AM)

**Enhanced:** Can be invoked on demand

```python
# .claude/skills/weekly-briefing/invoke.py

def invoke_skill(task: str) -> dict:
    """Generate CEO briefing on demand."""
    from generate_ceo_briefing import generate_briefing

    if "briefing" in task.lower() or "ceo" in task.lower():
        briefing = generate_briefing()
        return {
            "status": "success",
            "output": f"Generated briefing: {briefing}",
            "file_path": str(briefing)
        }
    else:
        return {
            "status": "error",
            "output": None,
            "error": "Task not recognized. Use: 'Generate CEO briefing'"
        }
```

## Testing Skill Invocation

### Manual Test

```python
# Test skill invocation
python .claude/skills/weekly-briefing/invoke.py "Generate CEO briefing"
```

### Claude Code Test

```
/skill weekly-briefing "Generate CEO briefing for this week"
```

## Summary

**Current State:**
- ✅ Skills organized in `.claude/skills/`
- ✅ SKILL.md files with proper YAML frontmatter
- ✅ Skills discoverable by Claude Code
- ❌ Skills not invocable via Skill tool (need invoke.py scripts)

**Required for Full Integration:**
1. Create `invoke.py` scripts for each skill
2. Test invocation via Claude Code
3. Document invocation patterns

**Recommendation:**
Focus on Phase 1 skills (weekly-briefing, daily-review, ralph, planning-agent) as they provide the most value when invoked on-demand.
