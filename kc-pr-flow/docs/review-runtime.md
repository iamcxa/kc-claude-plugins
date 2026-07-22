# Shadow Review Runtime

The shadow review runtime lets maintainers observe and measure `kc-pr-review` without changing the review users see or the action posted to GitHub. It is off by default and safe to disable at any time.

This first increment is observation and measurement only. It does not adapt lane scheduling, route models, choose findings or verdicts, post reviews, resume interrupted execution, or garbage-collect state.

## Prerequisites

- Bash 3.2 or newer
- `jq`
- Python 3.8 or newer with `O_NOFOLLOW` and `O_CLOEXEC`
- `shasum` or `sha256sum`
- Git for local `git_blob` evidence verification
- a writable user-local state directory

The runtime itself does not call models, the network, or GitHub. Python provides fail-closed safe I/O: every runtime file is read from one no-follow regular-file descriptor into a bounded private snapshot only when its file identity remains stable. Missing support, symlinks, path replacement, concurrent mutation, oversize data, duplicate JSON keys, unsafe integers, or impossible UTC dates stop runtime collection before accepted-state mutation. The review skill still performs its existing read-only head checks and retains all confirmation and posting authority.

Run the CLI examples below from the `kc-pr-flow` plugin root.

## Enable shadow observation

Enable the single post-collation observer seam for the current process:

```bash
export KC_PR_FLOW_REVIEW_SHADOW=on
```

Only the exact value `on` enables it. Unset, empty, and unknown values are off. The seam runs after the legacy review body, comments, event modifiers, and confirmation options are final, but before the existing user confirmation gate.

When enabled, the skill performs a fresh read-only exact-head check. A moved head, failed check, invalid receipt, or local runtime failure skips observation and leaves the legacy review byte-identical. Shadow success also cannot change the review.

The seam serializes exactly one closed `ShadowObservation/v1` (`kc-pr-flow.shadow-observation/v1`) after the legacy body, inline comments, event, options, confirmation input, and GitHub-call log are frozen. It contains only exact-head identity, six hashes of those frozen artifacts, typed lane/candidate observations, evidence pointers and hashes, synthesis, uncertainty, and usage provenance. Unknown fields, excerpts, prompts, diffs, comments, rationale, provider raw text, and other opaque values are rejected. The collector reports `observed` only after it emits and replays a complete lane/candidate/synthesis/`run.finished` lifecycle; all other outcomes are typed `not_observed` diagnostics. If collection fails after `run.started`, an incomplete diagnostic run may remain, but it is never observed or authoritative; increment 2.3 owns recovery.

State defaults to `${XDG_STATE_HOME:-$HOME/.local/state}/kc-pr-flow`. To isolate an evaluation:

```bash
export KC_PR_FLOW_STATE_DIR="$PWD/.tmp/kc-pr-flow-state"
```

Use a private, unshared directory and do not commit it.

## Inspect a receipt

First inventory candidate receipts for one PR. This procedure follows the runtime's state-root
precedence, refuses an unsafe root, does not follow directory symlinks, handles spaces in paths, and
prints identity from `show` without selecting a receipt. Run it from the plugin root after replacing
the PR number:

