---
title: Prove a useful Lite PR review journey before wider evaluation
status: implementation
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree: .worktrees/spacedock-ensign-pr-review-lite-value-pilot
pr:
gates:
    version: 1
    records:
        - id: gate:pr-review-lite-value-pilot:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:pr-review-lite-value-pilot-backlog-1
              briefing:
                id: briefing:pr-review-lite-value-pilot:backlog:attempt-1:revision-1
                digest: sha256:7a7170e5e7d1cf19d17b37cd1f3dd76590f6a84f5050c4838a386eccdc7f6d57
                room-ref: ./pr-review-lite-value-pilot/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:pr-review-lite-value-pilot:backlog:1
                briefing: briefing:pr-review-lite-value-pilot:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-20T01:13:25.639334Z"
                decision: approve
                reason: 'Captain replied 可以 to the presented dev2 Pilot successor direction on 2026-09-20: preserve old records, prove one complete development-sample journey before wider evaluation, retain quality and 33.3% thresholds; authorize task recording and ideation only, stop at design review.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:pr-review-lite-value-pilot:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:pr-review-lite-value-pilot-ideation-1
              briefing:
                id: briefing:pr-review-lite-value-pilot:ideation:attempt-1:revision-1
                digest: sha256:856daeeb6ce8f637986edc32cf3b30c1c0b84b457ea9e909da0b1610c06af757
                room-ref: ./pr-review-lite-value-pilot/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:pr-review-lite-value-pilot:ideation:1
                briefing: briefing:pr-review-lite-value-pilot:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-20T01:30:03.785094Z"
                decision: approve
                reason: 'Captain replied ok on 2026-09-20 to design Briefing 856daeeb: approve implementation limited to model-free comparison preparation, fixing the PR, revisions, model/tools and cost observation. No product changes or experimental spend; return a concrete launch package for separate authorization.'
              application:
                target-stage: implementation
                state: consumed
started: 2026-09-20T01:13:40Z
---

Resume the approved kc-pr-flow improvement under dev2 by first establishing whether one complete Lite review journey preserves useful review quality while reducing end-to-end time and cost. This is a successor product task, not a workflow-refit task, a fifth layer of the old PR stack, or a declaration that the previous validation passed.

## Captain authority and FO alignment

The Captain requested migration from the old dev flow to dev2. After reviewing the concrete successor plan, the Captain answered `可以` on 2026-09-20, approving: preserve the old records; retain Pilot; prove one complete development-sample journey before wider evaluation; and retain the existing five-pair quality and 33.3% time thresholds. The present authorization covers recording this task and dispatching ideation only, ending at design review. It does not authorize product implementation or model-based review experiments.

## FO alignment

Needed: yes. The old records conflate the retired automated measurement path with the later supervised comparison, and already-built protocol machinery must not predetermine further investment.

Result: Captain approved on 2026-09-20: first compare the current default review and the candidate Lite route on one separate development PR; measure the complete user journey and preserve required review questions; simplify or stop if preparation, dispatch, and synthesis overhead consumes the saving. Only afterward freeze a separate five-pair blind evaluation. The next stage must turn this direction into a concrete PRFAQ, Mermaid flow, falsifiable evidence plan and spend proposal; it must not run the experiments.

## Scope and stop condition

- Code root: `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v2`; workflow: this checkout's `docs/dev2`. Use this explicit workflow directory on every SD operation.
- Current integration baseline: `6bf62d1d7d3c343a97c973a7abd7424d03676437` (origin/main observed 2026-09-20).
- Preserve Pilot scope: a default-off, attended Lite path for bounded real PR review. No executable expansion; other profiles and Custom UI remain outside this slice.
- Current round: ideation only. Author a minimal development comparison and later held-out acceptance plan. Reuse existing instruments and product seams, and explicitly distinguish measurement, implementation, review quality, and delivery proof.
- One assigned ideation worker; no nested agents or experiment/model/cloud runs. Read-only source/provider/ledger inspection is allowed. A cost estimate must cite actual existing usage if available; otherwise mark it unknown and identify the prerequisite. Historical experiment budgets do not transfer.
- Stop at the design gate. Product changes, paid/model comparisons, corpus admission calls, default enablement, PR creation, push of product branches, merge, release and formal learning require their applicable later authorization. Task-state/report commits and sync are part of this approved workflow recording; no product commit is authorized.
- Do not change the old task, pins, branches, reports or PRs; do not move or close them. This task owns only successor direction and future approved work. No old validation verdict is imported.
- Preserve the existing branch's cumulative limits (20 changed files, 6,600 total changed lines, 1,903 focused changed lines from `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`) as historical candidate constraints. Assess the current candidate against them before any continuation; do not quietly reset the denominator when moving to current main. Any replacement baseline or scope/budget revision is a Captain decision at design review.

