#!/bin/bash
# usage: setup.sh <run-name> <control|mod>  -- builds /tmp/replay-c2/<run-name>/{origin.git,relay}; touches nothing outside /tmp/replay-c2
set -euo pipefail
RUN=$1; ARM=$2; R=/tmp/replay-c2/$RUN; REAL=/Users/kent/conductor/repos/subspace-relay
CAND=/tmp/val-643b; BASE=0cdb40a7; HEAD=d6a427aa
rm -rf "$R"; mkdir -p "$R"
git init -q --bare "$R/origin.git"
git -C "$R/origin.git" fetch -q "$REAL" 54a4e096a86b74f59257bea48552e568cc7b6d24:refs/heads/main 395edbd5bb7a497d1bb3739a55da2cb671556883:refs/heads/spacedock-state/dev2 79ef8e75601e259379ba8177d60657104223cc90:refs/heads/spacedock-ensign/owner-sees-all-feedback-room
git -C "$R/origin.git" symbolic-ref HEAD refs/heads/main
git clone -q --no-hardlinks "$R/origin.git" "$R/relay"
cd "$R/relay"
git config user.name "Replay Fixture"; git config user.email "fixture@example.invalid"; git config commit.gpgsign false; git config core.hooksPath /dev/null
git worktree add -q --detach docs/dev2/.spacedock-state origin/spacedock-state/dev2
git -C docs/dev2/.spacedock-state checkout -q -B spacedock-state/dev2 origin/spacedock-state/dev2
git -C docs/dev2/.spacedock-state branch -q --set-upstream-to=origin/spacedock-state/dev2
git worktree add -q -b spacedock-ensign/owner-sees-all-feedback-room .worktrees/spacedock-ensign-owner-sees-all-feedback-room origin/spacedock-ensign/owner-sees-all-feedback-room
git branch -q --set-upstream-to=origin/spacedock-ensign/owner-sees-all-feedback-room spacedock-ensign/owner-sees-all-feedback-room 2>/dev/null || true
printf 'docs/dev2/.spacedock-state/\ndocs/dev2-poc/.spacedock-state/\n' >> .git/info/exclude
if [ "$ARM" = mod ]; then
  git -C "$CAND" diff $BASE $HEAD -- kc-dev-flow-2/references/sd/workflow.md > /tmp/replay-c2/workflow.patch
  patch -p3 --no-backup-if-mismatch docs/dev2/README.md < /tmp/replay-c2/workflow.patch
  cp "$CAND"/kc-dev-flow-2/references/sd/mods/*.md docs/dev2/_mods/
  git add docs/dev2/README.md docs/dev2/_mods/observe-merged.md docs/dev2/_mods/watch-and-learn.md
  git commit -q -m "fixture: README with R1 to R3 and the two mods at $HEAD"
  git push -q origin main
fi
git status --short | head
