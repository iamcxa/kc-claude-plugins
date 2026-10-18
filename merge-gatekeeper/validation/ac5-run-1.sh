#!/bin/bash
set -u
REPO=iamcxa/kc-merge-gate-ac5-throwaway-20261018
NAME=${REPO#*/}
GATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-gatekeeper/kc-dev-flow-2/scripts/delivery_gate.py
W=/tmp/mg-ac5
export GIT_AUTHOR_NAME=ac5 GIT_AUTHOR_EMAIL=ac5@example.invalid GIT_COMMITTER_NAME=ac5 GIT_COMMITTER_EMAIL=ac5@example.invalid
run() { echo; echo "\$ $*"; "$@"; echo "[exit=$?]"; }
sh_run() { echo; echo "\$ $1"; sh -c "$1"; echo "[exit=$?]"; }
cd $W
echo "# AC-5 throwaway-repository run, $(date -u +%Y-%m-%dT%H:%M:%SZ); gate script at kc-dev-flow-2/scripts/delivery_gate.py of the PR branch, head $(git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-gatekeeper rev-parse HEAD)"
run gh repo create $REPO --private --description "throwaway: delivery_gate AC-5 test, delete me" --clone
cd $W/$NAME
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'Y'
name: ci
on:
  pull_request:
jobs:
  pass:
    runs-on: ubuntu-latest
    steps:
      - run: "true"
Y
echo "throwaway" > README.md
git add . && git commit -q -m "chore: base with a passing CI check" && git branch -M main
run git push -u origin main
git checkout -q -b feat
mkdir -p docs && echo "notes v1" > docs/notes.md
git add docs/notes.md && git commit -q -m "docs(notes): add notes"
run git push -u origin feat
run gh pr create --repo $REPO --base main --head feat --title "docs(notes): add notes" --body "AC-5 throwaway PR"
HEAD1=$(git rev-parse HEAD)
echo "head1=$HEAD1"
wait_ci() { for i in $(seq 1 40); do out=$(gh pr checks 1 --repo $REPO 2>&1); if echo "$out" | grep -q "pass" && ! echo "$out" | grep -qE "pending|queued|in_progress|fail"; then echo "$out"; return 0; fi; sleep 6; done; echo "$out"; return 1; }
echo; echo "\$ wait for CI on head1"; wait_ci; echo "[exit=$?]"
# workflow dir
mkdir -p $W/wf/task/dispatch
cat > $W/wf/README.md <<'R'
---
commissioned-by: kc-dev-flow-2
extensions: []
trunk: main
merge-grants: [docs-only:rule:0.95:squash:ADR 0023]
---

# throwaway workflow
R
printf -- '---\nprofile: pilot\n---\n\n# task\n' > $W/wf/task.md
: > $W/wf/gate.txt
printf '# validation-1\n\nDispatched: %s\nModel: sonnet\nCandidate: %s\n\n## Checklist\n\n- one\n' "$HEAD1" "$HEAD1" > $W/wf/task/dispatch/validation-1.md
SHORT1=${HEAD1:0:8}
CHECK="python3 $GATE check $W/wf/task.md --pr $REPO#1 --text-file $W/wf/gate.txt --head $SHORT1 --workflow-dir $W/wf"
echo; echo "\$ $CHECK   (retry while GitHub computes mergeability)"
for i in 1 2 3 4 5 6; do OUT=$($CHECK 2>&1); CODE=$?; [ $CODE -eq 0 ] && break; sleep 8; done
echo "$OUT"; echo "[exit=$CODE]"
LINE=$(echo "$OUT" | tail -n 1)
echo; echo "printed line (last line of the passing check):"; echo "$LINE"
CMD1=$(echo "$LINE" | sed -e 's/^next: run //' -e 's/ now; when gh pr view says MERGED.*$//')
echo; echo "== Step A: push a new commit so the PR head differs from the checked head =="
echo "notes v2" > docs/notes.md && git add docs/notes.md && git commit -q -m "docs(notes): change notes"
run git push origin feat
HEAD2=$(git rev-parse HEAD); echo "head2=$HEAD2"
run gh pr view 1 --repo $REPO --json state,headRefOid
sh_run "$CMD1"
echo; echo "PR after running the printed line with a moved head:"; run gh pr view 1 --repo $REPO --json state,headRefOid,mergedAt
echo; echo "== Step B: GitHub's own --match-head-commit refusal (bare gh pr merge pinned to head1) =="
run gh pr merge 1 --repo $REPO --squash --match-head-commit $HEAD1 --subject "docs(notes): add notes" --body ""
run gh pr view 1 --repo $REPO --json state,headRefOid,mergedAt
echo; echo "== Step C: re-validate head2 (Candidate line updated), CI green, check without --head, run the printed line =="
printf '# validation-2\n\nDispatched: %s\nModel: sonnet\nCandidate: %s\n\n## Checklist\n\n- one\n' "$HEAD2" "$HEAD2" > $W/wf/task/dispatch/validation-2.md
echo "\$ wait for CI on head2"; wait_ci; echo "[exit=$?]"
CHECK2="python3 $GATE check $W/wf/task.md --pr $REPO#1 --text-file $W/wf/gate.txt --workflow-dir $W/wf"
echo; echo "\$ $CHECK2"
for i in 1 2 3 4 5 6; do OUT=$($CHECK2 2>&1); CODE=$?; [ $CODE -eq 0 ] && break; sleep 8; done
echo "$OUT"; echo "[exit=$CODE]"
LINE2=$(echo "$OUT" | tail -n 1)
CMD2=$(echo "$LINE2" | sed -e 's/^next: run //' -e 's/ now; when gh pr view says MERGED.*$//')
sh_run "$CMD2"
run gh pr view 1 --repo $REPO --json state,headRefOid,mergedAt,mergeCommit
echo; echo "ask records written in the task folder:"; ls $W/wf/task/merge
echo; echo "repository left in place for the Captain to delete: $REPO"
run gh repo view $REPO --json nameWithOwner,isPrivate,visibility
