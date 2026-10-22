# implementation-1

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); batch 5
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (e66c9b32b2ca080116a2d016334b6b48fac716fd) implementing the narrowed cycle-3 design: kc-dev-flow-2/scripts/delivery_gate.py check runs kc-dev-flow-2/scripts/role_triggers.py on the committed task and holds the merge ask while it reports an owed repair-pass or amendment call (exit 1 adds one problem line plus the script's next: lines; exit 2 holds with its message), with kc-dev-flow-2/scripts/test_delivery_gate.py and the one ADR 0026 Amended paragraph; no review-round count (D2); only those files
Every acceptance criterion green with the evidence each names, each falsifier shown failing by a mutation you run (python3 -B, caches cleared), including the replay over the archived merge asks (fo-batch-sittings holds, no complete ask holds) and the HEAD-versus-disk residual stated in the PR body
kc-dev-flow-2/scripts/lint-skills.py and kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> exit 0; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-22 (narrowing 「可以」, D2 「按建議不算」). The entity title still names the dropped holds; title the PR for hold C only. After this ships, tasks that owe a call today (codex-reader-reads-receipt-marker, new-work-starts-from-a-story-map, agent-reads-governing-adr and others named in Batch overlap) hold at their merge asks until the call or a dated waiver is committed; that is intended. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
