---
title: "Teach agents to retain only comments with maintenance value"
status: implementation
source: "Captain-approved independent kc-dev-flow/S3 slice, 2026-08-15; does not alter the existing projection sequence"
product: kc-dev-flow
sprint: S3
started: 2026-08-15T12:03:26Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-comment-retention-discipline
issue:
pr:
mod-block:
design: required
lane: main
id: hpxks7c1kndqqhhr38kzna6q
---

## Problem

Agents have repeatedly produced code diffs where comments restate more code than they clarify. The portable kernel constrains absolute claims but does not require comments to preserve non-obvious maintenance value, so adopters lack a proportional rule that removes narration while retaining invariants, external constraints, hazards, and rejected alternatives.

This independent S3 slice must prove a behavior change through the installed loader within a 20-minute model-pressure cap, add no new skill, mod, linter, or standing model gate, and leave the existing projection sequence unchanged.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v1
  selected: production
  recommended: production
  basis: "A portable marketplace-released kernel changes long-lived authoring behavior for external adopters; it carries compatibility, release, rollback, and ownership obligations, while this slice changes no executable product behavior or external production state."
  obligations:
    architecture:
      - "Reuse the existing kernel authoring and minimality seam; add no skill, mod, linter, recurring gate, daemon, evaluator, or duplicate policy surface."
      - "Preserve the absolute-claim rule and keep the new comment-retention principle portable across languages and hosts."
    implementation:
      - "Keep canonical and vendored kernel copies byte-identical and record only the minimal independent S3 ROADMAP wording without changing projection sequence."
      - "Keep net always-loaded policy growth at or below roughly 50 words and aim near zero by rewriting existing minimality prose."
    testing:
      - "Run six paired installed-loader responses across three cases, repeating at most one ambiguous pair, within a 20-minute live-model cap."
      - "Require baseline redundant-comment retention at least once and candidate improvement without necessary-comment loss; otherwise report UNKNOWN or no-change."
      - "Run existing contract and release checks and verify no executable-behavior or test regression at the exact candidate revision."
  invariant_sources:
    - "docs/dev/_mods/kernel.md — authority, outcome, minimality, and verification discipline"
    - "docs/dev/README.md — Local Profile, Gate Authority, and state transaction"
    - "docs/dev/_mods/engineering-judgment.md — independent ideation recommendation and retained authority"
  scope_boundary: "No capability-scoped work-control-profile loading, repository-wide comment cleanup, language-specific style rules, RoboRev or PR-review policy change, new skill or mod, linter, recurring gate, daemon, generalized evaluator, or standing model run."
  promote_when:
    - "Re-enter ideation if the change gains executable enforcement, unattended model execution, language-specific policy, or external review-policy ownership."
  decision:
    authority: captain:kent
    at: 2026-08-15T12:03:26Z
