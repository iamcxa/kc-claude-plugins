# Typed interactive lifecycle — Contract Design

## Design Dispatch Manifest

```yaml
design-dispatch-manifest:
  lanes:
    - lane: domain
      role: generalist-contract-designer
      domain: schema
      panel_lane: domain-intent
      required_skills: []
      knowledge_module_path: plugins/ship-flow/references/domain-knowledge/schema.md
      registry_status: knowledge_module_missing
      routing_resolution: inherited-captain-selected-generalist-marker
      review_contract:
        worktree: <commissioned-worktree>
        mode: artifact-authoring then fresh read-only cross-review
      outputs:
        - transition-and-precedence-table
        - typed-fallback-evidence-contract
        - exact-head-rehydration-and-kill-switch-contract
        - empirical-gate-mapping
        - design-constraints
  integration:
    mode: single-designer
    owner: ship-design
  visual_verification:
    fragment_level: []
    whole_page: []
```

## Design Output

### Routing Resolution and Design Basis

- `lane`: non-UI, single-domain contract lane.
- `domain`: `schema`.
- `registry_status`: `knowledge_module_missing` (validation exit 11).
- `routing_resolution`: inherit the parent captain-selected `generalist-marker`.
- `grounding`: generalist contract analysis only; this artifact does **not** claim schema-specialist review or knowledge-module grounding.
- `decision_state`: parent D1-D7 are fixed; `open_design_questions`, `open_contract_decisions`, parent `open_decisions`, and this child's `open_decisions` are all empty.
- `distillation_method`: `design-flow` is unavailable in the current skill set, so `superpowers:brainstorming` supplied the fallback design discipline. No captain Q-loop was run because the assignment requires projection of already-confirmed D1-D7 rather than alternate product semantics.

### Authority Seam

The smallest new authority is one local, read-only-to-remote boundary between typed replay and the existing interactive confirmation renderer:

```text
validated terminal events.jsonl
  -> exact-identity replay + evidence verification
  -> InteractiveCollationDecision/v1
       {coverage, approve_eligible, effective_event,
        confirmed_blocker_refs, capability_gaps, confirmation_input}
  -> existing mandatory human confirmation
  -> existing posting path (outside typed authority)
```

`InteractiveCollationDecision/v1` is authoritative only for interactive coverage, verdict eligibility/effective-event precedence, and the confirmation input rendered for the current invocation. It does not classify code, choose lanes or providers, merge candidate findings, authorize a review, construct a pending payload, post to GitHub, reconcile a remote result, or grant any daemon capability.

The seam consumes the replay projection already derivable from the D2 event log plus a closed capability policy for the current exact-head review identity. The existing collator remains responsible for candidate/finding synthesis; this child changes the source from transient prose to validated typed terminal state. The existing confirmation UI and posting implementation remain downstream consumers and cannot treat the typed decision as posting authorization.

### Capability Ownership and Terminal-State Model

Before dispatch, the interactive run declares a closed, stably ordered set of capability obligations. Each obligation has exactly one core-owned authority record; provider adapters contribute attempts and evidence but never own lifecycle or verdict policy.

```yaml
schema: kc-pr-flow.capability-terminal/v1
review_identity:
  repository: owner/repo
  pr_number: 42
  base_sha: 40-hex
  head_sha: 40-hex
  config_hash: 64-hex
  review_key: 64-hex
  run_id: unique-run-id
capability: safe-capability-id
required: true
activation_condition: safe-policy-id
owner: core-collator
adapter_attempts:
  - ordinal: 1
    result: succeeded | transient_failure | terminal_failure | unavailable
    lane_result_ref: typed-event-id
fallback:
  status: not_needed | provided | declined | failed | unavailable
  evidence: []
terminal_state: clean | findings | evidence_backed_na | incomplete_required | incomplete_optional
```

Rules:

1. `required` is resolved from capability plus its activation condition, never from provider name, provider installation, or model availability.
2. `clean`, `findings`, and `evidence_backed_na` are satisfied terminal states. Each must resolve to typed terminal evidence from a successful adapter or a valid manual fallback; silence and missing output are not `clean`.
3. A required adapter `transient_failure` requires exactly one retry, so `adapter_attempts` has exactly two entries for that failure path and at most two entries overall. A second transient failure, a terminal failure, or unavailability closes adapter attempts and offers typed manual fallback; no third adapter attempt is valid.
4. A provided fallback is evaluated by the same core capability obligation and candidate/evidence rules as adapter output. The fallback is evidence, not a waiver of requiredness and not permission to approve.
5. A required capability without satisfied typed terminal evidence becomes `incomplete_required`. An optional capability failure becomes `incomplete_optional`, remains visible evidence, and does not independently lower coverage or approval eligibility.
6. The core collator rejects duplicate capability authority records, unknown terminal values, impossible attempt histories, evidence from another review identity, and fallback evidence that does not resolve through D3 pointers.

### Typed Manual-Fallback Evidence Contract

The manual fallback is a closed provider-neutral result, not prose acceptance of risk:

```yaml
schema: kc-pr-flow.manual-capability-result/v1
review_identity:
  repository: owner/repo
  pr_number: 42
  base_sha: 40-hex
  head_sha: 40-hex
  config_hash: 64-hex
  review_key: 64-hex
  run_id: unique-run-id
capability: safe-capability-id
terminal_assessment: clean | findings | evidence_backed_na
candidate_ids: []
evidence_pointer_ids: [typed-pointer-id]
recorded_by: interactive-human
recorded_at: UTC-RFC3339
```

- `evidence_pointer_ids` is non-empty for every assessment. `findings` additionally has non-empty `candidate_ids`; `clean` and `evidence_backed_na` cite the command, test, exact repository object, or other typed source that makes that conclusion evidence-backed.
- Every referenced candidate and pointer must equal the containing repository, PR, base, head, configuration, review key, and run identity. Rehydrated content must pass the existing pointer kind/object/content-hash checks before fallback can satisfy a required capability.
- The record stores identifiers, pointers, hashes, constrained enums, and timestamps only. It cannot persist a full diff, prompt, evidence excerpt, review body, comment text, rationale, or raw provider output.
- `declined`, `failed`, or `unavailable` fallback status carries a typed reason but no synthetic clean result; for a required capability it terminates as `incomplete_required`.
- A manual fallback cannot change capability requiredness, erase adapter failure evidence, suppress a confirmed blocker, select a GitHub event directly, or authorize posting.

### Interactive Decision and Verdict Precedence

The typed decision projection is closed over the current identity and records:

```yaml
schema: kc-pr-flow.interactive-collation-decision/v1
review_identity: {repository, pr_number, base_sha, head_sha, config_hash, review_key, run_id}
mode: typed
coverage: complete | incomplete
approve_eligible: true | false
effective_event: APPROVE | COMMENT | REQUEST_CHANGES
capabilities: [capability-terminal/v1]
confirmed_blocker_refs: []
capability_gap_refs: []
confirmation_input:
  identity_summary: typed-derived
  coverage_summary: typed-derived
  verdict_summary: typed-derived
  blocker_refs: []
  gap_refs: []
```

`confirmation_input` is derived from the same decision object as `coverage`, `approve_eligible`, and `effective_event`; it is not independently reconstructed from prose. Existing non-coverage event modifiers may contribute typed inputs, but the precedence below is immutable: confirmed blockers outrank gaps, and gaps outrank approval eligibility.

