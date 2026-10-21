---
title: The merge-ask check holds a question that omits the round count or the carried clauses, or a task that owes a special-role call
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:merge-ask-holds-missing-clauses:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:merge-ask-holds-missing-clauses-backlog-1
              briefing:
                id: briefing:merge-ask-holds-missing-clauses:backlog:attempt-1:revision-1
                digest: sha256:ddccb57f67c68ec8d052dd67533a52aff3d9e499946b1ccb0473cb30c5239dd8
                room-ref: ./merge-ask-holds-missing-clauses/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:merge-ask-holds-missing-clauses:backlog:1
                briefing: briefing:merge-ask-holds-missing-clauses:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T07:28:43.415116Z"
                decision: approve
                reason: Captain 「繼續」 (chat, 2026-10-21), answering FO's question 「這 5 張都批准進入設計嗎？」 for the five batch-5 backlog gates presented together; approves entering ideation under the pilot profile, as recommended.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain's 「可以」 (chat, 2026-10-21) to FO's batch-4 close question 「A、B、C 要不要合成一張任務，排進第五批？」, where A, B and C were package-issue candidates from the four batch-4 learn runs (all no-change: each observer finding restated an existing rule FO had not followed).
- A. The gate summary names no external-round count although the README requires "FO counts rounds and records the count in the committed gate summary": observer findings on commissioned-by-names-spacedock, db-surface-without-migrations and (partial) fo-write-rules-checked.
- B. The delivery question omits clauses the README's Delivery authority requires (approval also covers later external-review rounds on the same PR, merging the full head unless he says he merges or holds, removing the clean pushed worktree): observer findings on fo-batch-sittings and fo-write-rules-checked (partial).
- C. fo-batch-sittings merged while `role_triggers.py` owed an engineering-reviewer call for replacing Captain amendments 1 to 3; the observer found it after the merge and FO recorded it as not run.
- Shape asked for: `delivery_gate.py check`, which FO already runs before every merge ask, holds on each of A, B and C, so no new script and no new FO step.
- Upstream first: `delivery_gate.py` (its Sufficiency/Necessity clause checks are the precedent for A and B), `role_triggers.py` (C), the observer.
- Non-goals: the other candidates of the same list (D: seed check before a backlog gate; E: amendment wording and Override placement; F: single occurrences), each the Captain's separate call.

## FO alignment

Alignment: not needed before ideation; the Captain chose the combination and the check.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
