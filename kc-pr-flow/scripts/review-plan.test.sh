#!/usr/bin/env bash
# Contract tests for the conservative review delta router.
# shellcheck disable=SC2016

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLAN="$HERE/review-plan.sh"
RUNTIME="$HERE/review-runtime.sh"
TEST_ROOT="$(cd "$(mktemp -d)" && pwd -P)"
cleanup() {
  chmod -R u+rwX "$TEST_ROOT" 2>/dev/null || true
  rm -rf "$TEST_ROOT"
}
trap cleanup EXIT

PASS=0
FAIL=0
CASE_FILTER='all'
if [ "$#" -gt 0 ]; then
  if [ "$#" -ne 2 ] || [ "$1" != '--case' ]; then
    printf 'usage: %s [--case receipt-contract|mode-router|trust-boundary|skill-wiring]\n' "$0" >&2
    exit 2
  fi
  CASE_FILTER="$2"
fi

pass() { PASS=$((PASS + 1)); }
fail() { FAIL=$((FAIL + 1)); printf 'FAIL: %s\n' "$1"; }
assert_eq() {
  if [ "$2" = "$3" ]; then pass; else fail "$1 (expected [$2], got [$3])"; fi
}
assert_not_zero() {
  if [ "$2" -ne 0 ]; then pass; else fail "$1 (expected nonzero status)"; fi
}
assert_contains() {
  if grep -Eq "$2" "$1"; then pass; else fail "$3 (missing [$2])"; fi
}
assert_not_contains() {
  if grep -Fq "$2" "$1"; then fail "$3 (unexpected [$2])"; else pass; fi
}
assert_not_match() {
  if grep -Eq "$2" "$1"; then fail "$3 (unexpected pattern [$2])"; else pass; fi
}

sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    sha256sum "$1" | awk '{print $1}'
  fi
}

make_route_fixture() {
  local repo="$TEST_ROOT/repo" observation="$TEST_ROOT/observation.json"
  local state_root="$TEST_ROOT/state" observed run_id pointer anchor content_hash
  mkdir -p "$repo/src"
  git -C "$repo" init -q
  git -C "$repo" config user.email test@example.com
  git -C "$repo" config user.name Test
  git -C "$repo" remote add origin https://github.com/acme/widgets.git
  printf 'seed\n' >"$repo/README.md"
  git -C "$repo" add README.md
  git -C "$repo" commit -qm base
  ROUTE_BASE="$(git -C "$repo" rev-parse HEAD)"
  {
    printf 'def parse(value):\n    return value\n'
    printf '# filler\n%.0s' {1..20}
    printf 'TAIL = False\n'
  } >"$repo/src/parser.py"
  git -C "$repo" add src/parser.py
  git -C "$repo" commit -qm reviewed
  ROUTE_REVIEWED="$(git -C "$repo" rev-parse HEAD)"
  {
    printf 'def parse(value):\n    return value.strip()\n'
    printf '# filler\n%.0s' {1..20}
    printf 'TAIL = False\n'
  } >"$repo/src/parser.py"
  git -C "$repo" add src/parser.py
  git -C "$repo" commit -qm fixed
  ROUTE_FIXED="$(git -C "$repo" rev-parse HEAD)"

  # shellcheck source=/dev/null
  . "$RUNTIME"
  ROUTE_CONFIG="$TEST_ROOT/config.json"
  printf '%s' "$(review_runtime_config_canonical lite bugfix false false false false code_correctness)" \
    >"$ROUTE_CONFIG"
  ROUTE_CONFIG_HASH="$(review_runtime_config_hash lite bugfix false false false false code_correctness)"
  ROUTE_REVIEW_KEY="$(review_runtime_review_key acme/widgets 42 "$ROUTE_BASE" "$ROUTE_REVIEWED" "$ROUTE_CONFIG_HASH")"
  content_hash="$(git -C "$repo" show "$ROUTE_REVIEWED:src/parser.py" | review_runtime_sha256)"
  pointer="$(jq -S -c -n \
    --arg review_key "$ROUTE_REVIEW_KEY" --arg base "$ROUTE_BASE" \
    --arg head "$ROUTE_REVIEWED" --arg content_hash "$content_hash" '
      {schema:"kc-pr-flow.evidence-pointer/v1",kind:"git_blob",repository:"acme/widgets",
       review_key:$review_key,base_sha:$base,head_sha:$head,object_sha:$head,
       content_sha256:$content_hash,path:"src/parser.py",side:"RIGHT",line:2,locator:null}')"
  anchor="$(review_runtime_v2_git_anchor "$pointer" "$repo" acme/widgets)"
  jq -S -c -n \
    --arg base "$ROUTE_BASE" --arg head "$ROUTE_REVIEWED" \
    --arg config_hash "$ROUTE_CONFIG_HASH" --argjson pointer "$pointer" --arg anchor "$anchor" '
      {
        schema:"kc-pr-flow.shadow-observation/v1",
        identity:{repository:"acme/widgets",pr_number:42,base_sha:$base,head_sha:$head,
          config_hash:$config_hash,occurred_at:"2026-08-30T00:00:00Z"},
        behavior_hashes:{
          body_sha256:("1"*64),inline_comments_sha256:("2"*64),event_sha256:("3"*64),
          options_sha256:("4"*64),confirmation_input_sha256:("5"*64),
          github_call_log_sha256:("6"*64)},
        lanes:[{
          lane_id:"correctness",capability:"code_correctness",provider_family:"claude",
          terminal_status:"succeeded",
          usage:{input_tokens:10,output_tokens:5,total_tokens:15,provenance:"reported",
            provider_family:"claude",scope:"lane"},
          candidates:[{ordinal:1,path:"src/parser.py",side:"RIGHT",anchor_sha256:$anchor,
            category:"correctness",claim_key:"missing_strip",evidence:$pointer}]
        }],
        synthesis:{
          findings:[{path:"src/parser.py",side:"RIGHT",anchor_sha256:$anchor,
            category:"correctness",claim_key:"missing_strip",evidence:$pointer,
            candidate_refs:[{lane_id:"correctness",ordinal:1}]}],
          uncertain_candidate_refs:[]
        }
      }' >"$observation"
  observed="$(KC_PR_FLOW_STATE_DIR="$state_root" bash "$RUNTIME" shadow --enabled on \
    --head-check-status ok --live-head "$ROUTE_REVIEWED" --observation-file "$observation" \
    --repo-worktree "$repo")"
  assert_eq 'fixture observation is terminal' observed "$(jq -r '.status' <<<"$observed")"
  run_id="$(jq -r '.run_id' <<<"$observed")"
  ROUTE_EVENTS="$(find "$state_root" -path "*/$run_id/events.jsonl" -type f)"
  ROUTE_RECEIPT="$TEST_ROOT/receipt.json"
  bash "$RUNTIME" receipt --event-file "$ROUTE_EVENTS" --config-file "$ROUTE_CONFIG" \
    --repo-worktree "$repo" >"$ROUTE_RECEIPT"
  ROUTE_REPO="$repo"
}

