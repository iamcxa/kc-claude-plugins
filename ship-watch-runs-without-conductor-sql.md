---
title: "watch.sh runs without the Conductor SQL endpoint: sql is a degradable surface, session status and session message are the fallback reads"
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
id: 9xtwqxmktq2e15hr1qhx0bbb
gates:
    version: 1
    records:
        - id: gate:9xtwqxmktq2e15hr1qhx0bbb:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:9xtwqxmktq2e15hr1qhx0bbb-backlog-1
              briefing:
                id: briefing:9xtwqxmktq2e15hr1qhx0bbb:backlog:attempt-1:revision-1
                digest: sha256:febac74edab36f79f750a791eb8cd67413792deeea1893aabffb75ea4a16f4c4
                room-ref: ./ship-watch-runs-without-conductor-sql/review/backlog/briefing-1
---

The Conductor SQL endpoint (`conductor sql`) returned "The SQL search API endpoint is temporarily disabled (HTTP 503)" from 2026-09-13 ~04:20 UTC through at least 2026-09-14 08:00 UTC (re-probed at filing: still 503). `dispatch.sh` 0.2.0 exits 5 when the `sql "SELECT 1"` probe fails, so the whole `qnow-clerk-poc` batch ran on a scratch copy with the probe replaced by a stderr note, and `watch.sh` could not read transcripts at all; the ship FO watched by hand. What did work for every read across the batch: `conductor --json session status <sid>` (idle/working), `conductor --json session message <sid> --limit N --offset M` (offset past the end returns no `sessionIndex`, so a binary search finds the tail), `conductor --json workspace status <ws>`, and the state branch.

## Accepted outcome

1. `pins/conductor-cli.contract` marks `sql` as degradable: a failed sql probe makes `dispatch.sh` print a dated degraded notice and continue; the other read-only probes stay fatal.
2. `watch.sh` detects sql unavailability once per run and switches to the fallback reads named above; it still exits gate-prepared|pending|quota|question|stopped, reading questions from the entity's stage report (`Q:` lines) and the last assistant text of the session tail.
3. The degraded mode is recorded in the batch questions log with the probe output and date.
4. Fixture: a fake `conductor` on PATH whose `sql` returns the 503 text and whose `session message` serves a recorded tail; both exit paths are exercised.


## Acceptance criteria

* **AC-1** With a `conductor` on PATH whose `sql` prints the 503 text, `dispatch.sh --dry-run` exits 0 and prints one dated degraded notice on stderr; with `auth whoami` failing it still exits 5.
* **AC-2** `watch.sh <sprint> --once` against the same fake exits `gate-prepared` when the state branch shows a prepared gate, `question` when the session tail's last assistant text or the stage report carries a `Q:` line, `pending` otherwise, without calling `sql`.
* **AC-3** The fake `conductor` serves `session status` and `session message --limit N --offset M` from recorded files; `watch.test.sh` covers both exits in AC-2 and the sql-available path unchanged.
* **AC-4** The batch questions log receives one line naming the degraded mode, the probe output and the date, written by `watch.sh` on first detection.

## Non-goals

- No change to the pinned Conductor CLI version or to the other read-only probes.
- No transcript parsing beyond the last assistant text of the tail; no SQL replacement service.
- No change to the exit-code vocabulary of `watch.sh`.

## Route-back conditions

- Back to backlog if `conductor session message --offset` stops returning `sessionIndex` for the tail on CLI 0.85.0, or if the used-surface probe shape has to change to make the fallback work (that is the dispatch task's file).

Profile recommendation: pilot.
