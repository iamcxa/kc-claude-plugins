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
    printf 'usage: %s [--case receipt-contract|mode-router|trust-boundary|skill-wiring|s02-capability|s02-boundary|s02-gitlink]\n' "$0" >&2
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
  local fixture_name="${1-default}" finding_category="${2-correctness}"
  local receipt_capabilities="${3-code_correctness}"
  local lane_capability="${4-code_correctness}"
  local zero_findings="${5-false}"
  local repo="$TEST_ROOT/repo-$fixture_name" observation="$TEST_ROOT/observation-$fixture_name.json"
  local state_root="$TEST_ROOT/state-$fixture_name" observed run_id pointer anchor content_hash
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
  printf '%s' "$(review_runtime_config_canonical lite bugfix false false false false "$receipt_capabilities")" \
    >"$ROUTE_CONFIG"
  ROUTE_CONFIG_HASH="$(review_runtime_config_hash lite bugfix false false false false "$receipt_capabilities")"
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
    --arg config_hash "$ROUTE_CONFIG_HASH" --arg category "$finding_category" \
    --arg lane_capability "$lane_capability" \
    --argjson zero_findings "$zero_findings" \
    --argjson pointer "$pointer" --arg anchor "$anchor" '
      {
        schema:"kc-pr-flow.shadow-observation/v1",
        identity:{repository:"acme/widgets",pr_number:42,base_sha:$base,head_sha:$head,
          config_hash:$config_hash,occurred_at:"2026-08-30T00:00:00Z"},
        behavior_hashes:{
          body_sha256:("1"*64),inline_comments_sha256:("2"*64),event_sha256:("3"*64),
          options_sha256:("4"*64),confirmation_input_sha256:("5"*64),
          github_call_log_sha256:("6"*64)},
        lanes:[{
          lane_id:"correctness",capability:$lane_capability,provider_family:"claude",
          terminal_status:"succeeded",
          usage:{input_tokens:10,output_tokens:5,total_tokens:15,provenance:"reported",
            provider_family:"claude",scope:"lane"},
          candidates:(if $zero_findings then [] else
            [{ordinal:1,path:"src/parser.py",side:"RIGHT",anchor_sha256:$anchor,
              category:$category,claim_key:"missing_strip",evidence:$pointer}] end)
        }],
        synthesis:{
          findings:(if $zero_findings then [] else
            [{path:"src/parser.py",side:"RIGHT",anchor_sha256:$anchor,
              category:$category,claim_key:"missing_strip",evidence:$pointer,
              candidate_refs:[{lane_id:"correctness",ordinal:1}]}] end),
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

make_gitlink_route() {
  local fixture_name="$1" gitlink_repo gitlink_head
  make_route_fixture "$fixture_name"
  git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
  gitlink_repo="$TEST_ROOT/gitlink-repo-$fixture_name"
  mkdir -p "$gitlink_repo"
  git -C "$gitlink_repo" init -q
  git -C "$gitlink_repo" config user.email test@example.com
  git -C "$gitlink_repo" config user.name Test
  printf 'submodule\n' >"$gitlink_repo/README.md"
  git -C "$gitlink_repo" add README.md
  git -C "$gitlink_repo" commit -qm submodule
  gitlink_head="$(git -C "$gitlink_repo" rev-parse HEAD)"
  git -C "$ROUTE_REPO" update-index --add --cacheinfo "160000,$gitlink_head,vendor/child"
  git -C "$ROUTE_REPO" commit -qm gitlink
  GITLINK_ROUTE_HEAD="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
}

if [ "$CASE_FILTER" = all ] || [ "$CASE_FILTER" = s02-capability ]; then
  make_route_fixture security-category security
  git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
  sed '3s/# filler/# auth token/' "$ROUTE_REPO/src/parser.py" >"$TEST_ROOT/security-category-parser.py"
  cp "$TEST_ROOT/security-category-parser.py" "$ROUTE_REPO/src/parser.py"
  git -C "$ROUTE_REPO" add src/parser.py
  git -C "$ROUTE_REPO" commit -qm security-category
  security_category_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  security_category="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$security_category_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'security category cannot impersonate security receipt coverage' delta \
    "$(jq -r '.mode' <<<"$security_category")"
  assert_eq 'security category gap retains security capability' security \
    "$(jq -r '.required_capabilities | map(select(. == "security")) | join(",")' <<<"$security_category")"
  assert_eq 'security category gap cannot approve' COMMENT \
    "$(jq -r '.event_ceiling' <<<"$security_category")"

  make_route_fixture security-positive security security security
  git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
  sed '3s/# filler/# auth token/' "$ROUTE_REPO/src/parser.py" >"$TEST_ROOT/security-positive-parser.py"
  cp "$TEST_ROOT/security-positive-parser.py" "$ROUTE_REPO/src/parser.py"
  git -C "$ROUTE_REPO" add src/parser.py
  git -C "$ROUTE_REPO" commit -qm security-positive
  security_positive_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  security_positive="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$security_positive_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'security receipt capability preserves mapped security coverage' security \
    "$(jq -r '.required_capabilities | map(select(. == "security")) | join(",")' <<<"$security_positive")"
  assert_eq 'security receipt capability permits mapped resolve' resolve \
    "$(jq -r '.mode' <<<"$security_positive")"
  assert_eq 'security receipt capability permits mapped approve' APPROVE \
    "$(jq -r '.event_ceiling' <<<"$security_positive")"
fi

if [ "$CASE_FILTER" = all ] || [ "$CASE_FILTER" = s02-boundary ]; then
  make_route_fixture boundary
  git -C "$ROUTE_REPO" checkout -q "$ROUTE_REVIEWED"
  mkdir -p "$ROUTE_REPO/tests"
  printf '# src.parser\n' >"$ROUTE_REPO/tests/test_parser.py"
  git -C "$ROUTE_REPO" add tests/test_parser.py
  git -C "$ROUTE_REPO" commit -qm module-token-boundary
  module_token_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  module_token="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$module_token_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'module token alone cannot map a boundary hunk' delta \
    "$(jq -r '.mode' <<<"$module_token")"
  assert_eq 'module token boundary falls back to comment' COMMENT \
    "$(jq -r '.event_ceiling' <<<"$module_token")"

  make_route_fixture boundary-claim-key
  git -C "$ROUTE_REPO" checkout -q "$ROUTE_REVIEWED"
  mkdir -p "$ROUTE_REPO/tests"
  claim_key_reference="$(jq -r '.known_findings[0].claim_key' "$ROUTE_RECEIPT")"
  printf '# %s\n' "$claim_key_reference" >"$ROUTE_REPO/tests/test_parser.py"
  git -C "$ROUTE_REPO" add tests/test_parser.py
  git -C "$ROUTE_REPO" commit -qm claim-key-boundary
  claim_key_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  claim_key="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$claim_key_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'claim key maps a boundary hunk' resolve "$(jq -r '.mode' <<<"$claim_key")"
  assert_eq 'claim key boundary permits approve' APPROVE "$(jq -r '.event_ceiling' <<<"$claim_key")"
fi

if [ "$CASE_FILTER" = all ] || [ "$CASE_FILTER" = s02-gitlink ]; then
  make_gitlink_route gitlink-diff-ignore
  git -C "$ROUTE_REPO" config diff.ignoreSubmodules all
  diff_ignore_gitlink="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$GITLINK_ROUTE_HEAD" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  git -C "$ROUTE_REPO" config --unset diff.ignoreSubmodules
  assert_eq 'diff ignore cannot hide a changed gitlink' initial \
    "$(jq -r '.mode' <<<"$diff_ignore_gitlink")"

  make_gitlink_route gitlink-submodule-ignore
  git -C "$ROUTE_REPO" config submodule.vendor/child.ignore all
  submodule_ignore_gitlink="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$GITLINK_ROUTE_HEAD" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  git -C "$ROUTE_REPO" config --unset submodule.vendor/child.ignore
  assert_eq 'submodule ignore cannot hide a changed gitlink' initial \
    "$(jq -r '.mode' <<<"$submodule_ignore_gitlink")"

  inventory_functions="$(sed -n '/^review_plan_changed_paths()/,/^}/p; /^review_plan_changed_diff()/,/^}/p' "$PLAN")"
  assert_eq 'both Git diff inventory calls force changed gitlinks' 2 \
    "$(grep -c -- '--ignore-submodules=none' <<<"$inventory_functions")"
fi

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
  review_plan_event_allowed "$resolve" APPROVE acme/widgets 42 "$ROUTE_BASE" "$ROUTE_FIXED" \
    "$ROUTE_CONFIG_HASH" "$ROUTE_EVENTS" "$ROUTE_RECEIPT" "$ROUTE_REPO" "$ROUTE_CONFIG"
  assert_eq 'resolve permits APPROVE only after a fresh plan validation' 0 "$?"
  escalated="$(jq -S -c '.mode="delta" | .event_ceiling="APPROVE"' <<<"$resolve")"
  review_plan_validate_decision "$escalated" acme/widgets 42 "$ROUTE_BASE" "$ROUTE_FIXED" \
    "$ROUTE_CONFIG_HASH" "$ROUTE_EVENTS" "$ROUTE_RECEIPT" "$ROUTE_REPO" "$ROUTE_CONFIG"
  assert_not_zero 'shared validator rejects a delta APPROVE escalation' "$?"
  review_plan_event_allowed "$escalated" COMMENT acme/widgets 42 "$ROUTE_BASE" "$ROUTE_FIXED" \
    "$ROUTE_CONFIG_HASH" "$ROUTE_EVENTS" "$ROUTE_RECEIPT" "$ROUTE_REPO" "$ROUTE_CONFIG"
  assert_not_zero 'event gate rejects a mutated stored decision' "$?"

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
  review_plan_event_allowed "$delta" APPROVE acme/widgets 42 "$ROUTE_BASE" "$unseen_head" \
    "$ROUTE_CONFIG_HASH" "$ROUTE_EVENTS" "$ROUTE_RECEIPT" "$ROUTE_REPO" "$ROUTE_CONFIG"
  assert_not_zero 'delta refuses APPROVE at the executable event gate' "$?"
  review_plan_event_allowed "$delta" COMMENT acme/widgets 42 "$ROUTE_BASE" "$unseen_head" \
    "$ROUTE_CONFIG_HASH" "$ROUTE_EVENTS" "$ROUTE_RECEIPT" "$ROUTE_REPO" "$ROUTE_CONFIG"
  assert_eq 'delta permits COMMENT after a fresh plan validation' 0 "$?"

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
  review_plan_event_allowed "$delta" COMMENT acme/widgets 42 "$ROUTE_BASE" "$unseen_head" \
    "$changed_hash" "$ROUTE_EVENTS" "$ROUTE_RECEIPT" "$ROUTE_REPO" "$ROUTE_CONFIG"
  assert_not_zero 'event gate rejects changed frozen identity inputs' "$?"

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

  git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
  mkdir -p "$ROUTE_REPO/security"
  printf 'def authorize(token):\n    return bool(token)\n' >"$ROUTE_REPO/security/policy.py"
  git -C "$ROUTE_REPO" add security/policy.py
  git -C "$ROUTE_REPO" commit -qm security
  security_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  security="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$security_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'security change requires security review' security \
    "$(jq -r '.required_capabilities | map(select(. == "security")) | join(",")' <<<"$security")"

  git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
  mkdir -p "$ROUTE_REPO/.github/workflows"
  printf 'name: CI\non: push\njobs: {}\n' >"$ROUTE_REPO/.github/workflows/ci.yml"
  git -C "$ROUTE_REPO" add .github/workflows/ci.yml
  git -C "$ROUTE_REPO" commit -qm workflow
  workflow_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  workflow="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$workflow_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'workflow change requires GitHub Actions review' github-actions \
    "$(jq -r '.required_capabilities | map(select(. == "github-actions")) | join(",")' <<<"$workflow")"

  git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
  ln -s parser.py "$ROUTE_REPO/src/parser-link.py"
  git -C "$ROUTE_REPO" add src/parser-link.py
  git -C "$ROUTE_REPO" commit -qm symlink
  symlink_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  symlink="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$symlink_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'symlink change falls back to initial' initial "$(jq -r '.mode' <<<"$symlink")"

  git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
  git -C "$ROUTE_REPO" mv src/parser.py src/renamed-parser.py
  git -C "$ROUTE_REPO" commit -qm rename
  rename_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  rename="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$rename_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'rename falls back to initial' initial "$(jq -r '.mode' <<<"$rename")"

  orphan_tree="$(git -C "$ROUTE_REPO" mktree </dev/null)"
  orphan_head="$(printf 'unrelated\n' | git -C "$ROUTE_REPO" commit-tree "$orphan_tree")"
  git -C "$ROUTE_REPO" checkout -q "$orphan_head"
  nonancestor="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$orphan_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'non-ancestor history falls back to initial' initial "$(jq -r '.mode' <<<"$nonancestor")"

  make_route_fixture zero-findings correctness code_correctness code_correctness true
  assert_eq 'zero-finding S01 receipt is valid and closed' 0 \
    "$(jq -r '.known_findings | length' "$ROUTE_RECEIPT")"
  git -C "$ROUTE_REPO" checkout -q "$ROUTE_REVIEWED"
  mkdir -p "$ROUTE_REPO/docs"
  printf 'safe unseen work\n' >"$ROUTE_REPO/docs/zero-findings.md"
  git -C "$ROUTE_REPO" add docs/zero-findings.md
  git -C "$ROUTE_REPO" commit -qm zero-findings-unseen
  zero_findings_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
  zero_findings_delta="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$zero_findings_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'zero-finding predecessor permits safe unseen delta' delta \
    "$(jq -r '.mode' <<<"$zero_findings_delta")"
  assert_eq 'zero-finding delta remains comment-only' COMMENT \
    "$(jq -r '.event_ceiling' <<<"$zero_findings_delta")"
  assert_eq 'zero-finding delta inherits no findings' 0 \
    "$(jq -r '.inherited_finding_ids | length' <<<"$zero_findings_delta")"
  assert_eq 'zero-finding delta retains predecessor coverage' code_correctness \
    "$(jq -r '.required_capabilities | join(",")' <<<"$zero_findings_delta")"

  zero_findings_bad_coverage="$TEST_ROOT/zero-findings-bad-coverage.json"
  jq -S -c '.required_capabilities=[]' "$ROUTE_RECEIPT" >"$zero_findings_bad_coverage"
  bad_coverage="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$zero_findings_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$zero_findings_bad_coverage"
  )"
  assert_eq 'zero findings do not bypass capability coverage validation' initial \
    "$(jq -r '.mode' <<<"$bad_coverage")"

  wrong_identity="$(
    KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo other/widgets --pr 42 --base "$ROUTE_BASE" --head "$zero_findings_head" \
      --config-hash "$ROUTE_CONFIG_HASH" --config-file "$ROUTE_CONFIG" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$ROUTE_RECEIPT"
  )"
  assert_eq 'zero findings do not bypass predecessor identity validation' initial \
    "$(jq -r '.mode' <<<"$wrong_identity")"
