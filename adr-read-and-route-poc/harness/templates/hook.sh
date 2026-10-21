#!/bin/sh
# Session-start listing of ruling titles. Disposable harness piece; prints titles only, never a Status or body.
cd "$(dirname "$0")/../mira-app" || exit 0
echo "Rulings recorded for this workspace (titles only; open a ruling before relying on it):"
for repo in ../mira-decisions .; do
  echo "- $(git -C "$repo" remote get-url origin | sed 's#.*/\(example/[^/]*\)\.git#\1#') ($repo):"
  for f in "$repo"/docs/adr/[0-9]*.md; do
    printf '    %s\n' "$(head -n 1 "$f" | sed 's/^# //')"
  done
done