| State / transition | Preconditions | Typed authority result | Effective event and confirmation | Legacy / fallback behavior |
|---|---|---|---|---|
| Legacy selected pre-run | Kill switch is not exactly enabled when a fresh invocation samples mode, before typed dispatch begins | No typed interactive decision is started | Existing legacy derivation reaches mandatory human confirmation | Valid fail-safe selection for this fresh run; no typed runtime call is required |
| Typed valid and complete | Mode was selected pre-run; exact review identity validates; every required capability has satisfied terminal evidence | `coverage=complete`; `approve_eligible=true` unless another existing typed event modifier forbids it | Derive the effective event and confirmation input from typed state; human confirmation remains mandatory | No in-run legacy derivation |
| Typed manual fallback completes coverage | Required transient adapter work received its one required retry (or non-transient work terminated without retry) and valid fallback evidence satisfies every remaining obligation | Same as typed valid and complete; adapter failures remain visible evidence | Typed effective event reaches mandatory human confirmation | Manual fallback is typed evidence, not a legacy-mode switch |
| Typed incomplete after retry/fallback | At least one required capability remains unsatisfied after one retry where eligible and the fallback opportunity | `coverage=incomplete`; `approve_eligible=false`; explicit capability gaps | `COMMENT`, unless the confirmed-blocker row applies; confirmation explicitly names incomplete coverage | No silent fall-through to legacy approval; a legacy rerun requires a fresh explicit invocation |
| Typed confirmed blockers | One or more evidence-bound confirmed blockers exist, whether coverage is complete or incomplete | `approve_eligible=false`; blocker refs retained; gaps remain visible when present | `REQUEST_CHANGES` takes precedence over the incomplete-coverage COMMENT ceiling; mandatory human confirmation still applies | Neither fallback nor gaps may dilute the blocker verdict |
| Typed invalid or exact-identity/head mismatch | Replay, schema, hash, evidence, repository/PR/base/head/config/review-key/run binding, or current-head validation fails after typed execution has begun | Typed attempt ends fail-closed as invalid/incomplete; no accepted decision may claim complete coverage | Explicit `COMMENT` gap unless already-confirmed exact-identity blocker evidence independently supports `REQUEST_CHANGES`; never APPROVE | No in-run legacy fallback; operator may disable typed mode only for a fresh rerun |
| Kill switch changed during typed execution | Typed mode was already sampled and dispatch/rehydration began | Current run remains typed and D5-governed | Current typed decision follows blocker/gap precedence and confirmation | Switch affects only a later fresh run |
| Typed disabled after a failed run | Prior typed run is terminal invalid or incomplete; operator explicitly selects legacy for a new invocation | New run gets its own legacy execution identity; prior typed evidence remains inspectable but non-authoritative for the new run | Legacy path still reaches mandatory human confirmation | This is a new run, never continuation, repair, or silent fallback of the failed typed run |

### Exact-Identity Rehydration Contract

The interactive rehydration operation accepts only one already-terminal, replay-valid receipt and the caller's freshly observed identity. All of these fields must match before any replayed value can govern the collator:

- normalized repository identity and PR number;
- exact base SHA and current head SHA;
- effective configuration hash and derived `review_key`;
- selected terminal `run_id` with a complete lifecycle;
- every capability task/result identity, candidate/finding identity, and D3 evidence pointer/object/content hash.

The only permitted output is a new in-memory `InteractiveCollationDecision/v1` containing capability coverage, verdict eligibility/effective-event precedence, blocker/gap references, and confirmation input. The operation may use the existing safe snapshot, `replay`, `observe`, and `verify-evidence` primitives; it must not append to or repair the receipt.

This rehydration contract explicitly does **not**:

- resume an incomplete run or lane;
- reuse or continue an interrupted `run_id`;
- append recovery events or establish predecessor lineage;
- recover a lock or process identity;
- create authorization, posting intent, a pending payload, an idempotency key, or a remote marker;
- post, reconcile, retry, or otherwise mutate GitHub;
- implement retention, garbage collection, compaction, or any other 2.3 recovery behavior.

Missing terminal state, invalid evidence, unsafe input, or any identity mismatch produces a typed in-run failure subject to the precedence table. It never selects legacy behavior for the current run.

### Empirical Gate Mapping

G0 remains a prerequisite: the merged 2.1 authority-bound receipt/runtime/benchmark evidence must stay green before typed authority can activate.

