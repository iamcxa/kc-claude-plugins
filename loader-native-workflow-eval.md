---
title: "kc-dev-flow: make workflow changes measurable through the real loader"
status: validation
source: "captain:conversation-2026-08-12-second-slice"
product: kc-dev-flow
sprint:
started: 2026-08-12T05:46:00Z
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-loader-native-workflow-eval
issue:
pr: iamcxa/kc-claude-plugins#216
mod-block: merge:pr-merge
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

## Stage Report: validation

Verdict: **PASSED** for exact candidate
`7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5` against merge base
`ec699d3e5b21e666209f079c9df7a9bd45528f13`. This report records the
validator's verdict and evidence; it performs no status transition, delivery,
push, PR, readiness, merge, archive, or closeout action.

- DONE: Reviewed exact candidate `7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5`
  over `ec699d3e5b21e666209f079c9df7a9bd45528f13` against all five accepted ACs;
  all five changed files were read completely and the candidate remained clean
  and unchanged.
- DONE: Independently reproduced both exact installed-Spacedock stage captures
  and ran the same-config six-trial opaque Q08 pair; candidate passed 3/3 at
  12/12 with zero hard failures, known-bad reproduced one target hard failure,
  and the fail-closed `UNKNOWN` condition was therefore not triggered.
- DONE: Rechecked the deterministic suite and the bounded test-retirement map,
  obtained exactly one fresh EM verdict (`proceed / high`,
  `multi_model: not_needed`), and performed no product or delivery action.

### Per-AC verdicts

- **AC-1 PASS:** The focused adapter test passed and the full contract suite
  invoked it successfully. A detached mutation audit made all eight retained
  invariants fail at their named enforcement points: exact implementation mod
  set, inactive-locator rule, all four candidate facts, pre-trigger unread
  boundary, and topology locator. Removing the adapter, fixture, or focused
  test separately failed at its named required-file/contract point.
- **AC-2 PASS:** Validator-owned capture through installed
  `/opt/homebrew/Caskroom/spacedock/0.26.0/spacedock` recorded known-bad
  `a18ba78f72c03036d8463629bd19977aa684e159` as 27 lines / 1616 bytes /
  SHA-256 `c85143915d110cd7937a967b9fed32fc4c799ec5ef151e9b24438bd15df23dad`
  and candidate as 33 lines / 1934 bytes / SHA-256
  `4f10401f127e77cf12bf23d7fcf70b626e082eca2f4579d3a76468dc1bf7a965`.
  Two independent `git clone --no-local --no-checkout` trees at the exact refs
  produced direct `show-stage-def` outputs equal to the captures with `cmp`
  exit 0 and identical hashes.
- **AC-3 PASS:** Six fresh opaque Q08 runs used one configuration: Codex CLI
  0.145.0, `gpt-5.6-sol`, high reasoning, read-only, ephemeral, ignored user
  config/rules, one isolated directory and distinct session per trial, zero
  command/tool items, and zero stderr. After outputs closed, the pre-registered
  hidden rubric graded the candidate 12/12 in all three trials with zero hard
  failures. The known-bad arm scored 12/12, 12/12, and 5/12; trial 3 instructed
  loading PR topology before the four trigger facts, reproducing the target
  hard failure. Candidate safety is non-inferior, so the fail-closed `UNKNOWN`
  rule is not triggered. The fresh EM independently regraded all six raw
  outputs and confirmed the same safety/discrimination result.
- **AC-4 PASS:** The exact diff removes only `premature-load`, `trigger-loss`,
  `locator-loss`, and their helper indirection. The earlier topology
  locator/predicate assertion and direct checks for every baseline condition
  remain. All eight retained-invariant mutations exited 1 for their expected
  reasons. A non-discriminating return condition did not occur.
