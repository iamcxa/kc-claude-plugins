# implementation-1-message-1

Dispatched: 88f86f2749dadb6f4ef0cf9aa089c1827096865b (workflow checkout, kc-dev-flow-2 0.41.0 README); reform scope 1, second FO; follow-up message to the implementation-1 worker (Paseo b2274684)
Symptom: the operator's first credentialed launch was refused before any run by the isolated init check: "init lists skill schedule outside the spacedock export and the CLI's bundled set"; plugins and MCP servers were as in the no-login smoke
Model: claude-sonnet-5-5 (Claude via Paseo profile 'dev2 worker', thinking high; the same worker as implementation-1)

## Checklist

- Decide from evidence whether the skill named schedule is a skill the CLI itself ships that appears only with a login (not operator configuration), and say what the evidence is; if it is, add it to the cell's allowed bundled skills as a login-only entry, and keep every other unexpected skill, plugin or MCP server a breach.
- Make sure a worker in a run cannot use that skill to act outside the run (it creates scheduled cloud agents): state how the launch prevents it, or prevent it.
- Captain amendment 1 (in the task file) settles decision D1: the credential is a subscription token the Captain makes and keeps himself; the runner still only reads it from the environment.
- Re-run the unpaid checks (selfcheck, the two dry runs, the leaky-transcript scan) with exit codes; commit on the same branch in the private working repository; report the new candidate SHA. No paid run and no credential handling by you: the operator re-runs the first paid step.
- Append a complete new stage report that supersedes the earlier one.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0

Start in the assigned worktree; verify pwd and git root before edits.

Everything in implementation-1 stands, including: nothing from a case, a run or a private adopter goes onto this state branch; FO commits state. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

roborev not run: the candidate lives in a different, private repository that this repository's review daemon does not cover.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: behaviour-baseline-first-cell completed implementation
