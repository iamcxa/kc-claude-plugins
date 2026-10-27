# implementation-1

Dispatched: a11707d5ec19ee34777c7bdeac4c4d100bc84857 (workflow checkout, kc-dev-flow-2 0.31.0 README); batch 7, first implementation dispatch
Model: gpt-6.1-sol (Codex via Paseo, thinking high)

## Checklist

One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (c70f1b22cb1e4a66fd15c617647c778d54c59ec9) implementing the approved design and acceptance criteria in the task file; the revised peers text in kc-dev-flow-2/extensions/peers/EXTENSION.md, the new kc-dev-flow-2/extensions/paseo/EXTENSION.md, and the README, adoption and lint changes the design names, without the structured Captain-source check (Captain Amendment 1 supersedes AC-4 and the active-task migration clause of AC-5), and ADR 0038; if worker-knows-the-team-and-asks-early's PR merges first, rebase on it and recount; only the files the design names
ADR 0038 records the ruling the design names, quoting the Captain's words from the task file and its gate records
Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0/scripts/adr_lint.py docs/adr --since <base> --require 0038 exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; PR body written for FO; FO reads CI on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0

Number guards: ADR: 0038

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved 2026-10-27 (Captain 「全准」, batch 7, accepting the decisions as recommended; see the task's gate records and any ## Captain amendments). If a word-budget raise step is needed, quote the Captain's words from that gate record. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push the branch without force and without -u under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Your sandbox may not reach the GitHub API: do not run gh; write the PR title (Conventional Commit, scoped to the plugin) on the first line and the body after it to /tmp/impl-peers-rules-name-each-host-binding-pr.md, and FO opens the Draft PR and reads its CI. Do not bump versions. Stage named files only, no empty commits. If a push is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
