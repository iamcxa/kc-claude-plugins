---
title: Synthesize exact-head EM merge readiness before human landing
status: implementation
source: captain direction 2026-07-30 after reconcile-list-element-shape closeout
started: 2026-07-30T15:01:36Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-agy-first-whole-diff-review-seat
issue:
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design: required
lane:
id: 4a255s3z87s7x09vn2fnscep
product: kc-pr-flow
sprint: S6
---

## Captain-authored recut

The historical slug came from a broader proposal that bundled mandatory agy/Gemini routing,
daemon review-and-repair policy, and Carlove adoption. Sprint `kc-pr-flow/S6` narrows `4a` to one
end value: for one exact PR head, EM synthesizes existing CI, test, and review evidence into
`READY`, `NOT_READY`, or `UNKNOWN` with explicit confidence. Humans remain the sole merge
authority.

The captain already established the scope, appetite, cheapest cut, and exclusions in the dispatch,
so ideation does not reopen those questions. This is the stated small-scope reason for skipping a
new captain questionnaire.

## Problem

`kc-pr-review` already knows which exact head it reviewed, calibrates finding confidence, runs
tests, derives a typed review collation decision, and protects review posting with a human
confirmation gate. A separate daemon seam already observes CI. What it does not provide is one
deterministic landing projection that tells EM whether the combined evidence for that same head is
decisively ready, decisively not ready, or insufficient.

Without that projection, a human sees several nearby but non-equivalent signals:

- `APPROVE`, `COMMENT`, and `REQUEST_CHANGES` are review-post events, not a landing decision;
- a CI failure is decisive negative evidence, while pending or absent required CI is uncertainty;
- a test failure is decisive negative evidence, while a required test with no result is uncertainty;
- a moved head invalidates the combined evidence rather than proving the new head not ready.

Collapsing those states into a prose judgment risks treating incomplete evidence as clean, or
treating review-post authorization as merge authority. The bounded problem is landing synthesis,
not reviewer selection, posting, repair, or merge automation.

## Scope

### In

- Define one closed, deterministic, read-only EM decision contract over:
  - the existing `InteractiveCollationDecision/v1`;
  - one exact-head CI observation;
  - one exact-head test observation; and
  - one independently supplied observed PR head.
- Emit exactly one advisory `MergeReadinessDecision/v1` with:
  - `READY`, `NOT_READY`, or `UNKNOWN`;
  - explicit contract confidence;
  - the exact review identity;
  - a canonical input binding; and
  - sorted reason codes.
- Reject or fail closed on malformed input, unknown keys, contradictory states, or any head/identity
  mismatch.
- Preserve the existing per-finding confidence calibration and typed collation decision as inputs.
  The new adapter does not re-review, re-score findings, or reconstruct a decision from prose.
- Add focused RED-before-GREEN contract tests, one real CLI round trip, and the required
  `kc-pr-flow` documentation updates.

### Out

- `vf`: daemon review-post authority reconciliation.
- `x0f`: live freshness/coverage producers and their policy for populating the input observations.
- Auto-merge or any `gh pr merge` operation.
- Review posting, review-post authorization, or changes to the §6c human confirmation gate.
- Title/body auto-authoring, daemon redesign, ACP, or a general repair loop.
- Mandatory agy/Gemini routing, a new model seat, or a new review runtime.
- Carlove or any other cross-repo adoption.
- A new multi-model, daemon, or cross-repository evidence program.

If an acceptance criterion cannot be satisfied without one of those surfaces, implementation stops
and returns for a re-cut.

## Appetite and implementation sizing

- **Ideation-declared estimate:** one implementation worker session, at most **90 minutes**.
- **Declared tolerance:** **0 minutes** beyond that session. The worker parks with tests and an
  explicit open finding rather than silently extending the budget.
- **Hard stop:** any need to add a new evidence runtime, fetch live GitHub state inside the adapter,
  alter daemon/posting authority, add model routing, or adopt another repository.
- **Sizing:** ONE worker. The work is one behavior seam and one RED→GREEN loop; it is below the
  split triggers of more than 90 minutes, three independent behaviors, or meaningful parallel
  worktree benefit.

## Reverse-recovery audit

Audit pin: fresh `origin/main` fetched on 2026-07-30 at
`9cc0d1faa49e786837342b88062181460f037ac3`. The implementation branch has no
`kc-pr-flow/**` delta from that pin.

### Search strategies for the absence claim

**Strategy A — domain and verdict vocabulary.**

```bash
git grep -n -E '\b(READY|NOT_READY|UNKNOWN)\b' origin/main -- \
  kc-pr-flow/skills kc-pr-flow/scripts kc-pr-flow/reference kc-pr-flow/docs
git grep -n -i -E \
  'landing[ -_](decision|synthesis)|merge[ -_](readiness|decision)|ready[ -_]to[ -_]merge' \
  origin/main -- kc-pr-flow/skills kc-pr-flow/scripts kc-pr-flow/reference kc-pr-flow/docs
```

The first command returned no operational verdict enum. The second returned only the prose phrase
“merge-readiness” in `reference/learned-patterns.md:531`; it is not a contract and consumes none of
CI, test, or typed review evidence.

**Strategy B — structural/schema inventory.**

```bash
git ls-tree -r --name-only origin/main kc-pr-flow |
  rg '(review|decision|merge|runtime|post)'
git grep -n -E \
  'kc-pr-flow\.[a-z0-9-]*(decision|verdict|readiness)|InteractiveCollationDecision|effective_event' \
  origin/main -- kc-pr-flow/scripts kc-pr-flow/reference kc-pr-flow/skills
```

This found the existing interactive collation decision, review-post gates, and the unrelated
ablation verdict. It found no executable schema or adapter that accepts CI + test + review evidence
for one head and emits a landing verdict.

### Layer classification

