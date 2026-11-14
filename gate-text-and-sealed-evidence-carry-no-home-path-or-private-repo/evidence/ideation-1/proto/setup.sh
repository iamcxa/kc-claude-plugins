#!/bin/bash
# Throwaway: scratch HOME, fresh git init, linked state worktree, invented identifier list, guard installed.
# usage: setup.sh SC OVERLAY_SCRIPTS  (prints nothing private: HOME is a scratch folder)
set -euo pipefail
SC=$1; PKG=$2
export HOME=$SC/home GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=tw GIT_AUTHOR_EMAIL=tw@example.invalid GIT_COMMITTER_NAME=tw GIT_COMMITTER_EMAIL=tw@example.invalid
export KC_DEV2_IDENTIFIERS=$SC/ids.tsv
rm -rf "$HOME"; mkdir -p "$HOME/ws"
printf 'private-repo\tacme-hidden-app\nprivate-slug\tzz-unlisted-task\ntailnet-host\tbox.invented.invalid\n' > "$KC_DEV2_IDENTIFIERS"
git init -q -b main "$HOME/ws/repo"; git -C "$HOME/ws/repo" config user.email tw@example.invalid
git -C "$HOME/ws/repo" commit -q --allow-empty -m init
git -C "$HOME/ws/repo" config extensions.worktreeConfig true
git -C "$HOME/ws/repo" worktree add -q --orphan -b spacedock-state/dev2 "$HOME/ws/state"
git -C "$HOME/ws/state" commit -q --allow-empty -m 'state: init'
git init -q --bare "$HOME/ws/remote.git"; git -C "$HOME/ws/repo" remote add origin "$HOME/ws/remote.git"
git -C "$HOME/ws/state" push -q origin spacedock-state/dev2
python3 -B "$PKG/state_guard.py" install "$HOME/ws/state" --refuse home,private-repo,private-slug,tailnet-host
python3 -B "$PKG/state_guard.py" check "$HOME/ws/state"
