---
title: Four FO-record gaps from issue #815 that no existing task covers
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:issue-815-fo-record-gaps:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:issue-815-fo-record-gaps-backlog-1
              briefing:
                id: briefing:issue-815-fo-record-gaps:backlog:attempt-1:revision-1
                digest: sha256:682708ca0576fdeef2fe8b4599a1968a87fed7c0986e18def0550ea30019102a
                room-ref: ./issue-815-fo-record-gaps/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:issue-815-fo-record-gaps:backlog:1
                briefing: briefing:issue-815-fo-record-gaps:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-10T04:56:06.182671Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-10), answering 「決定：第 20 批這四張（FO 寫下的紀錄當下就由腳本檢查：relay 回報的四個紀錄漏洞、特別角色派工紀錄改由腳本產生、修改驗收條件時當下檢查、PR 說明的署名連結不再被誤擋）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。核准即接受四張任務檔現在寫下的內容；要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: iamcxa/kc-claude-plugins issue #815 (filed 2026-11-09 by the subspace-relay dev2 FO at the Captain's 「同意跑審查，且也同意回報問題」), forwarded to this FO by Paseo 1671c3a9 relaying the Captain's 「這個直接發給 dev2 fo」 (relayed, not a ruling here). The backlog gate is the Captain's.
- Bite (relay observers on four archived subspace-relay tasks, 2026-11-09, not re-run here): (1) `gate record` accepts a reason that does not quote the bound question, although `quotes_bound_question` in `kc-dev-flow-2/scripts/decision_ledger.py` exists (11 of 12 relay gates); (4) the built-screen check in `kc-dev-flow-2/scripts/design_surfaces.py` accepts exactly one `preview:` path while design review and validation need several; (5) `kc-dev-flow-2/scripts/dispatch_records.py --coverage` errors on an archived task directory; (6) the README's Captain steps say `<task>/captain-steps/<N>.md` while `kc-dev-flow-2/scripts/delivery_gate.py` accepts any path named on the summary's `Captain steps:` line (FO read 2026-11-09: the script names no `captain-steps` path).
- Not in this task: issue item 2 belongs to task archive-waits-for-observer-report; item 3 belongs to batch 18 task delivery-check-before-ask-is-provable (PR #817).
- Non-goals: changing Spacedock's own `gate record` (upstream, not ours); item (1) may only be held by a dev2 check FO already runs.

## Budget
- One package PR, or a split the ideation names; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- Each of items 1, 4, 5 and 6 is either fixed with a falsifier or declined with its reason in the design, and issue #815 is answered.

## FO alignment

Alignment: not needed; adopter-reported gaps with recorded bites.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
