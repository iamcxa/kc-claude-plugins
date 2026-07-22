# Review Runtime Contract

This reference defines the current `kc-pr-review` shadow receipt runtime. It is a compatibility boundary for maintainers and adapter authors. The runtime records and inspects review observations; it does not choose findings, verdicts, confirmation options, or GitHub mutations.

## Runtime boundary

The implementation is source-safe Bash 3.2 plus `jq`. Sourcing either runtime script declares functions without executing its CLI or changing the caller's options, traps, working directory, variables, or `umask`.

The runtime has no network, model, GitHub, posting, authorization, resume, or garbage-collection authority. In this increment, the legacy `kc-pr-review` flow remains authoritative for review analysis, rendering, confirmation, and posting.

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

The canonical configuration schema is `kc-pr-flow.review-config/v1`. It contains a sorted, deduplicated capability array and these effective modes:

| Field | Values | Default |
|---|---|---|
| `agent_tier` | `lite`, `standard`, `full` | `lite` |
| `pr_archetype` | `bugfix`, `cross_stack`, `docs`, `feature`, `mixed`, `refactor`, `style` | `mixed` |
| `full_pass` | boolean | `false` |
| `probe_required` | boolean | `false` |
| `cross_model` | boolean | `false` |
| `noise_filter` | boolean | `false` |

`config-hash` serializes the normalized object with `jq -S -c` and hashes those compact bytes without a trailing newline. Prompts, diffs, rendered review content, comments, and provider output are not configuration inputs.

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
      event.jsonl
      metadata.json
```

Managed directory components must be real directories, never symlinks. Run directories are mode `0700`; accepted event logs are mode `0600`. The default accepted-log size limit is 16 MiB and can be lowered with `KC_PR_FLOW_MAX_EVENTS_BYTES`.

Publication uses private temporary files or directories followed by rename. Appends validate each envelope plus the existing log's immutable run identity, hashes, and contiguous sequence; they do not enforce lane chronology. An append reserves the run at the PR directory, builds the next complete log privately, and renames it over the accepted log. Concurrent duplicate appends converge on one accepted event; conflicting or blocked appends do not modify accepted bytes.

Reservation and quarantine locks are owned `mkdir` locks with one `owner.pid`. A live or malformed owner fails closed with temporary-failure status. A provably dead owner is reclaimed once. `KC_PR_FLOW_RESERVATION_WAIT_ATTEMPTS` controls the bounded reservation wait.

Only rejected append input is copied to content-addressed quarantine with a typed reason. Read-only `validate`, `replay`, `show`, and `observe` operations do not quarantine an already-invalid receipt. Quarantine event and metadata files are mode `0400`, and their directory is `0500`. Complete matching quarantine publication is idempotent; incomplete or conflicting artifacts fail closed. The default combined quarantine-record limit is 4 MiB and can be lowered with `KC_PR_FLOW_MAX_QUARANTINE_BYTES`.

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
  -> synthesis.finished (optional while observation is partial)
```

`lane.started` carries a provider-neutral `kc-pr-flow.review-task/v1`. `finding.observed` carries a `kc-pr-flow.review-candidate/v1` whose ID binds run, lane, ordinal, and evidence hash. `lane.finished` carries a `kc-pr-flow.lane-result/v1` and must account for exactly the candidates observed for that lane. `synthesis.finished` carries unique `kc-pr-flow.review-finding/v1` records plus uncertain candidate IDs; together they must partition every observed candidate exactly once. Finding IDs bind the review key and constrained merge key.

Enforcement is intentionally layered. `validate` checks individual event envelopes and hashes, not
cross-event ordering. `append` additionally protects accepted run identity and contiguous sequence,
but can accept envelopes whose lane order is not replayable. Only `replay` and `show` enforce the
authoritative chronological lifecycle and candidate/finding relationships; `observe` inherits that
enforcement by delegating to replay. A log is not trustworthy as a receipt merely because
`validate` or `append` accepted every line.

The v1 validator also recognizes `head.observed`, `authorization.granted`, `post.intent`, `post.result`, `run.invalidated`, and `run.finished` with empty payloads. They are reserved envelope types in this increment and do not grant the shadow runtime the corresponding authority.

Payload schemas are closed. Unknown event types, unsupported schema majors, missing fields, identity or hash mismatches, and raw or opaque payload fields fail individual validation and are quarantined when submitted through append. Mixed-run identity or noncontiguous sequence blocks accepted-log mutation. Chronologically invalid lane or synthesis relationships fail `replay`/`show` without creating quarantine. Additive envelope fields participate in the integrity hash.

