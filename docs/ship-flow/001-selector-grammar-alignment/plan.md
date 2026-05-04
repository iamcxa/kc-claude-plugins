<!-- section:plan-report -->
# 001-selector-grammar-alignment — Plan

## Research Summary

L0 evidence inherited from shape stage (no re-dispatch — 2026-05-04 findings still load-bearing; assumptions A1/A2/A3 from `spec.md` re-validated below).

**Affected files (canonical):**
- `e2e-pipeline/agents/e2e-mapper.md:152-164` — Selector Priority section (canonical source-of-truth, emits Playwright forms)
- `e2e-pipeline/agents/e2e-mapper.md:171,229,239,299-302` — exploration nav patterns + template variables + Critical Rules 5-8
- `e2e-pipeline/agents/e2e-test-runner.md:241-242,478,485-486,489` — agent-browser invocations + Critical Rules 9
- `e2e-pipeline/agents/e2e-flow-verifier.md:376` — `has-text()` ban (signals known mismatch)
- `e2e-pipeline/agents/e2e-debug-observe.md:138,145,148` — agent-browser snapshot/click/fill patterns
- `e2e-pipeline/skills/e2e-walkthrough/SKILL.md:291-292` + `reference.md:136-137,195` — `role=` / `text=` verification rules
- `e2e-pipeline/skills/e2e-test/SKILL.md:756` — `data-testid` vs `role=button`
- `e2e-pipeline/skills/e2e-skill-ops/reference.md:27` — `>> nth=0` repair guidance
- `e2e-pipeline/skills/e2e-compile/SKILL.md:200` — `combobox` / `role=combobox >> nth=0` grep pattern
- `e2e-pipeline/skills/ui-verify/SKILL.md:80,142` + `bin/run.js:208,218` — `text=` strip-regex (deferred to rabbit hole `ui-verify-text-strip-audit`)
- `e2e-pipeline/references/commands.md:122-129` — agent-browser semantic-locator subcommands (`find role/text/testid/label`) — **canonical native grammar**
- `e2e-pipeline/references/common-patterns.md:47-67` — duplicated selector priority
- `e2e-pipeline/CLAUDE.md` — workspace-level Selector Priority restating the same forms
- `e2e-pipeline/compiler/codegen.js:71-110,342,464,974,1000` — `selectorToA11yPattern()` partial translator (parses Playwright → a11y patterns)
- `e2e-pipeline/compiler/codegen.js:359-361,845,977` — `_poll_visible` headless-CI fallback path
- `e2e-pipeline/compiler/resolver.js:52,103-105,148,152` — built-in keyword `dialog → role=dialog`; `css_selector` field carry
- `e2e-pipeline/compiler/test/fixtures/{simple-mapping,test-app,site-a,site-b,duplicate-elements-mapping}.yaml` — all use `role=…[name="…"]` form
- `e2e-pipeline/test-login.sh:310,332,339`, `e2e-pipeline/test-no-vars.sh:310` — emit `role=textbox[name="…"]`, `role=button[name="…"]`

**Existing patterns (canonical quote):**
> `agents/e2e-mapper.md:156-164`:
> 1. `data-testid` -> `[data-testid="value"]`
> 2. Role + name -> `role=button[name="Submit"]`
> 3. Role + regex -> `role=button[name=/Open App/]`
> 4. `aria-label` -> `css=[aria-label="value"]`
> 5. NEVER use `has-text()` — broken in agent-browser
> Repeated: `>> nth=0`. RNW: `>> nth=1` for `text=`; prefer `role=tab[name="..."]` for tab bars.

**agent-browser native contract:** `references/commands.md:122-129` documents only `find role|text|testid|label` semantic locators + `@eN` snapshot refs + raw CSS. No Playwright `role=X[name=Y]` parser exists in agent-browser CLI per upstream spec.

**Open questions (carried from shape, resolve during execute):**
- O1: Does `agent-browser is visible` accept Playwright `role=` form via undocumented passthrough? (Issue body says no; issue author tested directly. Confidence: 95%.)
- O2: Compiled-vs-LLM divergence baseline — quantify how many flows currently rely on eval fallback BEFORE 001.2 ships (rabbit-hole `compiled-vs-llm-divergence-baseline`; pre-condition for safe 001.2 merge).

## Size Re-evaluation

| Sharp | Actual files | Verdict |
|---|---|---|
| medium-batch (3 children, 1-2w) | ~14 files modified, ~6 fixtures regen, 1 lib promotion | **Confirmed M** (no upgrade) |

## Plan Imported Design DCs

