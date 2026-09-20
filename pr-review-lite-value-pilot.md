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

#### Captain external timing delegation and FO stop disposition — 2026-09-20

The Captain answered `交由助理計時並封存` to the explicit proposal that FO observe start/end outside the review agents, confirm complete output, and retain the evidence, including preparation and delivery time. This replaces Kent as the external timing/custody operator for a future authorized comparison; it supplies no timestamps for either stopped attempt and does not authorize a third attempt. Calibration case 1 explanation is acknowledged; do not invent the remaining human-checked calibration record.

FO checked the cycle 3 report against its three dispatched signals: 2 done, 0 skipped, 1 failed. The invocation/registration repair was exercised, but no complete legacy admission or final cost exists. Review arms, calibration and judge remain not run. The denied `rtk ls` had a permitted Glob alternative; the unexpected host marketplace refresh is the principal operational stop. Preserve the report's distinction between attempted local pull/clone, unknown marketplace before-state and no evidenced remote write. Current stopped experiment remains implementation, with no validation or third model launch.

A bounded FO read of primary vendor documentation found an existing candidate control, not a demonstrated repair: [environment variables](https://code.claude.com/docs/en/env-vars) describes `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` for suppressing nonessential traffic/background plugin commands, with official-marketplace auto-install controlled separately by `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL`. [Plugin discovery](https://code.claude.com/docs/en/discover-plugins) states that the nonessential-traffic flag also skips refresh before a named marketplace install, which can occur despite `DISABLE_AUTOUPDATER`. The proposed next invocation would retain `DISABLE_AUTOUPDATER=1`, explicitly clear inherited `FORCE_AUTOUPDATE_PLUGINS`, and apply both disable flags per process, without global configuration changes. This is a proposal only: the exact observed refresh branch and runtime preservation are not yet proven under those settings.

The broad traffic flag also disables feature-flag fetching, including AGENTS.md auto-loading, so a future correction must preserve the frozen instruction/tool surface in both arms and separate CLI children. The immutable target tree contains CLAUDE.md instruction files and no tracked AGENTS.md files, verified by a complete tree-name scan; that does not rule out ancestor or machine instructions. No Claude/model process, setting edit, cache repair or extra experiment was performed for this documentation check. The existing failure/unknown-cost evidence stands.

#### Captain Cloud retry and execution handoff — 2026-09-20

The Captain explicitly authorized another retry with a required host change: `授權重跑，但我要你跑在 conductor cloud 上做隔離，也方便我稍後如果闔上 macbook 螢幕時你不會被暫停`. Create one isolated Conductor Cloud workspace and move the active FO/operator and execution there, so subsequent orchestration does not depend on the Mac. The prior local attempts stay stopped. This grants one new Cloud attempt under the same four cost-stop allocations and stop-on-failure rule, not unlimited retries, product changes, posting or delivery. Prior unknown costs and Cloud/orchestration costs remain separately attributable or unknown.

Cloud Linux paths and executable hashes necessarily replace the Mac-specific host pins. Preregister a common Cloud runtime/tool baseline for both arms before the new admission; preserve the PR, control/treatment source revisions, exact experiment model and effort, output-quality criteria, complete elapsed-time boundary and separate-cost accounting. User-authorized Cloud provisioning and per-process startup corrections may use existing supported facilities; do not build a new platform or silently relax missing evidence. Assistant-owned external timing/custody already has explicit authorization. The Cloud FO must keep operating without local callbacks, persist status and evidence in the Cloud workspace and sync task-only state. Do not copy local credentials, settings, Keychain data or raw private failed transcripts to Cloud.

The local FO prepares a self-contained handoff containing task/state locations, source pins, current approvals/stops and the needed non-secret skill/toolkit bytes. After Cloud ownership is acknowledged, local task-state writes stop. A Cloud acknowledgement must prove remote Linux execution with CONDUCTOR_IS_LOCAL=0; workspace creation alone is not experiment execution or a guarantee against Cloud service suspension. The original acceptance/quality requirements and human calibration evidence boundary remain visible.

#### Cloud ownership registration — 2026-09-20

Kent's local FO acknowledged the observed Linux / `CONDUCTOR_IS_LOCAL=0`
readback in message `0026379b-0cf9-4653-bcb9-e97cfc520002` and stopped all
local task-state writes. Cloud workspace
`4815161d-63b0-44dc-b08d-8f5f43a3caee`, session
`d0e0b07a-6089-46aa-b035-61e910797310`, is the sole owner of the next
task-state, dispatch and evidence actions. Operator link:
`conductor://workspace?id=4815161d-63b0-44dc-b08d-8f5f43a3caee&session=d0e0b07a-6089-46aa-b035-61e910797310`.

The historical predecessor worktree was
`/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v2/.worktrees/spacedock-ensign-pr-review-lite-value-pilot`.
It is not accessed from Cloud. Its workflow-relative registration
`.worktrees/spacedock-ensign-pr-review-lite-value-pilot` maps through the normal
Spacedock stamped implementation dispatch to the isolated Cloud root
`/home/vercel-sandbox/kc-claude-plugins/.worktrees/spacedock-ensign-pr-review-lite-value-pilot`.
The Cloud launch checkout is `/home/vercel-sandbox/kc-claude-plugins` on
`conductor/pr-review-lite-cloud` at control commit
`6bf62d1d7d3c343a97c973a7abd7424d03676437`; that ambient branch is not renamed.
The separate state checkout is `docs/dev2/.spacedock-state` on
`spacedock-state/dev2`.

No local experiment process was running at transfer. The two prior Mac STOP
records, hashes and unknown costs remain separate and are not pooled with this
one authorized Cloud attempt. Cloud/orchestration/service cost is separate from
the four reported-cost stopping envelopes; the nominal USD 19.8448 is neither a
Cloud-fee cap nor an invoice guarantee. This ownership acknowledgement adds no
model run, product edit, delivery or retry authority. Human confirmation of the
complete three-case calibration key remains pending in this Cloud session; setup
and the one admission may proceed independently, but judge calibration may not.

#### Cloud pre-model boundary — 2026-09-20

The private Cloud registration at
`.context/pr-review-lite-value-pilot/runs/dev434-cloud1/registration/registration.md`
is complete before any experiment model launch; SHA-256
`44291112f8d48c92c8c6d46c59a68fc62645e88fc7d0966401b8497424726c07`.
It records exact Linux runtime/tool versions, normal Cloud OAuth auth with failed
bare-auth eligibility, pinned control/treatment/toolkit and target identities,
stable toolkit hash parity, ancestor instruction inventory, per-process traffic
controls, envelope separation, and the no-local-callback boundary.

Non-model checks passed: live PR base/head/title/body/files match the frozen
sample; patch hash remains
`1a88db01f8bc155c6434b37c626e949824953d7fa9b52828d7cd6db32cd5a914`;
both allowed `node --check` commands pass; the pure unmodified candidate planner
returns Lite/bugfix/four false modes on identical metadata; treatment totals
remain 18 files / 5,884 total changed lines / 1,903 focused lines against the
original denominator; source checkouts are clean; Cloud timeout and empty-stdin
smokes pass. A failed shared-clone setup exposed missing promisor blobs and was
preserved unused; the independent remote target clone is complete and clean.

Spacedock's stamped implementation dispatch created and registered the isolated
Cloud worktree at the recorded relative path, branch
`spacedock-ensign/pr-review-lite-value-pilot`, HEAD
`6bf62d1d7d3c343a97c973a7abd7424d03676437`. The sole implementation ensign is
`/root/spacedock_ensign_pr_review_lite_value_pilot_implementation`; no extra helper
was spawned. The admission launch file is syntax-checked, single-claim, prompt-file
fed, externally bounded, process-group isolated, and has preopened raw streams;
its hash is `fdf607a07bbdf6efd037ec0b7350b00e2525e6853412850ef23a52cdf389a57f`.
Experiment model launches at this boundary remain zero. The one authorized Cloud
admission may now start; arms and judge retain their independent prerequisites.

#### Cloud admission result — 2026-09-20

The single authorized Cloud admission completed successfully; see
[checkpoint](pr-review-lite-value-pilot/admission-cloud1-checkpoint/README.md) and
[sanitized summary](pr-review-lite-value-pilot/admission-cloud1-checkpoint/summary.json).
The final host receipt reports `claude-opus-5`, success, one result,
USD 0.46017775000000005 estimated/list-basis cost, 16 input / 31,223 cache-write /
169,858 cache-read / 7,201 output tokens, and no permission denials. Process elapsed
was 80.384955883 seconds; this is admission setup evidence, not an arm timing sample
or an invoice guarantee.

Actual legacy triage returned Lite / bugfix with `full_pass`, `probe_required`,
`cross_model` and `noise_filter` all false. It matches the unmodified candidate
planner on identical frozen PR metadata. Effective startup reported only the
pinned control plugin 1.12.0, Opus 5, Read/Grep/Glob/Bash, zero MCP servers, and
`dontAsk`; debug evidence reports zero active hooks, no declared marketplace,
plugin auto-update skipped and no marketplace pull/clone. No fallback, Agent,
write, web/MCP call, permission denial or tracked mutation was observed. Raw stream,
stderr, debug, argv source, prompt and process readback remain private with hashes.

Admission therefore permits the retained next step, control first, without forcing
a mode or reusing its analysis inside either arm. Its USD 4.50102225 unspent
threshold is non-transferable. Control has not started; calibration-key confirmation
is still pending and blocks only judge calibration, not the two arms.

#### Cloud control result — 2026-09-20

The retained first arm completed successfully; see
[checkpoint](pr-review-lite-value-pilot/control-cloud1-checkpoint/README.md) and
[sanitized summary](pr-review-lite-value-pilot/control-cloud1-checkpoint/summary.json).
External elapsed from before checkout/acquisition through FO observation of the
complete review, normal confirmation request and literal `END REVIEW` was
409.872228384 seconds. The one inclusive native-tree final receipt reports
USD 4.599209500000001 list-basis host cost, below its USD 4.9612 stop, with Opus 5
only. Unspent threshold is non-transferable.

The arm reacquired the frozen target/metadata, exported the control plugin and
toolkit inside the timed interval, used the registered common runtime and flags,
and produced a full legacy review with four declared review workers, eight proposed
inline comments, five advisory items, limitations and a non-posting confirmation
menu. Both permitted syntax checks passed. No dependency install, build, full test,
browser, posting, source edit, fallback, marketplace refresh, MCP/web use or tracked
mutation occurred. One Grep used a malformed path outside the target and was denied;
the same evidence was obtained through allowed in-target reads, so this was retained
as a non-required denial rather than concealed or repaired by operator intervention.
The complete output remains unedited and is not supplied to treatment.

Control is valid for the registered comparison. Treatment has not started. The
next arm must independently reacquire all material and use the CLI-backed candidate
route; it may not consume control findings, timing or cost. Human confirmation of
the three-case calibration key remains pending and still blocks judge calibration.

#### Captain model-free remediation-proposal continuation — 2026-09-21

After asking for progress, the Captain explicitly replied `繼續` to the proposed
next step: produce a concrete correction plan for the stopped treatment
subprocess-isolation and evidence gaps. Cloud workspace
`4815161d-63b0-44dc-b08d-8f5f43a3caee`, session
`d0e0b07a-6089-46aa-b035-61e910797310`, retains sole task-state ownership; this
follow-up must not depend on the local Mac.

This continuation authorizes one same-stage implementation ensign to produce an
English, reviewable correction proposal and sanitized evidence from bounded
model-free checks. It may inspect pinned source, use existing fixtures/stubs, and
run one-off private probes that never invoke Claude or another provider. It must
separate missing/unknown evidence from demonstrated unsafe behavior, identify the
smallest integrated source seam and material alternatives, preserve secret-safe
child-process custody, define fail-capable implementation/validation checks and
stop conditions, and assess the proposed change against the original
`3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8` denominator and unchanged 20-file /
6,600-total-line / 1,903-focused-line caps. With zero focused-line headroom, it
must demonstrate a credible within-cap simplification or surface the exact
Captain cap/scope decision; it may not reset the denominator or silently add a
wrapper.

No experiment/provider model call, new whole-attempt spend, product/source edit,
product commit or push, PR, posting, merge, default change, calibration or judge
is authorized. The stopped Cloud attempt, valid standalone admission/control
evidence, incomplete treatment and unknown treatment cost remain unchanged. The
all-three calibration answer key is still unrecorded but does not block this
model-free analysis. Any future comparison requires a separately approved,
immutable next candidate and explicit preregistration; reuse of the old control
for scoring is not assumed. FO may commit and push only task-specific state after
the ensign report is verified.

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


## Stage Report: implementation (cycle 3)

- DONE: Register one newly authorized attempt before any model call, preserving the failed first run and its unknown cost; demonstrate the corrected non-model invocation cannot inherit input or escape its timeout.
  [Replacement checkpoint](pr-review-lite-value-pilot/admission-retry1-checkpoint/README.md): approval registered before launch; literal-argument/empty-stdin and TERM-ignoring timeout probes passed; subcommand-first auth exited 0 with DEVNULL and durable outputs; all first-attempt hashes remain unchanged.
- FAILED: Execute at most one frozen legacy admission call with the approved model, effective configuration, durable raw outputs, explicit timeout and USD 4.9612 cost-stop setting; compare actual six modes with the candidate planner and retain any failure without retry.
  One call launched with exact startup model/tools/control-plugin and 1,200-second external watchdog; stopped at 27.04 seconds after a denied directory-listing command and unexpected CLI marketplace refresh. No legacy modes/final receipt; candidate modes match the frozen expectation but cannot establish agreement.
- DONE: Commit a sanitized task checkpoint with attributable effects, usage and unknowns; stop before review arms, calibration or judge for FO routing, without product changes or stage advancement.
  [Summary](pr-review-lite-value-pilot/admission-retry1-checkpoint/summary.json) binds raw argv, prompts, outputs, debug and transcript hashes; four unique main messages show partial 8 input / 25,752 cache-write / 52,551 cache-read / 2,196 output tokens. Final/current/previous/cumulative dollars remain unknown; no further model step occurred.
- DONE: Bound stop effects and source preservation.
  SIGTERM yielded wrapper exit -15 and absent process group; 74 control files match pinned Git, product/target tracked status is clean, runtime and old-run hashes match. Denied `rtk ls` had an allowed Glob alternative; CLI pull/clone refresh was outside model tools, with successful mutation unproven and marketplace before-state absent.
- SKIPPED: Review arms, calibration, judge, configuration/product repair, additional attempt, validation, PR and gate transition.
  These are outside this dispatch or prohibited after STOP; no human calibration or external stopwatch evidence was inferred. No nested worker was spawned.

### Summary

The corrected non-model invocation and pre-launch deadline were exercised, and exactly one registered admission ran; this replacement still stopped without a usable eligibility result or final cost receipt. The frozen CLI configuration did not prevent an unexpected background marketplace refresh, so operability remains unproven; product behavior and quality were not tested, and no configuration repair or further attempt is authorized. This is a committed implementation checkpoint for FO routing, not completed implementation, validation PASS or a new gate.


#### Cloud treatment STOP and attempt termination — 2026-09-20

The one authorized Cloud attempt is stopped. Its treatment interval began at
`2026-09-20T03:21:23.287772779Z`; the outer `claude-opus-5` process initialized
with the pinned treatment plugin and began reading frozen inputs. Before the
repository-owned adapter was invoked, the implementation ensign's read-only
preflight identified a mandatory Cloud custody gap in the unchanged adapter:
its separate child CLI calls do not retain durable child stderr, exact argv and
environment-key evidence, or a startup receipt proving effective empty
settings/hooks/plugins, and their argv omits the registered outer isolation
flags. Inherited traffic controls and `--tools ''` do not prove those missing
surfaces.

FO cancelled the treatment process group immediately after receiving that
finding. The launch ended by SIGTERM / exit 143; no adapter child, retry,
reviewer finalization, confirmation request or posting occurred. FO had launched
the outer process before the requested ensign preflight reply arrived. This
operator sequencing error consumed the treatment launch and is not repaired or
replayed. The interrupted outer call emitted no final result receipt, so its
cost is unknown rather than zero. Five unique outer messages expose incomplete
snapshots totaling 10 input / 74,175 cache-create / 217,768 cache-read / 17 output
tokens; these do not reconstruct a complete receipt or dollar amount. No adapter
capability child or provider envelope exists.

[Treatment STOP checkpoint](pr-review-lite-value-pilot/treatment-cloud1-stop/README.md)
binds the private raw stream/debug hashes and exact not-run work. Admission and
control remain standalone evidence, but treatment is incomplete, so no blind
quality adjudication, time/cost scoring, saving claim, promotion proposal or
validation PASS is possible. Calibration and judge were not run. State remains
implementation; no product, PR, review, merge, release, default or stage change
was made. This Cloud attempt has no authority for adapter repair, another arm or
model launch, calibration, judge, or delivery.
