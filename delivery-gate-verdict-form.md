---
title: delivery_gate.py accepts only "Verdict PASSED", a form no instruction asks validators to write
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:delivery-gate-verdict-form:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-gate-verdict-form-backlog-1
              briefing:
                id: briefing:delivery-gate-verdict-form:backlog:attempt-1:revision-1
                digest: sha256:6a3895b16481341591719201ccf2b3b09407a1c5768747f3a34d2021f08f4a53
                room-ref: ./delivery-gate-verdict-form/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-gate-verdict-form:backlog:1
                briefing: briefing:delivery-gate-verdict-form:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-15T00:24:46.8908Z"
                decision: approve
                reason: 'Captain approved both backlog gates (「准」): schedule as Pilot and enter ideation before the next kc-dev-flow-2 release and adopter sync.'
              application:
                target-stage: ideation
                state: consumed
---

Filed on the Captain's 「開」 (2026-10-14), from a package issue the spacedock-dev/subspace-relay FO reported: on relay task `owner-sees-all-feedback-page` (PR spacedock-dev/subspace-relay#368) the validator wrote `Verdict: PASSED, recommended. Artifact: candidate 985200258…`, and `delivery_gate.py check` exited 2 ("no passing validation report … names a candidate SHA"); the relay FO sent the validator back for a one-line report repair (relay state commits 387b786 and 940921b). On this workflow's task `fo-lifecycle-mod` a validator also wrote a "Verdict recommended: PASSED" form.

## Scope

- Confirmed 2026-10-14 on origin/main: `PASSED = re.compile(r"Verdict PASSED[\s\S]{0,160}?" + SHA)` in `kc-dev-flow-2/scripts/delivery_gate.py`; the docstring says only "`Verdict PASSED` within 160 characters". Nothing in the validation skill or stage text states that exact line.
- Every merge ask runs this check, so each new validator wording holds a delivery.
- Candidate fixes: accept a tolerant verdict form (for example `Verdict:? (recommended:? )?PASSED`, case-insensitive), or state one exact verdict line in the validation stage contract and check it there; which, and whether the checker or the contract owns it, is for ideation. Related: `dev2-laws-check`.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
