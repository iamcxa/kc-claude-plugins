<!-- section:plan-report -->
# Typed Interactive Lifecycle Plan

> **For executer:** preserve RED-before-GREEN evidence per task and commit one atomic task at a time.

**Goal:** Make exact-head typed state authoritative for interactive coverage, verdict eligibility, and confirmation input without acquiring posting or recovery authority.
**Architecture:** Extend the shipped Bash 3.2 + `jq` receipt runtime with one closed `InteractiveCollationDecision/v1` projection and terminal-only rehydration command, then consume that projection at the existing pre-confirmation review seam. Keep benchmark policy deterministic and remote behavior outside the runtime.
**Tech stack:** Bash 3.2+, Python 3.8+ safe-I/O helper, `jq`, JSONL, plain-Bash tests, GitHub Actions.

<details>
<summary>Mechanically imported design constraints</summary>

## Plan Imported Design DCs
<!-- section:plan-imported-design-dcs -->

| # | Type | Plan anchor | Decision |
|---|---|---|---|
| 1 | data-contract | T1 terminal exact-identity acceptance/rejection matrix | D1 |
| 2 | schema-contract | T1 closed decision projection and replay authority | D2 |
| 3 | data-contract | T1 evidence rehydration and forbidden-content scan | D3 |
| 4 | contract | T1 provider-neutral capability ownership; T3 usage policy | D4 |
| 5 | domain-contract | T1 capability terminal-state table | D5 |
| 6 | contract | T1 retry and typed manual-fallback matrix | D5 |
| 7 | contract | T1 COMMENT ceiling and blocker precedence | D5 |
| 8 | contract | T2 mandatory confirmation and no-mutation parity | D6 |
| 9 | schema-contract | T1 typed invalid/incomplete fail-closed behavior | D7 |
| 10 | contract | T2 pre-run kill-switch sampling | D7 |
| 11 | data-contract | T1 terminal-receipt-only rehydration boundary | D1 |
| 12 | data-contract | T3 ordered G1-G5 gate report | D5 |
| 13 | data-contract | T3 closed G5 branch eligibility and thresholds | D4 |

<!-- /section:plan-imported-design-dcs -->
</details>

## Research Summary

The shipped runtime already owns safe snapshotting, append/replay, evidence verification, provider-neutral observations, usage provenance, and authority-bound paired scoring. The smallest implementation surface is therefore `review-runtime.sh` plus its focused tests, the existing post-collation/pre-confirmation `kc-pr-review` seam, and the benchmark scorer/corpus. Current lane results are not yet the closed capability terminal model. The workflow still references the pre-archive 2.1 paths, so T4 repairs those exact CI inputs while synchronizing canonical/plugin docs. Research review produced no contract contradiction; the recovery circuit breaker forbids another research round.

## Size Re-evaluation

Confirmed M: four atomic tasks across runtime, skill integration, benchmark fixtures, canon, and CI. W2 is parallel because the skill/shadow task and benchmark task have disjoint write ownership after T1.

## Verification Spec

| DC | Verify procedure | Expected |
|---|---|---|
| DC-1 | `bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision` exact/moved identity fixtures | Only one complete terminal exact-identity run governs a decision; no recovery behavior runs. |
| DC-2 | Same case validates exact keys/schema and replay-derived output | Closed `InteractiveCollationDecision/v1` owns only coverage, event precedence, and confirmation input. |
| DC-3 | Same case mutates each pointer/object/content hash; scan state root for forbidden content | Every mutation fails closed and no raw review content persists. |
| DC-4 | Same case plus `bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh --case interactive-gates` | Capability authority is provider-neutral and unavailable usage stays null. |
| DC-5 | Runtime table covers all five terminal states and optional failure | Silence is not clean; optional incomplete evidence stays visible without blocking alone. |
| DC-6 | Runtime table covers transient retry, third attempt, and fallback evidence | Exactly one retry and one evidence-bound manual fallback are enforced. |
| DC-7 | Runtime table combines required gaps and blockers | Gap forbids APPROVE; blocker plus gap yields REQUEST_CHANGES. |
| DC-8 | `bash kc-pr-flow/scripts/review-shadow.test.sh --case typed-interactive-seam` | Both modes reach the same confirmation gate and mutation log is empty beforehand. |
| DC-9 | Runtime invalid/unsupported/incomplete matrix | Typed failure cannot govern approval or switch in-run to legacy. |
| DC-10 | Shadow test off/unset/unknown/on/mid-run-switch fixtures | Mode is sampled once before dispatch; changes affect only a fresh invocation. |
| DC-11 | `review-runtime.sh rehydrate-interactive` terminal/incomplete fixtures | Only terminal collator input reconstructs; no event append, resume, lock, retention, or remote state appears. |
| DC-12 | Benchmark gate-order fixtures force an earlier failure with later passing data | G1-G4 failures stop evaluation and cannot be repaired by G5. |
| DC-13 | Benchmark tests cover eligible/ineligible A/B observations and 19/20%, 60/61% boundaries | Only the two specified G5 branches can pass at the stated thresholds. |

