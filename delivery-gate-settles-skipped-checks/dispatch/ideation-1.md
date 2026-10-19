# ideation-1

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (workflow checkout, kc-dev-flow-2 0.25.0 README); batch 3, added before release
Model: sonnet

## Checklist

A design (PRFAQ and Mermaid) for how kc-dev-flow-2/scripts/delivery_gate.py check treats a check run that concludes SKIPPED or NEUTRAL, measured on the three observed holds in the task Scope (subspace-relay #398 and #401, subspace-web #150) with `gh pr view --json statusCheckRollup,mergeStateStatus` and each repository's branch protection or rulesets (`gh api`), read-only; compare the three candidate directions in the Scope and recommend one, naming what each would let through that the current hold catches
A falsifier set: the current hold's own tests in kc-dev-flow-2/scripts/test_delivery_gate.py that must keep holding (an empty rollup, a pending or failed required check), and a replay of the recommended rule over the committed merge/ask-N.json records and the three adopter PRs, verdict per case
The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"; a `### Batch overlap` section against chat-only-evidence-observer-blind (PR #679, open, which also edits kc-dev-flow-2/scripts/delivery_gate.py)
Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Profile: pilot. The Captain's words and the evidence are in the task file. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`). Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found; for GitHub's check and branch-protection semantics read GitHub's own documentation or API output, not an adopter's workaround.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Read adopter repositories (spacedock-dev/subspace-relay, spacedock-dev/subspace-web) only through read-only `gh` commands.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
