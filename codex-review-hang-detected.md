---
title: A Codex review that stops updating is detected, re-requested once, and named unread at the merge ask
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:codex-review-hang-detected:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:codex-review-hang-detected-backlog-1
              briefing:
                id: briefing:codex-review-hang-detected:backlog:attempt-1:revision-1
                digest: sha256:8d6370a2df1cee659d9ed60f37236370a6b23366d940c6c00c446a78f45549da
                room-ref: ./codex-review-hang-detected/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:codex-review-hang-detected:backlog:1
                briefing: briefing:codex-review-hang-detected:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-25T14:15:37.472492Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-25) answering the batch-6 backlog sitting, which listed this task's backlog briefing-1 question
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: batch 6 (2026-10-25): the Captain 「可以」 (chat), answering 「需要你決定：這份第 6 批的清單可以嗎？」 about FO's batch-6 list, item 4 「Codex 審查卡住會自動偵測（新票）」.
- Bite (FO, 2026-10-23 to 2026-10-25): the Codex code review stayed `running` with no update to its summary comment on iamcxa/kc-claude-plugins #709 (07:37Z to 12:57Z), #713 (12:38Z, then again after a 13:38Z re-request through 15:16Z), #714 (twice), #716 (04:28Z, then again after a 05:18Z re-request through 06:01Z). A single `@codex review` re-request cleared it within minutes three times; #713 and #716 never answered. Each was found by FO by hand from the summary comment's `Running since` time.
- Facts: `extensions/codex/codex_review.py` exits 3 (`running`) for all of these with no age; the summary comment carries `codex-review-state:v1` JSON and a `Running since <time>` field (read 2026-10-25).
- Outcome: the codex reader or `pr_watch.py wait` reports a running review older than a stated limit as stalled, FO re-requests once, and a second stall makes the merge ask name Codex as not read (the README rule already covers the naming).
- Upstream first: `extensions/codex/EXTENSION.md` Read rules, `codex_review.py`, `pr_watch.py`.
- Non-goals: changing Codex itself; counting a stalled review as a round.

## FO alignment

Alignment: not needed: an observed failure in one reader; the limit is a design value to state at ideation.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