## Canonical Doc Actions

| Doc | Action | Source | Rationale |
|---|---|---|---|
| ROADMAP.md | skip | plan | The existing parent row already owns the three-child delivery; this child creates no new roadmap item. |
| PRODUCT.md | update | design | Change Current increment from shadow-only to the shipped typed interactive authority and preserve the 2.3 boundary. |
| ARCHITECTURE.md | update | design | Record the closed decision projection, terminal rehydration, precedence, kill switch, and empirical gates. |

## Plan

### T1 — Derive a closed typed interactive decision from one terminal receipt
task_id: T1
layer: L4
wave: W1
files: `kc-pr-flow/scripts/review-runtime.sh`, `kc-pr-flow/scripts/review-runtime.test.sh`, `kc-pr-flow/test/fixtures/review-runtime/valid-events.jsonl`
skills_needed: [test, test-driven-development, best-practices, security-best-practices]
reviewer_questions: Does replay remain the only receipt projection authority; are capability requiredness, terminal states, one retry, fallback evidence, COMMENT ceiling, and blocker precedence core-owned; does exact-identity terminal rehydration avoid every PR3 operation and durable raw content?
tdd_contract:
  red_command: "bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision"
  expected_red_failure: "The runtime has no closed interactive decision or terminal-only rehydration command, and cannot reject the full capability/identity mutation matrix."
  green_command: "bash kc-pr-flow/scripts/review-runtime.test.sh --case interactive-decision"
  refactor_check: "bash -n kc-pr-flow/scripts/review-runtime.sh kc-pr-flow/scripts/review-runtime.test.sh && bash kc-pr-flow/scripts/review-runtime.test.sh"
parallel_group: serial
depends_on: []
owned_paths: [kc-pr-flow/scripts/review-runtime.sh, kc-pr-flow/scripts/review-runtime.test.sh, kc-pr-flow/test/fixtures/review-runtime/valid-events.jsonl]
integration_owner: executer@2.2
steps: Add the named RED matrix; implement closed capability/decision validation plus `rehydrate-interactive`; keep replay/evidence validation authoritative; run GREEN and full REFACTOR checks; commit explicit paths.
done: DC-1 through DC-7, DC-9, and DC-11 pass; state scans and call logs prove no PR3 recovery or mutation surface.

### T2 — Consume typed authority at the existing interactive confirmation seam
task_id: T2
layer: L4
wave: W2
files: `kc-pr-flow/skills/kc-pr-review/SKILL.md`, `kc-pr-flow/scripts/review-shadow.test.sh`
skills_needed: [test, test-driven-development, write-docs]
reviewer_questions: Is the kill switch sampled before dispatch; do off/unset/unknown select legacy for only that fresh run; does enabled typed mode consume exactly T1 output, preserve mandatory confirmation, refuse in-run legacy fallback, and make no GitHub call before confirmation?
tdd_contract:
  red_command: "bash kc-pr-flow/scripts/review-shadow.test.sh --case typed-interactive-seam"
  expected_red_failure: "The review skill exposes only the shadow observer seam and has no executable typed/legacy selection, fail-closed typed confirmation input, or mode-parity contract."
  green_command: "bash kc-pr-flow/scripts/review-shadow.test.sh --case typed-interactive-seam"
  refactor_check: "bash -n kc-pr-flow/scripts/review-shadow.test.sh && bash kc-pr-flow/scripts/review-shadow.test.sh"
parallel_group: pr2-w2
depends_on: [T1]
owned_paths: [kc-pr-flow/skills/kc-pr-review/SKILL.md, kc-pr-flow/scripts/review-shadow.test.sh]
integration_owner: executer@2.2
steps: Freeze legacy/confirmation/mutation artifacts in RED; document and exercise one pre-run switch plus typed command consumption; run GREEN and parity REFACTOR checks; commit explicit paths.
done: DC-8 and DC-10 pass, typed failures render explicit gaps, blocker precedence survives, and legacy/typed paths both stop at human confirmation.

