# Review Runtime Contract

This reference defines the current `kc-pr-review` receipt and typed interactive runtime. It is a compatibility boundary for maintainers and adapter authors. The runtime records review observations and derives coverage, approval eligibility, effective-event precedence, and confirmation input from one terminal exact-identity receipt. It does not choose findings, bypass confirmation, authorize posting, or mutate GitHub.

## Runtime boundary

The implementation is source-safe Bash 3.2 plus `jq`, with Python 3.8+ providing the fail-closed safe-I/O boundary. Sourcing either runtime script declares functions without executing its CLI or changing the caller's options, traps, working directory, variables, or `umask`.

Each receipt-runtime file consumer first creates one private mode-0600 snapshot from a no-follow regular-file descriptor. The helper requires `O_NOFOLLOW` and `O_CLOEXEC`, rejects non-regular and oversize sources, reads through the descriptor only, and requires matching pre-open, before-read, and after-read device, inode, size, mtime, and ctime identity. It also rejects duplicate JSON members, floats, and integers outside jq's exact range; a validation pass classifies a whole JSONL stream in one helper launch (`unique-json-lines`) rather than one launch per line. That batch falls back to the per-line check whenever it is unavailable, exits non-zero, or returns a verdict count that disagrees with the file it just read. The fallback is scoped to the launch that computes the verdicts: an append reuses the verdicts already computed for the log it extends, and that reuse is positional — it is **not** re-checked against the bytes finally copied, so a log swapped for an equal-length substitute between validation and copy is not detected. Impossible RFC 3339 UTC calendar values are rejected in the shell against the fixed `%Y-%m-%dT%H:%M:%SZ` grammar, which needs no interpreter; the helper keeps `rfc3339-utc` as the reference implementation those shell rules are held to, and `review-post.test.sh` drives both sides against one case table so that equivalence is checked rather than asserted. Missing Python or platform support returns dependency status 69; path replacement and durability failures return closed errors before accepted-state mutation. Concurrent mutation is caught only to the extent the cross-check on a computing launch covers it; the reused-verdict window described above is outside that coverage, and same-user mutation inside it is not in this runtime's threat model. The diagnostic shadow seam converts such failures to typed `not_observed`; enabled typed authority converts them to an explicit non-approval decision.

The runtime has no network, model, GitHub, posting, authorization, resume, or garbage-collection authority. In typed mode its derived decision is authoritative only for interactive coverage, approval eligibility, event precedence, and confirmation input. The existing `kc-pr-review` flow remains authoritative for review analysis, rendering, mandatory human confirmation, and posting.

## Phase 1 trusted post-fix planning

`scripts/review-plan.sh` is a separate read-only router for the default-off
post-fix route. It consumes a closed terminal runtime event file and produces
only these advisory schemas:

```json
{
  "schema": "kc-pr-flow.review-delta-receipt/v2",
  "predecessor": {"repository": "owner/repo", "pr_number": 42, "base_sha": "<40-hex>", "head_sha": "<40-hex>", "config_hash": "<64-hex>", "review_key": "<64-hex>", "run_id": "run-safe-token", "receipt_id": "<64-hex>"},
  "known_findings": [{"finding_id": "<64-hex>", "claim_key": "category-<16-hex>", "anchor_sha256": "<64-hex>", "category": "correctness", "evidence": {"schema": "kc-pr-flow.evidence-pointer/v1", "kind": "git_blob", "repository": "owner/repo", "review_key": "<64-hex>", "base_sha": "<40-hex>", "head_sha": "<40-hex>", "object_sha": "<40-hex>", "content_sha256": "<64-hex>", "path": "relative/path", "side": "RIGHT", "line": 7, "locator": null}, "evidence_sha256": "<64-hex>", "path": "relative/path", "side": "RIGHT", "resolution_state": "unresolved"}],
  "required_capabilities": ["code_correctness"],
  "coverage_gap_refs": [],
  "content_sha256": "<64-hex>"
}
```

```json
{
  "schema": "kc-pr-flow.review-plan-decision/v1",
  "identity": {"repository": "owner/repo", "pr_number": 42, "base_sha": "<40-hex>", "head_sha": "<40-hex>", "config_hash": "<64-hex>", "review_key": "<64-hex>"},
  "mode": "resolve",
  "reason_codes": ["trusted_predecessor", "ancestor_append", "known_finding_delta"],
  "review_range": {"from_exclusive": "<40-hex>", "to_inclusive": "<40-hex>"},
  "inherited_finding_ids": ["<64-hex>"],
  "required_capabilities": ["code_correctness"],
  "event_ceiling": "APPROVE",
  "fallback": {"router_advisory": true, "requires_existing_initial_review": false, "final_verdict_authority": "existing-review-runtime"}
}
```