```

## Ideation design

### Accepted bounds and criterion normalization

Protected value: agents produce maintainable code without comments that merely
narrate adjacent code, while preserving non-obvious invariants, external
constraints, hazards, and rejected alternatives.

Appetite: one ideation worker and one implementation worker. Behavioral pressure
uses the installed Spacedock loader and one ordinary-cost `gpt-5.6-terra`
high-reasoning worker. The correction has six fixed additional response slots
and no repeat. The three invalid calls remain accounted, so the cumulative total
may reach nine. The cumulative experiment stays within 20 minutes: 190 seconds
are consumed and at most 1,010 seconds remain for calls plus scoring.

Tolerance: no necessary rationale loss, executable-behavior change, or test
regression. Add no skill, mod, linter, recurring gate, daemon, general evaluator,
or standing model run. Keep net always-loaded policy growth at or below roughly
50 words and aim near zero. Comment volume may trigger review but is not a global
pass/fail ratio.

If cut, retain the existing absolute-claim rule and one portable comment-value
sentence. Explicit non-goals are capability-scoped `work-control-profile`
loading, repository-wide comment cleanup, language-specific style rules, and
RoboRev or PR-review policy changes.

The problem statement's protected value is retained as value. Production
compatibility, the 20-minute envelope, one bounded correction, exact projection
ordering, and the prohibited surfaces are Captain-imposed governing constraints.
The proposed kernel sentence is a mechanism and earns retention only through the
paired behavioral result below.

The assumption most likely to be wrong is that portable prose changes ordinary
agent behavior. A positive result therefore requires the exact baseline to
retain a known redundant comment at least once and the candidate to improve a
paired response without losing required rationale. Otherwise this item returns
`UNKNOWN` or no-change.

### Reverse recovery and subtractive result

Fresh `origin/main@004444c5501fc1ef32c9fe61ea616e8fdc3bc426`
already has the authoring and delivery seams:

- `kc-dev-flow/references/kernel.md:138-163` contains Outcome discipline and the
  absolute-claim authoring rule, including code comments.
- `kc-dev-flow/references/kernel.md:200-207` defines minimum and simple in the
  existing always-loaded minimality paragraph.
- `docs/dev/_mods/kernel.md` and the canonical kernel resolve to the same blob
  `cb0daf615fa642ce20eba7880d7ab6032f20d6a0`; the existing contract test checks
  their byte identity and the absolutes registry. An isolated exact-ref run of
  `scripts/kc-dev-flow-contract-test.py` passed.
- The installed `spacedock 0.26.0 (contract 3)` loader exposes exact stage text,
  but `show-stage-def` does not include the common kernel and is not by itself a
  valid treatment boundary.
- The installed `continue-dev-flow` ordinary-worker path requires the complete
  vendored kernel before the active stage and its declared mods. A captured tool
  trace and kernel digest, not stage bytes alone, must prove that read occurred.

The seam is `WORKING_UNIT_UNPROVEN / REQUIRED`: packaging, loading instructions,
and parity checks exist, but no bound baseline observation yet proves the stated
comment behavior. Its disproof hook is the exact-ref paired experiment; if the
baseline never retains a known redundant comment, no behavioral gap was
reproduced and the policy change is not earned. This is not a `MISSING`
capability and does not justify a new surface.

The smallest candidate edits the existing minimality paragraph in both
byte-identical kernel copies. Its proposed sentence is:

> Comments preserve non-obvious maintenance value—such as an invariant,
> external constraint, hazard, or rejected alternative—rather than narrate
> adjacent code.

The without-it arm is unmodified `origin/main`; the experimental with-it arm is
an exact implementation commit that differs only by that sentence in the two
byte-identical kernel copies. PRODUCT and ROADMAP wording is applied only after
the behavioral pair succeeds and never enters the experiment. If the without-it
arm already satisfies the behavioral ACs, or the candidate does not improve it,
ship no kernel rule. No fixture, scorer, runner, or model service is retained in
the repository.

### Fastest path and smallest cut

One implementation worker owns one independently releasable value surface:
capture the baseline through the actual ordinary-worker path, commit only the
kernel treatment, run its paired arm, and apply the minimal PRODUCT and ROADMAP
wording only after a positive result. The worker then executes existing
release/contract checks. The code-comment fixtures and outputs live outside the
repository and are discarded after their receipt is recorded.

There is no second slice: policy text and its behavioral proof cannot ship or be
blocked independently. This is docs/config/agent-instruction behavior, so a code
or browser E2E is not applicable; an installed `continue-dev-flow`
ordinary-worker run that proves the local kernel read is the real
behavior-producing boundary.

### Paired installed-loader experiment

Create six standalone non-git shadow roots with opaque names: baseline and
treatment for the redundant, necessary, and mixed cases. Installed Spacedock and
`continue-dev-flow` resolve only each shadow. Its task body contains only the
maintainability request and fixture; class/arm labels, candidate-as-proposal
wording, expected results, and rubric stay in a controller-only directory outside
the worker sandbox. The sentence appears only in the treatment kernel.

Before calls, retain Safehouse policy plus denial probes for the live entity,
product worktree, shared state, and controller rubric. Reject any git-linked
grant, readable target, or symlink escape. A byte diff must show each paired
shadow differs only by the sentence in `docs/dev/_mods/kernel.md`.

Use six fixed fresh-context `gpt-5.6-terra` high slots, one per case/arm. The
external manifest binds source and input digests, provider-native trace and
response digests, kernel digest, executable-token result, hidden score, and
elapsed time. A response counts only when retained tool events prove the complete
shadow-kernel read and matching SHA-256; reconstructed provenance is invalid.

No repeat, retry, auxiliary/grader model, or seventh response is authorized.
Calls plus scoring have 1,010 seconds remaining; cumulative elapsed is
`190 + correction_elapsed <= 1200`. Any invalid, missing, leaked, ambiguous,
non-improving, unaccounted, or late sample yields `UNKNOWN` and no product edit.

## Acceptance criteria

**AC-1 — The portable sentence improves redundant-comment removal in the bounded ordinary-agent baseline.**

Verified by: the six-response paired receipt binds `origin/main`, the exact
kernel-only treatment revision, installed loader and continuation-skill
identity, dispatch/stage/workflow/kernel bytes, tool-read evidence, three fixture
digests, opaque arms, `gpt-5.6-terra` high reasoning, and elapsed time. It proves
all effective instruction inputs except the proposed sentence are byte-identical.
The baseline retains at least one rubric-labeled redundant comment and the
candidate removes more redundant narration in at least one matched case without
a paired regression. Falsified by: either arm lacks a matching complete-kernel
read, the input diff contains another treatment, the baseline never retains
redundant narration, the candidate has no strict paired improvement, any arm
identity, case class, candidate-as-proposal wording, expected outcome, or hidden
rubric leaks through any model-readable path, task, workflow, or prompt, or the
run cannot finish honestly inside the response and cumulative time caps; the
result is then `UNKNOWN` or no-change.

**AC-2 — Necessary maintenance rationale is preserved with no executable change.**

Verified by: every candidate response for `N-necessary` and `M-mixed` retains
the frozen external-constraint, hazard, and rejected-alternative meanings, and a
token-aware comparison shows identical executable content. Falsified by: any
required meaning disappears, narration is merely rewritten as narration, or any
executable token changes. Semantic ambiguity is `UNKNOWN`; no repeat is
authorized.

**AC-3 — The shipped policy and documentation remain the smallest recovered surface.**

Verified by: the final diff changes the existing canonical/adopted kernel
paragraph, one PRODUCT sentence, and the independent S3 ROADMAP wording; the
kernel copies remain byte-identical, the existing absolute-claim rule remains,
and always-loaded policy growth stays roughly 50 words or fewer with a
near-zero target. Falsified by: a new skill, mod, linter, recurring gate, daemon,
general evaluator, standing run, capability-scoped work-control load, or an
unexplained additional product surface appears.

**AC-4 — Existing contract, release, authority, and S3 sequence behavior does not regress.**

Verified by: changed-file inspection contains no executable product change;
`scripts/kc-dev-flow-contract-test.py`, `scripts/marketplace-verify.sh`, relevant
release metadata checks, and exact-revision fresh validation pass; ROADMAP keeps
projection items 1 and 2 in the same order. Falsified by: any test failure,
canonical/adopted drift, hand-edited version metadata, executable behavior
change, or projection reorder.

### Proposed documentation diff

- In both kernel copies, add the single proposed comment-value sentence to the
  existing minimum/simple paragraph. Do not add a section or policy file.
- In `PRODUCT.md`, extend the existing `kc-dev-flow` summary with: “Its portable
  authoring discipline keeps comments for non-obvious maintenance value rather
  than adjacent-code narration.”
- In `docs/dev/ROADMAP.md` under `kc-dev-flow/S3`, add: “Independent lane (no
  sequence effect): `comment-retention-discipline` teaches portable
  maintenance-value comment retention and does not gate or reorder projection
  items 1–2.”
- `ARCHITECTURE.md` needs no change because this reuses the existing kernel,
  loader, parity check, release path, and ownership boundaries.

### Test and correction plan

1. Before product edits or calls, build opaque standalone shadow pairs, prove
   Safehouse denies the live entity/repository/state/rubric, and prove each pair
   differs only at the natural kernel sentence. Any failed preflight is
   `UNKNOWN` with zero additional calls.
2. Fill the six fixed baseline/treatment slots through installed
   `continue-dev-flow`, retaining provider-native tool traces and matching kernel
   digests. No repeat or seventh new response is authorized; calls plus scoring
   have 1,010 seconds remaining.
3. Only after a positive pair, apply the PRODUCT and ROADMAP wording. Run the
   existing kc-dev-flow contract, marketplace, frontmatter/version, and
   release checks. Record word-count and changed-surface observations without
   turning them into a new standing gate.
4. Fresh validation may authorize at most one bounded correction. Rejection
   after that returns to the Captain; it does not buy another model loop.

### Pre-mortem

If this design ships and agents still produce low-value comments, the likely
cause is that the sentence reads as style advice and loses to local imitation or
task pressure. The paired baseline/candidate result is the disproof instrument:
without a reproduced baseline defect and strict candidate improvement, do not
ship stronger prose or invent enforcement.

## Stage Report: ideation (cycle 1 — EM return)

- DONE: Recorded, committed, pushed, and re-read the Captain-approved
  `production` work-profile receipt before expanding acceptance criteria.
- DONE: Recovered the existing kernel authoring/minimality seam at fresh
  `origin/main@004444c5501fc1ef32c9fe61ea616e8fdc3bc426`; canonical and adopted
  kernels share blob `cb0daf615fa642ce20eba7880d7ab6032f20d6a0`, and the isolated
  exact-ref contract run passed.
- DONE: Reduced the design to one sentence in the existing kernel paragraph,
  minimal PRODUCT/ROADMAP wording, no ARCHITECTURE change, and no new policy or
  evaluator surface.
- DONE: Defined four falsifiable ACs and a six-response, three-case installed-
  loader experiment with one optional ambiguous-pair repeat and a 20-minute cap.
- FAILED: The fresh-context EM reviewed state commit
  `71e17fa76fac5158adeab3e7374db6866386ba8a` and artifact
  `sha256:8d27de8daa4a603a4d3e14be14fd92f09db92f796ce744c1685fac7f28c54e5c`,
  returning `return / high / multi_model:not_needed`. The recovered seam,
  no-new-surface design, no-change boundary, and S3 wording were supported; the
  stage-only experiment was rejected because its captured prompt omitted the
  kernel treatment.

### Summary

Return only the evidence design: the behavioral arm must prove that the actual
ordinary worker read the arm's complete vendored kernel, not merely the identical
implementation-stage output.

### Fresh EM verdict (cycle 1)

```yaml
engineering_judgment:
  question: "Whether comment-retention-discipline is sufficient to proceed as one implementation worker with the smallest recovered kernel edit, bounded paired installed-loader experiment, and minimal PRODUCT/ROADMAP wording while preserving the stated constraints."
  revision: "state artifact 71e17fa76fac5158adeab3e7374db6866386ba8a; artifact SHA-256 8d27de8daa4a603a4d3e14be14fd92f09db92f796ce744c1685fac7f28c54e5c; product comparison origin/main@004444c5501fc1ef32c9fe61ea616e8fdc3bc426"
  evidence_synthesis: "Artifact SHA-256 matches 8d27de8daa4a603a4d3e14be14fd92f09db92f796ce744c1685fac7f28c54e5c both on disk and in state commit 71e17fa76fac5158adeab3e7374db6866386ba8a; origin/main and the product comparison revision resolve to 004444c5501fc1ef32c9fe61ea616e8fdc3bc426, whose canonical and vendored kernels share blob cb0daf615fa642ce20eba7880d7ab6032f20d6a0. Installed spacedock is 0.26.0 contract 3. Its actual implementation-stage output contains only the implementation section and work-control-profile policy, not the kernel. The existing loader adapter captures that stage and builds runner prompts from only stage plus fixture scenario, so a kernel-only candidate produces no specified treatment in the six responses. The AC scan reports AC-1 through AC-4 as unevidenced with citations=0; the artifact nevertheless supplies explicit verification and falsifier conditions, and the ROADMAP records that this scanner citation count is not trustworthy."
  adjudications:
    - finding: F1
      disposition: supported
      basis: "Kernel Outcome discipline requires recovery of an existing seam and subtraction before addition. The exact comparison revision has the existing minimum/simple and absolute-claim seam, byte-identical canonical and vendored copies, and contract-test enforcement; the proposed edit reuses that paragraph and forbids a new skill, mod, linter, gate, daemon, evaluator, or standing run."
    - finding: F2
      disposition: unsupported
      basis: "Verification discipline requires an instrument able to fail on the asserted behavior and preservation of the behavior-producing boundary. `spacedock dispatch show-stage-def --stage implementation` omits the kernel, while `kc-dev-flow-loader-eval.py` sends only captured stage bytes and scenario to `runner_prompt`; the proposed candidate changes only the kernel. Therefore the specified paired inputs do not demonstrate that the worker received the treatment, so six responses and one repeat cannot falsify or establish the claimed policy effect."
    - finding: F3
      disposition: supported
      basis: "Kernel Outcome discipline requires value ACs with falsifiers and treats missing evidence as missing. AC-1 and AC-2 require a reproduced baseline defect, strict paired improvement, preserved rationale, unchanged executable tokens, and UNKNOWN or no-change on timeout, leakage, ambiguity, or non-improvement. The current unevidenced AC scan is explicitly not positive evidence and does not authorize the claim."
    - finding: F4
      disposition: supported
      basis: "The Local Profile assigns PRODUCT/ARCHITECTURE proposal to ideation and ROADMAP scheduling or strategy to the Captain or sprint commander. The artifact records Captain-approved independent S3 scope, preserves existing projection items 1 then 2, proposes no architecture mechanism, and maps the small documentation surface to AC-3 and AC-4; the implementation must keep the ROADMAP statement bounded to that approved order."
  risk_tradeoff: "The benefit is a one-sentence, portable refinement of an existing authoring/minimality seam with no retained evaluator or policy surface. The material risk is shipping or claiming a behavior improvement from an experiment whose baseline and candidate prompts are equivalent at the stated loader boundary; this can be avoided by returning only the evidence design to bind the actual worker context that loads the kernel, or by declining the claim when that boundary cannot be shown. The durable alternative is no kernel change."
  recommendation: "Amend the ideation artifact before implementation to name and capture the real ordinary-worker context that causes the complete vendored kernel to be read, prove that the baseline and candidate inputs differ only by the proposed kernel sentence, and retain the existing UNKNOWN/no-change outcome when that binding is unavailable; keep the one-worker, no-new-surface scope and bind ROADMAP wording to the approved S3 order."
  route: return
  confidence: high
  dissent: ""
  disproof_condition: "A reproducible installed ordinary-worker capture showing that both arms load the complete vendored kernel, with input manifests proving the candidate differs only by the proposed sentence and the hidden-rubric paired run remaining bounded, would remove F2 and could change the route to proceed."
  authority_boundary: "Captain Kent retains scope, ROADMAP strategy wording, irreversible decisions, and any acceptance of a changed experiment; Spacedock Gate Authority retains ideation advancement; work-item authority retains the artifact and ACs; the implementation worker may act only after those authorities accept the corrected design; the model provider supplies evidence only and has no gate or delivery authority."
