---
title: The ADR lint pointer scan tells a supersession assertion from a pointer
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:adr-lint-tells-supersession-assertion-from-pointer:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-lint-tells-supersession-assertion-from-pointer-backlog-1
              briefing:
                id: briefing:adr-lint-tells-supersession-assertion-from-pointer:backlog:attempt-1:revision-1
                digest: sha256:b1bbc3cf56fcca91bbde08e296e3a7e53f6d2aa1fdb7c434cf69b2128e983ff1
                room-ref: ./adr-lint-tells-supersession-assertion-from-pointer/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-lint-tells-supersession-assertion-from-pointer:backlog:1
                briefing: briefing:adr-lint-tells-supersession-assertion-from-pointer:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-07T08:09:19.231988Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-07), answering 「決定：第 17 批這五張（Paseo 瀏覽器當工人驗收的預設、決策紀錄檢查分清驗證取代與指向依據、派工時自動寫派工紀錄、沒給範圍時設計檢查說沒跑、觀察者列出沒有合併提問紀錄的合併）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

`adr_lint.py` no longer reports a file an ADR protects as "points at ADR N, Superseded by M" when the only citation is a test asserting that N's Status reads "Superseded by M".

## Scope

- Source: FO, from a bite in batch 16 (2026-11-07); no Captain words yet; the backlog gate is his.
- Bite: decline-becomes-task-only-with-a-bite implementation, worker report (Paseo ba392d9b, 2026-11-07): ADR 0064 lists `kc-dev-flow-2/scripts/test_sd_dispatch.py` under Protects; the required `adr_lint.py docs/adr --since ba055b8a7 --require 0064` then fails on that file's assertion `"## Status\n\nSuperseded by 0050" in (ROOT.parent / "docs/adr/0047-…").read_text()`, because `check_pointers` counts every `docs/adr/NNNN` string in a protected file as a pointer. The worker could only pass by splitting the path literal (dispatch record implementation-1-message-3), which hides the citation from the scan rather than fixing it.
- Upstream first: `check_pointers` in `kc-dev-flow-2/scripts/adr_lint.py`; its tests.
- Non-goals: changing which files an ADR may protect; the split path in test_sd_dispatch.py may stay or be reverted by this task.

## Budget
- One package PR touching adr_lint.py and its tests; workflow word budget unchanged.

## Stop condition
- A fixture whose protected file asserts a superseded ADR's Status passes the lint, and a fixture whose protected file cites a superseded ADR as its authority still fails.

## FO alignment

Alignment: not needed; a lint false positive with one observed bite.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
