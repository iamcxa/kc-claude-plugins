# Agent-native PR review runtime — Contract Design

## Design Dispatch Manifest

```yaml
design-dispatch-manifest:
  lanes:
    - lane: contract-interface
      role: contract/interface-designer
      trigger: open_contract_decisions
      decisions: [D1, D2, D3, D4, D5, D6, D7]
      required_skills: []
      adopter_routing:
        status: generalist-only
        domain: schema
        knowledge_module_status: missing
      outputs: [captain_decisions, design_constraints]
  integration:
    mode: single-designer
    owner: ship-design
  visual_verification:
    fragment_level: []
    whole_page: []
```

## Design Output

### Router HALT Resolution

- `domain`: `schema`
- `registry_status`: `knowledge_module_missing`
- `options_presented`: `skip`, `generalist-marker`, `file-specialist-first`
- `captain_selection`: `generalist-marker`
- `captain_selection_date`: `2026-07-22`
- `effect`: Proceed through contract design with an explicit generalist-only marker; do not claim schema-specialist grounding.

### Captain Decisions

- **D1|Captain decision**: Use a stable exact-head `review_key` plus a unique `run_id`; resume only compatible interrupted runs, model reruns and head/config changes as explicit successors, retain terminal receipts for 30 days, retain failed pending payloads for 24 hours, and never garbage-collect active or remotely uncertain runs. (ref: `shape.md:202`)
- **D2|Captain decision**: Make versioned append-only `events.jsonl` the sole authority for typed review-run records, derive receipts by replay, canonicalize and hash every payload, treat duplicate event IDs as no-ops, permit only additive optional fields within v1, and require a new major schema for breaking semantics. Until PR2, the legacy flow remains behavioral authority for verdict, confirmation, and posting. (ref: `shape.md:202`)
- **D3|Captain decision**: Preserve every provider observation as a candidate, derive merged finding identity from exact-head review key, path, side, evidence-content hash, category, and constrained claim key, keep uncertain matches separate, and persist only typed evidence pointers and hashes rather than excerpts or raw model output. (ref: `shape.md:203`)
- **D4|Captain decision**: Keep the core provider-neutral through narrow versioned task/result envelopes, isolate provider-specific behavior in adapters, record usage as `reported`, `estimated`, or `unavailable` without coercing missing values to zero, and admit only comparable within-provider reported usage to efficiency gates. (ref: `shape.md:204`)
- **D5|Captain decision**: Define requiredness by review capability rather than provider name, require typed terminal coverage with evidence from either an adapter or explicit manual fallback, retry required transient failures once, forbid APPROVE when required coverage remains incomplete, default such runs to an explicit COMMENT gap, preserve REQUEST_CHANGES for confirmed blockers, and keep optional-provider failures as evidence only. (ref: `shape.md:205`)
- **D6|Captain decision**: Bind authorization to the canonical exact-head payload hash and effective event, default daemon posting to deny with no daemon APPROVE in v1, write a restrictive pending payload before mutation, derive a deterministic idempotency key, reconcile ambiguous outcomes against a remote hidden marker before retry, and treat the remote GitHub review ID as mutation authority while retaining its local receipt. (ref: `shape.md:206`)
- **D7|Captain decision**: Ignore unknown optional fields only within a supported major version, quarantine unknown event types, invalid hashes, missing required fields, and unknown majors from reduction or mutation, preserve their bytes for inspection, and allow only metadata display plus an upgrade or legacy-fallback instruction. (ref: `shape.md:207`)

### Contract Details

#### D1 — Run identity and lifecycle retention

```text
review_key = sha256(repo_identity | pr_number | base_sha | head_sha | config_hash)
run_id     = unique identifier for one fresh execution
```

- A compatible crash resume retains `run_id`.
- Manual rerun, config change, appended head, rewritten head, or recovery fork creates a successor run with a typed reason.
- Cross-head finding IDs are never reused; append successors may reference predecessors only after evidence revalidation against the new exact head.
- GC is dry-run by default and requires explicit `gc --apply`.

#### D2 — Event authority and schema evolution

Authoritative path:

```text
<state-root>/<repo-key>/pr-<number>/<run-id>/events.jsonl
```

Minimum envelope:

```yaml
schema: kc-pr-flow.review-event/v1
event_id: sha256(run_id|sequence|event_type|payload_sha256)
run_id: string
review_key: sha256
sequence: integer
occurred_at: RFC3339
event_type: enum
payload: object
payload_sha256: sha256
```

