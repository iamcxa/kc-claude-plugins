# Dispatch: paseo-peer-sender-label-poc implementation cycle 1

Dispatched: 5b6a83bc36026d4f204805db124df85fa1653bf9
Model: sonnet
Worker: spacedock-ensign-paseo-peer-sender-label-poc-implementation (spacedock:ensign)

## Checklist

1. AC-1: a peer message sent through the plugin reaches the receiver with a sender label it can verify (sending agent id, provider, peer not Captain), in both directions Claude to Codex and Codex to Claude; evidence is each receiver's timeline plus its reply naming the verified sender
2. AC-2: a message carrying the same label text sent with plain send_agent_prompt fails the receiver's check and the receiver says so instead of treating it as the Captain; evidence is the receiver's reply for the forged message
3. AC-3: the acceptance steps the Captain runs to show his own typed message is not reported as a peer, plus cleanup done (plugin removed, agents archived, ~/.paseo/config.json identical to the pre-run copy) and what the POC does not prove

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Send your completion message to `main`, not `team-lead` (the completion block Spacedock appends names team-lead, which is not registered here).

Profile: poc. Follow the task's Scope, non-goals, budget and stop condition exactly; they are Captain rulings from 2026-10-19. A negative result ("Paseo gives a plugin no way to make a checkable label") with evidence is a valid outcome: stop and report it rather than building around it.

Environment: you run inside the Paseo app (daemon 0.11.4, `paseo` CLI on PATH, `pluginsEnabled: true` in ~/.paseo/config.json). You can use the `mcp__paseo__*` tools (create_agent, send_agent_prompt, get_agent_activity, archive_agent) if your session has them; otherwise the `paseo` CLI (`paseo --help`). Use cheap models for test agents: `codex/gpt-6-luna` and a sonnet or haiku Claude model (`paseo provider models claude`).

Facts the FO measured on 2026-10-19 (re-check what you rely on):
- A Codex agent called `mcp__paseo__send_agent_prompt` and woke an idle Claude agent; the Claude agent then woke an idle Codex agent the same way. The prompt arrived in the receiver's conversation as a plain user message with no sender marker; only the sender's finish notice came wrapped in `<paseo-system>`.
- The Paseo daemon launches each Claude agent with `--mcp-config` pointing at `http://127.0.0.1:6767/mcp/agents?callerAgentId=<that agent's id>` and a per-agent bearer token. So the daemon knows which agent made each call. That is a lead, not a design.
- Plugin docs: https://paseo.sh/llms.txt, https://paseo.sh/docs/plugins/reference.md (lifecycle hooks via server.on incl. agent.turn_started/turn_ended; before hooks agent.create / agent.session_open; server RPC; paseo.agents.ref(id).send; timeline.append). Verify every API against these docs and the installed version, not memory. Use the paseo-plugin skill for the plugin workflow.

Hard rules:
- Never print a Paseo agent's full process command line or any bearer token (`ps` output of a Paseo agent contains one). Never print ~/.paseo/local-credential, daemon-keypair.json or push-tokens.json.
- Do not restart the Paseo daemon (it hosts the FO and you). Do not change Paseo settings other than installing and removing this one plugin; copy ~/.paseo/config.json before you start and diff it at the end.
- Do not message, prompt, archive or otherwise touch any agent you did not create. Archive every agent you create before reporting.
- Put the plugin source under `scripts/paseo-peer-label-poc/` in your worktree (not a top-level plugin directory; marketplace registration is a non-goal). Confirm `bash scripts/version-parity-check.sh` and `bash scripts/skill-frontmatter-lint.sh` still pass.
- Comments: run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/scripts/comment_ratio.py` as the implementation skill directs; no comment narrates the change or cites a file:line, task or PR.
- Commit format `feat(scripts): …`; stage files explicitly, never `git add .`.

roborev (listed extension): Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`, where <base sha> is `git -C <worktree> merge-base HEAD origin/main`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