| Layer / seam | Classification | Fresh-main evidence | Disproof hook |
|---|---|---|---|
| PR head freshness and exact reviewed head | `WORKING_UNIT_UNPROVEN` | `skills/kc-pr-review/SKILL.md:110-119` records, rechecks, and re-reviews a moved head. `reference/review-runtime.md:81-104` binds the event lifecycle to immutable exact-head identity. | Run a controlled review where the PR head moves after collation; if the old result can still offer `APPROVE` without a delta/full re-review, reclassify `EXISTS_BROKEN`. |
| Typed review evidence and collation | `WORKING_UNIT_UNPROVEN` | `reference/review-runtime.md:123-139` defines the closed decision and evidence pointers. `scripts/review-runtime.sh:2316-2362` deterministically emits coverage, blockers, gaps, and the effective event. Focused suite: `305 passed, 0 failed`. | Corrupt a fixture's `head_sha`, `review_key`, or evidence hash and run `bash kc-pr-flow/scripts/review-runtime.test.sh`; acceptance would disprove the classification. |
| Finding confidence calibration | `WORKING_UNIT_UNPROVEN` | `skills/kc-pr-review/SKILL.md:975-997` requires quote-the-line verification and maps confidence bands before findings reach the final review decision. | A controlled fixture in which a `4/10` unverified finding reaches a posted inline CODE comment, or a `7/10` verified blocker disappears, disproves the classification. |
| Test evidence | `WORKING_UNIT_UNPROVEN` | `skills/kc-pr-review/SKILL.md:729-750` makes tests first-class review evidence with explicit event effects; `:1022-1037` renders the structured verification summary. | Run a testable PR review whose deterministic failing test does not reach Step 5/6 or affect the event; that would be `EXISTS_BROKEN`. |
| CI observation | `WORKING_UNIT_UNPROVEN` | `reference/pr-review-loop.md:20-28` binds `ci-gate` lookup to the PR head and distinguishes success, pending, failure, and none. It is an existing input source, not yet a landing contract. | Compare the recorded state with `gh api repos/{owner}/{repo}/statuses/<exact-head>`; a mismatch or an observation bound to another SHA disproves it. |
| Interactive review-post authority | `WORKING_UNIT_UNPROVEN` | `skills/kc-pr-review/SKILL.md:1641-1668` requires a closed `human_confirmed` gate; `:1723-1765` keeps §6c and its receipt as the posting authority. `scripts/review-post.sh:630-655` rechecks the head before mutation. Focused suite: `156 passed, 0 failed`. | Forge `human_confirmed:false`, change the event after confirmation, or move the head; if `review-post.test.sh` permits a POST, reclassify `EXISTS_BROKEN`. |
| Exact-head EM landing synthesis | `MISSING` | Both searches above found no operational `READY` / `NOT_READY` / `UNKNOWN` decision contract. The roadmap independently names only this gap at `docs/dev/ROADMAP.md:132-138`. | Re-run both searches on fresh `origin/main`. If an executable contract is found that accepts exact-head CI, test, and typed review evidence and emits a closed advisory landing verdict, stop and reclassify it instead of building another adapter. |

The `InteractiveCollationDecision/v1` is deliberately **not** classified `MISSING`: it is a
substantial existing review decision and the primary input to this task. Its incomplete fit for
landing synthesis is the reason to add a narrow adapter above it, not to replace it.

## Approaches considered

### Recommended — one pure decision adapter

Add one deterministic, read-only adapter to the existing review-runtime component. It accepts a
closed JSON input, validates identity and evidence state, and emits a closed advisory decision.
This reuses the shipped exact-head and collation seams and gives tests a single executable truth
table.

### Rejected fastest path — prose-only EM mapping

A short instruction telling EM how to read the signals is faster to author, but it cannot enforce
same-head binding, reject unknown keys, or prove that pending evidence never becomes `READY`. It
does not satisfy the acceptance criteria.

### Not taken — extend the review/daemon program

Extending `InteractiveCollationDecision/v1`, adding model routing, making the daemon fetch and post
the decision, or adopting other repositories could produce a more complete program. It changes
multiple authorities and depends on `vf`/`x0f`; none is needed to prove the core landing contract.

**Fastest path:** prose-only mapping, rejected because it is not executable or falsifiable.

**Smallest cut that satisfies the ACs:** one pure adapter plus its direct tests and documentation.

**Taking the cheap path:** the pure adapter. No captain scope cut is being made; the more thorough
program is already explicitly out of scope.

## Design determination

`design: required` because this task decides a new contract/interface shape.

### Input contract

The adapter consumes one closed `kc-pr-flow.merge-readiness-input/v1` object:

```json
{
  "schema": "kc-pr-flow.merge-readiness-input/v1",
  "review_identity": {
    "repository": "owner/repo",
    "pr_number": 42,
    "base_sha": "1111111111111111111111111111111111111111",
    "head_sha": "2222222222222222222222222222222222222222",
    "config_hash": "3333333333333333333333333333333333333333333333333333333333333333",
    "review_key": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "run_id": "run-example"
  },
  "observed_head_sha": "2222222222222222222222222222222222222222",
  "ci": {
    "required": true,
    "status": "PASS",
    "head_sha": "2222222222222222222222222222222222222222",
    "evidence_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "tests": {
    "required": true,
    "status": "PASS",
    "head_sha": "2222222222222222222222222222222222222222",
    "evidence_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
  },
  "review_decision": {
    "schema": "kc-pr-flow.interactive-collation-decision/v1",
    "review_identity": "<exactly the same object as review_identity>",
    "mode": "typed",
    "coverage": "complete",
    "approve_eligible": true,
    "effective_event": "APPROVE",
    "capabilities": [],
    "confirmed_blocker_refs": [],
    "capability_gap_refs": [],
    "confirmation_input": "<existing closed object>"
  }
}
```

Rules:

- `ci.status` and `tests.status` each belong to
  `PASS | FAIL | PENDING | UNKNOWN | UNAVAILABLE | NOT_REQUIRED`.
- `NOT_REQUIRED` is valid only when that observation's `required` is false.
- All three head values and the nested decision identity must equal
  `review_identity.head_sha`.
- The nested review decision must satisfy the existing
  `InteractiveCollationDecision/v1` validator. The adapter does not reconstruct it from prose.
- Unknown keys, duplicate keys, malformed hashes, or contradictory required/status pairs are invalid.
- `observed_head_sha` is an input, not fetched by this task. `x0f` owns the later live producer and
  freshness/coverage wiring.

### Output contract