Minimum event vocabulary:

```text
run.started
head.observed
lane.started
lane.finished
finding.observed
synthesis.finished
authorization.granted
post.intent
post.result
run.invalidated
run.finished
```

`events.jsonl` is authoritative only for typed review-run records; `receipt.json` and CLI output are rebuildable projections. In PR1, the existing prose flow remains behavioral authority for verdict, confirmation, and posting. Payloads are canonicalized with `jq -S -c` before hashing. Invalid events are rejected before append; a repeated `event_id` is a no-op.

#### D3 — Finding and evidence identity

```text
candidate_id = sha256(run_id | lane_id | ordinal | evidence_hash)
merge_key    = path | side | anchor_sha256 | category | claim_key
finding_id   = sha256(review_key | merge_key)
```

Providers produce candidates; the collator produces constrained `claim_key` and merge decisions. Uncertain matches remain separate.

Evidence pointers use a typed union: `git_blob | pr_body | issue | review_comment | command | test`. Source pointers include exact head/blob, repo-relative path, side, line range, locator when applicable, content hash, and typed result. Rehydration fetches the source and validates its hash; durable state stores no excerpt.

#### D4 — Provider and usage boundary

Core accepts `ReviewTask/v1` and `LaneResult/v1`. Adapters cannot choose the GitHub event, post to GitHub, write core lifecycle state, treat silence as clean, or persist provider-specific raw output.

Usage fields carry `provenance: reported | estimated | unavailable` and `scope: lane | run`. Missing values remain `null`, never zero. Efficiency gates compare only paired observations with the same provider family, measurement scope, and `reported` provenance.

#### D5 — Coverage and failure policy

Requiredness is defined by capability and activation condition, not installed provider name. Every owned capability terminates as `clean`, `findings`, or evidence-backed `na`.

- Required transient failure retries once.
- Provider unavailability routes to a typed per-capability manual fallback.
- Remaining required gaps set `coverage=incomplete` and `approve_eligible=false`, with an explicit COMMENT ceiling.
- Confirmed blockers may still yield REQUEST_CHANGES; incomplete coverage cannot dilute a blocking verdict.
- Optional provider failures remain evidence only.
- PR1 reports this policy in shadow state but does not enforce it; PR2 owns enforcement.

#### D6 — Authorization and remote mutation

Authorization binds repository, PR number, exact head, effective event, policy version, and canonical payload hash. Self-review event downgrade occurs before hashing.

```text
idempotency_key = sha256(repo | pr | head | effective_event | payload_sha256)
```

The runtime writes `post.intent` and a mode-0600 pending payload before mutation. PR3 adds a hidden remote marker. After timeout or connection ambiguity, it queries that marker before retry: one match reconciles locally, zero matches may retry while authorization remains valid, and multiple matches require human reconciliation.

#### D7 — Unsupported or invalid state

Unknown optional fields within v1 are ignored while original bytes remain intact. Unknown event types, required-field failures, hash mismatches, or unknown major versions are read-only quarantined and cannot reduce, resume, authorize, post, migrate, or be automatically garbage-collected. `show` may expose envelope metadata and an upgrade or legacy-fallback instruction.

### PR Boundary Ownership

| Child | Owns | Must not own |
|---|---|---|
| `2.1` Shadow review receipt | D1-D4 and D7 envelopes, validator, projection, evidence rehydration, baseline corpus, shadow receipt integration | Behavioral authority over verdict/confirmation/posting, resume, remote marker, coverage enforcement, token-improvement claim |
| `2.2` Typed interactive lifecycle | D5 enforcement, typed collator source of truth, exact-head interactive rehydration, legacy fallback | Daemon posting or remote idempotency |
| `2.3` Safe resume and once-only post | D1 retention/GC completion, D6 authorization/pending payload/remote reconciliation, daemon preauthorization | Daemon APPROVE v1 or auto-merge |

### Artifact Bundle Manifest

| Path | Type | Purpose |
|---|---|---|
| `docs/ship-flow/2-agent-native-pr-review-runtime/design.md` | Contract design | Canonical D1-D7 decisions and machine-readable hand-off to plan |

### Canonical Context

