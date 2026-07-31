---
title: Synthesize exact-head EM merge readiness before human landing
status: validation
source: captain direction 2026-07-30 after reconcile-list-element-shape closeout
started: 2026-07-30T15:01:36Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-agy-first-whole-diff-review-seat
issue:
pr: pr-merge:118:artifact-v1:4658c5609cd04c9943098d3f31cd5a9da200c70fe93707c401a548338e7216b4
ledger_pr:
pr_artifact_v1: eyJhdWRpdF9saW5rIjoiWzRhXSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvYTJlYjZiNDcwOTM1YTBjYTJjY2M0NTBhMWIwNDVhZjU2MGE2MDZjYi9hZ3ktZmlyc3Qtd2hvbGUtZGlmZi1yZXZpZXctc2VhdC5tZCkiLCJiYXNlIjoibWFpbiIsImJhc2Vfb2lkIjoiOWVkZGY5OTI4ZDZkN2FlMzkxZDNiMTFhZGFiMmU5MjBiNWVjMGIyYyIsImJvZHkiOiJHaXZlIEVNIG9uZSB0cnVzdHdvcnRoeSBleGFjdC1oZWFkIGxhbmRpbmcgc2lnbmFsIHdpdGhvdXQgbGV0dGluZyBjYWxsZXItYXV0aG9yZWQgcmV2aWV3IGV2aWRlbmNlIG1hc3F1ZXJhZGUgYXMgcHJvZHVjZXIgb3V0cHV0LlxuXG4jIyBXaGF0IGNoYW5nZWRcbi0gQ29tcG9zZSBtZXJnZSByZWFkaW5lc3MgZGlyZWN0bHkgd2l0aCB0aGUgZXhpc3RpbmcgcmV2aWV3IHByb2R1Y2VyLlxuLSBBY2NlcHQgb25seSBjbG9zZWQgZXhhY3QtaGVhZCBDSSBhbmQgdGVzdCBvYnNlcnZhdGlvbnMuXG4tIEJpbmQgY2Fub25pY2FsIHByb2R1Y2VyIG91dHB1dCBpbnRvIGVhY2ggYWR2aXNvcnkgZGVjaXNpb24uXG4tIEZhaWwgaW5jb25zaXN0ZW50IHByb2R1Y2VyIGV2aWRlbmNlIGNsb3NlZCBhcyB1bmtub3duLlxuLSBEb2N1bWVudCB0aGUgcHJvZHVjZXItb25seSBjb250cmFjdCBhbmQgaHVtYW4gbWVyZ2UgYm91bmRhcnkuXG5cbiMjIEV2aWRlbmNlXG4tIFJ1bnRpbWUgY29udHJhY3Q6IDM3Mi8zNzIgcGFzc2VkOyBleGVjdXRhYmxlIGRpZmYgY292ZXJhZ2UgcmVhY2hlZCA4OC4xNyUuXG4tIFJldmlldy1wb3N0OiAxNTYvMTU2IHBhc3NlZDsgcmVhbCByZWd1bGFyLWZpbGUgQ0xJIEUyRSB2ZXJpZmllZC5cblxuLS0tXG5bNGFdKC9pYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMvYmxvYi9hMmViNmI0NzA5MzVhMGNhMmNjYzQ1MGExYjA0NWFmNTYwYTYwNmNiL2FneS1maXJzdC13aG9sZS1kaWZmLXJldmlldy1zZWF0Lm1kKVxuIiwiYm9keV9zaGEyNTYiOiIxZTI2MzlkMmJkODA3MjM0NTE2NGRkODg0MjYwZjkwZGZlN2NkYzcyMTNkZTJlN2U4ZjkyYjFiZGRhZWU1ODE4IiwiZGlmZl9zaGEyNTYiOiI3ZDM2NmNjYWIyNzg1NTY3OTEzNWUzODZkYjQxM2U1NDU0ZWU3ZWU2Y2NjODQxZGNhZjhhNzlkZjQ5NmY3YTU4IiwiaGVhZCI6InNwYWNlZG9jay1lbnNpZ24vYWd5LWZpcnN0LXdob2xlLWRpZmYtcmV2aWV3LXNlYXQiLCJoZWFkX29pZCI6ImJlNDUwZTQyMjBiNzg5MzQwNmMzOGZmMDFiZjg0MjlkMDBiN2YzNjEiLCJsaXZlX3BhdGgiOiJhZ3ktZmlyc3Qtd2hvbGUtZGlmZi1yZXZpZXctc2VhdC5tZCIsInJlcG8iOiJpYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMiLCJ0aXRsZSI6IlN5bnRoZXNpemUgZXhhY3QtaGVhZCBFTSBtZXJnZSByZWFkaW5lc3MgYmVmb3JlIGh1bWFuIGxhbmRpbmcifQ
ledger_artifact_v1:
mod-block: pr-merge:product-pr:v1:4658c5609cd04c9943098d3f31cd5a9da200c70fe93707c401a548338e7216b4
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

## Initial approaches considered (superseded after validation cycle 2)

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

## Initial design determination (superseded after validation cycle 2)

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

## Initial acceptance criteria (superseded after validation cycle 2)

**Superseded criterion 1 — One exact-head input yields a closed readiness verdict.**
Verified by: `bash kc-pr-flow/scripts/review-runtime.test.sh` plus a direct `bash kc-pr-flow/scripts/review-runtime.sh decide-merge-readiness --input-file <fixture>` CLI round trip extending the existing decision fixture surface beside `kc-pr-flow/skills/kc-pr-review/SKILL.md:1270-1388` and asserting the complete positive, negative, and incomplete outputs. Falsified by: changing a positive fixture's CI status to `FAIL` while retaining expected `READY`, or deleting the production negative-evidence branch, makes the focused suite fail.

For one valid exact-head input, the adapter emits exactly one closed decision: all required positive
evidence yields `READY/HIGH`; an exact-head CI failure, test failure, or confirmed review blocker
yields `NOT_READY/HIGH`; and incomplete required evidence yields `UNKNOWN/LOW`. The baseline on
`origin/main@9cc0d1f` has no such command or schema, so the first contract invocation is the required
RED.

**Superseded criterion 2 — Identity failures cannot produce `READY`.**
Verified by: the negative fixture matrix extending `kc-pr-flow/scripts/review-runtime.test.sh:261`, including one-field-at-a-time head mutations and duplicate-key input, plus a direct CLI assertion that no case emits `READY`.
Falsified by: removing any one same-head equality check makes its targeted mutation fixture emit `READY` and fail the suite.

A moved observed head, mismatched CI/test head, nested review identity drift, malformed hash,
duplicate/unknown key, or invalid required/status pair cannot produce `READY`; each safely readable
case yields `UNKNOWN/LOW` with the matching reason, while unreadable input exits nonzero and the
documented caller behavior is `UNKNOWN`.

**Superseded criterion 3 — The decision adds no post or merge authority.**
Verified by: `bash kc-pr-flow/scripts/review-post.test.sh`, a merge-readiness CLI test with failing `gh`/network stubs and an empty call ledger, and a path-scoped diff assertion protecting `kc-pr-flow/skills/kc-pr-review/SKILL.md:1723` and the gate negatives at `kc-pr-flow/scripts/review-post.test.sh:227`.
Falsified by: adding any `gh` call populates the ledger and fails the focused test; changing §6c changes the protected recipe assertion.

The new decision is read-only and advisory. It neither creates a posting receipt nor calls a model,
network client, `gh pr review`, or `gh pr merge`; the existing §6c human confirmation and
review-post gates remain unchanged and green.

**Superseded criterion 4 — The implementation remains one bounded adapter.**
Verified by: `git diff --name-only origin/main...HEAD`, `git diff --check`, the focused runtime/post suites, and consistency searches anchored at `kc-pr-flow/CLAUDE.md:45`, `kc-pr-flow/README.md:50`, and `kc-pr-flow/reference/review-runtime.md:123` plus the changed executable/test paths.
Falsified by: any changed path or command implementing a listed out-of-scope system, or any published claim that `READY` authorizes merge, fails scope review.

