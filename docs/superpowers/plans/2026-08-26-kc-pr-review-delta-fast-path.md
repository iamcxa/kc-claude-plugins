# kc-pr-review Delta Fast Path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Phase 1's exact-head `initial`/`delta`/`resolve` router, trusted predecessor receipt, default-off skill wiring, and promotion evidence for a four-minute post-fix path with 100% known-finding recall.

**Architecture:** A new source-safe Bash helper replays the existing typed review runtime to mint and verify a closed delta receipt, then inspects local Git ancestry and the unseen range to emit an advisory review plan. The existing runtime adds local monotonic timing receipts; a separate scorer promotes the feature only after ordered identity, coverage, recall, precision, behavior, and latency gates pass. Posting stays entirely in `review-post.sh` and keeps its current exact-head and human-authorization contracts.

**Tech Stack:** Bash 3.2, `jq`, Python 3.8+ safe-I/O helper, local Git, JSON/JSONL fixtures, GitHub Actions, ShellCheck v0.9.0.

**Spec:** `docs/superpowers/specs/2026-08-26-kc-pr-review-latency-design.md`

## Global Constraints

- Implement Phase 1 only. Phases 2–6 remain promotion-gated follow-up work.
- `KC_PR_FLOW_DELTA_FAST_PATH=on` is the only enabling value; unset or any other value keeps the current full-review route.
- `ReviewDeltaReceipt/v1`, `ReviewPlanDecision/v1`, and `ReviewTiming/v1` use closed key sets and canonical `jq -S -c` hashing.
- A predecessor is trusted only after `review-runtime.sh replay` succeeds and identity, review key, receipt content hash, base, config, and ancestry all match.
- Missing, malformed, unsafe, stale, non-ancestor, rewritten, changed-base, config-incompatible, or unknown state selects `initial`.
- A required coverage gap caps authority at `COMMENT`; no script may emit a semantic correctness, security, goal-achievement, or final review verdict.
- Known predecessor must-fix findings remain inherited until current-head evidence resolves them; silence is not resolution.
- Preserve Step 2.1 exact-head checks, Step 6a quote-the-line verification, Step 6c human confirmation, and Step 7 closed posting authority.
- `review-post.sh` remains the only posting/reconcile/network authority and is not modified by this plan.
- Feature commits do not edit plugin versions; release-please owns versioning.
- Stage explicit paths; never use `git add .`.
- Run CI's ShellCheck v0.9.0 against every changed review shell file before the final task commit.

## File map

| File | Responsibility |
|---|---|
| `kc-pr-flow/scripts/review-plan.sh` | Source-safe receipt producer/validator and exact-head mode router; no model, network, event, confirmation, or posting authority |
| `kc-pr-flow/scripts/review-plan.test.sh` | Bash 3.2 contract tests for receipt trust, routing, rollback, source safety, and PR #1693 replay |
| `kc-pr-flow/test/fixtures/review-plan/pr1693-replay.json` | Sanitized immutable lineage, findings, changed-path classes, and expected Phase 1 decision |
| `kc-pr-flow/scripts/review-runtime.sh` | Existing receipt authority plus bounded local monotonic timing commands |
| `kc-pr-flow/scripts/review-runtime.test.sh` | Timing schema, identity, monotonicity, file-safety, and no-network tests |
| `kc-pr-flow/scripts/review-latency-benchmark.sh` | Source-safe ordered Phase 1 promotion scorer; consumes bound control/treatment evidence only |
| `kc-pr-flow/scripts/review-latency-benchmark.test.sh` | Gate ordering, 100% recall, precision parity, 240-second ceiling, and mutation-resistance tests |
| `kc-pr-flow/test/fixtures/review-plan/phase1-promotion.jsonl` | Sanitized control/treatment pairs for Phase 1 promotion scoring |
| `kc-pr-flow/skills/kc-pr-review/SKILL.md` | Minimal default-off routing invocation before current triage; preserves all judgment and posting gates |
| `kc-pr-flow/reference/review-triage.md` | Mode semantics, focused-lane obligations, fallback, timing boundary, and user-visible triage output |
| `kc-pr-flow/reference/review-runtime.md` | Delta receipt, plan decision, timing schema, CLI, failure policy, and authority boundary |
| `kc-pr-flow/CLAUDE.md` | Maintainer checks and default-off fast-path contract |
| `.github/workflows/review-plan-tests.yml` | Narrow Phase 1 behavioral suite |
| `.github/workflows/review-runtime-tests.yml` | Routes timing-runtime changes to the existing runtime suite |
| `.github/workflows/review-evaluation-tests.yml` | Routes latency scorer/fixture changes to the evaluation suite |
| `scripts/review-ci-routing.test.py` | Fails closed when Phase 1 owners or commands are missing from CI routing |

---

### Task 1: Trusted delta receipt producer and validator

**Files:**
- Create: `kc-pr-flow/scripts/review-plan.sh`
- Create: `kc-pr-flow/scripts/review-plan.test.sh`

**Interfaces:**
- Consumes: `review_runtime_replay EVENT_FILE -> kc-pr-flow.review-projection/v1`, `review_runtime_sha256`, and `review_runtime_snapshot_regular_file` from `kc-pr-flow/scripts/review-runtime.sh:8-31,193-223,1823-1975`.
- Produces: `review_plan_build_receipt EVENT_FILE -> kc-pr-flow.review-delta-receipt/v1`, `review_plan_validate_receipt RECEIPT PROJECTION -> 0|nonzero`, and CLI `review-plan.sh receipt --event-file FILE`.
- Authority: read-only local projection. It cannot call `gh`, network tools, model CLIs, `review-post.sh`, or any runtime append/start command.

