# kc-pr-review Delta Fast Path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and repair Phase 1's exact-head `initial`/`delta`/`resolve` router, trusted
predecessor receipt, default-off skill wiring, and structural scorer without claiming latency
promotion before independent actual-run evidence exists.

**Architecture:** A source-safe Bash helper replays the existing typed review runtime to mint and
verify a closed delta receipt, then inspects local Git ancestry and every unseen hunk to emit an
advisory review plan. The existing runtime records local monotonic timing, the skill revalidates
that plan and mechanically constrains events at existing confirmation/posting seams, and the committed synthetic
scorer remains structural with a fixed `do_not_promote` verdict. Posting stays entirely in
`review-post.sh` and keeps its current exact-head and human-authorization contracts.

**Tech Stack:** Bash 3.2, `jq`, Python 3.8+ safe-I/O helper, local Git, JSON/JSONL fixtures, GitHub Actions, ShellCheck v0.9.0.

**Spec:** `docs/superpowers/specs/2026-08-26-kc-pr-review-latency-design.md`

## Global Constraints

- Implement Phase 1 only. Phases 2–6 remain promotion-gated follow-up work.
- `KC_PR_FLOW_DELTA_FAST_PATH=on` is the only enabling value; unset or any other value keeps the current full-review route.
- `ReviewDeltaReceipt/v1`, `ReviewPlanDecision/v1`, and `ReviewTiming/v1` use closed key sets and canonical `jq -S -c` hashing.
- A predecessor is trusted only after `review-runtime.sh replay` succeeds and identity, review key, receipt content hash, base, config, and ancestry all match.
- Every projected Phase 1 lane is treated as required and must finish `succeeded`; any `failed`,
  `unavailable`, or non-empty `uncertain_candidate_ids` state prevents receipt issuance/validation
  and selects `initial`.
- Missing, malformed, unsafe, stale, non-ancestor, rewritten, changed-base, config-incompatible, or unknown state selects `initial`.
- `resolve` requires every changed hunk and every security/dependency/workflow signal to map to one
  replay-derived known finding, contract, or test boundary. Safe unmapped work selects `delta`;
  ambiguous or unsafe work selects `initial`.
- A required coverage gap caps authority at `COMMENT`; no script may emit a semantic correctness, security, goal-achievement, or final review verdict.
- For any non-`initial` plan, the plan ceiling is revalidated before legacy/typed confirmation,
  after event edits, for autonomous gates, and immediately before posting. `COMMENT` never permits
  `APPROVE`.
- Known predecessor must-fix findings remain inherited until current-head evidence resolves them; silence is not resolution.
- Preserve Step 2.1 exact-head checks, Step 6a quote-the-line verification, Step 6c human confirmation, and Step 7 closed posting authority.
- `review-post.sh` remains the only posting/reconcile/network authority and is not modified by this plan.
- Feature commits do not edit plugin versions; release-please owns versioning.
- Stage explicit paths; never use `git add .`.
- Run CI's ShellCheck v0.9.0 against every changed review shell file before the final task commit.
- The committed synthetic corpus is structural evidence only and must emit `do_not_promote`.
  Actual independently adjudicated control/treatment artifacts and runtime-observed timing require
  separate Captain authorization; this plan performs no paid run.

## Captain-approved revision (2026-08-27)

The Captain approved this exact amendment after the full-branch review. It changes neither the
Phase 1 seam nor the counted surface set; it strengthens lifecycle obligations and withdraws the
unsupported synthetic promotion claim.

| Surface | Pre-revision obligation | Revised obligation |
|---|---|---|
| `review-plan.sh` plus delta receipt/plan schemas | Receipt replay and changed-path route | Same surface; successful/uncertainty-free receipt, per-hunk/signal route, and per-Git-operation worktree gate |
| `review-runtime.sh` plus timing schema | Local monotonic timing | Same surface; only timing recorded at actual workflow boundaries is promotion-capable |
| `kc-pr-review/SKILL.md` confirmation/post seam | Store `PLAN_EVENT_CEILING` | Same seam; mechanically enforce the ceiling through legacy, typed, autonomous, and post paths |
| `review-latency-benchmark.sh` plus committed corpus | Synthetic Q1-Q6 promotion fixture | Same surface; structural Q1-Q6 tests with fixed `do_not_promote` |
| Existing plan/runtime/evaluation CI workflows | Phase 1 behavioral ownership | Same triggers/jobs; no new hosted or paid execution |

The revised outcome is a safe, default-off, **unpromoted** Phase 1 foundation. The four-minute and
100% must-fix targets are historical design targets; the later Captain-approved multi-pair rule
below controls promotion. Phases 2-6, specialist reduction, posting ownership, human confirmation,
actual evidence collection, and paid model/provider runs remain non-goals. Rollback remains setting
`KC_PR_FLOW_DELTA_FAST_PATH` to anything except `on`; receipts remain readable and do not gain
authority.

The revision is falsified if a same-file unrelated/security hunk selects `resolve`; a failed,
unavailable, or uncertain predecessor is trusted; `APPROVE` crosses a `COMMENT` ceiling; a Git
operation lacks an immediately preceding worktree validation; the synthetic corpus promotes; or a
four-field router trace is called byte-identical end-to-end behavior.

## Captain-approved Task 18 amendment (2026-08-28)

The receipt boundary now also binds completeness to one immutable canonical
`kc-pr-flow.review-config/v1` snapshot. This is an interface change within the existing
`review-plan.sh` / receipt / skill seam, not a new runtime, CI, or posting surface.

- `receipt --event-file FILE --config-file FILE` and `decide ... --config-file FILE` both require
  the safe canonical snapshot. The producer, receipt validator, and decision validator recompute
  its canonical hash and require it to equal the run/config identity.
- Its sorted, unique capability set must exactly equal the unique replayed lane capabilities.
  Missing, unsafe, malformed, duplicate-key, oversized, noncanonical, hash-mismatched, or
  capability-mismatched snapshots cannot mint or trust a receipt and select `initial`.
- The skill snapshots the one config file with its other immutable inputs and supplies that exact
  snapshot to initial routing and every authority-boundary rerun. A complete matching predecessor
  preserves its existing `delta` or `resolve` decision.

This amendment is falsified if a six-capability configuration with one succeeded replayed lane
issues a receipt or selects a non-`initial` decision. The fast path remains default-off; no network,
model, confirmation, posting, rollout, or promotion authority changes.

## Captain-approved slimming and measurement amendment (2026-08-28)

This route records measurement truth before follow-up runtime work. It adds no staging or publishing
lifecycle and no standing CI workflow; narrow source-safe checks belong only to existing contract-test
owners.

### Controlling promotion evidence

The current one-pair result is exploratory and cannot promote: control 444159 ms; treatment 335487
ms; 24.47% reduction; setup collector 438850 ms outside treatment latency; treatment-agent critical
path 285650 ms; combined treatment recall 6 of 14 actionable findings, with 8 misses. The eight
misses are semantic predecessor-observation misses, not router-dropped inherited IDs or newly
introduced delta hunks.

Promotion requires at least five real stacked control/treatment pairs, median review-to-confirmation
reduction of at least 33.3%, recall of at least 90%, zero missed frozen Critical/High defect classes,
and false positives no greater than control. The earlier four-minute and 100%-known-finding statements
remain historical and non-promotable; they do not describe a current promotion or override this rule.

