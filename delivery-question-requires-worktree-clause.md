---
title: The delivery question check requires the worktree-removal clause the README's delivery authority names
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:delivery-question-requires-worktree-clause:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-question-requires-worktree-clause-backlog-1
              briefing:
                id: briefing:delivery-question-requires-worktree-clause:backlog:attempt-1:revision-1
                digest: sha256:ba8563c210867d7ecddff66df52b43a9cab332e30fea940585d7d097192a5f72
                room-ref: ./delivery-question-requires-worktree-clause/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-question-requires-worktree-clause:backlog:1
                briefing: briefing:delivery-question-requires-worktree-clause:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-05T17:19:03.402913Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-06), answering 「決定：「合併問句要有移除 worktree 那一句」這張用 Pilot，照任務寫下的範圍、預算與停止條件進入構想嗎？」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

`delivery_gate.py question` holds a validation gate question that omits "removing its clean, pushed worktree", so an approval cannot be read as covering a cleanup it never named.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering FO's batch 14 retrospective ask 「Should I open these two backlog tasks?」, whose second item was this check gap.
- Bite: the batch 14 merge questions for #786 and #787 omitted the clause; `delivery_gate.py question` and `check` both exited 0 on them; FO then removed both clean, pushed worktrees without that authority, and the extension-instruction-check-sees-every-listed-extension observer recorded it as a Delivery authority violation (observer.md, 2026-11-05).
- Upstream first: README Delivery authority ("removing its clean, pushed worktree"); `delivery_gate.py` question clause checks (`ASK_FORM` and the existing clause list).
- Non-goals: changing who may remove a worktree.

- Batch 15: the Captain 「可以」 (chat, 2026-11-06), answering 「第 15 批做這 2 張，可以嗎？其他 4 張要退休或擱置，我下一題再問你。」, which named this task.

## Budget
- One package PR; the workflow word budget does not rise.

## Stop condition
- Replays of the #786 and #787 questions are held by `delivery_gate.py question`; the #788 question, which carries the clause, passes.

## FO alignment

Alignment: not needed: the clause is already the README's rule; the check only reads it.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