- [ ] **Step 1: Write the failing receipt-contract tests**

Create `review-plan.test.sh` with the repository's `PASS`/`FAIL` style and a `--case receipt-contract` filter. Build a complete terminal receipt in an isolated Git fixture using the same event constructors as `review-runtime.test.sh:473-570`, then assert this exact output shape:

```bash
receipt_out="$(bash "$PLAN" receipt --event-file "$terminal_events")"
assert_eq "receipt schema" "kc-pr-flow.review-delta-receipt/v1" \
  "$(jq -r '.schema' <<<"$receipt_out")"
assert_eq "receipt keys are closed" \
  "content_sha256,coverage_gap_refs,known_findings,predecessor,required_capabilities,schema" \
  "$(jq -r 'keys | sort | join(",")' <<<"$receipt_out")"
assert_eq "all terminal findings remain unresolved" "unresolved" \
  "$(jq -r '[.known_findings[].resolution_state] | unique | join(",")' <<<"$receipt_out")"
assert_eq "finding IDs come from replay" \
  "$(jq -r '.findings | map(.finding_id) | sort | join(",")' <<<"$projection")" \
  "$(jq -r '.known_findings | map(.finding_id) | sort | join(",")' <<<"$receipt_out")"
```

Add negative assertions for symlink/FIFO/oversized input, incomplete runtime lifecycle, duplicate JSON members, arbitrary `receipt_id`, changed `content_sha256`, changed `finding_id`, extra top-level/member keys, and missing evidence hashes. Stub `gh`, `curl`, `wget`, `ssh`, `codex`, and `agy` to exit 97 and assert the call ledger remains empty.

- [ ] **Step 2: Run RED and record the expected failure**

Run:

```bash
bash kc-pr-flow/scripts/review-plan.test.sh --case receipt-contract
```

Expected: FAIL because `review-plan.sh` and `review_plan_build_receipt` do not exist. Do not weaken the assertions.

- [ ] **Step 3: Implement the source-safe receipt boundary**

Create `review-plan.sh` with declarations only when sourced and this structure:

```bash
#!/usr/bin/env bash
# review-plan.sh — read-only exact-head planning for kc-pr-review.

review_plan_source_runtime() {
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || return 69
  # shellcheck source=/dev/null
  . "$here/review-runtime.sh" || return 69
}

review_plan_content_sha256() {
  jq -S -c 'del(.content_sha256)' | review_runtime_sha256
}

review_plan_build_receipt() (
  local event_file="$1" projection projection_hash receipt_id canonical content_sha256
  projection="$(review_runtime_replay "$event_file")" || return 3
  jq -e '.lifecycle.complete == true' >/dev/null <<<"$projection" || return 3
  projection_hash="$(printf '%s' "$projection" | jq -S -c . | review_runtime_sha256)" || return
  receipt_id="$(printf '%s' "$(jq -r '.run.run_id + "|" + .run.review_key' <<<"$projection")|$projection_hash" |
    review_runtime_sha256)" || return
  canonical="$(jq -S -c --arg receipt_id "$receipt_id" '
    .run as $run |
    {
      schema:"kc-pr-flow.review-delta-receipt/v1",
      predecessor:{
        repository:$run.repository,pr_number:$run.pr_number,
        base_sha:$run.base_sha,head_sha:$run.head_sha,
        config_hash:$run.config_hash,review_key:$run.review_key,
        run_id:$run.run_id,
        receipt_id:$receipt_id
      },
      known_findings:(.findings | map({
        finding_id,claim_key,
        evidence_sha256:.evidence.content_sha256,
        path,side,resolution_state:"unresolved"
      }) | sort_by(.finding_id)),
      required_capabilities:(.lanes | map(.capability) | sort | unique),
      coverage_gap_refs:[]
    }' <<<"$projection")" || return 3
  content_sha256="$(printf '%s' "$canonical" | review_runtime_sha256)" || return
  jq -S -c --arg hash "$content_sha256" '. + {content_sha256:$hash}' <<<"$canonical"
)
```

Implement `review_plan_validate_receipt` with one closed `jq -e` validator plus recomputation of:

```text
review_key = sha256(repository|pr_number|base_sha|head_sha|config_hash)
projection_content_sha256 = sha256(jq -S -c replay projection)
receipt_id = sha256(run_id|review_key|projection_content_sha256)
content_sha256 = sha256(canonical receipt without content_sha256)
```

Validate safe tokens, 40/64-hex fields, normalized relative paths, `LEFT|RIGHT|FILE`, sorted unique arrays, `resolution_state == unresolved`, and equality against the fresh replay projection. Never trust a matching self-hash without checking projection-derived fields.

- [ ] **Step 4: Implement the receipt CLI and source-safety gate**

Use explicit option parsing and this command boundary:

```bash
review_plan_main() {
  local command="${1:-}"
  [ "$#" -gt 0 ] && shift
  case "$command" in
    receipt) review_plan_main_receipt "$@" ;;
    decide) review_plan_main_decide "$@" ;;
    *) review_plan_usage; return 2 ;;
  esac
}

review_plan_source_runtime || return 69 2>/dev/null || exit 69
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  review_plan_main "$@"
fi
```

