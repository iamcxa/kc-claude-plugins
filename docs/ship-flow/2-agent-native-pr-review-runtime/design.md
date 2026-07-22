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

### Verify-return contract repair

Verify found that the original D2/D7 forward-compatibility rule contradicted D3: an integrity-valid unknown top-level field could durably retain raw provider content, while rejected input was copied byte-for-byte into quarantine. Verify also found that an identity-only run could be reported as observed and that evidence identity did not mechanically bind a finding to the reviewed base/head pair. These are contract defects, not implementation-only defects, so this design projection resolves them before execute resumes.

| Option | Forward evolution | Privacy and failure behavior | Cost | Disposition |
|---|---|---|---|---|
| Preserve arbitrary additive fields and rejected bytes | Maximum same-major flexibility and byte-level forensics | Violates the durable no-raw-content boundary; unknown fields and rejected input can retain prompts, diffs, excerpts, or provider output | Low migration cost, unacceptable disclosure risk | Rejected |
| Allow additive fields and redact with a denylist | Moderate same-major flexibility | Field names and nested encodings make redaction incomplete; validation success still does not prove content safety | Ongoing policy complexity and false-negative risk | Rejected |
| Close the v1 envelope, permit only typed hash-only extensions, and quarantine metadata | Evolution remains possible for non-semantic opaque facts; new fields or semantics require a new major | Durable state contains only known typed values, hashes, counts, timestamps, and evidence pointers; rejected input bytes never become durable | Explicit major-version upgrades for new semantics | **Selected — privacy-first** |

The selected option preserves the PR1 boundary: the runtime observes a sanitized projection of the already-completed legacy review, while the legacy flow remains the sole authority for verdict, confirmation, body, inline comments, event, options, and GitHub mutation.

#### Verify finding disposition

| Verify finding | Contract disposition | Downstream owner |
|---|---|---|
| Identity-only receipt reported as observed | D2 requires a closed collector input and complete started/finished lifecycle before `observed` | plan/execute |
| Additive fields and quarantine retain raw content | D2 closes the envelope; D7 makes quarantine metadata-only | design resolved; plan/execute |
| Finding/evidence identity not bound to exact head | D3 binds every pointer and derived identity to review/base/head plus evidence hash | design resolved; plan/execute |
| Snapshot symlink-swap TOCTOU | Input snapshots must use a no-follow open and verify the opened object is one stable regular file | plan/execute |
| jq-unsafe usage arithmetic | Every durable or compared integer is limited to `0..9007199254740991` | plan/execute |
| Parity oracle disconnected from the production seam | The executable parity fixture must enter through the exact serialized collector contract and frozen legacy artifacts | plan/execute |
| Benchmark recall unbound from candidates/evidence | Expected and observed findings must reference valid candidate/evidence identities; receipt hashes are recomputed from canonical arm content | plan/execute |
| Mixed-batch exit masking | Batch result precedence is `temporary/durability blocked > quarantined > success`; later rows cannot downgrade an earlier failure | plan/execute |
| Lock crash/PID reuse and append complexity | Preserve as explicit reliability/performance work for the safe-resume child unless the PR1 fix touches the same code safely | child 2.3 |
| Oversized limits, impossible timestamps, duplicated pointer predicates | Bound numeric configuration, validate calendar timestamps, and use one evidence-pointer validator while repairing PR1 | plan/execute |

### Captain Decisions

