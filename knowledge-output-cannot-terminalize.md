---
id: geef7a3dy7w12g7tq89h21te
title: "Work whose output is knowledge cannot terminalize: pr-merge requires a merged PR that such work never has"
status: validation
source:
product: repo-platform
sprint: S8
started: 2026-09-10T16:27:54Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-knowledge-output-cannot-terminalize
issue:
pr:
mod-block:
sprint-readiness: ready
gates:
    version: 1
    records:
        - id: gate:geef7a3dy7w12g7tq89h21te:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:geef7a3dy7w12g7tq89h21te-backlog-1
              briefing:
                id: briefing:geef7a3dy7w12g7tq89h21te:backlog:attempt-1:revision-1
                digest: sha256:320aa73c1906dbd2c2a98b1bf2f9c16b3409b284e2da8c621e9ad32ec7ebd802
                room-ref: ./knowledge-output-cannot-terminalize/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:geef7a3dy7w12g7tq89h21te:backlog:1
                briefing: briefing:geef7a3dy7w12g7tq89h21te:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T16:27:17.921751Z"
                decision: approve
                reason: Kent approved the explicitly presented upstream native knowledge-delivery repair under this existing defect owner with 批准; this is durable admission of that same bounded scope and Pilot profile, not a new scope decision.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:geef7a3dy7w12g7tq89h21te:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:geef7a3dy7w12g7tq89h21te-ideation-1
              briefing:
                id: briefing:geef7a3dy7w12g7tq89h21te:ideation:attempt-1:revision-1
                digest: sha256:56c26cade66a3ed12743b638879e0c7e3906a148cca2c3835e4187b68907ec28
                room-ref: ./knowledge-output-cannot-terminalize/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:geef7a3dy7w12g7tq89h21te:ideation:1
                briefing: briefing:geef7a3dy7w12g7tq89h21te:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T16:31:26.882364Z"
                decision: approve
                reason: Apply Kent current 批准 of the explicit native knowledge-delivery implementation design, transferred unchanged from approved Pilot ef2a0045 to this existing defect owner. Two shape handoff checks passed; implement the exact approved limits, product commits still require confirmation.
              application:
                target-stage: implementation
                state: consumed
---

## Historical problem and investigation

Preserved historical record. Retractions, version observations and proposed broad refits below describe earlier investigations; they do not override the current approved Development Brief at the end of this record.

Two statements in this workflow's own configuration contradict each other, and the runtime
implements the stricter one.

`docs/dev/README.md:69` scopes the hook conditionally:

> PR lifecycle | Spacedock `pr-merge`, **only when a PR is the selected delivery artifact**.

`docs/dev/_mods/pr-merge.md:342` scopes terminalization absolutely:

> The workflow's terminal `done` state **requires an authenticated merged product PR**, which
> those failure paths cannot provide.

and again at `:346`, instructing the agent to refuse to "claim or write terminal success"
without one. The `spacedock` binary implements the second reading: it refused
`--set digest-effect-unmeasured status=done` with `pr field is empty and mod-block is empty`.

So an entity whose accepted outcome is **knowledge rather than a diff** has no terminal path.
Concretely: a measurement that returns a verdict, a reverse-recovery audit, a keep-or-retire
decision, a spike that answers a question and produces no code. Each of these can be shaped,
worked, and finished, and then cannot be closed.

This is not hypothetical. `digest-effect-unmeasured` did exactly its job — its Step 0 kill
switch fired, it returned "no headroom, do not ship", and it saved the 480-run budget its own
plan had estimated. It is sitting at `backlog` because the correct answer produced no PR.

### What the workarounds cost

- `--force` bypasses a guard whose refusal message says a refusal "usually means a ceremony
  step was skipped". Using it here trains the habit of forcing past a guard that is usually
  right, to work around a case it does not model.
- Attaching an unrelated PR to make the field non-empty makes the tracker lie about what
  delivered the outcome.
- Leaving it open forever means the backlog stops distinguishing "not started" from "answered".

## Reproduced, 2026-08-20 — two separate defects

Run against `digest-effect-unmeasured` (status `backlog`, no `pr`, no worktree). Both were
discriminated by experiment, not inferred.

### 1. Every exit is gated, not just the terminal one

`--archive` is refused by the same guard as a terminal `--set`:

```
entity digest-effect-unmeasured cannot be archived — workflow has merge hook(s)
[pr-merge] that have not run (pr field is empty and mod-block is empty).
```

So archive is not the escape hatch for answered-without-delivery work. There is no non-forced
exit from the active set for an entity with no PR.

### 2. `merge guard` clears the precondition it then requires

The ceremony verb livelocks. Observed sequence:

1. `merge guard <slug> --verdict passed` prints `armed: mod-block set to merge:pr-merge` and
   **writes nothing** — the entity file is unmodified, `git status` clean.
2. Re-running it fails with `mod-block is empty`.
3. Setting the field by hand works: `--set <slug> mod-block=merge:pr-merge` writes
   `mod-block: merge:pr-merge`. So the field is writable and the value is accepted.
4. Running `merge guard` again with the block genuinely armed still reports `mod-block is
   empty` — **and clears the field**.

The verb's own help documents the shape of the bug: "the mod-block is cleared in its own step
first, then application, terminal status, verdict, and completed move in ONE locked write."
The clear is outside the locked write, so a failing terminal step leaves the entity stripped of
the precondition rather than rolled back. Each invocation therefore destroys the state the next
invocation demands.

This is independent of defect 1: it would strand a PR-delivered entity too, any time the
terminal write fails after the clear commits. Fixing the knowledge-output gap does not fix it.

### Where this points

Defect 2 is in the `spacedock` binary, not in the vendored `pr-merge.md` prose — the mod is
never reached. That answers the shape stage's first open question for defect 2 and narrows
defect 1's candidates to the binary's guard versus the mod's absolute claim at
`pr-merge.md:342`.

## Re-verified after checking against Spacedock 0.27 — defect 1 retracted

The Captain's instinct was right: check the scaffolding version before filing an upstream bug.
This workflow's `_mods/pr-merge.md` is **version 0.12.2**; the canonical mod shipped with the
installed 0.27.0-pre8 plugin is **0.27.0**. Fifteen versions of drift.

### Defect 1 — RETRACTED. There is an exit; the stale mod never mentions it.

Canonical 0.27 recognizes a second delivery sentinel the local copy has never heard of:
"terminal status carrying a valid merged sentinel (`pr-merge:` or **`local-merge:`**)".
Setting `pr=local-merge:{reason}` and running `--archive` worked on the first attempt:

```
archived: docs/dev/.spacedock-state/_archive/digest-effect-unmeasured.md
```

