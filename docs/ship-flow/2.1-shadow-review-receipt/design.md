# Shadow review receipt — Design Projection

## Design Source

This child implements the first reversible increment of the parent contract. The parent decisions remain canonical; this projection narrows them to the shadow boundary for independent planning and delivery.

## Child Contract

- **D1|Captain decision**: Inherit the parent exact-head run identity and successor semantics; PR1 implements fresh identity records but not resume or garbage collection.
- **D2|Captain decision**: Inherit the parent JSONL authority boundary; PR1 typed records are authoritative only for shadow state while legacy verdict, confirmation, and posting remain authoritative.
- **D3|Captain decision**: Inherit the parent candidate, merged-finding, and evidence-pointer identity without retaining excerpts or raw provider output.
- **D4|Captain decision**: Inherit the parent provider-neutral envelopes and typed usage provenance, including null rather than zero for unavailable usage.
- **D7|Captain decision**: Inherit the parent supported-version tolerance and read-only quarantine boundary.

- Implement D1 run identity without resume or garbage-collection behavior.
- Implement D2 append-only typed events, validation, and replay projections while the legacy flow remains the sole behavioral authority.
- Implement D3 candidate, finding, and evidence-pointer identity without storing source excerpts or raw provider output.
- Implement D4 provider-neutral task, result, and usage envelopes without moving lifecycle authority into adapters.
- Implement D7 read-only quarantine and safe metadata display for unsupported or invalid state.
- Observe one existing interactive review after classification. Do not dispatch a second review or change verdict, confirmation, review body, inline comments, or GitHub event.
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
    assertion: "Versioned append-only JSONL events are authoritative only for typed review-run records; projections are replayable caches, duplicate event IDs are no-ops, and the legacy flow remains authoritative for verdict, confirmation, and posting."
    rationale_decision: D2
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: data-contract
    assertion: "Provider candidates and merged finding identities bind exact-head evidence pointers and hashes; uncertain matches remain separate and durable state contains no source excerpts or raw provider output."
    rationale_decision: D3
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: contract
    assertion: "Core ReviewTask and LaneResult envelopes are provider-neutral; adapters cannot own lifecycle, verdict, authorization, or posting, and usage provenance preserves null for unavailable values."
    rationale_decision: D4
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: schema-contract
    assertion: "Unsupported majors, unknown event types, required-field failures, and hash mismatches are read-only quarantined and cannot reduce or mutate state; supported-v1 unknown optional fields retain original event bytes."
    rationale_decision: D7
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: contract
    assertion: "Shadow integration dispatches no additional review and leaves verdict, confirmation, review body, inline comments, and GitHub event unchanged."
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