For valid or contract-invalid input that can be safely read, emit exactly one closed
`kc-pr-flow.merge-readiness-decision/v1`:

```json
{
  "schema": "kc-pr-flow.merge-readiness-decision/v1",
  "review_identity": "<validated identity or null>",
  "input_sha256": "<sha256 of canonical input or null>",
  "verdict": "READY",
  "confidence": "HIGH",
  "reason_codes": ["all-required-evidence-positive"],
  "advisory_only": true
}
```

`reason_codes` are sorted and unique. `confidence` is contract confidence, not a new model score:

- `HIGH` means exact-head evidence is structurally complete and already decisive.
- `LOW` means readiness cannot be established from the supplied evidence.

The existing 1–10 finding confidence is consumed indirectly through the validated, post-calibration
review decision and is never recomputed. There is intentionally no medium landing confidence in
this cut: evidence is either sufficient for a decisive verdict or the result is `UNKNOWN`.

Unreadable/unsafe input may return nonzero with no decision; every caller must map adapter failure
to `UNKNOWN`, never to `READY`.

### Fail-closed decision table

Apply rows in order:

| Priority | Condition | Verdict | Confidence | Required reason |
|---|---|---|---|---|
| 1 | Input is malformed, has unknown/duplicate keys, contains an invalid nested decision, or has contradictory status/required fields | `UNKNOWN` | `LOW` | `invalid-input` |
| 2 | `observed_head_sha`, CI head, test head, nested decision identity, or top-level review identity disagree | `UNKNOWN` | `LOW` | `head-or-identity-mismatch` |
| 3 | On the same exact head, required CI or tests are `FAIL`, or the review decision has confirmed blockers / `REQUEST_CHANGES` | `NOT_READY` | `HIGH` | one or more of `ci-failed`, `tests-failed`, `review-blocked` |
| 4 | No decisive negative exists, but required CI/tests are pending, unknown, unavailable, or incorrectly not-required; or review coverage is incomplete / not approval-eligible | `UNKNOWN` | `LOW` | one or more of `ci-incomplete`, `tests-incomplete`, `review-incomplete` |
| 5 | Every required CI/test observation is `PASS`, every non-required observation is `NOT_REQUIRED`, the review decision is exact, complete, approval-eligible, `APPROVE`, and blocker/gap-free | `READY` | `HIGH` | `all-required-evidence-positive` |
| 6 | Any otherwise unreachable combination | `UNKNOWN` | `LOW` | `inconsistent-input` |

An exact-head negative in row 3 is sufficient to prove `NOT_READY` even if another required signal
is pending: one current blocker is decisive. Identity mismatch in row 2 takes precedence because old
negative evidence says nothing authoritative about the new head.

### Authority and side-effect boundary

- The adapter reads one bounded input and writes one JSON decision to stdout.
- It has no model, network, GitHub mutation, review-post, authorization, retry, daemon, or merge
  capability.
- `advisory_only` is always `true`; no output field can authorize posting or merging.
- §6c remains the interactive review-post authority. Humans remain the only merge authority.
- A consumer may display the decision but must never translate `READY` into an automatic merge.

## Acceptance criteria

**AC-1 — One exact-head input yields a closed readiness verdict.**
Verified by: `bash kc-pr-flow/scripts/review-runtime.test.sh` plus a direct `bash kc-pr-flow/scripts/review-runtime.sh decide-merge-readiness --input-file <fixture>` CLI round trip extending the existing decision fixture surface beside `kc-pr-flow/skills/kc-pr-review/SKILL.md:1270-1388` and asserting the complete positive, negative, and incomplete outputs. Falsified by: changing a positive fixture's CI status to `FAIL` while retaining expected `READY`, or deleting the production negative-evidence branch, makes the focused suite fail.

For one valid exact-head input, the adapter emits exactly one closed decision: all required positive
evidence yields `READY/HIGH`; an exact-head CI failure, test failure, or confirmed review blocker
yields `NOT_READY/HIGH`; and incomplete required evidence yields `UNKNOWN/LOW`. The baseline on
`origin/main@9cc0d1f` has no such command or schema, so the first contract invocation is the required
RED.

**AC-2 — Identity failures cannot produce `READY`.**
Verified by: the negative fixture matrix extending `kc-pr-flow/scripts/review-runtime.test.sh:261`, including one-field-at-a-time head mutations and duplicate-key input, plus a direct CLI assertion that no case emits `READY`.
Falsified by: removing any one same-head equality check makes its targeted mutation fixture emit `READY` and fail the suite.

A moved observed head, mismatched CI/test head, nested review identity drift, malformed hash,
duplicate/unknown key, or invalid required/status pair cannot produce `READY`; each safely readable
case yields `UNKNOWN/LOW` with the matching reason, while unreadable input exits nonzero and the
documented caller behavior is `UNKNOWN`.

**AC-3 — The decision adds no post or merge authority.**
Verified by: `bash kc-pr-flow/scripts/review-post.test.sh`, a merge-readiness CLI test with failing `gh`/network stubs and an empty call ledger, and a path-scoped diff assertion protecting `kc-pr-flow/skills/kc-pr-review/SKILL.md:1723` and the gate negatives at `kc-pr-flow/scripts/review-post.test.sh:227`.
Falsified by: adding any `gh` call populates the ledger and fails the focused test; changing §6c changes the protected recipe assertion.

The new decision is read-only and advisory. It neither creates a posting receipt nor calls a model,
network client, `gh pr review`, or `gh pr merge`; the existing §6c human confirmation and
review-post gates remain unchanged and green.

**AC-4 — The implementation remains one bounded adapter.**
Verified by: `git diff --name-only origin/main...HEAD`, `git diff --check`, the focused runtime/post suites, and consistency searches anchored at `kc-pr-flow/CLAUDE.md:45`, `kc-pr-flow/README.md:50`, and `kc-pr-flow/reference/review-runtime.md:123` plus the changed executable/test paths.
Falsified by: any changed path or command implementing a listed out-of-scope system, or any published claim that `READY` authorizes merge, fails scope review.

Implementation adds only the deterministic adapter to the existing review-runtime component, its
direct tests, and the approved `kc-pr-flow` documentation updates. It does not add agy routing,
daemon behavior, live evidence fetching, repair loops, cross-repo adoption, or a second runtime.

