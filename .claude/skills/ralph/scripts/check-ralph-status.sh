#!/bin/bash
# Check Ralph Wiggum status and progress
# Usage: ./scripts/check-ralph-status.sh

set -e

PRD_FILE="ralph/prd.json"
PROGRESS_FILE="ralph/progress.txt"
VAULT="AI_Employee_Vault"

echo "📊 Ralph Wiggum Status"
echo "═══════════════════════════════════════════════════════"
echo ""

# Check if Ralph is running
RALPH_PID=$(pgrep -f "ralph-claude.sh" || true)
if [ -n "$RALPH_PID" ]; then
  echo "🟢 Status: Running"
  echo "   PID: $RALPH_PID"
else
  echo "⚪ Status: Not running"
fi
echo ""

# Check if prd.json exists
if [ ! -f "$PRD_FILE" ]; then
  echo "❌ No task list found (prd.json)"
  echo ""
  echo "To get started:"
  echo "   1. Create prd.json in ralph/ directory"
  echo "   2. Add tasks following the format in prd.json.example"
  echo "   3. Run: ./scripts/start-ralph.sh 10"
  exit 1
fi

# Task overview
TOTAL=$(cat "$PRD_FILE" | jq '.userStories | length' 2>/dev/null || echo 0)
COMPLETED=$(cat "$PRD_FILE" | jq '[.userStories[] | select(.passes == true)] | length' 2>/dev/null || echo 0)
REMAINING=$((TOTAL - COMPLETED))

echo "📋 Task Progress:"
echo "   Total tasks: $TOTAL"
echo "   ✅ Completed: $COMPLETED"
echo "   ⏳ Remaining: $REMAINING"
echo ""

if [ "$REMAINING" -eq 0 ]; then
  echo "🎉 All tasks complete!"
  echo ""
  echo "To start a new task list:"
  echo "   1. Archive current prd.json (if desired)"
  echo "   2. Create new prd.json with fresh tasks"
  echo "   3. Run Ralph again"
  exit 0
fi

# Show pending tasks
echo "📌 Pending Tasks (in priority order):"
echo ""
cat "$PRD_FILE" | jq -r '.userStories[] | select(.passes == false) | "  \(.priority). \(.id): \(.title)"' 2>/dev/null | sort -n || echo "  No pending tasks"
echo ""

# Show completed tasks
if [ "$COMPLETED" -gt 0 ]; then
  echo "✅ Completed Tasks:"
  echo ""
  cat "$PRD_FILE" | jq -r '.userStories[] | select(.passes == true) | "  \(.id): \(.title)"' 2>/dev/null || echo "  No completed tasks"
  echo ""
fi

# Show recent progress
if [ -f "$PROGRESS_FILE" ]; then
  echo "📝 Recent Progress (last 20 lines):"
  echo ""
  tail -20 "$PROGRESS_FILE"
else
  echo "📝 No progress log yet (Ralph hasn't run)"
fi

echo ""
echo "═══════════════════════════════════════════════════════"

# Useful commands
echo ""
echo "🔧 Useful Commands:"
echo ""
echo "Start Ralph:"
echo "   ./scripts/start-ralph.sh [max_iterations]"
echo ""
echo "View full task list:"
echo "   cat ralph/prd.json | jq '.'"
echo ""
echo "View specific task:"
echo "   cat ralph/prd.json | jq '.userStories[0]'"
echo ""
echo "Mark task complete:"
echo "   # Edit ralph/prd.json, set passes: true for the task"
echo ""
echo "Reset all tasks:"
echo "   # Edit ralph/prd.json, set all passes: false"
echo ""
echo "View vault folders:"
echo "   ls $VAULT/Pending_Approval/"
echo "   ls $VAULT/Approved/"
echo "   ls $VAULT/Done/"