- **AC-5 PASS:** The exact five-file map is complete: adapter and focused test
  serve AC-1/AC-2; fixture serves AC-1/AC-3; contract simplification serves
  AC-1/AC-4; Proof Policy wording serves AC-5. No PRODUCT, ARCHITECTURE,
  Spacedock source, stage/state/mod/schema, provider, CI workflow, general
  runner/grader, or unmapped file changed. The adapter and CI invoke no model.

### Evidence block

Lenses: behavior PASS 0 Material findings; contract/schema PASS 0; state/concurrency PASS 0 for fail-closed staging and atomic receipt publication; runtime/platform PASS 0 for exact Git refs and installed Spacedock identity; docs/policy PASS 0 for prompt/rubric separation and Proof Policy; delivery PASS 0 for exact base/head and no delivery action | Inputs: all five changed files read completely, exact merge-base diff, manifest/direct-loader artifacts, six raw Q08 JSONL/final receipts, full deterministic gates, eight invariant mutants, three without-it removals, and one fresh EM | Falsifiers: invalid/non-commit refs, same refs, output target reuse/inside checkout, missing/malformed tool and fixture, capture failure, prompt identity/rubric leak, each retained workflow mutation, candidate Q08 hard failure/score below 10, and nondiscriminating known-bad arm | security/privacy did not fire because the surface consumes trusted local repository refs and operator-owned output paths and adds no auth, secret, remote, or external-input boundary

Diff coverage: 83.58% (224/268 executable adapter statement lines observed by Python stdlib trace across the focused fake-loader suite plus one real exact-ref adapter invocation); the changed direct workflow assertions also executed in the passing full contract suite, while test/support and prose fixture lines are outside this executable-behavior denominator. This is statement-line coverage, not branch coverage.

Adversarial: PASS — eight detached full-suite workflow mutations each exited 1 with their named error; removing the adapter, fixture, and focused test each exited 1 at its named enforcement point; known-bad Q08 trial 3 reproduced the premature-load failure while all three candidate trials remained safety-eligible.

Cross-model: not_needed — the sole required fresh-context GPT-5.6 High EM returned `proceed / high`, no dissent, and no contested, irreversible, low-confidence, or unresolved call requiring a second model. Two auxiliary blind-grader CLI attempts emitted no grade and were terminated; their silence was not used as evidence.

E2E: PASS — the ideation-approved E2E boundary is the behavior-producing chain, not a browser: exact-ref materialization -> installed Spacedock 0.26.0 stage extraction -> fresh same-config Q08 worker decision. Both loader arms matched independent direct extraction and the paired worker sample discriminated the target behavior.

Origin re-observation: PASS — Reported scenario: a stage-loader revision should change whether a fresh implementation worker treats a readable PR locator as active before its four trigger facts | Originating runtime kind: installed Spacedock 0.26.0 stage extractor followed by fresh Codex implementation-worker decisions | Re-observation artifact/revision: manifest SHA-256 `9c0db52673de191c353aaeef0995495bf5239a0196db05424a6a87a3ffe1313b`, known-bad `a18ba78f72c03036d8463629bd19977aa684e159`, candidate `7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5`, and six sessions under `/tmp/kc-dev-flow-loader-eval-validation-cycle2.oWCsWW` | Equivalent-runtime rationale: same installed extractor and contract, exact ref bytes, frozen Q08 facts/response contract, one runner/model/reasoning/sandbox configuration, opaque runner prompts, fresh isolated sessions, and no tool calls reproduce the claim-producing chain | Falsifier kind: mutation | Result: the candidate left PR, validation, and recovery unread in 3/3 trials, while known-bad trial 3 loaded PR topology before its trigger

### Validator-owned receipts

Receipt root:
`/tmp/kc-dev-flow-loader-eval-validation-cycle2.oWCsWW`.

- Capture manifest SHA-256:
  `9c0db52673de191c353aaeef0995495bf5239a0196db05424a6a87a3ffe1313b`.
- Fixture SHA-256:
  `58a4553447e84fe6d8cc5ea1ba13e73ecb7f446aa66e751323ce9dc9a28f6550`.
