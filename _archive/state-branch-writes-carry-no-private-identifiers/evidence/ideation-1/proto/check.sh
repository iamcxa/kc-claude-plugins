#!/bin/sh
# prototype: report whether a state checkout is guarded
s="$1"
d=$(git -C "$s" rev-parse --path-format=absolute --git-path hooks) || exit 2
for h in pre-commit pre-push; do
  if [ ! -x "$d/$h" ] || ! grep -q 'state guard' "$d/$h"; then echo "state guard: unguarded; $h hook missing for this checkout"; exit 1; fi
done
echo "state guard: guarded (pre-commit, pre-push)"
