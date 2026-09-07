# Profiled PR review capability protocol V1

- **Date:** 2026-09-05
- **Product:** `kc-pr-flow`
- **Design revision accepted:** 2026-09-07, Captain chat `確認`, following the complete revised flow plan.
- **Measurement revision accepted:** 2026-09-07, Captain chat `那就這樣繼續`, following the start-message to completed-review-message definition.
- **Pilot automation withdrawal accepted:** 2026-09-07, Captain chat `同意`, approving the presented replacement scope without increasing limits.
- **Required-field consolidation accepted:** 2026-09-07, Captain chat `批准`, approving the bounded code-and-test optimization after the local development trial.
- **Goal and reviewer integration accepted:** 2026-09-07, Captain chat `確認`, approving the presented eleven-file local integration and no-model verification scope.
- **Reviewer coverage seam repair accepted:** 2026-09-07, Captain chat `確認`, approving the two-file runtime implementation/test extension after the reproduced incomplete-confirmation failure.
- **Local submission packaging accepted:** 2026-09-07, Captain chat `可以`, approving two local commits: the prior automation withdrawal with required-field consolidation, followed by goal/reviewer integration with its runtime repair. No push or merge is authorized.

## Revision authority and delivery sequence

This document guides the implementer and reviewer of the default-off Lite route.
The September 7 confirmation accepts the design deltas below, not an execution
restart. These are target requirements, not claims about the current prototype.
Schema, catalog, runtime, and fixture changes remain to be implemented and verified.
Historical reports retain their original meaning; earlier review PASS results do
not validate this revision. The work item's validation status and historical stage
pin remain unchanged, and the expired pin exception is not renewed.

The later measurement acceptance replaces the automated-runner prerequisite with
the supervised comparison defined below. This changes the measurement owner and
interval, not the quality thresholds or product scope. That acceptance alone
does not authorize product implementation, paid runs, or workflow advancement.

The subsequent withdrawal approval permits a bounded local change in the existing
task worktree: remove this branch's automatic Pilot runner, admission, telemetry,
join/comparator, driver and CLI additions from the five ablation/evaluation files;
remove tests solely for that withdrawn path; and decouple mixed product tests in
`review-capability.test.py` without deleting their product assertions. Preserve
the original ablation tool, product validators, failure/retry evidence, and any
CI setup still needed by retained tests. Repair affected claims in this spec,
the plugin README, CLAUDE and runtime guide, and root architecture context.
Historical artifacts remain recoverable from prior commits and their work records;
withdrawal does not repair or pass the known integrity failure. This approval
does not restart the broader Lite implementation, change shared workflow state or
the old stage pin, authorize paid runs, or raise the limits below.

The later consolidation approval permits replacing the 15 required-field queries
inside `review_runtime_validate_line` with one query in `review-runtime.sh`, and
adding parity/missing-field cases to `review-runtime.test.sh`. Preserve the field
list, diagnostic/status, validation order and all other validation phases. Run
the full runtime and capability suites and repeat the local development fixture.
Reconcile only affected existing documentation; add no schema, workflow, service,
storage change or default activation. This bounded local optimization does not
restart the broader Lite implementation or grant shared-state, old-pin, paid-run,
posting or merge authority. Existing implementation limits remain unchanged.

The subsequent integration approval permits explicit source-bound goal material
and the existing outer agent's typed judgment through the current intake,
pending/finalize, and confirmation seams. Its eleven-file envelope is the
capability implementation/test, schema/catalog, profiled review skill block,
this spec, plugin CLAUDE/README/runtime guide, and the affected root
ARCHITECTURE/PRODUCT claims. Run missing-goal, judgment, binding, coverage and
real receipt regressions with fake answers. Preserve earlier pending changes,
existing caps, default-off behavior and publication ownership. Do not change
runtime/posting code, workflows, dependencies, versions, shared state or the
historical pin; stop before commit, push, external review or paid/model/cloud
runs. Archetype admission, transport grouping and blind evaluation remain later
work. This is bounded local implementation, not a workflow-stage transition.

The subsequent seam-repair approval adds `review-runtime.sh` and its existing
test file to that local envelope. A successful invocation may conservatively
retain incomplete coverage after reviewer judgment; preserve its observed result,
candidate/finding consistency, accepted severity, confirmed blockers and the
existing confirmation. Verify different-question and same-question partial
coverage, complete results, failed/skipped attempts and manual fallback. Keep
the existing limits and finish the already-approved protocol tests/docs. This
does not add event types, change storage or posting ownership, migrate old
receipts/locks, alter CI triggers, authorize model/cloud spend or permit a commit.

The later submission acceptance permits those two local commits after verification.
It supersedes the preceding commit stops for this packaging step, not their
implementation limits or the unchanged external-review, spend, shared-state,
historical-pin, push, posting and release boundaries.

| Accepted design delta | Preserved boundary |
|---|---|
| Separate capability contracts from model-process grouping; measure batching and parallel execution before fixing the arrangement. | Every required question retains an accountable capability and validated answer. |
| Give the General Reviewer evidence-bound accept/reject/unresolved judgment, with retained raw contributions and reasons. | Deterministic coverage, confirmed-blocker, confirmation, and posting authority remain in place. |
| Supply explicit goal evidence and substantive blind-adjudication material. | Missing support remains incomplete; no undeclared retrieval or executable expansion. |
| Admit ordinary Lite-eligible fixes, features, and refactors without the mixed-only classification restriction. | Unmodified legacy control, frozen per-arm configuration, five effective pairs, and all quality/time gates. |
| Observe start/end messages, test saving mechanisms, integrate Lite, and run the held-out blind evaluation. | Development samples cannot count as final blind samples or justify promotion. |

The approved outcome remains at least five ordinary PR pairs, median time reduced
by at least 33.3%, at least three pairs individually meeting that threshold, no
missed accepted Critical/High control findings, no increase in false positives,
and complete required coverage. The bounded first evaluation retains exactly five
effective primary slots plus one predesignated backup under the rules below.
No new isolation scheme, paid call, legacy-pin migration, default activation,
publication, merge, release, or implementation-limit increase is authorized here.

Delivery proceeds in this order; these are evidence dependencies, not new approval gates:

1. **Confirm observable timing.** Use the Captain's start message and the
   assistant's delivered complete review/end message, checked against retained
   platform timestamps or an external stopwatch. Keep the automated runner's
   timing and comparator out of the acceptance calculation; its integrity failure
   is not repaired or reclassified. Repairing that unused measurement path is not
   a prerequisite for this supervised comparison. No new isolation is authorized.
   Calibrate the independent judge on known defects, false alarms, and insufficient
   evidence, including human-checked examples, before using it for promotion.
2. **Test the saving mechanism.** Use separate development samples to compare shared
   material, batching/parallel arrangements, and fixed preparation/projection costs
   without deleting required questions. Record quality, full elapsed time, tokens,
   calls, and cost. Fix or stop an arrangement whose overhead erases the saving;
   claim only the smallest adequate arrangement actually compared, not a universal
   minimum. Development model calls require their own recorded budget coverage.
3. **Integrate the measured Lite slice.** Implement the accepted input, grouping,
   judgment, and validation changes at the existing seams. Map removed duplicate
   work to retained obligations and run regression/mutation checks. Other profiles,
   Custom UI, Nightwatch, Forge, and executable expansion stay out of this slice.
4. **Freeze and run the held-out evaluation.** Fix versions, ordinary PR inputs,
   admission rules, run order, tool/model conditions, budgets, and failure handling
   before outcomes. Apply the blind quality decision before opening timing. Retain
   every attempt; do not tune on or replace unsuccessful held-out samples.
