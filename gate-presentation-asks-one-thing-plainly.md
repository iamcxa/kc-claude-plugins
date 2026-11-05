---
title: FO's Captain-facing gate presentation asks one thing, leads with the conclusion, defines its terms and quotes the bound acceptance sentence
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:gate-presentation-asks-one-thing-plainly:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:gate-presentation-asks-one-thing-plainly-backlog-1
              briefing:
                id: briefing:gate-presentation-asks-one-thing-plainly:backlog:attempt-1:revision-1
                digest: sha256:766a4ed9b303ea4c24293920e8dac3e723ce6bdfbafcb0078cafad86b16ad9f6
                room-ref: ./gate-presentation-asks-one-thing-plainly/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:gate-presentation-asks-one-thing-plainly:backlog:1
                briefing: briefing:gate-presentation-asks-one-thing-plainly:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-05T09:13:03.539703Z"
                decision: approve
                reason: The Captain 「准」 (chat, 2026-11-05), answering 「決定：這批五張（派工交代句的檢查、退一步答案欄位、漏寫 Override、婉拒要寫明、閘門一次問一件事）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？其中「婉拒要寫明」照我提的三項範圍（沒寫 Declined 標籤的婉拒、沒有 F 條目的審查者、沒指明接手任務）。要改哪張直接說。」; accepts the outcome, scope, budget and stop condition in this file, Pilot.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「都開」 (chat, 2026-10-23), answering FO's 「要不要把這三項各開成一張待辦任務？我建議開。」, after his 「另外看一下我的 user scrope claude.md 有沒有特別適合 dev2 的部分可以移植的？」; FO read his global ~/.claude/CLAUDE.md and grepped the kc-dev-flow-2 0.28.0 package for each theme (2026-10-23).
- Port: from his global instructions, "One decision", "No undefined nouns", "Conclusion first" and "Open in plain language", plus a dev2 rule his file does not hold: the chat presentation carries the bound gate question's "approving accepts …" sentence verbatim.
- Bite: observers on four dev2 tasks (codex-reader-reads-receipt-marker, agent-reads-governing-adr, merge-ask-holds-missing-clauses, codex-reader-counts-code-review-only) recorded that the chat question the Captain answered did not carry the bound acceptance sentence; the Captain asked what an FO term meant several times in the 2026-10-21 to 10-23 sittings. The package holds none of these rules (grep of the 0.28.0 markdown for "conclusion first", "one decision", "eight words", "plain language": 0 files).
- Upstream first: Spacedock present-gate skill (render the gate once, name entity, stage, briefing, one recommendation and the decision); kc-dev-flow-2 README Gate content and FO steps.
- Non-goals: his personal language and status-block preferences.
- Rechecked 2026-11-05: grep of the 0.35.0 markdown for the same four phrases still finds 0 files.
- Batch 14: the Captain 「可以」 (chat, 2026-11-05), answering 「這 5 張當下一批，可以嗎？」, which named this task.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- The design names where the four rules and the verbatim acceptance sentence live and what reads them; if it proposes a check, replays of the four observed presentations that lacked the acceptance sentence are held.

## FO alignment

Alignment: needed at ideation; where the rules live (README, a skill, or the Spacedock presenter) is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
