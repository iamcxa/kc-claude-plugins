# Ideation: Fail loud on assertions that never run

## TL;DR

Design is required. The repair should wire the compiler's existing deferred-expect signal into
compile failure semantics, while adding a legal per-assertion `not_automated` hatch that is counted
and reported separately from active assertions. Do not use a flow-level allow flag. The corpus
population figures in the entity are historical only; acceptance must be proven by tracked compiler
tests that can run on any machine, not by a decaying `.context/flow-corpus.txt` measurement.

## Problem and Scope

Captain scope is inherited from the entity: improve token efficiency, accuracy, and determinism by
closing the silent-pass path for unsupported `expect:` strings. This entity directly serves
accuracy and determinism: a claim that the compiler cannot execute must stop compilation instead
of becoming a green runtime echo. It may cost tokens short-term because authors will have to repair
or explicitly classify old flows rather than receiving a silent success.

Scope is the honesty gate only:

- unmatched assertion strings become compiler errors;
- intentionally human-only checks get a per-assertion, visible, non-passing hatch;
- `/e2e-compile` prose and `--json` output expose the failure or hatch count;
- `/e2e-test` accepts the same hatch without classifying the flow as v1, and reports it as
  non-automated while continuing to run the flow's other assertions;
- existing coverage analysis remains the source of truth for "verified" accounting.

Out of scope:

- repairing corpus flows;
- measuring or accepting against corpus counts;
- broadening the expect grammar beyond what the three merged sibling entities already changed;
- adding a flow-level `--allow-deferred` option.

The corrected 2026-07-26 measurements in the brief supersede the entity body's stale numbers.
Because `.context/` and its corpus scripts are absent from this machine, no new corpus measurement
was taken. If implementation needs sizing beyond tracked fixtures, the unmeasured question is:
"against the sibling backlog's repaired corpus, how many unmatched strings remain after grammar and
page-qualifier changes, and how many are intentional non-automation candidates?"

## Design Determination

`design: required` because this changes the compiler contract, CLI/json diagnostics, flow authoring
syntax, and public docs.

Determination: deferred is no longer a runnable assertion state. The resolver should classify
assertion items into exactly three outcomes:

- `active`: compiler-recognized assertion that emits runtime checks and increments active counts;
- `not-automated`: explicit author declaration for a single assertion item, recorded in stats and
  reports but never counted as active or verified;
- `error`: unmatched string or malformed hatch, returned through the existing compile error channel.

Recommended YAML hatch:

```yaml
expect:
  - not_automated: "Verify the legal disclaimer copy with product counsel."
```

Rules for the hatch:

- only the exact object form `{not_automated: <non-empty string>}` is accepted;
- it is per assertion item inside `expect`, not a step-level or flow-level flag;
- it must not generate a runtime TODO echo;
- it increments a new `notAutomatedExpects` stat and appears in prose/json summaries;
- it does not contribute to `activeExpects`, `deferredExpects`, or coverage `verified_count`.

Unmatched legacy strings such as `manual confirm checkout email arrived` must fail compilation with
a structured error that points to the step id and the raw expect text. That preserves the useful
part of the prior spike: authors get a repairable compiler diagnostic instead of an exit-0 script.

The same contract must be wired through `/e2e-test`. The existing v1 detector should remain strict:
plain structured expect objects are still legacy/v1, but the one exact object shape
`{not_automated: <non-empty string>}` is recognized as v2. This is a narrow semantic carve-out, not
general object acceptance. During runner execution, a `not_automated` item records an expectation
result with status `not_automated`, reason text from the object, and no pass/fail assertion work.
The surrounding step and flow continue executing other actions and expectations. Run summaries add a
distinct `not_automated: N` count alongside passed/failed/skipped. Step status rules: action
failure or active expectation failure still yields FAIL; at least one passing active expectation
with no failures may yield PASS while also counting any hatches; a step with only non-automated
expectations and no action failure yields NOT_AUTOMATED, not PASS, because no automated assertion
proved it.

## Reverse-Recovery Audit Against origin/main

Audit target: `origin/main`, fetched during ideation.

- UI: N/A. This is a CLI/compiler behavior with no browser UI.
- Contract: EXISTS_BROKEN. `bin/e2e-compile.js:50-64` already carries stats into `--json`, and
  `bin/e2e-compile.js:107-114` maps stats/errors to skill presentation. The contract reports
  `deferredExpects` as a warning, which is the broken success semantics.
- Test orchestration contract: EXISTS_BROKEN. `skills/e2e-test/SKILL.md:71-79` currently treats
  all object expect entries as v1 and stops the whole flow. The sanctioned hatch would therefore be
  compiler-legal but runner-illegal unless this schema row gains the exact `not_automated` carve-out.
- Handler: EXISTS_BROKEN. `compiler/compiler.js:187-215` generates output and returns
  `success: true` even when `resolveResult.stats.deferredExpects` is nonzero.
- Domain: EXISTS_BROKEN. `compiler/resolver.js:277-376` recognizes the unsupported state by
  producing `{type: 'deferred', raw}` and incrementing `deferredCount`; it lacks the fail-loud
  conversion and legal hatch classification.
