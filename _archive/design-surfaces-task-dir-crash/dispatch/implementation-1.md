# implementation-1
Dispatched: 8ce0eb6050c889b21baccf50fec35231bc888d66 (workflow checkout, kc-dev-flow-2 0.39.1 README; route trial of 2026-11-13)
Model: gpt-6.1-sol (Codex via Paseo, thinking xhigh; repo roster .dev2/model-roster.json implementation row)
Budget: 1 implementation and 2 validation cycles, in one package PR.
Roster: source=repository; role=implementation; provider=codex; model=gpt-6.1-sol; effort=xhigh; host=paseo; digest=sha256:c34a62cb3a56f3eded8c398ed469a2e43b69c95a84528aa7ab998ddb482f66a1; commit=8ce0eb6050c889b21baccf50fec35231bc888d66

## Checklist
One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (8125e6d516d32abbf79c6772de10cde2c20900a8) implementing the approved design and acceptance criteria in the task file; Build the approved design: the task-argument resolution at the checker's entrance and its tests, starting from your local probe poc/design-surfaces-task-dir-crash at 54424755e (carry what meets the Pilot bar, rewrite what does not); AC-1 to AC-4 as written in the task file, each with its evidence command rerun on the candidate. This is build round 2 of at most 3 in the route trial; end the stage report with a '### Trial round 2' line in the same form as round 1 (premise and goal check, start and end with time source, base and candidate, check command with saved output and result, what blocked and what moved since round 1, which stop fired or none). Stop and report if anything outside the design, the named files or the Budget is needed; only the files the design names
Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1/scripts/adr_lint.py docs/adr --since <base> exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1/scripts/comment_ratio.py within its maximum; commit locally, no push; PR text written for FO; FO pushes, opens the Draft PR, runs RoboRev and reads CI; CI cost measured or stated as not measured

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved; the Captain's words are in the task's ideation gate record (read them there; this line does not restate them) and any ## Captain amendments. If a word-budget raise step is needed, quote the Captain's words from that gate record. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Write the PR title (Conventional Commit, scoped to the plugin) on the first line and the body after it to /tmp/impl-design-surfaces-task-dir-crash-pr.md. Do not bump versions. Stage named files only, no empty commits.

roborev not run: FO runs RoboRev after you report, because the Codex sandbox cannot reach the local roborev daemon.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: design-surfaces-task-dir-crash completed implementation
