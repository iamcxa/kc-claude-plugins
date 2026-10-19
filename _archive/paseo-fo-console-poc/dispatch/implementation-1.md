# Dispatch: paseo-fo-console-poc implementation cycle 1

Dispatched: 18dbf490b399ecaa8ec288188bd1cf25e5c9d3ab
Model: sonnet
Worker: spacedock-ensign-paseo-fo-console-poc-implementation (spacedock:ensign)

## Checklist

1. AC-1: the FO board lists live role=fo agents with repo, task, status and last activity; "waiting on Kent" matches Paseo's attention state; an agent labelled after install appears without reload; evidence is the board's data output for two test FOs (one idle, one with a pending permission prompt) compared with list_agents
2. AC-2: "new FO" creates an agent in the chosen workspace with role=fo and repo set; "open coordinator" opens the existing role=coordinator agent or creates exactly one; evidence is list_agents before and after each action, including a second "open coordinator" that creates nothing
3. AC-3: running the draft coordinator skill and profile, the coordinator dispatches a test FO, asks progress and relays "FO X says ...", reads no repo and changes no workflow state, and leaves a permission prompt it receives unanswered; evidence is both timelines, list_pending_permissions after its turn, and the named mechanism (or its absence) that keeps it from answering

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Send your completion message to `main`, not `team-lead`.

Profile: poc. Follow the task's Scope, non-goals, budget and stop conditions exactly (Captain rulings, 2026-10-19). The stop on "the coordinator can only be kept from answering a permission prompt by the model obeying" is a valid outcome: report it with every mechanism you checked (plugin lifecycle hooks such as agent.permission_requested, before hooks agent.create / agent.session_open, Paseo profiles, Claude tool restrictions such as disallowed tools on the coordinator agent).

Environment: you run inside the Paseo app, daemon 0.12.0, `paseo` CLI on PATH, `pluginsEnabled: true`. Use the paseo-plugin skill and https://paseo.sh/docs/plugins/reference.md; verify every API against them and the installed version, not memory. Use cheap models for test agents (claude haiku, codex/gpt-6-luna).

Facts measured by FO on 2026-10-19 (Paseo 0.12.0):
- agent-to-agent prompts arrive wrapped as `<paseo-system version="1" kind="agent-message" source-agent-id=…>`;
- `list_agents` returns `labels`, `requiresAttention`, `attentionReason` (e.g. "finished");
- a permission prompt raised by an agent on a peer's request is delivered to the SENDING agent as an `event="permission-required"` notification, and that sender can answer it with `respond_to_permission`; `list_pending_permissions` lists every agent's pending prompts. This is exactly what AC-3 must keep the coordinator from doing.

Where things go: put the plugin and the draft coordinator skill/profile under `scripts/paseo-fo-console-poc/` in your worktree. Do not add `kc-dev-flow-2/extensions/coordinator` (a later task). For "agent profile", choose between a Paseo profile and a dev2-style agent .md and say which and why in the report.

Hard rules:
- Never print a Paseo agent's full process command line or any bearer token; never print ~/.paseo/local-credential, daemon-keypair.json or push-tokens.json.
- Do not restart the Paseo daemon. Copy ~/.paseo/config.json before installing; after `paseo plugin remove` restore it and `cmp` it byte-identical; report the diff you saw.
- Never answer a permission prompt of any agent, including your own test agents; deny is allowed only for prompts raised by agents you created, and say so in the report.
- Do not message, prompt, rename, relabel or archive any agent you did not create. Archive every agent you create before reporting.
- Comments: run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/scripts/comment_ratio.py`; no comment narrates the change or cites a file:line, task or PR.
- Commit format `feat(scripts): …`; stage files explicitly; commit hooks run normally.

roborev (listed extension): Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`, where <base sha> is `git -C <worktree> merge-base HEAD origin/main`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.
