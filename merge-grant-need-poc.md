---
title: POC — is a per-class merge grant needed, or does the Captain's pre-authorized merge already cover it
variant: kc-dev-flow-2
profile: poc
merge: pr
status: backlog
---

Filed on the Captain's 「同意」 (chat, 2026-10-18) to FO's proposal to narrow merge-gatekeeper (PR #666) and turn the grant half into a measure-first POC: 「授權那半不要開成「之後重做」，改開一個 POC 待辦，先量兩件事：adopter 裡有多少 PR 可以被授權；「預先授權合併」是不是已經涵蓋了你要的效果。量完確定有需要，才把程式碼從分支拿回來。」

## Scope

- Measure 1: in subspace-relay, subspace-web and qnow, how many merged PRs over a stated window would class as grant-eligible (not `never`) under the never list #666 ships; read-only `gh`.
- Measure 2: how often the Captain already uses a pre-authorized merge at a delivery gate (「預先授權」, 「批准並合併」 and similar) and how many of his turns per delivered PR remain, from the dev2 ledgers and state of this repository and the adopters.
- Parked code: the grant, merge-line and calibrate code, its tests, ADR 0023 and the AC-5 real-repository run are on branch spacedock-ensign/merge-gatekeeper at 3fd841789db9c76d863ae4f723184c790471a7da; two Codex P1 on that code are open (review:5562139252: grants read from the working tree, not the fetched trunk; an unreadable PR state counted as pending).
- Bar: set by the Captain at the backlog gate; the code returns only if the POC passes it.
- Retrieval (FO, 2026-10-19): the PR branch was deleted on merge; 3fd841789db9c76d863ae4f723184c790471a7da stays reachable from GitHub's refs/pull/666/head (head a05b18a0): `git fetch origin refs/pull/666/head`.
