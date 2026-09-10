---
id: geef7a3dy7w12g7tq89h21te
title: "Work whose output is knowledge cannot terminalize: pr-merge requires a merged PR that such work never has"
status: implementation
source:
product: repo-platform
sprint: S8
started: 2026-09-10T16:27:54Z
completed:
verdict:
worktree:
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
  scope_boundary: Upstream internal/status/merge.go, internal/status/merge_guard_test.go, mods/pr-merge.md at most three files and 250 added plus deleted lines; separate local docs/dev/_mods/pr-merge.md follow-up at most one file and 40 added plus deleted lines.
  semantics_unchanged: false
  promote_when: [Consumer migration, Replacement state authority, Production support or release ownership]
  decision:
    authority: Kent explicitly approved the Pilot scope and upstream repair in the current conversation, as relayed by the First Officer
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

Standalone approved work. Kent approved the native knowledge-delivery dependency scope and Pilot profile in the current conversation. The approval refers to the manual Pilot's frozen ideation Briefing digest `ef2a004507cdb9033f64aca96dd1e608cd93ff4212c29a3333963722d547dede` at `dev-flow-manual-improvement-pilot/review/ideation/briefing-1/index.json`; it is a Briefing digest, not a Git revision. Reuse the [accepted shape](dev-flow-manual-improvement-pilot/shape-evidence/shape.md) and its existing [native probe](dev-flow-manual-improvement-pilot/shape-evidence/native-probe.py) / [raw captures](dev-flow-manual-improvement-pilot/shape-evidence/native-probe.json). This task remains the existing defect owner; the manual improvement cycle stays a separate dependent task.

## Problem

Spacedock 0.27.2's native merge consumer blocks an accepted knowledge-only result carrying the locally documented `local-merge:{reason}` value. Its success exit code can carry `signal: blocked` and leave approval pending. A rejected verdict syntactically finalizes but misrepresents the original approved experiment outcome `change`; an arbitrary hash or unrelated PR would invent delivery proof. Earlier successful direct archive observations did not prove this native terminal approval consumer.

## Accepted outcome

Provide an explicit native knowledge-delivery route in `merge guard` (the approved design proposes `--delivery knowledge`) which checks an already approved terminal briefing binding a no-product-diff outcome and retained evidence, refuses an open PR or product-delivery commitment, then reuses native locked approval consumption, finalize, archive and publication. Preserve genuine `pr-merge:{number}` and `local-merge:{sha}` behavior and all existing product-delivery safeguards. After executable support is verified, narrowly correct the local mod's invalid reason-sentinel instruction.

## Non-goals

No forced status/archive, invented merge credential, unrelated PR, rejected-verdict reinterpretation, alternate archive bypass, weakened product PR requirement, replacement workflow engine, new approval schema or additional runtime consumer without reshape, broad local mod refit, duplicate defect task, manual improvement-cycle implementation, recurring scheduler, paid/cloud execution, automatic external posting, automatic merge/release, consumer migration, production support commitment, or live original-task/approval/resource mutation by this implementation worker. Product commit, push, PR, merge, installation and original cleanup retain their existing explicit authority boundaries.

## Acceptance criteria

- **AC-1** A native disposable accepted-knowledge case with the explicit route and an approval bound to its no-product-diff outcome/evidence finalizes PASSED, consumes exactly that pending terminal approval and retains the evidence; `rc=0` without `signal=finalized` does not pass.
- **AC-2** Native attempts with no approval, changed briefing/evidence, an open PR, or a product-delivery commitment are refused before terminalization/approval consumption; the explicit knowledge flag alone is insufficient authority. The tests must exercise each refusal, not merely assert field presence.
- **AC-3** Genuine merged PR and local-merge sentinel paths retain their prior behavior, while open/absent product PR proof and invented reason sentinels remain non-terminal. No change to genuine local-merge meaning or use of rejected verdict substitutes for accepted knowledge.
- **AC-4** Native accepted knowledge archives once with durable evidence and approval consumption; repeat/restart after interrupted publication uses existing recovery without a second approval spend/archive. Conflicting state publication stops without silently overwriting peer edits.
- **AC-5** A disposable copy of the real original `first-cloud-dev-flow-improvement-run` snapshot reproduces the existing blocked path and proves the corrected explicit route against its accepted change/no-product-diff evidence. Retain source revision/hash, raw outputs, exits and state readback, and prove the real task, frozen approval, pins and cloud resources remain untouched. Any required reauthorization/rebinding is surfaced, never fabricated in the real record; actual original terminalization/cleanup/final check remain separately owned work.

## Route-back conditions

Stop and return the observed scope delta if correct authority binding requires an additional approval schema/runtime consumer, more than the three named upstream files, over 250 total added-plus-deleted upstream lines, more than the one named local mod file, or over 40 added-plus-deleted local lines. Do not weaken the predicate to fit the count. Consumer migration, replacement state authority, new paid execution, expanded permissions or production/release support require the Captain's corresponding new choice. Product behavior uncertainty or a real conflict stops at the existing owner boundary.

## Approved implementation shape

OBSERVED: the retained native probe supplies the refusal: an approved accepted-knowledge case returns exit 0 with blocked signal, unchanged active bytes and pending approval. Its synthetic rejected case finalizes but changes meaning. The dispatch's bounded upstream check found the same classifier on main `af70297ddae6ec64444849e8e3fcf57484bc16e1`; that is evidence at shape time, not permission to assume today's base.

DESIGNED: the upstream `merge guard` process selects the explicit knowledge route, verifies its bound terminal approval and no-product scope, and hands off to the existing gates-owned locked writer plus archive/publication. On missing/tampered authority or product delivery it refuses without spending approval; after an interrupted publication, native state recovery resumes the existing archive. Local mod prose describes this real native route only after it exists. Fresh verification owns positive, negative-control and copied-original-snapshot proof; none is claimed passing yet.

| Exact file | Previously measured lines | Estimated after | Purpose |
| --- | ---: | ---: | --- |
| Upstream `internal/status/merge.go` | 1049 | 1080–1110 | explicit authority-checked knowledge route |
| Upstream `internal/status/merge_guard_test.go` | 1161 | 1250–1300 | native positive/refusal/recovery and copied-snapshot proof |
| Upstream `mods/pr-merge.md` | 163 | 175–190 | supported route contract |
| Separate local `docs/dev/_mods/pr-merge.md` | 520 | 515–535 | narrow correction after runtime support |

Counts are inherited from the accepted shape's installed 0.27.2 read, unverified against the forthcoming isolated upstream checkout. Before editing, pin the live delivery base and remeasure those exact files; record any drift rather than refitting silently. Measure stop counts from `git diff --numstat <pinned-base>` with additions plus deletions, including tests/docs. Upstream initially permits at most 3 files/250 gross lines; the separate local follow-up permits 1 file/40 gross lines. No other product file is preauthorized by this shape. Evidence stays in task state and must not be used to hide implementation files from the count.

One upstream repair followed by its narrow existing-consumer prose correction is sufficient. Preserve evidence before any disposable fixture cleanup; no live resource cleanup is part of this worker scope. No new model/provider/cloud execution is authorized here. The broader manual cycle's proposed token/runtime budget is not a budget for this dependency; the First Officer's bounded implementation dispatch supplies its execution cap.

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
