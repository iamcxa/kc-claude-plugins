---
title: FO answers its own Paseo workers' permission requests by their listed ids
status: backlog
variant: kc-dev-flow-2
---

When a worker FO started through Paseo asks for a permission, FO answers with the request id Paseo lists for that worker, never a typed or guessed id, never to an archived worker, and without a Captain message for a routine approval.

Source: the Captain, chat 2026-11-03: 「ABC 都開，不屬於套件的本身也要討論一下」, answering 「決定：A、B、C 三個都開成 dev2 任務，跟 #768 一起發版嗎？要刪哪個直接說。」 He also said 「先不合併，我想要把這些也評估修復後，再一起發版」 about Release PR #768. FO had proposed it as: 「FO 批准自己 worker 的權限請求要做對」.

Gap, read on origin/main 2026-11-03 with git grep: the paseo extension covers spawning workers but says nothing about answering their permission requests; the peers extension only says never to answer another agent's request with respond_to_permission.

Bite: the Paseo agent-observatory plugin's reports of 2026-11-03 (sampled transcripts, not yet checked against the source by FO). The qnow FO called respond_to_permission twice with placeholder ids ('permission-exec-3e7b-unused', 'permission-exec-3b7e-placeholder') and once on an archived worker; the relay FO got "No pending Codex app-server permission request" three times, once after sending to the wrong worker; both sent the Captain a status message after nearly every routine approval.

Consumer: every adopter FO that lists the paseo extension and starts Codex workers through Paseo.
