# ideation-1

Dispatched: 19fe3b5b3d34d54908d288860909d10db1ae9226 (workflow checkout, kc-dev-flow-2 0.24.0 README); batch 2
Model: opus

## Checklist

A design (PRFAQ and Mermaid) for a gatekeeper that judges whether a PR can merge, lets FO merge one above a calibrated bar on the Captain's behalf, and lists what he should look at: first the bite counted from state and PR history (FO merge accidents, Captain review per PR); deterministic checks first (head equals the validated candidate, required CI); the model or product (OpenAI Decisions API beta, Codex, TypeSafe Jev, kc-pr-flow kc-pr-review) and how its bar is calibrated; an ADR draft with no number superseding ADR 0011's never-delegated merge clause; and data sent outside per repository. This is a Production task: run the prod profile's design security review
A `### Batch overlap` section naming each file the design would change and each other batch-2 task (workflow-budget-ratchet, special-role-triggers, worker-loads-declared-package, prod-security-validation-gate, ui-design-review-in-ideation, merge-gatekeeper) that changes the same file or check, so FO can order implementation
The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: prod. The Captain's words and the evidence are in the task file. This task is one of batch 2, six ideations run in parallel; read the other five task files only as they stand, and do not edit them. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main, released as 0.24.0 (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`). Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Read adopter state (relay, qnow, ss-web) only through read-only commands.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
