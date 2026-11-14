# validation-1
Dispatched: 88f86f2749dadb6f4ef0cf9aa089c1827096865b (workflow checkout, kc-dev-flow-2 0.41.0 README; reform scope 3, second FO)
Model: claude-opus-5-5 (Claude via Paseo, thinking medium; not the roster Codex row: the candidate is in another repository outside a sandboxed Codex worker's workspace and the readers need ssh; a different model from the Sonnet author; the same model family wrote the design)
Budget: 2 cycles per stage
Roster: source=repository; role=validation; provider=codex; model=gpt-6-astra; effort=xhigh; host=paseo; digest=sha256:c34a62cb3a56f3eded8c398ed469a2e43b69c95a84528aa7ab998ddb482f66a1; commit=88f86f2749dadb6f4ef0cf9aa089c1827096865b
Candidate: 17a4ff133f24da0d57fe4a395e96867516957250

## Checklist
An independent verdict at the candidate against the task's acceptance criteria, the approved design's last pass and both Captain amendments: AC-1 each of the five rules appears once in the text its reader loads (read the candidate's diff against its base; counts per reader by the design's commands); AC-3 the growth and what paid for it are stated and equal what the Captain accepted in amendment 2; the raise step's captain field holds only his sentence
AC-2 by your own fresh readers, text given as explicit files, no skill calls, transcripts checked for contamination: re-run the lost-and-restored scenario yourself at base, at the not-proposed commit and at the candidate (it is the one result with consequences); run one control scenario per role and confirm the rule does NOT trigger there; sample at least two other First Officer scenarios and one worker scenario at the candidate and judge each answer against the design's expected answer, counting "own judgement" answers apart
Read the candidate's whole diff for anything beyond the five rules, the two removals, the restored sentence, the raise step and the one outcomes-document line; the prepared PR text states the three known limits as limits; the limits of what you checked and anything not run

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0

Profile: pilot. The admitted outcome, Non-goals, Stop condition and acceptance criteria are in the task file; admission was recorded by FO under the Captain's standing grant (read the backlog gate record). Independent validation: assess, do not repair.

Time box: 20 minutes from dispatch, hard stop; the task's whole box ends 22:20 local on 2026-11-14. Wall-clock times from /bin/date only. Not doing: proposing new rules or new wording; a defect is reported, not repaired.

Where things are: FO gives the candidate worktree, the commits and how to reach a machine with an empty home in the spawn message only. The clean host has this package installed as a plugin holding the BASE text: give every reader its text as explicit files, tell it to answer from those files only and to invoke no skill, and discard and report any answer whose transcript shows a read of the plugin cache or a call of this package's skills. Do not update, disable or remove the installed plugin there; remove only what you copied. Print or copy no credential.

Reader answers and transcripts quote private package text: keep them out of the state checkout; the report describes each answer in your own words. No fenced code block in the report.

If your writes to the state checkout are refused, do not look for another route and do not run the scratch close: leave the report and logs as draft files in a folder you name in your final reply; FO lands them.

This state branch is public: write repository-relative paths in the task file and in anything under the task folder, never a home-directory path, a private repository name, a private task slug, an email or a hostname.

Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Before using Paseo's browser tools, read extensions/paseo/browser.md under your Package root.

roborev not run: the candidate lives in a different, private repository that this repository's review daemon does not cover.

Roster authors: implementation-1.md and its two messages: claude/claude-sonnet-5-5 high. This validator: claude/claude-opus-5-5, same family, a different model.

If you correct your stage report, append a complete new report under the exact heading `## Stage Report: validation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: extracted-package-says-five-rules-that-worked completed validation

Scratch: /tmp/dev2/kc-claude-plugins-3042bb224e995ded/extracted-package-says-five-rules-that-worked/validation-1
Put files and checkouts outside the task worktree or state checkout under that folder. Copy cited evidence into evidence/validation-1/ in the task folder. Never archive private repository evidence, secrets or personal data; instead write `Not archived (private): <what>; reproduce: <command>`. Before reporting, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/scratch.py close /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/extracted-package-says-five-rules-that-worked validation-1` and paste its output.
