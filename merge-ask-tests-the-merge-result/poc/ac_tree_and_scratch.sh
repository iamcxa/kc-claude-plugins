#!/bin/bash
# AC-7: the merge result merge-run tests is the tree that landed; AC-8: merge-run leaves no scratch.
# Usage: ac_tree_and_scratch.sh <delivery_gate.py> <code repo> <workflow dir>
set -u
gate=$1 repo=$2 wf=$3
built=$(git -C "$repo" merge-tree --write-tree eeee002303aca7c14237258253cd9318a5b3248c 6da9a765ee04e1e2c7836517ba01f75b0ea91d73)
landed=$(git -C "$repo" rev-parse '571a7bd8a24ce08fac149fbcc91c4561610834c7^{tree}')
echo "merge-tree of trunk eeee0023 and head 6da9a765: $built"
echo "tree of landed squash commit 571a7bd8:        $landed"
[ "$built" = "$landed" ] || { echo "AC-7 FAIL: trees differ"; exit 1; }
work=$(mktemp -d) tmp=$(mktemp -d)
touch "$work/t.md"
TMPDIR=$tmp python3 -B "$gate" merge-run "$work/t.md" --pr iamcxa/kc-claude-plugins#841 \
  --head 6da9a765ee04e1e2c7836517ba01f75b0ea91d73 --trunk 546a136386c94c58e430c91a6f3457b38bd73880 \
  --workflow-dir "$wf" --repo-dir "$repo" -- true
code=$?
left=$(find "$tmp" -mindepth 1 | wc -l | tr -d ' ')
echo "merge-run exit $code; entries left in its TMPDIR: $left; record: $(ls "$work/t/merge")"
rm -rf "$work" "$tmp"
[ "$code" = 0 ] && [ "$left" = 0 ] || { echo "AC-8 FAIL"; exit 1; }
echo "AC-7 and AC-8 hold"
