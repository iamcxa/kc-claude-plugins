# implementation-4

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #632 d127ec71
Model: sonnet
Fresh worker (prior implementation and validation workers sent shutdown_request). FO fix lane for the Codex round-2 P1 and P2; phase 1 investigation only.

## Checklist

Investigation first, with no candidate change: reproduce both Codex round-2 findings on #632 head d127ec71 (the documented observer_check.py invocation is bare while the file is mode 100644; the exit-1 recovery command does not quote the state path), sweep every `<package>/scripts/*.py` instruction in the files this PR already changes for the same bare-invocation defect, send FO the result and your proposed fix, then wait for FO's fix authorization message
After FO's fix authorization only: fix them with tests that fail without the fix (shown failing by a mutation run), including a test that runs the documented invocation as text rather than through sys.executable; push to #632's branch; CI green on the new head
Stage report: new head, the roborev_gate.py evidence= line, test and mutation results, and anything left for FO

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Repair under the workflow's Review-finding disposition step 3; the task stays in validation and you work as the implementation stage in the existing worktree. Approved design, D2 and D3 unchanged.

Worktree and PR: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-observer-before-merge-guard, branch spacedock-ensign/observer-before-merge-guard, PR iamcxa/kc-claude-plugins#632, head d127ec71 (includes #631's head 20c9ec53), base #631's branch. Bring the local worktree to origin's head first (`git merge --ff-only origin/spacedock-ensign/observer-before-merge-guard`). Do not create a new worktree. #633 is stacked on this branch; do not touch it.

The findings (Codex round 2, review:5500805789, under the task's `### Feedback Cycles`, Cycle 2):
1. P1 `extensions/learn/EXTENSION.md` around line 13: the documented `observer_check.py` invocation is bare while the file is mode 100644, so it exits 126; the same bare form is in `references/sd/workflow.md` and `skills/dev/SKILL.md`; the tests launch it through `sys.executable` and hide this. #631 fixed the same class for `workflow_checkout.py` with `test_every_instruction_runs_the_script_through_python3_unless_it_is_executable` in `scripts/test_workflow_checkout.py`; follow that pattern. Close the class within the files this PR already changes, including any other `<package>/scripts/*.py` named bare there (the validator of #631 reports `learning.py` bare in `skills/dev/SKILL.md` near line 23). Files the PR does not change are out of scope (FO filed `references/sd/adoption.md` separately).
2. P2 `scripts/observer_check.py` around line 72: quote the state path in the exit-1 recovery command with `shlex.quote`, tested with a whitespace-containing base.

Phase 1 (now): read-only investigation; do not edit, commit or push the worktree. Never run `git remote set-url` or any `git config` write in a worktree of this repository (shared config, including the Captain's main checkout); use a throwaway `git clone`. Send FO one message (to `main`) with the reproduction and proposed fix, then wait. FO's reply naming the fix is the only authorization to change the candidate.

Phase 2 (after FO's message): commit `fix(kc-dev-flow-2): ...`, stage named files only. Before pushing, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base d127ec71`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest. Put the `evidence=` or `incomplete:` line in the stage report. Push (never force), wait for CI (`gh pr checks 632 --repo iamcxa/kc-claude-plugins`).

Do not comment on the PR, request reviews, mark ready or merge. A file the PR does not already change is a scope change: stop and return it to FO.

Send your phase-1 report and your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
