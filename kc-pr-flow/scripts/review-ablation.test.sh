#!/usr/bin/env bash
# Tests for review-ablation.sh — the A/B skill-ablation harness.
#
# Three groups, all model-free:
#
#   comparator   the eight pinned fixtures of test-plan item 1. Every expected
#                value is an EXACT ENUMERATION produced by the ideation artifact
#                docs/dev/artifacts/skill-ablation-harness/sizing-simulation.py,
#                which is a different implementation by a different author. No
#                expected value here was read off this harness's own output.
#   arm          the span-match post-conditions of test-plan item 2. The
#                authority is the enumerated span table + its pinned sha256
#                sidecar (review-ablation-spans.tsv), never the set of spans the
#                builder happened to apply.
#   guard        the five false-null guards of AC-3 plus their positive control.
#                The authority is the runner-written manifest, whose provenance
#                pins are derived from the arm, prompt, runtime, and checkout
#                rather than copied from the agent-authored receipt.
#
# Every negative case constructs a defective artifact and requires a non-zero
# exit with a named error. Every group carries a positive control, because a
# check that only ever rejects is indistinguishable from a check that is broken.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ABLATION="$HERE/review-ablation.sh"
PLUGIN_ROOT="$(cd "$HERE/.." && pwd)"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEST_ROOT"' EXIT

PASS=0
FAIL=0
CASE='all'

if [ "${1:-}" = '--case' ] && [ "$#" -eq 2 ]; then
  CASE="$2"
elif [ "$#" -ne 0 ]; then
  printf 'usage: review-ablation.test.sh [--case comparator|arm|guard|run]\n' >&2
  exit 2
fi

case "$CASE" in
  all|comparator|arm|guard|run) ;;
  *)
    printf 'review-ablation.test.sh: unknown case: %s\n' "$CASE" >&2
    exit 2
    ;;
esac

pass() { PASS=$((PASS + 1)); }
fail() { FAIL=$((FAIL + 1)); printf 'FAIL: %s\n' "$1"; }

assert_eq() { # $1=description $2=expected $3=actual
  if [ "$2" = "$3" ]; then
    pass
  else
    fail "$1 (expected [$2], got [$3])"
  fi
}

# Assert a command exits non-zero AND names the failure. A non-zero exit with an
# empty diagnostic is indistinguishable from a crash, so both are required.
assert_rejects() { # $1=description $2=expected-error-substring $3..=command
  local description="$1" needle="$2" out rc
  shift 2
  out="$("$@" 2>&1)"
  rc=$?
  if [ "$rc" -eq 0 ]; then
    fail "$description (expected non-zero exit, got 0)"
    return
  fi
  case "$out" in
    *"$needle"*) pass ;;
    *) fail "$description (exit $rc but error did not name [$needle]; got: $(printf '%s' "$out" | head -3 | tr '\n' ' '))" ;;
  esac
}

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'review-ablation.test.sh: %s is required\n' "$1" >&2
    exit 69
  fi
}
require jq
require python3

# ---------------------------------------------------------------- fixture I/O

sha_of() { printf '%s' "$1" | shasum -a 256 | awk '{print $1}'; }

ARM_MANIFEST_SHA="$(sha_of arm-manifest)"
DRIVER_PROMPT_SHA="$(sha_of driver-prompt)"
MODEL_ID='claude-test-1'

# Emit one manifest + one receipt for a single run.
#
# emit_run <dir> <arm> <pr_number> <run_index> <claim_keys> <skill_sha> <tokens> <severity>
#
# claim_keys is a space-separated list; the empty string means a zero-finding
# run. Every other provenance field is held constant across a fixture so the
# guards stay quiet and only the dimension under test moves.
emit_run() {
  local dir="$1" arm="$2" pr="$3" idx="$4" keys="$5" skill_sha="$6" tokens="$7" sev="$8"
  local receipt manifest findings key stamp
  mkdir -p "$dir/manifests" "$dir/receipts"
  receipt="$dir/receipts/$arm-$pr-$idx.json"
  manifest="$dir/manifests/$arm-$pr-$idx.json"

  findings='[]'
  for key in $keys; do
    findings="$(printf '%s' "$findings" | jq -c --arg k "$key" --arg s "$sev" \
      '. + [{path:"src/a.ts",side:"RIGHT",anchor_sha256:("a"*64),
             evidence_sha256:("b"*64),category:"correctness",claim_key:$k,
             severity:$s,confidence:5,line:10}]')"
  done

  # The manifest is written by the runner BEFORE the agent runs, so its
  # timestamp necessarily precedes the receipt's. Fixtures respect that
  # ordering; the stale-receipt fixture below deliberately inverts it.
  jq -n --arg arm "$arm" --argjson pr "$pr" --argjson idx "$idx" \
        --arg path "$receipt" --arg skill "$skill_sha" \
        --arg arm_manifest "$ARM_MANIFEST_SHA" \
        --arg prompt "$DRIVER_PROMPT_SHA" --arg model "$MODEL_ID" \
    '{schema:"kc-pr-flow.ablation-manifest/v2",
      experiment_id:"11111111-1111-1111-1111-111111111111",
      nonce:"22222222-2222-2222-2222-222222222222",
      arm:$arm, run_index:$idx, slot_index:$idx,
      pr:{repository:"acme/widgets",number:$pr,base_sha:("c"*40),head_sha:("d"*40)},
      skill_sha256:$skill,
      arm_manifest_sha256:$arm_manifest,
      driver_prompt_sha256:$prompt,
      model_id:$model,
      checkout:{path:"/fixture",base_sha:("c"*40),head_sha:("d"*40),
                diff_sha256:("7"*64)},
      run_started_at:"2026-07-28T00:00:00Z",
      expected_receipt_path:$path}' >"$manifest"

  stamp="2026-07-28T01:00:0${idx}Z"
  jq -n --arg arm "$arm" --argjson pr "$pr" --argjson idx "$idx" \
        --argjson findings "$findings" --arg skill "$skill_sha" \
        --arg arm_manifest "$ARM_MANIFEST_SHA" \
        --arg prompt "$DRIVER_PROMPT_SHA" --arg model "$MODEL_ID" \
        --argjson tokens "$tokens" --arg stamp "$stamp" \
    '{schema:"kc-pr-flow.ablation-run/v3",
      arm:$arm, run_index:$idx, slot_index:$idx,
      experiment_id:"11111111-1111-1111-1111-111111111111",
      nonce:"22222222-2222-2222-2222-222222222222",
      pr:{repository:"acme/widgets",number:$pr,base_sha:("c"*40),head_sha:("d"*40)},
      skill_sha256:$skill,
      arm_manifest_sha256:$arm_manifest,
      driver_prompt_sha256:$prompt,
      model_id:$model,
      findings:$findings,
      usage:{input_tokens:$tokens,output_tokens:0,cache_creation_input_tokens:0,
             cache_read_input_tokens:9999,total_cost_usd:2.53},
      wallclock_ms:(1000+$idx), written_at:$stamp}' >"$receipt"
}