When sourced, preserve caller shell flags, umask, and working directory, matching the assertions in `review-runtime-benchmark.test.sh:643-647`.

- [ ] **Step 5: Run GREEN and regression suites**

Run:

```bash
bash kc-pr-flow/scripts/review-plan.test.sh --case receipt-contract
bash kc-pr-flow/scripts/review-runtime.test.sh --case evidence-binding
bash -n kc-pr-flow/scripts/review-plan.sh kc-pr-flow/scripts/review-plan.test.sh
```

Expected: all tests pass; no transport/model stub is called.

- [ ] **Step 6: Commit the independently reviewable receipt boundary**

```bash
git add kc-pr-flow/scripts/review-plan.sh \
  kc-pr-flow/scripts/review-plan.test.sh
git commit -m "feat(kc-pr-flow): add trusted review delta receipt"
```

---

### Task 2: Exact-head mode router and sanitized PR #1693 replay

**Files:**
- Modify: `kc-pr-flow/scripts/review-plan.sh` after the receipt functions from Task 1
- Modify: `kc-pr-flow/scripts/review-plan.test.sh` after `receipt-contract`
- Create: `kc-pr-flow/test/fixtures/review-plan/pr1693-replay.json`

**Interfaces:**
- Consumes: Task 1 `review_plan_validate_receipt`, exact `--repo/--pr/--base/--head/--config-hash`, safe local `--repo-worktree`, `--predecessor-events`, and `--delta-receipt`.
- Produces: `review_plan_decide REPO PR BASE HEAD CONFIG WORKTREE EVENTS RECEIPT -> kc-pr-flow.review-plan-decision/v1` and CLI `review-plan.sh decide ...`.
- Reason-code enum: `feature_disabled`, `missing_predecessor`, `invalid_predecessor`, `identity_mismatch`, `base_changed`, `config_changed`, `non_ancestor`, `ancestor_append`, `known_finding_delta`, `expanded_delta`, `unknown_delta`, `inherited_coverage_gap`.

- [ ] **Step 1: Add the sanitized PR #1693 replay fixture**

Create a public-safe manifest with immutable synthetic Git objects created by the test, not live PR text:

```json
{
  "schema": "kc-pr-flow.review-plan-replay/v1",
  "case_id": "pr1693-post-fix-shape",
  "repository": "datarecce/recce-cloud-infra",
  "pr_number": 1693,
  "commits": [
    {"name": "base", "files": {"src/parser.py": "def parse(value):\n    return value\n"}},
    {"name": "reviewed", "files": {"src/parser.py": "def parse(value):\n    return value.strip()\n"}},
    {"name": "fixed", "files": {
      "src/parser.py": "def parse(value):\n    return value.strip() or None\n",
      "tests/test_parser.py": "from src.parser import parse\n\ndef test_empty():\n    assert parse(' ') is None\n"
    }}
  ],
  "known_findings": [
    {"claim_key": "empty-input-contract", "path": "src/parser.py", "side": "RIGHT"}
  ],
  "expected": {
    "mode": "resolve",
    "reason_codes": ["trusted_predecessor", "ancestor_append", "known_finding_delta"],
    "required_capabilities": ["correctness", "test-coverage"],
    "event_ceiling": "APPROVE"
  }
}
```

The fixture is a shape replay, not a claim about the live PR's code. The test materializes all three commits, derives their SHAs, builds predecessor events from the reviewed commit, then calls `decide` on the fixed commit.

- [ ] **Step 2: Write failing routing and trust-boundary tests**

Add `--case mode-router` and `--case trust-boundary` with these assertions:

```bash
decision="$(KC_PR_FLOW_DELTA_FAST_PATH=on bash "$PLAN" decide \
  --repo "$repo_id" --pr 1693 --base "$base_sha" --head "$fixed_sha" \
  --config-hash "$config_hash" --repo-worktree "$fixture_repo" \
  --predecessor-events "$events" --delta-receipt "$receipt_file")"
assert_eq "PR1693 shape selects resolve" "resolve" "$(jq -r '.mode' <<<"$decision")"
assert_eq "resolve inherits finding IDs" "$finding_id" \
  "$(jq -r '.inherited_finding_ids | join(",")' <<<"$decision")"
assert_eq "router is advisory" "APPROVE" "$(jq -r '.event_ceiling' <<<"$decision")"
```

Cover these table cases exactly:

| Case | Expected mode | Expected ceiling |
|---|---|---|
| flag off | `initial` | `COMMENT` |
| missing receipt/events | `initial` | `COMMENT` |
| exact known path plus mechanically adjacent test | `resolve` | inherited ceiling |
| new unrelated path on ancestor append | `delta` | `COMMENT` until new required coverage completes |
| force-push/non-ancestor | `initial` | `COMMENT` |
| changed base or config | `initial` | `COMMENT` |
| inherited required gap | `delta` | `COMMENT` |
| unsafe worktree/symlink | `initial` | `COMMENT` |

Assert the output has only `schema`, `identity`, `mode`, `reason_codes`, `review_range`, `inherited_finding_ids`, `required_capabilities`, `event_ceiling`, and `fallback`.

- [ ] **Step 3: Run RED**

