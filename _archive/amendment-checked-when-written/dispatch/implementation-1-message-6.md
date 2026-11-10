# implementation-1-message-6

Dispatched: 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1 (workflow checkout, kc-dev-flow-2 0.37.0 README); batch 20, follow-up message to the implementation-1 worker (Paseo 31c50fc3), phase 2 of the Cycle 2 repair: FO fix authorization for F3
Symptom: none
Model: gpt-6.1-sol (Codex via Paseo, thinking xhigh; the same worker as implementation-1)

## Checklist

Phase 2 of the Cycle 2 repair, FO fix authorization for finding F3: apply the change your phase-1 report proposes (the live-declaration filtering inside the L4-only move_defects, so a tilde-fenced example cannot supply the marker) in kc-dev-flow-2/scripts/design_surfaces.py only; the shared unfenced, unmarked, amendment parser and the public check and seed functions stay byte-unchanged
Promote the F3 regression and its controls into kc-dev-flow-2/scripts/test_laws_check.py; show the F3 test failing with the fix reverted (python3 -B, caches cleared)
Re-run at the new candidate: all package test files, the existing mutation controls, the check and seed comparison, and the corpus replay with all seven named events unchanged; F2 is not part of this repair
One local commit on the existing branch, no push and no PR write; update the PR text file /tmp/impl-amendment-checked-when-written-pr.md if its claims change; FO pushes and runs RoboRev
Append one complete `## Stage Report: implementation` naming the new candidate SHA, every item followed by its own indented evidence line, evidence kept in the task folder in the state checkout

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0

Start in the assigned worktree; verify pwd and git root before edits.

Everything in implementation-1 stands. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: amendment-checked-when-written completed implementation
