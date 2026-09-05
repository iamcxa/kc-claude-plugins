# Profiled PR review capability protocol V1

- **Date:** 2026-09-05
- **Product:** `kc-pr-flow`
- **Delivery base:** `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`
- **Work item:** `profiled-pr-review-capability-protocol`
- **Profile:** Pilot / Product slice
- **Status:** shaped for a default-off Lite implementation

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
`unsupported_expansion`, whether it asks for a question, evidence, or both. This
is an explicit
shape delta from the Development Brief's executable bounded-expansion wording
and requires Captain acceptance at the ideation gate before build begins.

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
| Blind experiment execution and provenance | Existing `review-ablation` runner | Frozen corpus, whole-tree arm manifests, identical driver, runtime receipts. |
| Blind quality adjudication | Independent adjudicator | Sealed normalized envelopes and arm-hidden adjudication record. |
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
   from shape metadata only: changed paths, per-path line counts, diff shape,
   deterministic signal inputs, discovered test-command metadata, and accepted
   goal/concern pointers of kind `pr_body`, `issue`, or `review_comment`. It
   contains no `git_blob` pointer, diff-hunk body, repository-rule body, or file
   body.
3. **DESIGNED:** The Planner selects Lite, Standard, Full, or Custom and emits
   `ReviewPlan/v1` revision 1. The plan freezes required questions, capability
   assignments, evidence needs, mechanical tests, and timeouts before model
   dispatch. Executable Lite records an expansion reserve of zero.
4. **DESIGNED:** The plan pins the full current review configuration: Lite tier,
   `mixed` PR archetype, `full_pass: false`, `probe_required: false`,
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
6. **DESIGNED:** The capability adapter invokes each selected capability in
   parallel with a typed request. Each capability sees only the declared
   evidence and returns terminal answers for its assigned questions.
7. **DESIGNED:** The validator accepts a schema-valid, identity-, plan-, and
   evidence-bundle-matching result only when it carries exactly one terminal
   answer for every question in its request and every non-incomplete answer has
   at least one resolvable `git_blob` evidence reference. Missing, extra,
   duplicate, contradictory, or evidence-free assigned answers are rejected and
   make the invocation failed. Emitting any `ExpansionRequest/v1` ends
   executable Lite as `ABORTED_INCOMPLETE` with reason `unsupported_expansion`,
   whether it asks for a question, evidence, or both.
8. **DESIGNED:** The General Reviewer consumes only accepted evidence and
   results. It produces one canonical terminal per required question, retains
   every blocker and unresolved gap, and renders the current summary, findings,
   recommendation, event, and confirmation input.
