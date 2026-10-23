---
title: delivery_gate.py reads a folder task's index.md
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: FO, 2026-10-23, at the release-acceptance merge ask (PR #709). `delivery_gate.py check <task>/index.md` derives the dispatch folder by stripping `.md`, so it looks in `<task>/index/dispatch` and exits 2 ("no latest validation dispatch record"); passing the folder exits 2 ("Is a directory"). FO ran the check through a temporary `<name>.md` copy beside a symlink to the real folder; the record landed in the real `merge/ask-1.json`.
- Outcome: `delivery_gate.py check` accepts a folder task (its `index.md` or the folder) and reads `<task>/dispatch`, with a test.
- Upstream first: none checked yet; check whether other package scripts share the same path derivation before fixing one.
- Non-goals: other scripts' folder support unless they share the helper.

## FO alignment

Alignment: not needed: one script's path handling, observed failure.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
