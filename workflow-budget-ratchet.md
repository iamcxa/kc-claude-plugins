---
title: The workflow word budget only goes down, and rules a script enforces shrink to a pointer
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:workflow-budget-ratchet:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:workflow-budget-ratchet-backlog-1
              briefing:
                id: briefing:workflow-budget-ratchet:backlog:attempt-1:revision-1
                digest: sha256:4c554136b2814cfa35beb4612e3de90c6b22b181c396a14ff409e322520d3bef
                room-ref: ./workflow-budget-ratchet/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:workflow-budget-ratchet:backlog:1
                briefing: briefing:workflow-budget-ratchet:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-17T06:10:07.275849Z"
                decision: approve
                reason: Captain approved in chat (「准」) the six batch-2 backlog gates presented together in one message, accepting the recommended profiles (pilot; merge-gatekeeper prod) and the stated order
              application:
                target-stage: ideation
                state: pending
---

Filed on the Captain's words (chat, 2026-10-17): 「棘輪上限＋規則縮短建檔，文件不應該一直變長，除非可以證明文件內容不是一次性載入，這裡的意義是文件如果一次載入太長，那 llm 的注意力八成會失焦」.

## Scope

- Measured on origin/main 2026-10-17: `references/sd/workflow.md` 5495 words, `WORKFLOW_WORD_BUDGET` 5511 in `scripts/lint-skills.py`; at the budget's creation (7b84465e, 2026-10-09) 4414 words and budget 4420. Between those dates the budget was raised in about 22 commits, each to the new word count; the largest cut (#643) removed 70 words. Stage principles and SKILL files for ideation, implementation, validation and dev: 3127 to 3679 words over the same span.
- Ratchet: when a change shortens `workflow.md`, the budget falls to the new count in the same change; a raise needs a Captain ruling recorded with it, and is allowed only with evidence that the added text is not loaded at once (for example a passage moved to a mod, a script's output, or a file read only at one moment).
- Shrink: a rule that a script now checks (laws.md L1 and L2, `dispatch_records.py`, `delivery_gate.py`, `design_surfaces.py`, `observer_check.py`) is reduced in the prose to one pointer sentence when the script's failure message tells the reader what to do; ideation measures the words saved and checks each failure message first.
- Measure, not assert: the attention claim is the Captain's premise; the measure kept by this task is words loaded at once and the observer's count of rules stated in the README but not followed per task (the repeated pattern in observer reports since 2026-10-13).
- Two homes (FO, 2026-10-17, Captain asked 「law跟原則會重複嗎？」): each law in `references/sd/laws.md` opens with a **Rule.** line that restates a README rule (L1: the observer report before the merge sentinel, README `## Extensions` learn and `### done`; L2: the dispatch-record parts, README `## Stages`). No check compares them; `test_laws_check.py` compares laws.md with the runner's registry only. Candidate: the README stays the one home of each rule, laws.md's Rule line names the README section instead of restating it, and the README prose of a law-checked rule shrinks to a pointer.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it (his words are at the top of this file).
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
