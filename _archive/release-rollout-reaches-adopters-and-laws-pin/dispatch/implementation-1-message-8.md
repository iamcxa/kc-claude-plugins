# implementation-1-message-8

Dispatched: e8664a72b0f904e5dda3c391d52ab3abaca876b4 (workflow checkout, kc-dev-flow-2 0.38.1 README); batch 21, follow-up message to the implementation-1 worker (Paseo 68a83d28), validation dispatch refused on AC-10's wording
Symptom: replacement criterion words not found in the Captain's amendment
Model: gpt-6.1-sol (Codex via Paseo, thinking xhigh; the same worker as implementation-1)

## Checklist

RoboRev job 1728 on 61529999e is clean and the commit is pushed to Draft PR #838; the validation dispatch was refused before any worker ran, by kc-dev-flow-2/scripts/dispatch_records.py: "AC-10 (Captain amendment 1) adds words in a sentence kept from the criterion it replaces that are not in his words: has, installation, repository; remove them, or ask the Captain and record his answer as an amendment"
Reword AC-10 only, in the task file: in each sentence it keeps from the superseded AC-7 use AC-7's own words (for example "carries one pointer row", "states the D1 ruling"), and for what amendment 1 changes use only words found in its Captain: and Asked: lines (they say the list stays local and is not put into the dev2 repo); change no other criterion, no product file and no evidence, and do not widen or narrow what AC-10 requires
Check AC-11 and AC-12 for the same defect against their amendments and fix them the same way if they have it; commit the task file with the state commit command and report the exact old and new sentences; your final reply is your completion message, ending with the Done line

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1

Start in the assigned worktree; verify pwd and git root before edits.

Everything in implementation-1 stands. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: release-rollout-reaches-adopters-and-laws-pin completed implementation
