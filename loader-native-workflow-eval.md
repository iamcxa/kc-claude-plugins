---
title: "kc-dev-flow: make workflow changes measurable through the real loader"
status: implementation
source: "captain:conversation-2026-08-12-second-slice"
product: kc-dev-flow
sprint:
started: 2026-08-12T05:46:00Z
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-loader-native-workflow-eval
issue:
pr:
mod-block:
design: required
lane: main
id: zzr91wq8wmc29ddfsyjyfyz5
---

## Problem

The merged loader-activation repair is protected by a growing monolithic contract test and one-off Q08 receipts, but phrase-presence checks do not prove the behavior produced by Spacedock's real stage loader. Cut the next bounded slice so a workflow revision can be compared through the installed loader and existing pressure corpus, while deterministic CI keeps only unique mechanical invariants. Remove tests proven duplicate or behaviorless, without changing Spacedock, adding a mandatory model run to per-commit CI, or reopening the merged activation behavior.

## Proposed approach

Add one repository-local capture adapter and one tracked Q08 fixture. Given an
exact known-bad Git ref and an exact candidate ref, the adapter materializes
each ref's `docs/dev` tree, resolves `SPACEDOCK_BIN` or the installed
`spacedock`, and invokes the real
`dispatch show-stage-def --stage implementation` command for both arms. It
writes the exact stage bytes, SHA-256 digests, resolved commit SHAs, executable
path/version, fixture digest, paired opaque-arm prompts, and a closed manifest
to a new operator-owned output directory outside the checkout. It does not
parse the workflow README, infer selected mods, invoke or grade a model, mutate
workflow state, or become a per-commit Spacedock dependency.

Promote only the existing Q08 scenario, response contract, hard-failure rule,
and required behavior from the ignored local pressure corpus into one tracked
fixture. The generated runner prompt contains the exact loader output and Q08
facts but not the hidden rubric or the base/candidate identity. The manifest
retains the mapping for later grading.

At the validation boundary, run three fresh contexts per arm using the same
runner, model, reasoning level, and invocation configuration. Preserve raw
responses, session and configuration identity, output hashes, and grades.
Candidate evidence passes only when every candidate trial scores at least
10/12 with zero hard failures and candidate safety is non-inferior to the
known-bad arm. The known-bad arm must reproduce at least one Q08 premature-load
hard failure; otherwise the instrument is non-discriminating and the result is
`UNKNOWN`, not a pass.

Keep deterministic CI model-free and Spacedock-free. Refactor the current
activation block in `scripts/kc-dev-flow-contract-test.py` so direct assertions
continue to enforce the unique mechanical invariants: the exact implementation
`Policy mods` set, the inactive-locator rule, all four trigger facts, and the
pre-trigger unread boundary. Retire only the three self-mutants and their helper
indirection. Do not remove a direct invariant merely because pressure evidence
is green.

### Accepted value and constraints

- **Protected value:** a maintainer can compare a workflow revision through the
  installed behavior-producing loader and tell whether it changes the Q08
  activation decision, while deterministic CI retains the unique cheap guards.
- **Appetite:** one worker and one bounded evaluation surface. The expected
  product diff is one capture adapter, one focused deterministic test, one Q08
  fixture, the existing contract-test simplification, and the local Proof
  Policy wording.
- **Tolerance:** no Spacedock change, no new workflow/tracker/state authority,
  no full-corpus framework, and no mandatory model run in per-edit or
  per-commit CI.
- **Keep if cut:** keep exact-ref real-loader capture plus the tracked Q08
  fixture and retain all current deterministic tests; test retirement waits
  until the paired validation instrument discriminates.
- **Most likely false assumption:** three fresh paired Q08 runs may not
  reproduce the historical base failure because model behavior varies. That
  yields `UNKNOWN` and returns the candidate; it is not grounds to weaken the
  rubric or claim the wording is behaviorally proven.

### Reverse-recovery audit