```bash
PR_NUMBER='<positive-pr-number>'

if ! [[ "$PR_NUMBER" =~ ^[1-9][0-9]*$ ]]; then
  printf 'invalid PR number\n' >&2
  exit 2
fi

if [ -n "${KC_PR_FLOW_STATE_DIR:-}" ]; then
  STATE_ROOT="$KC_PR_FLOW_STATE_DIR"
elif [ -n "${XDG_STATE_HOME:-}" ]; then
  STATE_ROOT="$XDG_STATE_HOME/kc-pr-flow"
else
  if [ -z "${HOME:-}" ]; then
    printf 'HOME is required to resolve the default state root\n' >&2
    exit 2
  fi
  STATE_ROOT="$HOME/.local/state/kc-pr-flow"
fi

if [ ! -d "$STATE_ROOT" ] || [ -L "$STATE_ROOT" ]; then
  printf 'unsafe or missing state root: %s\n' "$STATE_ROOT" >&2
  exit 2
fi

FOUND=0
while IFS= read -r -d '' EVENT_FILE; do
  RUN_DIR="${EVENT_FILE%/events.jsonl}"
  PR_DIR="${RUN_DIR%/*}"
  REPOSITORY_DIR="${PR_DIR%/*}"
  REPOSITORY_KEY="${REPOSITORY_DIR##*/}"

  if ! [[ "$REPOSITORY_KEY" =~ ^[0-9a-f]{64}$ ]] ||
    [ ! -d "$REPOSITORY_DIR" ] || [ -L "$REPOSITORY_DIR" ] ||
    [ ! -d "$PR_DIR" ] || [ -L "$PR_DIR" ] ||
    [ ! -d "$RUN_DIR" ] || [ -L "$RUN_DIR" ] ||
    [ ! -f "$EVENT_FILE" ] || [ -L "$EVENT_FILE" ]; then
    continue
  fi

  if ! SHOW_OUTPUT="$(bash scripts/review-runtime.sh show --event-file "$EVENT_FILE")"; then
    printf 'invalid receipt: %q\n' "$EVENT_FILE" >&2
    continue
  fi

  RUN_ID="$(printf '%s' "$SHOW_OUTPUT" | jq -r '.run.run_id')" || continue
  HEAD_SHA="$(printf '%s' "$SHOW_OUTPUT" | jq -r '.run.head_sha')" || continue
  REVIEW_KEY="$(printf '%s' "$SHOW_OUTPUT" | jq -r '.run.review_key')" || continue
  printf 'run_id=%s\nhead_sha=%s\nreview_key=%s\npath=%q\n\n' \
    "$RUN_ID" "$HEAD_SHA" "$REVIEW_KEY" "$EVENT_FILE"
  FOUND=$((FOUND + 1))
done < <(find "$STATE_ROOT" -mindepth 4 -maxdepth 4 -type f \
  -path "*/pr-$PR_NUMBER/run-*/events.jsonl" -print0)

if [ "$FOUND" -eq 0 ]; then
  printf 'no valid receipts found for PR %s\n' "$PR_NUMBER" >&2
fi
```

Choose only an entry whose `head_sha` and `review_key` match the exact final review inputs. When the
collector returned a `run_id`, require that match too. If more than one entry still matches, stop and
obtain the intended run ID; do not guess the newest by path, modification time, or lexical order.

After identifying the exact managed event log, use its printed path below:

```bash
EVENT_FILE="<state-root>/<repository-key>/pr-<number>/run-<id>/events.jsonl"

bash scripts/review-runtime.sh validate --event-file "$EVENT_FILE"
bash scripts/review-runtime.sh show --event-file "$EVENT_FILE" | jq .
```

`validate` checks each envelope and hash independently; passing it does not prove cross-event lifecycle validity. `show` additionally validates authoritative chronological relationships and returns exact-head identity plus aggregate counts. Use `replay` when lane, candidate, finding, uncertainty, and usage objects are needed:

```bash
bash scripts/review-runtime.sh replay --event-file "$EVENT_FILE" | jq .
```

For a read-only exact-head observation:

```bash
bash scripts/review-runtime.sh observe \
  --event-file "$EVENT_FILE" \
  --expected-head "<40-character-reviewed-head>" \
  --expected-review-key "<64-character-review-key>"
```

Do not edit accepted JSONL by hand. The event envelope and every event payload are closed. The only same-major extension is a closed hash-only record containing namespace, key, value SHA-256, and byte count; it cannot affect replay. Rejected append input creates metadata-only quarantine containing its reason, input SHA-256, byte count, and timestamp, never the rejected bytes. Read-only validation or replay of an already-invalid receipt is not quarantined. Unsafe storage or inconsistent accepted state fails closed.

## Build an exact configuration hash

The skill computes this automatically. For a reproducible local probe:

```bash
CONFIG_HASH="$(bash scripts/review-runtime.sh config-hash \
  --agent-tier standard \
  --pr-archetype bugfix \
  --full-pass false \
  --probe-required true \
  --cross-model false \
  --noise-filter false \
  --capabilities correctness,tests)"
printf '%s\n' "$CONFIG_HASH"
```

