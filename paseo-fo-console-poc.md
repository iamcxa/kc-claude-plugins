---
title: A Paseo plugin shows the Captain which agent is the FO of which repo and every message agents sent each other
status: backlog
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:paseo-fo-console-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:paseo-fo-console-poc-backlog-1
              briefing:
                id: briefing:paseo-fo-console-poc:backlog:attempt-1:revision-1
                digest: sha256:b7a8936da6833fab48d71b2a7d5b17202e851bd47ad22798a6466f66f789e8b3
                room-ref: ./paseo-fo-console-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:paseo-fo-console-poc:backlog:1
                briefing: briefing:paseo-fo-console-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-19T09:53:39.261655Z"
                decision: hold
                reason: 'Captain 2026-10-19: 「改做小實測」 — run small Paseo peer probes first; the plugin POC is to be reshaped into an ''FO''s FO'' (a coordinator FO that aligns priorities, dispatches project FOs, tracks and aligns progress) instead of a roster/conversation view'
---

Paseo 0.12.0 gives agent-to-agent messages a sender identity the sender cannot forge:
the daemon wraps them as `<paseo-system version="1" kind="agent-message" source-agent-id=…>`.
Measured on 2026-10-19: a Codex agent received that envelope with the FO agent's id,
and its auto-review refused a tool call that only a peer message authorized. Two
problems remain, and both have caused real failures. First, finding the right peer:
FO sessions sent 183 peer messages between 2026-09-07 and 2026-10-12. Three went to the
wrong session and 20 failed because session names changed on restart. Second, the
Captain cannot see in one place what agents said to each other. Codex queue messages
were invisible in Conductor, and Paseo shows each agent's timeline separately. This POC
tests whether one Paseo plugin, with a screen in the Paseo app, can close both.

bite: three misaddressed peer messages and 20 failed sends caused by changing session
names (study of 9 workspaces, 2026-10-12); `codex queue` messages the Captain could not
see (2026-10-12).
consumer: the Captain, reading the screen in the Paseo app, and FO agents looking up a
peer by role and repo instead of by a session name.

## Scope

Captain ruling, 2026-10-19: 「開」 opens this POC, in reply to the proposal for a Paseo
plugin with an FO roster and a cross-agent conversation view.

In scope:
- One Paseo plugin, installed on this machine's daemon by local path, with:
  1. **Roster**: a screen, opened from a sidebar item, that lists live agents carrying a
     `role` label. Each row shows name, provider, `repo`, `role`, `task` labels and
     status. A plain query an FO agent can use to find a peer by role and repo.
  2. **Conversation view**: a screen listing agent-to-agent messages with sender id and
     name, receiver id and name, time and text. Messages the Captain typed are excluded.
- Labels set with Paseo's own `update_agent`, which agents can already call. The POC
  labels only test agents it creates, plus the kc-claude-plugins FO agent, which
  already carries `role=fo`, `repo=kc-claude-plugins`.
- Verify every plugin API against the installed Paseo 0.12.0, its plugin reference
  (https://paseo.sh/docs/plugins/reference.md) and the paseo-plugin skill, not memory.

Non-goals: a decisions inbox, an `/ask` command, dot or any hosted service, labelling
other people's or other FOs' agents, publishing to the Paseo registry or npm, changing
Paseo itself, changing kc-dev-flow-2's `peers` extension, and history from before the
plugin was installed unless the API gives it at no extra cost.

Budget and stop condition: one implementation cycle. Stop and report, with evidence, if
the plugin API offers no way to read agent-to-agent messages across agents. Polling
every agent's full timeline on a timer does not count as a way. Also stop and report if
the proof needs a daemon restart, a change to Paseo, or any setting other than
installing and removing this one plugin.

Cleanup: remove the plugin, archive every agent the worker created, keep
`~/.paseo/config.json` byte-identical to its pre-run copy, and do not change labels on
any agent the worker did not create. The POC code may be disposable; record what it does
not prove.

## FO alignment

Alignment with the Captain before implementation: not needed. The Captain chose this
outcome on 2026-10-19; POC defaults to no consultation.

## Acceptance criteria

**AC-1**: With the plugin installed, the roster lists every live agent that carries a
`role` label, with name, provider, repo, role, task and status, and an agent labelled
after install appears without a reload. An FO agent can find a peer by role and repo.
Verified by: the roster's data output (plugin RPC or SDK query) for two labelled test
agents and the kc-claude-plugins FO agent, and a test agent's own lookup naming the right
peer id. Limit: whether the screen renders correctly is checked by the Captain in the app
(AC-3).

**AC-2**: The conversation view lists agent-to-agent messages in both directions,
Claude to Codex and Codex to Claude, with the correct sender and receiver. A message the
Captain or the CLI typed is not listed as an agent message.
Verified by: the view's data output after two test agents exchange messages both ways,
compared with each receiver's raw `<paseo-system kind="agent-message">` envelope, plus one
CLI-sent message that does not appear.

**AC-3**: The Captain opens both screens in the Paseo app and sees the AC-1 and AC-2 data
readable in the current theme.
Verified by: the Captain's own check, run from the validation acceptance script; recorded
as not run if he did not run it.
