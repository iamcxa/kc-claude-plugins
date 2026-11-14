# implementation-1
Dispatched: 88f86f2749dadb6f4ef0cf9aa089c1827096865b (workflow checkout, kc-dev-flow-2 0.41.0 README; reform scope 1, second FO)
Model: gpt-6.1-sol (Codex via Paseo, thinking xhigh; repo roster .dev2/model-roster.json implementation row)
Budget: 2 cycles per stage
Roster: source=repository; role=implementation; provider=codex; model=gpt-6.1-sol; effort=xhigh; host=paseo; digest=sha256:c34a62cb3a56f3eded8c398ed469a2e43b69c95a84528aa7ab998ddb482f66a1; commit=88f86f2749dadb6f4ef0cf9aa089c1827096865b

## Checklist
One candidate (Conventional Commit title scoped to the plugin) on the assigned branch off origin/main implementing the approved design and acceptance criteria in the task file: the validation-principles sentence, the state guard reading gzip header names, and its test; only the three files the design names; nothing is installed or flipped by this change
Every acceptance criterion green with the evidence each names, on throwaway state checkouts with their own remotes (never the live clone); each falsifier shown failing by a mutation you run (python3 -B, caches cleared); a header-only name is refused and a clean gzip is accepted
The PR text says in its first lines what merging does and does not give: the home class stays at warn after this merges, with the design's four conditions for its flip listed, condition (a) already started by the release now going out; private-repo can be set to refuse once this change's release is synced, by a reinstall FO runs
kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> exit 0; kc-dev-flow-2/scripts/number_guards.py check exit 0; kc-dev-flow-2/scripts/comment_ratio.py within its maximum; commit locally, no push; PR text written for FO; FO pushes, opens the Draft PR, runs RoboRev and reads CI; CI cost measured or stated as not measured

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0

Profile: pilot. The admitted outcome, Non-goals, Stop condition and acceptance criteria are in the task file; admission was recorded by FO under the Captain's standing grant (read the backlog gate record). 

Approved design: `## Design` and `## Acceptance criteria` in the task file; the ideation gate was recorded by FO under the Captain's standing grant. Decision D1 (release order) was settled by the Captain: the release carrying the earlier state-write change goes ahead; FO takes no step on it. Decision D2: FO runs each later guard reinstall when its condition is met. Install the guard nowhere but your throwaway checkouts and run no `git config` write on this clone. If a change needs a file the design does not list, stop and return to FO. The identifier list is never in the repository, a fixture, the task file or the PR text: tests build their own list from invented names. The guard is live on this workflow's state checkouts (private task slugs and tailnet hostnames refuse; the other classes warn): a refused state commit reaches you as a failed `spacedock state commit` with the guard's two lines; say so and FO commits.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Write the PR title (Conventional Commit, scoped to the plugin) on the first line and the body after it to the file implementation/pr.md in the task's state folder, with your evidence. Do not bump versions. Stage named files only, no empty commits. If `spacedock state commit` or a local commit is refused by your sandbox, do not fall back to `git add` in the state checkout: write the files, say so in your final reply, and FO commits.

This state branch is public: write repository-relative paths in the task file and in anything under the task folder, never a home-directory path, a private repository name, a private task slug, an email or a hostname.

Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Before using Paseo's browser tools, read extensions/paseo/browser.md under your Package root.

roborev not run: FO runs RoboRev after you report, because the Codex sandbox cannot reach the local roborev daemon.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo completed implementation

Scratch: /tmp/dev2/kc-claude-plugins-3042bb224e995ded/gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo/implementation-1
Put files and checkouts outside the task worktree or state checkout under that folder. Copy cited evidence into evidence/implementation-1/ in the task folder. Never archive private repository evidence, secrets or personal data; instead write `Not archived (private): <what>; reproduce: <command>`. Before reporting, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/scratch.py close /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo implementation-1` and paste its output.
