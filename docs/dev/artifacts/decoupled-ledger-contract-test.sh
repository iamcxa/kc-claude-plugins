#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
PR_MERGE=${CONTRACT_PR_MERGE:-"$REPO_ROOT/docs/dev/_mods/pr-merge.md"}
LEDGER="$REPO_ROOT/docs/dev/ledger.csv"
SPACEDOCK_BIN=${SPACEDOCK_BIN:-spacedock}
MODE=${1:-all}
STATE_REF=refs/heads/spacedock-state/dev
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/decoupled-ledger-contract.XXXXXX")
trap 'rm -rf "$TEST_ROOT"' EXIT

fail() {
  printf 'decoupled-ledger-contract:FAIL:%s\n' "$*" >&2
  exit 1
}

pass() {
  printf 'decoupled-ledger-contract:PASS:%s\n' "$*"
}

extract_terminal_contract() {
  local destination=$1
  local contract_source=${2:-$PR_MERGE}

  if ! grep -q '^# decoupled-terminal-transaction:start$' "$contract_source"; then
    if grep -q 'has delivered the pre-merge ledger row but has' "$contract_source"; then
      fail 'RED: authenticated product MERGED still enters ledger finalization before terminal state'
    fi
    fail 'documented terminal transaction marker is missing'
  fi

  awk '
    /^# decoupled-terminal-transaction:start$/ { copying = 1; next }
    /^# decoupled-terminal-transaction:end$/ { copying = 0; found = 1; next }
    copying { print }
    END { if (!found) exit 64 }
  ' "$contract_source" >"$destination" ||
    fail 'documented terminal transaction marker is incomplete'

  grep -q '^terminalize_authenticated_product() {' "$destination" ||
    fail 'documented terminal transaction function is missing'
  if grep -Eq 'ledger_(verify|upsert)|ledger_pr=|ledger_artifact_v1=|(^|[[:space:]])(gh|curl)[[:space:]]|spacedock[[:space:]]+new' "$destination"; then
    fail 'terminal transaction reaches measurement, network, or task-creation authority'
  fi
  # shellcheck source=/dev/null
  source "$destination"
}

extract_archive_contract() {
  local destination=$1

  awk '
    /^# decoupled-archive-comparator:start$/ { copying = 1; next }
    /^# decoupled-archive-comparator:end$/ { copying = 0; found = 1; next }
    copying { print }
    END { if (!found) exit 64 }
  ' "$PR_MERGE" >"$destination" ||
    fail 'documented archive comparator marker is incomplete'
  grep -q '^archive_verify() {' "$destination" ||
    fail 'documented archive comparator function is missing'
  # shellcheck source=/dev/null
  source "$destination"
}

git_identity() {
  git -C "$1" config user.name 'Decoupled Ledger Fixture'
  git -C "$1" config user.email 'decoupled-ledger-fixture@example.invalid'
}