So knowledge-output work is not stranded. The capability existed; the vendored prose that
would have told an agent about it was fifteen versions behind. The original finding was a
stale-vendor artifact, not a missing terminal path — which is the same failure class this
repository keeps producing: a vendored reference drifting out of sync with the mechanism it
describes.

### Defect 2 — CONFIRMED on 0.27, and narrowed

Reproduced on a throwaway entity against the current binary. Conditional on `pr` being empty:

```
mod-block before: merge:pr-merge
guard says:       "... (pr field is empty and mod-block is empty).
                   Set mod-block=merge:pr-merge and invoke the hook."
mod-block after:  (empty)
```

Three things wrong in one run: the guard **misreports** a set `mod-block` as empty; it
**clears** the field as a side effect of the failed run; and its remediation text instructs the
operator to set exactly the field it just destroyed. Each invocation therefore destroys the
state the next invocation demands.

With `pr` non-empty the guard behaves coherently — it leaves the block intact and reports
`PR ... is pending — mod-block left intact`. So the livelock is specific to the empty-`pr`
path, which is precisely the path an operator reaches when the entity has no PR.

### New finding — `--archive` and `merge guard` disagree about `local-merge:`

The same sentinel value is read two ways by the same binary: `--archive` accepted
`pr=local-merge:...` as proof and archived, while `merge guard` read `pr=local-merge:test` as a
**pending** PR and refused with "never finalize on an open PR". One of the two is wrong about
what `local-merge:` means.

### Revised scope

Defect 1 is gone. What remains is (a) a scaffolding refit — the local `pr-merge.md` is
0.12.2 against canonical 0.27.0, and carries a kc-dev-flow runtime extension that a wholesale
replacement would destroy — and (b) two binary-level defects worth reporting upstream, both
reproduced against 0.27.0-pre8.

## Partial port applied, and the extension audited

### Ported (working, verified end to end)

`docs/dev/_mods/pr-merge.md` 0.12.2 -> 0.12.3. Three hunks brought forward from canonical
0.27.0, nothing else touched:

- the startup and idle hooks now recognize a merged sentinel (`pr-merge:` / `local-merge:`)
  and bypass `gh` for a sentinel row;
- terminalization hands off to `spacedock merge guard --verdict passed` instead of the
  hand-rolled two-`--set` sequence the 0.12.2 copy prescribed — that sequence is now refused
  by the binary, so the vendored prose was instructing a procedure that cannot succeed;
- a new `## Delivery without a PR` section documents the `local-merge:` escape, including why
  the reason string matters and why `--force` is not the answer.

Verified: a fresh entity with `pr=local-merge:{reason}` archives on the first attempt, the
workflow validates, and `kc-dev-flow-contract-test.py` passes.

The version stamp reads 0.12.3 with a scope note, **not** 0.27.0. Stamping the canonical
version on a partial port would make the next refit skip the remaining hunks — the same
drift-by-false-claim that produced this task.

### Extension audit — one third is now redundant, two thirds are not

The local extension is 392 lines in three sections:

| Section | Canonical 0.27.0 coverage | Verdict |
|---|---|---|
| `Portable delivery hardening from shipped Spacedock v0.27.0-pre3` (238 lines) | Covers every concept **and more** — repository qualifier, unresolved-worktree handling, and `dispatch trunk` appear in canonical and not in the extension. No command family the extension uses is missing from canonical. | **Redundant and behind.** It is a hand back-port of a pre-release that the released version has since superseded. |
| `Delivery topology decision` | Zero mentions of `topology` in canonical. | **Keep.** No upstream equivalent; an open backlog entity (`delivery-topology-review-deduplication`) tracks its own defect. |
| `Split-root audit-link correction` | Zero mentions of `split-root` or `audit-link` in canonical. | **Keep.** No upstream equivalent; a session debrief recorded the underlying defect (the audit-link template produces a dead link under split-root state). |

That makes the full refit tractable rather than a three-way merge of 492 lines: take the
canonical 124-line body, drop the 238-line back-port, carry the two genuinely local sections
forward. Roughly a 60% reduction in locally-maintained prose.

The redundancy itself is the lesson worth keeping: a hand back-port of an unreleased version
becomes stale debt the moment the release lands, and nothing told us — the file kept claiming
0.12.2 while carrying 0.27.0-pre3 content.

## Work profile receipt

Current receipt, admitted by Kent on 2026-09-11 for the approved upstream dependency repair. The surrounding investigation is historical; the current Development Brief below owns implementation scope.

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: Bounded native knowledge-only terminalization repair with real approval and persistence seams, without consumer migration or production support commitment.
  route: [shape, build, verify-deliver]
  obligations:
    architecture: [Preserve native gates and archive authority, Keep genuine PR and local-merge semantics]
    implementation: [Bind explicit knowledge delivery to an approved evidence-bearing terminal briefing, Reuse existing locked finalize and archive operations]
    testing: [Prove positive native terminalization and refusal controls, Verify archive-once recovery and a copied original task snapshot]
  scope_boundary: Upstream internal/status/merge.go, internal/status/merge_guard_test.go, mods/pr-merge.md, internal/gates/delivery.go, internal/gates/delivery_test.go, internal/gates/io.go, internal/cli/help.go, internal/status/mutate.go at most eight files and 850 added plus deleted lines against af70297ddae6ec64444849e8e3fcf57484bc16e1; separate local docs/dev/_mods/pr-merge.md follow-up at most one file and 40 added plus deleted lines.
  semantics_unchanged: false
  promote_when: [Consumer migration, Replacement state authority, Production support or release ownership]
  decision:
    authority: Kent approved the prior Pilot scope and explicitly approved the eight-file 850-gross-line amendment with 批准 on 2026-09-11, as relayed by the First Officer
    at: 2026-09-11
