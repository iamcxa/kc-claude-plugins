---
title: "POC: does a release contract group work better than a sprint ordinal"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint:
sprint-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: tjxctad7413wyp3acfx8wzzp
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