A receipt is trusted only after the predecessor event file is a private regular
file snapshot that replays successfully, the receipt exactly binds that replay,
repository/PR/base/configuration match, predecessor head is an ancestor of the
current head, and every inherited finding has a stable ID and evidence hash.
The current receipt validator accepts only `coverage_gap_refs:[]`; a receipt
claiming a gap is untrusted and selects `initial` with no synthetic ceiling.
Any missing, malformed, unsafe, stale, hash-mismatched, replay-invalid, or
non-ancestor input does the same.

`review-config.json` below is the same safe, private regular-file snapshot of
the exact canonical `kc-pr-flow.review-config/v1` bytes used to derive
`CONFIG_HASH`; it has no trailing newline. The receipt producer and every
non-initial decision must receive that same snapshot.

```bash
bash scripts/review-plan.sh receipt --event-file terminal-events.jsonl --config-file review-config.json --repo-worktree REPO_DIR
bash scripts/review-plan.sh decide --repo owner/repo --pr 42 --base BASE --head HEAD \
  --config-hash CONFIG_HASH --config-file review-config.json --repo-worktree REPO_DIR \
  --predecessor-events terminal-events.jsonl --delta-receipt receipt.json
```

| Router result | Required adapter behavior |
|---|---|
| valid `resolve` / `delta` | Keep the exact returned range, inherited IDs, required capabilities, and authority ceiling. |
| `initial` | The closed fallback object requires the existing full initial flow with no synthetic `COMMENT` ceiling. |
| nonzero, partial stdout, invalid JSON, invalid schema, or invalid closed shape | Discard stdout and run that same unchanged `initial` flow. |
| current required coverage gap | Keep review visible and cap at `COMMENT`; blocker evidence may still use the existing `REQUEST_CHANGES` path. |

The router cannot dispatch a reviewer, assert semantic correctness or security,
choose the review event, alter confidence, authorize a human confirmation, or
post a review. `event_ceiling` is only a maximum authority bound, ordered as
`APPROVE` > `COMMENT` > `REQUEST_CHANGES`; it can reduce authority but never
upgrade it.

The skill snapshots the original repository, PR, base, head, configuration,
worktree, predecessor-event, and receipt inputs before routing. A non-`initial`
decision is retained in memory as canonical `PLAN_JSON`, with an immutable
SHA-256 digest and immutable engagement marker. At every authority boundary it
reruns the existing `decide` command over those original inputs while the flag
is still `on`. The adapter captures the raw decision and rejects duplicate JSON
members before any jq parse or canonicalization, then validates and canonicalizes
the unique decision and requires exact equality with the stored plan. The same
raw-first rejection applies to initial engagement. It then validates the stored
digest and applies the event partial order. It never silently clamps a
disallowed event.

Before engagement, flag-off preserves legacy authority. Under flag-on, only a
fresh rerun that still selects `initial` preserves that authority; a fresh
`delta` or `resolve`, invalid result, or router failure blocks the boundary.
After engagement, a missing, mutated, stale, or identity-mismatched plan blocks.
If the flag is later off or unexported, the stored canonical plan and digest
remain authoritative and its ceiling is still enforced, without rerunning the
disabled router.

The same `review_plan_event_allowed` gate runs before presenting a legacy or
typed effective event at Step 6c, after each human event edit, before autonomous
gate creation, while constructing the confirmed post gate, and immediately
before interactive, autonomous, once-only, or legacy posting. Any failure
rejects that seam; it does not create confirmation or posting authority.

## Exact-head identity

A review is bound to these caller-supplied values:

- canonical repository identity supplied by the adapter, normally `owner/repository`;
- positive PR number;
- 40-character lowercase base SHA;
- 40-character lowercase reviewed head SHA; and
- 64-character lowercase effective configuration hash.

The review key is:

```text
sha256(repository|pr_number|base_sha|head_sha|config_hash)
```

The runtime validates that repository identity is non-empty and contains no control characters, but
does not normalize it. It hashes repository bytes exactly as supplied. Adapters must canonicalize
equivalent remote forms to `owner/repository` before `start`, event construction, or review-key
comparison. Git-origin URL normalization is a separate operation used only when verifying a local
`git_blob` evidence pointer.

The canonical configuration schema is `kc-pr-flow.review-config/v1`. It contains a sorted,
deduplicated capability array and these effective modes. Only that set-valued `capabilities` array
maps the legacy `correctness` spelling to `code_correctness`; repetitions and both spellings
collapse, while structured values or the alias in any other field are invalid.

