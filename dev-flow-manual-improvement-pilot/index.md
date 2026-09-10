---
title: "Pilot: one evidence-complete manual dev-flow improvement cycle"
status: ideation
product: kc-dev-flow
sprint: S8
sprint-readiness: ready
id: 3w83fmy975y617nrfhcy1mqq
gates:
    version: 1
    records:
        - id: gate:3w83fmy975y617nrfhcy1mqq:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:3w83fmy975y617nrfhcy1mqq-backlog-1
              briefing:
                id: briefing:3w83fmy975y617nrfhcy1mqq:backlog:attempt-1:revision-1
                digest: sha256:f4e4d284e5d60d57ff73cc00fdeaadeeb300eacee90a058825a018485ff7f528
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:3w83fmy975y617nrfhcy1mqq:backlog:1
                briefing: briefing:3w83fmy975y617nrfhcy1mqq:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T16:10:48.218365Z"
                decision: approve
                reason: Kent approved the proposed bounded manual Pilot with 同意 and resumed it with 繼續，額度回來了. Admit shaping of the recorded scope; no recurring activation, new cloud execution, product commit, merge or release authority is inferred.
              application:
                target-stage: ideation
                state: consumed
started: 2026-09-10T16:11:49Z
---

# One manually triggered dev-flow improvement cycle

Kent accepted the proposed Pilot with “同意” after the 2026-09-10 experiment debrief: repair the knowledge-only close gap, complete the original archive, then run one manually triggered improvement cycle with complete test evidence and token accounting. This standalone Development Brief records that scope and profile; S8 is execution grouping only, with no provider planning receipt. Automatic scheduling remains a later decision.

## Problem

