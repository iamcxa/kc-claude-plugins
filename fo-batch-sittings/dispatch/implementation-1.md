# implementation-1

Dispatched: ad44f0cbf42274ff65802cabc52ebe919f159fd5 (workflow checkout, kc-dev-flow-2 0.26.0 README); batch 4
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (ad44f0cbf42274ff65802cabc52ebe919f159fd5) implementing Cut 1 as the Captain ruled at the ideation gate and in Amendments 1 to 3: item 1 (the sitting line in kc-dev-flow-2/scripts/pr_watch.py tasks, with its tests), item 3 (the one sentence in kc-dev-flow-2/skills/ideation/principles.md), and item 4 (docs/adr/0028 whose ruling drops the recording-burst clause and whose Consequences record the reservation ruling of D3); no kc-dev-flow-2/scripts/decision_ledger.py --sittings (Amendment 1), no Cut 2 (Amendment 2), no interim rule from D4 (Amendment 3)
Every acceptance criterion still declared in the task file (AC-3, AC-4 and AC-7 are superseded with no replacement) green with the evidence each names, each falsifier shown failing by a mutation you run (python3 -B, caches cleared); AC-8 is a seam FO checks at the story-map design gate, not here
kc-dev-flow-2/scripts/lint-skills.py exits 0; kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> --require 28 exits 0; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0

Number guards: ADR: 0028

Profile: pilot. Approved design: `## Design`, `## Acceptance criteria` and `## Captain amendments` in the task file; ideation gate approved 2026-10-20 (D1 「好」, D2 「好，那就下一版，跟故事地圖一起」, D3 「好」, D4 「按建議」 and 「先不放，直到有方式可以找到“重複出現的同類發現”」). The ADR's Words line quotes those replies verbatim. If a change needs a file the design does not list, stop and return to FO. Open PRs: #685 and #686 touch kc-dev-flow-2/references/sd/workflow.md, and #687 touches kc-dev-flow-2/scripts/delivery_gate.py, kc-dev-flow-2/scripts/design_surfaces.py, kc-dev-flow-2/skills/validation/principles.md and adds docs/adr/0027; this task touches none of those files.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository (`git push -u` writes one): worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