Fresh source authority is `origin/main`
`ec699d3e5b21e666209f079c9df7a9bd45528f13`.

| Surface | Completeness | Need | Evidence and disproof hook |
|---|---|---|---|
| Installed Spacedock stage extractor | `WORKING` | `REQUIRED` | Spacedock 0.26.0 contract 3 extracted exact implementation subsections at both refs. Disproved by a direct invocation disagreeing with a captured artifact at the same ref/tool identity. |
| Activation mechanical checks | `WORKING_UNIT_UNPROVEN` for behavior | `REQUIRED` for syntax/structure | `scripts/kc-dev-flow-contract-test.py` parses stage declarations and checks the activation strings, but cannot observe loader-produced worker behavior. Disproved as a structural guard by a named invariant mutation surviving CI. |
| Q08 semantic scenario and rubric | `WORKING` but not durably consumable | `REQUIRED` | The ignored corpus recorded 3/3 historical premature loads for the principles-only arm and 3/3 safe repaired-loader runs plus one validation run. Disproved by fresh paired runs being unable to distinguish the exact known-bad arm. |
| Exact-ref capture orchestration | `MISSING` | `REQUIRED` | Two tracked-file searches for `show-stage-def`, Q08, and workflow-eval runners found no repository adapter; current evidence is hand-assembled in ignored `.context` and the archived work item. Disproved by locating an existing tracked adapter that accepts two exact refs and records the required loader provenance. |

The existing loader is therefore reused unchanged. The new responsibility is
only orchestration and capture at its public CLI boundary; it does not duplicate
the loader's Markdown extraction or policy-selection logic.

### Routes compared

1. **Selected — real-loader capture plus the smallest Q08 fixture.** Exercises
   installed Spacedock output, makes the prior manual receipt repeatable, keeps
   agent variability at validation, and lets CI keep only direct mechanical
   invariants.
2. **Extend the monolithic Python parser and mutant table.** Cheaper to type but
   rejected: it reads repository text through locally reimplemented rules and
   still cannot prove the behavior produced from real loader output.
3. **Run the full eight-scenario corpus in required CI.** Broader behavioral
   coverage but rejected: it adds nondeterministic provider cost and latency to
   every commit and exceeds the one-seam appetite.
4. **Keep manual commands and one-off receipts.** No product code, but rejected:
   it repeats the exact non-durable evidence problem and makes later comparisons
   operator-dependent.
5. **Change Spacedock to synthesize policy bundles.** Rejected for this slice:
   it changes another product and reopens loader architecture when the installed
   `show-stage-def` boundary already emits the bytes this evaluation needs.

## Design determination

`required` — proceed with one independently maintained evaluation surface. Its
lifecycle invariant is: given two exact commit SHAs and one executable identity,
capture exactly the two real implementation-stage outputs and enough provenance
to reproduce the pair; then let a fresh validator, not the capture adapter,
apply the hidden Q08 rubric. The adapter, focused deterministic test, and fixture
are inseparable parts of that one surface: without the adapter there is no real
loader evidence; without the fixture there is no stable behavioral question;
without the test the capture manifest can silently lie.

The simpler no-adapter route is insufficient because the previous repair needed
hand-built prompts and one-off receipts. A general evaluator, model runner,
grader, loader parser, or Spacedock change has no named AC failure when absent
and is returned from the route.

## Acceptance criteria

**AC-1 — Deterministic CI retains each unique mechanical invariant.**

Verified by: a focused adapter test uses a fake executable to prove exact ref
resolution, exact byte preservation and hashing, executable/version provenance,
closed manifest fields, prompt/rubric separation, refusal of invalid refs or an
existing output directory, and no manifest on failed capture. The existing
contract test directly asserts the exact implementation mod set, inactive
locator rule, four candidate facts, and pre-trigger unread boundary. Each check
is seen red against its named mutation before GREEN. Falsified by: any required
manifest fact can be omitted or forged while the tests pass, a failure leaves a
normal-looking complete receipt, or one of the retained workflow invariants is
no longer checked in deterministic CI. Current enforcement:
`scripts/kc-dev-flow-contract-test.py:1384`.

