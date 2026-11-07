# implementation-1-message-5

Dispatched: ba055b8a7a55a787ac989c4cef52d07dd75661ad (workflow checkout, kc-dev-flow-2 0.35.0 README); batch 16, follow-up message to the implementation-1 worker (Paseo ba392d9b), carrying Captain amendment 1 (a repeat-only case for the AC-4 falsifier)
Symptom: AC-4 falsifier confounded twice (Sonnet 9ca06dfd, b434816c); spacedock refuses the move to validation while the report holds a FAILED item
Model: gpt-6.1-sol (Codex via Paseo, thinking xhigh; the same worker as implementation-1)

## Checklist

1. Apply Captain amendment 1 in the task file (`## Captain amendments`, Amendment 1, 2026-11-07), which supersedes AC-4 for its falsifier sentence: add one replay record E whose finding is a below-P1 decline with no observed harm and no Captain ask, whose only route to a backlog task is a repeat in a later round or task, so the bite clause is the only rule that can require its task.
2. Add E to the candidate and base replay prompts and to the bite-clause-deleted mutation prompt, change no product file for this, and run fresh Sonnet agents through Paseo (model `sonnet` set explicitly, no tools): the candidate prompt twice, expecting E `violation` quoting the repeat condition, and the mutation prompt twice, expecting E `ok`; keep A–D's readings beside it.
3. Replace the FAILED item in a dated addendum to the implementation stage report with the result: DONE when both runs match, otherwise FAILED with the agent ids and quoted readings; archive each agent after recording, commit the state, and report.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0

Start in the assigned worktree; verify pwd and git root before edits.

Everything in implementation-1 stands. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: decline-becomes-task-only-with-a-bite completed implementation