```bash
bash kc-pr-flow/scripts/review-plan.test.sh --case mode-router
bash kc-pr-flow/scripts/review-plan.test.sh --case trust-boundary
```

Expected: FAIL because `decide` is not implemented.

- [ ] **Step 4: Implement conservative Git and path classification**

Implement these functions with no network access:

```bash
review_plan_git_identity_valid() {
  local worktree="$1" head="$2"
  [ -d "$worktree/.git" ] || git -C "$worktree" rev-parse --git-dir >/dev/null 2>&1 || return 1
  [ "$(git -C "$worktree" cat-file -t "$head" 2>/dev/null)" = commit ]
}

review_plan_ancestor() {
  git -C "$1" merge-base --is-ancestor "$2" "$3"
}

review_plan_changed_paths() {
  git -C "$1" diff --name-status --find-renames=50% "$2..$3"
}
```

Classify `resolve` only when every changed path is either a known-finding path or a test/fixture that mechanically names/imports one known-finding module. Accept adjacency only when the test lives under `test`, `tests`, `__tests__`, or `fixtures` and `git show HEAD:path` contains the known module basename or import path as a fixed string. Rename, copy, binary, submodule, unsafe path, ambiguous import, or unknown status cannot select `resolve`.

For a trusted ancestor with any extra safe path, select `delta`, add `expanded_delta`, include `correctness` plus the predecessor required capabilities, and set `event_ceiling:COMMENT` until current-run coverage completes. Phase 1 does not implement shared inventory or risk-triggered specialists; current full-review security and specialist rules still apply after routing.

Build the decision with typed `jq --arg/--argjson`, sorted unique arrays, and `review_range.from_exclusive = predecessor.head_sha`, `to_inclusive = current head`. Validate the canonical review key for the current identity but do not manufacture a current runtime run or authorization receipt.

- [ ] **Step 5: Run GREEN, adversarial mutations, and source safety**

```bash
bash kc-pr-flow/scripts/review-plan.test.sh --case mode-router
bash kc-pr-flow/scripts/review-plan.test.sh --case trust-boundary
bash kc-pr-flow/scripts/review-plan.test.sh
bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision
```

Expected: all pass. Mutating any one identity field, receipt hash, finding evidence hash, ancestry edge, or fixture path either selects `initial`/`COMMENT` or rejects input; it never preserves `resolve`.

- [ ] **Step 6: Commit the router and replay**

```bash
git add kc-pr-flow/scripts/review-plan.sh \
  kc-pr-flow/scripts/review-plan.test.sh \
  kc-pr-flow/test/fixtures/review-plan/pr1693-replay.json
git commit -m "feat(kc-pr-flow): route trusted post-fix reviews"
```

---

### Task 3: Default-off skill wiring and minimal reference contract

**Files:**
- Modify: `kc-pr-flow/skills/kc-pr-review/SKILL.md:104-121,191-197,935-941`
- Modify: `kc-pr-flow/reference/review-triage.md:3-6,122-164`
- Modify: `kc-pr-flow/reference/review-runtime.md:13-50,165-185,209-227`
- Modify: `kc-pr-flow/CLAUDE.md:53-90,134-152`
- Modify: `kc-pr-flow/scripts/review-plan.test.sh`

**Interfaces:**
- Consumes: Task 2 `review-plan.sh decide` and `ReviewPlanDecision/v1`.
- Produces: one documented pre-triage routing seam. `initial` enters the current flow byte-for-byte; `delta` reviews the unseen range and all newly required capabilities; `resolve` dispatches one focused correctness lane and targeted verification while inheriting known finding IDs.
- Preserves: current goal-achievement judgment, quote gate, tests/probe where activated, draft structure, two head checks, Step 6c confirmation, and Step 7 posting receipt.

- [ ] **Step 1: Write failing skill/reference contract assertions**

Add `--case skill-wiring` to `review-plan.test.sh`:

```bash
assert_file_contains "$SKILL" 'KC_PR_FLOW_DELTA_FAST_PATH=on'
assert_file_contains "$SKILL" 'review-plan.sh decide'
assert_file_contains "$SKILL" 'mode == "initial"'
assert_file_contains "$SKILL" 'coverage gap.*COMMENT'
assert_file_contains "$SKILL" 'Step 6c'
assert_file_contains "$REFERENCE" 'kc-pr-flow.review-delta-receipt/v1'
assert_file_contains "$REFERENCE" 'kc-pr-flow.review-plan-decision/v1'
```

Also assert `review-plan.sh` contains none of `gh pr review`, `review-post.sh post`, `authorization.granted`, or `human_confirmed`.

- [ ] **Step 2: Run RED**

```bash
bash kc-pr-flow/scripts/review-plan.test.sh --case skill-wiring
```

Expected: FAIL because the approved mode router is not yet wired into the skill/reference.

- [ ] **Step 3: Add the minimal Step 2.2 routing seam**

Immediately after `SKILL.md` Step 2.1, add a concise `Step 2.2: Trusted Post-Fix Route` section with this executable shape:

```bash
REVIEW_MODE=initial
if [ "${KC_PR_FLOW_DELTA_FAST_PATH:-off}" = on ]; then
  if ! PLAN_JSON="$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/review-plan.sh" decide \
    --repo "$REPO" --pr "$PR_NUMBER" --base "$BASE_SHA" --head "$REVIEWED_HEAD_SHA" \
    --config-hash "$CONFIG_HASH" --repo-worktree "$REPO_WORKTREE" \
    --predecessor-events "$PREDECESSOR_EVENTS" --delta-receipt "$DELTA_RECEIPT")"; then
    REVIEW_MODE=initial
    PLAN_EVENT_CEILING=COMMENT
    PLAN_REASON=router_failed
  else
    REVIEW_MODE="$(jq -r '.mode' <<<"$PLAN_JSON")"
    PLAN_EVENT_CEILING="$(jq -r '.event_ceiling' <<<"$PLAN_JSON")"
    PLAN_REASON="$(jq -r '.reason_codes | join(",")' <<<"$PLAN_JSON")"
  fi
fi
```

The prose must state:

- missing predecessor inputs are normal and select `initial`;
- `resolve` dispatches one focused correctness reviewer and runs known-finding plus affected-test verification in parallel;
- `delta` reviews every unseen changed path and inherited finding, and new required coverage must terminally complete;
- current unconditional specialist rules remain unchanged in Phase 1;
- `event_ceiling` can only reduce authority;
- before a clean draft and before posting, Step 2.1 still rechecks the live head;
- the user still receives the full Step 6 draft and explicitly confirms at Step 6c.

Do not copy schema validators or shell helpers into `SKILL.md`; point to `reference/review-runtime.md` and `review-plan.sh --help`.

- [ ] **Step 4: Document the runtime contract and maintainer commands**

In `reference/review-runtime.md`, add the two Phase 1 schemas, receipt trust predicates, router CLI, failure table, and explicit no-authority statement. In `review-triage.md`, document how `REVIEW_MODE` changes the diff range and lane count before size tiering; do not change initial-mode tiers. In `CLAUDE.md`, add:

```bash
bash scripts/review-plan.test.sh
bash scripts/review-latency-benchmark.test.sh
```

State that Phase 2 shared inventory, Phase 3 typed collation, Phase 4 recipe extraction, Phase 5 specialist routing, and Phase 6 tails remain unimplemented and promotion-gated.

- [ ] **Step 5: Run GREEN and protect posting authority**

```bash
bash kc-pr-flow/scripts/review-plan.test.sh --case skill-wiring
bash kc-pr-flow/scripts/review-plan.test.sh
bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision
bash kc-pr-flow/scripts/review-post.test.sh
```

Expected: skill contract passes and the entire once-only posting suite remains unchanged and green.

- [ ] **Step 6: Commit the independently reviewable skill wiring**

```bash
git add kc-pr-flow/skills/kc-pr-review/SKILL.md \
  kc-pr-flow/reference/review-triage.md \
  kc-pr-flow/reference/review-runtime.md \
  kc-pr-flow/CLAUDE.md \
  kc-pr-flow/scripts/review-plan.test.sh
git commit -m "docs(kc-pr-flow): wire the delta review fast path"
```

---

### Task 4: Runtime-owned monotonic timing receipt

**Files:**
- Modify: `kc-pr-flow/scripts/review-runtime.sh:193-250,3284-3307`
- Modify: `kc-pr-flow/scripts/review-runtime.test.sh:25-32` and add a focused `review-timing` test function before the final summary at `2883-2884`
- Modify: `kc-pr-flow/reference/review-runtime.md:165-185,209-227`

**Interfaces:**
- Produces CLI commands:
  - `review-runtime.sh timing-start --review-key HASH --mode initial|delta|resolve --output FILE`
  - `review-runtime.sh timing-mark --timing-file FILE --phase NAME`
  - `review-runtime.sh timing-finish --timing-file FILE --lane-durations-file FILE --output FILE`
- Produces closed `kc-pr-flow.review-timing-state/v1` private state and terminal `kc-pr-flow.review-timing/v1` receipt.
- Consumes only runtime-recorded monotonic nanoseconds and closed lane-duration observations; it accepts no caller-authored total duration.

- [ ] **Step 1: Write failing timing tests**

Add `review-timing` to the case-filter usage and implement assertions for:

```bash
bash "$RUNTIME" timing-start --review-key "$EXPECTED_REVIEW_KEY" \
  --mode resolve --output "$timing_state"
bash "$RUNTIME" timing-mark --timing-file "$timing_state" --phase identity_and_plan
bash "$RUNTIME" timing-mark --timing-file "$timing_state" --phase required_lanes_critical_path
timing="$(bash "$RUNTIME" timing-finish --timing-file "$timing_state" \
  --lane-durations-file "$lane_durations" --output "$timing_receipt")"
assert_eq "terminal timing schema" "kc-pr-flow.review-timing/v1" \
  "$(jq -r '.schema' <<<"$timing")"
assert_eq "timing is runtime measured" "review-runtime" \
  "$(jq -r '.measured_by' <<<"$timing")"
assert_match "critical path is runtime-derived" '^[0-9]+$' \
  "$(jq -r '.durations_ms.required_lanes_critical_path' <<<"$timing")"
```

Cover duplicate/backward marks, unsupported phase, symlink/FIFO/state swap, changed review key,
extra fields, negative/unsafe integers, caller-supplied total, and finish-before-required-marks.
Stub all network/model/post commands and assert no calls.

- [ ] **Step 2: Run RED**

```bash
bash kc-pr-flow/scripts/review-runtime.test.sh --case review-timing
```

Expected: usage rejects `timing-start`; no timing schema exists.

