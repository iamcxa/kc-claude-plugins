# Historical implementation records relocated from retained documentation

These are preserved verbatim historical shape and measurement records, not current status or renewed authority. The accepted correction limit in index.md remains authoritative. Source: the protocol specification and runtime usage document in the implementation worktree, read before relocation during correction of rejected candidate 55b7cd28. All accepted outcome, runtime, posting and stop boundaries remain in the retained contract and work item.

## Preserved block 1

- **Delivery base:** `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`
- **Work item:** `profiled-pr-review-capability-protocol`
- **Profile:** Pilot / Product slice
- **Status:** shaped for a default-off Lite implementation

## Preserved block 2

This
is an explicit
shape delta from the Development Brief's executable bounded-expansion wording
and requires Captain acceptance at the ideation gate before build begins.

## Preserved block 3

## Reverse-recovery audit

The boundary was the accepted exact-head-to-confirmation journey. Search one used
`rg` across current `kc-pr-review`, runtime, posting, triage, tests, and project
context. Search two compared the exact `origin/main` tree with the live heads and
file inventories of Draft PRs #352-#355. A reviewer-directed third search found
the existing `review-ablation` measurement harness and daemon cost ledger that
the first two searches missed; the route below now recovers them explicitly.

| Surface | Location | Completeness | Need | Decision and disproof hook |
|---|---|---|---|---|
| Exact-head identity, evidence pointers, typed coverage, replay | `review-runtime.sh`, `review-runtime.test.sh` | WORKING_UNIT_UNPROVEN | REQUIRED | **use**; a real typed Lite run with a moved-head mutation must fail closed. |
| Confirmation projection and posting owner | `kc-pr-review/SKILL.md`, `review-post.sh` | WORKING_UNIT_UNPROVEN | REQUIRED | **use**; the unchanged posting contract must reject an edited event or stale head. |
| Deterministic delta planner shape | Draft PR #353 `review-plan.sh` | WORKING_UNIT_UNPROVEN | REQUIRED | **recover selectively**; canonical equal inputs must yield equal plans, and invalid evidence must select the safe route. |
| Profile-scoped Evidence Builder | current tree | MISSING | REQUIRED | **build**; two searches found no owner producing a plan-selected bundle with mechanical-test receipts. |
| Capability manifest/request/result API | current tree | STUB | REQUIRED | **build** from existing capability names and lane results; schema mutations must be rejected. |
| General Reviewer question collation | current tree | STUB | REQUIRED | **build** around existing typed decision; duplicate/missing question terminals must fail. |
| Authority-bearing receipt projection | `review-runtime.sh` append/replay seam | STUB | REQUIRED | **build fail-closed mode**; a complete rendered Lite result must replay with every lane/reference and behavior hash sealed before confirmation. |
| Frozen blind-run provenance | `review-ablation.sh`, core, corpus, driver, tests | WORKING_UNIT | REQUIRED | **use runner and recover minimally**; base tests pass 82/0. Add committed whole-tree arms, five-PR Lite corpus, pinned effort/host/tools/timeout, and Pilot comparator. Existing alpha-0.05 comparator is not the wall-time verdict. |
| Historical cost ledger | `pr-review-daemon.sh` usage JSONL | WORKING_UNIT_UNPROVEN | REQUIRED | **use read-only**; fewer than five valid completed reviews or any malformed selected record blocks budget calculation. |
| Inline shadow collection recipes | `kc-pr-review/SKILL.md` | WORKING_UNIT_UNPROVEN | NO_OBSERVED_CONSUMER after Lite cutover | **removal candidate only**; delete only after default-off parity and without-it evidence. |
| Add-only expansion through current runtime | `review-runtime.sh` capability identity and attempt rules | INCOMPATIBLE | NOT REQUIRED IN EXECUTABLE LITE | **document only**; any request terminates incomplete. Runtime contract change requires a new accepted route. |

The resulting route is use existing identity/evidence/confirmation/posting,
recover only the planner idea rather than its 662-line implementation, and build
the missing protocol layer. No existing surface is deleted in shape.

## Preserved block 4

```yaml
project_context:
  impact: update
  authority: PRODUCT.md and ARCHITECTURE.md
  claim_locator: 'PRODUCT.md heading "kc-pr-flow: Agent-native PR review"; ARCHITECTURE.md heading "kc-pr-flow: Agent-native review runtime"'
  surface: review component boundaries, target capabilities, and success measures
  stale_claim: D5 describes coverage only by capability; D2 closes the runtime event envelope; ARCHITECTURE.md line 201 makes InteractiveCollationDecision/v1 the approval authority; docs/review-runtime.md says the runtime does not adapt lane scheduling
  approved_change: retain D2 and the line-201 authority; project question gaps into existing capability obligations; add a default-off external Planner without moving confirmation or posting authority
  landed_change: pending
  planned_check: compare every journey component and authority row in this spec against PRODUCT.md and ARCHITECTURE.md, then run the protocol contract tests on the delivered exact head
  validation_evidence: pending
```

## Preserved block 5

## Where implementation may touch

