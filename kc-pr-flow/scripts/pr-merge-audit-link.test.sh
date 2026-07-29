#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH='' cd -- "$SCRIPT_DIR/../.." && pwd)
MOD_PATH=${PR_MERGE_MOD_PATH:-"$REPO_ROOT/docs/dev/_mods/pr-merge.md"}
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/pr-merge-audit-link.XXXXXX")
RECIPE_PATH="$TEST_ROOT/pr-merge-audit-link-recipe.sh"
PASS_COUNT=0
FAIL_COUNT=0

cleanup() {
  if [ -n "${CODE_REPO:-}" ] && [ -n "${FO_REPO:-}" ]; then
    git -C "$CODE_REPO" worktree remove --force "$FO_REPO" >/dev/null 2>&1 || true
  fi
  rm -rf "$TEST_ROOT"
}
trap cleanup EXIT

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  printf 'ok %d - %s\n' "$((PASS_COUNT + FAIL_COUNT))" "$1"
}

fail() {
  FAIL_COUNT=$((FAIL_COUNT + 1))
  printf 'not ok %d - %s\n' "$((PASS_COUNT + FAIL_COUNT))" "$1"
}

assert_eq() {
  local label="$1"
  local expected="$2"
  local actual="$3"

  if [ "$actual" = "$expected" ]; then
    pass "$label"
  else
    fail "$label"
    printf '  expected: %s\n' "$expected"
    printf '  actual:   %s\n' "$actual"
  fi
}

assert_contains() {
  local label="$1"
  local expected="$2"
  local actual="$3"

  case "$actual" in
    *"$expected"*) pass "$label" ;;
    *)
      fail "$label"
      printf '  expected substring: %s\n' "$expected"
      printf '  actual:             %s\n' "$actual"
      ;;
  esac
}

assert_nonzero() {
  local label="$1"
  local actual="$2"

  if [ "$actual" -ne 0 ]; then
    pass "$label"
  else
    fail "$label"
    printf '  expected: nonzero\n'
    printf '  actual:   %s\n' "$actual"
  fi
}

sed -n '/^# pr-merge-audit-link-recipe:start$/,/^# pr-merge-audit-link-recipe:end$/p' "$MOD_PATH" |
  sed '1d;$d' >"$RECIPE_PATH"
if ! grep -q '^pr_merge_audit_link()' "$RECIPE_PATH"; then
  printf 'Bail out! marked pr-merge audit-link recipe was not extracted\n'
  exit 1
fi
# shellcheck source=/dev/null
. "$RECIPE_PATH"

CODE_REPO="$TEST_ROOT/code"
FO_REPO="$TEST_ROOT/fo"
STATE_REPO="$TEST_ROOT/state"
STUB_BIN="$TEST_ROOT/bin"
mkdir -p "$CODE_REPO" "$STATE_REPO" "$STUB_BIN"

git init -q "$CODE_REPO"
git -C "$CODE_REPO" checkout -q -b main
git -C "$CODE_REPO" config user.name "Audit Link Test"
git -C "$CODE_REPO" config user.email "audit-link@example.test"
mkdir -p "$CODE_REPO/docs/dev" "$CODE_REPO/docs/dev-split"
printf '%s\n' 'state: inline' >"$CODE_REPO/docs/dev/README.md"
printf '%s\n' 'inline entity' >"$CODE_REPO/docs/dev/inline.md"
printf '%s\n' 'state: .state' >"$CODE_REPO/docs/dev-split/README.md"
git -C "$CODE_REPO" add docs/dev/README.md docs/dev/inline.md docs/dev-split/README.md
git -C "$CODE_REPO" commit -q -m "fixture: code head"
CODE_SHA=$(git -C "$CODE_REPO" rev-parse HEAD)
CODE_SHORT_SHA=$(git -C "$CODE_REPO" rev-parse --short HEAD)

git -C "$CODE_REPO" branch fo
git -C "$CODE_REPO" worktree add -q "$FO_REPO" fo
git -C "$FO_REPO" config user.name "Audit Link Test"
git -C "$FO_REPO" config user.email "audit-link@example.test"
printf '%s\n' 'fo-only commit' >"$FO_REPO/fo-only.txt"
git -C "$FO_REPO" add fo-only.txt
git -C "$FO_REPO" commit -q -m "fixture: distinct fo head"
FO_SHA=$(git -C "$FO_REPO" rev-parse HEAD)

