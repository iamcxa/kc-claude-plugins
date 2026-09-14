---
title: "Name the execution group release, so a journey release slice lands in a field instead of prose"
status: implementation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: kc-dev-flow/S10
sprint-readiness: ready
started: 2026-09-14T14:18:36Z
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
            - id: gate-attempt:tjxctad7413wyp3acfx8wzzp-backlog-2
              briefing:
                id: briefing:tjxctad7413wyp3acfx8wzzp:backlog:attempt-2:revision-1
                digest: sha256:99bbaef973a576be53fb75f38d7402302f463202de5d24ed9ac6b6bd1c3757d9
                room-ref: ./sprint-to-release-contract-migration/review/backlog/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:tjxctad7413wyp3acfx8wzzp:backlog:2
                briefing: briefing:tjxctad7413wyp3acfx8wzzp:backlog:attempt-2:revision-1
                by: person:captain
                at: "2026-09-14T14:18:19.027062Z"
                decision: approve
                reason: 'Captain said ok to the re-admission under the corrected scope: name the execution group release, scalar, so a journey release slice lands in a field instead of prose. The seed carries the rescoped problem, accepted outcome, non-goals, AC-1..AC-5 and a v3 POC receipt whose falsifier is the journey release id''s uniqueness across the repository.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:tjxctad7413wyp3acfx8wzzp:validation
          stage: validation
          attempts:
            - id: gate-attempt:tjxctad7413wyp3acfx8wzzp-validation-1
              briefing:
                id: briefing:tjxctad7413wyp3acfx8wzzp:validation:attempt-1:revision-1
                digest: sha256:994ba9e4ef6ed42c15369de18901760324070f9d84361ee45dcaebba5ffb4fb8
                room-ref: ./sprint-to-release-contract-migration/review/validation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-09-14T14:06:42.899672Z"
                reason: 'The Captain named the actual goal after this room was bound: unify the vocabulary to release so kc-journey-map''s release slices can be imported into dev-flow. This POC asked whether release grouping outperforms the sprint ordinal, which is a different question, so its stop does not answer the one the Captain is deciding.'
            - id: gate-attempt:tjxctad7413wyp3acfx8wzzp-validation-2
              briefing:
                id: briefing:tjxctad7413wyp3acfx8wzzp:validation:attempt-2:revision-1
                digest: sha256:838b3d78a9b52296fb0c52931f739ad667c55c271b783cbf9621b648bc2311be
                room-ref: ./sprint-to-release-contract-migration/review/validation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:tjxctad7413wyp3acfx8wzzp:validation:2
                briefing: briefing:tjxctad7413wyp3acfx8wzzp:validation:attempt-2:revision-1
                by: person:captain
                at: "2026-09-14T14:54:09.107621Z"
                decision: revise
                reason: 'Captain rejected at the prove gate. The bare release id silently conflates across products: two entities from different products both carrying release: r1 are returned together by --where release=r1 with no refusal, no warning, and no journey-file cross-check anywhere, and product cannot disambiguate because product and release id are already independent axes in the live corpus. Concrete ask: qualify the identifier as <journey>/<release-id>, mirroring the existing <product>/S<number> convention that sprint already uses, and show the qualified form no longer conflates under the same forced-collision exercise.'
---

## The problem

`kc-journey-map` already hands dev-flow a release. Its `plan-release` mode prepares one Development
Brief in the five-section admission format and, per `references/map-from-conversation.md` step 5,
includes "the selected release/story IDs" inside those sections. Dev-flow already accepts that brief.
Producer and consumer are connected.

What is missing is a structured landing place. Those identifiers arrive as brief prose, so nothing
can ask which work items belong to a given release: the only queryable grouping field is `sprint`,
whose value is an ordinal allocated by a `docs/dev/ROADMAP.md` heading and unrelated to any journey
release. The import is legible to a reader and invisible to every query.

The Captain ruled on 2026-09-14 that the vocabulary unifies on `release` so the journey slice has a
field to land in, and that the field is scalar: one release per work item. Shared or integration work
keeps its multiple release/story origins in prose, matching `map-from-conversation.md` step 6, which
carries multiple origins in task prose and refuses to invent a single story owner rather than forcing
a scalar one.

