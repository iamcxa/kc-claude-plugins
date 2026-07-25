---
title: Close the compiled-vs-LLM path divergence and guard the eval-fallback removal
status: backlog
source: split out of the selector canon review, 2026-07-25 — these are the fixes that actually solved issue #7 and they sit next to code the canon correction will touch
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: 3jyaw0y3rd37ygqzwbasyr76
---

## Problem

PR #8 shipped two things that genuinely solved issue #7, plus a syntax ban that did
not. [[e2e-selector-canon-review]] removes the ban. The risk this entity exists for
is that the two real fixes are adjacent to the code being edited and read like part
of the same cargo cult, so a later reader — human or agent — reverts them together.

The two that must survive:

1. **`compiler/lib/selector-translate.js` + `_poll_snapshot_contains`** — visibility
   is decided by translating the selector to an a11y pattern and grepping the
   accessibility snapshot, rather than handing the raw selector to
   `agent-browser is visible`.
2. **The Eval-Fallback Removal Policy** (`agents/e2e-test-runner.md:548-561`) — a
   failed probe fails loudly instead of quietly retrying through `agent-browser eval`.

Issue #7's reproduction is the reason both matter: `is visible 'role=tab[name="Lineage"]'`
returned false, fell through to an `eval` fallback checking `offsetParent !== null`,
and the test **reported PASS**. A silent false-positive E2E test is the worst defect
class this pipeline can produce, and it is the same failure shape as the deferred
assertions in [[e2e-assertion-honesty-gate]] — a check that cannot fail.

## The divergence, which is the substantive half

The compiled path translates and greps; the LLM-driven path does not. `e2e-test-runner`
and `e2e-flow-verifier` still interpolate the raw selector into
`agent-browser is visible "<selector>"`. So the same mapping is evaluated by two
different mechanisms depending on which path runs it, and only one of them has issue
#7's fix. Bringing the runner and verifier onto the compiler's snapshot-grep closes
that.

This is not a new idea. PR #8 filed `docs/ship-flow/todos/compiled-vs-llm-divergence-baseline.md`
— "measure the divergence between the compiled and LLM paths before 001.2 ships" —
and it is still pending. The divergence it predicted is the one measured here.

## Notes for ideation

- Sequence after [[e2e-selector-canon-review]] lands the translator changes, or the
  two entities edit the same translation surface concurrently.
- The regression guard is the deliverable, not a promise. A test that fails when the
  eval fallback is reintroduced, and a test that fails when a raw selector reaches
  `is visible`, are worth more than any amount of comment or documentation — the ban
  they replace was documented in 13 places and still went wrong.
- Run PR #8's own pending baseline as part of this. It is the measurement that would
  have caught the canon defect three months ago, and leaving it pending a second time
  repeats the exact mistake being corrected.
- Falsification for the guard: reintroduce the eval fallback in a scratch copy and
  confirm the suite goes red. A suite that stays green under that edit is not a guard.