5. **Review and deliver.** Bind independent Claude review and actual verification to
   the final revision. Resolve known required findings and re-review, or record an
   explicit Captain-approved deferral; an earlier clean round cannot erase them.
   Recheck against current main without absorbing unrelated work. Report passed,
   failed, and unverified evidence separately; acceptance does not merge or enable
   Lite. Paid review remains subject to its recorded spend authority.

## Outcome and boundary

V1 separates pull-request review into deterministic planning and evidence,
typed review capabilities, and one General Reviewer host. The host behaves like
an interviewer: it receives evidence-backed answers to a fixed question set,
resolves every required question once, and renders the existing review and
confirmation shape. It does not own evidence collection, capability execution,
human authorization, or GitHub mutation.

This delivery defines Lite, Standard, Full, and Custom contracts but implements
only a default-off Lite path. Draft PRs #352-#355 remain unchanged as reference
material, not the control arm; this is not a fifth stacked layer and has no dependency
on their branch heads.

V1 explicitly excludes live runtime or browser probing, performance or
resource-exhaustion analysis, and cross-run duplicate suppression. It does not
integrate Nightwatch or `kc-plugin-forge`, change posting authority, or execute a
paid evaluation before a separate measured budget decision.

The executable Lite cut intentionally fixes the expansion reserve at zero.
`ExpansionRequest/v1` is a documented forward contract only: emitting any such
request ends executable Lite as `ABORTED_INCOMPLETE` with reason
`unsupported_expansion`, whether it asks for a question, evidence, or both.

## Authority map

| Decision or fact | Owner | Enforced boundary |
|---|---|---|
| Explicit supported-profile selection | User | Planner input preserves Lite, Standard, or Full; Custom is refused before intake in the Pilot. |
| Automatic profile recommendation | Deterministic Planner | Closed profile and signal rules in the schema-bound planner. |
| Required questions and capability assignments | Deterministic Planner | Catalog-bound `ReviewPlan/v1`; executable Lite has `plan_rev: 1`. |
| Repository facts and mechanical-test observations | Evidence Builder | Exact base/head binding and content hashes. |
| One review aspect's analysis | Named capability | `CapabilityRequest/v1` to `CapabilityResult/v1`. |
| Required-question coverage | Protocol validator | Closed question terminals; gaps forbid approval. |
| Review synthesis and event recommendation | General Reviewer | `ReviewDecision/v1`; no network or authorization fields. |
| Current runtime capability policy | Deterministic Protocol Projector | Accepted terminals and results project into one `capability-policy/v1`. |
| Authority-bearing runtime receipt | Deterministic Receipt Projector | Fail-closed existing event append/replay seam; shadow mode remains diagnostic only. |
| Human evidence-bound capability fallback | Existing interactive human | `manual-capability-result/v1` with verified frozen-identity evidence. |
| Supervised experiment identity, timing and admission | External operator | Frozen PR/version bindings, retained start/end observations and complete-result checks; no worker-authored timing. |
| Blind quality adjudication | Independent adjudicator | Sealed substantive evidence, arm-hidden envelopes, and quality-before-timing record. |
| Review confirmation | Existing human confirmation gate | Existing `InteractiveConfirmation` boundary. |
| GitHub posting and readback | Existing posting adapter | Existing authorization and once-only posting boundary. |
| Merge, release, spend, and profile promotion | Captain | Outside every V1 protocol object. |

Unknown, malformed, stale, contradictory, or incomplete required input is
non-green. No model-authored field can grant an authority in this table.

## One integrated journey

1. **OBSERVED:** `kc-pr-review` reads the PR and freezes an `IntakeIdentity/v1`
   containing repository, PR, base, head, and a protocol `intake_id`. It rechecks the head before
   confirmation and posting; current `review-runtime.sh` validates the final
   exact-head review identity.
2. **DESIGNED:** The Evidence Builder creates `EvidenceBundle/v1` revision 1
   from shape metadata and explicit goals: changed paths, per-path line counts, diff shape,
   deterministic signal inputs, discovered test-command metadata, and accepted
   goal material of class `pr_body`, `issue`, or `review_comment`. It
   contains no `git_blob` pointer, diff-hunk body, repository-rule body, or file
   body.
3. **DESIGNED:** The Planner selects Lite, Standard, Full, or Custom and emits
   `ReviewPlan/v1` revision 1. The plan freezes required questions, capability
   assignments, evidence needs, mechanical tests, and timeouts before model
   dispatch. Executable Lite records an expansion reserve of zero.
4. **DESIGNED:** The plan pins the full current review configuration: Lite tier,
   declared PR archetype, `full_pass: false`, `probe_required: false`,
   `cross_model: false`, `noise_filter: false`, and the effective capability
   set. The caller computes the canonical hash through `review-runtime.sh
   config-hash`, then invokes `review-runtime.sh start` with that hash; `start`
   consumes it and mints the final `review_key` and runtime run id.
   `ReviewIdentity.run_id` is
   the runtime run id returned by that call, not the protocol `intake_id`. A
   deterministic `IdentityBinding/v1` and side-car audit event record the
   intake-to-runtime binding once; bundle
   revision 2, requests, results, policy, receipt, and terminals emitted after
   the runtime identity is minted all carry the runtime run id. A parity fixture compares the entire canonical
   `review_config` with `review-runtime.sh config-hash` and proves the binding.
5. **DESIGNED:** The Evidence Builder runs only plan-selected mechanical tests
   and materializes only declared evidence into bundle revision 2. Every
   observation is bound to the exact base/head and a content hash; missing
   evidence stays missing.
6. **DESIGNED:** The adapter executes the frozen capability arrangement, which
   may batch compatible typed requests or run independent workers in parallel.
   Each request/result keeps its capability identity, declared material, and
   assigned answers; a shared model call grants no undeclared tools or evidence.
7. **DESIGNED:** The validator accepts a schema-valid, identity-, plan-, and
   evidence-bundle-matching result only when it carries exactly one terminal
   answer for every question in its request and every non-incomplete answer has
   at least one resolvable `git_blob` evidence reference. Missing, extra,
   duplicate, contradictory, or evidence-free assigned answers are rejected and
   make the invocation failed. Emitting any `ExpansionRequest/v1` ends
   executable Lite as `ABORTED_INCOMPLETE` with reason `unsupported_expansion`,
   whether it asks for a question, evidence, or both.
8. **DESIGNED:** The General Reviewer judges schema-accepted contributions against
   the frozen goal and evidence. It records accept/reject/unresolved dispositions
   with reasons, retains raw contributions, and produces one canonical terminal
   per required question. The validator preserves confirmed blockers and gaps
   before projection into the existing report and confirmation vocabulary.