```

## Historical accepted outcome and non-goals

A knowledge-output entity can reach `done` through a declared, non-forced path, and the
workflow's two statements about `pr-merge`'s scope agree with each other and with the runtime.

Open questions the shape stage owns:

1. **Where the defect is.** Three candidates, and the answer decides who owns the fix:
   the vendored `pr-merge.md` overreaches (it should gate PR-delivered entities, not all
   terminalization); or the `spacedock` binary's guard is broader than the mod it enforces;
   or `README.md:69`'s conditional scoping is the inaccurate line and terminalization
   genuinely should require a PR. Read the binary's guard before assuming the mod is wrong.
2. **What authenticates a knowledge outcome**, if not a merged PR. The candidate already
   present in this workflow is the entity's own recorded evidence plus a Captain gate — the
   same authority that admits the work. Whatever is chosen has to be as hard to fake as a
   merged PR, or the guard has been weakened rather than scoped.
3. **Whether the fix belongs upstream.** `pr-merge` is vendored from Spacedock. A local edit
   fixes this repository and drifts from source; an upstream change fixes every adopter and
   waits on someone else's release. This is the same keep-local-or-send-upstream question the
   retired improvement transport existed to answer, and it no longer has a mechanism.

Non-goals: changing how PR-delivered entities terminalize, weakening the merged-PR requirement
where a PR *is* the delivery artifact, and relaxing the guard by making `--force` routine.

## Historical acceptance evidence

A knowledge-output entity terminalizes without `--force`, and a PR-delivered entity still
cannot terminalize on an unmerged or absent PR. Both proven by attempting each, not by reading
the configuration. The two contradicting statements now say the same thing, and something
fails if they diverge again.

## Historical measurement

Entities stuck non-terminal with an accepted outcome and no delivery artifact. Currently at
least one (`digest-effect-unmeasured`).


## Historical provenance

The exact original `source` value is preserved below before the First Officer removes it from planning metadata. It records local discovery, not a provider planning receipt. No planning-provider reconcile or external posting is implied.

```yaml
source: "Blocked while closing digest-effect-unmeasured, 2026-08-20. That task's accepted output was a measurement verdict, not a diff. It has no PR and no worktree, and the mechanism refused its terminal transition: 'workflow has merge hook(s) [pr-merge] that have not run (pr field is empty and mod-block is empty)'."
```

## Development Brief

Standalone approved work. Kent approved the native knowledge-delivery dependency scope and Pilot profile in the current conversation. The approval refers to the manual Pilot's frozen ideation Briefing digest `ef2a004507cdb9033f64aca96dd1e608cd93ff4212c29a3333963722d547dede` at `dev-flow-manual-improvement-pilot/review/ideation/briefing-1/index.json`; it is a Briefing digest, not a Git revision. Reuse the [accepted shape](dev-flow-manual-improvement-pilot/shape-evidence/shape.md) and its existing [native probe](dev-flow-manual-improvement-pilot/shape-evidence/native-probe.py) / [raw captures](dev-flow-manual-improvement-pilot/shape-evidence/native-probe.json). This task remains the existing defect owner; the manual improvement cycle stays a separate dependent task. Kent subsequently approved the exact eight-file/850-gross-line archive-integration proposal in [candidate summary](knowledge-output-cannot-terminalize/implementation-evidence/candidate-summary.md) with `批准`; the current boundaries below incorporate that amendment without replacing prior evidence.

## Problem

Spacedock 0.27.2's native merge consumer blocks an accepted knowledge-only result carrying the locally documented `local-merge:{reason}` value. Its success exit code can carry `signal: blocked` and leave approval pending. A rejected verdict syntactically finalizes but misrepresents the original approved experiment outcome `change`; an arbitrary hash or unrelated PR would invent delivery proof. Earlier successful direct archive observations did not prove this native terminal approval consumer.

## Accepted outcome

Provide an explicit native knowledge-delivery route in `merge guard` (the approved design proposes `--delivery knowledge`) which checks an already approved terminal briefing binding a no-product-diff outcome and retained evidence, refuses an open PR or product-delivery commitment, then reuses native locked approval consumption, finalize, archive and publication. Preserve genuine `pr-merge:{number}` and `local-merge:{sha}` behavior and all existing product-delivery safeguards. After executable support is verified, narrowly correct the local mod's invalid reason-sentinel instruction.

## Non-goals

No forced status/archive, invented merge credential, unrelated PR, rejected-verdict reinterpretation, alternate archive bypass, weakened product PR requirement, replacement workflow engine, new gates frontmatter approval schema or separate approval protocol/consumer, broad local mod refit, duplicate defect task, manual improvement-cycle implementation, recurring scheduler, paid/cloud execution, automatic external posting, automatic merge/release, consumer migration, production support commitment, or live original-task/approval/resource mutation by this implementation worker. The expressly approved exception is extension of the existing native locked terminal consumer and frozen Briefing artifact semantics within the eight named upstream files; it creates no second consumer or authority. Product commit, push, PR, merge, installation and original cleanup retain their existing explicit authority boundaries.

## Acceptance criteria

- **AC-1** A native disposable accepted-knowledge case with the explicit route and an approval bound to its no-product-diff outcome/evidence finalizes PASSED, consumes exactly that pending terminal approval and retains the evidence; `rc=0` without `signal=finalized` does not pass.
- **AC-2** Native attempts with no approval, changed briefing/evidence, an open PR, or a product-delivery commitment are refused before terminalization/approval consumption; the explicit knowledge flag alone is insufficient authority. The tests must exercise each refusal, not merely assert field presence.
- **AC-3** Genuine merged PR and local-merge sentinel paths retain their prior behavior, while open/absent product PR proof and invented reason sentinels remain non-terminal. No change to genuine local-merge meaning or use of rejected verdict substitutes for accepted knowledge.
- **AC-4** Native accepted knowledge archives once with durable evidence and approval consumption, binding the same consumed approval and frozen evidence to the exact archived bytes. After publication of a clean committed archive fails, native state commit recovery resumes without a second approval spend/archive. Conflicting state publication and tampered archive proof/bytes stop without silently overwriting peer edits. The inherited hard crash between rename and archive commit is outside this repair.
- **AC-5** A disposable copy of the real original `first-cloud-dev-flow-improvement-run` snapshot reproduces the existing blocked path and proves the corrected explicit route against its accepted change/no-product-diff evidence. Retain source revision/hash, raw outputs, exits and state readback, and prove the real task, frozen approval, pins and cloud resources remain untouched. Any required reauthorization/rebinding is surfaced, never fabricated in the real record; actual original terminalization/cleanup/final check remain separately owned work.

## Route-back conditions

Stop and return the observed scope delta if correct authority binding requires a new gates frontmatter approval schema, separate approval protocol/consumer, any upstream file beyond the eight named files, over 850 total added-plus-deleted upstream lines against af70297ddae6ec64444849e8e3fcf57484bc16e1, more than the one named local mod file, or over 40 added-plus-deleted local lines. Unresolved product-scope proof returns to design rather than accepting a flag, arbitrary hash, or unverified zero-product claim. Do not weaken the predicate to fit the count. Consumer migration, replacement state authority, new paid execution, expanded permissions or production/release support require the Captain's corresponding new choice. Product behavior uncertainty or a real conflict stops at the existing owner boundary.

## Approved implementation shape

OBSERVED: the retained native probe supplies the refusal: an approved accepted-knowledge case returns exit 0 with blocked signal, unchanged active bytes and pending approval. Its synthetic rejected case finalizes but changes meaning. The dispatch's bounded upstream check found the same classifier on main `af70297ddae6ec64444849e8e3fcf57484bc16e1`; that is evidence at shape time, not permission to assume today's base.

DESIGNED: `merge guard --delivery knowledge` selects the explicit route and binds the exact prechecked attempt ID and Briefing digest to the existing `FinalizeTerminalApproval` consumer. Under its existing lock, the consumer compares those identities, resolves the frozen approved artifact through existing Git-source validation, requires a knowledge-only evidence declaration with explicit product scope/base/head and no product difference, and refuses a live PR/sentinel/product commitment. A no-product claim is checked against its bound scope, not accepted as a boolean or arbitrary hash; absence of product scope is an explicit typed claim reviewed by the human, not inferred from prose.

Reuse Briefing v1 artifacts for this declaration, without a new gates frontmatter schema or separate approval receipt. The knowledge write compares the whole checked entity snapshot so PR/body changes cannot survive that check. The native archive owner in internal/status/mutate.go reuses verification of the same consumed approval, frozen evidence, terminal PASSED state and empty PR, binding the validated snapshot to the exact bytes moved under native locking/comparison. Ordinary product delivery retains existing behavior; native archive, publication, conflict handling and resume remain the owners. Positive/archive-once, committed-archive publication-failure resume, conflict and tamper proof are required; the inherited rename-before-commit hard crash remains out of scope. Local mod prose changes only after executable proof. All positive/refusal/recovery acceptance evidence remains pending.

| Exact file | Estimated gross additions plus deletions | Purpose |
| --- | ---: | --- |
| Upstream `internal/status/merge.go` | 45–70 | explicit route and exact authority passed to native finalize |
| Upstream `internal/status/merge_guard_test.go` | 140–180 | native positive/refusal/archive/recovery and original-copy cases |
| Upstream `mods/pr-merge.md` | 20–30 | supported knowledge route and evidence contract |
| Upstream `internal/gates/delivery.go` | 100–140 | frozen evidence and exact approval checked under existing lock |
| Upstream `internal/gates/delivery_test.go` | 130–180 | approval substitution, product/PR drift, evidence tamper and single consumption |
| Upstream `internal/gates/io.go` | 15–25 | whole checked entity comparison for knowledge write |
| Upstream `internal/cli/help.go` | 5–10 | supported explicit flag help |
| Upstream `internal/status/mutate.go` | 20–35 | same-consumed-approval archive proof and exact archived-byte binding |
| Separate local `docs/dev/_mods/pr-merge.md` | at most 40 | narrow correction only after executable support |

The approved upstream stop is 8 named files / 850 gross added-plus-deleted lines against `af70297ddae6ec64444849e8e3fcf57484bc16e1`. The current candidate summary estimates 685–790 gross overall, including shared archive-proof/byte-binding support and positive/recovery/refusal tests; inherited per-file estimates above are not a new measurement or proof of fit. The separate local stop remains 1 named file / 40 gross lines against `c9c5752fda853737d4a937ad7f59564c5651ca53`. Measure `git diff --numstat <pinned-base>`, including tests/docs, without hiding implementation in evidence. Recheck roots, branches, statuses and bases before edits; further file/schema/consumer or product-scope changes return to design.

One upstream repair followed by its narrow existing-consumer prose correction is sufficient. Preserve evidence before any disposable fixture cleanup; no live resource cleanup is part of this worker scope. No new model/provider/cloud execution is authorized here. The broader manual cycle's proposed token/runtime budget is not a budget for this dependency; the First Officer's bounded implementation dispatch supplies its execution cap.

## Captain scope amendment — 2026-09-11

Kent explicitly approved the concrete seven-file / 650-gross-line reshape with `批准` in the current conversation, relayed by the First Officer. This accepts the exact existing-consumer/frozen-artifact/whole-entity extension in [the implementation scope stop](knowledge-output-cannot-terminalize/implementation-evidence/scope-stop.md); its historical “not authorized” wording records the prior stop, now superseded only by this amendment. The same accepted goal, Pilot profile, AC-1 through AC-5, and other non-goals remain in force. Product commits still require exact-file confirmation; no product edits occur until the First Officer creates and dispatches the new stage pin.

This is a human-authorized new scope boundary, not validation feedback or a workaround for a loader/pin refusal. Prior implementation/1 and the earlier ideation pin are immutable historical inputs; the First Officer will create a separate implementation/2 pin and retain both existing files unchanged:

- `knowledge-output-cannot-terminalize/ideation-stage-pin.json`: SHA-256 `c8f1c7c3b6770984ca66c1a2c8fdd07e32a0ac637a622749b0a573609b1df062`.
- `knowledge-output-cannot-terminalize/implementation-stage-pin.json`: SHA-256 `d8e261572377d9a930675e90ee42a1a4ada821a9f00511a44506ec3b13678c64`.

The original cloud experiment's semantic archival approval persists, but its frozen Briefing does not contain the new typed declaration. Native rebinding remains with its owner, preserving old approval history; this amendment neither mutates that live task nor promises that no further human authorization is needed. Historical three-file stage reports and implementation evidence remain unchanged.

## Stage Report: ideation

- DONE: 1. Reuse the accepted native knowledge-delivery shape and preserve historical discovery provenance.
  Approval-bound design: manual Pilot Briefing digest `ef2a004507cdb9033f64aca96dd1e608cd93ff4212c29a3333963722d547dede`; historical `source` bytes retained above before parent metadata correction. No repeated research or new fixture execution.
- DONE: 2. Admit the exact dependency scope, v3 Pilot receipt and falsifiable acceptance criteria.
  AC-1, AC-2, AC-3: accepted explicit-route design and retained native refusal distinguish bound knowledge from product delivery and invented proof; all positive implementation checks remain pending.
- DONE: 3. Bound persistence/recovery, real-snapshot verification and exact file/diff stop conditions.
  AC-4, AC-5: archive-once/recovery and copied original-task proof are designed requirements; the original task/approval/resources remain untouched. Three upstream files/250 gross lines and separate local one-file/40-line limits apply.
- SKIPPED: 4. Implement or validate the repair, change gates/frontmatter, or close the original experiment.
  This is an approved report-only admission handoff; implementation and independent acceptance proof belong to subsequent dispatched work.

### Summary

The existing defect owner now carries the approved standalone Development Brief, v3 Pilot receipt and bounded shape using the already retained evidence. Historical claims are preserved and clearly separated from current authority. Product implementation, positive native proof and original experiment closure remain pending.


## Stage Report: ideation (cycle 2)

- DONE: Confirm the committed current Development Brief and already-approved shape match the native knowledge-delivery repair, preserving original task authority.
  The current brief, Approved implementation shape and prior ideation report agree: AC-1 explicit approved knowledge finalization; AC-2 refusal controls; AC-3 genuine product-delivery semantics; AC-4 archive-once recovery; AC-5 copied-original proof. These are design mappings, not passing implementation evidence.
- DONE: Validate installed profile loading against ideation/1 and report only unresolved implementation dependencies; do not repeat existing research or probes.
  Installed 4.3.0 loader exited 0 against the committed ideation/1 pin: pilot-product-slice, shape, next implementation; contract digest cc4915cc2e4d5407d174a5eef77bb64ca078bc098f533e83db00f98785413558. The receipt, pin and approved authority bytes were preserved.

### Summary

The approved native knowledge-delivery shape is ready for the implementation handoff; no research, probes or product edits were repeated. Remaining dependencies are live base/file-count confirmation, implementation and fresh AC-1 through AC-5 proof within three upstream files/250 gross lines plus the separate one-file/40-line local correction; original-task terminalization and cleanup remain separately owned.


## Stage Report: implementation

- FAILED: Implement the approved explicit native knowledge-delivery route with real bound terminal approval/evidence and refusal controls; preserve existing product delivery behavior.
  Scope stop before product edits: [decisive native seam and proposed exact reshape](knowledge-output-cannot-terminalize/implementation-evidence/scope-stop.md); existing writer cannot bind a prechecked knowledge predicate without extending the approved file boundary.
- FAILED: Prove archive-once and interrupted-publication recovery plus copied original experiment snapshot, retaining raw outputs and source hashes without mutating real approval or resources.
  Original-copy baseline reproduced blocked/pending; no corrected candidate exists, so positive/archive/recovery proof is absent. All 18 real source files match retained hashes; cloud/resource operations zero.
- SKIPPED: Apply the narrow local mod correction only after executable support, run required focused/full/race checks, and return exact uncommitted diffs for Captain confirmation.
  No executable support; local mod stays unchanged. Existing focused tests 48 pass/0 fail; full suite interrupted at First Officer scope stop; race/gofmt and local contract deferred with no candidate.

### Acceptance evidence

- AC-1: NOT SATISFIED. [Copied original raw outputs](knowledge-output-cannot-terminalize/implementation-evidence/copied-original-baseline.json): baseline rc=0/signal=blocked; proposed explicit flag rc=1/unknown argument; no finalized candidate.
- AC-2: NOT SATISFIED. Missing exact-attempt/digest consumer constraint and full-entity comparison are source-proven at gates/delivery.go:26-48 and gates/io.go:313-369; proposed falsifiers are documented, not claimed executed.
- AC-3: BASELINE ONLY. [Focused tests](knowledge-output-cannot-terminalize/implementation-evidence/checks.json) exercise merged/open/malformed sentinels, native gate refusal and one locked approval replacement; changing these behaviors would fail their existing outcome/state assertions. 48 passed, zero failed; unchanged product code is not knowledge support.
- AC-4: NOT SATISFIED. No knowledge candidate exists; archive-once, publication interruption, conflict and native resume are deferred, not inferred from baseline checks.
- AC-5: PARTIAL. [Source hashes](knowledge-output-cannot-terminalize/implementation-evidence/original-source-hashes.json), byte-identical readonly snapshot and [post-probe readback](knowledge-output-cannot-terminalize/implementation-evidence/scope-stop-readback.json) prove original task/briefings/pins/evidence unchanged. Existing semantic archival approval persists; a new typed declaration is not machine-bound and requires explicit native rebinding by its owner.

### Exact candidate and boundary

- Upstream base: af70297ddae6ec64444849e8e3fcf57484bc16e1; COORD base: c9c5752fda853737d4a937ad7f59564c5651ca53. Both isolated product trees clean; both empty diff SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; 0 changed files/0 gross lines.
- Proposed reshape only: add gates/delivery.go, gates/delivery_test.go, gates/io.go and cli/help.go to the original three upstream files; estimate 455-635 gross lines, proposed stop 7 files/650 gross lines. Local consumer retains 1 file/40 gross lines. No new gate schema/protocol, installation, product commit, external delivery, paid execution or subagents.
- RoboRev observation: UNAVAILABLE (no committed candidate); zero requests, zero confirmations. Surface map and independent candidate review are inapplicable until a candidate exists. Required full/race/format exit checks remain outstanding.

### Summary

Implementation is incomplete and stopped at the explicit additional-consumer/file scope boundary, accepted by the First Officer. The existing frozen Briefing remains immutable evidence but does not supply a typed knowledge-delivery predicate; the smallest proposed repair extends the existing locked consumer and its tests, with exact authority and whole-entity drift checks, then reuses native archive/publication. The original task and approvals were preserved; no product changes were made.


## Stage Report: implementation (cycle 2)

- FAILED: Implement the approved explicit native knowledge-delivery route with real bound terminal approval/evidence and refusal controls; preserve existing product delivery behavior.
  Concrete seven-file candidate implements the locked approval/evidence consumer and refusal controls, but the native journey still fails at the unmodified archive owner; [candidate summary](knowledge-output-cannot-terminalize/implementation-evidence/candidate-summary.md).
- FAILED: Prove archive-once and interrupted-publication recovery plus copied original experiment snapshot, retaining raw outputs and source hashes without mutating real approval or resources.
  Consumer one-use/resume passes; archive-once/publication recovery and positive original rebinding remain unproven. All 18 real original files match retained hashes; cloud/resource operations zero.
- SKIPPED: Apply the narrow local mod correction only after executable support, run required focused/full/race checks, and return exact uncommitted diffs for Captain confirmation.
  Local mod stays unchanged because native archive support is incomplete. Exact uncommitted upstream patch retained; required full/race/full-tree format and local contract checks deferred at the First Officer's explicit partial-integration boundary.

### Acceptance evidence

- AC-1: PARTIAL. [Base failure](knowledge-output-cannot-terminalize/implementation-evidence/knowledge-before.stdout) was unknown --delivery; consumer now writes PASSED/consumed once. [Native integration](knowledge-output-cannot-terminalize/implementation-evidence/knowledge-archive.stdout) reports done/PASSED/consumed, archive=false, then empty-PR refusal; no finalized success is claimed.
- AC-2: CONSUMER PROOF. Tests exercise missing approval/declaration, wrong attempt/digest, true successor substitution, Briefing tamper, invalid evidence hash, duplicate declaration, open PR/invented reason, product claim/diff/dirty checkout/head drift, whole-entity PR/body drift, and tampered consumed verdict/decision. Removing their checks allows forbidden consumption or overwrites and fails the corresponding byte/state assertion.
- AC-3: BASELINE REGRESSION. [Focused run](knowledge-output-cannot-terminalize/implementation-evidence/candidate-focused.json) has 65 passing events/0 failures including existing merged/open/malformed sentinel and terminal delivery tests; [CLI run](knowledge-output-cannot-terminalize/implementation-evidence/candidate-cli.json) has 20/0. Final exact-worktree binding addition then passed valid/changed-worktree subcases; broader runs precede this small addition, not a claimed final full sweep.
- AC-4: PARTIAL. TestKnowledgeApprovalRefusalsAndResume validates consumed original approval/digest/frozen proof/terminal PASSED/completed on retry without rewriting or spending twice. Native archive integration remains 1 failure; publication-failure/conflict/resume proof awaits the archive owner change. Pre-existing rename-before-commit hard-crash recovery is outside this bounded repair.
- AC-5: PARTIAL. [Complete main/state Git-object copy](knowledge-output-cannot-terminalize/implementation-evidence/copied-original-candidate-bound-roots.json) refuses the original reason sentinel unchanged; the earlier candidate-copy result lacked a main Git object and is fixture limitation only. Neither proves a typed positive route. [Original preservation](knowledge-output-cannot-terminalize/implementation-evidence/original-preserved-cycle-2.json) verifies all 18 source files; existing semantic approval persists, typed native rebinding stays with its owner.

### Exact candidate and remaining decision

- Upstream base af70297ddae6ec64444849e8e3fcf57484bc16e1; 7 files/547 gross lines; [uncommitted patch](knowledge-output-cannot-terminalize/implementation-evidence/upstream-candidate.patch) SHA-256 9877481465237f39ee4450235d2a68a1e59710049626168c58e873952a8cad96. No product commit/push/PR/install.
- COORD base c9c5752fda853737d4a937ad7f59564c5651ca53; clean/zero diff, SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855. All three task pins unchanged; [readback](knowledge-output-cannot-terminalize/implementation-evidence/candidate-readback.json) records hashes, numstat and exact final targeted check.
- Smallest remaining file: internal/status/mutate.go runArchive, reusing gates proof of the same consumed knowledge approval and binding the actual archived bytes. No generic consumed flag, force, fake sentinel, policy change or alternate archive. Estimated integrated total 685–790 gross including required native recovery tests; recommend one 8-file/850-gross decision, not a promise to fit 650. Local 1-file/40 bound unchanged.
- Focused formatting and diff --check pass. Manual mapping names all five non-test surfaces; installed surface-map checker requires a committed candidate object and was not given a fabricated revision. RoboRev UNAVAILABLE, zero requests; full exit and independent candidate validation remain outstanding.

### Summary

The authorized seven-file work is now concrete and reviewable, with passing constrained-consumer/refusal evidence and an intentionally retained failing native archive test. The archive owner's separate empty-PR check is the remaining eighth-file integration boundary, so implementation is incomplete; product diffs remain uncommitted for exact-file confirmation. Original approvals, task evidence, pins and resources remain untouched.


## Captain scope amendment — 2026-09-11 (eight-file archive integration)

Kent explicitly replied `批准` to the exact eight-file/850-gross-line proposal in [candidate summary](knowledge-output-cannot-terminalize/implementation-evidence/candidate-summary.md), as relayed by the First Officer. This human-approved boundary adds only `internal/status/mutate.go` to the prior seven upstream files, with at most 850 added-plus-deleted lines against `af70297ddae6ec64444849e8e3fcf57484bc16e1`. The separate local `docs/dev/_mods/pr-merge.md` allowance remains one file/40 gross lines, after executable support.

The approved extension binds the same consumed approval and frozen evidence to the exact archived bytes, and requires positive/archive-once, clean committed-archive publication-failure resume, conflict and tamper proof. The inherited hard crash between rename and archive commit remains outside scope. The original live task, approval and resources stay untouched; no product commit, installation, provider access or new cloud execution is authorized. Existing product delivery, push/PR/merge and original cleanup authority boundaries remain in force.

This amendment updates current scope only; all historical amendments/reports and existing stage-pin bytes are preserved. The First Officer will create a separate `implementation/3` pin from the committed amended authority before dispatch; `implementation/2` is retained, never replaced to bypass a refusal. No product edits or new implementation/acceptance pass are claimed by this body-only amendment.


## Stage Report: implementation (cycle 3)

- DONE: Implement the approved explicit native knowledge-delivery route with real bound terminal approval/evidence and refusal controls; preserve existing product delivery behavior.
  The integrated eight-file candidate reuses the existing locked terminal consumer and archive owner, binds exact attempt/digest/frozen evidence and whole checked bytes, and preserves legacy product paths. [Review summary](knowledge-output-cannot-terminalize/implementation-evidence/integrated-summary.md); product remains uncommitted.
- DONE: Prove archive-once and interrupted-publication recovery plus copied original experiment snapshot, retaining raw outputs and source hashes without mutating real approval or resources.
  Native positive/refusal/recovery tests and complete copied-original synthetic binding pass. All 18 live original files match retained source hashes. No cloud, resource cleanup, provider or live approval mutation.
- DONE: Apply the narrow local mod correction only after executable support, run required focused/full/race checks, and return exact uncommitted diffs for Captain confirmation.
  Focused knowledge tests and local contract pass. Required full/race/format commands all ran; full and race each retain the identical pre-existing external cask failure reproduced on untouched base. This checklist records work performed, not all-green suite acceptance or permission to commit.

### Acceptance evidence

- AC-1: IMPLEMENTED / LOCAL PROOF. [Focused native run](knowledge-output-cannot-terminalize/implementation-evidence/integrated-focused.json) has 29 pass events, 0 fail, 0 skip. TestKnowledgeMergeNativeArchive proves finalized/PASSED/consumed, active entity absent and one native archive. Required full/race runs include existing product regression coverage.
- AC-2: REFUSAL PROOF. TestKnowledgeApprovalRefusalsAndResume and TestKnowledgeWholeEntityExpectation reject missing approval/declaration, wrong attempt/digest, real successor substitution, Briefing/evidence tamper, duplicate declaration, open PR/reason sentinel, product claim/diff/dirty checkout/head drift, changed worktree, whole-entity drift and tampered consumed approval/verdict. TestKnowledgeArchiveRejectsTampering rechecks the same consumed authority/evidence and actual bytes at the archive owner. Removing these constraints fails corresponding state/byte assertions.
- AC-3: PRODUCT REGRESSION PROOF. Existing genuine local-merge/pr-merge sentinels and merged/open/malformed delivery tests pass in the required suites. Full suite: 3,104 pass events, 2 fail events (one leaf plus parent), 11 skip; race: same counts and no data-race diagnostic. The sole failed leaf is TestContractCasks/edge-satisfies-pin: edge cask 0.27.1 below unchanged contract pin 0.28. [Serial candidate and untouched pinned-base controls](knowledge-output-cannot-terminalize/implementation-evidence/release-cask-control.json) reproduce the same failure. No release/install change or broad green claim.
- AC-4: RECOVERY PROOF. TestKnowledgeArchivePublicationRecovery covers native archive-once, clean committed-archive publication failure, native publish resume/no-op, and true peer conflict preservation; TestKnowledgeFailedCommitPreservesInterveningEdit prevents rollback clobbering later writes. Consumed retry revalidates original approval/binding/verdict/frozen proof without spending twice. The inherited hard crash between archive rename and commit remains outside scope.
- AC-5: COPIED ORIGINAL PROOF. [Complete Git-source original copy](knowledge-output-cannot-terminalize/implementation-evidence/copied-original-native-complete.json) reproduces blocked original reason sentinel, explicit refusal, then TEST ONLY native supersession/new declaration/new synthetic approval, finalized/unpublished after injected push rejection, and native recovery with identical archive bytes and HEAD. Historical approval is preserved as superseded in the copy. [Source preservation](knowledge-output-cannot-terminalize/implementation-evidence/original-preserved-cycle-3.json) proves all 18 live original files and records current task pins. Existing real semantic archival approval persists but never machine-bound this new declaration; live rebinding remains with its owner and no automatic reauthorization or original POC closure is claimed.

### Exact candidate and verification boundary

- Upstream base/head af70297ddae6ec64444849e8e3fcf57484bc16e1; eight approved files / 743 gross lines; [uncommitted patch](knowledge-output-cannot-terminalize/implementation-evidence/integrated-upstream.patch) SHA-256 cabbdd5221aec0b94597f4aeaca455810fe75b90922d76c4226fefda7547efe5.
- Coordinator base/head c9c5752fda853737d4a937ad7f59564c5651ca53; only docs/dev/_mods/pr-merge.md / 24 gross lines; [uncommitted patch](knowledge-output-cannot-terminalize/implementation-evidence/integrated-coord.patch) SHA-256 2ffa88aaef51a4b482a71d190b5f3cbcbc2a5579d539a7cb87adfab12d685d0c. Both branches remain spacedock-ensign/knowledge-output-cannot-terminalize; both diff --check pass. [Exact readback](knowledge-output-cannot-terminalize/implementation-evidence/integrated-readback.json).
- Raw commands/exits/counts: integrated-focused.{json,stdout,stderr}, integrated-full.{json,stdout,stderr}, integrated-race.{json,stdout,stderr}, integrated-local-contract.{json,stdout,stderr}, integrated-format.{json,stdout,stderr}. Local kc-dev-flow contract PASS. Full/race both rc=1 only for the reproduced pre-existing cask assertion; skipped tests remain skipped, not claimed proven.
- Required gofmt returned 0 and exposed only a pre-existing four-line whitespace delta in internal/release/runtime_live_evidence_workflow_test.go outside scope. Exact gofmt(HEAD) comparison proved its origin; only that delta was restored and retained as preexisting-gofmt.{json,patch}. Full run began before restoration; race and isolated controls bind final intended source. No ninth file included.
- [Manual surface map](knowledge-output-cannot-terminalize/implementation-evidence/integrated-surface-map.md) names all six upstream non-test surfaces and the local mod. Object-based checker and RoboRev UNAVAILABLE without an authorized product commit; zero RoboRev/provider requests. Fresh independent validation and exact-file Captain confirmation remain before product commit, delivery or installation.

### Summary

The approved integrated repair and local consumer correction are concrete, within both limits, and supported by positive native finalization, refusal, archive-once, publication recovery, conflict and complete copied-original proof. Required suites were executed and the sole failing release-state assertion also fails on the untouched base; this is not represented as an all-green suite. Exact product diffs remain uncommitted for independent review and Captain confirmation. Original live task approval, evidence and resources remain unchanged; no original closure or new cloud proof is claimed.


## Stage Report: validation

- FAILED: Independently verify the exact upstream and local candidate against AC-1 through AC-5, approved eight-file/850 and local one-file/40 scope, and native authority/data safety.
  Exact hashes and scope pass, but AC-4 loses a peer edit on failed archive commit; [independent review and smallest fix](knowledge-output-cannot-terminalize/validation-evidence/review.md).
- FAILED: Exercise meaningful native knowledge finalization/refusal/archive-once/committed-publication recovery cases; verify complete candidate test evidence and original-copy proof without altering live records.
  Fresh existing focused cases: 74 pass/0 fail/0 skip. Independent pre-lock-edit regression fails; retained before/after bytes prove data loss. Full/race raw logs and copied-original proof audited, all 18 live original hashes preserved.
- DONE: Review changed-surface necessity and consumer documentation, report exact hashes and all residuals, and preserve a durable validation verdict without product commits or external delivery.
  All 8 upstream/1 local surfaces reviewed and mapped; no scope excess or unmapped addition. Report/evidence only; no product mutation, provider/model/cloud call, installation or original closure.

### Acceptance evidence

- AC-1: PASS. TestKnowledgeMergeNativeArchive freshly reports finalized/PASSED/consumed with no active entity; missing native archive integration would fail it.
- AC-2: PASS for exercised native controls. Exact approval/successor/evidence/product/PR/whole-entity refusal cases preserve bytes; deleting the predicate allows forbidden consumption and fails those assertions.
- AC-3: PASS. Fresh merge regression preserves genuine sentinels and refuses open/malformed/missing product proof; explicit knowledge does not reinterpret rejection.
- AC-4: FAIL. `internal/status/merge.go:497-505` permits rollback of a stale snapshot read at line 750 and restored at line 803. [Independent raw failure](knowledge-output-cannot-terminalize/validation-evidence/rollback-prelock.json) shows peer edit in archived bytes before failed commit, absent after rollback. This is not the excluded hard crash.
- AC-5: VERIFIED PRODUCER PROOF. [Readback](knowledge-output-cannot-terminalize/validation-evidence/copied-original-audit.json) matches retained copy archive hash/HEAD and consumed synthetic approval; baseline blocked, native test-only rebinding and publication resume are explicit. All 18 real original files unchanged; live rebinding/cleanup/final check remain separately owned.

### Exact candidate and residuals

- Upstream patch SHA-256 `cabbdd5221aec0b94597f4aeaca455810fe75b90922d76c4226fefda7547efe5` against `af70297ddae6ec64444849e8e3fcf57484bc16e1`: 8 files/743 gross; local patch `2ffa88aaef51a4b482a71d190b5f3cbcbc2a5579d539a7cb87adfab12d685d0c` against `c9c5752fda853737d4a937ad7f59564c5651ca53`: 1 file/24 gross. [Final unchanged root/branch/hash readback](knowledge-output-cannot-terminalize/validation-evidence/final-readback.json).
- Full/race producer logs each have 3,104 pass/11 skip and one cask leaf failure plus parent; same release-state failure reproduced on untouched base. Race binds final patch; full preceded restoration of an unrelated pre-existing whitespace delta. No all-green claim or delegated acceptance of red residuals.
- Object-based source map and optional RoboRev remain UNAVAILABLE without an authorized product commit. No candidate objects fabricated. Exact-file commit approval, PR/delivery/provider checks, installation and original live closure remain outstanding.
- project_context: impact `none`; bound PRODUCT.md, ARCHITECTURE.md and CLAUDE.md retain their plugin/profile/loading/ownership claims. Fresh validation compared their stated surfaces with the full diff and native outcomes; review.md records scope and necessity.

### Summary

REJECTED: the accepted recovery/data-safety journey has one independently reproduced data-loss defect despite passing ordinary native cases. Bind the rollback preimage to the same checked under-lock entity snapshot or refuse unsafe rollback, within existing approved surfaces; retain this regression for one final recheck. Product candidates remain byte-identical and uncommitted; this verdict does not accept the separate existing red release-state constraint.


## Stage Report: implementation (cycle 4)

- DONE: Implement the approved explicit native knowledge-delivery route with real bound terminal approval/evidence and refusal controls; preserve existing product delivery behavior.
  Corrected the independently rejected AC-4 rollback data loss within the existing scope. Knowledge rollback retains current consumed bytes while reversing location/index staging; legacy product rollback is unchanged. No redundant preimage field, callback or rejection predicate remains. [Correction summary](knowledge-output-cannot-terminalize/implementation-evidence/correction-summary.md).
- DONE: Prove archive-once and interrupted-publication recovery plus copied original experiment snapshot, retaining raw outputs and source hashes without mutating real approval or resources.
  Both pre-consume and consume-to-archive peer edits now survive actual archive commit failure and native consumed retry. Unchanged independent reproducer passes; historical copied-original proof is retained with its predecessor hash, all 18 live originals remain unchanged.
- DONE: Apply the narrow local mod correction only after executable support, run required focused/full/race checks, and return exact uncommitted diffs for Captain confirmation.
  Local candidate and its passing contract proof remain unchanged. Corrected focused tests pass; full/race each retain only the previously controlled cask exception. Required formatting ran without absorbing unrelated formatting. No product commit or acceptance claim.

### Acceptance evidence

- AC-1: Final-source focused run has 76 passing test events, 0 fail, 0 skip, covering native knowledge finalization and existing delivery cases. [Raw command/hash/counts](knowledge-output-cannot-terminalize/implementation-evidence/correction-final-focused.json) bind the corrected uncommitted SHA-256, not a fabricated Git revision.
- AC-2: Approval identity, immutable evidence, product/no-diff checks, whole-entity write and consumed retry constraints are unchanged from independent validation; current focused/full/race runs exercise their refusal controls. Only merge.go and merge_guard_test.go differ from the rejected candidate.
- AC-3: Legacy rollback restores prior bytes as before, while knowledge rollback preserves consumed current bytes. Existing merged/open/malformed product cases pass. Corrected full/race each report 3,107 pass events, 2 fail events (one cask leaf plus parent), 11 skips; no data-race diagnostic. The unchanged TestContractCasks/edge-satisfies-pin failure remains edge 0.27.1 < pin 0.28, previously reproduced on untouched af70297 base. No all-green suite claim or release/install scope change.
- AC-4: CORRECTED / AWAITING INDEPENDENT RECHECK. TestKnowledgeRollbackPreservesPeerEdit injects peer body writes in both intervals, captures bytes in a failing pre-commit hook, requires byte-identical live restoration retaining the peer edit/consumed approval, and then successful native retry with one consumed approval. [Removing only the correction](knowledge-output-cannot-terminalize/implementation-evidence/correction-window-red.json) makes both cases fail. [Unchanged independent reproducer](knowledge-output-cannot-terminalize/implementation-evidence/correction-final-independent-replay/result.json) now shows actual failed commit, archived peer edit present, live=true, peer_edit_retained=true. Existing publication recovery, conflict and later-intervening-edit refusal tests pass. Pre-existing rename-before-commit hard crash remains excluded.
- AC-5: [Current preservation/readback](knowledge-output-cannot-terminalize/implementation-evidence/correction-readback.json) verifies the same 18 original source hashes and records unchanged task pins. Complete copied-original synthetic binding/publication recovery remains predecessor evidence at cabbdd5221aec0b94597f4aeaca455810fe75b90922d76c4226fefda7547efe5, independently reviewed; this correction freshly proves the affected rollback/retry path. It neither mutates nor reauthorizes the live original, and does not claim original task/resource closure or new cloud proof.

### Exact correction and review handoff

- Upstream base/head af70297ddae6ec64444849e8e3fcf57484bc16e1; same eight approved files / 801 gross lines; [corrected uncommitted patch](knowledge-output-cannot-terminalize/implementation-evidence/correction-upstream.patch) SHA-256 6dc9e67966b29ba29eca9ce28a375081ff6c0345ac32f4ef13846bc8d0e2f93e. COORD base/head c9c5752fda853737d4a937ad7f59564c5651ca53; same one file / 24 gross; [unchanged local patch](knowledge-output-cannot-terminalize/implementation-evidence/correction-coord.patch) SHA-256 2ffa88aaef51a4b482a71d190b5f3cbcbc2a5579d539a7cb87adfab12d685d0c. Both branches unchanged, diff --check passes.
- Required final-source evidence: correction-final-focused.*, correction-full.*, correction-race.*, correction-format.json. Full-tree format's verified pre-existing release-test whitespace was restored before all final runs. Earlier correction-focused.* and correction-independent-replay/ record a superseded preimage-rejection experiment; they are not final-source proof. No rejected evidence, pins or reports were overwritten.
- Installed correction loader accepted implementation-correction-1 with unchanged feedback-validation-1.json and loader-managed correction pin. Task status remains validation. A factual completion Annotation references annotation:rollback-peer-edit-loss and resolution:fo-repair-rollback; the First Officer owns review-round publication and independent recheck.
- Existing manual surface map remains applicable, with this bounded rollback change at merge.go:505,778; object-only map/RoboRev remain unavailable without an authorized product commit, zero requests. Fresh independent acceptance and Captain exact-file confirmation remain outstanding; no product commit/push/PR/install/provider/cloud action.

### Summary

The demonstrated data loss and adjacent consume-to-archive interval are repaired by retaining current knowledge entity bytes during location rollback, then reusing validated consumed-state retry. Both regression cases fail without the correction and pass with it; the independent reproducer now retains the peer edit through a real commit failure. The corrected candidate stays within scope and uncommitted. Required full/race runs retain the separately controlled pre-existing cask failure, so independent validation and acceptance remain with the First Officer/Captain.