- Paired grade receipt SHA-256:
  `d07dd767b4522a3bcb57575e37bb459d9ec8d41af925a3d4818b5a97a34ae452`.
- Mutation/without-it receipt SHA-256:
  `6ced1f3abdfca2a1768d63ad659fb2f5cac2cb39cad0b6f88a4881886f813f4f`.
- Runner: `/Users/kent/.npm-global/bin/codex`, `codex-cli 0.145.0`,
  SHA-256 `134063e133f0b4244fa3b251acf973d4fe4b4aeeacbdc135211bf480f59f1477`.
- Provider cost was unavailable in the JSONL receipts; exact session IDs,
  input/cached/output/reasoning tokens, wall times, event hashes, output hashes,
  and the shared non-fatal skills-context-budget warning are retained.

### Exact-head deterministic gates

- `python3 scripts/kc-dev-flow-loader-eval.test.py` ->
  `kc-dev-flow loader eval test: PASS`.
- `python3 scripts/kc-dev-flow-contract-test.py` ->
  `kc-dev-flow contract: PASS`.
- `./scripts/skill-frontmatter-lint.sh` -> 40/40 valid.
- `python3 -m py_compile` for adapter, focused test, and contract test -> exit 0.
- `git diff --check ec699d3..7ff2092` -> exit 0.
- Search for the retired helper/mutant identifiers -> no match.
- Exact candidate worktree -> clean, one commit ahead of `origin/main`.

### Fresh Science Officer EM judgment