9. **DESIGNED:** After rendering, the deterministic Receipt Projector starts
   after the existing `run.started` and converts accepted capability results and
   failed/unavailable outcomes of invoked capabilities into the remaining closed sequence:
   `lane.started`, zero or more `finding.observed`, `lane.finished`,
   `synthesis.finished`, and `run.finished`. It seals the current body,
   inline-comment, event, option, confirmation-input, and GitHub-call-log hashes,
   appends through the existing runtime seam, and requires replay to report a
   complete receipt. Each invocation lane is `succeeded` if and only if its
   result was fully accepted; otherwise it is `failed` or `unavailable`.
   Obligation satisfaction is evaluated only after the final attempt: a
   successful final attempt uses fallback `not_needed`; a final attempt that
   did not return a fully accepted result may be satisfied by a verified
   `provided` manual fallback; otherwise fallback
   is `declined`, `failed`, or `unavailable`. Any append, replay, lane/reference,
   or seal failure ends `ABORTED_INCOMPLETE` with reason
   `receipt_incomplete`; the existing fail-open shadow collector is never used
   as authority. An invoked lane that failed or was unavailable emits zero `finding.observed`
   events and contributes no candidate or finding. Every gate-eligible runtime candidate from an
   accepted result is promoted into exactly one finding; candidates with the
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
cannot change during that invocation. The ablation runner sets and records both
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
| `goal_alignment` | required | required | required | yes | Goal alignment reviewer |
| `code_correctness` | required | required | required | yes | Correctness reviewer |
| `test_evidence` | `code_change` signal | required | required | yes when activated | Test evidence reviewer |
| `security_risk` | required | required | required | yes | Security reviewer |
| `minimal_change` | `stacked_pr_shape` signal | required | required | no | Minimal-change reviewer |
| `silent_failure` | required | required | required | yes | Silent-failure reviewer |
| `type_design` | contract/type signal | required | required | yes when activated | Type-design reviewer |
| `documentation_accuracy` | required | required | required | yes | Documentation reviewer |
| `dependency_supply_chain` | dependency signal | dependency signal | required | yes when activated | Supply-chain reviewer |
| `ci_workflow_safety` | workflow signal | workflow signal | required | yes when activated | CI workflow reviewer |

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
emitted by executable Lite without a runtime-contract route-back. The executable Lite catalog enforces a question-to-capability
bijection: no capability owns two active required questions and no question has
two contributors. The catalog's requiredness rule includes a closed `waivable`
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
| `CapabilityManifest` | Skill-as-API public contract | id, version, questions, required/optional evidence classes, output ref, trust tier; no activation field |
| `PlannerInput` | Deterministic routing input | intake identity, requested mode, PR shape, deterministic signals, concerns |
| `ReviewPlan` | Frozen obligations and budgets | intake identity, plan rev, full review config, profile, questions, assignments, reserve |
| `EvidencePointer` | Content-addressed repository fact | identity, source kind, object, path/locator, hash |
| `EvidenceClassBinding` | Manifest-class coverage | evidence class plus class-tagged pointer/test refs or one missing reason |
| `EvidenceBundle` | Selected mechanical material | rev 1 intake identity or rev 2 review identity, revision/hash, parent hash, pointers, test observations, missing list |
| `CapabilityRequest` | One typed invocation | identity, plan rev/hash, bundle revision/hash, capability, question ids, exact evidence material and refs grouped by manifest class |
| `CapabilityResult` | One typed terminal response | identity, plan rev/hash, bundle revision/hash, capability, question answers, usage, status |
| `ExpansionRequest` | Bounded add-only request | cause, added questions/evidence, reserve charge |
| `QuestionTerminal` | One canonical collation | question id, state, finding/evidence/gap refs |
| `ReviewDecision` | General Reviewer result | identity, plan rev/hash, bundle revision/hash, terminals, findings, gaps, event, confirmation input |
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
| `REQUEST_INVALID` | `schema_failure`, `unsupported_major`, `invalid_identity` |
| `NEEDS_CLARIFICATION` | `missing_intent` |
| `ABORTED_STALE` | `stale_head` before review identity is minted |
| `INVALIDATED` | `identity_change`, `configuration_change` after review identity is minted |
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
declared order. Models never author signals, review keys, evidence hashes, plan
or bundle revision, requiredness, or terminal state.

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
3. an executable required obligation is satisfied if and only if its final
   adapter attempt returned a fully accepted result, or a verified `provided` exact-keyed
   `manual-capability-result/v1` for the same one-to-one assigned capability is
   provided with terminal assessment `clean` or `evidence_backed_na` and
   non-empty resolvable `git_blob` evidence at the frozen review identity. A
   satisfied obligation and question end in the accepted result or fallback
   assessment; otherwise both end `incomplete_required` and fallback is
   `declined`, `failed`, or `unavailable`, never `not_needed`. Lane status
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
   Catalog validation also forbids an
   executable-Lite manifest from listing `pr_body`, `issue`, or
   `review_comment` intent material as `required_evidence`; and
7. as an explicit protocol-side narrowing of the existing runtime, failed or
   unavailable lanes have no contributions, candidates, or findings;
   accepted-result gate-eligible runtime candidates each enter exactly one finding, identical runtime merge tuples
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
timeouts, the six current runtime modes, and the zero Lite expansion reserve are
part of the plan hash. Executable Lite pins `agent_tier: lite`,
`pr_archetype: mixed`, and the four boolean modes to false. The canonical
configuration hash consumes all six modes plus the plan's effective capability
set after sorting and deduplicating it; plan capability ordering is not
hash-bearing. The executable Lite Planner derives `pr_archetype` as the constant
`mixed`; it performs no title or model-based archetype classification.

Evidence acquisition is profile-scoped:

1. Bundle revision 1 binds `IntakeIdentity/v1` and contains shape metadata only:
   changed paths, per-path line counts, diff shape, deterministic signal inputs,
   discovered test-command metadata, and accepted goal/concern pointers of kind
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

