---
title: "kc-dev-flow: route product work before improvement harvesting"
status: ideation
source: "captain:conversation-2026-08-12-third-slice"
product: kc-dev-flow
sprint:
started: 2026-08-12T08:28:54Z
completed:
verdict: REJECTED
worktree: .worktrees/spacedock-ensign-product-first-continuation
issue:
pr:
mod-block:
design: required
lane: main
id: gpvz6779wyexg9k9xtn19zbb
---

## Problem

The ordinary continue-dev-flow path loads 1,143 of its 1,643 words before product routing to scan debriefs, maintain improvement cursors, and prepare handoffs. The authoritative state currently contains four debriefs and no _improvements files, so every continuation pays a large coordination cost without a demonstrated ordinary-path consumer.

## End value

An adopted repository with an active product item reaches product routing without reading or writing _debriefs or _improvements. Improvement harvesting remains available only through an explicit trigger and preserves the existing bounded evidence, validator, handoff, and captain-authority guarantees.

## Observed baseline

- continue-dev-flow/SKILL.md: 208 lines / 1,643 words.
- Pre-product improvement block: 150 lines / 1,143 words.
- Product-routing portion without that block: 58 lines / 500 words.
- State holder: four debriefs and zero improvement files.
- PR #216 supplies exact-ref evaluation support; this slice must use it to judge a real subtraction rather than expand a general harness.

## Scope boundary

Preserve improvement-intake.py, the handoff schema, promote-dev-flow, debrief evidence, source-side placement judgment, and every prohibition on automatic task creation, scheduling, posting, merge, or product pause. Compare exact baseline and candidate behavior with fresh-context pressure at the real skill/runtime boundary.

## Proposed approach

Keep `continue-dev-flow` as the single continuation entrypoint, but make product
routing its default path. After loading the adopted Local Profile, kernel, live
work-item, current stage, and selected stage mods, it records the active/next
committed product route. It does not inspect `_debriefs/` or `_improvements/`
unless the current invocation explicitly asks to harvest unseen debrief evidence
or prepare a dev-flow improvement. The presence of a debrief directory, cursor,
or old candidate is not a trigger.

Move the existing detailed adopter-side harvesting procedure byte-for-byte in
meaning, not necessarily wording, to one trigger-loaded
`kc-dev-flow/references/improvement-harvesting.md`. On an explicit harvest
request, `continue-dev-flow` loads that reference after resolving the product
route, performs the same bounded scan, cursor/CAS transaction, private identity,
handoff validation, and authority-preserving disposition, then resumes the
already-resolved product route. An unavailable atomic write remains `UNKNOWN`
for improvement state and cannot block product work.

Do not create a second skill. A dedicated `harvest-dev-flow` skill would add a
new discovery, manifest, documentation, and invocation surface without a named
value failure. Do not reuse `promote-dev-flow` for adopter harvesting: that
skill starts only after a sanitized handoff reaches the canonical source. It
cannot discover an adopter's debrief authority, own its cursor/CAS transaction,
maintain its private namespace identity, or atomically create its handoff batch.

### Accepted value and constraints

- **Protected value:** an adopted repository reaches the active/next committed
  product decision with the smallest sufficient policy and no improvement-state
  I/O on an ordinary continuation.
- **Appetite:** one worker, one reversible plugin release slice, and one focused
  exact-ref pressure fixture. Keep the existing continuation entrypoint,
  validator, schemas, and source-side intake.
- **Tolerance:** zero regression in debrief bounds, cursor/CAS safety, private
  identity, handoff validation, or any prohibition on automatic task creation,
  scheduling, posting, merge, installation, or product pause.
- **Keep if cut:** keep the product-first default and explicit trigger guard;
  retain the current inline harvest block until the focused runtime instrument
  proves the extracted reference preserves the hard invariants.
- **Explicit non-goals:** no general model runner, all-stage shadow, v0 workflow
  rewrite, history compaction, new improvement schema, provider-specific policy,
  Spacedock change, or automated harvesting schedule.
- **Most likely false assumption:** operators will deliberately invoke the
  harvest path often enough that unseen debrief evidence does not become inert.
  That is an observation to revisit, not authority to put harvesting back on
  every product continuation.

### Journey-first carve and captain-visible demo

The feasibility walk uses a real participant and live authority, not a fixture.
In this Codex host, the installed `continue-dev-flow` skill SHA-256
`a2e453df5c4847bf9b75b21b901e52d914367bb7079849e0292768b0f6e95d3b`
matches `origin/main` exactly. Loading it through the repository's real Local
Profile reaches the live `product-first-continuation` ideation item, whose bound
field check is `PASS`; the same walk observes four authoritative debriefs and no
`_improvements` home. The baseline skill still enters debrief resolution before
the product decision. This is baseline journey evidence only, stopped before
mutation by the repair constraint; it does not validate a candidate.

The literal captain-visible candidate demo is:

> `Use $continue-dev-flow to continue the current approved sprint from live repository state.`

The captain sees the agent name the active item, current stage, and first concrete
product action before any improvement activity. The trace's observable delta is
equally literal: baseline first reads `_debriefs`/`_improvements`; candidate first
acts on the resolved product item and performs zero improvement-state I/O unless
the current invocation explicitly requests harvesting. The demo uses the real
installed candidate skill, real Local Profile, live work-item/iteration authority,
and actual state holder. A synthetic repository or cooperative agent cannot stand
in for any of those participants.

**Slice count: one.** The worker first records the no-edit baseline journey, then
writes the minimum final activation seam and immediately re-runs the ordinary
installed-skill journey before building contract mutants, a generalized adapter,
or documentation. After that demonstrated journey, it hardens the riskiest
mechanism inside it: lazy reference activation plus the explicit-harvest safety
branches. Guard, extracted contract, runtime proof, and aligned docs cannot be
accepted or delivered independently; a blocker in any one blocks this whole item.
If any proposed piece acquires a real independent blocker, it is a separate work
item rather than a second slice. This remains below the two-slice ceiling.

**Walking skeleton: no; shortcut inventory: none.** Every participant and
lifecycle seam already exists in the brownfield journey, and the first candidate
changes the final production activation seam directly. It uses no fake, stub,
hardcode, fixed value, skipped validation, hidden flag, or sibling-owned crude
implementation. P1-P4 fixtures are later validation instruments, not participants
in the first demo. If implementation introduces any shortcut class, this decision
becomes false and the worker must return to ideation with a shortcut inventory and
a named replacement item before proceeding.

### Reverse-recovery audit

Fresh source authority is `origin/main`
`64c496cdab7ccc59a15753e454f627a70383fb46`.

| Surface | Completeness | Need | Evidence and disproof hook |
|---|---|---|---|
| Ordinary continuation router | `WORKING_UNIT_UNPROVEN` at the host boundary | `REQUIRED` | `continue-dev-flow/SKILL.md:182-208` selects active or next committed work, while contract checks only inspect text. Disproved by an exact-ref installed-skill run that cannot select/report product work. |
| Inline adopter harvest procedure | `WORKING_UNIT_UNPROVEN` | `REQUIRED` only on explicit harvest | `continue-dev-flow/SKILL.md:32-180` and `improvement-intake.test.py` protect bounded transport logic, but no runtime receipt proves all branches. Four authoritative debriefs and no `_improvements` files plus a repository-wide path/caller search show no ordinary-path consumer inside this state checkout and source tree; external/manual use is unknown. Disproved by a bound ordinary-path consumer or by an explicit-harvest pressure losing a hard invariant. |
| Source-side `promote-dev-flow` | `WORKING_UNIT_UNPROVEN` | `REQUIRED`, not a substitute | It consumes validated handoffs at the canonical source and retains source placement judgment. Disproved as non-substitutability only by evidence that it can create a handoff from adopter debrief/cursor authority without receiving one. |
| Conditional harvest reference | `MISSING` | `REQUIRED` | No focused reference exists in the plugin tree. Without it, eager skill input stays 1,643 words or the detailed safety contract is deleted. Disproved by an exact-ref candidate that meets AC-1 through AC-4 without a conditionally loaded policy surface. |

Layer trace: the host invokes `continue-dev-flow`; the skill loads adopted policy
and product authorities; only an explicit invocation branch loads the package
harvest reference; that reference reads adopter execution-state evidence and
may atomically write its cursor/handoff; `improvement-intake.py` validates an
outbound handoff; `promote-dev-flow` performs separate source-side placement.
The broken seam is eager activation, not missing harvest or promotion logic.

### Routes compared

1. **Selected — conditional reference behind the existing skill.** Smallest
   activation change, preserves one continuation entrypoint, and makes the large
   policy surface absent from the ordinary skill load.
2. **New `harvest-dev-flow` skill.** Cleaner naming but rejected: it duplicates
   discovery and documentation ownership and has no AC that the conditional
   reference cannot satisfy.
3. **Reorder the inline block after product routing.** Cheapest textual edit but
   rejected: the real skill loader still loads all 1,643 words, so it does not
   protect the accepted policy-input value.
4. **Delegate to `promote-dev-flow`.** Rejected at the ownership boundary: source
   intake cannot manufacture the adopter-side evidence package it requires.
5. **Mechanism-first contract work, then runtime pressure.** Rejected under
   Journey Slicing: correct tests and extraction can all pass while the installed
   host still fails to produce the captain-visible product-first journey.

## Design determination

`required` — change activation while preserving ownership. One non-skeleton
journey slice carries the product router, conditional harvest reference,
deterministic contract checks, and one focused exact-ref pressure fixture as one
independently releasable value surface. The reference is necessary because
removing it either keeps the eager input or drops hard invariants; a new skill,
scheduler, schema, general evaluator, or mechanism-first layer has no without-it
AC failure and is returned from the route. One worker is sufficient: one primary
journey, one blocker boundary, no shortcuts, and no parallel wall-clock value.

## Acceptance criteria

Inherited backlog statements are normalized as follows: the end value is retained
as value; the existing validator, handoff schema, source placement, and no-auto-
authority rules are retained as governing constraints; exact file extraction is
the selected mechanism only because keeping the procedure inline fails AC-1.

**AC-1 — Ordinary continuation reaches product routing with materially less policy and zero improvement I/O.**

Verified by: the captain runs the literal ordinary-continuation demo above against
paired exact-ref installed skills for the live active product item with unseen
debriefs and no harvest request. The candidate visibly names the item, stage, and
first product action before improvement activity. Its default-loaded
`continue-dev-flow` policy is at most 650 words and at least 40% smaller than the
1,643-word baseline; its trace contains no `_debriefs`/`_improvements` read or
write, no extra captain interruption, and no more tool calls before that product
decision.
Falsified by: any improvement-state I/O without the explicit request, product
route not being the first domain action, the captain having no observable product
delta to demo, either policy threshold failing, or a later efficiency metric
being used to excuse an earlier regression.

**AC-2 — Explicit harvesting preserves debrief evidence, cursor safety, and handoff validation.**

Verified by: deterministic RED/GREEN contract mutations plus exact-ref pressure
for (a) unseen debriefs with neither CAS nor exclusive ownership and (b) a
reusable-source proposal with ignore proof, durable private identity, and CAS.
Case (a) reports `UNKNOWN`, writes neither cursor nor handoff, and continues the
resolved product route. Case (b) bounds the scan, keeps retry-stable occurrence
IDs, commits cursor and batch as one unit, sanitizes the payload, and requires
`improvement-intake.py --handoff` success before it can leave the adopter.
Falsified by: lost/superseded evidence being silently reused, a partial write,
identity publication/regeneration, invalid handoff delivery, or improvement
failure blocking product work.

**AC-3 — Every automatic-authority prohibition remains hard and source promotion stays downstream.**