Capabilities are sorted and deduplicated. Use only effective normalized settings; never hash prompts, diffs, bodies, comments, or model output.

## Verify evidence and usage

Evidence is stored as typed pointers and hashes, not excerpts. Verify a `git_blob` pointer against a matching local GitHub repository:

```bash
bash scripts/review-runtime.sh verify-evidence \
  --pointer-json "<sanitized-pointer.json>" \
  --repo "<local-worktree>" | jq .
```

Other pointer kinds currently return typed unavailable status.

Compare two usage observations with:

```bash
bash scripts/review-runtime.sh compare-usage \
  --left-json "<baseline-usage.json>" \
  --right-json "<shadow-usage.json>" | jq .
```

A comparison is available only when both sides are complete provider-reported measurements from the same provider family and scope. Estimated, unavailable, cross-provider, cross-scope, partial, or null usage is unavailable, never zero.

## Score paired runs

The repository fixture demonstrates the closed sanitized corpus schema. Score a corpus locally:

```bash
bash scripts/review-runtime-benchmark.sh score \
  --corpus test/fixtures/review-runtime/paired-runs.jsonl | jq .
```

Before scoring, the benchmark recomputes the exact-head review key, every candidate fingerprint and run-bound candidate ID, and each arm's canonical receipt authority:

```text
content_sha256 = sha256(canonical behavior, lanes, candidates, findings, uncertain candidate refs, and usage)
receipt_id = sha256(run_id|review_key|content_sha256)
```

Expected and observed findings must resolve through a canonical candidate carrying the same evidence hash. A removed candidate, drifted evidence hash, or stale receipt hash makes the corpus invalid rather than inflating recall. The deterministic report then presents measures in this order:

1. Evidence recall against explicit expected finding IDs. Model silence is not truth.
2. Expected capability coverage and each lane's terminal status.
3. External behavior parity through body, event, and payload hashes.
4. Finding and candidate stability, including disagreements and uncertain candidates.
5. Usage comparability under the provenance rule above.

The report is a measurement artifact, not an improvement claim or release gate. Establish a trustworthy paired corpus before setting thresholds.

## Deferred capabilities

This shadow increment deliberately stops at observation and measurement. Increment 2.3 owns crash-safe lock recovery and PID-reuse handling, verified predecessor lineage, append/compaction performance, resume, retention/garbage collection, once-only posting, remote reconciliation, and daemon mutation. Do not interpret a shadow receipt, reserved event name, or successor hint as authority for any of those actions.

## Roll back

Disable future observation without deleting evidence:

```bash
unset KC_PR_FLOW_REVIEW_SHADOW
```

You may also set the variable to any value other than `on`. Existing receipts remain available for validation and paired analysis. Keeping them makes rollback reversible and preserves evidence for debugging.

## Troubleshooting

| Symptom | Meaning and action |
|---|---|
| No receipt appears | Confirm the gate is exactly `on`; Python 3.8+, `jq`, and a SHA-256 tool are available; the state root is writable; and the final review reached the shadow seam. Inspect the typed `not_observed` reason. The review itself should still continue. |
| `exact_head_mismatch` | The PR moved after review collation. Do not reuse the receipt; refresh and review the unseen delta or rewritten head. |
| `review_key_mismatch` | Repository, PR, base, head, or effective configuration differs. Recompute the canonical configuration and use the matching run. |
| `invalid_receipt` | Run `validate` for envelope diagnostics and `show` or `replay` for lifecycle diagnostics. Inspect metadata-only quarantine only when the invalid record came through rejected append input; read-only inspection does not create quarantine, and rejected bytes are intentionally unavailable. |
| append reports `blocked` | Another live owner holds the run reservation, storage is unsafe, the accepted log is inconsistent, or a size limit was reached. Preserve state and investigate; do not bypass the lock. |
| usage is unavailable | One side is missing, estimated, incomplete, cross-provider, or cross-scope. Collect comparable provider-reported data rather than substituting zero. |
| evidence is unavailable or mismatched | Confirm the local GitHub repository identity, object and path, blob type, and content hash. A mismatch cannot support a finding. |

For schemas, identities, storage rules, command contracts, and failure semantics, see the [normative runtime reference](../reference/review-runtime.md).
