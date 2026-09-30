---
title: A release is re-reviewed as one whole journey before its tasks are split, and a slice stays small enough to review
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:release-review:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:release-review-backlog-1
              briefing:
                id: briefing:release-review:backlog:attempt-1:revision-1
                digest: sha256:9ed3face13f8058974233b4bd608ebce32dfc43463aa6f2ab0c9ac0d7ffaa090
                room-ref: ./release-review/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:release-review:backlog:1
                briefing: briefing:release-review:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-30T10:01:33.899771Z"
                decision: approve
                reason: 'Captain 2026-09-30: 「我們來解決 520 問題」, with the five-per-slice rule folded in'
              application:
                target-stage: ideation
                state: consumed
---

A release gains tasks one at a time and nothing checks that together they still form one complete journey; batch C part 2 of the dev2 fixes.

## Scope

Captain 2026-09-30: 「有部分關係，你稍後可以找那個 peer ，有一個新的提議是 cl 認為每個切片只能有五件事，你可以跟他交換這個問題的細節，並且看看是否可以把這個規則跟 520 結合，那個 peer 就可以專心處理 relay + spacedock review 的旅程問題。我們來解決 520 問題。」 This task covers issue #520 and the proposed "a slice holds at most five things" rule.
Evidence (qnow, 2026-09-29, issue #520): over two days the Captain ruled eight-plus tasks into one release, each filed and designed on its own scope; the journey map's release stayed at its five stories of 2026-09-23 and the shop journey had none; cross-task holes surfaced only at Captain UAT (no brand context in the owner app, no signed-in identity in the office, no task that takes a real shop live on production). On 2026-09-30 the Captain then re-cut qnow's go-live slices from a whole-journey analysis before any dev2 fix.
Five-things rule, handed over 2026-09-30 by the peer session that drafted it (Captain not yet ruled on its design): proposed in a design review of another adopter's journey, where a reviewer could not discuss a release slice whose one column mixed two actors' actions and asked for at most five things per slice so people can hold the whole slice in their head. Captain: 「我覺得每片五件事最多可以開一個 PR 回去上游，讓切 slice時有依據，等於預設就是五件事。」 and 「我想像是可能會有 r2.1, r.2.2 等切片，每一片約莫是一天到兩天的實作量」. Draft: one thing is a story in the release whose status is not `exists` (steps, acceptance criteria and tasks are not counted); default limit 5, overridable per journey by a top-level `slice_limit`; advisory, not a gate: journey-lint prints a line like the existing `long-card (advisory)`, and `references/release-slicing.md` says a slice over the limit splits into sub-slices or states why not; the handoff budget check (`lib/journey-handoff.mjs`, estimate vs appetite) does not refuse on count, because `release-slicing.md` already says story count does not establish fit and this rule is about cognitive load, not fit. Case: after a redraw that adopter's first slice still held 14 stories, 10 not yet existing, and an independent read-only review flagged it as not a clear five-step demo; the other slices held 4, 4, 2 and 2. Public-repo rule: the package and its PR state only the generic reason.
Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: at which signals a release is re-reviewed as a whole journey (a task admitted into a release, a Captain scope ruling, a UAT failure that crosses tasks, before a batch enters implementation) and what the re-review produces; whether tasks carry `journey`, `journey-release` and `journey-story` so kc-journey-progress can compute completion; what "a slice holds at most five things" counts, where it is checked and what happens above five; which parts belong to kc-dev-flow-2 and which to kc-journey-map.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
