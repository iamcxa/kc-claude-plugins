---
title: "watch.sh runs without the Conductor SQL endpoint: sql is a degradable surface, session status and session message are the fallback reads"
status: implementation
source: "Captain 2026-09-14 「派」 (ship round 3, harden); findings recorded on spacedock-state/ship questions logs"
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r3
sprint-readiness: ready
started: 2026-09-14T13:50:50Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-ship-watch-runs-without-conductor-sql
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
              resolution:
                type: Resolution
                id: resolution:spacedock:9xtwqxmktq2e15hr1qhx0bbb:backlog:1
                briefing: briefing:9xtwqxmktq2e15hr1qhx0bbb:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T13:45:44.467595Z"
                decision: approve
                reason: 'batch admission: the Captain approved the five-task r3 batch; ship FO records on the batch conn'
                conn:
                    quote: 准
                    source: Captain chat 2026-09-14, approving the ship-cloud-wrapper-r3 batch of five (pilot profile)
              application:
                target-stage: ideation
                state: consumed
        - id: gate:9xtwqxmktq2e15hr1qhx0bbb:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:9xtwqxmktq2e15hr1qhx0bbb-ideation-1
              briefing:
                id: briefing:9xtwqxmktq2e15hr1qhx0bbb:ideation:attempt-1:revision-1
                digest: sha256:2520572e6c21ecaed5fc95daa393b2f60a2a7173cf5667b3a91aec750dbba1ac
                room-ref: ./ship-watch-runs-without-conductor-sql/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:9xtwqxmktq2e15hr1qhx0bbb:ideation:1
                briefing: briefing:9xtwqxmktq2e15hr1qhx0bbb:ideation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T14:02:53.155394Z"
                decision: approve
                reason: 'ideation read by the ship FO: shape grounded in dispatch.sh/watch.sh/contract/runbook. Ruling on the flagged AC-1 contradiction: keep the existing exit code (2) for a failing non-sql probe; AC-1''s ''5'' was the brief author''s error — correct AC-1 to ''exits non-zero as today (2)'' in the shape, non-goal #3 stands. Enter implementation.'
                conn:
                    quote: 准
                    source: Captain chat 2026-09-14, approving the ship-cloud-wrapper-r3 batch of five (pilot profile)
              application:
                target-stage: implementation
                state: consumed
---

The Conductor SQL endpoint (`conductor sql`) returned "The SQL search API endpoint is temporarily disabled (HTTP 503)" from 2026-09-13 ~04:20 UTC through at least 2026-09-14 08:00 UTC (re-probed at filing: still 503). `dispatch.sh` 0.2.0 exits 5 when the `sql "SELECT 1"` probe fails, so the whole `qnow-clerk-poc` batch ran on a scratch copy with the probe replaced by a stderr note, and `watch.sh` could not read transcripts at all; the ship FO watched by hand. What did work for every read across the batch: `conductor --json session status <sid>` (idle/working), `conductor --json session message <sid> --limit N --offset M` (offset past the end returns no `sessionIndex`, so a binary search finds the tail), `conductor --json workspace status <ws>`, and the state branch.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >
    Limited real use (ship first officers running the r3 batch and beyond) creates
    persistent value in dispatch.sh/watch.sh; the sql outage is not a one-off and the
    fallback path is likely to be iterated on. No production credentials, destructive
    mutation, or irreversible migration is in scope; a consumer (the ship FO) can take
    the new dispatch.sh/watch.sh versions without editing owned records or config.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - "pins/conductor-cli.contract marks sql as a degradable probe distinct from the fatal read-only probes"
      - "watch.sh gains a once-per-run sql-unavailability detector that switches to the session status/message fallback reads"
    implementation:
      - "dispatch.sh prints one dated degraded notice and continues past a failed sql probe; other read-only probes stay fatal"
      - "watch.sh reads Q: lines from the entity stage report and the session tail's last assistant text without calling sql"
      - "first detection of sql unavailability writes one line to the batch questions log naming the degraded mode, probe output, and date"
    testing:
      - "fixture: fake conductor on PATH whose sql returns the 503 text and whose session message serves a recorded tail, exercising both the sql-available and sql-503 exit paths (AC-1..AC-4)"
  scope_boundary: >
    No change to the pinned Conductor CLI version or to the other read-only probes;
    no transcript parsing beyond the last assistant text of the tail; no SQL
    replacement service; no change to watch.sh's exit-code vocabulary.
  semantics_unchanged: false
  promote_when:
    - "the degradable-sql fallback becomes load-bearing for a consumer outside kc-ship-flow's watch/dispatch pair"
    - "the batch questions log format this task writes to becomes a durable cross-workflow contract"
  decision:
    authority: "person:captain via batch conn (quote: 准; source: Captain chat 2026-09-14, approving the ship-cloud-wrapper-r3 batch of five (pilot profile))"
    at: "2026-09-14T13:45:44Z"