- [ ] **Step 3: Implement runtime monotonic primitives and closed state**

Use the existing safe-I/O private snapshot/write patterns. Add one monotonic helper through Python's standard library:

```bash
review_runtime_monotonic_ns() {
  python3 -c 'import time; print(time.monotonic_ns())'
}
```

`timing-start` writes mode `0600` state with `review_key`, `mode`, `start_ns`, ordered empty marks,
and a state content hash. `timing-mark` safe-snapshots, validates, records the current runtime clock,
rejects duplicate or backward phases, and atomically replaces the state. Allowed phases are:

```text
identity_and_plan
inventory
required_lanes_critical_path
targeted_verification_critical_path
collation_and_draft
confirmation_ready
```

`timing-finish` requires `confirmation_ready`, computes phase deltas from runtime timestamps, validates lane observations `{lane_id,duration_ms,provider_family|null}`, and emits:

```json
{
  "schema": "kc-pr-flow.review-timing/v1",
  "review_key": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "mode": "resolve",
  "durations_ms": {
    "identity_and_plan": 1200,
    "inventory": 900,
    "required_lanes_critical_path": 103000,
    "targeted_verification_critical_path": 78000,
    "collation_and_draft": 6400,
    "confirmation_wait": null,
    "external_ci_wait": null,
    "post_mutation": null,
    "review_to_confirmation_ready": 189500
  },
  "lane_durations_ms": [],
  "measured_by": "review-runtime"
}
```

Never compute critical-path time by summing lanes. The caller marks the start/end of a parallel phase; runtime records both clocks and derives the elapsed value.

- [ ] **Step 4: Run GREEN and runtime regressions**

```bash
bash kc-pr-flow/scripts/review-runtime.test.sh --case review-timing
bash kc-pr-flow/scripts/review-runtime.test.sh
bash kc-pr-flow/scripts/review-post.test.sh
```

Expected: timing tests and all existing runtime/post authority tests pass.

- [ ] **Step 5: Commit runtime timing as its own unit**

```bash
git add kc-pr-flow/scripts/review-runtime.sh \
  kc-pr-flow/scripts/review-runtime.test.sh \
  kc-pr-flow/reference/review-runtime.md
git commit -m "feat(kc-pr-flow): record review critical-path timing"
```

---

### Task 5: Ordered Phase 1 promotion scorer

**Files:**
- Create: `kc-pr-flow/scripts/review-latency-benchmark.sh`
- Create: `kc-pr-flow/scripts/review-latency-benchmark.test.sh`
- Create: `kc-pr-flow/test/fixtures/review-plan/phase1-promotion.jsonl`
- Modify: `kc-pr-flow/CLAUDE.md:134-152`

**Interfaces:**
- Consumes: closed sanitized control/treatment pairs, `ReviewPlanDecision/v1`, expected finding IDs, capability coverage, behavior hashes, adjudicated precision counts, and Task 4 `ReviewTiming/v1`.
- Produces: `kc-pr-flow.review-latency-promotion/v1` with ordered Q1-Q6 results and `promote|do_not_promote`.
- CLI: `review-latency-benchmark.sh score --corpus FILE`.

- [ ] **Step 1: Write the immutable promotion fixture**

Create JSONL cases for: known fix only, fix plus test, unrelated new path, force-push, corrupt receipt, security finding, unavailable required lane, cross-layer no dispute, and new material dispute. Each line uses this closed shape:

```json
{
  "schema": "kc-pr-flow.review-latency-pair/v1",
  "pair_id": "known-fix-only",
  "exact_head": {
    "repository": "acme/widgets",
    "pr_number": 1693,
    "base_sha": "1111111111111111111111111111111111111111",
    "head_sha": "2222222222222222222222222222222222222222",
    "config_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "review_key": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "expected": {
    "mode": "resolve",
    "must_fix_finding_ids": ["cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"],
    "required_capabilities": ["correctness", "test-coverage"],
    "maximum_event": "APPROVE"
  },
  "control": {
    "finding_ids": ["cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"],
    "adjudicated_posted": 1,
    "adjudicated_false_positive": 0,
    "behavior_hashes": {"event_sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd", "options_sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"}
  },
  "treatment": {
    "plan": {
      "schema": "kc-pr-flow.review-plan-decision/v1",
      "identity": {
        "repository": "acme/widgets",
        "pr_number": 1693,
        "base_sha": "1111111111111111111111111111111111111111",
        "head_sha": "2222222222222222222222222222222222222222",
        "config_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      },
      "mode": "resolve",
      "reason_codes": ["trusted_predecessor", "ancestor_append", "known_finding_delta"],
      "review_range": {
        "from_exclusive": "3333333333333333333333333333333333333333",
        "to_inclusive": "2222222222222222222222222222222222222222"
      },
      "inherited_finding_ids": ["cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"],
      "required_capabilities": ["correctness", "test-coverage"],
      "event_ceiling": "APPROVE",
      "fallback": "initial"
    },
    "finding_ids": ["cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"],
    "capability_gap_refs": [],
    "adjudicated_posted": 1,
    "adjudicated_false_positive": 0,
    "behavior_hashes": {"event_sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd", "options_sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"},
    "timing": {
      "schema": "kc-pr-flow.review-timing/v1",
      "review_key": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "mode": "resolve",
      "durations_ms": {
        "identity_and_plan": 1200,
        "inventory": 900,
        "required_lanes_critical_path": 103000,
        "targeted_verification_critical_path": 78000,
        "collation_and_draft": 47900,
        "confirmation_wait": null,
        "external_ci_wait": null,
        "post_mutation": null,
        "review_to_confirmation_ready": 231000
      },
      "lane_durations_ms": [
        {"lane_id": "correctness-1", "duration_ms": 103000, "provider_family": "openai"}
      ],
      "measured_by": "review-runtime"
    }
  }
}
```

