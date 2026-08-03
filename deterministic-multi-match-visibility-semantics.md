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
pr: pr-merge:pending:artifact-v1:8965c2c319d9a4f6722de169a7b202bdc28a9d46e3e489ca6e7d4533b59553c6
design: required
lane: main
id: d3mmhwzpdye4mtg6yc0jvmdz
pr_artifact_v1: eyJhdWRpdF9saW5rIjoiW2QzXSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvYjM0NDZlZTcwOTllMTRmY2ZiYTczOWM1MWQzZGMyMDliZmQ4YjVmNi9kZXRlcm1pbmlzdGljLW11bHRpLW1hdGNoLXZpc2liaWxpdHktc2VtYW50aWNzLm1kKSIsImJhc2UiOiJtYWluIiwiYmFzZV9vaWQiOiI4NDRmMzZhNTNiYzcwOTRiNzQ0NzZiM2U1N2NiNDdjNzBkNjlkNWRkIiwiYm9keSI6Ik1ha2UgdmlzaWJpbGl0eSBjaGVja3MgZGV0ZXJtaW5pc3RpYyB3aGVuIGhpZGRlbiBvciB6ZXJvLWFyZWEgRE9NIG1hdGNoZXMgcHJlY2VkZSB0aGUgcmVuZGVyZWQgZWxlbWVudCwgd2l0aG91dCBhbGxvd2luZyBhbWJpZ3VvdXMgc2VsZWN0b3JzIHRvIHBhc3MuXG5cbiMjIFdoYXQgY2hhbmdlZFxuXG4tIERlZmluZSBzaGFyZWQgdmlzaWJpbGl0eSByZXN1bHQgY2xhc3NlcywgYm91bmRlZCBldmlkZW5jZSwgYW5kIHN0cmljdCBjYXJkaW5hbGl0eS5cbi0gQWRkIHRoZSByZXRhaW5lZC16ZXJvLXJlY3QgcG9saWN5IGFuZCBDU1MgaWRlbnRpdHkgdmFsaWRhdGlvbi5cbi0gUm91dGUgY29tcGlsZXIsIGdlbmVyYXRlZCBzY3JpcHRzLCBtYXBwZXIsIHJ1bm5lciwgdmVyaWZpZXIsIGFuZCB3YWxrdGhyb3VnaCB0aHJvdWdoIG9uZSBwcm90b2NvbC5cbi0gQ291cGxlIGVuYWJsZWQgYW5kIGRpc2FibGVkIHN0YXRlIHRvIHRoZSBzZWxlY3RlZCByZW5kZXJlZCBjYW5kaWRhdGUuXG5cbiMjIEV2aWRlbmNlXG5cbi0gRnVsbCBzdWl0ZTogMSwwNDAvMSwwNDAgcnVubmFibGUgdGVzdHMgcGFzc2VkOyAyIGludGVudGlvbmFsIGJyb3dzZXIgc2tpcHMuXG4tIE93bmVkIGJyb3dzZXIvcnVudGltZSBtYXRyaXg6IDIvMiBwYXNzZWQ7IGV4ZWN1dGFibGUgZGlmZiBjb3ZlcmFnZSByZWFjaGVkIDg4LjE3JS5cblxuLS0tXG5bZDNdKC9pYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMvYmxvYi9iMzQ0NmVlNzA5OWUxNGZjZmJhNzM5YzUxZDNkYzIwOWJmZDhiNWY2L2RldGVybWluaXN0aWMtbXVsdGktbWF0Y2gtdmlzaWJpbGl0eS1zZW1hbnRpY3MubWQpXG5DbG9zZXMgIzkxXG4iLCJib2R5X3NoYTI1NiI6ImM4NzdjYTgwOWM2NjUzOTdmZDBiOTA2N2I2MDMzZGRiODZkZDg1YzdkYTMwMDUyM2I5Y2FmOTQyM2VmZTYyYjMiLCJkaWZmX3NoYTI1NiI6ImQ1ZGI4MzI2MTI5MGFhZWVjMmIzYzZjZWU4OWU1ZjMwZTI2YjZmNjE4ZDg5NjM1NzhkZTA4YTNhNzcwZDMzNTEiLCJoZWFkIjoic3BhY2Vkb2NrLWVuc2lnbi9kZXRlcm1pbmlzdGljLW11bHRpLW1hdGNoLXZpc2liaWxpdHktc2VtYW50aWNzIiwiaGVhZF9vaWQiOiJmMGQ4YjVjZWRlMTViN2U5M2FjOTIyYzMyMjI5YzhjOTM5NmRmNDBiIiwibGl2ZV9wYXRoIjoiZGV0ZXJtaW5pc3RpYy1tdWx0aS1tYXRjaC12aXNpYmlsaXR5LXNlbWFudGljcy5tZCIsInJlcG8iOiJpYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMiLCJ0aXRsZSI6ImZlYXQoZTJlLXBpcGVsaW5lKTogZGVmaW5lIGRldGVybWluaXN0aWMgdmlzaWJpbGl0eSBzZW1hbnRpY3MgKCM5MSkifQ
mod-block: pr-merge:product-pr:v1:8965c2c319d9a4f6722de169a7b202bdc28a9d46e3e489ca6e7d4533b59553c6
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

### Feedback Cycles

- Cycle 3: REJECTED — cycle-3 Science Officer/EM gate; surface 0.78h corrections vs
  16h estimate (4.9%); AC unchanged

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

## Stage Report: validation

TL;DR: **REJECTED.** Exact-head focused, full-suite, lint, marketplace, and the filed
visible/not-visible real-browser matrix are green, but fresh validation found two material AC-5
defects and a red 81.01% executable diff-coverage result. In particular, generated enabled/disabled
assertions leave the shared classifier after it selects the one rendered retained-zero-rect
candidate and then ask raw `agent-browser is enabled` about the first DOM match. An owned browser
falsifier with a disabled zero-rect first button and enabled rendered second button therefore
classified visibility as satisfied but exited 1 as “not enabled.” The claimed five-consumer test
also grades instruction wording rather than exercising those consumers, contrary to this
workflow's proof policy. No red residual is waived.

### Exact surface and scope

- Validated only worktree
  `.worktrees/spacedock-ensign-deterministic-multi-match-visibility-semantics`, branch
  `spacedock-ensign/deterministic-multi-match-visibility-semantics`, exact clean head
  `4d6367500212011dcda51e75d11246fa3e3a92ba`.
