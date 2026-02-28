#!/bin/bash
# Start Ralph Wiggum autonomous loop for AI Employee
# Usage: ./scripts/start-ralph.sh [max_iterations]

set -e

MAX_ITERATIONS=${1:-10}
RALPH_DIR="ralph"

echo "🤖 Starting Ralph Wiggum Autonomous Loop"
echo "═══════════════════════════════════════════════════════"
echo ""

# Check if Ralph directory exists
if [ ! -d "$RALPH_DIR" ]; then
  echo "❌ Error: Ralph directory not found"
  echo "   Expected: ./ralph/"
  exit 1
fi

# Check if prd.json exists
if [ ! -f "$RALPH_DIR/prd.json" ]; then
  echo "❌ No task list found (prd.json)"
  echo ""
  echo "Please create a task list first:"
  echo "   1. Edit ralph/prd.json with your tasks"
  echo "   2. Or use Claude Code to generate one"
  echo "   3. See docs/RALPH_IMPLEMENTATION_GUIDE.md for help"
  echo ""
  echo "Example: ralph/prd.json.example"
  exit 1
fi

# Show task overview
echo "📋 Task Overview:"
TOTAL=$(cat "$RALPH_DIR/prd.json" | jq '.userStories | length' 2>/dev/null || echo 0)
COMPLETED=$(cat "$RALPH_DIR/prd.json" | jq '[.userStories[] | select(.passes == true)] | length' 2>/dev/null || echo 0)
echo "   Total tasks: $TOTAL"
echo "   Completed: $COMPLETED"
echo "   Remaining: $((TOTAL - COMPLETED))"
echo ""

if [ "$COMPLETED" -eq "$TOTAL" ]; then
  echo "✅ All tasks are already complete!"
  echo "   Reset prd.json to start new tasks, or archive this run."
  exit 0
fi

# Show pending tasks
echo "📌 Pending Tasks:"
cat "$RALPH_DIR/prd.json" | jq -r '.userStories[] | select(.passes == false) | "  \(.priority). \(.id): \(.title)"' 2>/dev/null | sort -n || echo "  No pending tasks"
echo ""

echo "🔄 Starting Ralph with max $MAX_ITERATIONS iterations..."
echo "   Vault: AI_Employee_Vault"
echo "   Prompt: ralph/prompt-ai-employee.md"
echo ""
echo "⚠️  Ralph will:"
echo "   1. Pick highest priority task"
echo "   2. Execute autonomously"
echo "   3. Request approval for external actions"
echo "   4. Wait for your approval"
echo "   5. Continue until all tasks complete"
echo ""
echo "Press Ctrl+C to stop Ralph at any time"
echo ""

# Make script executable
chmod +x "$RALPH_DIR/ralph-claude.sh"

# Run Ralph
cd "$RALPH_DIR"
./ralph-claude.sh $MAX_ITERATIONS

# Exit with Ralph's exit code
RALPH_EXIT=$?
echo ""
if [ $RALPH_EXIT -eq 0 ]; then
  echo "🎉 Ralph completed all tasks successfully!"
else
  echo "⚠️  Ralph exited with code $RALPH_EXIT"
  echo "   Check ralph/progress.txt for details"
fi

exit $RALPH_EXIT
