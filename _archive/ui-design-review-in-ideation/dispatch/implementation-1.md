# implementation-1

Dispatched: 6ea3a4724515b974c34beb16bc3382683b6d45b9 (workflow checkout, kc-dev-flow-2 0.24.0 README); batch 2
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main implementing D1 to D3 as recommended: the packaged brief kc-dev-flow-2/skills/ideation/design-review.md (v2 with the inventory pass), the 14-word pointer in kc-dev-flow-2/skills/ideation/principles.md, and the design_review checks in kc-dev-flow-2/scripts/design_surfaces.py with tests; record the cycle-1 Refresh button miss in the brief's closing sentences; the ADR is the one under ## Number guards, its Words line quoting the Captain; every acceptance criterion in the task file green, each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
No FO-read word added beyond the design; the candidate's own kc-dev-flow-2/scripts/lint-skills.py exits 0; roborev evidence= line; push without force; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-17 in batch 2, accepting each decision as the gate question states. workflow-budget-ratchet has merged (#658): rebase on origin/main; workflow.md stays untouched. prod-security-validation-gate (#659, not merged) does not edit kc-dev-flow-2/scripts/design_surfaces.py. Your ideation prototype is under /tmp/proto; treat it as a draft, not as the candidate.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. Other batch-2 tasks are in flight in other worktrees; change only the files your design lists, and stop and return to FO if the change needs another.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