### Identity and blind adjudication

Before collection, Task 2 replaces v1 with a machine-owned v2 identity: the runtime derives canonical
claim keys and finding identity from validated v2 inputs. Models may supply evidence and bounded prose
but cannot author, select, or override identity. This explicitly supersedes the latency design's
section 7.2 ban on machine-derived claim keys. Invalid or ambiguous identity remains an unresolved,
fail-closed partition.

The closed severity rubric is `Critical`, `High`, `Medium`, and `Low`. Every blind adjudicator labels
every accepted finding; an incomplete label matrix fails closed. Per-finding severity is the maximum
submitted blind label, and class severity is the maximum member severity. Same-defect adjudication is
blind and de-identified, arm mapping stays sealed until freeze, transitivity conflicts remain
unresolved, and the Captain may reject a proposed match. PR #14 rewritten lineage is a fail-closed
fallback case, never one of the positive pairs.

### Required sequence, surfaces, and cleanup boundary

Execute in this order: preregister; v2 identity; memoized collector; paired runs and seal; blind
adjudication/freeze; timing analysis; recipe/test consolidation. No later step can convert unfrozen
or unresolved evidence into promotion evidence.

| Surface | Before | After |
|---|---|---|
| v1 identity | Reviewer-authored identity with a machine-derived-key prohibition | v2 machine-owned identity replaces v1; model prose remains untrusted |
| Existing event runtime | Repeated collector work | Memoized collector in the same runtime; no staging/publish lifecycle |
| `SKILL.md` recipes | Duplicated mechanical logic | Behavior-preserving deletion after frozen truth, with existing runtime authority retained |
| Existing contract-test owners | Current source-safe tests | Narrow v2 identity, collector, adjudication, and parity cases only; no new workflow |

Recipe and test consolidation may follow frozen measurement truth without enabling promotion. It may
delete duplicated skill logic only if the existing runtime remains authoritative and semantic safety
text—exact head, evidence/quote, coverage, confirmation, posting, and fail-closed rules—remains.
Rollback restores the prior recipe text without changing frozen evidence or promotion state.

### Follow-up task allocation

- Task 2 owns v2 identity and adds source-safe identity cases to the existing collation/runtime test
  owners; it does not introduce a new workflow.
- Task 3 owns the in-process memoized collector and adds its source-safe cases to the existing runtime
  test owner; collector setup remains outside treatment latency.
- Task 4 owns preregistration, pair sealing, blind adjudication, freeze, and timing analysis; it
  selects five provenance-valid ancestor pairs and excludes PR #14 from positives.
- Task 5 may consolidate recipes/tests only after Task 4 freezes measurement truth; parity tests do
  not establish semantic correctness or promotion.

## File map

| File | Responsibility |
|---|---|
| `kc-pr-flow/scripts/review-plan.sh` | Source-safe receipt producer/validator and per-hunk exact-head router; no model, network, confirmation, or posting authority |
| `kc-pr-flow/scripts/review-plan.test.sh` | Bash 3.2 contract tests for receipt trust, hunk/signal routing, ceiling enforcement, rollback, source safety, and PR #1693 replay |
| `kc-pr-flow/test/fixtures/review-plan/pr1693-replay.json` | Sanitized immutable lineage, findings, changed-path classes, and expected Phase 1 decision |
| `kc-pr-flow/scripts/review-runtime.sh` | Existing receipt authority plus bounded local monotonic timing commands |
| `kc-pr-flow/scripts/review-runtime.test.sh` | Timing schema, identity, monotonicity, file-safety, and no-network tests |
| `kc-pr-flow/scripts/review-latency-benchmark.sh` | Source-safe ordered Phase 1 structural scorer; cannot promote synthetic evidence |
| `kc-pr-flow/scripts/review-latency-benchmark.test.sh` | Gate ordering, simulated recall/precision/latency, mutation resistance, and fixed `do_not_promote` tests |
| `kc-pr-flow/test/fixtures/review-plan/phase1-promotion.jsonl` | Synthetic structural control/treatment shapes; never actual promotion evidence |
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
- Consumes: `review_runtime_sha256` from `kc-pr-flow/scripts/review-runtime.sh:8-17`,
  `review_runtime_snapshot_regular_file` from `kc-pr-flow/scripts/review-runtime.sh:193-223`, and
  `review_runtime_replay EVENT_FILE -> kc-pr-flow.review-projection/v1` from
  `kc-pr-flow/scripts/review-runtime.sh:1823-1975`.
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

Add predecessor-completeness negatives for zero lanes, empty derived `required_capabilities`, one
lane terminal changed to `failed`, one changed to `unavailable`, and one non-empty
`uncertain_candidate_ids` array. Both `receipt` production and receipt validation must reject each
case; none may produce a delta receipt with an `APPROVE`-capable route. Zero lanes must not pass by
vacuous `all([])`.

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
  jq -e '
    .lifecycle.complete == true and
    .uncertain_candidate_ids == [] and
    (.lanes | length > 0 and all(.[]; .result.terminal_status == "succeeded"))
  ' >/dev/null <<<"$projection" || return 3
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
        finding_id,claim_key,anchor_sha256,category,evidence,
        evidence_sha256:.evidence.content_sha256,
        path,side,resolution_state:"unresolved"
      }) | sort_by(.finding_id)),
      required_capabilities:(.lanes | map(.capability) | sort | unique),
      coverage_gap_refs:[]
    }' <<<"$projection")" || return 3
  jq -e '.required_capabilities | length > 0' >/dev/null <<<"$canonical" || return 3
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

Validate safe tokens, 40/64-hex fields, normalized relative paths, `LEFT|RIGHT|FILE`, sorted unique
arrays, `resolution_state == unresolved`, the replay-derived `anchor_sha256`, `category`, and closed
evidence pointer, `.lanes | length > 0`, every lane's
`result.terminal_status == succeeded`, empty `uncertain_candidate_ids`, receipt
`required_capabilities | length > 0`, and equality against the fresh replay projection. The
producer and validator must both reject zero lanes and empty required capabilities; do not rely on
vacuous `all([])`. A non-`git_blob` evidence pointer may remain inherited for `delta`, but cannot
authorize a `resolve` hunk. Never trust a matching self-hash without checking projection-derived
fields.

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
- Reason-code enum: `feature_disabled`, `missing_predecessor`, `invalid_predecessor`,
  `identity_mismatch`, `base_changed`, `config_changed`, `non_ancestor`, `ancestor_append`,
  `known_finding_delta`, `expanded_delta`, and `unknown_delta`.

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
| flag off | router not invoked; existing `initial` flow | existing authority unchanged |
| missing receipt/events | `initial` | `COMMENT` |
| exact known path plus mechanically adjacent test | `resolve` | inherited ceiling |
| same known path plus unrelated second hunk | `delta` | `COMMENT` |
| same known path plus security-shaped append | `delta` or `initial` | never above `COMMENT` |
| new unrelated path on ancestor append | `delta` | `COMMENT` until new required coverage completes |
| force-push/non-ancestor | `initial` | `COMMENT` |
| changed base or config | `initial` | `COMMENT` |
| failed/unavailable/uncertain predecessor | `initial` | existing initial authority only |
| unsafe worktree/symlink | `initial` | `COMMENT` |