- `origin/main`, the dispatched base, and merge-base all resolved to
  `844f36a53bc7094b74476b3e57cb47c70d69d5dd`.
- Diff measurement: 25 files, 2,885 insertions, 178 deletions; all 25 map to an AC:
  - AC-1/2/3/6/7 probe and protocol: `bin/e2e-visibility-probe.js`,
    `compiler/lib/visibility-probe.js`, `compiler/test/visibility-probe.test.js`.
  - AC-3/4 metadata and fail-before-browser resolution: `compiler/parser.js`,
    `compiler/compiler.js`, `compiler/resolver.js`, `compiler/test/cli.test.js`,
    `compiler/test/integration.test.js`, `compiler/test/resolver.test.js`,
    `compiler/test/visibility-policy-metadata.test.js`.
  - AC-1/3/4/5/6/7 generated behavior and runtime proof: `compiler/codegen.js`,
    `compiler/test/visibility-browser-runtime-real.test.js`,
    `compiler/test/visibility-consumer-contract.test.js`,
    `compiler/test/visibility-resolver-codegen.test.js`.
  - AC-5 consumer contracts: `agents/e2e-test-runner.md`, `agents/e2e-mapper.md`,
    `agents/e2e-flow-verifier.md`, `skills/e2e-walkthrough/SKILL.md`,
    `skills/e2e-walkthrough/reference.md`.
  - AC-5/8 published contracts and examples: `CLAUDE.md`, `docs/ci-integration.md`,
    `docs/writing-tests.md`, `references/commands.md`, `references/common-patterns.md`,
    `skills/e2e-compile/SKILL.md`.
- Unmapped files: zero.

### Findings

1. **P1 — retained-zero-rect enabled/disabled checks inspect the wrong candidate.**
   `e2e-pipeline/compiler/codegen.js:524-549` first accepts deterministic positive visibility,
   then lines 540-543 run raw `agent-browser is enabled "$selector"`. For a selector whose first
   match is a retained zero-rect disabled button and whose second match is the one rendered enabled
   button, the classifier correctly returns
   `unique_rendered_with_retained_zero_rect`, but the state command reads the first match. A fresh
   owned-runtime scratch fixture reproduced generated-script exit 1 and `target not enabled after
   1s`; the a11y diagnostic showed disabled ref `e1` followed by enabled ref `e2`. Cleanup closed
   and removed only the randomized test-owned app/run/profile/receipt roots.
2. **P1 — enabled/disabled state is sampled once instead of polled for the declared timeout.**
   The same `codegen.js:524-549` path spends the timeout only in `_poll_visibility`, then makes one
   `is enabled` call. A control that is already visible but changes disabled/enabled state during
   the remaining wait budget returns 1 immediately. The independent reviewer found the same call
   path; citation and control flow are correct.
3. **P2 — AC-5's five-consumer proof is not exercise-based.**
   `compiler/test/visibility-consumer-contract.test.js:102-145` asserts regexes over the four
   instruction files. That is the committed prose-grep shape Proof Policy rule 1 bans as behavioral
   evidence. Lines 147-163 then loop over consumer labels but execute the same CLI each time without
   reading or invoking mapper, runner, verifier, or walkthrough behavior. The test can remain green
   while a consumer ignores the documented recipe, so it cannot close AC-5 or the correctness lens.
4. **Coverage gate is red.** Full-suite V8 output converted through c8/LCOV and intersected with
   exact added/changed lines measured 866/1,069 = **81.01%**, below the required 85% bar. Per-file
   results were CLI 54/73, codegen 305/305, compiler 4/4, shared probe 309/472, parser 20/22, and
   resolver 174/193. The browser IIFE is exercised by the real E2E after stringification in Chrome,
   but Node V8 cannot attribute that execution back to its source lines; the workflow provides no
   waiver for that instrumentation boundary, so the raw measured result remains red.

### Per-AC verdict

- **AC-1 PASS:** `E2E_REAL_VISIBILITY=1 node --test
  compiler/test/visibility-browser-runtime-real.test.js` finished 2 passed, 0 failed. Strict
  hidden-first returned `raw_multi_match`; explicit retained policy returned
  `unique_rendered_with_retained_zero_rect`; neither returned absence.
- **AC-2 PASS:** focused classifier/CLI/resolver/consumer suites finished 59 passed, 0 failed and
  covered the eight result classes, hidden-style disqualification, second rendered candidate,
  inconsistent aggregates, and capped evidence.
- **AC-3 PASS:** focused fake-envelope and real invalid-CSS cases retained
  `invalid_selector`, `match_count: null`, terminal negative judgment, and nonzero exit.
- **AC-4 PASS:** resolver/compiler fixtures carried CSS identity and policy through single-site,
  multi-site, legacy, parameterized, positive, negative, enabled/disabled, and OR forms; missing
  non-CSS `css_selector` failed before output/browser startup.
- **AC-5 FAIL:** findings 1-3. The generated enabled/disabled seam is not deterministic for the
  approved multi-match exception, and four prose consumers lack independent exercise-based proof.
- **AC-6 PASS:** focused generated positive, negative, and OR matrices preserved retryable versus
  terminal exit meanings; terminal OR operand stopped after one attempt and was not masked.
- **AC-7 PASS for the criterion's visible/not-visible fixtures:** the owned real CLI/generated
  retained-ghost and invalid-CSS cases agreed. This does not cure AC-5's enabled/disabled defect.
- **AC-8 PASS:** the published YAML example parsed, compiled, and executed through generated
  support; the reviewed docs state strict default, exact exception, CSS identity migration,
  diagnostics, negative behavior, and uniqueness guidance.

### Required evidence block