## Source evidence and supersession

- Old task: `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/docs/dev/.spacedock-state/profiled-pr-review-capability-protocol/index.md`, held in validation. Read historical reports with their exact dates/revisions; they do not reflect all later candidate changes.
- Candidate worktree (read-only): `/Users/kent/conductor/workspaces/kc-claude-plugins/kc-pr-review-capability-pilot`; branch `feature/kc-pr-review-capability-protocol-pilot`; local and remote head observed `0d2e3164ccd2d60006688c5443717b818825a305` on 2026-09-20, clean; no PR found.
- Accepted candidate design: `docs/superpowers/specs/2026-09-05-kc-pr-review-capability-protocol-v1.md` at that candidate revision. September 7-9 authority entries supersede the earlier automated-runner prerequisite. `b7a21def78c63cacef07f76b7d11ced574de0dea` withdrew the new automatic Pilot runner/comparator. Its integrity defect remains historical and unresolved, but repairing that withdrawn path is not a prerequisite for supervised timing. Do not reintroduce that work.
- Native file handoff, result decoding, failure diagnostics and test-observation evidence repair have local fixture evidence. They do not prove live native completion, cancellation, cost, review quality or speed. The candidate corpus file contains comments only; no frozen real five-pair corpus is present.
- Prior default-off acceleration stack: iamcxa/kc-claude-plugins PRs #352, #353, #354 and #355. All observed open Draft with green checks; reference material only, not the control arm or a dependency chain for this task. Do not modify/merge/close them.
- Older measurement evidence: `/Users/kent/conductor/workspaces/kc-claude-plugins/kc-pr-review-speed/.context/accepted-kc-pr-review-slimming-plan.md`. Its exploratory latency and quality misses are bounded historical evidence; the later Lite experiment has a different control/population and cannot pool those timings.

## Acceptance criteria

**AC-1**: The current design identifies one intended user, one complete attended Lite review journey, the smallest useful scope, all authority owners and explicit stop/rollback paths, without equating existing implementation with value.
Verified by: A readable PRFAQ and rendered Mermaid with matching actors, branches, confirmation boundary and stops, cross-checked against current candidate/integration seams during ideation. Future runtime behavior remains unverified.

**AC-2**: The development comparison can falsify both end-to-end completion and the claimed saving mechanism, with quality considered before speed.
Verified by: A preregisterable one-development-PR plan with exact control/treatment revision policy, equivalent inputs/model/tools, externally observed start/end, all preparation/tests/retries/dispatch/synthesis charged, complete outputs and failures retained, quality questions and time/tokens/cost recorded, and a concrete simplify/stop decision rule. During ideation, verify instrument availability by read-only evidence; execute no review experiment.

**AC-3**: The implementation/adoption decision is proportional and evidence-bound.
Verified by: A keep/change/defer mapping for existing Lite seams, a current candidate size/count audit with the original denominator, a bounded candidate-to-current-main compatibility assessment, and an explicit proposal for any changed scope/limit. No source mutation or broad infrastructure rebuild during ideation.

**AC-4**: Later promotion preserves the accepted quality and time gates and cannot be claimed from the development sample.
Verified by: A separate frozen-corpus plan for five effective ordinary Lite PR pairs plus one predesignated backup, blinded quality adjudication before timing disclosure, no accepted Critical/High control miss, no extra aggregate false positives, complete required coverage, `1 - median(treatment) / median(control) >= 0.333`, and at least three of five pairs individually reaching 0.333. Failure/incomplete samples stay visible. This gate is planned, not executed or passed in ideation.

**AC-5**: Spend, delivery and learning claims retain their own evidence boundaries.
Verified by: A budget proposal derived from existing usage or explicitly unknown with its missing input; no new experimental calls before approval; the later exact candidate requires independent validation and explicit product delivery authority. Formal dev2 learning follows verified task closure and original PR merge, not this direction review.

## Current authorization

Record the admitted seed, bind and record the Captain's already-given initial approval, and dispatch ideation through the dev2 workflow. Return a concrete design gate; do not advance to implementation automatically.


