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
---

Both close receipts the wrapper has produced carry `merged_sha: null`: `close-receipt-ship-cloud-wrapper-r2.json` (kc-claude-plugins `spacedock-state/ship`, 2026-09-11) and `close-receipt-qnow-clerk-poc.json` (qnow `spacedock-state/ship`, 2026-09-14). Nothing in `close.py` reads the merge commit, although every closed task carries the `pr: pr-merge:N` sentinel that names it. On 2026-09-11 the r2 fence also had to be corrected by hand because debrief matching picked the ship FO's own debrief (it names every slug in its Filed section) instead of each worker's.

## Accepted outcome

1. At close, for every task with `pr: pr-merge:N`, `merged_sha` is resolved from `gh pr view N --repo <owner/repo> --json mergeCommit` (repo from the state checkout's remote) and written to the receipt; a task whose PR is not `MERGED` is refused with its state named, not closed with null.
2. Debrief matching prefers the debrief written by the task's own worker: a `_debriefs/*.md` whose body names the slug under `## Shipped` and whose frontmatter or body carries the worker's session id or dispatch token when present; the ship FO's debrief is never matched to a task. The r2 fence correction (paths -04/-05, shas 916010b3/b4c34965) is the fixture.
3. `close.py --validate` refuses a v2 receipt whose task `merged_sha` is null or not a 40-hex SHA.
4. Fixtures pin no real SHA from this repository; measured evidence is quoted in the PR body.

Profile recommendation: pilot (harden round; retained code with fixtures).