make_artifact() {
  local live_path=$1
  python3 - "$live_path" <<'PY'
import base64
import hashlib
import json
import sys

raw = json.dumps(
    {"live_path": sys.argv[1]}, sort_keys=True, separators=(",", ":")
).encode("utf-8")
print(base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii"))
print(hashlib.sha256(raw).hexdigest())
PY
}

setup_fixture() {
  local case_name=$1
  local form=$2
  local ledger_ref=$3
  local ledger_artifact=$4
  local artifact_values
  local empty_tree
  local remote_repo
  local state_commit

  FIXTURE_REPO="$TEST_ROOT/$case_name"
  remote_repo="$TEST_ROOT/remotes/$case_name.git"
  WORKFLOW_DIR="$FIXTURE_REPO/docs/dev"
  STATE="$WORKFLOW_DIR/.spacedock-state"
  SLUG=decoupled-ledger-fixture
  TERMINAL='done'
  PRODUCT_PR_NUMBER=77
  PRODUCT_MERGED_AT=2026-07-31T09:50:02Z
  PRODUCT_HOST_STATE=MERGED
  PRODUCT_AUTHENTICATED=yes
  export TERMINAL PRODUCT_HOST_STATE PRODUCT_AUTHENTICATED

  mkdir -p "$WORKFLOW_DIR"
  mkdir -p "$(dirname "$remote_repo")"
  git init -q --bare "$remote_repo"
  git init -q -b main "$FIXTURE_REPO"
  git_identity "$FIXTURE_REPO"
  git -C "$FIXTURE_REPO" remote add origin "$remote_repo"

  cat >"$WORKFLOW_DIR/README.md" <<'EOF'
---
commissioned-by: spacedock@0.26.0
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
state: .spacedock-state
trunk: main
stages:
  defaults:
    worktree: false
    concurrency: 1
  states:
    - name: validation
      initial: true
    - name: done
      terminal: true
---

# Decoupled ledger contract fixture
EOF
  printf 'docs/dev/.spacedock-state/\n' >"$FIXTURE_REPO/.gitignore"
  git -C "$FIXTURE_REPO" add -- .gitignore docs/dev/README.md
  git -C "$FIXTURE_REPO" commit -q -m 'test: initialize fixture workflow'
  git -C "$FIXTURE_REPO" push -q -u origin main

  empty_tree=$(git -C "$FIXTURE_REPO" mktree </dev/null)
  state_commit=$(printf 'state: initialize fixture\n' |
    git -C "$FIXTURE_REPO" commit-tree "$empty_tree")
  git -C "$FIXTURE_REPO" update-ref refs/heads/spacedock-state/dev "$state_commit"
  git -C "$FIXTURE_REPO" push -q origin "$STATE_REF:$STATE_REF"
  git -C "$FIXTURE_REPO" worktree add -q "$STATE" spacedock-state/dev
  git -C "$STATE" branch --set-upstream-to=origin/spacedock-state/dev spacedock-state/dev >/dev/null

  if [[ "$form" == folder ]]; then
    LIVE_ROOT=$SLUG
    LIVE_INDEX="$SLUG/index.md"
    ARCHIVE_ROOT="_archive/$SLUG"
    ARCHIVE_INDEX="$ARCHIVE_ROOT/index.md"
    mkdir -p "$STATE/$LIVE_ROOT"
    printf 'fixture descendant\n' >"$STATE/$LIVE_ROOT/evidence.txt"
  else
    LIVE_ROOT="$SLUG.md"
    LIVE_INDEX=$LIVE_ROOT
    ARCHIVE_ROOT="_archive/$SLUG.md"
    ARCHIVE_INDEX=$ARCHIVE_ROOT
  fi

  artifact_values=$(make_artifact "$LIVE_INDEX")
  PRODUCT_ARTIFACT_B64URL=$(printf '%s\n' "$artifact_values" | sed -n '1p')
  PRODUCT_ARTIFACT_SHA256=$(printf '%s\n' "$artifact_values" | sed -n '2p')
  PRODUCT_REF="pr-merge:$PRODUCT_PR_NUMBER:artifact-v1:$PRODUCT_ARTIFACT_SHA256"

  cat >"$STATE/$LIVE_INDEX" <<EOF
---
id: 7rgdvsjypgmzk8wh03h3vst9
title: Decoupled ledger fixture
status: validation
source: contract fixture
product: repo-platform
sprint:
started: 2026-07-31T08:00:00Z
completed:
verdict:
worktree: .worktrees/fixture
issue:
pr: $PRODUCT_REF
ledger_pr: $ledger_ref
pr_artifact_v1: $PRODUCT_ARTIFACT_B64URL
ledger_artifact_v1: $ledger_artifact
mod-block: pr-merge:product-pr:v1:$PRODUCT_ARTIFACT_SHA256
design: required
lane: main
---

## Fixture body

Product delivery is authenticated; measurement is deliberately unavailable.
EOF
  git -C "$STATE" add -- "$LIVE_ROOT"
  git -C "$STATE" commit -q -m 'state: seed product-merged fixture'
  git -C "$STATE" push -q origin "HEAD:$STATE_REF"
  git -C "$STATE" fetch -q --no-tags origin "$STATE_REF"
  [[ "$(git -C "$STATE" rev-parse HEAD)" == \
    "$(git -C "$STATE" rev-parse FETCH_HEAD)" ]] ||
    fail 'fixture seed was not observed at its real origin'
}

frontmatter_assert() {
  local entity_path=$1
  local expected_status=$2
  local expected_ledger_ref=$3
  local expected_ledger_artifact=$4

  python3 - "$entity_path" "$expected_status" "$PRODUCT_MERGED_AT" \
    "$PRODUCT_REF" "$PRODUCT_ARTIFACT_B64URL" \
    "$expected_ledger_ref" "$expected_ledger_artifact" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
expected = {
    "status": sys.argv[2],
    "completed": sys.argv[3],
    "pr": sys.argv[4],
    "pr_artifact_v1": sys.argv[5],
    "ledger_pr": sys.argv[6],
    "ledger_artifact_v1": sys.argv[7],
}
lines = path.read_text(encoding="utf-8").splitlines()
if not lines or lines[0] != "---":
    raise SystemExit("fixture:frontmatter-missing")
fields = {}
for line in lines[1:]:
    if line == "---":
        break
    key, separator, value = line.partition(":")
    if separator:
        fields[key] = value.strip()
for key, value in expected.items():
    if fields.get(key) != value:
        raise SystemExit(
            f"fixture:{key}:expected={value!r}:actual={fields.get(key)!r}"
        )
verdict = fields.get("verdict", "")
verdict_ok = verdict == "PASSED"
if fields.get("pr", "").startswith("direct-commit:"):
    verdict_ok = verdict.lower() == "passed"
if not verdict_ok or fields.get("worktree") != "":
    raise SystemExit("fixture:terminal-fields-incomplete")
if fields.get("mod-block") != "":
    raise SystemExit("fixture:mod-block-not-cleared")
PY
}

seed_direct_commit_terminal() {
  local direct_commit=$1

  python3 - "$STATE/$LIVE_INDEX" "$direct_commit" "$PRODUCT_MERGED_AT" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
updates = {
    "status": "done",
    "completed": sys.argv[3],
    "verdict": "passed",
    "worktree": "",
    "pr": f"direct-commit:{sys.argv[2]}",
    "pr_artifact_v1": "",
    "mod-block": "",
}
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
for index, line in enumerate(lines):
    key, separator, _ = line.partition(":")
    if separator and key in updates:
        ending = "\n" if line.endswith("\n") else ""
        value = f" {updates[key]}" if updates[key] else ""
        lines[index] = f"{key}:{value}{ending}"
path.write_text("".join(lines), encoding="utf-8")
PY
  PRODUCT_REF="direct-commit:$direct_commit"
  PRODUCT_ARTIFACT_B64URL=
  git -C "$STATE" add -- "$LIVE_ROOT"
  git -C "$STATE" commit -q -m 'state: seed direct-commit terminal fixture'
}

run_terminal() {
  terminalize_authenticated_product
}

frontmatter_field() {
  python3 - "$1" "$2" <<'PY'
import pathlib
import sys

lines = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
for line in lines[1:]:
    if line == "---":
        break
    key, separator, value = line.partition(":")
    if separator and key == sys.argv[2]:
        print(value.strip())
        raise SystemExit(0)
raise SystemExit(1)
PY
}

publish_state_head() {
  git -C "$STATE" push -q origin "HEAD:$STATE_REF" || return 1
  git -C "$STATE" fetch -q --no-tags origin "$STATE_REF" || return 1
  [[ "$(git -C "$STATE" rev-parse 'HEAD^{commit}')" == \
    "$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}')" ]]
}

assert_remote_terminal() {
  local observed_tip
  local terminal_copy

  git -C "$STATE" fetch -q --no-tags origin "$STATE_REF" ||
    fail 'terminal fixture could not observe the remote state ref'
  observed_tip=$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}')
  [[ "$observed_tip" == "$(git -C "$STATE" rev-parse 'HEAD^{commit}')" ]] ||
    fail 'terminal state was committed locally but not observed remotely'
  git -C "$STATE" cat-file -e "$observed_tip:$LIVE_INDEX" ||
    fail 'remote terminal observation does not contain the live entity'
  terminal_copy=$(mktemp "$TEST_ROOT/remote-terminal.XXXXXX")
  git -C "$STATE" show "$observed_tip:$LIVE_INDEX" >"$terminal_copy"
  [[ "$(frontmatter_field "$terminal_copy" status)" == 'done' ]] ||
    fail 'remote observation does not contain terminal state'
}

