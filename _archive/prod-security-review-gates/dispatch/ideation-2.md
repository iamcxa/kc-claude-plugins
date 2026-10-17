# ideation-2

Dispatched: 1383c9119eb5328543e2c4df5e562be22b74e355 (workflow checkout, kc-dev-flow-2 0.23.0 README); redo under Captain amendment 2
Model: sonnet

## Checklist

Captain amendment 2 applied: AC-1, AC-2, AC-4, AC-5, AC-6 and AC-7 moved under it as `Superseded text:` and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0/scripts/design_surfaces.py check exits 0
A redone `## Design` (PRFAQ and Mermaid) in which every prod task's ideation stage runs a security review while the design is written (kc-pr-flow's tob-security-reviewer or the threat-model brief this task already measured), its findings become design requirements and acceptance criteria, an adopter's own security focus file (for example qnow's `.claude/agents/security-reviewer.md`) is passed in when present, the ideation gate shows the review, and a missing reviewer holds the stage rather than skipping it; say what of the local branch (db8e04bc: extension, README row, observer sentence, ADR 0018 draft) is kept, rewritten or deleted
A replay on relay agent-front-door's design (read only) showing which findings become acceptance criteria, and whether the unbounded comment or session write becomes one
The words FO reads at each lifecycle moment, before and after, and the added cost per prod task measured on the replay
Acceptance criteria written as 'Amended by Captain, amendment 2', with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0

Profile: pilot. Captain amendment 2 is in the task file with his words and the question he answered. The validation-gate review is out of scope (backlog task prod-security-validation-gate). Evidence so far is under `prod-security-review-gates/security/`. ADR: 0018 (reserved). Ideation writes no repository file, branch or commit; the local branch `spacedock-ensign/prod-security-review-gates` is read only. Read relay and qnow only through read-only commands. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
