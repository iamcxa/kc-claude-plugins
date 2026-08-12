---
title: "kc-dev-flow: route product work before improvement harvesting"
status: ideation
source: "captain:conversation-2026-08-12-third-slice"
product: kc-dev-flow
sprint:
started: 2026-08-12T08:28:54Z
completed:
verdict:
worktree:
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

## Design determination

`required` — change activation while preserving ownership. The product router,
conditional harvest reference, deterministic contract checks, and one focused
exact-ref pressure fixture form one independently releasable value surface. The
reference is necessary because removing it either keeps the eager input or drops
hard invariants; a new skill, scheduler, schema, or general evaluator has no
without-it AC failure and is returned from the route. One worker is sufficient:
the slice is one primary journey, under 90 minutes of expected implementation,
with no independent behavior that earns parallel delivery.

## Acceptance criteria

Inherited backlog statements are normalized as follows: the end value is retained
as value; the existing validator, handoff schema, source placement, and no-auto-
authority rules are retained as governing constraints; exact file extraction is
the selected mechanism only because keeping the procedure inline fails AC-1.

**AC-1 — Ordinary continuation reaches product routing with materially less policy and zero improvement I/O.**

Verified by: paired exact-ref installed-skill pressure for an active product item
with unseen debriefs and no harvest request. The candidate's default-loaded
`continue-dev-flow` policy is at most 650 words and at least 40% smaller than the
1,643-word baseline; its first work-item/iteration action precedes any improvement
action; its trace contains no `_debriefs`/`_improvements` read or write, no extra
captain interruption, and no more tool calls before the product decision.
Falsified by: any improvement-state I/O without the explicit request, product
routing not being the first domain action, either policy threshold failing, or a
later efficiency metric being used to excuse an earlier regression.

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
README discovery wording (AC-5). Falsified by: a new skill or schema, Spacedock
change, mandatory model run in CI, general runner/grader, automated schedule, or
an unmapped file.

## Test plan

1. Write deterministic REDs for the explicit-trigger guard, default no-improvement
   route, conditional reference presence, CAS/write-unit rule, handoff validator,
   and every no-auto-authority boundary; then extract the minimum reference and
   return GREEN without changing `improvement-intake.py` behavior.
2. Reuse PR #216's exact-ref materialization, opaque-arm, hidden-rubric, and
   provenance pattern for one focused `continue-dev-flow` fixture. Do not turn it
   into a general model runner or all-skill harness. Install each exact plugin arm
   in an isolated host profile and invoke the real skill entrypoint.
3. Pre-register four pressures: P1 ordinary active item + unseen debriefs + no
   trigger; P2 explicit harvest + unseen debriefs + unavailable CAS/ownership;
   P3 explicit harvest + reusable-source candidate + CAS/private identity; P4 no
   committed work + unseen debriefs + no trigger. Preserve raw responses, tool and
   file traces, exact refs, skill/reference hashes, model/reasoning identity, and
   available usage/wall-time receipts before revealing arm identity and rubric.
4. Run the full `scripts/kc-dev-flow-contract-test.py`, focused loader/skill
   evaluation tests, `improvement-intake.test.py`, skill frontmatter lint, and
   `git diff --check` at the exact implementation head.

E2E applies at the behavior-producing skill boundary, not in a browser. Fake
fixtures prove deterministic contracts only; the four isolated installed-skill
pressures close routing and conditional-load behavior.

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

## Ideation EM judgment

