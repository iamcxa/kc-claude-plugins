# VERDICT-5v: return

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
