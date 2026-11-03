# 0052. FO answers its own Paseo workers' permission requests

Date: 2026-11-03

## Status

Accepted

## Context

The task fo-answers-own-worker-permissions-by-listed-id checked two First Officer
(FO) transcripts: seven refused agent/request pairs were recovered on the next
call, while about 2,100 routine permission turns ended in a Captain status
message. ADR 0048 says FO never answers a worker's permission; the Captain
subsequently chose that FO answers its own workers within its existing authority.

## Decision

**Words:** 「可以」 — Captain, chat, 2026-11-03.

**Asked:** 「決定：A 的方向定為『FO 回應自己 ensign 的權限請求，只批它自己本來就能做的事；推送到別人的 repo、合併、祕密、刪除、對外寫入一律交給你』，可以嗎？」

**Words, design approval:** 「可以」 — Captain, chat, 2026-11-03,
recorded in the task's ideation gate.

**Asked, design approval:** 「決定：七張設計照建議進實作，但驗收到期提醒的 D7 改成『在 kc-journey-map 登記 journey-progress/v1，預算放寬為兩個 PR，kc-journey-map 那個先合併』，可以嗎？」
That gate accepts this design's recommendation D1: FO may approve commands run
through the secrets wrapper without reading or printing a secret value, and
deletion of the task's own temporary files. Secret-value reads or prints and
other deletions remain held for the Captain.

**Options considered:**
- FO answers its own dispatched workers within its existing scope and authority,
  including wrapper runs and task-owned temporary-file cleanup (chosen).
- Treat wrapper runs and temporary-file cleanup as Captain holds too.
- Keep ADR 0048's prohibition on FO answering worker permissions.

**Recommended:** The first option, including D1, as the Captain accepted.

**Protects:** none

This replaces ADR 0048's sentence "FO never answers the worker's permission on
its behalf." The rest of ADR 0048 remains in force; that file is not changed.
The listed paseo extension's `Worker permission requests` section owns the
answering procedure, authority holds, paired ids, recovery and silent routine
answers. Another agent's requests still follow peers. A permission answer grants
no additional authority; ADR 0011's money and Captain-judgment boundaries remain.

## Consequences

The extension grows from 819 to 1,048 words by `wc -w`, and from 829 to 1,062 by
`normalized_words` in `kc-dev-flow-2/scripts/lint-skills.py`. This replaces ADR
0048's 819-word extension bound; the shared workflow and its word budget stay
unchanged. Dispatch reads 233 more normalized words; callback package words do
not increase. Routine answers produce no Captain reply; held requests produce
one message each. Recovery adds a status read after a refusal or missing block,
not before every answer.

Paseo's pending-request lookup rejects an id not pending for that agent. Scope,
authority and silence remain instructions for FO, with its own host's permission
checks as a backstop; this change adds no hook or mechanical policy checker.
Revisit if an authority boundary is crossed or routine approval messages persist.
