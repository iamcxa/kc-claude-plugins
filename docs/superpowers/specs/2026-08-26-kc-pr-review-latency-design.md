# Design: `kc-pr-review` latency reduction with evidence-preserving fast paths

- **Date:** 2026-08-26
- **Plugin:** `kc-pr-flow`
- **Target skill:** `kc-pr-flow/skills/kc-pr-review/SKILL.md`
- **Status:** Proposed; awaiting Captain approval
- **Primary outcome:** A post-fix review reaches the existing confirmation gate in at most four
  minutes on the promotion corpus, without losing any expected must-fix finding

## 1. Problem

`kc-pr-review` currently optimizes for broad first-pass coverage. A fresh invocation performs PR
discovery, intent reconstruction, tier selection, a multi-agent panel, pre-scans, compliance and
knowledge scans, test/probe work, optional cross-model reconciliation, typed/shadow preparation,
confirmation, posting, and mandatory learning. That is defensible for an initial review, but it is
too expensive when the same PR returns with a narrow fix for findings that were already reviewed.

The completed RED comparison exposed the mismatch:

| Scenario | Observed shape |
|---|---|
| No-skill control | One focused reviewer; expected completion within four minutes |
| Current skill | At least five lanes; two to five minutes before confirmation, excluding later tails |
| Cross-layer current skill | Codex and Gemini can add serial tails after the main parallel panel |

The design therefore introduces a fast path for trusted post-fix work. It does not promise a
three-times speedup for initial review. The initial-review panel remains the safety fallback until
separate evidence supports changing it.

## 2. Outcome contract

### 2.1 Required outcomes

1. A trusted post-fix review has a deterministic `resolve` or `delta` route instead of silently
   repeating a full initial review.
2. The promotion corpus retains **100% of expected must-fix findings**. Recall is evaluated before
   any latency or token improvement.
3. Eligible post-fix benchmark runs reach a confirmation-ready draft within **240 seconds**,
   measured from the first exact-head snapshot to the completed draft receipt. Human response time,
   GitHub Actions time, and post-confirmation GitHub mutation time are reported separately.
4. Exact-head validation, the quote-the-line gate, posting authorization, and once-only posting
   behavior remain mandatory.
5. Any uncertain identity, ancestry, receipt, required capability, or evidence state fails closed
   to a full review or a `COMMENT` ceiling. It never becomes an inferred clean result.

### 2.2 Quality metrics

Promotion is ordered. A later gate cannot repair an earlier failure.

| Gate | Metric | Acceptance |
|---|---|---|
| Q1 Identity | Exact repository, PR, base, head, config, and receipt binding | All valid; any mismatch rejected |
| Q2 Coverage | Required capability terminals | Complete, or effective event capped at `COMMENT` |
| Q3 Recall | Expected must-fix findings recovered | 100% per corpus case |
| Q4 Precision | Posted findings survive quote and evidence validation | No decrease from the full-review control; zero unquoted actionable findings |
| Q5 Behavior | Event, confirmation options, and posting authority | Same or more conservative than the control |
| Q6 Latency | Exact-head snapshot to confirmation-ready draft | At most 240 seconds per eligible post-fix promotion run |
| Q7 Cost | Reported comparable provider usage | Record only; no promotion claim until provider/scope match |

If Q1-Q5 pass but Q6 fails, the phase is safe but not promoted as a latency improvement. If Q1-Q5
fail, the phase is rolled back regardless of its speed.

### 2.3 Non-goals

- No script decides whether code is semantically correct, secure, aligned with the product goal, or
  worthy of `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`.
- No change to the human confirmation requirement or GitHub posting authority.
- No automatic acceptance of a prior review after new commits.
- No delta mode across a force-push, rebase, amended history, changed base, or untrusted receipt.
- No assumption that a clean specialist lane proves the whole PR secure.
- No initial-review three-times latency promise in this design.
- No concurrent rollout of multiple phases. Each phase earns promotion independently.
- No version bump in the feature change; release-please owns plugin versions.

## 3. Trust and timing model

### 3.1 Review modes

The router emits one of three modes:

