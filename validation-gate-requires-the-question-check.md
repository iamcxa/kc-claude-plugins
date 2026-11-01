---
title: A validation gate cannot be bound before the delivery question check passes
status: backlog
variant: kc-dev-flow-2
profile: pilot
gates:
    version: 1
    records:
        - id: gate:validation-gate-requires-the-question-check:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:validation-gate-requires-the-question-check-backlog-1
              briefing:
                id: briefing:validation-gate-requires-the-question-check:backlog:attempt-1:revision-1
                digest: sha256:2cff60765797645d97fe6b7571907bb19f2f1737186af25b4515bb6e3c3e02c5
                room-ref: ./validation-gate-requires-the-question-check/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:validation-gate-requires-the-question-check:backlog:1
                briefing: briefing:validation-gate-requires-the-question-check:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-01T17:47:59.462076Z"
                decision: approve
                reason: The Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering the batch 12 sitting 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」; approves Pilot, this outcome and these bounds, with the stated change.
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」, item 2: 開候選「`gate prepare` 要先擋下沒跑 `delivery_gate question` 的情況」.
- Bite: batch 11, 2026-11-01. FO bound four validation briefings without running `delivery_gate.py question`, and bound #757's on text that had failed it. Only the observers found this, after merge (`_archive/*/observer.md`).
- Consumer: every FO binding a validation gate.
- Upstream first: `spacedock gate prepare` is engine-owned, so check Spacedock first and say what it offers; `scripts/delivery_gate.py`, `scripts/laws_check.py`, `references/sd/workflow.md`.

## Non-goals

- A Spacedock change from this repository; reading the verdict.

## Budget

- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition

- A replay of the batch 11 sequence is refused or reported at or before binding, by a check that runs at that moment. If no package seam can run then, stop and return that to FO with the nearest available moment.

## FO alignment

Alignment: needed before ideation; the scope is the Captain's ruling.
Result: aligned at backlog: Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
