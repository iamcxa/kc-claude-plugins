---
title: A prod task's validation gate carries a security review that reaches code the change exposes, on a measured model and effort
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:prod-security-validation-gate:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:prod-security-validation-gate-backlog-1
              briefing:
                id: briefing:prod-security-validation-gate:backlog:attempt-1:revision-1
                digest: sha256:b85c50faff1c18fb4b9b45385e14d0407d4bea0c47c1febf81b8372242159e26
                room-ref: ./prod-security-validation-gate/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:prod-security-validation-gate:backlog:1
                briefing: briefing:prod-security-validation-gate:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-17T06:10:26.538311Z"
                decision: approve
                reason: Captain approved in chat (「准」) the six batch-2 backlog gates presented together in one message, accepting the recommended profiles (pilot; merge-gatekeeper prod) and the stated order
              application:
                target-stage: ideation
                state: pending
---

Filed on the Captain's 「照這樣做」 (chat, 2026-10-16), split out of `prod-security-review-gates` (its amendment 2 keeps the design-stage review there).

## Scope

- The bite: relay PR #347 (agent-front-door) exposed existing comment and session write paths with no cap; that code was outside the PR's diff. Replays on head 1c5b1870 with kc-pr-flow's `tob-security-reviewer` (declared model sonnet): standard tier found nothing; `security_tier: full` found the prompt injection (MEDIUM) and two LOW items but did not trace the session and room handlers, so it missed the unbounded writes. Evidence under `prod-security-review-gates/security/`.
- The bar stays the Captain's amendment-1 criterion of `prod-security-review-gates`: the validation-gate review names the unbounded comment or session write class (code reachable through the change but outside its diff).
- Evidence plan (engineering-reviewer disproof condition, 2026-10-16): at `security_tier: full`, two runs each on Sonnet 5.5, Opus 5.5 and Fable 5.1 on #347 at 1c5b1870, plus one control run per model on a PR with no public exposure; record findings, refusals (the `cyber` safety category), tokens, duration and cost per run.
- Then choose the default model and reasoning level from the measurement; a reasoning level is fixed per agent definition, so effort by complexity means two definitions FO chooses between by a written rule (for example public surface, auth or data access gets the higher one).
- Price per million tokens (input/output), Anthropic API table cached 2026-10-06: Fable 5.1 $10/$50, Opus 5.5 $4/$20, Sonnet 5.5 $2/$10.
- Gap (FO, 2026-10-17, from the Captain's question on #656): `kc-dev-flow-2/skills/ideation/profiles/prod.md` § Security review says nothing about a reviewer that refuses (the `cyber` safety category). A refusal has no `tob_security_review:` root line, so by the shape lock the check would refuse it and hold the ideation gate (inferred from the rule, not tested); the worker has no instruction and may stall or rerun. Decide the refusal handling with the model comparison.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it (his words are at the top of this file).
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