Current line counts were measured at the pinned delivery base. New-file counts
are shape estimates, not budgets.

| Path | Lines now | Estimated after | Journey obligation |
|---|---:|---:|---|
| `kc-pr-flow/schemas/review-capability-v1.schema.json` | 0 | 540 | Closed V1 protocol source of truth, including class bindings and side-car telemetry. |
| `kc-pr-flow/schemas/review-capability-catalog-v1.json` | 0 | 180 | Sole question requiredness and capability-manifest authority. |
| `kc-pr-flow/scripts/review-capability.py` | 0 | 640 | Schema adapter, deterministic Lite plan, selected evidence, result validation, side-car telemetry, collation, Pilot verdict projection. |
| `kc-pr-flow/scripts/review-capability.test.py` | 0 | 720 | Positive, mutation, identity, required-gap, expansion, and rollback checks. |
| `kc-pr-flow/test/fixtures/review-capability-v1.jsonl` | 0 | 260 | Single-file valid and invalid exact-head protocol examples. |
| `kc-pr-flow/skills/kc-pr-review/SKILL.md` | 1,974 | 2,040 | Default-off Lite orchestration and existing confirmation projection. |
| `kc-pr-flow/scripts/review-runtime.sh` | 3,307 | 3,387 | Reuse exact identity and typed decision; add one fail-closed receipt-projection operation over the existing append/replay seam. |
| `kc-pr-flow/scripts/review-runtime.test.sh` | 2,884 | 2,960 | Integration rejection and unchanged-default evidence. |
| `kc-pr-flow/scripts/review-post.sh` | unchanged | unchanged | Existing posting owner; zero-line assertion/readback target only. |
| `kc-pr-flow/scripts/review-ablation.sh` | 593 | 673 | Reuse guarded runner; add committed whole-tree Pilot arms and pinned harness fields. |
| `kc-pr-flow/scripts/review-ablation-core.py` | 656 | 736 | Add canonical tracked-tree manifest and exact five-pair Pilot comparison support. |
| `kc-pr-flow/scripts/review-capability-corpus.tsv` | 0 | 7 | Five pre-registered primary plus one designated backup Lite/Lite PR snapshot. |
| `kc-pr-flow/scripts/review-ablation.test.sh` | 894 | 1,114 | Whole-tree arm, provenance, cost-ledger, adjudication, and promotion mutations. |
| `kc-pr-flow/scripts/review-ablation-driver-prompt.md` | 67 | 85 | Byte-identical driver updated to stop after confirmation-request production. |
| `kc-pr-flow/scripts/pr-review-daemon.sh` | unchanged | unchanged | Existing cost-ledger producer; read-only assertion target. |
| `.github/workflows/review-runtime-tests.yml` | 48 | 58 | Add the focused check to the existing owner; no new workflow. |
| `kc-pr-flow/docs/review-runtime.md` | current | current + 20 | Explain external planning while retaining runtime approval authority. |
| `PRODUCT.md` | 109 | 125 | Durable outcome and Pilot measure. |
| `ARCHITECTURE.md` | 269 | 330 | Components, authority, and data flow. |
| `docs/superpowers/specs/2026-09-05-kc-pr-review-capability-protocol-v1.md` | 0 | 950 | Retained accepted contract. |

The mapping is bidirectional: each journey step maps to a row above, and each row
supports a named journey or required documentation/CI obligation. Individual
capability views are generated from the single catalog; creating one tracked
file per question crosses the file stop and returns to shape.

## Preserved block 6

These bounds were re-derived after adding the previously missing catalog,
runtime documentation, posting assertion target, retained shape file, and
fail-closed receipt-projection operation. They now also count the smallest
recovery of the existing ablation runner instead of a second measurement
harness. The current estimate is at most 20 changed files, 5,269 changed lines
including this retained shape, and 1,582 focused schema/catalog/fixture/test
lines. The file map includes the original 18 paths plus the plugin README and
CLAUDE context. These are ceilings, not targets; without-it review must still
remove unnecessary surfaces.

Edits to this retained shape also consume the total-line ceiling. The 331-line
risk allowance covers runtime/fallback authority repairs (120), launcher and
terminal correlation repairs (90), schema/mutation coverage repairs (80), and
documentation/count repairs (41). The focused estimate plus its 80-line repair
allowance is 1,662, leaving 138 before the unchanged 1,800-line stop. These
allowances do not guarantee sufficiency; a breached stop returns to shape.

## Preserved block 7

- Current `review-runtime.test.sh`: 372 passed, 0 failed at the pinned base.
- Current `review-post.test.sh`: 156 passed, 0 failed at the pinned base and
  within the 15-minute shape bound.
- Current `review-ablation.test.sh`: 82 passed, 0 failed at the pinned base with
  the repository venv activated.
- `git diff --check` must pass on this document before shape review.

## Preserved block 8

One real local fixture observed about 1 second of prepare work, 93 seconds of
receipt projection and 7 seconds of rehydration. This is mechanical overhead,
not measured review speed or hosted CI cost. Repeated append validation is a
source-backed explanation to investigate, not a reason to weaken integrity.

