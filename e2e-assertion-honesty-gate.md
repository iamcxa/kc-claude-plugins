---
title: Fail loud on assertions that never run
status: backlog
source: captain note — e2e-pipeline agent-native audit, 2026-07-25; scope cut A/B by the captain at ideation open (A = this entity, B = e2e-typed-operands)
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: 5vmvs9rfzqa7raxjfqptkeey
---

## Problem

`compiler/resolver.js:266` downgrades any `expect:` string that matches none of the 12
ordered patterns to `type: 'deferred'`, and `compiler/codegen.js:1674-1675` compiles that
to a bare `echo "TODO: ..."` which never touches `_STEP_RESULTS` — so the step keeps the
`pass` set at `codegen.js:985` (only the failure path at `codegen.js:588` flips it) and the
run exits green. Measured on the real local corpus: **368 of 794 expects (46.3%) resolve to
deferred**, ~25% excluding one outlier feature's near-duplicate copies. Demonstrated live on
a real project flow — `e2e-compile entity-inspector-drawer` prints `Compiled: 5 steps,
12 expects active, 11 expects deferred` then `OK`, dropping 48% of that flow's assertions at
exit 0. Separately, `scripts/lint-mapping.sh` rejects 5 selector forms the plugin's own docs
call "silently mishandled at runtime (false positive risk)", but the compiler never invokes
it — the ban is enforced by restating it in 13 markdown files.

Scope is the honesty gate only: make a deferred expect a compile failure, and give an
intentionally-unautomated assertion a legal per-assertion way to say so. Three neighbours were
split out and run earlier in the same sprint — the missing grammar permutations
([[e2e-expect-grammar-permutations]]), the discarded page qualifier
([[e2e-page-scoped-resolution]]), and the unenforced selector ban
([[e2e-selector-lint-gate]]) — so this entity carries one narrowing, not four.

**Runs last in sprint 1, and inherits a smaller blast radius because of it.** The grammar
entity recovers ~66 of the 368 deferred assertions before this gate lands, so the population
this must fail or hatch is ~302, and by then [[e2e-json-diagnostics]] is already emitting
structured errors with repair candidates — every one of those failures arrives fixable.

## Captain scope (verbatim, 2026-07-25)

- **What gets worse without this** — "最主要問題是我希望整個 e2e-pipeline 消耗 token 更有效率，
  更準確，更不隨機。"
- **Appetite / shape** — "先做 A，B 應該落下一個 entity，保持敏捷。"
- **Keep if forced to cut** — the gate itself (captain: "可以").
- **Happily NOT doing** — automating the ~35% free-form-prose class; it should fail loud, not
  be parsed (captain: "可以").
- **Assumption that could be wrong** — captain answered "我不知道"; the agent-authored candidate
  and its evidence are recorded below, and must be re-reviewed at the gate as agent-authored,
  not captain-authored.

## Open finding — the escape hatch cannot be flow-level

The captain could not name the risky assumption, so it was derived from the spike data
instead. Classifying all 368 deferred strings by why the author wrote them splits roughly in
half: about 49% look like "the author believed it worked" (visibility word-order, text-quoting
variants, raw selectors, unsupported predicates — all near-misses on supported vocabulary),
and about 51% look like "the author knew it was not automatable and used `expect:` as
documentation" (16% explicit `manual ...` checkpoints, 35% free-form prose).

That second half is the risk to the design. A flow-level `--allow-deferred` escape hatch lets
an author silence a whole flow in one flag, which reproduces exactly the silence this entity
exists to remove — and roughly half the corpus has a standing motive to reach for it. The
hatch has to be per-assertion and visible in the run summary (a "not automated" count that is
neither pass nor fail), not a flow-level mute. Ideation should treat this as the load-bearing
design decision.

Note the same failure has already happened once by this mechanism: 16% of deferred strings are
`manual ...` assertions that exist because `agents/e2e-flow-writer.md` Critical Rule 9 bans
`manual: true` without offering a replacement, so authors moved it into `expect:` strings where
it silently passes. A ban with no legal alternative produced the hole it was meant to close.

## Notes for ideation

- The gate will immediately red 17 of 87 corpus flows. Sizing the migration path for those —
  and deciding whether they are repaired, hatched, or quarantined — is in scope; repairing
  them is not.
- Reverse-recovery: the honest signal already exists and is merely unwired. `coverage.js:76`
  correctly declines to count a deferred expect toward `verified_count`, but coverage is
  opt-in (`--coverage`) and reported as a percentage, never as a gate. Classify that seam
  EXISTS_BROKEN and scope the repair to it rather than building a second measurement path.
- Spike is DONE — do not re-run it. Numbers, the full seven-class breakdown of the 368, and
  the reproduction scripts are recorded in [[e2e-typed-operands]].
- Watch the captain's stated goal: this entity serves "更準確" and "更不隨機" directly, but it
  does not by itself serve "消耗 token 更有效率" and may cost tokens short-term. Whether it
  still goes first is a captain call recorded at the gate, and the ledger row should carry a
  token baseline so the batch can be judged against the goal that motivated it.
