# VERDICT-5v Gate Record

# Round 1 Verdict: return

## Verdict

Return to ideation for one material carry-through repair. The compiler design is directionally
sound, and I would proceed on the core three-state contract once the `/e2e-test` consumer path is
designed and covered. As written, the legal `not_automated` hatch is valid for `/e2e-compile` but
still invalid for the test-runner surface that reads the same flow files.

No captain escalation trigger fired. This is a bounded EM ideation verdict; no irreversible decision,
scope authorship, residual acceptance, or EM/FO disagreement is needed.

## Reasoning

### Claim 1: The hatch avoids the original failure mode

Confidence: high.

The design correctly rejects the cheap flow-level mute. It requires a per-assertion object form,
counts the hatch separately, and requires unrelated unmatched strings in the same flow to keep
failing. That makes the cheapest way around the gate visible: authors can overuse one
`not_automated` item per assertion. That is not free in the same way `--allow-deferred` would be,
and the pre-mortem plus flow-writer doc change names the social risk.

What would change my mind: if implementation added a step-level or flow-level allow flag, or if one
`not_automated` item suppresses other unmatched `expect` strings.

### Claim 2: Carry-through is incomplete

Confidence: high.

The design covers parser, resolver, compiler, codegen, coverage accounting, `--json`, prose CLI
summary, `/e2e-compile`, the flow-writer agent, and writing-tests docs. It does not cover the
`/e2e-test` skill or `agents/e2e-test-runner.md`.

That is material because the current `/e2e-test` schema validation says:

```markdown
| Expect entries | strings | objects | SKIP |
```

The proposed legal hatch is:

```yaml
expect:
  - not_automated: "Verify the legal disclaimer copy with product counsel."
```

So a flow using the newly legal compiler syntax can still be classified by `/e2e-test` as legacy
format and skipped before agent dispatch. The runner agent also says "For each entry in the step's
`expect:` array, resolve and verify independently" and lists only string patterns. It has no
instruction for `not_automated` entries: visible non-pass accounting, skip semantics, or report
wording. This is exactly the sprint's expensive defect class: a semantic exists in one layer and
vanishes at a consumer.

What would change my mind: an ideation update that adds `/e2e-test` and `e2e-test-runner.md` to the
approved doc diff and adds a tracked test proving a flow containing `not_automated` is not rejected
as v1/object-expect legacy syntax.

### Claim 3: Migration sizing is acceptable for ideation, with a caveat

Confidence: medium.

The ideation notes are honest that the corpus population is stale and that `.context/` is absent.
I do not require inventing a count from a decayed corpus before implementation. The key product
decision is to fail loud rather than keep silent green runs, and the task is reversible in one
compiler change if the blast radius is worse than expected.

The caveat is that implementation should report the first available population signal it can get
from non-transient fixtures or a refreshed corpus, but I would not return the design solely on the
missing estimate.

What would change my mind: evidence that this gate will be enforced against production or CI flows
before any repair/quarantine mechanism can be applied, or that there is a stable corpus available
now and ideation deliberately chose not to measure it.

### Claim 4: `deferred` is genuinely removed from the green runtime path

Confidence: medium-high.

The ACs require unmatched strings to become compile errors, require codegen not to emit deferred
TODO echoes, require hatches not to count as active or verified, and require CLI subprocess proof in
both prose and JSON modes. Those tests can fail for the relevant claim-breaking edits. The existing
code has a single obvious green path to remove: `resolver.js` emits `{ type: 'deferred' }`, and
`codegen.js` turns it into a bare TODO echo. The proposed tests would catch leaving that path alive.

What would change my mind: if implementation keeps a defensive `deferred` branch in codegen that
emits any success-looking output, or if JSON reports unmatched strings as warnings while returning
`ok:true`.

## Required Return Fix

Add one carry-through AC and doc diff section for the `/e2e-test` consumer:

- `/e2e-test` schema validation must treat the exact object form
  `{not_automated: <non-empty string>}` as v2-valid, while continuing to reject other structured
  expect objects as legacy/v1 or malformed.
- `agents/e2e-test-runner.md` must define runner behavior for `not_automated`: record it as
  visible non-automated evidence, do not execute it as a passing assertion, do not count it as PASS,
  and do not let it suppress other unsupported expect strings.