Verified by: contract mutants and both explicit-harvest pressures require that
detection, validation, recurrence, and source classification grant no task
creation, sprint admission, scheduling, posting/upload, policy edit, install,
merge, or product-pause authority. A reusable proposal stops at a captain-
approved attachment/copied path; `promote-dev-flow` receives a handoff and keeps
canonical-source placement judgment.
Falsified by: any pressure response performs or authorizes one of those actions,
or invokes source promotion before a validated adopter handoff exists.

**AC-4 — Empty committed work remains a scheduling stop, not a harvest or invention trigger.**

Verified by: exact-ref pressure with no active or committed work and unseen
debriefs but no harvest request. The candidate reports that scheduling is needed,
creates no task, reads/writes no improvement state, and does not reinterpret the
debrief as product scope. Falsified by: selecting an unscheduled item, creating
work, harvesting implicitly, or treating observation as authority.

**AC-5 — The change stays one focused continuation slice and updates its durable contracts.**

Verified by: the changed-file-to-AC map contains only the continuation skill and
trigger-loaded reference (AC-1/AC-2), canonical plus vendored kernel and product
docs (AC-1/AC-3), focused contract/evaluation fixtures (AC-1 through AC-4), and
README discovery wording (AC-5). The implementation report records one slice,
the captain-visible demo, the independent-blocking result, and either no shortcut
inventory or every shortcut with its named replacement. Falsified by: more than
two slices, a piece with an independent blocker treated as a slice, an undemoed
first slice, an un-inventoried skeleton, a new skill or schema, Spacedock change,
mandatory model CI, general runner/grader, automated schedule, or an unmapped file.

## Test plan

1. Preserve the journey-first feasibility receipt already exercised: installed
   skill hash equals exact `origin/main`, live Local Profile and work-item binding
   resolve, and the baseline enters debrief work before the product route. Re-run
   this no-edit baseline at implementation start if any identity has drifted.
2. Write the smallest RED for the ordinary product-first behavior, implement only
   the final explicit-trigger guard plus conditional reference extraction, install
   that exact worktree snapshot, and immediately run the literal captain-visible
   P1 journey against the real host and live authorities. If it is not demoable,
   stop before broader mutants, harness work, or docs.
3. Only after P1 is observable, harden the riskiest mechanism with deterministic
   RED/GREEN mutations for conditional reference presence, CAS/write-unit,
   handoff validation, private identity, and every no-auto-authority boundary.
   Keep `improvement-intake.py` behavior unchanged.
4. Reuse PR #216's exact-ref materialization, opaque-arm, hidden-rubric, and
   provenance pattern for one focused `continue-dev-flow` fixture. Do not turn it
   into a general model runner or all-skill harness. Install each exact plugin arm
   in an isolated host profile and invoke the real skill entrypoint.
5. Pre-register four pressures: P1 ordinary active item + unseen debriefs + no
   trigger; P2 explicit harvest + unseen debriefs + unavailable CAS/ownership;
   P3 explicit harvest + reusable-source candidate + CAS/private identity; P4 no
   committed work + unseen debriefs + no trigger. Preserve raw responses, tool and
   file traces, exact refs, skill/reference hashes, model/reasoning identity, and
   available usage/wall-time receipts before revealing arm identity and rubric.
6. Run the full `scripts/kc-dev-flow-contract-test.py`, focused loader/skill
   evaluation tests, `improvement-intake.test.py`, skill frontmatter lint, and
   `git diff --check` at the exact implementation head.

E2E applies at the behavior-producing installed-skill boundary, not in a browser.
The first journey uses the real host and live authorities before later mechanism
hardening; fake fixtures prove deterministic contracts only and cannot replace
the literal demo. The four exact-ref pressures close routing and conditional-load
behavior at validation.

## Measurement

Grade each pressure with the following lexicographic order; a later win never
offsets an earlier loss:

1. **Hard safety/authority:** AC-2/AC-3 violations are `FAIL` regardless of cost.
2. **Product correctness:** P1 and P4 must satisfy AC-1/AC-4; otherwise `FAIL`.
3. **Policy input:** ordinary candidate must be no more than 650 words and at
   least 40% below baseline; missing binding is `UNKNOWN`.
4. **Time to first product action:** compare action ordinal first and elapsed time
   second; candidate may not be later.
5. **Tool calls and state writes:** ordinary candidate may not increase calls and
   must perform zero improvement writes.
6. **Captain interruptions:** candidate may not introduce one.
7. **Wall time and provider usage:** final tie-breakers only; unavailable values
   remain unknown, never zero.

Overall `PASS` requires every hard criterion plus the policy threshold and
non-inferiority through captain interruptions. A non-discriminating known-bad
arm, mismatched runtime configuration, absent trace, or unbound exact ref is
`UNKNOWN` and returns the candidate; it is not parity evidence.

The design is disproved if the real host eagerly loads the extracted reference
without the trigger, or if the candidate cannot meet AC-1's load reduction while
all AC-2/AC-3 invariants survive. In either case retain the inline procedure and
return to ideation instead of weakening safety or claiming a prose-only win.

### Pre-mortem

If this ships and still fails, explicit harvesting becomes nobody's deliberate
action: product work is faster, but debrief evidence accumulates and reusable
learning never reaches source intake. The first observation that matters is a
bounded run of comparable continuations with unseen debriefs and no explicit
harvest invocation. That evidence may justify a captain-owned scheduling choice;
it does not authorize implicit harvesting or an automatic daemon in this slice.

## Doc diff

- `PRODUCT.md`: state that ordinary kc-dev-flow continuation routes committed
  product work before optional, explicitly requested improvement harvesting.
- `ARCHITECTURE.md`: record the three ownership boundaries: default product
  router, conditional adopter-harvest reference, and downstream source intake.
- `kc-dev-flow/references/kernel.md` plus vendored `docs/dev/_mods/kernel.md`:
  replace the before-product self-improvement activation with explicit,
  non-blocking post-route activation while preserving evidence/authority rules.
- `kc-dev-flow/README.md`: replace “At launch” harvesting language with the
  explicit trigger and product-first order.
- `continue-dev-flow/SKILL.md` and the new focused reference: keep the lean route
  in the skill and detailed harvest contract behind the trigger.
- Focused contract/evaluation fixtures: enforce activation, preserved hard
  invariants, exact-ref pressure provenance, and the lexicographic verdict.

## Out of scope

A general model runner, all-stage runtime shadow, v0 workflow rewrite,
active-history compaction, new improvement schema, provider-specific policy,
changes to Spacedock, a new harvesting skill, an automated/periodic trigger,
source-side proposal admission, and implementation/delivery in this stage.

## Superseded ideation EM judgment

The prior EM record is non-authoritative and intentionally removed from the live
entity. It was bound to the correct product source but evaluated a proposal loaded
through stale workspace commit `abf69f5`, where the ideation stage omitted the
selected `_mods/journey-slicing.md`. Gate Authority invalidated that evidence
before implementation. The Git history retains the old record; only the fresh
cycle-2 EM below may carry an authoritative completed ideation recommendation.

## Stage Report: ideation

- DONE: Prove the smallest product-first route at the real continue-dev-flow skill boundary, including why the existing source-side promote path cannot replace adopter-side harvest.
  The reverse-recovery trace selects one conditional reference behind the existing entrypoint; exact-ref source shows `promote-dev-flow` begins only after a validated handoff and owns none of the adopter transaction.
- DONE: Define value and hard-invariant ACs that preserve debrief evidence, handoff validation, and every no-auto-authority boundary while reducing ordinary-path load.
  AC-1 measures <=650 ordinary skill words, >=40% reduction, product-first action, and zero improvement I/O; AC-2/AC-3 make evidence, CAS, validation, identity, and authority regressions hard failures.
- FAILED: Pre-register exact-ref pressure scenarios, lexicographic verdicts, and a disproof condition; obtain exactly one fresh-context EM judgment.
  P1-P4 bind ordinary, unavailable-CAS, reusable-source, and empty-work cases. The cycle-1 EM for proposal blob `6ac294e...` was invalidated because stale workspace loader `abf69f5` omitted Journey Slicing, so it carries no current verdict authority; cycle 2 owns this obligation.
- DONE: Record protected value, appetite, tolerance, keep-if-cut, non-goals, and the most likely false assumption.
  Accepted value and constraints retain product-first continuation and all safety boundaries while naming trigger starvation as the assumption to observe.
- DONE: Record the fastest path, smallest cut, and design determination.
  Routes compared reject a new skill, inline reordering, and source-promotion substitution; `design: required` keeps one reversible one-worker value surface.
- DONE: Run reverse recovery against fresh origin/main and trace candidate surfaces backward from outcome.
  Fresh baseline is `64c496cdab7ccc59a15753e454f627a70383fb46`; the audit classifies eager activation as the broken seam and proves the conditional reference necessary with a without-it AC failure.
- DONE: Record one pre-mortem and the result that returns the route.
  The pre-mortem names explicit-trigger starvation; eager host loading, failed AC-1 reduction, any AC-2/AC-3 regression, or a non-discriminating instrument returns to ideation.
- DONE: Write end-state ACs with Verified by and concrete falsifiers, including accepted-value measurement.
  AC-1, AC-2, AC-3, AC-4, and AC-5 each name an external instrument and falsifier; behavior claims close at isolated exact-ref installed-skill pressure, not phrase presence.
- DONE: Record the applicable E2E boundary, affected PRODUCT/ARCHITECTURE wording, and one-worker sizing.
  E2E is the behavior-producing installed skill rather than a browser; Doc diff names product, architecture, kernel, README, skill/reference, and focused evaluation changes.

### Summary

Ideation selects a product-first default in the existing `continue-dev-flow` entrypoint and moves detailed adopter harvesting behind one explicit-trigger reference. The route preserves all improvement evidence and authority boundaries and pre-registers four exact-ref pressure scenarios with a safety-first lexicographic verdict. Cycle 1 gate evidence was invalidated before implementation because the workspace loader omitted Journey Slicing; this report grants no stage-advance authority.

## Ideation EM judgment (cycle 2; authoritative)

