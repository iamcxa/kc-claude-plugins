---
title: "POC: does a release contract group work better than a sprint ordinal"
status: implementation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: kc-dev-flow/S10
sprint-readiness: ready
started: 2026-09-14T13:43:29Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: tjxctad7413wyp3acfx8wzzp
gates:
    version: 1
    records:
        - id: gate:tjxctad7413wyp3acfx8wzzp:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:tjxctad7413wyp3acfx8wzzp-backlog-1
              briefing:
                id: briefing:tjxctad7413wyp3acfx8wzzp:backlog:attempt-1:revision-1
                digest: sha256:d5fe505a9e6199259984e6b0b3913c79704d61f809c890b642be45320a4baa38
                room-ref: ./sprint-to-release-contract-migration/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:tjxctad7413wyp3acfx8wzzp:backlog:1
                briefing: briefing:tjxctad7413wyp3acfx8wzzp:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T13:42:57.235563Z"
                decision: approve
                reason: Captain said 派 for both ready items, after selecting POC and the kc-dev-flow/S10 grouping for this one. The seed carries the problem, accepted outcome, non-goals, AC-1..AC-5 and the v3 POC receipt with its decision, falsifier, budget and stop condition.
              application:
                target-stage: ideation
                state: consumed
---

## The problem

Dev-flow groups work with `sprint`, an ordinal. `docs/dev/ROADMAP.md` states the semantics itself:
identifiers are `<product>/S<number>`, with "no cross-product chronology or rank", allocated by
whichever heading lands in `main` first. Planning, meanwhile, has moved to releases:
`kc-journey-map` keeps a `releases:` list of `{id, name, goal}` with every story carrying
`release: rN`, and generates a per-release contract from it. `docs/dev/ROADMAP.md`'s own
`kc-journey-map` S1 and S2 headings are written as releases but numbered as ordinals, and each says
its stored `sprint: SN` is a compatibility identifier held until this migration.

The Captain ruled on 2026-09-14 that the grouping should be a release, that the roadmap and a
release register should be a kc-dev-flow specification rather than this repository's local policy,
that the minimum is `roadmap.md` plus `releases.md` and must work with no user journey present,
and that a release should line up with the repository's real release tag where possible. He then
ruled that this starts as a POC to find out whether that route is actually smoother.

Two assumptions in that route have never been executed. A release group must exist before work
starts, while release-please derives a tag from merged commits and cuts it afterwards, so equality
is impossible and only write-back could hold. And this repository publishes nine plugins on
independent version streams, so a release spanning two products has two tags, not one.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  basis: >-
    Kent selected POC on 2026-09-14 to find out whether the release route is
    smoother before its dependents are admitted. Two assumptions in that route
    have never been executed: tag write-back against a tag that only exists
    after merge, and a release covering two products with two version streams.
    The output is a record, not code, and a stop is a valid outcome.
  route: [build, prove]
  obligations:
    architecture:
      - Re-express real existing state; do not design a schema before the record says the route holds.
    implementation:
      - Write the draft files outside the repository tree and record the result in this work item only.
    testing:
      - AC-1 to AC-5, read at one exact revision that the record names.
  scope_boundary: >-
    No edit to ROADMAP.md, to any work item's grouping fields, to kc-dev-flow,
    or to kc-journey-map. No shipped contract, no schema, no retirement of the
    sprint field.
  poc_decision: Whether dev-flow adopts a package-owned release contract as its execution grouping, or keeps the sprint ordinal.
  poc_falsifier: >-
    Existence-disproof over this repository's real corpus: the live kc-journey-map
    and kc-dev-flow work items cannot be grouped into user-value releases without
    inventing releases nobody would have written, or no drafted release can be
    bound to the cut tags kc-journey-map-v0.2.0 and kc-journey-map-v0.2.1.
  poc_budget: One dispatch, and decision-ready inside 15 minutes; no provider requests and no file edits outside the work item.
  poc_stop_when: >-
    The record lists every non-terminal kc-journey-map and kc-dev-flow item against
    a drafted release or names the items needing an invented one, each drafted
    release carries its exact shipped tag or states why none exists, and the
    two-product cost is stated. Work stops at that observation whichever way it falls.
  poc_artifact: no-code
  poc_safety_boundary: none
  poc_decision_ready_minutes: 15
  decision:
    authority: Kent (Captain)
    at: 2026-09-14T00:00:00Z
```

## Accepted outcome

A record that answers whether to adopt the release contract, produced by re-expressing this
repository's real existing state rather than a fixture. It reports whether the live work items
group into user-value releases without inventing releases nobody would have written, whether a
release can carry a real tag by write-back, and what the two-product case costs. `proceed` returns
a candidate contract shape to the Captain; `stop` records that the sprint ordinal stays.

## Non-goals

- Editing `docs/dev/ROADMAP.md`, any work item's grouping fields, or any file in `kc-dev-flow`.
- Building `roadmap.md` or `releases.md` as a shipped contract, or writing their schema into the package.
- Changing `kc-journey-map`, its journey file, or its generated release contract.
- Retiring the `sprint` field, which stays until a separate Captain-admitted item removes it.
- Deciding delivery, merge, or release-please behavior.

## Acceptance criteria

- **AC-1** A draft `releases.md` and `roadmap.md`, written outside the repository tree, cover every
  non-terminal `kc-journey-map` and `kc-dev-flow` work item, or name the exact items that would need
  a release nobody would have written.
- **AC-2** The draft binds the `kc-journey-map` releases to the real journey file
  `docs/journey/kc-journey-map/draw-a-journey.yaml` and its `r1`/`r2`/`r3` entries, and shows the
  same two files standing alone for `kc-dev-flow`, which has no journey file.
- **AC-3** Tag write-back is exercised against the real cut tags `kc-journey-map-v0.2.0` and
  `kc-journey-map-v0.2.1`: each drafted release either carries the exact tag that shipped it or
  names why no tag exists yet, and the check that would catch a tag naming nothing is named.
- **AC-4** The two-product case is stated with its cost: what a release covering both
  `kc-dev-flow` and `kc-journey-map` does about having two tags.
- **AC-5** `poc_outcome` is recorded as `proceed`, `stop`, or `change`, with the exact revision read
  and the count of items that needed an invented release.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names
the changed premise, affected acceptance evidence, and recommended change or stop.