## Provider-neutral observations

Review tasks describe capability and lane identity, exact head, and optional provider hint. Lane results describe terminal status (`succeeded`, `failed`, or `unavailable`), the exact candidate set, optional provider family, and a usage observation. Provider adapters cannot own lifecycle, synthesis, verdict, authorization, or posting.

Usage records have `input_tokens`, `output_tokens`, `total_tokens`, `provenance`, `provider_family`, and `scope`. Provenance is `reported`, `estimated`, or `unavailable`; scope is `lane` or `run`. Unavailable usage requires null token values. A comparison is available only when both observations are complete, provider-reported, from the same non-null provider family, and at the same scope. Missing or incomparable usage is never interpreted as zero.

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
| `replay --event-file FILE` | Validate a complete authoritative log, enforce chronological relationships, and rebuild the deterministic `review-projection/v1`. |
| `show --event-file FILE` | Return a compact `review-summary/v1` with exact run identity and lane, candidate, finding, uncertain, and usage counts. |
| `config-hash ...` | Normalize the effective v1 review configuration and return its canonical hash. Options are `--agent-tier`, `--pr-archetype`, `--full-pass`, `--probe-required`, `--cross-model`, `--noise-filter`, and comma-separated `--capabilities`; omitted options use the defaults above. |
| `observe --event-file FILE --expected-head SHA --expected-review-key HASH` | Read-only replay plus exact-head/key check. Returns typed `observed` or `not_observed` status and never mutates the log. |
| `shadow ...` | Best-effort production seam. `--enabled` overrides `KC_PR_FLOW_REVIEW_SHADOW`. When enabled it accepts `--head-check-status`, `--live-head`, `--repo`, `--pr`, `--base`, `--head`, `--config-hash`, optional `--occurred-at`, and optional `--event-file`. It reuses a supplied exact-head log or creates one identity-only run and calls the observer once. Every dependency or observation failure fails open. |
| `verify-evidence --pointer-json FILE --repo DIR` | Verify one pointer from a private snapshot against the local repository. |
| `compare-usage --left-json FILE --right-json FILE` | Compare two private usage snapshots under the provenance rules above. |

The same operations are available as `review_runtime_*` functions after sourcing the script. Snapshot guarantees are operation-specific: `replay` and therefore `show`/`observe`, evidence verification, usage comparison, and paired benchmark scoring use private regular-file snapshots for their complete read. `validate` and `append` stream regular-file candidate input line by line and do not promise one immutable input snapshot; `-` is first copied to a temporary input file. Append still builds the accepted next log privately and publishes it with atomic rename.

The paired scorer is a separate source-safe CLI:

```bash
bash scripts/review-runtime-benchmark.sh score --corpus <sanitized-pairs.jsonl>
```

It validates a closed `kc-pr-flow.review-benchmark-pair/v1` corpus and emits a deterministic `kc-pr-flow.review-benchmark-report/v1`. Measurement order is evidence recall, capability coverage, external behavior parity, finding/candidate stability, then usage comparability. The scorer has no model or release-gate authority.

## Shadow failure policy

Normal receipt mutation is fail closed: unsafe storage, invalid input, noncontiguous state, active locks, or integrity failures cannot change accepted state. Rejected append input is observable through status codes and quarantine. Read-only validation or replay failures report errors or typed observer status without creating quarantine artifacts.

The production shadow seam is deliberately fail open because it has no behavioral authority. An unset gate performs no runtime call. When enabled, a failed dependency, invalid receipt, stale head, missing state, or observer error may produce one diagnostic outside the review body, then the byte-identical legacy draft, comments, options, event, confirmation, and posting flow continue. Shadow status must never cause a retry, another model dispatch, a content rewrite, or a GitHub mutation.

## Operational inspection

Use `validate` to diagnose individual envelopes. Use `show` before trusting a receipt because it also enforces the authoritative lifecycle; use `replay` when the complete typed projection is needed. Preserve rejected append bytes from quarantine for diagnosis, but do not copy them into accepted logs. A moved head or configuration change requires a new exact-head review identity.

This increment intentionally has no adaptive lane scheduling, model routing, resumable execution, retention/garbage collection, posting intent, remote reconciliation, or once-only GitHub mutation.
