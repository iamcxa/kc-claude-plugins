---
title: "close.py records merged_sha from the merged PR and matches each task's debrief by its worker, not the FO's"
status: backlog
source: "Captain 2026-09-14 「派」 (ship round 3, harden); findings recorded on spacedock-state/ship questions logs"
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r3
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: fgvjsq1wsftn2r6ay4yxp2q1
gates:
    version: 1
    records:
        - id: gate:fgvjsq1wsftn2r6ay4yxp2q1:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fgvjsq1wsftn2r6ay4yxp2q1-backlog-1
              briefing:
                id: briefing:fgvjsq1wsftn2r6ay4yxp2q1:backlog:attempt-1:revision-1
                digest: sha256:b8a5bd66a43bbc4856d5f586e7bd2ac2ddc826390eef26cd52f69dd2d8eda87a
                room-ref: ./ship-close-records-merged-sha-and-worker-debrief/review/backlog/briefing-1
---

Both close receipts the wrapper has produced carry `merged_sha: null`: `close-receipt-ship-cloud-wrapper-r2.json` (kc-claude-plugins `spacedock-state/ship`, 2026-09-11) and `close-receipt-qnow-clerk-poc.json` (qnow `spacedock-state/ship`, 2026-09-14). Nothing in `close.py` reads the merge commit, although every closed task carries the `pr: pr-merge:N` sentinel that names it. On 2026-09-11 the r2 fence also had to be corrected by hand because debrief matching picked the ship FO's own debrief (it names every slug in its Filed section) instead of each worker's.

## Accepted outcome

1. At close, for every task with `pr: pr-merge:N`, `merged_sha` is resolved from `gh pr view N --repo <owner/repo> --json mergeCommit` (repo from the state checkout's remote) and written to the receipt; a task whose PR is not `MERGED` is refused with its state named, not closed with null.
2. Debrief matching prefers the debrief written by the task's own worker: a `_debriefs/*.md` whose body names the slug under `## Shipped` and whose frontmatter or body carries the worker's session id or dispatch token when present; the ship FO's debrief is never matched to a task. The r2 fence correction (paths -04/-05, shas 916010b3/b4c34965) is the fixture.
3. `close.py --validate` refuses a v2 receipt whose task `merged_sha` is null or not a 40-hex SHA.
4. Fixtures pin no real SHA from this repository; measured evidence is quoted in the PR body.


## Acceptance criteria

* **AC-1** For a task with `pr: pr-merge:N`, `close.py` writes `merged_sha` as the 40-hex `mergeCommit.oid` from `gh pr view N --repo <owner/repo> --json state,mergeCommit`; when `state` is not `MERGED` it exits non-zero naming the slug and state, and writes no receipt.
* **AC-2** Debrief matching picks a `_debriefs/*.md` whose `## Shipped` names the slug and which is not the ship FO's own debrief; with the r2 fixture (two worker debriefs plus one FO debrief naming every slug) each task maps to its worker's file.
* **AC-3** `close.py --validate` refuses a v2 receipt whose task `merged_sha` is null or not 40 hex.
* **AC-4** `close.test.py` covers AC-1..AC-3 with fake `gh` output; no fixture pins a real SHA from this repository.

## Non-goals

- No schema version bump beyond what AC-3 needs; no change to `uat-doc.py` output.
- No network call other than `gh pr view`.

## Route-back conditions

- Back to backlog if the pr-merge mod's sentinel format changes from `pr-merge:N`, or if worker debriefs stop carrying a `## Shipped` section.

Profile recommendation: pilot (harden round; retained code with fixtures).
