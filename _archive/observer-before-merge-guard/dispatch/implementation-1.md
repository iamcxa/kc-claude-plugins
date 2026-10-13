# implementation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); code base #631 head 085e28aa (stacked)
Model: sonnet

## Checklist

One Draft PR (fix(kc-dev-flow-2): ...) stacked on #631 (branch off spacedock-ensign/workflow-checkout-must-match-trunk-readme at 085e28aa) adding scripts/observer_check.py, test_observer_check.py and test_observer_recovery.py and the text edits the design names (learn EXTENSION.md, workflow.md delivery and done paragraphs, skills/dev/SKILL.md, skills/observer/SKILL.md Read step 1, package README learn row, tests-workflow steps); AC-1 to AC-9 green with each falsifier shown failing by a mutation run, AC-5 included (Decision 3 accepted)
AC-8 run against the pinned Spacedock in CI (after Install pinned Spacedock, SPACEDOCK_BIN set), and AC-1 also run once by you against the real dev2 state branch at 9157341d and 6b435c6a
roborev_gate.py evidence= line, CI green on the PR head, lint-skills.py green (raise WORKFLOW_WORD_BUDGET from #631's 5369 only by the words this task adds, saying why), and the CI cost per PR measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-13 accepting D2 (late report saved by a path-scoped git commit into `_archive/<slug>/`, then `spacedock state commit`) and D3 (a one-line `observer not run: <reason>` observer.md, so AC-5 stays). D1 (a user-level guard on the Captain's machine) is excluded: do not build any hook. The design records no ADR; none is reserved. If your stage principles require one, stop and return to FO for a number.

Stacking: fix order is workflow-checkout-must-match-trunk-readme (PR #631, Draft, head 085e28aa, not merged), then this task, then worker-completion-goes-to-main. Branch off `origin/spacedock-ensign/workflow-checkout-must-match-trunk-readme` at 085e28aa and open your PR with that branch as its base, so the shared `references/sd/workflow.md`, `skills/dev/SKILL.md` and `lint-skills.py` edits sit on top of #631's. After #631 squash-merges, FO retargets yours to main and merges main back in (never rebase).

Delivery: one pull request in iamcxa/kc-claude-plugins, in your own worktree. Conventional Commit title `fix(kc-dev-flow-2): ...`. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. Reading the dev2 state branch for AC-1 is read only: `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state` with `--rev`; never commit there.

Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base 085e28aa`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Do not request reviews, comment on any PR or issue, mark ready or merge. Stop and return to FO if the change needs a file outside the design's list.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