```yaml
science_officer_em_upward_report:
  em_judgment: >-
    Proceed with the proposal's product-first continuation route: retain continue-dev-flow as the single entrypoint, load one improvement-harvesting reference only on an explicit current invocation request, and preserve promote-dev-flow as downstream source intake. This is the smallest sufficient, reversible route supported by the exact baseline and accepted outcome.
  evidence_synthesis: >-
    Bound evidence: origin/main resolves to 64c496cdab7ccc59a15753e454f627a70383fb46, and docs/dev/.spacedock-state/product-first-continuation.md hashes to proposal blob 6ac294e4701349054572c4ce4e3281a912985cf5. At the exact source ref, continue-dev-flow is 208 lines and 1,643 words; its lines 32-180 contain 1,143 words of pre-product harvesting policy, while the common loading and product-routing portions total 500 words. The skill enters debrief resolution before its product-work decision and owns bounded scanning, cursor and home comparison, atomic cursor-handoff writes, private pseudonymous identity, validation, and authority prohibitions. The exact-ref promote-dev-flow requires an already sanitized handoff and starts at canonical-source intake, so it has no adopter-side discovery or transaction capability. The exact-ref loader evaluator provides commit resolution, Git-archive materialization, opaque arms, hashes, and provenance, while Q08 demonstrates conditional stage-policy loading; it does not yet prove the proposed real-skill behavior. Four authoritative debrief records exist and no _improvements files exist. A bounded source-tree search found policy and documentation references but no bound ordinary-path consumer; external and manual use remain unknown. No candidate implementation, RED/GREEN result, or installed-skill pressure receipt exists yet, so this judgment accepts a falsifiable ideation route rather than claiming runtime completion.
  risk_tradeoff_call: >-
    The benefit is materially smaller ordinary continuation policy input, product routing before optional coordination work, and zero ordinary-path improvement-state I/O. The principal risk is trigger starvation, plus accidental loss of cursor, CAS, identity, validation, or authority invariants during extraction. The durable cost is one maintained conditional reference, focused contract mutations and exact-ref pressure fixtures, and aligned kernel and product documentation. Merely reordering the inline block preserves the eager 1,643-word load, deleting harvesting loses accepted value, a new skill adds discovery and lifecycle surface, and promote-dev-flow cannot cross the adopter ownership boundary. The proposal's explicit pre-mortem, hard-failure ordering, and return-on-disproof rule bound the risk without adding a scheduler or daemon.
  recommendation: >-
    Gate Authority should accept this ideation direction and, after confirming work-item authority records the exact accepted outcome and scope, dispatch one worker to establish deterministic REDs, extract only the minimum conditional reference, and run P1-P4 through isolated exact-ref installed-skill pressures. Return to ideation without weakening invariants if the host eagerly loads the reference, AC-1's policy reduction fails, any AC-2 or AC-3 invariant fails, provenance is unbound, or the known-bad arm is non-discriminating.
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: >-
    The local FO retains checklist accounting, dispatch, evidence-presence checks, state mechanics, and delivery mechanics, but holds no engineering adjudication, scope, provider-posting, gate-verdict, or stage-transition authority.
  engineering_judgment:
    question: >-
      Should ideation proceed with product routing first and one conditional improvement-harvesting reference behind the existing continue-dev-flow entrypoint, activated only by an explicit current invocation request?
    revision: >-
      Product baseline origin/main@64c496cdab7ccc59a15753e454f627a70383fb46; proposal blob 6ac294e4701349054572c4ce4e3281a912985cf5 at docs/dev/.spacedock-state/product-first-continuation.md.
    evidence_synthesis: >-
      Bound evidence: origin/main resolves to 64c496cdab7ccc59a15753e454f627a70383fb46, and docs/dev/.spacedock-state/product-first-continuation.md hashes to proposal blob 6ac294e4701349054572c4ce4e3281a912985cf5. At the exact source ref, continue-dev-flow is 208 lines and 1,643 words; its lines 32-180 contain 1,143 words of pre-product harvesting policy, while the common loading and product-routing portions total 500 words. The skill enters debrief resolution before its product-work decision and owns bounded scanning, cursor and home comparison, atomic cursor-handoff writes, private pseudonymous identity, validation, and authority prohibitions. The exact-ref promote-dev-flow requires an already sanitized handoff and starts at canonical-source intake, so it has no adopter-side discovery or transaction capability. The exact-ref loader evaluator provides commit resolution, Git-archive materialization, opaque arms, hashes, and provenance, while Q08 demonstrates conditional stage-policy loading; it does not yet prove the proposed real-skill behavior. Four authoritative debrief records exist and no _improvements files exist. A bounded source-tree search found policy and documentation references but no bound ordinary-path consumer; external and manual use remain unknown. No candidate implementation, RED/GREEN result, or installed-skill pressure receipt exists yet, so this judgment accepts a falsifiable ideation route rather than claiming runtime completion.
    adjudications:
      - finding: F1
        disposition: supported
        basis: >-
          Kernel Outcome discipline requires the smallest sufficient route and requires every new mechanism to prove necessity against a simpler alternative. Exact-ref continue-dev-flow places 1,143 words in one eager pre-product block, so textual reordering does not reduce the loaded skill surface. Removing harvesting violates the accepted value, while a second skill adds an independently discovered and maintained invocation surface. A trigger-loaded reference behind the existing entrypoint is therefore the smallest supported proposal, subject to AC-1's real-host disproof.
      - finding: F2
        disposition: supported
        basis: >-
          The exact-ref continue-dev-flow owns adopter execution-state discovery, bounded debrief selection, cursor and home comparison, atomic cursor-handoff commit, private source identity, sanitization, and handoff validation. Exact-ref promote-dev-flow begins only after one or more sanitized handoffs reach the canonical source and explicitly retains source placement judgment. Its intake contract neither discovers adopter state nor creates the required adopter transaction, so it cannot replace harvesting.
      - finding: F3
        disposition: supported
        basis: >-
          Kernel Verification discipline requires instruments that can fail, exact-revision binding, same-kind behavioral observation, and fresh validation. AC-1 through AC-5 name concrete falsifiers; P1 and P4 exercise ordinary and empty-work routing without implicit harvesting, while P2 and P3 exercise unavailable ownership and successful CAS/private-identity harvesting. The lexicographic verdict makes AC-2 and AC-3 safety or authority failures decisive before efficiency measures and treats missing provenance, traces, or discriminatory behavior as UNKNOWN. These are adequate ideation protections, though implementation must still produce the receipts.
      - finding: F4
        disposition: supported
        basis: >-
          The engineering-judgment iteration-size precheck counts independently releasable value surfaces rather than files or actors. The skill guard, conditional reference, aligned policy/docs, and focused fixture serve one primary continuation journey and one reversible release outcome; no independent scheduler, schema, source-admission mechanism, or second entrypoint is included. Trigger starvation is explicitly named, observable through comparable continuations with unseen debriefs, and reserved for a later captain-owned scheduling decision rather than hidden or automatically repaired.
    risk_tradeoff: >-
      The benefit is materially smaller ordinary continuation policy input, product routing before optional coordination work, and zero ordinary-path improvement-state I/O. The principal risk is trigger starvation, plus accidental loss of cursor, CAS, identity, validation, or authority invariants during extraction. The durable cost is one maintained conditional reference, focused contract mutations and exact-ref pressure fixtures, and aligned kernel and product documentation. Merely reordering the inline block preserves the eager 1,643-word load, deleting harvesting loses accepted value, a new skill adds discovery and lifecycle surface, and promote-dev-flow cannot cross the adopter ownership boundary. The proposal's explicit pre-mortem, hard-failure ordering, and return-on-disproof rule bound the risk without adding a scheduler or daemon.
    recommendation: >-
      Gate Authority should accept this ideation direction and, after confirming work-item authority records the exact accepted outcome and scope, dispatch one worker to establish deterministic REDs, extract only the minimum conditional reference, and run P1-P4 through isolated exact-ref installed-skill pressures. Return to ideation without weakening invariants if the host eagerly loads the reference, AC-1's policy reduction fails, any AC-2 or AC-3 invariant fails, provenance is unbound, or the known-bad arm is non-discriminating.
    route: proceed
    confidence: high
    dissent: ""
    disproof_condition: >-
      Change the route to return if an exact-ref installed-skill run shows the host loads improvement-harvesting without the explicit trigger, the candidate cannot meet AC-1's reduction and product-first behavior while preserving every AC-2 and AC-3 invariant, the focused instrument cannot discriminate a known-bad arm, or a newly bound ordinary-path consumer demonstrates that explicit-only activation fails accepted product value. Post-release evidence that comparable continuations repeatedly leave unseen debriefs unharvested would reopen the trigger decision for captain-owned scheduling, not authorize implicit harvesting.
    authority_boundary: >-
      Captain retains scope, architecture or schema, irreversibility, accepted red residuals, spending, and merge-governing choices; Gate Authority retains the ideation verdict and stage-advance decision; work-item authority retains scope, status, and acceptance recording; Spacedock execution-state authority retains transitions and durable state; delivery authority retains exact-head PR, required-check, merge, and terminalization decisions; the designated provider owner retains posting or upload authority. This advisory report creates no work, changes no stage, and grants no delivery or provider action.
```