SKILL_A="$(sha_of arm-A-skill)"
SKILL_B="$(sha_of arm-B-skill)"

# Build an M-PR, N-run-per-arm fixture. arm A runs take their fingerprint sets
# from a_spec, arm B from b_spec; each spec is a '|'-separated list of
# space-separated claim-key groups, one group per run.
build_fixture() { # <dir> <m> <a_spec> <b_spec> [tokens_a] [tokens_b] [sev_a] [sev_b]
  local dir="$1" m="$2" a_spec="$3" b_spec="$4"
  local tok_a="${5:-100}" tok_b="${6:-100}" sev_a="${7:-HIGH}" sev_b="${8:-HIGH}"
  local p i old_ifs
  local -a a_groups b_groups
  # Split the specs on '|' ONCE, with IFS restored before emit_run runs — that
  # function splits its own key list on whitespace, so leaking IFS='|' into it
  # collapses every run to a single finding and quietly turns each fixture into
  # the disjoint case.
  old_ifs="$IFS"
  IFS='|' read -r -a a_groups <<<"$a_spec"
  IFS='|' read -r -a b_groups <<<"$b_spec"
  IFS="$old_ifs"

  rm -rf "$dir"
  for ((p = 1; p <= m; p++)); do
    for i in "${!a_groups[@]}"; do
      emit_run "$dir" A "$p" "$i" "${a_groups[$i]}" "$SKILL_A" "$tok_a" "$sev_a"
    done
    for i in "${!b_groups[@]}"; do
      emit_run "$dir" B "$p" "$i" "${b_groups[$i]}" "$SKILL_B" "$tok_b" "$sev_b"
    done
  done
}

verdict_of() { # <dir> [mode] [arms]
  "$ABLATION" compare --mode "${2:-AB}" --arms "${3:-A,B}" --manifest-dir "$1/manifests"
}

# Round a float to 6 places so a pinned exact value compares stably.
round6() { python3 -c 'import sys;print(f"{float(sys.argv[1]):.6f}")' "$1"; }

# ------------------------------------------------------- group: comparator
#
# Authority for every expected value in this group:
#   docs/dev/artifacts/skill-ablation-harness/sizing-simulation.py, exact
#   enumeration over the full C(2N,N)^M assignment space. Reproduced there as:
#     floor           (2/6)^3  = 0.037037   (2/20)^3 = 0.001000
#     disjoint        N=2/M=3 -> 0.0370     N=3/M=3 -> 0.0010
#     superset        N=2/M=3 -> 0.0370
#     identical       -> 1.0000
#     joint must-flag -> 0.0010, all three dimensions
#     joint tokens    -> 0.0010, tokens only
#     joint must-not  -> 1.0000, none
#     joint empty     -> 1.0000, none, no ZeroDivisionError
# The sign-flipped case is enumerated by the same script's machinery; its
# construction and both values are recorded in the stage report.