if [ "$CASE_FILTER" = all ] || [ "$CASE_FILTER" = mode-router ]; then
  output="$(
    KC_PR_FLOW_DELTA_FAST_PATH=off bash "$PLAN" decide \
      --repo acme/widgets --pr 42 \
      --base 1111111111111111111111111111111111111111 \
      --head 2222222222222222222222222222222222222222 \
      --config-hash aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  )"
  assert_eq 'default-off selects initial' initial "$(jq -r '.mode' <<<"$output")"
  assert_eq 'default-off has no event ceiling' null "$(jq -r '.event_ceiling' <<<"$output")"
  assert_eq 'default-off has no inherited findings' 0 "$(jq -r '.inherited_finding_ids | length' <<<"$output")"
  assert_eq 'default-off has no required capabilities' 0 "$(jq -r '.required_capabilities | length' <<<"$output")"
  assert_eq 'default-off reason is explicit' feature_disabled "$(jq -r '.reason_codes | join(",")' <<<"$output")"
  assert_eq 'decision shape is closed' \
    event_ceiling,fallback,identity,inherited_finding_ids,mode,reason_codes,required_capabilities,review_range,schema \
    "$(jq -r 'keys | sort | join(",")' <<<"$output")"

  make_route_fixture
  resolve="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$ROUTE_FIXED" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'mapped ancestor fix selects resolve' resolve "$(jq -r '.mode' <<<"$resolve")"
  assert_eq 'resolve may reach approve after confirmation' APPROVE "$(jq -r '.event_ceiling' <<<"$resolve")"
  assert_eq 'resolve starts after predecessor head' "$ROUTE_REVIEWED" \
    "$(jq -r '.review_range.from_exclusive' <<<"$resolve")"
  assert_eq 'resolve inherits the known finding' 1 "$(jq -r '.inherited_finding_ids | length' <<<"$resolve")"
  # shellcheck source=/dev/null
  . "$PLAN"
  review_plan_validate_decision "$resolve" acme/widgets 42 "$ROUTE_BASE" "$ROUTE_FIXED" \
    "$ROUTE_CONFIG_HASH" "$ROUTE_EVENTS" "$ROUTE_RECEIPT" "$ROUTE_REPO" "$ROUTE_CONFIG"
  assert_eq 'shared validator accepts the executable resolve decision' 0 "$?"
  escalated="$(jq -S -c '.mode="delta" | .event_ceiling="APPROVE"' <<<"$resolve")"
  review_plan_validate_decision "$escalated" acme/widgets 42 "$ROUTE_BASE" "$ROUTE_FIXED" \
    "$ROUTE_CONFIG_HASH" "$ROUTE_EVENTS" "$ROUTE_RECEIPT" "$ROUTE_REPO" "$ROUTE_CONFIG"
  assert_not_zero 'shared validator rejects a delta APPROVE escalation' "$?"

  git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
  mkdir -p "$ROUTE_REPO/docs"
  printf 'new behavior\n' >"$ROUTE_REPO/docs/new.md"
  git -C "$ROUTE_REPO" add docs/new.md
  git -C "$ROUTE_REPO" commit -qm unseen
  unseen_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  delta="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$unseen_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'safe unseen work selects delta' delta "$(jq -r '.mode' <<<"$delta")"
  assert_eq 'delta cannot approve' COMMENT "$(jq -r '.event_ceiling' <<<"$delta")"
  assert_eq 'delta requires correctness plus predecessor coverage' code_correctness \
    "$(jq -r '.required_capabilities | join(",")' <<<"$delta")"

  missing="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$unseen_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --repo-worktree "$ROUTE_REPO"
  )"
  assert_eq 'missing predecessor falls back to initial' initial "$(jq -r '.mode' <<<"$missing")"

  mutated_receipt="$TEST_ROOT/mutated-receipt.json"
  jq -S -c '.known_findings[0].evidence_sha256=("f"*64)' "$ROUTE_RECEIPT" >"$mutated_receipt"
  mutated="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$unseen_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$mutated_receipt"
  )"
  assert_eq 'mutated receipt falls back to initial' initial "$(jq -r '.mode' <<<"$mutated")"

  changed_hash="b${ROUTE_CONFIG_HASH#?}"
  changed_config="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$unseen_head" \
      --config-hash "$changed_hash" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'changed config identity falls back to initial' initial "$(jq -r '.mode' <<<"$changed_config")"

  printf 'dirty\n' >"$ROUTE_REPO/untracked.txt"
  dirty="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$unseen_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'dirty route state falls back to initial' initial "$(jq -r '.mode' <<<"$dirty")"
  rm "$ROUTE_REPO/untracked.txt"

  git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
  printf '\000binary\n' >"$ROUTE_REPO/src/parser.py"
  git -C "$ROUTE_REPO" add src/parser.py
  git -C "$ROUTE_REPO" commit -qm binary
  binary_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  binary="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$binary_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'binary change falls back to initial' initial "$(jq -r '.mode' <<<"$binary")"

  git -C "$ROUTE_REPO" checkout -q "$ROUTE_REVIEWED"
  sed -e 's/return value/return value.strip()/' -e 's/TAIL = False/TAIL = True/' \
    "$ROUTE_REPO/src/parser.py" >"$TEST_ROOT/mixed-parser.py"
  cp "$TEST_ROOT/mixed-parser.py" "$ROUTE_REPO/src/parser.py"
  git -C "$ROUTE_REPO" add src/parser.py
  git -C "$ROUTE_REPO" commit -qm mixed-hunks
  mixed_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  mixed="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$mixed_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'same-file unrelated hunk prevents resolve' delta "$(jq -r '.mode' <<<"$mixed")"

  git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
  printf '{"dependencies":{"left-pad":"1.0.0"}}\n' >"$ROUTE_REPO/package.json"
  git -C "$ROUTE_REPO" add package.json
  git -C "$ROUTE_REPO" commit -qm dependency
  dependency_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  dependency="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$dependency_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'dependency change selects delta' delta "$(jq -r '.mode' <<<"$dependency")"
  assert_eq 'dependency change requires supply-chain' supply-chain \
    "$(jq -r '.required_capabilities | map(select(. == "supply-chain")) | join(",")' <<<"$dependency")"
