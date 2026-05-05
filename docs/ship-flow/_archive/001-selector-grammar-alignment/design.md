# 001-selector-grammar-alignment — Design

> **Retrofit notice:** This design.md was authored AFTER plan.md landed, exposing a ship-flow routing gap — design stage did not auto-trigger for non-UI contract design (selector grammar vocabulary between e2e-mapper and agent-browser runtime). Triggers in ship-shape Phase 8 / ship-plan Step 1.6 fire on `affects_ui:true` OR `domain:` set OR `*.tsx|*.css|*.html` glob OR `--design` flag — none matched this pitch despite a real cross-component contract decision being on the table. Captain explicitly chose to retrofit (vs lock the decision in plan T1.2 silently) so the gap leaves audit evidence for the ship-flow maintainer. See `docs/ship-flow/todos/ship-flow-non-ui-design-routing-gap.md` (filed alongside this commit).

## Design Question

The pitch has agreed on `option 1+3 hybrid` from issue #7 — align mapper to agent-browser native AND formalize translation layer in compiler. **What native form does the mapper emit as canonical?** Three candidates with non-trivial trade-offs across grep-friendliness, mapping-yaml schema stability, RNW edge cases, and fixture migration scope.

## Constraints

- **C1 — agent-browser CLI native vocabulary** (verified: `references/commands.md:122-129`): supports raw CSS, `@eN` snapshot refs, and `find role|text|testid|label` semantic-locator subcommand. No Playwright passthrough.
- **C2 — Existing mapping schema** is single-string `selector:` per element. Switching to multi-field requires migrating ~5 production fixtures + ~50 in-the-wild mappings (out of scope for this pitch — separate medium-batch).
- **C3 — RNW (React Native Web) reality** (per `agents/e2e-mapper.md:299-302`): many components emit `role` without matching `aria-label`; some emit `aria-label` without `role`. Pure CSS attr selectors hit `[role="x"]` ambiguity often.
- **C4 — Compiler translation cost**: any chosen form must round-trip through `selectorToA11yPattern()` to produce a11y-tree grep patterns for headless CI (`compiler/codegen.js:71-110`). Forms that diverge from current parser shape add code path.
- **C5 — Linter simplicity**: T1.1 plan task adds a mapping-grammar linter. Single-string forms keep the linter regex small; structured forms require schema-aware parsing.

## Candidates

### Candidate 1 — `find role <r> --name "<v>"` (subcommand string)

**Form (in mapping yaml):**
```yaml
elements:
  lineage_tab:
    selector: 'find role tab --name "Lineage"'
```

**Pros:**
- 1:1 with agent-browser native `find` subcommand → runner can invoke verbatim, no translation
- Self-documenting: reader sees the exact CLI call
- Linter regex stays small: ban `role=`, `>> nth=`, `text=`, `has-text(`; any `find role` line is whitelisted

**Cons:**
- Mixes two grammars in one yaml — some lines are CSS strings (`[data-testid="x"]`), some are CLI fragments (`find role tab --name "..."`). Mental overhead for readers.
- Compiler `selectorToA11yPattern` needs a NEW parser branch (currently parses `role=X[name=Y]` form); ~30 LOC addition.
- Doesn't extend cleanly to the `text` / `testid` / `label` cousins — would need parallel `find text "..."` strings, multiplying the grammar surface

**Migration cost:** ~5 fixtures + 2 bash scripts rewrite. ~30 LOC compiler addition. Existing in-the-wild mappings: re-run `/e2e-map` (mapper auto-regen).

### Candidate 2 — `[role="<r>"][aria-label="<v>"]` (pure CSS attr)

**Form (in mapping yaml):**
```yaml
elements:
  lineage_tab:
    selector: '[role="tab"][aria-label="Lineage"]'
```

**Pros:**
- Single grammar across the entire mapping — every `selector:` is CSS, period.
- Linter is 4 lines of regex. Reader knows what to expect.
- Compiler `selectorToA11yPattern` simpler — strip selector to `[role="X"]` substring and grep a11y tree by role + name pair (already half the existing logic).
- Aligned with browser-native standards — works in DevTools, Playwright (if anyone bisects with it), Cypress, etc.