authenticate_terminal_route() {
  local completed
  local direct_commit
  local entity="$STATE/$LIVE_INDEX"
  local product_artifact
  local product_ref
  local status
  local verdict
  local worktree

  status=$(frontmatter_field "$entity" status) || return 72
  completed=$(frontmatter_field "$entity" completed) || return 72
  verdict=$(frontmatter_field "$entity" verdict) || return 72
  worktree=$(frontmatter_field "$entity" worktree) || return 72
  product_ref=$(frontmatter_field "$entity" pr) || return 72
  product_artifact=$(frontmatter_field "$entity" pr_artifact_v1) || return 72
  [[ "$status" == 'done' && -n "$completed" && -z "$worktree" ]] || return 72

  case "$product_ref" in
    pr-merge:*)
      [[ "$verdict" == PASSED ]] || return 72
      [[ "${PRODUCT_AUTHENTICATED:-}" == yes && \
        "${PRODUCT_HOST_STATE:-}" == MERGED && \
        -n "${PRODUCT_MERGED_AT:-}" && \
        "$completed" == "$PRODUCT_MERGED_AT" && \
        "$product_ref" == "$PRODUCT_REF" && \
        -n "$product_artifact" && \
        "$product_artifact" == "$PRODUCT_ARTIFACT_B64URL" ]] || return 72
      ;;
    direct-commit:*)
      direct_commit=${product_ref#direct-commit:}
      [[ "$verdict" =~ ^[Pp][Aa][Ss][Ss][Ee][Dd]$ && \
        "$direct_commit" =~ ^[0-9a-f]{40}$ && \
        -z "$product_artifact" ]] || return 72
      git -C "$FIXTURE_REPO" fetch -q --no-tags origin main || return 72
      git -C "$FIXTURE_REPO" cat-file -e "$direct_commit^{commit}" || return 72
      git -C "$FIXTURE_REPO" merge-base --is-ancestor \
        "$direct_commit" origin/main || return 72
      ;;
    *) return 72 ;;
  esac
}

extract_commit_root() {
  local commit=$1
  local root=$2
  local destination=$3

  mkdir -p "$destination"
  git -C "$STATE" archive "$commit" "$root" |
    tar -xf - -C "$destination"
}