| Field | Values | Default |
|---|---|---|
| `agent_tier` | `lite`, `standard`, `full` | `lite` |
| `pr_archetype` | `bugfix`, `cross_stack`, `docs`, `feature`, `mixed`, `refactor`, `style` | `mixed` |
| `full_pass` | boolean | `false` |
| `probe_required` | boolean | `false` |
| `cross_model` | boolean | `false` |
| `noise_filter` | boolean | `false` |

`config-hash` serializes the normalized object as RFC 8785 JSON Canonicalization Scheme UTF-8 bytes
and hashes them without a trailing newline. Prompts, diffs, rendered review content, comments, and
provider output are not configuration inputs. The delta receipt boundary consumes one safe
canonical config snapshot, recomputes this hash, and requires its sorted unique capabilities to
equal the unique replayed lane capabilities before producing, validating, or trusting a
predecessor; invalid or mismatched input falls back to `initial`.

Every execution receives a fresh `run-*` ID. A successor may reference a predecessor and one of `manual_rerun`, `config_change`, `head_appended`, `head_rewritten`, or `recovery_fork`; the relationship does not change either run's immutable exact-head identity.

## State and durability

The state root is selected in this order:

1. `KC_PR_FLOW_STATE_DIR`;
2. `$XDG_STATE_HOME/kc-pr-flow`; or
3. `$HOME/.local/state/kc-pr-flow`.

Accepted logs use this layout:

```text
<state-root>/
  <sha256-repository-key>/
    pr-<number>/
      run-<unique-suffix>/
        events.jsonl
  quarantine/
    <event-sha256>-<reason>/
      metadata.json
```

Managed directory components must be real directories, never symlinks. Run directories are mode `0700`; accepted event logs are mode `0600`. The default accepted-log size limit is 16 MiB and can be lowered with `KC_PR_FLOW_MAX_EVENTS_BYTES`.

Publication uses private temporary files or directories followed by rename. Every `validate`, `append`, `replay`, `show`, `observe`, evidence, usage, and collector file is parsed only from its bounded private snapshot. Appends validate each envelope plus the existing log's immutable run identity, hashes, and contiguous sequence; they do not enforce lane chronology. An append reserves the run at the PR directory, builds the next complete log privately, and renames it over the accepted log. Concurrent duplicate appends converge on one accepted event; conflicting or blocked appends do not modify accepted bytes.

Reservation and quarantine locks are owned `mkdir` locks with one `owner.pid`. A live or malformed owner fails closed with temporary-failure status. A provably dead owner is reclaimed once. `KC_PR_FLOW_RESERVATION_WAIT_ATTEMPTS` controls the bounded reservation wait.

Only rejected append input creates content-addressed metadata-only quarantine. The sole mode-0400 `metadata.json` contains exactly `reason_code`, rejected `input_sha256`, `byte_count`, and `quarantined_at`; rejected bytes, links, excerpts, and raw values are never retained. The containing directory is mode `0500`. Read-only `validate`, `replay`, `show`, and `observe` operations do not quarantine an already-invalid receipt. Complete matching publication is idempotent; incomplete or conflicting artifacts fail closed. The default metadata-record limit is 4 MiB and can be lowered with `KC_PR_FLOW_MAX_QUARANTINE_BYTES`.

## Review timing receipt

The runtime can record one local `kc-pr-flow.review-timing-state/v1` and close it
as `kc-pr-flow.review-timing/v1`. This path is measurement-only: it has no
network, model, confirmation, authorization, or posting authority. The caller
supplies the exact review key, review mode, phase boundaries, and closed lane
observations; it cannot supply a total duration or a clock value.

`timing-start` records Python's monotonic nanosecond clock in a new mode-0600
state file. `timing-mark` safe-snapshots and validates that state, records a new
runtime clock value, then passes the expected snapshot to one foreground
publication helper. The helper takes a nonblocking kernel lock on the bound
timing-parent descriptor, rechecks the expected bytes under that lock, and
performs the descriptor-bound atomic replacement in the same process. The lock
serializes only the publication critical section. A competing publication
either observes changed bytes or returns temporary status 75; process death
releases the lock without a lock pathname or stale artifact. The state is
closed and content-hashed. Marks are unique and may
only advance through this order:

```text
identity_and_plan
inventory
required_lanes_critical_path
targeted_verification_critical_path
collation_and_draft
confirmation_ready
```

Each of the first five marks closes the phase with that name. Its duration is
the elapsed time since `timing-start` or the preceding mark. The terminal
`confirmation_ready` mark closes the promotion interval;
`review_to_confirmation_ready` is the elapsed time from start through that
mark. This total is derived directly from the two runtime timestamps, not by
summing phase or lane observations.