**Cons:**
- **C3 RNW reality bites:** many RNW components have `role` without `aria-label`. Falls back to `[role="tab"]` + nth-of-type, which is positional → fragile.
- Some elements have `name` that's NOT in `aria-label` but in text content (e.g., `<button>Submit</button>` has no aria-label, name comes from textContent). CSS can't query textContent. Pushes back to `:has-text()`-like ban-list — exact same Playwright trap.
- The `name="..."` semantics in agent-browser's `find role` is actually broader than CSS `aria-label` (it matches `aria-labelledby` chains, accessible name computation per WAI-ARIA). CSS attr selector loses that.

**Migration cost:** ~5 fixtures + 2 scripts. Compiler ~10 LOC simplification. BUT: every existing element where name comes from textContent / aria-labelledby / placeholder needs a different selector — likely 30-40% of mappings.

### Candidate 3 — Structured `{role, name}` object

**Form (in mapping yaml):**
```yaml
elements:
  lineage_tab:
    role: tab
    name: Lineage
```

**Pros:**
- Schema-enforceable: yaml validator can require `(role, name)` or `(testid)` or `(text)` shapes. No grammar drift possible.
- Compiler can dispatch on shape, not parse strings. ~20 LOC simpler than Candidate 1.
- Cleanly extends to `{testid}`, `{text}`, `{label}`, `{css}` — each variant explicit.
- Captain (or future maintainer) reading mapping yaml sees intent immediately.

**Cons:**
- **Breaking change:** every existing mapping yaml must be migrated. Estimate: ~50 in-the-wild mappings (Recce app, demo apps, etc.) Captain owns one repo's mappings (Recce); others live in user-land.
- Out-of-scope ballooning: this becomes a separate medium-batch (schema migration + back-compat shim + migration script).
- Plan T2.4 fixture regen: not a string substitution but a structural rewrite.
- Contract changes for ALL consumers (runner, verifier, debug-observe, compiler, linter) — much wider blast radius than 1 or 2.

**Migration cost:** ~50 mappings × structural rewrite. Schema validator addition. Back-compat shim that accepts old single-string form for transition window. Plan-task count likely 12-15 instead of 9. **This is its own pitch.**

## Trade-off Matrix

| | Cand 1 (subcommand str) | Cand 2 (CSS attr) | Cand 3 (structured) |
|---|---|---|---|
| Single grammar in yaml | ✗ (mixed) | ✓ | ✓ |
| Linter regex simplicity | ✓ small | ✓ smallest | n/a (schema) |
| Compiler translation LOC | +30 (new branch) | -10 (simplify) | -20 (dispatch) |
| RNW edge cases (no aria-label / textContent name) | ✓ handled by `find role --name` | ✗ falls back to fragile selectors | ✓ schema covers |
| WAI-ARIA accessible-name match | ✓ native | ✗ aria-label only | ✓ via `find role` underneath |
| Fixture migration scope (this pitch) | ~5 fixtures, ~30 LOC compiler | ~5 fixtures + 30-40% selector rework | ~5 fixtures + schema migration |
| In-the-wild mapping migration | re-run /e2e-map (auto) | partial rework needed | full migrate, separate pitch |
| Scope creep risk | low | medium (RNW rework) | high (own pitch) |
| Self-documenting | strong | medium | strongest |
| Aligned with browser standards | weak (subcommand syntax) | strong | medium (custom shape) |

## Recommendation

**Candidate 1** — `find role <r> --name "<v>"` subcommand string form.

