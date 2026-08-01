#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
SUBJECT="$SCRIPT_DIR/github-repo-write.sh"
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/github-repo-write.XXXXXX")
REAL_GIT=$(command -v git)
PASS_COUNT=0
FAIL_COUNT=0

cleanup() {
  if [ -n "${REPO:-}" ] && [ -n "${LINKED_WORKTREE:-}" ]; then
    git -C "$REPO" worktree remove --force "$LINKED_WORKTREE" >/dev/null 2>&1 || true
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
  local label="$1" expected="$2" actual="$3"
  if [ "$actual" = "$expected" ]; then
    pass "$label"
  else
    fail "$label"
    printf '  expected: %s\n  actual:   %s\n' "$expected" "$actual"
  fi
}

assert_contains() {
  local label="$1" expected="$2" actual="$3"
  case "$actual" in
    *"$expected"*) pass "$label" ;;
    *)
      fail "$label"
      printf '  expected substring: %s\n  actual:             %s\n' "$expected" "$actual"
      ;;
  esac
}

assert_not_contains() {
  local label="$1" rejected="$2" actual="$3"
  case "$actual" in
    *"$rejected"*)
      fail "$label"
      printf '  rejected substring: %s\n  actual:              %s\n' "$rejected" "$actual"
      ;;
    *) pass "$label" ;;
  esac
}

REPO="$TEST_ROOT/repo"
LINKED_WORKTREE="$TEST_ROOT/linked"
STUB_BIN="$TEST_ROOT/bin"
GH_LOG="$TEST_ROOT/gh.log"
GIT_LOG="$TEST_ROOT/git.log"
mkdir -p "$REPO" "$STUB_BIN"

git init -q "$REPO"
git -C "$REPO" checkout -q -b main
git -C "$REPO" config user.name "Repository Preflight Test"
git -C "$REPO" config user.email "repo-preflight@test.com"
printf '%s\n' fixture >"$REPO/fixture.txt"
git -C "$REPO" add fixture.txt
git -C "$REPO" commit -q -m "fixture: initial"
git -C "$REPO" remote add origin git@github.com:acme/widgets.git

cat >"$STUB_BIN/gh" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >>"$GH_LOG"
if [ "${1:-}" = repo ] && [ "${2:-}" = view ]; then
  printf '%s\n' "${GH_CANONICAL_REPO:-acme/widgets}"
  exit 0
fi
if [ "${1:-}" = pr ] && [ "${2:-}" = merge ]; then
  printf '%s\n' merged
  exit 0
fi
printf 'unexpected gh command: %s\n' "$*" >&2
exit 64
EOF
chmod +x "$STUB_BIN/gh"
export GH_LOG
cat >"$STUB_BIN/git" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = -C ] && [ "${3:-}" = push ]; then
  printf '%s\n' "$*" >>"$GIT_LOG"
  printf '%s\n' pushed
  exit 0
fi
exec "$REAL_GIT" "$@"
EOF
chmod +x "$STUB_BIN/git"
export GIT_LOG REAL_GIT
PATH="$STUB_BIN:$PATH"
export PATH

MATCH_OUT="$TEST_ROOT/match.out"
MATCH_ERR="$TEST_ROOT/match.err"
GH_CANONICAL_REPO=acme/widgets "$SUBJECT" preflight --worktree "$REPO" \
  >"$MATCH_OUT" 2>"$MATCH_ERR"
assert_eq "matching remote returns the canonical repository" \
  "acme/widgets" "$(cat "$MATCH_OUT")"
assert_eq "matching remote emits no diagnostic noise" "" "$(cat "$MATCH_ERR")"

: >"$GIT_LOG"
MATCH_PUSH_OUT=$(GH_CANONICAL_REPO=acme/widgets "$SUBJECT" push --worktree "$REPO" \
  --remote origin --branch main --set-upstream 2>"$TEST_ROOT/match-push.err")
assert_eq "validated push returns transport output" "pushed" "$MATCH_PUSH_OUT"
assert_eq "validated push pins worktree, remote, branch, and upstream mode" \
  "-C $REPO push -u origin main" "$(cat "$GIT_LOG")"