9. **DESIGNED:** After rendering, the deterministic Receipt Projector starts
   after the existing `run.started` and converts accepted capability results and
   failed/unavailable outcomes of invoked capabilities into the remaining closed sequence:
   `lane.started`, zero or more `finding.observed`, `lane.finished`,
   `synthesis.finished`, and `run.finished`. It seals the current body,
   inline-comment, event, option, confirmation-input, and GitHub-call-log hashes,
   appends through the existing runtime seam, and requires replay to report a
   complete receipt. Each invocation lane is `succeeded` if and only if its
   result was schema/evidence accepted; otherwise it is `failed` or `unavailable`.
   Successful invocation is not completed coverage: reviewer uncertainty may
   leave the required question incomplete while retaining confirmed findings.
   Obligation satisfaction is evaluated only after the final attempt: a
   successful final attempt uses fallback `not_needed`; a final attempt that
   did not return a fully accepted result may be satisfied by a verified
   `provided` manual fallback; otherwise fallback
   is `declined`, `failed`, or `unavailable`. Any append, replay, lane/reference,
   or seal failure ends `ABORTED_INCOMPLETE` with reason
   `receipt_incomplete`; the existing fail-open shadow collector is never used
   as authority. An invoked lane that failed or was unavailable emits zero `finding.observed`
   events and contributes no candidate or finding. Every gate-eligible runtime candidate from an
   accepted reviewer disposition is promoted into exactly one finding; candidates with the
   same path, side, evidence content hash, category, and claim key merge into
   one finding. Executable Lite seals `uncertain_candidate_ids: []`.
   Capability-terminal projection reads only the final attempt's lane, so an
   earlier or failed lane cannot safely contribute a candidate.
   The Pilot review receipt deliberately emits no `head.observed`; the fresh
   head check remains at the existing pre-confirmation seam, outside this closed
   receipt sequence, because replay would classify that event as unexpected and
   prevent `lifecycle.complete`.
10. **DESIGNED + OBSERVED:** Every incomplete required question is
    deterministically projected onto at least one incomplete required obligation
    in `capability-policy/v1`. The runtime order is render, seal and append
    receipt, rehydrate `InteractiveCollationDecision/v1`, then request human
    confirmation. Existing typed confirmation prevents approval and preserves
    blocker precedence.
11. **OBSERVED:** Existing posting code rechecks identity and owns GitHub
    mutation. The Pilot stops at a posting preview and never exercises the
    remote mutation path.

Unhappy paths are terminal and visible:

- invalid intake returns `REQUEST_INVALID`;
- missing intent needed to plan returns `NEEDS_CLARIFICATION`;
- a moved head before planning returns `ABORTED_STALE`;
- an identity or head change after the review identity is minted returns
  `INVALIDATED: identity_change`, and a configuration change returns
  `INVALIDATED: configuration_change`; a stale head in the plan-to-identity window remains
  `ABORTED_STALE` on the intake identity;
- a capability-level required-coverage gap with at least one invoked lane does
  not abort: it projects
  `incomplete_required`, `coverage: incomplete`, `approve_eligible: false`, and
  a COMMENT ceiling at confirmation. Those question/obligation and decision
  states are the closed AC-10 disposition, so no `RunTerminal` is emitted and
  the pair remains a promotion failure;
- if missing required evidence skips every planned capability, the zero-lane
  receipt cannot reach existing `lifecycle.complete`; it ends
  `ABORTED_INCOMPLETE: receipt_incomplete`, still non-posting and
  promotion-failing;
- any executable-Lite expansion request returns `ABORTED_INCOMPLETE` with reason
  `unsupported_expansion`;
- terminal `post.result` outcomes remain exactly `posted`,
  `posted_reconciled`, or `failed`; the Pilot only renders a preview;
- invalidation remains the separate `run.invalidated` event with reason
  `head_moved`, `payload_changed`, `identity_changed`, or `expired`;
- an ambiguous attempt emits no terminal `post.result`, retains a
  `kc-pr-flow.pending-post/v1` payload, and is never retried blindly. Ambiguous
  and pending are dispositions/artifacts, not posting status values.

## Profiles and selection

The three named profiles reuse the existing visible tier semantics so the Pilot
does not introduce a second size vocabulary:

| Selection | User meaning | Default entry rule | Review contract |
|---|---|---|---|
| Lite | weak / quick | filtered change below 200 lines and no security signal | Existing Lite-equivalent always-on questions plus deterministic signal-required questions. |
| Standard | medium | 200-500 filtered lines or a security signal | Lite plus design, test, failure, and contract questions. |
| Full | strong | above 500 filtered lines or above 20 changed files | Complete V1 question bank and broader evidence allowance. |
| Custom | user-selected | explicit UI multi-select or natural-language selection | Selected questions plus every catalog entry marked `waivable: false`. |

Automatic routing evaluates Full first, then Standard, then Lite. Thus a
150-line change across 25 files is Full, not Lite; overlapping predicates never
depend on table-reading order.

The current 8-pass rule remains part of every profile contract: when
`full_pass: true` would otherwise select Lite, the effective profile is Standard.
Executable Lite pins `full_pass: false`, so the Pilot cannot bypass that floor.

An explicit user choice wins over automatic recommendation, except that a
request cannot suppress a non-waivable security, identity, or required-coverage
obligation. The Planner records the requested and effective selection and the
reason for every addition. Custom is a selection mode, not a fourth strength.
Because current `review_config` has no `custom` tier, a future Custom plan maps
to the smallest of Lite, Standard, or Full whose catalog question bank is a
superset of the effective Custom selection, with the order fixed as Lite,
Standard, Full. The plan records both `profile: custom` and that backing tier.

The Pilot implements Lite only. Standard and Full keep the current path. An
explicit Custom selection returns one unavailable/not-implemented response
before `IntakeIdentity/v1` is created, outside every executable protocol object,
so it emits no `RunTerminal` and never approximates the selection. These are
complete selection contracts, not executable paths. Enabling another profile or
a non-zero expansion reserve is a route-back condition. If automatic routing
selects Standard or Full for a pre-registered primary treatment pair, that
unchanged-path substitution is recorded as a promotion failure.

The filtered line count is routing metadata only; it does not set the current
runtime's `noise_filter` mode, which remains false for executable Lite.

`KC_PR_FLOW_PROFILED_REVIEW` is a new default-off delivery switch. The review
entrypoint samples it exactly once, before any review dispatch, alongside the
existing `KC_PR_FLOW_REVIEW_TYPED` switch. The profiled Lite path is selected
only when both values are exactly `on`. Unset, `off`, unknown values, or
`KC_PR_FLOW_PROFILED_REVIEW=on` while `KC_PR_FLOW_REVIEW_TYPED` is not exactly
`on` select the unchanged legacy route for that fresh invocation. The route
cannot change during that invocation. The supervised operator sets and records both
values explicitly and never inherits ambient values.

## Question bank and capability mapping

Question identity is global within one review run. A question appears once in
the plan. Executable Lite assigns it to exactly one capability; future profiles
may allow multiple contributors only after a runtime-contract route-back. The
final collation contains exactly one terminal for every required `question_id`;
the schema validator rejects missing or duplicate terminals.

This table is a non-normative view generated from
`review-capability-catalog-v1.json`; tests fail if it drifts from that sole
requiredness authority.

| Question | Lite | Standard | Full | Non-waivable | Default capability |
|---|---|---|---|---|---|
| `goal_alignment` | required | required | required | yes | `goal_alignment` |
| `code_correctness` | required | required | required | yes | `code_correctness` |
| `test_evidence` | `code_change` signal | required | required | yes when activated | `test_evidence` |
| `security_risk` | required | required | required | yes | `security_risk` |
| `minimal_change` | `stacked_pr_shape` signal | required | required | no | `minimal_change` |
| `silent_failure` | required | required | required | yes | `silent_failure` |
| `type_design` | `contract_change` signal | required | required | yes when activated | `type_design` |
| `documentation_accuracy` | required | required | required | yes | `documentation_accuracy` |
| `dependency_supply_chain` | `dependency_change` signal | `dependency_change` signal | required | yes when activated | `dependency_supply_chain` |
| `ci_workflow_safety` | `workflow_change` signal | `workflow_change` signal | required | yes when activated | `ci_workflow_safety` |