Implementation adds only the deterministic adapter to the existing review-runtime component, its
direct tests, and the approved `kc-pr-flow` documentation updates. It does not add agy routing,
daemon behavior, live evidence fetching, repair loops, cross-repo adoption, or a second runtime.

## Initial test plan (superseded after validation cycle 2)

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

## Initial proposed documentation diff (superseded after validation cycle 2)

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

## Initial spike determination (superseded after validation cycle 2)

No spike needed. The risky mechanism is closed JSON validation plus deterministic jq projection,
and the existing component already proves it:

- `review-runtime.sh:2316-2362` emits the exact-head interactive collation decision;
- `review-runtime.test.sh` is green at `305 passed, 0 failed`;
- `review-post.test.sh` is green at `156 passed, 0 failed`.

Implementation still rechecks the load-bearing `MISSING` claim on fresh `origin/main` before RED.

## Initial pre-mortem (superseded after validation cycle 2)

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

## Stage Report: validation

TL;DR — **REJECTED** on re-review at exact code head
`8224cd45d36a73c7a3bc4ff4063cc4ed17dcb6ff`. The two cycle-1 counterexamples are
closed and a real `rehydrate-interactive` decision remains `READY/HIGH`. The broader producer
compatibility claim is still false: two fresh inconsistent fixtures that the existing producer
rejects — duplicate retry lane identity and an impossible manual-fallback timestamp — both emit
`READY/HIGH/all-required-evidence-positive`. The committed positive unit fixture also has zero
capabilities even though the producer requires at least one obligation.

- DONE: Pin the exact product and base surfaces.
  Product `HEAD` and upstream both equal
  `8224cd45d36a73c7a3bc4ff4063cc4ed17dcb6ff`; current `origin/main` is
  `dab82f697120f26de9e653d0b6561d66d67d73ba`; the merge-base is
  `9cc0d1faa49e786837342b88062181460f037ac3`. Current-main changes overlap none
  of the five feature paths. The product worktree remained clean.
- FAILED: AC-1 — the closed verdict table still accepts invalid positive evidence.
  The expected positive/negative/incomplete truth table passes **66/0**, and a real producer
  decision passes both the focused and direct regular-file CLI paths. Fresh inconsistent fixtures
  with duplicate retry lane identity and an impossible timestamp each nevertheless emitted
  `READY/HIGH`, contradicting the documented rule that invalid evidence emits `UNKNOWN/LOW`.
- FAILED: AC-2 — identity binding is repaired, but invalid typed decisions can still emit `READY`.
  Coordinated repository drift now returns `UNKNOWN/LOW/invalid-input`; the runtime re-derives
  `review_key` at `review-runtime.sh:2393-2405,2608-2613`, and the independent
  `review-key` command derived `0fc1eb5c...3f09b` for `other/repo`. The prior
  unsatisfied-clean and satisfied-incomplete mutations also fail closed. AC-2 remains failed
  because `review-runtime.sh:2509-2514` omits the producer's unique-lane rule at `:2229`,
  while `:2480-2481` checks timestamp shape but omits the semantic RFC3339 validation at
  `:2284-2286`.
- DONE: AC-3 — authority remains read-only and local.
  Focused command stubs retained an empty call ledger. The base/head blobs for
  `kc-pr-flow/skills/kc-pr-review/SKILL.md`, `review-post.sh`, and `review-post.test.sh`
  match; the fresh review-post suite returned **156/0**. No fetch, network, post,
  authorization, or merge path was added.
- DONE: AC-4 — scope remains the approved adapter.
  The whole feature diff is exactly five paths, **760 insertions / 5 deletions**. The
  correction is exactly the runtime and its test. Current `origin/main` has zero overlap with
  those five paths, and no daemon, routing, repair-loop, manifest, cross-repo, or merge
  implementation entered the diff.
- DONE: Prove both cycle-1 repairs independently.
  The focused suite returned **66/0**. Replacing the review-key equality guard with an
  unconditional success returned **65/1**, failing only coordinated identity drift. Treating a
  claimed clean terminal as satisfied returned **65/1**, failing only the unsatisfied-required
  capability case. Both mutations were isolated scratch copies.
- DONE: Prove real producer compatibility.
  `review-runtime.test.sh:606-644` invokes the actual `rehydrate-interactive` producer and feeds
  its result through `decide-merge-readiness`; focused merge readiness returned **66/0** and
  interactive decision returned **51/0**. A separately preserved **8,893-byte regular-file**
  producer fixture emitted `READY/HIGH/all-required-evidence-positive`, and its canonical input
  hash matched
  `5999f4450557467a6272854587160c5628b49024d4a4116eee787a73d60abd1b`.
- FAILED: Attack producer consistency beyond the supplied regressions.
  An isolated test-only extension of the focused matrix returned **66 passed / 2 failed**:
  duplicate attempts using `types-1` for both ordinals and a manual clean fallback dated
  `2026-99-99T99:99:99Z` each actually returned `READY/HIGH/all-required-evidence-positive`
  instead of `UNKNOWN/LOW/invalid-input`. In addition, the committed positive fixture at
  `review-runtime.test.sh:127-145` has `capabilities:[]` and is expected to be `READY` at
  `:182-188`, while `rehydrate-interactive` requires a non-empty obligation array at
  `review-runtime.sh:2202`.
- DONE: Reproduce the canonical-hash RED proof against untouched main.
  The current focused test against the base runtime exited 1 at **17 passed / 49 failed**.
  The reordered/pretty canonical-value precondition passed; the input-binding assertion failed
  with expected `25e92b...022b` and actual empty. Exact head returned **66/0**.
- DONE: Run complete and static validation.
  Merge readiness **66/0**; interactive decision **51/0**; complete runtime **371/0**;
  review-post **156/0**. Bash syntax, `git diff --check`, exact changed-path checks, and
  CI-pinned ShellCheck v0.9.0 all exited 0.
- DONE: Measure executable diff coverage.
  Full-suite Bash xtrace observed **63/72 changed shell trace points = 87.50%**. The
  denominator excludes comments, braces, continuation-only lines, and embedded jq program
  bodies, counting each shell command that executes a jq program once. The nine uncovered
  points are the unexpected duplicate-check return, malformed-canonical-input fallback, and
  CLI argument-error branches at `review-runtime.sh:2432,2435-2436,3144-3145,3151-3152,
  3157-3158`.
- DONE: Run the mandatory different-vendor read-only review.
  Antigravity `agy` 1.1.8 reviewed the exact
  `9cc0d1f...8224cd4` five-path diff in sandbox/plan mode and returned `No findings.`
  There were no citations to verify. The local adversarial counterexamples remain authoritative
  for this verdict.
- FAILED: Reconcile documentation absolutes.
  `reference/review-runtime.md:129,135-149`, `README.md:68-74`, and
  `CLAUDE.md:59-64` promise a validated producer decision and say invalid evidence cannot emit
  `READY`; the two direct inconsistent-fixture results disprove those absolutes at this head.
- SKIPPED: Browser/full-stack E2E.
  This change has no UI, service, or remote mutation. The real regular-file CLI round trip is the
  applicable E2E surface and passed.

### Material finding

1. **HIGH — the nested decision validator still accepts producer-impossible capability
   records and can label them `READY/HIGH`.**
   At `review-runtime.sh:2509-2514`, retry ordinals and the first transient result are checked,
   but lane-result references need not be unique as required by the producer at `:2229`.
   At `:2480-2481`, `recorded_at` needs only match a digit-shaped regex, whereas the producer
   invokes semantic RFC3339 validation at `:2284-2286`. The same validator permits an empty
   `capabilities` array at `:2497-2499`, although producer policy requires at least one
   obligation at `:2202`. All three gaps can support an otherwise positive decision; the first
   two were exercised through the real CLI and both returned
   `READY/HIGH/all-required-evidence-positive`.

Required repair: share or faithfully mirror one complete post-projection validator from
`rehydrate-interactive`; at minimum require a non-empty capability set, unique retry lane
references, and semantic manual-result timestamps, then add direct fail-closed mutations for each.
Because manual fallback evidence is carried in the decision, its closed pointer shape and identity
binding should be checked by that shared validator as well.

