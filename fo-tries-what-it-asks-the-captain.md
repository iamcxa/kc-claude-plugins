---
title: FO runs any step it asks the Captain to run or look at, as far as it goes without his credentials, and names the one step only he can do
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:fo-tries-what-it-asks-the-captain:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fo-tries-what-it-asks-the-captain-backlog-1
              briefing:
                id: briefing:fo-tries-what-it-asks-the-captain:backlog:attempt-1:revision-1
                digest: sha256:5d93bd5c4e59e52a707a26702879e3c788dd6207c41b26a30c16fcd689aa4f3d
                room-ref: ./fo-tries-what-it-asks-the-captain/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fo-tries-what-it-asks-the-captain:backlog:1
                briefing: briefing:fo-tries-what-it-asks-the-captain:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-03T07:44:53.312067Z"
                decision: approve
                reason: The Captain 「進」 (chat, 2026-11-03), answering the batch 13 sitting 「決定：這批七張（A 權限、B 同症狀計數、C 改寫條件比對原話、D release 驗收不在正式站、來源標註、FO 先自己試、release 驗收到期提醒）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？要改哪張直接說。」; approves Pilot, these outcomes and bounds.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: intake from the subspace-relay dev2 FO (Paseo agent 1671c3a9, 2026-10-21), quoting the Captain there (relayed, not a ruling in this session): 「都准。但注意，412 你以後應該要自己先測試過才轉給我 UAT，這是 dev2 規範有缺，還是寫得不夠好沒有讓你執行？」 and 「可以，提給 dev2 fo」; an earlier instance on 2026-10-13 (relay task agent-review-identity): 「之後你要我跑的東西你應該要自己跑過一次」.
- Bite: relay PR #412 (task room-modals-try-copy, profile pilot): FO did not run the validator's acceptance script as written before the gate, which breaks the existing rule in kc-dev-flow-2 0.27.0 `skills/validation/principles.md` ("FO runs it as written before the gate"); separately FO asked the Captain for a browser UAT step (open an owner link, sign in as owner) that neither FO nor the validator had driven.
- The gap reported: the rule covers only the acceptance script. Nothing covers an ad-hoc check FO asks of the Captain outside it (a browser flow, an extra command, a token step), so FO can hand him an untried step and stay compliant.
- Shape proposed by the relaying FO (its wording, not the Captain's): before FO asks the Captain to run or look at anything, it runs that step itself as far as it goes without his credentials (for a UI flow, a real browser up to the step that needs his account or token), shows the observed output, and names the one step only he can do and why.
- First ideation step: check whether the miss is a missing rule or an unenforced one (the acceptance-script half is an existing rule FO did not follow), and where a check could catch it (the gate presentation, delivery_gate.py's ask text, the observer).
- Upstream first: validation principles, the README's FO steps and Delivery authority, delivery_gate.py, the observer; relay's state record for the evidence.
- Batch 13: the Captain 「可以」 (chat, 2026-11-03), answering 「決定：這批加入那 3 張，共 7 張一起進 backlog gate 嗎？」, which named this task.
- Further bite: the agent-observatory report on the qnow FO, 2026-11-03 (sampled; not yet checked against the source): a handbook command the FO handed the Captain, seed-captain-fixtures.py, failed with No such file or directory.

## Non-goals
- FO using the Captain's own credentials or account to finish a step; a new stage.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- Replays of relay #412 and the qnow handbook step are caught before the ask reaches the Captain, and a step FO ran itself, shown with its observed output and the one step only he can do, passes.

## FO alignment

Alignment: needed at ideation; whether a new rule or an enforcement point is the answer is the Captain's call.
Result: aligned at backlog: Batch 13 backlog sitting, the Captain 「進」 (chat, 2026-11-03), answering 「決定：這批七張（A 權限、B 同症狀計數、C 改寫條件比對原話、D release 驗收不在正式站、來源標註、FO 先自己試、release 驗收到期提醒）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？要改哪張直接說。」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
