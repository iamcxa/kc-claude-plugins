# implementation-9

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); resumed worker (SendMessage), phase 2 of the Cycle 1 repair: FO fix authorization
Model: sonnet

## Checklist

Apply /tmp/mg-p1/codex-p1-proposal.patch to kc-dev-flow-2/scripts/delivery_gate.py and its tests: a quoted prod profile is read as prod through the shared frontmatter reader; instruction directories match at any depth; the trunk ref is fetched inside check before the revert search, and a failed fetch holds the ask (fail closed)
Each fix's failing-first test passes and its mutation fails it (python3 -B, caches cleared); kc-dev-flow-2/scripts/lint-skills.py exits 0; all package test files pass; roborev evidence= line; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Number guards: ADR: 0023

Profile: prod. Task merge-gatekeeper, PR iamcxa/kc-claude-plugins#666, your existing worktree and branch. FO ruling on (3): fetch inside check, fail closed on error (0.5 s measured), rather than holding on trunk-ref age. Validation-1's F4 (never-eligible path list) stays a Captain decision outside this repair. Commit the state report with `spacedock state commit merge-gatekeeper --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