Assert the output has only `schema`, `identity`, `mode`, `reason_codes`, `review_range`, `inherited_finding_ids`, `required_capabilities`, `event_ceiling`, and `fallback`.

Add `--case worktree-safety`. Build one real repository, a symlink to it, a regular file, a missing
path, and a path whose parent component is a symlink. Put a ledger-writing `git` stub first on
`PATH`, call each public decision path with every unsafe worktree, and assert every case selects
`initial`/`COMMENT` without one ledger entry. Then call the helper directly on the real directory
and assert it returns that directory's canonical absolute path. The runtime safe-I/O helper is a
regular-file snapshot boundary only; do not cite or call it as directory validation.

- [ ] **Step 3: Run RED**

```bash
bash kc-pr-flow/scripts/review-plan.test.sh --case mode-router
bash kc-pr-flow/scripts/review-plan.test.sh --case trust-boundary
bash kc-pr-flow/scripts/review-plan.test.sh --case worktree-safety
```

Expected: FAIL because `decide` is not implemented.

- [ ] **Step 4: Implement conservative Git and path classification**

Implement one directory gate and route every Git invocation through it:

```bash
review_plan_real_worktree() {
  python3 - "$1" <<'PY'
import os
import stat
import sys

raw = sys.argv[1]
if not os.path.isabs(raw) or os.path.normpath(raw) != raw:
    raise SystemExit(2)
candidate = raw
try:
    mode = os.lstat(candidate).st_mode
except OSError:
    raise SystemExit(2)
cursor = os.sep
for component in candidate.split(os.sep)[1:]:
    cursor = os.path.join(cursor, component)
    try:
        if stat.S_ISLNK(os.lstat(cursor).st_mode):
            raise SystemExit(2)
    except OSError:
        raise SystemExit(2)
if not stat.S_ISDIR(mode) or os.path.realpath(candidate) != candidate:
    raise SystemExit(2)
print(candidate)
PY
}

review_plan_git() {
  local worktree="$1" canonical
  shift
  canonical="$(review_plan_real_worktree "$worktree")" || return 2
  command git -C "$canonical" "$@"
}

review_plan_git_identity_valid() {
  local worktree="$1" head="$2"
  review_plan_git "$worktree" rev-parse --git-dir >/dev/null 2>&1 || return 1
  [ "$(review_plan_git "$worktree" cat-file -t "$head" 2>/dev/null)" = commit ]
}

review_plan_ancestor() {
  review_plan_worktree_adapter ancestor "$1" "$2" "$3" \
    "${KC_PR_FLOW_MAX_PLAN_ANCESTRY_COMMITS:-10000}" \
    "${KC_PR_FLOW_MAX_PLAN_COMMIT_BYTES:-1048576}" \
    "${KC_PR_FLOW_MAX_PLAN_ANCESTRY_SECONDS:-2}"
}

review_plan_changed_paths() {
  review_plan_git "$1" diff --name-status --find-renames=50% "$2..$3"
}
```

Bind the opened worktree plus its `.git` entry, Git directory, common directory, and object
directory before routing. Revalidate every bound identity immediately before and after every
`rev-parse`, `cat-file`, `diff`, `ls-tree`, `show`, or other Git operation. Determine ancestry from
bounded raw exact-SHA commit objects and their `parent` headers through one persistent batch
process, not Git graft, shallow, ref, or config semantics. Traverse at most 10,000 commits by
default (100,000 hard maximum), read at most 1 MiB per commit by default (4 MiB hard maximum), use a
2-second wall-clock deadline by default (30-second hard maximum), and select `initial` on any limit. Run a
fixed system Git with an allowlisted environment. Operational commands use a private,
configuration-free Git directory, the explicitly bound worktree and object directory, exact object
IDs, no refs, no shallow/graft metadata, no inherited or repository-local config, no object
alternates, and replacement objects disabled. No direct `git -C` call may exist outside the
adapter. The helper rejects a final symlink, symlinked parent, non-directory, unresolved path,
metadata/object replacement, or identity change without releasing Git output. Add deterministic
test hooks that replace either the opened worktree or its `.git` entry and require `initial` with no
mixed-identity result.

Before parsing, read each existing base/head blob directly from the bound object store and require
the independent byte policy: regular blob mode, at most 4 MiB by default and 16 MiB hard maximum,
no NUL byte, and strict UTF-8 decoding. Git attributes, diff drivers, and numeric diff statistics
must not decide whether an object is text. Obtain the unseen diff with
`--unified=0 --no-ext-diff --no-textconv --no-renames` and parse every ordinary hunk,
including multiple hunks in one known file. For each hunk, derive its old coordinate interval;
treat a zero-length insertion as anchored at its old line. A hunk maps to a known finding only when
the receipt carries replay-derived `git_blob` evidence for the predecessor head, the paths match,
and the evidence line lies in that old interval. A contract/test/fixture hunk may map only when the
path is mechanically classified as such and that **same hunk body** references exactly one known
finding through its claim key, evidence locator, or normalized module path. Occurrence count is
irrelevant: repeated tokens for that one finding remain one mapping, while tokens resolving to two
or more known findings are ambiguous. File-level import presence never authorizes a different hunk.

Classify security, dependency, and workflow signals per hunk/path before selecting `resolve`. A
signal is mapped only when the same hunk already maps to a predecessor finding or required
capability of the corresponding class. A safe ordinary hunk or signal with no mapping selects
`delta`/`COMMENT`; an ambiguous mapping, malformed/combined diff, rename, copy, binary, submodule,
unsafe path, unknown status, or unclassifiable signal selects `initial`. The unrelated append and
`unrelated_authorization_bypass` security-shaped append from the full-branch review must never
select `resolve` even when another hunk in that file fixes the known finding.

For a trusted ancestor with any extra safe path, select `delta`, add `expanded_delta`, include `correctness` plus the predecessor required capabilities, and set `event_ceiling:COMMENT` until current-run coverage completes. Phase 1 does not implement shared inventory or risk-triggered specialists; current full-review security and specialist rules still apply after routing.

Build the decision with typed `jq --arg/--argjson`, sorted unique arrays, and `review_range.from_exclusive = predecessor.head_sha`, `to_inclusive = current head`. Validate the canonical review key for the current identity but do not manufacture a current runtime run or authorization receipt.

- [ ] **Step 5: Run GREEN, adversarial mutations, and source safety**

```bash
bash kc-pr-flow/scripts/review-plan.test.sh --case mode-router
bash kc-pr-flow/scripts/review-plan.test.sh --case trust-boundary
bash kc-pr-flow/scripts/review-plan.test.sh --case worktree-safety
bash kc-pr-flow/scripts/review-plan.test.sh
bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision
```

Expected: all pass. Mutating any one identity field, receipt hash, finding evidence hash, ancestry edge, or fixture path either selects `initial`/`COMMENT` or rejects input; it never preserves `resolve`.

