#!/bin/bash
DIRTY=$(git diff --name-only HEAD 2>/dev/null | grep -E '(skills/|agents/|\.claude-plugin/|hooks/)' | head -5)
if [ -n "$DIRTY" ]; then
  echo "forge hint: detected uncommitted plugin changes:"
  echo "$DIRTY"
  echo ""
  echo "Consider running /kc-plugin-forge validate-only before committing."
fi
