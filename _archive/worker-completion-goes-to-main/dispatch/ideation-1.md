# ideation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README)
Model: sonnet

## Checklist

A design (PRFAQ and Mermaid) for the kc-dev-flow-2 side of making a dispatched worker send its completion to main, not the unregistered team-lead, without changing Spacedock; upstream spacedock-dev/spacedock #523 and #608 read and their state stated
Acceptance criteria with reproducible evidence clauses and falsifiers, citing the 2026-10-13 evidence on journey-map-dev2-contract (cycle-1 worker tried team-lead; later dispatches with an explicit main line sent to main)
Unresolved decisions for the Captain, each with a recommendation and what gets worse under it, including whether to add this evidence to the upstream issues (an outward-facing comment)

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. The Captain's words and the evidence are in the task file. Fix order ruled by the Captain: 1 workflow-checkout-must-match-trunk-readme, 2 observer-before-merge-guard, 3 worker-completion-goes-to-main; these three are designed in parallel and implemented in that order, so name any file the design expects to share with the other two.

Canonical package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main 9e68eb87 (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>`). The adopter README for this workflow is /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/README.md. Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) for an existing mechanism, and say what you found.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
