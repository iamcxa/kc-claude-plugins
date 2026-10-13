# ideation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README)
Model: sonnet

## Checklist

A design (PRFAQ and Mermaid) for a script that checks the FO-written records the observer found wrong on 2026-10-13, extending the dispatch_records.py pattern: for each candidate in the task's Scope, keep it (with the exact record and rule it checks) or drop it with a reason, including whether the Applied: none wording gap needs a README sentence instead
Acceptance criteria with reproducible evidence clauses and falsifiers, each kept check replayed against the archived records that showed the violation (named in the task) and against a record that complies
Unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. The Captain's words and the evidence are in the task file. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`); the released package is 0.22.0. Archived task records you may read (read only): /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/ (task files, their dispatch/ folders and observer.md). Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) for an existing mechanism, and say what you found. The two tasks learn-delivery-follow-through and fo-record-checks are designed in parallel; name any file you expect both to change.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