Lenses: correctness **FAIL, 3 findings**; silent-failure **PASS, 0 findings**; type-design **PASS,
0 findings**; concurrency **PASS, 0 findings**; resource-lifecycle **PASS, 0 findings**;
manifest/back-compat **PASS, 0 findings**. Security did not fire: no auth, permission, trust-boundary,
secret-bearing workflow, or shell hook changed.
Diff coverage: **FAIL — 866/1,069 changed executable lines = 81.01%** from full-suite
NODE_V8_COVERAGE → c8 LCOV intersection; required bar is 85%.
Adversarial: strict-cardinality mutation (`match_count === 1` → `>= 1`) made 5 probe tests red;
invalid-CSS-to-`no_match` mutation made 1 probe test red; disabled-first/enabled-second retained
candidate fixture made the owned generated E2E red with exit 1.
Cross-model: preferred Claude Opus/high tool-less diff attempts timed out sleeping at 6m30s and
5m22s after an `AUTH_MISSING` preflight; only owned PIDs were terminated. One bounded fallback
requested `gemini-3.1-pro-high`/high and succeeded in 168.998s, conversation
`27a21e80-1fb2-4163-ab97-a2ec85120f0c`; agy reported **Gemini 3.6 Flash (High)** / High. One
accepted finding (enabled state is not polled); three findings declined after citation checks as
unreachable infrastructure-only stale reporting, outside the specified CLI contract, and an
intentional prose placeholder.
E2E: expected real matrix **PASS 2/2** in 21.35s with fresh owned namespaces; claim-breaking
disabled-first/enabled-second retained fixture **FAIL as falsifier**, generated exit 1 after
classifier success; all owned state cleaned, unrelated browser/profile/session state preserved.

### Other exit evidence

- Fresh full `npm test`: 1,025 passed, 0 failed, 2 intentional real-browser skips in 126.04s.
- `npm run lint`: exit 0, 215 warnings and 2 infos, no fixes applied.
- `git diff --check`: exit 0.
- `scripts/version-parity-check.sh`: all seven plugins consistent.
- `scripts/marketplace-verify.sh`: L0 parity, L1 schema, and isolated L2 installability for all
  seven plugins passed.
- `scripts/skill-frontmatter-lint.sh`: 38 skill directories passed.

### Return to implementation

- Make enabled/disabled state judgment operate on the same uniquely rendered candidate selected
  by the shared probe, and poll the state transition within the declared timeout without reverting
  to first-match scalar semantics.
- Replace prose-regex grading with an exercise that can fail when mapper, runner, verifier, or
  walkthrough behavior ignores the protocol; do not relabel repeated CLI calls as four consumer
  executions.
- Raise measured executable diff coverage to at least 85% with a tool/reporting shape that honestly
  accounts for browser-executed source, then rerun the exact owned real matrix and falsifiers.

### Summary

Fresh validation reproduced the filed visibility fix and its invalid-selector behavior, but found
that enabled/disabled assertions leave the deterministic candidate seam and regress to first-match
state inspection, while their timeout does not poll state. The consumer proof is prose grading, and
raw changed-line coverage is 81.01%. The validation gate is therefore REJECTED and returns to
implementation with no residual waived.

## Stage Report: implementation — correction round 1

TL;DR: **IMPLEMENTATION CORRECTION COMPLETE.** Exact product head
`1d5e6c90ce44e1ba3d07302b1da59240445846aa` closes all four validation-return items without
changing issue, version, PR, ruleset, or stage authority. Enabled/disabled are now first-class
shared judgments over the same rendered candidate selected by the atomic probe, valid state
mismatches retry inside the declared timeout, the four instruction consumers execute their own
committed Bash recipes in tests, and honest exact-head executable diff coverage is 88.06%. The
branch is normally pushed; status remains `implementation` pending fresh validation.

### Authority, scope, and effort

- Re-entered the existing isolated product worktree at dispatched head `4d636750` and the durable
  state checkout at `837d361`; re-read issue #91 plus the full entity/AC/report before editing.
- Audited both directions across all 25 pre-existing changed files: every issue/AC clause has an
  implementation, test, consumer, or documentation owner, and every changed file maps back to
  AC-1 through AC-8. No unrelated file or second feature lane was admitted.
- Correction round started `2026-08-02T18:29:47Z` and finished product push verification at
  `2026-08-02T18:57:55Z`: **28m08s (0.47 working hours)**. This is 2.9% of the 16h estimate and
  2.1% of the 22h tolerance; neither the 5h seam stop condition nor the 22h park condition fired.

### RED to GREEN correction evidence

- RED: the focused 60-test boundary initially finished 53 passed / 7 failed. Failures reproduced
  unsupported shared enabled/disabled assertions, missing selected-candidate state, raw first-match
  `is enabled`, and one-shot state sampling instead of delayed-transition polling.
- GREEN: `compiler/lib/visibility-probe.js` now emits bounded `rendered_candidate` state from the
  uniquely nonzero-layout-visible candidate. Native `:disabled` and ancestor `aria-disabled=true`
  are inspected by one shared `inspectCandidate` implementation that is both directly executable
  under Node coverage and embedded verbatim into browser expressions.
- GREEN: generated `_poll_enabled_state` delegates every attempt to the same atomic visibility/state
  judgment. `no_match`, `all_non_rendered`, and valid state mismatch remain retryable; invalid CSS,
  transport/envelope/probe failure, and cardinality failure remain terminal without sleeping.
- GREEN: the final focused boundary finished 64 passed / 0 failed. Strict singleton, retained
  duplicate, terminal cardinality, invalid CSS, positive, negative, OR, session, quoting, report,
  and generated-support parity regressions remain green.
- GREEN: `visibility-consumer-contract.test.js` no longer grades prose regexes or relabels repeated
  CLI calls. It extracts and executes the actual mapper, runner, verifier, and walkthrough Bash
  recipes with real exit/result/report assertions; compiled generated scripts are exercised
  separately through their generated support.

### Exact-head gates and disposition

- Commits: `fb2144e` (`fix(e2e-pipeline): couple control state to rendered candidate`) and
  `1d5e6c9` (`test(e2e-pipeline): keep visibility harness lint-clean`). Remote branch head was
  read back as exact `1d5e6c90ce44e1ba3d07302b1da59240445846aa` after a normal, non-force push.
- Required owned real browser: **2 passed / 0 failed** in 40.56s on exact final head. The matrix
  retains no-match, all-non-rendered, singleton, strict/retained ghost, hidden-style extra,
  two-rendered, invalid CSS, disabled-first/enabled-second retained state, and delayed enabled and
  disabled transitions. Delayed cases require at least two atomic attempts and report candidate
  index 1 with the final expected state; all test-owned sessions/profiles/artifacts are cleaned.
- Exact-head full `npm test`: **1,033 passed / 0 failed / 2 intentional real-browser skips** in
  126.59s.