- **D1|Captain decision**: Use a stable exact-head `review_key` plus a unique `run_id`; resume only compatible interrupted runs, model reruns and head/config changes as explicit successors, retain terminal receipts for 30 days, retain failed pending payloads for 24 hours, and never garbage-collect active or remotely uncertain runs. (ref: `shape.md:202`)
- **D2|Captain decision**: Make versioned append-only `events.jsonl` the sole authority for typed review-run records, derive receipts by replay, canonicalize and hash every payload, treat duplicate event IDs as no-ops, and close the supported-v1 top-level envelope. Forward evolution within v1 is allowed only through a typed hash-only extension slot; new top-level fields or semantic values require a new major schema. Until PR2, the legacy flow remains behavioral authority for verdict, confirmation, and posting. (ref: `shape.md:202`; verify-return privacy repair)
- **D3|Captain decision**: Preserve every provider observation as a candidate; bind each source pointer to the reviewed base/head pair; derive both candidate and merged-finding identity from the evidence-content hash as well as exact-head review key, path, side, category, and constrained claim key; keep uncertain matches separate; and persist only typed evidence pointers and hashes rather than excerpts or raw model output. (ref: `shape.md:203`; verify-return identity repair)
- **D4|Captain decision**: Keep the core provider-neutral through narrow versioned task/result envelopes, isolate provider-specific behavior in adapters, record usage as `reported`, `estimated`, or `unavailable` without coercing missing values to zero, and admit only comparable within-provider reported usage to efficiency gates. (ref: `shape.md:204`)
- **D5|Captain decision**: Define requiredness by review capability rather than provider name, require typed terminal coverage with evidence from either an adapter or explicit manual fallback, retry required transient failures once, forbid APPROVE when required coverage remains incomplete, default such runs to an explicit COMMENT gap, preserve REQUEST_CHANGES for confirmed blockers, and keep optional-provider failures as evidence only. (ref: `shape.md:205`)
- **D6|Captain decision**: Bind authorization to the canonical exact-head payload hash and effective event, default daemon posting to deny with no daemon APPROVE in v1, write a restrictive pending payload before mutation, derive a deterministic idempotency key, reconcile ambiguous outcomes against a remote hidden marker before retry, and treat the remote GitHub review ID as mutation authority while retaining its local receipt. (ref: `shape.md:206`)
- **D7|Captain decision**: Reject unknown top-level fields, unknown event types, invalid hashes, missing required fields, and unknown majors from reduction or mutation. Quarantine retains only `reason_code`, rejected-input SHA-256, byte count, and timestamp—never rejected bytes—and display is limited to those metadata plus an upgrade or legacy-fallback instruction. (ref: `shape.md:207`; verify-return privacy repair)

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
extensions:
  - namespace: constrained-token
    key: constrained-token
    value_sha256: sha256
    byte_count: jq-safe non-negative integer
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

The v1 top-level key set is closed. `extensions` is the only same-major evolution point: each entry contains constrained identifiers, a SHA-256 value commitment, and a jq-safe byte count, but no string value, nested value, encoded payload, or arbitrary bytes. Extension entries are observational metadata only and cannot alter validation, reduction, identity, coverage, authorization, or mutation semantics. Any such semantic change requires a new major version.

#### D3 — Finding and evidence identity

```text
candidate_id = sha256(run_id | lane_id | ordinal | evidence_content_sha256)
merge_key    = path | side | evidence_content_sha256 | category | claim_key
finding_id   = sha256(review_key | merge_key)
```

Providers produce candidates; the collator produces constrained `claim_key` and merge decisions. Uncertain matches remain separate.

Evidence pointers use a typed union: `git_blob | pr_body | issue | review_comment | command | test`. Every pointer carries the exact `review_key`, `base_sha`, and `head_sha`. A `git_blob` pointer binds `object_sha` to `base_sha` for `LEFT` and to `head_sha` for both `RIGHT` and `FILE`; non-git sources bind their typed locator/version to the same exact-head pair. Candidate and finding validation requires the nested pointer's `review_key`, `base_sha`, and `head_sha` to equal the containing event identity. Source pointers include repository-relative location, line range, locator when applicable, content hash, and typed result. Rehydration fetches the source, verifies the exact-head/object binding, and validates the content hash before the evidence can support a candidate or finding; durable state stores no excerpt.

#### D2/D3 — Sanitized shadow collection and terminal observation

