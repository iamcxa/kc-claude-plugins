# implementation-3

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README)
Model: sonnet
Lane: FO fix under Review-finding disposition step 3; entity stays in validation. Phase 1 investigation only; phase 2 needs FO's fix message (recorded as implementation-4).

## Checklist

Investigation first, with no candidate change: reproduce each of the four assigned items on #627 head 89769eb6 and #628 head d8281e1c, send FO the reproduction result per item (confirmed or not, with the command and output), then wait for FO's fix authorization message
After FO's fix authorization only: fix each item FO authorizes, each with a test that fails without the fix (shown failing by a mutation run); push #627, merge (never rebase) its branch into the -map branch, push #628; CI green on both new heads
Stage report: new heads of both PRs, the roborev_gate.py evidence= line per PR, test and mutation results per item, and anything left for FO

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. This is a repair under the workflow's Review-finding disposition step 3 (FO fix authorization), not a new design. The entity stays in validation; you work as the implementation stage in the existing worktrees. Approved design, D1, D2 and Amendment 1 are unchanged.

Worktrees and PRs (iamcxa/kc-claude-plugins), both already exist; do not create new ones:
- #627: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-journey-map-dev2-contract, branch spacedock-ensign/journey-map-dev2-contract, head 89769eb6, base main.
- #628: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-journey-map-dev2-contract-map, branch spacedock-ensign/journey-map-dev2-contract-map, head d8281e1c, stacked on #627's branch.

The four assigned items (Codex round 1 on the PRs, plus one validation Polish item), as recorded under the task's `### Feedback Cycles`, Cycle 1:
1. P1 #627 `map_footprint.py` (around line 265): a declared state checkout that is missing falls back to the workflow dir, and `audit` reports `unrecorded 0` / `invalid 0` without reading anything. Make it a configuration error.
2. P2 #627 `map_footprint.py` (around line 237): `Map footprints: not needed: <reason>` passes when valid footprints exist. Require zero valid lines for that form.
3. P2 #628 `journey-fold.mjs` (around line 72): a block-style question that is the last node, in a file with no trailing newline, gets `answer:` glued to the last line. Insert a newline at a non-newline EOF.
4. Validation Polish: add a test asserting `journey-reconcile` exits 1 on a duplicate story id.

Phase 1 (now): read-only investigation. Reproduce each item in a throwaway copy or temp directory; do not edit, commit or push either worktree. Send FO one message with, per item: confirmed / not reproduced, the exact command, and the observed output. Then wait. FO replies with a fix authorization naming the items to fix; that message is the only authorization to change the candidate.

Phase 2 (after FO's message): fix only the authorized items. Commit with Conventional Commit subjects scoped to the plugin (`fix(kc-dev-flow-2): ...`, `fix(kc-journey-map): ...`), stage named files only, no version bumps. Before each push, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>` with base 89769eb6 for #627 and d8281e1c for #628. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Push #627 first, then `git merge` #627's branch into the -map branch (never rebase, never force-push) and push #628. Wait for CI on both heads (`gh pr checks`).

Do not comment on the PRs, request reviews, mark them ready, or merge; FO asks Codex for the next round. Keep the comment-ratio rule (5% maximum). If a fix would change an accepted criterion, a schema version or anything beyond the four items, stop and return it to FO as a scope change.
