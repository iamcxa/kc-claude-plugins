# implementation-13

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #643 bbc4a20e
Model: sonnet
Fresh worker replacing the stalled implementation-12 worker (Dispatch Retries there), with the recovery clause.

## Checklist

Recovery first: the previous worker stalled mid phase 2 and left uncommitted edits to kc-dev-flow-2/scripts/pr_watch.py and kc-dev-flow-2/scripts/test_pr_watch.py in the task worktree (76 insertions, 27 deletions against bbc4a20e); run git status and git diff, keep what matches the authorization below and redo or discard the rest
The FO-authorized round-5 fix (implementation-12 in the task's dispatch folder): the merge-ask line only when every listed reviewer passes on the head; a findings outcome prints the review-step line naming the review id; Copilot answered is always the review-step line, only not-run and an absent reader pass; running, not-reviewed, requested and error keep the hold line; the seen-based release and its parameters removed; the four changed and four new tests; the seven mutations each shown red; AC-12 recount at or under the design column
Commit with named files only, the roborev gate, push to #643's branch without force, CI green on the new head, stage report appended

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Repair under the workflow's Review-finding disposition step 3; the task stays in validation and you work as the implementation stage in the existing worktree of PR iamcxa/kc-claude-plugins#643. The finding is recorded under the task's `### Feedback Cycles`, Cycle 5, and the authorization is the record `fo-lifecycle-mod/dispatch/implementation-12.md` in the state checkout; read both. Captain's push grant for this task (redo ideation gate, 「准」): the implementation worker may push the task branch of the Draft PR.

The prior ensign was shut down because it stalled. Its worktree holds uncommitted changes: run `git status` and `git diff` first; commit legitimate work or reset broken changes.

Commit `fix(kc-dev-flow-2): ...`, stage named files only. Before pushing, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base $(git merge-base HEAD origin/main)`; on exit 1 fix the findings inside your scope, at most twice, and report the rest. Push (never force), wait for CI. Run each mutation with a time cap. Never run `git remote set-url` or any `git config` write in a worktree of this repository. No replays, adopter copies, comments, review requests, ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