Reasoning weights (in order):
1. **Scope discipline (heaviest):** this pitch's appetite is medium-batch, ~9 tasks. Candidate 3 is a separate pitch; Candidate 2 absorbs RNW-rework work that's not in shape's scope-in. Candidate 1 fits the appetite.
2. **RNW correctness (C3):** mapper's `>> nth=N` + `text=` patterns existed precisely BECAUSE pure CSS attr selectors don't cover RNW well. Going to Candidate 2 means re-creating the same problem under a new name. Candidate 1 outsources the heavy lifting to agent-browser's accessible-name computation.
3. **Compiler additions are tractable:** +30 LOC for a new parse branch is trivial vs +schema validator + migration scaffolding (Cand 3).
4. **Mixed grammar acceptable trade:** yaml-readers see `find role` as a clear signal "this is a semantic locator, not a CSS selector"; documented in updated `agents/e2e-mapper.md` with examples for both `find role` and `[data-testid="..."]` styles.
5. **Door left open for Cand 3:** if/when someone files a future pitch to formalize mapping schema, the migration path from Cand 1 strings to Cand 3 objects is mechanical (regex parse). Cand 2 → Cand 3 is harder because Cand 2 strings have ambiguous semantics (role=tab vs role=tabpanel both map to `[role="tabpanel"]` if we got attr names wrong).

## Hand-off to Plan (revised)

- design-skipped: false — design stage retrofitted (see Retrofit notice above)
- canonical_selector_form: `find role <r> --name "<v>"` (Candidate 1)
- breaks: ban `role=X[name=...]`, `>> nth=N`, `text=` (except inside `find text "..."`), `has-text(`
- repeated_elements_form: `:nth-of-type(N)` CSS pseudo (NOT `>> nth=N`)
- compiler_translation: new parse branch in `selectorToA11yPattern` accepting `find role <r> --name "<v>"` → a11y-tree pattern `role=<r> name=/<v>/i`
- rabbit_holes_added:
  - `ship-flow-non-ui-design-routing-gap` — file maintainer-eval prompt + this case as evidence
  - (existing) `compiled-vs-llm-divergence-baseline`, `agent-browser-selector-grammar-doc`, `ui-verify-text-strip-audit`
- plan_amendments_required:
  - T1.2: lock canonical form to Cand 1 (already aligned; no diff needed)
  - T2.4: fixture regen rewrites `role=textbox[name="Email"]` → `find role textbox --name "Email"` (Cand 1) — already aligned with current plan draft; verify no Cand 2 leakage in fixture rewrite specs
  - T0.1: linter test fixture should include 1 example each of all 4 banned forms

## Captain Decision

> **Decision:** Candidate 1 — `find role <r> --name "<v>"` subcommand string form.
>
> **Rationale (captain-endorsed; agent-drafted recommendation accepted verbatim):**
>
> 1. **Scope discipline:** this pitch's appetite is medium-batch, ~9 tasks. Candidate 3 is a separate pitch; Candidate 2 absorbs RNW-rework work that's not in shape's scope-in. Candidate 1 fits the appetite.
> 2. **RNW correctness (C3):** mapper's `>> nth=N` + `text=` patterns existed precisely BECAUSE pure CSS attr selectors don't cover RNW well. Going to Candidate 2 means re-creating the same problem under a new name. Candidate 1 outsources the heavy lifting to agent-browser's accessible-name computation.
> 3. **Compiler additions are tractable:** +30 LOC for a new parse branch is trivial vs +schema validator + migration scaffolding (Cand 3).
> 4. **Mixed grammar acceptable trade:** yaml-readers see `find role` as a clear signal "this is a semantic locator, not a CSS selector"; documented in updated `agents/e2e-mapper.md` with examples for both `find role` and `[data-testid="..."]` styles.
> 5. **Door left open for Cand 3:** if/when someone files a future pitch to formalize mapping schema, the migration path from Cand 1 strings to Cand 3 objects is mechanical (regex parse). Cand 2 → Cand 3 is harder because Cand 2 strings carry ambiguous role/aria-label semantics.
>
> **Date:** 2026-05-04
> **Approval method:** captain delegated to agent recommendation ("按你建議") — this is documented as agent-drafted-captain-endorsed rather than captain-original-authored, per ship-shape Captain Bet discipline (cf. INVARIANTS Principle 6 Rule C ABC clause). Future retro: if Bet outcome falls on the contract-form decision, this attribution informs whether the rationale was load-bearing.

## Course Correction (Post-PR-Review, 2026-05-05)