```

## EM feedback disposition

- Retained the supported recovered seam, one-sentence kernel candidate,
  no-new-surface boundary, value/falsifier ACs, no-change alternative, and
  Captain-approved independent S3 wording.
- Rejected `show-stage-def` and the existing stage-only loader adapter as the
  behavioral boundary; both omit the kernel treatment.
- Bound every counted response to an installed `continue-dev-flow`
  ordinary-worker trace that proves a matching complete local-kernel read.
- Made the experiment causal: the treatment commit changes only the two
  byte-identical kernel copies, and every other effective instruction input must
  match. PRODUCT/ROADMAP wording follows only after a positive result.
- Added no response, retry, time, worker, policy, or retained evaluator surface.

## Stage Report: ideation (cycle 2 — final)

- DONE: Applied only the EM-required evidence-boundary correction; accepted
  value, scope, proposed product sentence, and explicit non-goals are unchanged.
- DONE: The installed ordinary-worker path now must prove the exact arm's
  complete kernel read through tool evidence and matching digests; stage-only
  capture is an invalid sample.
- DONE: The treatment commit is kernel-only and all other effective instruction
  inputs must be byte-identical; PRODUCT/ROADMAP changes happen after behavioral
  success and do not contaminate the pair.
- DONE: The three cases, six initial responses, one optional ambiguous-pair
  repeat, 20-minute cap, necessary-rationale guard, and `UNKNOWN/no-change`
  boundaries remain unchanged.
- DONE: `spacedock status --read comment-retention-discipline --ac-scan`
  enumerated AC-1 through AC-4 and reported `unevidenced=true citations=0`; this
  is recorded as pre-implementation evidence absence, not treated as a pass or
  as a finding from the ROADMAP's known-unreliable citation counter.
- DONE: The fresh-context EM reviewed state commit
  `0fe1b09f25ab7563182171d123677920c1dd143f` and artifact
  `sha256:40d53ffcc1792bf32a76335a6fadd4c28de6d1d3162cba284a662e42fddf8300`,
  returning `proceed / high / multi_model:not_needed` with all F1-F4 findings
  supported and the paired run retained as implementation-owned evidence.

### Summary

The bounded repair now measures the actual instruction consumer: no response
counts unless the ordinary worker demonstrably read the candidate or baseline
kernel, and the two arms differ only by the proposed sentence. Proceed as one
implementation worker; apply PRODUCT/ROADMAP wording only after a positive pair.

### Fresh EM verdict (cycle 2)

```yaml
engineering_judgment:
  question: "Whether the single bounded correction closes cycle-1 F2 so comment-retention-discipline may proceed as one implementation worker without a new policy or evaluator surface."
  revision: "state commit 0fe1b09f25ab7563182171d123677920c1dd143f; artifact SHA-256 40d53ffcc1792bf32a76335a6fadd4c28de6d1d3162cba284a662e42fddf8300; product comparison origin/main@004444c5501fc1ef32c9fe61ea616e8fdc3bc426"
  evidence_synthesis: "Artifact SHA-256 is 40d53ffcc1792bf32a76335a6fadd4c28de6d1d3162cba284a662e42fddf8300 both on disk and in state commit 0fe1b09f25ab7563182171d123677920c1dd143f; product comparison origin/main resolves to 004444c5501fc1ef32c9fe61ea616e8fdc3bc426, where canonical and vendored kernels share blob cb0daf615fa642ce20eba7880d7ab6032f20d6a0. The installed continue-dev-flow skill requires a complete vendored kernel read before stage policy. The corrected artifact rejects stage-only capture, counts a response only with an ordinary-worker tool trace and matching arm kernel digest, requires a kernel-only treatment commit and byte-identical other effective inputs, and retains explicit no-change and UNKNOWN outcomes. No behavioral result exists yet; that is the implementation experiment's evidence obligation."
  adjudications:
    - finding: F1
      disposition: supported
      basis: "Kernel Outcome discipline requires recovery and subtraction before addition. The exact product comparison contains the existing absolute-claim and minimum/simple kernel seam, its canonical and vendored copies are byte-identical, and the candidate is one sentence in that seam with no independent lifecycle surface."
    - finding: F2
      disposition: supported
      basis: "Kernel Verification discipline requires an instrument able to fail and observation at the behavior-producing boundary. Cycle 1 used stage-only bytes that omit the kernel; the correction instead invokes installed continue-dev-flow, which requires the complete vendored kernel, and rejects any response without trace evidence of that exact read, a matching digest, a kernel-only treatment commit, and a manifest showing every other effective input byte-identical. Missing evidence, mismatched input, or failed read is explicitly non-counting."
    - finding: F3
      disposition: supported
      basis: "AC-1 and AC-2 require a reproduced baseline defect, strict paired improvement, preserved external-constraint, hazard, and rejected-alternative rationale, and identical executable tokens. The design preserves three cases, six initial responses, at most one ambiguous matched-pair repeat, a maximum of eight responses, and a 20-minute envelope with UNKNOWN or no-change for timeout, leakage, ambiguity, missing output, or non-improvement."
    - finding: F4
      disposition: supported
      basis: "The valid Production receipt retains long-lived compatibility and release obligations while prohibiting added workflow surfaces. PRODUCT and ROADMAP changes are expressly post-positive-pair, ARCHITECTURE has no proposed change because ownership and runtime seams are reused, and the ROADMAP wording is bounded to an independent S3 lane that neither gates nor reorders projection items 1 then 2."
  risk_tradeoff: "The benefit is a causal, bounded observation of one existing kernel seam with no retained runner, scorer, linter, skill, mod, gate, daemon, or evaluator. The material risk is treating an unexecuted or incompletely bound run as proof; the trace/digest, input-manifest, response, retry, and time failures now resolve that risk to UNKNOWN or no-change. The durable alternative remains no kernel change."
  recommendation: "Proceed to the one-worker implementation experiment exactly as recorded: reject any response lacking complete-kernel read evidence or an identical-input manifest, make only the kernel treatment before a positive pair, and apply PRODUCT and ROADMAP wording only after that result."
  route: proceed
  confidence: high
  dissent: ""
  disproof_condition: "Return or block the route if the installed ordinary-worker run cannot emit complete local-kernel read evidence and a matching digest, if any other effective input differs between arms, if the cap is exceeded, or if the paired result loses necessary rationale, changes executable tokens, lacks a reproduced baseline defect, or lacks strict improvement."
  authority_boundary: "Captain Kent retains scope, Production obligations, PRODUCT and ROADMAP strategy wording, and irreversible decisions; Spacedock Gate Authority retains ideation advancement; work-item authority retains the artifact and ACs; Spacedock FO retains dispatch and state mechanics; the implementation worker performs only the accepted bounded experiment; provider output is evidence only and has no gate, delivery, or policy authority."