- A tracked test under `e2e-pipeline/compiler/test/` must prove the consumer-facing contract that a
  flow with `not_automated` is not rejected as "Expect entries: objects" legacy syntax. If no
  executable `/e2e-test` harness exists there, the design must name the smallest feasible tracked
  test or explicitly classify that proof gap.

## Conditions If Narrow

Not applicable. I am returning rather than narrowing because the current design would make one
supported flow surface accept the hatch and another supported flow surface reject it.

---

# Round 2 Verdict: proceed

## Verdict

Proceed. The return condition is actually closed: the updated ideation makes the
`not_automated` hatch legal for `/e2e-test` without weakening general v1 detection, and AC-7 now
requires behavioral proof that can fail for the specific carry-through break I returned.

No captain escalation trigger fired. This remains a bounded EM ideation verdict; no irreversible
decision, scope re-cut, residual acceptance, or seat disagreement is present.

## Reasoning

### Claim 1: The v1 carve-out is precise enough to implement

Confidence: high.

The updated design does not accept structured expect objects generally. It says the existing v1
detector remains strict, and only the exact object form `{not_automated: <non-empty string>}` is
recognized as v2. Plain objects remain legacy/v1 or malformed. That is a deterministic rule an
orchestrator prompt or a small parser helper can apply: an expect entry is valid if it is a string,
or if it is an object with exactly one key, `not_automated`, whose value is a non-empty string.
Everything else stays on the old rejection path.

What would change my mind: implementation accepting any object with a `not_automated` key plus other
keys, accepting empty/non-string reasons, or changing the v1 detector from "objects are rejected
except the exact sanctioned hatch" to "objects are mostly allowed."

### Claim 2: The `/e2e-test` carry-through gap is closed at design level

Confidence: high.

The updated scope, reverse-recovery audit, doc diff, and test plan now cover both missing consumers
from round 1: `skills/e2e-test/SKILL.md` and `agents/e2e-test-runner.md`. The runner semantics are
also explicit enough to prevent a renamed silent pass: `not_automated` records its own expectation
status and count, does not run browser assertion commands, does not mark the expectation PASS, and
a hatch-only step reports `NOT_AUTOMATED` rather than PASS.

What would change my mind: implementation updating only `/e2e-compile` docs while leaving
`/e2e-test` schema validation or runner result accounting unchanged.

### Claim 3: AC-7 is falsifiable

Confidence: medium-high.

AC-7 is not a prose-grep. It requires a fresh-context `/e2e-test` run or a tracked
prompt-behavior harness over a synthetic flow with an active expect, a `not_automated` expect, a
following executable step, and a hatch-only step. The named observations can fail: v1 classification,
whole-flow skip, missing later-step execution, missing `not_automated: 1`, or hatch-only PASS all
falsify the AC.

The "fresh-context run" option is acceptable because this is an LLM-runner behavior surface, and the
workflow allows exercised behavior as proof for prompt/agent bodies. The test plan also gives the
safer fallback: a tracked harness that invokes the real skill/runner contract. Validation should use
the harness if the fresh-context run cannot be made reproducible enough to audit.

What would change my mind: validation offering only a diff or grep of the skill/agent prompt, or a
manual transcript that does not include the synthetic fixture and observed later-step execution.

## Conditions If Narrow

Not applicable. This is a proceed verdict.

---

# Round 3 Validation Verdict: proceed

## Verdict

Proceed. The implementation satisfies the validated ACs, including the `/e2e-test` carry-through
condition that caused the first return. No material finding remains.

No captain escalation trigger fired. This is a validation verdict held by EM under Gate Authority;
there is no residual red gate, no scope re-cut, no irreversible exception, and no EM/FO
disagreement to escalate.

## Reasoning

### Claim 1: AC-7 is satisfied by the tracked harness

Confidence: medium-high.

The implementation did not use a fresh-context `/e2e-test` run; it used the alternative tracked
harness route. That is acceptable here. `compiler/e2e-test-contract.js` is not a prose-grep and not
a constant-only assertion: it applies the exact-shape detector to real expect entries, rejects
legacy/malformed object entries, walks a synthetic flow, records executed step ids, and computes
runner-style step/summary statuses.