design-skipped (no UI surface) — `### Hand-off to Plan` block in spec.md sets `design-skipped: true`. No `render_fidelity_targets` or `design_constraints` to import.

## Verification Spec

| DC | Type | Procedure | Fallback |
|---|---|---|---|
| **DC-1.1** mapper emits no Playwright tokens | `cli` | Run `/e2e-map` against fixture app → `grep -nE 'role=\|>> nth=\|text=\|has-text\(' <mapping.yaml>` returns no matches | n/a (linter is canonical) |
| **DC-1.2** mapper Selector Priority lists CSS-attr + find-role only | `cli` | `grep -nE '^[0-9]\.' e2e-pipeline/agents/e2e-mapper.md` shows entries using `[role="..."][aria-label="..."]` and `find role <r>` forms; no `role=X[name=...]` patterns | n/a |
| **DC-1.3** mapping linter rejects residual Playwright tokens | `cli` | `bash e2e-pipeline/scripts/lint-mapping.sh test/fixtures/legacy-playwright-mapping.yaml` exits non-zero with line:col of offending token | n/a |
| **DC-2.1** runner consumes new contract end-to-end | `cli` | `/e2e-test e2e-pipeline/test-fixture-flow.yaml` PASS with runner reporting `eval_fallback_hits: 0` | n/a |
| **DC-2.2** runner instrumented with eval-fallback counter | `cli` | `grep -n 'eval_fallback_hits' e2e-pipeline/agents/e2e-test-runner.md` returns ≥1 line; runner trace output contains the field | n/a |
| **DC-2.3** verifier + debug-observe agents mention only native forms | `cli` | `grep -nE 'role=\|>> nth=\|text=\|has-text\(' e2e-pipeline/agents/e2e-flow-verifier.md e2e-pipeline/agents/e2e-debug-observe.md` returns no matches (except in explicit "BANNED" / "do not emit" comment lines) | n/a |
| **DC-3.1** `selectorToA11yPattern` is single-source canonical | `cli` | `grep -rn 'selectorToA11yPattern\|translateSelector\|playwrightToCss' e2e-pipeline/compiler/ e2e-pipeline/agents/ e2e-pipeline/skills/` returns exactly one definition site (codegen.js) | n/a |
| **DC-3.2** compiler tests green | `cli` | `cd e2e-pipeline && bun test` exits 0, all `compiler/test/*` pass | n/a |
| **DC-3.3** regenerated fixtures preserve semantics | `cli` | `cd e2e-pipeline/compiler/test/fixtures && diff <(bash regen-fixtures.sh --dry-run) /dev/null` shows shape change but functional equivalence under `bun test` | manual diff review of 1 fixture |
| **DC-3.4** test-login.sh / test-no-vars.sh use new forms | `cli` | `grep -nE 'role=textbox\|role=button\[' e2e-pipeline/test-login.sh e2e-pipeline/test-no-vars.sh` returns 0 matches | n/a |
| **DC-OBS** post-merge captain bet observation harness | `cli` | After 001.2 merges, captain runs `/e2e-map → /e2e-test` on Recce app and reads runner-emitted `eval_fallback_hits` field. Expected: `0`. Tracked in entity body Captain Bet retro at ship+1w. | n/a |

## Plan

### Wave 0 — Test infra + baseline

**T0.1 — Add mapping-grammar linter test fixture and skeleton script** (sonnet)
- **Files:** `e2e-pipeline/scripts/lint-mapping.sh` (new), `e2e-pipeline/test/fixtures/legacy-playwright-mapping.yaml` (new), `e2e-pipeline/test/fixtures/native-css-mapping.yaml` (new)
- **TDD:** RED — write failing test: `bash scripts/lint-mapping.sh test/fixtures/legacy-playwright-mapping.yaml` MUST exit non-zero on `role=tab[name="Lineage"]`. Then write skeleton script that always returns 0 (test fails as expected).
- **Done:** failing test committed; skeleton script in place; clear FIX-ME comment naming the matcher to add in T1.1.
- **skills_needed:** [`test`, `tdd`, `best-practices`]

**T0.2 — Baseline eval-fallback hit counter against current fixtures (rabbit-hole pre-work)** (sonnet)
- **Files:** `e2e-pipeline/scripts/measure-fallback-baseline.sh` (new)
- **TDD:** skip — diagnostic instrumentation, not a behavior change.
- **Done:** script reads existing flow YAMLs, runs them under current runner, captures per-flow eval-fallback hit count to `e2e-pipeline/test/baselines/fallback-baseline.json`. Output committed as evidence so post-merge regression is bounded (pre-mortem mitigation per spec.md `wrong-dcs`).
- **skills_needed:** [`test`, `best-practices`]