- Honest exact-head executable diff coverage from full-suite `NODE_V8_COVERAGE` through c8/LCOV,
  intersected with exact committed changed lines: CLI 70/73; codegen 289/289; compiler 4/4;
  shared probe 424/533; parser 20/22; resolver 174/193; **total 981/1,114 = 88.06% PASS**.
  No files, branches, or browser source were excluded, relabelled, or waived.
- `npm run lint`: exit 0 with the pre-existing 215 warnings and 2 infos; no fixes applied.
  `git diff --check origin/main...HEAD`, version parity, release-path/JSONPath checks, plugin
  directory enumeration, skill frontmatter lint, marketplace schema, and isolated installation of
  all seven plugins passed.
- AC-5 implementation evidence is now green and the prior correction findings have no known red
  residual. Fresh validation remains a separate gate; this report does not advance the entity,
  create a PR, mutate version/release metadata, or change issue/ruleset state.

## Stage Report: validation — cycle 2

TL;DR: **REJECTED.** Fresh validation on exact clean product head
`1d5e6c90ce44e1ba3d07302b1da59240445846aa` against exact base
`844f36a53bc7094b74476b3e57cb47c70d69d5dd` closed all four findings returned by validation
cycle 1, passed the owned runtime matrix, passed the full suite, and measured honest executable
diff coverage at 88.06%. It also reproduced one new boundary failure: accepted `wait: 0` mapped
visibility assertions execute zero probe attempts, emit no final visibility evidence, throw a JSON
parse error, and are reported as probe infrastructure failure. This falsifies AC-6's final-evidence
and terminal-distinction contract. Because this is validation cycle 2, the rejection requires
captain escalation; validation has no authority to waive, correct, advance, or start another round.

### Exact authority and scope

- Re-read the full current `docs/dev/README.md`, root and plugin instructions, issue #91 including
  the captain-approved contract, the validation stage definition, the complete entity through
  state head `4308ed474580b8b670e20287b8640c3f79447e99`, and the exact product diff. The product worktree
  began and ended clean on the dispatched head. No product, issue, PR, version, marketplace,
  ruleset, or stage-status surface was edited.
- Audited all 25 changed files in both directions; none is unrelated and none is missing an AC
  owner. Runtime/classifier/compiler files (`bin/e2e-visibility-probe.js`, `compiler/codegen.js`,
  `compiler/compiler.js`, `compiler/lib/visibility-probe.js`, `compiler/parser.js`, and
  `compiler/resolver.js`) map to AC-1 through AC-7. The eight compiler test files map to AC-1
  through AC-7 and the correction falsifiers. `CLAUDE.md`, the three agents, two walkthrough
  files, compile skill, four docs/references, and the consumer-contract test map to AC-5 and AC-8.
  The writing example also maps to the compiled AC-8 exercise. **25/25 mapped; zero scope drift.**

### Cycle-1 blocker re-falsification

1. **Rendered-candidate identity is closed.** Focused and owned-runtime cases select the enabled
   or disabled state from the same uniquely rendered candidate. The disabled first zero-rect node
   cannot override the enabled second rendered candidate, and delayed enabled/disabled transitions
   require at least two atomic attempts while retaining candidate index 1.
2. **Enabled/disabled polling is closed for positive timeout budgets.** The owned real delayed
   transition cases poll state instead of sampling once, finish with the expected final state, and
   retain attempts and elapsed time.
3. **Consumer proof is closed.** Mapper, runner, verifier, and walkthrough tests extract and
   execute each consumer's committed shared-protocol recipe; generated support is exercised
   separately. The proof is behavioral and can fail when a consumer recipe drifts.
4. **Coverage is closed.** Fresh full-suite V8 coverage converted to c8 LCOV and intersected with
   exact added executable lines measured 981/1,114 = **88.06%**, with no browser-source waiver,
   excluded file, or relabelled denominator.

### Material finding: accepted zero-timeout input loses AC-6 evidence

**P3 generally; Material for this task because AC-6 is false.** `compiler/resolver.js:715-718`
admits `wait: 0` and threads it as numeric `step.timeout`; blame shows that admission is
pre-existing at `^8267dda`. New mapped-visibility support in `compiler/codegen.js:453-483` uses
`while [ "$_count" -lt "$_timeout" ]`, so timeout zero skips `_probe_visibility_once` entirely,
then asks `_record_visibility_result` to parse empty `_VISIBILITY_LAST_RESULT`. The polling path
was introduced by feature commits `13b9a8c` and `050da815`, so the accepted input is old but the
empty-evidence mapped-visibility regression is introduced by this product diff. The equivalent OR
path at `compiler/codegen.js:486-522` has the same zero-iteration shape.

Fresh generated-script reproduction used a valid strict singleton envelope and exact
`step.timeout: 0`. It exited 1 with:

- stderr: `SyntaxError: Unexpected end of JSON input` while recording the result;
- stdout: `deterministic visibility probe failed for heading`, which selects the terminal
  infrastructure branch at `compiler/codegen.js:1973-1979` instead of a normal assertion timeout;
- metrics: the step failed but `visibility_results` was `[]`, so there was no result class,
  selector, policy, match count, attempts, elapsed time, or candidate evidence;
- probe count: zero, despite the supplied envelope classifying as `unique_rendered` if invoked.

This contradicts AC-6's requirement that generated polling/reporting retain final evidence,
attempt count, elapsed time, and the retryable-versus-terminal distinction. A sufficient falsifier
for a correction is a generated mapped visibility fixture with the public `wait: 0` boundary that
either (a) is rejected before code generation with an explicit timeout-domain error, or (b) makes
one defined probe attempt and records its final evidence, while never emitting JSON parse failure
or misclassifying a normal assertion boundary as probe infrastructure failure. Single and OR
mapped paths both need the same defined contract. Validation does not choose between those designs.

### Per-AC verdict

- **AC-1 PASS:** owned real strict and retained multi-match cases preserve raw cardinality and do
  not collapse hidden-first duplicates into absence.
- **AC-2 PASS:** focused classifier, CLI, policy, resolver, and codegen tests cover all result
  classes, hidden-style disqualification, second rendered candidate identity, inconsistent
  aggregates, enabled/disabled state, and capped evidence.
- **AC-3 PASS:** invalid CSS remains terminal `invalid_selector` with `match_count: null` in direct
  and generated owned-runtime paths; the invalid-CSS scratch mutation is caught.