run_comparator_cases() {
  local dir out

  # F1 — identical fingerprint sets across arms. T=0, p=1, not material.
  # Fails if the statistic is inverted (an inverted T would flag identity).
  dir="$TEST_ROOT/f1"
  build_fixture "$dir" 3 'x y|x y|x y' 'x y|x y|x y'
  out="$(verdict_of "$dir")"
  assert_eq 'F1 identical: T_anchor' '0.000000' "$(round6 "$(printf '%s' "$out" | jq -r '.t_observed.anchor_set')")"
  assert_eq 'F1 identical: p_joint' '1.000000' "$(round6 "$(printf '%s' "$out" | jq -r '.p_joint')")"
  assert_eq 'F1 identical: material' 'false' "$(printf '%s' "$out" | jq -r '.material')"
  assert_eq 'F1 identical: flagged_dimensions empty' '0' "$(printf '%s' "$out" | jq -r '.flagged_dimensions | length')"

  # F2 — disjoint sets, perfect within-arm agreement, N=3/M=3. T=1, p=1/1000.
  # Fails if the permutation enumeration is wrong (any other assignment count
  # moves this value off the floor).
  dir="$TEST_ROOT/f2"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  out="$(verdict_of "$dir")"
  assert_eq 'F2 disjoint N=3/M=3: T_anchor' '1.000000' "$(round6 "$(printf '%s' "$out" | jq -r '.t_observed.anchor_set')")"
  assert_eq 'F2 disjoint N=3/M=3: p_anchor' '0.001000' "$(round6 "$(printf '%s' "$out" | jq -r '.p_dim.anchor_set')")"
  assert_eq 'F2 disjoint N=3/M=3: p_joint' '0.001000' "$(round6 "$(printf '%s' "$out" | jq -r '.p_joint')")"
  assert_eq 'F2 disjoint N=3/M=3: material' 'true' "$(printf '%s' "$out" | jq -r '.material')"
  assert_eq 'F2 disjoint N=3/M=3: assignment space' '8000' "$(printf '%s' "$out" | jq -r '.assignments')"

  # F2b — the same shape at N=2/M=3, which pins the floor formula
  # (2/C(2N,N))^M rather than the single number 1/1000. Fails if the
  # label-swap collapse is not accounted for (1/6^3 = 0.00463 instead).
  dir="$TEST_ROOT/f2b"
  build_fixture "$dir" 3 'x y|x y' 'u v|u v'
  out="$(verdict_of "$dir")"
  assert_eq 'F2b disjoint N=2/M=3: p_anchor is 1/27' '0.037037' "$(round6 "$(printf '%s' "$out" | jq -r '.p_dim.anchor_set')")"
  assert_eq 'F2b disjoint N=2/M=3: assignment space' '216' "$(printf '%s' "$out" | jq -r '.assignments')"

  # F3 — arm B a consistent superset of arm A. T=1/3, p=1/27 at N=2/M=3.
  dir="$TEST_ROOT/f3"
  build_fixture "$dir" 3 'x y|x y' 'x y z|x y z'
  out="$(verdict_of "$dir")"
  assert_eq 'F3 superset: T_anchor is 1/3' '0.333333' "$(round6 "$(printf '%s' "$out" | jq -r '.t_observed.anchor_set')")"
  assert_eq 'F3 superset: p_anchor is 1/27' '0.037037' "$(round6 "$(printf '%s' "$out" | jq -r '.p_dim.anchor_set')")"

  # F4 — SIGN-FLIPPED: between-arm agreement EXCEEDS within-arm agreement, so
  # D(p) is negative, and |D| is the extreme of the assignment space. The
  # two-sided statistic reaches the same floor as F2. A signed one-sided
  # statistic reports p=1.0 on this exact data, so this assertion is what fails
  # if anyone reverts T to the round-1 signed form.
  dir="$TEST_ROOT/f4"
  build_fixture "$dir" 3 'a b|b c|b d' 'a b c|a d|b'
  out="$(verdict_of "$dir")"
  assert_eq 'F4 sign-flipped: D(p) is negative' 'true' \
    "$(printf '%s' "$out" | jq -r '.per_pr[0].anchor_set < 0')"
  assert_eq 'F4 sign-flipped: p_anchor equals the F2 floor' '0.001000' \
    "$(round6 "$(printf '%s' "$out" | jq -r '.p_dim.anchor_set')")"
  assert_eq 'F4 sign-flipped: material' 'true' "$(printf '%s' "$out" | jq -r '.material')"

  # F5 — all three dimensions moved. p_joint at the floor, all three flagged.
  dir="$TEST_ROOT/f5"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v' 100 300 HIGH NIT
  out="$(verdict_of "$dir")"
  assert_eq 'F5 all three moved: p_joint' '0.001000' "$(round6 "$(printf '%s' "$out" | jq -r '.p_joint')")"
  assert_eq 'F5 all three moved: flagged_dimensions' 'anchor_set severity_mix tokens' \
    "$(printf '%s' "$out" | jq -r '.flagged_dimensions | sort | join(" ")')"

  # F6 — tokens move ALONE; anchors and severities are identical across arms.
  # Only `tokens` may be flagged. This is the assertion that fails if the
  # max-statistic flags every dimension whenever any one of them moves.
  dir="$TEST_ROOT/f6"
  build_fixture "$dir" 3 'x y|x y|x y' 'x y|x y|x y' 100 300 HIGH HIGH
  out="$(verdict_of "$dir")"
  assert_eq 'F6 tokens only: p_joint' '0.001000' "$(round6 "$(printf '%s' "$out" | jq -r '.p_joint')")"
  assert_eq 'F6 tokens only: flagged_dimensions is tokens alone' 'tokens' \
    "$(printf '%s' "$out" | jq -r '.flagged_dimensions | sort | join(" ")')"

  # F7 — arms identical on all three dimensions. Must not fire.
  dir="$TEST_ROOT/f7"
  build_fixture "$dir" 3 'x y|x y|x y' 'x y|x y|x y' 100 100 HIGH HIGH
  out="$(verdict_of "$dir")"
  assert_eq 'F7 identical arms: p_joint' '1.000000' "$(round6 "$(printf '%s' "$out" | jq -r '.p_joint')")"
  assert_eq 'F7 identical arms: no dimension flagged' '0' \
    "$(printf '%s' "$out" | jq -r '.flagged_dimensions | length')"

  # F8 — every run zero-finding on both arms. The severity histogram carries a
  # dedicated EMPTY category, so this is similarity 1, not a division by zero.
  dir="$TEST_ROOT/f8"
  build_fixture "$dir" 3 '||' '||'
  out="$(verdict_of "$dir")"
  assert_eq 'F8 all-empty runs: p_joint' '1.000000' "$(round6 "$(printf '%s' "$out" | jq -r '.p_joint')")"
  assert_eq 'F8 all-empty runs: severity_mix defined (not null)' 'true' \
    "$(printf '%s' "$out" | jq -r '.t_observed.severity_mix != null')"
  assert_eq 'F8 all-empty runs: no dimension flagged' '0' \
    "$(printf '%s' "$out" | jq -r '.flagged_dimensions | length')"

  # The verdict must carry both certification sentences, so the residual
  # travels with the artifact instead of living only in the entity body.
  assert_eq 'verdict carries certifies.null_result' 'true' \
    "$(printf '%s' "$out" | jq -r '(.certifies.null_result // "") | length > 0')"
  assert_eq 'verdict carries certifies.detection_scope' 'true' \
    "$(printf '%s' "$out" | jq -r '(.certifies.detection_scope // "") | length > 0')"
  assert_eq 'verdict echoes the invoked mode' 'AB' "$(printf '%s' "$out" | jq -r '.mode')"
}

# ------------------------------------------------------------- group: arm
#
# Authority: the enumerated span table and its pinned sha256 sidecar
# (review-ablation-spans.tsv), both of which exist before the builder runs.
# NEVER the set of spans the builder applied — checking only what was applied is
# a check that cannot fail.

BASELINE="$PLUGIN_ROOT"