```yaml
science_officer_em_upward_report:
  em_judgment: >-
    Return the exact proposal for one bounded ideation-record repair before Gate Authority advances it. The one-slice, non-skeleton, journey-first technical route is professionally sound and F1 through F5 are supported, but F6 is unsupported: the live entity still claims that the invalidated EM returned proceed/high/not_needed for obsolete proposal blob 6ac294e and still summarizes the proposal as carrying that proceed judgment. Those stale claims contradict the statement that only the cycle-2 record may govern the current blob.
  evidence_synthesis: >-
    The real stage loader selects engineering-judgment, journey-slicing, reverse-recovery-audit, and work-control-profile. Workspace HEAD and origin/main both resolve to 64c496cdab7ccc59a15753e454f627a70383fb46; the live proposal hashes to Git blob 1fdaada701fbafb8f9e04a59839b564a5df16546 and SHA-256 bd60ca48e759ecf0d648a70f9f989ee7dbdd915d726352acffa8728369d84b9a. Exact-source continue-dev-flow is 208 lines and 1,643 words, with lines 32-180 carrying 1,143 words of eager pre-product harvesting policy; the remaining loading and product-routing text is 500 words. Its installed Codex copy is byte-identical at SHA-256 a2e453df5c4847bf9b75b21b901e52d914367bb7079849e0292768b0f6e95d3b. Exact-source promote-dev-flow requires an already sanitized handoff and retains canonical-source placement judgment, so it cannot perform adopter discovery, cursor/CAS, private-identity, or atomic handoff production. The live state inventory contains four debrief files and no _improvements directory or files. The bound-field validator returns PASS bound to the proposal SHA-256, and the AC scan finds AC-1 through AC-5 with unevidenced=false. The loader evaluator binds exact commits, Git-archive stage bytes, opaque arms, hashes, tool identity, and Q08 prompt provenance; Q08 proves conditional stage-policy loading behavior but does not implement or grade the proposed skill journey. No candidate implementation, RED/GREEN receipt, or candidate installed-skill pressure exists yet, which is appropriate at ideation. The blocking record defect is primary text in the current proposal: its Stage Report still says the completed fresh EM returned proceed/high/not_needed for obsolete blob 6ac294e, and its Summary still says the proposal carries a fresh proceed judgment, despite the preceding supersession section and the current 1fdaada blob.
  risk_tradeoff_call: >-
    The selected route buys a materially smaller ordinary continuation policy surface, product routing before optional coordination, and zero ordinary-path improvement-state I/O while preserving explicit harvesting. Its implementation risk is accidental loss of cursor/CAS, private identity, validation, or no-auto-authority guarantees; its product risk is trigger starvation. Its durable cost is one conditional reference, focused contract mutations and exact-ref pressure fixtures, plus aligned kernel, product, architecture, and README text. Inline reordering retains the eager 1,643-word load, deleting harvesting loses accepted value, a new skill adds discovery and lifecycle ownership, and promote-dev-flow cannot cross the adopter boundary. Returning now costs only a bounded record correction; proceeding with stale authoritative-looking EM claims risks Gate Authority advancing the wrong artifact and defeats exact-revision judgment.
  recommendation: >-
    Gate Authority should return the entity to ideation record repair only: remove every Stage Report and Summary claim that the invalidated 6ac294e EM is the completed governing judgment, insert this cycle-2 report bound to source 64c496cdab7ccc59a15753e454f627a70383fb46 and proposal blob 1fdaada701fbafb8f9e04a59839b564a5df16546, then reproduce the proposal hash, bound-field PASS, and AC scan. If those receipts remain green and no proposal content changes beyond judgment-record reconciliation, Gate Authority may proceed with the existing one-worker journey-first route without another scope or architecture decision.
  route: return
  confidence: high
  multi_model: not_needed
  fo_boundary: >-
    The FO may perform checklist accounting, dispatch preparation, evidence-presence checks, state mechanics, and delivery mechanics, but may not adjudicate F1-F6, rewrite the accepted scope, install this recommendation as a gate verdict, advance the stage, create work, post provider content, or authorize delivery.
  engineering_judgment:
    question: >-
      Should Gate Authority proceed with repaired proposal blob 1fdaada701fbafb8f9e04a59839b564a5df16546 as a one-slice, non-skeleton, journey-first product-first continuation route, or return it?
    revision: >-
      Product source origin/main and workspace HEAD 64c496cdab7ccc59a15753e454f627a70383fb46; proposal Git blob 1fdaada701fbafb8f9e04a59839b564a5df16546; proposal SHA-256 bd60ca48e759ecf0d648a70f9f989ee7dbdd915d726352acffa8728369d84b9a.
    evidence_synthesis: >-
      The real stage loader selects engineering-judgment, journey-slicing, reverse-recovery-audit, and work-control-profile. Workspace HEAD and origin/main both resolve to 64c496cdab7ccc59a15753e454f627a70383fb46; the live proposal hashes to Git blob 1fdaada701fbafb8f9e04a59839b564a5df16546 and SHA-256 bd60ca48e759ecf0d648a70f9f989ee7dbdd915d726352acffa8728369d84b9a. Exact-source continue-dev-flow is 208 lines and 1,643 words, with lines 32-180 carrying 1,143 words of eager pre-product harvesting policy; the remaining loading and product-routing text is 500 words. Its installed Codex copy is byte-identical at SHA-256 a2e453df5c4847bf9b75b21b901e52d914367bb7079849e0292768b0f6e95d3b. Exact-source promote-dev-flow requires an already sanitized handoff and retains canonical-source placement judgment, so it cannot perform adopter discovery, cursor/CAS, private-identity, or atomic handoff production. The live state inventory contains four debrief files and no _improvements directory or files. The bound-field validator returns PASS bound to the proposal SHA-256, and the AC scan finds AC-1 through AC-5 with unevidenced=false. The loader evaluator binds exact commits, Git-archive stage bytes, opaque arms, hashes, tool identity, and Q08 prompt provenance; Q08 proves conditional stage-policy loading behavior but does not implement or grade the proposed skill journey. No candidate implementation, RED/GREEN receipt, or candidate installed-skill pressure exists yet, which is appropriate at ideation. The blocking record defect is primary text in the current proposal: its Stage Report still says the completed fresh EM returned proceed/high/not_needed for obsolete proposal blob 6ac294e, and its Summary still says the proposal carries a fresh proceed judgment, despite the preceding supersession section and the current 1fdaada blob.
    adjudications:
      - finding: F1
        disposition: supported
        basis: >-
          Kernel Outcome discipline requires the smallest sufficient route and necessity evidence for each new mechanism. Exact-source continue-dev-flow eagerly carries 1,143 pre-product harvesting words, so reordering does not satisfy AC-1; deleting the procedure violates retained safety value, while a second skill adds an independent discovery and maintenance surface. Exact-source promote-dev-flow begins with validated sanitized handoffs at canonical-source intake. One trigger-loaded reference behind the existing entrypoint is therefore the smallest supported production route, subject to the registered real-host disproof.
      - finding: F2
        disposition: supported
        basis: >-
          Journey Slicing requires the thinnest real journey before mechanism hardening and forbids a fixture from replacing a participant. The proposal names the literal captain command, the visible item-stage-first-action result, zero ordinary improvement-state I/O, and an installed candidate using the real host, Local Profile, live work-item and iteration authorities, and actual state holder. Its test order runs that journey immediately after the minimum activation seam and before contract mutants, generalized harness work, or documentation; P1-P4 remain later instruments.
      - finding: F3
        disposition: supported
        basis: >-
          Journey Slicing defines a walking skeleton by crude cross-owner implementation and requires an inventory for fake, stub, hardcode, fixed-value, or skipped-validation shortcuts. The brownfield host, continuation entrypoint, product router, adopter harvest transaction, validator, and downstream promotion path already exist; the first candidate changes the final production activation seam directly. The proposal records no shortcut and fail-closes that classification by requiring a return to ideation with a named replacement if implementation introduces one.
      - finding: F4
        disposition: supported
        basis: >-
          Engineering Judgment counts independently releasable value surfaces, while Journey Slicing applies the independent-blocking test rather than file or actor count. The guard, extracted safety contract, installed-runtime proof, contract checks, and aligned docs are lifecycle obligations of the same observable continuation journey and cannot independently satisfy or ship its accepted outcome. The proposal declares one slice, below the two-slice ceiling, and correctly requires any piece acquiring its own real blocker to become a separate captain-owned work item.
      - finding: F5
        disposition: supported
        basis: >-
          Kernel Outcome and Verification discipline require value-level ACs, exact-revision behavior evidence, instruments seen to fail, same-kind runtime observation, falsifiers, and retained authority. AC-1 through AC-5 each name verification and concrete failure; P1-P4 cover ordinary routing, unavailable atomic ownership, successful bounded harvesting, and empty committed work. The lexicographic verdict makes safety and authority failures decisive, treats missing provenance or non-discrimination as UNKNOWN, and prevents later efficiency from offsetting product regressions. The pre-mortem and disproof conditions preserve trigger-starvation visibility without granting scheduling or implicit-harvest authority.
      - finding: F6
        disposition: unsupported
        basis: >-
          Engineering Judgment and Kernel Verification discipline require the governing record to bind the exact artifact and leave no contradictory unmet obligation. Although the old structured EM block was deleted and labeled superseded, the current 1fdaada proposal still states in its Stage Report that the completed fresh EM returned proceed/high/not_needed for obsolete blob 6ac294e and still summarizes itself as carrying that proceed judgment. The prior verdict is therefore not fully removed from the live governing prose, and the entity falsely records the cycle-2 EM obligation as already completed.
    risk_tradeoff: >-
      The selected route buys a materially smaller ordinary continuation policy surface, product routing before optional coordination, and zero ordinary-path improvement-state I/O while preserving explicit harvesting. Its implementation risk is accidental loss of cursor/CAS, private identity, validation, or no-auto-authority guarantees; its product risk is trigger starvation. Its durable cost is one conditional reference, focused contract mutations and exact-ref pressure fixtures, plus aligned kernel, product, architecture, and README text. Inline reordering retains the eager 1,643-word load, deleting harvesting loses accepted value, a new skill adds discovery and lifecycle ownership, and promote-dev-flow cannot cross the adopter boundary. Returning now costs only a bounded record correction; proceeding with stale authoritative-looking EM claims risks Gate Authority advancing the wrong artifact and defeats exact-revision judgment.
    recommendation: >-
      Gate Authority should return the entity to ideation record repair only: remove every Stage Report and Summary claim that the invalidated 6ac294e EM is the completed governing judgment, insert this cycle-2 report bound to source 64c496cdab7ccc59a15753e454f627a70383fb46 and proposal blob 1fdaada701fbafb8f9e04a59839b564a5df16546, then reproduce the proposal hash, bound-field PASS, and AC scan. If those receipts remain green and no proposal content changes beyond judgment-record reconciliation, Gate Authority may proceed with the existing one-worker journey-first route without another scope or architecture decision.
    route: return
    confidence: high
    dissent: >-
      No material dissent remains on F1 through F5 or the technical route. The sole disagreement is with F6 and any immediate proceed recommendation while obsolete 6ac294e verdict claims remain in the live entity.
    disproof_condition: >-
      Change this route to proceed when the live entity contains no superseded-EM outcome claim, contains only the cycle-2 judgment bound to proposal blob 1fdaada701fbafb8f9e04a59839b564a5df16546, and reproduces the same proposal hash, bound-field PASS, and complete AC scan without scope drift. Return the technical route again if an exact-ref installed candidate eagerly loads harvesting without an explicit trigger, misses AC-1, loses any AC-2 or AC-3 invariant, or uses a non-discriminating or unbound pressure instrument.
    authority_boundary: >-
      Captain retains scope, architecture or schema, irreversibility, accepted red residuals, spending, merge-governing choices, and any later harvesting schedule; Gate Authority retains the ideation verdict and stage-advance decision; work-item authority retains scope, status, and acceptance recording; Spacedock execution-state authority retains transitions, gate durability, and state commits; delivery authority retains exact-head PR, required-check, merge, release, terminalization, and archive decisions; the designated provider owner retains posting, upload, and external mutation authority; the FO retains only orchestration, checklist, dispatch, evidence-presence, state-mechanics, and delivery-mechanics duties. This advisory record creates no work, mutates no state, advances no stage, and grants no delivery or provider action.
```

## Stage Report: ideation (cycle 2)

- DONE: Load the current ideation contract and apply Journey Slicing to the repaired proposal.
  The live stage loader selected Engineering Judgment, Journey Slicing, Reverse Recovery Audit, and Work Control Profile at source `64c496cdab7ccc59a15753e454f627a70383fb46`; the complete Journey Slicing mod was read before the repair.
- DONE: Carve the thinnest real end-to-end installed-skill journey and name its literal captain-visible demo.
  AC-1 binds the literal captain command to the real installed candidate, host, Local Profile, live work item and iteration authority, and actual state holder; success visibly names item, stage, and first product action before improvement coordination, with zero ordinary-path improvement-state I/O.
- DONE: Make and fail-close the walking-skeleton and shortcut decision.
  The route is not a walking skeleton because all brownfield participants already exist and the first candidate changes the final production activation seam; the shortcut inventory is `none`, and AC-5 returns the item to ideation if implementation introduces a fake, stub, hardcode, fixed value, skipped validation, temporary flag, or sibling crude path without a named replacement.