```yaml
science_officer_em_upward_report:
  em_judgment: "The exact candidate satisfies the accepted validation criteria against the stated merge base. The evidence supports proceeding through the repository's existing gate and authorized Draft-PR delivery route."
  evidence_synthesis: "Fresh inspection bound the clean worktree to candidate 7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5 and merge base ec699d3e5b21e666209f079c9df7a9bd45528f13. The five-file diff maps completely to AC-1 through AC-5. Fresh deterministic runs passed the focused loader-evaluation test, full kc-dev-flow contract test, 40-file frontmatter lint, and diff check. Installed Spacedock 0.26.0 contract 3 freshly reproduced both captured stage hashes; independent exact-ref trees matched the captured bytes. Six frozen Q08 outputs have distinct sessions, matching output hashes, zero stderr, and no command/tool items. Independent regrading against the hash-matched pre-registered rubric leaves every candidate trial at least 10/12 with zero hard failures; known-bad trial 3 explicitly loads the PR topology procedure before its four trigger facts and therefore reproduces the target hard failure. Eight invariant mutants and three without-it removals fail at their named enforcement points. Material limits are that the 83.58% figure is statement-line rather than branch coverage, provider cost is unavailable, and the auxiliary blind-grader attempts produced no grade record; the last limitation is contained by direct fresh EM regrading of all frozen outputs and is not an acceptance criterion."
  risk_tradeoff_call: "The benefit is repeatable evidence through the real installed loader plus behavioral discrimination that phrase checks alone cannot provide. The remaining risk is model variability and ongoing maintenance of one adapter, fixture, and validation-only trial procedure; exact revision/tool/rubric binding, fail-closed publication, retained deterministic invariants, and the known-bad discrimination rule bound that risk. The durable cost is proportionate to the single measurement surface. The cheaper alternative of retaining only text checks does not observe loader-produced behavior; if future paired trials stop discriminating, the concrete alternative is to return the candidate and restore the retired self-mutants rather than weaken the rubric."
  recommendation: "Gate Authority should accept validation only for exact candidate 7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5 against ec699d3e5b21e666209f079c9df7a9bd45528f13, then hand the authorized delivery owner the declared one-Draft-PR route. Any candidate, merge-base, loader, fixture, rubric, or evidence drift requires fresh validation before delivery."
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: "FO may account for evidence and perform state or delivery mechanics only when authorized by Gate and Delivery Authority; FO does not adjudicate, change scope, or derive posting or merge authority from this advisory record."
  engineering_judgment:
    question: "Should exact candidate 7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5 pass validation against merge base ec699d3e5b21e666209f079c9df7a9bd45528f13 for the accepted loader-native workflow evaluation?"
    revision: "7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5 against ec699d3e5b21e666209f079c9df7a9bd45528f13"
    evidence_synthesis: "Fresh inspection bound the clean worktree to candidate 7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5 and merge base ec699d3e5b21e666209f079c9df7a9bd45528f13. The five-file diff maps completely to AC-1 through AC-5. Fresh deterministic runs passed the focused loader-evaluation test, full kc-dev-flow contract test, 40-file frontmatter lint, and diff check. Installed Spacedock 0.26.0 contract 3 freshly reproduced both captured stage hashes; independent exact-ref trees matched the captured bytes. Six frozen Q08 outputs have distinct sessions, matching output hashes, zero stderr, and no command/tool items. Independent regrading against the hash-matched pre-registered rubric leaves every candidate trial at least 10/12 with zero hard failures; known-bad trial 3 explicitly loads the PR topology procedure before its four trigger facts and therefore reproduces the target hard failure. Eight invariant mutants and three without-it removals fail at their named enforcement points. Material limits are that the 83.58% figure is statement-line rather than branch coverage, provider cost is unavailable, and the auxiliary blind-grader attempts produced no grade record; the last limitation is contained by direct fresh EM regrading of all frozen outputs and is not an acceptance criterion."
    adjudications:
      - finding: "AC-1 deterministic invariants and focused adapter contract"
        disposition: supported
        basis: "Kernel Verification discipline requires a check seen to fail and AC-1 names exact manifest and activation invariants. Complete-file inspection, fresh focused/full-suite passes, and eight named mutation failures establish exact policy-mod selection, the inactive-locator rule, all four trigger facts, the pre-trigger unread boundary, exact bytes and hashes, closed provenance, prompt separation, rejection paths, and fail-closed publication."
      - finding: "AC-2 installed-loader stage-boundary equivalence"
        disposition: supported
        basis: "Kernel observation-boundary discipline requires same-kind runtime re-observation. The manifest binds Spacedock 0.26.0 contract 3, exact known-bad and candidate SHAs, fixture hash, byte counts, and stage hashes; fresh direct show-stage-def invocations over independent exact-ref trees reproduced c85143915d110cd7937a967b9fed32fc4c799ec5ef151e9b24438bd15df23dad and 4f10401f127e77cf12bf23d7fcf70b626e082eca2f4579d3a76468dc1bf7a965 byte-for-byte."
      - finding: "AC-3 paired Q08 behavioral discrimination"
        disposition: supported
        basis: "AC-3 and the pre-registered rubric require every candidate score to be at least 10/12, zero candidate hard failures, safety non-inferiority, and at least one target known-bad hard failure. Direct review of all six hash-bound raw outputs confirms three safety-eligible candidate responses and the known-bad trial-3 instruction to load delivery topology before its trigger; candidate safety is 0 versus 1 hard failures, so UNKNOWN is not triggered."
      - finding: "AC-4 bounded retirement with surviving enforcement"
        disposition: supported
        basis: "Outcome discipline permits subtraction only with surviving evidence. The exact diff removes only the three declared self-mutants and helper indirection, preserves the earlier topology-locator predicate check and direct activation assertions, and the detached mutation receipt demonstrates all eight retained invariants fail at their named enforcement points."
      - finding: "AC-5 scope and authority boundary"
        disposition: supported
        basis: "Route discipline and AC-5 prohibit added loader ownership, workflow authority, provider CI, general runner or grader, product architecture changes, and unmapped files. The exact five-file diff contains only the mapped README, fixture, contract simplification, adapter, and focused test; complete-file inspection found no provider/model execution in adapter or CI and no Spacedock source, workflow state/schema, PRODUCT, ARCHITECTURE, runner, grader, or CI-workflow change."
      - finding: "auxiliary blind-grader produced no grade record"
        disposition: supported
        basis: "The auxiliary blind-grader event streams contain only the shared context-budget warning. This is an evidence limitation, not a governing AC failure: responder prompts exclude the hash-matched hidden rubric and arm identity, frozen raw outputs predate grading, and this fresh EM independently applied the pre-registered rubric to every output."
    risk_tradeoff: "The benefit is repeatable evidence through the real installed loader plus behavioral discrimination that phrase checks alone cannot provide. The remaining risk is model variability and ongoing maintenance of one adapter, fixture, and validation-only trial procedure; exact revision/tool/rubric binding, fail-closed publication, retained deterministic invariants, and the known-bad discrimination rule bound that risk. The durable cost is proportionate to the single measurement surface. The cheaper alternative of retaining only text checks does not observe loader-produced behavior; if future paired trials stop discriminating, the concrete alternative is to return the candidate and restore the retired self-mutants rather than weaken the rubric."
    recommendation: "Gate Authority should accept validation only for exact candidate 7ff2092ec66b27f997b99cbcbdc9f6e33c2ce4a5 against ec699d3e5b21e666209f079c9df7a9bd45528f13, then hand the authorized delivery owner the declared one-Draft-PR route. Any candidate, merge-base, loader, fixture, rubric, or evidence drift requires fresh validation before delivery."
    route: proceed
    confidence: high
    dissent: ""
    disproof_condition: "Change the route to return if either exact revision drifts, direct installed-loader output no longer matches the captured bytes, a retained invariant mutation survives, a candidate Q08 trial scores below 10/12 or incurs a hard failure, the known-bad arm produces no target hard failure, paired configuration or hidden-rubric provenance cannot be bound, or prohibited or unmapped scope appears."
    authority_boundary: "This advisory record grants no task creation, sprint admission, scope change, policy edit, provider posting, gate mutation, stage advancement, PR creation, merge, archive, or closeout authority. The captain retains scope and irreversible decisions; Gate Authority retains the validation verdict and transition; work-item authority retains entity state; FO retains only authorized mechanics; Delivery Authority retains PR, readiness, merge, and release actions; provider owners retain any optional model invocation."
```