The fixture must use this full closed shape on every line. Recompute each case's canonical review
key and hashes from its own identity and evidence instead of copying the illustrative repeated hex.

- [ ] **Step 2: Write failing ordered-gate tests**

Follow `review-runtime-benchmark.test.sh:79-205` and assert:

```bash
report="$(bash "$BENCHMARK" score --corpus "$FIXTURE")"
assert_eq "good corpus promotes" "promote" "$(jq -r '.verdict' <<<"$report")"
assert_eq "target is four minutes" "240000" "$(jq -r '.latency.target_ms' <<<"$report")"
```

Mutate one dimension at a time and require the first failed gate:

| Mutation | Failed gate |
|---|---|
| arbitrary review key or stale head | Q1 `identity` |
| required capability gap | Q2 `required_coverage` |
| remove one expected must-fix | Q3 `must_fix_recall` |
| add adjudicated false positive | Q4 `precision` |
| event/options become less conservative | Q5 `behavior_parity` |
| set one eligible run to `240001` ms | Q6 `latency` |

Reject symlink/FIFO/oversized corpus, duplicate JSON members, unsafe numbers, self-resealed hashes,
and any timing whose `measured_by` is not `review-runtime`. Assert corpus bytes are unchanged after
scoring and reversed input order yields the same report bytes.

- [ ] **Step 3: Run RED**

```bash
bash kc-pr-flow/scripts/review-latency-benchmark.test.sh
```

Expected: FAIL because the scorer does not exist.

- [ ] **Step 4: Implement the source-safe scorer**

Mirror the safe corpus snapshot pattern at `review-runtime-benchmark.sh:20-54`, then validate each
pair and derive gates rather than trusting caller verdicts:

```bash
phase1_promotion() {
  jq -S -c -s '
    def recall($expected; $observed):
      (($expected - $observed) | length) == 0;
    def precision_not_worse:
      .treatment.adjudicated_false_positive <= .control.adjudicated_false_positive;
    sort_by(.pair_id) as $pairs |
    ($pairs | all(.identity_valid)) as $q1 |
    ($pairs | all(.treatment.capability_gap_refs | length == 0)) as $q2 |
    ($pairs | all(recall(.expected.must_fix_finding_ids; .treatment.finding_ids))) as $q3 |
    ($pairs | all(precision_not_worse)) as $q4 |
    ($pairs | all(.behavior_parity == true)) as $q5 |
    ($pairs | all(.treatment.timing.durations_ms.review_to_confirmation_ready <= 240000)) as $q6 |
    {
      schema:"kc-pr-flow.review-latency-promotion/v1",
      phase:"review-plan",
      quality_gates:{identity:$q1,required_coverage:$q2,must_fix_recall:$q3,
        precision:$q4,behavior_parity:$q5},
      latency:{target_ms:240000,eligible_runs:($pairs|length),
        passing_runs:([$pairs[] | select(.treatment.timing.durations_ms.review_to_confirmation_ready <= 240000)]|length),
        max_ms:([$pairs[].treatment.timing.durations_ms.review_to_confirmation_ready]|max)},
      verdict:(if $q1 and $q2 and $q3 and $q4 and $q5 and $q6 then "promote" else "do_not_promote" end)
    }'
}
```

Do not use fixture-provided `identity_valid` or `behavior_parity` booleans literally. Recompute the
review key, schema hashes, coverage set, event ceiling ordering, and behavior-hash equality inside
the validator; the skeleton only shows gate ordering.

- [ ] **Step 5: Run GREEN and deterministic scorer checks**

```bash
bash kc-pr-flow/scripts/review-latency-benchmark.test.sh
bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh --case interactive-gates
bash kc-pr-flow/scripts/review-plan.test.sh
```

Expected: all pass; any Q1-Q5 failure prevents promotion even when latency is one millisecond.

- [ ] **Step 6: Commit promotion evidence as its own unit**

```bash
git add kc-pr-flow/scripts/review-latency-benchmark.sh \
  kc-pr-flow/scripts/review-latency-benchmark.test.sh \
  kc-pr-flow/test/fixtures/review-plan/phase1-promotion.jsonl \
  kc-pr-flow/CLAUDE.md
git commit -m "test(kc-pr-flow): gate delta review latency promotion"
```

---

### Task 6: CI ownership and final Phase 1 verification

**Files:**
- Create: `.github/workflows/review-plan-tests.yml`
- Modify: `.github/workflows/review-runtime-tests.yml:7-22,40-48`
- Modify: `.github/workflows/review-evaluation-tests.yml:6-41,50-85`
- Modify: `scripts/review-ci-routing.test.py:11-17,68-109`

**Interfaces:**
- Produces: one `plan` CI owner for `review-plan.sh`, its test, and replay fixture; existing `runtime` owns timing commands; existing `evaluation` owns latency scoring.
- Consumes: Task 1-5 behavioral commands without adding dependencies.