- DONE: Apply the slice ceiling and independent-blocking test.
  The proposal contains one slice, below the maximum of two. AC-5 records that the guard, extracted contract, installed-runtime proof, contract checks, and aligned docs cannot independently satisfy or ship the accepted journey; any piece that acquires an independent real blocker must become a separate captain-owned work item rather than a second slice.
- DONE: Reorder verification so the real journey precedes mechanism hardening.
  AC-1, AC-2, AC-3, AC-4, and AC-5 each retain a verification instrument and falsifier; the test plan runs the literal real-host P1 journey immediately after the smallest production activation seam and before contract mutants, generalized harness work, or documentation.
- DONE: Obtain exactly one replacement fresh-context EM judgment against the repaired proposal and exact source.
  The cycle-2 GPT-5.6 High EM evaluated proposal blob `1fdaada701fbafb8f9e04a59839b564a5df16546` against source `64c496cdab7ccc59a15753e454f627a70383fb46`, supported F1-F5, and returned `return`, `high`, and `multi_model: not_needed` solely because the live report still carried obsolete cycle-1 verdict claims.
- DONE: Reconcile the invalidated cycle-1 verdict without altering the substantive repaired proposal.
  Every current Stage Report and Summary claim that cycle 1 governs has been removed; cycle 1 is explicitly non-authoritative, and the complete cycle-2 judgment is the only authoritative fresh-context EM record. The proposal prefix through the supersession section remains SHA-256 `5ccf3324616b1553256f70d593ec3a8f82f15302cac3213d54663ac56caea45c`.
- DONE: Preserve ideation-only authority and product scope.
  This repair changes only the durable state report: it creates no product code, tests, docs, work, stage transition, provider action, delivery action, or accepted red residual.

### Post-EM reconciliation

The EM reviewed product source `64c496cdab7ccc59a15753e454f627a70383fb46`, proposal Git blob `1fdaada701fbafb8f9e04a59839b564a5df16546`, and proposal SHA-256 `bd60ca48e759ecf0d648a70f9f989ee7dbdd915d726352acffa8728369d84b9a`. Changes after that review are limited to invalidating obsolete cycle-1 outcome claims and inserting the cycle-2 EM and stage record. The substantive proposal through `## Superseded ideation EM judgment` is unchanged and retains SHA-256 `5ccf3324616b1553256f70d593ec3a8f82f15302cac3213d54663ac56caea45c`. The bound-field validator and complete AC scan are reproduced after this reconciliation.

### Summary

The repaired ideation record now contains one authoritative fresh-context EM judgment. It returns only for the stale cycle-1 record defect, supports F1-F5 and the one-worker journey-first technical route, and explicitly permits Gate Authority to proceed without another scope or architecture decision when the proposal hash, bound-field validation, and AC scan remain green. This report records that repair; Gate Authority retains the verdict and stage-advance decision.

## Stage Report: implementation

- DONE: Implement the smallest accepted production seam in an isolated worktree with RED before GREEN.
  `scripts/kc-dev-flow-contract-test.py` first failed because the ordinary skill was 1,643 words and had no product-first activation contract. The implementation keeps the existing `continue-dev-flow` entrypoint, reduces its default-loaded policy to 640 words, and moves the detailed adopter procedure behind `references/improvement-harvesting.md`. Later focused REDs covered missing evaluator entrypoint ordering, unsupported host selection, discarded timeout evidence, false-positive path exclusions, unavailable Git authority, broad ordinary state enumeration, private-key command disclosure, explicit-route ordering, write-count semantics, and compatible durable identity records; each closed GREEN in the same implementation session as its minimum repair.
- DONE: Exercise the literal P1 journey before broader hardening.
  An exact installed initial candidate was invoked with `Use $continue-dev-flow to continue the current approved sprint from live repository state.` against the real holder and live authorities. It named item `product-first-continuation`, stage `implementation`, and the first product action of auditing commit `76fb9e9` against AC-1 through AC-5 before any `_debriefs` or `_improvements` I/O. The run was interrupted before nested implementation and made no repository change. Final-head isolated pressure at `e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47` independently passes P1 with zero claim, trace, or artifact failures, 6 tool calls versus baseline 7, and 51.186 seconds versus baseline 68.323.
- DONE: Preserve explicit harvesting and hard authority boundaries.
  P2 at the exact candidate resolves the product item first, reports improvement state `UNKNOWN` under unavailable CAS/exclusive ownership, writes no improvement state, and passes. P3's same-ref supplemental receipt uses fixture SHA-256 `b0db244da2db1d4ef82e8521c42b4a3e1278989c9cf9b0b03b5b8a4843d7bbca`, GPT-5.6 Sol High, and the installed plugin tree SHA-256 `e0ccc82f5872ecc6c7f193fdfdf103704fe3fafcbff9240110078e10aa6b5ff5`; it passes in 200.931 seconds with one ignored durable identity, one handoff, validator PASS, one atomic cursor-plus-handoff commit, 19 tool calls, and zero claim, trace, or artifact failures. Task creation, sprint admission, scheduling, posting/upload, policy edit, installation, merge, source promotion, and product pause remain false in the closed response contract and mutants.
- DONE: Keep empty committed work a scheduling stop.
  Final exact candidate P4 passes with no active item or stage, no task creation, no implicit harvest, no improvement-state I/O, and no captain interruption attributed merely to reporting that scheduling authority is needed.
- DONE: Preserve exact-ref receipts and uncertainty without converting missing evidence to zero.
  The paired receipt is `/tmp/kc-dev-flow-continuation-eval-e2740f53-20260812/manifest.json`: known-bad `64c496cdab7ccc59a15753e454f627a70383fb46` fails P2 product-first ordering and P3 private-key trace safety; candidate P1, P2, and P4 pass; candidate P3 is `UNKNOWN` after an exit-124 400.011-second timeout, so the paired aggregate remains `UNKNOWN`. The supplemental receipt is `/tmp/kc-dev-flow-continuation-eval-e2740f53-p3-20260812/manifest.json` and closes P3 at the same exact candidate, fixture, plugin tree, model, reasoning, prompt hash, and behavior contract. It reports 501,227 input tokens, 451,328 cached input tokens, 8,511 output tokens, and 3,707 reasoning output tokens. Implementation does not install a validation verdict; fresh validation must adjudicate the paired timeout plus supplemental closure.
- DONE: Meet the accepted policy-input budget and keep runtime discovery exact.
  The ordinary skill is 640 words versus baseline 1,643, a 61.0% reduction, within the 650-word limit. Exact Git archive materialization, isolated Codex installation, plugin-tree hashing, opaque arm identity, closed output schema, raw JSONL/stderr retention, command trace, state artifact inspection, model/reasoning identity, wall time, tool calls, and available usage are recorded. Plain `gpt-5.6` was rejected by the ChatGPT-account host and remains preserved as an `UNKNOWN` receipt; the supported machine route is `gpt-5.6-sol` with High reasoning.
- DONE: Apply only the ideation-approved durable documentation contract.
  `PRODUCT.md` states product-first continuation and explicit harvesting; `ARCHITECTURE.md` records default product router, conditional adopter-harvest reference, and downstream source intake; canonical and vendored kernels are byte-identical and make optional harvest post-route and non-blocking; the package README replaces launch-time harvesting with explicit activation.
- DONE: Map every changed file to the accepted criteria.
  `kc-dev-flow/skills/continue-dev-flow/SKILL.md` maps to AC-1 through AC-4; `kc-dev-flow/references/improvement-harvesting.md` maps to AC-2/AC-3; `kc-dev-flow/references/kernel.md` and `docs/dev/_mods/kernel.md` map to AC-1 through AC-3; `PRODUCT.md`, `ARCHITECTURE.md`, and `kc-dev-flow/README.md` map to AC-1/AC-3/AC-5; `kc-dev-flow/references/absolutes.registry` maps to AC-2/AC-3; the P1-P4 fixture, focused evaluator, evaluator test, and package contract test map to AC-1 through AC-5. No changed file is unmapped.
- DONE: Apply the independent-blocking test and delivery-topology rule after the exact facts existed.
  Candidate `e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47` has merge-base `64c496cdab7ccc59a15753e454f627a70383fb46`, 12 changed files, 2,031 additions, 169 deletions, and 8 commits. There are no dependent green layers and no independent green slices: the production route, conditional safety contract, aligned docs, and focused evaluator cannot independently satisfy or verify the accepted journey. The numeric trigger is yes, so delivery requires one Draft PR with the exact `## Native stack exception` heading and explicit reviewer acknowledgement before readiness. Mechanical share is 14 gross registry lines, vendored-policy share is 10 gross lines, and generated plus lock-file share is zero; none is subtracted from the 2,200 gross count.
- DONE: Inventory walking-skeleton shortcuts.
  Shortcut inventory is `none`: the first journey changes the final brownfield production activation seam and uses the real entrypoint, host, installed plugin, Local Profile, work-item/iteration authority, validator, Git transaction, and source-intake boundary. No fake, stub, hardcode, fixed-value product path, skipped validator, temporary flag, or sibling crude implementation remains.
- DONE: Run scoped tests during iteration and the full relevant suite at the exact implementation head.
  PASS: `python3 scripts/kc-dev-flow-contract-test.py`; `python3 scripts/kc-dev-flow-continuation-eval.test.py`; `python3 scripts/kc-dev-flow-loader-eval.test.py`; `python3 kc-dev-flow/scripts/improvement-intake.test.py` (9 tests); `./scripts/skill-frontmatter-lint.sh` (40 skills); `./scripts/version-parity-check.sh`; `./scripts/marketplace-verify.sh` (schema and isolated installs); canonical/vendored kernel byte comparison; and `git diff --check origin/main...HEAD`. `origin/main` remained exactly `64c496cdab7ccc59a15753e454f627a70383fb46` after fetch.
- DONE: Commit and push the implementation without advancing stage or creating delivery authority.
  Branch `spacedock-ensign/product-first-continuation` is remote-confirmed at `e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47`; the isolated worktree is clean and preserved. This worker created no PR, merge, release, stage transition, provider post, task, sprint admission, or accepted red residual.

### Summary

Implementation routes ordinary continuation to committed product work before optional improvement harvesting, cuts default policy input by 61.0%, and preserves explicit harvesting, validator, private identity, atomic cursor/handoff, downstream placement, and captain authority. One focused slice is committed and pushed at exact head `e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47`. Mechanical gates are green; exact candidate P1/P2/P4 and supplemental P3 are green. The formal paired aggregate remains transparently `UNKNOWN` because one candidate P3 sample timed out, so fresh validation—not this report—owns the exact acceptance verdict and any stage advance.

## Stage Report: validation

Verdict: REJECTED

- FAILED: Independently validate exact candidate e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47 against AC-1 through AC-5, including literal real-host P1 and paired-timeout plus same-ref supplemental P3 evidence.
  AC-1, E2E, and Origin re-observation record the non-discriminating P1 result; AC-2 preserves the paired P3 timeout as UNKNOWN and the same-ref supplement as separate PASS evidence.
- DONE: Adversarially challenge the retained reference and focused evaluator, inspect the full diff and authority boundaries, re-observe origin behavior, and run the exact-head suite.
  Material findings, Adversarial, Diff coverage, Origin re-observation, and Full exact-head verification record the without-it, known-bad, direct-mutant, 12-file, origin, and suite evidence.
- DONE: Produce the complete validation record and exactly one fresh-context Science Officer EM judgment.
  Verdict, Lenses, Cross-model, the Validation Science Officer EM judgment, its disproof condition and authority boundary, and Delivery topology and Native stack exception contain the required record.

### Material findings

