---
title: "Name the execution group release, so a journey release slice lands in a field instead of prose"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: kc-dev-flow/S10
sprint-readiness: ready
started:
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