- Runtime/codegen: EXISTS_BROKEN. `compiler/codegen.js:1687-1688` emits a TODO echo for deferred
  expects, so an uncompiled assertion becomes output text rather than a failing condition.
- LLM runner: EXISTS_BROKEN. `agents/e2e-test-runner.md:231-256` only describes string
  expectations, and `agents/e2e-test-runner.md:458-470` returns passed/failed/skipped without a
  non-automated count. It needs the same three-state expectation semantics as the compiler.
- Persistence/readback: WORKING for the existing honest signal. `compiler/coverage.js:61-79`
  increments `verified_count` only for executable element expectations; deferred/non-automated
  expects already do not count as verified. This seam should be reused, not duplicated.
- Tests: EXISTS_BROKEN. `compiler/test/resolver.test.js` currently asserts that an unrecognized
  expect becomes deferred, and `compiler/test/codegen.test.js:577-586` asserts TODO echo generation.
  These are the tests to invert.

Repair scope: resolver/compiler/CLI/codegen tests and docs around the existing signal. Do not build
a second coverage or corpus scanner.

## Acceptance Criteria

**AC-1 — Unmatched expect strings fail compilation.**
Verified by: a tracked CLI test in `e2e-pipeline/compiler/test/cli.test.js` that compiles a fixture
with an unmatched string under normal prose mode and asserts exit code 1, no compiled output file,
and a diagnostic naming the step id plus raw expect text. Falsified by: changing the compiler so
the same fixture exits 0, writes a script, or omits the raw expect from the diagnostic.

**AC-2 — JSON diagnostics expose the same failure.**
Verified by: a tracked CLI test invoking the same fixture with `--json --dry-run` and asserting
stdout is one JSON document with `ok:false`, exit code 1, `stats.deferredExpects` or equivalent
unmatched count nonzero, and an `errors[]` entry for the deferred assertion. Falsified by: returning
`ok:true`, emitting prose on stdout, dropping the error entry, or requiring callers to parse stderr.

**AC-3 — The escape hatch is per assertion.**
Verified by: tracked parser/resolver/compiler tests using one step with both an active assertion and
`- not_automated: "..."`, asserting compile success, `activeExpects` counts only the active assertion,
`notAutomatedExpects` counts the hatch, and no flow-level flag exists in `--help`. Falsified by: any
flow-level allow option, a hatch that suppresses unrelated unmatched strings in the same flow, or a
hatch that increments active/verified counts.

**AC-4 — Non-automated assertions never become runtime passes.**
Verified by: a tracked codegen/compiler test that compiles a fixture containing only
`not_automated` expects and asserts the generated script contains no deferred TODO assertion echo and
does not call success/failure assertion machinery for that item; coverage tests assert it leaves
`verified_count` unchanged. Falsified by: generated runtime output that treats the hatch as a pass,
or coverage treating it as verified evidence.

**AC-5 — The real CLI path proves the end value.**
Verified by: an E2E-first tracked test that drives `bin/e2e-compile.js` as a subprocess for both
prose and `--json` modes using repository fixtures, proving unsupported assertions fail before
script execution and explicit `not_automated` assertions compile with visible counts. Falsified by:
unit tests passing while the installed CLI still exits 0 for unsupported assertions or hides the
not-automated count from CLI consumers.

**AC-6 — Documentation describes the new contract.**
Verified by: validation comparing the implementation diff against the approved doc diff below and
running the doc-linked CLI fixture tests, not by prose-grep alone. Falsified by: docs still saying
unmatched expects are silently deferred, recommending `manual ...` strings, or omitting the
`not_automated` syntax and reporting semantics.

**AC-7 — e2e-test keeps legal hatches out of v1 rejection.**
Verified by: a fresh-context `/e2e-test` run or tracked prompt-behavior harness using a synthetic
flow with one active expect, one `{not_automated: "..."}` expect, and one following executable step;
the observed result must execute the following step, avoid the v1-format stop path, and report
`not_automated: 1` separately from passed/failed/skipped. The fixture must also include a step whose
only expectation is `not_automated` and observe that step as NOT_AUTOMATED rather than PASS.
Falsified by: the same fixture being classified as v1, the surrounding flow being skipped, the hatch
counted as PASS, or the non-automated count missing from the structured runner summary.

## Proposed Doc Diff

`e2e-pipeline/docs/writing-tests.md`

Before:

```markdown
Every `expect:` string is matched against an ordered list of regex patterns in
`compiler/resolver.js`. The first pattern that matches wins; a string matching none
of them is silently deferred -- `/e2e-compile` reports it as a "Warnings" line and it
becomes a `TODO` echo at runtime instead of a real assertion.
```

After:

```markdown
Every string item in `expect:` is matched against an ordered list of regex patterns in
`compiler/resolver.js`. The first pattern that matches wins; a string matching none
of them is a compile error, because it would not produce a runtime assertion.

For assertions that are intentionally not automatable, use a per-assertion object:

expect:
  - not_automated: "Verify the legal disclaimer copy with product counsel."

`not_automated` items compile, appear in the compile summary, and never count as
active or verified assertions.
```