- P1: The focused evaluator accepts ordinary execution-state enumeration that
  reveals improvement evidence. scripts/kc-dev-flow-continuation-eval.py:300-367
  retains command text but discards command output, then recognizes improvement
  access only when the command itself contains _debriefs or _improvements. The
  preserved exact-candidate P1 command rg --files docs/dev/_state | sort emitted
  docs/dev/_state/_debriefs/2026-08-12-01.md, while the manifest still recorded
  zero trace failures and PASS. A direct mutant containing the same broad
  enumeration returned no failure. This violates AC-1 and the candidate skill's
  own prohibition on enumerating the execution-state tree on an ordinary
  continuation.
- P1: The focused evaluator never grades the required first product action.
  scripts/kc-dev-flow-continuation-eval.py:243-250 checks route, active item, and
  stage but does not compare first_product_action with the live work-item action.
  A P1 response naming Harvest unseen debriefs before product work as its first
  action returned no claim failure. The instrument can therefore pass a response
  that fails AC-1's captain-visible product delta.

### Acceptance results

- AC-1: FAIL. Candidate policy size is 640 words versus 1,643, a 61.0% reduction;
  the exact fixture P1 uses 6 tool calls versus baseline 7 and is faster in this
  sample. Those later measurements cannot offset the earlier safety-order loss:
  the candidate P1 trace enumerates the unseen debrief path and its grader misses
  both that access and a wrong-first-action mutant. The literal live-holder run
  was captured only at initial candidate 76fb9e97c712d8bdbdfa3ba03826494208754bd8,
  not at the exact final head.
- AC-2: PASS as supplemental behavior evidence, not as a rewrite of the paired
  receipt. Exact-candidate P2 reports UNKNOWN under unavailable ownership and
  writes nothing. The paired P3 remains UNKNOWN after exit 124 at 400.011
  seconds. The separate P3 receipt passes at the same candidate SHA, fixture
  SHA-256 b0db244da2db1d4ef82e8521c42b4a3e1278989c9cf9b0b03b5b8a4843d7bbca,
  plugin-tree SHA-256 e0ccc82f5872ecc6c7f193fdfdf103704fe3fafcbff9240110078e10aa6b5ff5,
  skill/reference hashes, model, reasoning, and prompt hash. It validates one
  ignored durable identity, one valid handoff, and one cursor-plus-handoff commit.
  The original timeout remains UNKNOWN and is not converted to PASS.
- AC-3: PASS on the inspected response contract, authority mutants, artifacts,
  and P2/P3 traces. No task creation, sprint admission, scheduling, posting,
  policy edit, install, merge, promotion, or product pause is exercised; intake
  remains captain-review-only and source placement remains downstream.
- AC-4: PASS on the exact candidate P4 evidence. It returns scheduling with no
  active item or stage, creates no work, performs no improvement-state I/O, and
  does not treat the unseen debrief as scope.
- AC-5: PASS for focus and durable scope, but it cannot rescue AC-1. All 12
  changed files map to AC-1 through AC-5, the change remains one inseparable
  continuation slice, no new skill/schema/scheduler/general runner or Spacedock
  change appears, and the shortcut inventory remains none.

Lenses: behavior FAIL with 2 P1 findings; contract/schema FAIL because the closed response grader omits the required first-action value; state/concurrency PASS for P2/P3 cursor, identity, and atomic-write evidence; security/privacy PASS for exact candidate P3 with the known-bad private-key leak detected; runtime/platform FAIL because the exact final live-holder P1 is absent and the substitute trace exposes debrief enumeration; docs/policy PASS across PRODUCT, ARCHITECTURE, README, canonical/vendored kernel, skill, reference, and absolute registry; delivery PASS for exact-head and topology classification. Inputs were merge base 64c496cdab7ccc59a15753e454f627a70383fb46, candidate e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47, all 12 changed files, both preserved manifests and raw traces, the real-holder initial-candidate trace, the selected validation policies, and fresh origin refs. Falsifiers were the known-bad P2/P3 arm, missing-reference mutation, broad-state-enumeration trace mutant, and wrong-first-action response mutant.

Diff coverage: 100% (5/5 coverable behavior contracts exercised: conditional-reference presence and P1-P4; 12/12 changed files and all authority boundaries inspected). The direct P1 falsifiers reddened the acceptance claim even though the checked-in deterministic suites stayed green.

Adversarial: Removing kc-dev-flow/references/improvement-harvesting.md from an exact-head Git clone makes the package contract fail with missing kc-dev-flow/references/improvement-harvesting.md, supporting bounded retention of the trigger-loaded safety contract. The exact-ref known-bad arm fails P2 product-first ordering and P3 private-key trace safety. Conversely, the evaluator incorrectly accepts rg --files docs/dev/_state and a wrong first_product_action, so the new evaluator is returned for bounded repair rather than accepted as a discriminating AC-1 instrument.

Cross-model: not_needed — the fresh validation EM finds two reproducible, contract-bound P1 defects with high confidence; the recommendation is neither contested, irreversible, low-confidence, nor unresolved.

E2E: FAIL — the behavior-producing installed-skill boundary at exact candidate e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47 was exercised, but its P1 trace enumerated docs/dev/_state and exposed the unseen _debriefs path. The only literal run against the real live split-root holder is bound to earlier candidate 76fb9e97c712d8bdbdfa3ba03826494208754bd8, so it cannot close final-head validation.

Origin re-observation: FAIL — Reported scenario: Use the installed continue-dev-flow skill to continue the current approved sprint from live repository state, name product-first-continuation, validation stage, and the first concrete product action before any improvement activity | Originating runtime kind: Codex installed-skill host against the live split-root Spacedock holder | Re-observation artifact/revision: /tmp/kc-dev-flow-continuation-eval-e2740f53-20260812 at e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47 plus /private/tmp/kc-dev-flow-p1.kLLSrJ at 76fb9e97c712d8bdbdfa3ba03826494208754bd8 | Equivalent-runtime rationale: the exact-head fixture matches the host, installed exact plugin delivery path, model/reasoning configuration, invocation text, active-item shape, and unseen-debrief condition, but it does not match the live holder; the live-holder artifact matches authority but predates the final revision, so neither artifact alone or together is exact-head origin closure | Falsifier kind: mutation | Result: the exact-head P1 raw trace emits the unseen debrief path through broad state enumeration while the grader returns PASS, and no exact-final live-holder receipt exists.

### Full exact-head verification

- PASS: python3 scripts/kc-dev-flow-contract-test.py.
- PASS: python3 scripts/kc-dev-flow-continuation-eval.test.py.
- PASS: python3 scripts/kc-dev-flow-loader-eval.test.py.
- PASS: python3 kc-dev-flow/scripts/improvement-intake.test.py, 9 tests.
- PASS: ./scripts/skill-frontmatter-lint.sh, 40 skills.
- PASS: ./scripts/version-parity-check.sh.
- PASS: ./scripts/marketplace-verify.sh, schema and all isolated installs.
- PASS: canonical/vendored kernel byte comparison.
- PASS: git diff --check for 64c496cdab7ccc59a15753e454f627a70383fb46..e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47.
- PASS: after fresh fetch, origin/main remains 64c496cdab7ccc59a15753e454f627a70383fb46 and the local and remote candidate remain e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47.

### Delivery topology and Native stack exception

The required Native stack exception is accurate. The merge-base diff has 12
changed files, 2,031 additions, and 169 deletions, so 2,200 gross changed lines
triggers the greater-than-1,500 rule. There are no independently reviewable and
verifiable dependent layers and no independent green slices; splitting the
production route, conditional contract, aligned docs, and its focused evidence
would not produce separately releasable value. The delivery shape therefore
remains one Draft PR with the exact heading ## Native stack exception and
explicit non-author reviewer acknowledgement before readiness. Mechanical share
is 14 gross registry lines, vendored-policy share is 10 gross lines, and
generated plus lock-file share is zero; none is subtracted. This classification
grants no push, PR, readiness, merge, or release authority.

## Validation Science Officer EM judgment