run_arm_cases() {
  local dir out

  # B8 (positive control, run first so the negatives are known to be
  # discriminating rather than universal) — the full 11-span ablation is
  # ACCEPTED and writes a manifest recording the resolved span set.
  dir="$TEST_ROOT/arm-ok"
  out="$("$ABLATION" arm --tree "$BASELINE" --dest "$dir/B" --arm B 2>&1)"
  assert_eq 'B8 full ablation accepted' '0' "$?"
  assert_eq 'B8 arm manifest records 11 CUT spans' '11' \
    "$(jq -r '[.spans[] | select(.kind != "keep")] | length' "$dir/B/arm-manifest.json" 2>/dev/null)"
  assert_eq 'B8 arm manifest records the post-condition result' 'pass' \
    "$(jq -r '.post_condition.span_match' "$dir/B/arm-manifest.json" 2>/dev/null)"
  assert_eq 'B8 keyword canary recorded as a canary, not the proof' 'canary' \
    "$(jq -r '.post_condition.keyword_grep_role' "$dir/B/arm-manifest.json" 2>/dev/null)"

  # Arm A is the unablated baseline and must also be accepted, with a
  # skill_sha256 that differs from arm B's.
  "$ABLATION" arm --tree "$BASELINE" --dest "$dir/A" --arm A >/dev/null 2>&1
  assert_eq 'B8 arm A and arm B skill_sha256 differ' 'true' \
    "$(python3 -c 'import json,sys
a=json.load(open(sys.argv[1]))["skill_sha256"]
b=json.load(open(sys.argv[2]))["skill_sha256"]
print("true" if a!=b else "false")' "$dir/A/arm-manifest.json" "$dir/B/arm-manifest.json" 2>/dev/null)"

  # B4 — THE LOAD-BEARING CASE. An arm that removes only the 7 keyword-bearing
  # spans leaves S2, S3, S4 and S10 on disk, still instructing the gate. The
  # round-2 keyword post-condition ACCEPTS it. Span match must REJECT it.
  assert_rejects 'B4 keyword-only arm is rejected by span match' 'CUT span still present' \
    "$ABLATION" arm --tree "$BASELINE" --dest "$TEST_ROOT/arm-kw" --arm B --spans S1,S5,S6,S7,S8,S9,S11

  # ...and the rejection must name the four spans the keyword grep cannot see,
  # not merely fail. A rejection for the wrong reason is not this check passing.
  out="$("$ABLATION" arm --tree "$BASELINE" --dest "$TEST_ROOT/arm-kw2" --arm B \
    --spans S1,S5,S6,S7,S8,S9,S11 2>&1)"
  for sid in S2 S3 S4 S10; do
    case "$out" in
      *"$sid"*) pass ;;
      *) fail "B4 rejection names $sid (the spans the keyword grep cannot see)" ;;
    esac
  done

  # B1 — a removal whose target text is not present EXACTLY ONCE. The sprint's
  # own silent-no-op failure, encoded: a patch that matches two places removes
  # the wrong one and still reports success. Constructed so the pin still holds
  # (line 975 is untouched) and only the uniqueness precondition breaks, which
  # is what keeps this case distinct from B3's pin drift.
  dir="$TEST_ROOT/arm-nosuch"
  mkdir -p "$dir"
  cp -R "$BASELINE" "$dir/tree"
  python3 - "$dir/tree/skills/kc-pr-review/SKILL.md" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
body = p.read_text(encoding="utf-8")
line = body.split("\n")[974]
p.write_text(body + "\n" + line + "\n", encoding="utf-8")
PY
  assert_rejects 'B1 ablation target not uniquely present' 'expected exactly 1' \
    "$ABLATION" arm --tree "$dir/tree" --dest "$dir/out" --arm B

  # B2 — an empty baseline hit set. With no spans selected there is nothing to
  # prove was removed, and an arm B that removed nothing must not be usable.
  assert_rejects 'B2 empty baseline hit set' 'empty' \
    "$ABLATION" arm --tree "$BASELINE" --dest "$TEST_ROOT/arm-empty" --arm B --spans ''

  # B3 — a resolved span whose sha256 disagrees with its pin: the tree moved
  # under the enumeration table. The pins are the authority; a mismatch is a
  # signal to re-derive, never to hand-adjust the line numbers.
  dir="$TEST_ROOT/arm-drift"
  mkdir -p "$dir"
  cp -R "$BASELINE" "$dir/tree"
  python3 - "$dir/tree/reference/review-triage.md" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