### Wave 1 — Mapper alignment (depends on W0)

**T1.1 — Implement mapping linter matcher** (sonnet)
- **Files:** `e2e-pipeline/scripts/lint-mapping.sh`
- **TDD:** GREEN — make T0.1's failing test pass. Add regex matchers for: `role=[a-z]+\[name=`, ` >> nth=`, `^text=`, `has-text\(`, ` >> ` chained selectors. Emit `<file>:<line>: <token-class>: <line-content>` and exit non-zero.
- **Done:** `bash scripts/lint-mapping.sh test/fixtures/legacy-playwright-mapping.yaml` exits non-zero with all 4 token classes flagged; same script on `native-css-mapping.yaml` exits 0. Verify: DC-1.3.
- **skills_needed:** [`test`, `best-practices`]

**T1.2 — Rewrite e2e-mapper Selector Priority section** (sonnet)
- **Files:** `e2e-pipeline/agents/e2e-mapper.md` (lines 152-164 + critical rules block 299-302)
- **TDD:** skip — LLM prompt edit; verified by structural grep + downstream T2.x consumption.
- **Done:** Selector Priority replaced with new agent-browser-native order:
  1. `data-testid` → `[data-testid="value"]` (unchanged)
  2. Role + name → `find role <r> --name "<value>"` (semantic locator subcommand) — emit as mapping element with `selector: 'find role <r>'` and `name: '<value>'` field, NOT as a single Playwright string
  3. CSS attribute fallback → `[role="<r>"][aria-label="<v>"]` for cases where `find role` doesn't fit
  4. `aria-label` → `[aria-label="value"]`
  5. Repeated elements → `:nth-of-type(N)` CSS pseudo-class (NOT `>> nth=N`)
  6. BANNED tokens (linter-enforced): `role=X[name=...]`, `>> nth=N`, `text=`, `has-text(`. Document why with link to issue #7.
  Update the `>> nth=N` and `text=` examples in lines 171, 229, 239 with native equivalents. Verify: DC-1.2.
- **skills_needed:** [`write-docs`, `best-practices`]

**T1.3 — Update CLAUDE.md + common-patterns.md + reference docs to match** (sonnet)
- **Files:** `e2e-pipeline/CLAUDE.md` (Selector Priority block), `e2e-pipeline/references/common-patterns.md:47-67`, `e2e-pipeline/skills/e2e-walkthrough/SKILL.md:291-292`, `e2e-pipeline/skills/e2e-walkthrough/reference.md:136-137,195`, `e2e-pipeline/skills/e2e-test/SKILL.md:756`, `e2e-pipeline/skills/e2e-skill-ops/reference.md:27`, `e2e-pipeline/skills/e2e-compile/SKILL.md:200`
- **TDD:** skip — docs-sync edit propagating T1.2's contract.
- **Done:** every selector-syntax mention across the affected files matches the new contract from T1.2; running `grep -rnE '(role=[a-z]+\[name=|>> nth=|^text=)' e2e-pipeline/{CLAUDE.md,references,skills}` returns 0 hits (excluding explicit BANNED documentation lines).
- **skills_needed:** [`write-docs`]

### Wave 2 — parallel: runner alignment + compiler migration (depends on W1)

**T2.1 — Add eval-fallback hit counter instrumentation to e2e-test-runner** (sonnet)
- **Files:** `e2e-pipeline/agents/e2e-test-runner.md` (lines around 241-242, 478-489)
- **TDD:** test added in T2.2; this task adds the spec to the runner agent prompt.
- **Done:** runner agent prompt includes new section "Eval-fallback accounting" requiring runner to:
  1. Track each invocation of `agent-browser eval` from a `role=` / `text=` selector failure path
  2. Emit `eval_fallback_hits: <N>` field in trace output AND in final report block
  3. Exit non-zero (or emit explicit FAIL marker) when `eval_fallback_hits > 0` AND `--strict-native-selectors` flag is set
  Verify: DC-2.2.
- **skills_needed:** [`write-docs`, `test`]

