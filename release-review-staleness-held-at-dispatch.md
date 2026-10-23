---
title: The first implementation dispatch of a task in a release is held while the release's review record is older than the map
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「照更正後的建議退回設計重做」 (chat, 2026-10-23), answering FO's 「「擋派工」這一段，是照我更正後的建議退回設計重做（不涵蓋），還是照 D2 不做（涵蓋）？」; recorded as release-acceptance Captain Amendment 2, which moves that task's AC-1 to AC-4 here.
- Bite: issue #571 item 1, qnow R4 (2026-10-10): an implementation was dispatched after the release changed (signals 1 and 2 recorded) with no new review. Evidence copies: release-acceptance/r4-acceptance.md.
- What exists (release-acceptance implementation phase-1 report, 2026-10-23): since #704 the review record is a file `reviews/<journey>/<release-id>.md` with `Reviewed:` and `map at <commit>`, checked by kc-journey-map/lib/journey-review.mjs; the design's `Release changed:` and timed `Release review:` marks do not exist on main; staleness can be read by comparing the map at the record's commit with the map now; workflow.md is under a word budget (ADR 0020) while extensions and pr_watch.py next: lines cost no README words; ADR 0029 D2 (no seed hold) is a different moment, ruled not to cover this.
- Shape asked for: hold the first implementation dispatch of a task in a release while its review record is stale, with the check placed where this package can run it.
- Upstream first: Spacedock dispatch build (no precondition input as of 0.27.2), kc-journey-map journey-review.mjs and the review record, kc-dev-flow-2 pr_watch.py and extensions.
- Non-goals: the release walk (release-acceptance keeps it); a seed-time hold (D2).

## FO alignment

Alignment: needed at ideation; where the check lives and whether it raises the word budget are his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
