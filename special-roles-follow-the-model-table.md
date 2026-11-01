---
title: Special roles follow the Captain's model table, and the trigger check recognizes Codex models
status: ideation
variant: kc-dev-flow-2
profile: pilot
gates:
    version: 1
    records:
        - id: gate:special-roles-follow-the-model-table:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:special-roles-follow-the-model-table-backlog-1
              briefing:
                id: briefing:special-roles-follow-the-model-table:backlog:attempt-1:revision-1
                digest: sha256:b2c65d5d5587dfaa508f2ffe71c13a4672dad8862a220fd572d9f9f14c343bb2
                room-ref: ./special-roles-follow-the-model-table/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:special-roles-follow-the-model-table:backlog:1
                briefing: briefing:special-roles-follow-the-model-table:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-01T17:48:13.754386Z"
                decision: approve
                reason: The Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering the batch 12 sitting 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」; approves Pilot, this outcome and these bounds, with the stated change.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」, items 3 and 5. The Captain, chat 2026-11-02: 「我認為 codex 的實作者可以預設比 claude 多高一個推理等級，例如 Sonnet / high，對應 Sol / xhigh，總監也是」 and 「不要用到 max，最高就是 xigh 就好」.
- The table he approved:

| Role | On Claude | On Codex |
|---|---|---|
| implementation | Sonnet / high | Sol / xhigh |
| chief-engineer | Opus / xhigh | Astra / xhigh |
| engineering-reviewer | Opus / xhigh | Astra / xhigh |
| design-director | Sonnet / high | Sol / xhigh |
| ideation | Opus / high | Astra / xhigh |
| validation | Opus / high | Astra / xhigh |
| observer | Sonnet / high | Sol / high |

- Chief-engineer and engineering-reviewer run on a different family from the workers; so usually Opus / xhigh here, Astra / xhigh when the workers are Claude.
- Bite: `role_triggers.py` ranks Claude model names only, so a Codex engineering-reviewer call on 2026-10-30 had to be recorded as a waiver (`_archive/peers-paseo-rule-matches-practice.md`, FO alignment). `agents/design-director.md` and FO's notes disagreed on its model.
- Consumer: every FO dispatching a special role.
- Upstream first: `agents/*.md`, `scripts/role_triggers.py`, `references/sd/workflow.md` Stages.

## Non-goals

- Host changes; automatic model substitution; changing when a role is called.

## Budget

- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition

- A Reviewer line naming a table model on either family clears its event; a cheaper one does not. Each role's declared settings and the workflow text agree with the table.

## FO alignment

Alignment: needed before ideation; the scope is the Captain's ruling.
Result: aligned at backlog: Batch 12 backlog sitting: the Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