```

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

## Shape (ideation)

### Accepted journey

**sql-available path (unchanged)**

1. OBSERVED — the ship FO runs `dispatch.sh <sprint> --conn-quote … --conn-source …`
   (bash, `kc-ship-flow/scripts/dispatch.sh`); `check_contract()` reads
   `pins/conductor-cli.contract` against `conductor --help`/`--version`.
2. OBSERVED — `dispatch.sh` runs `conductor auth whoami`, `conductor workspace list
   --limit 1`, `conductor --json sql "SELECT 1"` (external `conductor` binary against
   the Conductor cloud API); all three succeed and `dispatch.sh` proceeds to
   `workspace create` unchanged.
3. OBSERVED — the ship FO runs `watch.sh <sprint> --once` (bash,
   `kc-ship-flow/scripts/watch.sh`); the same three probes succeed, so the
   sql-unavailability detector records "available" this run and takes no fallback
   branch.
4. OBSERVED — per fenced slug, `watch.sh` reads `gate_status()` from the entity
   frontmatter at `$workflow_dir/.spacedock-state/<slug>.md` (or `<slug>/index.md`,
   local file), then `workspace_status()`/`session status()` and, when idle,
   `transcript_exit()` via `conductor --json sql "SELECT transcript FROM
   session_transcripts_view …"` (external `conductor` binary), printing one
   `<slug> gate-prepared|pending|quota|question|stopped` line per slug on stdout.

**sql-503-degraded path (new)**

5. OBSERVED (2026-09-13 ~04:20 UTC through at least 2026-09-14 08:00 UTC, re-probed
   at filing: still 503) — `conductor sql` returns "The SQL search API endpoint is
   temporarily disabled (HTTP 503)".
6. DESIGNED — `dispatch.sh`'s `conductor --json sql "SELECT 1"` probe fails;
   `dispatch.sh` recognizes only the `sql` shape as degradable (`auth whoami` and
   `workspace list` stay fatal, unchanged `die … 2`), prints one dated degraded
   notice to stderr, and continues to the readiness/claim-fence/`workspace create`
   flow exactly as the sql-available path does.
7. DESIGNED — `watch.sh`'s own `sql "SELECT 1"` probe fails the same way, checked
   once per process invocation; on first detection this run, `watch.sh` appends one
   line to `$state_dir/_ship_questions/<sprint>.log` naming the degraded mode
   ("sql-503"), the probe's stderr, and the current UTC date, then continues polling.
8. DESIGNED — per fenced slug in the degraded branch, `watch.sh` still calls
   `gate_status()` (local file, no CLI) and, when not gate-prepared,
   `workspace_status()`/`session status()` exactly as before — those probes are
   unaffected by the sql outage.
9. DESIGNED — for an idle session, instead of `transcript_exit()`'s `sql` query,
   the fallback tail-reader binary-searches `conductor --json session message <sid>
   --limit 1 --offset M`: an offset past the end returns a JSON object with no
   `sessionIndex` key (the empty-tail signal), which bounds the search to the last
   real message; that message's `text` is matched against the same quota/question
   phrase and marker rules `transcript_exit()` already applies to the sql-sourced
   transcript's last assistant block.
10. DESIGNED — `watch.sh` prints the same `<slug> <exit>` vocabulary on stdout as
    the sql-available path; the only caller-visible difference is the one-time
    stderr degraded notice and the one questions-log line.

**Unhappy paths, same terms**

- `auth whoami` / `workspace list` / `workspace create` still die with their
  existing exit codes (2 / 7) exactly as today — those probes are untouched by this
  change. **Flag:** AC-1 as written says "with `auth whoami` failing it still exits
  5"; the current code exits 2 for that probe (5 is reserved for the used-surface
  contract-mismatch check). Non-goal #3 ("no change to the exit-code vocabulary")
  reads as binding, so this shape keeps `auth whoami` failure at exit 2 and treats
  AC-1's "5" as a wording slip to reconcile at the gate, not a spec to implement
  literally — surfaced here rather than silently resolved.
