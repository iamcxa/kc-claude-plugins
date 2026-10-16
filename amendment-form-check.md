---
title: design_surfaces.py does not check a Captain amendment's own form
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:amendment-form-check:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:amendment-form-check-backlog-1
              briefing:
                id: briefing:amendment-form-check:backlog:attempt-1:revision-1
                digest: sha256:14cbf6e42f10d8251d22634c12e4fe1cfec16a908b4d0566a24a3587f0de3797
                room-ref: ./amendment-form-check/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:amendment-form-check:backlog:1
                briefing: briefing:amendment-form-check:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-16T03:13:50.642844Z"
                decision: approve
                reason: 'Captain approved batch 1 (「批准」): schedule as Pilot and enter ideation; as the gate question states, this accepts profile pilot and five parallel ideations with dev2-laws-check''s design read by the other four for overlap.'
              application:
                target-stage: ideation
                state: consumed
---

Filed from a learn package-issue candidate the Captain approved (「好」, chat, 2026-10-15). The observer reports on `delivery-gate-verdict-form` and `fo-lifecycle-mod` found FO-written amendments that break the README `## Captain amendments` rules, and `scripts/design_surfaces.py check` passed both tasks.

## Scope

- An amendment `Design:` line carries FO's own sentences beyond the Captain's words and his `Asked:` question (delivery-gate-verdict-form amendment 2; acceptance criterion AC-12 then attributed one of them to the Captain). Rule: "FO adds no words of its own".
- Replacement criteria AC-9 to AC-14 under amendment 2 lack "Amended by Captain, amendment N" (delivery-gate-verdict-form). Rule: "writes any replacement as a new `**AC-N**` ... that says 'Amended by Captain, amendment N'".
- A `Supersedes:` line reads `none` while criteria were moved under that amendment (fo-lifecycle-mod amendments 3 and 6). `design_surfaces.py` checks only that a superseded id is no longer declared, not that a moved criterion is named in `Supersedes:`.
- Candidates for ideation to keep or drop; the first is a judgement of meaning and may stay with the observer.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
