# ideation-1

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README)
Model: sonnet

## Checklist

A design (PRFAQ and Mermaid) for making /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/dispatch_records.py fail a follow-up dispatch record that lacks the parts the README Stages rules require: decide whether a follow-up record may point at an earlier record's checklist or must carry it, name each part the check enforces (Package root line, checklist, scope notes, main completion line) and how a follow-up record is told apart from a first dispatch, or why no marker is needed
Acceptance criteria with reproducible evidence clauses and falsifiers, replayed against the three archived records named in the task (each must fail) and against compliant records from the same folder (each must pass), plus the count of currently archived and active records the new check would fail and how that cost is handled
Unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. The Captain's words and the evidence are in the task file. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`); the released package is 0.22.1. Archived task records you may read (read only): /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/ (task files, their dispatch/ folders and observer.md). Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) for an existing mechanism, and say what you found.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
