---
title: A release is walked after its last story by picky-user reviewers on different models, and the design director rules what to solve, how and when
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:release-walk-picky-reviewers-and-director:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:release-walk-picky-reviewers-and-director-backlog-1
              briefing:
                id: briefing:release-walk-picky-reviewers-and-director:backlog:attempt-1:revision-1
                digest: sha256:6de9d2629d6e8b4fc0ca15135fccd425d1501e32d0f28ae67ef95ffdcc3225d1
                room-ref: ./release-walk-picky-reviewers-and-director/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「可以」 (chat, 2026-10-23), answering 「把版本驗收的第二個 PR 拆成新任務、先過設計閘門，目前這張只用 #709 結案，可以嗎？」; recorded as release-acceptance Captain Amendment 4, which moves that task's AC-6, AC-7, AC-8, AC-11 and AC-12 here, with its Amendments 1 (a design-director pass over the walk, works-but-unusable class) and 3 (at least two picky-user reviewers on different models and personas, the director's ruling table with at most three backlog tasks, deferred-to-UAT findings fed in, a fixture smoke check first, a single-model fallback).
- Bite: release-acceptance r3-acceptance.md and r4-acceptance.md (hand walks that found what no task validation saw); the kc-paseo-plugins r1.5 critique (four blocking problems after six task gates, the Captain's 「這個 UX 完全不行」, relayed); the hand-run picky-user review (product-review-path-before-backlog intake/method-notes-for-dev2.md).
- Starting design: release-acceptance `### PR 2 design` and its implementation stage report (cycle 3): a release-acceptance extension, a due trigger through pr_watch.py, the walk report schema under ADR 0012, deferred-findings listing, director pass 3, the docs-only-PR close path, and the open points it names for the Captain (close path, director model and inputs, a non-Claude operating reviewer, a journeys README key, one larger PR).
- Depends on: #709 (kc-journey-map walk list and accept mode) and #708 (the design-director agent, merged 0701aa8d).
- Non-goals: the pre-implementation review hold (release-review-staleness-held-at-dispatch).

## FO alignment

Alignment: needed at ideation; the open points named in the starting design are his.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
