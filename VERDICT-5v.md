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
