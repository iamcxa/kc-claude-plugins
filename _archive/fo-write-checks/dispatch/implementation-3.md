# implementation-3

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (workflow checkout, kc-dev-flow-2 0.25.0 README); resumed worker (SendMessage), phase 2 of the Cycle 1 repair: FO fix authorization
Model: sonnet

## Checklist

Apply both phase-1 fixes: declined_items in kc-dev-flow-2/scripts/delivery_gate.py keeps every non-empty item except 'none', 'nothing' and 'n/a'; the reserved-line match in kc-dev-flow-2/scripts/dispatch_records.py is anchored to a line start with an optional bullet and an optional 'Number guards:' prefix; move the two reproductions into kc-dev-flow-2/scripts/test_delivery_gate.py and kc-dev-flow-2/scripts/test_dispatch_records.py, each failing under its mutation (python3 -B, caches cleared)
Write docs/adr/0025-a-declined-item-carries-a-bracketed-reason-and-a-reserved-adr-lands-or-is-released.md as proposed in phase 1; kc-dev-flow-2/scripts/adr_lint.py passes with --require 0025
Confirm --names over the committed dispatch records still prints the same lines; all package test files pass; roborev evidence= line; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Number guards: ADR: 0025

Profile: pilot. Task fo-write-checks, PR iamcxa/kc-claude-plugins#671, your existing worktree and branch. FO rulings: keep the 'Number guards:' prefix, because a record AC-1 requires to pass writes the reserved line that way; the ADR text is yours as proposed, its Words line quoting the Captain's own words only. Commit the state report with `spacedock state commit fo-write-checks --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
