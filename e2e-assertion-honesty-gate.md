---
title: Fail loud on assertions that never run
status: implementation
source: captain note — e2e-pipeline agent-native audit, 2026-07-25; scope cut A/B by the captain at ideation open (A = this entity, B = e2e-typed-operands)
started: 2026-07-26T10:23:26Z
completed:
verdict:
worktree: mini:~/mini-legs/dev-5vmvs9rf-honesty-impl
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

### Feedback Cycles

**Cycle 1 — ideation gate, 2026-07-26. Verdict: RETURN.** Adjudicated on codex (mini leg
`dev-5vmvs9rf-gate`, verdict at `origin/mini/dev-5vmvs9rf-gate:VERDICT-5v.md`).

One material condition: the proposed per-assertion hatch is an object
(`- not_automated: "..."`), and `skills/e2e-test/SKILL.md:77` classifies object expect entries as
v1 format, with `:79` stopping execution of the **whole flow**. FO-verified from source. So a flow
using the sanctioned escape hatch would compile cleanly and then be refused entirely by the test
runner — worse than the silence this entity exists to remove.

Third instance of one failure class in this sprint: a semantic constructed at one layer and lost
at a consumer ([[e2e-json-diagnostics]] at the coverage consumer, [[e2e-page-scoped-resolution]] at
the runner prompt, this one at the v1 detector). Treat it as this codebase's default failure mode.

**Cycle 2 — re-gate, 2026-07-26. Verdict: PROCEED.** Same adjudicator, resumed in-session.

The condition was closed by extending scope to `/e2e-test` and `agents/e2e-test-runner.md` while
keeping the v1 detector strict — a carve-out for one exact shape rather than accepting objects
generally — plus AC-7, verified behaviorally rather than by prose-grep.

Three implementation guardrails carried from the verdict's "what would change my mind":

1. Reject any object carrying `not_automated` **plus other keys**, and reject empty or non-string
   reasons. The detector rule is "objects are rejected except the exact sanctioned hatch", never
   "objects are mostly allowed".
2. Do not update `/e2e-compile` docs while leaving `/e2e-test` schema validation or runner result
   accounting unchanged — that is precisely the round-1 defect returning under a new name.
3. Validation must not accept a diff or grep of the skill/agent prompt as AC-7 evidence. It needs
   the synthetic fixture and an observed later-step execution; if a fresh-context run cannot be
   made auditable, use the tracked harness the test plan already names.

**Cycle 3 — validation gate, 2026-07-26. Verdict: PROCEED, no conditions.**

Fresh codex validator reported pass; same adjudicator ruled on it, resumed in-session. Three
judgments the FO put to it rather than settling:

1. **AC-7 was satisfied by a route the gate did not specify.** It had accepted a fresh-context
   `/e2e-test` run OR a tracked harness, flagging the former as possibly unauditable. The
   implementation built `compiler/e2e-test-contract.js` — a tracked module runnable anywhere —
   turning an LLM-prompt behavioral claim into executable code. Accepted, because the validator's
   adversarial edit (loosening `isNotAutomatedExpect` to accept any object carrying the key) turned
   the suite red at `1 !== 4`. The harness exercises the contract rather than restating constants.
2. **`deferred` survives as a counter name.** Judged not a material residual: it no longer means
   runtime pass. Falsifier recorded — any path where `deferredExpects > 0` returns `ok:true`, writes
   a script, or emits a TODO-style non-assertion instead of failing before codegen.
3. **The hatch's social risk is unresolvable by construction**, so the mitigation is visibility, and
   the implementation makes it real in five places: CLI prose `expects not automated`, JSON
   `notAutomatedExpects`, `/e2e-compile` presentation, `/e2e-test` summary `not_automated: N`, and
   the runner keeping hatch-only steps at `NOT_AUTOMATED` rather than PASS.

**Cycle 4 — validation gate reopened, 2026-07-27. Verdict: RETURN, blocks merge.**

A cross-vendor pass (agy) was run before opening the PR and **its entire round was discarded**:
four of five findings cited lines past the end of the file they named (`e2e-test-contract.js` is
104 lines; it cited :134, :180, :201), and its central mechanism — "dual execution" in
`skills/e2e-test/SKILL.md` Phase 1.5 — does not exist anywhere in `skills/` or `agents/`. Per the
fabricated-citation rule the round was thrown out rather than triaged.

One of the questions it had been asked was then investigated directly by the FO, and found a real
defect by a different mechanism. Reproduced, not argued: a step whose only expect is a hatch
compiles clean and the generated bash records `_STEP_RESULTS+=("pass")`. `_STEP_RESULTS` is only
reassigned to `"fail"` on an assertion failure path, and `codegen.js:1687` deliberately emits no
assertion for a hatch — so a flow of purely manual checks reports every step passing when replayed
through the compiled script.

The gate ruled this a defect, not design: compiled scripts are the deterministic replay/CI
artifact, so their step status is part of the honesty contract. AC-4 avoided emitting assertion
machinery but the compiled surface still violates the value AC-4 exists to protect. **Fourth
instance of this sprint's recurring failure class** — semantic present at five consumers, absent at
the sixth, and the sixth is the one CI actually runs.

Scope of the fix is the hatch-only case only; a step with an active assertion plus a hatch
correctly records `pass`.

