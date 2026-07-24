# Typed interactive lifecycle — Shape Projection

> Compatibility normalization only. This child was shaped under an older Ship-Flow contract. The confirmed product direction, captain articulation, and Captain Bet are inherited verbatim from `../2-agent-native-pr-review-runtime/shape.md`; D1-D7 and PR ownership are inherited from `../2-agent-native-pr-review-runtime/design.md`. No new captain articulation or product bet is introduced here.

## Shape Output

### Captain Articulation Trail (verbatim parent reuse)

1. **Desired outcome** — captain: “我的目標是，讓 PR toolkit 更 agent-native 以便 token 使用更有效率，跨 llm 表現更好，PR review 結果更穩定。”
2. **Delivery shape** — captain: “我想讓你切三個 PR分三個階段，讓整個 toolkit 更 agent-native，更有效率，更穩定。”
3. **Runtime direction** — captain confirmed Bash + `jq` + JSONL, machine-local XDG state, exact-head rehydration, and no full diff/prompt/raw-output persistence.
4. **Failure policy** — captain confirmed retry-first; unresolved required coverage forbids APPROVE and defaults to an explicit COMMENT gap.
5. **Posting authority** — captain confirmed interactive human authorization and daemon posting only under explicit preauthorization plus typed/head/idempotency gates.

### Captain Bet (inherited from parent gate approval 2026-07-22)

> 我的目標是，讓 PR toolkit 更 agent-native 以便 token 使用更有效率，跨 llm 表現更好，PR review 結果更穩定

### Problem

The captain's stated goal is more efficient, cross-model-stable PR review. Child 2.1 made the exact-head lifecycle observable, but interactive coverage, verdict, and confirmation still derive from transient prose. Without this child, typed evidence cannot safely govern the interactive decision and a required lane failure can still depend on model interpretation rather than the confirmed failure policy.

### Acceptance Outcome

On one unchanged PR head, an interactive reviewer derives coverage, verdict eligibility, and confirmation input from validated typed state. A required gap can never produce APPROVE, confirmed blockers still produce REQUEST_CHANGES, human confirmation remains mandatory, and a pre-run kill switch selects the legacy path for a fresh run. Promotion requires non-inferior must-fix recall before any stability or efficiency claim.

### Outcome Card

#### Will get

- **W1 — Typed interactive authority:** When a review reaches collation, the interactive reviewer can derive coverage, verdict eligibility, and confirmation input from exact-head typed state. (Check: G1-G3)
- **W2 — Fail-closed coverage:** When required coverage fails after one retry and typed manual fallback, the reviewer can see an explicit incomplete-coverage COMMENT ceiling while confirmed blockers remain REQUEST_CHANGES. (Check: G2)
- **W3 — Evidence-gated rollout:** When the typed path is considered for default use, the maintainer can compare recall first and only then claim lower reported usage or bounded local rehydration cost, otherwise retaining the legacy path. (Check: G4-G5)

#### Won't get

- PR3 resume, posting authorization, pending-payload, remote-marker, reconciliation, or idempotency behavior.
- Daemon mutation, daemon APPROVE, auto-merge, or migration of `kc-pr-review-resolve`.
- Reviewer-intelligence, lane-selection, model-routing, synthesis-policy, or prompt redesign.
- A service, database, dashboard, MCP runtime, or durable full diffs, prompts, excerpts, or raw provider output.

#### Why this scope

The three-day boundary spends the existing 2.1 foundation on one reversible interactive behavior change. Remote side effects remain isolated in 2.3, and reviewer-intelligence work remains rejected because neither is needed to prove typed lifecycle value.

## Appetite and Boundary Proof

Appetite: **3 working days**, preserving the parent allocation.

Child 2.1 is already merged and verified at exact head, with runtime `279/0`, shadow `155/0`, benchmark `135/0`, five successful exact-head CI checks, and no unresolved blocking finding. Therefore 2.2 consumes the existing D1-D4/D7 event, replay, exact-head evidence, usage, and benchmark foundation rather than rebuilding it.

| Bounded work | Budget |
|---|---:|
| Typed collator authority for interactive coverage, verdict eligibility, and confirmation input | 0.8 day |
| D5 retry, manual-fallback, COMMENT-ceiling, and blocker-precedence enforcement | 0.6 day |
| Exact-head rehydration at the interactive seam | 0.4 day |
| Human-confirmation preservation plus kill-switch/legacy parity | 0.3 day |
| Paired empirical gates and focused verification | 0.3 day |
| **Planned** | **2.4 days** |
| **Headroom** | **0.6 day (20%)** |

The cut is sufficient because every row terminates at the interactive confirmation boundary. D1 retention/GC completion and D6 mutation/reconciliation are owned by 2.3; prompt or reviewer-intelligence changes are not prerequisites.

## Scope In

