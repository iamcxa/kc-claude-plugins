# implementation-1

Dispatched: ac67eb0a56d6f78baa5fb2973f9727cefa3e06b9 (workflow checkout, kc-dev-flow-2 0.30.0 README); batch 6, first implementation dispatch
Model: sonnet

## Checklist

One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (ac67eb0a56d6f78baa5fb2973f9727cefa3e06b9) implementing the approved design and acceptance criteria in the task file; with the Captain's decisions as recommended: D1 after a chief-engineer call any new review round owes a fresh call (no file-path surface), D2 the merge ask keeps not counting review rounds; only the files the design names
Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.30.0/scripts/adr_lint.py docs/adr --since <base> exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.30.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.30.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.30.0

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved 2026-10-25 (Captain 「全准」, batch 6, accepting the decisions as recommended). If a word-budget raise step is needed, quote the Captain's words from that gate record. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Open as Draft. Do not bump versions. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.30.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