## Stage Report: ideation

- DONE: Prove the smallest product-first route at the real continue-dev-flow skill boundary, including why the existing source-side promote path cannot replace adopter-side harvest.
  The reverse-recovery trace selects one conditional reference behind the existing entrypoint; exact-ref source shows `promote-dev-flow` begins only after a validated handoff and owns none of the adopter transaction.
- DONE: Define value and hard-invariant ACs that preserve debrief evidence, handoff validation, and every no-auto-authority boundary while reducing ordinary-path load.
  AC-1 measures <=650 ordinary skill words, >=40% reduction, product-first action, and zero improvement I/O; AC-2/AC-3 make evidence, CAS, validation, identity, and authority regressions hard failures.
- DONE: Pre-register exact-ref pressure scenarios, lexicographic verdicts, and a disproof condition; obtain exactly one fresh-context EM judgment.
  P1-P4 bind ordinary, unavailable-CAS, reusable-source, and empty-work cases; the single fresh GPT-5.6 High EM returned `proceed`, `high`, and `multi_model: not_needed` for baseline `64c496...` and proposal blob `6ac294e...`.
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

Ideation selects a product-first default in the existing `continue-dev-flow` entrypoint and moves detailed adopter harvesting behind one explicit-trigger reference. The route preserves all improvement evidence and authority boundaries, pre-registers four exact-ref pressure scenarios with a safety-first lexicographic verdict, and carries one fresh independent `proceed` judgment without granting stage or delivery authority.
