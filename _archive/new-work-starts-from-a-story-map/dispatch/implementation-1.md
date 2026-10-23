# implementation-1

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); batch 5
Model: sonnet

## Checklist

Two Draft PRs from branches off origin/main (cebd0ab93c7f9b681d55434cfc99c19b2d9dd8ba, which holds #693 and #694): one in kc-journey-map for Cut 1 items 1 to 5 (release-review.md step 0 and record, interrogation.md arms, classes, rank and cap, ruling form, SKILL.md mode rows, journey-map-question schema 1.0.0 to 1.1.0 with contract-versions.json and CHANGELOG, journey-review.mjs and its test), and one in kc-dev-flow-2 for items 6 to 8 (skills/dev/SKILL.md new-work sentence, kc-dev-flow-2/scripts/pr_watch.py sittings next: line, ADR 0029); only the files Cut 1 names
Every acceptance criterion AC-1 to AC-11 green with the evidence each names, each falsifier shown failing by a mutation you run (python3 -B or node, caches cleared); AC-5 and AC-6 live rehearsals run as the criteria state; the words FO reads measured as AC-7, AC-8 and AC-10 state
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/scripts/lint-skills.py and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/scripts/adr_lint.py docs/adr --since <base> exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/scripts/comment_ratio.py within its maximum; roborev evidence= line per PR; push without force and without -u; CI green on both PR heads; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0

Number guards: ADR: 0029

Profile: pilot. Approved design: `## Design` (Cut 1 items 1 to 8 and the Not-changed list) and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-22 (Captain 「可以」, accepting D5 option (a), the scope added since the backlog gate and the stated AC-8 departure). Captain rulings D1 to D4 are under `## FO alignment`; Amendment 1 is under `## Captain amendments`. ADR 0029 carries D1 and D4's routing ruling with his words as quoted in Cut 1 item 8. If a change needs a file the design does not list, stop and return to FO.

Delivery: two pull requests in iamcxa/kc-claude-plugins, both from the worktree `dispatch build` made for you, on two branches; `git fetch origin` first and base each branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit titles scoped to each plugin (feat(kc-journey-map): ..., feat(kc-dev-flow-2): ...). Open as Draft. Do not bump versions. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>` for each branch. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put each printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