Signals are never model-authored. They are a pure function of content-hashed
changed paths and diff shape; PR title, description, comments, accepted intent,
and model output cannot set or clear them. They may add a question but cannot
mark one clean. A capability may
answer `clean`, `findings`, or `evidence_backed_na`; execution failure,
unavailability, timeout, invalid output, duplicate answers, or internally
contradictory answers maps to `incomplete_required` in executable Lite. Lite
assigns exactly one capability to each required question and emits no active
optional obligation. `contradictory_required` is a new forward-contract state;
the current runtime's `incomplete_optional` state is retained but neither is
emitted by executable Lite without a runtime-contract route-back. The existing
Lite catalog's question-to-capability bijection remains a valid content mapping,
not a one-model-call-per-capability requirement. Compatible requests may share a
worker while retaining per-question results; no required answer may be omitted.
The catalog's requiredness rule includes a closed `waivable`
flag; the Planner cannot override it.
For executable Lite, the `test_evidence` manifest requires `diff_hunks` and
lists `mechanical_tests` as optional evidence. Absence of a discoverable test
command therefore does not itself create a required-evidence gap.

## JSON Schema protocol

`kc-pr-flow/schemas/review-capability-v1.schema.json` is the V1 shape source of
truth. `kc-pr-flow/schemas/review-capability-catalog-v1.json` is the sole V1
content authority for question definitions, per-profile requiredness, closed
signal predicate ids, capability manifests, and question-to-capability mapping.
It is validated by the schema. No requiredness or manifest rule is duplicated
in Python. The schema uses JSON Schema 2020-12, `additionalProperties: false` on
authority-bearing objects, closed enums, bounded strings and arrays. Runtime
validators consume its version and fixtures; hand-written runtime checks may be
stricter for safe I/O but may not accept an instance the schema rejects.

| `$defs` object | Purpose | Required binding |
|---|---|---|
| `IntakeIdentity` | Pre-plan exact-head identity | repository, PR, base, head, protocol intake id |
| `ReviewIdentity` | Plan-derived exact review identity | repository, PR, base, head, run id, config hash, review key |
| `IdentityBinding` | Intake-to-runtime correlation | intake identity, review identity, plan hash, timestamp |
| `QuestionDefinition` | Stable question catalog entry | id, version, requiredness rule, closed `waivable` flag |
| `CapabilityManifest` | Skill-as-API public contract | id, version, questions, required/optional evidence classes, optional required-any alternatives, output ref, trust tier; no activation field |
| `PlannerInput` | Deterministic routing input | intake identity, requested mode, PR shape, deterministic signals, concerns |
| `ReviewPlan` | Frozen obligations and budgets | intake identity, plan rev, full review config, profile, questions, assignments, execution grouping, reserve |
| `EvidencePointer` | Content-addressed repository fact | identity, source kind, object, path/locator, hash |
| `GoalInput` / `GoalInputs` | Host-acquired explicit goals / input array | intake identity, source class, locator, original substantive text |
| `GoalMaterial` | Frozen non-Git goal fact | GoalInput plus content hash and record id, preserved across bundle revisions |
| `EvidenceClassBinding` | Manifest-class coverage | evidence class plus class-tagged pointer/test refs or one missing reason |
| `EvidenceBundle` | Selected mechanical material | rev 1 intake identity or rev 2 review identity, revision/hash, parent hash, pointers, test observations, missing list |
| `CapabilityRequest` | One logical capability request | identity, plan rev/hash, bundle revision/hash, capability, question ids, exact evidence material and refs grouped by manifest class |
| `CapabilityResult` | One logical capability response | identity, plan rev/hash, bundle revision/hash, capability, question answers, usage, status |
| `ExpansionRequest` | Bounded add-only request | cause, added questions/evidence, reserve charge |
| `QuestionTerminal` | One canonical collation | question id, state, finding/evidence/gap refs |
| `ReviewerRequest` | Handoff to the existing outer agent | identity, plan/bundle/results/fallback hashes, required questions with selected requests and validated answers |
| `ReviewerJudgment` | Evidence-bound outer-agent assessment | echoed bindings, question assessments, contribution ordinals/dispositions, reasons and selected evidence references |
| `ReviewDecision` | Validated General Reviewer result | identity, plan rev/hash, bundle revision/hash, contribution dispositions/reasons/evidence, terminals, findings, gaps, event, confirmation input |
| `ConfirmationProjection` | Existing user gate input | identity, effective event, decision hash, confirmation required |
| `PostingOutcome` | Read-only `post.result` projection | review key and exact head, run id, payload hash, idempotency key, outcome, remote id when verified |
| `PostingInvalidation` | Read-only `run.invalidated` projection | review key and exact head, run id, closed invalidation reason |
| `RunTerminal` | Closed run outcome | validated identity or bounded invalid-intake echo, status, reason, non-posting disposition |
| `AuditEvent` | Non-authoritative side-car trace | full identity, sequence, event type, payload hash, prior/self hash, fractional RFC3339 timestamp, monotonic nanoseconds for timed events |

`RunTerminal` records non-success dispositions only and has a closed status
enum: `REQUEST_INVALID`,
`NEEDS_CLARIFICATION`, `ABORTED_STALE`, `INVALIDATED`, and
`ABORTED_INCOMPLETE`. Its exhaustive status-to-reason matrix is:

| Status | Permitted reasons |
|---|---|
| `REQUEST_INVALID` | `schema_failure`, `invalid_identity`, `unsupported_major` |
| `NEEDS_CLARIFICATION` | `missing_intent` |
| `ABORTED_STALE` | `stale_head` |
| `INVALIDATED` | `identity_change`, `configuration_change` |
| `ABORTED_INCOMPLETE` | `required_gap`, `contradiction`, `unsupported_expansion`, `receipt_incomplete`, `projection_mismatch` |

In executable Lite, `required_gap` has exactly one trigger: the General Reviewer
fails to emit one canonical terminal for a frozen required `question_id`.
Ordinary capability failure instead reaches the non-aborting incomplete-coverage
decision described above. `contradiction` is forward-contract-only with
`contradictory_required` and has no executable Lite trigger.
`NEEDS_CLARIFICATION: missing_intent` is also forward-contract-only because
executable Lite routing does not require intent. No other reason is valid. This
prose matrix is generated from the schema and is not a second authority. Before
the review identity is minted, terminals bind `IntakeIdentity/v1`; after it is
minted, terminals bind `ReviewIdentity/v1`. For `REQUEST_INVALID` reasons
`schema_failure` and `invalid_identity`, where no valid intake identity can
exist, the schema instead permits one bounded non-authoritative echo containing
only the submitted repository, PR, base, head, and intake-id scalar fields; it
cannot satisfy or authorize any later object.
`REQUEST_INVALID: unsupported_major` is evaluated only after a valid
`IntakeIdentity/v1` exists, such as when a schema-valid Planner input requests
an unsupported protocol major, and therefore always binds that identity rather
than the invalid-intake echo.
A head move after `ReviewIdentity/v1` is minted maps to protocol
`INVALIDATED: identity_change` because head is part of that identity; this is
separate from posting-layer `run.invalidated: head_moved`.
Each permitted status/reason pair has a rejecting mutation fixture.

`PostingOutcome.outcome` maps one-to-one onto the existing terminal
`post.result` enum: `posted`, `posted_reconciled`, or `failed`. It joins the
`post.intent.payload_sha256` to `post.result` by their shared
`idempotency_key`; there is no
invented authorization hash. `PostingInvalidation` separately projects
`run.invalidated` and its four existing reasons. An ambiguous attempt produces
neither object: the absence of `post.result` plus the retained
`kc-pr-flow.pending-post/v1` payload is its non-terminal disposition. Both
projections use the posting run's ordinary `run_id`, not the review run id.
`review-post.sh` never emits either new schema directly and remains the posting
authority.

