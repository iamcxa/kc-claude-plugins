# ideation-1
Dispatched: 88f86f2749dadb6f4ef0cf9aa089c1827096865b (workflow checkout, kc-dev-flow-2 0.41.0 README; reform scope 1, second FO)
Model: claude-opus-5-5 (Claude via Paseo, thinking high; repo roster .dev2/model-roster.json ideation row)
Budget: 2 cycles per stage
Roster: source=repository; role=ideation; provider=claude; model=claude-opus-5-5; effort=high; host=paseo; digest=sha256:c34a62cb3a56f3eded8c398ed469a2e43b69c95a84528aa7ab998ddb482f66a1; commit=88f86f2749dadb6f4ef0cf9aa089c1827096865b

## Checklist
A design, written into the task file, that places each of the five rules once in the text its reader loads in the extracted package at the pinned base commit: for each rule the exact proposed wording, the file and section it goes in, which reader loads that file (First Officer, stage worker, or both), the outcome it serves by its number in the package's outcomes document, the existing sentence it replaces or makes unnecessary quoted with its file, and the net word change per reader by the package's own counting command or, if none exists, by a stated wc command
The fresh-reader proof designed so it can be run as written: the reader prompt for each role holding none of the rules' wording, what exactly the reader is given, the five questions, and how answers are judged; say what one reader per role and one run cannot show
Acceptance criteria refined only where the admitted ones are untestable as written, each change named; anything the design cannot place without restructuring a profile, and any decision only the Captain can make, reported instead of decided; a plain statement of what is not done

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0

Profile: pilot. The admitted outcome, Non-goals, Stop condition and acceptance criteria are in the task file; admission was recorded by FO under the Captain's standing grant (read the backlog gate record). Ideation writes no repository file, branch or commit: the design, the criteria and any ADR draft live in the task file, and a draft carries no ADR number.

Where the work is: the extracted package is the root of a private working repository; FO gives its local path and the pinned base commit in the spawn message only. Read it there, read-only, at that commit (use `git show`/`git -C <path> ... <sha>` or a detached scratch worktree you remove afterwards); do not check out or change the branch its main checkout is on, and never read, name or quote the laptop-only branches that hold raw runs. In the task file name that repository only as "the private working repository" and files by path relative to its root.

Time box: two hours from dispatch for the whole task; this ideation dispatch should take well under one hour. At 30 minutes ask yourself whether the work still serves the stated goal (five rules, each once, where its reader loads it); if not, stop and report. Not doing: any other rule, restructuring profiles, a new script, tests, any change to this repository.

The five rules came from a day's use by the second dev2 FO; their source wording is in the task's Scope. If a rule already exists in the package text in other words, say so with the quote: placing it once may then mean deleting or merging, not adding.

This state branch is public: write repository-relative paths in the task file and in anything under the task folder, never a home-directory path, a private repository name, a private task slug, an email or a hostname.

Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Before using Paseo's browser tools, read extensions/paseo/browser.md under your Package root.

roborev not run: ideation produces no code candidate.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: ideation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: extracted-package-says-five-rules-that-worked completed ideation

Scratch: /tmp/dev2/kc-claude-plugins-3042bb224e995ded/extracted-package-says-five-rules-that-worked/ideation-1
Put files and checkouts outside the task worktree or state checkout under that folder. Copy cited evidence into evidence/ideation-1/ in the task folder. Never archive private repository evidence, secrets or personal data; instead write `Not archived (private): <what>; reproduce: <command>`. Before reporting, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/scratch.py close /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/extracted-package-says-five-rules-that-worked ideation-1` and paste its output.
