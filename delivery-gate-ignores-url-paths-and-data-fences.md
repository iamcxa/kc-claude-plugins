---
title: delivery_gate.py question stops reading URL paths and data fences as Captain files and commands
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:delivery-gate-ignores-url-paths-and-data-fences:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-gate-ignores-url-paths-and-data-fences-backlog-1
              briefing:
                id: briefing:delivery-gate-ignores-url-paths-and-data-fences:backlog:attempt-1:revision-1
                digest: sha256:189dd7b6de15cb7c390c51d9dc49ede301d33182e83d828dd6b98da2dcb399e2
                room-ref: ./delivery-gate-ignores-url-paths-and-data-fences/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-gate-ignores-url-paths-and-data-fences:backlog:1
                briefing: briefing:delivery-gate-ignores-url-paths-and-data-fences:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-09T04:57:39.631425Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-09), answering 「決定：第 18 批這四張（驗證回答 Captain 能不能合併並因此主動讀完審查意見、合併檢查不再把網址和資料區塊當成檔案和指令、合併提問紀錄能證明檢查在提問前跑、數字寫明是哪次執行算出來的並涵蓋 learn 證據）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。核准即接受四張任務檔現在寫下的內容；要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-09T04:59:05Z
---

## Scope

- Source: the subspace-relay dev2 FO (Paseo 1671c3a9, 2026-11-08), relaying the Captain's 「草稿可以送，直接給dev2 fo」 (relayed, not a ruling here); draft at /tmp/fo-issues/kc-dev-flow-2-delivery-gate-false-positives.md. The backlog gate is the Captain's.
- Bite (relay FO's first-hand report, rechecked by it on 0.36.0, not re-run here): `delivery_gate.py question` refused complete gate texts on two of three subspace-relay validation gates on 2026-11-08 and on the 2026-11-06 llms-teaches-versions gate: site URL paths in code spans (`/llms.txt`, `/web/favicon.svg`, `/pair`) and an elided package path (`.../scripts/adr_lint.py`) as S4 missing files; an XML namespace URI in braces and a YAML block in a mentioned design file as S5 unrecorded commands. The FO passed only by rewriting a scratch copy and disclosing the override. Archived evidence: subspace-relay `_archive/pair-pages-favicon.md` and `_archive/signed-in-job-split.md`.
- Corroboration (this FO, 2026-11-08, 0.35.0): a YAML fence inside a chief-engineer report cited by path in a gate summary was flagged S5 for dispatch-build-writes-the-dispatch-record; FO cited the report by name instead.
- Upstream first: `absolute_paths` and `inspect_steps` in `kc-dev-flow-2/scripts/delivery_gate.py` and their tests.
- Proposed direction (relay FO's): S4 only for tokens under an existing filesystem root; S5 only for fences with a shell or empty info string, skipping data fences and URIs in braces.
- Non-goals: weakening S5 for real shell commands a validation report shows; changing what a Captain step records.

## Budget
- One package PR touching delivery_gate.py and its tests; workflow word budget unchanged.

## Stop condition
- Each of the five recorded inputs passes `delivery_gate.py question`, and a real shell fence or an existing absolute path still holds, each with a falsifier.

## FO alignment

Alignment: not needed; a gate-check false positive with recorded bites on two adopters.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