git -C "$REPO" remote set-url origin https://github.com/legacy/widgets.git
TRANSFER_ERR="$TEST_ROOT/transfer.err"
: >"$GH_LOG"
: >"$GIT_LOG"
GH_CANONICAL_REPO=modern/widgets "$SUBJECT" push --worktree "$REPO" \
  --remote origin --branch main --set-upstream \
  >"$TEST_ROOT/transfer.out" 2>"$TRANSFER_ERR"
TRANSFER_RC=$?
if [ "$TRANSFER_RC" -ne 0 ]; then
  pass "transferred repository fails before a write"
else
  fail "transferred repository fails before a write"
fi
TRANSFER_DIAGNOSTIC=$(cat "$TRANSFER_ERR")
assert_contains "transfer diagnostic names configured identity" \
  "configured remote identity: legacy/widgets" "$TRANSFER_DIAGNOSTIC"
assert_contains "transfer diagnostic names canonical identity" \
  "canonical GitHub identity: modern/widgets" "$TRANSFER_DIAGNOSTIC"
assert_contains "transfer diagnostic gives an exact repair command" \
  "git remote set-url origin 'https://github.com/modern/widgets.git' 'https://github.com/legacy/widgets.git'" \
  "$TRANSFER_DIAGNOSTIC"
assert_eq "preflight never rewrites the user remote" \
  "https://github.com/legacy/widgets.git" "$(git -C "$REPO" remote get-url origin)"
assert_eq "transferred repository never reaches git push" "" "$(cat "$GIT_LOG")"

git -C "$REPO" remote set-url origin git@github.com:modern/widgets.git
git -C "$REPO" config --unset-all remote.origin.pushurl >/dev/null 2>&1 || true
git -C "$REPO" remote set-url --add --push origin git@github.com:legacy/widgets.git
: >"$GIT_LOG"
PUSHURL_ERR="$TEST_ROOT/pushurl.err"
GH_CANONICAL_REPO=modern/widgets "$SUBJECT" push --worktree "$REPO" \
  --remote origin --branch main >"$TEST_ROOT/pushurl.out" 2>"$PUSHURL_ERR"
PUSHURL_RC=$?
if [ "$PUSHURL_RC" -ne 0 ]; then
  pass "stale pushurl fails before a write"
else
  fail "stale pushurl fails before a write"
fi
PUSHURL_DIAGNOSTIC=$(cat "$PUSHURL_ERR")
assert_contains "pushurl diagnostic names the actual configured destination" \
  "configured push identity: legacy/widgets" "$PUSHURL_DIAGNOSTIC"
assert_contains "pushurl diagnostic gives the pushurl repair command" \
  "git remote set-url --push origin 'git@github.com:modern/widgets.git' 'git@github.com:legacy/widgets.git'" \
  "$PUSHURL_DIAGNOSTIC"
assert_eq "stale pushurl never reaches git push" "" "$(cat "$GIT_LOG")"
assert_eq "preflight never rewrites pushurl" "git@github.com:legacy/widgets.git" \
  "$(git -C "$REPO" remote get-url --push origin)"

git -C "$REPO" config --unset-all remote.origin.pushurl
git -C "$REPO" remote set-url --add --push origin git@github.com:modern/widgets.git
git -C "$REPO" remote set-url --add --push origin git@github.com:legacy/widgets.git
: >"$GIT_LOG"
MULTI_ERR="$TEST_ROOT/multi-pushurl.err"
GH_CANONICAL_REPO=modern/widgets "$SUBJECT" push --worktree "$REPO" \
  --remote origin --branch main >"$TEST_ROOT/multi-pushurl.out" 2>"$MULTI_ERR"
MULTI_RC=$?
if [ "$MULTI_RC" -ne 0 ]; then
  pass "mixed current and stale pushurls fail before a write"
else
  fail "mixed current and stale pushurls fail before a write"
fi
assert_contains "multi-pushurl repair targets the exact stale URL" \
  "git remote set-url --push origin 'git@github.com:modern/widgets.git' 'git@github.com:legacy/widgets.git'" \
  "$(cat "$MULTI_ERR")"