| Mode | Meaning | Default work |
|---|---|---|
| `initial` | No trusted predecessor covers this PR lineage | Existing full review flow |
| `delta` | A trusted predecessor exists, but new work exceeds exact finding resolution | Review unseen commits, affected surfaces, and inherited unresolved findings |
| `resolve` | New work is bound to known findings and their adjacent tests/contracts | One focused resolution lane plus required targeted verification |

`delta` and `resolve` are optimizations, not alternative truth systems. They produce the same typed
candidate, finding, evidence, confirmation, and posting contracts as an initial review.

### 3.2 Trusted predecessor

A predecessor is trusted only when all of the following are mechanically verified:

- Its terminal receipt replays successfully through `review-runtime.sh`.
- Repository and PR number match exactly.
- The predecessor head is an ancestor of the current head.
- Base SHA and effective review configuration remain compatible.
- Every known finding has a stable ID and evidence hash.
- The receipt came from private runtime state or an equivalently safe regular-file snapshot.
- Required capability coverage at the predecessor head was complete, or its gaps remain inherited
  and continue to cap the event at `COMMENT`.

Failure of any predicate selects `initial`. A force-push or rewritten history always selects
`initial`; no similarity heuristic may override the ancestry result.

### 3.3 Timing fields

Every benchmark receipt records monotonic durations, not caller-authored wall-clock claims:

```json
{
  "schema": "kc-pr-flow.review-timing/v1",
  "review_key": "<sha256>",
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

`review_to_confirmation_ready` is the promotion metric. Parallel work contributes its critical
path, not the sum of lane durations. External CI and human waits remain visible but do not get
misattributed to the skill.

## 4. Architecture

The fast path is a sequence of deterministic adapters around the existing judgment boundary:

```text
exact PR identity + trusted predecessor
  -> review-plan router
  -> shared exact-head inventory
  -> required reviewer and specialist lanes
  -> typed candidate collation
  -> existing review-runtime confirmation projection
  -> unchanged human confirmation
  -> unchanged authorized posting
```

Scripts may reject, normalize, bind, route, count, sort, deduplicate, and cap authority. They may
not manufacture semantic claims, mark a security surface clean, raise finding confidence, suppress
an evidence-bearing finding, or choose the final review event.

The rollout uses six phases. Each phase has a default-off feature flag, a closed interface, a
fail-closed fallback, an evidence gate, and an independent rollback boundary.

## 5. Phase 1: mode router and trusted delta receipt

### 5.1 Purpose

Add `review-plan.sh`, a deterministic router that decides whether a run is `initial`, `delta`, or
`resolve`. This phase removes the largest repeated cost: applying the full initial-review topology
to an exact-head descendant that only addresses known findings.

The script does not select a verdict. It selects the minimum review obligations that are safe for
the verified lineage and explains every decision with machine-readable reason codes.

### 5.2 Input interface

```text
bash kc-pr-flow/scripts/review-plan.sh decide \
  --repo OWNER/REPO --pr N --base BASE_SHA --head HEAD_SHA \
  --config-hash HASH --repo-worktree DIR \
  [--predecessor-events FILE] [--delta-receipt FILE]