```

## Stage Report: implementation — UNKNOWN, no product change

- `UNKNOWN`: stopped after three baseline provider responses. The test prompts
  exposed the frozen case classes in fixture paths (`R-redundant`,
  `N-necessary`, and `M-mixed`), and the required ordinary-worker entity read
  exposed the candidate sentence and hidden scoring rubric. AC-1 declares that
  leakage non-counting, so no response can enter the paired receipt.
- `UNKNOWN`: the outer JSON event capture also did not retain a matching kernel
  digest line for every response even though complete local-kernel reads were
  observed. The strict exact-arm provenance bar therefore remains unmet.
- DONE: stopped all model work before treatment. No retry was used because the
  accepted design permits a repeat only for semantic scorer ambiguity, not for
  prompt/provenance defects. Total provider responses: 3 of the maximum 8.
- DONE: made no product edit or commit. The assigned branch remains at
  `004444c5501fc1ef32c9fe61ea616e8fdc3bc426`; canonical/adopted kernels,
  `PRODUCT.md`, `docs/dev/ROADMAP.md`, `ARCHITECTURE.md`, versions, release
  metadata, workflow policy, and the user-owned untracked file remain untouched.
- DONE: re-observed PR #240 as open and Ready at
  `8af38c437201abf2f47fbbc3966af028c80daa2e`, with
  `docs/dev/ROADMAP.md` in its file set. No projection wording was copied,
  stacked, or absorbed.

### Dispatched checklist

1. `FAILED` — Produce a valid exact-arm ordinary-worker receipt. The baseline
   responses crossed an invalid behavior-producing boundary: fixture paths and
   the live entity leaked the hidden classification/candidate, and matching
   per-response kernel-digest provenance was not retained. The result is
   `UNKNOWN`, not a countable baseline or positive pair.
2. `SKIPPED` — Apply the positive-pair-gated documentation diff. No positive
   pair was earned, so the canonical/adopted kernel sentence, `PRODUCT.md`, and
   independent S3 `docs/dev/ROADMAP.md` wording were not changed.
3. `SKIPPED` — Commit and verify an exact candidate. No candidate revision or
   product diff exists, so contract/release checks, changed-file-to-AC mapping,
   RoboRev observation, and delivery-topology loading were not earned.

Route: `return to ideation for Captain-approved experiment correction`.

### Bounded experiment receipt

```yaml
experiment:
  result: UNKNOWN
  product_change: none
  clock_start: 2026-08-15T12:40:16Z
  scoring_complete: 2026-08-15T12:43:26Z
  elapsed_seconds: 190
  provider_calls:
    model: gpt-5.6-terra
    reasoning: high
    codex_cli: 0.147.0
    completed: 3
    baseline: 3
    treatment: 0
    maximum: 8
  arm:
    opaque_id: arm-7m3q
    revision: 004444c5501fc1ef32c9fe61ea616e8fdc3bc426
    kernel_sha256: 300149e43cf2bc3c548fbdae750a90d305869280af5517436932741047210473
  loader:
    spacedock: "0.26.0 (contract 3)"
    continue_dev_flow_version: 2.5.0
    continue_dev_flow_sha256: 28c358633fd7a0d076c4175e783e1a872607627f814192b06bc51eb9877b959f
    dispatch_sha256: 9580de96cc07d7477ee3d81f6e583f533d580d9f67060ef78e9ab93df0aaba64
    implementation_stage_sha256: 2d60ff0b2f1303390d87ce67c987d9f126c902530b0bfee8665aeb64983e7f78
    workflow_readme_sha256: e7bc979d867b79f2669326cd164a74b70e50d326ef087f5db9c7588105b9df5d
    work_control_profile_sha256: 2cbe5de8dbebbd88f8d200b8fa7c87b740ed6a8b5efe27ee53eec3a2a0089a81
  cases:
    - id: R
      fixture_sha256: b67c98373da4174600725a17e0c13ccad78a990a18846fb817144f2d249fe6e7
      output_sha256: a304bb68f2495fccf716673809c8db148da0e7b9aa0ed34a6aa3f22343657ea6
      executable_tokens_identical: true
      observed_comment_result: "removed both adjacent-code narration comments"
      counted: false
    - id: N
      fixture_sha256: d96c94497e514fd89347ef0085f4f4aca91a4ee7e0138114d8fb815fe622e74b
      output_sha256: 4fda36a6cf331663030a5d221908e334479481e5516ae9abc6333b2273938ada
      executable_tokens_identical: true
      observed_comment_result: "retained both wire-compatibility and caller-array rationales"
      counted: false
    - id: M
      fixture_sha256: 4b20b965481874b16ea1d38cdd67e390bc864eddcc4bcbc078a66011b7043834
      output_sha256: 6d4a543c9cf19b6b9e5940760e4015c0ace5aa658fe1db927bb80e54eb9774d4
      executable_tokens_identical: true
      observed_comment_result: "removed narration and retained the concurrency hazard/rejected-alternative rationale"
      counted: false
  falsifiers:
    - "fixture paths exposed the hidden case classification"
    - "the ordinary-worker entity read exposed the candidate and rubric"
    - "matching digest evidence was not retained for every response"
