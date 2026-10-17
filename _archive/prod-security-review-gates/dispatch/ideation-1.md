# ideation-1

Dispatched: 1383c9119eb5328543e2c4df5e562be22b74e355 (workflow checkout, kc-dev-flow-2 0.23.0 README); batch 1
Model: sonnet

## Checklist

A design (PRFAQ and Mermaid) for which gates of a prod-profile task carry a security reviewer and what each reviews (the seed suggests a threat model at ideation and the diff plus the served artifact at validation), after the upstream check of kc-pr-flow's tob-security-reviewer, tob-actions-auditor and tob-supply-chain-checker and how kc-pr-review dispatches them; the cost per task; what happens to relay's local 'specialists are risk-selected' policy; a replay on relay task agent-front-door (read only)
A `### Batch overlap` section naming each file the design would change and each other batch-1 task (prod-security-review-gates, dev2-laws-check, extension-instruction-reaches-dispatch, names-check-before-dispatch, amendment-form-check) that changes the same file or check, so FO can order implementation
The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0

Profile: pilot. The Captain's words and the evidence are in the task file. This task is one of batch 1, five ideations run in parallel; read the other four task files only as they stand, and do not edit them. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main, released as 0.23.0 (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`). Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Read adopter state (relay, qnow, ss-web) only through read-only commands.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