body = p.read_text(encoding="utf-8").split("\n")
# Reword one line INSIDE S10's range, leaving the line count untouched. The
# range still resolves to real content, so it is the sha256 comparison — not
# the empty-span guard — that has to catch this.
body[223] = body[223] + " (reworded since the table was enumerated)"
p.write_text("\n".join(body), encoding="utf-8")
PY
  assert_rejects 'B3 span sha256 disagrees with its pin' 'does not match its pin' \
    "$ABLATION" arm --tree "$dir/tree" --dest "$dir/out" --arm B

  # B5 — a KEEP span missing from the built arm. K2 is the collator's
  # confidence table: ablating it would remove a SECOND, independent mechanism
  # and confound AC-2. Injected by asking the builder to also cut K2.
  assert_rejects 'B5 KEEP span K2 ablated is rejected' 'K2' \
    "$ABLATION" arm --tree "$BASELINE" --dest "$TEST_ROOT/arm-keep" --arm B \
    --spans S1,S2,S3,S4,S5,S6,S7,S8,S9,S10,S11,K2

  # B6 — S6 is an EDIT, not a cut: only the substring ' after the verification
  # gate' goes, and '**Apply confidence gates**' must survive. Cutting the whole
  # line would ablate confidence gating as well and confound AC-2.
  #
  # The defective artifact is a span table whose S6 row is mistyped `cut`
  # instead of `cut_sub` — the realistic way this is lost, since the table is
  # hand-maintained data. The authority the check reads is the literal
  # surviving-half string enumerated in the spec, not anything the builder
  # produced.
  dir="$TEST_ROOT/arm-s6"
  mkdir -p "$dir"
  awk -F '\t' 'BEGIN {OFS="\t"} $1 == "S6" {$5="cut"; $6="-"} {print}' \
    "$HERE/review-ablation-spans.tsv" >"$dir/mistyped.tsv" 2>/dev/null
  assert_rejects 'B6 S6 surviving half lost' 'Apply confidence gates' \
    "$ABLATION" arm --tree "$BASELINE" --dest "$dir/out" --arm B --table "$dir/mistyped.tsv"

  # B7 — a residual keyword-canary hit outside the K1 whitelist means the
  # enumeration table missed a site. A CLEAN canary proves nothing; a DIRTY one
  # is a real failure. Injected into a file the table does not enumerate.
  dir="$TEST_ROOT/arm-canary"
  mkdir -p "$dir"
  cp -R "$BASELINE" "$dir/tree"
  printf '\nEvery finding must pass the pre-emit verification gate before posting.\n' \
    >>"$dir/tree/reference/learned-patterns.md"
  assert_rejects 'B7 residual keyword canary hit fails the build' 'canary' \
    "$ABLATION" arm --tree "$dir/tree" --dest "$dir/out" --arm B

  # B9 — remove_span must validate and mutate the same exact bytes. A CUT span
  # at a true EOF has no trailing newline; the old implementation counted
  # `text` but replaced `text + "\n"`, so it silently wrote the file unchanged.
  dir="$TEST_ROOT/arm-eof"
  mkdir -p "$dir/tree/skills/kc-pr-review"
  printf 'header\ntrue eof span' >"$dir/tree/skills/kc-pr-review/SKILL.md"
  printf 'E1\tskills/kc-pr-review/SKILL.md\t2\t2\tcut\t%s\n' \
    "$(sha_of 'true eof span')" >"$dir/spans.tsv"
  "$ABLATION" arm --tree "$dir/tree" --dest "$dir/out" --arm B \
    --table "$dir/spans.tsv" >/dev/null 2>&1
  assert_eq 'B9 EOF span without trailing newline is removed' 'header' \
    "$(cat "$dir/out/skills/kc-pr-review/SKILL.md" 2>/dev/null)"

  # B10 — every cut_sub row owns its removal text. A second cut_sub in another
  # file must remove that row's text, never reuse S6's module-level constant.
  dir="$TEST_ROOT/arm-cut-sub"
  mkdir -p "$dir/tree/skills/kc-pr-review" "$dir/tree/reference"
  printf '**Apply confidence gates** after the verification gate\n' \
    >"$dir/tree/skills/kc-pr-review/SKILL.md"
  printf 'Keep prefix and remove second clause\n' >"$dir/tree/reference/second.md"
  {
    printf 'S6\tskills/kc-pr-review/SKILL.md\t1\t1\tcut_sub\t after the verification gate\t%s\n' \
      "$(sha_of '**Apply confidence gates** after the verification gate')"
    printf 'S12\treference/second.md\t1\t1\tcut_sub\t and remove second clause\t%s\n' \
      "$(sha_of 'Keep prefix and remove second clause')"
  } >"$dir/spans.tsv"
  "$ABLATION" arm --tree "$dir/tree" --dest "$dir/out" --arm B \
    --table "$dir/spans.tsv" >/dev/null 2>&1
  assert_eq 'B10 second cut_sub uses its own enumerated removal text' 'Keep prefix' \
    "$(cat "$dir/out/reference/second.md" 2>/dev/null)"
}

# ----------------------------------------------------------- group: guard
#
# Authority: the runner-written manifest. It is written before the agent is
# launched through a separate runner path, so every guard compares the receipt
# against runner-authored state. This is not an OS-enforced trust boundary.

run_guard_cases() {
  local dir

  # C6 (positive control first) — arm A and arm A' with EQUAL skill_sha256 are
  # ACCEPTED under --mode AA and emit a verdict. This is what proves the
  # mode-dependent arming check is not simply always-reject.
  dir="$TEST_ROOT/g-aa"
  build_fixture "$dir" 3 'x y|x y|x y' 'x y|x y|x y'
  # rebuild arm B as A_prime carrying arm A's skill hash
  python3 - "$dir" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
skill_a = None
for f in sorted((root / "receipts").glob("A-*.json")):
    skill_a = json.loads(f.read_text())["skill_sha256"]
for f in sorted((root / "receipts").glob("B-*.json")):
    d = json.loads(f.read_text()); d["arm"] = "A_prime"; d["skill_sha256"] = skill_a
    f.rename(f.with_name(f.name.replace("B-", "A_prime-", 1))).write_text(json.dumps(d))
for f in sorted((root / "manifests").glob("B-*.json")):
    d = json.loads(f.read_text()); d["arm"] = "A_prime"; d["skill_sha256"] = skill_a
    d["expected_receipt_path"] = d["expected_receipt_path"].replace("/B-", "/A_prime-")
    f.rename(f.with_name(f.name.replace("B-", "A_prime-", 1))).write_text(json.dumps(d))
PY
  assert_eq 'C6 AA with equal skill_sha256 is accepted' 'false' \
    "$(verdict_of "$dir" AA A,A_prime | jq -r '.material')"
  assert_eq 'C6 AA verdict echoes its arms' 'A A_prime' \
    "$(verdict_of "$dir" AA A,A_prime | jq -r '.arms | join(" ")')"

  # C1 — mis-armed pair: both arms carry the SAME skill_sha256 though the
  # invocation says AB. Under AB the hashes are required to DIFFER.
  dir="$TEST_ROOT/g-misarmed"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  python3 - "$dir" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
for f in (root / "receipts").glob("B-*.json"):
    d = json.loads(f.read_text()); d["skill_sha256"] = "1" * 64; f.write_text(json.dumps(d))
for f in (root / "receipts").glob("A-*.json"):
    d = json.loads(f.read_text()); d["skill_sha256"] = "0" * 64; f.write_text(json.dumps(d))
PY
  assert_rejects 'C1 fabricated receipt-only skill hashes disagree with runner manifests' \
    'skill_sha256 disagrees with its runner-written manifest' verdict_of "$dir" AB A,B

  # ...and the mirror: differing hashes under AA must also be rejected, or the
  # check is one-sided and AC-1 could be run on a genuinely ablated pair.
  dir="$TEST_ROOT/g-aa-differ"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  assert_rejects 'C1b differing skill_sha256 under AA' 'skill_sha256' verdict_of "$dir" AA A,B

  # C2 — a failed run: the manifest names an expected_receipt_path that holds
  # no file. Observed for real in spike 2, where a run exited is_error:false
  # having written no receipt. It must never read as an empty finding set.
  dir="$TEST_ROOT/g-missing"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  rm -f "$dir/receipts/B-2-1.json"
  assert_rejects 'C2 missing receipt at the manifest path' 'no receipt' verdict_of "$dir" AB A,B

  # C3a — a stale receipt: its nonce disagrees with the manifest's.
  dir="$TEST_ROOT/g-nonce"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  python3 - "$dir/receipts/B-1-0.json" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1]); d = json.loads(p.read_text())
