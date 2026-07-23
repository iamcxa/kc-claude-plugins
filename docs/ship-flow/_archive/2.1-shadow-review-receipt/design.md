# Shadow review receipt — Design Projection

## Design Source

This child implements the first reversible increment of the parent contract. The parent decisions remain canonical; this projection narrows them to the shadow boundary for independent planning and delivery.

## Verify-return rationale

Verify demonstrated that the original projection could report an identity-only run as observed, accept arbitrary raw data through additive v1 fields, preserve rejected input bytes in quarantine, and validate evidence that was not bound to the reviewed base/head pair. The parent contract now selects a closed known envelope, typed hash-only extensions, metadata-only quarantine, exact-head evidence/finding identity, and complete-terminal observation. This child imports those repairs without gaining any behavioral authority.

## Child Contract

- **D1|Captain decision**: Inherit the parent exact-head run identity and successor semantics; PR1 implements fresh identity records but not resume or garbage collection.
- **D2|Captain decision**: Inherit the parent JSONL authority boundary, closed v1 top-level envelope, typed hash-only extension slot, sanitized collector input, and complete-terminal observation rule; PR1 typed records are authoritative only for shadow state while legacy verdict, confirmation, and posting remain authoritative.
- **D3|Captain decision**: Inherit the parent candidate and merged-finding identity with evidence-content hashes, and bind evidence pointers to the exact review key/base/head pair without retaining excerpts or raw provider output.
- **D4|Captain decision**: Inherit the parent provider-neutral envelopes and typed usage provenance, including null rather than zero for unavailable usage.
- **D7|Captain decision**: Inherit the parent closed-envelope rejection rule and metadata-only quarantine boundary; rejected input bytes are never retained.

- Implement D1 run identity without resume or garbage-collection behavior.
- Implement D2 append-only typed events, closed-envelope validation, hash-only extensions, replay projections, and a sanitized collector whose `observed` result requires a complete terminal receipt, while the legacy flow remains the sole behavioral authority.
- Implement D3 candidate, finding, and evidence-pointer identity with evidence-content hashes and exact review-key/base/head/object binding (`LEFT` to base; `RIGHT` and `FILE` to head), without storing source excerpts or raw provider output.
- Implement D4 provider-neutral task, result, and usage envelopes without moving lifecycle authority into adapters.
- Implement D7 metadata-only quarantine and safe metadata display for unsupported or invalid state; never persist or link to rejected bytes.
- Observe one existing interactive review after classification through one closed `ShadowObservation/v1` projection. Do not dispatch a second review or change verdict, confirmation, review body, inline comments, options, GitHub event, confirmation input, or mocked/real GitHub mutation.
- Use the parent's exact closed `ShadowObservation/v1` key/type schema and translate every declared lane through `lane.started`, ordered candidate events, and `lane.finished`, followed by `synthesis.finished` and `run.finished`. Report `observed` only after replay proves that complete lifecycle; identity-only or incomplete telemetry is `not_observed` with a typed reason and remains fail-open to the legacy flow.
- Establish deterministic fixtures and a paired-run corpus. Do not claim token improvement from this increment.

### Hand-off to Plan
<!-- section:hand-off-to-plan -->

```yaml
design-skipped: false
design_constraints:
  - type: data-contract
    assertion: "A stable exact-head review_key groups unique runs; PR1 creates fresh run IDs and typed successor metadata but does not implement resume or garbage collection."
    rationale_decision: D1
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: schema-contract
    assertion: "Versioned append-only JSONL events are authoritative only for typed review-run records; projections are replayable caches, duplicate event IDs are no-ops, the v1 top-level envelope is closed, and same-major evolution is limited to typed hash-only extensions with no arbitrary values or semantic authority; the legacy flow remains authoritative for verdict, confirmation, and posting."
    rationale_decision: D2
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: data-contract
    assertion: "Provider candidate and merged-finding identities include evidence-content hashes; each nested evidence pointer equals the containing event review_key/base_sha/head_sha, and git_blob object_sha binds LEFT to base_sha and RIGHT or FILE to head_sha; uncertain matches remain separate and durable state contains no source excerpts or raw provider output."
    rationale_decision: D3
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: contract
    assertion: "Core ReviewTask and LaneResult envelopes are provider-neutral; adapters cannot own lifecycle, verdict, authorization, or posting, and usage provenance preserves null for unavailable values."
    rationale_decision: D4
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: schema-contract
    assertion: "Unknown top-level fields, unsupported majors, unknown event types, required-field failures, and hash mismatches are excluded from accepted state and cannot reduce or mutate state; quarantine stores exactly reason code, rejected-input SHA-256, byte count, and timestamp, never rejected bytes."
    rationale_decision: D7
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: contract
    assertion: "Shadow integration dispatches no additional review and leaves verdict, confirmation, review body, inline comments, options, GitHub event, confirmation input, and GitHub mutation unchanged; production parity tests invoke the same sanitized collector boundary."
    rationale_decision: D2
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: data-contract
    assertion: "The shadow seam accepts the exact closed ShadowObservation/v1 schema from the parent; every declared lane maps to lane.started, ordered candidate events, and lane.finished, followed by synthesis.finished and run.finished; observed requires that complete replay-valid lifecycle, while identity-only or incomplete receipts are not_observed with a typed reason."
    rationale_decision: D2
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: contract
    assertion: "Runtime snapshots use a no-follow stable regular-file open, integers stay jq-safe, batch status cannot downgrade blocked work, benchmark findings bind canonical candidates/evidence and receipt content, and PRODUCT/ARCHITECTURE/plugin docs are synchronized before verify reruns."
    rationale_decision: D2
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
open_decisions: []
artifact_paths:
  - path: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - path: docs/ship-flow/2.1-shadow-review-receipt/design.md
render_fidelity_targets: []
```

<!-- /section:hand-off-to-plan -->

## Design Report

- status: passed
- parent_decisions_imported: D1, D2, D3, D4, D7
- child_open_decisions: 0
- behavioral_authority_change: none

## Design Readiness Review

Design Readiness Review: skipped - no risk trigger