`timing-finish` requires the complete ordered mark set. It safe-snapshots a
closed JSON array of unique lane observations with exactly `lane_id`,
nonnegative jq-safe `duration_ms`, and `provider_family` as a safe token or
null. Lane durations remain attribution data only; they never determine a
parallel phase's critical-path duration. The terminal receipt keeps
`confirmation_wait`, `external_ci_wait`, and `post_mutation` null because this
runtime does not observe those later waits or mutations.

## Event envelope and lifecycle

Each line is a `kc-pr-flow.review-event/v1` object. Required envelope fields are schema, event and run identities, exact-head identity, sequence, UTC occurrence time, event type, canonical payload and payload hash, and full-record integrity hash.

Hash formulas are:

```text
payload_sha256 = sha256(jq_-S_-c(payload))
event_id       = sha256(run_id|sequence|event_type|payload_sha256)
integrity      = sha256(jq_-S_-c(event_without_integrity_sha256))
```

The first event must be `run.started` at sequence one. All later events must preserve the first event's run and exact-head identity. On append, a repeated identical event ID is an idempotent duplicate; reuse with different content is quarantined.

The current typed observation lifecycle is:

```text
run.started
  -> lane.started
  -> finding.observed (zero or more, before that lane finishes)
  -> lane.finished
  -> synthesis.finished
  -> run.finished
```

`lane.started` carries a provider-neutral `kc-pr-flow.review-task/v1`. `finding.observed` carries a `kc-pr-flow.review-candidate/v2` whose ID binds run, lane, ordinal, and evidence hash. `lane.finished` carries a `kc-pr-flow.lane-result/v1` and must account for exactly the candidates observed for that lane. `synthesis.finished` carries unique `kc-pr-flow.review-finding/v2` records plus uncertain candidate IDs; together they must partition every observed candidate exactly once. The runtime NFC-normalizes repository-relative paths and uses RFC 8785 canonical UTF-8 bytes to derive the machine-owned claim key and finding ID. The finding ID binds repository, review key, path, side, exact evidence identity, deterministic anchor, category, and claim key while excluding lane, ordinal, and prose. Equal complete identities from multiple lanes collapse to one finding; received duplicate finding IDs are invalid. `run.finished` carries exactly the six SHA-256 hashes of the frozen legacy body, inline comments, event, options, confirmation input, and GitHub-call log. A shadow receipt is complete only when every declared lane is terminal, synthesis partitions all candidates, `run.finished` is last, and those behavior hashes are present.

Enforcement is intentionally layered. `validate` checks individual event envelopes and hashes, not
cross-event ordering. `append` additionally protects accepted run identity and contiguous sequence,
but can accept envelopes whose lane order is not replayable. Only `replay` and `show` enforce the
authoritative chronological lifecycle and candidate/finding relationships; `observe` inherits that
enforcement by delegating to replay. A log is not trustworthy as a receipt merely because
`validate` or `append` accepted every line.

The v1 validator recognizes closed payload schemas for `head.observed`, `authorization.granted`, `post.intent`, `post.result`, and `run.invalidated` (see "Once-only posting" below). An empty `run.finished` remains syntactically reserved for forward compatibility but cannot make a shadow observation complete. These event names grant `review-runtime.sh` itself no interactive, authorization, or posting authority — that authority lives only in `scripts/review-post.sh`.

Payload schemas are closed. Unknown event types, unsupported schema majors, missing fields, identity or hash mismatches, and raw or opaque payload fields fail individual validation and create metadata-only quarantine when submitted through append. Mixed-run identity or noncontiguous sequence blocks accepted-log mutation. Chronologically invalid lane or synthesis relationships fail `replay`/`show` without creating quarantine. The only optional envelope field is `extensions`: a closed array whose entries contain exactly a safe namespace, safe key, SHA-256 of the external value, and jq-safe byte count. Extensions participate in record integrity but have no replay or semantic authority.

## Provider-neutral observations

Review tasks describe capability and lane identity, exact head, and optional provider hint. Lane results describe terminal status (`succeeded`, `failed`, or `unavailable`), the exact candidate set, optional provider family, and a usage observation. Provider adapters cannot own lifecycle, synthesis, verdict, authorization, or posting.

Usage records have `input_tokens`, `output_tokens`, `total_tokens`, `provenance`, `provider_family`, and `scope`. Provenance is `reported`, `estimated`, or `unavailable`; scope is `lane` or `run`. Unavailable usage requires null token values. A comparison is available only when both observations are complete, provider-reported, from the same non-null provider family, and at the same scope. Missing or incomparable usage is never interpreted as zero.

## Typed interactive authority

