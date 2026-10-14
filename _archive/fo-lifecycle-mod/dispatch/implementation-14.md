# implementation-14

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #643 eb643a18
Model: sonnet
Narrowing under Captain amendment 6 after FO stopped the repair loop (Cycle 6).

## Checklist

Captain amendment 6 applied on #643 (head eb643a18): kc-dev-flow-2/scripts/pr_watch.py stops printing any merge-ask (delivery_gate) line or reviewer hold line; tasks and wait report facts only (state, draft, checks, reviewer outcomes with their review id) plus the kept steps (record a PR, keep one wait, observer before the sentinel, learn after the archive, mark ready on a green or settled-unchecked draft); remove the code and tests that only served the removed lines, and keep or adapt the tests for the kept behaviour, including the no-CI settle
Restore in kc-dev-flow-2/references/sd/workflow.md the FO rule that before the merge-ask gate prepare FO runs /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/delivery_gate.py check with its exit handling, in at most the words amendment 6 allows (about 30 to 50), and set WORKFLOW_WORD_BUDGET to the new count with its reason line; AC-9's grep and AC-11 are amended by amendment 6's Design line, so say in the report which assertions changed
Mutations for the kept behaviour each shown red; AC-12 recount with the merge-ask row recounted from the shipped text; roborev evidence= line; push without force; CI green; stage report appended

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Captain amendment 6 in the task file narrows the approved design: the script reports facts and keeps the steps validation showed working; the merge-ask decision returns to FO under the README with /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/delivery_gate.py. The open Codex round-6 P1 (reviewer applicability) is resolved by removing the merge-ask judgement, not by adding applicability logic. Captain's push grant for this task (redo ideation gate, 「准」): the implementation worker may push the task branch of the Draft PR.

Work in the existing worktree of PR iamcxa/kc-claude-plugins#643 (fetch and fast-forward to origin's head first). Commit `fix(kc-dev-flow-2): ...` (named files only). Before pushing, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base $(git merge-base HEAD origin/main)`; on exit 1 fix the findings inside your scope, at most twice, and report the rest. Push (never force), wait for CI. Run each test suite and mutation with a time cap. Never run `git remote set-url` or any `git config` write in a worktree of this repository. No replays, adopter copies, comments, review requests, ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