## Test plan

1. **RED before GREEN**
   - Add the final contract fixtures and assertions first.
   - Invoke `review-runtime.sh decide-merge-readiness` on untouched implementation.
   - Record the expected nonzero/unknown-command RED; do not treat prose grep as RED.
2. **Closed-schema validation**
   - Exercise valid exact identity, each status enum, unknown key, duplicate key, malformed hash,
     invalid nested decision, and contradictory `required`/`NOT_REQUIRED`.
3. **Decision-table coverage**
   - Positive all-pass → `READY/HIGH`.
   - CI fail, test fail, and review blocker independently → `NOT_READY/HIGH`.
   - Negative plus another pending signal → `NOT_READY/HIGH`.
   - Pending, unknown, unavailable, and required-but-not-required without a negative →
     `UNKNOWN/LOW`.
   - Moved observed head and each one-field identity drift → `UNKNOWN/LOW`.
4. **Purity/authority**
   - Put failing stubs for `gh` and likely network commands first on `PATH`.
   - Run the real CLI and require an empty call ledger.
   - Preserve the §6c/post-gate recipe byte-for-byte.
5. **Regression**
   - `bash kc-pr-flow/scripts/review-runtime.test.sh`
   - `bash kc-pr-flow/scripts/review-post.test.sh`
   - `git diff --check`
6. **CLI E2E**
   - Invoke the committed adapter from a shell with a real fixture file and parse its stdout with
     `jq`; this is the end-to-end surface for this CLI-only contract.
   - Browser/full-stack E2E is skipped because the task has no UI, service, or remote mutation.
7. **Scope/doc review**
   - Inspect changed paths and search for contradictory merge-authority wording.
   - Re-run the two absence searches before implementation; if the `MISSING` premise collapsed on
     fresh `origin/main`, stop instead of adding a duplicate adapter.

## Proposed documentation diff

The behavior is published through `kc-pr-flow` runtime documentation, so docs land with the
adapter:

- `kc-pr-flow/reference/review-runtime.md` CLI table, before: no merge-readiness command. After:
  “`decide-merge-readiness --input-file FILE` validates one closed exact-head CI/test/review input
  and emits one advisory `MergeReadinessDecision/v1`; it performs no network, post, authorization,
  or merge operation.”
- `kc-pr-flow/CLAUDE.md` typed-runtime section, after:
  “EM landing synthesis is a read-only projection over the existing collation decision and
  caller-supplied exact-head CI/test observations. `READY` is advisory and never merge authority;
  invalid, stale, or incomplete required evidence yields `UNKNOWN`.”
- `kc-pr-flow/README.md`, mirror the user-facing verdict/confidence vocabulary and the
  human-only merge-authority boundary.

No `PRODUCT.md` or `ARCHITECTURE.md` change is proposed: this is a bounded plugin runtime contract
already documented in the plugin-owned published surfaces. The §6c review-post wording is not
changed.

## Spike determination

No spike needed. The risky mechanism is closed JSON validation plus deterministic jq projection,
and the existing component already proves it:

- `review-runtime.sh:2316-2362` emits the exact-head interactive collation decision;
- `review-runtime.test.sh` is green at `305 passed, 0 failed`;
- `review-post.test.sh` is green at `156 passed, 0 failed`.

Implementation still rechecks the load-bearing `MISSING` claim on fresh `origin/main` before RED.

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is **criteria that pass without
delivering value**: a fixture can claim `READY` while one CI/test observation is not actually bound
to the review decision's exact head.

## Stage Report: ideation

TL;DR: Re-cut historical `4a` into one pure EM landing-decision adapter over recovered exact-head
review, CI, and test evidence. The design emits advisory `READY`, `NOT_READY`, or `UNKNOWN` with
explicit confidence, fails closed on stale/incomplete evidence, preserves §6c and human merge
authority, and excludes agy/daemon/cross-repo expansion.

- DONE: Preserved the captain-authored S6 end value and exclusions; did not reopen scope.
- DONE: Fetched and audited `origin/main@9cc0d1f` with domain-vocabulary and structural/schema
  searches.
- DONE: Classified exact-head identity, typed review evidence, confidence calibration, tests, CI
  observation, and review-post authority as existing `WORKING_UNIT_UNPROVEN` seams with file:line
  evidence and disproof hooks.
- DONE: Named only exact-head EM landing synthesis `MISSING`, with two absence searches and a
  premise-collapse hook.
- DONE: Ran the recovered focused suites: review runtime `305 passed, 0 failed`; review post
  `156 passed, 0 failed`.
- DONE: Chose the cheap path: one deterministic read-only adapter over the existing collation
  decision; rejected prose-only judgment and the broader multi-model/daemon program.
- DONE: Recorded `design: required`, closed input/output shapes, confidence semantics, and the
  ordered fail-closed decision table.
- DONE: AC-1 — defined a real CLI round trip whose all-positive, exact negative, and incomplete
  fixtures prove the three verdict/confidence pairs; untouched main supplies the missing-command RED.
- DONE: AC-2 — defined one-field identity/status mutations, malformed and duplicate-key cases, and
  a direct assertion that none can emit `READY`.
- DONE: AC-3 — preserved §6c/post-gate authority, required an empty side-effect ledger under failing
  `gh`/network stubs, and retained the complete review-post regression suite.
- DONE: AC-4 — bounded the changed component/docs paths and made any agy, daemon, live-fetch,
  repair, cross-repo, second-runtime, or merge-authority addition a scope failure.
- DONE: Recorded a 90-minute one-worker appetite, zero tolerance, hard-stop/re-cut boundary,
  no-spike determination, and one-sentence pre-mortem.
- SKIPPED: Browser/full-stack E2E because this is a local CLI decision contract with no UI,
  service, or remote mutation; the real CLI round trip is the end-to-end proof surface.
- SKIPPED: Product implementation, `vf`, `x0f`, daemon/posting changes, merge automation, model
  routing, and cross-repo adoption, per captain scope.

### `--ac-scan`

```text
stage=ideation
ac=AC-1 line=298 unevidenced=false citations=1
ac=AC-2 line=307 unevidenced=false citations=1
ac=AC-3 line=316 unevidenced=false citations=1
ac=AC-4 line=324 unevidenced=false citations=1
```