d["nonce"] = "99999999-9999-9999-9999-999999999999"; p.write_text(json.dumps(d))
PY
  assert_rejects 'C3a receipt nonce disagrees with its manifest' 'nonce' verdict_of "$dir" AB A,B

  # C3b — a stale receipt at a reused output path: written_at PRECEDES the
  # manifest's run_started_at, so the file predates the run that claims it.
  dir="$TEST_ROOT/g-stale"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  python3 - "$dir/receipts/B-1-0.json" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1]); d = json.loads(p.read_text())
d["written_at"] = "2020-01-01T00:00:00Z"; p.write_text(json.dumps(d))
PY
  assert_rejects 'C3b receipt predates its manifest run_started_at' 'run_started_at' verdict_of "$dir" AB A,B

  # C4 — two receipts equal under the duplicate projection (canonical JSON
  # minus run_index, slot_index, written_at): one receipt copied across runs to
  # inflate within-arm agreement. Constructible precisely BECAUSE those three
  # fields are projected out; round 1 hashed them in, so its guard could never
  # fire.
  dir="$TEST_ROOT/g-dupe"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  python3 - "$dir" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
src = json.loads((root / "receipts" / "B-1-0.json").read_text())
dst = json.loads((root / "receipts" / "B-1-1.json").read_text())
src.update({"run_index": dst["run_index"], "slot_index": dst["slot_index"],
            "written_at": dst["written_at"]})
(root / "receipts" / "B-1-1.json").write_text(json.dumps(src))
PY
  assert_rejects 'C4 duplicate receipt under the projection' 'duplicate' verdict_of "$dir" AB A,B

  # C5 — provenance disagreement anywhere across the experiment, not merely
  # within the compared pair. A silently substituted model invalidates the
  # comparison even if it happened on the arm not being read.
  dir="$TEST_ROOT/g-model"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  python3 - "$dir/receipts/B-3-2.json" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1]); d = json.loads(p.read_text())
d["model_id"] = "claude-substituted-9"; p.write_text(json.dumps(d))
PY
  assert_rejects 'C5 model_id disagrees across the experiment' 'model_id' verdict_of "$dir" AB A,B

  dir="$TEST_ROOT/g-prompt"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  python3 - "$dir/receipts/A-2-1.json" <<'PY'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1]); d = json.loads(p.read_text())
d["driver_prompt_sha256"] = "0" * 64; p.write_text(json.dumps(d))
PY
  assert_rejects 'C5b driver_prompt_sha256 disagrees across the experiment' 'driver_prompt_sha256' \
    verdict_of "$dir" AB A,B

  # V1's remaining pins are checked against the independent run manifest, not
  # merely for receipt-to-receipt consistency. Each defect below rewrites every
  # receipt consistently; the rejected implementation accepted all three.
  dir="$TEST_ROOT/g-arm-manifest"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  python3 - "$dir" <<'PY'
import json, pathlib, sys
for f in (pathlib.Path(sys.argv[1]) / "receipts").glob("*.json"):
    d = json.loads(f.read_text()); d["arm_manifest_sha256"] = "9" * 64
    f.write_text(json.dumps(d))
PY
  assert_rejects 'C5c arm_manifest_sha256 must match the runner manifest' \
    'arm_manifest_sha256 disagrees with its runner-written manifest' verdict_of "$dir" AB A,B

  dir="$TEST_ROOT/g-prompt-authority"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  python3 - "$dir" <<'PY'
import json, pathlib, sys
for f in (pathlib.Path(sys.argv[1]) / "receipts").glob("*.json"):
    d = json.loads(f.read_text()); d["driver_prompt_sha256"] = "8" * 64
    f.write_text(json.dumps(d))
PY
  assert_rejects 'C5d driver_prompt_sha256 must match the runner manifest' \
    'driver_prompt_sha256 disagrees with its runner-written manifest' verdict_of "$dir" AB A,B

  dir="$TEST_ROOT/g-model-authority"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  python3 - "$dir" <<'PY'
import json, pathlib, sys
for f in (pathlib.Path(sys.argv[1]) / "receipts").glob("*.json"):
    d = json.loads(f.read_text()); d["model_id"] = "fabricated-model"
    f.write_text(json.dumps(d))
PY
  assert_rejects 'C5e model_id must match the runner manifest' \
    'model_id disagrees with its runner-written manifest' verdict_of "$dir" AB A,B

  # The falsifying edit named in AC-3: if the receipt loader ever defaults a
  # missing file to {"findings": []}, C2 must go red. C2 covers the rejection;
  # this pins the positive half it is the complement of — the verdict reports
  # the literal number of runs it consumed, so a loader that silently
  # substituted an empty receipt would have to either report 18 while one file
  # is absent (caught by C2) or report a short count here.
  dir="$TEST_ROOT/g-count"
  build_fixture "$dir" 3 'x y|x y|x y' 'u v|u v|u v'
  assert_eq 'C2b verdict reports the literal run count it consumed' '18' \
    "$(verdict_of "$dir" AB A,B | jq -r '.runs_compared')"
}

# ------------------------------------------------------------- group: run
#
# `run` is where spike 2's finding lives: a real headless review exited
# is_error:false at turn 43 having deferred to background work, and wrote no
# receipt. These cases are model-free — KC_PR_FLOW_ABLATION_EXEC substitutes a
# stub for the agent — and pin the two halves of that lesson.

make_source_repo() {
  local dir="$1"
  mkdir -p "$dir"
  git -C "$dir" init -q
  git -C "$dir" config user.name 'Ablation Test'
  git -C "$dir" config user.email 'ablation@example.invalid'
  printf 'base\n' >"$dir/review.txt"
  git -C "$dir" add review.txt
  git -C "$dir" commit -qm base
  TEST_BASE_SHA="$(git -C "$dir" rev-parse HEAD)"
  printf 'head\n' >"$dir/review.txt"
  git -C "$dir" commit -qam head
  TEST_HEAD_SHA="$(git -C "$dir" rev-parse HEAD)"
}

make_arm() {
  local dest="$1" arm="${2:-B}"
  "$ABLATION" arm --tree "$BASELINE" --dest "$dest" --arm "$arm" >/dev/null
}