assert_eq "mixed pushurls never reach git push" "" "$(cat "$GIT_LOG")"

git -C "$REPO" config --unset-all remote.origin.pushurl
git -C "$REPO" remote set-url --add --push origin https://secret-token@github.com/acme/widgets.git
: >"$GIT_LOG"
CREDENTIAL_ERR="$TEST_ROOT/credential.err"
GH_CANONICAL_REPO=acme/widgets "$SUBJECT" push --worktree "$REPO" \
  --remote origin --branch main >"$TEST_ROOT/credential.out" 2>"$CREDENTIAL_ERR"
CREDENTIAL_RC=$?
if [ "$CREDENTIAL_RC" -ne 0 ]; then
  pass "credential-bearing push URL fails before a write"
else
  fail "credential-bearing push URL fails before a write"
fi
assert_not_contains "unsupported URL diagnostic redacts credentials" \
  "secret-token" "$(cat "$CREDENTIAL_ERR")"
assert_contains "unsupported URL diagnostic identifies the safe repair class" \
  "credential-free github.com URL" "$(cat "$CREDENTIAL_ERR")"
assert_eq "credential-bearing URL never reaches git push" "" "$(cat "$GIT_LOG")"

git -C "$REPO" config --unset-all remote.origin.pushurl
git -C "$REPO" config --unset-all remote.origin.url
git -C "$REPO" config --add remote.origin.url git@github.com:modern/widgets.git
git -C "$REPO" config --add remote.origin.url git@github.com:legacy/widgets.git
: >"$GIT_LOG"
MULTI_URL_ERR="$TEST_ROOT/multi-url.err"
GH_CANONICAL_REPO=modern/widgets "$SUBJECT" push --worktree "$REPO" \
  --remote origin --branch main >"$TEST_ROOT/multi-url.out" 2>"$MULTI_URL_ERR"
MULTI_URL_RC=$?
if [ "$MULTI_URL_RC" -ne 0 ]; then
  pass "mixed current and stale ordinary remote URLs fail before a write"
else
  fail "mixed current and stale ordinary remote URLs fail before a write"
fi
assert_contains "multi-URL repair targets the exact stale URL" \
  "git remote set-url origin 'git@github.com:modern/widgets.git' 'git@github.com:legacy/widgets.git'" \
  "$(cat "$MULTI_URL_ERR")"
assert_eq "mixed ordinary URLs never reach git push" "" "$(cat "$GIT_LOG")"

CANONICAL_TARGET=$(GH_CANONICAL_REPO=modern/widgets "$SUBJECT" preflight \
  --repo legacy/widgets 2>"$TEST_ROOT/target.err")
assert_eq "explicit PR target resolves independently of push remote" \
  "modern/widgets" "$CANONICAL_TARGET"

git -C "$REPO" config --unset-all remote.origin.pushurl >/dev/null 2>&1 || true
git -C "$REPO" config --unset-all remote.origin.url
git -C "$REPO" config --add remote.origin.url git@github.com:acme/widgets.git
git -C "$REPO" branch feature
git -C "$REPO" worktree add -q "$LINKED_WORKTREE" feature
MAIN_BRANCH_BEFORE=$(git -C "$REPO" branch --show-current)
LINKED_BRANCH_BEFORE=$(git -C "$LINKED_WORKTREE" branch --show-current)
: >"$GH_LOG"
HEAD_SHA=0123456789012345678901234567890123456789
MERGE_OUT=$(cd "$LINKED_WORKTREE" && GH_CANONICAL_REPO=acme/widgets "$SUBJECT" merge \
  --repo acme/widgets --pr 42 --head "$HEAD_SHA" --method squash)
assert_eq "merge command returns transport output" "merged" "$MERGE_OUT"
MERGE_CALL=$(tail -n 1 "$GH_LOG")
assert_eq "merge pins canonical repo and reviewed head" \
  "pr merge 42 --repo acme/widgets --match-head-commit $HEAD_SHA --squash" "$MERGE_CALL"
