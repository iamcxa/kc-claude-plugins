---
title: FO answers its own Paseo workers' permission requests by their listed ids
status: backlog
variant: kc-dev-flow-2
gates:
    version: 1
    records:
        - id: gate:fo-answers-own-worker-permissions-by-listed-id:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fo-answers-own-worker-permissions-by-listed-id-backlog-1
              briefing:
                id: briefing:fo-answers-own-worker-permissions-by-listed-id:backlog:attempt-1:revision-1
                digest: sha256:a0980e15d318f3da5e9c3255e90ea4a61b21eae8905bdd1a2cd4d3bd5c96627f
                room-ref: ./fo-answers-own-worker-permissions-by-listed-id/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-03T07:37:03.138084Z"
                reason: The Captain added a boundary to the outcome (chat, 2026-11-03); the bound briefing predates it.
            - id: gate-attempt:fo-answers-own-worker-permissions-by-listed-id-backlog-2
              briefing:
                id: briefing:fo-answers-own-worker-permissions-by-listed-id:backlog:attempt-2:revision-1
                digest: sha256:2fd09df20acdcff9d45e39f9cc840f5f3a2849975f1aedefb42b8a2174e65858
                room-ref: ./fo-answers-own-worker-permissions-by-listed-id/review/backlog/briefing-2
              withdrawal:
                by: agent:first-officer
                at: "2026-11-03T07:38:56.594021Z"
                reason: The Captain widened the batch 13 sitting to seven tasks (chat, 2026-11-03); the bound question named four.
            - id: gate-attempt:fo-answers-own-worker-permissions-by-listed-id-backlog-3
              briefing:
                id: briefing:fo-answers-own-worker-permissions-by-listed-id:backlog:attempt-3:revision-1
                digest: sha256:97b677babe6419fab2ac19f090020da3315d13b827e321b8aeece83acc7732ba
                room-ref: ./fo-answers-own-worker-permissions-by-listed-id/review/backlog/briefing-3
---

## Scope
- Source: Batch 13 sitting, the Captain, chat 2026-11-03: 「ABC 都開，不屬於套件的本身也要討論一下」, answering 「決定：A、B、C 三個都開成 dev2 任務，跟 #768 一起發版嗎？要刪哪個直接說。」; and 「先不合併，我想要把這些也評估修復後，再一起發版」 about Release PR #768. FO had proposed it as 「FO 批准自己 worker 的權限請求要做對」. Then the Captain 「paseo-fo-board 是另外一個狀況，FO指揮官是另外一個組合。單討論 FO 與 ensign 則是 FO應該回應 ensign 的權限請求，合理嗎？」, and 「可以」 answering 「決定：A 的方向定為『FO 回應自己 ensign 的權限請求，只批它自己本來就能做的事；推送到別人的 repo、合併、祕密、刪除、對外寫入一律交給你』，可以嗎？」.
- Outcome: when a worker FO started through Paseo asks for a permission, FO answers with the request id Paseo lists for that worker, never a typed or guessed id, never to an archived worker, and without a Captain message for a routine approval. FO approves only what it could do itself; a push to a repository the Captain does not own, a merge or close, a secret read, a deletion or irreversible action, and any message to a person or other outward write go to the Captain. A coordinator over several FOs (`paseo-fo-board`) is a separate arrangement and outside this task.
- Gap, read on origin/main 2026-11-03 with git grep: `extensions/paseo/EXTENSION.md` covers spawning workers but not answering their permission requests; `extensions/peers/EXTENSION.md` only says never to answer another agent's request with respond_to_permission.
- Bite: the Paseo agent-observatory reports of 2026-11-03 (sampled transcripts, not yet checked against the source). The qnow FO called respond_to_permission twice with placeholder ids ('permission-exec-3e7b-unused', 'permission-exec-3b7e-placeholder') and once on an archived worker; the relay FO got "No pending Codex app-server permission request" three times, once after sending to the wrong worker; both sent the Captain a status message after nearly every routine approval.
- Consumer: every adopter FO that lists the paseo extension and starts workers through Paseo.
- Upstream first: `extensions/paseo/EXTENSION.md`, `extensions/peers/EXTENSION.md`, and Paseo's own skill for list_pending_permissions and respond_to_permission.

## Non-goals
- Approving a request without FO reading it; changing worker permission modes; answering another agent's request, which the peers rule keeps forbidden.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## FO alignment
Alignment: needed before ideation; the scope is the Captain's ruling and the evidence is an observatory sample, which ideation must check against its source first.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Stop condition
- Each observed failure (a guessed id, a wrong or archived worker, a message per routine approval) is named and stopped at a point FO reaches before respond_to_permission, shown on a replay of the observed sequence.
