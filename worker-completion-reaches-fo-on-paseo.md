---
title: A stage worker's completion reaches the FO on Paseo, whichever model it runs on
status: backlog
variant: kc-dev-flow-2
profile: pilot
---

## Scope

- Source: Batch 12 sitting: the Captain 「可以」 (chat, 2026-11-02), answering 「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」. FO had stated: 「工作者完成時要確實通知到 FO」, 「排第一」.
- Bite: batch 12, 2026-11-01. Four Claude ideation workers spawned with `paseo agent run --no-wait` were told to send completion to `main`; all four `SendMessage(to="main")` calls were refused because `main` resolves to the worker itself. Three fell back to `send_agent_prompt`; the roster worker ended with no signal, and the Captain asked 「卡住了嗎」 about nine hours later. `agent run` has no notify option; `create_agent` defaults `notifyOnFinish` true.
- Consumer: every FO dispatching a worker through Paseo.
- `main` is enforced by the `dispatch_records.py` regex, a `references/sd/workflow.md` sentence pinned in `test_sd_dispatch.py`, and `MAIN_LINE` in `replay_dispatch.py`. A Claude worker through Paseo hands publication to FO as a Codex worker does.
- Upstream first: Spacedock's completion contract, Paseo's own skill, `extensions/paseo/EXTENSION.md`.

## Non-goals

- A polling watcher; a change to Spacedock or Paseo; workers on non-Paseo hosts.

## Budget

- One package PR. Keep the rule in `extensions/paseo/EXTENSION.md`; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition

- A real Claude worker and a real Codex worker through Paseo each deliver a completion the FO receives, with no fallback improvised by the worker. If `create_agent`'s callback does not reach the FO on a stage worker, stop and return that evidence to FO.

## FO alignment

Alignment: needed before ideation; the scope is the Captain's ruling.
Result: aligned at backlog: Batch 12 sitting: the Captain 「可以」 (chat, 2026-11-02), answering 「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