- [ ] **Step 1: Write failing CI routing expectations**

Add `plan` to `WORKFLOWS`, route each new file to exactly one behavioral owner plus the static
contracts workflow, and add:

```python
"plan": ["bash kc-pr-flow/scripts/review-plan.test.sh"],
"evaluation": [
    "bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh",
    "bash kc-pr-flow/scripts/review-ablation.test.sh",
    "bash kc-pr-flow/scripts/review-latency-benchmark.test.sh",
],
```

Expected routes:

```python
"kc-pr-flow/scripts/review-plan.sh": {"plan"},
"kc-pr-flow/scripts/review-plan.test.sh": {"plan"},
"kc-pr-flow/test/fixtures/review-plan/pr1693-replay.json": {"plan"},
"kc-pr-flow/scripts/review-latency-benchmark.sh": {"evaluation"},
"kc-pr-flow/scripts/review-latency-benchmark.test.sh": {"evaluation"},
"kc-pr-flow/test/fixtures/review-plan/phase1-promotion.jsonl": {"evaluation"},
```

- [ ] **Step 2: Run RED**

```bash
python3 scripts/review-ci-routing.test.py
```

Expected: FAIL because `review-plan-tests.yml` and new route ownership do not exist.

- [ ] **Step 3: Add the narrow workflows**

Create `review-plan-tests.yml` using the pinned checkout and required `bash`, `jq`, `python3`, and
SHA-256 tools from `review-runtime-tests.yml:31-48`. Use exact PR/push path filters for the plan
script, test, fixture, runtime dependency, skill/reference wiring, and workflow itself. Run only:

```bash
bash kc-pr-flow/scripts/review-plan.test.sh
```

Add timing-owned paths to `review-runtime-tests.yml`; add latency scorer/test/fixture paths and
command to `review-evaluation-tests.yml`. Keep pull-request and push path lists byte-equal as
required by `review-ci-routing.test.py:61-66`.

- [ ] **Step 4: Run GREEN static and behavioral contracts**

```bash
python3 scripts/review-ci-routing.test.py
bash kc-pr-flow/scripts/review-plan.test.sh
bash kc-pr-flow/scripts/review-runtime.test.sh
bash kc-pr-flow/scripts/review-post.test.sh
bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh
bash kc-pr-flow/scripts/review-latency-benchmark.test.sh
bash scripts/skill-frontmatter-lint.sh
bash scripts/version-parity-check.sh
```

Expected: all pass. Do not run the paid `review-ablation.sh` acceptance experiment without a
separate budget authorization; its unit test remains part of the existing evaluation workflow.

- [ ] **Step 5: Run pinned syntax and ShellCheck gates**

```bash
bash -n kc-pr-flow/scripts/review-plan.sh \
  kc-pr-flow/scripts/review-plan.test.sh \
  kc-pr-flow/scripts/review-runtime.sh \
  kc-pr-flow/scripts/review-runtime.test.sh \
  kc-pr-flow/scripts/review-latency-benchmark.sh \
  kc-pr-flow/scripts/review-latency-benchmark.test.sh

docker run --rm --platform linux/amd64 -v "$PWD:/mnt" -w /mnt \
  koalaman/shellcheck:v0.9.0 \
  kc-pr-flow/scripts/review-plan.sh \
  kc-pr-flow/scripts/review-plan.test.sh \
  kc-pr-flow/scripts/review-runtime.sh \
  kc-pr-flow/scripts/review-runtime.test.sh \
  kc-pr-flow/scripts/review-latency-benchmark.sh \
  kc-pr-flow/scripts/review-latency-benchmark.test.sh
```

If Docker is unavailable, use the pinned Rosetta-compatible binary command documented in
`kc-pr-flow/CLAUDE.md`; do not substitute a newer ShellCheck release.

- [ ] **Step 6: Verify the accepted scope and rollback proof**

```bash
KC_PR_FLOW_DELTA_FAST_PATH=off bash kc-pr-flow/scripts/review-plan.test.sh --case mode-router
KC_PR_FLOW_DELTA_FAST_PATH=on bash kc-pr-flow/scripts/review-plan.test.sh --case mode-router
git diff origin/main...HEAD --name-only
git diff --check origin/main...HEAD
```

Expected: off selects the existing `initial` route, on passes all exact-head cases, and changed
files are limited to Phase 1 implementation/tests/docs/CI plus the approved spec/plan.

- [ ] **Step 7: Commit CI ownership**

```bash
git add .github/workflows/review-plan-tests.yml \
  .github/workflows/review-runtime-tests.yml \
  .github/workflows/review-evaluation-tests.yml \
  scripts/review-ci-routing.test.py
git commit -m "ci(kc-pr-flow): gate the delta review fast path"
```

## Deferred promotion-gated phases

This implementation plan ends after Phase 1. Do not add these to a Phase 1 task or commit:

- Phase 2: shared exact-head inventory.
- Phase 3: typed finding collation.
- Phase 4: move shadow/confirmation recipes into runtime and shrink `SKILL.md`.
- Phase 5: risk-triggered specialist routing, including any reduction of today's unconditional
  security reviewer.
- Phase 6: nonblocking learning and indexed posting state, only if measured timing warrants it.

Each deferred phase needs its own plan after Phase 1 promotion evidence passes the earlier quality
gates and the Captain accepts the next rollout boundary.