### Evidence block

- Lenses: correctness FAIL (1 HIGH finding with three producer-rule gaps); silent-failure FAIL
  (inconsistent fixtures become positive without diagnostics); type-design FAIL (the consumer's
  accepted language is wider than its named producer type); authority/scope PASS. Security and
  resource-lifecycle triggers did not fire for this local contract-consistency re-review.
- Diff coverage: **87.50%** — 63/72 changed shell trace points under the complete 371-case
  runtime suite.
- Adversarial: targeted guard removal **65/1**; terminal-satisfaction widening **65/1**;
  fresh inconsistent-fixture matrix **66/2**, with both failures caused by unexpected
  `READY/HIGH`.
- Cross-model: `agy` 1.1.8 returned `No findings.` for the exact five-path diff; no citations
  existed, and no cross-model finding was relied on.
- E2E: PASS for the positive path — a real producer artifact in a regular file emitted
  `READY/HIGH` and matched its canonical hash. FAIL for fail-closed compatibility — two
  producer-inconsistent regular inputs also emitted `READY/HIGH`.

### Feedback Cycles

- Cycle 2: REJECTED / DESIGN RESET APPROVED — exact repaired-head re-review; surface 61m
  implementation wall-clock vs estimate 90m (68%); AC narrowed: replace duplicated consumer
  semantic validation with one canonical post-projection authority before further implementation.

### `--ac-scan`

```text
stage=validation
ac=AC-1 unevidenced=false citations=3
ac=AC-2 unevidenced=false citations=4
ac=AC-3 unevidenced=false citations=3
ac=AC-4 unevidenced=false citations=2
```

### Summary

The repaired head correctly binds `review_key`, rejects the two supplied terminal-state
contradictions, preserves a real producer's positive result, remains read-only, and is fully
regression-green. It still does not validate the whole decision language emitted by the existing
producer. Because directly inconsistent capability records can receive `READY/HIGH`, the
re-review verdict is **REJECTED** with no waiver recommendation.

## Active ideation reset after validation cycle 2

This section supersedes the initial approach, contract, acceptance criteria, test plan,
documentation proposal, spike determination, and pre-mortem above. The implementation and
validation reports remain as evidence; rejected code head
`8224cd45d36a73c7a3bc4ff4063cc4ed17dcb6ff` is not a passing baseline.

The captain approved the reset after two consecutive validation rejections. The captain-authored
problem, bounded `kc-pr-flow` scope, advisory-only authority, and exclusions remain unchanged. The
reset changes only how the readiness reducer obtains its typed review decision.

### Why the architecture must change

The rejected adapter accepts a caller-supplied `InteractiveCollationDecision/v1` and then tries to
recognize the producer's language with a second field-by-field jq grammar. Cycle 1 found stale
`review_key` and terminal-satisfaction gaps. The repair added those predicates. Cycle 2 then found
three more producer-only rules:

- duplicate retry lane references are rejected by `rehydrate-interactive` but accepted by the
  readiness validator;
- a digit-shaped but impossible manual-fallback timestamp is rejected by the producer's semantic
  RFC3339 check but accepted by the readiness validator; and
- the readiness validator accepts zero capabilities although the producer requires at least one
  obligation.

Two of those inconsistent decisions emitted
`READY/HIGH/all-required-evidence-positive` through the real rejected CLI. The recurring failure is
therefore not “three missing predicates.” It is a producer/consumer language split: every copied
validator can lag the producer again.

### Live merge-target reverse-recovery refresh

Refresh pin: `origin/main@6f51c552552cee56b09fc2b60983adbcedb7243d`, fetched on
2026-07-31 before this reset.

The `kc-pr-flow` delta from the original audit pin
`9cc0d1faa49e786837342b88062181460f037ac3` to the live merge target is release metadata only:

```text
M kc-pr-flow/.claude-plugin/plugin.json
M kc-pr-flow/.codex-plugin/plugin.json
M kc-pr-flow/CHANGELOG.md
```

Neither `review-runtime.sh` nor its tests changed on the merge target. Re-running the original
domain-vocabulary and structural searches against live `origin/main` still finds no
`READY | NOT_READY | UNKNOWN` executable verdict and no merge-readiness command. It finds only the
prose phrase in `reference/learned-patterns.md:531`.

| Layer / seam | Classification at live merge target | Evidence and reset consequence |
|---|---|---|
| Terminal receipt replay, policy validation, and exact identity | `WORKING_UNIT_UNPROVEN` | `origin/main:kc-pr-flow/scripts/review-runtime.sh:2068-2314` rejects malformed receipt/policy, moved identity, impossible retry/fallback state, semantically invalid manual timestamps, and unbound or unverifiable evidence. Keep it as the only review-language authority. |
| `InteractiveCollationDecision/v1` projection | `WORKING_UNIT_UNPROVEN` | `origin/main:kc-pr-flow/scripts/review-runtime.sh:2316-2362` constructs the decision only after the producer validations pass. The active design consumes this in-process return value and never reparses a caller-authored decision. |
| Decision-only validators | `EXISTS_BROKEN` | The existing skill recipe at `kc-pr-flow/skills/kc-pr-review/SKILL.md:1302-1388` and rejected readiness code at `review-runtime.sh:2439-2603` describe weaker languages than the producer. The readiness reset removes its copy; changing the interactive recipe is not required for this bounded seam because its decision already comes directly from the producer call. |
| Exact-head merge-readiness reducer on `origin/main` | `MISSING` | Live-main searches find no command or schema. Keep the narrow reducer, but feed it only the producer's successful in-process output. |
| Rejected readiness reducer at `8224cd4` | `EXISTS_BROKEN` | The verdict table itself is deterministic, but its review input can be producer-impossible and still reach `READY`. Delete the duplicated review-decision grammar and change the input boundary. |
| Review-post and human merge authority | `WORKING_UNIT_UNPROVEN` | The existing §6c and `review-post.sh` boundaries remain outside this implementation. No reset approach may add posting, authorization, or merge behavior. |

The load-bearing classification is one broken seam above a recovered producer, not a missing
producer. Implementation must re-fetch `origin/main` and stop if either runtime path changed since
this pin.

### Approaches compared

#### Recommended — compose readiness directly with the existing producer

Keep `review_runtime_rehydrate_interactive` as the sole canonical authority for the review
decision. `decide-merge-readiness` accepts caller-supplied CI, test, and observed-head observations
plus the same terminal receipt, policy, repository worktree, and exact identity arguments already
accepted by `rehydrate-interactive`. Inside one runtime invocation it:

1. safe-snapshots and validates the closed observation input;
2. calls `review_runtime_rehydrate_interactive` exactly once with the supplied producer sources;
3. maps any producer nonzero/invalid result to `UNKNOWN/LOW/invalid-review-evidence`;
4. accepts review evidence only from the successful in-process decision returned by that call;
5. binds that decision and the observations into the canonical input hash; and
6. applies the existing exact-head negative/incomplete/positive verdict table.

The external input has no `review_decision` member and no decision-file option. Unknown keys fail
closed. The accepted review language is therefore the successful output language of the producer
itself, not a consumer approximation of it.

This is the cheapest sound reset because both functions already live in
`kc-pr-flow/scripts/review-runtime.sh`; implementation removes the large copied decision grammar
and threads the producer's existing arguments into one command. It needs no new runtime, schema
authority, state store, secret, model, network access, or daemon.

#### Not taken — shared canonical post-projection validator

Extract one decision-only validator, run every producer result through it before emission, and call
the same function from readiness. This is smaller in apparent call-surface change, and it would
close the three cycle-2 fields if the validator required a non-empty capability set, unique retry
lane references, and semantic timestamps.

It is not the cheapest complete solution. Some producer guarantees bind a terminal to source-only
facts that the projected decision does not retain: a lane reference must name the matching replay
lane/result, finding references must come from replay findings, and evidence pointers must resolve
against the supplied repository. A decision-only validator either accepts a broader language than
the producer or enlarges the decision with enough source material to replay those checks. Moving
all producer rules into a post-projection schema would also require reworking the typed interactive
recipe's separate validator. That is a wider refactor than direct composition.