```

Inputs are safe-snapshotted using the existing `review-runtime-safe-io.py` boundary. The script
accepts no PR body, diff prose, agent prompt, event choice, or caller-authored clean/secure claim.

### 5.3 Schemas

`ReviewDeltaReceipt/v1` binds the previous reviewed identity to known findings and their terminal
state:

```json
{
  "schema": "kc-pr-flow.review-delta-receipt/v1",
  "predecessor": {
    "repository": "owner/repo",
    "pr_number": 1693,
    "base_sha": "<40-hex>",
    "head_sha": "<40-hex>",
    "config_hash": "<64-hex>",
    "review_key": "<64-hex>",
    "run_id": "<safe-token>",
    "receipt_id": "<64-hex>"
  },
  "known_findings": [
    {
      "finding_id": "<64-hex>",
      "claim_key": "<safe-token>",
      "evidence_sha256": "<64-hex>",
      "path": "relative/path",
      "side": "RIGHT",
      "resolution_state": "unresolved"
    }
  ],
  "required_capabilities": ["correctness"],
  "coverage_gap_refs": [],
  "content_sha256": "<64-hex>"
}
```

`ReviewPlanDecision/v1` is closed and advisory:

```json
{
  "schema": "kc-pr-flow.review-plan-decision/v1",
  "identity": {
    "repository": "owner/repo",
    "pr_number": 1693,
    "base_sha": "<40-hex>",
    "head_sha": "<40-hex>",
    "config_hash": "<64-hex>"
  },
  "mode": "resolve",
  "reason_codes": ["trusted_predecessor", "ancestor_append", "known_finding_delta"],
  "review_range": {"from_exclusive": "<40-hex>", "to_inclusive": "<40-hex>"},
  "inherited_finding_ids": ["<64-hex>"],
  "required_capabilities": ["correctness", "test-coverage"],
  "event_ceiling": "APPROVE",
  "fallback": "initial"
}
```

`event_ceiling` is a maximum authority bound, not a recommended event. An inherited or newly
detected required coverage gap changes it to `COMMENT`. Confirmed blocker evidence can still select
`REQUEST_CHANGES` through the existing typed decision path.

### 5.4 Routing predicates

`resolve` requires all of:

- a trusted predecessor;
- ancestor-only history growth;
- every changed hunk maps to a known-finding path, its directly imported/consumed contract, or a
  test/fixture for that surface;
- no unknown file class or new security/dependency/workflow signal;
- no inherited required coverage gap.

`delta` requires a trusted predecessor and ancestor-only growth but permits additional affected
surfaces. Those surfaces add capabilities; they never inherit a clean verdict from the predecessor.

All other cases select `initial`. Ambiguity selects `initial` rather than guessing.

### 5.5 Fail-closed fallback

- Missing, malformed, unsafe, stale, hash-mismatched, or replay-invalid receipt -> `initial`.
- Changed base, force-push, non-ancestor head, or unavailable local objects -> `initial`.
- Unknown path classification or unbounded generated diff -> `initial`.
- Incomplete required capability after dispatch -> confirmation may proceed only with `COMMENT` or
  `REQUEST_CHANGES`; never `APPROVE`.
- Router crash or timeout -> ignore its partial output and run the existing initial flow.

### 5.6 Acceptance

| Dimension | Acceptance |
|---|---|
| Recall | 100% of predecessor must-fix IDs remain required until evidence marks them resolved |
| Precision | Router emits no semantic finding and cannot change confidence |
| Latency | Router p95 local execution at most 2 seconds on the fixture corpus |
| Behavior | Force-push, untrusted receipt, and unknown delta select `initial`; coverage gaps cap at `COMMENT` |

### 5.7 RED and GREEN commands

```bash
# RED: tests exist first and fail before review-plan.sh implements the contract.
bash kc-pr-flow/scripts/review-plan.test.sh --case mode-router
bash kc-pr-flow/scripts/review-plan.test.sh --case trust-boundary

# GREEN: router contract plus existing runtime identity gates pass.
bash kc-pr-flow/scripts/review-plan.test.sh
bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision
```

The RED fixtures include PR #1693's shape: known blockers fixed on an appended head, conditional
authorization to approve when verification is green, and no permission to treat unseen work as
already reviewed.

### 5.8 Rollback boundary

`KC_PR_FLOW_DELTA_FAST_PATH=on` enables the router. Unset or any other value runs the current initial
flow and leaves prior receipts readable. Rolling back does not delete receipts or reinterpret them.

## 6. Phase 2: shared exact-head inventory

### 6.1 Purpose

Add one deterministic inventory producer so triage, pre-scan activation, specialist routing, test
selection, and agent prompts stop independently re-reading and reclassifying the same diff.

### 6.2 Interface and schema

```text
bash kc-pr-flow/scripts/review-inventory.sh build \
  --repo-worktree DIR --base BASE_SHA --head HEAD_SHA --output FILE