## Ideation design

[PRFAQ and comparison plan](pr-review-lite-value-pilot/design.md), [rendered journey](pr-review-lite-value-pilot/journey.png), [Mermaid source](pr-review-lite-value-pilot/journey.mmd), and [sanitized source/count/usage audit](pr-review-lite-value-pilot/source-audit.json).

## Stage Report: ideation

- DONE: Reconcile current candidate and historical approvals into a minimal Pilot PRFAQ with a rendered, semantically checked Mermaid flow and a keep/change/defer mapping.
  Design FAQ, current-evidence reconciliation, flow and mapping preserve the supervised path; installed Mermaid CLI rendered the image, which was inspected and corrected for both-arm sequencing and admission-stop wording.
- DONE: Produce a falsifiable one-development-PR comparison and separate five-pair blind acceptance plan, with existing instrument evidence, a concrete budget proposal or exact missing cost input, and no experiment execution.
  Design specifies exact version policy, full externally observed time, quality-first scoring, failure retention and simplification rule; proposed development-only USD 19.8448 includes admission, both arms and judge work, with actual native spend enforcement still unverified.
- DONE: Audit candidate limits and current-main compatibility without mutating product, then write and commit the ideation Stage Report and design in the task state, naming unresolved Captain decisions and stopping at design review.
  Source audit pins candidate 0d2e3164 and main 6bf62d1d; 18 files / 5,884 total / 1,903 focused fit original limits; only ARCHITECTURE.md overlaps main changes, at separate inspected hunks. Task-scoped state commit contains this report; no product or gate mutation.
- DONE: AC-1 — intended user, attended journey, minimal scope, owners and stop/rollback paths.
  Design FAQ plus rendered flow were cross-checked against candidate skill, worker and adapter seams; visual semantic check passed, future live execution remains unverified.
- DONE: AC-2 — falsifiable development completion and saving mechanism.
  One-PR plan names unchanged control triage, both opt-in flags, exact versions, external endpoints, all overhead, calibrated quality and failure rules; native lane timing and cost must come from actual host observations, not null sidecar fields.
- DONE: AC-3 — proportional implementation/adoption decision.
  Keep/change/defer table and read-only original-denominator count audit recommend reuse before product changes; focused headroom is zero and static compatibility is not tested integration.
- DONE: AC-4 — separate held-out five-pair acceptance without denominator drift.
  Exactly five effective slots plus one unavailable-to-both-only backup, no accepted Critical/High control misses, no extra aggregate false positives, complete coverage, aggregate 0.333 and three-of-five individual 0.333 retained; corpus has zero rows, evaluation not run.
- DONE: AC-5 — separate spend, delivery and learning evidence.
  Six existing numeric ledger entries support only the USD 4.9612 historical planning ceiling; design does not authorize spend, product changes, independent paid review, five-pair runs, delivery or learning.

### Summary

The single recommendation is to approve this development-first design into an implementation stage restricted to model-free readiness preparation, reusing the current candidate and original limits. Product value, live host reliability, enforceable aggregate spend, independent validation and delivery remain unproven; the next dispatch may freeze execution inputs and document existing supervised budget controls, but separate explicit spend authority is required for a later development launch. This is completed ideation evidence only, with no model experiment, product edit, old-state change or gate advancement.


## Stage Report: implementation

- DONE: Freeze one concrete development PR and exact control/treatment, model/effort, host/tool, timeout, run-order and calibration inputs using read-only evidence; distinguish provisional sample selection from the later paid eligibility decision.
  [Readiness package](pr-review-lite-value-pilot/readiness/README.md): PR iamcxa/kc-claude-plugins#434, immutable source/patch, pinned plugin/runtime/toolkit, Opus 5/high, control-first order and synthetic calibration; legacy eligibility and human calibration checks remain pending.
- DONE: Verify existing host/operator timing, cancellation, aggregate parent/child usage and budget controls without model calls, then prepare a concrete launch package with attributable evidence, precise commands/prompt templates, cost proposal and any actual blocker.
  [Runbook](pr-review-lite-value-pilot/readiness/runbook.md) and [audit](pr-review-lite-value-pilot/readiness/evidence.json): documentation/source inspection plus local timeout smoke; native total-attempt deadline remains unproven, while the existing optional CLI backend contains 120-second communicate timeout/process-group cancellation.
