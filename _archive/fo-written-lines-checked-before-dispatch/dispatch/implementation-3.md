# implementation-3

Dispatched: ac67eb0a56d6f78baa5fb2973f9727cefa3e06b9 (workflow checkout, kc-dev-flow-2 0.30.0 README); resumed worker (SendMessage), phase 2 of the Cycle 1 repair: FO fix authorization
Model: sonnet

## Checklist

Apply the proposed one-line fix in kc-dev-flow-2/scripts/design_surfaces.py exactly (the escaped-quote check runs only on lines that start with Captain: or Asked:), and commit it with your three new tests and the changed moved-criterion fixture in kc-dev-flow-2/scripts/test_design_surfaces.py, kc-dev-flow-2/scripts/test_dispatch_records.py and kc-dev-flow-2/scripts/test_laws_check.py; leave kc-dev-flow-2/scripts/laws_check.py unchanged; name the bounded limit (a second line of a multi-line Asked: value is not checked) in your stage report
Push with `git push origin spacedock-ensign/fo-written-lines-checked-before-dispatch`; if the permission check refuses it, stop and report, and FO pushes under the Captain's 「授權推」 for this PR
All package test files pass; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.30.0

Profile: pilot. Task fo-written-lines-checked-before-dispatch, PR iamcxa/kc-claude-plugins#724, your existing worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-written-lines-checked-before-dispatch` and branch. Commit the state report with `spacedock state commit fo-written-lines-checked-before-dispatch --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.30.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready. If a push or gh call is refused by the permission check, stop and report it.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