```

Output `ReviewInventory/v1`:

```json
{
  "schema": "kc-pr-flow.review-inventory/v1",
  "identity": {"base_sha": "<40-hex>", "head_sha": "<40-hex>"},
  "changed_paths": [
    {
      "path": "relative/path",
      "status": "modified",
      "additions": 12,
      "deletions": 3,
      "classes": ["code", "backend"],
      "signals": ["error-handling"]
    }
  ],
  "diff_totals": {"files": 1, "additions": 12, "deletions": 3},
  "signals": {
    "security_sensitive": false,
    "dependency_change": false,
    "workflow_change": false,
    "cross_layer": false,
    "unknown": false
  },
  "candidate_test_paths": [],
  "content_sha256": "<64-hex>"
}
```

The inventory contains facts and conservative signals. `security_sensitive:false` means no
configured mechanical signal matched; it does not mean the diff is secure. Agents receive the
inventory plus the exact diff range, not an inventory-only substitute for source review.

### 6.3 Fail-closed fallback

- Parse failure, binary ambiguity, rename ambiguity, unsafe path, submodule change, or unsupported
  file status sets `signals.unknown=true`.
- An unknown inventory forces `initial` or expands required capabilities; it cannot narrow work.
- Hash or head mismatch discards the inventory and rebuilds once. A second mismatch uses the
  current direct-reading flow and caps a fast-path result at `COMMENT`.

### 6.4 Acceptance

| Dimension | Acceptance |
|---|---|
| Recall | Every changed Git path and status appears exactly once; fixture security/dependency/workflow signals have 100% recall |
| Precision | False-positive signals may add work but never suppress a lane; no semantic cleanliness claim |
| Latency | One inventory build is faster than the median sum of duplicated inventory scans and stays below 3 seconds p95 |
| Behavior | Consumers bind the same base/head/content hash; unknown data expands coverage |

### 6.5 RED and GREEN commands

```bash
bash kc-pr-flow/scripts/review-inventory.test.sh --case exact-head
bash kc-pr-flow/scripts/review-inventory.test.sh --case conservative-signals
bash kc-pr-flow/scripts/review-inventory.test.sh
bash kc-pr-flow/scripts/review-plan.test.sh --case inventory-binding
```

### 6.6 Rollback boundary

`KC_PR_FLOW_REVIEW_INVENTORY=on` makes the shared inventory authoritative for mechanical inputs.
Turning it off restores direct consumers without changing review receipts or posting state.

## 7. Phase 3: typed finding collation

### 7.1 Purpose

Add a deterministic collator for schema validation, evidence binding, stable IDs, deduplication,
source-set merging, quote-gate enforcement, and required-capability accounting. This replaces
repeated ad hoc parsing without transferring semantic judgment to a script.

### 7.2 Semantic boundary

Reviewer lanes still decide whether an issue exists and emit a constrained candidate. The collator
may reject malformed evidence, keep uncertain candidates visible, merge exact fingerprints, and
apply already-specified confidence destinations. It may not invent a claim key, decide two
different claims are equivalent, raise confidence, label code secure, suppress a valid finding, or
choose the review event.

Fingerprint inputs are reviewer-assigned and evidence-bound. On uncertain equivalence, candidates
remain separate. Extra review is safer than a false merge that hides a defect.

### 7.3 Interface and schema

```text
bash kc-pr-flow/scripts/review-collate.sh collate \
  --plan FILE --inventory FILE --candidate-jsonl FILE --output FILE
