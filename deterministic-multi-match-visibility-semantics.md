---
title: Define deterministic visibility semantics for hidden-first multi-match selectors
status: validation
source: GitHub issue #91; committed e2e-pipeline/S1 work item
product: e2e-pipeline
sprint: S1
started: 2026-08-02T14:13:18Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-deterministic-multi-match-visibility-semantics
issue: "91"
pr:
design: required
lane: main
id: d3mmhwzpdye4mtg6yc0jvmdz
---

## Problem

`agent-browser is visible <selector>` resolves a CSS selector with
`document.querySelector`, then measures that one object. A hidden or zero-area first match can
therefore produce `false` even when a later match is rendered. Worse, malformed CSS such as `[` is
also printed as `false` by the supported CLI, so raw boolean polling cannot distinguish absence
from a selector error.

Fresh proof against `origin/main` `0a1079c`, `agent-browser 0.32.0`, and managed Chrome for
Testing `151.0.7922.47` reproduced the filed symptom:

| observation | result |
|---|---|
| `get count h1` over `[style-visible 0x0, style-visible 1264x45]` | `2` |
| raw `is visible h1` | `false` |
| accessibility snapshot | one heading, `Visible later` |
| one IIFE DOM probe | candidate 0 nonzero-layout-visible `false`; candidate 1 `true` |
| raw `is visible '['` | `false` |
| IIFE `querySelectorAll('[')` | `SyntaxError`, retained as `invalid_selector` |

The previous Chrome/agent-browser observation is therefore reproduced rather than inherited.
The issue is not a timing tweak: five consumers currently make different visibility decisions,
and none retains DOM cardinality plus candidate evidence.

## Scope authority

Scope is already captain-authored in issue #91's 2026-08-01 decision and committed in
`e2e-pipeline/S1`; no new scope questions are needed. The required outcome is one visibility
contract across runner, mapper, verifier, walkthrough, and compiled scripts. The decision is:

- default to strict raw DOM cardinality;
- permit one explicitly mapped exception, `retained-zero-rect`;
- keep parser, invalid-selector, and browser/protocol failures terminal and fail-loud;
- retain match count and bounded per-candidate evidence in every result;
- make non-unique mappings unique unless they exhibit the exact retained-zero-rect signature.

This entity does not reopen sprint membership, issue priority, or the captain's rejection of plain
`any-visible` and vaguely named active-tree scoping.

## Value

A visible page must no longer be reported absent because a retained zero-area node sorts first,
while an over-broad mapping must not become a false PASS merely because one of several unrelated
matches happens to be rendered. The operator gets a stable result class, count, and evidence that
explains whether the selector matched nothing, matched only non-rendered nodes, matched exactly
one rendered node, or violated cardinality.

## Options considered

### 1. Plain `any-visible` — rejected

Pass when any candidate is rendered. This fixes the reproduction cheaply but lets `h1` or
`[role="heading"]` pass when they match two real application states and the rendered candidate is
not the one the mapping intended. Visibility aggregation cannot recover selector identity.

### 2. Active-tree filtering — rejected

Drop hidden/zero-area candidates before counting. The term is underspecified, and filtering a
genuinely hidden sibling also converts the same ambiguous selector into a false PASS. The
accessibility tree cannot establish raw DOM cardinality because it deliberately omits or collapses
DOM candidates.

### 3. Strict raw cardinality plus one named exception — taken

Exactly one raw DOM match is the default. `retained-zero-rect` may pass only when exactly one
candidate is nonzero-layout-visible and every extra candidate is style-visible with no
positive-area client rect. `display:none`, `visibility:hidden`, opacity-hidden, or a second
rendered candidate disqualifies the exception.

This is the cheapest compatible seam because it uses the already-supported `agent-browser eval`
IIFE path, the existing mapping `css_selector`, the existing owned browser runtime, and Node that
compiled scripts already require. It does not add an accessibility-name implementation, modify
agent-browser, or invent a third selector field.

## Fastest path, smallest cut, and taken path

- **Fastest path:** paste the IIFE and policy logic into the four agent instructions and emit a
  fifth copy from `codegen.js`. Rejected because five copies can drift while still looking alike.
- **Smallest cut:** fix only compiled scripts, where deterministic code is easiest. Not authorized:
  the issue explicitly requires all five consumers, so this would cut scope rather than choose a
  cheaper mechanism.
- **Taken path:** one dependency-free module plus a thin CLI adapter. Agents invoke the adapter
  around their existing owned browser command; codegen imports that module and emits its standalone
  support. No consumer is deferred.
- **More thorough path not taken:** patch upstream agent-browser with accessible-locator
  cardinality, cross-frame/shadow traversal, and perceptibility or hit-testing. None is needed to
  satisfy the current-document zero-rect defect, and each changes a different contract.