- DONE: Commit the task-specific readiness artifact and implementation Stage Report, preserve product bytes and old records, and stop before every experimental/admission/judge call or stage transition for the Captain's separate spend decision.
  This path-scoped state commit contains this report and readiness companions only; owned product worktree remains clean at 6bf62d1d7d3c343a97c973a7abd7424d03676437; status remains implementation and no gate operation was performed.
- FAILED: Substantiate a strict USD 19.8448 aggregate maximum charge from inspected controls.
  Documented CLI budgets stop at reported spend; in-flight overshoot has no established upper bound. Separate CLI capability costs are not included in the outer native-tree receipt and must be reconciled once per attempt.
- DONE: Check the package without executing an experiment.
  [Checks](pr-review-lite-value-pilot/readiness/checks.json): exact target files pass Node syntax-only checks, six shell templates pass bash -n, retained JSON parses, and actual candidate plan() selects Lite; malformed syntax/schema or different planner modes would fail these bounded checks, which do not establish review quality or model reliability.
- SKIPPED: Product implementation, model/admission/judge calls, dependency installation, independent validation, PR creation, product push, merge, release and gate transition.
  These are outside this checkpoint's authorization; no nested worker, model prompt or target mutation was made. Calibration examples are frozen but not human-approved; paid control triage is not inferred.

### Summary

Prepared one reviewable development-only launch proposal using the existing optional CLI worker path, with four USD 4.9612 stopping thresholds (USD 19.8448 nominal total); proposed treatment allocation is USD 2.4806 outer plus USD 2.4806 across all capability attempts. Recommend one Captain decision accepting that backend-and-budget-stop proposal, including unbounded in-flight overshoot risk; if an absolute invoice ceiling remains required, hold rather than build a new enforcement system. The approved native design, original 20-file/6,600-line/1,903-focused-line limits, historical records and separate unfunded five-pair evaluation remain intact; this is readiness only, not completed product implementation or validation PASS.

### Feedback Cycles

#### FO readiness disposition — 2026-09-20

The three assigned readiness outputs are delivered; the checkpoint does not complete product implementation or satisfy the later live quality/time criteria. State remains implementation at the explicit Captain backend/spend decision. Do not dispatch validation or launch a model call from this report alone.

- **Needs decision — experiment method.** The approved attended native Lite comparison requires a total 120-second capability deadline. The source sets that requirement; the inspected native documentation did not establish enforcement, which is missing evidence rather than a demonstrated defect. The retained CLI adapter has a source-owned communicate timeout and process-group cleanup. Selecting it changes the treatment method and permits conclusions only about the CLI-backed route. FO recommends that small method revision for one development pair; no native-proof claim or new enforcement project follows.
- **Needs decision — budget interpretation, coupled to the selected method.** The proposed USD 19.8448 is the sum of budget-stop settings, not a substantiated maximum bill. Existing vendor documentation says stopping follows reaching reported spend; this review found no bound on in-flight overshoot. Separate CLI workers require their own receipts added once to the outer receipt. FO recommends presenting the exact one-pair, stop-threshold proposal for Captain acceptance, with failure ending the pair and no replacement/repair runs. No spending grant exists yet.
- **Retained limits.** Legacy admission, model availability, calibration, startup/configuration parity and live cancellation/usage remain unexecuted. Node syntax and deterministic plan output prove only those narrow checks. The .mjs sample's missing test-evidence signal is recorded and is not silently corrected or treated as rendered-UI proof. Original product and historical workflow bytes remain unchanged.

Before any accepted launch, carry the exact Captain method/spend decision into the task and run assignment, settle the recorded operational prerequisites, and preserve all raw failures. If the Captain requires a strict invoice maximum, hold with that specific unmet requirement. The FO has authorized neither product repair nor experiment execution in this disposition.

#### Captain backend and spend approval — 2026-09-20

The Captain replied `核准` to the presented one-development-pair proposal: use the existing CLI capability backend, PR iamcxa/kc-claude-plugins#434, and four USD 4.9612 reported-cost stopping thresholds (USD 19.8448 nominal total), with the explicitly stated inability to guarantee a zero-overshoot bill. This accepts that experiment-method and budget interpretation for this one attempt; it does not authorize a replacement candidate, repeated whole arm, repair/model retry beyond the retained bounded transient attempt, product edits, default enablement, posting, PR publication, merge, release or the later five-pair batch.

