# ideation-2

Dispatched: a11707d5ec19ee34777c7bdeac4c4d100bc84857 (workflow checkout, kc-dev-flow-2 0.31.0 README); batch 7, revision after interview round 2; follow-up to the ideation-1 worker
Model: gpt-6-astra (Codex via Paseo, thinking high)

## Checklist

Revise the peers and paseo texts and design against interview round 2 (/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/fo-interviews-extension/round-2-batch7-texts.md, "Text B" in the FO reading and each FO's answers): choose the binding by how peers actually reach the session (Claude Code running inside Paseo uses the Paseo route), so a Paseo-hosted FO without the paseo extension listed can still answer; the no-steer rule names `activeTurnBehavior` explicitly, applies to peers and not to the FO's own workers, says how a reply to an asker that is running is sent, and gives a wait bound; add answering a peer's ask, recording an exchange that belongs to no task, an incoming ask while a Captain gate is open, and checking the FO's own backlog for an existing task before opening one; put "unavailable originals stay unverified" before "read the original"
Recount the words FO reads at each moment with the same counter, and update the acceptance criteria and the Needs decision section so each still has reproducible evidence and a falsifier
Append a complete new `## Stage Report: ideation` with every item DONE or SKIPPED and evidence, ending in a `### Summary` that says it supersedes the earlier one; run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0/scripts/design_surfaces.py check` on the task file and report its output

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0

Profile: pilot. Change only the task file's design, criteria and report. Leave the structured Captain-source check as designed: FO has proposed to the Captain moving it to its own task, and he has not ruled. Keep what round 2 did not question. Use Paseo's own skill and `paseo agent send --help` for activeTurnBehavior, not another FO's usage. Ideation writes no repository file, branch or commit other than the task file through `spacedock state commit`. Do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