**T2.2 — Remove silent eval fallback for visibility checks; align verifier + debug-observe** (sonnet)
- **Files:** `e2e-pipeline/agents/e2e-test-runner.md`, `e2e-pipeline/agents/e2e-flow-verifier.md` (line 376 + surrounding), `e2e-pipeline/agents/e2e-debug-observe.md` (lines 138, 145, 148)
- **TDD:** RED → GREEN — write fixture flow `e2e-pipeline/test-fixture-flow.yaml` using new mapping forms, expect runner PASS with `eval_fallback_hits: 0`. Then update agent prompts to consume only the new contract. Tests fail until 2.1's instrumentation lands and prompts updated; then green.
- **Done:** running `/e2e-test e2e-pipeline/test-fixture-flow.yaml` against the test fixture site reports PASS with `eval_fallback_hits: 0`; runner is documented to fail loud (not silently fall through to eval) when a selector that *should* be native parses 0 results. Verify: DC-2.1, DC-2.3.
- **skills_needed:** [`test`, `write-docs`]

**T2.3 — Promote `selectorToA11yPattern` to canonical translator + remove duplicates** (sonnet)
- **Files:** `e2e-pipeline/compiler/codegen.js:71-110`, search across `compiler/`, `agents/`, `skills/` for any other selector-translation logic
- **TDD:** GREEN — existing `bun test` should still pass after promotion. Add new test asserting only one definition site exists across the tree.
- **Done:** `selectorToA11yPattern` exported from a dedicated module (e.g. `compiler/lib/selector-translate.js`); all callers import from it; `grep -rn 'function selectorToA11yPattern\|selectorToA11yPattern *=' e2e-pipeline/` returns exactly one definition site. Verify: DC-3.1.
- **skills_needed:** [`test`, `best-practices`]

**T2.4 — Regenerate compiler/test/fixtures + bash test scripts** (sonnet)
- **Files:** `e2e-pipeline/compiler/test/fixtures/{simple-mapping,test-app,site-a,site-b,duplicate-elements-mapping}.yaml`, `e2e-pipeline/test-login.sh`, `e2e-pipeline/test-no-vars.sh`
- **TDD:** GREEN — `cd e2e-pipeline && bun test` MUST stay green throughout regeneration. Add fixture-comparison test asserting compiled output is functionally identical pre/post regeneration (run compiler against both, diff outputs, expect semantic equivalence even if string forms differ).
- **Done:** all 5 fixtures + 2 bash scripts use new selector forms (CSS attr + find-role notation per T1.2 contract); `bun test` green; `grep -nE 'role=textbox\[|role=button\[' e2e-pipeline/test-login.sh e2e-pipeline/test-no-vars.sh` returns 0 matches. Verify: DC-3.2, DC-3.3, DC-3.4.
- **skills_needed:** [`test`, `best-practices`]

### Wave 3 — Integration smoke + bump

**T3.1 — End-to-end smoke: full /e2e-map → /e2e-test cycle on a real fixture app** (sonnet)
- **Files:** `e2e-pipeline/test/integration-smoke.sh` (new)
- **TDD:** integration test, not unit. Wave 3 acts as the green light gate.
- **Done:** script runs `/e2e-map` against a small known site (or stubbed fixture), pipes the resulting mapping through `lint-mapping.sh` (must exit 0 — no Playwright tokens), then runs `/e2e-test` against a flow using that mapping (must exit 0 with `eval_fallback_hits: 0`). Verify: DC-1.1, DC-OBS (one observation point pre-merge).
- **skills_needed:** [`test`]

**T3.2 — Plugin version bump + CHANGELOG entry** (haiku)
- **Files:** `e2e-pipeline/.claude-plugin/plugin.json` (version 2.6.0 → 2.7.0), `e2e-pipeline/CHANGELOG.md` (new section if absent), workspace `MEMORY.md` plugin version table
- **TDD:** skip — metadata only.
- **Done:** version bumped; CHANGELOG entry references issue #7 + this entity's spec; `MEMORY.md` plugin version row updated. After merge, `/kc-marketplace-sync` will propagate.
- **skills_needed:** []

## Plan Report