A prior POC on this entity asked a different question — whether release grouping outperforms the
sprint ordinal — and recorded `stop`. That record and its validation stay below as evidence about
grouping practice. They do not answer this admission, which is an interoperability requirement rather
than a benefit comparison, and the Captain has not reopened them.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: pilot-product-slice
  basis: >-
    Kent selected POC on 2026-09-14 over the recommended Pilot. One assumption in
    the accepted outcome has never been executed: that a journey release
    identifier can be carried into the field without transformation. Journey
    files name their releases r1, r2, r3, which are unique inside one journey and
    not across the repository, so the identifier may need qualifying before it can
    be a grouping value at all. A disposable run settles that before the contract
    change is committed to.
  route: [build, prove]
  obligations:
    architecture:
      - Keep the field scalar; shared work keeps multiple origins in prose, as kc-journey-map already does.
      - Decide nothing about kc-journey-map's own output; the transformation, if any, belongs on the dev-flow side.
    implementation:
      - Change the loader's frontmatter reading and the package documents that state the grouping contract.
    testing:
      - AC-1 to AC-5, with AC-5 carried end to end on a real journey release rather than a fixture.
  scope_boundary: >-
    The accepted outcome and complete non-goal list in this task remain unchanged.
    Excludes a list-valued field, any change to kc-journey-map, other adopters'
    records, retiring sprint, and any release-equals-tag claim.
  poc_decision: Whether a scalar `release` field carries a journey release slice end to end without transforming the identifier.
  poc_falsifier: >-
    Existence-disproof over the real journey files: if two journeys both name a
    release `r1`, a bare journey release id is not unique across the repository,
    AC-5's "copied without transformation" is false, and the design owes a
    qualification rule it does not currently have.
  poc_budget: One dispatch, and decision-ready inside 15 minutes — the same ceiling the Captain set for the earlier POCs in this session on 2026-09-14, not a derived one.
  poc_stop_when: >-
    The record either carries one real journey release from
    `docs/journey/kc-journey-map/draw-a-journey.yaml` into a committed work item's
    `release` field and returns it from `spacedock status --where release=<id>`, or
    names the exact collision or transformation that blocks it, with the command
    output that settled it. Work stops at that observation whichever way it falls.
  poc_artifact: retained
  poc_safety_boundary: the kc-dev-flow loader and its tests, plus this repository's own docs/dev records
  poc_decision_ready_minutes: 15
  decision:
    authority: Kent (Captain)
    at: 2026-09-14T00:00:00Z
```

## Accepted outcome

A work item names its journey release in a frontmatter field called `release`, and
`spacedock status --where release=<id>` returns that release's work items. The dispatch loader reads
the same field, so an item carrying `release` and `release-readiness: ready` dispatches exactly as
one carrying `sprint` does today. An adopter that has not migrated keeps dispatching on `sprint`
unchanged.

## Non-goals

- A list-valued field, or any attempt to hold more than one release per work item.
- Changing `kc-journey-map`, its journey file, the generated release contract, or what
  `plan-release` writes into the brief.
- Automatic migration of other adopters' records.
- Retiring `sprint`, which stays accepted until a separate Captain-admitted item removes it.
- Any claim that a release equals a release-please tag.
- Reviving the deleted `release` route step, or renaming the `### Feedback Cycles` section.

## Acceptance criteria

- **AC-1** A work item whose frontmatter carries `release` and `release-readiness: ready` and no
  `sprint` key loads through `profile-contract-loader.py` at a first working stage without a
  `ContractError`.
- **AC-2** A work item carrying only `sprint` and `sprint-readiness: ready` still loads, and
  `profile-contract-loader.test.py` and `profile-spacedock-route.test.py` exit 0.
- **AC-3** An item carrying both key pairs with conflicting values is refused by a named error rather
  than silently resolved to one of them.
- **AC-4** `spacedock status --workflow-dir docs/dev --where release=<id>` returns exactly the items
  carrying that value, exercised against a real committed item rather than a fixture.