Every protocol object names its schema major. Unsupported majors fail closed.
Canonical JSON uses UTF-8, duplicate-key rejection, sorted object keys, array
ordering defined per field, and SHA-256 over the canonical bytes. Set-valued
arrays are sorted and unique; ordered event and finding arrays retain their
declared order. Models propose analyses and dispositions; validators derive final
coverage and eligibility. Models do not author signals, review keys, evidence
hashes, plan or bundle revision, or requiredness.

The protocol validator additionally enforces rules JSON Schema alone cannot
express:

1. every evidence reference in a terminal, finding, or decision resolves to an
   accepted `EvidencePointer` at the frozen identity and bundle hash; separately
   named test-observation references resolve to content-hashed
   `EvidenceBundle.test_observations` and never masquerade as pointers;
2. a `CapabilityResult` is accepted, and its lane projects `succeeded`, only if
   it contains exactly one terminal answer for every `question_id` in its
   request and every answer names at least one resolvable `git_blob` reference.
   A `findings` answer has at least one capability contribution;
   `clean` and `evidence_backed_na` have none. Otherwise the result is rejected,
   and the invocation lane projects `failed`; `unavailable` is reserved for an
   adapter or provider that produced no result;
3. a required obligation needs both a valid capability result/fallback and a
   resolved, validated reviewer disposition. The final adapter attempt must have
   returned a fully accepted result, or a verified `provided` exact-keyed
   `manual-capability-result/v1` for the same one-to-one assigned capability is
   provided with terminal assessment `clean` or `evidence_backed_na` and
   non-empty resolvable `git_blob` evidence at the frozen review identity. Without
   valid capability support, fallback is `declined`, `failed`, or `unavailable`,
   never `not_needed`. Valid support with unresolved judgment still leaves the
   obligation `incomplete_required`; it does not rewrite the attempt/fallback history. Lane status
   remains per invocation. A Lite `findings` manual fallback is rejected;
4. every emitted required obligation uses the existing activation condition
   `configured`; signal-gated questions are resolved deterministically before
   projection, inactive optional questions emit no obligation, and the plan
   rejects a second contributor to any required question. The existing
   `observed_optional` behavior is reserved for the unchanged current path;
   `contradictory_required` and `incomplete_optional` are forward-contract
   states outside executable Lite. Catalog validation independently enforces
   the same executable-Lite question-to-capability bijection, so a catalog edit
   cannot introduce a second contributor or assign two active required
   questions to one capability; and
5. projected runtime evidence arrays contain verified `git_blob` pointers only.
   A satisfied obligation carries at least one such pointer. Mechanical-test
   observations remain content-hashed in `EvidenceBundle.test_observations` and
   may be referenced by new-schema results and terminals, but never enter the
   existing runtime evidence array;
6. before any model call, every `required_evidence` class in each planned
   capability's frozen manifest must appear exactly once in bundle revision 2:
   either with at least one class-tagged pointer/test observation, or in the
   exhaustive missing list with a closed reason. `CapabilityRequest.evidence`
   preserves those per-class groups. A bundle or request with an omitted,
   duplicated, wrongly tagged, or missing required class is rejected; a
   required class listed missing forbids a non-incomplete answer and makes the
   question/obligation `incomplete_required`. The adapter skips that capability
   call: it records obligation `terminal_state: incomplete_required`,
   `fallback.status: unavailable`, zero adapter attempts, and no runtime lane,
   rather than paying for an answer that must be rejected.
   As a second explicit protocol-side narrowing of the existing runtime, this
   unavailable status is obligation-side only: a skipped capability emits
   no runtime `lane.started` or `lane.finished`, keeping replayed lanes in exact
   bijection with recorded adapter attempts.
   For `goal_alignment`, the plan must also declare explicit goal material from
   `pr_body`, `issue`, or `review_comment`; absent or insufficient goal support
   prevents a clean answer. Diff-only inference cannot satisfy that obligation; and
7. as an explicit protocol-side narrowing of the existing runtime, failed or
   unavailable lanes have no contributions, candidates, or findings;
   reviewer-accepted gate-eligible runtime candidates each enter exactly one finding, identical runtime merge tuples
   collapse into one finding, and executable Lite has no uncertain candidates.

`incomplete_required` is validator-derived only and is never a
`CapabilityResult` answer value.

Each rule has a mutation fixture, including rejection of a non-`git_blob`
projected runtime pointer and a second contributor to a required Lite question.
`InteractiveCollationDecision/v1` remains the
single authority for final coverage, approval eligibility, blocker precedence,
and event. The new schemas determine protocol inputs and question coverage,
then project into that existing authority; they do not compete with it.
Before confirmation, the rendered confirmation projection must equal the
derived `InteractiveCollationDecision/v1` for effective event, confirmed blocker
refs, capability gap refs, and approval eligibility; any mismatch ends
`ABORTED_INCOMPLETE` with reason `projection_mismatch`. A successful run is
represented by a complete receipt plus
the derived decision, not by a `RunTerminal` success value.

## Plugin document protocol

The catalog stores each capability's public manifest. A generated capability
view exposes that manifest plus operating instructions; it is not a second
authority and is checked byte-for-byte against the catalog fields. Private
provider prompts and unrelated tools remain outside the caller context.

```yaml
capability:
  schema: kc-pr-flow.capability-manifest/v1
  id: code_correctness
  version: 1
  questions: [code_correctness]
  required_evidence: [diff_hunks]
  optional_evidence: [repository_rules, mechanical_tests, related_source]
  trust_tier: repository-read-only
  input_schema_ref: review-capability-v1.schema.json#/$defs/CapabilityRequest
  output_schema_ref: review-capability-v1.schema.json#/$defs/CapabilityResult
```

`QuestionDefinition.requiredness` plus its closed signal-predicate ids are the
only activation authority. `CapabilityManifest` has no activation field and
cannot subtract a question. Because authority-bearing objects reject unknown
properties, a manifest containing `activation_signals` is invalid rather than a
second routing vocabulary.

The caller invokes `capability + typed payload`; it does not concatenate caller
text into a provider system prompt. A capability has repository-read authority
only for evidence explicitly named in its request. V1 capability adapters have
no network, GitHub mutation, lifecycle, synthesis, or authorization authority.

## Planner and evidence rules

Planning is a pure function of `PlannerInput` plus the versioned catalog. The
same canonical input produces the same canonical plan. Profile selection,
question requiredness, capability mapping, evidence selection, test selection,
timeouts, frozen execution grouping, the six current runtime modes, and the zero
Lite expansion reserve are part of the plan hash. Executable Lite pins
`agent_tier: lite` and the four boolean modes to false. The canonical
configuration hash consumes all six modes plus the plan's effective capability
set after sorting and deduplicating it; plan capability ordering is not
hash-bearing. The prototype's constant `mixed` value is not an admission rule:
each arm's archetype is recorded and frozen without forcing the control to change
its normal triage. Archetype differences must be reported, not hidden as savings
from plugin grouping alone.

Evidence acquisition is profile-scoped:

1. Bundle revision 1 binds `IntakeIdentity/v1` and contains shape metadata and goals:
   changed paths, per-path line counts, diff shape, deterministic signal inputs,
   discovered test-command metadata, and accepted goal material of class
   `pr_body`, `issue`, or `review_comment`. For this contract, repository
   content-bearing means `EvidencePointer.kind == git_blob`; revision 1 admits
   none. Repository instructions and all repository file material wait for
   plan-selected revision 2.
