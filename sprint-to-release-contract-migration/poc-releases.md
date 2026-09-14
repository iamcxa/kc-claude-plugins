# releases.md (DRAFT — POC artifact, not shipped, written outside the code repository tree)

Revision read: kc-claude-plugins `origin/main` @ `0bbf6233831543b8e8874a44a73b4868f6a1ed50`
(2026-09-14T21:45:11+08:00); Spacedock state checkout `spacedock-state/dev` @
`0daaab3db1415ec2259784c9b18b21c9940721a2`.

## kc-journey-map (journey file bound: `docs/journey/kc-journey-map/draw-a-journey.yaml`)

| release id | goal (from journey file `releases:`) | shipped tag | tag fit |
|---|---|---|---|
| r1 | "A person can draw a story map by talking, and plan with it." | none isolated | r1 stories ship mixed inside v0.1.0 and v0.2.0; no tag is r1-only |
| r2 | "The same map can be checked against the code that exists." | `kc-journey-map-v0.2.0` (majority) | mixed tag — PR #416/#417 are r2-shaped, PR #415 ("editable native planning canvas") is r1-shaped; v0.2.0 is not a clean r2 cut |
| r3 | "Author a function model, iterate on it quickly, and hand one agreed Development Brief to development planning." | none | PR #419 ("prepare selected releases for development", in v0.2.0) touches the r3 `handoff` step, but r3's `model`/`funcmap` stories are still `status: unverified` in the journey file — v0.2.0 cannot be called "r3 shipped" |
| (patch, no release id) | — | `kc-journey-map-v0.2.1` | pure bugfixes (#431, #434) to already-`exists` r1/r2 stories; a patch tag inside an already-cut release, not a new release cut |

Neither tag names nothing (the falsifier's disqualifying case did not trigger), but neither tag
equals one release 1:1 either — both are hand-matched by majority PR content.

## kc-dev-flow (no journey file — stands alone on `roadmap.md` + `releases.md`)

`docs/journey/kc-dev-flow/` does not exist; `kc-dev-flow` releases are read from
`docs/dev/ROADMAP.md` sprint headings directly, with no journey column. Only S9 ("ship-flow glue
POC") carries written goal prose among the headings any live item is actually stamped with; S7/S8
are bare Linear-project links, and `ship-cloud-wrapper-r3` (5 live items) is a captain-named group
never written as a ROADMAP heading at all. See `poc-roadmap.md` for the full per-item table and the
correction against an earlier claim that "the sprint headings already read as releases" for the live
corpus.

## Two-product case (AC-4)

Named pair `kc-dev-flow` + `kc-journey-map`: **zero** of the 12 cleanly-bound releases in this real
corpus span both. But the *class* is not zero-instance: `journey-map-poc` (sprint value on 4 items
excluded from this corpus by the strict product filter — `default-to-the-journey-alone`,
`collapse-to-one-board`, `evidence-means-executable-code`, `reverse-a-story-map-from-linear`, all
stamped `product: kc-team-ops`) is one live release-shaped group already spanning `kc-team-ops` and
`kc-journey-map`. `default-to-the-journey-alone` is, by slug, the exact r1 story in the journey
file, sitting under a different product label than the journey it belongs to. So "no release
observed spans two products" is true only for the named pair; a same-shaped case already exists one
product-pair over.

This repository runs release-please in monorepo manifest mode with one independent component per
plugin (`kc-claude-plugins/CLAUDE.md`), so a release spanning two products needs two tags cut
independently — confirmed here structurally, not exercised against a real cross-product release
because none of the 12 cleanly-bound releases in the strict 2-product corpus is cross-product.