```

The raw, invalid model outputs and fixtures were kept only long enough to score
and hash this receipt, then discarded. Because no countable baseline exists,
the observed comment edits are not evidence for either no-change or treatment
benefit. A future attempt requires a Captain-approved experiment correction that
separates ordinary-worker authority loading from an opaque rubric without
changing the accepted cap or silently granting a retry.

### Summary

The behavior claim remains unproved. Prompt/rubric leakage and incomplete
per-response provenance invalidated all three baseline samples, so the worker
stopped inside the cap and left the product branch unchanged.

## Stage Report: ideation (cycle 3 — Captain-approved correction)

- DONE: The authoritative experiment above now uses opaque standalone shadows;
  model-readable tasks contain only the request and fixture, with hidden mapping
  and scoring outside a Safehouse boundary.
- DONE: The executable handoff is denial/diff preflight, six fixed traced calls,
  then external scoring. Each response needs a retained matching kernel digest;
  only a complete positive receipt earns product edits.
- DONE: Recorded six new slots, no repeat, nine cumulative calls at most, 190
  consumed seconds, and 1,010 seconds remaining. Every non-pass is
  `UNKNOWN/no-change`.
- DONE: Made no product edit, provider call, scope expansion, or new EM request;
  the assigned code branch remains clean at `004444c5501fc1ef32c9fe61ea616e8fdc3bc426`.
- DONE: AC scan enumerated AC-1 through AC-4 without claiming implementation
  evidence; bound work-context validation returned `PASS`.

### Correction receipt

```yaml
experiment_correction: {authority: captain:kent, prior_invalid_responses: 3,
  additional_response_slots: 6, repeat_or_retry_slots: 0,
  cumulative_response_ceiling: 9, prior_elapsed_seconds: 190,
  remaining_seconds: 1010, cumulative_elapsed_ceiling_seconds: 1200,
  model: gpt-5.6-terra, reasoning: high, nonpass: UNKNOWN}