- Make validated typed lifecycle state the interactive collator source of truth for coverage, verdict eligibility, and confirmation input.
- Enforce parent D5 exactly: capability-based requiredness; typed terminal evidence from an adapter or explicit manual fallback; one retry for required transient failures; incomplete required coverage forbids APPROVE and yields an explicit COMMENT ceiling; confirmed blockers remain REQUEST_CHANGES; optional-provider failures remain evidence only.
- Rehydrate evidence only for the same exact repository, PR, base, head, and review identity before it can govern the interactive decision.
- Preserve mandatory human confirmation.
- Provide one pre-run operator kill switch: disabled selects the legacy path for a fresh run. Once typed authority starts, invalid or incomplete typed state remains subject to D5's COMMENT ceiling and blocker precedence; it cannot silently fall through to legacy APPROVE.
- Evaluate the paired fixed-head corpus in gate order: recall, coverage/verdict safety, then comparable reported usage or bounded local exact-head interrupted rehydration cost.

## Scope Out

- All 2.3 ownership: compatible interrupted-run resume, retention and garbage collection, authorization hashing, posting intent, pending payloads, idempotency keys, GitHub mutation, ambiguous-result reconciliation, remote receipts or markers, and daemon preauthorization.
- Reviewer-intelligence, prompt, lane-selection, model-routing, or finding-synthesis redesign.
- `kc-pr-review-resolve`, auto-merge, daemon APPROVE, or removal of the interactive human confirmation gate.
- A server, database, dashboard, MCP service, shared remote state, or full raw-content persistence.
- New schema direction, provider-specific lifecycle authority, or a changed parent Captain Bet.

## Empirical Gates

| Gate | Passing evidence | Failure effect |
|---|---|---|
| **G0 — Dependency** | The merged 2.1 receipt, exact-head rehydration, and authority-bound paired scorer remain green. | Do not activate typed authority. |
| **G1 — Exact head** | Every governing receipt and evidence pointer validates against the current repository, PR, base, head, and review identity. | End the typed attempt as an explicit incomplete-coverage COMMENT, preserving REQUEST_CHANGES for confirmed blockers. A fresh legacy rerun requires a new explicit operator choice. |
| **G2 — Coverage/verdict safety** | Every required capability has typed terminal evidence after at most one retry and, when needed, explicit manual fallback; remaining gaps force `coverage=incomplete`, `approve_eligible=false`, and COMMENT, while confirmed blockers retain REQUEST_CHANGES. | Block default promotion. |
| **G3 — Human/rollback parity** | Before dispatch, the operator selects typed or legacy mode; either path reaches mandatory human confirmation. Typed-mode failure cannot change modes in-run or restore APPROVE eligibility. Disabling typed mode affects only a fresh run. | Keep the typed path off for subsequent runs; the current typed run remains D5-governed. |
| **G4 — Recall first** | On the sanitized fixed-head paired corpus, typed-path must-fix recall is non-inferior to the legacy baseline; no expected must-fix finding recovered by legacy is lost. | Stop; stability and efficiency results cannot authorize promotion. |
| **G5 — Efficiency second** | After G4 passes, either (a) paired observations with the same provider family and measurement scope and `reported` provenance show at least 20% median token reduction, or (b) a fresh interactive invocation validates one already-terminal exact-head receipt and reconstructs only its collator coverage/verdict/confirmation input at a cost no greater than 60% of a full review rerun. Missing, estimated, cross-provider, or cross-scope usage is ineligible and never coerced to zero. | Make no efficiency claim and retain the legacy path. |

The 60% alternative is rehydration-only: it reads a replay-valid terminal receipt for the same exact-head review identity and reconstructs collator input. It cannot continue an incomplete lifecycle, resume a lane, reuse an interrupted `run_id`, append recovery events, recover locks or predecessors, manage retention, or touch pending/remote mutation state. Those behaviors, ambiguous-result recovery, at-most-once posting, and idempotency remain 2.3 ownership.

## Assumptions

### A1 — Critical

- **Claim:** The 2.1 authority-bound paired corpus can detect loss of its expected must-fix findings before typed interactive promotion.
- **Confidence at shape:** 95/100.
- **Verified by:** `design-contract` — `docs/ship-flow/_archive/2.1-shadow-review-receipt/verify.md` records benchmark `135/0`, authority binding, exact-head CI, and no unresolved blocker.
- **Failure consequence:** Keep typed authority off; usage or stability evidence cannot override recall loss.

### A2 — Important

- **Claim:** Parent D5 fully fixes the product semantics needed for coverage and verdict enforcement without reviewer-intelligence or prompt changes.
- **Confidence at shape:** 90/100.
- **Verified by:** `design-contract` — parent D5 and PR boundary ownership assign enforcement to 2.2 and remote mutation to 2.3.

### A3 — Important

- **Claim:** The interactive slice fits 2.4 planned days because 2.1 already supplies D1-D4/D7 runtime, validation, exact-head, usage, and benchmark foundations.
- **Confidence at shape:** 85/100.
- **Verified by:** `codebase-grep` — dependency verify evidence plus the bounded budget above.

## Pre-mortem