Also update the caution at lines 373-381 to say the bad page-scoped text example now fails
compilation and should be rewritten to a supported text or element assertion.

`e2e-pipeline/skills/e2e-compile/SKILL.md`

Before:

```markdown
| `stats.deferredExpects > 0` | Add: `Warnings: N expects deferred (unrecognized format -- see docs/writing-tests.md#expect-grammar-reference)` |
```

After:

```markdown
| `ok: false` with deferred assertion errors | Present as compilation failures and show the raw unsupported `expect:` text plus repair guidance |
| `stats.notAutomatedExpects > 0` | Add: `Not automated: N expects declared with not_automated` |
```

`e2e-pipeline/agents/e2e-flow-writer.md`

Append to Critical Rule 9:

```markdown
If a checkpoint is genuinely human-only and cannot be represented as `Execute external` or
`Verify external`, use a single `expect` item with `not_automated: "<reason>"`. Do not write
`manual ...` as a plain expect string.
```

`e2e-pipeline/skills/e2e-test/SKILL.md`

Before:

```markdown
| Expect entries | strings | objects | SKIP |

If ANY fail: warn with migration guidance (`app:`->`mapping:`, `name:`->`id:`, structured->`grammar strings`). All v1 -> stop execution of this flow.
```

After:

```markdown
| Expect entries | strings or `{not_automated: "<reason>"}` objects | other objects | SKIP |

If ANY fail: warn with migration guidance (`app:`->`mapping:`, `name:`->`id:`, unsupported structured expects->grammar strings or `not_automated` only when genuinely human-only). All v1 -> stop execution of this flow.
```

Also update result presentation so single, batch, and multi-site summaries include
`not_automated: N` when present, without treating it as pass/fail/skip.

`e2e-pipeline/agents/e2e-test-runner.md`

Add to expectation validation:

```markdown
| `{not_automated: "<reason>"}` | Record expectation status `not_automated` with the reason. Do not run browser assertion commands, do not mark it PASS, and continue validating the step's other expectations. Any other object-shaped expect remains invalid legacy/v1 input and should have been stopped by the orchestrator. |
```

Update the report template and structured summary:

```markdown
| Not automated | N |

- not_automated: N
```

The runner's `FLOW COMPLETE` and `STEP COMPLETE` back-channel messages must carry the same
`not_automated` count so the `/e2e-test` orchestrator can include it in final summaries. A step with
only non-automated expectations reports result `NOT_AUTOMATED`; a step with passing active
expectations may report `PASS` while still listing the non-automated expectation separately.

## Test Plan

Implementation should run one RED/GREEN loop per behavior:

1. RED: invert the existing resolver test that expects unrecognized strings to become deferred.
   GREEN: resolver returns an error detail for unmatched strings and no resolved deferred item.
2. RED: invert the codegen TODO echo test. GREEN: codegen has no deferred branch reachable from
   compiler output; if a defensive branch remains, it must fail generation rather than echo.
3. RED: add CLI subprocess tests for normal and `--json` unmatched-expect failures. GREEN:
   compile exits 1, reports structured diagnostics, and does not write output on failure.
4. RED: add parser/resolver/compiler tests for `{not_automated: "..."}`. GREEN: it compiles,
   increments `notAutomatedExpects`, and does not silence other unmatched strings.
5. RED: add coverage/codegen tests proving `not_automated` is visible in stats but absent from
   `verified_count` and runtime assertion code. GREEN: stats and coverage agree.
6. RED: add a fresh-context `/e2e-test` behavioral fixture, or a tracked prompt-behavior harness
   that invokes the real skill/runner contract, with active + `not_automated` expects and a later
   executable step. GREEN: the run avoids v1 rejection, executes the later step, and reports
   `not_automated` outside pass/fail/skip, including a hatch-only step reported as NOT_AUTOMATED.
   A grep over `SKILL.md` or the agent prompt is not sufficient evidence.
7. Exit check: run `cd e2e-pipeline && npm install && npm test`. The known local caveat is the
   five `Integration: migrate + compile real carlove flow` failures caused by a hardcoded absent
   project path; validation should report those separately if still present.

Ideation baseline run on this machine:

- `cd e2e-pipeline && npm install && npm test`
- Result: 668 tests, 663 pass, 5 fail.
- Failing suite: `Integration: migrate + compile real carlove flow`, five subtests, matching the
  brief's known path-dependent local defect.

No corpus harness was run: `.context/` and `flow-corpus.txt` are not present in this worktree.

## Pre-Mortem

If this ships exactly per spec and still fails, the most likely cause is a hidden assumption:
authors may overuse `not_automated` as documentation unless flow-writing guidance makes the legal
hatch explicit but socially narrow.

## Implementation Sizing

One worker session. The behavior crosses resolver/compiler/CLI/codegen/docs, but it is one vertical
compiler seam with tracked fixtures and one RED-to-GREEN loop per behavior. Split only if the fresh
`origin/main` audit shows a new schema or CLI contract has landed after this ideation branch.