The validator's adversarial check is meaningful for the guardrail I named. Loosening
`isNotAutomatedExpect` to accept any object carrying `not_automated` made the harness fail on the
strict detector count, then reverting restored green. That proves the test would catch the forbidden
weakening: accepting objects generally instead of carving out only the sanctioned shape.

Residual risk: the harness is still a contract harness for a prompt-runner surface, not a live LLM
execution. That is acceptable because both prompt consumers also moved with the same semantics, and
the approved AC allowed a tracked harness route when the real runner contract was otherwise not a
normal executable. I would not accept this evidence if the prompt files had not moved.

What would change my mind: if `skills/e2e-test/SKILL.md` or `agents/e2e-test-runner.md` lacked the
same exact-shape rule and `NOT_AUTOMATED` accounting, or if the harness only asserted literal text
instead of running detector and summary logic.

### Claim 2: Surviving `deferred` is diagnostic, not a green state

Confidence: high.

The old harmful behavior was "unmatched means deferred means TODO echo means green." That path is
gone. Resolver still increments `deferredExpects`, but unmatched expect strings now also enter
`errors`, cause compile failure, and are exposed in JSON with `ok:false`. Codegen retains only a
defensive `deferred` branch that throws if such an item reaches generation.

Keeping the old counter name is not a material residual because it no longer means runtime pass or
warning-only success. It remains useful for compatibility and diagnostics.

What would change my mind: any path where `deferredExpects > 0` returns `ok:true`, writes a script,
or emits a TODO/runtime non-assertion instead of failing before codegen.

### Claim 3: The social-risk mitigation is visible

Confidence: high.

The implementation cannot prevent authors from writing many `not_automated` entries, but that was
accepted at ideation because the mitigation is per-assertion visibility. The implementation makes
that visibility real: CLI prose reports `expects not automated`, JSON includes
`notAutomatedExpects`, `/e2e-compile` presentation names `Not automated`, `/e2e-test` summaries carry
`not_automated: N`, and the runner status model keeps hatch-only steps at `NOT_AUTOMATED` rather
than PASS.

What would change my mind: hatch counts being omitted from either CLI or `/e2e-test` summaries, or
hatch-only steps counted as passed/verified evidence.

## Evidence Checked

- Implementation diff: 16 files, `+571/-32`, scoped to compiler, tests, and relevant docs/prompts.
- Implementation report: scoped suite 415/415, full suite 675/680 with only known local carlove
  failures on that machine.
- Validation report: fresh validation pass, 680/680 on the machine where the corpus path resolves,
  direct AC probes, and an adversarial edit that made the AC-7 harness fail.
- Direct inspection: `isNotAutomatedExpect` requires exactly one key, exact key name, string value,
  and non-empty trimmed reason; `codegen` throws on defensive `deferred`; `/e2e-test` and runner
  prompts include exact-shape and `not_automated` result accounting.

## Conditions If Narrow

Not applicable. This is a proceed verdict.

---

# Round 4 Reopened Validation Question: return

## Ruling

Defect. A hatch-only step recorded as `pass` in the compiled bash script is not correct design.

This blocks the merge and returns to implementation for a narrow fix. The defect is bounded, but it
is on the CI-facing runtime surface, which is the surface most likely to turn "not automated" back
into green evidence.

## Reasoning

Confidence: high.

The accepted design deliberately made hatches non-passing and visible. `/e2e-compile` is honest,
JSON is honest, `/e2e-test` is honest, and the LLM runner reports hatch-only steps as
`NOT_AUTOMATED`. The compiled bash script is now the inconsistent consumer: a snapshot/wait/browser
step starts by recording `_STEP_RESULTS+=("pass")`, and `not-automated` emits no assertion path that
can change that result. For a hatch-only step, the script therefore reports PASS even though no
automated assertion proved the step.

That is the same failure shape this entity exists to remove, one layer down: an assertion-like item
that intentionally does no verification is represented as passing in the execution result. AC-4 was
aimed at preventing the hatch from becoming runtime pass evidence; the current compiled-script
surface violates the value of that AC even if it avoids emitting explicit assertion machinery.

The fact that compile summaries expose `notAutomatedExpects` is not enough for this surface. A CI job
or replay user can run the generated script later, read its JUnit/metrics/footer, and see a passed
step. Visibility has to carry into the compiled runtime result for hatch-only steps.

## Minimum Correct Fix