assert_not_contains "merge never requests branch deletion" "--delete-branch" "$MERGE_CALL"
assert_eq "merge does not switch the primary worktree" \
  "$MAIN_BRANCH_BEFORE" "$(git -C "$REPO" branch --show-current)"
assert_eq "merge does not switch the linked worktree" \
  "$LINKED_BRANCH_BEFORE" "$(git -C "$LINKED_WORKTREE" branch --show-current)"
assert_eq "merge leaves local feature branch cleanup separate" \
  "feature" "$(git -C "$REPO" branch --list feature --format='%(refname:short)')"

: >"$GIT_LOG"
"$REAL_GIT" -C "$LINKED_WORKTREE" update-ref refs/remotes/origin/review-head HEAD
"$REAL_GIT" -C "$LINKED_WORKTREE" config branch.feature.remote origin
"$REAL_GIT" -C "$LINKED_WORKTREE" config branch.feature.merge refs/heads/review-head
"$REAL_GIT" -C "$LINKED_WORKTREE" config push.default current
ALIAS_PUSH_OUT=$(GH_CANONICAL_REPO=acme/widgets "$SUBJECT" push \
  --worktree "$LINKED_WORKTREE" --remote origin --tracked)
assert_eq "local-alias push returns transport output" "pushed" "$ALIAS_PUSH_OUT"
assert_eq "push.default=current cannot replace the configured PR head" \
  "-C $LINKED_WORKTREE push origin HEAD:refs/heads/review-head" \
  "$(cat "$GIT_LOG")"

: >"$GIT_LOG"
"$REAL_GIT" -C "$LINKED_WORKTREE" config push.default matching
FORCE_PUSH_OUT=$(GH_CANONICAL_REPO=acme/widgets "$SUBJECT" push \
  --worktree "$LINKED_WORKTREE" --remote origin --tracked --force-with-lease)
assert_eq "tracked force-push returns transport output" "pushed" "$FORCE_PUSH_OUT"
assert_eq "push.default=matching force-push still targets one upstream ref" \
  "-C $LINKED_WORKTREE push --force-with-lease origin HEAD:refs/heads/review-head" \
  "$(cat "$GIT_LOG")"

: >"$GH_LOG"
DELETE_ERR="$TEST_ROOT/delete.err"
GH_CANONICAL_REPO=acme/widgets "$SUBJECT" merge --repo acme/widgets \
  --pr 42 --head "$HEAD_SHA" --method squash --delete-branch \
  >"$TEST_ROOT/delete.out" 2>"$DELETE_ERR"
DELETE_RC=$?
if [ "$DELETE_RC" -ne 0 ]; then
  pass "merge rejects combined branch deletion"
else
  fail "merge rejects combined branch deletion"
fi
assert_contains "branch-deletion rejection directs separate cleanup" \
  "clean up remote and local branches separately" "$(cat "$DELETE_ERR")"
assert_not_contains "rejected branch deletion never reaches GitHub" \
  "pr merge" "$(cat "$GH_LOG")"

CREATE_SKILL="$SCRIPT_DIR/../skills/kc-pr-create/SKILL.md"
REVIEW_SKILL="$SCRIPT_DIR/../skills/kc-pr-review/SKILL.md"
RESOLVE_SKILL="$SCRIPT_DIR/../skills/kc-pr-review-resolve/SKILL.md"
REORG_SKILL="$SCRIPT_DIR/../skills/kc-pr-reorg/SKILL.md"
API_PATTERNS="$SCRIPT_DIR/../reference/gh-api-patterns.md"

for skill in "$CREATE_SKILL" "$REVIEW_SKILL" "$RESOLVE_SKILL"; do
  if grep -Fq 'scripts/github-repo-write.sh" preflight --repo' "$skill"; then
    pass "$(basename "$(dirname "$skill")") requires the canonical preflight"
  else
    fail "$(basename "$(dirname "$skill")") requires the canonical preflight"
  fi
done

