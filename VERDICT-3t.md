## Previous Round

Cycle 1 verdict was `return`. The resolver design, corpus evidence, AC-1 through AC-5,
omitted-qualifier compatibility, `_global` grandfathering, and `resolve()` / `resolveMultiSite()`
symmetry were judged sound. The return was only for two carry-through gaps: `shared: true` did
not reach `agents/e2e-test-runner.md`, and the task promised a structured `repair` field that
gz's landed JSON contract did not define.

## Fresh Verdict

verdict: proceed

## Reasoning

Both returned conditions are actually closed.

Condition 1 is closed by carry-through, not narrowing. Adding `agents/e2e-test-runner.md` to the
audit and doc-diff scope is the right solution. `/e2e-test` has its own direct mapping lookup
instructions and does not call `compiler/resolver.js`; leaving it on literal `_global` fallback
would recreate the same advertised-but-not-enforced semantic one layer later. The proposed three
prompt edits carry the shared-page rule to the runner's resolution order and expectation lookup.

Condition 2 is closed by withdrawing the bad promise. gz's landed tier-1 shape is exactly
`{step_id, field, got, candidates, message}`. There is no `repair` field, so removing that
language is better than inventing a new field inside 3t. AC-6 now verifies the JSON shape through
tracked `cli.test.js`, including a non-empty `candidates` list, which directly guards against
the earlier failure mode where the human message survives but the machine-actionable half is
lost.

Ruling on the escalated question: 3t should populate `candidates` for page-not-found with the
mapping's real page keys. This is not a contract change; it uses gz's existing "did you mean"
field for exactly the same class of payload. The current gz `resolveNavigate` path passing `[]`
is an outlier to reconcile later, not a reason to weaken 3t's diagnostics. The corpus defects are
mistyped page names, so an empty list would discard the most useful hint. Implementation should
not broaden scope merely to retrofit every existing page-not-found producer unless that is a
small shared-helper consequence; the gate approval is for 3t's page-binding refusals.

The reported `_global` count imprecision is not a scope gap. The three prompt/doc consumers are
now in scope, and the two additional hits are compiler tests/fixtures that implementation is
already expected to touch or account for. I would not return the ideation over that accounting
wording.

## Confidence Per Claim

- High: `e2e-test-runner.md` carry-through closes the material runtime-consumer gap.
- High: Withdrawing the nonexistent `repair` field is correct against gz's landed contract.
- High: AC-6 is falsifiable and CI-reproducible for the JSON-layer guarantee.
- Medium-high: Populating page candidates is the better bounded judgment; it improves repair
  quality without adding schema, while leaving one known gz asymmetry for later cleanup.

## What Would Change My Mind

- If implementation cannot populate page candidates without changing gz's JSON schema or
  widening into a broader diagnostics refactor.
- If the runner prompt edits fail to state both explicit-location and location-less shared-page
  fallback.
- If AC-6 becomes a prose/string-only assertion instead of parsing `--json` and checking keys.

## Conditions

None. Proceed to implementation.