**AC-2 — The adapter exercises installed Spacedock output at the stage boundary.**

Verified by: on the exact implementation candidate, run the adapter against
known-bad `a18ba78f72c03036d8463629bd19977aa684e159` and that exact candidate SHA
using installed Spacedock. For each arm, the captured stage bytes and hash equal
a direct `spacedock dispatch show-stage-def` invocation over an independently
materialized tree, and the manifest binds the executable path/version, refs,
resolved SHAs, fixture, and outputs. Falsified by: the adapter derives a stage
with repository parsing, accepts different resolved revisions, captures output
from a different tool identity, or differs byte-for-byte from the direct loader
invocation. Prior real-loader evidence:
`docs/dev/.spacedock-state/_archive/loader-native-stage-contract.md:413`.

**AC-3 — Fresh paired Q08 pressure distinguishes safe activation behavior.**

Verified by: at validation, six fresh isolated runs (three per opaque arm) use
the adapter-generated prompts, one runner/model/reasoning/configuration, and a
rubric hidden until all raw outputs close. Every candidate run scores at least
10/12 with zero hard failures and no more hard failures than the known-bad arm;
the known-bad arm produces at least one hard failure for loading PR, validation,
or recovery before its trigger. Falsified by: a candidate hard failure, safety
regression, mismatched runner configuration, exposed rubric/arm identity,
missing raw receipt, or zero target hard failures in the known-bad arm. The last
case is `UNKNOWN` and returns the candidate; it never proves parity. Prior Q08
receipt audit: `docs/dev/.spacedock-state/_archive/loader-native-stage-contract.md:451`.

**AC-4 — Every retired test has a surviving enforcement point.**

Verified by: the implementation report maps each removal before deletion and
the exact candidate diff contains no broader retirement:

| Proposed removal | Existing overlapping enforcement point that remains |
|---|---|
| `premature-load` self-mutant | Direct equality check that implementation `Policy mods` is exactly `_mods/work-control-profile.md`. |
| `trigger-loss` self-mutant | Direct retained assertion for the pre-trigger unread sentence plus direct retained assertions for all four candidate facts. |
| `locator-loss` self-mutant | Existing earlier contract assertion that the exact `pr-merge.md#delivery-topology-decision` locator and its `dependent green layers, independent green slices, and numeric trigger` predicates remain in the workflow. |
| `implementation_activation_errors` helper indirection | The same unique baseline conditions become direct `require(...)` assertions; no condition loses an enforcement point. |

Falsified by: any removed case lacks a named surviving check, any direct
mechanical invariant is removed, or the full deterministic suite does not fail
when a retained invariant is mutated. A non-discriminating AC-3 run also returns
the candidate with the prior tests restored rather than accepting the
retirement. Current self-mutant enforcement:
`scripts/kc-dev-flow-contract-test.py:1424`.

**AC-5 — The slice adds no loader, workflow authority, or per-commit model gate.**

Verified by: the changed-file-to-AC map contains only the capture adapter and
focused test (AC-1/AC-2), one Q08 fixture (AC-1/AC-3), the existing contract-test
simplification (AC-1/AC-4), and `docs/dev/README.md` Proof Policy wording
(AC-5). CI executes only deterministic Python checks; fresh model pressure is a
validation-stage receipt. Falsified by: a Spacedock source change, new stage or
state field, model/provider call from CI or the adapter, full-corpus runner or
grader, PRODUCT/ARCHITECTURE behavior change, or an unmapped changed file.
Current Proof Policy: `docs/dev/README.md:136`.

## Test plan

1. Write focused adapter tests first. RED must cover invalid/non-commit refs,
   missing or wrong executable version output, exact binary stage bytes
   including the trailing newline, arm separation, fixture/rubric non-leakage,
   fail-closed publication, and an already-existing output target.
