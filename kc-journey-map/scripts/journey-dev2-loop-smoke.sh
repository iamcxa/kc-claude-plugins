#!/usr/bin/env bash
# Runs the ruling-to-map loop against the real Spacedock CLI in a disposable workflow:
# gate record, footprint add/check/audit, archive, reconcile, fold. Needs `spacedock`, `node`
# and python3 on PATH, and runs from a checkout that holds both kc-journey-map and kc-dev-flow-2.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FOOT="$HERE/../kc-dev-flow-2/extensions/journey-map/map_footprint.py"
FOLD="$HERE/lib/journey-fold.mjs"
RECON="$HERE/lib/journey-reconcile.mjs"
[ -f "$FOOT" ] || { echo "missing $FOOT: kc-dev-flow-2 must be in the checkout" >&2; exit 2; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
WF="$TMP/wf"
mkdir -p "$WF"
fail=0

# expect <exit code> <label> <command...>: runs, prints the code and the output, asserts the code.
expect() {
  local want="$1" label="$2"; shift 2
  local code=0 out
  out="$("$@" 2>&1)" || code=$?
  printf '%s: exit %s\n' "$label" "$code"
  [ -z "$out" ] || printf '%s\n' "$out" | sed 's/^/    /'
  if [ "$code" != "$want" ]; then echo "FAIL $label: wanted exit $want" >&2; fail=1; fi
  LAST="$out"
}
has() { # has <label> <pattern>: the last output contains the pattern
  if ! grep -Eq -- "$2" <<<"$LAST"; then echo "FAIL $1: output lacks /$2/" >&2; fail=1; fi
}

cat > "$WF/README.md" <<'YAML'
---
commissioned-by: kc-dev-flow-2
entity-type: task
id-style: slug
entity-label: task
entity-label-plural: tasks
stages:
  defaults:
    worktree: false
    concurrency: 1
  states:
    - name: backlog
      initial: true
      gate: true
    - name: implementation
    - name: done
      terminal: true
---

# smoke workflow
YAML
cat > "$WF/shop-task.md" <<'YAML'
---
title: A journey task
status: backlog
journey: shop
journey-release: r1
journey-story: enter-by-qr
---

## FO alignment

Release: none
YAML
node --input-type=module -e "
import { writeFileSync } from 'node:fs'
import { FLOW, BLOCK } from '$HERE/lib/fixtures/journey-fold-shapes.mjs'
writeFileSync('$TMP/flow.yaml', FLOW)
writeFileSync('$TMP/block.yaml', BLOCK)"
MAP="$TMP/flow.yaml"

git -C "$TMP" init -q -b main
git -C "$TMP" -c user.name=smoke -c user.email=smoke@example.invalid -c commit.gpgsign=false add wf
git -C "$TMP" -c user.name=smoke -c user.email=smoke@example.invalid -c commit.gpgsign=false -c core.hooksPath=/dev/null commit -qm seed
sd() { spacedock "$@" --workflow-dir "$WF"; }
sd status --validate >/dev/null
sd gate prepare shop-task --question "Who issues codes?" --artifact "$WF/shop-task.md" --summary "smoke" >/dev/null
sd gate record shop-task --decision approve --actor person:captain \
  --reason "Captain smoke: 「好，由平台發」" >/dev/null
TASK="$WF/shop-task.md"

echo "== 1. a ruling with no footprint is caught twice"
expect 1 "check, no footprint" python3 "$FOOT" check "$TASK"
mkdir -p "$WF/_archive"
mv "$TASK" "$WF/shop-task" "$WF/_archive/"
expect 1 "audit, archived without a record" python3 "$FOOT" audit "$WF" --since 2000-01-01
has audit 'unrecorded 1'
expect 1 "reconcile, archived without a record" node "$RECON" "$MAP" --workflow-dir "$WF"
has reconcile 'stale-open 1'

echo "== 2. the footprint is added; the map does not hold it yet"
mv "$WF/_archive/shop-task.md" "$WF/_archive/shop-task" "$WF/"
expect 0 "add" python3 "$FOOT" add "$TASK" --question q1 --source "$(grep -o 'gate-attempt:[^ ]*' "$TASK" | head -1)" \
  --words "好，由平台發" --answer "Platform issues codes."
printf 'Map footprints: 1 in footprints.jsonl\n' >> "$TASK"
expect 0 "check, with footprint" python3 "$FOOT" check "$TASK"
expect 0 "audit, with a record" python3 "$FOOT" audit "$WF" --since 2000-01-01
mv "$TASK" "$WF/shop-task" "$WF/_archive/"
expect 1 "reconcile, footprint unfolded" node "$RECON" "$MAP" --workflow-dir "$WF"
has reconcile 'unfolded 1'

echo "== 3. the fold writes a draft and the count reaches 0"
FP="$WF/_archive/shop-task/footprints.jsonl"
before="$(shasum -a 256 "$MAP")"
expect 0 "fold" node "$FOLD" "$MAP" --footprints "$FP" --out "$TMP/draft.yaml"
has fold 'applied fp:shop-task:1'
[ "$(shasum -a 256 "$MAP")" = "$before" ] || { echo "FAIL source file changed" >&2; fail=1; }
expect 1 "fold, existing --out is refused" node "$FOLD" "$MAP" --footprints "$FP" --out "$TMP/draft.yaml"
expect 0 "fold twice" node "$FOLD" "$TMP/draft.yaml" --footprints "$FP" --out "$TMP/draft2.yaml"
has fold-twice 'already fp:shop-task:1'
cmp -s "$TMP/draft.yaml" "$TMP/draft2.yaml" || { echo "FAIL folding twice changed bytes" >&2; fail=1; }
changed="$(diff "$MAP" "$TMP/draft.yaml" | grep -c '^[<>]' || true)"
echo "lines differing (flow shape): $changed"
[ "$changed" = 2 ] || { echo "FAIL flow fold touched $changed lines, wanted one removed and one added" >&2; fail=1; }
expect 0 "reconcile on the draft" node "$RECON" "$TMP/draft.yaml" --workflow-dir "$WF"
has reconcile-draft 'answered 2'
has reconcile-draft 'unfolded 0'
has reconcile-draft 'stale-open 0'

echo "== 4. another major is refused by both consumers"
printf '{"schema":"journey-footprint/v2","kind":"answered"}\n' > "$TMP/v2.jsonl"
expect 1 "fold, v2 line" node "$FOLD" "$MAP" --footprints "$TMP/v2.jsonl" --out "$TMP/v2-draft.yaml"
has fold-v2 'journey-footprint/v2'
cp "$FP" "$TMP/fp.bak"
printf '{"schema":"journey-footprint/v2","kind":"answered"}\n' >> "$FP"
expect 1 "reconcile, v2 line" node "$RECON" "$MAP" --workflow-dir "$WF"
has reconcile-v2 'journey-footprint/v2'
cp "$TMP/fp.bak" "$FP"

echo "== 5. a block-style map takes the fold as added lines inside the question"
FPB="$TMP/block.jsonl"
node --input-type=module -e "
import { writeFileSync } from 'node:fs'
import { footprint } from '$HERE/lib/fixtures/journey-fold-shapes.mjs'
writeFileSync('$FPB', JSON.stringify(footprint({ journey: 'review', story: 'front-door', question: 'public-contract' })) + '\n')"
expect 0 "fold, block shape" node "$FOLD" "$TMP/block.yaml" --footprints "$FPB" --out "$TMP/block-draft.yaml"
removed="$(diff "$TMP/block.yaml" "$TMP/block-draft.yaml" | grep -c '^<' || true)"
added="$(diff "$TMP/block.yaml" "$TMP/block-draft.yaml" | grep -c '^>' || true)"
echo "lines removed $removed, added $added"
{ [ "$removed" = 0 ] && [ "$added" = 3 ]; } || { echo "FAIL block fold wanted 0 removed, 3 added" >&2; fail=1; }

if [ "$fail" = 0 ]; then echo "journey-dev2-loop-smoke: all steps passed"; else echo "journey-dev2-loop-smoke: FAILED" >&2; exit 1; fi
