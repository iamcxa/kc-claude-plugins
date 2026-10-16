# 0017. History laws judge only the events a push adds

Date: 2026-10-16

## Status

Accepted

## Context

dev2's checks (`observer_check.py`, `dispatch_records.py`) run only when a first officer or worker runs them, and the 2026-10-14 failures were at that layer: an archive with no observer report, dispatches built before `dispatch_records.py --names`. A history check can run on every push to the state branch, but a law added after history exists fails on events that predate it. Measured 2026-10-16 on this repository's state branch: judging the whole history to its commit `e73634e6`, L1 fails 15 of 25 tasks and L2 fails 90 of 149 records, because the rules came later. A violation is a committed fact that no later commit un-writes.

## Decision

**Words:** 「就按照新的建議」 — Captain, 2026-10-16, chat, answering 「這三個新建議可以嗎？」 (item 1: 「dev2-laws-check（#651）：改成「只檢查這次推送新增的事件」，不再保證「歷史上的違規永遠是紅燈」。」)

**Options considered:**
- each run judges only the events the commits of the push add (`before..after`), reported once (chosen)
- per-law anchors with a run red until the anchor moves (the first build of this task; withdrawn by the Captain's amendment)
- a waiver list per violation — not chosen: with nothing staying red there is nothing to waive

**Recommended:** the first option, as the Captain accepted.

`laws_check.py` reads each commit of `--before..--after` at its own commit and judges the events that commit adds; a `--before` or `--after` that is not a commit, or a range commit with no parent in the clone, exits 2 and is never read as green. An archive move is not an event: rename detection is on.

## Consequences

Adoption starts green and a violation is reported once. A red run that is not seen leaves no trace after the next push, so GitHub's failed-run notice is the whole signal. The run detects after the push and cannot stop `merge guard`. Reopen if a violation reported once is recorded as missed.