#### Not taken — producer-generated validated receipt

Wrap the decision in a new receipt containing a schema version, canonical decision hash, and
producer/source hashes, then require readiness to consume the receipt. A self-asserted receipt is
not provenance: any caller that can forge the decision can also recompute its unkeyed hashes and
set a `validated` field. Making the receipt authoritative requires one of:

- a secret/signature authority;
- a protected durable state lookup; or
- replaying the producer sources and byte-comparing the decision.

The first two add new authority/runtime state and are out of scope. The third collapses to the
recommended direct-composition design plus an unnecessary envelope. The receipt therefore adds
schema and lifecycle cost without closing the gap more cheaply.

**Fastest path:** add the three cycle-2 predicates to the copied jq validator. Rejected: it is the
third field-by-field patch and leaves the language split intact.

**Smallest cut that satisfies the active ACs:** remove caller-supplied review decisions and compose
the reducer with the existing producer in the same runtime invocation.

**Taking the cheap path:** direct in-process composition. No captain scope cut is being made. The
more thorough signed/durable receipt program is unnecessary and explicitly excluded.

### Design determination

`design: required` because this reset changes the readiness command and input contract.

#### External observation contract

The caller supplies one closed `kc-pr-flow.merge-readiness-observations/v1` object:

```json
{
  "schema": "kc-pr-flow.merge-readiness-observations/v1",
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
  }
}
```

Status rules remain `PASS | FAIL | PENDING | UNKNOWN | UNAVAILABLE | NOT_REQUIRED`;
`NOT_REQUIRED` is valid only when `required:false`. Duplicate members, unknown keys, malformed
hashes, and contradictory status/required pairs are invalid.

The command reuses the producer's existing source arguments:

```text
decide-merge-readiness
  --observations-file FILE
  --event-file FILE
  --policy-file FILE
  --repo-worktree DIR
  --repo OWNER/REPO
  --pr N
  --base SHA
  --head SHA
  --config-hash HASH
  --review-key HASH
  --run-id ID
```

There is deliberately no `--decision-file` and no `review_decision` JSON member. The exact
identity flags are passed unchanged to `review_runtime_rehydrate_interactive`. A successful
producer result must repeat that identity exactly; a nonzero producer result or identity mismatch
maps to `UNKNOWN/LOW` and cannot reach the verdict table.

#### Internal binding and output

After a successful producer call, the runtime constructs an internal canonical object:

```json
{
  "schema": "kc-pr-flow.merge-readiness-binding/v1",
  "observations": "<canonical observation object>",
  "review_decision": "<successful in-process producer output>"
}
```

`input_sha256` binds the canonical bytes of that internal object. The public
`MergeReadinessDecision/v1` output shape and verdict/confidence vocabulary remain unchanged:
`READY/HIGH`, `NOT_READY/HIGH`, or `UNKNOWN/LOW`, sorted unique reasons, and
`advisory_only:true`.

The ordered verdict table remains:

1. malformed observations or producer rejection → `UNKNOWN/LOW`;
2. observed/CI/test head mismatch with the producer identity → `UNKNOWN/LOW`;
3. same-head CI/test failure or validated review blocker → `NOT_READY/HIGH`;
4. required evidence incomplete or validated review incomplete → `UNKNOWN/LOW`;
5. all required observations positive and validated review approval-eligible → `READY/HIGH`;
6. unreachable remainder → `UNKNOWN/LOW/inconsistent-input`.

## Acceptance criteria

**AC-1 — Only producer output can drive review readiness.**

The readiness command accepts no caller-supplied review decision. It invokes the existing
`review_runtime_rehydrate_interactive` producer exactly once and uses only that successful
in-process result. Duplicate retry lane identity, impossible manual timestamp, empty obligations,
malformed/unbound manual evidence pointers, and the two cycle-1 contradictions cannot produce
`READY`.

Verified by: focused additions to `bash kc-pr-flow/scripts/review-runtime.test.sh --case
merge-readiness` that run the real producer path, mutate the producer receipt/policy for every
cycle-1 and cycle-2 counterexample, and require `UNKNOWN/LOW/invalid-review-evidence`; a contract
negative adds `review_decision` to the observation JSON and requires
`UNKNOWN/LOW/invalid-input`. Falsified by: replacing the producer call with a caller-provided
decision makes the exact mutation matrix red. Baseline: at rejected head `8224cd4`, duplicate lane
identity and impossible timestamp both emitted `READY/HIGH`; the active proof requires zero such
false positives.

**AC-2 — Exact-head evidence yields the closed verdict table.**

One real producer-derived decision plus same-head observations yields `READY/HIGH` only when every
required signal is positive. A same-head CI failure, test failure, or validated review blocker
yields `NOT_READY/HIGH`; pending/unavailable required evidence or a validated review gap yields
`UNKNOWN/LOW`; any observed/CI/test head mismatch yields `UNKNOWN/LOW`.

Verified by: the focused truth-table matrix plus a direct regular-file CLI round trip that invokes
the complete new command, parses stdout with `jq`, and checks the canonical internal binding hash.
Falsified by: deleting one negative, incomplete, or identity branch makes its isolated fixture
return the wrong verdict. End-value measurement: the cycle-2 producer-inconsistent false-positive
count moves from 2 to 0 while a real producer positive remains `READY/HIGH`.

**AC-3 — The decision remains advisory and side-effect free.**

The reset performs no model, network, GitHub, posting, authorization, daemon, repair, or merge
operation. `READY` remains advisory; §6c and human merge authority are unchanged.

Verified by: `bash kc-pr-flow/scripts/review-post.test.sh` plus the real focused CLI with failing
`gh`, `curl`, `wget`, `nc`, `ssh`, and `git` stubs and an empty call ledger; compare
`kc-pr-flow/skills/kc-pr-review/SKILL.md`, `review-post.sh`, and `review-post.test.sh` to
`origin/main`, anchored at the §6c authority in
`kc-pr-flow/skills/kc-pr-review/SKILL.md:1723` and the posting-gate negatives in
`kc-pr-flow/scripts/review-post.test.sh:227`. Falsified by: any call-ledger entry or protected-path
diff fails the criterion.

**AC-4 — One runtime cut replaces duplicated validation.**

The implementation removes the readiness adapter's field-by-field
`InteractiveCollationDecision/v1` grammar and adds no second decision validator or validation
receipt. The whole feature remains one existing-runtime behavior with focused tests and plugin
docs.

Verified by: `bash kc-pr-flow/scripts/review-runtime.test.sh --case merge-readiness` plus
`git diff --name-only origin/main...HEAD`, limited to `kc-pr-flow/scripts/review-runtime.sh`,
`kc-pr-flow/scripts/review-runtime.test.sh`,
`kc-pr-flow/reference/review-runtime.md`, `kc-pr-flow/README.md`, and
`kc-pr-flow/CLAUDE.md`; searches show no readiness-side `def interactive_decision`, decision-file
option, signature/state authority, or new executable, with the replacement boundary anchored at
`kc-pr-flow/scripts/review-runtime.sh:2365` and its focused test entry at
`kc-pr-flow/scripts/review-runtime.test.sh:118`. Run the focused/default runtime suites,
review-post suite, pinned ShellCheck v0.9.0, Bash syntax, and `git diff --check`. Falsified by: a
caller-supplied decision reaches the reducer, a second validator remains, or an excluded path or
authority enters the diff.

### RED proof and test plan

1. **Pin the rejected RED baseline.**
   - Fetch `origin/main`; pin product head `8224cd45...` and live base.
   - Add the final source-mutation matrix before production edits.
   - Against `8224cd4`, record that duplicate retry lane identity and impossible timestamp violate
     AC-1 by emitting `READY/HIGH`; also record the new observation-only CLI contract failure.
   - This is the active RED. The old missing-command RED is historical evidence only.