2. Implement the minimum capture adapter and fixture. Use a fake Spacedock only
   for deterministic unit cases; do not duplicate stage parsing in fixtures or
   test helpers.
3. Refactor the activation checks to direct baseline assertions and delete only
   the three mapped self-mutants/helper indirection. Exercise mutations of every
   retained direct invariant, then run the complete
   `scripts/kc-dev-flow-contract-test.py` suite.
4. Run the adapter through installed Spacedock against exact known-bad
   `a18ba78...` and the exact implementation head. Independently materialize
   both refs and compare direct CLI output byte-for-byte with the captured
   artifacts.
5. During fresh validation, execute the six pre-registered Q08 runs. Freeze raw
   outputs before revealing the rubric and arm mapping; record per-trial score,
   hard failure, session/model/config identity, hashes, wall time, and available
   provider usage without turning cost into a safety credit.
6. Run `python3 scripts/kc-dev-flow-contract-test.py`, the focused adapter test,
   `./scripts/skill-frontmatter-lint.sh`, and `git diff --check` at the exact
   implementation and validation heads.

E2E applies at the stage boundary, not in a browser: AC-2 re-runs the real
installed Spacedock consumer, and AC-3 re-runs the behavior-producing agent kind
against those exact bytes. Fake-executable tests are deterministic CI only and
cannot close either runtime claim.

## Measurement

- **Deterministic CI:** number of unique retained invariants, mutation REDs,
  focused capture cases, and full-suite result. Target: all named direct
  invariants survive and the three duplicate self-mutants/helper are absent.
- **Stage-boundary loader integration:** exact tool identity, resolved SHAs,
  stage byte counts, hashes, and direct-versus-captured byte equality for both
  arms. The feasibility spike already reproduced the historical values:
  `a18ba78...` ->
  `c85143915d110cd7937a967b9fed32fc4c799ec5ef151e9b24438bd15df23dad`
  (27 lines / 227 words / 1616 bytes), and `ec699d3...` ->
  `4f10401f127e77cf12bf23d7fcf70b626e082eca2f4579d3a76468dc1bf7a965`
  (33 lines / 269 words / 1934 bytes).
- **Non-deterministic pressure:** six raw trials, per-arm hard failures and
  0-12 scores, safety comparison, runner identity, and available cost receipts.
  Historical 3/3 failures and 3/3-plus-one safe runs are context only; they do
  not satisfy AC-3.

No single blended score is produced. Mechanical green cannot substitute for
loader equality, loader equality cannot substitute for worker behavior, and
provider cost cannot offset a safety failure.

### Pre-mortem and stop boundary

If this ships and still fails, the likely cause is a nondiscriminating Q08
sample: both arms look safe because the current runner reconstructs the desired
boundary without relying on the changed stage bytes. In that case the capture
adapter is still a truthful loader receipt, but it has not justified test
retirement. Return to implementation, restore the removed self-mutants, and ask
ideation whether another pre-registered scenario or a loader-enforced
representation is worth the added surface. Stop immediately if implementation
requires parsing Markdown, changing Spacedock, invoking a provider inside the
adapter/CI, or adding a general runner/grader.

## Doc diff

- `docs/dev/README.md` Proof Policy: distinguish fast deterministic contract
  checks from the installed-loader capture and validation-only pressure
  evidence, and name the focused evaluator command.
- `PRODUCT.md`: no change. This adds evidence for the existing portable
  workflow outcome, not a user-facing capability.
- `ARCHITECTURE.md`: no change. The adapter remains repository-local validation
  support and neither changes the plugin/runtime architecture nor owns loader
  semantics.

## Out of scope

Changing or wrapping Spacedock internals; implementing a Markdown/stage/mod
parser; changing the merged inactive-locator or four-fact activation semantics;
running a model in per-edit/per-commit CI; importing the full pressure corpus;
building a generic prompt runner, grader, dashboard, or receipt service;
changing task state or delivery authority; adding a stage, mod, registry, or
tracker; editing PRODUCT/ARCHITECTURE; and using historical Q08 receipts as the
new candidate's validation.

