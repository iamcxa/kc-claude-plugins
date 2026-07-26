# Stage Report 5v: Assertion Honesty Implementation

## TL;DR

Implemented fail-loud handling for unsupported `expect:` strings and a strict per-assertion
`not_automated` hatch. Compiler, CLI JSON/prose output, codegen, coverage, `/e2e-compile` docs,
`/e2e-test` schema guidance, and the test-runner result contract now carry the same semantic. The
full suite has the expected 5 local carlove failures caused by `/Users/kent/Project/carlove` being
absent; all other tests passed.

## Produced

- `e2e-pipeline/compiler/resolver.js`: unmatched expect strings become compile errors with step id
  and raw text; exact `{not_automated: "<non-empty reason>"}` is accepted and counted separately;
  malformed objects are rejected.
- `e2e-pipeline/compiler/compiler.js`, `e2e-pipeline/bin/e2e-compile.js`: summaries and JSON stats
  expose `notAutomatedExpects`; failing unmatched assertions stop before output write.
- `e2e-pipeline/compiler/codegen.js`: defensive `deferred` expects throw; `not-automated` emits no
  runtime assertion/TODO/pass machinery.
- `e2e-pipeline/compiler/e2e-test-contract.js`: tracked AC-7 harness for strict `/e2e-test` expect
  validation and synthetic runner result accounting.
- Docs/prompts updated in `e2e-pipeline/docs/writing-tests.md`,
  `e2e-pipeline/skills/e2e-compile/SKILL.md`, `e2e-pipeline/skills/e2e-test/SKILL.md`,
  `e2e-pipeline/agents/e2e-flow-writer.md`, and `e2e-pipeline/agents/e2e-test-runner.md`.

## RED Evidence

- Resolver fail-loud: `resolveExpects: unrecognized expect string is a compile error` failed because
  the pre-fix resolver returned `[{ type: 'deferred', raw: ... }]` and no error.
- Hatch semantics: `resolveExpects: not_automated hatch is per assertion and not active` failed
  because `{not_automated: ...}` became `type: 'deferred'`; malformed hatch cases had no
  `notAutomatedExpects` stat and were not strict errors.
- Codegen honesty: `deferred expect fails code generation instead of emitting TODO echo` failed
  because generated script contained `echo "TODO: expect ... not compiled (Phase 2)"`.
- CLI behavior: `unmatched expect exits 1 and does not write compiled output` failed with exit 0 and
  `Compiled: 1 steps, 0 expects active, 1 expects deferred (Phase 2)`; JSON mode failed with
  `{"ok":true,...,"deferredExpects":1,"errors":[]}`.
- Non-automated reporting: CLI `not_automated` tests failed because prose reported deferred and JSON
  omitted `notAutomatedExpects`.
- AC-7 runner contract: `e2e-test not_automated contract harness` initially failed on missing module
  `../e2e-test-contract.js`, proving there was no tracked behavioral harness for the synthetic
  fixture.

RED command:

```bash
cd e2e-pipeline
node --test compiler/test/resolver.test.js compiler/test/codegen.test.js compiler/test/coverage.test.js compiler/test/cli.test.js compiler/test/e2e-test-contract.test.js
```

Pre-fix result: 414 tests run in the scoped set, 404 pass, 10 fail.

## GREEN Evidence

Scoped behavior suite:

```bash
cd e2e-pipeline
node --test compiler/test/resolver.test.js compiler/test/codegen.test.js compiler/test/coverage.test.js compiler/test/cli.test.js compiler/test/e2e-test-contract.test.js
```

Result: 415/415 pass.

Full suite:

```bash
cd e2e-pipeline
npm install
npm test
```

Result: 680 tests, 675 pass, 5 fail. The 5 failures are the known pre-existing local failures in
`Integration: migrate + compile real carlove flow`:

- `corpus files exist and are readable`
- `migrate produces a typed copy without modifying the original`
- `full pipeline: migrate -> compile -> bash -n passes`
- `generated script ends with exit 0 path`
- `original corpus files are not modified after all operations`

Failure digest: every failure references missing `/Users/kent/Project/carlove/.claude/e2e/flows/gate-login-flow.yaml`.

Lint:

```bash
cd e2e-pipeline
npm run lint
```

Result: exit 0. Biome reported existing warnings and applied no fixes.

## AC-7 Behavioral Fixture

Tracked harness test:

```bash
cd e2e-pipeline
node --test compiler/test/e2e-test-contract.test.js
```

The synthetic flow includes one active expect plus one `not_automated` expect, a following executable
step, and a hatch-only step. Observed result executes `active-and-hatch`, `following-executable`, and
`hatch-only`; summary reports `passed: 2`, `failed: 0`, `skipped: 0`, `not_automated: 2`; the
hatch-only step status is `NOT_AUTOMATED`.

## Decisions

- Because `/e2e-test` is a skill plus LLM runner prompt rather than a standalone binary, I added a
  tracked contract harness for the approved synthetic fixture instead of claiming prose-grep proof.
- I kept `deferredExpects` in stats for unmatched assertion diagnostics and compatibility, but it is
  now a failing count, not a warning/success state.
- I included both `step_id` and `stepId` on unmatched expect error details to preserve the existing
  snake-case structured error style while supporting direct JSON consumers.