`KC_PR_FLOW_REVIEW_TYPED` is sampled once before provider dispatch. Only the exact value `on` selects typed mode; unset, off, and unknown values select legacy mode for that fresh invocation. Once typed mode starts, an invalid, incomplete, unsupported, or stale typed result cannot switch the same invocation back to legacy.

The capability policy is closed and provider-neutral. Each capability is required or optional and ends in exactly one of `clean`, `findings`, `evidence_backed_na`, `incomplete_required`, or `incomplete_optional`. A required transient adapter failure permits exactly one retry. If it still lacks terminal evidence, an evidence-bound interactive manual result may provide the terminal state. Required gaps forbid approval; optional gaps remain visible without blocking on their own. Confirmed blockers always take precedence and select REQUEST_CHANGES.

`InteractiveCollationDecision/v1` (`kc-pr-flow.interactive-collation-decision/v1`) is a closed derived projection with exact review identity, typed capability terminals, required-gap and blocker references, coverage, approval eligibility, effective event, and confirmation input. It is derived only by replaying one complete terminal receipt and verifying its exact identity and evidence. It grants no authorization or posting authority.

`rehydrate-interactive` is terminal-only and read-only. It rejects incomplete lifecycle state, moved identity, invalid policy, unsupported terminal state, extra retry, unbound fallback, or mismatched evidence. It does not append, repair, resume, recover a lock, establish predecessor lineage, retain or collect state, dispatch a model, contact a remote service, create authorization, or post.

## Advisory merge readiness

`MergeReadinessDecision/v1` (`kc-pr-flow.merge-readiness-decision/v1`) is a closed advisory
projection over one in-process `rehydrate-interactive` result, one caller-supplied CI observation,
one caller-supplied test observation, and one independently supplied observed PR head. Callers
supply the terminal receipt, capability policy, repository worktree, exact review identity, and one
closed `kc-pr-flow.merge-readiness-observations/v1` file; they cannot supply a review decision. The
canonical input binding is `kc-pr-flow.merge-readiness-binding/v1`, combining the normalized
observations with the exact successful producer result.

All identities and observation heads must match the reviewed head. Complete positive evidence
emits `READY/HIGH`; a same-head required CI/test failure or confirmed review blocker emits
`NOT_READY/HIGH`; stale, invalid, or incomplete required evidence emits `UNKNOWN/LOW`. Contract
confidence describes whether the closed supplied evidence is structurally sufficient and
decisive; it does not replace per-finding confidence calibration.

The adapter safe-snapshots the observation file, invokes the existing local producer exactly once,
and writes one decision. Producer rejection maps to `UNKNOWN/LOW/invalid-review-evidence`. It does
not fetch live state, contact GitHub, dispatch a model, authorize or post a review, or merge a PR.
The producer still performs its documented read-only local Git evidence verification.
`advisory_only` is `true`, and humans remain the merge authority. A caller that cannot obtain a
decision because an input file is unsafe or unreadable must treat the result as `UNKNOWN`, never as
`READY`.

## Evidence pointers

Durable observations store `kc-pr-flow.evidence-pointer/v1` metadata and a SHA-256 content hash, never source excerpts. Supported kinds are `git_blob`, `pr_body`, `issue`, `review_comment`, `command`, and `test`.

A pointer binds repository, 40-character object SHA, kind-specific locator data, and content hash. Paths must be relative, normalized, and free of traversal, backslashes, repeated separators, or control characters.

`verify-evidence` currently rehydrates only `git_blob` pointers. It verifies a safe local Git worktree, normalizes HTTPS/SSH/scp-like GitHub origin forms to `owner/repository` for this comparison only, and checks object type `blob` plus the exact content hash. That normalization does not apply to event or review-key construction. Other pointer kinds return typed `unavailable` status. A mismatch cannot support a finding or authority decision.

## CLI and library API

All commands print compact JSON except `config-hash`, which prints a hash, and CLI usage/errors on standard error.