make_corpus() {
  local path="$1"
  printf 'acme/widgets\t63\t%s\t%s\n' "$TEST_BASE_SHA" "$TEST_HEAD_SHA" >"$path"
}

write_stub() {
  local path="$1"
  cat >"$path" <<'STUB'
#!/usr/bin/env bash
set -u
pwd >"${KC_PR_FLOW_ABLATION_TEST_CWD:?}"
git rev-parse HEAD >"${KC_PR_FLOW_ABLATION_TEST_HEAD:?}"
jq -n \
  --arg arm "$KC_PR_FLOW_ABLATION_ARM" \
  --argjson run "$KC_PR_FLOW_ABLATION_RUN_INDEX" \
  --argjson slot "$KC_PR_FLOW_ABLATION_SLOT_INDEX" \
  --arg exp "$KC_PR_FLOW_ABLATION_EXPERIMENT_ID" \
  --arg nonce "$KC_PR_FLOW_ABLATION_NONCE" \
  --arg repo "$KC_PR_FLOW_ABLATION_REPOSITORY" \
  --argjson pr "$KC_PR_FLOW_ABLATION_PR_NUMBER" \
  --arg base "$KC_PR_FLOW_ABLATION_BASE_SHA" \
  --arg head "$KC_PR_FLOW_ABLATION_HEAD_SHA" \
  --arg skill "$KC_PR_FLOW_ABLATION_SKILL_SHA256" \
  --arg arm_manifest "$KC_PR_FLOW_ABLATION_ARM_MANIFEST_SHA256" \
  --arg prompt "$KC_PR_FLOW_ABLATION_DRIVER_PROMPT_SHA256" \
  '{schema:"kc-pr-flow.ablation-run/v3",arm:$arm,run_index:$run,slot_index:$slot,
    experiment_id:$exp,nonce:$nonce,
    pr:{repository:$repo,number:$pr,base_sha:$base,head_sha:$head},
    skill_sha256:$skill,arm_manifest_sha256:$arm_manifest,
    driver_prompt_sha256:$prompt,model_id:"claude-test-1",findings:[],
    usage:{input_tokens:1,output_tokens:1,cache_creation_input_tokens:1,
      cache_read_input_tokens:0,total_cost_usd:0.01},
    wallclock_ms:1,written_at:"2099-01-01T00:00:00Z"}' \
  >"$KC_PR_FLOW_ABLATION_RECEIPT"
printf '%s\n' '{"is_error":false,"duration_ms":3210,"total_cost_usd":0.12,"usage":{"input_tokens":11,"output_tokens":12,"cache_creation_input_tokens":13,"cache_read_input_tokens":14},"modelUsage":{"claude-test-1":{"canonicalModel":"claude-test-1"}}}'
STUB
  chmod +x "$path"
}

run_run_cases() {
  local dir stub out manifest corpus

  # R1 — the ordinary path. The manifest must be written BEFORE the agent runs,
  # which is the whole reason it can serve as a freshness authority: a record
  # written afterwards could be back-dated by whatever it is checking.
  dir="$TEST_ROOT/run-ok"
  mkdir -p "$dir"
  make_source_repo "$dir/source"
  make_arm "$dir/arm"
  corpus="$dir/corpus.tsv"
  make_corpus "$corpus"
  stub="$dir/stub.sh"
  write_stub "$stub"
  out="$(
    cd "$TEST_ROOT" || exit 1
    KC_PR_FLOW_ABLATION_EXEC="$stub" \
      KC_PR_FLOW_ABLATION_TEST_CWD="$dir/agent-cwd" \
      KC_PR_FLOW_ABLATION_TEST_HEAD="$dir/agent-head" \
      "$ABLATION" run \
      --arm-dir run-ok/arm --arm B --experiment-id e1 --nonce n1 \
      --run-index 0 --slot-index 2 --repository acme/widgets --pr-number 63 \
      --base-sha "$TEST_BASE_SHA" --head-sha "$TEST_HEAD_SHA" \
      --source-repo run-ok/source --corpus run-ok/corpus.tsv \
      --out-dir run-ok/out --model test-model 2>&1
  )"
  assert_eq 'R1 run reports the receipt path it collected' "$dir/out/receipts/B-63-0.json" "$out"

  manifest="$dir/out/manifests/B-63-0.json"
  assert_eq 'R1 manifest names the receipt path the runner will read' \
    "$dir/out/receipts/B-63-0.json" "$(jq -r '.expected_receipt_path' "$manifest")"
  assert_eq 'R1 manifest records the randomized slot assignment' '2' \
    "$(jq -r '.slot_index' "$manifest")"
  assert_eq 'R1 manifest carries a run_started_at taken before launch' 'true' \
    "$(jq -r '(.run_started_at // "") | length > 0' "$manifest")"
  assert_eq 'R1 manifest binds skill_sha256 from the arm manifest' \
    "$(jq -r '.skill_sha256' "$dir/arm/arm-manifest.json")" \
    "$(jq -r '.skill_sha256' "$manifest")"
  assert_eq 'R1 manifest binds arm_manifest_sha256 from the arm manifest' \
    "$(jq -r '.arm_manifest_sha256' "$dir/arm/arm-manifest.json")" \
    "$(jq -r '.arm_manifest_sha256' "$manifest")"
  assert_eq 'R1 manifest binds the independently hashed driver prompt' \
    "$(shasum -a 256 "$HERE/review-ablation-driver-prompt.md" | awk '{print $1}')" \
    "$(jq -r '.driver_prompt_sha256' "$manifest")"
  assert_eq 'R1 manifest binds the runtime-reported model id' 'claude-test-1' \
    "$(jq -r '.model_id' "$manifest")"
  assert_eq 'R1 agent ran from a pristine checkout at the frozen head' "$TEST_HEAD_SHA" \
    "$(cat "$dir/agent-head" 2>/dev/null)"
  assert_eq 'R1 manifest records independently resolved checkout head' "$TEST_HEAD_SHA" \
    "$(jq -r '.checkout.head_sha' "$manifest")"
  assert_eq 'R1 manifest records a non-empty base-to-head diff hash' 'true' \
    "$(jq -r '(.checkout.diff_sha256 // "") | test("^[0-9a-f]{64}$")' "$manifest")"
  assert_eq 'R1 receipt usage comes from runner JSON, not agent self-report' \
    '11 12 13 14 0.12' \
    "$(jq -r '.usage | [.input_tokens,.output_tokens,
      .cache_creation_input_tokens,.cache_read_input_tokens,.total_cost_usd]
      | join(" ")' "$dir/out/receipts/B-63-0.json")"
  assert_eq 'R1 receipt wallclock comes from runner JSON' '3210' \
    "$(jq -r '.wallclock_ms' "$dir/out/receipts/B-63-0.json")"

  # R2 — THE SPIKE-2 SHAPE. The agent exits CLEAN and writes nothing. This must
  # be a failed run, never an empty finding set: if a missing receipt silently
  # became "0 findings", both arms would compare identical and the harness would
  # report "no material difference" for a review that never finished.
  dir="$TEST_ROOT/run-noreceipt"
  mkdir -p "$dir"
  make_source_repo "$dir/source"
  make_arm "$dir/arm"
  corpus="$dir/corpus.tsv"
  make_corpus "$corpus"
  stub="$dir/stub.sh"
  cat >"$stub" <<'STUB'