For the documented future expansion contract, the window opens only after all
plan-revision-1 capability results bound to evidence-bundle revision 2 are
accepted or terminal. Requests are collected
and sorted by `question_id` into one add-only batch; reserve exhaustion ends the
run as `ABORTED_INCOMPLETE` with reason `required_gap`, never first-come
selection. Executing that contract
requires a new accepted route and changes to current requiredness rules.

## General Reviewer rules

The General Reviewer is the sole synthesis host but not a super-capability. It
may compare results, identify contradictions, select the highest supported
severity only among non-contradictory contributions, merge same-candidate
contributions, and render the closed result. Authoring an
`ExpansionRequest/v1` is a forward contract only; in executable Lite it is the
`unsupported_expansion` terminal, not a permitted synthesis step. The General
Reviewer may not inspect
undeclared repository content, dispatch an unplanned capability, downgrade
requiredness, delete a finding, infer clean from silence, or produce
authorization.

Candidate severity is carried by the accepted `CapabilityResult`; synthesis may
select the maximum supported severity across merged contributions but cannot
invent or silently lower it. Capability contributions first retain the existing
quote-survives verification gate: a claim without a motivating source line that
survives inspection is forced to confidence 4-5 and demoted to advisory. Before typed candidate creation, the deterministic
adapter applies the existing confidence destination gate: 7-10 become ordinary
candidates; 5-6 become candidates whose summary appends `Medium confidence —
verify`; 3-4 become separately typed advisory observations rendered in the
summary/body but never runtime candidates or blockers; and 1-2 are dropped
unless severity is `CRITICAL`. An unscored observation defaults to 6, and a
multi-source observation takes the maximum score and receives the existing
multi-source summary prefix. For question-state purposes, `clean` means no
gate-eligible candidate; retained advisories are still rendered and included in
the sealed body hash, so they are not hidden as silence.

Here, a **capability contribution** is the pre-confidence-gate item returned in
`CapabilityResult`; a **runtime candidate** is the post-gate typed item eligible
for `finding.observed`. Dropped contributions and retained advisories are never
runtime candidates. Unqualified `candidate` below means runtime candidate.

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

The existing `review-ablation` harness remains the sole experiment runner and
provenance owner. V1 recovers its frozen-corpus validation, pristine checkouts,
arm manifests, byte-identical driver prompt, runtime-reported model id,
no-posting/no-mutation guards, confirmation-ready stop, usage, cost, and
wall-clock receipts. It does not reuse the existing alpha-0.05
`anchor_set`/`severity_mix`/`tokens` comparator as the Pilot verdict.

The Pilot updates the byte-identical driver stop from the end of Step 6a to the
moment the Step 6c confirmation request has been generated, before human input.
Both arms therefore pay every step needed to become confirmation-ready. For
Pilot runs, the byte-identical driver emits
`kc-pr-flow.ablation-driver-receipt/v1`, which retains the existing v3 fields and
adds the symmetric configuration and retry reports. The runner, not the prompt, wraps it as
`kc-pr-flow.ablation-run/v4`. Control records `protocol_mode: legacy` and
`coverage: not_applicable`. The byte-identical driver receipt output is extended
symmetrically with the six-key `review_config.modes` observed by each arm's skill.
The control driver reads those values directly from ordinary triage state and
does not enable the diagnostic shadow switch.
That report is corroboration only: the frozen corpus admission record is the
configuration authority, and the runner makes a missing or mismatching report
a promotion failure. Treatment is a closed `oneOf`: either it records the
derived decision's coverage and approval eligibility with `run_terminal: null`,
or it records one `RunTerminal` with decision fields absent. It derives
capability count from frozen `capability-policy/v1`, and evidence bytes plus lane
critical-path milliseconds from the validated non-authoritative side-car. The
byte metric sums canonical evidence payload bytes across dispatched requests;
the lane critical path is the latest finish minus earliest start across all
invocations and retries. A treatment terminal
without an agent findings receipt is still recorded as a failed-run v4 receipt;
an unexplained missing receipt in either arm fails the experiment.
Each v4 pair also records retries and human intervention. Treatment retry count
is runner-derived from side-car adapter-attempt records; control retry count is
the symmetric driver's reported retry count and is informational, never a gate
authority. The runner writes `human_intervention_count: 0` only after verifying
the driver stopped before human input; any resumed prompt or human input
invalidates the run instead of being recorded as zero.
An admitted treatment that reports non-Lite cannot fall through to legacy: its
corroborative configuration mismatch makes the pair a promotion failure before
the treatment `oneOf` is evaluated, so no third receipt branch is reachable.

