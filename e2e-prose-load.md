---
title: Cut the prose an agent must read before doing any work
status: backlog
source: captain note — e2e-pipeline agent-native audit, 2026-07-25; filed after the captain named token efficiency as the batch's primary goal
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: ywn5zzq3n7a7arzv3avsjsns
---

## Problem

A single `/e2e-flow` run reads **116 KB of instruction prose (~29K tokens) before performing
any work**: `skills/e2e-flow/SKILL.md` (25.3 KB) + its `reference.md` (10.1 KB) +
`references/learned-patterns.md` (11.1 KB) + `knowledge-capture.md` (5.2 KB) + the
flow-writer (13.8 KB), flow-verifier (20.7 KB) and trace-analyzer (16.5 KB) agent bodies +
`agent-teams.md` (13.6 KB). `agents/e2e-test-runner.md` alone is 31.5 KB. This is the
pipeline's largest single token line item and it is paid on every invocation regardless of
what the run actually needs.

Three distinguishable drivers, worth separating before cutting anything:

1. **Unbounded append-only memory.** `learned-patterns.md` is read in full at startup by six
   skills, grows by design (D1 auto-append with no ceiling), and has no retrieval — every run
   pays for all 16 entries to use none or one. This is memory without retrieval.
2. **Restated invariants.** The banned-selector rules alone appear in 13 markdown files. Each
   copy is both token cost and drift surface; [[e2e-schema-contract]] deletes them by making
   the contract an artifact rather than a recital.
3. **Prose as control flow.** Roughly 100 of the 202 lines of `skills/e2e-compile/SKILL.md`
   teach the agent to reformat the compiler's human prose into different human prose;
   `skills/e2e-flow/SKILL.md` spends a comparable share on Teams-vs-subagent branching,
   sentinel lifecycle, and timeout handling. [[e2e-json-diagnostics]] and
   [[e2e-retire-flow-sentinel]] each remove one of these.

## Notes for ideation

- This entity was originally cut from the batch as "context tax, low value" — a judgment made
  against a framing of the problem as false-green correctness. The captain's stated primary
  goal is token efficiency, which inverts that call: this is the most direct instrument for it
  and the others reach it only as a side effect. Re-triage accordingly.
- Much of the reduction is a consequence of entities already filed rather than independent
  work. Scope this one to what they do not cover — principally the retrieval question for
  `learned-patterns.md` — and measure the total, so the batch has one number to be judged by.
- Establish the baseline before any of the batch lands, or the improvement is unprovable. The
  measurement is a byte count over a fixed read-set, which is cheap and repeatable.
- Guard against the obvious failure mode: prose deleted without its invariant being enforced
  somewhere executable is not a saving, it is a regression with a smaller diff.
