# implementation-1

Dispatched: 146727ded0d4ce8014ea0b41a45dc3409d6b269b (workflow checkout, kc-dev-flow-2 0.34.0 README); batch 12, first implementation dispatch
Model: gpt-6.1-sol (Codex via Paseo, thinking xhigh; the Captain, chat 2026-11-02: 「Sonnet / high，對應 Sol / xhigh」)

## Checklist

One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/spacedock-ensign/worker-completion-reaches-fo-on-paseo (c129cb215c2630d08853eeffae0fd5a2ee7e40c6) implementing the approved design and acceptance criteria in the task file; the design approved at the 2026-11-02 ideation gate (「照建議」), with D1 to D5 as recorded; the files its implementation section names; stacked on PR #763, so write the PR text with base branch spacedock-ensign/worker-completion-reaches-fo-on-paseo; the Done line is: Done: special-roles-follow-the-model-table completed implementation; only the files the design names
ADR 0049 records the ruling the design names, quoting the Captain's words from the task file and its gate records
Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> --require 0049 exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; commit locally, no push; PR text written for FO; FO pushes, opens the Draft PR, runs RoboRev and reads CI; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0

Number guards: ADR: 0049

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved; the Captain's words are in the task's ideation gate record (read them there; this line does not restate them) and any ## Captain amendments. If a word-budget raise step is needed, quote the Captain's words from that gate record. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/spacedock-ensign/worker-completion-reaches-fo-on-paseo. Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Write the PR title (Conventional Commit, scoped to the plugin) on the first line and the body after it to /tmp/impl-special-roles-follow-the-model-table-pr.md. Do not bump versions. Stage named files only, no empty commits.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