The bounded harness delta adds two operations: `pilot-arm` accepts only committed
whole-plugin control and treatment trees and pins their commit plus canonical
tracked-tree hash; `pilot-compare` consumes guarded joined receipts plus a sealed
arm-hidden adjudication record and applies the five promotion rules below. Run
manifests additionally pin reasoning effort, host executable hash, tool-policy
hash, timeout, and the exact sampled activation environment. The runner sets
`KC_PR_FLOW_REVIEW_TYPED=off` and `KC_PR_FLOW_PROFILED_REVIEW=off` for control,
and sets both to `on` for treatment; it records both values per run and rejects
any other pairing. Ambient operator values are never inherited. The prompt is
still byte-identical; the two pinned switches are part of the intentional arm
difference. Missing receipts, changed provenance, incomplete treatment, or
comparator-schema drift fail the experiment rather than falling back to the
older ablation verdict.

The pinned tool policy is mechanical: the model child receives an empty
temporary GitHub CLI config directory, no GitHub token variables, an empty MCP
configuration, and no web-fetch/search tools. The runner rejects inherited
credentials before launch and hashes this policy into the manifest. Both arms
review only the frozen local checkout; the prose no-posting instruction is not
the only guard.

The treatment is the default-off Lite path. The control is the current default
path with its unmodified triage at a frozen exact revision, not a forced Full
tier. Before freezing the corpus, both the frozen control triage and the new
deterministic Planner independently evaluate every candidate and record their
complete six-key `review_config.modes` values in the corpus row. A primary or backup
row is admissible only when both report `agent_tier: lite`,
`pr_archetype: mixed`, and `full_pass`, `probe_required`, `cross_model`, and
`noise_filter` as false. The
frozen admission record is the sole authority for those expected values. The
primary Pilot corpus contains exactly five such PRs.
The Planner independently contributes the deterministic profile/tier decision;
its `mixed` archetype is a fixed Pilot value, while the control triage supplies
the independent archetype observation used for admission.
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
availability, and timeout policy. Each pair records the actual control tier.
The runner validates the control receipt's corroborative `review_config`
against its frozen corpus admission record, including `agent_tier`,
`pr_archetype`, and all four boolean modes: `full_pass`, `probe_required`,
`cross_model`, and `noise_filter`. Any control value other than
`agent_tier: lite`, `pr_archetype: mixed`, and all four booleans false invalidates the
pair and makes that primary pair a promotion failure rather than crediting the
extra control work as protocol savings.
Before adjudication, both arms are normalized into the same current review
summary/finding/recommendation envelope, with capability and terminal provenance
hidden. Pair-to-arm labels stay sealed from the adjudicator. Independent
adjudication freezes accepted findings, same-defect partitions, false positives,
and maximum severity before timing is opened.

Review-to-confirmation-ready includes intake, evidence acquisition, planning,
mechanical tests, capability calls, validation, synthesis, rendering, receipt
projection and append, replay, rehydration, and confirmation-request production.
It excludes human wait and actual GitHub posting in both arms. An unsupported
expansion ends the treatment sample as a promotion failure.

Promotion requires all of:

1. in every pair in the promotion evaluation set, control reaches its legacy
   confirmation request and treatment's v4 receipt has `coverage: complete`, no
   invalid/incomplete `RunTerminal`, and reaches its typed confirmation request;
2. within the promotion evaluation set, no accepted Critical or High control
   finding is absent from treatment;
3. within the promotion evaluation set, aggregate treatment false positives are
   no greater than control;
4. within the promotion evaluation set, treatment median wall time is at least
   33.3% lower than control; and
5. at least three of the exactly five effective primary pairs individually
   clear 33.3%.

Rule 5 is a per-pair consistency guard; it does not replace rule 4's aggregate
median requirement, and both must pass.

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
corresponding control run. Because exact `pr_archetype: mixed` admission excludes
conventional `feat:` or `fix:` commit-message prefixes and other named-archetype cues, the eligible pool is deliberately
narrower than ordinary Lite. If the budgeted admission pass cannot fill five
primary rows plus the backup, the Pilot stops without weakening the predicate,
reselecting after results, or claiming promotion.