durable_archive() {
  local archive_commit
  local archive_parent
  local observed_copy
  local observed_tip
  local parent_copy
  local remote_tip

  authenticate_terminal_route || {
    printf 'archive:refused:terminal-authentication\n' >&2
    return 72
  }
  if [[ -n "$(git -C "$STATE" status --porcelain)" ]]; then
    printf 'archive:refused:durable-live-root-drift\n' >&2
    return 75
  fi

  git -C "$STATE" fetch -q --no-tags origin "$STATE_REF" || return 73
  remote_tip=$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}') || return 73
  archive_parent=$(git -C "$STATE" rev-parse 'HEAD^{commit}') || return 73
  if [[ "$archive_parent" != "$remote_tip" ]]; then
    printf 'archive:refused:terminal-state-not-remote-durable\n' >&2
    return 74
  fi
  git -C "$STATE" cat-file -e "$archive_parent:$LIVE_INDEX" || return 73
  if git -C "$STATE" cat-file -e "$archive_parent:$ARCHIVE_INDEX" 2>/dev/null; then
    return 73
  fi

  parent_copy=$(mktemp -d "$TEST_ROOT/archive-parent.XXXXXX") || return 73
  extract_commit_root "$archive_parent" "$LIVE_ROOT" "$parent_copy" || return 73

  "$SPACEDOCK_BIN" status --workflow-dir "$WORKFLOW_DIR" --archive "$SLUG" ||
    return 76
  [[ ! -e "$STATE/$LIVE_ROOT" && -e "$STATE/$ARCHIVE_INDEX" ]] ||
    return 76
  archive_verify "$parent_copy/$LIVE_ROOT" "$STATE/$ARCHIVE_ROOT" || {
    diff -u "$parent_copy/$LIVE_INDEX" "$STATE/$ARCHIVE_INDEX" >&2 || true
    return 76
  }

  git -C "$STATE" add -A -- "$LIVE_ROOT" "$ARCHIVE_ROOT" || return 77
  [[ -z "$(git -C "$STATE" diff --name-only)" ]] || return 77
  [[ -z "$(git -C "$STATE" ls-files --others --exclude-standard)" ]] || return 77
  git -C "$STATE" diff --cached --quiet && return 77
  git -C "$STATE" commit -q --signoff --only \
    -m "docs(dev): archive $SLUG" -- "$LIVE_ROOT" "$ARCHIVE_ROOT" || return 77
  archive_commit=$(git -C "$STATE" rev-parse 'HEAD^{commit}') || return 77
  [[ "$(git -C "$STATE" rev-parse "$archive_commit^")" == "$archive_parent" ]] ||
    return 77
  git -C "$STATE" log -1 --format=%B "$archive_commit" |
    grep -q '^Signed-off-by: ' || return 77

  git -C "$STATE" fetch -q --no-tags origin "$STATE_REF" || return 78
  [[ "$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}')" == "$archive_parent" ]] ||
    return 78
  [[ "$(git -C "$STATE" rev-list --count "FETCH_HEAD..HEAD")" == 1 ]] ||
    return 78
  git -C "$STATE" push -q origin "HEAD:$STATE_REF" || return 78
  git -C "$STATE" fetch -q --no-tags origin "$STATE_REF" || return 78
  observed_tip=$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}') || return 78
  [[ "$observed_tip" == "$archive_commit" ]] || return 78
  git -C "$STATE" cat-file -e "$observed_tip:$ARCHIVE_INDEX" || return 78
  if git -C "$STATE" cat-file -e "$observed_tip:$LIVE_INDEX" 2>/dev/null; then
    return 78
  fi
  observed_copy=$(mktemp -d "$TEST_ROOT/archive-observed.XXXXXX") || return 78
  extract_commit_root "$observed_tip" "$ARCHIVE_ROOT" "$observed_copy" || return 78
  archive_verify "$parent_copy/$LIVE_ROOT" "$observed_copy/$ARCHIVE_ROOT" || return 78
}

assert_single_archive() {
  local count
  count=$(find "$STATE/_archive" -type f \
    \( -name "$SLUG.md" -o -path "*/$SLUG/index.md" \) | wc -l | tr -d ' ')
  [[ "$count" == 1 ]] || fail "expected one archived entity, found $count"
  frontmatter_assert "$STATE/$ARCHIVE_INDEX" 'done' "$1" "$2"
  git -C "$STATE" show "HEAD:$ARCHIVE_INDEX" >/dev/null
}

assert_remote_archive() {
  local observed_tip

  git -C "$STATE" remote get-url origin >/dev/null 2>&1 ||
    fail 'archive fixture has no real origin'
  git -C "$STATE" fetch -q --no-tags origin refs/heads/spacedock-state/dev ||
    fail 'archive fixture could not observe the remote state ref'
  observed_tip=$(git -C "$STATE" rev-parse 'FETCH_HEAD^{commit}')
  [[ "$observed_tip" == "$(git -C "$STATE" rev-parse 'HEAD^{commit}')" ]] ||
    fail 'archive completion was not observed at the remote state ref'
  git -C "$STATE" cat-file -e "$observed_tip:$ARCHIVE_INDEX" ||
    fail 'remote observation does not contain the archived entity'
  if git -C "$STATE" cat-file -e "$observed_tip:$LIVE_INDEX" 2>/dev/null; then
    fail 'remote observation still contains the live entity'
  fi
}

auth_guard_matrix() {
  local before
  local after
  local guard

  for guard in flag host-state merged-at product-ref artifact; do
    setup_fixture "auth-$guard" flat '' ''
    before=$(git -C "$STATE" rev-parse HEAD)
    case "$guard" in
      flag) PRODUCT_AUTHENTICATED=no ;;
      host-state) PRODUCT_HOST_STATE=CLOSED ;;
      merged-at) PRODUCT_MERGED_AT= ;;
      product-ref) PRODUCT_REF=pr-merge:999:artifact-v1:wrong ;;
      artifact) PRODUCT_ARTIFACT_B64URL= ;;
    esac
    if run_terminal; then
      fail "terminalized with invalid product authentication guard: $guard"
    fi
    after=$(git -C "$STATE" rev-parse HEAD)
    [[ "$before" == "$after" ]] ||
      fail "authentication rejection committed state: $guard"
    grep -q '^status: validation$' "$STATE/$LIVE_INDEX" ||
      fail "authentication rejection changed task state: $guard"
  done
}

