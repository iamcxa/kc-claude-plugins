# ideation-1

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (workflow checkout, kc-dev-flow-2 0.25.0 README); batch 3, added before release
Model: sonnet

## Checklist

A design (PRFAQ and Mermaid) for when FO owes a chief-engineer or engineering-reviewer call, built on counts read from structured records, per the Captain's direction in Scope: candidate counts such as review findings per file or sentence across rounds (from PR review comments and their paths), validation REJECTED verdicts, Feedback Cycles or stage-report cycle headings, Captain overrides and holds, amendments that supersede accepted criteria, and a design or amendment that names an earlier Captain gate it reverses; for each, which role it calls and why
Measure every candidate count over the four repositories' committed records (kc-claude-plugins, subspace-relay, subspace-web and qnow; paths and the per-repository findings in fo-batch-sittings/dogfood/), read-only: per task, the count, the threshold that would have fired, and whether a call was then made or judged owed; report false fires and misses for each threshold, and the expected calls per task (cost in Opus calls)
Name which existing kc-dev-flow-2/scripts/role_triggers.py events and README `Reviewer:` rules the design keeps, changes or drops, and fix its observed blind spots (stage-report cycle headings, a level-2 Feedback Cycles heading, a call worded "third repair cycle"); a `### Batch overlap` section against delivery-gate-settles-skipped-checks; the words FO reads at each lifecycle moment, before and after, per root learning.md
Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Profile: pilot. The Captain's words and the evidence are in the task file; his direction is to avoid keyword triggers. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`), including the chief-engineer and engineering-reviewer agent files. Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found. State checkouts, read-only: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state, /Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state, /Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2/.spacedock-state, /Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2/.spacedock-state; PR review comments through read-only `gh api`.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