Also require the same-known-file unrelated hunk, security-shaped append, failed lane, unavailable
lane, uncertain candidate, and worktree replacement cases to fail closed as specified above.

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
- Produces: one documented pre-triage routing seam plus mechanical ceiling checks within the
  existing confirmation/post seams. `initial`
  preserves the current **planner state**; `delta` reviews the unseen range and all newly required
  capabilities; `resolve` dispatches one focused correctness lane and targeted verification while
  inheriting known finding IDs.
- Preserves: current goal-achievement judgment, quote gate, tests/probe where activated, draft structure, two head checks, Step 6c confirmation, and Step 7 posting receipt.

- [ ] **Step 1: Write failing skill/reference contract assertions**

Add `--case skill-wiring` to `review-plan.test.sh`:

```bash
assert_file_contains "$SKILL" 'KC_PR_FLOW_DELTA_FAST_PATH=on'
assert_file_contains "$SKILL" 'review-plan.sh decide'
assert_file_contains "$SKILL" 'mode == "initial"'
assert_file_contains "$SKILL" 'coverage gap.*COMMENT'
assert_file_contains "$SKILL" 'PLAN_EVENT_CEILING'
assert_file_contains "$SKILL" 'Step 6c'
assert_file_contains "$REFERENCE" 'kc-pr-flow.review-delta-receipt/v1'
assert_file_contains "$REFERENCE" 'kc-pr-flow.review-plan-decision/v1'
```

Also assert `review-plan.sh` contains none of `gh pr review`, `review-post.sh post`, `authorization.granted`, or `human_confirmed`.

Add legacy, typed, autonomous, and immediate-pre-post harnesses. For each, feed a validated
`delta` plan with `event_ceiling:COMMENT`; assert `COMMENT` and `REQUEST_CHANGES` survive and
`APPROVE` is rejected before confirmation/gate construction/posting. A missing, stale, mutated, or
identity-mismatched plan after the fast path engages must fail closed rather than fall back to an
unbounded legacy event.

- [ ] **Step 2: Run RED**

```bash
bash kc-pr-flow/scripts/review-plan.test.sh --case skill-wiring
```

Expected: FAIL because the approved mode router is not yet wired into the skill/reference.

- [ ] **Step 3: Add the minimal Step 2.2 routing seam**

Immediately after `SKILL.md` Step 2.1, add a concise `Step 2.2: Trusted Post-Fix Route` section with this executable shape:

```bash
REVIEW_MODE=initial
FAST_PATH_ENGAGED=0
unset PLAN_JSON PLAN_EVENT_CEILING PLAN_REASON CANDIDATE_PLAN_JSON

# Immutable inputs for the initial decision and every authority-boundary rerun.
PLAN_INPUT_REPO="$REPO"
PLAN_INPUT_PR_NUMBER="$PR_NUMBER"
PLAN_INPUT_BASE_SHA="$BASE_SHA"
PLAN_INPUT_HEAD_SHA="$REVIEWED_HEAD_SHA"
PLAN_INPUT_CONFIG_HASH="$CONFIG_HASH"
PLAN_INPUT_WORKTREE="$REPO_WORKTREE"
PLAN_INPUT_PREDECESSOR_EVENTS="$PREDECESSOR_EVENTS"
PLAN_INPUT_DELTA_RECEIPT="$DELTA_RECEIPT"

review_plan_decide_fresh() {
  bash "${CLAUDE_PLUGIN_ROOT}/scripts/review-plan.sh" decide \
    --repo "$PLAN_INPUT_REPO" --pr "$PLAN_INPUT_PR_NUMBER" \
    --base "$PLAN_INPUT_BASE_SHA" --head "$PLAN_INPUT_HEAD_SHA" \
    --config-hash "$PLAN_INPUT_CONFIG_HASH" --repo-worktree "$PLAN_INPUT_WORKTREE" \
    --predecessor-events "$PLAN_INPUT_PREDECESSOR_EVENTS" \
    --delta-receipt "$PLAN_INPUT_DELTA_RECEIPT"
}

review_plan_canonical_for_inputs() {
  local raw_candidate candidate
  raw_candidate="$(cat)" || return 1
  . "${CLAUDE_PLUGIN_ROOT}/scripts/review-plan.sh" || return 1
  # This closed validator rejects raw duplicate members before its first jq parse.
  review_plan_validate_decision "$raw_candidate" "$PLAN_INPUT_REPO" \
    "$PLAN_INPUT_PR_NUMBER" "$PLAN_INPUT_BASE_SHA" "$PLAN_INPUT_HEAD_SHA" \
    "$PLAN_INPUT_CONFIG_HASH" "$PLAN_INPUT_PREDECESSOR_EVENTS" \
    "$PLAN_INPUT_DELTA_RECEIPT" "$PLAN_INPUT_WORKTREE" || return 1
  candidate="$(printf '%s' "$raw_candidate" | jq -S -c -e \
    --arg repository "$PLAN_INPUT_REPO" \
    --argjson pr_number "$PLAN_INPUT_PR_NUMBER" \
    --arg base_sha "$PLAN_INPUT_BASE_SHA" \
    --arg head_sha "$PLAN_INPUT_HEAD_SHA" \
    --arg config_hash "$PLAN_INPUT_CONFIG_HASH" '
      . as $plan |
      select(
        $plan.schema == "kc-pr-flow.review-plan-decision/v1" and
        $plan.identity.repository == $repository and
        $plan.identity.pr_number == $pr_number and
        $plan.identity.base_sha == $base_sha and
        $plan.identity.head_sha == $head_sha and
        $plan.identity.config_hash == $config_hash and
        ($plan.mode == "initial" or $plan.mode == "delta" or $plan.mode == "resolve")
      ) |
      $plan
    ')" || return 1
  printf '%s\n' "$candidate"
}

review_plan_sha256() {
  python3 -c 'import hashlib, sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())'
}

if [ "${KC_PR_FLOW_DELTA_FAST_PATH:-off}" = on ] &&
   CANDIDATE_PLAN_JSON="$(review_plan_decide_fresh)" &&
   CANDIDATE_PLAN_JSON="$(printf '%s' "$CANDIDATE_PLAN_JSON" |
     review_plan_canonical_for_inputs)"; then
  REVIEW_MODE="$(jq -r '.mode' <<<"$CANDIDATE_PLAN_JSON")"
  case "$REVIEW_MODE" in
    delta|resolve)
      PLAN_JSON="$CANDIDATE_PLAN_JSON"
      PLAN_JSON_SHA256="$(printf '%s' "$PLAN_JSON" | review_plan_sha256)"
      PLAN_EVENT_CEILING="$(jq -r '.event_ceiling' <<<"$PLAN_JSON")"
      PLAN_REASON="$(jq -r '.reason_codes | join(",")' <<<"$PLAN_JSON")"
      FAST_PATH_ENGAGED=1
      ;;
    initial) ;;
  esac
fi
unset CANDIDATE_PLAN_JSON
readonly FAST_PATH_ENGAGED
if [ "$FAST_PATH_ENGAGED" -eq 1 ]; then
  readonly PLAN_JSON_SHA256
fi

review_plan_event_allowed() {
  local requested_event="$1" fresh_plan fresh_mode stored_plan stored_hash ceiling engaged
  case "$requested_event" in APPROVE|COMMENT|REQUEST_CHANGES) ;; *) return 1 ;; esac

  engaged="${FAST_PATH_ENGAGED:-0}"
  case "$engaged" in 0|1) ;; *) return 1 ;; esac

  # Flag-off preserves legacy authority only before any fast path engaged.
  if [ "$engaged" -eq 0 ]; then
    [ "${KC_PR_FLOW_DELTA_FAST_PATH:-off}" = on ] || return 0
    fresh_plan="$(review_plan_decide_fresh)" || return 1
    fresh_plan="$(printf '%s' "$fresh_plan" | review_plan_canonical_for_inputs)" || return 1
    fresh_mode="$(jq -r '.mode' <<<"$fresh_plan")" || return 1
    if [ "${REVIEW_MODE:-initial}" = initial ] && [ "$fresh_mode" = initial ]; then
      return 0
    fi
    return 1
  fi

  # Once engaged, validate the stored plan and its immutable digest even if the flag disappears.
  [ "${PLAN_JSON+x}" = x ] && [ "${PLAN_JSON_SHA256+x}" = x ] || return 1
  stored_plan="$(printf '%s' "$PLAN_JSON" | review_plan_canonical_for_inputs)" || return 1
  stored_hash="$(printf '%s' "$stored_plan" | review_plan_sha256)" || return 1
  [ "$stored_hash" = "$PLAN_JSON_SHA256" ] || return 1
  case "$(jq -r '.mode' <<<"$stored_plan")" in delta|resolve) ;; *) return 1 ;; esac

  if [ "${KC_PR_FLOW_DELTA_FAST_PATH:-off}" = on ]; then
    fresh_plan="$(review_plan_decide_fresh)" || return 1
    fresh_plan="$(printf '%s' "$fresh_plan" | review_plan_canonical_for_inputs)" || return 1
    [ "$fresh_plan" = "$stored_plan" ] || return 1
  fi

  ceiling="$(jq -r '.event_ceiling' <<<"$stored_plan")" || return 1
  case "$ceiling:$requested_event" in
    APPROVE:APPROVE|APPROVE:COMMENT|APPROVE:REQUEST_CHANGES|\
    COMMENT:COMMENT|COMMENT:REQUEST_CHANGES) return 0 ;;
    *) return 1 ;;
  esac
}
```

