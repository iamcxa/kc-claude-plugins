---
id: w1py17w13ga14nd3k6sbp358
title: pr-merge builds a dead audit link under split-root state
status: ideation
source: found by the FO while assembling xn's PR draft, 2026-07-25
started: 2026-07-29T06:07:23Z
completed:
verdict:
worktree:
issue:
pr:
design:
lane: main
---

## Problem

`_mods/pr-merge.md`'s audit-link extraction rule formats the link as
`[{short-id}](/{owner}/{repo}/blob/{short-sha}/{path-to-entity-file})`, where `short-sha` comes
from `git rev-parse --short HEAD` in the code worktree. That assumes the entity file lives in
the code repo at a path reachable from the code branch — true for single-root workflows, false
for this one.

This workflow is split-root (`state: .spacedock-state`). Verified on xn's branch:
`git ls-tree -r HEAD -- docs/dev` lists only `README.md`, `_mods/`, and `ledger.csv` — the
entity files are not on the code branch at all. They live at the ROOT of the `spacedock-state/dev`
branch. So the templated link 404s.

The FO worked around it by hand for xn (pointing at a `spacedock-state/dev` commit SHA plus the
branch-root filename), but every future PR from a split-root workflow will hit the same thing.
Whatever the fix is, note that using the branch NAME is ambiguous to GitHub because it contains
a slash (`spacedock-state/dev`); a commit SHA avoids that.