| Gate | Design intent | Plan-verifiable evidence and threshold | Failure behavior |
|---|---|---|---|
| G1 — Exact head | Only one exact repository/PR/base/head/config/review-key/run identity can govern an interactive decision | Positive and negative fixtures prove terminal receipt acceptance for an exact match and typed rejection for each moved-head, base, repository, PR, configuration, review-key, run, event, candidate, finding, pointer, object, and content-hash mismatch | End current typed attempt at COMMENT ceiling unless confirmed blockers require REQUEST_CHANGES; no in-run legacy approval |
| G2 — Coverage/verdict safety | Capability requiredness, retry budget, fallback evidence, gap ceiling, and blocker precedence are core-owned | Table-driven tests cover required adapter success, one transient retry, forbidden third attempt, valid and invalid manual fallback, optional failure, incomplete required coverage, and simultaneous gap plus blocker. No required gap may emit APPROVE; blocker plus gap must emit REQUEST_CHANGES | Block typed-default promotion |
| G3 — Human/rollback parity | Mode is sampled once before execution; both modes retain confirmation; typed failure cannot switch modes | Off/unset/unknown switch fixtures prove no typed call; enabled fixtures prove typed derivation; mid-run switch changes are ignored; every terminal branch reaches the same mandatory confirmation gate; posting call log stays empty before confirmation | Keep typed disabled for later fresh runs; current typed run remains D5-governed |
| G4 — Recall first | Safety and efficiency cannot compensate for lost must-fix findings | On the sanitized authority-bound fixed-head corpus, every expected must-fix finding recovered by legacy is also recovered by typed state. The gate is non-inferior only when the lost expected must-fix count is zero | Stop evaluation; G5 is not considered and typed default remains off |
| G5 — Efficiency second | Accept either trustworthy token reduction or bounded terminal-receipt local reconstruction, never a mixed or inferred claim | After G4 passes: **branch A** requires paired same-provider-family, same-scope, complete `reported` usage and at least 20% median total-token reduction; estimated, unavailable, null, cross-provider, or cross-scope values are ineligible. **Branch B** requires a fresh invocation to safe-snapshot, replay, exact-identity/evidence-validate, and reconstruct only terminal-receipt collator coverage/verdict/confirmation input at median measured local cost no greater than 60% of the paired full-review-rerun cost. Branch B makes no token claim and performs no model/provider or remote call | If neither branch passes, make no efficiency claim and retain legacy as the default |

Gate ordering is executable policy: G1-G3 must pass for safety, G4 must pass before G5 is evaluated, and a G5 result cannot repair a G1-G4 failure.

### Captain Decisions

- **D1|Captain decision**: Preserve the parent's stable exact-head `review_key` and unique `run_id` semantics. This child may read one complete terminal run for the same identity but does not resume interrupted work, create successor lineage, or implement retention and recovery. (source: parent design D1; child shape G1 and 2.3 boundary)
- **D2|Captain decision**: Keep valid append-only JSONL events as typed run authority and replay as the only receipt projection authority. This child gives only the validated interactive decision projection authority over coverage, verdict eligibility/effective-event precedence, and confirmation input; the log is not posting authority. (source: parent design D2; `ARCHITECTURE.md` authority boundaries)
- **D3|Captain decision**: Preserve evidence-bound candidate/finding identity and require every adapter or manual-fallback pointer to bind the same review/base/head identity and verified content hash, without durable excerpts or raw provider output. (source: parent design D3; `ARCHITECTURE.md` finding and evidence identity)
- **D4|Captain decision**: Preserve provider-neutral capability records and usage provenance. Adapters cannot own lifecycle or verdict, missing usage remains unknown, and only comparable same-provider/scope `reported` observations enter G5 branch A. (source: parent design D4; `PRODUCT.md` success measures)
- **D5|Captain decision**: Define requiredness by capability, require typed terminal adapter or explicit manual-fallback evidence, retry a required transient failure once, forbid APPROVE for unresolved required coverage, emit an explicit COMMENT gap, preserve REQUEST_CHANGES for confirmed blockers, and keep optional-provider failures as evidence only. (source: parent design D5; `ARCHITECTURE.md` coverage and failure policy)
- **D6|Captain decision**: Preserve the posting boundary: the typed interactive decision reaches mandatory human confirmation but cannot authorize or perform GitHub mutation, create pending payload/idempotency/remote-marker state, reconcile ambiguity, or grant daemon APPROVE. (source: parent design D6; child PR boundary)
- **D7|Captain decision**: Reject unsupported, invalid, incomplete, or identity-mismatched state from interactive authority. Once typed execution begins, such failure is typed and D5-governed; it cannot reduce to an unconstrained legacy approval or mutate accepted/remote state. (source: parent design D7; child G1/G3)