fi

replay_fixture_decide() {
  local fixture="$1" scenario_index="$2" scenario_id head_kind receipt_kind config_kind worktree_kind history_kind
  local scenario_head decision_receipt decision_config_hash decision_config_file orphan_tree decision
  scenario_id="$(jq -r --argjson index "$scenario_index" '.scenarios[$index].id' "$fixture")"
  head_kind="$(jq -r --argjson index "$scenario_index" '.scenarios[$index].head' "$fixture")"
  receipt_kind="$(jq -r --argjson index "$scenario_index" '.scenarios[$index].receipt' "$fixture")"
  config_kind="$(jq -r --argjson index "$scenario_index" '.scenarios[$index].config' "$fixture")"
  worktree_kind="$(jq -r --argjson index "$scenario_index" '.scenarios[$index].worktree' "$fixture")"
  history_kind="$(jq -r --argjson index "$scenario_index" '.scenarios[$index].history' "$fixture")"
  case "$head_kind" in
    fixed)
      git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
      scenario_head="$ROUTE_FIXED"
      ;;
    unseen)
      git -C "$ROUTE_REPO" checkout -q "$ROUTE_FIXED"
      mkdir -p "$ROUTE_REPO/docs"
      printf 'new behavior\n' >"$ROUTE_REPO/docs/$scenario_id.md"
      git -C "$ROUTE_REPO" add "docs/$scenario_id.md"
      git -C "$ROUTE_REPO" commit -qm "$scenario_id"
      scenario_head="$(git -C "$ROUTE_REPO" rev-parse HEAD)"
      ;;
    *) fail "replay fixture has unknown head kind: $head_kind"; return 1 ;;
  esac
  if [ "$history_kind" = nonancestor ]; then
    orphan_tree="$(git -C "$ROUTE_REPO" mktree </dev/null)"
    scenario_head="$(printf 'unrelated\n' | git -C "$ROUTE_REPO" commit-tree "$orphan_tree")"
    git -C "$ROUTE_REPO" checkout -q "$scenario_head"
  fi
  if [ "$worktree_kind" = dirty ]; then
    printf 'dirty\n' >"$ROUTE_REPO/untracked-$scenario_id.txt"
  fi

  decision_receipt="$ROUTE_RECEIPT"
  case "$receipt_kind" in
    trusted) ;;
    missing) decision_receipt='' ;;
    mutated)
      decision_receipt="$TEST_ROOT/replay-$scenario_id-mutated-receipt.json"
      jq -S -c '.known_findings[0].evidence_sha256=("f"*64)' "$ROUTE_RECEIPT" >"$decision_receipt"
      ;;
    *) fail "replay fixture has unknown receipt kind: $receipt_kind"; return 1 ;;
  esac
  decision_config_hash="$ROUTE_CONFIG_HASH"
  decision_config_file="$ROUTE_CONFIG"
  case "$config_kind" in
    trusted) ;;
    changed) decision_config_hash="b${ROUTE_CONFIG_HASH#?}" ;;
    *) fail "replay fixture has unknown config kind: $config_kind"; return 1 ;;
  esac

  if [ -n "$decision_receipt" ]; then
    decision="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$scenario_head" \
      --config-hash "$decision_config_hash" --config-file "$decision_config_file" \
      --repo-worktree "$ROUTE_REPO" --predecessor-events "$ROUTE_EVENTS" \
      --delta-receipt "$decision_receipt")"
  else
    decision="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
      --repo acme/widgets --pr 42 --base "$ROUTE_BASE" --head "$scenario_head" \
      --config-hash "$decision_config_hash" --repo-worktree "$ROUTE_REPO")"
  fi
  [ "$worktree_kind" != dirty ] || rm "$ROUTE_REPO/untracked-$scenario_id.txt"
  printf '%s' "$decision"
}

