---
title: From one Paseo screen the Captain sees what each FO is busy with, starts FOs, and opens a coordinator that only starts and talks to them
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
            - id: gate-attempt:paseo-fo-console-poc-backlog-2
              briefing:
                id: briefing:paseo-fo-console-poc:backlog:attempt-2:revision-1
                digest: sha256:f665d9a1abfafb773b87bc0b6556efb916b7be916192c82288fde72330a5d03b
                room-ref: ./paseo-fo-console-poc/review/backlog/briefing-2
---

Kent wants one entry point in Paseo for his FOs. From a plugin screen he sees which FOs
exist and what each is busy with, starts a new FO, and opens a coordinator, the "FO's FO".
The coordinator only starts FOs and talks to them; it never checks their work. Kent
discusses details with each FO directly. Today he finds FOs by scrolling Paseo's agent
list. One FO is still titled `<system_instruction>`, with no labels (`list_agents`,
2026-10-19). The cross-FO coordination run (DOT#0007, DOT#0008) is done by hand, and
nothing enforces its rule that no agent answers another agent's permission prompt.

Measured on Paseo 0.12.0 (2026-10-19) and relied on here:
- agent-to-agent prompts carry an unforgeable sender envelope;
- `list_agents` returns labels plus `requiresAttention` and `attentionReason`;
- a permission prompt raised on a peer's request is routed to the sending agent, which
  can answer it with `respond_to_permission`.

bite: a peer lookup by label would have returned the wrong kc-claude-plugins FO
(2026-10-19, corrected by relabelling); a permission prompt raised on a peer's request
reached the peer, not Kent (2026-10-19 probe, denied by hand).
consumer: Kent, using the screen as his entry point to FOs, and the coordinator agent.

## Scope

Kent's words, 2026-10-19, Claude session de83e726:
「我想要的是一個更明確的操作模式，例如設計 paseo plugin 做個 UI 我從那邊當進入點，那裡也要可以開 session，而你在那邊作為 FO's FO 只負責啟動與溝通其他 FO不自己檢查工作內容，或甚至我可以看到有哪些 FO 分別在忙什麼，簡單就好」;
「我覺得 FO's FO 應該要有自己的 skill + agnet profile，認同嗎？跟 FO 一樣操作，但是放在 dev2 內，這個 poc 也跑在 dev2 內，等於基於 paseo，擴充 SD 套件的邊界能力」;
「可以」 (11:08:05Z) to handing this scope to the dev2-poc FO, which rewrites this task and
brings it back to his backlog gate. The scope below was relayed by the coordinator
a88dedae. The dev2-poc FO checked the quoted words in that transcript.

In scope:
1. One Paseo plugin screen, opened from a sidebar item:
   - an **FO board** of agents labelled `role=fo`. Each row shows its `repo` label, its
     `task` label (kept by the FO itself; the board does not read the FO's work), a status
     (busy, idle, or waiting on Kent, from Paseo's own `requiresAttention` and
     `attentionReason`), and the time of last activity. A row opens that agent in Paseo's
     own view;
   - a **new FO** button that creates an agent in a chosen workspace with `role=fo` and
     `repo` set;
   - an **open coordinator** button that opens the single `role=coordinator` agent, or
     creates it if none exists.
2. A **draft coordinator skill and agent profile**, tried inside this POC and shaped like a
   kc-dev-flow-2 extension (as `peers` is) with a Paseo host binding. They live in the POC's
   own directory. `kc-dev-flow-2/extensions/coordinator` comes only after a later task,
   once this POC shows they work. The coordinator:
   - starts FOs and talks with them: it dispatches, asks for progress, and relays as
     "FO X says …";
   - never reads a repository, verifies an FO's work, changes workflow state, or
     dispatches workers;
   - never answers any agent's permission prompt. Prompts it receives are left for Kent
     (DOT#0008).
3. Boundary: spacedock drives workflows; the coordinator only talks to FOs. No change to
   spacedock or to the kc-dev-flow-2 package in this POC.

Non-goals: an agent-to-agent conversation view; choosing priorities from ADRs
automatically; dot access (deferred in DOT#0008); labelling or renaming any existing agent
other than the ones the worker creates; publishing to the Paseo registry or npm; changing
Paseo.

Budget and stop condition: one implementation cycle. Stop and report, with evidence, if
the plugin API offers no way to list agents with their labels and attention state, or no
way to create an agent from a plugin screen. Also stop and report if the coordinator rule
"answer no permission prompt" can only be kept by the model choosing to obey it: no Paseo
mechanism (plugin hook, profile or tool restriction) keeps the prompt from being answered
by the coordinator. Record the mechanisms checked. A daemon restart, a Paseo change, or
any setting beyond installing and removing this one plugin also stops the work.

Cleanup: remove the plugin, archive every agent the worker created, keep
`~/.paseo/config.json` byte-identical to its pre-run copy, and leave every existing agent's
name and labels unchanged. The POC code may be disposable; record what it does not prove.

## FO alignment

Alignment with the Captain before implementation: not needed. Kent set the direction and
approved this scope on 2026-10-19 in session de83e726, quoted above. POC defaults to no
consultation.

## Acceptance criteria

**AC-1**: The FO board lists every live agent labelled `role=fo` with repo, task, status
and last activity. Its "waiting on Kent" status matches Paseo's own attention state, and an
agent labelled after install appears without a reload.
Verified by: the board's data output for two test FOs (one idle, one with a pending
permission prompt), compared with `list_agents`. Limit: whether the screen renders
correctly is checked by Kent (AC-4).

**AC-2**: "New FO" creates an agent in the chosen workspace with `role=fo` and `repo` set.
"Open coordinator" opens the existing `role=coordinator` agent, or creates exactly one when
none exists.
Verified by: `list_agents` before and after each button's action (or the RPC each button
calls), including a second "open coordinator" that creates no second agent.

**AC-3**: Running the draft skill and profile, the coordinator dispatches a test FO, asks
it for progress and relays the answer as "FO X says …". It does not read the FO's
repository or change workflow state. When the test FO raises a permission prompt the
coordinator receives, the coordinator does not answer it, and the prompt stays pending
for Kent.
Verified by: the coordinator's and the test FO's timelines; `list_pending_permissions`
still showing the prompt after the coordinator's turn ends; the mechanism (or its
absence) that keeps the coordinator from answering, named.

**AC-4**: Kent opens the screen from the sidebar, sees the board, uses "open coordinator",
and opens one FO from its row.
Verified by: Kent's own check from the validation acceptance script; recorded as not run
if he did not run it.