Pre-registration records the hypothesized saving mechanism: smaller
per-capability evidence payloads and parallel critical-path execution must
offset the treatment's higher capability count and charged mechanical tests.
It also records the fixed arm coupling: treatment is typed plus profiled while
control is the current legacy route, so timing supports the combined-route
effect and cannot be attributed to profiled plugins alone.
Both arms record token totals and outer wall time. Treatment additionally
records capability count, evidence payload bytes, and lane critical-path time
from the side-car, so a miss cannot be explained away after timing opens.

The cost ceiling reads only numeric completed-review entries from the existing
`~/.claude/audit/pr-daemon-usage.jsonl` ledger whose action begins
`Action taken: REVIEW`; at least five qualifying entries must exist, and the
maximum measured cost of those review-bearing daemon iterations becomes the
hard per-run experiment ceiling. The composite action may read
`Action taken: REVIEW #N / FIX #M`; an iteration may therefore include bundled fix work, so
this intentionally overestimates rather than claiming an isolated review cost.
Malformed, idle, or unclassified entries are rejected. The harness fixture
proves those filters and refuses to launch when the ledger is insufficient.

## Reverse-recovery audit

The boundary was the accepted exact-head-to-confirmation journey. Search one used
`rg` across current `kc-pr-review`, runtime, posting, triage, tests, and project
context. Search two compared the exact `origin/main` tree with the live heads and
file inventories of Draft PRs #352-#355. A reviewer-directed third search found
the existing `review-ablation` measurement harness and daemon cost ledger that
the first two searches missed; the route below now recovers them explicitly.

| Surface | Location | Completeness | Need | Decision and disproof hook |
|---|---|---|---|---|
| Exact-head identity, evidence pointers, typed coverage, replay | `review-runtime.sh`, `review-runtime.test.sh` | WORKING_UNIT_UNPROVEN | REQUIRED | **use**; a real typed Lite run with a moved-head mutation must fail closed. |
| Confirmation projection and posting owner | `kc-pr-review/SKILL.md`, `review-post.sh` | WORKING_UNIT_UNPROVEN | REQUIRED | **use**; the unchanged posting contract must reject an edited event or stale head. |
| Deterministic delta planner shape | Draft PR #353 `review-plan.sh` | WORKING_UNIT_UNPROVEN | REQUIRED | **recover selectively**; canonical equal inputs must yield equal plans, and invalid evidence must select the safe route. |
| Profile-scoped Evidence Builder | current tree | MISSING | REQUIRED | **build**; two searches found no owner producing a plan-selected bundle with mechanical-test receipts. |
| Capability manifest/request/result API | current tree | STUB | REQUIRED | **build** from existing capability names and lane results; schema mutations must be rejected. |
| General Reviewer question collation | current tree | STUB | REQUIRED | **build** around existing typed decision; duplicate/missing question terminals must fail. |
| Authority-bearing receipt projection | `review-runtime.sh` append/replay seam | STUB | REQUIRED | **build fail-closed mode**; a complete rendered Lite result must replay with every lane/reference and behavior hash sealed before confirmation. |
| Frozen blind-run provenance | `review-ablation.sh`, core, corpus, driver, tests | WORKING_UNIT | REQUIRED | **use runner and recover minimally**; base tests pass 82/0. Add committed whole-tree arms, five-PR Lite corpus, pinned effort/host/tools/timeout, and Pilot comparator. Existing alpha-0.05 comparator is not the wall-time verdict. |
| Historical cost ledger | `pr-review-daemon.sh` usage JSONL | WORKING_UNIT_UNPROVEN | REQUIRED | **use read-only**; fewer than five valid completed reviews or any malformed selected record blocks budget calculation. |
| Inline shadow collection recipes | `kc-pr-review/SKILL.md` | WORKING_UNIT_UNPROVEN | NO_OBSERVED_CONSUMER after Lite cutover | **removal candidate only**; delete only after default-off parity and without-it evidence. |
| Add-only expansion through current runtime | `review-runtime.sh` capability identity and attempt rules | INCOMPATIBLE | NOT REQUIRED IN EXECUTABLE LITE | **document only**; any request terminates incomplete. Runtime contract change requires a new accepted route. |

