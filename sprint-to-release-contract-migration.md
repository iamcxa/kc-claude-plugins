---
title: "POC: does a release contract group work better than a sprint ordinal"
status: validation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: kc-dev-flow/S10
sprint-readiness: ready
started: 2026-09-14T13:43:29Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-sprint-to-release-contract-migration
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

## Stage Report: implementation

- DONE: Count the invented-release rate against the real corpus.
  22 non-terminal `kc-journey-map`/`kc-dev-flow` work items read via `spacedock status`; 12/22
  (55%) bind to an already-named release, 10/22 (45%) need an invented or unlanded release, and
  only 3/22 (14%) are strictly worse off under a release contract than under the sprint ordinal
  today. Full per-item table in `poc-roadmap.md`.
- DONE: Exercise tag write-back and journey binding against the real tags and journey file.
  `kc-journey-map-v0.2.0` binds to r2 as majority content but also carries r1-shaped PR #415 (mixed
  tag); `kc-journey-map-v0.2.1` binds to no release id (pure bugfix patch tag). Both are hand-matched
  with no automated check today (`scripts/version-parity-check.sh` has no release-id notion; grepped
  `kc-journey-map/lib/lint.mjs` and `lib/release-contract.mjs` at `origin/main` for "tag" — no hits).
  `kc-journey-map` releases r1/r2/r3 read directly from `docs/journey/kc-journey-map/draw-a-journey.yaml`
  `releases:`; `kc-dev-flow` has no journey file and stands alone on ROADMAP sprint prose.
- DONE: Record `poc_outcome` with the exact revision, invented-release count, and two-product cost.
  `poc_outcome: stop` at `origin/main@0bbf6233831543b8e8874a44a73b4868f6a1ed50` /
  `spacedock-state/dev@0daaab3db1415ec2259784c9b18b21c9940721a2`; two-product cost is zero
  occurrences for the named pair kc-dev-flow+kc-journey-map, but one same-shaped case
  (`journey-map-poc`, kc-team-ops+kc-journey-map) already exists in the excluded 4-item set.

### Summary

Real-corpus POC on whether a release contract beats the sprint ordinal. 10 of 22 live
`kc-journey-map`/`kc-dev-flow` items need an invented or unlanded release, but only 3 are actually
worse off than under the sprint ordinal; both checked shipped tags bind only approximately to a
release, hand-matched, with no automated check to catch a false binding; and the two-product cost
this route was meant to justify has zero occurrences for the named pair (one same-shaped case
exists one product-pair over). Recommendation recorded below: `stop` — keep the sprint ordinal, do
not schedule a shipped release-contract migration on this evidence.

Revision read: kc-claude-plugins `origin/main` @ `0bbf6233831543b8e8874a44a73b4868f6a1ed50`
(2026-09-14T21:45:11+08:00) for `docs/dev/ROADMAP.md` and
`docs/journey/kc-journey-map/draw-a-journey.yaml` (diffed against the stale local checkout tip
`7b103a10`, identical content on both files — no drift). Spacedock state checkout
`spacedock-state/dev` @ `0daaab3db1415ec2259784c9b18b21c9940721a2` for the work-item corpus, via
`spacedock status --workflow-dir docs/dev --json --fields slug,status,sprint,product,title --limit 0`
(94 total entities).

Draft artifacts (written outside the code repository tree, inside this work item per the
`implementation` obligation): `docs/dev/.spacedock-state/sprint-to-release-contract-migration/poc-roadmap.md`,
`docs/dev/.spacedock-state/sprint-to-release-contract-migration/poc-releases.md`.

**AC-1 — corpus coverage.** 22 non-terminal work items carry `product` in
`{kc-journey-map, kc-dev-flow}` (4 + 18). 4 further items (`default-to-the-journey-alone`,
`collapse-to-one-board`, `evidence-means-executable-code`, `reverse-a-story-map-from-linear`) carry
`product: kc-team-ops`, `sprint: journey-map-poc` and are excluded by the strict product filter —
named in `poc-roadmap.md` because `default-to-the-journey-alone` is, by slug, the exact r1 story in
the journey file, sitting under a different product label than the journey it belongs to. Within
the 22-item corpus: 12 (55%) bind to a release that already exists and was already named for a
reason other than this migration — a ROADMAP sprint heading or the separately-named
`ship-cloud-wrapper-r3` group. Of those 12, only `dev-94-ship-flow-thin-wrapper` (S9) binds to a
heading that itself carries written End-value/Exit prose; S7/S8 are bare Linear-project links and
`ship-cloud-wrapper-r3` is a captain-named group never written as a ROADMAP heading — zero live
items are stamped S1/S2/S4/S5, the headings that do carry release-shaped prose. 10 of 22 (45%) need
an invented release or cannot be admitted to the release their stamped ordinal names: 6 items carry
no `sprint` value at all; 2 items (`retire-the-provider-backed-planning-path`, this POC itself) are
stamped `kc-dev-flow/S10`, an ordinal with no landed ROADMAP heading yet; 1 item
(`spacedock-project-status-updates`, `S3`) is stamped a heading ROADMAP has since marked RETIRED for
new admissions; 1 item (`extract-the-journey-map-plugin`) is packaging/publishing infrastructure
that no journey story covers. Only 3 of the 10 are strictly worse off under a release contract than
under the sprint ordinal today (the 2 S10 items and the 1 packaging item); the other 7 are equally
unlabeled or blocked under either system. Full corpus, per-item binding, and this split are in
`poc-roadmap.md`.