2. **Producer-only review input.**
   - Positive fixture must be created by the real `rehydrate-interactive` source path.
   - Mutate source policy/receipt for coordinated stale key, unsatisfied-clean,
     satisfied-incomplete, duplicate retry lane, impossible timestamp, empty obligations,
     malformed pointer, pointer identity drift, and evidence verification failure.
   - Every producer rejection maps to `UNKNOWN/LOW/invalid-review-evidence`.
   - Supplying `review_decision`, `--decision-file`, or any unknown key/option is rejected.
3. **Observation schema and identity.**
   - Exercise every status enum, duplicate/unknown members, malformed hashes, invalid
     required/status pairs, and one-at-a-time observed/CI/test head mutations.
4. **Verdict table.**
   - Real producer all-pass → `READY/HIGH`.
   - Independent CI fail, test fail, and producer-derived review blocker →
     `NOT_READY/HIGH`.
   - Exact negative plus another pending signal stays `NOT_READY/HIGH`.
   - Pending/unknown/unavailable required evidence and producer-derived required gap →
     `UNKNOWN/LOW`.
5. **Canonical binding.**
   - Pretty/reordered observation JSON and the same producer result hash identically.
   - Changing either an observation or producer source changes the internal binding hash.
6. **Purity and regression.**
   - Failing transport stubs plus empty call ledger.
   - `bash kc-pr-flow/scripts/review-runtime.test.sh --case merge-readiness`
   - `bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision`
   - `bash kc-pr-flow/scripts/review-runtime.test.sh`
   - `bash kc-pr-flow/scripts/review-post.test.sh`
   - Bash syntax, pinned ShellCheck v0.9.0, `git diff --check`, exact changed-path review.
7. **CLI E2E.**
   - Invoke the committed command with real regular receipt, policy, repository worktree,
     exact identity, and observation files; parse its decision and independently recompute the
     internal binding hash.
   - Browser/full-stack E2E remains skipped because there is no UI, service, or remote mutation.

### Proposed documentation diff

- `kc-pr-flow/reference/review-runtime.md`
  - Before at rejected head: `decide-merge-readiness --input-file FILE` accepts a closed object
    containing a caller-supplied review decision.
  - After: `decide-merge-readiness` accepts closed CI/test/head observations plus the existing
    terminal receipt, policy, repository worktree, and exact identity arguments; it calls
    `rehydrate-interactive` in-process and accepts no decision file or decision JSON member.
  - Add: producer rejection maps to advisory `UNKNOWN/LOW`; the canonical binding hashes the
    successful producer output together with observations.
- `kc-pr-flow/CLAUDE.md`
  - Replace the claim that a mutation matrix validates a caller-provided decision with:
    “Readiness consumes only the successful in-process `rehydrate-interactive` result; callers
    supply observations and producer sources, never a review decision.”
- `kc-pr-flow/README.md`
  - Preserve the three verdict/confidence pairs and human-only merge authority.
  - Add the bounded provenance statement: invalid producer sources or observations yield
    `UNKNOWN`; no caller-authored decision can reach `READY`.

No `PRODUCT.md`, `ARCHITECTURE.md`, §6c, skill recipe, review-post, daemon, or release metadata
change is proposed.

### Risk spike

Read-only spike completed on rejected head `8224cd4`:

- `review_runtime_rehydrate_interactive` and `review_runtime_decide_merge_readiness` are functions
  in the same Bash runtime, so the reducer can capture the producer result and status without a
  new executable or process authority.
- The producer's current source validation already holds the cycle-2 rules at
  `review-runtime.sh:2202` (non-empty obligations), `:2229` (unique lane references), and
  `:2284-2286` (semantic timestamp), plus pointer shape/identity/content verification at
  `:2291-2314`.
- `bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision` passed
  **51/0**. Its mutation matrix independently covers impossible timestamps, missing obligations,
  fallback shape, pointer identity/content drift, retries, and exact identity.

Spike result: direct composition relies on an existing exercised mechanism. No implementation
spike or new schema authority is needed. The remaining risk is argument/input plumbing and
canonical binding, covered by focused RED/GREEN and the real CLI round trip.

### Fresh appetite and implementation sizing

- **Ideation-declared estimate:** one implementation worker, **90 minutes**.
- **Declared tolerance:** **15 minutes**. At **105 minutes**, stop and park with the focused RED,
  current diff, and explicit open finding; do not compress validation or add another patch cycle.
- **Hard stop/re-cut:** any need for a second runtime, signature/secret/state authority, live
  GitHub fetching, daemon/posting changes, model routing, cross-repo adoption, or a caller-supplied
  review-decision validator.
- **Sizing:** ONE worker. This is one behavior seam and one RED→GREEN loop. No extra reviewer or
  parallel dispatch is included in the appetite.

### Active pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a **hidden assumption**:
the reducer may accidentally hash only observations rather than the exact successful producer
decision, allowing two distinct review results to share one advertised input binding.

## Measurement

D1 launched 2026-07-30T15:02:24Z | tokens: n/a
D2 launched 2026-07-30T15:41:11Z | tokens: n/a
D3 launched 2026-07-30T16:18:28Z | tokens: n/a
D4 launched 2026-07-30T16:21:00Z | tokens: n/a
D5 launched 2026-07-30T16:38:39Z | tokens: n/a
D6 launched 2026-07-30T17:01:09Z | tokens: n/a
D7 launched 2026-07-30T17:11:06Z | tokens: n/a
D8 launched 2026-07-30T23:29:42Z | tokens: n/a
D9 launched 2026-07-30T23:53:37Z | tokens: n/a
D10 launched 2026-07-31T06:21:45Z | tokens: n/a
D11 launched 2026-07-31T06:52:56Z | tokens: n/a
D12 launched 2026-07-31T08:31:33Z | tokens: n/a
D13 launched 2026-07-31T08:37:43Z | tokens: n/a
D14 launched 2026-07-31T08:46:40Z | tokens: n/a

## Stage Report: ideation

TL;DR — Cycle 2 is re-cut around one structural invariant: merge readiness no longer accepts or
validates caller-supplied `InteractiveCollationDecision/v1`. The command composes directly with the
existing `rehydrate-interactive` producer in the same runtime invocation, so only a successful
producer result can drive `READY`, `NOT_READY`, or review-derived `UNKNOWN`. This removes the
duplicated consumer language instead of adding a third field patch.

- DONE: Treated rejected head `8224cd4` and its validation report as failure evidence, not a
  baseline.
- DONE: Refreshed `origin/main@6f51c55`; confirmed intervening `kc-pr-flow` changes are only
  release manifests and changelog, with no runtime overlap.
- DONE: Re-ran the reverse-recovery trace and classified the producer/projection
  `WORKING_UNIT_UNPROVEN`, live-main readiness `MISSING`, and rejected decision-only consumer
  `EXISTS_BROKEN`.
- DONE: Compared direct producer composition, a shared post-projection validator, and a
  producer-generated receipt.
- DONE: Chose the cheap sound path: direct in-process composition with no caller decision member
  or option. Rejected the decision-only validator because source-only producer guarantees are not
  retained in the projection; rejected the receipt because unkeyed self-hashes add no provenance.
- DONE: Defined the closed observation contract, reused producer source arguments, internal
  producer+observation binding, ordered verdict table, and advisory-only output.
- DONE: AC-1 — Re-cut producer-only review evidence around every cycle-1/cycle-2 counterexample.
- DONE: AC-2 — Re-cut the exact-head verdict table around zero producer-inconsistent false
  positives while preserving a real producer positive.
- DONE: AC-3 — Preserved the advisory-only decision, §6c, empty side-effect ledger proof, and
  human-only merge authority.
- DONE: AC-4 — Bounded the reset to one existing runtime, its focused tests, and plugin docs, with
  the duplicated consumer validator removed and no new receipt/runtime authority.
- DONE: Defined a RED against exact rejected head `8224cd4`, not untouched main: both proven
  producer-inconsistent positives and the new observation-only boundary must fail before GREEN.
- DONE: Recorded the focused producer-mutation test plan, real CLI E2E, purity stubs, regression
  gates, doc before/after wording, risk spike, and implementation boundary.
- DONE: Ran the producer spike at `51 passed, 0 failed`, covering the existing source-validation
  authority reused by the reset.