```yaml
science_officer_em_upward_report:
  em_judgment: >-
    Return exact candidate e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47 to implementation. The product-first route and explicit-harvest safety behavior are promising, but AC-1 is not closed: the exact-head P1 trace enumerates the execution-state tree and emits an unseen debrief path while the focused evaluator reports PASS, and a separate mutant proves the evaluator also accepts the wrong first product action. Mechanical green and a same-ref P3 retry cannot override a non-discriminating P1 instrument or missing exact-final live-holder evidence.
  evidence_synthesis: >-
    Fresh origin fetch binds origin/main to 64c496cdab7ccc59a15753e454f627a70383fb46 and both local and remote candidate to e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47. All 12 changed files and the full diff were inspected. The ordinary skill is 640 words versus 1,643 and the candidate P1 sample uses 6 tool calls versus baseline 7, but its command rg --files docs/dev/_state emits docs/dev/_state/_debriefs/2026-08-12-01.md. parse_trace retains only command strings, and grade_trace searches those strings for literal improvement paths, so the manifest records no trace failures. Direct broad-enumeration and wrong-first-action mutants both survive. The checked-in full suite passes, the missing-reference mutation fails, and known-bad 64c496cdab7ccc59a15753e454f627a70383fb46 fails P2 ordering and P3 private-key safety. Candidate P2 and P4 pass. The paired candidate P3 stays UNKNOWN after exit 124 at 400.011 seconds; its raw and stderr hashes verify, and the timeout diagnostic is preserved. A separate P3 run is independently PASS with the same candidate, fixture, plugin tree, skill/reference hashes, model, reasoning, and prompt hash, valid intake, private identity, and atomic two-file commit, but it remains supplemental evidence rather than rewriting the original timeout. The only live-holder literal P1 is bound to earlier candidate 76fb9e97c712d8bdbdfa3ba03826494208754bd8, not the exact final head. The numeric delivery trigger is correctly classified as one Draft PR requiring the Native stack exception.
  risk_tradeoff_call: >-
    Product-first continuation buys a 61.0% smaller ordinary skill and removes default harvesting work, while the conditional reference preserves explicit-harvest safety. Accepting now risks shipping an AC-1 regression behind a grader that can certify both hidden debrief enumeration and a wrong first action; that is more damaging than the bounded delay of repairing two focused grading seams and rerunning final-head origin evidence. Removing the reference would lose AC-2 and AC-3 behavior, and deleting the evaluator would lose the required installed-runtime check, so the lower-cost alternative is to retain both, make P1 grading observe broad-enumeration outputs and the exact expected action, add mutants, and rerun the exact-final live-holder P1.
  recommendation: >-
    Gate Authority should record REJECTED and return the item to implementation for one bounded correction: make the evaluator fail broad execution-state enumeration or any output revealing _debriefs/_improvements on P1/P4, require the work-item-derived first product action, add both RED mutants, and rerun the literal live-holder P1 plus the focused paired evidence at the corrected exact head. Preserve the original P3 timeout as UNKNOWN and the matching supplemental run as a separate PASS receipt. Do not alter the accepted product-first route, harvest contract, scope, or delivery topology unless the correction exposes a new premise.
  route: return
  confidence: high
  multi_model: not_needed
  fo_boundary: >-
    The FO may account for this rejected gate, dispatch the bounded implementation correction, verify evidence presence, and perform authorized state mechanics. It may not reinterpret the ACs, turn the supplemental P3 PASS into the original paired PASS, advance the stage, push or create a PR, approve the Native stack exception, ready or merge delivery, or exercise captain, gate, work-item, delivery, or provider authority.
  engineering_judgment:
    question: >-
      Should exact candidate e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47 pass validation against AC-1 through AC-5, including literal P1 origin behavior and the paired-timeout plus same-ref supplemental P3 evidence?
    revision: >-
      Merge base and fresh origin/main 64c496cdab7ccc59a15753e454f627a70383fb46; local and remote candidate e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47; paired receipt /tmp/kc-dev-flow-continuation-eval-e2740f53-20260812; supplemental receipt /tmp/kc-dev-flow-continuation-eval-e2740f53-p3-20260812.
    evidence_synthesis: >-
      Fresh origin fetch binds origin/main to 64c496cdab7ccc59a15753e454f627a70383fb46 and both local and remote candidate to e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47. All 12 changed files and the full diff were inspected. The ordinary skill is 640 words versus 1,643 and the candidate P1 sample uses 6 tool calls versus baseline 7, but its command rg --files docs/dev/_state emits docs/dev/_state/_debriefs/2026-08-12-01.md. parse_trace retains only command strings, and grade_trace searches those strings for literal improvement paths, so the manifest records no trace failures. Direct broad-enumeration and wrong-first-action mutants both survive. The checked-in full suite passes, the missing-reference mutation fails, and known-bad 64c496cdab7ccc59a15753e454f627a70383fb46 fails P2 ordering and P3 private-key safety. Candidate P2 and P4 pass. The paired candidate P3 stays UNKNOWN after exit 124 at 400.011 seconds; its raw and stderr hashes verify, and the timeout diagnostic is preserved. A separate P3 run is independently PASS with the same candidate, fixture, plugin tree, skill/reference hashes, model, reasoning, and prompt hash, valid intake, private identity, and atomic two-file commit, but it remains supplemental evidence rather than rewriting the original timeout. The only live-holder literal P1 is bound to earlier candidate 76fb9e97c712d8bdbdfa3ba03826494208754bd8, not the exact final head. The numeric delivery trigger is correctly classified as one Draft PR requiring the Native stack exception.
    adjudications:
      - finding: V1
        disposition: supported
        basis: >-
          AC-1 and the candidate skill prohibit ordinary improvement-state inspection and broad execution-state enumeration. The exact P1 trace emits the unseen debrief path through rg --files docs/dev/_state, while scripts/kc-dev-flow-continuation-eval.py:300-367 discards command output and returns no trace failure. The same command survives a direct validator mutant.
      - finding: V2
        disposition: supported
        basis: >-
          AC-1 requires the captain-visible first concrete product action. scripts/kc-dev-flow-continuation-eval.py:243-250 verifies only route, item, and stage; a structurally valid P1 response whose first action is Harvest unseen debriefs before product work receives no claim failure.
      - finding: V3
        disposition: supported
        basis: >-
          Work Control and Verification discipline keep unavailable evidence typed. The paired P3 exit 124, elapsed 400.011 seconds, empty usage, and UNKNOWN verdict remain intact. Hash checks establish that the separate P3 PASS uses the same exact candidate, fixture, installed tree, prompt, model, and reasoning, so it supports AC-2 and AC-3 independently without changing the paired timeout into PASS.
      - finding: V4
        disposition: supported
        basis: >-
          Outcome discipline requires retained surfaces to survive without-it challenge and delivery policy binds topology to exact counts and independence. Removing the harvest reference makes the package contract fail and removes the explicit-harvest safety path; the known-bad arm makes the focused runner speak. The 2,200-line, 12-file diff crosses the numeric trigger but has no independent green layer or slice, so one Draft PR with the exact Native stack exception heading is the accurate topology after validation is repaired.
    risk_tradeoff: >-
      Product-first continuation buys a 61.0% smaller ordinary skill and removes default harvesting work, while the conditional reference preserves explicit-harvest safety. Accepting now risks shipping an AC-1 regression behind a grader that can certify both hidden debrief enumeration and a wrong first action; that is more damaging than the bounded delay of repairing two focused grading seams and rerunning final-head origin evidence. Removing the reference would lose AC-2 and AC-3 behavior, and deleting the evaluator would lose the required installed-runtime check, so the lower-cost alternative is to retain both, make P1 grading observe broad-enumeration outputs and the exact expected action, add mutants, and rerun the exact-final live-holder P1.
    recommendation: >-
      Gate Authority should record REJECTED and return the item to implementation for one bounded correction: make the evaluator fail broad execution-state enumeration or any output revealing _debriefs/_improvements on P1/P4, require the work-item-derived first product action, add both RED mutants, and rerun the literal live-holder P1 plus the focused paired evidence at the corrected exact head. Preserve the original P3 timeout as UNKNOWN and the matching supplemental run as a separate PASS receipt. Do not alter the accepted product-first route, harvest contract, scope, or delivery topology unless the correction exposes a new premise.
    route: return
    confidence: high
    dissent: >-
      No material dissent remains on AC-2 through AC-5, the conditional-reference architecture, or the delivery topology. The rejected call differs only from the implementation report's provisional interpretation of P1 and from treating green deterministic suites as sufficient despite two surviving AC-1 mutants and missing exact-final live-holder closure.
    disproof_condition: >-
      Change the route to proceed when a corrected exact head makes both broad-enumeration and wrong-first-action mutants fail, its exact candidate P1 trace performs no command or output-level improvement-state enumeration, the literal installed-skill run against the live holder names the current item, validation stage, and first concrete product action before improvement activity, and the full suite plus P2/P3/P4 evidence remain green with the original P3 timeout still recorded separately as UNKNOWN.
    authority_boundary: >-
      Captain retains scope, accepted outcome changes, irreversibility, spending, and any harvesting schedule; Gate Authority retains the validation verdict and stage transition; work-item authority retains scope, status, and acceptance; Spacedock execution-state authority retains durable transitions and report commits; delivery authority retains Draft PR creation, Native stack exception acknowledgement, readiness, merge, release, terminalization, and archive; provider owners retain posting and upload. This EM is advisory and grants none of those actions.
```

### Summary

Validation rejects exact candidate e2740f535334f1c12dfb9e2bc3e9f6bb4ecceb47.
The product-first route, conditional harvest contract, P2/P3/P4 behavior, full
mechanical suite, and Native stack exception classification are retained. The
bounded correction is in the focused evaluator and final-head origin receipt:
ordinary broad state enumeration and a wrong first action must both redden, then
the literal real-holder P1 must be rerun at the corrected exact head. No code,
delivery, provider, stage-transition, or scope authority was exercised in
validation.

### Feedback Cycles

- Cycle 1: REJECTED — fresh validation / EM loop; surface 153m implementation wall-clock vs estimate 90m (170%); AC unchanged

## Stage Report: implementation correction

- DONE: Repair both validation findings without changing the accepted product-first route.
  `parse_trace` now retains command output; P1/P4 grading rejects command-level improvement access, broad execution-state enumeration, and output-level improvement-path disclosure. Claim grading now compares the work-item-derived first product action after only case and terminal-punctuation normalization, so a semantically wrong action still fails. The checked-in mutants redden the original broad-enumeration/output-leak and wrong-action defects before the corrected grader turns them green.
- DONE: Remove the live continuation discovery paths exposed by exact runtime evidence.
  The ordinary skill reads the workflow path named by nearest instructions, reads iteration authority first, short-circuits an explicitly empty iteration to scheduling, and reads an active item's exact bound entity rather than enumerating the workflow or execution-state parent. This closed the additional real P4 reproducer found after the two rejected evaluator findings. The ordinary skill is 650 words versus the 1,643-word baseline, a 60.4% reduction within the accepted 650-word ceiling.
- DONE: Keep the focused fixture and artifact grader bound to real authority semantics.
  The Local Profile now binds `docs/dev/_state` as the debrief home instead of asking the model to guess it. The artifact grader accepts a handoff reference relative to the repository, `_state`, or the sibling `_improvements/state.yaml`; a new RED test proves the previously rejected `handoffs/...` sibling reference. These are evaluator corrections, not new product policy.
- DONE: Preserve exact model receipts without smoothing failures.
  The latest complete paired receipt is `/tmp/kc-dev-flow-continuation-eval-4ebb960a-20260812/manifest.json`, SHA-256 `f579541db7c7c0b36468af3902f9534f0a988dd83195d201b201b172f3ef27a3`. It binds candidate `4ebb960a5c79337863607f0c8dd09ae426fa10c0`, fixture SHA-256 `b0db244da2db1d4ef82e8521c42b4a3e1278989c9cf9b0b03b5b8a4843d7bbca`, plugin tree SHA-256 `6e0c7b3a183e501eaee331afe11a1311c47e8c94713ce11b1672a3c2a1ea1f6a`, skill SHA-256 `6ad7dbc6b4e302c49e31850a7553040776acdf6bc78114403272bc4c18fe0f27`, GPT-5.6 Sol High, and Codex CLI 0.145.0. Candidate P1, P2, and P4 PASS with zero claim, trace, or artifact failures. Candidate P3 has zero claim and trace failures, validator PASS, one valid private identity, one handoff, and one atomic two-file commit, but the manifest remains FAIL because the then-current grader rejected its correct state-relative `handoffs/...` cursor reference.
- DONE: Close the P3 grader false negative mechanically without manufacturing a model verdict.
  The final correction at `bd2ba881ae9e68f97a203c0c49d90a18bc85983d` adds the state-parent-relative reference to the closed accepted set. Its RED test fails against the old grader with `P3 cursor does not reference the handoff batch` and passes after the one-line normalization. The final plugin tree and skill hashes are byte-identical to the `4ebb960a` receipt because this final change touches only the evaluator and its test. The earlier `/tmp/kc-dev-flow-continuation-eval-aefa64b8-20260812/manifest.json` independently records P3 PASS against the same plugin-tree and skill hashes; it remains separate evidence and does not rewrite either paired aggregate.
- DONE: Run the complete relevant deterministic suite after the final correction.
  PASS: `python3 scripts/kc-dev-flow-continuation-eval.test.py`; `python3 scripts/kc-dev-flow-contract-test.py`; `python3 scripts/kc-dev-flow-loader-eval.test.py`; `python3 kc-dev-flow/scripts/improvement-intake.test.py` (9 tests); `bash scripts/skill-frontmatter-lint.sh` (40 skills); `bash scripts/version-parity-check.sh`; `bash scripts/marketplace-verify.sh` (schema and all isolated installs); and `git diff --check`.
- DONE: Commit and push the bounded correction while preserving delivery and gate authority.
  Local and remote branch `spacedock-ensign/product-first-continuation` are both `bd2ba881ae9e68f97a203c0c49d90a18bc85983d`; fresh `origin/main` remains `64c496cdab7ccc59a15753e454f627a70383fb46`. The merge-base diff is 12 files, 2,288 additions, 180 deletions, and 14 commits. It remains one inseparable slice above the numeric trigger, so the previously recorded one-Draft-PR `## Native stack exception` topology is unchanged. No PR currently exists, and this worker created no PR, merge, release, stage transition, task, sprint admission, provider post, or accepted red residual.
- OPEN EVIDENCE: Do not treat implementation completion as a validation verdict.
  The final full model manifest remains transparently FAIL for the now-repaired P3 grader false negative, and no new model run was started merely to rewrite that receipt. The literal real-holder run was performed at earlier policy bytes and is not exact-final origin closure. Fresh validation still owns whether the corrected deterministic instrument, same-plugin-byte model receipts, and any exact-final origin re-observation satisfy the rejected gate's disproof condition.

### Summary

The bounded implementation correction is committed and remote-confirmed at `bd2ba881ae9e68f97a203c0c49d90a18bc85983d`. It closes the rejected output/broad-enumeration and wrong-first-action falsifiers, removes workflow and execution-state discovery scans, binds the pressure fixture to its real state home, and fixes the state-relative artifact grader. The complete deterministic suite is green. Model receipts are preserved exactly: the latest paired aggregate is not relabeled, and fresh validation—not this implementation report—retains the acceptance and stage-transition decision.

### Feedback Cycles

- Cycle 2: IMPLEMENTATION CORRECTION COMPLETE — repaired rejected AC-1 instrument and runtime findings; exact model aggregate preserved as FAIL pending fresh validation; AC unchanged