git init -q "$STATE_REPO"
git -C "$STATE_REPO" checkout -q -b spacedock-state/dev
git -C "$STATE_REPO" config user.name "Audit Link Test"
git -C "$STATE_REPO" config user.email "audit-link@example.test"
printf '%s\n' 'split entity' >"$STATE_REPO/split.md"
git -C "$STATE_REPO" add split.md
git -C "$STATE_REPO" commit -q -m "fixture: state head"
STATE_SHA=$(git -C "$STATE_REPO" rev-parse HEAD)
printf '%s\n' 'staged-only entity' >"$STATE_REPO/staged.md"
git -C "$STATE_REPO" add staged.md

INLINE_WORKFLOW="$FO_REPO/docs/dev"
INLINE_ENTITY="$INLINE_WORKFLOW/inline.md"
SPLIT_WORKFLOW="$CODE_REPO/docs/dev-split"
SPLIT_ENTITY="$STATE_REPO/split.md"
export INLINE_WORKFLOW INLINE_ENTITY SPLIT_WORKFLOW SPLIT_ENTITY STATE_REPO

cat >"$STUB_BIN/gh" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' 'acme/widgets'
EOF
chmod +x "$STUB_BIN/gh"

cat >"$STUB_BIN/spacedock" <<'EOF'
#!/usr/bin/env bash
workflow_dir=
operation=
entity_ref=

if [ "${1:-}" != status ]; then
  printf 'unsupported spacedock command\n' >&2
  exit 64
fi
shift
while [ "$#" -gt 0 ]; do
  case "$1" in
    --workflow-dir)
      workflow_dir=$2
      shift 2
      ;;
    --resolve)
      operation=resolve
      entity_ref=$2
      shift 2
      ;;
    --short-id)
      operation=short-id
      entity_ref=$2
      shift 2
      ;;
    --json)
      shift
      ;;
    *)
      printf 'unsupported spacedock argument: %s\n' "$1" >&2
      exit 64
      ;;
  esac
done

if [ "$operation" = short-id ]; then
  printf '%s\n' "$entity_ref"
  exit 0
fi
if [ "$operation" != resolve ]; then
  printf 'missing spacedock operation\n' >&2
  exit 64
fi

case "${RESOLVE_MODE:-ok}" in
  nonzero)
    printf 'resolver transport failed\n' >&2
    exit 17
    ;;
  malformed)
    printf '{\n'
    ;;
  missing-workflow)
    printf '{"path":"%s"}\n' "$SPLIT_ENTITY"
    ;;
  missing-path)
    printf '{"workflow":"%s"}\n' "$STATE_REPO"
    ;;
  empty-workflow)
    printf '{"workflow":"","path":"%s"}\n' "$SPLIT_ENTITY"
    ;;
  empty-path)
    printf '{"workflow":"%s","path":""}\n' "$STATE_REPO"
    ;;
  nonstring-workflow)
    printf '{"workflow":7,"path":"%s"}\n' "$SPLIT_ENTITY"
    ;;
  nonstring-path)
    printf '{"workflow":"%s","path":[]}\n' "$STATE_REPO"
    ;;
  missing-blob)
    printf '{"workflow":"%s","path":"%s/staged.md"}\n' "$STATE_REPO" "$STATE_REPO"
    ;;
  ok)
    if [ "$workflow_dir" = "$INLINE_WORKFLOW" ]; then
      printf '{"workflow":"%s","path":"%s"}\n' "$INLINE_WORKFLOW" "$INLINE_ENTITY"
    elif [ "$workflow_dir" = "$SPLIT_WORKFLOW" ]; then
      printf '{"workflow":"%s","path":"%s"}\n' "$STATE_REPO" "$SPLIT_ENTITY"
    else
      printf 'unknown workflow fixture: %s\n' "$workflow_dir" >&2
      exit 65
    fi
    ;;
  *)
    printf 'unknown resolver mode: %s\n' "$RESOLVE_MODE" >&2
    exit 64
    ;;