```

Each `ReviewCandidate/v2` extends the existing candidate shape with presentation-safe evidence:

```json
{
  "schema": "kc-pr-flow.review-candidate/v2",
  "review_key": "<64-hex>",
  "lane_id": "correctness-1",
  "capability": "correctness",
  "candidate_id": "<64-hex>",
  "path": "relative/path",
  "side": "RIGHT",
  "anchor_sha256": "<64-hex>",
  "claim_key": "missing-timeout",
  "category": "correctness",
  "severity": "HIGH",
  "confidence": 8,
  "summary": "Bounded review text",
  "evidence": {
    "pointer": {"schema": "kc-pr-flow.evidence-pointer/v1"},
    "quoted_line_sha256": "<64-hex>",
    "quote_verified": true
  }
}
```

Output `ReviewCollation/v1`:

```json
{
  "schema": "kc-pr-flow.review-collation/v1",
  "review_key": "<64-hex>",
  "findings": [],
  "advisory_candidates": [],
  "uncertain_candidate_refs": [],
  "capability_terminals": [],
  "coverage_gap_refs": [],
  "event_ceiling": "COMMENT",
  "content_sha256": "<64-hex>"
}
```

Raw reviewer prose is bounded and treated as untrusted data. Evidence hashes and Git objects, not
prose similarity, bind a candidate to the reviewed head.

### 7.4 Fail-closed fallback

- Invalid schema, unknown key, duplicate candidate ID, invalid path, stale head, or evidence hash
  mismatch routes the candidate to uncertainty and makes its required capability incomplete.
- Missing or failed required capability creates a coverage gap and caps the event at `COMMENT`.
- A candidate without a surviving quote cannot be actionable; it remains advisory/uncertain.
- Collator failure falls back to current manual collation with the fast path capped at `COMMENT`.
- A valid evidence-bearing finding is never dropped because another lane was silent.

### 7.5 Acceptance

| Dimension | Acceptance |
|---|---|
| Recall | 100% of expected must-fix IDs present after collation; all input candidate refs partition into finding or uncertainty |
| Precision | Zero actionable findings without verified quote/evidence; no decrease in adjudicated precision versus control |
| Latency | Local collation p95 at most 2 seconds for the largest promotion fixture |
| Behavior | Source-set merge, confidence destination, coverage ceiling, and exact-head identity match current contracts |

### 7.6 RED and GREEN commands

```bash
bash kc-pr-flow/scripts/review-collate.test.sh --case evidence-and-dedup
bash kc-pr-flow/scripts/review-collate.test.sh --case coverage-gaps
bash kc-pr-flow/scripts/review-collate.test.sh
bash kc-pr-flow/scripts/review-runtime.test.sh --case evidence-binding
bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh --case interactive-gates
```

### 7.7 Rollback boundary

`KC_PR_FLOW_TYPED_COLLATION=on` enables the collator. Off restores current synthesis. Typed
collation receipts remain readable evidence but grant no posting authority.

## 8. Phase 4: move recipes into the existing tested runtime

### 8.1 Purpose

`SKILL.md` currently embeds large shadow-ledger and typed-confirmation shell recipes. Move their
mechanical behavior behind commands in the existing `review-runtime.sh`, retain the tested schemas,
and replace the embedded code with a short invocation and judgment rules.

This phase is a behavior-preserving extraction. It must not change lane selection, findings,
confirmation options, effective event, or GitHub calls.

### 8.2 Runtime interfaces

The existing runtime gains narrow adapters rather than a second state machine:

```text
bash kc-pr-flow/scripts/review-runtime.sh collect-shadow \
  --observation-file FILE --expected-head SHA --expected-review-key HASH

bash kc-pr-flow/scripts/review-runtime.sh prepare-confirmation \
  --mode legacy|typed --legacy-event EVENT --decision-file FILE \
  --identity-file FILE [--blocker-evidence-file FILE]

bash kc-pr-flow/scripts/review-runtime.sh confirm-post \
  --confirmation-file FILE --requested-event EVENT --state confirmed
