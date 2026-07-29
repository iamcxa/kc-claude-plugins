---
title: Fix split-root audit links in the ship-flow workflow mod
status: backlog
source: Fresh Claude EM validation of w1, 2026-07-29
started:
completed:
verdict:
worktree:
issue:
pr:
design:
lane:
id: n8m5j28bgyxhmntx0tzg188g
---

`docs/ship-flow/README.md` declares a live split-root workflow, but
`docs/ship-flow/_mods/pr-merge.md` still builds PR audit links from the code
worktree's short SHA and repo-relative entity path. Those links cannot reach
entities stored at the root of `spacedock-state/ship-flow`.

Treat the completed `w1` contract as evidence and precedent, not as permission
to copy blindly. Re-resolve the live ship-flow mod and state layout, then decide
the smallest parity repair with its own RED/GREEN evidence. Keep this separate
from `w1`; do not widen the existing PR.
