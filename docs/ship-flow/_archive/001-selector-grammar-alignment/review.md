<!-- section:review-report -->
# 001-selector-grammar-alignment — Review

## PR Draft

**Title:** e2e-pipeline 2.7.0 — selector grammar alignment (mapper ↔ agent-browser runtime)

**Body:**

```markdown
Closes #7.

## Problem

The `e2e-mapper` agent emits Playwright-style selector vocabulary (`role=tab[name="..."]`, `>> nth=N`, bare `text=`, `has-text(`), but `e2e-test-runner` shells out to `agent-browser` CLI which uses Chrome/Chromium via CDP and only natively parses CSS / `@eN` snapshot refs / its `find role|text|testid|label` semantic-locator subcommand. Mappings produced by `/e2e-map` therefore "passed" `/e2e-test` only via the runner's silent eval-based DOM fallback — false positives. Compiled deterministic scripts (`e2e-compile.js`) lack that fallback and would fail systemically once the eval crutch is removed. The compiler's `selectorToA11yPattern()` partially mitigated, but the mapper-to-runner contract was never formalized.

## Approach

Hybrid of issue #7 options 1 (mapper alignment) + 3 (translation layer):

- **Option 1 — `find role <r> --name "<v>"` subcommand flavor** (Candidate 1 per `design.md`): mapper now emits agent-browser-native vocabulary. CSS-attr flavor (option 1a) rejected for RNW edge cases; subcommand flavor (1b) outsources accessible-name computation to agent-browser's native `find` resolver.
- **Option 3 — formalize `selectorToA11yPattern`** as the single canonical translator at `compiler/lib/selector-translate.js` (extracted from `compiler/codegen.js`). Compiled CI scripts have a deterministic a11y-grep path independent of LLM-runner-side eval fallback.
- **Option 2 (Playwright runtime swap) explicitly rejected** — see `spec.md → ## Deletes`.

## User Journey

> Captain runs `/e2e-map http://my-app:8000`. Mapper produces YAML where every element uses native vocabulary (CSS attr selectors or `find role <r> --name "<v>"` subcommand strings). Captain runs `bash scripts/lint-mapping.sh <mapping.yaml>` — exits 0 (no banned tokens). Captain runs `/e2e-test <flow.yaml>`. Runner reports `eval_fallback_hits: 0` in trace + final report. Compiled script via `/e2e-compile` produces a11y-grep based bash that doesn't rely on `_poll_visible` for any natively-mappable element.

## Done Criteria + Verification

| DC | Type | Procedure | Result |
|---|---|---|---|
| DC-1.2 | cli | `grep -nE 'find role [a-z]+ --name' agents/e2e-mapper.md` | ✅ 9 canonical examples; banned-form mentions only in BAN context |
| DC-1.3 | cli | `bash scripts/lint-mapping.sh test/fixtures/legacy-playwright-mapping.yaml` → exit 2 (4 token classes flagged); same on `native-css-mapping.yaml` → exit 0 | ✅ |
| DC-2.2 | cli | `grep eval_fallback_hits agents/e2e-test-runner.md` | ✅ 8 hits (counter init, log line, final report ×2, strict-mode, Critical Rule 14) |
| DC-2.3 | cli | global ban-form grep on `agents/e2e-flow-verifier.md` + `agents/e2e-debug-observe.md` | ✅ 0 non-ban-context matches |
| DC-3.1 | cli | `grep 'function selectorToA11yPattern\|playwrightTo\|toCss' e2e-pipeline/` | ✅ 1 hit (single definition in `compiler/lib/selector-translate.js:25`) |
| DC-3.2 | cli | `cd e2e-pipeline && bun test` | ✅ 489 pass / 0 fail across 10 files |
| DC-3.3 | cli | fixture regen preserves semantics | ✅ bun test green post-T2.4 |
| DC-3.4 | cli | `grep 'role=[a-z]+\[' test-login.sh test-no-vars.sh` | ✅ 0 matches |
| DC-1.1 | cli | runtime — `/e2e-map` against live target produces native-only mapping | ⏸ DEFERRED (Captain Bet observation window) |
| DC-2.1 | cli | runtime — `/e2e-test` reports `eval_fallback_hits: 0` against fixture flow + live target | ⏸ DEFERRED (Captain Bet observation window) |
| DC-OBS | cli | post-merge captain bet — fresh `/e2e-map → /e2e-test` cycle reports `eval_fallback_hits: 0` within 1 week of merge | ⏸ DEFERRED (this IS the bet observation; ship+1w retro) |

3 runtime DCs explicitly captain-acked deferred to bet observation window per `verify.md → Verdict`. Linter (DC-1.3) prevents regression continuously between merge and retro.

## Captain Bet (observation gate)

Within 1 week of merge, captain expects two simultaneous signals:

1. **(A)** Fresh `/e2e-map → /e2e-test` against any live target reports `eval_fallback_hits: 0`.
2. **(C)** No legitimate use case is silently killed by the eval-fallback removal — every flow that fails post-merge categorizes as "real selector mismatch the new linter would have caught", not "eval fallback was supporting a valid path".

If (1) fails → Cand 1 assumption (`find role` subcommand sufficiency) was wrong. If (2) fails → pre-mortem `wrong-dcs` realized; eval fallback was load-bearing somewhere we didn't audit.

## Changes

12 commits (1 design retrofit + 10 task commits + 1 UAT inline fix) on top of execute base `8586ca1`:

- `e886712` T0.1 linter skeleton + RED fixtures
- `42f451a` T1.1 linter matcher GREEN
- `82497ee` T1.2 mapper Selector Priority canonical rewrite
- `7fc8c06` T1.3 doc-sync 7 files
- `a55845c` T2.1 eval-fallback counter instrumentation spec
- `aac6e83` T2.3 promote `selectorToA11yPattern` to canonical
- `07bd00e` T2.4 fixture + bash script regen
- `f3c68e4` T2.2 remove eval fallback + align consumers + fixture flow
- `31961e5` T0.2 baseline measurement script
- `4212431` T3.1 integration smoke script
- `1d86fba` T3.2 version bump 2.6.0 → 2.7.0 + CHANGELOG
- `da6ebcf` UAT — runner Critical Rule 9 stale RNW guidance fix

## Canonical Docs Update

- ARCHITECTURE.md: **skipped** — file does not exist in this repo (plugin marketplace, no top-level architecture doc); pitch is plugin-internal contract change with no architectural surface change.
- PRODUCT.md: **skipped** — file does not exist; pitch is plugin-internal, no PRODUCT-level user-facing capability change.
- README.md: `1de3ab2` — workspace marketplace README plugin row bumped 2.6.0 → 2.7.0.
- ROADMAP.md: `f58fdf3` (remove from Next) + `a63e7e0` (append to Shipped 2026-05-05).
- CHANGELOG.md: `1d86fba` (T3.2) — detailed 2.7.0 entry with Changed / Added / Captain Bet / References sections (in-plugin doc; not a top-level canonical doc per ship-flow taxonomy).

## Quality Gate

- bun test: 489 pass / 0 fail across 10 files
- linter functional: legacy fixture exit 2, native fixture exit 0
- global ban-form scan (positive guidance, e2e-pipeline/): 0 non-ban-context matches
- Code review (haiku pair: pr-review-toolkit:code-reviewer + silent-failure-hunter): 7 findings, 0 BLOCKING after 100% citation spot-check (1 hallucination dropped, 2 misframed CRITICAL/BLOCKING reduced to NIT, 2 WARNING + 3 NIT deferred as rabbit-holes)

## Rabbit-Holes Filed

(carried from spec + verify; will surface in Captain Bet retro or as separate pitches if needed)

- `ui-verify-text-strip-audit` — audit ui-verify text= strip-regex; preserve, migrate, or unify
- `agent-browser-selector-grammar-doc` — pull canonical out-of-tree agent-browser CLI selector grammar reference into `references/`
- `compiled-vs-llm-divergence-baseline` — divergence reporter; baseline eval-fallback hit count per flow
- (verify, B4 WARNING) `integration-smoke.sh:331` — `grep -oE '[0-9]+' | tail -1` could extract timestamp instead of hit count
- (verify, B3 WARNING) `lint-mapping.sh:94` — text= regex edge cases (unquoted YAML, concat false-positive)
- (verify, A3 NIT) `selector-translate.js:62` — empty-string-vs-null on malformed regex
- (verify, A1 NIT) `codegen.js:1074` — re-export removal idealism (deferred due to test-breakage risk)
- (verify, B1 D2-candidate) `_poll_visible` non-eval fallback documentation — pin into CLAUDE.md to prevent future framing confusion

## Ship-Flow Routing Gap (filed during shape)

Pitch surfaced a ship-flow design-stage routing gap for non-UI contract design. See `docs/ship-flow/todos/ship-flow-non-ui-design-routing-gap.md` for maintainer-eval prompt + this pitch as evidence trail. Design.md was retrofitted mid-execute; captain chose Option A (full retrofit) over Option B (silent decision) to maximize gap-exposure value.

Entity: #001-selector-grammar-alignment
Ship-flow: shape → design (retrofit) → plan → execute → verify → review → ship-final (autonomous)
Tracker: GitHub issue #7
```

## Canonical Docs Update

- ARCHITECTURE.md: skipped — file does not exist in this repo (plugin marketplace; no top-level architecture canonical)
- PRODUCT.md: skipped — file does not exist (plugin-internal pitch; no user-facing capability change at marketplace level)
- README.md: `1de3ab2` — workspace marketplace README plugin row bumped 2.6.0 → 2.7.0
- ROADMAP.md: `f58fdf3` (remove from Next) + `a63e7e0` (append to Shipped 2026-05-05)
- Umbrella closeout: no — entity is `pattern: pitch` with `children[]: [001.1, 001.2, 001.3]` shaped-children, but children are sub-tasks within a single pitch (not separately tracked entities); single-pitch closeout pattern. No parent umbrella row to remove.

## D2 Knowledge Candidates

From `execute.md → ## Knowledge Captures` + `verify.md → ## Knowledge Captures`:

> **Knowledge candidates** — these patterns generalized beyond this entity. Add to CLAUDE.md or auto-memory?

1. **Tier-1 global scan after multi-task contract change** (D1, captured in execute) — when a contract is rewritten across N agents/files, run a fresh global ban-form grep over the WHOLE plugin tree before committing the stage. Stale guidance hides in adjacent sections (Critical Rules, Gotchas, Examples) the per-task agents won't audit. Caught 1 leak (commit `da6ebcf`) in this pitch alone.
2. **Two-mode bash orchestrator pattern** (D1, captured in execute) — when a script's primary action requires a runtime that bash can't dispatch (LLM agents, browser session), default to documenter-mode (prints manual invocation + writes skeleton output) with optional automated-mode behind explicit env-var detection.
3. **Haiku reviewer severity-misframing as the dominant noise mode** (D1, captured in verify) — n=2 here at 50% rate (`silent-failure-hunter`). Citations are valid but severity inflates from NIT to BLOCKING/CRITICAL. Spot-check protocol works; severity reclassification at verify-time IS the value-add. Don't take haiku CRITICAL/BLOCKING at face value.
4. **code-reviewer 33% hallucination rate on regex/pattern reasoning** (D1, captured in verify) — citations valid but A2's regex analysis was wrong. Pattern: when a finding's reasoning depends on understanding regex semantics, mentally run the regex on the cited content during spot-check.
5. **Compiled-script `_poll_visible` is the documented non-eval fallback** (D2-candidate, captured in verify) — eval-fallback removal scope is LLM runner ONLY. Future readers will issue "silent failure" findings if not documented. Worth pinning into `e2e-pipeline/CLAUDE.md` Selector Priority section.
6. **Step 4.0 runtime preflight + plugin-internal pitches: ship-flow design gap** (D2-candidate, captured in verify) — pitches that touch only LLM-agent prompts + bash linters + compiler code have no application "dev server" to bring up. Either ship-flow grows a "runtime-not-applicable / runtime-deferred-to-bet-window" class explicitly, or every plugin-internal pitch hits PROMPT_CAPTAIN at verify. Captured for ship-flow maintainer alongside the existing routing-gap todo.

Captain decides: reply with which candidates to accept. Default action: leave as captured in stage artifacts (no immediate auto-promote).

## Token Summary

Approximate (from per-stage agent reports):

| Stage | Dispatches | Approx Tokens (in / out) |
|---|---|---|
| Shape | 1 (general-purpose L0 codebase research, sonnet) | 65k / 5k |
| Design (retrofit) | 0 (inline main-session) | ~15k / 8k inline |
| Plan | 0 (inline main-session, no fresh-context research dispatched) | ~25k / 12k inline |
| Execute | 9 sonnet + 1 haiku task dispatches | ~480k / 120k |
| Verify | 2 haiku reviewers (code-reviewer + silent-failure-hunter) | ~30k / 8k |
| Review (this stage) | 0 (cross-review skipped — medium-batch, no opt-in; canonical docs patched inline because no `planner` teammate spawned) | ~20k / 6k inline |
| **Total estimate** | **13 dispatches + significant inline** | **~635k input + 159k output** |

**Budget vs actual:** spec didn't carry an explicit `token_budget` field for this entity. Rough industry-norm comparison: a medium-batch pitch with 9 task dispatches typically lands 400-600k tokens. We're at the upper end (~635k) due to:
- Generous research dispatch in shape (full L0 codebase scan)
- 2 haiku reviewers in verify (~60k combined)
- Multiple wave-3 deliverables that produced large bash scripts (T0.2 ~290 LOC, T3.1 ~435 LOC each generated by sonnet ~10-15k each)

Not over-budget by any blowing-out-of-scope sense. Within expected medium-batch range.

## Review Report

**status: passed** (cross-review skipped per Layer A sizing rule: medium-batch + no `pr-review-opt-in`)

- **stage_cost:** 0 fresh dispatches in review stage (planner teammate not spawned; canonical docs patched inline by main session).
- **planner_dispatch_status:** N/A — no team active for this pitch. Canonical doc patches applied inline:
  - ARCHITECTURE.md: skip (file absent)
  - PRODUCT.md: skip (file absent)
  - README.md: 1 commit (`1de3ab2`)
  - ROADMAP.md: 2 commits (`f58fdf3` remove + `a63e7e0` append)
- **verify_results_carried_forward:** 0 BLOCKING; 2 WARNING + 3 NIT deferred to rabbit-holes; 3 runtime DCs captain-acked deferred to bet observation window.
- **canonical_sync_status:** 4-doc audit complete:
  - ARCHITECTURE.md ✅ skip (rationale recorded)
  - PRODUCT.md ✅ skip (rationale recorded)
  - README.md ✅ patched
  - ROADMAP.md ✅ flipped Next → Shipped
- **cross_review_skipped:** medium-batch + no `pr-review-opt-in: true` flag → SKIP per ship-review Layer A sizing rule. Captain may opt-in via frontmatter for any future multi-domain pitch where multi-persona review adds value.
- **captain_ack_audit:** stub flags = none (no stubs in plan); render_fidelity_status = `not-applicable` (`affects_ui: false`); runtime DC deferral = captain-acked 2026-05-05 (Option 2 from verify.md prompt; see `verify.md → ## Verdict` for verbatim record).
- **started_at:** 2026-05-05T11:30:00Z
- **completed_at:** 2026-05-05T11:50:00Z
- **duration_minutes:** ~20

## Hand-off to Ship

- **pr_url:** TBD — ship-final stage opens PR via `gh pr create` (entity status will advance to `ship`, then `done` after merge).
- **review_verdict:** `passed`
- **captain_ack_stubs:** none required (no `## Plan Report → Stub Flags` entries in plan.md). 3 runtime DCs deferral captain-acked at verify stage 2026-05-05 (option 2 — Captain Bet observation window).
- **roadmap_row_ready:** `true` — already in Shipped (commit `a63e7e0`). Ship-final's job is PR creation; ROADMAP no longer needs flip.
- **umbrella_closeout:** no — entity is single-pitch with shaped-children captured as plan tasks, not separate entity records. No parent umbrella row.
- **next_stage:** ship-final — PR creation with body drafted in `## PR Draft` above. Captain merge gate.

<!-- /section:review-report -->