- DONE: Set a fresh one-worker 90-minute appetite with 15-minute tolerance and explicit stop/re-cut
  exclusions.
- SKIPPED: Browser/full-stack E2E because the surface is a local CLI with no UI, service, or remote
  mutation.
- SKIPPED: Product code changes; ideation changes only this task state.

### Summary

The active design makes `rehydrate-interactive` the single review-language authority. The
readiness reducer receives observations and producer sources, obtains the decision in-process,
binds that exact result into its input hash, and never accepts a caller-authored decision. This is
the smallest bounded reset that structurally prevents another producer/consumer validator drift
while preserving advisory-only human merge authority.

## Stage Report: implementation

TL;DR — Replaced the rejected caller-decision consumer grammar with direct composition over the
existing `rehydrate-interactive` producer. The exact rebased product head
`b2b71acb0583ab3573bc3d43229e8677f141b0e0` is pushed and remote-equal. Fresh exact-head gates are
green at merge-readiness **67/0**, interactive producer **49/0**, full runtime **372/0**,
unchanged review-post **156/0**, pinned ShellCheck v0.9.0, Bash syntax, diff checks, and a real
regular-file CLI round trip.

- DONE: AC-1 — removed caller-supplied review decisions from the external contract. The reducer at
  `kc-pr-flow/scripts/review-runtime.sh:2402-2571` validates only closed observations, calls
  `review_runtime_rehydrate_interactive` once at `:2459`, maps producer rejection to
  `UNKNOWN/LOW/invalid-review-evidence`, and uses only the successful returned decision.
- DONE: AC-1 — deleted the readiness-side `InteractiveCollationDecision/v1` jq grammar. A static
  review of the reducer found one producer-call site and zero copied `interactive_decision`,
  `manual_result`, or `fallback` definitions.
- DONE: AC-1 — focused source mutations cover coordinated stale key, unsatisfied clean,
  satisfied incomplete, duplicate lane reference, impossible timestamp, empty obligations,
  malformed pointer, pointer identity drift, and evidence verification failure at
  `kc-pr-flow/scripts/review-runtime.test.sh:311-364`. Every case now emits
  `UNKNOWN/LOW/invalid-review-evidence`.
- DONE: AC-1 — a supplied `review_decision` member is closed-schema invalid, and the rejected
  `--input-file` caller-decision surface is refused at the CLI boundary
  (`review-runtime.test.sh:369-464`).
- DONE: AC-2 — exact-head CI/test/review truth-table cases remain closed and ordered. Real
  producer-positive evidence reaches `READY/HIGH`; current CI, test, and review negatives reach
  `NOT_READY/HIGH`; incomplete required evidence reaches `UNKNOWN/LOW`; observed/CI/test head
  drift reaches `UNKNOWN/LOW/head-or-identity-mismatch`.
- DONE: AC-2 — `input_sha256` hashes the normalized
  `kc-pr-flow.merge-readiness-binding/v1` containing both observations and the exact producer
  output (`review-runtime.sh:2487-2496`). The focused test independently constructs those canonical
  bytes at `review-runtime.test.sh:176-185`.
- DONE: AC-3 — preserved advisory-only human merge authority. The real CLI ran with failing
  `gh`, `curl`, `wget`, `nc`, and `ssh` stubs and an empty mutation/transport ledger; the reducer
  block also contains no such command call. `kc-pr-flow/skills/kc-pr-review/SKILL.md`,
  `scripts/review-post.sh`, and `scripts/review-post.test.sh` hash byte-for-byte to
  `origin/main@9eddf99`.
- DONE: AC-3 evidence wording correction — local `git` is deliberately not stubbed.
  Direct composition reuses `rehydrate-interactive`, whose evidence verification makes read-only
  `git -C <repo>` calls against the supplied worktree. The proved boundary is no model, network,
  GitHub, posting, authorization, daemon, repair, or merge authority. This corrects the earlier
  over-broad purity wording without expanding scope.
- DONE: AC-4 — final `origin/main...HEAD` changed paths are exactly the approved runtime, focused
  test, and three plugin documentation files:
  `kc-pr-flow/scripts/review-runtime.sh`,
  `kc-pr-flow/scripts/review-runtime.test.sh`,
  `kc-pr-flow/reference/review-runtime.md`,
  `kc-pr-flow/README.md`, and `kc-pr-flow/CLAUDE.md`.
- DONE: AC-4 — docs now publish the producer-only observation/source contract, canonical internal
  binding, producer-rejection behavior, advisory verdict vocabulary, and human-only merge
  boundary at `reference/review-runtime.md:133-154,179`, `README.md:68-76`, and
  `CLAUDE.md:59-67`.

### Strict TDD evidence

- **Rejected-head RED construction:** the disconnected worker left no durable active-reset RED
  transcript. A detached scratch worktree used production from exact rejected head
  `8224cd45d36a73c7a3bc4ff4063cc4ed17dcb6ff` plus the recovered final test file, without changing
  the product WIP.
- **RED result:** `bash kc-pr-flow/scripts/review-runtime.test.sh --case merge-readiness` exited 1
  at **17 passed / 50 failed**. Transcript SHA-256:
  `47e604dd25eda9458eae5a072a6bd6929ee62b59ab68e2f5ca3a425177450cab`.
  The observation-only command failed first with
  `expected [0], got [2]`; every one of the 50 new behavior assertions was subsequently reachable
  and failed.
- The 17 RED passes were not hidden behavior claims: 14 were pre-existing producer regression
  assertions, two were explicitly labeled arrangement preconditions, and one was the explicitly
  labeled regression-only empty transport-ledger invariant.
- **Exact rejected false positives:** running the old caller-decision CLI against its three
  producer-impossible decisions emitted
  `READY|HIGH|all-required-evidence-positive` for duplicate retry lane identity, impossible manual
  timestamp, and empty capabilities. The new command refuses that caller-decision boundary and the
  source-mutation matrix routes the same producer inconsistencies through the canonical producer.
- **Exact-head GREEN:** focused merge-readiness **67 passed / 0 failed**, transcript SHA-256
  `bfe5ff854d2916f4821a6e783f472aa45a61b201be9a5685e4eca60652d206a6`.
- **Old-fixture audit:** no unrelated historical scenario was repurposed. The obsolete
  caller-decision fixture matrix was replaced because that external contract was removed; the
  existing real terminal-rehydration setup remains the producer arrangement and its historical
  producer assertions stay in the `interactive-decision` case.

### Exact-head verification

All final checks below ran after rebasing onto `origin/main@9eddf99`, on product head
`b2b71acb0583ab3573bc3d43229e8677f141b0e0`:

```bash
bash kc-pr-flow/scripts/review-runtime.test.sh --case merge-readiness
bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision
bash kc-pr-flow/scripts/review-runtime.test.sh
bash kc-pr-flow/scripts/review-post.test.sh
bash -n kc-pr-flow/scripts/review-runtime.sh \
  kc-pr-flow/scripts/review-runtime.test.sh
docker run --rm --platform linux/amd64 -v "$PWD:/mnt" -w /mnt \
  koalaman/shellcheck:v0.9.0 \
  kc-pr-flow/scripts/review-runtime.sh \
  kc-pr-flow/scripts/review-runtime.test.sh
git diff --check origin/main...HEAD
git diff --name-only origin/main...HEAD
```

- Merge-readiness: **67 passed, 0 failed**; SHA-256 `bfe5ff854d2916f4821a6e783f472aa45a61b201be9a5685e4eca60652d206a6`.
- Interactive producer: **49 passed, 0 failed**; SHA-256 `62c340c29c2efdf1a7f899a3b3261cdfe46c27ba7bc0eac9daa9e7b1e9227fba`.
- Default runtime: **372 passed, 0 failed**; SHA-256 `5db3881a318270326fc94f24cb5eb3e085606719b6ee4b43d203bf4f6b04be9a`.
- Review-post ripple: **156 passed, 0 failed**; SHA-256 `e7240ae969d70f9e851f7e89ac48b5d9d743175e34fb95c151f6ae580d609bfc`.
- Pinned ShellCheck v0.9.0 exited 0 with empty output; Bash syntax and
  `git diff --check origin/main...HEAD` exited 0.