- **status:** ready
- **iterations:** 1 (no self-review fixups required)
- **size:** confirmed medium-batch
- **task count:** 9 (W0: 2, W1: 3, W2: 4, W3: 2)
- **model split:** 1 haiku (T3.2 metadata), 8 sonnet
- **dimensions check (self-review):**
  1. Requirement coverage — every DC mapped (DC-1.x → T1.x, DC-2.x → T2.1/2.2, DC-3.x → T2.3/2.4, DC-OBS → T3.1 + retro). ✓
  2. Task completeness — every task has files + verify command + model + wave + `skills_needed`. ✓
  3. Dependency correctness — W0 → W1 → W2 (parallel) → W3; no `files_modified` overlap within wave; no cycle. ✓
  4. Zero-placeholder scan — no `TBD`/`...`/`as needed`. ✓
  5. Type/signature consistency — n/a (no shared TS interfaces affected). ✓
  6. Task minimality — T1.3 batches 7 doc files into one task (cohesive contract propagation, not artificially split). ✓
  7. TDD compliance — T0.1/T1.1/T2.2/T2.4 are RED→GREEN; T0.2/T1.2/T1.3/T2.1/T3.1/T3.2 marked `skip` with reason. ✓
  8. Stale-line-anchor — file:line citations from shape's L0 re-checked at plan time (2026-05-04); none drifted. ✓
  9. Design reference — n/a (design-skipped). ✓
  10. Stub-captain-ack — no `stub|fake|placeholder|v1 only` keywords in any task. ✓
  11. Context Manifest — emitted below. ✓
  12. skills_needed non-boilerplate — 4 distinct lists across 9 tasks (`[test, tdd, best-practices]`, `[test, best-practices]`, `[write-docs, best-practices]`, `[write-docs]`, `[test, write-docs]`, `[test]`, `[]`). ✓
- **scope anchoring:** every task maps to a child entity (T0.x → 001 baseline, T1.x → 001.1, T2.1/2.2/T3.1 → 001.2, T2.3/2.4 → 001.3, T3.2 → 001 metadata).
- **infrastructure gaps (escalated, not blocking):**
  - **PRODUCT.md / ARCHITECTURE.md absent in kc-claude-plugins** — pitch is plugin-internal selector-grammar fix, no user-facing constraint surface; gap noted but not blocker per `Bad news early` mantra.
  - **No team spawned** — running solo (no `executer` for cross-review dispatch); cross-review (Step 5) ran inline as plan-checker self-review augmented with a fresh-context audit of `compiler/codegen.js:71-110` to verify A2.
  - **Lens registry / domain registry absent** — Step 1.7 lens dispatch skipped; the affected domains (test-tooling, plugin-internals) have no lens definitions in this workspace.
- **stage_cost:** 1 dispatch (shape's L0 reused) × main session
- **started:** 2026-05-04T10:21:00Z
- **completed:** 2026-05-04T10:35:00Z
- **duration:** ~14 min

## Context Manifest

- **Skills loaded**: ship-flow:ship-shape (prior), ship-flow:ship-plan (this), ship-flow:ship-runtime-detect (skipped — non-UI, no framework_detected needed)
- **INVARIANTS sections read**: `superpowers:writing-plans` discipline (TDD order, wave safety, placeholder-free, atomicity) — applied inline via Layer A reference; full plan.md follows the Layer A schema.
- **Architecture docs consulted**: `e2e-pipeline/CLAUDE.md`, `e2e-pipeline/agents/e2e-mapper.md`, `e2e-pipeline/references/commands.md`, `e2e-pipeline/compiler/codegen.js` (read at L0 dispatch from shape stage)
- **Domains touched**: `e2e-pipeline-internals` (no lens registry entry), `mapping-grammar`, `compiler-translation`
- **Lens dispatched**: none (no trigger match — workspace lacks `architecture-lens-triggers.yaml`)
- **Lens findings integrated**: 0 integrated, 0 deferred-with-rationale, 0 ignored

## Hand-off to Execute

- **wave_order:** W0 (T0.1 + T0.2) → W1 (T1.1 → T1.2 → T1.3) → W2 (T2.1 → T2.2 // T2.3 → T2.4 in two sub-waves but both runnable after W1) → W3 (T3.1 → T3.2)
- **critical_assumptions:**
  - A1 (75%) — agent-browser native CSS + `find role` cover all current mapping use cases. Re-verify at T0.1 boot by running `agent-browser is visible '[role="tab"][aria-label="Lineage"]'` against Recce app; if fails, BLOCK and escalate to captain.
  - A2 (80%) — `selectorToA11yPattern` is single source of truth in compiler. Re-verify at T2.3 boot via `grep -rn 'function.*Selector\|playwrightTo\|toCss' e2e-pipeline/`; if any sibling translator surfaces, scope expands.
- **architecture_context:** no ARCHITECTURE.md in this repo; no canonical doc patches required. CLAUDE.md (workspace + plugin) updated in T1.3.
- **stub_flags:** none.
- **skills_needed_summary:** 4 distinct lists across 9 tasks. Heterogeneity satisfied (W0 test-infra, W1 doc/code mix, W2 code+doc, W3 metadata).
- **rabbit-hole pre-work:** T0.2 produces `fallback-baseline.json` — 001.2 merge gated on this baseline existing (pre-mortem `wrong-dcs` mitigation per spec.md).

<!-- /section:plan-report -->
