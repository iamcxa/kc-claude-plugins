---
title: Kent starts and watches every FO from one Paseo board, and only he answers a permission prompt
variant: kc-dev-flow-2
merge: pr
status: backlog
---

## Scope

- Source: the Captain's answer 「可以，但他應該也要可以讀 ADR mcp 看下這個旅程地圖大概了解一下 https://github.com/iamcxa/kc-claude-plugins/pull/676」 (2026-10-19T14:18Z, Claude session de83e726), to the coordinator's question 「要不要開一筆正式任務，交付這個看板和總指揮，並把「所有 agent 都不能回應權限」那項 Paseo 設定一起做進去？」. Filing only; it sets no profile and no Paseo config.
- Bite: DOT#0007 (iamcxa/dot-decision-log PR #9) ran the first cross-FO round over Claude Code SendMessage; held cross-mode messages expired unseen and the coordinator relayed by hand. DOT#0008 moved the round to Paseo and recorded that a receiving FO can answer another agent's permission prompt with `respond_to_permission`, with nothing but prose stopping it.
- Consumer: the Captain (one entry point that shows which FO is busy with what and opens sessions, his words 2026-10-19T10:53Z: 「只負責啟動與溝通其他 FO不自己檢查工作內容」) and the coordinator agent the board runs.
- Part 1, the board and a restricted coordinator: the archived POC `paseo-fo-console-poc` (docs/dev2-poc; AC-1 to AC-3 passed at 79a712d7, archived undelivered with `boundary-crossed: external-seam`; code on branch spacedock-ensign/paseo-fo-console-poc under scripts/paseo-fo-console-poc/, with a coordinator/EXTENSION.md draft). Its stated holes: the coordinator's tool lock rests on a plugin `before agent.create` hook and the undocumented `resolveInheritedProviderConfig`; the coordinator can `create_agent` an unrestricted child; `requiresAttention` stays false while a prompt is pending, only `pendingPermissions` shows it.
- Part 2, only the Captain answers a permission prompt: the proposed route is Paseo's `paseoTools.disabledTools` turning `respond_to_permission` off for every agent. Unverified; changing Paseo config needs the Captain's approval.
- Part 3, the coordinator reads decision records: through the ADR MCP, read-only. Depends on kc-decision-log P1 (journey map docs/journey/kc-decision-log/, PR #676 merged; Pilot release S01, S02, S04, S10, S11, where an authorized client reads exact-version decisions). P1's appetite, Development Brief and handoff are pending, and the dot-decision-log local server refuses every data route and MCP call until an identity transport and owner exist. Not built; this part waits for it.
- Upstream first: Paseo's own plugin and config docs and source for `disabledTools`, `before agent.create` and permission routing, not a sibling FO's usage; the kc-dev-flow-2 `peers` extension for the message rules.
- Non-goals: to be set at ideation. The coordinator does not inspect work content or repositories.

## FO alignment

Owner: the Captain ruled 2026-10-20 (「我覺得不太適合，這個 poc 應該要另外找人做，因為它還沒進 dev2 life cycle」) that this work is not this FO's: it is a POC run outside the dev2 lifecycle by another agent. This FO does not dispatch it.

Alignment: needed before ideation: whether parts 1 and 2 go ahead before kc-decision-log P1, and whether part 2's Paseo config change is approved, are the Captain's.
Release review: not needed: FO tooling, on no product journey map.
Surfaces: ui
Visible change: the Captain opens and watches FO sessions from one Paseo panel, and a permission prompt from any agent can be answered only by him.

## Peers

- Peer: FO coordinator (cross-FO trial) = Paseo agent a88dedae-9e10-44b0-a00a-4153c889e063 (Claude session de83e726); reply, 2026-10-19. Asked this FO to file the task; FO checked the Captain's answer and the question before it in session de83e726's transcript, PR #676's merged state and the POC branch head 79a712d7 before filing.
