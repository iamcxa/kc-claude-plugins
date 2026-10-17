---
title: chief-engineer and engineering-reviewer start on recorded events, not on FO's judgement
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:special-role-triggers:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:special-role-triggers-backlog-1
              briefing:
                id: briefing:special-role-triggers:backlog:attempt-1:revision-1
                digest: sha256:74c822b9bd672956a82c4848d8e7232193807f3120443cf9287065eab87beb1d
                room-ref: ./special-role-triggers/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:special-role-triggers:backlog:1
                briefing: briefing:special-role-triggers:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-17T06:10:14.079276Z"
                decision: approve
                reason: Captain approved in chat (「准」) the six batch-2 backlog gates presented together in one message, accepting the recommended profiles (pilot; merge-gatekeeper prod) and the stated order
              application:
                target-stage: ideation
                state: consumed
---

Filed on the Captain's 「可以，建成待辦」 (chat, 2026-10-16), after FO listed six moments in one session where a special role applied and was not used. The README says FO calls them when it judges they are needed; FO rarely judges its own work to need a second opinion, the same failure as the relay prod task where risk-selected security review never fired.

## Scope

- Evidence, session of 2026-10-15/16 on this workflow:
  - chief-engineer would apply: delivery-gate-verdict-form, three Codex P1 rounds of one class (the Captain asked FO to step back twice); dev2-laws-check, a fourth P1 of one class; prod-security-review-gates, its stop rule fired twice and the Captain asked for a rethink three times.
  - engineering-reviewer would apply: FO-proposed amendments that replaced an approved design (delivery-gate-verdict-form amendment 2, dev2-laws-check amendment 1); narrowing a stated guarantee (dev2-laws-check, Cycle 3); accepting residual security risk on a prod design (prod-security-review-gates, first actual use on 2026-10-16).
- Candidate triggers: chief-engineer when FO's circuit breaker fires (the same class of finding a second time) or the Captain asks FO to step back, before FO proposes a new route; engineering-reviewer when FO proposes an amendment that replaces approved design, narrows a guarantee, or accepts a risk, with its verdict in the gate question.
- Candidate enforcement: a `Reviewer:` line the check scripts or the observer can require when the event is in state (an amendment entry, a Feedback Cycles line naming a repeated class).
- Cost: each call is an Opus run; count the triggers per batch before choosing.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it (his words are at the top of this file).
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