**Trigger:** Copilot pull-request review on PR #8 generated 7 inline findings; 5 of them (C1, C4, C5, C6, C7 — see https://github.com/iamcxa/kc-claude-plugins/pull/8) cited the same root contract bug.

**Root cause:** `find role <r> --name "<v>"` is documented in agent-browser as a **subcommand chain** family (`agent-browser find role X click --name Y "value"`), NOT a selector grammar. Storing it in mapping yaml `selector:` fields and passing it to `agent-browser is visible/click/fill '<string>'` was structurally wrong — agent-browser would interpret the entire `find role X --name Y` string as a CSS selector and fail at runtime, OR fall back to eval (the very fallback this PR was removing).

**Why design.md missed this:** Candidate 1 analysis treated `find role <r> --name "<v>"` as if agent-browser had a unified "selector engine" that accepts both CSS strings and `find role` subcommand strings. agent-browser actually treats `find role` as a verb-prefix subcommand family — the action verb (`click`/`fill`/`is visible`) is the CHILD command, not a separate command consuming the find-role-string as input.

**Pre-mortem fired exactly as expected.** Captain Bet retro condition (1) — "agent-browser native CSS + `find role` subcommand sufficient to replace Playwright forms" — was wrong. Specifically: native CSS attribute form is sufficient; `find role` subcommand strings are NOT a viable selector representation.

**Course correction: switch canonical form to Candidate 2** (CSS attribute, `[role="<r>"][aria-label="<v>"]`). This was the option danyelf (issue reporter) listed as 1a in the original issue body, originally rejected here for RNW edge cases. The rejection rationale stands (RNW components frequently emit `role` without `aria-label`), but it's a SOFT limitation (rabbit-hole: add `data-testid` to those components) compared to Cand 1's HARD failure (selector strings that agent-browser cannot parse).

### Updated rationale weights

1. **Structural correctness (new)** — Cand 2 strings parse as native CSS in agent-browser. Cand 1 strings DO NOT parse as anything valid; they cause runtime failures.
2. **Scope discipline (unchanged)** — Cand 2 fits medium-batch appetite; Cand 3 still scope-blowout.
3. **RNW correctness** — DOWNGRADED from "heavy weight" to "soft limitation". Components without aria-label add `data-testid` (rabbit-hole; not a structural blocker).
4. **Compiler additions** — Cand 2 needs translator branches for `[role="X"][aria-label="Y"]` → snapshot-literal `<role> "<name>"` format. Smaller delta than Cand 1's invalid translation patterns.
5. **Door open for Cand 3** — unchanged. Cand 2 → Cand 3 migration is mechanical regex parse later if/when schema migration is in scope.

### Captain Decision (revised)

> **Revised Decision:** Candidate 2 — `[role="<r>"][aria-label="<v>"]` CSS attribute form.
>
> Approval method: Copilot static-contract review on PR #8 supplied evidence equivalent to the deferred runtime DCs (DC-1.1, DC-2.1). Captain accepted Path C (in-PR fixup) on 2026-05-05 after reading the 7-finding summary. RNW edge cases captured as separate rabbit-hole.
>
> Date: 2026-05-05

### Knowledge captures (D1 / D2)

- **[D1] Subcommand-chain vs selector-grammar confusion** — when an external CLI exposes a `find <kind> <args> <action>` subcommand family, that command structure is NOT interchangeable with a selector-string grammar. A "selector" in mapping yaml expects a string consumable by single-shot action commands; a subcommand chain expects multi-arg orchestration. Confusing the two leads to runtime failures where stored "selectors" can't actually be invoked. Future schema design must distinguish these layers explicitly.
- **[D2] PR-review-as-runtime-DC equivalence** — when verify-stage runtime DCs are deferred to post-merge bet observation, external static contract review (Copilot, manual reviewer) can supply equivalent gating evidence pre-merge. The Captain Bet's "(1) failed → assumption wrong" condition is what Copilot caught; effectively the bet's pre-merge equivalent ran via diff-aware static analysis instead of live runtime. Worth recording as a fallback gate for plugin-internal pitches that lack a project dev server.
