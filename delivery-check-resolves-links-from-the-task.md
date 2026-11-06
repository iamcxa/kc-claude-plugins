---
title: The delivery check resolves a report's relative Markdown links against the task folder, not the shell's current directory
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:delivery-check-resolves-links-from-the-task:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-check-resolves-links-from-the-task-backlog-1
              briefing:
                id: briefing:delivery-check-resolves-links-from-the-task:backlog:attempt-1:revision-1
                digest: sha256:23187241979e330ede36c7eb8884b7719c28cd95d4ee02553b92d0765f72712f
                room-ref: ./delivery-check-resolves-links-from-the-task/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-check-resolves-links-from-the-task:backlog:1
                briefing: briefing:delivery-check-resolves-links-from-the-task:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-06T14:28:48.874767Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-06), answering 「決定：第 16 批這五張（跳過的 CI 不擋、Codex 只貼安全摘要時提醒、交付檢查的相對路徑、ADR 編號跨流程預留、婉拒只在出過事時開任務）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？核准即接受「婉拒只在出過事時開任務」任務裡寫的標準（指出真的錯並說得出誰受害、再次出現、或你要求）。要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

`delivery_gate.py question` and `check` read a relative `.md` path named in the gate text or the validation report from the task's own folder, so the result does not depend on where FO runs the command.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering FO's batch 15 retrospective ask 「要為這個路徑解析的缺陷開一張待辦嗎？」.
- Bite: at the batch 15 validation gate of delivery-question-requires-worktree-clause (2026-11-06), `delivery_gate.py question` run from the repository root printed "Captain steps record fails: message S5: unrecorded command or link '/plugin marketplace add iamcxa/kc-claude-plugins'": the report names `validation/README.md`, and the check opened the repository's root README.md instead. Run from the task folder, the same text printed "gate text complete" (FO runs, 2026-11-06).
- Added 2026-11-06 from fo-feedback round 005 (qnow FO, operator report): on qnow #1338, `delivery_gate.py question` failed on web paths in the validator's report read as local files, and the Captain waived it (「豁免網址路徑誤判」); same resolver, so URLs belong in this task's scope.
- Upstream first: `delivery_gate.py` `inspect_steps` (the `markdown` path list and `Path(...)` resolution) and `captain_step_problems`.
- Non-goals: changing which links count as steps.

- Batch 16: the Captain 「可以，就這樣」 (chat, 2026-11-06), answering 「這批做 2、3、4、5、9 這 5 張，可以嗎？」, which named this task.

## Budget
- One package PR; the workflow word budget does not rise.

## Stop condition
- The same gate text and report give the same verdict whether `question` runs from the repository root, the state checkout or the task folder; a replay of the batch 15 case passes from the repository root.

## FO alignment

Alignment: not needed: a resolution bug in an existing check; the rule it applies does not change.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
