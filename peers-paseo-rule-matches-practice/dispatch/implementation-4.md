# implementation-4

Dispatched: a6612948936a4f075625147b21aabd3b10b19eee (workflow checkout, kc-dev-flow-2 0.33.1 README); batch 11, first implementation dispatch
Model: gpt-6.1-sol (Codex via Paseo, thinking high; FO builds this dispatch and spawns it in one shell command through paseo agent run --new-workspace local --cwd <worktree>, the generated prompt unchanged; the Captain's interim dispatch directive, chat 2026-10-26: 「接下來派工結束後新的派工盡量用 sol / astra，推理等級可以比 claude 高一級」)

## Checklist

One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (a6612948936a4f075625147b21aabd3b10b19eee) implementing the approved design and acceptance criteria in the task file; Captain amendment 2 in the task file: move superseded AC-7 and AC-8 into its entry and write replacements under fresh ids as the Captain amendments rule says, keeping every duty they carry other than the flag on notices; change the peers Paseo binding so peer asks and information-only notices set notifyOnFinish true and requested replies set it false, and a finish callback on a notice needs no action; the sentence on failed quiet messages now applies to replies only; update ADR 0046 and the PR text to match; one follow-up commit on the existing branch of PR #754, same files; the real evidence is real-pair/README.md and the rerun stays with FO; only the files the design names
ADR 0046 records the ruling the design names, quoting the Captain's words from the task file and its gate records
Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/scripts/adr_lint.py docs/adr --since <base> --require 0046 exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/scripts/comment_ratio.py within its maximum; roborev evidence= line; commit locally, no push; PR text written for FO; FO pushes, opens the Draft PR, runs RoboRev and reads CI; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1

Number guards: ADR: 0046

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved; the Captain's words are in the task's ideation gate record (read them there; this line does not restate them) and any ## Captain amendments. If a word-budget raise step is needed, quote the Captain's words from that gate record. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Write the PR title (Conventional Commit, scoped to the plugin) on the first line and the body after it to /tmp/impl-peers-paseo-rule-matches-practice-pr.md. Do not bump versions. Stage named files only, no empty commits.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
