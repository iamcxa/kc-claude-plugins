# Validation 5v: Assertion Honesty

Verdict: **pass**

Validated fresh in `/Users/kent/mini-legs/dev-5vmvs9rf-honesty-val` on branch `review`, checked out
from `origin/mini/dev-5vmvs9rf-honesty-impl`. I ran the required dependency install before tests:

```bash
cd e2e-pipeline && npm install
```

Result: exit 0, `added 10 packages`, `audited 11 packages`, with one high-severity advisory reported
by npm.

## Scope Read

Requested artifacts read:

- `git diff origin/main...origin/mini/dev-5vmvs9rf-honesty-impl`
- `git show origin/mini/dev-5vmvs9rf-honesty-impl:STAGE-REPORT-5v.md`
- `git show origin/mini/dev-5vmvs9rf-assertion-honesty:IDEATION-5v.md`
- `git show origin/spacedock-state/dev:e2e-assertion-honesty-gate.md`
- `docs/dev/README.md` validation stage and Proof Policy

Diff scope matched the first-officer fact: 16 files changed, `+571/-32`. No `carlove` or
`spacedock-state` paths were touched.

## AC Results

**AC-1 — PASS: unmatched expect strings fail compilation.**

Manual CLI fixture:

```bash
node bin/e2e-compile.js unmatched-expect --flows-dir "$tmp/flows" --mappings-dir "$tmp/mappings" --output-dir "$tmp/out"
```

Observed:

```text
exit=1
stdout=
stderr=ERROR: Step 'check-login': unsupported expect string 'manual confirm checkout email arrived' -- rewrite it using docs/writing-tests.md#expect-grammar-reference or declare {not_automated: <reason>} when genuinely human-only
output_exists=no
```

Implementation anchor: `e2e-pipeline/compiler/resolver.js:412` creates the unsupported-expect error
and increments `deferredCount`; `e2e-pipeline/compiler/compiler.js` returns before codegen on resolver
errors.

**AC-2 — PASS: JSON diagnostics expose the same failure.**

Command:

```bash
node bin/e2e-compile.js --json --dry-run unmatched-expect --flows-dir "$tmp/flows" --mappings-dir "$tmp/mappings" --output-dir "$tmp/out"
```

Observed exit 1 with one JSON stdout document:

```json
{"ok":false,"flow":"unmatched-expect","stats":{"total":1,"activeExpects":0,"deferredExpects":1,"notAutomatedExpects":0,"skipped":0,"resolveErrors":1},"errors":[{"step_id":"check-login","stepId":"check-login","field":"expect","raw":"manual confirm checkout email arrived","got":"manual confirm checkout email arrived","candidates":[],"message":"Step 'check-login': unsupported expect string 'manual confirm checkout email arrived' -- rewrite it using docs/writing-tests.md#expect-grammar-reference or declare {not_automated: <reason>} when genuinely human-only"}],"coverage":null}
```

Anchor: `e2e-pipeline/bin/e2e-compile.js:59` adds `resolveErrors`; `e2e-pipeline/compiler/resolver.js:101`
adds `raw`/`got` details for unsupported expects.

**AC-3 — PASS: the escape hatch is per assertion.**

Legal hatch plus active assertion:

```text
exit=0
stdout=Compiled: 1 steps, 1 expects active, 1 expects not automated
OK: not-automated-expect
output_exists=yes
```

Same flow shape with a hatch plus an unsupported string still failed:

```json
{"ok":false,"flow":"hatch-plus-unmatched","stats":{"total":1,"activeExpects":0,"deferredExpects":1,"notAutomatedExpects":1,"skipped":0,"resolveErrors":1},"errors":[{"stepId":"mixed-check","raw":"manual confirm checkout email arrived"}]}
```

`node bin/e2e-compile.js --help | rg -c 'allow-(deferred|manual|not-automated)'` found no flow-level
allow flag. Anchor: `e2e-pipeline/compiler/resolver.js:301` accepts only a single expect object item,
and `e2e-pipeline/compiler/test/cli.test.js:200` covers absence of a flow-level flag.

**AC-4 — PASS: non-automated assertions never become runtime passes.**

Focused suite:

```bash
node --test compiler/test/resolver.test.js compiler/test/codegen.test.js compiler/test/coverage.test.js compiler/test/cli.test.js compiler/test/e2e-test-contract.test.js
```

Observed: `# tests 415`, `# pass 415`, `# fail 0`.

Anchors: `e2e-pipeline/compiler/codegen.js:1687` skips `not-automated` without assertion machinery;
`e2e-pipeline/compiler/codegen.js:1690` throws if old `deferred` reaches codegen; coverage only
increments `verified_count` from `or-visible`/`elementName` assertions at
`e2e-pipeline/compiler/coverage.js:63` and `:76`. The specific coverage test at
`e2e-pipeline/compiler/test/coverage.test.js:137` observed `verified_count=0` and summary
`verified=0` for a hatch-only expect.