If the shared transport cannot be made to work for all five consumers, the task parks for re-cut;
it does not silently fall back to five private implementations or drop a consumer.

## Reverse-recovery audit

Audit target: freshly fetched `origin/main` at `0a1079c4904bdd5c8cee6f5e3d01b997faf8f1f4`.

| layer | verdict | evidence and consequence |
|---|---|---|
| upstream CSS resolution | **EXISTS_BROKEN** | `agent-browser` v0.32.0 `cli/src/native/element.rs:479-589,688-705,915-958` uses `document.querySelector` and checks that first object; the same implementation is still present at v0.33.2 |
| upstream count/eval capability | **WORKING** | v0.32.0 exposes `get count` and `eval`; the fresh live spike proved one IIFE can retain `querySelectorAll` exceptions and per-candidate rect/style evidence |
| owned runtime | **WORKING** | `e2e-pipeline/bin/e2e-browser-runtime.js:11-41,2585-2653` allowlists `eval`, pins the namespace/session/profile and managed Chrome executable, and already routes every consumer |
| selector grammar authority | **WORKING** | `compiler/lib/selector-policy.js:1-76` owns the banned classes; `compiler/lib/selector-translate.js:1-153` owns the mapping DSL to snapshot translation |
| mapping locator shape | **EXISTS_BROKEN** | `compiler/resolver.js:61-65` reads `selector` and optional `css_selector`, but `resolveElement()` at `:225-246` returns only `selector`; visibility expects at `:367-405` discard `cssSelector` even when page-scoped resolution found it |
| compiled positive visibility | **EXISTS_BROKEN** | `compiler/codegen.js:769-787,1762-1788` uses a first-occurrence accessibility substring for translatable locators and raw `is visible` otherwise; neither path has DOM count or candidate evidence |
| compiled negative visibility | **EXISTS_BROKEN** | `compiler/codegen.js:655-676,1791-1804` treats raw `false` as success, so malformed CSS can be downgraded to absence |
| runner | **EXISTS_BROKEN** | `agents/e2e-test-runner.md:323-349` maps visible/not-visible directly to raw scalar `is visible` |
| verifier | **EXISTS_BROKEN** | `agents/e2e-flow-verifier.md:161-173` repeats the raw scalar check and has no cardinality evidence |
| walkthrough | **EXISTS_BROKEN** | `skills/e2e-walkthrough/reference.md:187-190,244-249` splits a11y substring and raw scalar checks, so it cannot produce the shared algebra |
| mapper | **MISSING** | `agents/e2e-mapper.md:160-218` derives selectors from snapshots but never proves that the DOM selector it writes resolves or is unique |
| shared probe/classifier | **MISSING** | multi-strategy search for `visibility_policy`, `retained-zero-rect`, and the result names returned no tracked implementation |
| reports | **MISSING** | no consumer currently records visibility result class, DOM match count, effective policy, and bounded candidate evidence together |

This is not a greenfield visibility system. Browser ownership, eval, selector parsing, mapping
resolution, polling, reports, and generated-script Node support already exist. The repair is to add
one classifier seam and route the existing five consumers through it.

Live branch-protection facts were also read, rather than inferred from workflow files. Main
currently requires the context `version parity (plugin.json / marketplace.json / codex / README)`.
This task does not rename that job or change merge policy.

## Spike result

The riskiest mechanism was spiked through the exact fresh `origin/main` runtime, not by calling a
bare browser command:

1. A flow-managed, previously absent profile opened `https://example.com` through the owned
   runtime with `agent-browser 0.32.0` and managed Chrome for Testing 151.
2. One IIFE installed `[style-visible 0x0, style-visible positive-area]` candidates.
3. The scalar command reproduced `count=2`, `visible=false`; the snapshot exposed the later node.
4. A single eval returned both candidates with `checkVisibility(...)` and rect evidence.
5. Malformed CSS returned a retained `SyntaxError` from the IIFE even though raw `is visible`
   returned `false`.
6. Owned cleanup returned `canonical_profile: unchanged` and `cleanup: removed`.

Result: the mechanism is viable. The plugin must classify the eval payload itself; composing raw
`get count`, `get box`, and `is visible` calls cannot provide atomic evidence or keep invalid CSS
distinct from absence.

## Design determination — `design: required`

This task decides a mapping/API shape, result algebra, CLI protocol, and generated-script
interface. It is not a trivial restoration of an already documented contract.

### Mapping API

```yaml
pages:
  home:
    elements:
      page_heading:
        selector: 'role=heading[name="Home"]'
        css_selector: 'main > h1[data-testid="page-heading"]'
        visibility_policy: retained-zero-rect
```

