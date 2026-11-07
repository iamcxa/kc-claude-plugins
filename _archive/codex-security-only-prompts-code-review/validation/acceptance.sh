#!/usr/bin/env bash
set -euo pipefail

# 1. Export the reviewed bytes. Expect the exact head and five changed paths.
REPO='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-codex-security-only-prompts-code-review'
PKG='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0'
HEAD_SHA='37b1c0b7a9561ee48165cefbc9424a4390fe9d0a'
BASE_SHA='ba055b8a7a55a787ac989c4cef52d07dd75661ad'
RUN_DIR=$(mktemp -d /tmp/codex-security-acceptance.XXXXXX)
mkdir -p "$RUN_DIR/candidate" "$RUN_DIR/base"
git -C "$REPO" archive "$HEAD_SHA" | tar -x -C "$RUN_DIR/candidate"
git -C "$REPO" archive "$BASE_SHA" | tar -x -C "$RUN_DIR/base"
git -C "$REPO" rev-parse "$HEAD_SHA"
git -C "$REPO" diff --name-only "$BASE_SHA...$HEAD_SHA" > "$RUN_DIR/changed.txt"
printf '%s\n' kc-dev-flow-2/extensions/codex/EXTENSION.md kc-dev-flow-2/extensions/codex/codex_review.py kc-dev-flow-2/extensions/codex/test_codex_review.py kc-dev-flow-2/scripts/pr_watch.py kc-dev-flow-2/scripts/test_pr_watch.py > "$RUN_DIR/expected.txt"
diff -u "$RUN_DIR/expected.txt" "$RUN_DIR/changed.txt"
cat "$RUN_DIR/changed.txt"

# 2. Exercise the reader and watcher. Expect 36 and 135 tests, both OK.
cd "$RUN_DIR/candidate/kc-dev-flow-2/extensions/codex"
python3 -B -m unittest test_codex_review
cd "$RUN_DIR/candidate/kc-dev-flow-2/scripts"
python3 -B -m unittest test_pr_watch

# 3. Read historical PR 727 from GitHub. Needs authenticated gh and network.
# Expect exit 4 in both, a security-only request in the candidate, no evidence=.
for SIDE in base candidate; do
  STATUS=0
  python3 -B -I "$RUN_DIR/$SIDE/kc-dev-flow-2/extensions/codex/codex_review.py" iamcxa/kc-claude-plugins 727 > "$RUN_DIR/$SIDE-727.txt" || STATUS=$?
  test "$STATUS" -eq 4
  printf '%s exit %s\n' "$SIDE" "$STATUS"
  cat "$RUN_DIR/$SIDE-727.txt"
done
python3 - "$RUN_DIR" <<'PY'
from pathlib import Path
import sys
r = Path(sys.argv[1])
assert (r / 'base-727.txt').read_text() == 'not reviewed: no Codex evidence covers 5dee91fb7\n'
text = (r / 'candidate-727.txt').read_text()
assert 'security-only=summary:6434584622' in text
assert 'next: comment `@codex review` on the PR once' in text
assert 'evidence=' not in text
assert len(text.splitlines()) == 2 and len(text.split()) <= 26
print('Historical security-only replay: PASS')
PY

# 4. Check the word bounds and decision records. Expect unchanged 5939 words,
# extension 310 -> 325, routing lint OK, and 61 ADRs checked with exit 0.
python3 - "$RUN_DIR" <<'PY'
from pathlib import Path
import sys
r = Path(sys.argv[1])
for path, delta in [('kc-dev-flow-2/references/sd/workflow.md', 0), ('kc-dev-flow-2/extensions/codex/EXTENSION.md', 15)]:
    before = (r / 'base' / path).read_text()
    after = (r / 'candidate' / path).read_text()
    a, b = len(before.split()), len(after.split())
    assert b - a <= delta
    if delta == 0:
        assert before == after
    print(f'{path}: {a} -> {b}')
PY
cd "$RUN_DIR/candidate"
python3 -B kc-dev-flow-2/scripts/lint-skills.py
GIT_DIR=$(git -C "$REPO" rev-parse --absolute-git-dir) GIT_WORK_TREE="$RUN_DIR/candidate" python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE_SHA" --require 0039
printf 'ACCEPTANCE PASS; export and logs: %s\n' "$RUN_DIR"