#!/usr/bin/env bash
printf '{"is_error":false}\n'
exit 0
STUB
  chmod +x "$stub"
  assert_rejects 'R2 clean exit with no receipt is a FAILED run' 'wrote no receipt' \
    env KC_PR_FLOW_ABLATION_EXEC="$stub" "$ABLATION" run \
    --arm-dir "$dir/arm" --arm B --experiment-id e1 --nonce n1 \
    --run-index 0 --slot-index 0 --repository acme/widgets --pr-number 63 \
    --base-sha "$TEST_BASE_SHA" --head-sha "$TEST_HEAD_SHA" \
    --source-repo "$dir/source" --corpus "$corpus" \
    --out-dir "$dir/out" --model test-model

  assert_eq 'R2 no receipt file was invented on the failed path' 'absent' \
    "$([ -e "$dir/out/receipts/B-63-0.json" ] && echo present || echo absent)"

  # R3 — deterministic outputs are cleared before launch and any non-zero
  # headless exit fails immediately. The stale non-empty receipt must not turn
  # a crashed retry into an apparent success.
  dir="$TEST_ROOT/run-crash-stale"
  mkdir -p "$dir"
  make_source_repo "$dir/source"
  make_arm "$dir/arm"
  corpus="$dir/corpus.tsv"
  make_corpus "$corpus"
  stub="$dir/stub.sh"
  cat >"$stub" <<'STUB'
#!/usr/bin/env bash
printf '{"is_error":true}\n'
exit 42
STUB
  chmod +x "$stub"
  mkdir -p "$dir/out/receipts"
  printf '{"schema":"kc-pr-flow.ablation-run/v3","findings":[]}\n' \
    >"$dir/out/receipts/B-63-0.json"
  assert_rejects 'R3 crashed retry rejects a stale non-empty receipt' \
    'headless review exited 42' \
    env KC_PR_FLOW_ABLATION_EXEC="$stub" "$ABLATION" run \
    --arm-dir "$dir/arm" --arm B --experiment-id e1 --nonce n1 \
    --run-index 0 --slot-index 0 --repository acme/widgets --pr-number 63 \
    --base-sha "$TEST_BASE_SHA" --head-sha "$TEST_HEAD_SHA" \
    --source-repo "$dir/source" --corpus "$corpus" \
    --out-dir "$dir/out" --model test-model
  assert_eq 'R3 stale receipt was cleared before the crashed launch' 'absent' \
    "$([ -e "$dir/out/receipts/B-63-0.json" ] && echo present || echo absent)"

  # R4 — a tuple outside the frozen corpus is rejected before any model starts.
  dir="$TEST_ROOT/run-corpus"
  mkdir -p "$dir"
  make_source_repo "$dir/source"
  make_arm "$dir/arm"
  corpus="$dir/corpus.tsv"
  make_corpus "$corpus"
  stub="$dir/stub.sh"
  printf '#!/usr/bin/env bash\nexit 99\n' >"$stub"
  chmod +x "$stub"
  assert_rejects 'R4 runner refuses a revision outside the frozen corpus' \
    'frozen corpus' \
    env KC_PR_FLOW_ABLATION_EXEC="$stub" "$ABLATION" run \
    --arm-dir "$dir/arm" --arm B --experiment-id e1 --nonce n1 \
    --run-index 0 --slot-index 0 --repository acme/widgets --pr-number 63 \
    --base-sha "$TEST_BASE_SHA" --head-sha "$(printf 'f%.0s' {1..40})" \
    --source-repo "$dir/source" --corpus "$corpus" \
    --out-dir "$dir/out" --model test-model

  assert_eq 'R5 default corpus freezes the three approved snapshots exactly' \
    "$(cat <<'EXPECTED'
iamcxa/kc-claude-plugins	17	4489933ddf5237187c4866ab45bdecc5bdb2d0f0	f3aed43341d5fe4616d76ba02946bd4913ae260e
iamcxa/kc-claude-plugins	19	d62f2c6659d76799994482dd58be2dc2b05fb3ea	031b4908cf405724b2ed7d1b829f3c001eea7aa2
iamcxa/kc-claude-plugins	50	536be3e7d7d8371a9e84b693804407ea1b54bc60	7c448243c0512d137a47cdf36a9b255658f096a3
EXPECTED
)" "$(grep -v '^#' "$HERE/review-ablation-corpus.tsv" 2>/dev/null)"

  # V6 — the implementation may claim only what it enforces. The runner writes
  # the manifest independently and withholds its path, but it does not sandbox
  # the agent from every writable ancestor.
  assert_eq 'R6 source carries no unenforced never-writable absolute' '0' \
    "$(grep -c 'never writable by it' "$ABLATION" || true)"
}

case "$CASE" in
  all) run_comparator_cases; run_arm_cases; run_guard_cases; run_run_cases ;;
  comparator) run_comparator_cases ;;
  arm) run_arm_cases ;;
  guard) run_guard_cases ;;
  run) run_run_cases ;;
esac

printf '\nreview-ablation.test.sh: %d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
