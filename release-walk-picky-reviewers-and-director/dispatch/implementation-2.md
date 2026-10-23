# implementation-2

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); resumed worker (SendMessage), Captain Amendment 2
Model: sonnet

## Checklist

Move AC-8 and AC-14 under `Superseded text:` in Captain Amendment 2 per ADR 0005 (no replacement for the per-item conditions); add one criterion with a fresh id marked "Amended by Captain, amendment 2": the design director runs on one model per walk, opus when any task the walk covers was designed on opus (its ideation dispatch record says `Model: opus`), otherwise sonnet, printed by the script, with a falsifier; leave every other criterion unchanged
On PR #714: remove the per-item escalation (the `escalate` subcommand and its `Items:` line, the `model`, `escalated_for` and `sonnet_ruling` fields, their checks, tests and fixtures, the escalation text in EXTENSION.md and design-director pass 3), add the one-model-per-walk rule, rewrite ADR 0033's ruling and consequences to match (the measured AC-8 tokens stay as the reason), and keep the ac8/ evidence folder in the task as the record
All remaining tests and mutations green; repository lint-skills.py and skill-frontmatter-lint.sh exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/adr_lint.py docs/adr --since <base> --require 0033 --require 0034 exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; CI green on the PR head; append the stage report and commit it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0

Number guards: ADR: 0033

Number guards: ADR: 0034

Profile: pilot. Task release-walk-picky-reviewers-and-director, PR iamcxa/kc-claude-plugins#714, your existing worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-picky-reviewers-and-director` and branch. Captain Amendment 2 (2026-10-23) is under ## Captain amendments in the task file; the chief-engineer result under ## FO alignment explains why per-item escalation saved nothing. If removing the escalation needs a file the design does not list, stop and return to FO. Commit the state report with `spacedock state commit release-walk-picky-reviewers-and-director --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge. If a push or gh call is refused by the permission check, stop and report it.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