- **AC-5** A Development Brief produced by `kc-journey-map`'s `plan-release` names a release
  identifier that is copied into the `release` field without transformation, shown end to end on one
  real journey release from `docs/journey/kc-journey-map/draw-a-journey.yaml`.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names
the changed premise, affected acceptance evidence, and recommended change or stop.

## Prior POC record — a different question

The two stage reports below were produced against the superseded POC framing. They are retained as
evidence about grouping practice, not as acceptance evidence for the criteria above.

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

## Stage Report: validation

- DONE: Recount the 22-item corpus and the 10-invented figure from the named revisions.
  Re-derived the corpus independently: checked out `spacedock-state/dev@0daaab3db1415ec2259784c9b18b21c9940721a2`
  into an isolated worktree and re-ran `spacedock status --workflow-dir <pinned> --json --fields
  slug,status,sprint,product,title --limit 0` (94 total, 22 matching `product in
  {kc-journey-map, kc-dev-flow}` and `status != done` — same corpus). The 12-bind / 10-invented /
  3-strictly-worse split matches the implementation stage's table item-for-item, including the S7/S8
  bare-Linear-link vs S9 real-prose distinction (confirmed against `docs/dev/ROADMAP.md` at
  `origin/main@0bbf6233`). **One supporting claim is wrong and I would classify it differently.**
  `poc-roadmap.md` states "zero live non-terminal items are currently stamped with those four
  ordinals [S1, S2, S4, S5]" to argue release-shaped ROADMAP prose isn't actually attached to live
  items. It is wrong: `show-release-stories-on-journey-boards` and `derive-release-story-progress`
  both carry `sprint: S1`, `product: kc-journey-map`, and `kc-journey-map`'s own `### Sprint S1 —
  inspect release stories with honest evidence states` heading (ROADMAP.md ~L454) does carry
  release-shaped prose. This does not change the 12/10/3 count — both items were already counted in
  the 12 "bound" group via content-match to journey release r2, not via the S1 heading, so the
  outcome arithmetic is unaffected. What it does surface: `kc-dev-flow` and `kc-journey-map` each
  independently number their own `S1`/`S2`/etc., stored as the bare string `S1` with no product
  prefix in most entries (only the `S10` items use a `kc-dev-flow/`-prefixed form) — an ordinal
  collision risk across products that is itself evidence for, not against, one of the problem
  statement's own premises. Net: the recount confirms the headline figures and finds one overstated
  supporting sentence that, corrected, does not move the verdict.
- DONE: Test the finding on a second corpus.
  Two adopter repos with a `docs/dev` workflow exist on this machine. `carlove-v1` has no
  `docs/dev/.spacedock-state` yet (still on `TASK-TEMPLATE.md`, pre-spacedock) and could not run the
  same classification. `subspace-v0` (`/Users/kent/conductor/repos/subspace-v0`) has
  `docs/dev/.spacedock-state` with a `sprint:` field on its entities. Read all 122 entity files
  directly (no `spacedock` binary run needed — parsed frontmatter): 107 non-terminal (`status !=
  done`), of which **92 (86%) carry no `sprint` value at all** — a higher invented/unlabeled rate
  than this repository's 45%, under the *existing* sprint mechanism, before any release contract is
  even proposed. `subspace-v0` has no `ROADMAP.md`, no sprint-ordinal headings, and no
  `docs/journey/` directory — the release-contract/journey-binding half of this POC (AC-2, AC-3) has
  no analog there at all; only the grouping-rate half is comparable. Verdict: the grouping-rate
  finding **holds and is not specific to this repository's roadmap habits** — a sibling repo shows
  the same gap in starker form under the mechanism already in use, which argues that low grouping
  rates are a practice problem independent of which mechanism (sprint or release) is chosen, not an
  artifact of `kc-claude-plugins`' particular ROADMAP prose habits.
- DONE: Separate the grouping-rate finding from the tag-binding finding and state which carries the
  `stop`.
  The **grouping-rate finding carries the `stop`**: only 1 of the 12 "bound" items (`dev-94`, S9)
  binds to a ROADMAP heading with real release-shaped prose the corpus's own author would recognize
  as a release description; the rest bind to a bare Linear-project link or a captain-named group
  never written as a heading at all. Combined with only 3 of 22 items (14%) being strictly worse off
  under a release contract than under the sprint ordinal today, this is a "no net benefit shown"
  result — the burden was on the new mechanism to demonstrate improvement over the incumbent, and it
  did not, independent of tags. The **tag-binding finding does not independently carry a `stop`**:
  the POC's own falsifier's strong form ("no drafted release can be bound to the cut tags") did not
  trigger on either `kc-journey-map-v0.2.0` or `-v0.2.1` — both bind approximately, by majority PR
  content, not to nothing. The gap named ("no check today would catch a tag naming nothing") is a
  missing automated check, not a structural impossibility. A tag-binding design that never claimed
  1:1 tag-to-release equality — e.g. a many-to-many release↔tag mapping with a lint that flags a
  commit whose scope doesn't match any story in its claimed release, rather than asserting exactly
  one tag per release — is not falsified by this evidence and would survive it; it would still need
  the not-yet-built check before "aligns with the real tag" could be trusted rather than hand-matched
  as done here. If Kent wants the release route specifically to fix loose tag alignment, that
  redesign is the shape to bring back, not this record's literal 1:1 claim.

### Summary

Independent recount confirms the implementation stage's headline figures (22-item corpus, 12
bound / 10 invented / 3 strictly worse) hold at the named revisions, with one overstated supporting
sentence (a false "zero items stamped S1/S2/S4/S5" claim) that does not change the count once
corrected. A second corpus (`subspace-v0`, the only other on-machine repo with a spacedock-state
`docs/dev` workflow) shows a worse grouping rate (86% unlabeled) under the existing sprint mechanism
alone, before any release contract — the low-grouping-rate finding is not an artifact of this
repository's roadmap habits. The `stop` is carried by the grouping-rate finding (no net benefit
shown against the incumbent sprint ordinal), not by the tag-binding finding, whose falsifier did not
trigger and which would survive a redesign that never claims 1:1 tag equality. Validation confirms
`poc_outcome: stop`; recommend Kent's ruling stand as recorded, with the corrected S1/S2/S4/S5
sentence noted for anyone re-reading `poc-roadmap.md`.

Revision read: same as implementation — `kc-claude-plugins origin/main@0bbf6233831543b8e8874a44a73b4868f6a1ed50`,
`spacedock-state/dev@0daaab3db1415ec2259784c9b18b21c9940721a2`. Second-corpus revision:
`subspace-v0` local checkout at `/Users/kent/conductor/repos/subspace-v0`, `docs/dev/.spacedock-state`
working tree read directly (122 files) on 2026-09-14; no separate pin taken since the repo is not
part of this POC's scope boundary and the count is a one-off comparison, not a tracked claim.

```yaml
validation_outcome: confirms poc_outcome: stop
recount:
  corpus_count: 22
  bound_count: 12
  invented_count: 10
  strictly_worse_count: 3
  discrepancy_found: >-
    poc-roadmap.md's "zero live items stamped S1/S2/S4/S5" claim is false — 2 kc-journey-map items
    carry sprint: S1 and kc-journey-map's own S1 heading carries release-shaped prose. Does not
    change the 12/10/3 count; both items were already counted as bound via journey-release
    content-match, not via the S1 heading.
