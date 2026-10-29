---
title: Batch-10 obligations owed after release are met or returned to the Captain
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the batch-10 chief-engineer delivery review (2026-10-29), listing what is owed after the release that carries PRs #748 to #751; filed by FO with no Captain ruling yet. Precedent: amendment-form-check-round3-followups.
- Owed: (1) #751 adr-reserved-when-design-names-one AC-3 native build-and-spawn proof at the first Pilot or Prod implementation-1 dispatch after that release (its Captain amendment 1, 2026-10-29); (2) #749 captain-amendment-form-checked's law L3 is inactive until `dev2-laws.yml` on spacedock-state/dev2 moves its pin (22219a3e at review time); five live tasks it newly refuses (kc-decision-log-handoff-trial, adr-required-statement, relay limit-telemetry-posthog, qnow branch-hours-generate-starts and operator-secret-hardening) are repaired before the pin moves, then one real state-push run is watched; (3) #748 gate-requires-recorded-reviews: one observed adopted delivery gate; (4) archive-waits-for-observer-report reserves its ADR by hand (its placeholder sits outside the headings #751 reads).
- Known limit, not owed: #751 reads only some design headings (6 of 13 tasks with an ADR placeholder use one it reads).

- Added 2026-10-29: Codex P2 on PR #749 (review 5695880112, kc-dev-flow-2/scripts/laws_check.py): an amendment with an unmatched fence makes laws_check report `cannot judge` (exit 2) even when its bytes are unchanged, so unrelated updates of that task fail the law indefinitely; accept byte-identical records before the unmatched-fence comparison. Fix before moving the dev2-laws pin, since L3 is inactive until then.
## Non-goals

- New checks; widening #751's headings (a separate task if the Captain wants it).

## Budget

- No package PR unless an obligation fails; state edits and one CI pin bump PR at most.

## Stop condition

- Each of the four is met with its receipt recorded here, or returned to the Captain with what failed.

## FO alignment

Alignment: not needed before ideation: obligations from approved tasks.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
