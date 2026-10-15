# implementation-1

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README)
Model: sonnet

## Checklist

One Draft PR (fix(kc-dev-flow-2): ...) from a branch off origin/main changing only kc-dev-flow-2/scripts/pr_watch.py and kc-dev-flow-2/scripts/test_pr_watch.py as the approved design gives them (session-keyed default state, working-directory fallback, --state override, old shared file left unread); AC-1 to AC-5 green with each falsifier shown failing by a mutation run, including the two-session overlap test and the committed replay of the 2026-10-14 loss
The words FO reads at each moment shown unchanged (the tasks output byte-identical in the default case), roborev evidence= line, CI green on the PR head, CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-15 accepting D1 and D2 as stated in the gate question. The design records no ADR; none is reserved. If your stage principles require one, stop and return to FO for a number.

Delivery: one pull request in iamcxa/kc-claude-plugins from a branch off origin/main (fetch first; #643 is merged there), in your own worktree. Push and Draft PR under the Captain's standing grant for repositories he owns ("No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar"). Conventional Commit title `fix(kc-dev-flow-2): ...`. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. The other task in flight (pr-watch-state-per-session or delivery-gate-verdict-form) changes no file of yours.

Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge. Stop and return to FO if the change needs a file outside the design's list.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