terminal_without_ledger() {
  local archive_contract="$TEST_ROOT/archive-contract.sh"
  local contract_file="$TEST_ROOT/terminal-contract.sh"
  local digest
  local form
  local pre_push_hook

  extract_terminal_contract "$contract_file"
  extract_archive_contract "$archive_contract"

  setup_fixture unauthenticated flat '' ''
  PRODUCT_AUTHENTICATED=no
  if run_terminal; then
    fail 'terminalized without authenticated product evidence'
  fi
  grep -q '^status: validation$' "$STATE/$LIVE_INDEX" ||
    fail 'unauthenticated product changed task state'

  auth_guard_matrix

  setup_fixture dirty-archive flat 'malformed ledger ref' 'opaque historical bytes'
  run_terminal
  assert_remote_terminal
  printf '\nunauthorized archive drift\n' >>"$STATE/$LIVE_INDEX"
  if durable_archive; then
    fail 'archive accepted a live root that differed from its durable terminal commit'
  fi
  [[ -e "$STATE/$LIVE_INDEX" && ! -e "$STATE/$ARCHIVE_INDEX" ]] ||
    fail 'failed archive mutated the live/archive roots'

  setup_fixture nondurable-terminal flat '' ''
  pre_push_hook="$(git -C "$FIXTURE_REPO" rev-parse --absolute-git-dir)/hooks/pre-push"
  printf '#!/bin/sh\nexit 1\n' >"$pre_push_hook"
  chmod +x "$pre_push_hook"
  if run_terminal; then
    fail 'terminal fixture unexpectedly pushed through the rejecting pre-push hook'
  fi
  rm -f "$pre_push_hook"
  if durable_archive; then
    fail 'archive accepted terminal state that was not durable at a remote origin'
  fi
  [[ -e "$STATE/$LIVE_INDEX" && ! -e "$STATE/$ARCHIVE_INDEX" ]] ||
    fail 'non-durable archive refusal mutated the live/archive roots'

  for form in flat folder; do
    setup_fixture "terminal-$form" "$form" \
      'malformed ledger ref' 'opaque historical bytes'
    run_terminal
    assert_remote_terminal
    digest=$(git -C "$STATE" rev-parse HEAD)
    frontmatter_assert "$STATE/$LIVE_INDEX" 'done' \
      'malformed ledger ref' 'opaque historical bytes'
    git -C "$STATE" show "$digest:$LIVE_INDEX" >/dev/null
    durable_archive
    assert_single_archive 'malformed ledger ref' 'opaque historical bytes'
    assert_remote_archive
    [[ ! -e "$WORKFLOW_DIR/ledger.csv" ]] ||
      fail 'terminal fixture unexpectedly created a ledger'
  done

  pass 'terminal-without-ledger'
}

compatibility() {
  local archive_contract="$TEST_ROOT/archive-contract.sh"
  local contract_file="$TEST_ROOT/terminal-contract.sh"
  local before
  local after
  local digest
  local ledger_ref
  local ledger_artifact
  local label
  local archive_text
  local empty_tree
  local unreachable_commit
  local reachable_commit

  extract_terminal_contract "$contract_file"
  extract_archive_contract "$archive_contract"
  before=$(git hash-object "$LEDGER")
  python3 - "$LEDGER" <<'PY'
import csv
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
with path.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.reader(handle))
expected = [
    "task_id", "slug", "dispatches", "rework_rounds", "wallclock_hours",
    "tokens_if_known", "diff_coverage", "escaped_defects_7d",
]
if not rows or [cell.strip() for cell in rows[0]] != expected:
    raise SystemExit("compatibility:header")
if any(len(row) != 8 for row in rows[1:]):
    raise SystemExit("compatibility:eight-column-history")
if not any(any(cell.strip() == "" for cell in row) for row in rows[1:]):
    raise SystemExit("compatibility:blank-history-missing")
if not any(row[7].strip().startswith("pending:") for row in rows[1:]):
    raise SystemExit("compatibility:dated-pending-history-missing")
if not any(any(cell.strip() == "n/a" for cell in row) for row in rows[1:]):
    raise SystemExit("compatibility:unknown-history-missing")
PY

  digest=$(printf 'a%.0s' {1..64})
  while IFS='|' read -r label ledger_ref ledger_artifact; do
    setup_fixture "compatibility-$label" flat "$ledger_ref" "$ledger_artifact"
    run_terminal
    frontmatter_assert "$STATE/$LIVE_INDEX" 'done' "$ledger_ref" "$ledger_artifact"
  done <<EOF