## Stage Report: validation (cycle 2)

Verdict: REJECTED

- FAILED: Independently validate exact candidate bd2ba881ae9e68f97a203c0c49d90a18bc85983d against AC-1 through AC-5 without relabeling preserved model evidence.
  The corrected P3 artifact rule replays GREEN, but the latest paired P1 still uses 10 candidate tool calls versus 7 for its paired known-bad arm. The checked-in `paired_verdict` therefore remains `FAIL` after the P3 false negative is mechanically cleared, which violates AC-1's pre-registered ordinary-call non-inferiority rule.
- DONE: Re-test both rejected P1 falsifiers, the live broad-state discovery path, exact-final origin behavior, retained-surface necessity, and the full relevant suite.
  The broad enumeration, output leak, and wrong-first-action mutants now fail; the exact installed live-holder run resolves the item, validation stage, and first action without a state-tree walk or improvement-state command; the missing-reference mutation fails; all deterministic gates pass.
- DONE: Produce one authoritative fresh-context cycle-2 Science Officer EM judgment with AC, lens, origin, receipt, topology, and authority accounting.
  The judgment recommends another bounded AC-1 correction, preserves the accepted scope and topology, and records the required captain escalation after two consecutive rejected validation cycles.

### Material findings

- P1: The latest complete paired receipt preserves an ordinary-path tool-call
  regression. In `/tmp/kc-dev-flow-continuation-eval-4ebb960a-20260812/manifest.json`,
  candidate `4ebb960a5c79337863607f0c8dd09ae426fa10c0` uses 10 P1 tool calls while
  paired known-bad `64c496cdab7ccc59a15753e454f627a70383fb46` uses 7. Final candidate
  `bd2ba881ae9e68f97a203c0c49d90a18bc85983d` has the same plugin-tree and skill
  hashes as that candidate arm. Replaying the manifest through the final
  `paired_verdict` with only the corrected P3 artifact failure cleared still
  returns `FAIL`. AC-1 and the accepted lexicographic measurement prohibit an
  ordinary candidate increase; the earlier same-byte `aefa64b8` sample at 7
  candidate calls versus 8 baseline calls is conflicting supplemental evidence,
  not authority to discard the newer paired regression.

### Acceptance results

- AC-1: FAIL. The final ordinary skill is 650 words versus 1,643, a 60.4%
  reduction. Direct mutations now reject `rg --files docs/dev/_state`, the live
  `docs/dev/.spacedock-state` enumeration form, output-level improvement-path
  disclosure, and a wrong first action. The exact installed live-holder run names
  `product-first-continuation`, `validation`, and the fresh validation action
  without `rg --files`, `find`, `ls`, a tree walk, or an improvement-state
  command. Those gains do not override the latest paired 10-versus-7 tool-call
  regression. The live entity contains historical prose quoting the old debrief
  path, so the conservative output matcher flags a replay of that prose even
  though the commands read only the exact work-item record; this is an
  instrumentation limit, not evidence of improvement-state I/O, and it does not
  repair the independent tool-count failure.
- AC-2: PASS as bounded evidence, without rewriting either manifest. The `4ebb960a`
  candidate P2 has zero failures and preserves `UNKNOWN` with no write under
  unavailable authority. Its P3 has zero claim/trace failures, validator `PASS`,
  one durable private identity, one handoff, and one atomic commit; the final
  deterministic RED/GREEN accepts its state-relative `handoffs/...` reference.
  The separate `aefa64b8` P3 is `PASS` against the same plugin-tree and skill
  hashes. The complete `4ebb960a` manifest remains `FAIL`.
- AC-3: PASS. Closed authority mutants and preserved P2/P3 responses exercise no
  task creation, sprint admission, scheduling, posting/upload, policy edit,
  installation, merge, promotion, or product pause. Handoff validation stays
  upstream of captain-approved delivery and source placement stays downstream.
- AC-4: PASS. The `4ebb960a` candidate P4 has zero claim, trace, and artifact
  failures. The corrected direct live-form mutant rejects broad state discovery,
  and the skill now short-circuits an explicitly empty iteration before work-item
  or execution-state inspection.
- AC-5: PASS for focus and durable scope, but it cannot rescue AC-1. All 12
  changed files map to AC-1 through AC-5, the change remains one inseparable
  continuation slice, the retained reference fails its without-it mutation, and
  no new skill, schema, scheduler, general runner, or Spacedock change appears.

Lenses: behavior FAIL with one P1 non-inferiority finding; contract/schema PASS for the closed claims, trace, and final artifact normalization, with the quoted-path output-matcher limit recorded; state/concurrency PASS for P2/P3 ownership and atomicity; security/privacy PASS for private identity and sanitized handoff boundaries; runtime/platform FAIL because the latest paired P1 increases tool calls; docs/policy PASS across PRODUCT, ARCHITECTURE, README, canonical/vendored kernel, skill, reference, and absolutes registry; delivery PASS for exact-head, install, version, and topology facts. Inputs were merge base `64c496cdab7ccc59a15753e454f627a70383fb46`, candidate `bd2ba881ae9e68f97a203c0c49d90a18bc85983d`, all 12 changed files, both preserved manifests and raw traces, the exact-final live-holder receipt, selected validation policies, and fresh origin refs. Falsifiers were the rejected broad-enumeration/output and wrong-action mutants, final P3 RED/GREEN replay, missing-reference mutation, known-bad arm, and post-P3 paired-verdict replay.

Diff coverage: 100% (5/5 coverable behavior contracts exercised: conditional-reference necessity and P1-P4; 12/12 changed files and every authority boundary inspected). The surviving finding is a pre-registered cross-arm measurement, not an untested possibility.

Adversarial: The two rejected P1 falsifiers and the newly exposed live `.spacedock-state` enumeration form now redden. Removing `kc-dev-flow/references/improvement-harvesting.md` from an exact-head clone makes the package contract fail. Re-grading the preserved `4ebb960a` raw P1-P4 responses at final head yields zero claim and trace failures; deterministic RED/GREEN closes only the P3 state-relative artifact false negative. When that P3 run is changed to `PASS` for the purpose of exercising the final aggregate, `paired_verdict` still returns `FAIL` because candidate P1 has 10 calls versus 7. No model rerun was used to relabel the receipt.

Cross-model: not_needed — the receipt fields and checked-in verdict function reproduce the finding deterministically with high confidence. The earlier same-byte favorable P1 sample is explicit dissent, but it does not make the newer paired regression ambiguous under the accepted all-criteria pass rule; another model would not adjudicate away a recorded non-pass.

E2E: FAIL — the behavior-producing installed-skill boundary routes product work correctly, but the latest same-runtime paired P1 violates the accepted tool-call non-inferiority check at 10 versus 7. The exact-final live-holder observation is supporting origin evidence, not a paired cost control.

Origin re-observation: PASS — Reported scenario: use the installed `continue-dev-flow` skill to continue the current approved sprint from live repository state and name `product-first-continuation`, validation, and its first concrete product action before improvement activity | Originating runtime kind: Codex installed-skill host against the live split-root Spacedock holder | Re-observation artifact/revision: `/tmp/kc-dev-flow-p1-bd2ba88.icWPvL` at `bd2ba881ae9e68f97a203c0c49d90a18bc85983d`, install receipt SHA-256 `e4596a353a24b356136d1ad4828610a3b6817216d58d693079da6f53a577faeb`, raw trace SHA-256 `bde9dc606e000d95f405810a796c600aff11d5d75ef40ae883648cae400fa894` | Equivalent-runtime rationale: exact Git-archive plugin installation, GPT-5.6 Sol High, real workflow README, iteration authority, Spacedock work-item authority, actual state holder, and the literal invocation prefix were preserved; the appended observation-only clause stopped before stage work and granted no mutation or harvest authority | Falsifier kind: mutation | Result: the run resolved `gp / product-first-continuation`, stage `validation`, and the exact-final validation action; its 25 shell commands contained no broad direct state enumerator or improvement-state path access, and the product and state worktrees remained clean.

### Full exact-head verification

- PASS: `python3 scripts/kc-dev-flow-continuation-eval.test.py`.
- PASS: `python3 scripts/kc-dev-flow-contract-test.py`.
- PASS: `python3 scripts/kc-dev-flow-loader-eval.test.py`.
- PASS: `python3 kc-dev-flow/scripts/improvement-intake.test.py`, 9 tests.
- PASS: `bash scripts/skill-frontmatter-lint.sh`, 40 skills.
- PASS: `bash scripts/version-parity-check.sh`.
- PASS: `bash scripts/marketplace-verify.sh`, schema and all isolated installs.
- PASS: canonical and vendored kernel are byte-identical.
- PASS: `git diff --check origin/main...HEAD`.
- PASS: fresh fetch leaves origin/main at `64c496cdab7ccc59a15753e454f627a70383fb46` and local/remote candidate at `bd2ba881ae9e68f97a203c0c49d90a18bc85983d`; `gh pr list` returns no PR for the branch.

### Delivery topology and Native stack exception

The merge-base diff remains 12 files, 2,288 additions, 180 deletions, and 14
commits. No dependent green layer or independent green slice exists, so the
accepted topology remains one Draft PR with the exact `## Native stack exception`
heading and explicit non-author reviewer acknowledgement before readiness. This
validation grants no PR creation, readiness, merge, release, or terminalization
authority.

## Validation Science Officer EM judgment (cycle 2; authoritative)