```

### Summary

Implementation now has six opaque fixed slots and an isolated, digest-bound
ordinary-worker path. If that clean pair cannot finish within the remaining
1,010 seconds, the result is `UNKNOWN` and the product remains unchanged.

## Stage Report: implementation (cycle 2 correction) — UNKNOWN, no product change

- DONE: The no-call preflight passed before the correction clock started.
  Safehouse selected each standalone non-git shadow as the project/workdir
  grant, reported no common Git directory or linked-worktree grants, and denied
  direct and symlink reads of the product worktree, live state, and controller
  rubric. All symlinks were removed before dispatch.
- FAILED: Exactly six new fixed responses completed, but all six were invalid.
  The nested Codex read-only sandbox rejected every filesystem command before
  execution with `sandbox_apply: Operation not permitted`; every worker returned
  `BLOCKED`, and no retained trace contained a complete kernel read or matching
  kernel digest. Under AC-1 and the Captain-approved correction, none counts and
  the final result is `UNKNOWN`.
- SKIPPED: No positive matched pair exists, so the candidate sentence,
  `PRODUCT.md`, and independent S3 `docs/dev/ROADMAP.md` wording were not edited.
- SKIPPED: With no candidate revision, product checks, changed-file-to-AC
  mapping, PR #240/RoboRev observation, delivery-topology loading, and a product
  commit were not earned.

Route: `return to Captain; the authorized correction is exhausted`.

### Corrected bounded experiment receipt

```yaml
experiment:
  result: UNKNOWN
  product_change: none
  correction_clock_start: 2026-08-15T13:09:19Z
  calls_and_initial_scoring_complete: 2026-08-15T13:10:15Z
  correction_elapsed_seconds: 56
  cumulative_elapsed_seconds: 246
  cumulative_elapsed_ceiling_seconds: 1200
  provider_calls:
    model: gpt-5.6-terra
    reasoning: high
    codex_cli: 0.146.0
    prior_invalid: 3
    correction_completed: 6
    correction_counted: 0
    cumulative_completed: 9
    repeat_or_retry: 0
    cumulative_ceiling: 9
  prompt:
    sha256: 020fa882963549e946042a31fac65c4949579b6ff2154a432048bf4162b7ce2c
    model_readable_scope: "request and fixture only"
  loader:
    continue_dev_flow_version: 2.5.0
    continue_dev_flow_sha256: 28c358633fd7a0d076c4175e783e1a872607627f814192b06bc51eb9877b959f
  preflight:
    safehouse_version: 0.9.0
    isolated_policy_sha256: 9ff0d2fdeb13c9eef61a5e8a7801c0fc0d4efe611b47a9d64116cd7e900e8db2
    controller_deny_sha256: 6ef0ffdaa232b68d55873c48a4ba8eec0bf8cf560f5b23d7712f563b33160732
    capture_program_sha256: c9d16c41a6285b48d5b9f65fc88af14ad4293c0beca63b4ad32751862d72ab43
    trace_retention_probe_sha256: 1519251b1062dc71aac04deae5db105723af8a133f66c7607333540ff5e43875
    git_linked_grants: none
    live_product_read: denied
    live_state_read: denied
    controller_read: denied
    symlink_escape: denied
    paired_diff: "only docs/dev/_mods/kernel.md candidate sentence"
  shared_inputs:
    workflow_readme_sha256: 6b434c4044b910970a6125195ecd7d2dbb90dad14caf25b0f1b20b45fa26c4b2
    roadmap_sha256: 9afdee290b6f328054817d262444f0235237c5c22f5323a8e0d2a0d4ac1c2698
    work_control_profile_sha256: 2cbe5de8dbebbd88f8d200b8fa7c87b740ed6a8b5efe27ee53eec3a2a0089a81
    response_schema_sha256: b19cca5edc55eced90537b2293e150f27b381fb2c18ba3a2360e18284fdb5ff3
    baseline_kernel_sha256: 300149e43cf2bc3c548fbdae750a90d305869280af5517436932741047210473
    treatment_kernel_sha256: 06ca694e3c0d66fca90439829485ed0a9f8bd59ef275ea4f0124316c110ac207
  responses:
    - opaque_root: 17ab43
      hidden_assignment: R-baseline
      thread: 01a0058a-bec6-7840-a937-860903ccef5c
      task_sha256: 04e4f0e22d80c1e27adc749e804a25ad0e6be2ff923469841fc4e1053060e8a3
      trace_sha256: f8ad0fbc133915a95966d8563af30578734d3c41e4c8f34f78911e208e51b4bf
      stderr_sha256: 2b6aa4f0644b803be608b20f83c7edefcefca5179039e0ee9f98462fab3347ff
      elapsed_seconds: 27.755
      result: BLOCKED
      kernel_read: false
      counted: false
    - opaque_root: 83cf26
      hidden_assignment: R-treatment
      thread: 01a0058a-bebc-7840-a0df-cce99937c4b2
      task_sha256: 04e4f0e22d80c1e27adc749e804a25ad0e6be2ff923469841fc4e1053060e8a3
      trace_sha256: 66acb6aff6465113ad5bc6502bb4a65f6731c52f40990f25630f9c109c89da59
      stderr_sha256: a312a3a38c9da60e9b7ccbfe526715c460525b38218e122da2599c282b29b4b2
      elapsed_seconds: 26.116
      result: BLOCKED
      kernel_read: false
      counted: false
    - opaque_root: 29de71
      hidden_assignment: N-baseline
      thread: 01a0058a-beca-7c92-832b-296fd546d9cc
      task_sha256: d6859f2bb0f1e23db4d7f2700fa0ac4bb52ef7008b1201e43d09ae74fc3f38ed
      trace_sha256: 0d1f955b8b9be2c2f279b86c2fabfa5ef21d6bdc904328df61da24645704c099
      stderr_sha256: 4def3acf41456bab44639d1ce78ef9c75548f6751746416cdc8c8c2a814c00b1
      elapsed_seconds: 27.552
      result: BLOCKED
      kernel_read: false
      counted: false
    - opaque_root: 95fa08
      hidden_assignment: N-treatment
      thread: 01a0058a-bec7-7263-ace4-1048be25a0ff
      task_sha256: d6859f2bb0f1e23db4d7f2700fa0ac4bb52ef7008b1201e43d09ae74fc3f38ed
      trace_sha256: 69eff3231fe522bf82b1f118dad772494f79c837e242366b1f68e4076f8b0170
      stderr_sha256: 2e4e2e545501af0f1898fd9e0d4d781938b5cc76911c3e4d48d4ff8da8808d2a
      elapsed_seconds: 22.971
      result: BLOCKED
      kernel_read: false
      counted: false
    - opaque_root: 3bc614
      hidden_assignment: M-baseline
      thread: 01a0058a-bece-72e2-82c3-27dea60acb70
      task_sha256: 793eb0305ee2d4454d7fc63568ce58ae04ab41a928a01e942b42328511971283
      trace_sha256: e1658ae57291a95046fd41a86a90b60adf5b156799d4b62b4b0c041f9a904688
      stderr_sha256: 52bb72be4dda77857c7cab285b6fc742a9ca50bb84f04f54b62a277e4b27b08d
      elapsed_seconds: 25.152
      result: BLOCKED
      kernel_read: false
      counted: false
    - opaque_root: a640ed
      hidden_assignment: M-treatment
      thread: 01a0058a-beab-7340-b5db-edf51971d724
      task_sha256: 793eb0305ee2d4454d7fc63568ce58ae04ab41a928a01e942b42328511971283
      trace_sha256: 880a7d091f5269693e9089cedbbbc6b1e5ca366488cd6aed234d8bd151983e93
      stderr_sha256: 8e4384e2b79e37c3c6cdbd02dded5bfec9db7a61262344bf432ab9db27d2ad22
      elapsed_seconds: 23.361
      result: BLOCKED
      kernel_read: false
      counted: false
  falsifier: >-
    All six traces lack the required complete local-kernel read and matching
    digest because the nested Codex sandbox denied filesystem execution.
```

The six disposable shadows and controller artifacts were retained only through
hashing and receipt construction, then discarded. The assigned product branch
remains clean at `004444c5501fc1ef32c9fe61ea616e8fdc3bc426`; the user-owned
untracked `e2e-pipeline/scripts/measure-prose-load.sh` in the shared root remains
untouched.

### Summary

The correction satisfied isolation, causal-diff, trace-retention, call-count,
and time controls, but the actual ordinary-worker reads never executed. The
behavior claim therefore remains unproved, the authorized nine-call ceiling is
exhausted, and no product change was made.
