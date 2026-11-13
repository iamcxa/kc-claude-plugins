# implementation-1
Dispatched: 88f86f2749dadb6f4ef0cf9aa089c1827096865b (workflow checkout, kc-dev-flow-2 0.41.0 README; Pilot probe completion, 2026-11-13)
Model: gpt-6.1-sol (Codex via Paseo, thinking xhigh; repo roster .dev2/model-roster.json implementation row)
Budget: 1 implementation and 2 validation cycles, in one package PR.
Roster: source=repository; role=implementation; provider=codex; model=gpt-6.1-sol; effort=xhigh; host=paseo; digest=sha256:c34a62cb3a56f3eded8c398ed469a2e43b69c95a84528aa7ab998ddb482f66a1; commit=88f86f2749dadb6f4ef0cf9aa089c1827096865b

## Checklist
One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (6a1eaf837bd6087cd0b8b665dc19beaed3c44dff) implementing the approved design and acceptance criteria in the task file; Build the approved design with decisions D1 and D2 as the Captain approved them at the ideation gate (his words are in the gate record): the Pilot-only proof-record check in the design check, the skip for designs already approved at their ideation gate, the one sentence in the observer skill, and the test fixtures the design names. Start from the local probe poc/design-check-reads-each-pilot-criterion-for-its-proof-record at 9f403d6 (carry what meets the Pilot bar, rewrite what does not), and delete that branch once your candidate is committed, saying so. No change to the workflow text or its word budget. Every acceptance criterion as written in the task file, each with its evidence command rerun on the candidate and command, exit and output path recorded per criterion; what cannot run stays under Not provable now with the reason. The sibling task budget-form-counts-ideation-rounds-and-times-each-round may later edit two of the same test files: keep your fixture edits minimal and say which hunks it will meet. Stop and report if anything outside the design, the named files or the Budget is needed; only the files the design names
Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/adr_lint.py docs/adr --since <base> exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/comment_ratio.py within its maximum; commit locally, no push; PR text written for FO; FO pushes, opens the Draft PR, runs RoboRev and reads CI; CI cost measured or stated as not measured

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved; the Captain's words are in the task's ideation gate record (read them there; this line does not restate them) and any ## Captain amendments. If a word-budget raise step is needed, quote the Captain's words from that gate record. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Write the PR title (Conventional Commit, scoped to the plugin) on the first line and the body after it to the file implementation/pr.md in the task's state folder (/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/design-check-reads-each-pilot-criterion-for-its-proof-record/implementation/pr.md), committed with your evidence. Do not bump versions. Stage named files only, no empty commits.

roborev not run: FO runs RoboRev after you report, because the Codex sandbox cannot reach the local roborev daemon.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: design-check-reads-each-pilot-criterion-for-its-proof-record completed implementation

Scratch: /tmp/dev2/kc-claude-plugins-3042bb224e995ded/design-check-reads-each-pilot-criterion-for-its-proof-record/implementation-1
Put files and checkouts outside the task worktree or state checkout under that folder. Copy cited evidence into evidence/implementation-1/ in the task folder. Never archive private repository evidence, secrets or personal data; instead write `Not archived (private): <what>; reproduce: <command>`. Before reporting, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/scratch.py close /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/design-check-reads-each-pilot-criterion-for-its-proof-record implementation-1` and paste its output.
