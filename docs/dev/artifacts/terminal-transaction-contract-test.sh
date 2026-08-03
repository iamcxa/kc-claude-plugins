#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
PR_MERGE=${CONTRACT_PR_MERGE:-"$REPO_ROOT/docs/dev/_mods/pr-merge.md"}
SPACEDOCK_BIN=${SPACEDOCK_BIN:-spacedock}
MODE=${1:-all}
STATE_REF=refs/heads/spacedock-state/dev
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/terminal-transaction-contract.XXXXXX")
trap 'rm -rf "$TEST_ROOT"' EXIT

fail() {
  printf 'terminal-transaction-contract:FAIL:%s\n' "$*" >&2
  exit 1
}

pass() {
  printf 'terminal-transaction-contract:PASS:%s\n' "$*"
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
  git -C "$1" config user.name 'Terminal Transaction Fixture'
  git -C "$1" config user.email 'terminal-transaction-fixture@example.invalid'
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

# The ledger_pr / ledger_artifact_v1 arguments seed frontmatter keys the schema no
# longer declares. They are retained because live entities still carry them until the
# state migration lands; the assertions prove the terminal transaction preserves
# fields it does not own rather than clobbering them.
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
  SLUG=terminal-transaction-fixture
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

# Terminal transaction contract fixture
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
title: Terminal transaction fixture
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
  archive_verify "$parent_copy/$LIVE_ROOT" "$STATE/$ARCHIVE_ROOT" || return 76

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

terminal_transaction() {
  local archive_contract="$TEST_ROOT/archive-contract.sh"
  local contract_file="$TEST_ROOT/terminal-contract.sh"
  local digest
  local empty_tree
  local form
  local guard
  local pre_push_hook
  local reachable_commit
  local unreachable_commit
  local valid_product_artifact
  local valid_product_merged_at
  local valid_product_ref

  extract_terminal_contract "$contract_file"
  extract_archive_contract "$archive_contract"

  setup_fixture local-guard-matrix flat '' ''
  valid_product_artifact=$PRODUCT_ARTIFACT_B64URL
  valid_product_merged_at=$PRODUCT_MERGED_AT
  valid_product_ref=$PRODUCT_REF
  for guard in PRODUCT_AUTHENTICATED PRODUCT_HOST_STATE PRODUCT_MERGED_AT \
    PRODUCT_REF PRODUCT_ARTIFACT_B64URL; do
    PRODUCT_AUTHENTICATED=yes
    PRODUCT_HOST_STATE=MERGED
    PRODUCT_MERGED_AT=$valid_product_merged_at
    PRODUCT_REF=$valid_product_ref
    PRODUCT_ARTIFACT_B64URL=$valid_product_artifact
    case "$guard" in
      PRODUCT_AUTHENTICATED) PRODUCT_AUTHENTICATED=no ;;
      PRODUCT_HOST_STATE) PRODUCT_HOST_STATE=CLOSED ;;
      PRODUCT_MERGED_AT) PRODUCT_MERGED_AT= ;;
      PRODUCT_REF) PRODUCT_REF=pr-merge:77:artifact-v1:mismatch ;;
      PRODUCT_ARTIFACT_B64URL) PRODUCT_ARTIFACT_B64URL= ;;
    esac
    if run_terminal; then
      fail "$guard guard accepted invalid local evidence"
    fi
    grep -q '^status: validation$' "$STATE/$LIVE_INDEX" ||
      fail "$guard refusal changed task state"
  done

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
    [[ ! -e "$WORKFLOW_DIR/ledger.csv" ]] ||
      fail 'terminal fixture unexpectedly created a ledger'
  done

  # The legacy direct-commit route is the second of two terminalization routes and
  # has its own authentication guard: the commit must be reachable from origin/main.
  # This coverage lived in the deleted `compatibility` mode, which seeded it with
  # ledger frontmatter values; the route under test was never the ledger.
  setup_fixture direct-unreachable flat \
    'malformed ledger ref' 'opaque historical bytes'
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
    'malformed ledger ref' 'opaque historical bytes'
  reachable_commit=$(git -C "$FIXTURE_REPO" rev-parse 'origin/main^{commit}')
  seed_direct_commit_terminal "$reachable_commit"
  publish_state_head || fail 'could not publish valid direct-commit fixture state'
  durable_archive
  assert_single_archive 'malformed ledger ref' 'opaque historical bytes'

  pass 'terminal-transaction'
}

case "$MODE" in
  terminal-transaction | all)
    terminal_transaction
    ;;
  *)
    fail 'usage: terminal-transaction-contract-test.sh [terminal-transaction|all]'
    ;;
esac