### Summary

The prior agy-first proposal is no longer the task. Ideation now specifies the smallest S6 core:
one closed, deterministic EM adapter that binds existing CI, test, and typed review evidence to one
exact head and emits an advisory landing verdict. Existing review decisions and human confirmation
remain authoritative for their own surfaces; the new contract adds no posting or merge authority.

## Stage Report: implementation

TL;DR — Implemented and pushed one closed local
`decide-merge-readiness --input-file FILE` adapter at code commit
`56864d5461854509b2bbccec6fe82e58b2f5871a`. The exact current branch is green at focused
merge-readiness **47/0**, default runtime **352/0**, unchanged review-post **156/0**, pinned
ShellCheck v0.9.0, Bash syntax, `git diff --check`, and a real regular-file CLI round trip.
`READY` remains advisory; protected §6c/post files are byte-identical to `origin/main`.

- DONE: Closed advisory adapter — one exact-head CI/test/review input emits fail-closed `READY`, `NOT_READY`, or `UNKNOWN` without post or merge authority.
- DONE: RED/GREEN plus verification — recorded untouched-main RED, focused and default GREEN, review-post regression, direct CLI E2E, pinned ShellCheck, syntax, and diff checks.
- DONE: Bounded approved diff and handoff — only the five approved `kc-pr-flow` runtime/test/documentation paths changed, code commit `56864d5` is pushed, and validator commands are recorded below.

- **DONE: AC-1 — one exact-head input emits one closed decision.**
  `kc-pr-flow/scripts/review-runtime.sh:2397` safe-snapshots one bounded input, applies the closed
  nested `InteractiveCollationDecision/v1` validator, hashes canonical JSON, and executes the
  ordered negative/incomplete/positive table. The CLI entry is
  `kc-pr-flow/scripts/review-runtime.sh:3061`. Positive required evidence emits
  `READY/HIGH/all-required-evidence-positive`; same-head CI/test/review negatives emit
  `NOT_READY/HIGH`; incomplete evidence emits `UNKNOWN/LOW`.
- **DONE: AC-2 — invalid or stale evidence cannot emit `READY`.**
  `kc-pr-flow/scripts/review-runtime.test.sh:116-370` covers recursive duplicate members,
  malformed JSON/hash, unknown keys/status, contradictory `required/NOT_REQUIRED`, observed/CI/test
  head mutations, all seven nested review-identity fields, invalid nested decisions, and the
  otherwise-unreachable inconsistent fallback. Identity mismatch has priority over negative
  evidence. Reason arrays are sorted/unique.
- **DONE: AC-3 — no post or merge authority was added.**
  The test runs the real CLI with failing `gh`, `curl`, `wget`, `nc`, `ssh`, and `git` stubs and
  requires an empty call ledger (`review-runtime.test.sh:367`). The source contains no transport,
  post, authorization, or merge operation. `kc-pr-flow/skills/kc-pr-review/SKILL.md`,
  `scripts/review-post.sh`, and `scripts/review-post.test.sh` match `origin/main` byte-for-byte;
  the unchanged post suite is **156 passed, 0 failed**.
- **DONE: AC-4 — bounded adapter and approved docs only.**
  Changed paths are exactly `kc-pr-flow/scripts/review-runtime.sh`,
  `kc-pr-flow/scripts/review-runtime.test.sh`, `kc-pr-flow/reference/review-runtime.md`,
  `kc-pr-flow/README.md`, and `kc-pr-flow/CLAUDE.md`. Documentation publishes the advisory
  contract and human-only merge boundary at `reference/review-runtime.md:133-155,173`,
  `README.md:68-74`, and `CLAUDE.md:59-66`.

### TDD evidence

- **Initial RED on untouched production:** after tests were written and before production edits,
  `bash kc-pr-flow/scripts/review-runtime.test.sh --case merge-readiness` exited 1. First failure:
  `decide-merge-readiness command exists (expected [0], got [2])`. Log SHA-256:
  `a6a82fe898d3cea24881f24c697caf99758a6cdac9c9066ba18efcc9f5d1a7f0`.
  Result: **1 passed, 44 failed**. All 44 behavior assertions were reachable because the shell
  test continues after each assertion.
- The sole initial RED pass was the empty side-effect ledger. It is explicitly labeled in the test
  as a **regression-only authority invariant**, not evidence that the missing command existed:
  untouched main had no adapter capable of calling a stub.
- **Initial GREEN:** focused contract **45 passed, 0 failed**. A fixture-authoring warning in the
  first attempt showed the duplicate-member case had accidentally become malformed JSON; that
  attempt was not accepted. The fixture was corrected to contain a real duplicate member before
  the recorded GREEN (log SHA-256
  `32b94ba1a80e8c74adbfa5a6f689fad2691dd21c0bd67a5ff6a6f3f90834645a`).
- **Review-cycle RED:** the read-only reviewer found that the first hash assertion began from
  already-canonical JSON. The added reordered/pretty fixture has one labeled arrangement
  precondition and one behavior assertion. Against untouched `origin/main`, that assertion failed:
  `input binding normalizes key order and whitespace (expected [25e92b...], got [])`; exit 1,
  **2 passed / 45 failed**, log SHA-256
  `40e74693230d75dc18fd4188bc6540f226ab029123209bdd7dbb0be5f6b07414`.
- **Review-cycle GREEN:** focused contract **47 passed, 0 failed**, log SHA-256
  `5c9391d0fbdddfd23f96b539b60293a6a66df30129da690c76674da606b458df`.
  No production change was needed because the adapter already hashes `jq -S -c` output.
- **Old-behavior fixture audit:** no existing scenario was repurposed. The implementation adds one
  new isolated test function and calls it from both `--case merge-readiness` and the default CI
  path; all historical default assertions remain in place.

### Verification and validator commands

From the committed code worktree/repository root:

```bash
bash kc-pr-flow/scripts/review-runtime.test.sh --case merge-readiness
bash kc-pr-flow/scripts/review-runtime.test.sh
bash kc-pr-flow/scripts/review-post.test.sh
bash -n kc-pr-flow/scripts/review-runtime.sh kc-pr-flow/scripts/review-runtime.test.sh
docker run --rm --platform linux/amd64 -v "$PWD:/mnt" -w /mnt \
  koalaman/shellcheck:v0.9.0 \
  kc-pr-flow/scripts/review-runtime.sh kc-pr-flow/scripts/review-runtime.test.sh
git diff --check origin/main...HEAD
git diff --name-only origin/main...HEAD
```

- Final focused: **47 passed, 0 failed**.
- Final default runtime: **352 passed, 0 failed**, log SHA-256
  `d4a81c6bdff89c9272f5e45102f7abef9d0c5a8f38df09853be7a8fa9f2a3b8c`.
- Review-post: **156 passed, 0 failed**, log SHA-256
  `e7240ae969d70f9e851f7e89ac48b5d9d743175e34fb95c151f6ae580d609bfc`.
- Direct E2E: a real regular input file passed through
  `bash kc-pr-flow/scripts/review-runtime.sh decide-merge-readiness --input-file FILE`; `jq`
  asserted schema, `READY`, `HIGH`, canonical reason, advisory flag, input hash, and exact head.
  CLI output SHA-256:
  `ad85fce8d4553bf6b02cd3040725145c56016d8b4ac1ccd90be9a5280e3864d2`.
- Static/scope: Bash syntax 0, pinned ShellCheck v0.9.0 0, `git diff --check` 0. The only
  out-of-scope vocabulary in added executable/test lines is the failing side-effect stub list.
- CI timing disclosure: the required workflow has `timeout-minutes: 20`. Under the same local
  machine conditions, the untouched 305-case default suite took **93.24s** and the branch's
  350-case pre-review suite took **102.13s**, an **8.89s** increase. This is a suite delta, not a
  reproduction of the full mutable `ubuntu-latest` job. The final two canonicalization assertions
  add one local CLI invocation and do not change production complexity.

### Review and appetite drift

- A single read-only code-review child was spawned because root `AGENTS.md` prescribes one
  `code-reviewer` subagent for a small single-seam change. FO correctly flagged that this still
  violated the entity's declared **ONE worker** envelope: there were two agents, although only one
  writer and one code worktree. No further workers were spawned.
- Appetite effect: the review consumed one bounded concurrent read-only turn inside the same
  implementation session and introduced no new production surface. It found no critical or
  important issue and one in-scope minor proof gap, closed by the canonical-input test above. The
  worker-count drift is real and not reclassified away; zero tolerance was honored after the FO
  checkpoint by stopping further fan-out and accepting no scope expansion.

### Scope and handoff

- Commit `56864d5461854509b2bbccec6fe82e58b2f5871a` is pushed to
  `origin/spacedock-ensign/agy-first-whole-diff-review-seat`; local HEAD and upstream matched after
  `git pull --rebase origin main` and push.
- No PR was created and no merge was performed, per dispatch.
- SKIPPED: browser/full-stack E2E because the feature has no UI, service, or remote mutation. The
  regular-file CLI round trip is the E2E surface.
- SKIPPED by scope: `vf`, `x0f`, agy/model routing, daemon behavior, live GitHub fetching,
  review-post authority changes, auto-merge, repair loops, and cross-repo adoption.

### `--ac-scan`

```text
stage=implementation
ac=AC-1 line=298 unevidenced=false citations=2
ac=AC-2 line=307 unevidenced=false citations=2
ac=AC-3 line=316 unevidenced=false citations=3
ac=AC-4 line=324 unevidenced=false citations=3
```

### Summary

The assigned branch now contains one validator-runnable, read-only exact-head landing projection:
strict inputs become advisory `READY`, `NOT_READY`, or `UNKNOWN`; stale and malformed inputs fail
closed; and review/post/merge authority remains outside the adapter. The branch and this split-root
report are ready for an independent validation stage.

## Stage Report: validation

TL;DR — **REJECTED** at exact code head
`56864d5461854509b2bbccec6fe82e58b2f5871a` against
`origin/main@9cc0d1faa49e786837342b88062181460f037ac3`. The intended truth table,
canonical hashing, local CLI wiring, regression suites, static gates, authority boundary, coverage,
and adversarial mutations all reproduced. The closed-input claim did not: two inputs that cannot be
valid outputs of the existing typed decision producer still emit `READY/HIGH`. One carries a
`review_key` for a different repository identity; the other calls a required capability `clean`
despite having no successful adapter attempt and an unavailable fallback.

- DONE: Pin and preserve the exact product surface.
  Product `HEAD`, upstream, and requested code head all equal `56864d5461854509b2bbccec6fe82e58b2f5871a`;
  merge-base and `origin/main` equal `9cc0d1faa49e786837342b88062181460f037ac3`.
  The worktree remained clean; validation changed no product file.
- FAILED: AC-1 — one valid exact-head input yields the closed verdict table.
  The expected positive, CI/test/review-negative, incomplete, sorted-reason, advisory-only, and
  canonical-hash cases pass in focused **47/0**. A real regular-file positive CLI round trip also
  passed with input hash `83ac397a81a1925c9c3f8dcadee307aa8b2e63b4e9eb1d41a51d71cf4d1e4530`
  and output hash `a744474323c260558c67bef6244d85309651635db1084aedffe0f1f6aa2b8272`.
  AC-1 still fails because the accepted `review_decision` need not be one the typed producer can
  derive: a required `types` capability with zero attempts, `fallback.status=unavailable`, and
  `terminal_state=clean` emitted `READY/HIGH`.
- FAILED: AC-2 — identity and invalid-decision failures cannot emit `READY`.
  The focused matrix catches one-sided head and nested-identity mutations, malformed/duplicate
  JSON, unknown keys/status, bad hashes, and required/status contradictions. It misses coordinated
  top-level+nested drift and producer-inconsistent capability terminals. Changing both repository
  fields from `acme/widgets` to `other/repo` while retaining the original review key
  `f7da797d...5cc61` emitted `READY/HIGH`; the runtime's own `review-key` command derives
  `0fc1eb5c...3f09b` for `other/repo`, proving the supplied key is stale.