- `visibility_policy` is optional and accepts only `strict` or
  `retained-zero-rect`; absence means `strict`.
- The effective DOM selector is `css_selector` when present, otherwise `selector` only when that
  value is literal CSS accepted by `querySelectorAll`.
- A resolved mapped visibility assertion using non-CSS locator DSL (`role=`, `text=`, `xpath=`, or
  another translated form) without `css_selector` fails before browser execution with mapping
  path, page, element, and remediation. It must not be passed to `querySelectorAll` and mislabeled
  `invalid_selector`.
- `css_selector` becomes the DOM identity authority for mapped visibility as well as the existing
  action fallback. A third `visibility_selector` is not added: it would duplicate the same CSS
  identity and would not solve equivalence to computed accessible-name matching.
- Built-in mapped visibility such as `dialog` supplies a compiler-owned literal DOM selector;
  literal text expectations remain accessibility-text assertions and are not reclassified as
  mapped selector visibility.
- Parameterized selectors substitute both `selector` and `css_selector` before probing. Reports
  retain the template identity and effective substituted DOM selector.

The compatibility cost is explicit: existing resolved `role=`/`text=` visibility mappings without
`css_selector` must be migrated. Keeping their a11y-substring fallback would preserve the exact
count-blind behavior this task exists to remove.

### Render predicate

For each candidate, `nonzero-layout-visible` is exactly:

```text
element.checkVisibility({opacityProperty: true, visibilityProperty: true}) === true
AND
at least one element.getClientRects() rectangle has width > 0 and height > 0
```

`aria-hidden` and `inert` are evidence only. Computed `display`, `visibility`, and `opacity`, every
bounded client rect, and the bounding rect are evidence. `IntersectionObserver`, `offsetParent`,
computed style alone, the accessibility tree, and rect alone are not classifiers.

If `checkVisibility` is unavailable or throws, the probe returns `probe_error`; it does not weaken
the named predicate with a fallback. Known limits are documented: `display:contents`, visible
overflow from zero-sized containers, clipping, transforms, occlusion, and offscreen position. This
is layout visibility for the reproduced defect, not perceptibility or actionability.

### Probe scope and evidence bounds

The query root is the current document evaluated by the existing owned browser command. It does not
silently pierce shadow roots or cross frame boundaries, because that would count a different set
than the CSS selector consumed by current agent-browser actions. Open/closed shadow DOM, iframe
aggregation, viewport intersection, hit testing, and occlusion are explicit limits/out of scope.

The browser IIFE computes aggregates over **all** matches before truncating evidence. It returns:

```json
{
  "probe_version": 1,
  "probe_scope": "current-document",
  "match_count": 2,
  "nonzero_layout_visible_count": 1,
  "style_visible_zero_rect_count": 1,
  "non_style_visible_count": 0,
  "candidate_evidence_limit": 10,
  "candidate_evidence_truncated": false,
  "candidates": []
}
```

Candidate evidence is capped at ten but classification uses the uncapped aggregate counts. Each
candidate includes index, tag, literal role attribute, `data-testid`, a control-stripped and
length-capped label, `aria-hidden`, `inert`, `checkVisibility`, computed style, capped client rects,
rect count/truncation, and bounding rect. It never includes `innerHTML`, input values, cookies,
storage, or browser profile data.

For `probe_error` and `invalid_selector`, `match_count` is `null`, never `0`; otherwise an error
could be mistaken for `no_match`.

### Result algebra

| result | invariant | positive assertion | negative assertion |
|---|---|---|---|
| `probe_error` | command, envelope, API, or predicate failure; count `null` | terminal FAIL | terminal FAIL |
| `invalid_selector` | `querySelectorAll` throws `SyntaxError`; count `null` | terminal FAIL | terminal FAIL |
| `no_match` | raw count `0` | retry until deadline | PASS |
| `all_non_rendered` | raw count `>=1`, rendered count `0` | retry until deadline | PASS |
| `unique_rendered` | raw count `1`, rendered count `1` | PASS | retry until deadline |
| `raw_multi_match` | raw count `>1`, rendered count `1`, exception absent or ineligible | terminal FAIL | terminal FAIL |
| `multiple_rendered` | rendered count `>1` | terminal FAIL | terminal FAIL |
| `unique_rendered_with_retained_zero_rect` | policy opt-in, one rendered, all extras style-visible zero-rect | PASS | retry until deadline |

For `or-visible`, both operands are probed per attempt. A terminal error or cardinality failure in
either operand is not masked by the other operand passing. Only valid non-terminal states may be
combined with OR.

Polling stays in the caller, not inside the synchronous IIFE. Reports retain the final result,
attempt count, elapsed time, effective selector/policy, match count, aggregates, and final bounded
evidence. Cardinality failures are terminal instead of being polled until a duplicate happens to
disappear; that keeps the strict mapping defect fail-loud.

