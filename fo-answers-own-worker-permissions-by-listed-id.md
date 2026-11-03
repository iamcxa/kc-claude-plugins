---
title: FO answers its own Paseo workers' permission requests by their listed ids
status: backlog
variant: kc-dev-flow-2
---

## Scope
- Source: Batch 13 sitting, the Captain, chat 2026-11-03: 「ABC 都開，不屬於套件的本身也要討論一下」, answering 「決定：A、B、C 三個都開成 dev2 任務，跟 #768 一起發版嗎？要刪哪個直接說。」; and 「先不合併，我想要把這些也評估修復後，再一起發版」 about Release PR #768. FO had proposed it as 「FO 批准自己 worker 的權限請求要做對」.
- Outcome: when a worker FO started through Paseo asks for a permission, FO answers with the request id Paseo lists for that worker, never a typed or guessed id, never to an archived worker, and without a Captain message for a routine approval.
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