- **AC-4 PASS:** CSS identity and explicit policy survive single-site, multi-site, legacy,
  parameterized, positive, negative, enabled/disabled, and OR forms; unresolved non-CSS mappings
  fail before output/browser startup.
- **AC-5 PASS:** mapper, runner, verifier, walkthrough, and generated support now have independent
  exercise-based shared-protocol proof. Enabled/disabled judgment uses the selected rendered
  candidate and polls delayed state for positive timeout budgets.
- **AC-6 FAIL:** accepted timeout zero executes no mapped visibility judgment, records no final
  visibility evidence, raises a JSON parse error, and reports an assertion boundary as terminal
  probe failure.
- **AC-7 PASS:** direct CLI and generated owned-runtime results agree for strict/retained ghost,
  invalid selector, rendered-candidate state, and delayed transitions covered by the real matrix.
- **AC-8 PASS:** published examples parse, compile, and execute; docs consistently state the
  strict default, explicit exception, CSS identity migration, diagnostics, negative behavior, and
  uniqueness guidance.

### Required evidence block

Lenses: correctness **FAIL, 1 finding**; silent-failure **FAIL, same finding**; type-design **PASS,
0 findings**; concurrency **PASS, 0 findings**; resource-lifecycle **PASS, 0 findings**;
manifest/back-compat **PASS, 0 findings**. Security did not fire: no auth, permission,
trust-boundary, secret-bearing workflow, or shell hook changed.
Diff coverage: **PASS — 981/1,114 exact added executable lines = 88.06%** from the final full-suite
NODE_V8_COVERAGE to c8 LCOV intersection. Per file: CLI 70/73; codegen 289/289; compiler 4/4;
shared probe 424/533; parser 20/22; resolver 174/193.
Adversarial: strict-cardinality scratch mutation (`match_count === 1` to `>= 1`) made 7 tests red;
invalid-CSS-to-`no_match` scratch mutation made 1 test red; generated `wait: 0` reproduction made
the unmutated product emit zero attempts, empty `visibility_results`, JSON parse failure, and the
wrong terminal diagnostic.
Cross-model: exactly one read-only Claude Opus 5 / high call completed in 159.373s API time
(181.491s wall), session `e17ea11e-c6e7-42af-9224-8bc55c017cb0`; no duplicate or fallback call was
made. It confirmed all four returned blockers closed and identified the zero-timeout polling/report
boundary, which local parser, blame, code-path, and generated-runtime reproduction accepted.
E2E: exact owned real browser test **PASS 1/1 in 47.582s** with direct and generated no-match,
all-non-rendered, singleton, strict/retained ghost, hidden-style extra, two-rendered, invalid CSS,
rendered-candidate enabled state, and delayed enabled/disabled matrices; test-owned app, run,
session, profile, and receipt state closed without touching unrelated browser state.

### Other exit evidence

- Focused protocol suites: **67 passed / 0 failed**.
- Fresh final full `npm test`: **1,033 passed / 0 failed / 2 intentional real-browser skips** out
  of 1,035 tests in 173 suites, duration 125.255s.
- `npm run lint`: exit 0 with 215 warnings and 2 infos; no fixes or product mutation.
- `git diff --check origin/main...HEAD`: exit 0.
- `scripts/version-parity-check.sh`: all seven plugin manifests and marketplace entries consistent;
  e2e-pipeline remains 3.2.0 across plugin, release, marketplace, and Codex surfaces.
- `scripts/marketplace-verify.sh`: L0 parity, L1 schema, and isolated L2 installation passed for all
  seven plugins.
- `scripts/skill-frontmatter-lint.sh`: all 38 skill directories passed.
- Product branch and remote remained exact `1d5e6c90ce44e1ba3d07302b1da59240445846aa` and the
  product worktree remained clean after validation.

### Cycle-2 escalation and disposition

Correction round 1 used 0.47 working hours against the 16h estimate and 22h tolerance, so the
effort budget itself remains healthy. That does not override the independent validation-cycle
circuit breaker. This is the **second validation rejection**: do not automatically dispatch a
third implementation/validation round, do not waive AC-6, and do not advance the entity. Captain
must adjudicate whether the public timeout domain should reject zero or define one immediate probe,
then explicitly authorize any correction path. The validator made no product or status mutation.

## Stage Report: implementation — correction round 2

- DONE: For single and OR mapped visibility, wait: 0 performs the defined immediate probe set without sleeping, records attempts=1 and populated final evidence, and preserves normal 0/1/2 result semantics.
  Product commit `9e788e8` makes both generated mapped pollers probe before checking retry budget; reverting either poller to the old `< timeout` guard makes its zero-timeout aggregate test fail on probe count, result evidence, and verdict.
- DONE: Generated single and OR fixtures cover satisfied, retryable, and terminal wait: 0 outcomes with RED-before-GREEN evidence, exact probe counts, and non-empty visibility_results.
  Six generated-runtime tests in `visibility-resolver-codegen.test.js` require 1 single eval or 2 OR evals, zero `sleep 1`, elapsed 0, exact judgments, and 1 or 2 final reports; deleting either operand probe or report makes the corresponding aggregate assertion fail.
- DONE: The correction remains limited to the captain-approved polling boundary and exits with focused, full-suite, real-runtime, coverage, lint, parity, and install evidence plus an honest correction-round budget record.
  Only `compiler/codegen.js` and its generated-runtime test changed; exact remote head `9e788e8b09904073d8a66e782d472258a8b91cab` passed every named exit gate below without parser/resolver, unrelated helper, release, PR, issue, or status mutation.

### Summary

The accepted timeout domain is preserved: zero now means one immediate single probe or both OR
operand probes, with no retry sleep. The ordinary satisfied, retryable, and terminal judgments
are recorded with `attempts: 1`, `elapsed_seconds: 0`, and bounded final evidence before returning.

### RED before GREEN and old-fixture audit

- RED on exact pre-correction head: focused suite finished **16 passed / 6 failed**. Every new case
  observed zero evals, `visibility_results: []`, `SyntaxError: Unexpected end of JSON input`, and
  infrastructure-failure routing instead of the fixture's satisfied/retryable/terminal outcome.
- GREEN after the two-poller correction: the same focused file finished **22 passed / 0 failed**;
  the full visibility boundary finished **74 passed / 0 failed / 1 intentional real-browser skip**.