### Artifact Bundle Manifest

| Path | Type | Purpose |
|---|---|---|
| `docs/ship-flow/2.2-typed-interactive-lifecycle/design.md` | Non-UI contract design | Child-local typed authority, transition precedence, fallback evidence, rehydration boundary, empirical gates, and plan hand-off |
| `docs/ship-flow/2-agent-native-pr-review-runtime/design.md` | Inherited contract source | Canonical parent D1-D7 and PR1/PR2/PR3 ownership |
| `docs/ship-flow/_archive/2.1-shadow-review-receipt/verify.md` | Dependency evidence | Verified terminal receipt, exact-head, evidence, usage, and benchmark foundation |

### Canonical Context

| Doc | Sections read | Design-stage intent | Current edit |
|---|---|---|---|
| `PRODUCT.md` | Outcome, target capabilities, success measures, delivery boundary, current increment, non-goals | Preserve recall-first evaluation, human control, provider-reported usage rules, and the three reversible increments | None; this artifact projects the existing product contract |
| `ARCHITECTURE.md` | Decision record, authority boundaries, run/event identity, finding/evidence identity, coverage/failure policy, increment boundaries | Bound the new interactive authority to D5 collation and exact-head rehydration without crossing D6 or 2.3 ownership | None; this artifact projects the existing architecture contract |
| `kc-pr-flow/skills/kc-pr-review/SKILL.md` | Typed shadow ledger, collation, pass coverage, shadow seam, confirmation gate | Reuse the existing post-collation/pre-confirmation seam and typed ledger rather than redesign dispatch, synthesis, prompts, or posting | None in design stage |
| `kc-pr-flow/scripts/review-runtime.sh` and runtime verification corpus | Replay, observe, evidence verification, usage comparison, paired scoring | Extend from shipped read-only primitives; do not duplicate receipt authority or recovery behavior | None in design stage |

## Schema Design Output

This is a generalist-marker schema intent projection for later `## Intent Match Findings`; it is not a specialist certification.

### Authority layers touched

- Accepted event layer: unchanged D2 JSONL authority and closed schemas.
- Replay layer: terminal receipt projection plus exact-identity/evidence validation.
- Interactive decision layer: new closed capability terminal/fallback/decision projections.
- Confirmation layer: existing mandatory human gate consumes typed confirmation input.
- Remote side-effect layer: untouched and outside this child.

### Persistence evolution safety

- Change shape: additive closed schemas and additive runtime commands or library functions.
- Existing accepted receipts: never rewritten, backfilled, repaired, or reinterpreted beyond their declared schema major.
- Durable content: typed identifiers, enums, pointers, hashes, counts, and timestamps only; no raw review content.

### Ownership and isolation

- State remains machine-local under the configured XDG root and bound to normalized repository/PR/exact-head/config/run identity.
- No shared service, tenant table, role policy, or remote authorization surface is introduced.
- Provider adapters supply results; the core collator owns capability requiredness, terminal-state validation, precedence, and decision projection.

### Projection rebuild

- Rebuild source: exactly one replay-valid terminal event log.
- Rebuild output: in-memory `InteractiveCollationDecision/v1` only.
- Stale-read tolerance: none for interactive authority; any current-head or identity mismatch is a typed failure.
- Recovery behavior: none; incomplete or unsafe receipts are rejected, not repaired.

### Intent anchors for later verification

| Intent ID | Required comparison |
|---|---|
| I1 | The implementation's authority surface stops at typed coverage, event precedence, and confirmation input. |
| I2 | Capability requiredness and terminal states match the closed ownership model, including exactly one retry after a required transient failure and no third attempt. |
| I3 | Manual fallback is evidence-backed and cannot act as a waiver, blocker suppressor, or posting authorization. |
| I4 | REQUEST_CHANGES outranks COMMENT gaps; COMMENT gaps make APPROVE impossible. |
| I5 | Exact-identity terminal rehydration reconstructs only collator input and implements none of the forbidden recovery/remote behaviors. |
| I6 | Mode is selected pre-run; in-run typed failure cannot silently invoke legacy approval. |
| I7 | G1-G5 are evaluated in order, with G4 recall first and exactly the two permitted G5 branches. |