## Ideation EM judgment

One completed fresh-context GPT-5.6 High EM reviewed the exact revision,
installed-loader observations, route alternatives, conservative test-retirement
map, and the three-layer evidence contract. It returned `proceed / high` with no
dissent and `multi_model: not_needed`.

```yaml
science_officer_em_upward_report:
  em_judgment: "Proceed with the bounded repo-local evaluator and one tracked Q08 fixture. The proposal is a reversible, single-value-surface measurement improvement that exercises the installed loader boundary without changing activation semantics or adding nondeterministic CI."
  evidence_synthesis: "At origin/main ec699d3e5b21e666209f079c9df7a9bd45528f13, installed Spacedock 0.26.0 contract 3 produced distinct, byte-recorded implementation-stage outputs for known-bad base a18ba78 and current ec699d3, establishing that exact-ref snapshot materialization through show-stage-def is feasible. Historical Q08 results support the targeted failure mode but are not acceptance evidence; acceptance remains conditional on three fresh same-runner trials per arm with a hidden rubric. The evaluator records provenance and exact output bytes and hashes while remaining model-free and Markdown-parser-free. Deterministic CI retains direct assertions for every unique mechanical invariant. Material limits are that the evaluator and fresh paired trials do not yet exist, and absence of a premature-load failure in the known-bad arm must remain UNKNOWN rather than being interpreted as success."
  risk_tradeoff_call: "The benefit is repeatable evidence at the real loader boundary, which phrase checks cannot provide. The principal risk is mistaking environment-bound or model-variable results for deterministic contract proof; exact binary, version, path, SHAs, prompts, bytes, hashes, manifests, same-runner pairing, and the explicit UNKNOWN rule contain that risk. Durable cost is one small evaluator, one fixture, and validation-time trial execution. The cheaper alternatives either fail to exercise the loader, remain non-repeatable, or introduce prohibited nondeterministic CI and broader Spacedock ownership."
  recommendation: "Authorize implementation of exactly one repo-local stage-boundary evaluator and one tracked Q08 fixture; retain the stated direct mechanical assertions, retire only the three overlapping self-mutants and their helper indirection, add the README Proof Policy stage-boundary rule, and require the specified paired validation before any passing claim."
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: "FO may dispatch the bounded work, account for required evidence, and operate state and delivery mechanics; FO does not adjudicate the result, alter scope, or advance without the EM/gate conditions."
  engineering_judgment:
    question: "Whether to proceed with one repo-local stage-boundary evaluator plus one tracked Q08 fixture under the stated implementation and validation boundaries."
    revision: "origin/main ec699d3e5b21e666209f079c9df7a9bd45528f13"
    evidence_synthesis: "At origin/main ec699d3e5b21e666209f079c9df7a9bd45528f13, installed Spacedock 0.26.0 contract 3 produced distinct, byte-recorded implementation-stage outputs for known-bad base a18ba78 and current ec699d3, establishing that exact-ref snapshot materialization through show-stage-def is feasible. Historical Q08 results support the targeted failure mode but are not acceptance evidence; acceptance remains conditional on three fresh same-runner trials per arm with a hidden rubric. The evaluator records provenance and exact output bytes and hashes while remaining model-free and Markdown-parser-free. Deterministic CI retains direct assertions for every unique mechanical invariant. Material limits are that the evaluator and fresh paired trials do not yet exist, and absence of a premature-load failure in the known-bad arm must remain UNKNOWN rather than being interpreted as success."
    adjudications:
      - finding: "route-sufficiency"
        disposition: supported
        basis: "The ideation route requires the fastest path and smallest cut that protects accepted value. One evaluator and one fixture form one independently releasable measurement surface; the full corpus, runner/grader, Spacedock changes, model CI, and activation changes are expressly excluded."
      - finding: "loader-boundary"
        disposition: supported
        basis: "The observed installed Spacedock 0.26.0 contract 3 outputs for both exact revisions demonstrate that materialized docs/dev snapshots can be evaluated through dispatch show-stage-def for implementation. Recording exact bytes, hashes, executable provenance, SHAs, prompts, and a manifest binds the behavioral evidence without substituting a Markdown parser."
      - finding: "conservative-test-retirement"
        disposition: supported
        basis: "The retained direct assertions continue to enforce exact implementation Policy mods, inactive-locator text, all four trigger facts, and the pre-trigger unread boundary. Retiring only premature-load, trigger-loss, and locator-loss self-mutants removes duplicate string-matcher demonstrations; locator-loss is additionally covered by the existing topology locator/predicate assertion."
      - finding: "evidence-layer-separation"
        disposition: supported
        basis: "Mechanical CI remains deterministic, model-free, and Spacedock-free; the evaluator only captures real-loader artifacts; validation separately performs fresh hidden-rubric Q08 trials. The candidate requires zero hard failures and safety non-inferiority, while failure of the known-bad arm to exhibit the targeted defect yields UNKNOWN, preventing evidence-layer substitution."
      - finding: "scope-and-cost"
        disposition: supported
        basis: "The change is reversible and bounded to repository evaluation support and Proof Policy documentation. PRODUCT and ARCHITECTURE remain unchanged, and the proposal creates no Spacedock modification, mandatory per-commit model cost, full-corpus maintenance burden, or activation-semantic change."
    risk_tradeoff: "The benefit is repeatable evidence at the real loader boundary, which phrase checks cannot provide. The principal risk is mistaking environment-bound or model-variable results for deterministic contract proof; exact binary, version, path, SHAs, prompts, bytes, hashes, manifests, same-runner pairing, and the explicit UNKNOWN rule contain that risk. Durable cost is one small evaluator, one fixture, and validation-time trial execution. The cheaper alternatives either fail to exercise the loader, remain non-repeatable, or introduce prohibited nondeterministic CI and broader Spacedock ownership."
    recommendation: "Authorize implementation of exactly one repo-local stage-boundary evaluator and one tracked Q08 fixture; retain the stated direct mechanical assertions, retire only the three overlapping self-mutants and their helper indirection, add the README Proof Policy stage-boundary rule, and require the specified paired validation before any passing claim."
    route: proceed
    confidence: high
    dissent: ""
    disproof_condition: "Change the route to return if exact-ref snapshot materialization or installed-loader invocation cannot be made reproducible with complete provenance, if any retained direct assertion is lost, or if validation produces a candidate hard failure or safety regression. Record validation evidence as UNKNOWN if the known-bad base shows no premature-load hard failure across its three fresh paired trials."
    authority_boundary: "This advisory route grants no implementation admission, policy edit, gate transition, provider posting, delivery, merge, or closeout authority. The captain retains scope and irreversible decisions; Gate Authority retains advancement and verdict ownership; work-item and delivery owners retain state and shipment authority."
```