| Doc | Sections Read | Update Intent | Skip Rationale |
|---|---|---|---|
| `PRODUCT.md` | File absent | Create a repository-level agent-native review capability and success-measures section during canonical sync. | No existing product constraints were available to read; this design does not invent them. |
| `ARCHITECTURE.md` | File absent | Create context/decision sections for event authority, provider boundary, exact-head invalidation, coverage eligibility, and posting authority. | No existing architecture constraints were available to read; D1-D7 are proposed new decisions, not claims about current canon. |
| `kc-pr-flow/CLAUDE.md` | External reviewers, persistence, docs policy | Preserve graceful degradation, untrusted-input handling, and plugin documentation sync. | — |
| `kc-pr-flow/skills/kc-pr-review/SKILL.md` | Exact-head, coverage, cross-model, confirmation, posting | Mechanize existing invariants without changing PR1 behavior. | — |

## Design Readiness Review

Design Readiness Review: skipped - no risk trigger

The `schema` registry match describes a local capability and event-envelope contract. The change has one non-visual lane and no destructive persistence or multi-domain surface.

### Hand-off to Plan
<!-- section:hand-off-to-plan -->

```yaml
design-skipped: false
design_constraints:
  - type: data-contract
    assertion: "A stable exact-head review_key groups unique runs; resume reuses only compatible interrupted run IDs, while reruns and head/config changes create typed successors; terminal retention is 30 days, failed pending payload retention is 24 hours, and active or remotely uncertain runs are not garbage-collected."
    rationale_decision: D1
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: schema-contract
    assertion: "Versioned append-only JSONL events are authoritative for typed review-run records and projections are replayable caches; PR1 leaves the legacy flow authoritative for verdict, confirmation, and posting; canonical payload hashing, duplicate-event no-op behavior, and major-version evolution rules are mechanically validated."
    rationale_decision: D2
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: data-contract
    assertion: "Provider observations retain candidate identity; merged finding identity includes exact-head review key, path, side, evidence-content hash, category, and claim key; uncertain matches remain separate and durable evidence stores pointers and hashes only."
    rationale_decision: D3
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: contract
    assertion: "Core runtime exchanges provider-neutral ReviewTask and LaneResult envelopes; adapters cannot own lifecycle, verdict, authorization, or posting; usage provenance is reported, estimated, or unavailable, missing usage remains null and is never coerced to zero, and only comparable within-provider reported usage satisfies efficiency gates."
    rationale_decision: D4
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: contract
    assertion: "Coverage requiredness is capability-based; every required capability has typed terminal evidence; one retry and typed manual fallback precede an incomplete-coverage COMMENT ceiling; incomplete coverage can never yield APPROVE or dilute confirmed blockers, which may still yield REQUEST_CHANGES."
    rationale_decision: D5
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: contract
    assertion: "Authorization binds exact repo, PR, head, effective event, and canonical payload hash; a deterministic idempotency key and restrictive pending payload are persisted before mutation; ambiguous mutations reconcile the deterministic remote marker before retry; the remote GitHub review ID is mutation authority and its local receipt is retained; daemon posting is default-deny and cannot APPROVE in v1."
    rationale_decision: D6
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: schema-contract
    assertion: "Unknown optional fields within supported v1 are tolerated while original event bytes are preserved; unsupported majors, unknown event types, required-field failures, and hash mismatches are read-only quarantined and cannot reduce, resume, authorize, post, migrate, or be garbage-collected automatically; only metadata display plus an upgrade or legacy-fallback instruction is allowed."
    rationale_decision: D7
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
open_decisions: []
artifact_paths:
  - path: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
render_fidelity_targets: []
```

<!-- /section:hand-off-to-plan -->

## Design Report

status: passed
stage_cost: $0.00 (one generalist contract designer plus one fresh read-only cross-reviewer; local workflow)
iterations: 1 captain batch decision + 3 cross-review rounds
contradictions_resolved: 7
captain_decisions: 7
reviewer_verdict: PROCEED

### Metrics

status: passed
duration_minutes: 12
iteration_count: 4
captain_decisions_count: 7
reviewer_verdict: PROCEED

### Notes

- Generalist-only schema routing is an explicit limitation, not specialist evidence.
- Child 1 remains shadow-only and cannot claim token improvement or alter GitHub behavior.
- Cross-review confirmed every shape hand-off decision maps to a D-marker and plan-readable constraint; all seven non-UI rubric factors passed.
