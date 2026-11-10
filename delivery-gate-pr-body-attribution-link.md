---
title: delivery_gate.py stops holding a gate text that names the PR body for its attribution link
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:delivery-gate-pr-body-attribution-link:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-gate-pr-body-attribution-link-backlog-1
              briefing:
                id: briefing:delivery-gate-pr-body-attribution-link:backlog:attempt-1:revision-1
                digest: sha256:f99c4b53a57c195cfafe1508865745a3308c963d5bfd4c88b028ab864f1297e4
                room-ref: ./delivery-gate-pr-body-attribution-link/review/backlog/briefing-1
---

## Scope

- Source: FO's D2 disposition at the delivery-gate-ignores-url-paths-and-data-fences ideation (2026-11-09), whose recommendation was a separate backlog task; no Captain words yet; the backlog gate is his.
- Bite (that ideation worker's report, reproduced on 0.36.0, not re-run here): a gate text naming `review/pr-body.md` holds on 0.36.x under the FO-named-card link rule, on the PR body's attribution link; FO's workaround is to describe the PR body without its path or record the link as a step.
- Upstream first: the named-card link handling in `kc-dev-flow-2/scripts/delivery_gate.py` and its tests.
- Non-goals: the five inputs delivery-gate-ignores-url-paths-and-data-fences covers.

## Budget
- One package PR touching delivery_gate.py and its tests; workflow word budget unchanged.

## Stop condition
- A gate text naming the PR body passes without a recorded link step, and a real Captain link in a named card still holds, each with a falsifier.

## FO alignment

Alignment: not needed; a gate-check false positive found during batch 18 ideation.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