### Hand-off constraints for Plan

- Turn each `design_constraints[]` item below into a falsifiable Done Criterion with positive and negative fixtures.
- Preserve the three-day child boundary and use the existing Bash 3.2 + `jq` runtime and Python 3.8+ safe-I/O helper only where already required.
- Keep implementation additive and interactive-only; do not couple this child to 2.3 or reviewer/prompt changes.
- Later verify must emit `## Intent Match Findings` against I1-I7 and G1-G5.

## Design Readiness Review

Design Readiness Review: skipped - no risk trigger

Exact skip rationale: this is one non-UI local contract lane with no multi-domain, destructive persistence, network-contract, authorization, tenancy, or visual risk trigger; no recent matching debrief or captain-explicit readiness mod was supplied. The required fresh adversarial non-UI cross-review remains the design-stage gate.

### Hand-off to Plan
<!-- section:hand-off-to-plan -->

```yaml
design-skipped: false
design_constraints:
  - type: data-contract
    assertion: "Interactive authority accepts exactly one complete replay-valid terminal run bound to repository, PR, base SHA, current head SHA, configuration hash, review_key, and run_id; it does not resume, repair, retain, collect, or create successors."
    rationale_decision: D1
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: schema-contract
    assertion: "Valid append-only JSONL remains typed run authority and replay remains receipt projection authority; InteractiveCollationDecision/v1 is a closed derived projection authoritative only for coverage, approve eligibility/effective-event precedence, and confirmation input, never posting."
    rationale_decision: D2
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: data-contract
    assertion: "Every adapter or manual-fallback candidate and evidence pointer equals the containing repository/PR/base/head/config/review-key/run identity and passes object/content-hash rehydration; durable state stores no diff, prompt, excerpt, rationale, review text, or raw provider output."
    rationale_decision: D3
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: contract
    assertion: "Capability obligations and terminal records are provider-neutral and core-owned; adapters cannot own requiredness, lifecycle, verdict, authorization, or posting; usage remains reported, estimated, or unavailable with missing values null."
    rationale_decision: D4
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: domain-contract
    assertion: "Each capability has one authority record and terminates as clean, findings, evidence_backed_na, incomplete_required, or incomplete_optional; satisfied states require typed evidence, silence is never clean, and optional failures remain visible without independently blocking completion."
    rationale_decision: D5
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: contract
    assertion: "A required transient adapter failure requires exactly one retry and no third attempt; remaining required work gets one typed manual-fallback opportunity whose evidence satisfies the same capability and D3 identity rules rather than waiving coverage."
    rationale_decision: D5
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: contract
    assertion: "Any incomplete required capability sets coverage=incomplete and approve_eligible=false with an explicit COMMENT ceiling, while any evidence-bound confirmed blocker selects REQUEST_CHANGES even when coverage is incomplete."
    rationale_decision: D5
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: contract
    assertion: "Both typed and legacy fresh-run paths retain mandatory human confirmation; the typed decision cannot authorize or execute GitHub mutation or create pending payload, idempotency, remote-marker, reconciliation, or daemon state."
    rationale_decision: D6
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: schema-contract
    assertion: "Unsupported, invalid, incomplete, unsafe, or exact-identity-mismatched typed state cannot govern approval; after typed execution begins it ends as a typed D5-governed gap and cannot silently fall through to legacy approval or mutate accepted/remote state."
    rationale_decision: D7
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: contract
    assertion: "The kill switch is sampled once before dispatch: off, unset, or unknown selects legacy only for that fresh run; enabled starts typed execution; later switch changes affect only a new invocation."
    rationale_decision: D7
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: data-contract
    assertion: "Exact-head rehydration reads one terminal receipt and reconstructs only collator coverage, verdict eligibility/effective-event precedence, blocker/gap refs, and confirmation input; it performs no incomplete-run/lane resume, lock/process recovery, event append, predecessor work, posting, pending-payload, remote-marker, reconciliation, idempotency, retention, or compaction behavior."
    rationale_decision: D1
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: data-contract
    assertion: "Promotion gates execute in order: G1 exact identity, G2 coverage/verdict safety, G3 human/rollback parity, G4 non-inferior must-fix recall with zero lost expected must-fix findings, then G5 efficiency; no later gate repairs an earlier failure."
    rationale_decision: D5
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
  - type: data-contract
    assertion: "G5 passes only through either at least 20% median total-token reduction from complete same-provider-family same-scope reported pairs, or terminal-receipt-only local collator rehydration at median measured cost no greater than 60% of a paired full-review rerun; the second branch makes no token claim and neither branch admits estimated, unavailable, null, cross-provider, or cross-scope usage."
    rationale_decision: D4
    source_artifact: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
open_decisions: []
artifact_paths:
  - path: docs/ship-flow/2.2-typed-interactive-lifecycle/design.md
render_fidelity_targets: []
```