- Existing mapped timeout fixtures retain their original intent: first-try positive cases still
  terminate immediately, delayed enabled/disabled cases still require a second atomic probe, and
  terminal-first single/OR cases still perform exactly one immediate attempt set with no sleep.

### Exact-head gates, CI difference, and effort

- Owned real browser: **2 passed / 0 failed** in 52.07s. Fresh full suite: **1,039 passed / 0 failed /
  2 intentional real-browser skips** across 173 suites in 135.61s; instrumented coverage run matched.
- Honest executable diff coverage against base `844f36a5`: **991/1,124 = 88.17%**. The correction
  added ten covered `codegen.js` lines; no browser source, file, or denominator was waived.
- Lint exited 0 with the pre-existing 215 warnings and 2 infos. `git diff --check`, version parity,
  release-path/JSONPath validation, plugin enumeration, 38-skill frontmatter lint, marketplace
  schema, and isolated clean-HOME installation of all seven plugins passed.
- Six tests were added. No current GitHub workflow invokes `e2e-pipeline`'s `npm test`, so no existing
  CI job timeout margin is consumed; the local full-suite measurement increased from the cycle-2
  125.26s reference to 135.61s (+10.35s, 8.3%).
- Dispatch-to-exact-product-readback was **18m49s (0.31 working hours)**. Together with correction
  round 1, corrections total **0.78h**, 4.9% of the 16h estimate and 3.5% of the 22h tolerance.
  The branch is pushed normally; entity status remains `implementation` for authorized validation cycle 3.

## Stage Report: validation — cycle 3

TL;DR: **PASSED.** Fresh validation on exact clean product head
`9e788e8b09904073d8a66e782d472258a8b91cab` against freshly fetched
`origin/main` `844f36a53bc7094b74476b3e57cb47c70d69d5dd` reproduced AC-1 through AC-8
with zero Material residuals. The captain-approved `wait: 0` contract now performs one immediate
single probe or both OR operand probes, performs no sleep, records attempts 1 / elapsed 0 and
populated bounded final evidence, and preserves satisfied, retryable, and terminal routing. Both
loop guards were broken in a detached scratch worktree and all six zero-timeout cases went red.

### Exact authority and scope

- Fetched `origin/main` immediately before review; merge-base and base both resolved to
  `844f36a53bc7094b74476b3e57cb47c70d69d5dd`. The assigned branch, local HEAD, and remote feature
  branch all resolved to exact `9e788e8b09904073d8a66e782d472258a8b91cab`.
- The product worktree was clean before validation and remained clean after every focused,
  adversarial, real-browser, full-suite, coverage, lint, and compatibility check.
- Exact diff: 25 files, 3,311 insertions, 178 deletions, all under `e2e-pipeline/`. Shared
  probe/CLI/codegen/parser/resolver/compiler files map to AC-1 through AC-7; the eight changed test
  files map to the same behavior and falsifiers; the three agents, walkthrough skill/reference,
  compile skill, selector authority, and four published docs/references map to AC-5 and AC-8.
  **25/25 changed files mapped; zero unrelated files and zero missing AC owners.**
- No product, issue, PR, version, release, marketplace, ruleset, or stage-status surface was edited.
  The only durable validation write is this entity report.

### Cycle-2 correction falsification and prior-finding closure

1. The six generated `wait: 0` cases independently returned the required single/OR probe counts
   (1/2), zero retry sleeps, attempts 1, elapsed 0, non-empty `visibility_results`, and distinct
   satisfied/retryable/terminal result classes and failure messages.
2. A separate generated snapshot-action fixture eliminated the test step's own `sleep 0` and
   observed **zero sleep invocations of any kind**. Its single satisfied path retained one bounded
   candidate; its OR satisfied-plus-terminal path retained one and two candidates respectively,
   both with evidence limit 10 and `candidate_evidence_truncated: false`.
3. Replacing both immediate `while :` guards with the pre-correction `< timeout` form in a detached
   scratch worktree made all six zero-timeout cases red. Each reported zero evals and empty final
   results; retryable and terminal cases also falsely exited success. The scratch worktree was
   removed after the falsifier and the product tree was never edited.
4. All cycle-1 findings remain closed: enabled/disabled state comes from the selected rendered
   candidate; delayed state changes poll; mapper, runner, verifier, and walkthrough execute their
   committed recipes; exact executable diff coverage remains above 85%.

### Per-AC verdict

- **AC-1 PASS:** owned Chrome/runtime proof finished 2 passed / 0 failed. Strict hidden-first
  classified `raw_multi_match`; explicit retained policy classified
  `unique_rendered_with_retained_zero_rect`; neither path reported absence.
- **AC-2 PASS:** the focused 192-test boundary exercised all eight result classes, exact exception
  eligibility, hidden-style and second-rendered disqualification, uncapped aggregates, capped
  candidate evidence, and CLI/generated classifier parity.
- **AC-3 PASS:** malformed policy/envelope/transport/predicate inputs remained terminal
  `probe_error`; invalid CSS remained terminal `invalid_selector` with `match_count: null` in direct
  and generated real-runtime paths and could not satisfy a negative assertion.
- **AC-4 PASS:** resolver/compiler fixtures carried effective CSS identity and policy through
  single-site, multi-site, legacy, parameterized, positive, negative, enabled/disabled, and OR
  forms; non-CSS mapped visibility without `css_selector` failed before generated output/browser.
- **AC-5 PASS:** mapper, runner, verifier, and walkthrough tests extracted and executed each
  committed shared-protocol recipe; generated support was exercised separately. Selected-candidate
  enabled/disabled and report fields remained coupled to the same shared seam.
- **AC-6 PASS:** single and OR `wait: 0` satisfied, retryable, and terminal paths executed the
  immediate probe set, never slept, retained attempts/elapsed/final evidence, and preserved 0/1/2
  judge semantics. A terminal OR operand was not masked by its satisfied peer.
- **AC-7 PASS:** direct CLI and generated Bash agreed in the owned browser for strict/retained
  hidden-first, invalid-CSS, selected-candidate state, and delayed transitions; a scratch source
  perturbation test retained CLI/generated drift coupling.
- **AC-8 PASS:** published YAML examples parsed, compiled, and executed through generated support;
  reviewed guidance consistently states the strict default, exact exception, CSS identity
  requirement, negative/error behavior, diagnostics, and uniqueness guidance.