| Command | Contract |
|---|---|
| `start` | Create a private exact-head run and emit its `run.started` event. Required: `--repo`, `--pr`, `--base`, `--head`, `--config-hash`; `--occurred-at` defaults to current UTC. `--predecessor-run-id` and `--successor-reason` must be supplied together. |
| `append --event-file FILE` | Append each candidate JSONL line to its managed run. `-` reads standard input. Returns counts for appended, duplicate, quarantined, and blocked records. |
| `validate --event-file FILE` | Stream and validate event envelopes independently, then return valid/invalid counts. It does not enforce authoritative cross-event relationships. `-` reads standard input. |
| `replay --event-file FILE` | Validate a complete authoritative log, enforce chronological relationships, and rebuild the deterministic `review-projection/v2`. |
| `show --event-file FILE` | Return a compact `review-summary/v1` with exact run identity and lane, candidate, finding, uncertain, and usage counts. |
| `config-hash ...` | Normalize the effective v1 review configuration and return its canonical hash. Options are `--agent-tier`, `--pr-archetype`, `--full-pass`, `--probe-required`, `--cross-model`, `--noise-filter`, and comma-separated `--capabilities`; omitted options use the defaults above. |
| `timing-start --review-key HASH --mode initial\|delta\|resolve --output FILE` | Create one new mode-0600 content-hashed monotonic timing state. Existing, linked, or non-regular output targets are refused. |
| `timing-mark --timing-file FILE --phase NAME` | Safe-snapshot and validate timing state, append one forward phase mark with the runtime clock, then serialize the publication critical section with a bound-parent kernel lock, expected-byte recheck, and descriptor-bound atomic replacement. |
| `timing-finish --timing-file FILE --lane-durations-file FILE --output FILE` | Require all phase marks, validate closed lane observations, and write plus print one mode-0600 `ReviewTiming/v1` receipt. It accepts no caller total. |
| `observe --event-file FILE --expected-head SHA --expected-review-key HASH` | Read-only replay plus exact-head/key check. Returns typed `observed` or `not_observed` status and never mutates the log. |
| `rehydrate-interactive --event-file FILE --policy-file FILE --repo-worktree DIR --repo OWNER/REPO --pr N --base SHA --head SHA --config-hash HASH --review-key HASH --run-id ID` | Replay one complete terminal receipt, verify exact identity and evidence, and emit one closed `InteractiveCollationDecision/v1`. It never appends or performs recovery or remote behavior. |
| `decide-merge-readiness --observations-file FILE --event-file FILE --policy-file FILE --repo-worktree DIR --repo OWNER/REPO --pr N --base SHA --head SHA --config-hash HASH --review-key HASH --run-id ID` | Validate closed exact-head CI/test/head observations, invoke `rehydrate-interactive` once from the supplied producer sources and identity, and emit one advisory `MergeReadinessDecision/v1`. It accepts no caller decision and performs no network, post, authorization, or merge operation. |
| `review-key ...` | Validate repository, PR, base, head, and config inputs and print their canonical review key. It uses the same construction as events, evidence, and the collector. |
| `shadow --observation-file FILE ...` | Best-effort production seam. `--enabled` overrides `KC_PR_FLOW_REVIEW_SHADOW`; enabled collection also requires `--head-check-status` and, when successful, `--live-head`. It accepts exactly one closed `ShadowObservation/v1` (`kc-pr-flow.shadow-observation/v1`) file, persists a fresh `run.started`, builds and preflight-replays the remaining complete lifecycle before appending those events, then observes once. Every dependency, validation, head, append, or replay failure returns typed `not_observed` and fails open only to the unchanged legacy review. A post-start failure may leave an incomplete non-authoritative run for increment 2.3 recovery. |
| `verify-evidence --pointer-json FILE --repo DIR` | Verify one pointer from a private snapshot against the local repository. |
| `compare-usage --left-json FILE --right-json FILE` | Compare two private usage snapshots under the provenance rules above. |

The same operations are available as `review_runtime_*` functions after sourcing the script. Runtime file and standard-input consumers read one bounded safe snapshot. The serialized `ShadowObservation/v1` file is the sole collector input authority; replay of its emitted JSONL is the sole receipt projection authority. Evidence verification uses the exact pointer snapshot plus the reviewed Git object and content hash, never a caller-supplied excerpt.

The paired scorer is a separate source-safe CLI:

```bash
bash scripts/review-runtime-benchmark.sh score \
  --corpus <sanitized-pairs.jsonl> \
  [--local-costs <bound-rehydration-measurements.json>]

bash scripts/review-runtime-benchmark.sh measure-local \
  --runtime scripts/review-runtime.sh \
  --target <local-measurement-target.json> \
  --event-file <terminal-events.jsonl> \
  --control-file <full-review-rerun-control.json> \
  --policy-file <capability-policy.json> \
  --repo-worktree <reviewed-worktree>
```

It snapshots and validates a closed `kc-pr-flow.review-benchmark-pair/v1` corpus and emits a deterministic `kc-pr-flow.review-benchmark-report/v1` with one ordered promotion report. Each pair recomputes the exact-head review key. Each arm recomputes candidate fingerprints and run-bound candidate IDs, then `content_sha256` over canonical behavior, lanes, candidates, findings, uncertain candidate refs, and usage, followed by `receipt_id = sha256(run_id|review_key|content_sha256)`. Expected and observed findings must resolve through candidates with the same evidence hash before recall is scored.

