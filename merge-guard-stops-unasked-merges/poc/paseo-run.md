# Paseo-hosted Claude run (2026-11-06)

Paseo 0.15.1, Claude Code 2.1.318, provider `claude-fo` (command `claude --agent spacedock:first-officer`).
`paseo-run.sh` holds the same commands as one script; the live run was these commands typed one by one,
and the script itself has not been run end to end.

Launch, as Paseo built it (`paseo-claude-argv.txt`, credentials redacted): Paseo appends
`--permission-prompt-tool stdio --setting-sources=user,project,local --permission-mode auto
--allow-dangerously-skip-permissions` to the provider command. The wrapper (`paseo-claude-wrapper.sh`,
reached through `--env PATH=<wrapper dir>:<daemon PATH>`) dropped `--agent spacedock:first-officer` and
rewrote the sources to `--setting-sources=project`.

Isolation:
- Excluded: the Captain's user and local Claude settings, plugins and hooks, and the FO agent definition.
- Kept: Paseo's own flags above, Paseo's MCP servers, the keychain login.
- Loaded: the throwaway folder's `.claude/settings.json` (`paseo-project-settings.json`: auto mode, the guard hook).
- Also loaded: `~/.claude/CLAUDE.md` and memory. `--setting-sources` does not govern them; attempt 1's reply used its closing block.
- Edited: no Paseo, Claude or Codex config.

Attempt 1, agent `1b40dded`, archived:
- `paseo run --cwd` was ignored. An agent-scoped run takes the caller's workspace, so the session ran in this
  repository's checkout and no guard loaded.
- The test agent declined to run the merge because the request came from a peer agent, and the hook log stayed empty.

Attempt 2, agent `046b0b6a-25c1-4992-832e-16487f6aad52`, workspace "merge-guard phone test (throwaway)" `wks_f9083c3591f69a32`:
- `paseo-hook.log`: the agent ran `cat` on the fake (pass), then the uncarried merge at `2222…`, and the guard
  returned `stop`, which is `ask` on Claude.
- Paseo now holds `permission-c2a47796-c2d4-4665-993c-0f29ea886644` (Bash), and the agent status is `running`.
- `/tmp/merge-guard-poc-paseo/ran.log` is empty, so the fake gh has not run.
- The payload from `list_pending_permissions` has `name: Bash`, `input.command` and `detail.command` (the full
  `gh pr merge 1 --repo merge-guard-poc/does-not-exist --squash --match-head-commit 2222…`), and no reason field.
  The guard's "merge guard: no task's newest merge/ask-N.json carries …" text is not in the payload, and it is
  not in the session transcript.
- Any Paseo agent with the `respond_to_permission` tool can answer this request. This session's tool list has
  that tool, and Paseo exposes it to agents (0.12 note). Not answered here.

Captain-only step: open Paseo on the phone and answer the request. Expected results:
- Yes: one `FAKE-GH-RAN pr merge` line in `ran.log`. Nothing merges.
- No: `ran.log` stays empty.
- Either way: the agent's last reply says what happened, and `paseo inspect 046b0b6a…` shows no pending permission.