### Shared executable seam

Add `compiler/lib/visibility-probe.js`, dependency-free except Node builtins, exporting:

- `buildProbeExpression(cssSelector, evidenceLimits)`;
- `unwrapEvalEnvelope(raw, transportExit)`;
- `classifyVisibility(evidence, policy)`;
- `judgeVisibility(result, assertion)`;
- `renderStandaloneSupport()`.

Add `bin/e2e-visibility-probe.js` as the thin adapter:

- `expression --selector <css>` prints the one IIFE expression;
- `judge --policy <policy> --assert visible|not-visible --transport-exit <n>` reads the
  agent-browser JSON envelope from stdin, prints one JSON result, and exits `0` for satisfied, `1`
  for retryable, or `2` for terminal failure.

Agents obtain the expression, execute it with their existing `{{browser_command}} eval ... --json`,
then send the envelope and transport status to `judge`. They never invoke bare agent-browser or
treat a failed transport as empty JSON. Codegen imports the same module and emits the expression,
envelope parser, classifier, and judgment protocol into standalone Bash/Node support; it does not
copy policy logic into `codegen.js`.

### Consumer behavior

| consumer | required behavior |
|---|---|
| mapper | probe every emitted concrete DOM selector; emit `css_selector` for non-CSS locator DSL; keep strict by default; on the exact ghost signature report a proposed `visibility_policy: retained-zero-rect` diff with evidence rather than silently widening the mapping |
| runner | use the shared CLI for visible, not-visible, enabled, and disabled pre-visibility checks; keep every expectation's structured result in the report |
| verifier | use the same classifier; prefer making a selector unique; never treat eval as a fallback/silent pass because this eval is now the declared assertion mechanism |
| walkthrough | replace the current snapshot/raw split for mapped visibility with the shared classifier; literal text observation may still use snapshots |
| compiled scripts | replace mapped `_poll_snapshot_contains`/raw `_poll_visible` with generated shared support; keep literal text snapshot assertions separate |

### When mappings must be unique

Refine the effective DOM selector when the result is `raw_multi_match` or `multiple_rendered`, or
when any extra candidate is `display:none`, `visibility:hidden`, opacity-hidden, inert/aria-hidden
for a reason other than the exact layout signature, a responsive variant, or a distinct app state.
Prefer a stable `data-testid` or stable attribute. Use `:nth-of-type(N)` only when positional
identity is genuinely part of the application contract.

Do not use `retained-zero-rect` to excuse a generally broad heading/role/tag selector. The opt-in is
eligible only after the probe shows exactly one nonzero-layout-visible candidate and every extra is
style-visible with no positive-area client rect. The mapper/verifier may propose the field but do
not auto-apply a behavioral loosening.

## Cross-vendor challenge

A fresh adversarial pass ran through `agy` with Gemini 3.1 Pro High after the Claude wrapper's auth
stop-gate was unavailable in this worker.

Accepted findings:

- non-CSS locator DSL cannot honestly be reimplemented with `querySelectorAll`; require the
  existing literal `css_selector` when such a mapping is resolved for visibility;
- malformed/missing eval envelopes need explicit `probe_error` tests;
- candidate evidence must be capped, while classification must use uncapped aggregate counts;
- the IIFE stays synchronous and caller polling owns time;
- `display:none` and `visibility:hidden` extras must disqualify the exception.

Adjudicated differently:

- recursive open-shadow-root traversal is not adopted; it changes the selector root and would not
  match current action semantics;
- `offsetWidth`/`offsetHeight` is not accepted as a `checkVisibility` fallback because it weakens
  the captain-approved predicate;
- transform/clip-path limitations are documented rather than expanded into perceptibility work;
- a third `visibility_selector` field is not added because it duplicates `css_selector` and leaves
  the same identity-equivalence problem.

The challenge's most important residual risk is retained in the pre-mortem: a mapping's
`css_selector` may not denote the same intended identity as its accessible locator.

## Acceptance criteria

**AC-1 — Hidden-first visibility no longer follows the first DOM match**

On the supported browser/runtime pair, the `[style-visible zero-area, rendered]` fixture reports
`match_count: 2`; strict policy returns `raw_multi_match`, while explicit
`retained-zero-rect` returns `unique_rendered_with_retained_zero_rect`. No path reports absence.

Verified by: a real-browser test through `bin/e2e-browser-runtime.js` using the managed Chrome for
Testing executable and supported agent-browser, plus runner, verifier, walkthrough, mapper, and
generated-script fixture invocations. The test asserts runtime/session/profile ownership evidence
before inspecting the classification. Baseline that can move the wrong way: fresh `origin/main`
returns raw `is visible h1 = false` for this exact fixture.