fi

if [ "$CASE_FILTER" = all ] || [ "$CASE_FILTER" = receipt-contract ]; then
  fixture="$HERE/../test/fixtures/review-plan/pr1693-replay.json"
  jq -e '
    (keys | sort) == ["expected","finding","pr_number","repository","schema"] and
    .schema == "kc-pr-flow.review-plan-replay/v1" and
    .expected == {mapped_fix_ceiling:"APPROVE",mapped_fix_mode:"resolve",
      unseen_ceiling:"COMMENT",unseen_mode:"delta"}
  ' "$fixture" >/dev/null
  assert_eq 'compact replay fixture is closed and deterministic' 0 "$?"
  assert_contains "$PLAN" 'review_runtime_validate_delta_receipt_snapshots' \
    'planner delegates receipt validation to S01'
  assert_contains "$PLAN" 'review_plan_snapshot_inputs' 'planner owns one frozen input set'
  assert_not_contains "$PLAN" 'review_runtime_build_delta_receipt' 'planner does not mint receipts'
  assert_not_match "$PLAN" '^[[:space:]]*receipt\)' 'planner CLI does not expose receipt authority'
fi

if [ "$CASE_FILTER" = all ] || [ "$CASE_FILTER" = trust-boundary ]; then
  # shellcheck source=/dev/null
  . "$RUNTIME"
  # shellcheck source=/dev/null
  . "$PLAN"
  review_plan_safe_path src/app.py
  assert_eq 'ordinary repository path is safe' 0 "$?"
  review_plan_safe_path ../escape
  assert_not_zero 'parent traversal is unsafe' "$?"
  review_plan_safe_path 'src/bad\path'
  assert_not_zero 'backslash path is unsafe' "$?"

  trust_repo="$TEST_ROOT/trust-repo"
  mkdir -p "$trust_repo"
  git -C "$trust_repo" init -q
  git -C "$trust_repo" config user.email test@example.com
  git -C "$trust_repo" config user.name Test
  printf 'safe\n' >"$trust_repo/app.txt"
  git -C "$trust_repo" add app.txt
  git -C "$trust_repo" commit -qm safe
  trust_base="$(git -C "$trust_repo" rev-parse HEAD)"
  printf '\000binary\n' >"$trust_repo/app.txt"
  git -C "$trust_repo" add app.txt
  git -C "$trust_repo" commit -qm binary
  trust_head="$(git -C "$trust_repo" rev-parse HEAD)"
  trust_top="$(GIT_DIR=/definitely/missing GIT_WORK_TREE=/definitely/missing \
    review_plan_git "$trust_repo" rev-parse --show-toplevel)"
  assert_eq 'ambient Git selectors cannot redirect exact reads' "$trust_repo" "$trust_top"
  review_plan_changed_object_is_safe "$trust_repo" "$trust_base" "$trust_head" app.txt
  assert_not_zero 'raw binary blob is rejected independently of attributes' "$?"

  driver="$TEST_ROOT/external-diff.sh"
  ledger="$TEST_ROOT/external-diff.log"
  printf '#!/bin/sh\nprintf invoked >>"%s"\nexit 97\n' "$ledger" >"$driver"
  chmod +x "$driver"
  git -C "$trust_repo" config diff.external "$driver"
  review_plan_changed_diff "$trust_repo" "$trust_base" "$trust_head" >/dev/null
  assert_eq 'repository external diff is disabled' 0 "$?"
  assert_eq 'repository external diff is never invoked' 0 "$([ -s "$ledger" ] && printf 1 || printf 0)"
fi

if [ "$CASE_FILTER" = all ] || [ "$CASE_FILTER" = skill-wiring ]; then
  SKILL="$HERE/../skills/kc-pr-review/SKILL.md"
  REFERENCE="$HERE/../reference/review-runtime.md"
  assert_contains "$SKILL" 'KC_PR_FLOW_DELTA_FAST_PATH=on' 'skill documents exact opt-in'
  assert_contains "$SKILL" 'review-plan\.sh.*decide' 'skill invokes the planner'
  assert_contains "$SKILL" 'review_plan_validate_decision' 'skill reuses the shared decision validator'
  assert_contains "$SKILL" 'legacy presentation, typed presentation, human edit, confirmation' \
    'skill names the existing event authority seams'
  assert_contains "$SKILL" 'Step 6c' 'skill preserves human confirmation'
  assert_contains "$REFERENCE" 'kc-pr-flow\.review-plan-decision/v1' \
    'runtime reference documents the plan schema'
  for forbidden in 'gh pr review' 'review-post.sh post' 'authorization.granted'; do
    assert_not_contains "$PLAN" "$forbidden" "planner has no posting authority: $forbidden"
  done
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