### T3 — Enforce recall-first promotion and the two efficiency branches
task_id: T3
layer: L7
wave: W2
files: `kc-pr-flow/scripts/review-runtime-benchmark.sh`, `kc-pr-flow/scripts/review-runtime-benchmark.test.sh`, `kc-pr-flow/test/fixtures/review-runtime/paired-runs.jsonl`
skills_needed: [test, test-driven-development, benchmark]
reviewer_questions: Does the scorer evaluate G1-G3 then zero-loss G4 before G5; does branch A require complete same-provider/scope reported pairs and median reduction at least 20%; does branch B measure only local terminal-receipt collator rehydration at no more than 60% with no token or remote claim?
tdd_contract:
  red_command: "bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh --case interactive-gates"
  expected_red_failure: "The paired scorer reports measurements but has no ordered promotion verdict, threshold boundaries, or terminal-rehydration efficiency branch."
  green_command: "bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh --case interactive-gates"
  refactor_check: "bash -n kc-pr-flow/scripts/review-runtime-benchmark.sh kc-pr-flow/scripts/review-runtime-benchmark.test.sh && bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh"
parallel_group: pr2-w2
depends_on: [T1]
owned_paths: [kc-pr-flow/scripts/review-runtime-benchmark.sh, kc-pr-flow/scripts/review-runtime-benchmark.test.sh, kc-pr-flow/test/fixtures/review-runtime/paired-runs.jsonl]
integration_owner: executer@2.2
steps: Add gate-order and threshold RED fixtures; derive deterministic promotion eligibility from bound observations; run GREEN, full corpus, and repeat-report REFACTOR checks; commit explicit paths.
done: DC-12 and DC-13 pass, zero expected must-fix loss is mandatory, and ineligible usage never becomes an efficiency claim.

### T4 — Synchronize canon, operator docs, and runtime CI
task_id: T4
layer: meta
wave: W3
files: `PRODUCT.md`, `ARCHITECTURE.md`, `kc-pr-flow/README.md`, `kc-pr-flow/CLAUDE.md`, `kc-pr-flow/reference/review-runtime.md`, `kc-pr-flow/docs/review-runtime.md`, `.github/workflows/review-runtime-tests.yml`
skills_needed: [write-docs, github-workflows]
reviewer_questions: Do all docs describe the same typed authority, terminal-only rehydration, human gate, empirical thresholds, and PR3 exclusions; does CI point at archived 2.1 evidence and validate the current 2.2 plan/ledger without stale paths?
TDD: skip -- canonical prose and workflow path wiring reuse T1-T3 behavior suites plus action/static validators.
parallel_group: serial
depends_on: [T2, T3]
owned_paths: [PRODUCT.md, ARCHITECTURE.md, kc-pr-flow/README.md, kc-pr-flow/CLAUDE.md, kc-pr-flow/reference/review-runtime.md, kc-pr-flow/docs/review-runtime.md, .github/workflows/review-runtime-tests.yml]
integration_owner: executer@2.2
steps: Update canon/plugin docs; repair every `docs/ship-flow/2.1-shadow-review-receipt` workflow reference to `_archive/2.1-shadow-review-receipt`; add 2.2 path filters and ledger validation; run all runtime suites, `actionlint`, YAML parse, stale-path scan, `git diff --check`, and final late-thread requery/global scans; commit explicit paths.
done: Canon and operator docs agree, CI has no live reference to the archived-away 2.1 path, all suites pass, and final exact-head review inventory is freshly re-queried.

## Context Manifest

- **Skills loaded**: ship-plan, ship-flow:test-driven-development, spacedock:ensign; superpowers:writing-plans unavailable in this worker runtime.
- **INVARIANTS sections read**: ship-plan Layer A/Layer B, TDD ledger, wave/parallel metadata, plan self-review, C15 line budget, hand-off contract.
- **Architecture docs consulted**: PRODUCT.md, ROADMAP.md, ARCHITECTURE.md, shape.md, design.md, kc-pr-flow/CLAUDE.md, archived 2.1 plan.
- **Domains touched**: schema with inherited generalist-marker; no specialist knowledge module claimed.
- **Lens dispatched**: event-saga lexical trigger returned 3 SKIP and 0 FLAG in the prior bounded plan attempt.
- **Lens findings integrated**: 0 integrated, 0 deferred, 0 ignored because every matched concern was SKIP.
- **Folder guidance**: files=`kc-pr-flow/**` -> folder_guidance_files=[kc-pr-flow/CLAUDE.md]; folder_guidance_skills=[]; codex_context_boundary=root AGENTS.md/CLAUDE.md intentionally excluded from folder_guidance_files.