- Direct E2E used regular observation, terminal receipt, policy, and repository files. It invoked
  the full committed command, independently rehydrated the producer, recomputed the canonical
  binding hash `b1aa8b7806bf15b2a06f3acd6cc030fe28b6071b8fd78537aa79958ee036eb3e`,
  and asserted schema, `READY/HIGH`, canonical reason, `advisory_only:true`, exact head, matching
  binding, and empty transport ledger. Decision-output SHA-256:
  `07fd702af34dec333e27e666af6a19401140560533529d304678d46d3aa933d9`.
- Browser/full-stack E2E is skipped because this is a local CLI with no UI, service, or remote
  mutation. The regular-file producer-composed CLI invocation is the end-to-end surface.

### CI timing disclosure

- `.github/workflows/review-runtime-tests.yml` retains `timeout-minutes: 20`.
- Latest successful live-main job before push, run `30566386141` / job `90951846061` at
  `6f51c55`, used 559 of 1200 seconds; its runtime-contract step used 75 seconds.
- The exact-head local default suite used 242 seconds. The same-machine untouched baseline
  previously recorded in this entity was 93.24 seconds, a local delta of 148.76 seconds.
  Conservatively adding that complete local delta to the live-main job projects about 708 seconds,
  leaving about 492 seconds before the job cap. This is a margin disclosure, not a reproduction of
  mutable `ubuntu-latest`.

### Review, scope, and durability

- This worker began with `git status`, `git diff --check`, and a semantic review of the recovered
  five-path WIP. Because the implementation author had disconnected, the replacement worker's
  read-only whole-diff review was independent of the author. It found no critical, important, or
  in-scope minor defect; no extra reviewer/model worker was spawned.
- The recovery preserved legitimate WIP and made no product edit beyond the recovered five paths.
  No new runtime, receipt/signature/state authority, model route, daemon behavior, GitHub fetch,
  posting behavior, repair loop, merge operation, or cross-repo adoption entered the diff.
- Product commits were rebased onto live `origin/main` and pushed with an exact old-head
  force-with-lease. Local and remote branch tips both equal
  `b2b71acb0583ab3573bc3d43229e8677f141b0e0`; the product worktree is clean and upstream-equal.
- No PR was created and no merge was performed, per dispatch.

### Summary

Merge readiness now receives only exact-head observations and canonical producer sources. It calls
the existing terminal producer once, binds the successful producer decision into the decision
hash, rejects producer-impossible evidence as `UNKNOWN`, and cannot accept a caller-authored
review decision. The bounded five-path implementation is pushed with fresh exact-head RED/GREEN,
regression, purity, E2E, static, timing, and independent-review evidence.

## Stage Report: validation

TL;DR — **PASS / GATE READY for human landing.** Fresh validation found no material finding on
exact product head `b2b71acb0583ab3573bc3d43229e8677f141b0e0` against current remote main
`9eddf9928d6d7ae391d3b11adab2e920b5ec0b2c`. The producer-composed reset closes the two rejected
caller-decision architectures: only observations and producer sources cross the CLI boundary,
producer-inconsistent evidence fails closed, exact-head verdict ordering is preserved, and no
posting or merge authority entered the five-path diff.

- DONE: Independently reproduced every active criterion at exact product/base heads and attacked the
  producer-only contract with all prior counterexamples plus fresh inconsistent inputs. AC-1 and
  AC-2 evidence: `kc-pr-flow/scripts/review-runtime.test.sh:116-470` and
  `kc-pr-flow/scripts/review-runtime.sh:2402-2568`.
- DONE: Validated the five mapped paths with the required lenses, 88.17% executable diff coverage,
  an isolated guard-breaking mutation, real regular-file CLI E2E, full/ripple/static checks, and
  conservative CI-margin evidence. AC-3 and AC-4 scope anchors:
  `kc-pr-flow/scripts/review-runtime.sh:2402-2568`,
  `kc-pr-flow/scripts/review-runtime.test.sh:116-470`, and
  `kc-pr-flow/reference/review-runtime.md:133-154`.
- DONE: Ran the mandatory different-vendor `agy` review, discarded stale/timed-out/citation-invalid
  rounds, verified the one cited regression claim against the base, and published the gate-ready
  five-line evidence block with a PASS verdict. The review reconfirmed AC-1, AC-2, AC-3, and AC-4;
  citation-audit policy: `docs/dev/README.md:984-990`.

### Exact head, scope, and fresh-review boundary

- Product `HEAD`, its upstream, and the remote branch all equal
  `b2b71acb0583ab3573bc3d43229e8677f141b0e0`; the product worktree is clean.
- Remote and local `origin/main` both equal
  `9eddf9928d6d7ae391d3b11adab2e920b5ec0b2c`, which is also the merge base.
  The product branch is three commits ahead and zero behind.
- `origin/main...HEAD` is exactly **5 files, 696 insertions, 5 deletions**:
  `kc-pr-flow/scripts/review-runtime.sh`,
  `kc-pr-flow/scripts/review-runtime.test.sh`,
  `kc-pr-flow/reference/review-runtime.md`,
  `kc-pr-flow/README.md`, and `kc-pr-flow/CLAUDE.md`.
- `git diff --summary` is empty: no mode change or new executable entered the diff.
- The validator read the complete five-file change, the active reset AC, and the unchanged producer
  and post-authority context. It made no product edit, did not finish implementation, create a PR,
  post, merge, amend, or widen scope.

### Acceptance criteria

- DONE: AC-1 — PASS — only producer output drives readiness.
  `review_runtime_decide_merge_readiness` accepts a closed observations file plus the existing
  producer's receipt, policy, repository, and exact-identity sources
  (`kc-pr-flow/scripts/review-runtime.sh:2402-2415`). A static reducer scan found exactly one
  `review_runtime_rehydrate_interactive` call at
  `kc-pr-flow/scripts/review-runtime.sh:2459-2461`. There is no caller decision option:
  direct `--input-file` and `--decision-file` probes both exited 2 as unknown options. The focused
  matrix returned **67/0**, including the nine coordinated stale-key, terminal-state, lane,
  timestamp, obligation, pointer, and evidence-verification source mutations at
  `kc-pr-flow/scripts/review-runtime.test.sh:308-364`; every mutation reached
  `UNKNOWN/LOW/invalid-review-evidence`. A caller `review_decision` member was closed-schema invalid.
- DONE: AC-2 — PASS — exact-head truth table and canonical internal binding.
  The real producer positive returned `READY/HIGH/all-required-evidence-positive`; CI, test, and
  producer-derived review negatives returned `NOT_READY/HIGH`; pending, unknown, unavailable, or
  incomplete review evidence returned `UNKNOWN/LOW`; and all three observed/CI/test head mutations
  returned `UNKNOWN/LOW/head-or-identity-mismatch`
  (`kc-pr-flow/scripts/review-runtime.test.sh:163-305`). The reducer binds canonical observations and the exact
  producer result in `kc-pr-flow.merge-readiness-binding/v1`
  (`kc-pr-flow/scripts/review-runtime.sh:2488-2496`). The independent regular-file E2E recomputed the same
  `input_sha256`, `db4df89d887b4a783dd38650fde6697c7273c6d4ed5557201f584a962de64045`.
- DONE: AC-3 — PASS — advisory and side-effect free.
  The real CLI output kept `advisory_only:true`; failing `gh`, `curl`, `wget`, `nc`, and `ssh`
  stubs recorded a zero-byte call ledger and the reducer contains zero prohibited command tokens.
  Unsafe-directory observations exited 2 with zero stdout. Local `git` remained intentionally
  available for producer evidence verification. Base/head blob IDs are identical for
  `kc-pr-flow/skills/kc-pr-review/SKILL.md`, `scripts/review-post.sh`, and
  `scripts/review-post.test.sh`; the fresh unchanged post suite returned **156/0**. Authority and
  ripple anchors: `kc-pr-flow/skills/kc-pr-review/SKILL.md:1723`,
  `kc-pr-flow/scripts/review-post.test.sh:227`, and
  `kc-pr-flow/scripts/review-runtime.sh:2402-2568`.