**AC-2 — journey binding.** `kc-journey-map` releases r1/r2/r3 are read directly from the journey
file's `releases:` list (goal text quoted verbatim in `poc-releases.md`); 3 of the 4 non-terminal
`kc-journey-map` items bind to r1/r2 by story/system-note match, 1 (`extract-the-journey-map-plugin`)
does not bind to any journey story. `kc-dev-flow` has no journey file (`docs/journey/kc-dev-flow/`
does not exist) and stands alone on ROADMAP sprint prose read as releases directly — same two draft
files, no journey column.

**AC-3 — tag write-back.** `kc-journey-map-v0.2.0` binds to r2 as its majority content (PR #416,
#417 are r2-shaped) but also carries PR #415 (r1-shaped) — a mixed tag, not a clean r2 cut.
`kc-journey-map-v0.2.1` binds to no release id: both its commits (#431, #434) are bugfixes to
stories already `status: exists` in r1/r2 — a patch tag inside an already-cut release. Neither tag
names nothing (the falsifier's disqualifying case does not trigger), but no tag cleanly equals one
release. **No check today would catch a tag naming nothing.** `scripts/version-parity-check.sh`
validates version-string propagation across `plugin.json`/marketplace/manifest; it has no notion of
a journey release id or of matching a CHANGELOG PR's scope against a story's `release:` field. That
check does not exist and would need to be built before write-back could be trusted rather than
hand-matched, as done here.

**AC-4 — two-product cost.** Zero of the 12 cleanly-bound releases in the strict `{kc-dev-flow,
kc-journey-map}` corpus span both products — true for the named pair only. The class is not
zero-instance: `journey-map-poc` (the sprint value on the 4 excluded `kc-team-ops` items above) is
one live release-shaped group already spanning `kc-team-ops` and `kc-journey-map`. The two-tag cost
is real but unexercised for the named pair: this repository runs release-please in monorepo manifest
mode with one independent component per plugin (`kc-claude-plugins/CLAUDE.md`), so a release
spanning two products needs two tags (e.g. `kc-dev-flow-vX` and `kc-journey-map-vY`) cut
independently and possibly on different dates, and a release contract would have to record both
rather than one.

**Two assumptions named in the problem, resolved.** (1) A release group existing before work starts
versus release-please cutting a tag afterward: resolved as approximate write-back only — of the 2
tags checked, 0 bind 1:1 to a release id; both are hand-matched by majority PR content, not equal.
(2) A release spanning two version streams: never observed in the real corpus — no evidence it is
needed yet, only that it would cost two tags if it occurred.

```yaml
poc_outcome: stop
revision_read:
  code: kc-claude-plugins@0bbf6233831543b8e8874a44a73b4868f6a1ed50
  state: spacedock-state/dev@0daaab3db1415ec2259784c9b18b21c9940721a2
invented_release_count: >-
  10 of 22 non-terminal kc-journey-map + kc-dev-flow items (45%) need an invented or unlanded
  release; of those, only 3 (14% of 22) are strictly worse off than under the sprint ordinal today
  (2 items on an unlanded kc-dev-flow/S10, 1 packaging item with no journey story) — the other 7
  are equally ungrouped or blocked under either system.
two_product_tag_cost: >-
  Zero occurrences for the named pair kc-dev-flow + kc-journey-map (0 of 12 cleanly-bound releases
  span both). The class is not zero-instance: journey-map-poc is one live release-shaped group
  already spanning kc-team-ops and kc-journey-map, excluded from the strict corpus by the product
  filter. If a kc-dev-flow + kc-journey-map release occurred, this repository's release-please
  monorepo-manifest mode (one independent component per plugin) would need two independently-cut
  tags, and the release contract would have to record both rather than treating the release as one
  shipped unit.
reasoning: >-
  The falsifier's strong form (cannot group at all, or no tag binds at all) did not trigger — 12 of
  22 items bind cleanly and both checked tags bind approximately. But only 1 of those 12 binds to a
  ROADMAP heading that itself carries release-shaped prose (S9); the rest bind to a bare Linear link
  or a captain-named group with no written release text, so "the sprint headings already read as
  releases" does not hold for the live corpus. Tag write-back is hand-matched with no automated
  check to catch a false binding. Against that, only 3 of 22 items (14%) are strictly worse off
  under a release contract than under the sprint ordinal today, and the two-product cost this route
  was meant to justify has zero occurrences for the named pair, though one same-shaped case
  (journey-map-poc) already exists one product-pair over. The corpus does not show the release
  route is unworkable, but it also does not show 45%-needing-invention and hand-matched tags are a
  net improvement over an ordinal that already groups 100% of this corpus by product, cheaply.
  Recommend keeping the sprint ordinal; do not schedule a shipped release-contract migration on this
  evidence. If Kent wants the release route anyway for other reasons (roadmap/release register as a
  kc-dev-flow specification, tag alignment where cheap), that is a `change`-shaped follow-up, not a
  `proceed` this record supports.
```
