---
id: gajgn9tgv26f90ndq0sv0ext
title: Make --json and --coverage compose instead of silently cancelling
status: backlog
source: found by the EM at [[e2e-json-diagnostics]]'s validation gate, 2026-07-26 — flagged twice in the implementer's own code comments and missed by two validation cycles, two reviewer lenses and two cross-model passes
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

`--json` silently suppresses coverage output. The `--json` early-returns at
`bin/e2e-compile.js:165-177` (batch) and `:249-260` (single-flow) sit *ahead* of the coverage
blocks at `:180-216` and `:266-314`, so adding `--json` skips them entirely.

Measured, not read:

    --all --coverage            -> coverage.json (1.1K) + coverage-history.json written
    --all --coverage --json     -> the coverage output directory does not exist. No file,
                                   no warning, exit code unchanged.

Single-flow is a partial loss (the document still carries `coverage`, but nothing is written to
disk and no regression warning fires). Batch is total: `flowResults` entries are
`{flow, ok, stats, errors}` with no `coverage` key, so a consumer cannot recover it either.

This matters because `skills/e2e-compile/SKILL.md` Phase 2 now adds `--json` unconditionally,
so the skill route lost the capability. `compiler/test/cli.test.js:329-341` asserts that
`--coverage` writes `coverage.json` — a tested guarantee bypassed by the exact flag the skill
always sends, with no test covering the combination.

**Why this is a follow-up and not a pre-merge fix**, so the next owner does not re-litigate it:
five independent searches found no consumer — no CI workflow invokes `e2e-compile`, no other
skill or agent references `--coverage`, no `coverage*.json` exists under `carlove/.claude/e2e`,
every reference to those artifacts across the plugin is inside the compiler's own write path or
documentation with no external reader, and no `coverage-history.json` exists on any workspace
tree. Nothing accrues harm in the meantime, so [[e2e-json-diagnostics]] shipped a doc correction
instead. The compounding risk it would otherwise carry — a trend file accumulating a hole — does
not apply, because no trend file was ever started.

Likely shape: move the early-returns after the coverage blocks, add a `coverage` key to batch
entries for parity, and add the test combination `cli.test.js:329-341` never covers.
`docs/commands.md:40` and `docs/writing-tests.md:386` still advertise
`/e2e-compile --all --coverage` and belong to this entity, not to the doc round that preceded it.