### Required evidence block

Lenses: executable JS/CLI/codegen/protocol plus agent/skill/docs contract diff; correctness **PASS,
0 findings**; security **PASS, 0 findings**; silent-failure **PASS, 0 findings**; type-design **PASS,
0 findings**; concurrency **PASS, 0 findings**; resource-lifecycle **PASS, 0 findings**;
manifest/back-compat **PASS, 0 findings**. Security fired because mapping selector input crosses
YAML, shell argv, and browser eval/report boundaries; hostile quoting, sanitized/bounded evidence,
and forbidden secret fields were exercised.
Diff coverage: **PASS — 991/1,124 exact added executable lines = 88.17%** from the final full-suite
`NODE_V8_COVERAGE` converted to c8 LCOV and intersected with exact added lines. Per file: CLI
70/73; codegen 299/299; compiler 4/4; shared probe 424/533; parser 20/22; resolver 174/193.
Adversarial: mutating both mapped pollers back to the pre-correction `< timeout` loop guard made
**6/6 zero-timeout tests red** across single/OR satisfied, retryable, and terminal outcomes; the
failures showed zero evals, empty reports, and false-success routing. A separate unmutated
snapshot-action control proved 1/2 evals, zero sleeps, and populated bounded candidate evidence.
Cross-model: exactly one actual read-only whole-diff review was requested from `agy` with
`gemini-3.1-pro-high` / high; it inspected all 25 files, returned **0 actionable findings**, and
named only the accepted selector-identity and current-document scope residuals. Its cited
probe/state, poller/order, and consumer-exercise lines were verified locally. One earlier malformed
argument-order preflight returned usage guidance and reviewed no diff; it was not a review call.
E2E: exact owned real-browser/runtime test **PASS 2/2 in 43.89s** with direct and generated
no-match, all-non-rendered, singleton, strict/retained ghost, hidden-style extra, two-rendered,
invalid CSS, rendered-candidate enabled state, and delayed enabled/disabled cases; owned test state
closed without touching unrelated browser/profile/session state.

### Other exit evidence

- Focused AC/protocol boundary: **192 passed / 0 failed** in 13 suites.
- Fresh final instrumented `npm test`: **1,039 passed / 0 failed / 2 intentional real-browser
  skips** out of 1,041 tests in 173 suites, duration 130.27s.
- `npm run lint`: exit 0 with 215 existing warnings and 2 infos; no fixes applied.
- `git diff --check origin/main...HEAD`: exit 0.
- `scripts/version-parity-check.sh`: release paths, JSONPath targets, plugin enumeration, and all
  plugin/marketplace/Codex versions passed.
- `scripts/marketplace-verify.sh`: L0 parity, L1 schema, and isolated clean-HOME L2 installation
  passed for all seven plugins.
- `scripts/skill-frontmatter-lint.sh`: all 38 skill directories passed.

### Reviewer adjudication and residuals

The cross-vendor reviewer supplied no finding to accept or decline. Its cited lines were accurate;
the phrase “non-empty bounded evidence” was independently sharpened with an executable fixture
because the committed zero-timeout vectors use empty candidate arrays. Final result records are
always populated; candidate evidence is populated when matches exist and is legitimately empty for
`no_match`. The two named residuals remain the already accepted design bounds: accessible locator
and `css_selector` identity can diverge, and current-document probing does not cross shadow/frame
boundaries.

### Summary

Fresh cycle-3 validation closes the authorized zero-timeout correction and re-confirms every prior
boundary on the exact product head. All ACs, the complete evidence block, real-runtime proof,
changed-line coverage, full suite, and compatibility gates pass with zero Material residuals, so
the validation verdict is **PASSED**.

## Stage Report: implementation — correction round 3

### Completion checklist

- **DONE — Runner enabled/disabled instructions invoke the shared visibility judge directly with assertion enabled or disabled so state is taken from the selected rendered_candidate; they explicitly forbid a separate raw selector state check.** Evidence: the runner table now prescribes `--assert enabled` / `--assert disabled`, names `rendered_candidate` as the state authority, and contains the explicit prohibition.
- **DONE — The actual runner consumer exercise includes enabled/disabled rendered-candidate vectors, including disabled zero-rect first plus enabled rendered second, and a raw-first-match or state-decoupling mutation makes that runner exercise red.** Evidence: the aggregate test executes the runner's extracted recipe against candidate 0 disabled/zero-rect plus candidate 1 enabled/rendered and rejects both in-memory mutations.
- **DONE — The correction remains confined to AC-5 runner guidance and its executable consumer contract, preserves the already-passed compiled wait: 0 path, and exits with focused/full/real-runtime/coverage/lint/parity/install evidence plus correction-round effort.** Evidence: exact commit `f0d8b5cede15b7e93ac922c32229c8c9396df40b` changes only the two authorized files; all required gates below passed.

### Summary

The runner's public enabled/disabled contract now uses the shared visibility judge directly, so the
state decision is coupled to the uniquely selected rendered candidate rather than a raw first DOM
match. One executable consumer test covers both state assertions and proves that raw-first-match or
state-decoupled guidance cannot remain green. No production classifier, resolver, codegen, wait,
release, or workflow-state semantics changed.

### RED to GREEN and falsifiability

- False-green reproduction: changing only the prior runner state table to prescribe a raw first-match
  check left the extracted Bash recipe byte-identical, and the existing three consumer tests passed.
- RED: the new aggregate runner exercise failed 1/4 before guidance correction. Both state cases used
  assertion `visible`; the enabled case passed accidentally, the disabled case incorrectly returned
  satisfied/status 0, and the explicit raw-check prohibition was absent.
- GREEN: after the smallest runner guidance correction, the consumer contract passed 4/4. Enabled
  resolves satisfied/status 0 while disabled resolves retryable/status 1 from rendered candidate
  index 1, whose enabled state is true.
- Adversarial evidence is executable in that test: mutating the runner row to raw first-match state or
  replacing the recipe's assertion with `visible` changes the state summaries and is detected.
- Old-fixture audit: the runner contains no competing enabled/disabled raw-state instruction, and the
  focused suite re-ran all six previously added generated `wait: 0` cases without regression.

### Exact-head verification