The initial event-query cloud experiment produced one merged repair (#412), but individual raw test results and whole-cycle actor usage were incomplete. Actual knowledge-only terminalization remains blocked: the mod documents a reason sentinel while Spacedock 0.27.2 accepts a real local-merge hash. The existing `knowledge-output-cannot-terminalize` task owns that defect; do not file a duplicate. A recurring loop would currently repeat these evidence and completion gaps.

## Accepted outcome

A bounded, manually triggered improvement cycle can select one eligible finding, preserve reproducible failure evidence, produce and independently verify a focused repair, and reach an honest close with complete evidence and measured usage. The original experiment's already-approved archive is a prerequisite to live replay. The shape stage first proves or names the exact knowledge-only closure dependency, checks existing fixes, and proposes the smallest reviewable implementation and execution budget.

## Non-goals

No recurring or unattended Routine activation, automatic merge or release, whole-profile coverage claim, new paid provider arrangement, automatic external issue/review posting, production data, destructive cleanup, replacement workflow engine, fabricated usage or delivery proof, or duplicated knowledge-terminalization repair task. This admission authorizes shaping and local proof preparation; a new cloud/model execution waits for its concrete budget and launch configuration. Product commits require Kent's confirmation of exact files. Existing state-tracking commits and original archive approval remain authorized.

## Acceptance criteria

- **AC-1** One manually triggered execution selects one eligible PR feedback item first, otherwise one eligible issue/finding, with a stable deduplication identity and explicit stop/retry limits; duplicate input does not start duplicate work.
- **AC-2** The selected case has retained raw stdout, stderr, exit status and exact code/runtime provenance; a same-case before/after retest and a negative control distinguish an actual repair from a misleading success summary.
- **AC-3** Every participating actor has an explicit usage boundary covering input, cached input, output and reasoning where available; missing fields remain unknown, subsets are not double-counted, and quality outcomes accompany any cost comparison.
- **AC-4** A fresh reviewer evaluates the exact candidate and retained evidence; a known failing control cannot be reported ready. External review publication and merge remain human-authorized.
- **AC-5** The original experiment and the Pilot's selected delivery route reach a legitimate native terminal/archive path, with consumed approval, evidence retained, actual cleanup measurement and successful final check; no forced state or invented merge sentinel is accepted.

## Route-back conditions

Return a concrete scope delta if closure requires changing upstream Spacedock authority, consumer migration, replacing the state engine, paid execution beyond an approved budget, unattended operation, expanded permissions, or a new production commitment. Preserve pending original approval and existing evidence. Unavailable usage or provider evidence is a limitation, not a zero or pass.

## Dependency and next proof

`knowledge-output-cannot-terminalize` is the existing defect owner. Establish live upstream status before implementing a second local workaround. The first shape output must explain the true terminal consumer and demonstrate its riskiest path in a disposable local fixture or explicitly report it blocked. Do not run another cloud baseline merely to rediscover the close defect.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: Retained tooling and evidence for Kent's limited manual improvement runs, with human-owned external mutations and no unattended service commitment.
  route: [shape, build, verify-deliver]
  obligations:
    architecture: [Keep native state and approval authority, reuse the existing finding owner and queue]
    implementation: [Bound one manual cycle and preserve raw evidence and actor usage]
    testing: [Exercise same-case failure and repair plus negative controls and real terminalization]
  scope_boundary: One manual improvement cycle; recurring operation, release, production use and broad profile coverage excluded.
  semantics_unchanged: false
  promote_when: [Unattended recurring operation, consumer migration, production support or rollback duty]
  decision:
    authority: Kent, current conversation approval of the proposed Pilot
    at: 2026-09-10T16:04:06.089743+00:00
```

## Shape decision — 2026-09-11

Shape is complete; implementation and AC acceptance are pending. Recommend one local, manually operated cycle using task-owned evidence files and existing Git, Python subprocess capture, Spacedock state/gate commands, and the existing finding owner. Do not build a scheduler, platform, new provider adapter, or general improvement framework. All admitted non-goals remain unchanged. `semantics_unchanged: false`: native knowledge delivery authority and task-local evidence/selection behavior would change; no change has been implemented.

### Closure dependency and bounded native falsifier

OBSERVED: installed 0.27.2 `internal/status/merge.go:147-157,312-338` recognizes rejected work or authentic merged delivery, not an accepted knowledge-only answer. `format.go:446-450` defines `local-merge:` as a genuine local merge. Local `_mods/pr-merge.md:29-41` instead prescribes a reason suffix. The dispatch's live upstream check pins `spacedock-dev/spacedock` main `af70297ddae6ec64444849e8e3fcf57484bc16e1` to the same classifier; its recent 40 pull requests and related keyword searches found no matching fix, not proof across every branch. Repo PR 261 at `49e6624857aa0c8470638edd5aab8a8b0f7a957e` only exercised archive, not this consumer.

OBSERVED: [native probe](shape-evidence/native-probe.py) created a disposable local Git fixture with a merge hook and synthetic approved terminal gate. [Raw command captures](shape-evidence/native-probe.json) show `gate consume` leaves approval pending; `merge guard --verdict passed` returns exit 0 with `signal: blocked`, active bytes unchanged and no archive. Exit zero alone is therefore not success. The copied fixture's `--verdict rejected` finalizes, but that changes accepted knowledge into rejected work. It is a syntactic escape, not a semantically valid close: the original gate explicitly accepts outcome `change`, and `ARCHITECTURE.md` describes proceed/stop/change as experiment outcomes. No live outcome, approval, original task, or resource was changed.

DESIGNED dependency delta (not admitted implementation): existing `knowledge-output-cannot-terminalize` owns an upstream native knowledge-delivery branch. Add an explicit knowledge route to `merge guard` (proposed `--delivery knowledge`), require an already approved terminal briefing binding the no-product-diff outcome and retained evidence, refuse a live/open PR or product delivery commitment, then reuse the existing gates-owned locked finalize/archive/publish operations. Do not broaden `local-merge:` or repurpose verdict rejected. Preserve valid PR/local-merge paths. The authority predicate must be checked by the consumer, not only prose or a caller flag; if binding it needs additional schema/consumer changes, stop and reshape rather than weaken it.

DESIGNED positive native fixture: same synthetic accepted-knowledge case with the explicit bound route must produce PASSED, consume exactly that pending approval, archive once, retain briefing/evidence, publish state and survive repeated invocation without duplicate consumption. Refusal controls: missing approval, changed evidence/briefing, product/open PR masquerading as knowledge, invented merge reason, and interrupted publish. Existing product PR refusal must remain. A positive fixture is not yet implemented or passing. Actual original cleanup and `poc-close-guard.py check-final` remain pending after a real corrected terminal path.

### One accepted manual journey

1. OBSERVED — installed `profile-contract-loader.py` loads the exact task/README and committed `ideation-stage-pin.json`, attempt `ideation/1`, plugin 4.3.0, digest `cc4915cc2e4d5407d174a5eef77bb64ca078bc098f533e83db00f98785413558`. The pin, receipt and accepted scope are preserved. COORD product tree is clean at `c9c5752fda853737d4a937ad7f59564c5651ca53`; outer kinshasa tree is a separate clean checkout at `6b408ac102978d4bbf3614a7109934191520aa9b`, not the delivery base.
2. DESIGNED — an operator invokes existing `gh` read commands once for eligible PR feedback, otherwise existing issue/finding records. Eligibility means unresolved, locally reproducible, inside the admitted one-case scope, no active owner/duplicate repair, and within budget. Persist selected native comment/node ID (or repo + issue ID; local finding uses existing task ID plus case hash), source revision, source kind, eligibility/exclusion reason and existing owner in task-owned `run/selection.json`; no new external post. Re-read current owner before dispatch. With no eligible case, record no-work and stop.
3. DESIGNED — Python task-local `capture-case.py` atomically claims `run/<source-key>/` with exclusive directory creation; existing running or completed identity returns the stored state without dispatch. Input edits stay the same source identity, require an explicit revision/retry entry, and never silently form new work. Persist run ID and a running marker before child launch. Stale claim after process death requires explicit operator recovery; it cannot auto-relaunch. Git state is the durable owner, not a second tracker.
4. DESIGNED — `capture-case.py` runs an explicit argv in the pinned isolated candidate checkout through `subprocess`, writing exact binary stdout/stderr and metadata: exit/signal/timeout, start/end UTC plus monotonic elapsed, argv, cwd, environment allowlist, input hashes, Git HEAD/diff hash, executable/version and loaded contract hashes. Timeout or disk/export failure preserves partial bytes and marks incomplete. No command is inferred or executed from provider text. Inputs contain synthetic data; raw files are inspected for secrets before state publication, and original bytes stay local if redaction is required.
5. DESIGNED — the authorized implementation agent repairs at most the selected case. A fresh verification process runs the identical case on before and candidate revisions, plus the known failing negative control (for example restore the defective producer); compare exact outputs and exit statuses. One unrelated passing command cannot establish repair. `verify-run.py` refuses missing, mismatched, truncated or tampered captures. Raw file transport/readback with hashes must succeed before any cloud workload; a summarized batched event is insufficient.
6. DESIGNED — existing runtime/session exports provide one usage record per actor: coordinator, implementer, fresh reviewer, any provider/auxiliary calls, and closeout. `run/usage.json` binds actor/session/event IDs and start/end cumulative anchors covering selection through final cleanup/reporting. Record input including cached input, output including reasoning where available, cache-write semantics, scope exclusions and quality outcome. Use cumulative differences OR unique incremental records, never both; cached/reasoning subsets are not added again. Missing fields/actors remain null/unknown and prohibit total-cost or efficiency claims. Monetary totals require actual same-provider rates/billing, not inferred token prices.
7. DESIGNED — the fresh reviewer receives exact candidate SHA/diff plus retained raw before/after/control files and independently runs `verify-run.py`; incomplete usage prevents a complete-cost claim, failing control prevents ready. Persist review verdict and scope in `run/review.md` and existing Stage Report. A correction invalidates the prior exact-candidate verdict. No response, timeout, or reviewer unavailability leaves not-ready; at most one bounded correction/re-review, no automatic paid retry.
8. OBSERVED closure refusal / DESIGNED success — existing `spacedock gate` and corrected native `merge guard` own delivery and archive; PR creation/public review/merge remain Captain-authorized. The original experiment must genuinely close before this live replay. Preserve evidence outside disposable worktrees, measure actual cleanup, and run the original POC final check. For a selected code repair, use its genuine approved PR/local merge route; for no-product knowledge, use the corrected explicit native route, never an alternate archive verb.

### Persistence, recovery and safety

Task folder owns evidence and identity; existing state branch owns lifecycle. No scheduler or independent database. Atomic complete markers follow raw-file fsync/rename; absent markers mean incomplete, never successful. A single local manual operator owns selection; concurrent claim collision stops before launch. Cross-machine concurrent execution is excluded. Resume revalidates source/candidate hashes and authoritative state, then continues only unfinished bookkeeping; rerun needs an explicit attempt and remaining budget. A crashed child is terminated only by its recorded process identity, not broad process-name cleanup. Preserve live cloud resources and existing user work. State conflicts stop through native recovery; do not auto-resolve concurrent entity edits.

### Where it touches and stop numbers

Counts below were read on this turn. `after` is an estimate, not implemented output. C = COORD product base `c9c5752fda853737d4a937ad7f59564c5651ca53`; S = installed Spacedock source 0.27.2, whose merge classifier matches the dispatch's pinned upstream main. Upstream counts must be remeasured against the real delivery base before its owner builds.

| File / owner | Lines now | Estimated after | Journey seam |
| --- | ---: | ---: | --- |
| Pilot state `capture-case.py` (new) | 0, absent | 90–120 | selection claim and exact per-case process capture |
| Pilot state `verify-run.py` (new) | 0, absent | 70–100 | independently validate hashes, before/after/control and usage completeness |
| Pilot state `run/selection.json`, `run/usage.json`, `run/review.md` (new, three files) | 0 each, absent | 25 / 60 / 25 | retained one-run inputs, accounting and review |
| S `internal/status/merge.go` (existing defect owner) | 1049 | 1080–1110 | explicit accepted knowledge branch and checked authority |
| S `internal/status/merge_guard_test.go` (existing defect owner) | 1161 | 1250–1300 | native success/refusal/recovery fixtures |
| S `mods/pr-merge.md` (existing defect owner) | 163 | 175–190 | native route contract after executable support |
| C `docs/dev/_mods/pr-merge.md` (consumer follow-up in existing owner) | 520 | 515–535 | replace invalid reason instructions with supported route |
| C `kc-dev-flow/scripts/poc-close-guard.py` (reuse unchanged) | 366 | 366 | original pending/final measurement check |
| S `internal/status/format.go` (reuse unchanged) | 538 | 538 | preserve genuine local-merge semantics |

The two task-local helpers are justified only if plain subprocess capture plus independent readback needs retained logic; implementation must remove either if existing command composition passes all falsifiers without it. They are not a plugin-wide API. Raw `.stdout`, `.stderr` and per-case metadata are evidence, not policy/source counts; expected five case executions (before, after, control, fresh after, fresh control), three files each, at most 10 MiB total. Larger/truncated output stops before declaring completeness; do not silently trim. The selected product repair's exact files cannot truthfully be named before selection; stop for Captain review of that concrete diff, limited to two product files and 150 added+deleted lines.

Pilot preparation stops above 2 executable helper files or 220 added+deleted executable lines; total planned authored manifest/review/helper files above 5 or 350 added+deleted lines stops. Measure against the state commit that admitted this shape; later run artifacts are reported separately (15 case artifacts, 10 MiB). Upstream dependency stops above 3 implementation/doc files or 250 added+deleted lines, or any additional approval schema/runtime consumer; measure `git diff --numstat <upstream delivery base>` and count additions plus deletions, not net growth. The local mod follow-up is a separate existing-owner commit: 1 file, 40 added+deleted lines. Do not hide any of those limits by slicing a rewritten file or excluding tests. Crossing requires reduce/reshape/promote before more implementation.

### Acceptance falsifiers and execution budget

| Acceptance | Designed falsifier / required readback | Current acceptance |
| --- | --- | --- |
| AC-1 | Feed the same native source twice including edited text; second invocation must produce no new claim/agent. Kill after claim and confirm no automatic launch. PR feedback outranks eligible issue input. | pending |
| AC-2 | Exact frozen case must fail before, pass after; defective producer control must fail. Delete/tamper a raw stream or change candidate hash: verifier must refuse. Exported hashes must match actual raw files. | pending |
| AC-3 | Duplicate final cumulative event and a cached/reasoning subset must not raise totals; remove one actor/field and total becomes unknown. Compare quality and same measurement boundaries before making efficiency claims. | pending |
| AC-4 | A fresh exact-candidate reviewer must reject known failing control; mutate candidate after review and readiness must be invalidated. External publication remains separate. | pending |
| AC-5 | Current native probe proves blocked/pending without mutation. Future positive route must consume/archive honestly, refusal controls remain red, cleanup numeric and final close passes. | observed refusal; positive pending |

Proposed later budget, not launch approval: local-only first, one eligible case, one implementer and one fresh reviewer, no cloud launch, 20 implementer active minutes + 10 reviewer + 10 coordinator/closeout (40 actor-minutes maximum); each local capture command 60 seconds, 5 case executions, one correction/re-review within the same caps, zero automatic retries. If model calls are selected, launch configuration must name exact installed model/provider, account and cancellable runtime before review. Proposed aggregate ceiling is 1,000,000 input tokens including cache and 30,000 output including reasoning; check all-actor counters before each new turn. These are dispatch stop ceilings, not a verified hard provider spend cap; in-flight usage can overshoot, so no dollar cap is claimed. If a hard money cap is required or counters cannot bound continuation, stop and revise the budget. Existing source usage is partial; cloud 3/3 is owner-reported, not independent raw evidence, and is not a comparative baseline.

### Triggered shape receipts

```yaml
reverse_recovery:
  trigger: proposed manual evidence/duplicate-handling capability
  boundary: COORD kc-dev-flow scripts and skills, exact original task evidence, installed native merge consumer
  layers:
    - surface: exact contract loading
      location: kc-dev-flow/scripts/profile-contract-loader.py
      completeness: WORKING
      need: REQUIRED
      evidence: installed pinned ideation/1 invocation succeeded
      disproof_hook: change the pinned contract bytes and require refusal
    - surface: raw capture and dedup orchestration
      location: task-local capture-case.py proposed; existing subprocess and Git reused
      completeness: MISSING
      need: REQUIRED
      evidence: filename enumeration plus manual/dedup/stdout/usage content search of kc-dev-flow scripts and skills found no integrated runner; external/manual implementations outside this bounded search remain unknown
      disproof_hook: demonstrate an existing same-source second invocation producing no duplicate work and independently readable per-case streams
    - surface: knowledge terminal consumer
      location: installed internal/status/merge.go
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: synthetic accepted knowledge passed verdict remains blocked with unchanged pending state
      disproof_hook: run native-probe.py against a corrected upstream binary
  decision: use existing tools; recover native closure via existing defect owner
project_context:
  impact: none
  authority: root PRODUCT.md, ARCHITECTURE.md, CLAUDE.md
  claim_locator: PRODUCT.md kc-dev-flow entry; ARCHITECTURE.md KC Dev Flow profile and PR delivery sections
  surface: repository-owned runtime and profile-native delivery
  stale_claim: none
  approved_change: none
  landed_change: none
  planned_check: fresh validation confirms task-local helpers add no platform, scheduler or provider authority and native knowledge route preserves optional PR delivery
  validation_evidence: pending
```

No journey_slices receipt: the upstream closure repair already has an independent owner, so it is a dependency, not a second Pilot slice. No new retained document is proposed; existing mod contract repair applies present-tense/checkable-claim rules only after runtime support. No automatic project-context rewrite. Optional improvement-harvest reference was mentioned by architecture but no matching file was found in the scoped kc-dev-flow file inventory; this is not authority to recreate it.

### Exact Captain decision

Recommend admitting the upstream native knowledge-delivery scope delta under existing `knowledge-output-cannot-terminalize`, with the explicit bound-approval route and limits above. This is one authority decision because the Pilot cannot satisfy AC-5 without that dependency. It does not approve cloud/model launch, external posting, merge, or product commits; exact upstream files/diff and live execution configuration remain reviewable next boundaries. Preserve the original pending approval until an honest compatible consumer exists.

## Stage Report: ideation

1. DONE: Determine the legitimate knowledge-only terminalization dependency from live upstream evidence and a bounded local falsifier; preserve existing approval.
   AC-5: dispatch-pinned upstream check plus `shape-evidence/native-probe.py` / `native-probe.json` prove blocked accepted knowledge; rejected syntax succeeds only by changing meaning. Positive path DESIGNED, original approval untouched.
2. DONE: Shape one manual improvement journey with raw case evidence, per-actor usage, duplicate handling and independent same-case/negative-control verification.
   AC-1, AC-2, AC-3, AC-4: journey steps 2–7 and acceptance table bind each consumer, artifact, failure and recovery path; implementation acceptance remains pending.
3. DONE: Provide the smallest file-level implementation plan, limits, execution budget and exact Captain decision needed; cite AC-1 through AC-5 without claiming designed behavior already passes.
   File counts, delivery bases, diff stop numbers, bounded local-only execution proposal and upstream scope delta above; no launch/product mutation performed.
4. SKIPPED: Implement the selected repair, run live replay, publish review, or terminalize either real task.
   Shape-only authorization; AC-1–AC-4 positive execution and AC-5 legitimate closure/cleanup/final-check are not yet accepted.

### Summary

Completed the bounded Pilot shape and retained a runnable native refusal probe with raw results. The recommended route reuses local tools and existing state ownership; upstream knowledge-delivery authority is the blocking dependency, and the next decision is its explicit scope delta. No positive implementation, independent cloud result, complete cost comparison, or terminal completion is claimed.