second_corpus:
  repo: subspace-v0
  non_terminal_count: 107
  no_sprint_value_count: 92
  no_sprint_value_rate: 86%
  release_contract_analog: none (no ROADMAP.md, no journey file — only grouping-rate half is comparable)
  verdict: grouping-rate finding holds and replicates in starker form; not specific to this repo's roadmap habits
claim_separation:
  carries_the_stop: grouping-rate finding (no net benefit vs incumbent sprint ordinal)
  does_not_independently_carry_the_stop: tag-binding finding (falsifier's strong form did not trigger; gap is a missing check, not a structural impossibility)
  survives_redesign: a many-to-many tag-to-release binding with a scope-drift lint, never claiming 1:1 tag equality, is not falsified by this record
```

## Stage Report: implementation (cycle 2)

- DONE: Settle the falsifier — are journey release ids unique across this repository?
  `find . -path "*/docs/journey/*" -type f` finds exactly one product journey file,
  `docs/journey/kc-journey-map/draw-a-journey.yaml` (`releases: r1, r2, r3`). No collision at
  `docs/journey/`. A second, non-`docs/journey/` file names `r1` too:
  `kc-journey-map/skills/kc-journey-map/references/journey.example.yaml` (a teaching example, never
  a `plan-release` source). Named residual, not a stop: bare ids are unique only by vacuity — the
  moment a second real product journey exists (e.g. `docs/journey/kc-dev-flow/`, absent today per the
  prior POC), both would start at `r1`. No qualification rule invented; AC-5's "copied without
  transformation" holds for the current single-journey repository.
- DONE: Loader accepts `release`+`release-readiness: ready`, still accepts `sprint` unchanged, refuses a conflicting pair by name (AC-1..AC-3).
  `kc-dev-flow/scripts/profile-contract-loader.py` lines ~735-770: presence is judged on a non-empty
  value (`^release:[ \t]*[^\s#]`) so the entity template's blank `sprint:` placeholder never collides
  with a real `release` value; both pairs present raises `ContractError("frontmatter must not carry
  both release and sprint")`. `profile-contract-loader.test.py` adds: release-only load at the first
  working stage, sprint-only load (regression), release with a blank `sprint:` template line still
  loads, three release placeholder refusals (`null`, `[r1]`, deferred readiness), and two
  both-pairs-present refusals (differing values, and equal values — the equal-value case is a
  deliberately broader refusal than AC-3's literal "conflicting values", since the field is scalar and
  two scheduling identities on one item is refused regardless of whether they happen to agree; noted
  here as a bounded design choice, not silent over-reach). A one-line change that would make each
  test fail: removing the presence check collapses the release/sprint branch and fails the
  release-only case; reverting `[^\s#]` to a bare `^release:`/`^sprint:` fails the blank-template case.
  `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` exits 0 (5 sub-suites PASS).
- DONE: AC-2 — `profile-contract-loader.test.py` and `profile-spacedock-route.test.py` exit 0.
  Both run clean at commit `a5fd90de`. Also re-ran `scripts/kc-dev-flow-contract-test.py` (checks the
  packaged docs against fixed prose, including the exact adopter sentence this change touched) and
  `scripts/skill-frontmatter-lint.sh` (46/46 skills valid) — both exit 0.
- DONE: AC-4 and AC-5 exercised against real committed content.
  Filed `release-field-r1-evidence-record` via `spacedock new` (state commit `b36ef133`), frontmatter
  `release: r1` / `release-readiness: defer` (deferred, not ready — proves the field/query without
  entering `--next`'s dispatch queue). Byte equality: `grep -oE 'id: r1'
  docs/journey/kc-journey-map/draw-a-journey.yaml` and the entity's `release:` line both read `r1`.
  `spacedock status --workflow-dir docs/dev --where release=r1 --json` returns exactly one entity,
  slug `release-field-r1-evidence-record`; `--where release=r2` returns zero; `--validate` exits 0
  (`VALID`, pre-existing unrelated flat-entity warnings only); `--next --json` omits the item
  (confirmed by grep). No r1 story in the journey file is open work today (all `status: exists`), so
  the record is filed as labeled evidence rather than invented work — retention past this entity's
  close is `without-it unanswered` for Kent.
- DONE: Package documents that state the grouping contract.
  Updated `kc-dev-flow/README.md` (the loader's canonical contract paragraph),
  `kc-dev-flow/skills/adopt-dev-flow/SKILL.md`, `kc-dev-flow/skills/choose-work-profile/SKILL.md`, and
  this repository's own `docs/dev/README.md` adoption doc to state the `release`/`release-readiness`
  alternative alongside unchanged `sprint`/`sprint-readiness`. `scripts/kc-dev-flow-contract-test.py`
  (checks fixed adopter prose byte-for-byte after whitespace normalization) still exits 0 after these
  edits.

### Summary

Falsifier settled: no real collision today (one product journey, one unrelated teaching example
sharing `r1` as a label, named as a residual). Loader now accepts a scalar `release` +
`release-readiness: ready` pair as an alternative to `sprint` + `sprint-readiness: ready`, refuses
both pairs present by a named error, and treats presence as non-empty-value so the entity template's
blank `sprint:` placeholder never false-collides. AC-1..AC-5 exercised: loader tests green, package
docs updated, and one real committed entity carries `release: r1` end to end, queryable by
`spacedock status --where release=r1`.

Code branch fast-forwarded from dispatch tip `7b103a10` to `origin/main@ed452eb2` before starting —
the dispatched worktree predated `docs/journey/kc-journey-map/draw-a-journey.yaml`'s merge (PR #428);
AC-5 cannot be exercised without it. Validation should pin the same code SHA.

Revisions: code `kc-claude-plugins` `spacedock-ensign/sprint-to-release-contract-migration@a5fd90de`
(based on `origin/main@ed452eb2`). State `spacedock-state/dev@b36ef133`.

## Stage Report: validation (cycle 2, prove)

- DONE: Re-run the loader tests, contract test, and frontmatter lint at the
  candidate commit, in a checkout resolved independently rather than reused
  from the implementation worker's worktree.
  `git worktree add --detach /tmp/validation-check-a5fd90de a5fd90de` from
  the code worktree, `git status --porcelain` empty. All four green at
  `a5fd90de51c899ba68241755daa08293724d5fd4`:
  `profile-contract-loader.test.py` (5 sub-suites PASS, includes the
  release-only, sprint-only, blank-`sprint:`-template, three placeholder
  refusals, and two conflicting-pair refusals named in cycle 2's report),
  `profile-spacedock-route.test.py` PASS, `kc-dev-flow-contract-test.py`
  PASS, `skill-frontmatter-lint.sh` (46/46 skills valid). Confirmed the
  conflicting-pair refusal is a named `ContractError`, not a silent
  resolution: `profile-contract-loader.py` raises
  `ContractError("frontmatter must not carry both release and sprint")`
  when both `^release:[ \t]*[^\s#]` and `^sprint:[ \t]*[^\s#]` match — the
  `[^\s#]` presence check is why a still-blank `sprint:` template placeholder
  never false-collides with a real `release` value (exercised by the
  `release-blank-sprint-template` sub-case, also passing).
- DONE: Attack the falsifier — create a second journey file in a disposable
  copy, name a release `r1` in it too, and report what `--where release=r1`
  actually does.
  Built a disposable copy of both the code worktree and the state checkout
  (never committed, never pushed), added
  `docs/journey/kc-dev-flow/draw-a-journey.yaml` with its own `releases: [{id:
  r1, ...}]`, and filed a second entity (`spacedock new`, product:
  kc-team-ops, `release: r1`) alongside the real
  `release-field-r1-evidence-record` (product: kc-dev-flow, `release: r1`,
  which itself already references `kc-journey-map`'s r1). **Answer: yes, it
  conflates them, and nothing at any layer refuses or warns.**
  `spacedock status --where release=r1 --json` returns both entities as one
  result set:
  `{"slug":"disposable-fixture-r1-collision","product":"kc-team-ops","release":"r1",...}`,
  `{"slug":"release-field-r1-evidence-record","product":"kc-dev-flow","release":"r1",...}`
  — indistinguishable except by reading `product` yourself, which the query
  does not do. `--validate` still returns `VALID` (only pre-existing,
  unrelated flat-entity-room warnings). The loader's own regex never opens
  `docs/journey/` at all — its check is shape-only (presence via
  `[^\s#]`, null/collection rejection) — so **the second journey file I
  created had zero effect on any command**; no code path today consults a
  journey file to verify a release id is real or unique. Sharper than the
  fixture shows: `product` cannot serve as an implicit disambiguator even in
  the live corpus, because the real `release-field-r1-evidence-record`
  already carries `product: kc-dev-flow` while naming `kc-journey-map`'s r1 —
  release id and product are independent axes today, not just in this
  fixture. This is the named residual from cycle 2's report, now demonstrated
  rather than inferred: bare release ids are unique only because exactly one
  product journey file exists; a second one collides silently the moment it
  exists, with no refusal, no warning, and no journey-file cross-check
  anywhere in the loader or the query path.
- DONE: Judge whether `release-field-r1-evidence-record` belongs in this
  workflow.
  **Verdict: artifact, not a deliverable — recommend withdrawal, but not by
  me.** Three rules, all pointing the same way. (1) `docs/dev/README.md`
  frontmatter declares `entity-type: task`; the backlog section describes an
  admitted item as carrying "the required Development Brief or Exploration
  Brief." This entity's own body says "this record exists to carry the
  evidence rather than to name new work" and its Non-goals disclaim naming
  work — it fails the entity-type test by its own text, not by my inference.
  (2) CLAUDE.md's without-it test: the evidence it exists to hold (byte
  equality, the `--where release=r1` query result) already lives verbatim in
  cycle 2's implementation stage report above; removing the entity breaks
  nothing that isn't already recorded elsewhere. (3) The entity's own
  route-back condition names this migration's close as its retirement
  trigger, and this validation stage is that close. I am not withdrawing it
  myself: its own text says "without-it disposition is Kent's call," and
  CLAUDE.md's mis-delete cost applies. One tension worth naming plainly
  rather than laundering: AC-4/AC-5 required exercising the query "against a
  real committed item rather than a fixture," and this entity is itself
  fixture-shaped (`release-readiness: defer`, no open work, filed solely to
  carry evidence) — it satisfies the letter of "real committed item" (it is
  committed, not a throwaway file) while being, in substance, a fixture,
  because no real r1 story was open to serve as evidence directly.

### Summary

All four required checks (loader tests, route test, contract test, skill
lint) reran green at `a5fd90de` in an independently resolved checkout. The
conflicting-pair refusal is confirmed as a named `ContractError`, and the
blank `sprint:` template placeholder is confirmed non-colliding by
construction (presence requires a non-empty value). The falsifier is
answered directly: two entities naming the same bare `release: r1` from
different products **are silently conflated** by `spacedock status --where
release=r1` — returned together, indistinguishable without manually reading
`product`, with no refusal or warning at any layer, and no code path
consults a journey file to check real-world uniqueness. This is the residual
cycle 2 named (unique only by vacuity, one product journey today) now
demonstrated empirically rather than argued. `release-field-r1-evidence-record`
is judged an evidence artifact rather than a workflow deliverable by its own
declared entity type and Non-goals, and by the without-it test — recommend
Kent rule on withdrawal per its own route-back condition; not withdrawn here.

```yaml
poc_outcome: proceed
evidence: >-
  AC-1..AC-3 (loader tests) and AC-4/AC-5 (real committed entity, query
  round-trip) all pass at candidate commit a5fd90de51c899ba68241755daa08293724d5fd4,
  reconfirmed in an independently resolved detached worktree with a clean
  git status. The falsifier's precondition (two real product journeys
  naming the same release id) does not hold in the live repository today
  (one product journey, docs/journey/kc-journey-map/draw-a-journey.yaml);
  under that precondition the carry is byte-exact and the query returns
  exactly one entity, matching the receipt's poc_stop_when first branch.
strongest_limit: >-
  Demonstrated by construction, not inferred: a second product journey
  naming the same bare release id collides silently. spacedock status
  --where release=r1 conflates entities from different products with no
  refusal, no warning, and no journey-file cross-check anywhere in the
  loader or query path — confirmed via a disposable second journey file
  and a disposable second entity, and independently via the live corpus,
  where the real release-field-r1-evidence-record already carries
  product: kc-dev-flow for kc-journey-map's r1, showing product cannot
  serve as an implicit disambiguator even today. No qualification rule
  exists; none is proposed by this record (out of the accepted scope
  boundary, which excludes inventing one).
reversal_fact: >-
  A second product journey file appearing under docs/journey/ (e.g.
  docs/journey/kc-dev-flow/) that reuses r1/r2/r3-shaped ids reverses the
  "unique by vacuity" premise this migration shipped under, and would
  silently conflate real work items across products under one release
  query with no error surfaced anywhere.
cleanup: >-
  Disposable journey file, disposable entity, and disposable code/state
  copies used for the falsifier were created outside any tracked worktree
  and were not committed; none persist. release-field-r1-evidence-record
  (the real, committed evidence entity) is left in place per its own
  Kent's-call route-back condition — not cleaned up by this stage.