Call `review_plan_event_allowed "$EFFECTIVE_EVENT"` before presenting the legacy or typed effective
event at Step 6c, after every human edit, before creating an autonomous gate, when constructing the
confirmed post gate, and immediately before either posting path. A nonzero result blocks that seam;
before confirmation the caller may start a new explicit `initial` review, while after confirmation
it requires a fresh review plan. A router failure is only provisional `initial`: it preserves legacy
authority under flag-on only if the function's fresh rerun also returns `mode=initial`. Once
`FAST_PATH_ENGAGED=1`, missing, stale, mutated, or identity-mismatched plan state always fails closed.
If the flag is later `off` or unexported, the engaged run still validates the stored plan digest and
enforces its ceiling; flag loss can never turn a stored `COMMENT` ceiling into legacy `APPROVE`.
This is the exact Task 9 harness target and adds no CLI, schema, or surface.

The prose must state:

- missing predecessor inputs are normal and select `initial`;
- `resolve` dispatches one focused correctness reviewer and runs known-finding plus affected-test verification in parallel;
- `delta` reviews every unseen changed path and inherited finding, and new required coverage must terminally complete;
- current unconditional specialist rules remain unchanged in Phase 1;
- `event_ceiling` can only reduce authority and is mechanically enforced at every confirmation and
  posting boundary above;
- before a clean draft and before posting, Step 2.1 still rechecks the live head;
- the user still receives the full Step 6 draft and explicitly confirms at Step 6c.

Beyond the exact Step 2.2 snippet above, do not copy additional schema validators or shell helpers
into `SKILL.md`; point to `reference/review-runtime.md` and `review-plan.sh --help`.

Extend `--case skill-wiring` with a router stub that prints a valid JSON prefix and exits 9. Assert
the existing planner-state trace (`mode`, serialized plan, ceiling, and reason only) matches the
flag-off trace and that `PLAN_JSON`,
`PLAN_EVENT_CEILING`, and `PLAN_REASON` are unset. Repeat with exit 0 plus malformed JSON. This is
the rollback contract: helper failure adds neither a synthetic decision nor a lower event ceiling.
Name these assertions `planner-state parity`; do not call them byte-identical existing-flow tests.

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
bash kc-pr-flow/scripts/review-plan.test.sh --case event-ceiling
bash kc-pr-flow/scripts/review-plan.test.sh
bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision
bash kc-pr-flow/scripts/review-post.test.sh
```

Expected: skill contract and all ceiling paths pass, `COMMENT` cannot produce an `APPROVE` gate or
post request, and the entire once-only posting suite remains unchanged and green.

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

### Task 5: Ordered Phase 1 structural scorer

**Files:**
- Create: `kc-pr-flow/scripts/review-latency-benchmark.sh`
- Create: `kc-pr-flow/scripts/review-latency-benchmark.test.sh`
- Create: `kc-pr-flow/test/fixtures/review-plan/phase1-promotion.jsonl`
- Modify: `kc-pr-flow/CLAUDE.md:134-152`

**Interfaces:**
- Consumes: closed synthetic control/treatment shapes, `ReviewPlanDecision/v1`, expected finding IDs,
  capability coverage, behavior hashes, simulated adjudication counts, and Task 4-shaped
  timing objects inside `ReviewLatencyPair/v1` that cannot claim runtime measurement.
- Produces: `kc-pr-flow.review-latency-promotion/v1` with ordered structural Q1-Q6 results and a
  fixed `do_not_promote` verdict for the committed corpus.
- CLI: `review-latency-benchmark.sh score --corpus FILE`.

- [ ] **Step 1: Write the immutable structural fixture**

Create JSONL cases for: known fix only, fix plus test, unrelated new path, force-push, corrupt
receipt, security finding, unavailable required lane, cross-layer no dispute, and new material
dispute. Each line uses the closed shape below plus
`"evidence_tier":"synthetic-structural"`. The scorer accepts no other tier in this task:

```json
{
  "schema": "kc-pr-flow.review-latency-pair/v1",
  "pair_id": "known-fix-only",
  "evidence_tier": "synthetic-structural",
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
    "capability_coverage": [
      {"capability": "correctness", "status": "complete", "gap_ref": null},
      {"capability": "test-coverage", "status": "complete", "gap_ref": null}
    ],
    "capability_gap_refs": [],
    "event_evidence": {
      "effective": {
        "schema": "kc-pr-flow.review-event-evidence/v1",
        "review_key": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "event": "APPROVE",
        "coverage_gap_refs": [],
        "source_sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
      },
      "posted": null
    },
    "adjudicated_posted": 1,
    "adjudicated_false_positive": 0,
    "behavior_hashes": {"event_sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd", "options_sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"},
    "timing": {
      "fixture_kind": "synthetic-structural",
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
      ]
    }
  }
}
```

The fixture must use this full closed shape on every line. Recompute each case's canonical review
key and hashes from its own identity and evidence instead of copying the illustrative repeated hex.
For a treatment whose plan mode is `initial`, set `timing:null`; it remains a Q1-Q5 fallback case
and is never latency-eligible. For `delta` and `resolve`, the structural timing shape is required;
it has no receipt schema or `measured_by` field and never calls itself `ReviewTiming/v1` or
`review-runtime` evidence. The fixture builder
derives `event_evidence.effective` from the bound typed decision artifact and, when a review was
posted, derives `event_evidence.posted` from the bound posting receipt; `source_sha256` is that safe
snapshot's canonical SHA-256, not a caller-authored event claim.

- [ ] **Step 2: Write failing ordered-gate tests**

Follow `review-runtime-benchmark.test.sh:79-205` and assert:

```bash
report="$(bash "$BENCHMARK" score --corpus "$FIXTURE")"
assert_eq "structural corpus never promotes" "do_not_promote" \
  "$(jq -r '.verdict' <<<"$report")"
