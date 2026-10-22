# implementation-1

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); batch 5 addition
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (126efaf06b4d3f06c29d6b071189ed7771c41ee9) implementing the approved cycle-3 design: the kc-dev-flow-2:design-director agent and skill (sonnet), pass 1a and 1b at ideation, pass 2 and 2b at validation, the design surfaces checker changes (upheld declines, decision lines grouped by kind and owner, each Preview: path, the built-screen refusal with a non-preview screenshot or a quoted waiver), the workflow.md sentence and clause (+15 words, 5374 to 5389) with the kc-dev-flow-2/scripts/lint-skills.py budget step carrying the Captain's quoted words, the new ADR 0030 and a one-line pointer in ADR 0022; only the files the design names
Every acceptance criterion AC-1 to AC-13 green with the evidence each names, each falsifier shown failing by a mutation you run (python3 -B, caches cleared); the AC-7 replay of the shipped agent on the kc-paseo-plugins tasks in the replay folder; the words FO reads measured as AC-8 states
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/lint-skills.py and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/adr_lint.py docs/adr --since <base> --require 0030 exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0

Number guards: ADR: 0030

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file, cycle 3; ideation gate approved 2026-10-22 (Captain 「可以」, accepting D-7 as designed and the +15-word workflow.md raise, 5374 to 5389). Captain Amendment 1, the backlog gate resolution and rulings D-1 to D-6 and the design-guide ruling are under `## Captain amendments` and `## FO alignment`. The budget step's captain value is his 「可以」 to the ideation gate question that named the raise (recorded in the gate resolution). If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
