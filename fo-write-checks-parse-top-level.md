---
title: The FO-write checks parse only top-level declines and unfenced Scope, closing two Codex round-3 edge cases
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:fo-write-checks-parse-top-level:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fo-write-checks-parse-top-level-backlog-1
              briefing:
                id: briefing:fo-write-checks-parse-top-level:backlog:attempt-1:revision-1
                digest: sha256:8bcea6368a28ede1bb44811cc281012dda12f422dcbde366130b6862102c29a2
                room-ref: ./fo-write-checks-parse-top-level/review/backlog/briefing-1
---

## Scope

- Source: Codex round 3 on iamcxa/kc-claude-plugins#687 at head 2b86a62490de623faf7365ef29931a9d5c35e3f9 (evidence=review:5587635979, 2026-10-20), two P2 findings that FO declined in the fo-write-rules-checked validation gate summary under the README round-3 rule ("From round 3 a finding that is neither does not start a repair cycle … files it as a new backlog task").
- Finding 1, `kc-dev-flow-2/scripts/delivery_gate.py` `declined_items()`: a decline reason that itself mentions another `Declined:` or `FO declines:` label yields overlapping items for the outer and nested match, so one real item can satisfy two F-numbered findings and the gate proceeds with one finding undisposed. Count only non-overlapping top-level items.
- Finding 2, `kc-dev-flow-2/scripts/design_surfaces.py`: the Scope search selects a fenced `## Scope` example placed before the real section; the example is unchanged in baseline and working copy, so real Scope edits compare equal and the hold returns clean. Parse the unfenced document, as the amendment parser already does.
- Decline reason at the gate: neither is P1 or Material; both need a crafted text (a nested decline label, a fenced Scope example ahead of the real one) that no task in the four measured state checkouts holds — to re-measure at ideation.
- Bite: none observed beyond the reviewer's constructed examples.
- Non-goals: any other change to the two scripts.

## FO alignment

Alignment: not needed before ideation; both findings name their fix.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