assert_eq "structural gates still exercise Q1-Q6" "true" \
  "$(jq -r '[.quality_gates[]] + [.latency.structural_pass] | all' <<<"$report")"
assert_eq "target is four minutes" "240000" "$(jq -r '.latency.target_ms' <<<"$report")"
```

This 240000-ms assertion is legacy structural-fixture coverage only. It cannot promote the route;
the real-pair promotion rule in the Captain-approved slimming and measurement amendment controls
Task 4 and later evidence collection.

Q2 passes only when every required capability has a unique `complete` coverage entry and there are
no gap refs, or when every incomplete required capability has a unique gap entry and the bound
effective event—and the posted event when present—is `COMMENT` or `REQUEST_CHANGES`. The latter
also requires `plan.event_ceiling == COMMENT`; an `APPROVE` at any effective/posted layer fails Q2.

Mutate one dimension at a time and require the first failed gate:

| Mutation | Failed gate |
|---|---|
| arbitrary review key or stale head | Q1 `identity` |
| omit a required capability with no gap receipt | Q2 `required_coverage` |
| required capability gap plus effective `APPROVE` | Q2 `required_coverage` |
| remove one expected must-fix | Q3 `must_fix_recall` |
| add adjudicated false positive | Q4 `precision` |
| event/options become less conservative | Q5 `behavior_parity` |
| set one eligible run to `240001` ms | Q6 `latency` |

Add these positive and boundary assertions:

```bash
assert_eq "initial fallbacks are excluded from latency" "2" \
  "$(jq -r '.latency.excluded_initial_runs' <<<"$report")"
assert_eq "only delta and resolve are eligible" "7" \
  "$(jq -r '.latency.eligible_runs' <<<"$report")"

gap_comment="$(mutate_case unavailable-required-lane \
  '.treatment.plan.event_ceiling="COMMENT" |
   .treatment.event_evidence.effective.event="COMMENT" |
   .treatment.event_evidence.effective.coverage_gap_refs=.treatment.capability_gap_refs')"
assert_eq "gaps capped to COMMENT pass Q2" "true" \
  "$(score_gate "$gap_comment" required_coverage)"

gap_request_changes="$(mutate_case unavailable-required-lane \
  '.treatment.plan.event_ceiling="COMMENT" |
   .treatment.event_evidence.effective.event="REQUEST_CHANGES" |
   .treatment.event_evidence.effective.coverage_gap_refs=.treatment.capability_gap_refs')"
assert_eq "gaps capped to REQUEST_CHANGES pass Q2" "true" \
  "$(score_gate "$gap_request_changes" required_coverage)"
```

Also prove Q2 fails for a gap with plan ceiling `APPROVE`, effective event `APPROVE`, missing gap
references, missing/invalid `source_sha256`, or posted `APPROVE`. Prove an initial fallback with
`timing:null` can pass Q1-Q5 and does not change Q6 counts or maximum; an initial fallback carrying
a timing object is rejected instead of improving latency. Reject duplicate capability entries,
duplicate/orphan gap refs, a `complete` entry with non-null `gap_ref`, a `gap` entry with null
`gap_ref`, and extra keys before gate scoring.

Reject symlink/FIFO/oversized corpus, duplicate JSON members, unsafe numbers, self-resealed hashes,
and any structural timing whose closed `fixture_kind` is not `synthetic-structural` or that adds a
receipt `schema` / `measured_by` claim. Assert corpus bytes are unchanged after
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
    def event_at_or_below_comment:
      . == "COMMENT" or . == "REQUEST_CHANGES";
    def hash64: type == "string" and test("^[0-9a-f]{64}$");
    def event_evidence_valid($gaps):
      .treatment.event_evidence as $e |
      ($e | keys | sort == ["effective","posted"]) and
      ($e.effective | keys | sort ==
        ["coverage_gap_refs","event","review_key","schema","source_sha256"]) and
      ($e.effective.schema == "kc-pr-flow.review-event-evidence/v1") and
      ($e.effective.review_key == .exact_head.review_key) and
      ($e.effective.source_sha256 | hash64) and
      ($e.effective.source_sha256 == .treatment.behavior_hashes.event_sha256) and
      (($gaps - $e.effective.coverage_gap_refs) | length == 0) and
      ($e.effective.event | event_at_or_below_comment) and
      ($e.posted == null or
        (($e.posted | keys | sort ==
          ["event","review_key","schema","source_sha256"]) and
         ($e.posted.schema == "kc-pr-flow.posted-review-evidence/v1") and
         ($e.posted.review_key == .exact_head.review_key) and
         ($e.posted.source_sha256 | hash64) and
         ($e.posted.event | event_at_or_below_comment)));
    def coverage_entry_valid($refs):
      (keys | sort == ["capability","gap_ref","status"]) and
      (.capability | type == "string" and length > 0) and
      (if .status == "complete" then .gap_ref == null
       elif .status == "gap" then
         .gap_ref as $gap_ref |
         ($gap_ref | type == "string" and length > 0) and
         ($refs | index($gap_ref)) != null
       else false
       end);
    def capability_coverage_shape:
      .treatment as $t |
      ($t.capability_gap_refs | type == "array" and sort == . and unique == .) and
      ($t.capability_coverage | type == "array" and
        all(.[]; coverage_entry_valid($t.capability_gap_refs))) and
      ([$t.capability_coverage[].capability] | unique | length) ==
        ($t.capability_coverage | length) and
      ([$t.capability_coverage[] | select(.status == "gap") | .gap_ref] | sort) ==
        $t.capability_gap_refs;
    def required_coverage_safe:
      .expected.required_capabilities as $required |
      .treatment.capability_gap_refs as $gaps |
      [.treatment.capability_coverage[] | select(.status == "complete") | .capability] as $completed |
      [.treatment.capability_coverage[] |
        . as $entry |
        select($entry.status == "gap" and ($gaps | index($entry.gap_ref)) != null) |
        $entry.capability] as $documented_gap_caps |
      ($required - $completed) as $missing |
      if ($missing | length) == 0 and ($gaps | length) == 0 then true
      else (($missing - $documented_gap_caps) | length) == 0 and
        (($gaps | length) > 0) and
        (.treatment.plan.event_ceiling == "COMMENT") and event_evidence_valid($gaps)
      end;
    def latency_eligible:
      .treatment.plan.mode == "delta" or .treatment.plan.mode == "resolve";
    def recall($expected; $observed):
      (($expected - $observed) | length) == 0;
    def precision_not_worse:
      .treatment.adjudicated_false_positive <= .control.adjudicated_false_positive;
    sort_by(.pair_id) as $pairs |
    [$pairs[] | select(latency_eligible)] as $eligible |
    ($pairs | all(._derived.identity_valid)) as $q1 |
    ($pairs | all(capability_coverage_shape and required_coverage_safe)) as $q2 |
    ($pairs | all(recall(.expected.must_fix_finding_ids; .treatment.finding_ids))) as $q3 |
    ($pairs | all(precision_not_worse)) as $q4 |
    ($pairs | all(._derived.behavior_parity)) as $q5 |
    (($eligible | length) > 0 and
      ($eligible | all(.treatment.timing.durations_ms.review_to_confirmation_ready <= 240000))) as $q6 |
    {
      schema:"kc-pr-flow.review-latency-promotion/v1",
      phase:"review-plan",
      quality_gates:{identity:$q1,required_coverage:$q2,must_fix_recall:$q3,
        precision:$q4,behavior_parity:$q5},
      latency:{target_ms:240000,eligible_runs:($eligible|length),
        excluded_initial_runs:([$pairs[] | select(.treatment.plan.mode == "initial")]|length),
        passing_runs:([$eligible[] | select(.treatment.timing.durations_ms.review_to_confirmation_ready <= 240000)]|length),
        max_ms:([$eligible[].treatment.timing.durations_ms.review_to_confirmation_ready]|max // null),
        structural_pass:$q6},
      evidence_tier:"synthetic-structural",
      verdict:"do_not_promote"
    }'
}
```