esac
EOF
chmod +x "$STUB_BIN/spacedock"
PATH="$STUB_BIN:$PATH"
export PATH

if [ "$CODE_SHA" != "$FO_SHA" ]; then
  pass 'precondition: inline FO and code worktrees have distinct heads'
else
  fail 'precondition: inline FO and code worktrees have distinct heads'
fi

if git -C "$CODE_REPO" cat-file -e "$CODE_SHORT_SHA:docs/dev-split/split.md" 2>/dev/null; then
  fail 'precondition: committed buggy split-root tuple names no code blob'
else
  pass 'precondition: committed buggy split-root tuple names no code blob'
fi

INLINE_OUT="$TEST_ROOT/inline.out"
INLINE_ERR="$TEST_ROOT/inline.err"
RESOLVE_MODE=ok PR_MERGE_ENTITY_REPO_PATH=docs/dev/inline.md \
  pr_merge_audit_link "$CODE_REPO" "$INLINE_WORKFLOW" inline >"$INLINE_OUT" 2>"$INLINE_ERR"
INLINE_RC=$?
assert_eq 'inline recipe exits zero' '0' "$INLINE_RC"
assert_eq \
  'inline recipe retains code-head short SHA and repo-relative path' \
  "[inline](/acme/widgets/blob/$CODE_SHORT_SHA/docs/dev/inline.md)" \
  "$(cat "$INLINE_OUT")"
assert_eq 'inline recipe emits no diagnostic' '' "$(cat "$INLINE_ERR")"

SPLIT_OUT="$TEST_ROOT/split.out"
SPLIT_ERR="$TEST_ROOT/split.err"
RESOLVE_MODE=ok PR_MERGE_ENTITY_REPO_PATH=docs/dev-split/split.md \
  pr_merge_audit_link "$CODE_REPO" "$SPLIT_WORKFLOW" split >"$SPLIT_OUT" 2>"$SPLIT_ERR"
SPLIT_RC=$?
assert_eq 'split-root recipe exits zero' '0' "$SPLIT_RC"
assert_eq \
  'split-root recipe uses full state SHA and state-root-relative path' \
  "[split](/acme/widgets/blob/$STATE_SHA/split.md)" \
  "$(cat "$SPLIT_OUT")"
assert_eq 'split-root recipe emits no diagnostic' '' "$(cat "$SPLIT_ERR")"

run_negative_case() {
  local mode="$1"
  local diagnostic="$2"
  local stdout_path="$TEST_ROOT/$mode.out"
  local stderr_path="$TEST_ROOT/$mode.err"
  local rc

  RESOLVE_MODE="$mode" PR_MERGE_ENTITY_REPO_PATH=docs/dev-split/split.md \
    pr_merge_audit_link "$CODE_REPO" "$SPLIT_WORKFLOW" split >"$stdout_path" 2>"$stderr_path"
  rc=$?
  assert_nonzero "$mode resolver result stops audit-link construction" "$rc"
  assert_contains "$mode resolver result emits its diagnostic" "$diagnostic" "$(cat "$stderr_path")"
  assert_eq "$mode resolver result emits no tuple or link" '' "$(cat "$stdout_path")"
}

run_negative_case nonzero 'pr-merge audit link: resolver command failed for split'
run_negative_case malformed 'pr-merge audit link: resolver returned malformed JSON for split'
run_negative_case missing-workflow 'pr-merge audit link: resolver result missing workflow for split'
run_negative_case missing-path 'pr-merge audit link: resolver result missing path for split'
run_negative_case empty-workflow 'pr-merge audit link: resolver result has empty workflow for split'
run_negative_case empty-path 'pr-merge audit link: resolver result has empty path for split'
run_negative_case nonstring-workflow 'pr-merge audit link: resolver result has non-string workflow for split'
run_negative_case nonstring-path 'pr-merge audit link: resolver result has non-string path for split'
run_negative_case missing-blob "pr-merge audit link: resolved blob missing for split: $STATE_SHA:staged.md"

printf '1..%d\n' "$((PASS_COUNT + FAIL_COUNT))"
printf '# pass %d\n' "$PASS_COUNT"
printf '# fail %d\n' "$FAIL_COUNT"
[ "$FAIL_COUNT" -eq 0 ]