2. The Planner selects questions and evidence needs.
3. After the final review identity is minted, the Evidence Builder, as sole
   bundle-revision owner, runs only selected deterministic tests/checks and
   reads only selected repository material into bundle revision 2. Revision 2
   binds `ReviewIdentity/v1` and its parent revision-1 bundle hash.
4. Revision 2 is an exhaustive partition of every plan-declared and
   manifest-required evidence class: each class has class-tagged material or one
   closed missing reason, never neither or both. This partition is validated
   before dispatch.
5. Revision 2 cannot recollect or silently replace a valid revision-1 fact.
   Any `ExpansionRequest/v1` ends the run as `ABORTED_INCOMPLETE` with reason
   `unsupported_expansion`; the request is recorded in the side-car only, and
   no bundle revision 3 exists in the executable Lite Pilot.

Goal material includes the substantive accepted objective, not merely a locator.
The Evidence Builder freezes its source and content; the reviewer must support a
goal-alignment answer with that material and relevant code. Missing or ambiguous
intent leaves the question incomplete under the existing report/confirmation
shape, rather than inventing intent or adding a new user interaction gate.
The host supplies `GoalInputs` through `--goal-material-file`; the adapter does
not retrieve or authenticate sources. `freeze_goals` rejects identity mismatch
and excludes empty/locator-only text. `requests` checks selected revision
continuity and hashes. `required_any_evidence` on goal alignment requires at
least one goal-source class in addition to diff evidence. Goal records remain
outside the Git-only runtime pointer vocabulary.

This ordering prevents the weak profile from paying for Full evidence before it
is selected. Mechanical tests record command, cwd, exit status, started/finished
time, stdout/stderr digest, and exact head. Requests, results, and decisions bind
both the bundle revision and bundle hash. A timed-out or unavailable check is
not converted to a pass; a bundle-revision mismatch is rejected. A fixture
proves revision 1 has no `git_blob` pointer. Before dispatch, the adapter
resolves every selected reference against the accepted bundle and puts the
exact content bytes the capability will consume into its typed request; request
payload measurement includes those bytes, not only their reference list.

Executable Lite permits one initial attempt and one retry only after a
`transient_failure`. If no retry is scheduled, the first failure is classified
`terminal_failure` or `unavailable`; after the optional retry, the final outcome
is `succeeded`, `terminal_failure`, or `unavailable`. Manual fallback follows
the existing closed runtime contract. Excluding `transient_failure` as a final
retry outcome is a third explicit protocol-side narrowing of the base runtime.

Batch only compatible requests within their frozen evidence/tool permissions.
Transport grouping does not merge logical attempts or obligations: the adapter
validates each result separately and records each logical lane, while recording
physical model calls and shared usage once. Missing members remain incomplete;
partial batch success cannot satisfy them. Freeze the grouping before dispatch,
preserve the retry limits, and charge General Reviewer work and all retries
to the measured route; that role need not add a separate agent process.
No grouping is claimed faster until development evidence
supports it; deterministic collation remains validation, not a substitute judge.

For the documented future expansion contract, the window opens only after all
plan-revision-1 capability results bound to evidence-bundle revision 2 are
accepted or terminal. Requests are collected
and sorted by `question_id` into one add-only batch; reserve exhaustion ends the
run as `ABORTED_INCOMPLETE` with reason `required_gap`, never first-come
selection. Executing that contract
requires a new accepted route and changes to current requiredness rules.

## General Reviewer rules

Initial dispatch returns `ReviewerRequest` at the existing pending boundary.
The current outer review agent supplies `ReviewerJudgment` through
`--finalize-dir` and `--reviewer-judgment-file`; no additional reviewer process
is launched. `checked_judgments` verifies binding, reasons, evidence and ordinal
coverage; `check_decision` checks retained findings/severity and coverage before
the runtime rebuilds confirmation. A new fallback requires a refreshed request
and judgment. Re-entry after `result.json` is written is rejected before writes.

The General Reviewer performs an evidence-bound model judgment, not merely
deterministic concatenation. It compares schema-accepted capability contributions
with the explicit goal, selected code, and test observations; records an
accept/reject/unresolved disposition, reason, and resolvable evidence for each;
and proposes one terminal per required question. Raw contributions remain bound
to the decision, including rejected or advisory items. Rejection needs a reason
supported by the frozen material; silence is not rejection or evidence of clean.
Unresolved support or contradictions leave affected coverage incomplete.

The validator checks disposition completeness, identity, evidence, and coverage
before projection. A model cannot make a failed/skipped capability complete,
remove a confirmed blocker, lower requiredness, or authorize posting. The reviewer
cannot inspect undeclared material or invoke an unplanned capability. Any
`ExpansionRequest/v1` retains the `unsupported_expansion` terminal. A raw High
claim is not automatically a confirmed defect, but rejecting it requires the
same retained evidence/reason and remains visible to independent adjudication.

Accepted contributions retain their supported severity; merged contributions
use the maximum, with no silent lowering. Existing quote-survives verification
still applies: a claim without a motivating source line that survives inspection
is forced to confidence 4-5 and demoted to advisory. Before typed candidate creation, the deterministic
adapter applies the existing confidence destination gate: 7-10 become ordinary
candidates; 5-6 become candidates whose summary appends `Medium confidence —
verify`; 3-4 become separately typed advisory observations rendered in the
summary/body but never runtime candidates or blockers; and 1-2 are omitted from published findings
unless severity is `CRITICAL`. An unscored observation defaults to 6, and a
multi-source observation takes the maximum score and receives the existing
multi-source summary prefix. For question-state purposes, `clean` requires
resolved coverage and no gate-eligible candidate; retained advisories are rendered and included in
the sealed body hash, so they are not hidden as silence.

Here, a **capability contribution** is the raw item returned in `CapabilityResult`;
a **runtime candidate** is a reviewer-accepted, post-confidence-gate item eligible
for `finding.observed`. Rejected/unresolved items and advisories are not runtime
candidates, but remain in the bound review record; unresolved questions retain
gaps. Unqualified `candidate` below means runtime candidate.

Within the frozen exact-head run, candidate merge identity is the existing
runtime tuple of source path, side, evidence content hash, category, and claim
key; `question_id` is deliberately excluded. One
candidate may be referenced by multiple question terminals. Same-candidate
contributions with the identical runtime merge tuple must merge across
questions; non-identical matches remain separate findings. Executable Lite does
not use the runtime's uncertain-candidate bucket.
Executable Lite rejects duplicate or internally contradictory answers and maps
the affected required question to `incomplete_required`. The forward-contract
`contradictory_required` state is not projected into the current runtime.

The deterministic Protocol Projector derives `confirmed_blocker_refs` as
exactly the finding ids whose maximum supported severity is `CRITICAL` or
`HIGH`. The catalog freezes that threshold from current `kc-pr-review` prose
practice; it is new typed policy, not a pre-existing runtime severity rule. The
General Reviewer cannot edit that set. Omitting a qualifying finding or adding a
non-qualifying one invalidates the projection; any qualifying ref forces
`REQUEST_CHANGES` and `approve_eligible: false` before confirmation.