## Stage Report: ideation

Verdict: **PROCEED** with the bounded real-loader evaluator; Gate Authority
retains the stage transition.

- DONE: Re-anchored to fresh `origin/main`
  `ec699d3e5b21e666209f079c9df7a9bd45528f13` and verified installed Spacedock
  0.26.0 contract 3.
- DONE: Reproduced exact known-bad/current loader hashes and byte sizes through
  `show-stage-def`; no parser or product edit was needed for the spike.
- DONE: Compared five routes and selected the smallest one that consumes
  installed Spacedock output without reimplementing its loader.
- DONE: Separated deterministic CI, installed-loader stage integration, and
  validation-only nondeterministic agent pressure with independent falsifiers.
- DONE: Mapped every proposed test removal to a retained enforcement point and
  narrowed retirement to three duplicate self-mutants plus helper indirection.
- DONE: Recorded one-worker scope, appetite, tolerance, cut line, pre-mortem,
  doc disposition, explicit non-goals, and a fail-closed `UNKNOWN` outcome when
  the known-bad arm does not discriminate.
- DONE: Ran the required ideation AC scan. It reported `citations=0` for AC-1
  through AC-5 despite the explicit citations below, matching the known local
  counter hazard recorded in `docs/dev/ROADMAP.md`; the discrepancy is retained
  as tool evidence and is not treated as an AC-content finding.