**AC-2 — Strict cardinality and the exception have one result algebra**

Every consumer produces the eight named result classes with the same match-count and aggregate
invariants. `retained-zero-rect` passes only with one rendered candidate and all extras
style-visible with no positive-area rect; hidden-style or second-rendered extras fail.

Verified by: table-driven tests in `compiler/test/visibility-probe.test.js` covering zero matches,
one rendered, one non-rendered, all non-rendered at count greater than one, strict ghost duplicate,
eligible opt-in duplicate, `display:none`, `visibility:hidden`, opacity zero, two rendered,
unsupported `checkVisibility`, and more candidates than the evidence cap. A drift test invokes the
CLI and generated support against the same vectors.

**AC-3 — Selector and protocol errors can never become absence**

YAML/parser errors, unsupported mapping locator shape, invalid policy, invalid CSS, browser command
failure, malformed JSON, missing result fields, and predicate failure remain explicit terminal
failures. `probe_error` and `invalid_selector` carry `match_count: null` and cannot satisfy a
negative assertion.

Verified by: compiler/dry-run fixtures for invalid mapping metadata; CLI tests with `[` and hostile
quoted selectors; fake-browser tests for nonzero transport, empty output, malformed/duplicate JSON
fields, and valid `no_match`; and a real-browser invalid-CSS case proving raw `false` is replaced by
`invalid_selector` with sanitized `SyntaxError` evidence.

**AC-4 — Non-CSS mapping locators have an explicit DOM identity**

A resolved `role=`/`text=`/other non-CSS mapped visibility assertion without `css_selector` fails
before browser startup and names mapping, page, element, and remediation. With `css_selector`, the
resolver carries selector, effective DOM selector, and policy through single-site, multi-site,
legacy `is visible`, positive, negative, enabled/disabled, parameterized, and OR forms.

Verified by: resolver and real compiler/dry-run fixtures for each expect shape, including an
agent-browser spawn counter that remains zero on the missing-`css_selector` case. Falsifier: drop
`cssSelector` or `visibilityPolicy` in any resolver branch and its shape-specific test goes red.

**AC-5 — All five consumers use the shared seam**

Runner, mapper, verifier, walkthrough, and compiled scripts no longer use raw scalar visibility or
snapshot substring matching for mapped element visibility. Each reports result class, effective
policy, match count, attempt count, and bounded evidence; literal text assertions remain explicitly
separate.

Verified by: agent/skill contract tests that require the CLI protocol and reject raw mapped
`is visible`/snapshot instructions; a codegen test showing mapped visibility imports/emits shared
support; and an executable five-consumer fixture matrix. The bounded claim is that the shipped
consumer instructions and generated code point to one classifier, not that a future copy is
impossible.

**AC-6 — Positive, negative, and OR polling preserve terminal failures**

Positive assertions retry only `no_match` and `all_non_rendered`; negative assertions pass those
two, retry a well-formed visible singleton/eligible exception, and never pass an error or
multi-match. OR cannot mask one operand's invalid selector, probe error, or cardinality failure.

Verified by: fake-clock tests over the full judgment matrix, including state transitions before a
deadline and terminal-first cases that assert one attempt and no sleep. Reports retain final
evidence plus attempts and elapsed time.

**AC-7 — Standalone compiled behavior matches the agent-facing CLI**

Generated Bash scripts classify the same fixtures and exit with the same pass/retry/terminal
meaning as `bin/e2e-visibility-probe.js`, including named sessions and hostile selector quoting.

Verified by: compile a fixture flow, execute the emitted script with a fake browser envelope matrix,
then run the hidden-first and invalid-CSS cases against the owned real browser runtime. A source
drift test perturbs the shared classifier in a scratch copy and proves both CLI and generated output
change together. Full `npm test`, `npm run lint`, and `git diff --check` remain green.

**AC-8 — Published guidance teaches uniqueness instead of policy escape**

The selector authority and user-facing testing/CI docs state the strict default, exact exception,
non-CSS `css_selector` requirement, result diagnostics, negative behavior, and when to make a
mapping unique.

Verified by: documentation contract tests plus a doc-probe that compiles/runs the published YAML
examples. Validation compares the reviewed before/after wording below with the landed diff.

## Test plan

1. RED first in `visibility-probe.test.js` for the result algebra, invalid CSS, predicate failure,
   uncapped classification/capped evidence, sanitization, and exact exception.
2. RED resolver/compiler tests for metadata enum, non-CSS-without-CSS refusal, every expect shape,
   parameter substitution, OR, multi-site, and zero browser spawns.
