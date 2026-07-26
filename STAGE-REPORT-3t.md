# Stage Report: 3t Page-Scoped Resolution

Implemented page-scoped element resolution in `e2e-pipeline/compiler/resolver.js` with
tracked coverage in `resolver.test.js` and `cli.test.js`, plus the approved prompt/docs
carry-through in `agents/e2e-test-runner.md`, `agents/e2e-mapper.md`,
`skills/e2e-test/SKILL.md`, and `docs/writing-tests.md`.

## Produced

- `buildSymbolTable()` now returns both the existing flat table and `byPage`/`sharedPages`.
  Unqualified element references still use the flat table and preserve the old ambiguous
  behavior.
- Qualified action and expect element forms resolve against the stated page first, then shared
  pages (`shared: true`, plus literal `_global` unless `shared: false`).
- Added expect grammar support for `<element> is visible on <page>`.
- Wrong-page and missing-page diagnostics use gz's existing tier-1 JSON shape only:
  `{step_id, field, got, candidates, message}`.
- Updated runner prompt text to state both required fallbacks: explicit-location shared fallback
  and location-less current-page-then-shared fallback.

Commits:

- `70744e2 Bind page-qualified element resolution`
- `62515a7 Document page-scoped shared element lookup`

## RED Evidence

Scoped RED command:

```bash
cd /Users/kent/mini-legs/dev-3tp0ym1m-page-scoped-impl/e2e-pipeline
node --test compiler/test/resolver.test.js compiler/test/cli.test.js
```

Failure digest before implementation:

- `resolve: explicit page qualifier rejects element found only on another real page` failed with
  `0 !== 1`; current resolver silently resolved `Click heading on login`.
- `resolve: explicit missing page qualifier returns page-not-found with page candidates` failed
  with `0 !== 1`; captured page was ignored.
- `resolveExpects 3t: "element is visible on page" resolves and binds the page qualifier`
  failed as `actual 'deferred'`, proving the grammar row was absent.
- `resolveExpects 3t: explicit page qualifier rejects expect element found only on another real
  page` failed with `0 !== 1`.
- `resolveMultiSite: explicit page qualifier rejects element found only on another page within
  the same site` failed with `0 !== 1`.
- `--json 3t page binding: page and element diagnostics keep tier-1 keys and candidates` failed
  because the CLI returned `ok:true` and `errors:[]`.

I tightened the shared-page tests after that RED run: unique `_global`/`shared:true` elements
already passed accidentally under the old flat lookup, so the committed tests use collision
shapes that fail before the page-scoped shared fallback and pass after it.

## Checks

Scoped GREEN:

```bash
cd /Users/kent/mini-legs/dev-3tp0ym1m-page-scoped-impl/e2e-pipeline
node --test compiler/test/resolver.test.js compiler/test/cli.test.js
```

Result: pass, `102` tests, `0` failures.

Real compile path:

```bash
cd /Users/kent/mini-legs/dev-3tp0ym1m-page-scoped-impl/e2e-pipeline
node bin/e2e-compile.js --verbose --dry-run list-data-completeness \
  --flows-dir compiler/test/fixtures \
  --mappings-dir compiler/test/fixtures \
  --output-dir /tmp/e2e-page-binding-out
```

Result: exit `0`; `tab_all visible on service-schedule` and `data_table visible on
service-schedule` resolved as active expects; summary was `Compiled: 12 steps, 6 expects active,
5 expects deferred`.

Full-suite exit check:

```bash
cd /Users/kent/mini-legs/dev-3tp0ym1m-page-scoped-impl/e2e-pipeline
npm test
```

Result: failed, `659` tests, `654` pass, `5` fail. All failures are in the pre-existing
`Integration: migrate + compile real carlove flow` suite because
`/Users/kent/Project/carlove/.claude/e2e/flows/gate-login-flow.yaml` is missing. I did not edit
`/Users/kent/Project/carlove`, per scope guardrail.

## Decisions

- Updated older ambiguity tests to omit the page qualifier where they intend to preserve today's
  flat mapping-wide ambiguity behavior. Qualified duplicates now correctly disambiguate by page.
- Populated page-not-found `candidates` with mapping page keys for 3t's page-binding refusals,
  using gz's existing field without schema changes.
- Left `resolveNavigate()`'s existing empty page candidates untouched; that reconciliation is
  explicitly out of scope.