The resulting route is use existing identity/evidence/confirmation/posting,
recover only the planner idea rather than its 662-line implementation, and build
the missing protocol layer. No existing surface is deleted in shape.

## Retained documents and project context

The new protocol spec is a retained contract under Retained Document Policy
Rules 1-4 and 6-8. Its per-section overlap check covers `PRODUCT.md`,
`ARCHITECTURE.md`, `kc-pr-flow/README.md`, `kc-pr-flow/CLAUDE.md`,
`kc-pr-flow/docs/review-runtime.md`, `reference/review-runtime.md`, and
`reference/review-triage.md`. Durable rules live here or in the executable
schema/catalog. Only documents whose durable claim changes are edited; the
others are overlap-checked without receiving a redundant link. Experiment
status and measured results stay in the work item, not this retained document.

```yaml
project_context:
  impact: update
  authority: PRODUCT.md and ARCHITECTURE.md
  claim_locator: 'PRODUCT.md heading "kc-pr-flow: Agent-native PR review"; ARCHITECTURE.md heading "kc-pr-flow: Agent-native review runtime"'
  surface: review component boundaries, target capabilities, and success measures
  stale_claim: D5 describes coverage only by capability; D2 closes the runtime event envelope; ARCHITECTURE.md line 201 makes InteractiveCollationDecision/v1 the approval authority; docs/review-runtime.md says the runtime does not adapt lane scheduling
  approved_change: retain D2 and the line-201 authority; project question gaps into existing capability obligations; add a default-off external Planner without moving confirmation or posting authority
  landed_change: pending
  planned_check: compare every journey component and authority row in this spec against PRODUCT.md and ARCHITECTURE.md, then run the protocol contract tests on the delivered exact head
  validation_evidence: pending
```

## Where implementation may touch

Current line counts were measured at the pinned delivery base. New-file counts
are shape estimates, not budgets.

| Path | Lines now | Estimated after | Journey obligation |
|---|---:|---:|---|
| `kc-pr-flow/schemas/review-capability-v1.schema.json` | 0 | 540 | Closed V1 protocol source of truth, including class bindings and side-car telemetry. |
| `kc-pr-flow/schemas/review-capability-catalog-v1.json` | 0 | 180 | Sole question requiredness and capability-manifest authority. |
| `kc-pr-flow/scripts/review-capability.py` | 0 | 640 | Schema adapter, deterministic Lite plan, selected evidence, result validation, side-car telemetry, collation, Pilot verdict projection. |
| `kc-pr-flow/scripts/review-capability.test.py` | 0 | 720 | Positive, mutation, identity, required-gap, expansion, and rollback checks. |
| `kc-pr-flow/test/fixtures/review-capability-v1.jsonl` | 0 | 260 | Single-file valid and invalid exact-head protocol examples. |
| `kc-pr-flow/skills/kc-pr-review/SKILL.md` | 1,974 | 2,040 | Default-off Lite orchestration and existing confirmation projection. |
| `kc-pr-flow/scripts/review-runtime.sh` | 3,307 | 3,387 | Reuse exact identity and typed decision; add one fail-closed receipt-projection operation over the existing append/replay seam. |
| `kc-pr-flow/scripts/review-runtime.test.sh` | 2,884 | 2,960 | Integration rejection and unchanged-default evidence. |
| `kc-pr-flow/scripts/review-post.sh` | unchanged | unchanged | Existing posting owner; zero-line assertion/readback target only. |
| `kc-pr-flow/scripts/review-ablation.sh` | 593 | 673 | Reuse guarded runner; add committed whole-tree Pilot arms and pinned harness fields. |
| `kc-pr-flow/scripts/review-ablation-core.py` | 656 | 736 | Add canonical tracked-tree manifest and exact five-pair Pilot comparison support. |
| `kc-pr-flow/scripts/review-capability-corpus.tsv` | 0 | 7 | Five pre-registered primary plus one designated backup Lite/Lite PR snapshot. |
| `kc-pr-flow/scripts/review-ablation.test.sh` | 894 | 1,114 | Whole-tree arm, provenance, cost-ledger, adjudication, and promotion mutations. |
| `kc-pr-flow/scripts/review-ablation-driver-prompt.md` | 67 | 85 | Byte-identical driver updated to stop after confirmation-request production. |
| `kc-pr-flow/scripts/pr-review-daemon.sh` | unchanged | unchanged | Existing cost-ledger producer; read-only assertion target. |
| `.github/workflows/review-runtime-tests.yml` | 48 | 58 | Add the focused check to the existing owner; no new workflow. |
| `kc-pr-flow/docs/review-runtime.md` | current | current + 20 | Explain external planning while retaining runtime approval authority. |
| `PRODUCT.md` | 109 | 125 | Durable outcome and Pilot measure. |
| `ARCHITECTURE.md` | 269 | 330 | Components, authority, and data flow. |
| `docs/superpowers/specs/2026-09-05-kc-pr-review-capability-protocol-v1.md` | 0 | 950 | Retained accepted contract. |