- DONE: AC-3 — no post, network, or merge authority was added.
  The focused empty-call-ledger assertion passed; added out-of-scope command vocabulary is confined
  to the failing test stubs. `kc-pr-review/SKILL.md`, `review-post.sh`, and
  `review-post.test.sh` have identical base/head blobs, and the fresh review-post suite returned
  **156 passed, 0 failed**.
- DONE: AC-4 — the diff remains the approved bounded adapter.
  The exact five paths are the runtime, its test, and the three approved plugin docs: 581 insertions
  and 5 deletions, with every path mapped to AC-1/2/3/4 and no agy routing, daemon, live-fetch,
  repair, cross-repo, manifest, or merge implementation.
- DONE: Independently verify the canonical-hash review-cycle proof.
  Current tests against the untouched main runtime returned **2 passed, 45 failed** and exit 1.
  The reordered/pretty arrangement precondition passed, while
  `input binding normalizes key order and whitespace` failed with expected
  `25e92b...022b`, actual empty. Exact head returned **47/0**.
- DONE: Run the focused/full/static validation set.
  Merge-readiness **47/0**; complete review-runtime **352/0** in 104.09s; review-post **156/0** in
  376.78s; Bash syntax, pinned ShellCheck v0.9.0, `git diff --check`, and changed-path checks all
  exited 0.
- DONE: Measure executable diff coverage.
  Full-suite Bash xtrace observed **54/63 changed shell command trace points = 85.71%**. The
  denominator excludes comments, braces, continuation-only lines, and embedded jq program-body
  lines, counting the shell command that executes each jq program once. The nine uncovered points
  are dependency/canonicalization fallbacks and CLI argument-error branches.
- DONE: Break two core claims in isolated scratch copies.
  Removing observed-head equality returned **46/1** with the exact moved-head assertion failing.
  Removing the CI-negative reason returned **44/3**, failing CI-negative, sorted multi-negative,
  and negative-over-pending assertions. Both mutations exited 1.
- DONE: Attempt the mandatory different-vendor review.
  Codex invoked Antigravity `agy` 1.1.8 in read-only sandbox/plan mode. It returned
  `NOT_READY/HIGH` with three findings, but all three cited
  `docs/ship-flow/scripts/auto-merge-readiness*.mjs`, which do not exist and are outside the exact
  five-path diff. With 3/3 citations invalid, the entire cross-model round is discarded under the
  citation rule; no cross-model finding is accepted or used for this verdict.
- SKIPPED: Browser/full-stack E2E.
  This is an approved local CLI contract with no UI, service, or remote mutation. The direct
  regular-file CLI round trip is the required E2E surface and passed.

### Material findings

1. **HIGH — a stale review key can still produce `READY/HIGH`.**
   `review-runtime.sh:2432-2442` checks only identity field shapes. It never re-derives the documented
   `sha256(repository|pr_number|base_sha|head_sha|config_hash)` binding before
   `:2538-2547` accepts top-level/nested equality and `:2589-2603` emits `READY`. The test at
   `review-runtime.test.sh:314-329` changes only the nested identity, so coordinated drift remains
   untested. This contradicts the exact-identity guarantee in
   `reference/review-runtime.md:23-27,129,140-149`.
2. **HIGH — the nested decision validator accepts producer-impossible capability states.**
   `review-runtime.sh:2443-2487` validates shapes but not the producer's satisfaction/terminal-state
   relationships enforced at `:2174-2188,2248-2265`. A required capability with no attempt,
   unavailable fallback, and `clean` terminal passes; empty gap/blocker arrays then make the
   decision approval-eligible and `READY/HIGH`. The existing invalid-decision case at
   `review-runtime.test.sh:331-344` tests only an unknown key, not semantic invalidity. This
   contradicts the published claim that merge readiness consumes a validated derived
   `InteractiveCollationDecision/v1`.

Required repair: re-derive and compare `review_key`; reuse or extract one strict
`InteractiveCollationDecision/v1` validator (including capability satisfaction and fallback
relationships); add direct coordinated-identity and impossible-terminal mutations; and use at
least one positive fixture produced by the real terminal rehydration path before claiming the
input is a validated existing decision.

### Evidence block

- Lenses: Bash JSON decision adapter + shell tests + published contract docs. Correctness FAIL
  (2 HIGH findings); silent-failure FAIL (2); type-design FAIL (1 shared closed-contract defect);
  security FAIL (1 identity-integrity defect because caller evidence crosses into a merge
  recommendation); resource-lifecycle PASS (0, private snapshot/trap cleanup inspected);
  concurrency and manifest/back-compat did not fire because no shared/async state or installed
  manifest/frontmatter contract changed.
- Diff coverage: **85.71%** — 54/63 changed executable shell command trace points under the complete
  352-case runtime suite.
- Adversarial: PASS — observed-head guard removal returned 46/1; CI-negative removal returned 44/3.
- Cross-model: `agy` 1.1.8 attempted from Codex; 3/3 citations invalid and the entire round was
  discarded. No cross-model finding was relied on.
- E2E: PASS — real regular-file CLI input emitted the closed `READY/HIGH` advisory decision and
  matched its canonical input hash; browser/full-stack is N/A because there is no UI/service/remote
  mutation.

### Feedback Cycles

- Cycle 1: REJECTED — fresh validation; surface 42m implementation wall-clock vs estimate 90m
  (47%); AC unchanged

### Summary

The implementation is narrow, read-only, well exercised, and regression-clean, but it is not yet
the promised exact-head landing contract. Its own CLI proves that stale identity binding and a
semantically invalid typed decision can be labeled `READY/HIGH`. Validation therefore returns
**REJECTED** with concrete file-anchored repairs and no waiver recommendation.

## Stage Report: implementation

TL;DR — Feedback cycle 1 is repaired and pushed at exact code head
`8224cd45d36a73c7a3bc4ff4063cc4ed17dcb6ff`. The readiness adapter now re-derives the
`review_key` binding and rejects producer-impossible capability terminal states. A real
`rehydrate-interactive` result remains `READY/HIGH`. Focused correction is **66/0**, full
interactive rehydration is **51/0**, complete runtime is **371/0**, and review-post is **156/0**.