The protocol audit is a side-car stream with no replay or review authority. Its
event names may record accepted, rejected, duplicated, contradictory, expanded,
collated, confirmed, and posting observations, but authority-bearing facts ride
only in the existing eleven closed runtime event types and payloads. Each audit
event repeats repository, PR, base, head, run id, config hash, and review key,
and binds previous hash, payload hash, self hash, sequence, and timestamp. It
cannot alter the derived decision or the posting state. This stream begins only
after `IdentityBinding/v1`; pre-plan terminal objects are their own evidence and
do not masquerade as full-identity audit events. `review-capability.py` records
the canonical UTF-8 evidence-payload byte count for each capability request and
monotonic-nanosecond start/finish values for every invocation and retry. Side-car
wall timestamps use RFC3339 with fractional seconds. The runtime event envelope
and its extensions receive no timing or size fields.

An existing interactive-human fallback may satisfy a question only when its
exact-keyed `manual-capability-result/v1` names the capability assigned one-to-one
to that question in the frozen Lite plan and carries non-empty verified
`git_blob` evidence at the frozen review identity. The new-schema wrapper, not
the existing object, binds the evidence-bundle hash. Its
`terminal_assessment` must be `clean` or `evidence_backed_na` and becomes the
question and obligation terminal. A human who finds a defect leaves the question
`incomplete_required`; the derived decision has incomplete coverage,
`approve_eligible: false`, and a `COMMENT` ceiling. The defect remains rendered
in the summary/body and sealed in `body_sha256`. In a valid typed run,
`confirmed-blocker-evidence/v1` is corroborative only and its refs must exactly
equal the derived decision's refs; it preserves `REQUEST_CHANGES` by itself only
when typed decision production is invalid. A `findings` fallback is
forward-contract-only and requires a runtime-contract route-back. Otherwise the
question remains incomplete.

## Blind evaluation and promotion

The operator runs a one-off supervised comparison and retains the original
messages, outputs and timestamp observations outside the worker's editable
review artifacts. The acceptance table is an operator-checked record, not a new
service, schema, ledger or product component. A fresh reader must be able to
recompute its durations and quality decision from those retained observations.

For each PR and version, elapsed time is simply **end minus start**:

- **Start:** the Captain sends the designated start message for that run.
- **End:** the assistant delivers the complete review and confirmation request,
  with an explicit end message. A progress update or an unsupported completion
  claim does not qualify; the operator checks the output and required coverage.
- **Source:** use independently observable platform timestamps that represent
  those events, or an external stopwatch observing the same events. Select one
  method for both versions before running and retain its resolution and evidence.
  Do not assume a message-creation timestamp proves completed output delivery.
  If neither source is available, report timing unavailable rather than invent it.

This is user-observed end-to-end waiting time, including scheduling, queueing,
input acquisition, checkout/material preparation, mechanical tests, planning,
model/tool execution, retries, validation and final-response delivery. Pin inputs
and setup policy before start, but do not precompute either version's review
materials outside the measured interval. Posting, merging and the wait for the
Captain's final confirmation remain outside both runs; independent blind scoring
happens afterward and has its own cost. Do not subtract perceived idle time or
combine these observations with historical host-only or runner-arm timings.

Register every attempt before start and retain PR/base/head, control/treatment
revision, actual model/effort, configuration, start/end evidence, duration,
complete/failed/interrupted outcome, output, retries and any human intervention.
Failure, timeout, cancellation, missing output, missing timing, or a request for
mid-review help stays visible and fails that sample; it is not a quick success or
silently replaced. Passive timing observation is not help with the review.

The branch-added automatic Pilot path is withdrawn; the pre-existing ablation
tool remains a separate instrument. Historical Pilot receipts, costs, timings and
the unresolved receipt/join integrity defect retain their original meaning, not
acceptance authority here. Do not relabel synthetic records as observed messages
or claim this supervised method proves worker-proof automation or sandbox security.

Freeze committed whole-plugin control/treatment versions, identical task wording,
and the existing matching no-posting/tool restrictions. Control uses both typed
and profiled switches `off`; treatment uses both `on`. Preserve actual runtime
identity/coverage evidence and provider usage reports, but never substitute
worker-authored elapsed fields for the operator's two observed endpoints.

The treatment is the default-off Lite path. The control is the current default
path with its unmodified triage at a frozen exact revision, not a forced Full
tier. Before freezing the corpus, both the frozen control triage and the new
deterministic Planner independently evaluate every candidate and record their
complete six-key `review_config.modes` values in the corpus row. A primary or backup
row is admissible only when both report `agent_tier: lite` and `full_pass`,
`probe_required`, `cross_model`, and `noise_filter` as false. Each arm's actual
`pr_archetype` is frozen, but `mixed` is not an eligibility requirement. The
frozen admission record is the sole authority for those expected values. The
primary Pilot corpus contains exactly five such PRs.
The eligible pool includes ordinary fixes, features, and refactors; it does not
require stacked PRs or exclude candidates solely for conventional title prefixes.
Record PR shape and applicability; do not claim coverage of non-Lite populations.
The PR corpus and exact heads are pre-registered and hash-frozen before the first
run as five `primary` rows plus one designated `backup` row. Every attempted pair
remains in the record. The backup may replace exactly one primary only when that
primary's exact input becomes unavailable to both arms; its designation, reason,
and both terminals are recorded without editing the frozen corpus.

The promotion evaluation set is exactly five effective primary slots. Initially
they are the five frozen primary rows. One allowed substitution assigns the
designated backup to the unavailable primary's ordinal; the original row and
both unavailable terminals remain audit evidence outside the evaluation set.
No other substitution or exclusion changes the set. Every effective slot must
contribute one admissible control timing sample and one admissible treatment
timing sample. A control sample excluded from the primary median for any reason,
a treatment selecting a profile other than Lite, or a treatment-only invalid or
incomplete terminal is a promotion failure; none becomes a discarded sample or
an unchanged-path substitute. Non-Lite control tiers remain reported separately
as audit evidence, never as credited samples.

Pairs use the same PR input, model family, reasoning level, host, tool
availability, and timeout policy. Freeze run order and environment/cache policy
before outcomes; do not give one arm an uncharged warmed preparation. Each pair
records the actual control tier.
The operator checks each version's observed `review_config`
against its frozen corpus admission record, including `agent_tier`,
`pr_archetype`, and all four boolean modes: `full_pass`, `probe_required`,
`cross_model`, and `noise_filter`. Any mismatch with that arm's frozen record,
non-Lite tier, or true boolean invalidates the pair and fails promotion, rather
than crediting extra control work or silently discarding a failed sample.
Before adjudication, both arms are normalized into the same current review
summary/finding/recommendation envelope, with capability and terminal provenance
hidden. Preserve each substantive claim, motivating quote, relevant frozen code,
explicit goal, and cited test observations; hashes identify material but do not
replace its contents. Both arms use the same evidence-availability policy.
Pair-to-arm labels and timing stay sealed from the independent adjudicator,
which is separate from the treatment's General Reviewer. Retain raw contribution
dispositions for later audit without leaking capability or arm identity into the
blind packet. Calibrated adjudication freezes accepted findings, same-defect
partitions, false positives, and maximum severity before timing is opened.
Insufficient adjudication evidence cannot count as a quality pass. The judge is
blinded, not the workers operating their own route; no double-blind claim is made.

Promotion requires all of:

1. in every pair in the promotion evaluation set, control reaches its legacy
   confirmation request and treatment's validated decision has `coverage: complete`,
   no invalid/incomplete terminal, and reaches its typed confirmation request;
2. within the promotion evaluation set, no accepted Critical or High control
   finding is absent from treatment;
3. within the promotion evaluation set, aggregate treatment false positives are
   no greater than control;
4. within the promotion evaluation set, median treatment end-minus-start time is
   at least 33.3% lower than the control median; and
5. at least three of the exactly five effective primary pairs individually
   clear 33.3%.