empty||
draft|ledger-pr:draft:artifact-v1:$digest|legacy-draft-bytes
pending|ledger-pr:pending:artifact-v1:$digest|legacy-pending-bytes
numbered|ledger-pr:99:artifact-v1:$digest|legacy-numbered-bytes
merged|ledger-merge:99:artifact-v1:$digest|legacy-merged-bytes
malformed|ledger-pr:banana:not-a-digest|legacy-malformed-bytes
EOF

  after=$(git hash-object "$LEDGER")
  [[ "$before" == "$after" ]] || fail 'historical ledger rows changed'

  before=$(git -C "$REPO_ROOT" rev-parse \
    'spacedock-state/dev:_archive/agy-first-whole-diff-review-seat.md')
  archive_text=$(git -C "$REPO_ROOT" show \
    'spacedock-state/dev:_archive/agy-first-whole-diff-review-seat.md')
  grep -q '^ledger_pr: ledger-merge:119:artifact-v1:' <<<"$archive_text" ||
    fail 'historical ledger merge reference is unreadable'
  after=$(git -C "$REPO_ROOT" rev-parse \
    'spacedock-state/dev:_archive/agy-first-whole-diff-review-seat.md')
  [[ "$before" == "$after" ]] || fail 'historical archived entity changed'

  setup_fixture direct-unreachable flat \
    'ledger-merge:119:artifact-v1:legacy' 'legacy-direct-bytes'
  empty_tree=$(git -C "$FIXTURE_REPO" mktree </dev/null)
  unreachable_commit=$(printf 'test: unreachable direct commit\n' |
    git -C "$FIXTURE_REPO" commit-tree "$empty_tree")
  seed_direct_commit_terminal "$unreachable_commit"
  publish_state_head || fail 'could not publish unreachable direct-commit fixture state'
  if durable_archive; then
    fail 'legacy direct-commit route accepted a commit not reachable from origin/main'
  fi
  [[ -e "$STATE/$LIVE_INDEX" && ! -e "$STATE/$ARCHIVE_INDEX" ]] ||
    fail 'direct-commit authentication refusal mutated the live/archive roots'

  setup_fixture direct-valid folder \
    'ledger-merge:119:artifact-v1:legacy' 'legacy-direct-bytes'
  reachable_commit=$(git -C "$FIXTURE_REPO" rev-parse 'origin/main^{commit}')
  seed_direct_commit_terminal "$reachable_commit"
  publish_state_head || fail 'could not publish valid direct-commit fixture state'
  durable_archive
  assert_single_archive \
    'ledger-merge:119:artifact-v1:legacy' 'legacy-direct-bytes'
  assert_remote_archive

  pass 'compatibility'
}

derive_archive_metrics() {
  python3 - "$1" <<'PY'
import datetime
import pathlib
import re
import sys

text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
lines = text.splitlines()
fields = {}
for line in lines[1:]:
    if line == "---":
        break
    key, separator, value = line.partition(":")
    if separator:
        fields[key] = value.strip()

started = datetime.datetime.fromisoformat(fields["started"].replace("Z", "+00:00"))
completed = datetime.datetime.fromisoformat(fields["completed"].replace("Z", "+00:00"))
dispatches = len(re.findall(r"^D[0-9]+ launched ", text, re.MULTILINE))
rework = len(set(re.findall(r"Cycle ([0-9]+): REJECTED", text)))
hours = f"{(completed - started).total_seconds() / 3600:.2f}".rstrip("0").rstrip(".")
token_values = re.findall(
    r"^D[0-9]+ launched [^\n|]+\| tokens:[ \t]*([^ \t\r\n]+)",
    text,
    re.MULTILINE,
)
tokens = "n/a" if len(token_values) == dispatches and set(token_values) == {"n/a"} else "unknown"
coverages = re.findall(
    r"Diff coverage:[^\n]*\*\*([0-9]+(?:\.[0-9]+)?)%\*\*", text
)
coverage = coverages[-1] if coverages else "unknown"
deadline = (completed.date() + datetime.timedelta(days=7)).isoformat()
print(",".join((str(dispatches), str(rework), hours, tokens, coverage, f"pending:{deadline}")))
PY
}

archive_derive() {
  local archive_copy="$TEST_ROOT/archive.md"
  local unknown_copy="$TEST_ROOT/archive-unknown.md"
  local ledger_copy="$TEST_ROOT/ledger.csv"
  local state_tree_before
  local state_tree_after
  local derived
  local unknown

  state_tree_before=$(git -C "$REPO_ROOT" rev-parse 'spacedock-state/dev^{tree}')
  git -C "$REPO_ROOT" show \
    'spacedock-state/dev:_archive/agy-first-whole-diff-review-seat.md' >"$archive_copy"
  derived=$(derive_archive_metrics "$archive_copy")
  [[ "$derived" == '14,2,18.81,n/a,88.17,pending:2026-08-07' ]] ||
    fail "archive derivation mismatch: $derived"

  cp "$LEDGER" "$ledger_copy"
  python3 - "$ledger_copy" "$derived" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
task_id = "4a255s3z87s7x09vn2fnscep"
row = f"{task_id}, agy-first-whole-diff-review-seat, {sys.argv[2].replace(',', ', ')}"
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
matches = [i for i, line in enumerate(lines) if line.startswith(task_id + ",")]
if len(matches) != 1:
    raise SystemExit("archive-derive:ledger-row")
ending = "\n" if lines[matches[0]].endswith("\n") else ""
lines[matches[0]] = row + ending
path.write_text("".join(lines), encoding="utf-8")
if row not in path.read_text(encoding="utf-8").splitlines():
    raise SystemExit("archive-derive:upsert")
PY
  cmp -s "$LEDGER" "$ledger_copy" ||
    fail 'derived exemplar did not reproduce its historical row byte-for-byte'

  python3 - "$archive_copy" "$unknown_copy" <<'PY'
import pathlib
import re
import sys

text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"(\| tokens:)[^\n]*", r"\1", text)
text = re.sub(r"^.*Diff coverage:.*$", "", text, flags=re.MULTILINE)
pathlib.Path(sys.argv[2]).write_text(text, encoding="utf-8")
PY
  unknown=$(derive_archive_metrics "$unknown_copy")
  [[ "$unknown" == '14,2,18.81,unknown,unknown,pending:2026-08-07' ]] ||
    fail "missing optional evidence was not reported unknown: $unknown"

  state_tree_after=$(git -C "$REPO_ROOT" rev-parse 'spacedock-state/dev^{tree}')
  [[ "$state_tree_before" == "$state_tree_after" ]] ||
    fail 'archive-first observation mutated workflow state'

  pass 'archive-derive'
}