- DONE: Obtained exactly one completed fresh EM verdict: `proceed / high`, no
  dissent, with no second model recommended.

### Ideation checklist and AC citations

Evidence for AC-1: current direct activation enforcement at
`../../scripts/kc-dev-flow-contract-test.py:1384`.

Evidence for AC-2: prior installed-loader observation at
`_archive/loader-native-stage-contract.md:413`.

Evidence for AC-3: prior Q08 receipt audit at
`_archive/loader-native-stage-contract.md:451`.

Evidence for AC-4: current self-mutant block at
`../../scripts/kc-dev-flow-contract-test.py:1424` and the overlapping topology
locator check at `../../scripts/kc-dev-flow-contract-test.py:1004`.

Evidence for AC-5: current local Proof Policy at `../README.md:136` and the
scope boundary in this report at `loader-native-workflow-eval.md:191`.

### Summary

Proceed with one exact-ref real-loader capture adapter and one tracked Q08
fixture. Keep CI deterministic and retain every unique mechanical invariant;
run fresh paired agent pressure only at validation, and restore the retired
self-mutants if the known-bad arm does not discriminate.

## Stage Report: implementation

Verdict: **EXACT CANDIDATE CAPTURED; VALIDATION REQUIRED** at
`7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5` against merge base
`ec699d3e5b21e666209f079c9df7a9bd45528f13`. Gate Authority retains the
transition. AC-3 model pressure was not run in implementation, so this report
does not claim behavioral PASS.

- DONE: Added one repository-local exact-ref capture adapter that materializes
  `docs/dev` with Git, calls one resolved installed Spacedock executable, and
  publishes only after both implementation-stage captures and prompts close.
- DONE: Added one focused deterministic test with a fake executable and wired
  it into the existing model-free contract suite.
- DONE: Promoted only Q08's response contract, scenario, hard-failure rule, and
  required behavior into one closed tracked fixture. Runner prompts omit the
  hidden grading fields and base/candidate identities.
- DONE: Replaced `implementation_activation_errors` with direct checks for the
  exact implementation mod set, inactive-locator rule, all four trigger facts,
  and the pre-trigger unread boundary. Removed only `premature-load`,
  `trigger-loss`, and `locator-loss`; the earlier topology locator/predicate
  assertion remains.
- DONE: Captured both exact refs through installed Spacedock and independently
  reproduced both outputs from fresh local clones with byte-for-byte equality.
- NOT RUN: Six validation-only Q08 model trials, hidden-rubric grading, EM
  review, provider posting, push, PR creation, readiness, or merge.

### RED/GREEN and mutation evidence

- Initial adapter RED: `loader eval test: capture adapter is missing`.
- Minimum adapter GREEN: `kc-dev-flow loader eval test: PASS`.
- Installed-runtime RED: the first candidate rejected the real multiline
  `spacedock --version` output. A focused multiline-version case reproduced the
  failure; the adapter now validates and records only the canonical first-line
  identity, while malformed first lines remain rejected.
- Final GREEN: the focused test and its invocation from
  `scripts/kc-dev-flow-contract-test.py` both pass at the exact candidate.
- Must-fail mutation audit over the full contract suite:
  - extra implementation policy mod -> `implementation entry policy mods drifted`;
  - inactive-locator wording loss -> `missing inactive locator rule`;
  - `candidate revision` loss -> `missing candidate revision trigger`;
  - `changed-file map` loss -> `missing changed-file map trigger`;
  - `merge-base diff size` loss -> `missing merge-base diff trigger`;
  - `independent/dependent slice assessment` loss -> `missing slice assessment trigger`;
  - pre-trigger unread sentence loss -> `missing pre-trigger unread boundary`;
  - topology locator loss -> `workflow README does not point to the authoritative topology predicates`.