3. RED codegen runtime tests for positive/negative/OR exit semantics, transport/envelope failures,
   session routing, shell quoting, and literal-text separation.
4. RED contract tests for mapper, runner, verifier, walkthrough, shared report fields, and mapper
   proposal-not-auto-opt-in behavior.
5. GREEN the shared module/CLI, then resolver, then generated support, then the four instruction
   consumers; each dispatch owns a complete RED-to-GREEN loop.
6. Run the real owned-browser matrix against current supported agent-browser and managed Chrome:
   no match, all non-rendered, singleton rendered, hidden-first ghost duplicate under both policies,
   hidden-style extra, two rendered, invalid CSS.
7. Run focused compiler/contract suites, then full `npm test`, `npm run lint`,
   `scripts/version-parity-check.sh`, `scripts/marketplace-verify.sh`, and `git diff --check`.

E2E-first acceptance is required, not skipped: AC-1 and AC-7 exercise the generated and
agent-facing flows through the real owned browser runtime.

## Doc diff

| surface | before | after |
|---|---|---|
| `e2e-pipeline/CLAUDE.md` Selector Priority | `css_selector` is needed for certain click/fill paths; visibility may translate to snapshot text | `css_selector` is also the effective DOM identity for non-CSS mapped visibility; strict count is default; only `retained-zero-rect` may opt in |
| `references/common-patterns.md` | “snapshot vs is visible” chooses between a11y substring and scalar DOM boolean | mapped visibility always uses the shared result algebra; snapshots remain corroboration/literal-text evidence |
| `references/commands.md` | raw `is visible` returns text `true`/`false` | raw behavior is diagnostic only; product assertions use `e2e-visibility-probe` and preserve invalid-selector/probe errors |
| `docs/writing-tests.md` | visible/not-visible grammar has no cardinality or mapping metadata rule | document strict default, YAML policy example, non-CSS `css_selector` requirement, and negative semantics |
| `docs/ci-integration.md` and `skills/e2e-compile/SKILL.md` | compiled visibility uses `_poll_snapshot_contains`; CI table treats raw visibility as the fallback | compiled mapped visibility embeds the shared DOM classifier; describe result fields and migration failure |
| mapper/runner/verifier/walkthrough contracts | snapshot/raw scalar split | one CLI protocol, reports, unique-mapping guidance, and proposal-only exception behavior |

Implementation applies these wording changes with behavior; validation verifies both landed
together. Historical plan documents are not rewritten.

## Appetite and stop condition

- **Ideation-declared estimate:** 16 working hours through implementation plus focused validation.
- **Declared tolerance:** 22 working hours (+37.5%).
- **Stop condition:** if the shared eval-envelope/classifier plus standalone parity is not green
  within the first 5 hours, or total work reaches 22 hours, park with committed RED evidence and a
  re-enterable seam. Do not cut a consumer or compress real-browser/full-suite validation.

The estimate is above 90 minutes and spans three independent behavior boundaries, so implementation
uses three sequential worker sessions rather than one oversized dispatch:

1. shared probe/CLI, mapping validation, and result-algebra RED-to-GREEN;
2. resolver/codegen/standalone positive-negative-OR RED-to-GREEN;
3. mapper, runner, verifier, walkthrough, reports, docs, and contract RED-to-GREEN.

They are sequential because sessions 2 and 3 consume session 1's API. Parallel work would create
shared-file and semantic contention rather than useful wall-clock savings.

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a **hidden assumption**:
the mapping's `css_selector` names a different DOM candidate set than its accessible `selector`, so
the classifier is deterministic about the wrong identity.

Mitigation in scope: the mapper probes every emitted effective DOM selector, reports both locator
forms and candidate identity evidence, and prefers a unique test ID. The system does not claim it
can prove computed-accessible-name equivalence from DOM CSS alone.

## Out of scope

- changing agent-browser upstream or raising the supported minimum solely for this issue;
- application-specific RNW duplicate cleanup;
- computed accessible-name reimplementation inside the plugin;
- Shadow DOM or cross-frame aggregation;
- viewport intersection, occlusion, hit-testing, or true user perceptibility/actionability;
- automatic application of `retained-zero-rect` by mapper or verifier;
- rewriting historical plans, issue mutation, release/version work, or sprint membership changes;
- generated-output hardening tracked separately by #39.

## Stage Report: ideation

- DONE: Reproduced the hidden-first/visible-later and invalid-CSS collapse against fresh
  `origin/main`, the supported `agent-browser 0.32.0`, and managed Chrome for Testing 151 through
  the owned runtime; cleanup removed only the flow-managed profile.
- DONE: Reverse-recovered upstream first-match behavior, selector policy/translation, mapping
  resolver, compiler, runner, mapper, verifier, walkthrough, generated scripts, reporting, and
  live branch-protection context with file:line evidence.