scope_diff_guard() {
  python3 - "$1" <<'PY'
import pathlib
import re
import sys

for line_number, line in enumerate(
    pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines(), 1
):
    if not line.startswith("+") or line.startswith("+++"):
        continue
    addition = line[1:]
    forbidden = (
        r"\bspacedock\s+(?:new|commission|sprint|advance|promote)\b",
        r"\bautomatic_[A-Za-z0-9_]*(?:task|process)[A-Za-z0-9_]*\s*\(\)",
        r"\b(?:create|open)_[A-Za-z0-9_]*(?:task|process)[A-Za-z0-9_]*\s*\(\)",
    )
    if any(re.search(pattern, addition) for pattern in forbidden):
        print(
            f"scope:auto-process-mutation:{line_number}:{addition}",
            file=sys.stderr,
        )
        raise SystemExit(1)
PY
}

scope_check() {
  local changed
  local contract_diff="$TEST_ROOT/contract.diff"
  local path
  local untracked

  changed=$(git -C "$REPO_ROOT" diff --name-only origin/main --)
  untracked=$(git -C "$REPO_ROOT" ls-files --others --exclude-standard)
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    case "$path" in
      docs/dev/README.md | docs/dev/_mods/pr-merge.md | \
        docs/dev/artifacts/decoupled-ledger-contract-test.sh) ;;
      *) fail "scope includes unauthorized path: $path" ;;
    esac
  done < <(printf '%s\n%s\n' "$changed" "$untracked" | sort -u)

  git -C "$REPO_ROOT" diff --unified=0 --no-ext-diff origin/main -- \
    docs/dev/README.md docs/dev/_mods/pr-merge.md >"$contract_diff"
  scope_diff_guard "$contract_diff" ||
    fail 'authorized contract diff adds automatic task or process mutation'

  pass 'scope'
}

scope_mutation_probe() {
  local auth_mutation="$TEST_ROOT/pr-merge-auth-mutation.md"
  local baseline_mutation="$TEST_ROOT/pr-merge-baseline-mutation.md"
  local ledger_mutation="$TEST_ROOT/pr-merge-ledger-mutation.md"
  local mutated_diff="$TEST_ROOT/contract-mutated.diff"
  local unknown_mutation="$TEST_ROOT/unknown-mutation.sh"

  git -C "$REPO_ROOT" diff --unified=0 --no-ext-diff origin/main -- \
    docs/dev/README.md docs/dev/_mods/pr-merge.md >"$mutated_diff"
  printf '+automatic_measurement_task(){ spacedock new repo-platform --workflow-dir docs/dev; }\n' \
    >>"$mutated_diff"
  if scope_diff_guard "$mutated_diff"; then
    fail 'scope guard accepted automatic task creation outside the terminal marker'
  fi

  python3 - "$PR_MERGE" "$ledger_mutation" "$baseline_mutation" <<'PY'
import pathlib
import sys

text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
text = text.replace(
    "# decoupled-terminal-transaction:end",
    "  ledger_verify premerge fixture fixture docs/dev/ledger.csv\n"
    "# decoupled-terminal-transaction:end",
    1,
)
pathlib.Path(sys.argv[2]).write_text(text, encoding="utf-8")
baseline = text.replace(
    "# decoupled-terminal-transaction:start",
    "has delivered the pre-merge ledger row but has",
    1,
)
pathlib.Path(sys.argv[3]).write_text(baseline, encoding="utf-8")
PY
  if (extract_terminal_contract "$TEST_ROOT/ledger-mutation.sh" "$ledger_mutation"); then
    fail 'terminal contract accepted ledger re-coupling'
  fi
  if (extract_terminal_contract "$TEST_ROOT/baseline-mutation.sh" "$baseline_mutation"); then
    fail 'terminal contract accepted the ledger-gated baseline'
  fi

  python3 - "$PR_MERGE" "$auth_mutation" <<'PY'
import pathlib
import sys

text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
old = '''  if [ "${PRODUCT_AUTHENTICATED:-}" != yes ] ||
    [ "${PRODUCT_HOST_STATE:-}" != MERGED ] ||'''
new = '''  if [ "${PRODUCT_HOST_STATE:-}" != MERGED ] ||'''
if old not in text:
    raise SystemExit("mutation:auth-guard-source")
pathlib.Path(sys.argv[2]).write_text(text.replace(old, new, 1), encoding="utf-8")
PY
  if CONTRACT_PR_MERGE="$auth_mutation" bash "$0" terminal-without-ledger \
    >/dev/null 2>&1; then
    fail 'terminal suite accepted authentication-guard removal'
  fi

  python3 - "$0" "$unknown_mutation" <<'PY'
import pathlib
import sys

text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
old = 'coverage = coverages[-1] if coverages else "unknown"'
new = 'coverage = coverages[-1] if coverages else "0"'
if old not in text:
    raise SystemExit("mutation:unknown-source")
pathlib.Path(sys.argv[2]).write_text(text.replace(old, new, 1), encoding="utf-8")
PY
  if bash "$unknown_mutation" archive-derive >/dev/null 2>&1; then
    fail 'archive derivation accepted invented zero coverage'
  fi

  pass 'mutation-probes'
}

