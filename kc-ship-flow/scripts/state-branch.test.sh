#!/usr/bin/env bash
# Behavior contract for how intent.sh and holder.sh find the state branch.
#
# These two scripts had no tests, which is how `branch=spacedock-state/dev` survived
# in both of them. It is the pair that pushes to a remote state branch, so a wrong
# branch here does not fail loudly: it writes one workflow's state onto another's.
#
# Self-check -- prove this suite catches the bug it was written for (manual):
#   sed -i.bak 's|branch=$(git -C "$state" for-each-ref.*|branch=spacedock-state/dev|' \
#     kc-ship-flow/scripts/holder.sh
#   bash kc-ship-flow/scripts/state-branch.test.sh; echo "exit: $?"
# Expect case a to FAIL and a non-zero exit.

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

PASS=0
FAIL=0
pass() { printf 'case %s: PASS - %s\n' "$1" "$2"; PASS=$((PASS + 1)); }
fail() { printf 'case %s: FAIL - %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

# One bare repository standing in for the remote, carrying two state branches so a
# script writing to the wrong one is visible rather than merely unproven.
setup() {
  local name=$1 branch=$2 remote=${3:-origin}
  local bare="$TMP_DIR/$name.git" work="$TMP_DIR/$name"
  git init -q --bare "$bare"
  git init -q "$work" && git -C "$work" remote add "$remote" "$bare"
  git -C "$work" -c user.name=t -c user.email=t@l commit -q --allow-empty -m seed
  for b in spacedock-state/dev spacedock-state/ship; do
    git -C "$work" branch -q -f "$b" HEAD
    git -C "$work" push -q "$remote" "$b"
  done
  git -C "$work" checkout -q "$branch"
  git -C "$work" branch -q --set-upstream-to "$remote/$branch"
  echo "$work"
}
tip() { git -C "$TMP_DIR/$1.git" rev-parse "$2" 2>/dev/null || echo missing; }

# (a) the bug: a ship state root must not write to the dev branch
W=$(setup a spacedock-state/ship)
before_dev=$(tip a spacedock-state/dev)
if bash "$HERE/holder.sh" claim "$W" writer-one >/dev/null 2>&1; then
  after_dev=$(tip a spacedock-state/dev)
  after_ship=$(tip a spacedock-state/ship)
  if [ "$after_dev" = "$before_dev" ] && [ "$after_ship" != "$before_dev" ]; then
    pass a "a ship state root writes to spacedock-state/ship and leaves dev untouched"
  else
    fail a "wrote to the wrong branch: dev moved=$([ "$after_dev" != "$before_dev" ] && echo yes || echo no) ship moved=$([ "$after_ship" != "$before_dev" ] && echo yes || echo no)"
  fi
else
  fail a "holder.sh claim failed on a ship state root"
fi

# (b) a branch name carrying a slash survives the strip
if [ "$(git -C "$W" rev-parse --abbrev-ref HEAD)" = "spacedock-state/ship" ]; then
  pass b "the branch name keeps its slash"
else
  fail b "checkout is not on spacedock-state/ship"
fi

# (c) a remote that is not named origin is used, not origin
W2=$(setup c spacedock-state/ship upstream)
before=$(tip c spacedock-state/ship)
if bash "$HERE/holder.sh" claim "$W2" writer-one >/dev/null 2>&1 \
  && [ "$(tip c spacedock-state/ship)" != "$before" ]; then
  pass c "a remote named upstream is fetched and pushed, not a hardcoded origin"
else
  fail c "did not reach a remote named upstream"
fi

# (d) no upstream: refuse with a reason, and write nothing
W3=$(setup d spacedock-state/ship)
git -C "$W3" branch -q --unset-upstream
err=$(bash "$HERE/holder.sh" claim "$W3" writer-one 2>&1 >/dev/null)
if [ -n "$err" ] && [ ! -f "$W3/_holder.json" ] && printf '%s' "$err" | grep -q "tracks no upstream"; then
  pass d "a checkout with no upstream is refused by name, and nothing is written"
else
  fail d "expected a named refusal and no record; got: $err"
fi

# (e) the same derivation guards intent.sh, not only holder.sh
W4=$(setup e spacedock-state/ship)
git -C "$W4" branch -q --unset-upstream
err=$(bash "$HERE/intent.sh" show "$W4" some.claim 2>&1 >/dev/null)
if printf '%s' "$err" | grep -q "tracks no upstream"; then
  pass e "intent.sh refuses the same way, so the fence and the intent agree"
else
  fail e "intent.sh did not refuse for the same reason; got: $err"
fi

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
