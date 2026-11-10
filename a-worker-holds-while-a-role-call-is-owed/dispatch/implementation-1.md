# implementation-1
Dispatched: e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e (workflow checkout, kc-dev-flow-2 0.36.0 README; batch 18)
Model: Codex

## Checklist
One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (f980a097bf15d8d1382c039949c6b9aefc5439c8) implementing the approved design and acceptance criteria in the task file; the Captain approved D1-D4 as recommended; base on origin/main, which now carries #821's mechanism question and unrelated: decline form in kc-dev-flow-2/scripts/role_triggers.py, so the reasonless-decline half of the stop condition is tested against it; any Behaviour replay that builds dispatches writes them under a prefix of its own (never the un-prefixed /tmp/spacedock-dispatch/spacedock-ensign-<slug>-<stage>.md path another session's builds use), see case-confirmation.md and the ideation harness note; only the files the design names
Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0/scripts/adr_lint.py docs/adr --since <base> exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0/scripts/comment_ratio.py within its maximum; commit locally, no push; PR text written for FO; FO pushes, opens the Draft PR, runs RoboRev and reads CI; CI cost measured or stated as not measured

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved; the Captain's words are in the task's ideation gate record (read them there; this line does not restate them) and any ## Captain amendments. If a word-budget raise step is needed, quote the Captain's words from that gate record. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Write the PR title (Conventional Commit, scoped to the plugin) on the first line and the body after it to /tmp/impl-a-worker-holds-while-a-role-call-is-owed-pr.md. Do not bump versions. Stage named files only, no empty commits.

roborev not run: FO runs RoboRev after you report, because the Codex sandbox cannot reach the local roborev daemon.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: a-worker-holds-while-a-role-call-is-owed completed implementation
