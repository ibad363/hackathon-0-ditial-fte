#!/bin/bash
# Ralph Wiggum for AI Employee - Autonomous loop
# Usage: ./ralph-claude.sh [max_iterations]

set -e

MAX_ITERATIONS=${1:-10}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../" && pwd)"
VAULT_PATH="$PROJECT_ROOT/AI_Employee_Vault"
PRD_FILE="$SCRIPT_DIR/prd.json"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"
ARCHIVE_DIR="$SCRIPT_DIR/archive"
LAST_TASK_FILE="$SCRIPT_DIR/.last-task"

# Ensure vault exists
if [ ! -d "$VAULT_PATH" ]; then
  echo "❌ Error: Vault not found at $VAULT_PATH"
  exit 1
fi

# Archive previous run if task changed
if [ -f "$PRD_FILE" ] && [ -f "$LAST_TASK_FILE" ]; then
  CURRENT_TASK=$(jq -r '.description // empty' "$PRD_FILE" 2>/dev/null || echo "")
  LAST_TASK=$(cat "$LAST_TASK_FILE" 2>/dev/null || echo "")

  if [ -n "$CURRENT_TASK" ] && [ -n "$LAST_TASK" ] && [ "$CURRENT_TASK" != "$LAST_TASK" ]; then
    # Archive the previous run
    DATE=$(date +%Y-%m-%d)
    # Create safe folder name from description
    FOLDER_NAME=$(echo "$LAST_TASK" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-50)
    ARCHIVE_FOLDER="$ARCHIVE_DIR/$DATE-$FOLDER_NAME"

    echo "📦 Archiving previous run: $LAST_TASK"
    mkdir -p "$ARCHIVE_FOLDER"
    [ -f "$PRD_FILE" ] && cp "$PRD_FILE" "$ARCHIVE_FOLDER/"
    [ -f "$PROGRESS_FILE" ] && cp "$PROGRESS_FILE" "$ARCHIVE_FOLDER/"
    echo "   Archived to: $ARCHIVE_FOLDER"

    # Reset progress file for new run
    echo "# Ralph Progress Log - AI Employee" > "$PROGRESS_FILE"
    echo "Started: $(date)" >> "$PROGRESS_FILE"
    echo "" >> "$PROGRESS_FILE"
    echo "## Codebase Patterns" >> "$PROGRESS_FILE"
    echo "" >> "$PROGRESS_FILE"
    echo "## Task Progress" >> "$PROGRESS_FILE"
    echo "" >> "$PROGRESS_FILE"
  fi
fi

# Track current task
if [ -f "$PRD_FILE" ]; then
  CURRENT_TASK=$(jq -r '.description // empty' "$PRD_FILE" 2>/dev/null || echo "")
  if [ -n "$CURRENT_TASK" ]; then
    echo "$CURRENT_TASK" > "$LAST_TASK_FILE"
  fi
fi

# Initialize progress file if it doesn't exist
if [ ! -f "$PROGRESS_FILE" ]; then
  echo "# Ralph Progress Log - AI Employee" > "$PROGRESS_FILE"
  echo "Started: $(date)" >> "$PROGRESS_FILE"
  echo "" >> "$PROGRESS_FILE"
  echo "## Codebase Patterns" >> "$PROGRESS_FILE"
  echo "" >> "$PROGRESS_FILE"
  echo "## Task Progress" >> "$PROGRESS_FILE"
  echo "" >> "$PROGRESS_FILE"
fi

echo "🤖 Starting Ralph for AI Employee"
echo "📁 Vault: $VAULT_PATH"
echo "🔄 Max iterations: $MAX_ITERATIONS"
echo ""

# Check if prd.json exists
if [ ! -f "$PRD_FILE" ]; then
  echo "❌ No prd.json found in $SCRIPT_DIR"
  echo ""
  echo "Please create a task list first:"
  echo "  1. Use Claude Code to generate prd.json"
  echo "  2. Or copy prd.json.example and modify it"
  echo "  3. See docs/RALPH_IMPLEMENTATION_GUIDE.md for details"
  exit 1
fi

# Show task overview
TOTAL_TASKS=$(cat "$PRD_FILE" | jq '.userStories | length' 2>/dev/null || echo "0")
COMPLETED_TASKS=$(cat "$PRD_FILE" | jq '[.userStories[] | select(.passes == true)] | length' 2>/dev/null || echo "0")
echo "📋 Tasks: $COMPLETED_TASKS / $TOTAL_TASKS completed"
echo ""

for i in $(seq 1 $MAX_ITERATIONS); do
  echo ""
  echo "═══════════════════════════════════════════════════════"
  echo "  Ralph Iteration $i of $MAX_ITERATIONS"
  echo "═══════════════════════════════════════════════════════"

  # Run Claude Code with Ralph prompt
  cd "$VAULT_PATH"
  OUTPUT=$(cat "$SCRIPT_DIR/prompt-ai-employee.md" | claude --cwd "$VAULT_PATH" 2>&1 | tee /dev/stderr) || true

  # Check for completion signal
  if echo "$OUTPUT" | grep -q "<promise>TASK_COMPLETE</promise>"; then
    echo ""
    echo "✅ Ralph completed all tasks!"
    echo "   Completed at iteration $i of $MAX_ITERATIONS"
    echo ""
    echo "📊 Final Status:"
    cat "$PRD_FILE" | jq -r '.userStories[] | "  \(.id): \(.title) - \(.passes)"' 2>/dev/null || echo "  Could not display tasks"
    exit 0
  fi

  echo "Iteration $i complete. Continuing..."
  sleep 2
done

echo ""
echo "⚠️  Ralph reached max iterations ($MAX_ITERATIONS) without completing all tasks."
echo "📝 Check $PROGRESS_FILE for status."
echo ""
echo "📊 Remaining tasks:"
cat "$PRD_FILE" | jq -r '.userStories[] | select(.passes == false) | "  \(.id): \(.title)"' 2>/dev/null || echo "  Could not display tasks"
exit 1