if [ "$CASE_FILTER" = all ] || [ "$CASE_FILTER" = receipt-contract ]; then
  fixture="$HERE/../test/fixtures/review-plan/pr1693-replay.json"
  jq -e '
    (keys | sort) == ["pr_number","repository","scenarios","schema"] and
    .schema == "kc-pr-flow.review-plan-replay/v2" and
    (.scenarios | type == "array" and length == 7) and
    all(.scenarios[];
      (keys | sort) == ["config","expected","head","history","id","receipt","worktree"] and
      (.id | type == "string" and test("^[a-z0-9-]+$")) and
      (.head == "fixed" or .head == "unseen") and
      (.receipt == "trusted" or .receipt == "missing" or .receipt == "mutated") and
      (.config == "trusted" or .config == "changed") and
      (.worktree == "clean" or .worktree == "dirty") and
      (.history == "ancestor" or .history == "nonancestor") and
      (.expected | (keys | sort) == ["event_ceiling","mode"] and
        (.mode == "resolve" or .mode == "delta" or .mode == "initial")))
  ' "$fixture" >/dev/null
  assert_eq 'replay fixture is closed and deterministic' 0 "$?"
  make_route_fixture replay
  replay_count="$(jq -r '.scenarios | length' "$fixture")"
  replay_index=0
  while [ "$replay_index" -lt "$replay_count" ]; do
    replay_id="$(jq -r --argjson index "$replay_index" '.scenarios[$index].id' "$fixture")"
    replay_expected_mode="$(jq -r --argjson index "$replay_index" '.scenarios[$index].expected.mode' "$fixture")"
    replay_expected_ceiling="$(jq -r --argjson index "$replay_index" '.scenarios[$index].expected.event_ceiling' "$fixture")"
    replay_decision="$(replay_fixture_decide "$fixture" "$replay_index")"
    assert_eq "replay $replay_id selects its fixture mode" "$replay_expected_mode" \
      "$(jq -r '.mode' <<<"$replay_decision")"
    assert_eq "replay $replay_id selects its fixture ceiling" "$replay_expected_ceiling" \
      "$(jq -r '.event_ceiling' <<<"$replay_decision")"
    replay_index=$((replay_index + 1))
  done
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

  fsmonitor="$TEST_ROOT/fsmonitor.sh"
  fsmonitor_ledger="$TEST_ROOT/fsmonitor.log"
  printf '#!/bin/sh\nprintf invoked >>"%s"\nexit 0\n' "$fsmonitor_ledger" >"$fsmonitor"
  chmod +x "$fsmonitor"
  git -C "$trust_repo" config core.fsmonitor "$fsmonitor"
  review_plan_route_state "$trust_repo" "$trust_base" "$trust_head" >/dev/null
  assert_eq 'route state remains readable with hostile fsmonitor configured' 0 "$?"
  assert_eq 'repository fsmonitor executable is never invoked' 0 \
    "$([ -s "$fsmonitor_ledger" ] && printf 1 || printf 0)"