- DONE: Chose strict raw cardinality plus the exact `retained-zero-rect` opt-in, defined the
  current-document render predicate, eight-result algebra, positive/negative/OR polling,
  fail-loud error behavior, bounded diagnostics, and unique-mapping guidance.
- DONE: Located ownership in one dependency-free module plus CLI/codegen adapters and priced the
  compatibility requirement that non-CSS mapped visibility must carry `css_selector`.
- DONE: Recorded value/mechanism ACs, real-browser and standalone proof, appetite/tolerance,
  three behavior-complete dispatches, doc before/after changes, design determination, one-sentence
  pre-mortem, and explicit out-of-scope boundaries.
- DONE: Ran a fresh Gemini cross-vendor challenge, adopted the non-CSS/envelope/evidence findings,
  and recorded why Shadow DOM piercing, predicate fallback, and a third selector field are not
  taken.
- DONE: `spacedock status --read deterministic-multi-match-visibility-semantics --ac-scan`
  resolves AC-1 through AC-8. `unevidenced=true` is expected at ideation; the planned external
  proofs are named under each AC.

### Summary

Reproduced hidden-first/visible-later and invalid-selector collapse on the current supported
agent-browser/runtime, recovered all five consumers and upstream capabilities from fresh
`origin/main`, accepted the captain's strict-plus-one-exception contract, and located ownership in
one shared DOM probe/classifier with a CLI and codegen adapter. The design prices the non-CSS
locator compatibility migration, defines the complete result/polling/report algebra, records exact
ACs and doc changes, and includes a fresh Gemini cross-vendor challenge with adjudication.

### Gate handoff

- taking the cheap path: reuse existing owned eval, `css_selector`, and Node support around one
  shared module;
- no scope cut: all five consumers remain required;
- design: required;
- spike: passed on `origin/main` `0a1079c`, agent-browser `0.32.0`, Chrome for Testing
  `151.0.7922.47`;
- primary residual risk: accessible locator and DOM selector identity can diverge;
- implementation dispatch: three sequential behavior-complete RED-to-GREEN sessions.

## Stage Report: implementation

- DONE: Added the dependency-free shared visibility probe/CLI, parser policy validation, exact
  eight-result algebra, bounded evidence, sanitized errors, and fail-loud protocol handling in
  commit `68491ba` (`feat(e2e-pipeline): add deterministic visibility probe`).
- DONE: Slice 1 closed RED to GREEN, including a missing-protocol-field falsifier that initially
  misclassified malformed evidence as `no_match`; the focused suite finished 52/52 green.
- DONE: Threaded effective DOM identity and policy through resolver, compiler, single/multi-site,
  legacy, parameterized, enabled/disabled, positive/negative, and OR forms in commit `9e2d18e`
  (`feat(e2e-pipeline): compile deterministic visibility semantics`).
- DONE: Generated scripts embed the shared standalone support, preserve named sessions and hostile
  selector quoting, record both OR operands, stop terminal failures without sleeping, and add
  `visibility_results` only when mapped visibility is present.
- DONE: Slice 2 closed RED to GREEN, including a built-in dialog CSS falsifier; its full suite was
  1,004 passed, 0 failed, 1 skipped.
- DONE: Routed mapper, runner, verifier, walkthrough, and compiled scripts through the shared seam;
  updated reports, selector authority, commands, patterns, testing, CI, and compile guidance in
  checkpoint commit `0b8ff269565178162bf094256c89a4718b0bc681`.
- DONE: Mapper guidance probes every concrete DOM selector, keeps strict as default, proposes but
  never auto-applies the exact exception, reports both locator forms, and does not claim computed
  accessible-name equivalence from DOM evidence.
- DONE: Consumer shell recipes preserve judge exit 0/1/2 under `set -e`; a new contract test was
  observed RED for unsafe capture/equivalence wording and GREEN after the correction.
- DONE: Slice 3 focused result was 6 passed, 0 failed, 1 real-browser skip; the executable
  five-consumer matrix, generated metrics, and published YAML compile/run example all passed.
- DONE: Fresh full `npm test` finished 1,010 passed, 0 failed, 2 real-browser skips in 117.3s.
- DONE: `npm run lint` exited 0 with the existing 214 warnings and 2 infos; `git diff --check`,
  `scripts/version-parity-check.sh`, and `scripts/marketplace-verify.sh` all passed.
- FAILED: Owned real-browser attempt 1 used a fresh test-owned app/run/profile but failed on its
  first `open` after 158.0s: `Resource temporarily unavailable (os error 35)` after five retries.
- FAILED: One bounded retry with a second fresh app/run/profile failed at the same first-open
  boundary after 157.3s; neither attempt reached receipt assertions or selector classification.