The report may expose whether simulated Q1-Q6 passed, but that field is named `structural_pass` and
does not influence `verdict`. Reject any corpus line whose `evidence_tier` is missing, changed, or
self-resealed. Do not add an `actual` tier in this task: doing so requires a separately approved
source-manifest contract and independently collected evidence.

The external pair schema does not permit `_derived`. Before calling `phase1_promotion`,
`review_latency_validate_pair` recomputes the review key with `review_runtime_sha256`, validates
schema/content hashes and event-ceiling ordering, compares control/treatment behavior hashes, and
adds only the in-memory `_derived:{identity_valid,behavior_parity}` object. Never accept those
booleans from corpus JSON; a corpus member containing `_derived` fails closed as an extra key.
Before scoring, validate the entire closed pair schema and enforce `timing == null` for `initial`,
a valid bound structural timing member of `ReviewLatencyPair/v1` for `delta` or `resolve`, and
equality among
exact-head, plan, timing shape, event-evidence, and behavior receipt identities. Q1-Q5 evaluate
every pair. Structural Q6 and its aggregates evaluate only `delta` and `resolve`; none of these
durations is represented as a measured review or used for promotion.

- [ ] **Step 5: Run GREEN and deterministic scorer checks**

```bash
bash kc-pr-flow/scripts/review-latency-benchmark.test.sh
bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh --case interactive-gates
bash kc-pr-flow/scripts/review-plan.test.sh
```

Expected: all pass; mutations still identify the first structural gate failure, and an entirely
favorable synthetic corpus still returns `do_not_promote` even when latency is one millisecond.

- [ ] **Step 6: Commit structural scoring evidence as its own unit**

```bash
git add kc-pr-flow/scripts/review-latency-benchmark.sh \
  kc-pr-flow/scripts/review-latency-benchmark.test.sh \
  kc-pr-flow/test/fixtures/review-plan/phase1-promotion.jsonl \
  kc-pr-flow/CLAUDE.md
git commit -m "test(kc-pr-flow): keep synthetic latency evidence structural"
```

---

### Task 6: CI ownership and final Phase 1 verification

**Files:**
- Create: `.github/workflows/review-plan-tests.yml`
- Modify: `.github/workflows/review-runtime-tests.yml:7-22,40-48`
- Modify: `.github/workflows/review-evaluation-tests.yml:6-41,50-85`
- Modify: `scripts/review-ci-routing.test.py:11-17,58-66,68-109`

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
The structural corpus report must be `do_not_promote`; a favorable synthetic `promote` result fails
this task even when every individual Q1-Q6 simulation is green.

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

## Post-review repair execution order

Tasks 7-11 are the current execution authority after the 2026-08-27 full-branch review. They repair
the already-implemented Tasks 1-6 without adding a surface or changing the accepted seam.

### Task 7: Make predecessor trust terminal and uncertainty complete

**Files:**
- Modify: `kc-pr-flow/scripts/review-plan.sh`
- Modify: `kc-pr-flow/scripts/review-plan.test.sh`
- Modify: `kc-pr-flow/test/fixtures/review-plan/pr1693-replay.json`

**Interfaces:**
- Consumes: fresh `review-runtime.sh replay` projection.
- Produces: a delta receipt only when every projected lane succeeded and uncertainty is empty; each
  known finding carries replay-derived anchor/category/evidence metadata.

- [ ] Write zero-lane, empty-required-capabilities, failed, unavailable, uncertain-candidate,
  missing-anchor, and mutated-evidence tests; verify each fails before implementation.
- [ ] Require `.lanes | length > 0`,
  `.lanes | all(.result.terminal_status == "succeeded")`,
  `.uncertain_candidate_ids == []`, and receipt `required_capabilities | length > 0` in both
  producer and validator; copy and exactly compare `anchor_sha256`, `category`, and the closed
  evidence pointer.
- [ ] Run `bash kc-pr-flow/scripts/review-plan.test.sh --case receipt-contract` and the full plan
  suite; require all cases green.
- [ ] Commit only the three named paths with
  `fix(kc-pr-flow): require complete predecessor evidence`.

### Task 8: Route every hunk and revalidate every Git operation

**Files:**
- Modify: `kc-pr-flow/scripts/review-plan.sh`
- Modify: `kc-pr-flow/scripts/review-plan.test.sh`
- Modify: `kc-pr-flow/test/fixtures/review-plan/pr1693-replay.json`

**Interfaces:**
- Consumes: Task 7 receipt evidence and `git diff --unified=0`.
- Produces: `resolve` only for fully mapped hunks/signals; safe unmapped work becomes
  `delta`/`COMMENT`; ambiguity becomes `initial`.

- [ ] Add RED cases for two hunks in one known file, an unrelated ordinary append, an
  `unrelated_authorization_bypass` append, contract/test hunks lacking a same-hunk reference,
  dependency/workflow signals, malformed diff, and path replacement between Git reads.
- [ ] Parse each zero-context hunk and implement the exact mapping/signaling rules in revised Task 2;
  do not use file membership as a hunk proxy.
- [ ] Move `review_plan_real_worktree` into `review_plan_git` so it runs immediately before every
  Git invocation; remove cached-canonical bypasses.
- [ ] Run `bash kc-pr-flow/scripts/review-plan.test.sh --case mode-router`, `--case
  trust-boundary`, `--case worktree-safety`, and the full suite; require the adversarial cases to
  select only the revised modes/ceilings.
- [ ] Commit only the three named paths with
  `fix(kc-pr-flow): fail closed on unmapped review hunks`.

### Task 9: Carry the event ceiling through confirmation and posting