fi

if [ "$CASE_FILTER" = all ] || [ "$CASE_FILTER" = skill-wiring ]; then
  SKILL="$HERE/../skills/kc-pr-review/SKILL.md"
  REFERENCE="$HERE/../reference/review-runtime.md"
  plan_cleanup_recipe="$TEST_ROOT/delta-plan-cleanup-recipe.sh"
  typed_recipe="$TEST_ROOT/typed-interactive-recipe.sh"
  assert_contains "$SKILL" 'KC_PR_FLOW_DELTA_FAST_PATH=on' 'skill documents exact opt-in'
  assert_contains "$SKILL" 'review-plan\.sh.*decide' 'skill invokes the planner'
  assert_contains "$SKILL" 'review_plan_validate_decision' 'skill reuses the shared decision validator'
  for seam in legacy-presentation typed-presentation human-edit confirmation \
    autonomous-construction interactive-pre-post autonomous-pre-post; do
    assert_contains "$SKILL" "review_plan_guard_event.*# $seam" \
      "skill executes the event guard at $seam"
  done
  assert_contains "$SKILL" 'Step 6c' 'skill preserves human confirmation'
  assert_contains "$REFERENCE" 'kc-pr-flow\.review-plan-decision/v1' \
    'runtime reference documents the plan schema'
  for forbidden in 'gh pr review' 'review-post.sh post' 'authorization.granted'; do
    assert_not_contains "$PLAN" "$forbidden" "planner has no posting authority: $forbidden"
  done

  sed -n '/^# delta-plan-cleanup-recipe:start$/,/^# delta-plan-cleanup-recipe:end$/p' "$SKILL" |
    sed '1d;$d' >"$plan_cleanup_recipe"
  # shellcheck source=/dev/null
  . "$RUNTIME"
  # shellcheck source=/dev/null
  . "$plan_cleanup_recipe"
  if declare -F review_plan_cleanup_inputs >/dev/null &&
    declare -F review_plan_guard_event_final >/dev/null; then
    pass

    success_dir="$(review_runtime_private_snapshot_dir)"
    success_events="$success_dir/events.jsonl"
    success_receipt="$success_dir/receipt.json"
    success_config="$success_dir/config.json"
    printf 'immutable events\n' >"$success_events"
    printf 'immutable receipt\n' >"$success_receipt"
    printf 'immutable config\n' >"$success_config"
    PLAN_INPUT_DIR="$success_dir"
    PLAN_INPUT_EVENTS="$success_events"
    PLAN_INPUT_RECEIPT="$success_receipt"
    PLAN_INPUT_CONFIG="$success_config"
    PLAN_INPUT_READY=true
    # shellcheck disable=SC2317,SC2329 # Invoked by review_plan_guard_event_final.
    review_plan_guard_event() {
      [ "$(cat "$PLAN_INPUT_EVENTS")" = 'immutable events' ] &&
        [ "$(cat "$PLAN_INPUT_RECEIPT")" = 'immutable receipt' ] &&
        [ "$(cat "$PLAN_INPUT_CONFIG")" = 'immutable config' ]
    }
    review_plan_guard_event_final COMMENT
    assert_eq 'final authority guard reads immutable bytes before cleanup' 0 "$?"
    assert_eq 'successful final guard removes exact snapshot files and directory' false \
      "$([ -e "$success_events" ] || [ -e "$success_receipt" ] ||
          [ -e "$success_config" ] || [ -e "$success_dir" ] && printf true || printf false)"
    assert_eq 'successful cleanup resets plan handles and readiness' '||||false' \
      "$PLAN_INPUT_DIR|$PLAN_INPUT_EVENTS|$PLAN_INPUT_RECEIPT|$PLAN_INPUT_CONFIG|$PLAN_INPUT_READY"

    partial_dir="$(review_runtime_private_snapshot_dir)"
    partial_events="$partial_dir/events.jsonl"
    partial_receipt="$partial_dir/receipt.json"
    partial_config="$partial_dir/config.json"
    printf 'partial events\n' >"$partial_events"
    PLAN_INPUT_DIR="$partial_dir"
    PLAN_INPUT_EVENTS="$partial_events"
    PLAN_INPUT_RECEIPT="$partial_receipt"
    PLAN_INPUT_CONFIG="$partial_config"
    PLAN_INPUT_READY=false
    review_plan_cleanup_inputs
    assert_eq 'partial snapshot cleanup removes known file and empty directory' false \
      "$([ -e "$partial_events" ] || [ -e "$partial_dir" ] && printf true || printf false)"
    assert_eq 'partial cleanup resets plan handles and readiness' '||||false' \
      "$PLAN_INPUT_DIR|$PLAN_INPUT_EVENTS|$PLAN_INPUT_RECEIPT|$PLAN_INPUT_CONFIG|$PLAN_INPUT_READY"
    assert_not_contains "$plan_cleanup_recipe" 'rm -rf' +      'plan snapshot cleanup never uses recursive deletion'
  else
    fail 'skill defines executable plan snapshot cleanup and final guard'
  fi

  sed -n '/^# typed-interactive-recipe:start$/,/^# typed-interactive-recipe:end$/p' "$SKILL" |
    sed '1d;$d' >"$typed_recipe"
  # shellcheck source=/dev/null
  . "$typed_recipe"
  review_plan_guard_event() {
    case "$1" in COMMENT|REQUEST_CHANGES) return 0 ;; *) return 3 ;; esac
  }
  review_interactive_prepare_confirmation legacy APPROVE null null true >/dev/null 2>&1
  assert_not_zero 'legacy presentation executes the COMMENT ceiling' "$?"

  legacy_confirmation="$(review_interactive_prepare_confirmation legacy COMMENT null null true)"
  review_interactive_apply_event_edit "$legacy_confirmation" APPROVE >/dev/null 2>&1
  assert_not_zero 'human event edit executes the COMMENT ceiling' "$?"
  review_interactive_confirm_post "$legacy_confirmation" APPROVE confirmed >/dev/null 2>&1
  assert_not_zero 'human confirmation executes the COMMENT ceiling' "$?"

  typed_approve="$TEST_ROOT/typed-approve.sh"
  cat >"$typed_approve" <<'MOCK'
