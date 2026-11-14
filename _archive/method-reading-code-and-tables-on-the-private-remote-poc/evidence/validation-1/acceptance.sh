#!/usr/bin/env bash
# Minimal acceptance check (no user-visible surface). Needs gh access to the private working repository; pass its owner/name as $1.
set -u
D=$(mktemp -d); gh repo clone "$1" "$D/c" -- -q && cd "$D/c" || exit 1
git rev-parse HEAD                               # expect 2b391a40f926646b6be949cb2cf07466005e277c
ls behaviour/results/method-against-no-method*/table.md   # expect two tables
for c in behaviour/cells/*/; do python3 -B behaviour/run_cell.py selfcheck "$c" >/dev/null; echo "$c exit=$?"; done   # expect exit=0 x4
python3 -B behaviour/table_rule_check.py >/dev/null; echo "table_rule exit=$?"   # expect 0
git diff --name-only HEAD^ HEAD | grep -cE '/r-|run-?list|blind|packet|key'      # expect 0
rm -rf "$D"
