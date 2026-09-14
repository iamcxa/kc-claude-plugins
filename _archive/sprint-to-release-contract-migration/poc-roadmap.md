# roadmap.md (DRAFT — POC artifact, not shipped, written outside the code repository tree)

Every non-terminal `kc-journey-map` and `kc-dev-flow` work item, read via
`spacedock status --workflow-dir docs/dev --json --fields slug,status,sprint,product,title --limit 0`
at state revision `0daaab3db1415ec2259784c9b18b21c9940721a2` (94 total entities; 22 match
product in {kc-journey-map, kc-dev-flow} and status != done).

## Excluded by product filter — 4 items, named for visibility

`default-to-the-journey-alone`, `collapse-to-one-board`, `evidence-means-executable-code`,
`reverse-a-story-map-from-linear` all carry `product: kc-team-ops`, `sprint: journey-map-poc`. They
are excluded from the 22-item corpus below by the strict product filter, but
`default-to-the-journey-alone` is, by slug, the exact r1 story `ask-which-boards-to-draw` / journey
`default-to-the-journey-alone` in `draw-a-journey.yaml` — a literal journey story sitting outside
the `kc-journey-map` product label. `journey-map-poc` is itself a release-shaped group spanning two
products (`kc-team-ops` and `kc-journey-map`), which matters for AC-4.

## kc-journey-map — 4 items

| slug | status | binds to |
|---|---|---|
| journey-canvas-unreachable-from-another-machine | validation | r1 (regression against an existing `exists` render story) |
| show-release-stories-on-journey-boards | validation | r2 (title and `buildJourneyBoard`/release-stories system note match r2's contract-checking goal) |
| derive-release-story-progress | implementation | r2 (follow-on to PR #417 "derive optional local task progress", which shipped inside r2-majority tag v0.2.0) |
| **extract-the-journey-map-plugin** | implementation | **none** — packaging/publishing infrastructure, not a journey story; no `release:` field in the journey file covers plugin extraction |

## kc-dev-flow — 18 items

Bind to an existing named release (9 items; 12 with the 3 kc-journey-map rows above):

| slug | status | release | release has written goal prose? |
|---|---|---|---|
| first-cloud-dev-flow-improvement-run | validation | S8 | no — bare Linear-project link only |
| dev-52-inventory-kc-dev-flow-removal-candidates | backlog | S8 | no — bare Linear-project link only |
| dev-94-ship-flow-thin-wrapper | backlog | S9 | yes — ROADMAP S9 carries its own description |
| plugin-owned-dev-flow-contracts | backlog | S7 (content match; stored sprint label `kc-dev-flow/plugin-owned-contracts` drifts from the ROADMAP heading name — same drift class the journey-map product/sprint fields already show) | no — bare Linear-project link only |
| adopter-contract-test-ships-with-the-package | ideation | ship-cloud-wrapper-r3 | no ROADMAP heading exists for this name at all; it is a captain-named group, not a written release |
| direct-path-below-poc-admission-rule | backlog | ship-cloud-wrapper-r3 | same |
| pr-merge-extension-separates-canonical-from-local-policy | backlog | ship-cloud-wrapper-r3 | same |
| pr-merge-extension-text-matches-spacedock-0-27 | backlog | ship-cloud-wrapper-r3 | same |
| pr-merge-released-body-pin-per-mod-version | backlog | ship-cloud-wrapper-r3 | same |

Correction against an earlier draft of this file: of these 9, only `dev-94-ship-flow-thin-wrapper`
binds to a ROADMAP heading that itself carries End-value/Exit prose (S9). S7 and S8 are bare Linear
links with no in-repo release text. `ship-cloud-wrapper-r3` is not a ROADMAP heading at all. "The
sprint headings already read as releases" is true for S1, S2, S4, S5 in the ROADMAP file, but **zero
live non-terminal items are currently stamped with those four ordinals** — the corpus's real bound
items mostly rely on Linear or a bare captain-given name, not ROADMAP prose.

Need an invented release, or cannot be admitted to the release that exists (10 items; 9 kc-dev-flow
+ 1 kc-journey-map, cross-referenced):

| slug | status | why | worse under release than under sprint? |
|---|---|---|---|
| retire-the-provider-backed-planning-path | validation | stamped `kc-dev-flow/S10`; no `S10` heading exists in `docs/dev/ROADMAP.md` yet | **yes** — sprint ordinal at least allocates a label immediately; release prose has not been written |
| sprint-to-release-contract-migration (this POC) | implementation | same — `kc-dev-flow/S10`, no landed heading | **yes**, same reason |
| extract-the-journey-map-plugin | implementation | no journey story covers plugin packaging | **yes** — this is release-specific: a sprint ordinal never needed a story to bind to |
| spacedock-project-status-updates | implementation | stamped `S3`; ROADMAP marks S3 "RETIRED for new admissions" | no — the sprint ordinal is equally stuck; a retired heading blocks new admission either way |
| delivery-base-trunk-test-conflates-file-and-lineage | backlog | no `sprint` value at all | no — equally ungrouped under the ordinal today |
| delivery-topology-review-deduplication | backlog | no `sprint` value at all | no — same |
| release-smoke-runs-at-the-release-pr | backlog | no `sprint` value at all | no — same |
| spacedock-projector-automation-sunset-review | backlog | no `sprint` value at all | no — same |
| spacedock-route-test-passes-nowhere | backlog | no `sprint` value at all | no — same |
| versioned-adoption-lock-local-policy | backlog | no `sprint` value at all | no — same |

**Split that matters for the verdict:** of the 10, only 3 are release-specific problems (the 2 S10
items whose ordinal was allocated before any release prose existed, plus the 1 packaging item with
no journey story). The other 7 are unlabeled or blocked under the sprint ordinal today too — moving
to a release contract would not make those 7 worse, but would not fix them either.

Count used for `poc_outcome`: **10 of 22** non-terminal items (45%) need an invented release or
cannot be admitted to the one release that already exists for their stamped ordinal; **3 of 22**
(14%) are strictly worse off under a release contract than under the sprint ordinal.
