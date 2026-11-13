# implementation-1
Dispatched: 88f86f2749dadb6f4ef0cf9aa089c1827096865b (workflow checkout, kc-dev-flow-2 0.41.0 README; merge-front batch, 2026-11-13)
Model: gpt-6.1-terra (Codex via Paseo, thinking xhigh; the Captain's comparison of 2026-11-13: model one tier lower at xhigh; the same worker as ideation-1)
Budget: 1 implementation and 2 validation cycles, in one package PR.
Roster: source=repository; role=implementation; provider=codex; model=gpt-6.1-terra; effort=xhigh; host=paseo; digest=sha256:c34a62cb3a56f3eded8c398ed469a2e43b69c95a84528aa7ab998ddb482f66a1; commit=88f86f2749dadb6f4ef0cf9aa089c1827096865b

## Checklist
One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (6a1eaf837bd6087cd0b8b665dc19beaed3c44dff) implementing the approved design and acceptance criteria in the task file; Build Captain amendment 1 and nothing else: add to kc-dev-flow-2/extensions/codex/EXTENSION.md, at the step where FO marks a PR ready, one sentence saying FO comments a Codex review request on the PR once at that moment (the Captain's words are in the amendment; render them in the file's English, adding nothing), keeping the existing after-a-repair sentence consistent with it. No script change, no automation, no test of new behaviour; your ideation probe is not carried into the PR. If a lint budget counts that file's words, report the count before and after and stop if a raise is needed. Run AC-5's evidence on the candidate and record command, exit and output path. Delete the poc branch once the candidate is committed and say so. Stop and report if anything else is needed; only the files the design names
Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/adr_lint.py docs/adr --since <base> exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/comment_ratio.py within its maximum; commit locally, no push; PR text written for FO; FO pushes, opens the Draft PR, runs RoboRev and reads CI; CI cost measured or stated as not measured

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved; the Captain's words are in the task's ideation gate record (read them there; this line does not restate them) and any ## Captain amendments. If a word-budget raise step is needed, quote the Captain's words from that gate record. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Write the PR title (Conventional Commit, scoped to the plugin) on the first line and the body after it to the file implementation/pr.md in the task's state folder (/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/ready-pr-gets-a-codex-code-review-without-fo-noticing/implementation/pr.md), committed with your evidence. Do not bump versions. Stage named files only, no empty commits.

roborev not run: FO runs RoboRev after you report, because the Codex sandbox cannot reach the local roborev daemon.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: ready-pr-gets-a-codex-code-review-without-fo-noticing completed implementation

Scratch: /tmp/dev2/kc-claude-plugins-3042bb224e995ded/ready-pr-gets-a-codex-code-review-without-fo-noticing/implementation-1
Put files and checkouts outside the task worktree or state checkout under that folder. Copy cited evidence into evidence/implementation-1/ in the task folder. Never archive private repository evidence, secrets or personal data; instead write `Not archived (private): <what>; reproduce: <command>`. Before reporting, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/scratch.py close /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/ready-pr-gets-a-codex-code-review-without-fo-noticing implementation-1` and paste its output.