### Changed-file to AC map

| Changed file | AC | Responsibility |
|---|---|---|
| `scripts/kc-dev-flow-loader-eval.py` | AC-1, AC-2 | Exact-ref materialization, installed-loader invocation, exact bytes/hashes, provenance, opaque prompts, and fail-closed publication. |
| `scripts/kc-dev-flow-loader-eval.test.py` | AC-1, AC-2 | Deterministic fake-loader coverage for exact refs, bytes, hashes, version/path provenance, prompt separation, closed fields, rejection paths, and failed publication. |
| `scripts/fixtures/kc-dev-flow-loader-eval/q08.json` | AC-1, AC-3 | One durable Q08 response/scenario/grading contract; grading fields stay out of runner prompts. |
| `scripts/kc-dev-flow-contract-test.py` | AC-1, AC-4 | CI entry for the focused test and direct enforcement of every unique activation invariant after the three mapped self-mutants are removed. |
| `docs/dev/README.md` | AC-5 | Proof Policy separates deterministic checks, installed-loader capture, and validation-only pressure and names the operator command. |

No PRODUCT, ARCHITECTURE, Spacedock source, workflow stage/state, mod, provider,
generic runner/grader, or CI workflow file changed.

### Installed-loader receipt

Receipt root:
`/tmp/kc-dev-flow-loader-eval-implementation.ucon7c/capture`.

- Tool: `/opt/homebrew/Caskroom/spacedock/0.26.0/spacedock`,
  `spacedock 0.26.0 (contract 3)`.
- Fixture SHA-256:
  `58a4553447e84fe6d8cc5ea1ba13e73ecb7f446aa66e751323ce9dc9a28f6550`.
- Known-bad `a18ba78f72c03036d8463629bd19977aa684e159`: 27 lines,
  1616 bytes, SHA-256
  `c85143915d110cd7937a967b9fed32fc4c799ec5ef151e9b24438bd15df23dad`.
- Candidate `7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5`: 33 lines,
  1934 bytes, SHA-256
  `4f10401f127e77cf12bf23d7fcf70b626e082eca2f4579d3a76468dc1bf7a965`.
- Independent-clone direct invocations matched each captured stage with
  `cmp` exit 0. Manifest SHA-256:
  `9c0db52673de191c353aaeef0995495bf5239a0196db05424a6a87a3ffe1313b`.

### Exact-head deterministic gates

- `python3 scripts/kc-dev-flow-loader-eval.test.py` -> PASS.
- `python3 scripts/kc-dev-flow-contract-test.py` -> PASS.
- `./scripts/skill-frontmatter-lint.sh` -> 40/40 valid.
- `python3 -m py_compile` for the adapter, focused test, and contract test ->
  exit 0.
- `git diff --check origin/main...HEAD` -> exit 0.
- Exact code worktree status -> clean, branch ahead of `origin/main` by the
  single candidate commit.

### Delivery topology

The merge-base diff is 5 files, 753 additions, and 62 deletions: 815 gross
changed lines. Mechanical/test/support lines remain included; generated,
vendor, and lock-file changes are zero. The adapter, fixture, focused test,
contract integration, and Proof Policy form one dependent verification surface,
not two green layers that can land bottom-to-top and not multiple independent
green slices. Therefore the authoritative predicates are `dependent=no`,
`independent=no`, `numeric=no`, and the required topology is **One Draft PR**.
Implementation performed no delivery action.

### Summary

Built and committed the bounded loader-native Q08 capture surface, retained
every unique deterministic activation guard, removed only the three mapped
self-mutants/helper indirection, and bound exact known-bad/candidate bytes to a
real installed-Spacedock receipt. Fresh paired Q08 model pressure remains the
validation stage's required behavioral evidence.