CREATE_PUSH_COUNT=$(grep -Fc 'scripts/github-repo-write.sh" push' "$CREATE_SKILL")
if [ "$CREATE_PUSH_COUNT" -ge 4 ] &&
   grep -Fq 'scripts/github-repo-write.sh" push' "$RESOLVE_SKILL" &&
   grep -Fq 'scripts/github-repo-write.sh" push' "$REORG_SKILL"; then
  pass "all branch-push skills route the write through the validated adapter"
else
  fail "all branch-push skills route the write through the validated adapter"
fi

if grep -Fq -- '--tracked' "$RESOLVE_SKILL"; then
  pass "review resolution preserves the tracked PR head refspec"
else
  fail "review resolution preserves the tracked PR head refspec"
fi

CREATE_PATTERN="gh pr create --repo \"\$REPO\""
if grep -Fq "$CREATE_PATTERN" "$CREATE_SKILL"; then
  pass "PR creation pins the canonical repository explicitly"
else
  fail "PR creation pins the canonical repository explicitly"
fi

MERGE_PATTERN="github-repo-write.sh\" merge --repo \"\$REPO\""
if grep -Fq "$MERGE_PATTERN" "$API_PATTERNS"; then
  pass "the shared API reference routes merges through the safe adapter"
else
  fail "the shared API reference routes merges through the safe adapter"
fi

REVIEW_PREFLIGHT_LINE=$(grep -nF 'scripts/github-repo-write.sh" preflight --repo' "$REVIEW_SKILL" | head -1 | cut -d: -f1)
ONCE_ONLY_LINE=$(grep -nF '**Once-only posting path' "$REVIEW_SKILL" | head -1 | cut -d: -f1)
if [ -n "$REVIEW_PREFLIGHT_LINE" ] && [ -n "$ONCE_ONLY_LINE" ] &&
   [ "$REVIEW_PREFLIGHT_LINE" -lt "$ONCE_ONLY_LINE" ]; then
  pass "review canonicalizes its explicit PR target before once-only posting"
else
  fail "review canonicalizes its explicit PR target before once-only posting"
fi

assert_marked_push_fails_closed() {
  local label="$1" skill="$2" marker="$3" recipe
  recipe="$TEST_ROOT/$marker.sh"
  sed -n "/^# $marker:start$/,/^# $marker:end$/p" "$skill" | sed '1d;$d' >"$recipe"
  if ! grep -Fq 'github-repo-write.sh" push' "$recipe"; then
    fail "$label exposes an executable validated-push recipe"
    return
  fi
  pass "$label exposes an executable validated-push recipe"

  git -C "$REPO" remote set-url origin git@github.com:modern/widgets.git
  git -C "$REPO" config --unset-all remote.origin.pushurl >/dev/null 2>&1 || true
  git -C "$REPO" remote set-url --add --push origin git@github.com:legacy/widgets.git
  "$REAL_GIT" -C "$REPO" update-ref refs/remotes/origin/main HEAD
  "$REAL_GIT" -C "$REPO" config branch.main.remote origin
  "$REAL_GIT" -C "$REPO" config branch.main.merge refs/heads/main
  : >"$GIT_LOG"
  GH_CANONICAL_REPO=modern/widgets CLAUDE_PLUGIN_ROOT="$SCRIPT_DIR/.." \
    bash "$recipe" >"$TEST_ROOT/$marker.out" 2>"$TEST_ROOT/$marker.err"
  local rc=$?
  if [ "$rc" -ne 0 ]; then
    pass "$label aborts when its effective push destination is stale"
  else
    fail "$label aborts when its effective push destination is stale"
  fi
  assert_eq "$label never bypasses into git push" "" "$(cat "$GIT_LOG")"
}

assert_marked_push_fails_closed "create AI-fix path" "$CREATE_SKILL" \
  "github-repo-create-ai-fix-push"
assert_marked_push_fails_closed "review-resolution path" "$RESOLVE_SKILL" \
  "github-repo-review-resolve-push"

printf '%d passed, %d failed\n' "$PASS_COUNT" "$FAIL_COUNT"
[ "$FAIL_COUNT" -eq 0 ]