# coverage-harness:start
coverage_ratchet() {
  local trace_file="$TEST_ROOT/coverage.trace"
  local run_output="$TEST_ROOT/coverage-runs.log"
  local uncovered_file="$TEST_ROOT/coverage-uncovered.log"
  local covered
  local total
  local percent
  local failures=0
  local mode

  exec 9>"$trace_file"
  for mode in terminal-without-ledger compatibility archive-derive scope mutation-probes all; do
    if ! BASH_XTRACEFD=9 PS4='+TRACE:${BASH_SOURCE}:${LINENO}:' \
      bash -x "$0" "$mode" >>"$run_output" 2>&1; then
      failures=$((failures + 1))
    fi
  done
  exec 9>&-

  read -r covered total percent < <(
    python3 - "$REPO_ROOT" "$0" "$trace_file" "$uncovered_file" <<'PY'
import pathlib
import re
import subprocess
import sys

repo = pathlib.Path(sys.argv[1]).resolve()
script = pathlib.Path(sys.argv[2]).resolve()
trace = pathlib.Path(sys.argv[3])
uncovered_file = pathlib.Path(sys.argv[4])
relative = script.relative_to(repo).as_posix()
diff = subprocess.run(
    ["git", "-C", str(repo), "diff", "--unified=0", "--no-ext-diff", "origin/main", "--", relative],
    check=True,
    stdout=subprocess.PIPE,
    text=True,
).stdout.splitlines()

added = set()
new_line = None
for line in diff:
    match = re.match(r"^@@ -[0-9]+(?:,[0-9]+)? \+([0-9]+)(?:,([0-9]+))? @@", line)
    if match:
        new_line = int(match.group(1))
        continue
    if new_line is None or line.startswith("---") or line.startswith("+++"):
        continue
    if line.startswith("+"):
        added.add(new_line)
        new_line += 1
    elif line.startswith("-"):
        continue
    else:
        new_line += 1

lines = script.read_text(encoding="utf-8").splitlines()
candidates = set()
heredoc = None
continuation_start = None
excluded = False
for number, raw in enumerate(lines, 1):
    stripped = raw.strip()
    if stripped == "# coverage-harness:start":
        excluded = True
        continue
    if stripped == "# coverage-harness:end":
        excluded = False
        continue
    if excluded:
        continue
    if heredoc is not None:
        if stripped == heredoc:
            heredoc = None
        continue
    heredoc_match = re.search(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)", raw)
    logical = continuation_start or number
    if stripped and not stripped.startswith("#"):
        structural = (
            stripped in {"{", "}", "then", "else", "fi", "do", "done", "esac", ";;"}
            or bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*\(\)\s*\{$", stripped))
            or bool(re.match(r"^(for|case)\b", stripped))
            or bool(re.match(r"^[^ )]+\)$", stripped))
        )
        if not structural and logical in added:
            candidates.add(logical)
    if heredoc_match:
        heredoc = heredoc_match.group(1)
    continued = raw.rstrip().endswith(("\\", "|", "||", "&&"))
    if continued and continuation_start is None:
        continuation_start = number
    elif not continued:
        continuation_start = None

executed = set()
pattern = re.compile(r"^\++TRACE:(.*):([0-9]+):")
for line in trace.read_text(encoding="utf-8", errors="replace").splitlines():
    match = pattern.match(line)
    if not match:
        continue
    source = pathlib.Path(match.group(1)).resolve()
    if source == script:
        executed.add(int(match.group(2)))

covered = len(candidates & executed)
total = len(candidates)
percent = 100.0 if total == 0 else covered * 100.0 / total
uncovered_file.write_text(
    "".join(f"{number}: {lines[number - 1]}\n" for number in sorted(candidates - executed)),
    encoding="utf-8",
)
print(covered, total, f"{percent:.2f}")
PY
  )
  printf 'decoupled-ledger-contract:COVERAGE:%s/%s=%s%%\n' \
    "$covered" "$total" "$percent"
  if ((failures != 0)); then
    tail -n 80 "$run_output" >&2
    fail "coverage run had $failures failing focused mode(s)"
  fi
  awk -v percent="$percent" 'BEGIN { exit !(percent >= 85) }' ||
    {
      sed -n '1,120p' "$uncovered_file" >&2
      fail "executable changed-line coverage $percent% is below 85%"
    }
  pass 'coverage'
}
# coverage-harness:end

case "$MODE" in
  terminal-without-ledger)
    terminal_without_ledger
    ;;
  compatibility)
    compatibility
    ;;
  archive-derive)
    archive_derive
    ;;
  scope)
    scope_check
    ;;
  mutation-probes)
    scope_mutation_probe
    ;;
  coverage)
    coverage_ratchet
    ;;
  all)
    terminal_without_ledger
    compatibility
    archive_derive
    scope_check
    scope_mutation_probe
    ;;
  *)
    fail 'usage: decoupled-ledger-contract-test.sh [terminal-without-ledger|compatibility|archive-derive|scope|mutation-probes|coverage|all]'
    ;;
esac