- **Category:** `wrong-dcs`
- **Projection:** A lower-token typed run could pass structural coverage while silently missing must-fix findings that the legacy baseline caught.
- **Mitigation:** G4 blocks stability and efficiency claims until must-fix recall is non-inferior.

## Canonical Context

- `PRODUCT.md` already records recall-first evaluation, typed interactive delivery, human control, and the 2.3 posting boundary. Compatibility normalization introduces no new product impact.
- `ARCHITECTURE.md` already records D2-D5/D7, exact-head authority, typed fallback, and increment ownership. Compatibility normalization introduces no new architecture decision.
- `ROADMAP.md` already carries the confirmed parent pitch and rejected alternatives. No roadmap, product, architecture, README, parent, sibling, or code edit belongs to this phase.
- Recent debrief guidance warns that a late unresolved review thread can appear after an earlier inventory. That remains existing final merge-gate ownership; G1 proves exact-head typed evidence only and does not claim thread reconciliation.

## Domain Registry Validation

- `classify`: `bash "${CLAUDE_PLUGIN_ROOT:-plugins/ship-flow}/lib/registry-resolve.sh" --classify docs/ship-flow/2.2-typed-interactive-lifecycle/shape.md`
- `validate`: `bash "${CLAUDE_PLUGIN_ROOT:-plugins/ship-flow}/lib/registry-resolve.sh" --validate --domain=schema`
- `domain`: `schema`
- `affects_ui`: `false`
- `design_required`: `true`
- `contract_decision_required`: `false`
- `registry_status`: `knowledge_module_missing`
- `resolution`: inherited captain-selected `generalist-marker` from the parent design; do not claim schema-specialist grounding.
- `result`: `proceed`

### Hand-off to Design

- `ui_surfaces`: `[]`
- `open_design_questions`: `[]`
- `open_contract_decisions`: `[]`
- `unresolved_product_direction`: `[]`
- `pm_framing_output`: parent `docs/ship-flow/2-agent-native-pr-review-runtime/shape.md` PM receipts and confirmed articulation.
- `domain`: `schema` with inherited `generalist-marker` routing.
- `design_required`: `true` because this is a non-UI contract-bearing authority change.
- `contract_decision_required`: `false` because parent D1-D7 resolved the semantics and parent design hands off `open_decisions: []`.

Design must project, not reopen, these inherited contracts:

1. **D2/D3/D7:** accepted typed state is replay-valid and exact-head/evidence-bound; invalid or unsupported state cannot govern the interactive decision.
2. **D4:** usage remains `reported | estimated | unavailable`; only comparable same-provider/scope `reported` values satisfy G5's token branch, while its alternative branch measures only local exact-head rehydration cost.
3. **D5 (verbatim parent decision):** “Define requiredness by review capability rather than provider name, require typed terminal coverage with evidence from either an adapter or explicit manual fallback, retry required transient failures once, forbid APPROVE when required coverage remains incomplete, default such runs to an explicit COMMENT gap, preserve REQUEST_CHANGES for confirmed blockers, and keep optional-provider failures as evidence only.”
4. **PR boundary:** design the interactive transition/precedence table, fallback evidence contract, kill-switch behavior, and G1-G5 acceptance mapping without introducing D6 posting/idempotency or reviewer/prompt semantics. The transition table must distinguish pre-run legacy selection from in-run typed failure, which remains D5-governed, and must define the 60% branch as terminal-receipt collator-input reconstruction with every incomplete-run/recovery operation forbidden. The resulting `design.md` must leave plan no semantic choice among alternate coverage, verdict, usage, or boundary behaviors.

## Sharp Report

status: passed
stage_cost: not metered (one fresh L0 reader plus one fresh read-only adversarial reviewer)
path: sharp-only
reviewer_verdict: PROCEED after one bounded VETO correction cycle

### Metrics

status: passed
duration_minutes: 15
iteration_count: 0
path: sharp-only
open_contract_decisions_count: 0
domain_matches_count: 1

## Stage Report: shape

- DONE: Normalize the existing shaped-child into a child-local shape artifact without changing the confirmed parent pitch or asking the captain to restate it.
  The compatibility projection reuses the parent articulation and Captain Bet verbatim and introduces no captain Q-loop.
- DONE: Prove the three-day boundary is sufficient and explicitly exclude PR3 posting/idempotency plus reviewer-intelligence or prompt redesign.
  The 2.4-day bounded budget retains 20% headroom and the Scope Out/PR boundary leaves remote mutation and reviewer behavior outside 2.2.
- DONE: Emit a contract-bearing Hand-off to Design grounded in parent D5, with empirical recall/usage gates and no unresolved product-direction question.
  The hand-off fixes D5 semantics, orders G4 recall before G5 reported-usage or terminal-receipt rehydration evidence, and records empty product/design decision lists.

### Summary

This compatibility pass converts the older shaped child into the current child-local shape contract while preserving its confirmed three-PR bet. It advances a non-UI schema contract lane to full design with inherited decisions, explicit empirical gates, and no scope drift into 2.3.