- DONE: Both failed attempts cleaned their unique test-owned state; unrelated agent-browser
  namespaces/processes/profiles were identified and left untouched.
- FAILED: AC-1 is FAILED/UNPROVEN because hidden-first strict/exception behavior did not execute
  through the supported owned real-browser/runtime pair in this stage.
- DONE: AC-2, AC-3, AC-4, AC-5, AC-6, and AC-8 have focused executable, compiler, consumer,
  reporting, documentation, and full-suite evidence on the committed head.
- FAILED: AC-7 is FAILED/UNPROVEN because CLI/generated parity passed fake-envelope fixtures but
  the required owned real-browser hidden-first and invalid-CSS cases never ran past startup.
- FAILED: The third completion-checklist item is incomplete at its real-browser boundary; no
  runtime residual is waived or accepted, and implementation is not marked complete.

### Summary

Three sequential RED-to-GREEN slices produced a clean, re-enterable implementation checkpoint at
`0b8ff269565178162bf094256c89a4718b0bc681`. Shared algebra, resolver/codegen parity, all five
consumers, reports, docs, focused tests, full tests, lint, parity, installability, and diff checks
are green. Implementation remains parked because two isolated owned-runtime attempts failed before
navigation/classification with OS error 35, leaving AC-1 and AC-7 FAILED/UNPROVEN.

## Stage Report: implementation (cycle 2)

- DONE: Diagnosed the prior `Resource temporarily unavailable (os error 35)` boundary as
  `spawnSync` starving the test-owned HTTP server's Node event loop while runtime navigation waited.
- DONE: Replaced the real harness's synchronous child execution with bounded async `spawn` while
  preserving piped stdin/stdout/stderr and explicit runtime timeout behavior.
- DONE: Closed each successive harness boundary without weakening ownership: injected the mapping
  app, stopped reusing the generated script's closed receipt, added generated navigation, isolated
  app/run/profile/receipt/artifact roots per invocation, and shortened only socket-budget app IDs.
- DONE: The final real CLI matrix exercised no-match, all-non-rendered, singleton, strict ghost,
  retained ghost, hidden-style duplicate, two-rendered, and invalid CSS on one verified owned binding.
- DONE: The final generated ghost flow navigated on its own fresh binding and reported
  `unique_rendered_with_retained_zero_rect`, `match_count: 2`, satisfied judgment, and exit 0.
- DONE: The final generated negative invalid-CSS flow navigated on a second fresh binding and
  reported `invalid_selector`, `match_count: null`, terminal judgment, and overall script exit 1.
- DONE: Every generated case asserted `initial_reused: false`, verified first navigation, exact
  app/run/session/profile identity, and a closed receipt with `owned-session-closed` cleanup.
- DONE: Rebased cleanly onto `origin/main` `844f36a`; the exact implementation commits are
  `d5b9946`, `13b9a8c`, `050da81`, and harness correction `4d63675` across the reviewed 25-file scope.
- DONE: Fresh post-rebase owned real-browser proof finished 2 passed, 0 failed; changing ghost
  cardinality, collapsing invalid CSS, reusing a receipt, or losing navigation ownership makes it red.
- DONE: Fresh focused visibility proof finished 60 passed, 0 failed, 1 gated real-browser skip;
  resolver, classifier, generated support, consumer contracts, metrics, and published examples are covered.
- DONE: Fresh full `npm test` finished 1,025 passed, 0 failed, 2 intentional real-browser skips;
  `npm run lint` exited 0 with 215 warnings and 2 infos and applied no fixes.
- DONE: `git diff --check origin/main...HEAD`, version parity, marketplace schema, and isolated
  installability for all seven plugins passed on the rebased head.
- DONE: Pushed the feature branch normally without force; no PR, version mutation, or validation
  stage advancement was performed.
- DONE: AC-1 is PASS: strict hidden-first returns `raw_multi_match`, explicit retained policy
  returns `unique_rendered_with_retained_zero_rect`, and neither path reports absence in the real runtime.
- DONE: AC-7 is PASS: agent-facing CLI and independently owned generated Bash agree on retained
  ghost success and invalid-CSS terminal failure against the supported real browser/runtime pair.
- DONE: The prior implementation report's failed real-runtime evidence is superseded by this fresh
  post-rebase proof; all ACs now have implementation evidence and implementation is complete.

### Summary

The earlier failures were harness lifecycle defects, not a product-classifier failure: synchronous
children starved the local server, then shared app/receipt assumptions violated normal generated-flow
ownership. Fresh isolated CLI and generated browser runs now prove AC-1 and AC-7 on the rebased four-
commit head, all required gates are green, and implementation is complete pending separate validation.