**Files:**
- Modify: `kc-pr-flow/scripts/review-plan.test.sh`
- Modify: `kc-pr-flow/skills/kc-pr-review/SKILL.md`
- Modify: `kc-pr-flow/reference/review-triage.md`
- Modify: `kc-pr-flow/reference/review-runtime.md`

**Interfaces:**
- Produces: rerun-and-compare plan validation plus mechanical event checks at legacy, typed,
  autonomous, confirmed-gate, and immediate-pre-post seams. `review-post.sh` remains the posting
  owner and is not modified.

- [ ] Add RED end-to-end harnesses showing the current legacy and typed paths can escalate a
  `COMMENT` plan to `APPROVE`; exercise the exact `review_plan_event_allowed` snippet and pin these
  expectations: flag-off before engagement preserves legacy; fresh `initial` under flag-on
  preserves legacy; no-engagement `delta` blocks; flag loss or unexport after engagement still
  enforces the stored `COMMENT` ceiling (or fails closed); missing/mutated/stale/identity-mismatched
  plan blocks; autonomous and immediate-pre-post paths use the same gate.
- [ ] Implement the immutable input snapshot, in-memory `PLAN_JSON`, existing-`decide`
  rerun/canonical comparison, and event case check from revised Task 3 at every listed seam. Reject
  duplicate JSON members in the raw decision before any jq parse or canonicalization, both on
  initial engagement and on every authority-boundary rerun. Never
  clamp silently to a more favorable event; reject invalid authority. Under flag-on, only a fresh
  rerun that still returns `mode=initial` may preserve legacy authority when no fast path engaged.
  After engagement, make the engagement marker and stored plan digest immutable; flag loss uses the
  stored valid ceiling and cannot restore legacy authority.
- [ ] Rename every four-field trace assertion from byte-identical flow to planner-state parity.
- [ ] Run `bash kc-pr-flow/scripts/review-plan.test.sh --case skill-wiring`, `--case event-ceiling`,
  the full plan suite, `bash kc-pr-flow/scripts/review-runtime.test.sh --case
  interactive-decision`, and `bash kc-pr-flow/scripts/review-post.test.sh`.
- [ ] Commit only the four named paths with
  `fix(kc-pr-flow): enforce delta plan event ceilings`.

### Task 10: Make synthetic evidence structurally non-promotable

**Files:**
- Modify: `kc-pr-flow/scripts/review-latency-benchmark.sh`
- Modify: `kc-pr-flow/scripts/review-latency-benchmark.test.sh`
- Modify: `kc-pr-flow/test/fixtures/review-plan/phase1-promotion.jsonl`
- Modify: `kc-pr-flow/CLAUDE.md`

**Interfaces:**
- Produces: ordered structural Q1-Q6 reporting with `evidence_tier:synthetic-structural` and an
  unconditional `do_not_promote` verdict.

- [ ] Change the favorable-corpus expectation to `do_not_promote`; keep gate-mutation tests that
  name the first structural failure and verify this RED state before implementation.
- [ ] Reject any missing/changed evidence tier and remove synthetic timing/provenance language that
  implies an observed review run. Keep fixture generators explicitly structural.
- [ ] Run `bash kc-pr-flow/scripts/review-latency-benchmark.test.sh`, `bash
  kc-pr-flow/scripts/review-runtime-benchmark.test.sh --case interactive-gates`, and the full plan
  suite; require the committed corpus verdict to be `do_not_promote`.
- [ ] Do not collect actual artifacts or run `review-ablation.sh`; both need separate authorization.
- [ ] Commit only the four named paths with
  `test(kc-pr-flow): keep synthetic latency evidence structural`.

### Task 11: Re-run safe proof and obtain a fresh exact-head review

**Files:**
- Modify only documentation already in the Phase 1 file map if implementation truth changed.

- [ ] Revalidate the worktree root, branch, clean ownership, and exact head before each verification
  batch.
- [ ] Run `review-plan.test.sh`, `review-latency-benchmark.test.sh`, focused timing, full
  `review-runtime.test.sh`, `review-runtime-benchmark.test.sh`, CI routing, `git diff --check`, Bash
  syntax, and pinned ShellCheck v0.9.0. Run `review-post.test.sh` because Task 9 touches its callers.
- [ ] Record that hosted Phase 1 CI cost remains unmeasured unless current provider evidence exists;
  do not invent a per-PR number.
- [ ] Lock the resulting exact head and obtain a fresh full-branch review against the accepted
  design and this amendment, without handing the reviewer the implementation justification.
- [ ] Keep the feature default-off and report `do_not_promote` unconditionally for this Phase 1
  repair. A clean fresh review is necessary but not sufficient: enabling the flag or any promotion
  still requires a separate Captain decision plus the separately authorized actual evidence
  contract.

### Task 18: Bind receipt completeness to canonical review configuration

**Files:**
- Modify: `docs/superpowers/plans/2026-08-26-kc-pr-review-delta-fast-path.md`
- Modify: `docs/superpowers/specs/2026-08-26-kc-pr-review-latency-design.md`
- Modify: `kc-pr-flow/reference/review-runtime.md`
- Modify: `kc-pr-flow/scripts/review-plan.sh`
- Modify: `kc-pr-flow/scripts/review-plan.test.sh`
- Modify: `kc-pr-flow/skills/kc-pr-review/SKILL.md`

**Interfaces:**
- Consumes: one safe canonical `kc-pr-flow.review-config/v1` snapshot, the exact run
  `config_hash`, and the replay-derived unique lane capability set.
- Produces: a receipt only when the snapshot canonically hashes to the run identity and its
  capability set exactly equals replay; a missing or invalid snapshot leaves routing at `initial`.

- [ ] Write the six-configured/one-replayed-lane RED first. Verify producer rejection, receipt
  validator rejection, and `decide` `initial`, then cover full matching lanes, wrong member,
  hash mismatch, missing/symlink/FIFO/oversize/duplicate-key/extra-key/noncanonical snapshots,
  and raw duplicate members before `jq` canonicalization.
- [ ] Reuse the runtime configuration canonicalization rule; do not accept a caller-supplied hash
  or capability list. Add the safe config snapshot to receipt and decision CLI parsing and to each
  internal receipt/decision validator.
- [ ] Make the skill preserve the same immutable config snapshot for its first route and every
  authority-boundary rerun. Preserve default-off and missing-predecessor `initial` behavior.
- [ ] Run focused receipt, trust-boundary, mode-router, and skill-wiring cases, then the full plan
  suite, Bash 5/macOS Bash 3.2 syntax, ShellCheck v0.11 and v0.9 when available, JSON validation,
  and `git diff --check`.

## Deferred promotion-gated phases

This implementation plan ends after Phase 1. Do not add these to a Phase 1 task or commit:

- Phase 2: shared exact-head inventory.
- Phase 3: typed finding collation.
- Phase 4: move shadow/confirmation recipes into runtime and shrink `SKILL.md`; the section above
  permits only behavior-preserving cleanup after frozen measurement truth, never promotion or removal
  of semantic safety text.
- Phase 5: risk-triggered specialist routing, including any reduction of today's unconditional
  security reviewer.
- Phase 6: nonblocking learning and indexed posting state, only if measured timing warrants it.

Each deferred phase needs its own plan after separately authorized actual Phase 1 evidence passes
the earlier quality gates and the Captain accepts the next rollout boundary.
