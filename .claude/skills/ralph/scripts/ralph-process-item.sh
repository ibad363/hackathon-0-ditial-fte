#!/bin/bash
# Ralph Item Processor - Process individual items with Claude Code
# Usage: ./ralph-process-item.sh <item_path>

set -e

ITEM_PATH="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go up from .claude/skills/ralph/scripts/ to project root
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
VAULT_PATH="$PROJECT_ROOT/AI_Employee_Vault"

if [ -z "$ITEM_PATH" ]; then
  echo "Error: No item path provided"
  exit 1
fi

# Convert relative path to absolute
if [[ ! "$ITEM_PATH" = /* ]]; then
  # Check if path already starts with vault relative components
  if [[ "$ITEM_PATH" == Needs_Action/* ]] || [[ "$ITEM_PATH" == In_Progress/* ]] || [[ "$ITEM_PATH" == Pending_Approval/* ]] || [[ "$ITEM_PATH" == Approved/* ]] || [[ "$ITEM_PATH" == Done/* ]]; then
    ITEM_PATH="$VAULT_PATH/$ITEM_PATH"
  else
    # Path is relative to current directory
    ITEM_PATH="$(pwd)/$ITEM_PATH"
  fi
fi

if [ ! -f "$ITEM_PATH" ]; then
  echo "Error: Item not found at $ITEM_PATH"
  exit 1
fi

ITEM_NAME=$(basename "$ITEM_PATH")
ITEM_RELATIVE="${ITEM_PATH#$VAULT_PATH/}"

# Create prompt for this item
PROMPT="# AI Employee Task Processing

You are processing an item detected by the AI Employee system.

## Task Item
**File:** $ITEM_RELATIVE

**Instructions:**
1. Read the item file to understand what needs to be done
2. Check Dashboard.md for context
3. Check Company_Handbook.md for rules
4. Think about the best approach
5. Execute the task using available tools and skills
6. For external actions (email, social media, payments):
   - Create approval request in Pending_Approval/
   - Wait for human approval (monitor Approved/ folder)
   - Execute after approval
7. Move completed item to Done/
8. Update relevant files

## Available Skills:
- email-manager: Send/reply to emails
- calendar-manager: Create/update calendar events
- slack-manager: Send Slack messages
- linkedin-manager: Post to LinkedIn
- twitter-manager: Post to Twitter/X
- facebook-instagram-manager: Post to Facebook/Instagram
- whatsapp-manager: Send WhatsApp messages
- odoo-manager: Accounting operations
- content-generator: Generate content
- weekly-briefing: Generate business summaries
- approval-manager: Manage approval workflow

## Important Rules:
- Always get human approval for external actions
- Follow Company_Handbook.md rules
- Log all actions
- Be thorough and thoughtful
- Create clear documentation

Process this item now. When complete, move it to Done/ and output:
\`\`\`
<promise>ITEM_COMPLETE:$ITEM_NAME</promise>
\`\`\`
"

# Run Claude Code with the prompt
cd "$VAULT_PATH"
echo "$PROMPT" | claude 2>&1
