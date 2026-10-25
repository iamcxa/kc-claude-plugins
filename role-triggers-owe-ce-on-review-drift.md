---
title: role_triggers.py owes a chief-engineer call when consecutive review rounds find new findings in the same file the last round fixed
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:role-triggers-owe-ce-on-review-drift:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:role-triggers-owe-ce-on-review-drift-backlog-1
              briefing:
                id: briefing:role-triggers-owe-ce-on-review-drift:backlog:attempt-1:revision-1
                digest: sha256:e4942e964e1d983794b901ff2d56e41b0efc2df16c990358038750a773c37d39
                room-ref: ./role-triggers-owe-ce-on-review-drift/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:role-triggers-owe-ce-on-review-drift:backlog:1
                briefing: briefing:role-triggers-owe-ce-on-review-drift:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-25T14:15:25.976039Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-25) answering the batch-6 backlog sitting, which listed this task's backlog briefing-1 question
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「都開」 (chat, 2026-10-23), answering FO's 「要不要把這三項各開成一張待辦任務？我建議開。」, after his 「另外看一下我的 user scrope claude.md 有沒有特別適合 dev2 的部分可以移植的？」; FO read his global ~/.claude/CLAUDE.md and grepped the kc-dev-flow-2 0.28.0 package for each theme (2026-10-23).
- Port: from his global instructions, the circuit breaker ("when the same approach has twice failed to move the state forward, stop"), read as a drift trigger for the chief-engineer.
- Bite: on new-work-starts-from-a-story-map, Codex rounds 1 to 3 on iamcxa/kc-claude-plugins#704 each found new findings in kc-journey-map/lib/journey-review.mjs, the file the previous round fixed; on #675 (2026-10-19) every round found a new gap in the same merge-wording grant. In both FO called the chief-engineer by memory; role_triggers.py counts only repair passes and Captain amendments.
- Upstream first: kc-dev-flow-2 role_triggers.py events; delivery_gate.py hold C (PR #703); workflow.md findings step 5 (round 3 declines).
- Non-goals: changing the round-3 decline rule.
- Batch 6 (2026-10-25): the Captain 「可以」 (chat, 2026-10-25), answering 「需要你決定：這份第 6 批的清單可以嗎？」 about FO's batch-6 list, which placed this task second and widened it: the merge ask also holds while `role_triggers.py` lists a call owed. Bite: iamcxa/kc-claude-plugins#709 merged with an engineering-reviewer call owed for release-acceptance Amendments 1 to 4 (observer, `_archive/release-acceptance/observer.md`); `delivery_gate.py check` exited 0. Drift bite added: #714 rounds 1 to 3 each found a new gap in the same `release_acceptance.py` clean predicate and FO called no chief-engineer.

## FO alignment

Alignment: needed at ideation; what counts as "the same surface" is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