<!-- /section:hand-off-to-plan -->

## Design Report

status: passed
stage_cost: not metered (single generalist-marker contract worker plus one required fresh read-only adversarial cross-review)
iterations: 0 captain loops; 1 fresh cross-review pass
contradictions_resolved: 0 new; inherited D1-D7 project all fixed semantics
captain_decisions: 7 inherited
reviewer_verdict: PROCEED
design_readiness_review: skipped - no risk trigger

### Adversarial Cross-review

- `verdict`: `PROCEED`.
- `seven_factor_rubric`: 7/7 PASS — feasibility, executable scope, quality, DC adequacy, canonical sync, reverse-audit previous stage, and Constraint Coverage.
- `constraint_audit`: C1-C13 PASS; 13 constraints carry 13 valid D back-references and collectively represent D1-D7.
- `reverse_audit`: shape has no open design or contract decision; no UI/theme target applies; all seven inherited decisions are represented; transition precedence, typed fallback, exact-head/kill-switch, PR boundary, and G1-G5 are present.
- `non_blocking_caveat`: the manifest names the expected schema knowledge-module path while recording `knowledge_module_missing`. Retained because it is the authoritative registry receipt and every routing section explicitly says generalist-marker/no specialist claim.
- `coaching_note`: Preserve the exact D-to-constraint trace and terminal-receipt-only boundary in plan so resolved design intent cannot become execute-stage ambiguity.

### Metrics

status: passed
duration_minutes: 15
iteration_count: 1
captain_decisions_count: 7
reviewer_verdict: PROCEED

### Notes

- The registry resolution is explicitly generalist-marker; no schema-specialist grounding is claimed.
- This artifact emits no UI, render-fidelity, or whole-page visual target.
- `design-flow` was unavailable; the fallback method distilled already-confirmed decisions and did not reopen them.

## Stage Report: design

- DONE: Define the smallest typed authority seam that can replace legacy coverage/verdict derivation without taking posting authority.
  `InteractiveCollationDecision/v1` owns only typed coverage, event precedence, and confirmation input before mandatory human confirmation; all remote authority stays outside the seam.
- DONE: Specify capability-based requiredness, one retry, typed manual fallback, and the incomplete-coverage COMMENT ceiling; confirmed blockers may still request changes.
  The capability terminal model, fallback schema, and precedence table make a third attempt invalid, COMMENT fail-closed, and REQUEST_CHANGES dominant.
- DONE: Bind typed rehydration to the exact reviewed head and make legacy fallback/kill-switch behavior explicit and fail-safe.
  Rehydration requires the full exact review identity and terminal receipt; mode is sampled pre-run and typed failure cannot switch to legacy in-run.
- DONE: Convert every contract choice into plan-verifiable constraints and preserve the empirical gates: non-inferior recall first; only comparable reported usage may support efficiency.
  Thirteen typed constraints cover D1-D7 and G1-G5, including the 20% reported-token and 60% terminal-receipt local-rehydration branches.

### Summary

This design projects the inherited parent contract into one interactive-only typed authority seam and leaves plan no coverage, precedence, fallback, rehydration, rollout, or PR-boundary semantic choice. The single fresh adversarial cross-review passed all seven factors and all 13 constraints; final metrics are recorded above.
