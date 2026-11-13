Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved; the Captain's words are in the task's ideation gate record (read them there; this line does not restate them) and any ## Captain amendments. If a word-budget raise step is needed, quote the Captain's words from that gate record. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Write the PR title (Conventional Commit, scoped to the plugin) on the first line and the body after it to the file implementation/pr.md in the task's state folder (/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/merge-ask-is-produced-from-records/implementation/pr.md), committed with your evidence. Do not bump versions. Stage named files only, no empty commits.

roborev not run: FO runs RoboRev after you report, because the Codex sandbox cannot reach the local roborev daemon.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: merge-ask-is-produced-from-records completed implementation

Scratch: /tmp/dev2/kc-claude-plugins-3042bb224e995ded/merge-ask-is-produced-from-records/implementation-1
Put files and checkouts outside the task worktree or state checkout under that folder. Copy cited evidence into evidence/implementation-1/ in the task folder. Never archive private repository evidence, secrets or personal data; instead write `Not archived (private): <what>; reproduce: <command>`. Before reporting, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/scratch.py close /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/merge-ask-is-produced-from-records implementation-1` and paste its output.