Promotion is fail-closed and ordered: G1 valid bound inputs, G2 complete required capability coverage, G3 external behavior parity, G4 zero lost expected must-fix findings, then G5 efficiency. G5 branch A requires complete same-provider/scope reported usage and median token reduction of at least 20%. Branch B requires median local terminal-collation cost no greater than 60% of a designed full rerun.

Branch B uses one optional corpus-owned `local-measurement-binding/v1`. The binding covers the raw terminal artifact SHA, recomputed decision SHA, `full-review-rerun-control/v1` SHA, treatment and control units, `canonical-artifact-bytes/v1`, and a canonical binding SHA. The control receipt is captured from the designed full rerun and records the sanitized full-review artifact SHA and its canonical byte units. `measure-local` safe-snapshots the raw receipt and control, invokes only fresh `rehydrate-interactive`, counts the canonical decision bytes, and emits zero model and remote calls. It does not invoke replay as a full-rerun substitute. The scorer independently rechecks the decision, producer, and measurement-binding hashes and requires every observation field to equal the paired binding, so a caller-resealed self-hash or arbitrary unit value is ineligible. Later gates cannot repair an earlier failure.

## Failure policy

Normal receipt mutation is fail closed: unavailable safe-I/O support, unsafe storage, invalid input, noncontiguous state, active locks, or integrity failures cannot change accepted state. Rejected append input is observable through status codes and metadata-only quarantine. Read-only validation or replay failures report errors or typed observer status without creating quarantine artifacts.

The production shadow seam is deliberately fail open because it has no behavioral authority. An unset gate performs no runtime call. When enabled, a failed dependency, invalid receipt, stale head, missing state, or observer error may produce one diagnostic outside the review body, then the byte-identical legacy draft, comments, options, event, confirmation, and posting flow continue. Shadow status must never cause a retry, another model dispatch, a content rewrite, or a GitHub mutation.

Typed mode is fail closed within the selected invocation. A validated closed decision is primary
typed authority and may require REQUEST_CHANGES. If decision production is invalid, only a complete
`confirmed-blocker-evidence/v1` receipt bound to the exact repository, PR, base, head, config,
review key, and run may preserve independently confirmed blockers and pass a decisionless
REQUEST_CHANGES post gate. Missing, malformed, bare-array, hash-drifted, or identity-drifted
evidence produces COMMENT with no blockers. Evidence inconsistent with a valid decision
invalidates the whole typed confirmation. Typed state cannot approve by falling back to legacy.
Both modes still require the existing human confirmation and a valid closed post-gate receipt
before any GitHub action.

## Operational inspection

Use `validate` to diagnose individual envelopes. Use `show` before trusting a receipt because it also enforces the authoritative lifecycle; use `replay` when the complete typed projection is needed. Quarantine intentionally cannot recover rejected input: diagnose from its bounded reason, input hash, byte count, and timestamp. A moved head or configuration change requires a new exact-head review identity.

## Once-only posting (increment 2.3)

`scripts/review-post.sh` is the only kc-pr-flow component with posting, reconcile, or network authority; `review-runtime.sh` stays as described above — it records and replays the five reserved events but never posts. `review-post.sh` reuses the runtime's event log, safe-I/O, reservation locks, and idempotent-append convergence for its own posting-lifecycle run (`post` / `resume` / `gc`), started fresh per posting attempt rather than reusing a shadow receipt's run.

Protocol (durable-before-mutate, reconcile-before-retry): `run.started -> head.observed -> authorization.granted -> post.intent` land before any network call; the POST is then classified `posted` / `failed` (definite) or `ambiguous` (timeout, network drop, 5xx, or unknown — the pending payload stays durable, no blind retry). On resume, an intent lacking a terminal result reconciles via `GET .../reviews`, matching an embedded `<!-- kc-pr-flow-post-receipt: <idempotency_key> -->` marker in the caller's own review body; a match means the earlier POST landed (`post.result{outcome: posted_reconciled}`, no second POST). `idempotency_key = sha256(review_key|commit_id|payload_sha256)`, so a moved head or changed payload can never collide with a prior post's key — either invalidates the run (`run.invalidated{reason: head_moved | payload_changed | identity_changed}`) instead of posting the stale payload.

A retry is licensed only by a reconcile read that **positively confirms** remote state, because the failure being defended against is a POST that landed while its response was lost. Three rules follow. (1) A `list` response that is not a reviews array of objects, or whose marker scan exits nonzero even after emitting a candidate id, is never read as "marker absent" or "marker found"; it fails closed (`ambiguous{reason: reconcile_unavailable}`, pending kept, no POST or further retry). (2) An absent marker on a *usable* list only proves "never landed" once `KC_PR_FLOW_RECONCILE_CONFIRM_SECONDS` (default 60) has elapsed since that run's `post.intent`: GitHub's review list is read-after-write eventually consistent, so inside that window an absent marker is indistinguishable from lag and resume reports `ambiguous{reason: reconcile_unconfirmed}` rather than retrying. A later resume past the window retries the identical payload once, then re-reconciles. (3) The marker match deliberately ignores review author — `idempotency_key` already pins the exact payload, while the login a token posts under (user vs bot vs app slug) is not knowable to the caller, so matching on it would turn an identity mismatch into a duplicate review.