- DONE: AC-1 — validated typed decisions still produce the closed readiness verdict.
  `review-runtime.sh:2464-2560` now validates the manual fallback shape, bounded retry sequence,
  fallback/identity relationship, provider satisfaction, terminal state, and finding-reference
  relationship already enforced by terminal rehydration. `review-runtime.test.sh:603-645`
  creates a complete capability policy, runs the real `rehydrate-interactive` producer, and proves
  that its output remains `READY/HIGH/all-required-evidence-positive`.
- DONE: AC-2 — both validation findings fail closed.
  `review-runtime.sh:2393-2405,2608-2613` re-derives
  `sha256(repository|pr_number|base_sha|head_sha|config_hash)` with the runtime's existing
  `review_runtime_review_key` function. The coordinated repository mutation at
  `review-runtime.test.sh:330-340` now returns `UNKNOWN/LOW/invalid-input`. The two bidirectional
  impossible-terminal cases at `review-runtime.test.sh:342-385` now also return
  `UNKNOWN/LOW/invalid-input`.
- DONE: AC-3 — authority remains unchanged.
  The focused suite's failing `gh`, `curl`, `wget`, `nc`, `ssh`, and `git` stubs retained an empty
  call ledger. No network, fetch, post, authorization, merge, or daemon path was added.
  `review-post.test.sh` remains unchanged and is green at **156/0**.
- DONE: AC-4 — correction scope is exactly the two authorized runtime/test paths.
  Feedback-cycle commit `8224cd4` changes only
  `kc-pr-flow/scripts/review-runtime.sh` and
  `kc-pr-flow/scripts/review-runtime.test.sh`. The whole feature diff remains the approved five
  runtime/test/documentation paths; no published statement required correction.

### Correction TDD evidence

- **RED before production repair:** with the three correction assertions added against code head
  `56864d5`, `bash kc-pr-flow/scripts/review-runtime.test.sh --case merge-readiness` exited 1 at
  **63 passed / 3 failed**. The coordinated stale key and unsatisfied-clean cases each actually
  emitted `READY|HIGH|all-required-evidence-positive`; the satisfied-incomplete case emitted
  `UNKNOWN|LOW|review-incomplete` instead of failing input validation. Failure-output SHA-256:
  `5e0eb38a82c232a84e564ebe3cf8b1a89e1b29b8eca273706d787b3557d0381d`.
- **GREEN:** after the minimum runtime repair, the identical focused command returned
  **66 passed / 0 failed**. All three new behavior assertions were reachable and red in the
  recorded pre-fix run. The real-rehydration positive assertions were green preconditions:
  they prove compatibility with the existing producer and are not claimed as RED evidence.
- **Old-behavior fixture audit:** no historical case was repurposed. The three rejected inputs are
  new isolated mutations. The real-producer fixture derives a separate complete policy from the
  existing interactive fixture and leaves the historical incomplete/blocker scenario unchanged.

### Correction verification

From the code worktree/repository root:

```bash
bash kc-pr-flow/scripts/review-runtime.test.sh --case merge-readiness
bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision
bash kc-pr-flow/scripts/review-runtime.test.sh
bash kc-pr-flow/scripts/review-post.test.sh
bash -n kc-pr-flow/scripts/review-runtime.sh kc-pr-flow/scripts/review-runtime.test.sh
shellcheck kc-pr-flow/scripts/review-runtime.sh kc-pr-flow/scripts/review-runtime.test.sh
docker run --rm --platform linux/amd64 -v "$PWD:/mnt" -w /mnt \
  koalaman/shellcheck:v0.9.0 \
  kc-pr-flow/scripts/review-runtime.sh kc-pr-flow/scripts/review-runtime.test.sh
git diff --check
```

- Focused merge readiness: **66 passed, 0 failed**.
- Full interactive decision: **51 passed, 0 failed**.
- Complete runtime: **371 passed, 0 failed**.
- Unchanged review-post ripple: **156 passed, 0 failed**.
- Bash syntax, `git diff --check`, local ShellCheck 0.11.0, and CI-pinned ShellCheck 0.9.0:
  exit 0.
- Direct E2E: a real regular input file passed through
  `decide-merge-readiness --input-file FILE`; `jq` asserted schema, `READY`, `HIGH`, canonical
  reason, advisory flag, exact head, and canonical input hash. Output SHA-256:
  `63e7a101d38ff01debf9169bda076cf89472e8f1418e9e119f27fa80278e2036`.
- CI margin: the correction adds three local adapter mutations and one terminal-rehydration
  positive path. The complete runtime suite finished locally without timeout at **371/0**; live
  exact-head CI remains the merge authority.

### Scope and handoff

- Code commit `8224cd45d36a73c7a3bc4ff4063cc4ed17dcb6ff` is pushed to
  `origin/spacedock-ensign/agy-first-whole-diff-review-seat`; local HEAD equals upstream and the
  code worktree is clean.
- `origin/main` advanced during the final fetch to
  `dab82f697120f26de9e653d0b6561d66d67d73ba`; the feature merge-base remains
  `9cc0d1faa49e786837342b88062181460f037ac3`. The intervening `kc-pr-flow` changes are release
  metadata only (`plugin.json` files and `CHANGELOG.md`), not either repaired runtime path.
  Fresh validation should nevertheless pin both the new code head and current base.
- No PR was created, no merge was performed, and no additional worker or reviewer was spawned.
- SKIPPED by scope: browser/full-stack E2E, live GitHub/CI fetching, vf/x0f/agy/model routing,
  daemon behavior, posting, merging, repair loops, and cross-repo adoption.

### Feedback Cycles

- Cycle 1: REPAIRED — same implementation worker/worktree; two HIGH validation findings closed;
  AC and design unchanged; no scope or worker-count expansion

### `--ac-scan`

```text
stage=implementation
ac=AC-1 unevidenced=false citations=2
ac=AC-2 unevidenced=false citations=3
ac=AC-3 unevidenced=false citations=2
ac=AC-4 unevidenced=false citations=2
```

### Summary

The exact-head advisory adapter now accepts only identities bound to their derived review key and
only capability terminals consistent with the existing typed producer's attempt, fallback, and
satisfaction rules. Both validator-reproduced false recommendations are closed, a real producer
output remains positive, the code head is pushed, and the correction is ready for fresh validation.