- If the `session message` binary search never finds a `sessionIndex` boundary for
  a stale/unknown session id, the search must terminate after a bounded number of
  probes and report `pending` rather than looping — a named stop condition for
  build, not an open-ended retry.
- A double outage (both `sql` and `session message` unavailable) leaves `watch.sh`
  unable to render quota/question/stopped for an idle session; per non-goals ("no
  SQL replacement service"), the design accepts falling through to the existing
  idle-streak `pending`/`stopped` path rather than inventing a third data source.

### semantics_unchanged: false

What changes, named exactly:

1. `dispatch.sh`'s `sql` probe failure changes from fatal (`die … 2`, halts before
   any `workspace create`) to non-fatal (one dated stderr notice, continues).
2. `watch.sh` gains a new persistent side effect it never had: the batch questions
   log write at `$state_dir/_ship_questions/<sprint>.log`.
3. `watch.sh`'s idle-session tail-read data source switches from `sql` to `session
   message` binary search when degraded; the reported `<slug> <exit>` vocabulary is
   unchanged.

Unchanged: `dispatch.sh`/`watch.sh` argv and flags, the fence-file format, every
other probe's exit code, the pinned Conductor CLI version.

### Persistence / recovery / data-safety boundaries (questions-log write)

- **Location** — new `$state_dir/_ship_questions/<sprint>.log` (plain text,
  append-only), sibling to the existing `_ship_fence/<sprint>.json`.
- **Write frequency** — at most once per `watch.sh` process per degraded
  transition (first detection only); a `--once` run writes at most one line total,
  and a looping run writes on the first poll that observes the 503, not every
  `SHIP_WATCH_POLL_S` cycle. Recovery-then-re-degradation across a long-running
  loop or across process restarts is not distinguished in this slice — a stop
  number, not a silent guarantee.
- **Concurrency** — disjoint per-sprint files match the existing fence-file
  design (one dispatcher process per sprint), so a plain `>>` append needs no added
  lock, mirroring `poll_state_file`'s single-writer assumption.
- **Recovery** — the log is advisory/informational only, never read back by
  `watch.sh`; losing or truncating it does not change `watch.sh`'s own exit
  vocabulary or block a future run. No rotation/retention is designed here (non-goal:
  no durable audit-trail service).
- **Data safety** — no secrets in the line (503 text + date only, both already
  public-facing diagnostic strings); `mkdir -p` the log directory the same way
  `_ship_fence` already is; a failed `mkdir -p`/write must degrade the log, not the
  polling loop — wrap the write so a filesystem hiccup cannot become fatal to
  `watch.sh`.

### Where it touches

Diff base: current tree (this branch's `HEAD`, unmodified by this stage).

| Path | lines now | lines after (est.) |
|---|---|---|
| `kc-ship-flow/pins/conductor-cli.contract` | 7 | ~9 (add `session message` shape; mark `sql` degradable via a `#`-comment the tokenizer must learn to strip) |
| `kc-ship-flow/scripts/dispatch.sh` | 229 | ~240 (sql probe becomes non-fatal + dated notice; contract tokenizer strips comments) |
| `kc-ship-flow/scripts/watch.sh` | 278 | ~340 (once-per-run sql detector, questions-log writer, `session message` binary-search fallback tail-reader reusing the quota/question rules) |
| `kc-ship-flow/scripts/fixtures/fake-conductor-watch/conductor` | 120 | ~160 (serve `session message --limit --offset`; env knob to force the `sql` 503 text) |
| `kc-ship-flow/scripts/fixtures/fake-conductor-dispatch/conductor` | (unread, small) | + env knob to force the `sql` 503 text for AC-1 |
| `kc-ship-flow/scripts/watch.test.sh` | 163 | ~220 (AC-2/AC-3/AC-4 cases: degraded exits without `sql`, unchanged sql-available path, questions-log line) |
| `kc-ship-flow/scripts/dispatch.test.sh` | (unread) | + one case for AC-1's degraded-continue + unchanged-fatal-probe |
| `$state_dir/_ship_questions/<sprint>.log` | 0 (new, runtime-created) | 1 line per degraded run |