Rule 5 is a per-pair consistency guard; it does not replace rule 4's aggregate
median requirement, and both must pass. Report `1 - median(treatment) /
median(control)` and each pair's `1 - treatment / control`; require at least
0.333 for the aggregate and at least three pairs, without rounding a miss to pass.
The operator retains and checks the arithmetic after the blind quality verdict
is frozen, without delegating sample admission to the defective automated join.

Synthetic fixtures, structural timing, discarded invalid pairs, and fewer than
five effective primary slots cannot promote. Five pairs support only this guarded
Lite Pilot, not a general statistical quality claim. The legal first cost step
uses pre-existing production telemetry from the current default path, not
experiment control runs, to calculate a conservative per-run cost ceiling. No
experiment model call in either control or treatment occurs until that ceiling
and a fixed total experiment budget are recorded and Captain-approved.
The pre-freeze control-triage admission pass is itself a control-arm model call,
occurs only after that approval, and is charged against the same fixed total.
It uses the identical pinned tool policy, frozen checkout, and exact head as the
corresponding control run. If the budgeted admission pass cannot fill five
primary rows plus the backup, the Pilot stops without weakening the predicate,
reselecting after results, or claiming promotion.

Pre-registration records the saving mechanism selected on development samples:
shared evidence and measured execution grouping must offset mechanical tests,
General Reviewer judgment, and protocol overhead. A higher capability count
does not prescribe more physical model calls. Freeze the selected arrangement
before held-out runs; development results do not satisfy promotion.
It also records the fixed arm coupling: treatment is typed plus profiled while
control is the current legacy route, so timing supports the combined-route
effect and cannot be attributed to profiled plugins alone.
Both arms retain actual provider token/cost reports and externally observed
end-to-end time. Missing usage remains unknown, never zero. Treatment additionally
records logical capability count, physical model calls and grouping, evidence
payload bytes, and lane critical-path time
from the side-car, so a miss cannot be explained away after timing opens.

The cost ceiling reads only numeric completed-review entries from the existing
`~/.claude/audit/pr-daemon-usage.jsonl` ledger whose action begins
`Action taken: REVIEW`; at least five qualifying entries must exist, and the
maximum measured cost of those review-bearing daemon iterations becomes the
hard per-run experiment ceiling. The composite action may read
`Action taken: REVIEW #N / FIX #M`; an iteration may therefore include bundled fix work, so
this intentionally overestimates rather than claiming an isolated review cost.
The operator rejects malformed, idle, or unclassified entries and does not start
an experiment when the ledger or the separately approved budget is insufficient.


## Retained documents and project context

The new protocol spec is a retained contract under Retained Document Policy
Rules 1-4 and 6-8. Its per-section overlap check covers `PRODUCT.md`,
`ARCHITECTURE.md`, `kc-pr-flow/README.md`, `kc-pr-flow/CLAUDE.md`,
`kc-pr-flow/docs/review-runtime.md`, `reference/review-runtime.md`, and
`reference/review-triage.md`. Durable rules live here or in the executable
schema/catalog. Only documents whose durable claim changes are edited; the
others are overlap-checked without receiving a redundant link. Experiment
status and measured results stay in the work item, not this retained document.


Implementation evidence and the path-by-path ownership map live in the work item.
The authority map above remains the durable component boundary. Capability views
are generated from the catalog; one tracked file per question is not permitted.

## Implementation stop numbers

Measure from `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`. Stop and report before
continuing when any threshold is crossed:

- more than 20 changed files;
- more than 6,600 total changed lines; or
- more than 1,903 changed lines across the schema, catalog, protocol fixtures, and their
  focused tests.

The focused limit reflects the previously recorded Captain approval in the work
item, not a new increase in this revision. Include all relevant runtime/ablation
tests and corpus changes; historical over-limit reports are not rewritten.


Also stop immediately if correctness needs full-catalog evidence before
planning, any executable expansion, a new CI workflow, a new posting owner,
persistent cross-run state, runtime/browser probing, or executable Standard,
Full, or Custom paths. The Captain then chooses reduce scope, reshape with new
thresholds, or promote the profile.

Hosted CI cost per PR is unmeasured. The implementation may add one focused
command to the existing review-runtime workflow, but it must measure its added
wall time before any cost claim or workflow-trigger widening.

## Required verification

- Implementation must demonstrate one mutation that makes each authority-bearing
  validator fail; green-only fixtures do not prove the gate.
- Fixtures must prove full-config hash parity, question-gap projection, receipt
  replay completeness, intake-to-runtime id binding, evidence reference
  resolution, non-`git_blob` runtime
  pointer rejection, non-incomplete answer provenance, second-contributor
  rejection, missing-assigned-answer rejection without approval, rejection of a
  candidate on a non-succeeded lane, rejection of non-empty Lite uncertain
  candidates, rejection of `clean` when a manifest-required evidence class is
  missing, pre-dispatch rejection when a required evidence class is neither
  materialized nor listed missing, valid rehydration with
  `terminal_state: incomplete_required`, `fallback.status: unavailable`, zero
  attempts, and no runtime lane when a required class is listed
  missing, catalog rejection of a manifest carrying an
  `activation_signals` field, rejection of goal-alignment success without explicit
  goal support, bounded invalid-intake echo acceptance only for its two permitted
  `REQUEST_INVALID` reasons, a failed-final-attempt plus verified `provided` fallback yielding a
  valid non-incomplete obligation, the same failure plus declined fallback
  yielding no approval, rejection of a Lite `findings` manual fallback,
  valid-decision blocker evidence whose refs differ yielding invalid
  confirmation with COMMENT/no blockers/no approval,
  capability failure yielding incomplete coverage and a COMMENT ceiling without
  a `RunTerminal`, default-off and rollback parity with the unchanged route,
  exact-on/exact-on profiled activation sampled once before dispatch, rejection
  of every other profiled/typed switch pairing, and catalog-level enforcement
  of the executable-Lite question-to-capability bijection,
  Critical/High blocker-ref exactness and forced `REQUEST_CHANGES`, confidence
  destination boundaries, bundle-revision mismatch rejection, rendered/derived
  confirmation parity, terminal-post-result parity, separate invalidation
  parity, ambiguous-result absence with retained pending payload, all
  run-terminal status/reason
  pairs including zero-lane-all-skipped `receipt_incomplete` and
  `projection_mismatch`, zero
  `git_blob` pointers in bundle revision 1, and
  prose-table/catalog parity. Grouping fixtures must retain every logical answer,
  reject missing batch members and cross-request evidence, and avoid double-counted
  physical-call cost. Reviewer fixtures must reject missing dispositions/reasons,
  unresolved-to-clean conversion, and suppressed confirmed blockers; retain raw
  rejected contributions and prove an evidence-supported rejection.
- Withdrawal checks preserve the original ablation commands and baseline tests,
  reject removed Pilot entry points, and retain mixed-test product assertions for
  dispatch/result binding, raw failures/retries, identity invalidation, and
  confirmation. Removed automation tests do not waive the supervised acceptance
  rules above; historical results remain historical and the integrity failure
  remains unresolved rather than repaired.
- Supervised acceptance checks the retained start/end observations and complete
  outputs against the frozen PR/version bindings, preserves failed or interrupted
  attempts, and independently recomputes the five-pair arithmetic. Missing or
  substituted observations and incomplete reviews cannot yield a passing sample.
  Verify ordinary non-mixed Lite admission, development/holdout separation and
  arm-hidden substantive evidence. Calibrate the independent judge on known
  defects, false alarms and insufficient evidence, including human-checked cases.
  Green schemas or timings cannot replace the blind quality decision.