#!/usr/bin/env bash
printf '%s\n' '{"approve_eligible":true,"capabilities":[],"capability_gap_refs":[],"confirmation_input":{"blocker_refs":[],"coverage_summary":"typed-derived","gap_refs":[],"identity_summary":"typed-derived","verdict_summary":"typed-derived"},"confirmed_blocker_refs":[],"coverage":"complete","effective_event":"APPROVE","mode":"typed","review_identity":{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":42,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"},"schema":"kc-pr-flow.interactive-collation-decision/v1"}'
MOCK
  chmod 0700 "$typed_approve"
  typed_identity='{"base_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","config_hash":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","head_sha":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","pr_number":42,"repository":"acme/widgets","review_key":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","run_id":"run-typed"}'
  review_interactive_prepare_confirmation typed COMMENT "$typed_identity" null \
    "$typed_approve" >/dev/null 2>&1
  assert_not_zero 'typed presentation executes the COMMENT ceiling' "$?"

  interactive_gate="$(review_interactive_confirm_post "$legacy_confirmation" COMMENT confirmed)"
  edited_interactive_gate="$(jq -S -c \
    '.effective_event="APPROVE" | .confirmation.effective_event="APPROVE"' \
    <<<"$interactive_gate")"
  review_interactive_post_gate_valid "$edited_interactive_gate" >/dev/null 2>&1
  assert_not_zero 'interactive immediate pre-post executes the COMMENT ceiling' "$?"

  autonomous_key="$(printf 'd%.0s' {1..64})"
  autonomous_head="$(printf 'b%.0s' {1..40})"
  review_autonomous_post_gate "$autonomous_key" "$autonomous_head" APPROVE daemon \
    >/dev/null 2>&1
  assert_not_zero 'autonomous construction executes the COMMENT ceiling' "$?"
  autonomous_gate="$(review_autonomous_post_gate \
    "$autonomous_key" "$autonomous_head" COMMENT daemon)"
  edited_autonomous_gate="$(jq -S -c '.effective_event="APPROVE"' <<<"$autonomous_gate")"
  review_autonomous_post_gate_valid "$edited_autonomous_gate" >/dev/null 2>&1
  assert_not_zero 'autonomous immediate pre-post executes the COMMENT ceiling' "$?"
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[ "$PASS" -gt 0 ] && [ "$FAIL" -eq 0 ]
