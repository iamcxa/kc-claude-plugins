# implementation-1

Dispatched: 7a5c79c64249ee15dac1c1da378c60f36dd0ed3e (workflow checkout, kc-dev-flow-2 0.29.0 README); first implementation dispatch
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (7a5c79c64249ee15dac1c1da378c60f36dd0ed3e) implementing the approved design (## Design: The change, file by file) and AC-1 to AC-8, with the Captain's D1 to D3 as recommended: the package README holds the recommended list, copilot is offered unchecked and choosing codex and copilot writes second-reviewer: copilot, the template line becomes extensions: [learn, peers]; only the files the design names
ADR 0035 records the Captain's rulings that learn and peers are required and on by default, the rest recommended (journey-map with release-acceptance as one choice, codex, roborev) and copilot optional, chosen at install through a UI, quoting his words from ## Scope and the gate records
Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.29.0/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.29.0/scripts/adr_lint.py docs/adr --since <base> --require 0035 exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.29.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.29.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.29.0

Number guards: ADR: 0035

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved 2026-10-25 (Captain 「准」, accepting D1 to D3 as recommended). The word-ledger raise step quotes the Captain's words in ## Scope. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.29.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