FO will first dispatch the retained implementation owner for the single admission call and its no-model setup/readbacks, then drive the remaining authorized comparison only while the frozen prerequisites hold. Human calibration-key confirmation is requested separately and remains pending until the actual Captain answer; approval of spend is not fabricated calibration evidence. Admission may run independently before that answer. Admission mismatch, invalidity, execution failure, budget stop or unavailable required evidence ends the pair; preserve raw evidence, actual known/unknown cost and not-run portions. No silent retry, fallback, target replacement, source repair or budget reset is authorized.

This is an implementation-stage experiment checkpoint under the approved Pilot, not a new workflow gate. The preparation report remains historical. Return all outcomes to FO; further stage advancement requires the actual comparison outcome and its proper review route.


#### Captain retry approval — 2026-09-20

The Captain explicitly replied `核准重跑` after the stopped preflight report and the proposed correction of the launch invocation. This authorizes one new attempt of the same development comparison with the existing PR, immutable revisions, model/effort, CLI treatment, cost-stop allocations and failure rules. Use a new private run directory and preserve the entire failed first attempt. Its unknown dollar cost remains unknown and is not erased by the new authorization or included as zero in any total. The new nominal USD 19.8448 settings are stopping thresholds, not a hard cumulative bill including the previous incident.

First correct the operator invocation: use proven subcommand grammar, explicit stdin isolation for non-model subprocesses, durable stdout/stderr capture and an external timeout before launch. Never allow an auth/help check to inherit the orchestration script or enter interactive mode. No product change, new enforcement platform, model fallback, replacement PR, further whole-attempt retry or product delivery is authorized.

Dispatch one implementation worker for registered no-model setup and at most one legacy admission call, then report to FO before the review arms or judge. The former implementation worker is absent from the live roster; the replacement owns the existing clean task worktree. The Captain's `ok` after the explanation acknowledges calibration case 1's meaning; it is not a fabricated approval of all three answers or externally observed arm timing. Those remaining prerequisites must be handled before dependent calls. State remains implementation.

## Stage Report: implementation (cycle 2)

- FAILED: Freeze and register the single approved CLI-backed development attempt, verify immutable input/runtime/plugin bindings and no-model launch prerequisites, then execute at most one existing legacy-control admission call within its USD 4.9612 budget-stop threshold.
  Exact source/runtime checks passed, but the intended auth-only preflight entered a model session before registration without a budget/deadline flag; stopped as operator execution error. Intended admission was not run.
- DONE: Preserve unedited stream, command, terminal, model/configuration and actual usage evidence; compare actual six-mode legacy admission with the frozen candidate planner and report proceed or stop without forcing Lite, repairing outputs, rerunning or changing target.
  [Checkpoint](pr-review-lite-value-pilot/admission-checkpoint/README.md) retains raw transcript/input privately, command and interruption evidence; original stdout/stderr and final cost are unavailable. Actual legacy modes are absent, so no eligibility comparison/pass is claimed and disposition is STOP.
- DONE: Write and commit a task-scoped checkpoint and report to FO with exact cost/unknowns and any pending human calibration/timing prerequisite; run no review arm or judge until FO resumes the same authorized attempt.
  [Sanitized summary and hashes](pr-review-lite-value-pilot/admission-checkpoint/summary.json): four unique observed main message IDs, 8 input / 17,490 cache-write / 36,809 cache-read / 3,047 output tokens; final dollars and additional Max billing unknown. Human calibration/timing remain unperformed; pair stopped.
- DONE: Bound unintended effects and terminate owned work.
  Effective snapshot shows Opus 5 and Bash/Glob/Grep/Read; three denied tools, two successful local Globs and one git rev-parse; no Agent/write/network tool observed. Product and target tracked trees clean, 74 plugin files unchanged, original launch PIDs/matching run CLIs absent.
- SKIPPED: Intended admission, control, treatment, calibration, judge, replay/replacement, product repair and stage/gate transition.
  Failure ends this pair; accidental preflight is not eligible comparison evidence. Direct auth subcommand, explicit DEVNULL and a pre-launch deadline are remediation guidance only, not a retry authorization.

### Summary

The bounded experiment segment failed before valid admission because our auth-check invocation entered a model path and inherited its enclosing Python script as user input. The process was stopped and the pair remains stopped; raw transcript plus observed partial usage are retained, while missing final cost and lost stdout/stderr remain unknown/unavailable. This is operator execution failure, not candidate behavior or Lite quality; status stays implementation and no further model step, product change or validation was performed.