Exactly-once also has to survive a plain re-invocation, not only a crash-resume, so `post` reconciles against the remote marker *before* its own POST and settles as `posted_reconciled` when the identical payload is already live. That covers a prior run which reached terminal `posted` and therefore has no pending payload left for the skill's pending-based rediscovery scan to find. Rule (1) governs that pre-POST read with no exception: an unusable body or failed marker scan makes `post` fail closed exactly as `resume` does (`ambiguous{reason: reconcile_unavailable}`, pending kept, no POST). An earlier revision let `post` proceed on local silence instead — no other run for the PR having recorded a `post.intent` for the same idempotency key — but that argument holds only inside a single durable state root. A wiped or reconfigured state directory, a different machine, or a stateless runner leaves the local check blind, and an unusable list simultaneously hides the marker that would have caught the duplicate. The refusal sits *after* the local consultation, so local durable state still wins wherever it can positively decide: a prior run that reached terminal `posted` settles as `posted_reconciled`, and an unsettled prior attempt still reports `ambiguous{reason: prior_attempt_unsettled}`. Only the case with no positive confirmation from either source is refused, so the path to the POST is a reviews array of objects whose marker scan exits zero with no match and no local intent for this payload. The shipped `gh` adapter produces this element shape; custom `KC_PR_FLOW_POST_TRANSPORT` implementations and future adapters receive the same fail-closed checks at fresh post, resume, and post-retry reconciliation. A `head` response that does not carry a 40-hex `head_sha` is likewise a transport error, never compared against the reviewed head — misreading a shape-invalid response as `head_moved` would silently discard a postable review. `gc` validates its clock input for the same class of reason: a non-numeric `--now-epoch` made the within-window comparison error out and read as false, expiring evidence still inside its retention window.

The pending payload (`kc-pr-flow.pending-post/v1`) is a closed schema — `schema`, `review_key`, `run_id`, `commit_id`, `event`, the serialized `payload` (`body` + `comments`), `payload_sha256`, `idempotency_key`, `authorized_at`, `expires_at` — written mode `0600` in a mode-`0700` run dir via private-temp-plus-rename. A failed, unreconciled pending payload expires after `KC_PR_FLOW_PENDING_RETENTION_SECONDS` (default 7 days / 604800); `gc` never removes a pending payload that is still within its window and lacks a terminal result, since that is exactly the evidence needed to reconcile an uncertain remote result later.

`KC_PR_FLOW_ONCE_ONLY_POST` (default off) gates only `post` (fresh authorization + intent) — absence denies every caller, daemon or interactive alike, so a daemon iteration with no explicit preauthorization takes this path zero times by default. `resume` and `gc` are never gated by this flag: rolling back (unsetting it) disables the new path for fresh invocations but never deletes pending-payload files or receipt events, so an uncertain remote result from a prior new-path POST stays reconcilable.

**Autonomous authorization.** A caller with no human at §6c presents `kc-pr-flow.autonomous-post-gate/v1` instead of the interactive receipt, because `human_confirmed` must stay a claim only the human path can make. The autonomous gate has no such field, a closed key set (`authorized_by`, `effective_event`, `head_sha`, `review_key`, `schema`) that refuses one being smuggled in, and requires `authorized_by == "daemon"`. Unlike the interactive gate it must name the review it authorizes: `review_post_gate_valid` compares `review_key` and `head_sha` against the request and refuses a mismatch, because a replayed or copied autonomous gate has nobody present to notice it being applied to the wrong PR or an old head. It is produced by `review_autonomous_post_gate`, which validates its own output, and autonomous posting is reachable only through the once-only path — so with `KC_PR_FLOW_ONCE_ONLY_POST` off, an autonomous gate authorizes nothing.

This increment intentionally has no adaptive lane scheduling, model routing, crash-safe lock recovery and PID-reuse handling, predecessor-lineage verification, or append/compaction performance work — those remain deferred. The autonomous gate above is authorization and binding only: it carries **no event ceiling and no expiry**, and nothing yet rechecks a moved head immediately before an autonomous post or refuses one whose typed decision reports required coverage gaps. Those remain deferred, so today the autonomous path is bounded by what a gate may name, not by a full preauthorization contract.
