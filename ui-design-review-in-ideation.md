---
title: A ui task's ideation runs a design review over its previews and turns the findings into requirements and criteria
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:ui-design-review-in-ideation:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:ui-design-review-in-ideation-backlog-1
              briefing:
                id: briefing:ui-design-review-in-ideation:backlog:attempt-1:revision-1
                digest: sha256:5e30aa55686d7f9ab6b30c2e80b95cb57f39a344218afa5ddffb69ed38c3925f
                room-ref: ./ui-design-review-in-ideation/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:ui-design-review-in-ideation:backlog:1
                briefing: briefing:ui-design-review-in-ideation:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-17T06:10:32.253897Z"
                decision: approve
                reason: Captain approved in chat (「准」) the six batch-2 backlog gates presented together in one message, accepting the recommended profiles (pilot; merge-gatekeeper prod) and the stated order
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-17T06:11:26Z
---

Filed on the Captain's 「同意設計待辦」 (chat, 2026-10-17), to FO's proposal to file the subspace-web FO's design-director proposal as one task that reuses the mechanism of prod-security-review-gates (a specialist review inside ideation; its findings become design requirements and acceptance criteria; `design_surfaces.py check` refuses a design whose review is missing or whose findings have no disposition).

## Scope

- The bite (relayed by the subspace-web FO, dhaka-39, 2026-10-17; to be re-read from state at ideation): subspace-web holder-panel-header-and-polish ideation revised twice for design quality (layout and hierarchy, then a 12-point critique), its refresh button, and disclosure-chevrons-follow-state for inconsistent chevrons; qnow vehicle-based-pricing and reception-holds-slot design defects (column width, a brand-wide apply with no confirm, no non-default cue, a new-booking window with no model picker). Each was visible in the preview before the gate.
- Trigger: `Surfaces: ui` in any profile. The ideation worker runs the review after drawing its previews, over the previews and the operable preview where one exists.
- Brief checklist (from the proposal): hierarchy and redundancy; one spacing, inset and alignment system; design-system conformance; every state (empty, loading, error, long content, many items, overflow); flow logic (the task can be completed, unsafe one-click actions, non-default cues); cross-control consistency; platform conventions; light, dark and phone.
- Disposition per finding: fixed (preview redrawn), an acceptance criterion, declined with a reason (minor only), or a Needs decision; a major finding is never declined by the worker.
- Reviewer: open. Installed `design:design-critique` (Anthropic's design plugin 1.2.0, a 595-word interactive skill, synced from the claude.ai organisation, no licence file in its folder) and e2e-pipeline's `ui-verify` (this repository; checks computed CSS against expected tokens, needs a declarative YAML and agent-browser) are candidates; whether dev2 owns the brief, depends on either, or needs neither is for ideation.
- Order: after prod-security-review-gates lands, reusing its seam.
- Proof before shipping (proposal): replay the brief fresh on the archived holder-panel cycle-1 and cycle-3 previews and the chevron cycle-1 preview; it names at least the duplicated count, the crowded chrome, the off-system refresh button and the opposite chevrons, or it does not ship.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it (his words are at the top of this file).
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Replay pre-registration (written before any replay run, 2026-10-17)

Expected findings per archived preview, from the recorded words of the people who found them, not from any run. Source: subspace-web `origin/spacedock-state/dev2`, `_archive/holder-panel-header-and-polish.md` (Ruling, cycle-3 dispatch `dispatch/ideation-3.md` points 1, 2, 11, Captain amendment 1) and `_archive/disclosure-chevrons-follow-state.md` (Ruling). Preview commits: holder cycle 1 `eb69c1f`, cycle 3 `acc75f5`, chevron cycle 1 `2b2cdd6` (`git log` of that branch).

| Preview | Defect that must be named (any severity, by what it is) | Recorded by |
| --- | --- | --- |
| holder cycle 1 | H1 the same count stated twice: rail header "3 comments" and the "All feedback 3" card | FO critique point 1, approved by the Captain 「可以，退回」 |
| holder cycle 1 | H2 crowded chrome above the first comment (profile card, feedback card, Updated line, lag sentence) | FO critique point 2 |
| holder cycle 1 | H3 the Refresh control is a text button unlike the toolbar's icon buttons | Captain 「refresh 按鈕不好看」 |
| holder cycle 1 | H4 phone: a second feedback surface above the document besides the tray, tray label "Not submitted · 0" | FO critique point 11 |
| holder cycle 3 | H5 phone refresh icon drawn as a visible 44px filled square unlike the 26px toolbar icons | Captain amendment 1 「手機上的重新整理按鈕有點怪」 |
| holder cycle 3 | none of H1 to H4 may be reported as present: they were fixed in cycle 3 (a report of one is a false positive) | cycle-3 stage report, measured D1, F2 |
| chevron cycle 1 | C1 the three disclosure controls draw the same state with opposite chevron directions (closed menu points down, closed tray and drawer point up) | Captain 「chevrons有點怪」 on this preview |

Pass rule from the Captain's relayed proposal: the brief names H1, H2, H3, C1 (the proposal's "duplicated count, crowded chrome, off-system refresh button, opposite chevrons") or it does not ship. Added here: H5 on cycle 3 (the defect a fix introduced), and a count of unfounded findings on cycle 3. A finding "names" a defect when its `seen:` text describes it; I read the reports, so matching is judged by me and stated as such.
