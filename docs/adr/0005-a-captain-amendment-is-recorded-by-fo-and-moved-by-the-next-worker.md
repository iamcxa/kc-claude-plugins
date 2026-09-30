# 0005. A Captain amendment is recorded by FO and applied by the next worker, and ideation checks its own gaps

Date: 2026-09-30

## Status

Accepted

## Context

Four ideation-stage gaps from an adopter's dogfooding and this repository's last two
tasks each cost a worker round, a hand rewrite at a gate, or a drifting ADR number:
`dispatch build --stamp` succeeded for a task with no `## FO alignment` section and the
worker then held; `gate prepare` accepted an ideation report with no
`## Acceptance criteria` section; after an approved ideation gate the Captain changed
the direction, the superseded criteria stayed in force for `status --read --ac-scan`,
and the FO rewrote the acceptance script by hand (in review-cadence the implementation
worker's state commit 1f3c19f6 rewrote 65 lines, so the wording he approved survives
only in git history); an ideation worker committed an ADR draft to a branch in the
shared checkout. Spacedock 0.27.2 reads no task body at dispatch or `gate prepare`
(read from the binary and the v0.27.2 source in the task's ideation, 2026-09-30), and
`--ac-scan` lists a criterion moved out of `## Acceptance criteria` no longer, while
annotating it in place leaves it listed as unevidenced.

## Decision

**Words:** 「准」 — Captain, ideation gate of this task, 2026-09-30. The gate reason
recorded by FO adds: design approved with option A (FO records his words in
`## Captain amendments`, the next worker moves the superseded criteria), the live probe
of AC-4(b) kept for validation.

**Options considered:**
- FO records the Captain's words in the task's `## Captain amendments`; the next
  dispatched worker moves each superseded criterion's block into the entry and writes any
  replacement under a fresh id (chosen)
- FO also moves and rewrites the criteria — rejected: it adds an FO write to accepted
  criteria, which `### ideation` forbids, and passes his intent through the FO's paraphrase
- routed re-ideation for each amendment — rejected: `status --set status=ideation` after a
  spent approval is not a documented route, and it costs a gate attempt for text he
  already stated
- annotate a superseded criterion in place — rejected: `--ac-scan` still lists it as
  unevidenced
- a second check mode, `design_surfaces.py check --seed`, that FO runs before the backlog
  gate (chosen)
- run the one shipped check at that moment — rejected: it refuses a legitimate `ui` seed
  for the artifacts the worker authors later
- `design_surfaces.py check` refuses a missing or empty `## Acceptance criteria` section
  by the grammar `--ac-scan` reads (chosen)
- rely on `--ac-scan`'s exit code — rejected: it is 0 for a plain `- AC-1:` list and for
  an empty section
- an ADR draft stays in the task file with no number, FO reserves it at implementation
  dispatch and the implementation worker writes the file (chosen)
- a throwaway worktree for ideation — rejected: it creates a branch per task and the
  draft still needs a number

The rule later work must follow: an amendment has one record, `## Captain amendments`,
in the form `workflow.md` gives; its `Supersedes:` criteria are withdrawn and are
moved, not annotated; `check` exits 1 for an entry without `Captain:` and for a
superseded id still declared. The heading is matched like Spacedock's own: any case,
surrounding whitespace ignored. The record and the move rule reach a dispatched
implementation or validation worker through `Captain amendments` in that stage's
`context-sections` in `workflow.md`, not through a sentence in its `principles.md`.
The FO runs `check --seed` before the backlog gate and holds it until it exits 0.
Ideation writes no repository file, branch or commit, and names an ADR by ruling and
short title with no number.

## Consequences

Between FO's record and the worker's move the task shows both, and `check` says so.
That FO records an amendment, that FO runs the seed check, and that ideation writes no
repository file are prose steps: `check` refuses only the state after a skipped move,
and nothing blocks an ideation worker from writing a file. An adopter receives the FO
steps by re-syncing its workflow README from `workflow.md`; until then its FO does not
run the seed check. The criteria rule follows `--ac-scan`'s grammar as read in 0.27.2;
the parity test in `scripts/test_sd_dispatch.py` fails if a Spacedock release changes
it. The live probe at validation (one Sonnet run per arm, the candidate package and
origin/main 05b772b7, the same scratch task whose design described the old flow) had both
arms write an acceptance script that follows the amendment and never runs the superseded
behaviour, so the two `principles.md` sentences it was meant to justify were removed, as this
decision said they would be. Limit: N=1 per arm, one model, and the probe ran after the
superseded criterion had been moved; the effect of the record before the move is unmeasured.
Reopen if Spacedock adds a task-body hook at dispatch or `gate prepare`.
