# implementation-2

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); resumed worker (SendMessage), phase 2 for PR 1 (kc-journey-map) on chief-engineer advice
Model: sonnet

## Checklist

Build PR 1 only, feat(kc-journey-map): AC-5 (journey-walk.mjs prints release-walk/v1), AC-9 (journey-accept.mjs turns a report into map proposals only), AC-10 (the acceptance task cannot become a journey orphan), the accept-release mode doc, release-walk registered in kc-journey-map/lib/schemas.mjs and contract-versions.json by the ADR 0012 mechanism, and ADR 0031 in this PR; one Draft PR from a branch off origin/main (c3514876339cb732d0bea8b2d2dd45c234bcdeaf); only kc-journey-map files and docs/adr/0031
Every one of AC-5, AC-9 and AC-10 green with the evidence each names, each falsifier shown failing by a mutation you run; the full kc-journey-map lib/*.test.mjs suite and journey-dev2-loop-smoke.sh pass
Do not build the kc-dev-flow-2 half (AC-1 to AC-4 wait on the Captain's D2 reading; AC-6 to AC-8, AC-11, AC-12 and Amendment 1 wait on PR 2 after #708); in the stage report answer item 16a (who writes each finding's class and owners) and item 16b (how a report-only task reaches done under merge: pr), so PR 2 can be written
roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0

Number guards: ADR: 0031

Profile: pilot. Approved design: ## Design and ## Acceptance criteria (ideation gate approved 2026-10-22, decision d-51p8nj); Captain decision 7 approved two PRs in either order. Your phase-1 report and the chief-engineer advice (Reviewer line under ## FO alignment, 2026-10-23) set this step: the kc-journey-map half held on main, so it is built now against current main. If a change needs a file outside kc-journey-map/ and docs/adr/0031, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in your existing worktree; `git fetch origin` first and base the branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