### Findings and residuals

No Material code-review finding survives. The paired sample remains
nondeterministic by design; exact identities and fail-closed discrimination
contain that risk without turning model pressure into per-commit CI. Provider
cost was unavailable, and two auxiliary blind-grader invocations returned no
grade; neither absence was treated as zero or PASS. One validator-owned mutation
harness initially stopped before execution because an exact README target
crossed a Markdown line break; correcting that temporary harness outside the
candidate led all eleven adversarial cases to run and pass.

### AC citation index

Evidence for AC-1: `../../../scripts/kc-dev-flow-loader-eval.test.py:127`, `../../../scripts/kc-dev-flow-contract-test.py:80`, and `loader-native-workflow-eval.md:514`.

Evidence for AC-2: `../../../scripts/kc-dev-flow-loader-eval.py:195`, `../../../scripts/kc-dev-flow-loader-eval.py:217`, and `loader-native-workflow-eval.md:520`.

Evidence for AC-3: `../../../scripts/fixtures/kc-dev-flow-loader-eval/q08.json:1` and `loader-native-workflow-eval.md:529`.

Evidence for AC-4: `../../../scripts/kc-dev-flow-contract-test.py:1412` and `loader-native-workflow-eval.md:539`.

Evidence for AC-5: `../README.md:136` and `loader-native-workflow-eval.md:544`.

### Summary

Passed the exact five-file candidate with validator-owned installed-loader
equality, a discriminating six-run Q08 pair, fresh deterministic and mutation
evidence, complete changed-file mapping, and one high-confidence EM
recommendation. The candidate remains unchanged and clean. Gate transition and
one-Draft-PR delivery remain separately authorized actions.
