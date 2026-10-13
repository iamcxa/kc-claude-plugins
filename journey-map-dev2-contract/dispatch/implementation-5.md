# implementation-5

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README)
Model: sonnet
Fresh worker (context-budget probe found no transcript for the cycle-2 worker; prior implementation and validation workers sent shutdown_request). FO fix lane, Review-finding disposition step 3, Codex round 2 findings; phase 1 investigation only.

## Checklist

Investigation first, with no candidate change: reproduce each of the four Codex round-2 items on #627 head c811de1f and #628 head f320d6d3, send FO the reproduction result per item (confirmed or not, with the command and output), then wait for FO's fix authorization message
After FO's fix authorization only: fix each item FO authorizes, each with a test that fails without the fix (shown failing by a mutation run); push #627, merge (never rebase) its branch into the -map branch, push #628; CI green on both new heads
Stage report: new heads of both PRs, the roborev_gate.py evidence= line per PR, test and mutation results per item, and anything left for FO

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. This is a repair under the workflow's Review-finding disposition step 3 (FO fix authorization), not a new design. The entity stays in validation; you work as the implementation stage in the existing worktrees. Approved design, D1, D2 and Amendment 1 are unchanged.

Worktrees and PRs (iamcxa/kc-claude-plugins), both already exist; do not create new ones:
- #627: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-journey-map-dev2-contract, branch spacedock-ensign/journey-map-dev2-contract, head c811de1f, base main.
- #628: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-journey-map-dev2-contract-map, branch spacedock-ensign/journey-map-dev2-contract-map, head f320d6d3, stacked on #627's branch.

The four assigned items (Codex review round 2 on the repaired heads), as recorded under the task's `### Feedback Cycles`, Cycle 2. Cycle 1's four fixes are already in both heads.
1. P1 #627 `map_footprint.py` (around line 277): a nonexistent or mistyped workflow directory makes `audit` glob a missing `_archive` and print `unrecorded 0` / `invalid 0`, exit 0. This is the same class as cycle 1's P1: close the class, not this one path. Every command that scans a directory must fail with a configuration error when a path the caller supplied, or the README declares, does not exist. Decide whether a missing `_archive` under an existing workflow is a legitimate zero (a workflow with no archived tasks yet) and state your reasoning in the report.
2. P2 #627 `map_footprint.py` (around line 51): the amendment regex crosses the next `### Amendment` heading when an amendment has no `Captain:` line, giving it the later amendment's words and date and losing the later one. Bound each match to its own amendment section.
3. P1 #628 `journey-fold.mjs` (around line 101): `already` is decided from `source.ref` alone, so an answer reworded after folding is neither restored nor reported as a conflict, and reconcile does not count it in `unfolded`. Require the stored answer and status to match before `already`; otherwise report a conflict (the existing conflict path writes nothing for that question). Say what reconcile counts it as.
4. P2 #628 `journey-fold.mjs` (around line 46): two questions with the same id inside one story fold into the first. Require exactly one match; refuse otherwise, naming the story and question.

Phase 1 (now): read-only investigation. Reproduce each item in a throwaway copy or temp directory; do not edit, commit or push either worktree. Send FO one message with, per item: confirmed / not reproduced, the exact command, and the observed output. Then wait. FO replies with a fix authorization naming the items to fix; that message is the only authorization to change the candidate.

Phase 2 (after FO's message): fix only the authorized items. Commit with Conventional Commit subjects scoped to the plugin (`fix(kc-dev-flow-2): ...`, `fix(kc-journey-map): ...`), stage named files only, no version bumps. Before each push, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>` with base c811de1f for #627 and f320d6d3 for #628. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Push #627 first, then `git merge` #627's branch into the -map branch (never rebase, never force-push) and push #628. Wait for CI on both heads (`gh pr checks`).

Do not comment on the PRs, request reviews, mark them ready, or merge; FO asks Codex for the next round. Keep the comment-ratio rule (5% maximum). If a fix would change an accepted criterion, a schema version or anything beyond the four items, stop and return it to FO as a scope change.

Send your phase-1 report and your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