For compiled bash output, a step with at least one active assertion and one or more hatches may still
record `pass` when the active assertions pass. The defect is only the hatch-only case.

Minimum fix:

- Detect steps whose resolved `expects` are present and all have `type: 'not-automated'`.
- Record those steps in `_STEP_RESULTS` as a distinct value, preferably `not_automated`, not `pass`.
- Keep script exit code non-failing unless there are real failures; `not_automated` is not a failure.
- Update runtime summaries that consume `_STEP_RESULTS`:
  - metrics JSON counts `not_automated` separately and preserves per-step `"result":"not_automated"`;
  - JUnit should not emit hatch-only steps as plain passing testcases. The least disruptive encoding
    is `<skipped message="not automated"/>` while preserving a distinct internal result;
  - footer/prose should include the count, e.g. `PASS: hatchonly (0/1 automated steps passed, 0
    skipped, 1 not automated)`.
- Add a tracked codegen/runtime test compiling a hatch-only fixture and asserting the generated
  script/result surface does not contain `_STEP_RESULTS+=("pass")` for that step and does expose the
  non-automated count/status.

## What Would Change My Mind

Evidence that generated bash is explicitly not a supported reporting surface for compiled flows,
or that CI never consumes `_STEP_RESULTS`, JUnit, metrics, or footer output from hatch-only flows.
The current code and workflow do not support that reading: compiled scripts are the deterministic
replay/CI artifact, so their step status is part of the honesty contract.

---

# Round 5 Final Validation Verdict: proceed

## Verdict

Proceed. The narrow hatch-only compiled replay defect is closed.

No captain escalation trigger fired. This is still a bounded validation gate ruling: the returned
defect was repaired directly, no scope was re-cut, no residual red condition is being accepted, and
no seat disagreement is present.

## Reasoning

### Claim 1: The hatch-only predicate is correct

Confidence: high.

The implemented predicate is the right one:

```js
function stepSuccessResult(step) {
  var expects = Array.isArray(step.expects) ? step.expects : [];
  if (expects.length === 0) return 'pass';
  return expects.every(function(expect) { return expect.type === 'not-automated'; })
    ? 'not_automated'
    : 'pass';
}
```

That triggers only for non-empty expect lists where every resolved expect is `not-automated`.
Steps with no expects remain unchanged as `pass`, and mixed active-plus-hatch steps remain `pass`
when their active assertions pass. That matches the return ruling exactly.

### Claim 2: The new status reaches the compiled-script consumers

Confidence: high.

I found the relevant `_STEP_RESULTS` readers and they now handle the new value:

- `_handle_failure` overwrites the last result with `fail`, so action/assertion failures still win.
- JUnit counts `not_automated` under skipped and emits `<skipped message="not automated"/>`.
- Metrics preserves per-step `"result":"not_automated"` and adds `summary.not_automated`.
- The normal footer counts `not_automated` and reports automated and non-automated counts.
- The cleanup-trap footer carries the same count/reporting path for flows with finalizers.
- Retry/flake and exit-code logic remain failure-driven through `_FAILED_STEPS`; `not_automated` is
  visible but non-failing, which is the intended behavior.

The other `_STEP_RESULTS` appends are not missing consumers: finalizers remain `pass`/`fail` because
they are not normal resolved expect-bearing steps, and `verify-external`/`execute-external` remain
the existing step-level `skip` path.

### Claim 3: The regression test would fail on the original defect

Confidence: high.

The added test is anchored to the exposed defect. It generates a `hatchonly` flow with one
`manual-only` snapshot step whose sole expect is `not-automated`, slices the generated script at
that step's `_record_step_name "manual-only"` block, and asserts that block contains
`_STEP_RESULTS+=("not_automated")` and not `_STEP_RESULTS+=("pass")`.

It also executes the generated script with fake browser plumbing and checks all three returned
surfaces: footer output, metrics JSON, and JUnit XML. A bare absence-of-string test could pass for
the wrong reason; this one is tied to the specific step and to runtime output.

## What Would Change My Mind

Evidence of another `_STEP_RESULTS` consumer outside `compiler/codegen.js` that treats unknown
values as passing, or a supported compiled-script output mode that bypasses JUnit, metrics, and both
footer paths. I did not find one in the inspected codegen surface.