## Plan Report

status: passed
stage_cost: one bounded recovery authoring pass over existing research
iterations: 1 self-review; prior research reviewer circuit breaker invoked with no contradiction
dimensions: 13/13 design constraints anchored; 4/4 atomic tasks; 3-wave DAG; disjoint W2 ownership; runnable verification; PR3 exclusions; canonical sync
reviewer_verdict: PROCEED under recovery circuit breaker
scope_anchoring: T1 maps Scope In typed authority/D5/rehydration; T2 maps confirmation/kill switch; T3 maps G4-G5; T4 maps durable sync and CI viability.
skill-coverage: PASS

### Metrics

status: passed
duration_minutes: 4
iteration_count: 1
task_count: 4
verification_spec_count: 13
model_split: recovery planner only; existing producer and lens receipts reused

### Hand-off to Execute
<!-- section:hand-off-to-execute -->
- **tdd-ledger**: `tdd-ledger.txt` and `tdd-ledger.jsonl`; validate with `validate-tdd-ledger.py --plan plan.md` and `--require-ledger-jsonl tdd-ledger.jsonl` before dispatch.
- **wave_order**: W1 T1 -> W2 (T2 || T3) -> W3 T4.
- **critical_assumptions**: 2.1 replay/evidence/safe-I/O primitives remain green; T2 and T3 write sets stay disjoint; terminal rehydration never appends; fresh GitHub thread/head inventory is re-queried after all changes.
- **architecture_context**: T4 updates PRODUCT/ARCHITECTURE and plugin/operator docs, repairs archived 2.1 CI paths, and leaves ROADMAP unchanged.
- **stub_flags**: none.
- **skills_needed_summary**: T1 runtime/security/test; T2 skill/docs/parity test; T3 benchmark/test; T4 docs/workflow; four distinct lists.
- **canonical_doc_actions_summary**: PRODUCT update from design; ARCHITECTURE update from design; ROADMAP skip because the parent row already owns this child.

| Task ID | Parallel group | Depends on | Owned paths | Integration owner |
|---|---|---|---|---|
| T1 | serial | - | runtime, runtime test, valid-events fixture | executer@2.2 |
| T2 | pr2-w2 | T1 | review skill, shadow test | executer@2.2 |
| T3 | pr2-w2 | T1 | benchmark, benchmark test, paired corpus | executer@2.2 |
| T4 | serial | T2,T3 | canon, plugin/operator docs, workflow | executer@2.2 |

| Task ID | Verify Lens | Reviewer Question | Affected Path Family | Required Skills | Evidence Required |
|---|---|---|---|---|---|
| T1 | schema/security/silent | Can invalid, silent, or mismatched state govern approval or persist raw content? | runtime/test/fixture | test, TDD, best-practices, security | RED/GREEN mutation matrix, forbidden-content and no-append logs |
| T2 | interaction/parity | Can switch timing bypass typed failure or human confirmation? | skill/shadow test | test, TDD, write-docs | frozen artifacts, confirmation count, empty mutation log |
| T3 | benchmark/adversarial | Can later/weak evidence repair recall or admit an ineligible efficiency claim? | scorer/test/corpus | test, TDD, benchmark | ordered verdict fixtures, boundary probes, repeat-report diff |
| T4 | documentation/workflow | Can docs or CI imply PR3 or reference stale 2.1 locations? | canon/docs/workflow | write-docs, github-workflows | cold-read scan, actionlint/YAML, global stale-path and late-thread scans |

<!-- section:context-routing-manifest -->
```yaml
context-routing-manifest:
  domain_matches: [schema]
  knowledge_modules: []
  required_skills: []
  stage_hints: {plan: [generalist-marker]}
  consumer_obligations: [preserve D1-D7, enforce D5 interactively, keep D6 and recovery in PR3, query exact head and late threads before merge]
  future_provider_boundary: "Provider hints are non-authoritative; the local registry remains canonical."
```
<!-- /section:context-routing-manifest -->

## Context Routing Receipt

The inherited schema/generalist marker maps T1-T3 to their contract questions and evidence rows; T4 owns canonical/CI synchronization. No unavailable specialist module is claimed.
<!-- /section:hand-off-to-execute -->
<!-- /section:plan-report -->