**AC-5 — PASS: the real CLI path proves the end value.**

The manual subprocess evidence above used `bin/e2e-compile.js`, not just unit calls. It proved prose
and JSON failure for unsupported assertions before output write, plus prose and JSON success with
visible `notAutomatedExpects` for the explicit hatch.

**AC-6 — PASS: documentation describes the new contract.**

Docs landed with the approved contract:

- `e2e-pipeline/docs/writing-tests.md:342` says unmatched strings are compile errors, not deferred
  warnings.
- `e2e-pipeline/docs/writing-tests.md:347` documents per-assertion `not_automated`.
- `e2e-pipeline/docs/writing-tests.md:354` says hatches never count active or verified.
- `e2e-pipeline/skills/e2e-compile/SKILL.md:110` tells `/e2e-compile` to present unsupported
  assertions as failures.
- `e2e-pipeline/agents/e2e-flow-writer.md:260` tells authors not to write `manual ...` as plain
  expect strings.

The doc-linked behavior was exercised through the CLI commands above.

**AC-7 — PASS: e2e-test keeps legal hatches out of v1 rejection.**

Direct contract probe:

```text
valid exact hatch: errors=0
extra key rejected: errors=1
empty reason rejected: errors=1
blank reason rejected: errors=1
non-string reason rejected: errors=1
other object rejected: errors=1
executed=active-and-hatch,following-executable,hatch-only
summary={"total_steps":3,"passed":2,"failed":0,"skipped":0,"not_automated":2}
statuses=active-and-hatch:PASS,following-executable:PASS,hatch-only:NOT_AUTOMATED
```

Tracked harness also passed in the focused suite. Anchors:
`e2e-pipeline/compiler/e2e-test-contract.js:3` strict detector,
`e2e-pipeline/compiler/e2e-test-contract.js:26` synthetic runner accounting, and
`e2e-pipeline/compiler/test/e2e-test-contract.test.js:28` behavioral fixture.

## Guardrails

1. **Strict detector held.** `isNotAutomatedExpect` requires exactly one key, exact key name,
   non-array object, string value, and non-empty trimmed reason
   (`e2e-pipeline/compiler/e2e-test-contract.js:3`). The direct probe and tracked test rejected
   extra-key, empty, blank, non-string, and unrelated objects.
2. **Both consumers moved.** `skills/e2e-test/SKILL.md:77` updates schema validation, `:79` states
   the exact-shape rule, `:423` includes `not_automated` in returned results, and `:560` excludes it
   from pass/fail/skip counts. `agents/e2e-test-runner.md:237`, `:259`, `:472`, `:632`, and `:651`
   carry runner verification, step status, flow summary, and back-channel accounting.
3. **AC-7 harness exercises behavior.** The harness is not a constant-only grep: it runs
   `validateExpectEntries` and `summarizeSyntheticRunnerResults` over a synthetic flow, observes the
   following executable step in `executedStepIds`, and checks hatch-only `NOT_AUTOMATED`.

## Judgment Checks

`deferred` is not renamed into a green path. Resolver still increments `deferredExpects` for
diagnostics, but unmatched strings enter `errors` and fail compile. Codegen has only a defensive
`deferred` branch that throws. The only other `deferred` references found in executable code are
unrelated finalizer wording or test names.

I did not find a cheaper bypass. There is no flow-level allow flag; the hatch is per expect item.
An author can still add many `not_automated` entries, but each one is visible in
`notAutomatedExpects`/`not_automated` and does not count as active, passed, or verified.

Coverage accounting holds: `analyzeCoverage` increments `verified_count` only for resolved element
assertions and `or-visible`, so hatch-only expects leave `verified_count` unchanged.

## Adversarial Spot-Check

Scratch worktree: `/tmp/e2e-honesty-adversarial-84386`.

I loosened `compiler/e2e-test-contract.js:isNotAutomatedExpect` to accept any object carrying a
`not_automated` key. Before the edit:

```text
node --test compiler/test/e2e-test-contract.test.js
baseline_exit=0
```

After the claim-breaking edit:

```text
adversarial_exit=1
not ok 1 - strict v1 detector allows only exact not_automated objects
Expected values to be strictly equal:
1 !== 4
# pass 1
# fail 1
```

After reverting in the scratch worktree:

```text
revert_exit=0
```

## Full Suite

Command:

```bash
cd e2e-pipeline && npm test
```

Observed:

```text
# tests 680
# suites 154
# pass 675
# fail 5
# cancelled 0
# skipped 0
# todo 0
```

The five failures are the scoped-out, pre-existing `Integration: migrate + compile real carlove flow`
machine-local failures caused by missing `/Users/kent/Project/carlove/...`.

## Independent Review

Ran:

```bash
codex review --base origin/main
```

The reviewer reported no discrete regression: unsupported expects become compile errors, the hatch is
strictly counted, and TODO assertion codegen is removed.

## Findings

No material findings.