The production shadow seam accepts one `ShadowObservation/v1` projection created after legacy collation is frozen. Its top-level keys are exactly `schema`, `identity`, `behavior_hashes`, `lanes`, and `synthesis`:

```yaml
schema: kc-pr-flow.shadow-observation/v1
identity: {repository, pr_number, base_sha, head_sha, config_hash, occurred_at}
behavior_hashes: {body_sha256, inline_comments_sha256, event_sha256, options_sha256, confirmation_input_sha256, github_call_log_sha256}
lanes:
  - {lane_id, capability, provider_family?, terminal_status, usage, candidates[]}
synthesis: {findings[], uncertain_candidate_refs[]}
```

All objects use exact key sets. `lanes` is a non-empty array unique by `lane_id`; every lane has one capability, one `succeeded | failed | unavailable` terminal status, typed usage, and zero or more candidates unique by `(lane_id, ordinal)`. Candidate projections contain exactly `ordinal`, `path`, `side`, `anchor_sha256`, `category`, `claim_key`, and one D3 evidence pointer; they contain no runtime-generated IDs. Each finding contains the same merge fields plus one D3 evidence pointer and a non-empty unique `candidate_refs[]` array of `{lane_id, ordinal}` values that must resolve to declared candidates with the same evidence-content hash. `uncertain_candidate_refs[]` uses the same reference type, resolves to declared candidates, and is disjoint from finding membership. Every integer is jq-safe. All strings are constrained identifiers, paths, enums, repository identity, timestamps, or hashes; raw review content and arbitrary nested values are invalid.

The collector creates the run identity, then deterministically emits `run.started`; for each declared lane, `lane.started`, its ordered `finding.observed` candidate events, and one `lane.finished`; then one `synthesis.finished` and one `run.finished`. It computes candidate/finding IDs from the canonical D3 formulas and rejects unresolved or inconsistent references before publishing accepted state. `observed` is valid only when replay proves that exact sequence class, one started/finished pair for every declared lane, terminal synthesis and run records, exact-head identity, and all internal references. An identity-only or otherwise incomplete run is `not_observed` with a typed reason; fail-open means legacy behavior continues, not that incomplete telemetry is promoted to success.

The production parity fixture serializes this exact `ShadowObservation/v1`, passes it to the same collector executable used by the skill, and surrounds that call with frozen legacy body, inline-comments, event, options, confirmation-input, and mocked-GitHub-log artifacts. Off, on, and collector-failure runs compare every artifact byte-for-byte and assert that the mocked mutation log remains empty.

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

Unknown top-level fields are invalid in v1. Unknown event types, required-field failures, hash mismatches, or unknown major versions are excluded from accepted state and cannot reduce, resume, authorize, post, migrate, or be automatically garbage-collected. Quarantine is a separate metadata-only record containing exactly a typed reason code, SHA-256 of the rejected input, byte count, and timestamp; it never contains or links to the rejected bytes. `show` may expose only that metadata and an upgrade or legacy-fallback instruction.

### PR Boundary Ownership

| Child | Owns | Must not own |
|---|---|---|
| `2.1` Shadow review receipt | D1-D4 and D7 closed envelopes, metadata-only quarantine, validator, projection, exact-head evidence rehydration, sanitized collector, complete-terminal observation, baseline corpus, shadow receipt integration | Behavioral authority over verdict/confirmation/posting, resume, remote marker, coverage enforcement, token-improvement claim |
| `2.2` Typed interactive lifecycle | D5 enforcement, typed collator source of truth, exact-head interactive rehydration, legacy fallback | Daemon posting or remote idempotency |
| `2.3` Safe resume and once-only post | D1 retention/GC completion, D6 authorization/pending payload/remote reconciliation, daemon preauthorization | Daemon APPROVE v1 or auto-merge |

### Artifact Bundle Manifest

