---
title: A peer FO's status reaches other FOs fresh, so a stale line is not relayed to the Captain
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:peer-status-reaches-fresh:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:peer-status-reaches-fresh-backlog-1
              briefing:
                id: briefing:peer-status-reaches-fresh:backlog:attempt-1:revision-1
                digest: sha256:fab4edc4bff6684565f1a88b14d19171662102bf71f1305a2d93f6b1874ba04d
                room-ref: ./peer-status-reaches-fresh/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:peer-status-reaches-fresh:backlog:1
                briefing: briefing:peer-status-reaches-fresh:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-30T08:18:32.199545Z"
                decision: approve
                reason: The Captain 「對，全准且全確認」 (chat, 2026-10-30), answering FO's joint batch-11 backlog sitting of six gates whose ask was 「決定：六張全准進設計，並確認上面三件事？要改哪張直接說。」; accepts FO's recommendation and the confirmations stated in the gate question.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: interview round 004 finding (state .notes/fo-feedback/round-004.md, 2026-10-28), proposed by FO; the Captain chose theme B for batch 11 (「那就 B 可以」, chat, 2026-10-30), whose row named 「FO 之間狀態過期」.
- Bite: on 2026-10-28 relay told the Captain Web's half waited on his merge after it had merged (b71f912), and web's status named a v0 step CL had already cleared; web corrected relay twice. Their originals sit in their sessions; this is the two-sided account.
- Upstream first: `extensions/peers/EXTENSION.md`, `extensions/paseo/EXTENSION.md`, Paseo agent labels (next, next-owner).

## Non-goals

- A shared status store or a new service; receipts for every message.

## Budget

- One package PR to the peers and paseo extension text; no new script.

## Stop condition

- The two 2026-10-28 events replay as prevented by the stated rule (a peer pushes merged, released or unblocked when it happens, or a Captain action named from a peer is checked at its source first).

## FO alignment

Alignment: not needed before ideation: text inside the extensions' existing authority.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
