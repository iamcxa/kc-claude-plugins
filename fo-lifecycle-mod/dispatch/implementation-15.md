# implementation-15

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #643 5e10c355
Model: sonnet
Fresh worker; FO fix lane for the Codex round-7 P1 (directory-form entities); phase 1 investigation only.

## Checklist

Investigation, with no candidate change: reproduce on #643 head 5e10c355 the Codex round-7 P1 (kc-dev-flow-2/scripts/pr_watch.py tasks scans only top-level *.md, so a task stored as <slug>/index.md is never seen; this workflow has two live ones, journey-server-host-pilot and release-acceptance); check how Spacedock itself resolves an entity (flat file or directory index) from its source, and send FO the reproduction and proposed fix (both forms, no duplicate scan when a <slug>/ sidecar folder sits beside <slug>.md), then wait for FO's fix authorization message
After FO's fix authorization only: the fix with tests that fail without it (shown failing by a mutation run), AC-12's recount unchanged or lower, roborev evidence= line, push to #643's branch without force, CI green on the new head, stage report appended

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Repair under the workflow's Review-finding disposition step 3; the task stays in validation and you work as the implementation stage in the existing worktree of PR iamcxa/kc-claude-plugins#643 (fetch and fast-forward to origin's head first). The finding is Codex round 7 (review:5519583959). Captain's push grant for this task (redo ideation gate, 「准」): the implementation worker may push the task branch of the Draft PR. Under Captain amendment 4, fix it in the script with a test, not with prose. Read Spacedock's own source for how it resolves an entity, not an adopter's layout.

Phase 1 (now): read-only; do not change the candidate. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Send FO one message (to `main`) with the reproduction and proposed fix, then wait. FO's reply naming the fix is the only authorization to change the candidate.

Phase 2 (after FO's message): commit `fix(kc-dev-flow-2): ...`, stage named files only. Before pushing, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base $(git merge-base HEAD origin/main)`; on exit 1 fix the findings inside your scope, at most twice, and report the rest. Push (never force), wait for CI. Run each suite and mutation with a time cap. No replays, adopter copies, comments, review requests, ready or merge.

Send your phase-1 report and your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
