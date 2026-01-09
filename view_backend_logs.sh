#!/bin/bash
# View backend logs in real-time or save to file

echo "================================"
echo "Backend Log Viewer"
echo "================================"
echo ""
echo "Choose an option:"
echo "  1) View logs in real-time (live updates)"
echo "  2) Save last 200 lines to file"
echo "  3) Search for policy selections"
echo "  4) Search for Q-values"
echo ""
read -p "Enter choice (1-4): " choice

TERMINAL_FILE="/Users/tzhang/.cursor/projects/Users-tzhang-projects-a2i2-survey/terminals/7.txt"

case $choice in
  1)
    echo ""
    echo "📺 Watching live logs... (Press Ctrl+C to stop)"
    echo ""
    tail -f "$TERMINAL_FILE" 2>/dev/null || echo "Terminal 7 not found. Is the server running?"
    ;;
  2)
    OUTPUT_FILE="backend_logs_$(date +%Y%m%d_%H%M%S).txt"
    tail -200 "$TERMINAL_FILE" > "$OUTPUT_FILE" 2>/dev/null
    if [ $? -eq 0 ]; then
      echo "✅ Saved 200 lines to: $OUTPUT_FILE"
    else
      echo "❌ Could not read Terminal 7"
    fi
    ;;
  3)
    echo ""
    echo "🔍 Policy Selections:"
    echo "─────────────────────────────────────"
    grep "Selected policy:" "$TERMINAL_FILE" 2>/dev/null || echo "No policy selections found"
    ;;
  4)
    echo ""
    echo "📊 Q-Values:"
    echo "─────────────────────────────────────"
    grep "Q-values:" "$TERMINAL_FILE" 2>/dev/null || echo "No Q-values found"
    ;;
  *)
    echo "Invalid choice"
    ;;
esac

echo ""

