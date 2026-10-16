# 0017. History laws judge only events after an anchor

Date: 2026-10-16

## Status

Accepted

## Context

dev2's checks (`observer_check.py`, `dispatch_records.py`) run only when a first officer or worker runs them, and the 2026-10-14 failures were at that layer: an archive with no observer report, dispatches built before `dispatch_records.py --names`. A history check can run on every push to the state branch, but a law added after history exists fails on events that predate it. Measured 2026-10-16 on this repository's state branch at its commit `e73634e6`: with no anchor L1 fails 15 of 25 tasks and L2 fails 10 of 48 records, because the rules came later. A violation is a committed fact that cannot be repaired.

## Decision

**Words:** 「准」 — Captain, 2026-10-16, at the batch-1 ideation gate for `dev2-laws-check`, accepting D1 to D4 as the gate question recommends them.

**Options considered:**
- every law judges only events in commits that are strict descendants of an anchor commit the adopter names for it; a law with no anchor prints `not judged`; moving the anchor is the acceptance of an earlier violation (chosen)
- judge all history — not chosen: red on 15 of 25 tasks forever
- a waiver list per violation — not chosen for v1: moving the anchor is the acceptance, and a list is the next step only if that hides something that bites

**Recommended:** the first option, as the Captain accepted.

`laws_check.py` judges an event only when its commit is a strict descendant of the law's anchor; a missing anchor, an anchor that is not an ancestor of the judged revision, or shallow history exits 2 and is never read as green. An archive move is not an event: a record's adding commit is found with rename detection on.

## Consequences

An adopter turns a law on by naming an anchor in its workflow file, and a release that adds a law turns no adopter red. The run detects after the push and cannot stop `merge guard`. A violation before the anchor is never reported by CI again. Reopen if moving anchors hides violations that later bite.
