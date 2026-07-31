#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
README="$REPO_ROOT/docs/dev/README.md"
PR_MERGE="$REPO_ROOT/docs/dev/_mods/pr-merge.md"
LEDGER="$REPO_ROOT/docs/dev/ledger.csv"
SPACEDOCK_BIN=${SPACEDOCK_BIN:-spacedock}
MODE=${1:-all}
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

  if ! grep -q '^# decoupled-terminal-transaction:start$' "$PR_MERGE"; then
    if grep -q 'has delivered the pre-merge ledger row but has' "$PR_MERGE"; then
      fail 'RED: authenticated product MERGED still enters ledger finalization before terminal state'
    fi
    fail 'documented terminal transaction marker is missing'
  fi

  awk '
    /^# decoupled-terminal-transaction:start$/ { copying = 1; next }
    /^# decoupled-terminal-transaction:end$/ { copying = 0; found = 1; next }
    copying { print }
    END { if (!found) exit 64 }
  ' "$PR_MERGE" >"$destination" ||
    fail 'documented terminal transaction marker is incomplete'

  grep -q '^terminalize_authenticated_product() {' "$destination" ||
    fail 'documented terminal transaction function is missing'
  if grep -Eq 'ledger_(verify|upsert)|ledger_pr=|ledger_artifact_v1=|(^|[[:space:]])(gh|curl)[[:space:]]|spacedock[[:space:]]+new' "$destination"; then
    fail 'terminal transaction reaches measurement, network, or task-creation authority'
  fi
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
  local state_commit

  FIXTURE_REPO="$TEST_ROOT/$case_name"
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
  git init -q -b main "$FIXTURE_REPO"
  git_identity "$FIXTURE_REPO"

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

  empty_tree=$(git -C "$FIXTURE_REPO" mktree </dev/null)
  state_commit=$(printf 'state: initialize fixture\n' |
    git -C "$FIXTURE_REPO" commit-tree "$empty_tree")
  git -C "$FIXTURE_REPO" update-ref refs/heads/spacedock-state/dev "$state_commit"
  git -C "$FIXTURE_REPO" worktree add -q "$STATE" spacedock-state/dev

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
if fields.get("verdict") != "PASSED" or fields.get("worktree") != "":
    raise SystemExit("fixture:terminal-fields-incomplete")
if fields.get("mod-block") != "":
    raise SystemExit("fixture:mod-block-not-cleared")
PY
}

run_terminal() {
  terminalize_authenticated_product
}

durable_archive() {
  if ! git -C "$STATE" diff --quiet -- "$LIVE_ROOT" ||
    ! git -C "$STATE" diff --cached --quiet -- "$LIVE_ROOT"; then
    printf 'archive:refused:durable-live-root-drift\n' >&2
    return 75
  fi

  "$SPACEDOCK_BIN" status --workflow-dir "$WORKFLOW_DIR" --archive "$SLUG"
  [[ ! -e "$STATE/$LIVE_ROOT" && -e "$STATE/$ARCHIVE_INDEX" ]] ||
    return 76
  git -C "$STATE" add -- "$LIVE_ROOT" "$ARCHIVE_ROOT"
  git -C "$STATE" commit -q --signoff -m "docs(dev): archive $SLUG" -- \
    "$LIVE_ROOT" "$ARCHIVE_ROOT"
}

assert_single_archive() {
  local count
  count=$(find "$STATE/_archive" -type f \
    \( -name "$SLUG.md" -o -path "*/$SLUG/index.md" \) | wc -l | tr -d ' ')
  [[ "$count" == 1 ]] || fail "expected one archived entity, found $count"
  frontmatter_assert "$STATE/$ARCHIVE_INDEX" 'done' "$1" "$2"
  git -C "$STATE" show "HEAD:$ARCHIVE_INDEX" >/dev/null
}

terminal_without_ledger() {
  local contract_file="$TEST_ROOT/terminal-contract.sh"
  local digest
  local form

  extract_terminal_contract "$contract_file"

  setup_fixture unauthenticated flat '' ''
  PRODUCT_AUTHENTICATED=no
  if run_terminal; then
    fail 'terminalized without authenticated product evidence'
  fi
  grep -q '^status: validation$' "$STATE/$LIVE_INDEX" ||
    fail 'unauthenticated product changed task state'

  setup_fixture dirty-archive flat 'malformed ledger ref' 'opaque historical bytes'
  run_terminal
  printf '\nunauthorized archive drift\n' >>"$STATE/$LIVE_INDEX"
  if durable_archive; then
    fail 'archive accepted a live root that differed from its durable terminal commit'
  fi
  [[ -e "$STATE/$LIVE_INDEX" && ! -e "$STATE/$ARCHIVE_INDEX" ]] ||
    fail 'failed archive mutated the live/archive roots'

  for form in flat folder; do
    setup_fixture "terminal-$form" "$form" \
      'malformed ledger ref' 'opaque historical bytes'
    run_terminal
    digest=$(git -C "$STATE" rev-parse HEAD)
    frontmatter_assert "$STATE/$LIVE_INDEX" 'done' \
      'malformed ledger ref' 'opaque historical bytes'
    git -C "$STATE" show "$digest:$LIVE_INDEX" >/dev/null
    durable_archive
    assert_single_archive 'malformed ledger ref' 'opaque historical bytes'
    [[ ! -e "$WORKFLOW_DIR/ledger.csv" ]] ||
      fail 'terminal fixture unexpectedly created a ledger'
  done

  pass 'terminal-without-ledger'
}

compatibility() {
  local contract_file="$TEST_ROOT/terminal-contract.sh"
  local before
  local after
  local digest
  local ledger_ref
  local ledger_artifact
  local label
  local archive_text

  extract_terminal_contract "$contract_file"
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

scope_check() {
  local changed
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

  grep -q 'human-triggered.*measurement' "$README" ||
    fail 'README does not keep observation human-triggered'
  grep -q 'cannot block.*terminal' "$README" ||
    fail 'README does not state the non-authoritative measurement boundary'
  grep -q 'new explicit captain approval' "$README" ||
    fail 'README does not preserve captain scope authority'

  pass 'scope'
}

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
  all)
    terminal_without_ledger
    compatibility
    archive_derive
    scope_check
    ;;
  *)
    fail 'usage: decoupled-ledger-contract-test.sh [terminal-without-ledger|compatibility|archive-derive|scope|all]'
    ;;
esac
