---
title: FO's idle line says a release is due for its walk once its last story is built, reading the journey file the workflow names
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:release-walk-due-trigger:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:release-walk-due-trigger-backlog-1
              briefing:
                id: briefing:release-walk-due-trigger:backlog:attempt-1:revision-1
                digest: sha256:7a1d6adea08b14ed68a7d8769122139335f3596f1be93106fe830c1ff44e31ff
                room-ref: ./release-walk-due-trigger/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:release-walk-due-trigger:backlog:1
                briefing: briefing:release-walk-due-trigger:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-03T07:44:58.900972Z"
                decision: approve
                reason: The Captain 「進」 (chat, 2026-11-03), answering the batch 13 sitting 「決定：這批七張（A 權限、B 同症狀計數、C 改寫條件比對原話、D release 驗收不在正式站、來源標註、FO 先自己試、release 驗收到期提醒）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？要改哪張直接說。」; approves Pilot, these outcomes and bounds.
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain 「拆」 (chat, 2026-10-23), answering FO's 「這張任務要不要拆成兩半？」 on release-walk-picky-reviewers-and-director D5: Part B of that design (the due trigger, a `journeys:` README key, the pr_watch.py line) becomes this follow-up, after that task's PR and #711 merge; D4 (how the idle script learns where the journey file is) comes with it.
- Bite: release-acceptance r3-acceptance.md and r4-acceptance.md were walked only because the Captain asked.
- Starting design: release-walk-picky-reviewers-and-director `## Design` Part B and its D4 options, and the moved AC-11 there.
- Carried from release-walk-picky-reviewers-and-director (state, 2026-10-23), its section `### Moved to release-walk-due-trigger`, verbatim:

  ### Moved to release-walk-due-trigger (Captain D5)

  Part B and D4 are not in this task: the `due` subcommand, the README `journeys:` key, the `pr_watch.py tasks` line and their tests. Their design stays in that task's own ideation; the text of the criterion that moves, for FO to carry (an amendment-free move, this task still being in ideation; that task's file is not edited from here): "AC-11: `due` prints one `next:` line for a release whose `acceptance` is `pending delivery acceptance` and which no live or archived task file claims with `release-acceptance: <journey>/<release>`, prints nothing for a claimed release, and prints `release-acceptance not run: kc-journey-map not found` when the sibling install is absent; `pr_watch.py tasks` includes the line only when `release-acceptance` is listed. Verified by `test_release_acceptance.py` against real `journey-progress.mjs` output on the example with all stories' tasks done, and `test_pr_watch.py` for the listing condition; a split-root scratch run of `spacedock new`, `status --set` and `state commit` repeated in the implementation report. Falsifier: removing the field from the claiming task makes the line reappear." Measured today (2026-10-23, Spacedock 0.27.2, scratch split-root repo in `/tmp`, deleted): `spacedock new r1-acceptance`, `status --set r1-acceptance release-acceptance=book-pickup/r1`, `state commit` kept the field and `status --archived --all-fields --json` listed it; an empty custom key is not listed, only a set value. That task depends on this one landing first, since `due` extends `release_acceptance.py`.

- Non-goals: the walk itself.
- Batch 13: the Captain 「可以」 (chat, 2026-11-03), answering 「決定：這批加入那 3 張，共 7 張一起進 backlog gate 嗎？」, which named this task. It pairs with release-walk-off-production-before-release in the same batch: that task decides where the walk runs and that production waits; this one says when it is due.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- The moved AC-11 holds: `due` prints one `next:` line for a release pending delivery acceptance that no task claims, nothing for a claimed release, and `release-acceptance not run: kc-journey-map not found` when the sibling install is absent, and `pr_watch.py tasks` shows it.

## FO alignment

Alignment: needed at ideation; D4 is his.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
