---
title: Release-walk picky reviewers can run on Gemini through Paseo
status: ideation
variant: kc-dev-flow-2
profile: pilot
gates:
    version: 1
    records:
        - id: gate:picky-reviewers-may-run-on-gemini:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:picky-reviewers-may-run-on-gemini-backlog-1
              briefing:
                id: briefing:picky-reviewers-may-run-on-gemini:backlog:attempt-1:revision-1
                digest: sha256:a4f46fda7b74cf046f55add81715ac4393dc096ecdd9cc8ff9903abc1d110d86
                room-ref: ./picky-reviewers-may-run-on-gemini/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:picky-reviewers-may-run-on-gemini:backlog:1
                briefing: briefing:picky-reviewers-may-run-on-gemini:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-02T03:30:41.220002Z"
                decision: approve
                reason: The Captain 「可以」 (chat, 2026-11-02), answering 「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」; approves Pilot, this outcome and these bounds.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain, chat 2026-11-02: 「挑剔使用者應該要可以改，甚至使用 gemini 的模型」. Batch 12 sitting: the Captain 「可以」 (chat, 2026-11-02), answering 「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」.
- Bite: `extensions/release-acceptance/EXTENSION.md` says reviewers run "on different Claude models", so a Gemini reviewer is outside its words, though `release_acceptance.py` reviewer `model` is free text.
- Consumer: the next release walk in a repository listing release-acceptance; subspace-relay lists it (read 2026-11-02).
- First a POC, before any package text changes: one Gemini reviewer through Paseo's `antigravity` provider, in a restricted mode, walks a small part of an existing journey and returns a report that `release_acceptance.py` accepts. If it cannot, stop and return that to FO.
- If it can: the extension text stops naming one family and says a non-Claude reviewer is launched through Paseo with an explicitly chosen mode. The choice stays in the task's `Reviewers:` field, not the model roster.
- Antigravity's Paseo default mode is `full-access`; the trial must not use it. FO's standing rule: never `--dangerously-skip-permissions` with agy.
- Upstream first: `extensions/release-acceptance/EXTENSION.md`, `release_acceptance.py`, Paseo `antigravity` provider and its modes, `kc-team-ops` gemini skill.

## Non-goals

- Gemini as a stage worker, FO or special role; proving two models find different things; changing the design director's model rule.

## Budget

- One package PR changing the extension text, after the POC. Workflow word budget unchanged.

## Stop condition

- The POC's report passes `ra check` at its walk tier and its trace shows the requested model and restricted mode; or the task stops with that evidence and no package change.

## FO alignment

Alignment: needed before ideation; the scope is the Captain's ruling.
Result: aligned at backlog: Batch 12 sitting: the Captain 「可以」 (chat, 2026-11-02), answering 「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