- DONE: AC-4 — PASS — one bounded runtime cut.
  The exact five paths are the existing runtime, its existing test, and three plugin docs. The
  reducer contains one producer-call site and no second caller-decision grammar. No decision file,
  new executable, receipt/signature/state authority, model route, network fetch, daemon, repair
  loop, posting operation, merge operation, or cross-repo adoption entered the diff. Bash syntax,
  pinned ShellCheck v0.9.0, `git diff --check`, exact changed-path review, and protected-path blob
  checks all exited 0. Replacement and test anchors:
  `kc-pr-flow/scripts/review-runtime.sh:2402-2568`,
  `kc-pr-flow/scripts/review-runtime.test.sh:116-470`, and
  `kc-pr-flow/reference/review-runtime.md:133-154`.

### Published-guarantee falsifiers

- **“Only producer output” / “no caller decision”:** closed-schema member mutation returned
  `UNKNOWN/LOW/invalid-input`; legacy `--input-file` and `--decision-file` commands exited 2.
- **“Exactly one producer call”:** the reducer slice contains one call site, and the direct E2E
  used the producer-composed committed command.
- **“Invalid, stale, or incomplete evidence cannot become READY”:** the source-mutation matrix,
  three head mutations, all incomplete statuses, malformed/duplicate observation cases, and an
  unsafe regular-file probe all failed closed.
- **“Canonical binding”:** the focused pretty/reordered-input case and an independent E2E
  rehydration both reconstructed the binding bytes and matched the emitted hash.
- **“No live/network/post/auth/merge authority”:** the failing-command ledger stayed empty,
  protected post/skill blobs matched the base, and the unchanged post suite passed.

### Fresh executable verification

- Focused merge-readiness: **67 passed, 0 failed**, 414.29s.
- Focused interactive producer: **49 passed, 0 failed**, 174.37s.
- Complete runtime under isolated Bash-5.3 runtime-only xtrace: **372 passed, 0 failed**, 760.99s.
  A first inherited-xtrace attempt was discarded because Bash 3.2 routed trace text through
  stderr and perturbed the suite; it supplied no verdict or coverage evidence.
- Complete runtime without instrumentation: **372 passed, 0 failed**, 609.00s.
- Untouched-base runtime, timed on the same host immediately afterward: **305 passed, 0 failed**,
  202.12s.
- Unchanged review-post ripple: **156 passed, 0 failed**, 482.06s.
- Pinned `koalaman/shellcheck:v0.9.0` over the runtime and test exited 0 with empty output.
- Bash syntax, `git diff --check origin/main...HEAD`, exact five-path, no-mode-change,
  producer-call-count, legacy-option, prohibited-command, and protected-blob checks all passed.

### Coverage, adversarial, and E2E details

The runtime-only trace observed 82 of 93 changed executable shell command points, **88.17%**.
The denominator excludes comments, declarations that only define functions, braces,
continuation-only lines, and embedded jq program bodies while counting the shell command that
executes each jq program once. The 11 unobserved fail-safe points are the unexpected
duplicate-classifier return, canonical-observation fallback, producer-canonicalization/identity
fallbacks, and missing-value/required-argument CLI diagnostics at
`review-runtime.sh:2426,2429-2430,2466-2467,2484-2485,3028-3029,3056-3057`.

In an isolated copied tree, replacing the observed-head equality with `true` turned the focused
suite red at **66 passed, 1 failed**. The sole failure changed the observed-head mutation from
`UNKNOWN/LOW/head-or-identity-mismatch` to
`READY/HIGH/all-required-evidence-positive`, directly proving that the committed guard is
behaviorally covered.

The regular-file E2E used a real terminal receipt, merge-ready policy, evidence repository, and
positive observations. The untouched committed CLI returned the closed
`READY/HIGH/all-required-evidence-positive` advisory decision at exact fixture head
`5aeb592e2550875f04ba112a17529eae333db476`, with zero stderr and zero transport-ledger bytes.
Independent producer rehydration and binding reconstruction matched
`db4df89d887b4a783dd38650fde6697c7273c6d4ed5557201f584a962de64045`; output SHA-256 was
`cb3c1dad991fe74056be6117130d593a29ccb776cc9ec3bfb061b7bce0d8c3d9`.
Browser/full-stack E2E is not the applicable surface because this change has no UI, service, or
remote mutation.

### Different-vendor review audit

Codex used Google Antigravity `agy` 1.1.9 first, in read-only plan/sandbox mode. The initial
workspace-backed round reported the wrong project head and was discarded. A clean-project retry
timed out. The first embedded-patch response had more than one-third wrong citations and was
discarded under the repo citation rule. A stricter embedded round cited the wrong test line for a
claim that the default suite skipped full interactive coverage; independent base comparison proved
that focused `interactive-decision` was already a separate case on `origin/main`, so the claimed
regression was not change-induced and the citation-invalid round was discarded. The final
citation-free, embedded exact-five-path review returned exactly `NO_MATERIAL_FINDINGS`. The CLI did
not expose an exact model ID; no discarded round influenced this verdict.

### CI-margin disclosure

- `.github/workflows/review-runtime-tests.yml` retains `timeout-minutes: 20`.
- There is no GitHub check run for exact head `b2b71acb`; this is explicitly not live exact-head CI
  proof.
- Fresh live-main run `30566386141`, job `90951846061`, at `6f51c55` completed successfully in
  559 seconds. Its runtime-contract step used 75 seconds and review-post used 282 seconds.
- Same-host exact-head runtime minus untouched-base runtime is 609.00 - 202.12 =
  **406.88 seconds**. Conservatively adding that whole local delta to the live-main job projects
  **965.88 of 1200 seconds**, leaving about **234 seconds**. This is a margin estimate across
  different runners, not a claim that mutable `ubuntu-latest` was reproduced.

### Material findings

None.

### Evidence block

- Lenses: PASS — correctness 0 findings; silent-failure 0; type-design 0; security/trust-boundary 0; resource-lifecycle 0. Correctness always fired; input validation/fallbacks fired silent-failure; the new observations/binding/decision contracts fired type-design; caller-controlled evidence crossing into a merge advisory fired security; the private snapshot/trap fired resource-lifecycle. Concurrency did not fire because no locks, async ordering, or shared mutable state changed. Manifest/back-compat did not fire because no manifest, frontmatter, install-resolution, or existing command contract changed; the command is additive.
- Diff coverage: PASS — 82/93 changed executable shell command points observed, **88.17%**, above the 85% ratchet.
- Adversarial: PASS — isolated observed-head guard removal returned **66/1** and produced the exact forbidden `READY/HIGH` false positive.
- Cross-model: PASS — Codex → Google Antigravity `agy` 1.1.9; final citation-free exact-patch round returned `NO_MATERIAL_FINDINGS`; stale, timed-out, or citation-invalid rounds were discarded and not relied on.
- E2E: PASS — real regular-file producer-composed CLI returned `READY/HIGH`, exact identity and independently matched binding `db4df89d...64045`, with zero stderr and zero transport calls; browser/full-stack is not applicable because there is no UI, service, or remote mutation.

### Feedback cycles

- Fresh post-reset validation: **PASS**. No post-reset correction cycle was opened. The two
  historical rejections remain attached to the superseded caller-decision architectures and are
  not counted again against this reset.

### `--ac-scan`

```text
stage=validation
ac=AC-1 unevidenced=false citations=4
ac=AC-2 unevidenced=false citations=4
ac=AC-3 unevidenced=false citations=4
ac=AC-4 unevidenced=false citations=3
```

### Summary

Exact-head validation accepts the active producer-composed reset. The committed reducer has one
producer authority, no caller-decision surface, closed exact-head observations, deterministic
producer-bound hashing, ordered fail-closed verdicts, and advisory-only behavior. Focused,
complete, ripple, static, coverage, adversarial, E2E, cross-vendor, scope, and timing checks are
green with no material finding. Human landing remains the next authority; validation did not post,
create a PR, or merge.