- Focused visibility/protocol boundary: **75 passed / 0 failed / 1 intentional real-browser skip**.
- Owned real browser: **2 passed / 0 failed** in 42.00s.
- Fresh instrumented full suite: **1,040 passed / 0 failed / 2 intentional real-browser skips** out
  of 1,042 tests across 173 suites in 131.00s.
- Honest executable diff coverage against base `844f36a5`: **991/1,124 = 88.17%**. Per file:
  CLI 70/73; codegen 299/299; compiler 4/4; parser 20/22; resolver 174/193; probe 424/533.
- `npm run lint`: exit 0 with the pre-existing 215 warnings and 2 infos; no fixes applied.
- `git diff --check`, version parity/release paths/JSONPath/plugin enumeration, 38-skill
  frontmatter lint, marketplace schema, and isolated clean-HOME install of all seven plugins passed.
- No current workflow invokes the full `e2e-pipeline npm test`, so no existing CI timeout is
  consumed. The fresh 131.00s run is 0.73s slower than cycle 3's 130.27s reference (0.6%).
- Product branch local and remote both read back exact clean head
  `f0d8b5cede15b7e93ac922c32229c8c9396df40b`.

### Effort

Dispatch-to-exact-product-readback took **13m00s (0.22 working hours)**. Corrections now total
**1.00h**, 6.3% of the 16h estimate and 4.5% of the 22h tolerance. Entity status remains
`implementation` for the captain-authorized fourth validation cycle.

## Stage Report: validation (cycle 4)

TL;DR: **PASSED.** Fresh validation bound local and remote product head to
`f0d8b5cede15b7e93ac922c32229c8c9396df40b` over freshly fetched base `844f36a5`, reproduced
AC-1 through AC-8, and found zero Material residuals. The AC-5 runner correction now exercises
enabled/disabled state from `rendered_candidate`; two independent scratch mutations made it red.

- DONE: Independently falsify AC-5 on exact head f0d8b5c: exercise the actual runner enabled and disabled guidance against disabled zero-rect candidate 0 plus enabled rendered candidate 1, prove state comes from rendered_candidate, and prove raw-first-match or assertion-decoupling mutations make the exercise red.
  Clean consumer exercise passed 4/4; raw-first-match guidance and `--assert visible` scratch mutations each failed 1/4 with disabled falsely satisfied/status 0.
- DONE: Reproduce AC-1 through AC-8, including all prior cycle-1 findings and captain-approved AC-6 single/OR wait: 0 satisfied, retryable, and terminal behavior, with the complete five-line evidence block, exactly one actual cross-vendor review, adversarial mutations, honest executable diff coverage, and owned real-browser/runtime evidence.
  Focused visibility boundary passed 75/75 plus one intentional browser skip; all six zero-timeout cases and selected-candidate/delayed state cases were green.
- DONE: Audit every changed file to an AC, run focused checks then one final full suite plus earned lint/parity/frontmatter/marketplace/install gates, and return PASSED only with zero Material residuals; never edit product or mutate PR, issue, version, release, ruleset, or status state.
  All 25 files map to AC-1 through AC-8; product stayed clean and no hosted/status surface changed.

### Per-AC verdict

- AC-1 PASS: owned runtime classified strict hidden-first as `raw_multi_match` and retained policy as `unique_rendered_with_retained_zero_rect`, never absence.
- AC-2 PASS: focused tables exercised all eight classes, exact exception eligibility, hidden-style/two-rendered disqualification, and bounded evidence.
- AC-3 PASS: invalid CSS, policy, transport, envelope, and predicate failures stayed terminal; invalid selector retained `match_count: null`.
- AC-4 PASS: resolver/compiler fixtures carried CSS identity and policy through every mapped form and failed non-CSS-without-`css_selector` before browser output.
- AC-5 PASS: four consumer recipes executed; runner enabled/disabled used assertions `enabled`/`disabled`, candidate index 1 state, and no raw state check.
- AC-6 PASS: six single/OR `wait: 0` cases made 1/2 probes, zero retry sleeps, populated final evidence, and distinct satisfied/retryable/terminal routing.
- AC-7 PASS: CLI and generated Bash agreed in the owned browser for retained ghost, invalid CSS, selected-candidate state, and delayed transitions.
- AC-8 PASS: the published YAML parsed, compiled, and executed; reviewed guidance retains strict default, exact exception, CSS identity, diagnostics, and uniqueness.

### Required evidence block

Lenses: executable JS/CLI/codegen/protocol plus agent/skill/docs contract diff; correctness **PASS, 0 findings**; security **PASS, 0 findings**; silent-failure **PASS, 0 findings**; type-design **PASS, 0 findings**; concurrency **PASS, 0 findings**; resource-lifecycle **PASS, 0 findings**; manifest/back-compat **PASS, 0 findings**.
Diff coverage: **PASS — 991/1,124 exact added executable lines = 88.17%** from the final full-suite `NODE_V8_COVERAGE` converted to c8 LCOV and intersected with committed added lines.
Adversarial: raw-first-match guidance and assertion-to-visible scratch mutations each made the AC-5 consumer exercise red; clean product stayed 4/4 and the scratch tree was removed after both checks.
Cross-model: exactly one actual read-only whole-diff review completed through `agy` requested as `gemini-3.1-pro-high` / high on exact head and all 25 files; **0 actionable findings**. A cached wrong-project attempt was terminated before verdict and did not count as a review.
E2E: exact owned browser/runtime test **PASS 2/2 in 49.72s** across direct/generated hidden-first, invalid CSS, rendered-candidate enabled, and delayed enabled/disabled cases; owned cleanup completed.

### Other exit evidence

- Final instrumented `npm test`: **1,040 passed / 0 failed / 2 intentional skips** out of 1,042 tests in 173 suites, 137.43s.
- `npm run lint` exited 0 with 215 pre-existing warnings and 2 infos; `git diff --check`, version/release parity, plugin enumeration, 38-skill frontmatter lint, marketplace schema, and clean-HOME install of all seven plugins passed.
- Cross-vendor citations for runner, consumer mutation harness, wait-zero codegen/tests, and delayed selected-candidate polling were checked against the exact files and were accurate.

### Summary

Fresh cycle-4 validation independently closes the runner guidance false-green that invalidated
cycle 3 while retaining every earlier correction and proof boundary. All ACs, required evidence,
real runtime, coverage, full suite, and compatibility gates pass with zero Material residuals, so
the validation verdict is **PASSED**.
