---
title: A task whose approved backlog gate was never consumed can be retired
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: handed over by the kc-adr FO (Paseo session 1bcf070c), 2026-10-25, relaying the Captain's 「轉」 answering 「要不要把這個 Spacedock 缺口轉給 dev2 FO」 (relayed).
- Bite: dev2 task `kc-decision-log-handoff-trial`. The Captain retired it on 2026-10-25 (「按建議退休」, relayed; recorded under a `## Closed` section). Its backlog gate holds an approval targeting ideation, application `state: pending`, condition `approved-pending`. `spacedock merge guard <slug> --verdict rejected` refuses ("entity carries no binding pending terminal-target approval"); `gate withdraw` covers only open gates; `status --set` has no archive (Spacedock 0.27.2 `gate --help`, 2026-10-25). The task stays in backlog with only the Closed note as a guard; a boot that reads the pending approval may offer to consume it and dispatch ideation.
- Precedent that worked: the 2026-10-20 follow-up closes (for example `_archive/codex-review-round3-followups.md`, verdict REJECTED, archived by merge guard) carried no gates block. A task past its backlog gate cannot take that route.
- Upstream first: the missing operation is Spacedock's (gate lifecycle and merge guard). This task decides the dev2 side: whether dev2 documents an interim route (for example consume, then hold at the ideation gate) or only carries the gap to the Spacedock owner. An issue or PR on the Spacedock repository needs the Captain's approval first.
- Non-goals: editing state by hand or forcing a terminal `status --set`.

## FO alignment

Alignment: needed before ideation: the upstream route and any interim dev2 route are the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
