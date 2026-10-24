# implementation-1

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); first implementation dispatch, with Captain Amendment 1
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (1694ade349babde54f6c9791df77be8c63b48bbb) implementing the approved cycle-2 design (## Design: The walk, Director pass 3 and per-item escalation, Close path, Fixtures, ADRs) and AC-1 to AC-14; only the files the design names, ADRs 0033 and 0034 for its two ADR drafts
Captain Amendment 1 (2026-10-23, ## Captain amendments) and the Captain ruling under ## FO alignment that its point 2 is a second run of the extension on the same release after the fix tasks land (this task still closes per D1): add new criteria with fresh ids marked "Amended by Captain, amendment 1" for (a) record.md rendering one row per reviewer complaint id with the task it went to, its status and reason, (b) a re-walk mode refusing a prior report digest that does not match, a reviewer whose id, model or persona differs from the prior row, and an own prior complaint left unmarked, and accepting new complaints, (c) the re-walk record.md opening with that table; a deferral names its release (a field and a check --tier final refusal when none is named); the complaint-to-task link is one line on the filed task, found by scanning as deferred scans journey-release; leave AC-1 to AC-14 unchanged; if the AC-13 600-word EXTENSION.md cap cannot hold the second mode, stop and return to FO
Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared); the re-walk is tested on fixtures only and listed under ### Not claimed
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/lint-skills.py, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/adr_lint.py docs/adr --since <base> --require 0033 --require 0034 exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0

Number guards: ADR: 0033

Number guards: ADR: 0034

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file, cycle 2; ideation gate approved 2026-10-23 (Captain 「准」, digest 9d4c90c8), with the D1, D2, D3 and D5 rulings under ## FO alignment. Captain Amendment 1 and its ruling were added after the gate; the engineering-reviewer result under ## FO alignment lists the build effects. ADR 0034 was written into ## Number guards by FO because /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/number_guards.py reserve returns one number per kind per task and the design has two ADR drafts. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