Reconciled against the journey: every file above is named in a journey step
(1/6/9 → `dispatch.sh`/contract; 3/7/9/10 → `watch.sh`/fixtures/tests); no journey
step depends on a file the table omits.

### Task-specific acceptance checks (tied to AC-1..AC-4)

- **AC-1** — `fake-conductor-dispatch` forced to print the 503 text on `sql`:
  `dispatch.sh --dry-run` exits 0, stderr contains exactly one dated degraded line.
  Separately, `FAKE_CONDUCTOR_AUTH_FAIL=1` (existing knob) still exits **2** (see
  the AC-1 wording flag above) — falsifiable by asserting the literal exit code,
  not "non-zero".
- **AC-2** — `watch.test.sh` new case: fake conductor forced into 503-`sql` mode,
  no `sql` argv line ever appears in `FAKE_CONDUCTOR_LOG` for that run (falsifies
  "switches to fallback reads" if `sql` is still called); slug outcomes match
  gate-prepared/question/pending per the existing fixture's frontmatter and
  transcript-tail fixtures, driven through `session message` instead.
- **AC-3** — same `watch.test.sh` run also exercises the unmodified sql-available
  cases (existing test-cases a/b/d/e/f/g/h/i) unchanged, proving no regression;
  fake conductor's `session message --limit --offset` responses come from a
  recorded fixture file, not computed live.
- **AC-4** — after the 503-forced run, `$state_dir/_ship_questions/<sprint>.log`
  exists with exactly one line naming "sql-503", containing the probe's stderr
  text and today's date; a second `--once` invocation in the same process/run
  does not append a second line (falsifies "on first detection" if it grows
  unbounded per poll).

### Stop numbers

Measured against the diff base above (current tree).

- **Changed files:** stop and report past 8 (the table's count); an unplanned 9th
  file is the shape's boundary being wrong, not a budget to spend.
- **Changed lines:** stop and report past ~250 net changed lines across all files;
  the estimate above sums to roughly that with headroom.
- **Named runaway risk:** the `session message` binary-search fallback tail-reader
  in `watch.sh` (journey step 9) — it is the one genuinely new algorithm (everything
  else is a probe-failure branch or a log line), and its termination-bound/edge-case
  handling (stale session id, `sessionIndex` boundary detection) is where scope
  creep is most likely; if it grows past a small bounded loop, stop and report
  rather than generalizing it into a standalone library.

## Stage Report: ideation

- DONE: One accepted end-to-end journey (each step marked OBSERVED or DESIGNED, naming the acting program and file/stream) covering the sql-503-degraded path and the sql-available path, explicit non-goals, and a stated semantics_unchanged declaration, satisfying AC-1..AC-4
  Read `dispatch.sh` (229 lines), `watch.sh` (278 lines), `pins/conductor-cli.contract`, `watch.test.sh`, `fake-conductor-watch/conductor`, and `docs/ship/runbooks/conductor-cloud.md` to ground every journey step in the real code; see "## Shape (ideation)" → Accepted journey + semantics_unchanged.
- DONE: Persistence/recovery/data-safety boundaries for the degraded-mode questions-log write, plus a file-level "where it touches" table (pins/conductor-cli.contract, dispatch.sh, watch.sh, the fixture, the questions log)
  See "## Shape (ideation)" → Persistence/recovery/data-safety boundaries and Where it touches table (8 rows, reconciled against the journey both directions).
- DONE: Task-specific acceptance checks able to falsify the slice (tied to AC-1..AC-4) and the stop numbers (changed files/lines) implementation halts on
  See "## Shape (ideation)" → Task-specific acceptance checks and Stop numbers (8 files / ~250 lines / session-message binary-search reader named as the runaway risk).

### Summary

Grounded the shape in the actual `dispatch.sh`/`watch.sh`/`pins/conductor-cli.contract` code and the `conductor-cloud.md` runbook (which already explains why `sql` was chosen over `session message --after`). Flagged one concrete discrepancy: AC-1's "auth whoami failing still exits 5" does not match the current code (exit 2); resolved the shape toward the non-goal ("no change to exit-code vocabulary") and surfaced it explicitly rather than silently picking a side. Reverse-recovery-audit and journey-slicing references were evaluated and not loaded: this is a direct repair of an already-named broken seam (the 503 outage), and the accepted outcome is one integrated slice.