The mapping is bidirectional: each journey step maps to a row above, and each row
supports a named journey or required documentation/CI obligation. Individual
capability views are generated from the single catalog; creating one tracked
file per question crosses the file stop and returns to shape.

## Implementation stop numbers

Measure from `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`. Stop and report before
continuing when any threshold is crossed:

- more than 20 changed files;
- more than 5,600 total changed lines; or
- more than 1,800 changed lines across the schema, catalog, protocol fixtures, and their
  focused tests.

These bounds were re-derived after adding the previously missing catalog,
runtime documentation, posting assertion target, retained shape file, and
fail-closed receipt-projection operation. They now also count the smallest
recovery of the existing ablation runner instead of a second measurement
harness. The current estimate is at most 20 changed files, 5,269 changed lines
including this retained shape, and 1,582 focused schema/catalog/fixture/test
lines. The file map includes the original 18 paths plus the plugin README and
CLAUDE context. These are ceilings, not targets; without-it review must still
remove unnecessary surfaces.

Edits to this retained shape also consume the total-line ceiling. The 331-line
risk allowance covers runtime/fallback authority repairs (120), launcher and
terminal correlation repairs (90), schema/mutation coverage repairs (80), and
documentation/count repairs (41). The focused estimate plus its 80-line repair
allowance is 1,662, leaving 138 before the unchanged 1,800-line stop. These
allowances do not guarantee sufficiency; a breached stop returns to shape.

Also stop immediately if correctness needs full-catalog evidence before
planning, any executable expansion, a new CI workflow, a new posting owner,
persistent cross-run state, runtime/browser probing, or executable Standard,
Full, or Custom paths. The Captain then chooses reduce scope, reshape with new
thresholds, or promote the profile.

Hosted CI cost per PR is unmeasured. The implementation may add one focused
command to the existing review-runtime workflow, but it must measure its added
wall time before any cost claim or workflow-trigger widening.

## Shape checks

- Current `review-runtime.test.sh`: 372 passed, 0 failed at the pinned base.
- Current `review-post.test.sh`: 156 passed, 0 failed at the pinned base and
  within the 15-minute shape bound.
- Current `review-ablation.test.sh`: 82 passed, 0 failed at the pinned base with
  the repository venv activated.
- `git diff --check` must pass on this document before shape review.
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
  `activation_signals` field or requiring intent-kind evidence in executable
  Lite, bounded invalid-intake echo acceptance only for its two permitted
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
  prose-table/catalog parity.
- Measurement fixtures must prove committed whole-tree arm drift rejection,
  exact five-primary-plus-one-designated-backup corpus enforcement, dual-router
  full-six-mode admission, failure of promotion when any effective primary control sample is
  excluded, exact Lite/mixed/all-four-false control-mode
  enforcement, rejection of a missing or admission-mismatching corroborative
  driver receipt config, retry-source and zero-human-intervention enforcement,
  effort/host/tools/timeout parity, exact
  control-off/treatment-on activation switch enforcement, sealed
  adjudication input, exact Pilot driver-receipt schema, non-Lite treatment
  failure before `oneOf` evaluation, v4
  receipt coverage/terminal and runner-derived treatment
  telemetry, unexplained missing-receipt failure, both quality gates, the 33.3%
  median and three-of-five gates, mechanical no-posting policy, and rejection of
  absent, unparseable, or non-monotonic side-car byte/timing telemetry, plus an
  insufficient or malformed historical cost ledger.
