# 0031. A release is accepted by walking it, and the two plugins meet only at two named schemas

Date: 2026-10-23

## Status

Proposed

## Context

A release whose stories are all development-complete is not thereby usable: `journey-progress.mjs` prints `acceptance: pending delivery acceptance` for it and `cell-contract.md` says that is not delivery acceptance. Two walks of an adopter's releases, run by hand on 2026-10-09 and 2026-10-10 (issue 571), found an action off-screen at common laptop widths that no single task's validation saw, a proof line that could not be performed until an opt-in secret was found, and an asset served as the wrong content type. The label has no consumer: on 2026-10-23, two bounded searches of kc-dev-flow-2, kc-journey-map and `docs/` on origin/main (`git grep -i "delivery acceptance"` and `git grep -i -E 'release.{0,12}(acceptance|walk)|acceptance (task|walk)'`, CHANGELOGs excluded) found only the label's producer, its rendering and its tests. ADR 0012 already records that kc-journey-map and kc-dev-flow-2 are joined only by versioned shapes, each owned by its producer and versioned by `contract-versions.json`.

## Decision

**Words:** 「現在開」 — Captain, 2026-10-10, chat, accepting the First Officer's recommendation that the mechanism's main body lives in kc-dev-flow-2 and a kc-journey-map mode produces the walk list from the map and takes the result back, joined by a declared contract and not shared code; 「准」 — Captain, 2026-10-22, at the ideation gate of `release-acceptance` (gate decision d-51p8nj).

**Options considered:**
- the walk list is `release-walk/v1`, owned and versioned by kc-journey-map; the walk's report is `release-acceptance/v1`, owned and versioned by kc-dev-flow-2; neither plugin imports the other's files; the map changes only by a proposal the Captain accepts (chosen)
- one plugin owns both shapes and the other imports its code — not chosen, a schema lives with its producer (ADR 0012)
- a new story field on the map that records acceptance — not chosen, a clean walk would then write the map without the Captain accepting an edit, and the field has no consumer
- a map-level entry-point field so the walk list names where to start — not chosen, the walker finds the entry and the report records it

**Recommended:** the first option, as the approved design of `release-acceptance` states it.

A release is accepted by operating it end to end from the person's first situation, not by counting finished tasks. kc-journey-map prints the walk list and turns a walk's report into proposed map edits; it writes neither the map nor the report. kc-dev-flow-2 owns the walk, its report and how a failure routes. The two meet only at `release-walk/v1` and `release-acceptance/v1`; each side refuses a schema string it does not know.

## Consequences

This record is Proposed until the kc-dev-flow-2 half merges: only `release-walk/v1`, `journey-walk.mjs` and `journey-accept.mjs` exist when it lands, and `journey-accept.mjs` reads a `release-acceptance/v1` report whose producer is not yet shipped, so its consumer tests use a synthetic report. `journey-accept.mjs` checks the schema string, the journey, the release, that each story is on the release and that each result is one of four; it does not check that every story was walked or that a finding is right. `source.commit` pins the walk to a map revision only when the journey file is committed. A clean walk leaves no mark on the map: its acceptance lives in the caller's own gate record. Reopen if a consumer needs a field the walk list lacks, or if a walk's report proposes an edit the Captain rejects as unfounded.