```yaml
science_officer_em_upward_report:
  em_judgment: >-
    Return exact candidate bd2ba881ae9e68f97a203c0c49d90a18bc85983d for another bounded AC-1 correction. The rejected broad-enumeration and wrong-action falsifiers are closed, exact-final origin behavior now routes correctly, AC-2 through AC-5 remain supported, and P3's state-relative artifact failure is a proven grader false negative. However, the latest paired P1 uses 10 candidate tool calls versus 7 for its known-bad arm. Replaying the final aggregate after clearing only that P3 false negative still returns FAIL, so the accepted non-inferiority criterion is not met.
  evidence_synthesis: >-
    Fresh origin fetch binds origin/main to 64c496cdab7ccc59a15753e454f627a70383fb46 and local/remote candidate to bd2ba881ae9e68f97a203c0c49d90a18bc85983d. Final policy identity is plugin tree 6e0c7b3a183e501eaee331afe11a1311c47e8c94713ce11b1672a3c2a1ea1f6a and skill 6ad7dbc6b4e302c49e31850a7553040776acdf6bc78114403272bc4c18fe0f27, byte-identical to the 4ebb960a and aefa64b8 candidate receipts. The two rejected P1 mutants and the live broad-state form now fail; the complete deterministic suite, missing-reference mutation, and final P3 artifact RED/GREEN behave as required. The exact installed live-holder run names the item, validation stage, and next product action without improvement-state access. Preserved 4ebb960a candidate P1/P2/P4 and P3 claims/traces are clean, P3 artifacts are otherwise valid, and aefa64b8 independently supplies a same-byte P3 PASS. The complete 4ebb960a manifest remains FAIL. Its P1 candidate uses 10 calls versus 7 baseline; setting only its repaired P3 artifact result to PASS still makes checked-in paired_verdict return FAIL. The earlier aefa64b8 P1 sample is favorable at 7 versus 8 calls, but does not erase the later paired regression.
  risk_tradeoff_call: >-
    The candidate buys a 60.4% smaller ordinary skill, correct product-first routing, and preserved explicit-harvest safety. Accepting it would waive a captain-approved AC after a preserved runtime sample failed it; rerunning the same matrix until a favorable stochastic sample appears would weaken evidence rather than improve the product. The bounded alternative is to reduce ordinary resolution work while retaining direct-path and no-improvement-I/O guards, prove P1 first against a paired same-runtime control, and only then spend on any exact-policy evidence invalidated by that correction.
  recommendation: >-
    Gate Authority should record REJECTED and return only the ordinary P1 resolution path for bounded correction. Preserve the accepted product-first route, harvest contract, ACs, and one-PR topology. Do not relabel either existing manifest and do not start another full model matrix merely to obtain a different aggregate. Because this is the second consecutive rejection at validation, present the local Gate Authority escalation to the captain with the recommendation another bounded correction rather than an ideation reset, scope cut, or stop.
  route: return
  confidence: high
  multi_model: not_needed
  fo_boundary: >-
    The FO may account for the rejected checklist, present the required two-cycle escalation, dispatch the bounded correction after authority resolves it, and perform authorized state mechanics. It may not waive the tool-call AC, choose a favorable sample, alter scope, advance the stage, create or ready a PR, approve the Native stack exception, merge, release, terminalize, or exercise captain, gate, work-item, delivery, or provider authority.
  engineering_judgment:
    question: >-
      Should exact candidate bd2ba881ae9e68f97a203c0c49d90a18bc85983d pass validation when the corrected P1 falsifiers and origin behavior are green but the latest paired P1 increases tool calls from 7 to 10?
    revision: >-
      Merge base and fresh origin/main 64c496cdab7ccc59a15753e454f627a70383fb46; local and remote candidate bd2ba881ae9e68f97a203c0c49d90a18bc85983d; paired receipt /tmp/kc-dev-flow-continuation-eval-4ebb960a-20260812/manifest.json; supplemental receipt /tmp/kc-dev-flow-continuation-eval-aefa64b8-20260812/manifest.json; origin receipt /tmp/kc-dev-flow-p1-bd2ba88.icWPvL.
    evidence_synthesis: >-
      Exact-head source, preserved raw traces, manifests, deterministic tests, origin behavior, without-it mutation, and fresh remote refs support the synthesis above. The finding is reproduced by the repository's own paired_verdict after changing only the mechanically disproved P3 artifact failure; it does not depend on reviewer wording or a new model sample.
    adjudications:
      - finding: V2-1
        disposition: supported
        basis: >-
          AC-1 and Measurement require ordinary candidate tool calls not to increase. The latest complete paired receipt records 10 candidate P1 calls and 7 known-bad calls. Final policy bytes match that candidate, and final paired_verdict remains FAIL after the P3 artifact false negative alone is cleared.
      - finding: V2-2
        disposition: supported
        basis: >-
          The prior correction genuinely closes its assigned defects. Direct broad-state, output-leak, live-path, and wrong-action mutants now fail, final raw P1-P4 claims/traces re-grade clean, and the exact installed live-holder run resolves product work without a state-tree walk or improvement-state command.
      - finding: V2-3
        disposition: supported
        basis: >-
          AC-2 through AC-4 retain valid evidence without laundering receipt status. P2 and P4 pass; 4ebb960a P3 has valid behavior and artifacts except for the mechanically disproved relative-reference grader error; aefa64b8 supplies a separate same-byte P3 PASS. Neither complete manifest is rewritten.
      - finding: V2-4
        disposition: supported
        basis: >-
          The missing-reference mutation fails, all 12 files map to accepted criteria, and the 2,468-line gross diff has no independently deliverable layer or slice. The existing one-Draft-PR Native stack exception topology remains accurate after rejection.
    risk_tradeoff: >-
      Correct product routing and smaller policy input are valuable, but they do not authorize waiving a separately accepted runtime-cost boundary. Another bounded resolution-path correction is cheaper and more reversible than an ideation reset, while a scope cut or stop is disproportionate because AC-2 through AC-5 and the route itself remain sound.
    recommendation: >-
      Return for one bounded AC-1 correction, then require a pre-registered paired P1 to satisfy action, state-I/O, and tool-call checks before any wider model spend. If policy bytes change, re-establish only the behavior evidence invalidated by that change after P1 clears. Escalate this two-cycle gate result to the captain as required by the local workflow.
    route: return
    confidence: high
    dissent: >-
      The earlier aefa64b8 paired P1 favors the same candidate policy bytes at 7 calls versus 8 baseline, showing model variance rather than a deterministic policy floor. That sample supports feasibility but cannot supersede the newer complete paired receipt or the accepted requirement that every hard criterion and non-inferiority check pass. The exact-final live observation also routes correctly but is not a paired cost control.
    disproof_condition: >-
      Change the route to proceed when a corrected exact head retains all direct P1/P4 falsifier failures and live-holder product-first behavior, and one pre-registered same-runtime paired P1 records the correct item, stage, and work-item-derived action with zero improvement-state I/O, no broad discovery, and candidate tool calls no greater than its paired known-bad arm. Do not run the remaining expensive pressures merely to relabel preserved receipts before this P1 condition clears.
    authority_boundary: >-
      Captain retains scope, AC revisions, two-cycle escalation resolution, irreversibility, spending, and any harvest schedule; Gate Authority retains validation verdict and transition; work-item authority retains scope and acceptance; Spacedock retains durable state; delivery authority retains Draft PR creation, exception acknowledgement, readiness, merge, release, terminalization, and archive; provider owners retain posting and upload. This advisory judgment grants none of those actions.
```

### Summary

Validation cycle 2 rejects exact candidate
`bd2ba881ae9e68f97a203c0c49d90a18bc85983d`. The bounded correction genuinely
closed both prior P1 instrument defects, removed live broad-state discovery,
fixed the P3 artifact grader, and preserved AC-2 through AC-5. The latest paired
receipt nevertheless records 10 candidate P1 calls versus 7 baseline calls, and
the final aggregate remains `FAIL` after the P3 false negative is cleared. Scope,
ACs, and delivery topology remain unchanged; the local two-cycle escalation now
belongs to the captain, with the EM recommendation another bounded correction.

### Feedback Cycles

- Cycle 2: REJECTED — corrected prior findings and exact-final origin behavior, but preserved paired P1 tool-call non-inferiority remains red; AC unchanged
- Cycle 3: CAPTAIN-APPROVED BOUNDED CORRECTION — two-cycle escalation resolved in favor of one ordinary-resolution correction; surface 1 bounded correction vs estimate 1 (100%); AC unchanged

## Stage Report: implementation correction (cycle 3)

Outcome: STOPPED AT PRE-REGISTERED CANARY RED

- DONE: Reduce only the ordinary P1 resolution path at exact candidate `452dabd1eb7fcf1519b5c1e72917331ca06e3d88`.
  The ordinary skill now uses the already-loaded instruction chain, batches the workflow README with the complete vendored kernel, batches independent iteration/identity/ownership/delivery reads, and defers project context until the product action will execute. The accepted route, exact work-item authority, explicit-harvest contract, P2-P4 policy, ACs, and 650-word ceiling remain unchanged.
- DONE: Record deterministic RED before the smallest GREEN.
  Before implementation, `scripts/kc-dev-flow-continuation-eval.test.py` failed because no P1-only selector existed. A replay of the preserved 10-call P1 trace then reddened all three targeted redundancies: paginated kernel reads, nested-instruction rediscovery, and product-context read before the stop-before-action boundary. The minimum GREEN adds bounded `--pressure P1` selection, fail-closed paired-P1 verdict coverage, those three trace falsifiers, and the small policy wording above.
- DONE: Map every cycle-3 changed file to accepted scope.
  `kc-dev-flow/skills/continue-dev-flow/SKILL.md` maps to AC-1 ordinary resolution cost while preserving AC-2 through AC-4 boundaries. `scripts/kc-dev-flow-continuation-eval.py`, `scripts/kc-dev-flow-continuation-eval.test.py`, and `scripts/kc-dev-flow-contract-test.py` map to AC-1 paired non-inferiority and AC-5 focused falsifiable evidence. No cycle-3 changed file is unmapped.
- DONE: Run the complete diff-earned deterministic suite before model spend.
  PASS: continuation evaluator tests; package contract; loader evaluator; improvement intake (9 tests); skill frontmatter test plus lint (40 skills); version parity; marketplace schema and every isolated plugin install; and `git diff --check`. The ordinary skill is exactly 650 words.
- DONE: Pre-register the captain-bound spend ladder before execution.
  `/tmp/kc-dev-flow-p1-spend-ladder-452dabd1-20260812.md`, SHA-256 `06f837a0e34c60c7136c3382f5683b93fb89a5dc25413ba6cb6bb1173d0500ba`, binds candidate `452dabd1eb7fcf1519b5c1e72917331ca06e3d88`, known-bad `64c496cdab7ccc59a15753e454f627a70383fb46`, P1 only, Terra medium before Sol high, exact output paths, paired action/state-I/O/tool-call pass conditions, and mandatory stop on the first non-PASS. Both output paths were absent before execution.
- FAILED: Pass the Terra medium paired-P1 canary.
  `/tmp/kc-dev-flow-continuation-p1-terra-medium-452dabd1-20260812/manifest.json`, SHA-256 `4c71adba4a83cb1662fbf35af9036f898c41c7f7cb2ec987c2c5e575ec9d5026`, uses GPT-5.6 Terra Medium, Codex CLI 0.145.0, fixture SHA-256 `b0db244da2db1d4ef82e8521c42b4a3e1278989c9cf9b0b03b5b8a4843d7bbca`, and only P1. The known-bad arm uses 4 calls and fails broad state enumeration, improvement-path output disclosure, and premature PRODUCT read. The candidate arm improves the prior candidate sample from 10 calls to 6, returns the exact item, implementation stage, and `Run the focused implementation contract.`, performs zero improvement-state I/O, and has no claim or artifact failures. It remains red because it paginates the vendored kernel across two calls and 6 candidate calls exceed the paired 4-call known-bad arm. Paired verdict: `FAIL`.
- NOT RUN: Sol high final paired P1 and P2-P4.
  The Terra canary activated the pre-registered stop condition. `/tmp/kc-dev-flow-continuation-p1-sol-high-452dabd1-20260812` does not exist. No sample was repeated, no receipt was relabeled, and no wider model matrix was run for ceremony.
- DONE: Commit and push the exact bounded correction without exercising gate or delivery authority.
  Local and remote branch `spacedock-ensign/product-first-continuation` are both `452dabd1eb7fcf1519b5c1e72917331ca06e3d88`; fresh `origin/main` remains `64c496cdab7ccc59a15753e454f627a70383fb46`. The merge-base diff is 12 files, 2,450 additions, 188 deletions, and remains one inseparable slice above the numeric trigger. The accepted one-Draft-PR `## Native stack exception` topology is unchanged. No PR, readiness action, merge, release, stage transition, task, sprint admission, provider post, or accepted red residual was created.
- BLOCKED BY AUTHORITY: The accepted P1 non-inferiority condition remains red.
  This implementation session has exhausted the captain-approved verification ladder at its first red. Another code correction or model sample requires a fresh captain/gate decision; the worker cannot waive 6-versus-4, rerun until favorable, or advance validation.

### Summary

Cycle 3 reduced the exact candidate's ordinary P1 sample from 10 calls to 6 while retaining exact action resolution, zero improvement-state I/O, and every safety boundary. The pre-registered Terra canary still fails paired non-inferiority against a 4-call known-bad arm because the candidate paginates the kernel. Per captain instruction, the ladder stopped and Sol high plus P2-P4 were not run. Exact code is committed and pushed; the item remains in implementation pending new authority.

### Feedback Cycles

- Cycle 3: CANARY FAIL — ordinary candidate calls reduced 10 to 6 but remain above paired baseline 4; mandatory spend stop honored; AC unchanged
- Cycle 4: CAPTAIN-APPROVED DESIGN RESET — replace unsafe single-sample tool-call dominance with safety-first comparability and non-gating efficiency observation; surface one AC clarification vs estimate one (100%); AC revised, product scope unchanged; 20-minute total cap