```

The outputs remain the existing closed `ShadowObservation/v1`,
`InteractiveCollationDecision/v1`, `InteractiveConfirmation/v1`, and
`InteractivePostGate/v1` contracts. No new authority schema is introduced.

### 8.3 Skill shape

After extraction, `SKILL.md` keeps:

- when each runtime command is called;
- the semantic and authority boundaries;
- exact-head, quote, coverage, confirmation, and posting rules;
- concise failure behavior;
- links to `reference/review-runtime.md` and command `--help`.

It no longer carries copied function bodies or directory-scanning recipes. Any prose cut that can
change findings remains subject to the existing paid ablation gate and explicit budget approval.
Mechanical recipe extraction is covered by behavior-hash parity and shell tests; it is not evidence
that a semantic prose cut is safe.

### 8.4 Fail-closed fallback

- Runtime command failure in typed mode yields the existing `COMMENT` ceiling unless complete,
  independently confirmed blocker evidence preserves `REQUEST_CHANGES`.
- Shadow mode remains best effort and behavior-neutral.
- Confirmation or post-gate validation failure blocks posting.
- No in-run typed-to-legacy fallback may create `APPROVE`.

### 8.5 Acceptance

| Dimension | Acceptance |
|---|---|
| Recall | Candidate/finding/evidence behavior hashes match the pre-extraction control |
| Precision | Draft body, inline comments, event, options, confirmation, and GitHub-call hashes match |
| Latency | Runtime preparation does not regress local p95; SKILL word count decreases by the exact extracted recipe span |
| Behavior | Existing shadow, interactive decision, merge-readiness, and post tests stay green |

### 8.6 RED and GREEN commands

```bash
bash kc-pr-flow/scripts/review-runtime.test.sh --case recipe-extraction
bash kc-pr-flow/scripts/review-shadow.test.sh
bash kc-pr-flow/scripts/review-runtime.test.sh
bash kc-pr-flow/scripts/review-post.test.sh
bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh
```

The RED case compares the documented invocation to the pre-extraction behavior hashes and fails
until the runtime commands own the recipes.

### 8.7 Rollback boundary

`KC_PR_FLOW_RUNTIME_RECIPES=on` selects the extracted path during rollout. Off uses the prior recipe
path until parity is promoted. The final cleanup of embedded recipes occurs only after the flag-on
path passes the promotion corpus; reverting that cleanup restores the previous instruction path.

## 9. Phase 5: risk-triggered specialist routing

### 9.1 Purpose

Replace unconditional specialist dispatch on eligible fast-path runs with conservative,
inventory-driven obligations. This phase begins with `resolve` and `delta`; initial-review routing
does not change until a separate initial-review benchmark earns it.

### 9.2 Routing policy

A security specialist is required when any of the following is true:

- the inventory matches auth, identity, permission, policy, credential, token, secret, crypto,
  network-boundary, deserialization, command-execution, dependency, workflow, infrastructure, or
  deployment signals;
- a predecessor security finding is unresolved or its evidence surface changed;
- the delta crosses a trust boundary or changes an externally reachable interface;
- the inventory is unknown;
- the focused reviewer requests escalation.

Supply-chain and GitHub Actions specialists retain their existing dependency/workflow triggers.
Cross-model review is required on the fast path only when an unresolved predecessor dispute needs
it or a newly found material conflict activates the existing arbitration contract. Provider silence
never clears a finding.

### 9.3 Policy schema

```json
{
  "schema": "kc-pr-flow.specialist-routing-policy/v1",
  "review_key": "<64-hex>",
  "mode": "resolve",
  "obligations": [
    {
      "capability": "security",
      "required": false,
      "activation_reason_codes": [],
      "fallback_event_ceiling": "COMMENT"
    }
  ],
  "content_sha256": "<64-hex>"
}
```

The script emits obligations, not security verdicts. `required:false` means the configured
mechanical activation predicate did not require a specialist for this delta. The focused reviewer
still reviews correctness and may escalate.

### 9.4 Fail-closed fallback

- Unknown or malformed inventory -> require the specialist or run `initial`.
- Required specialist unavailable after the one existing bounded retry/manual evidence path ->
  coverage gap and `COMMENT` ceiling.
- A prior security finding cannot be resolved without evidence from its required capability.
- Any recall loss in the shadow comparison immediately disables risk routing.

### 9.5 Acceptance

| Dimension | Acceptance |
|---|---|
| Recall | 100% must-fix recall overall and 100% of security-labeled expected findings on the promotion corpus |
| Precision | No increase in posted false positives; skipped specialists do not produce clean/security claims |
| Latency | Eligible post-fix runs meet 240 seconds without relying on a missing required lane |
| Behavior | Unknown, trust-boundary, dependency, workflow, and inherited-security cases still dispatch specialists or cap at `COMMENT` |

### 9.6 RED and GREEN commands

```bash
bash kc-pr-flow/scripts/review-specialist-routing.test.sh --case conservative-triggers
bash kc-pr-flow/scripts/review-specialist-routing.test.sh --case inherited-security
bash kc-pr-flow/scripts/review-specialist-routing.test.sh
bash kc-pr-flow/scripts/review-latency-benchmark.sh shadow --corpus post-fix
```

The shadow benchmark compares risk routing with the full specialist control on the same exact
heads. Promotion requires all quality gates before latency is considered.

### 9.7 Rollback boundary

`KC_PR_FLOW_RISK_ROUTING=on` enables conditional specialists for `delta`/`resolve` only. Off restores
the unconditional specialist topology. The policy receipt is advisory and has no posting authority.

## 10. Phase 6: nonblocking learning and indexed posting state

### 10.1 Entry criterion

This phase is implemented only if phase 1-5 timing receipts show that post-collation learning or
state-directory scanning materially blocks the target. “Material” means either contributes at
least 10% of median `review_to_confirmation_ready`, or at least 20 seconds p50, on the promoted
post-fix corpus. Without that evidence, this phase is not built.

### 10.2 Nonblocking learning

Step 8 becomes a durable candidate enqueue followed by later evaluation:

```json
{
  "schema": "kc-pr-flow.learning-candidate/v1",
  "review_key": "<64-hex>",
  "finding_fingerprints": ["<64-hex>"],
  "candidate_kinds": ["skill", "project"],
  "created_at": "<RFC3339>",
  "content_sha256": "<64-hex>"
}
```

The current review may return after a mode-`0600` candidate is durably queued. A later explicit
learning command or the next review drains it. Project-level writes still require human
confirmation. Learning failure never changes the already-confirmed review event or retries a post.

### 10.3 Posting state index

Replace per-invocation directory scans with an atomic index from exact review key to candidate run
IDs:

```json
{
  "schema": "kc-pr-flow.pending-post-index/v1",
  "repository_key": "<64-hex>",
  "pr_number": 1693,
  "entries": [
    {
      "review_key": "<64-hex>",
      "run_id": "<safe-token>",
      "state": "pending",
      "pending_payload_sha256": "<64-hex>"
    }
  ],
  "content_sha256": "<64-hex>"
}
```

The index is an optimization, not authority. Every hit is revalidated against the run events and
pending payload before use. A missing, corrupt, or stale index falls back to the existing bounded
scan; it never licenses a fresh post or deletes evidence.

### 10.4 Fail-closed fallback

- Learning queue failure is surfaced but does not rewrite or repeat the posted review.
- Index mismatch or unsafe file -> existing scan.
- Ambiguous remote posting outcome -> preserve pending state and follow existing reconciliation;
  never infer success or retry from the index.
- Garbage collection remains governed by existing retention and terminal-result rules.

### 10.5 Acceptance

| Dimension | Acceptance |
|---|---|
| Recall | Learning fingerprints are durably queued without changing review finding recall |
| Precision | Existing D1/D2 write thresholds and human gate remain unchanged |
| Latency | Removes the measured blocking contribution that justified the phase |
| Behavior | Once-only posting tests show no duplicate, stale-head post, premature GC, or lost ambiguous state |

### 10.6 RED and GREEN commands

```bash
bash kc-pr-flow/scripts/review-learning-queue.test.sh
bash kc-pr-flow/scripts/review-post.test.sh --case state-index
bash kc-pr-flow/scripts/review-post.test.sh
bash kc-pr-flow/scripts/review-latency-benchmark.sh compare --corpus post-fix
```

### 10.7 Rollback boundary

`KC_PR_FLOW_NONBLOCKING_TAILS=on` enables both optimizations only after the entry criterion and
tests pass. Off restores blocking learning and directory scanning while retaining queued candidates
and pending-post evidence for safe reconciliation.

## 11. Benchmark and promotion protocol

### 11.1 Corpus

The post-fix corpus contains at least these fixed classes:

1. Known blocker fixed by one appended commit, no new surface.
2. Known blocker fixed plus adjacent regression test.
3. Known blocker fixed plus unrelated new code: must select `delta` or `initial`, not `resolve`.
4. Force-pushed head: must select `initial`.
5. Untrusted or corrupted predecessor receipt: must select `initial`.
6. Security finding fixed on a security surface: specialist remains required.
7. Required lane unavailable: confirmation allowed only with a `COMMENT` ceiling.
8. Cross-layer predecessor with no new dispute: no unnecessary serial arbitration tail.
9. New material cross-model conflict: arbitration remains conditional and bounded; timeout leaves
   the dispute visible and caps authority rather than hiding it.

Each case binds immutable base/head SHAs, expected must-fix finding IDs, required capabilities, and
the maximum permitted event. PR #1693 supplies the first real-world replay shape; sanitized fixtures
make the suite stable and public-safe.

### 11.2 Arms

| Arm | Meaning |
|---|---|
| Control | Current full `kc-pr-review` behavior at the pinned head |
| Shadow | New phase computes receipts but cannot alter dispatch, draft, event, or posting |
| Treatment | Promoted phase owns its bounded interface behind the feature flag |

Run control and treatment with the same model/provider family and comparable scope when making
token claims. Latency remains valid when independently measured by the runtime, but provider delays
and unavailable lanes must stay visible in the report.

### 11.3 Promotion report

Extend the existing ordered G1-G5 benchmark philosophy rather than replace it:

```json
{
  "schema": "kc-pr-flow.review-latency-promotion/v1",
  "phase": "review-plan",
  "quality_gates": {
    "identity": "pass",
    "required_coverage": "pass",
    "must_fix_recall": "pass",
    "precision": "pass",
    "behavior_parity": "pass"
  },
  "latency": {
    "target_ms": 240000,
    "eligible_runs": 9,
    "passing_runs": 9,
    "max_ms": 231000
  },
  "verdict": "promote"
}
```

The scorer emits `do_not_promote` on any earlier quality failure, regardless of latency. A run that
times out without complete required evidence may complete as `COMMENT`, but it cannot count as a
successful four-minute `APPROVE`-eligible run.

### 11.4 Full verification command set

```bash
bash kc-pr-flow/scripts/review-plan.test.sh
bash kc-pr-flow/scripts/review-inventory.test.sh
bash kc-pr-flow/scripts/review-collate.test.sh
bash kc-pr-flow/scripts/review-specialist-routing.test.sh
bash kc-pr-flow/scripts/review-runtime.test.sh
bash kc-pr-flow/scripts/review-shadow.test.sh
bash kc-pr-flow/scripts/review-post.test.sh
bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh
bash kc-pr-flow/scripts/review-latency-benchmark.test.sh
bash scripts/skill-frontmatter-lint.sh
bash scripts/version-parity-check.sh
```

The paid `review-ablation.sh` experiment is not silently added to this command set. Any semantic
instruction cut that needs it must present the current measured budget and obtain explicit approval
before starting the pre-registered run.

## 12. Preserved authority and failure invariants

The following remain true in every phase:

1. **Exact head:** the draft and post bind the current full head SHA. A moved head invalidates the
   draft until its unseen delta or rewritten full diff is reviewed.
2. **Quote gate:** every actionable finding cites and survives verification of its motivating line.
3. **Coverage:** missing required capabilities are visible and forbid `APPROVE`.
4. **Finding recall:** a predecessor must-fix finding remains open until evidence at the descendant
   head resolves it; absence from a new lane is not resolution.
5. **Security:** scripts route and validate evidence; reviewers judge security.
6. **Goal:** agents judge whether the PR achieves its stated goal; scripts only carry the result.
7. **Verdict:** typed projections constrain possible events but do not choose on semantic grounds.
8. **Human authority:** interactive posting requires the existing confirmed post gate.
9. **Post safety:** `review-post.sh` remains the only network/posting authority under once-only mode.
10. **Ambiguity:** force-push, untrusted receipt, unknown inventory, evidence drift, and full coverage
    gaps expand review or cap at `COMMENT`; none create a clean result.

## 13. Expected rollout effect

Phase 1 should produce most of the post-fix latency gain by replacing a repeated full panel with a
trusted focused route. Phases 2-4 remove repeated local work and instruction load while preserving
the judgment topology. Phase 5 removes specialist lanes only where exact-head shadow evidence proves
that conservative routing preserves recall. Phase 6 is conditional and is not built unless timing
attribution shows its tails are material.

The target is deliberately asymmetric: post-fix review earns an at-most-four-minute path with 100%
known-finding recall; initial review keeps its current coverage until independent evidence supports
a narrower topology.
