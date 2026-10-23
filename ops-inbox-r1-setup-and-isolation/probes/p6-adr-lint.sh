#!/usr/bin/env bash
# P6: the axis ADR draft from the task file against kc-adr's linter. $1 = a kc-claude-plugins checkout, $2 = the task file.
set -u
L=$(mktemp -d); mkdir -p "$L/docs/adr"
git -C "$1" show origin/main:kc-adr/scripts/adr_lint.py > "$L/adr_lint.py"
F="$L/docs/adr/0099-every-ops-event-becomes-a-prepared-decision.md"
awk '/^### Axis ADR draft/{f=1} f&&/^### Contract v1/{exit} f&&/^> ?/' "$2" | sed -E 's/^> ?//' | sed 's/^# NNNN\./# 0099./' > "$F"
cd "$L"; python3 -I adr_lint.py docs/adr --require 0099; echo "draft: exit $?"
python3 -I adr_lint.py docs/adr --require 0100; echo "wrong number: exit $?"
grep -v '^\*\*Words:\*\*' "$F" > "$F.tmp" && mv "$F.tmp" "$F"; python3 -I adr_lint.py docs/adr --require 0099; echo "no Words lines: exit $?"
rm -rf "$L"
