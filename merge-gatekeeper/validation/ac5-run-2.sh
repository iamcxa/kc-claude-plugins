#!/bin/bash
set -u
REPO=iamcxa/kc-merge-gate-ac5-throwaway-20261018
NAME=${REPO#*/}
GATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-gatekeeper/kc-dev-flow-2/scripts/delivery_gate.py
W=/tmp/mg-ac5
export GIT_AUTHOR_NAME=ac5 GIT_AUTHOR_EMAIL=ac5@example.invalid GIT_COMMITTER_NAME=ac5 GIT_COMMITTER_EMAIL=ac5@example.invalid
run() { echo; echo "\$ $*"; "$@"; echo "[exit=$?]"; }
sh_run() { echo; echo "\$ $1"; sh -c "$1"; echo "[exit=$?]"; }
cd $W/$NAME
echo "# AC-5 second run with the prose-first merge line, $(date -u +%Y-%m-%dT%H:%M:%SZ); gate script head $(git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-gatekeeper rev-parse HEAD); repository $REPO (left in place)"
git checkout -q main && git pull -q origin main
git checkout -q -b feat2
echo "notes v3" > docs/notes.md
git add docs/notes.md && git commit -q -m "docs(notes): second change"
run git push -u origin feat2
run gh pr create --repo $REPO --base main --head feat2 --title "docs(notes): second change" --body "AC-5 second throwaway PR"
HEAD1=$(git rev-parse HEAD); echo "head1=$HEAD1"
wait_ci() { for i in $(seq 1 40); do out=$(gh pr checks 2 --repo $REPO 2>&1); if echo "$out" | grep -q "pass" && ! echo "$out" | grep -qE "pending|queued|in_progress|fail"; then echo "$out"; return 0; fi; sleep 6; done; echo "$out"; return 1; }
echo; echo "\$ wait for CI on head1"; wait_ci; echo "[exit=$?]"
rm -rf $W/wf2; mkdir -p $W/wf2/task/dispatch
cp $W/wf/README.md $W/wf2/README.md
printf -- '---\nprofile: pilot\n---\n\n# task\n' > $W/wf2/task.md; : > $W/wf2/gate.txt
printf '# validation-1\n\nDispatched: %s\nModel: sonnet\nCandidate: %s\n\n## Checklist\n\n- one\n' "$HEAD1" "$HEAD1" > $W/wf2/task/dispatch/validation-1.md
SHORT1=${HEAD1:0:8}
CHECK="python3 $GATE check $W/wf2/task.md --pr $REPO#2 --text-file $W/wf2/gate.txt --head $SHORT1 --workflow-dir $W/wf2"
echo; echo "\$ $CHECK"
for i in 1 2 3 4 5 6; do OUT=$($CHECK 2>&1); CODE=$?; [ $CODE -eq 0 ] && break; sleep 8; done
echo "$OUT"; echo "[exit=$CODE]"
LINE=$(echo "$OUT" | tail -n 1)
CMD1=${LINE#*ask him: }
echo; echo "command after the prose (the whole text after 'ask him: ', run unmodified):"; echo "$CMD1"
echo; echo "== Step A: push a new commit so the PR head differs from the checked head =="
echo "notes v4" > docs/notes.md && git add docs/notes.md && git commit -q -m "docs(notes): move the head"
run git push origin feat2
HEAD2=$(git rev-parse HEAD); echo "head2=$HEAD2"
run gh pr view 2 --repo $REPO --json state,headRefOid
sh_run "$CMD1"
echo; echo "the re-run inside that command, shown unswallowed:"; sh_run "$CHECK"
run gh pr view 2 --repo $REPO --json state,headRefOid,mergedAt
echo; echo "== Step B: GitHub's own --match-head-commit refusal (bare gh pr merge pinned to head1) =="
run gh pr merge 2 --repo $REPO --squash --match-head-commit $HEAD1 --subject "docs(notes): second change" --body ""
run gh pr view 2 --repo $REPO --json state,headRefOid,mergedAt
echo; echo "== Step C: re-validate head2, CI green, check without --head, run the printed command unmodified =="
printf '# validation-2\n\nDispatched: %s\nModel: sonnet\nCandidate: %s\n\n## Checklist\n\n- one\n' "$HEAD2" "$HEAD2" > $W/wf2/task/dispatch/validation-2.md
echo "\$ wait for CI on head2"; wait_ci; echo "[exit=$?]"
CHECK2="python3 $GATE check $W/wf2/task.md --pr $REPO#2 --text-file $W/wf2/gate.txt --workflow-dir $W/wf2"
echo; echo "\$ $CHECK2"
for i in 1 2 3 4 5 6; do OUT=$($CHECK2 2>&1); CODE=$?; [ $CODE -eq 0 ] && break; sleep 8; done
echo "$OUT"; echo "[exit=$CODE]"
LINE2=$(echo "$OUT" | tail -n 1)
CMD2=${LINE2#*ask him: }
sh_run "$CMD2"
run gh pr view 2 --repo $REPO --json state,headRefOid,mergedAt,mergeCommit
echo; echo "ask records in the task folder:"; ls $W/wf2/task/merge
echo; echo "repository left in place for the Captain to delete: $REPO"
run gh repo view $REPO --json nameWithOwner,isPrivate,visibility