| Path | Type | Purpose |
|---|---|---|
| `docs/ship-flow/2-agent-native-pr-review-runtime/design.md` | Contract design | Canonical D1-D7 decisions and machine-readable hand-off to plan |

### Canonical Context

| Doc | Sections Read | Update Intent | Skip Rationale |
|---|---|---|---|
| `PRODUCT.md` | `kc-pr-flow: Agent-native PR review` outcome, target capabilities, delivery boundary, current increment, non-goals | Preserve exact-head receipts, rehydrated pointer evidence, no durable raw content, and shadow-only authority. | No edit in this bounded design-artifact repair; the existing product contract already selects the privacy-first outcome. |
| `ARCHITECTURE.md` | `kc-pr-flow: Agent-native review runtime` decision record, shadow data flow, identity, increment boundaries | Follow-on canonical sync must replace identity-only observation, arbitrary additive-v1 tolerance, original-byte quarantine, and stale evidence-binding language with this repaired D2/D3/D7 contract before verify can pass. | Not edited because this verify-return assignment is restricted to parent/child design artifacts; drift is explicit and remains a downstream blocker. |
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
    assertion: "Versioned append-only JSONL events are authoritative for typed review-run records and projections are replayable caches; PR1 leaves the legacy flow authoritative for verdict, confirmation, and posting; canonical payload hashing and duplicate-event no-op behavior are mechanically validated; the v1 top-level envelope is closed and same-major evolution is limited to typed hash-only extensions with no arbitrary values or semantic authority."
    rationale_decision: D2
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: data-contract
    assertion: "Provider observations retain candidate identity; candidate and merged finding identity include the evidence-content hash; each nested evidence pointer equals the containing event review_key/base_sha/head_sha, and git_blob object_sha binds LEFT to base_sha and RIGHT or FILE to head_sha; uncertain matches remain separate and durable evidence stores pointers and hashes only."
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
    assertion: "Unknown top-level fields, unsupported majors, unknown event types, required-field failures, and hash mismatches are excluded from accepted state and cannot reduce, resume, authorize, post, migrate, or be garbage-collected automatically; quarantine stores exactly reason code, rejected-input SHA-256, byte count, and timestamp, never rejected bytes; only metadata display plus an upgrade or legacy-fallback instruction is allowed."
    rationale_decision: D7
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: data-contract
    assertion: "The shadow seam consumes the exact closed ShadowObservation/v1 schema after legacy collation is frozen; every declared lane maps to lane.started, ordered candidate events, and lane.finished, followed by synthesis.finished and run.finished; observed requires that complete replay-valid lifecycle, while identity-only or incomplete receipts are not_observed; the same serialized collector entrypoint drives byte-parity tests."
    rationale_decision: D2
    source_artifact: docs/ship-flow/2-agent-native-pr-review-runtime/design.md
  - type: contract
    assertion: "Runtime file snapshots use a no-follow open and verify the opened object is one stable regular file; integers are limited to jq-safe range; batch status cannot downgrade blocked work; benchmark findings are bound to canonical candidates/evidence and receipt content; canonical PRODUCT/ARCHITECTURE/docs are synchronized before verify reruns."
    rationale_decision: D2
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
iterations: 1 captain batch decision + 4 cross-review rounds
contradictions_resolved: 7
captain_decisions: 7
reviewer_verdict: PROCEED

### Metrics

status: passed
duration_minutes: 12
iteration_count: 5
captain_decisions_count: 7
reviewer_verdict: PROCEED

### Notes

- Generalist-only schema routing is an explicit limitation, not specialist evidence.
- Child 1 remains shadow-only and cannot claim token improvement or alter GitHub behavior.
- First verify-return cross-review VETOed incomplete `FILE` binding, an underspecified collector schema/lifecycle, stale pass claims, and incomplete reverse-audit. Those findings were incorporated; the fresh bounded re-review returned PROCEED with all seven non-UI factors passing. Canonical synchronization remains an execute prerequisite, not an unresolved design decision.
