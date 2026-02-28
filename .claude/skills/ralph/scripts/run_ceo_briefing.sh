#!/bin/bash
# Run Monday Morning CEO Briefing via Ralph Wiggum
# This script starts Ralph with the CEO briefing task list

set -e

RALPH_DIR=".claude/skills/ralph"
TASK_FILE="$RALPH_DIR/prd_monday_ceo_briefing.json"
MAX_ITERATIONS=20

echo "=========================================="
echo "Monday Morning CEO Briefing"
echo "=========================================="
echo ""
echo "Starting Ralph Wiggum autonomous execution..."
echo ""

# Check if task file exists
if [ ! -f "$TASK_FILE" ]; then
    echo "❌ Task file not found: $TASK_FILE"
    exit 1
fi

# Show task overview
echo "📋 Tasks to be completed:"
TOTAL=$(cat "$TASK_FILE" | jq '.userStories | length' 2>/dev/null || echo 0)
COMPLETED=$(cat "$TASK_FILE" | jq '[.userStories[] | select(.passes == true)] | length' 2>/dev/null || echo 0)
echo "   Total tasks: $TOTAL"
echo "   Completed: $COMPLETED"
echo "   Remaining: $((TOTAL - COMPLETED))"
echo ""

if [ "$COMPLETED" -eq "$TOTAL" ]; then
    echo "✅ All tasks are already complete!"
    echo ""
    echo "To reset and run again, mark tasks as passes: false in prd.json"
    exit 0
fi

echo "🔄 Starting Ralph with CEO briefing task list..."
echo "   Max iterations: $MAX_ITERATIONS"
echo ""

# Make Ralph script executable
chmod +x "$RALPH_DIR/scripts/ralph-claude.sh"

# Run Ralph
cd "$RALPH_DIR"
./scripts/ralph-claude.sh $MAX_ITERATIONS

# Exit with Ralph's exit code
RALPH_EXIT=$?
echo ""
if [ $RALPH_EXIT -eq 0 ]; then
    echo "=========================================="
    echo "✅ Monday Morning CEO Briefing Complete!"
    echo "=========================================="
    echo ""
    echo "Check your Briefings folder for the output:"
    echo "   AI_Employee_Vault/Briefings/YYYY-MM-DD_Monday_Briefing.md"
    echo "   AI_Employee_Vault/Briefings/YYYY-MM-DD_Monday_Actions.md"
else
    echo "=========================================="
    echo "⚠️  Ralph encountered issues (exit code: $RALPH_EXIT)"
    echo "=========================================="
    echo "   Check Ralph progress: $RALPH_DIR/progress.txt"
fi

exit $RALPH_EXIT
