# Product Contracts

This document records durable product outcomes for repository capabilities. It is written for contributors who need to change a capability without rediscovering its purpose from implementation details.

## kc-pr-flow: Agent-native PR review

### Outcome

PR review should use model context efficiently, behave consistently across supported model providers, and produce stable review results without weakening must-fix recall or human control.

### Who it serves

- Reviewers who need an evidence-backed result tied to the exact PR head.
- Maintainers who need to inspect, compare, resume, and safely retire review runs.
- Teams that use different model providers but expect the same lifecycle and safety rules.

### Target capabilities

- Emit a compact, validatable receipt for each exact-head review run.
- Represent provider work, findings, evidence, coverage, and usage with typed provider-neutral contracts.
- Rehydrate evidence from source pointers instead of retaining full diffs, prompts, or raw model output.
- Make incomplete required coverage explicit and ineligible for approval.
- Resume compatible interrupted work while invalidating stale heads, configurations, and authorizations.
- Post an approved payload at most once and preserve enough evidence to reconcile an ambiguous remote result.

### Success measures

Measures are evaluated in this order:

1. Must-fix finding recall is non-inferior to the legacy review flow.
2. Shadow mode preserves the legacy verdict, confirmation, and GitHub output exactly.
3. Repeated equivalent runs produce compatible coverage and finding identities, with disagreements remaining visible.
4. Efficiency claims require either a median provider-reported token reduction of at least 20% across complete same-provider/scope pairs, or a median local terminal-receipt collation cost no greater than 60% of a full review rerun. Missing or unbound measurements are unknown, never zero.
5. Interrupted and ambiguous runs recover without stale-head reuse or duplicate posting.

### Delivery boundary

The capability ships in three reversible increments:

1. A shadow receipt and paired-run baseline, with no behavioral authority.
2. A typed interactive lifecycle, guarded by recall and fallback gates.
3. Safe resume and once-only posting, with daemon mutation defaulting to deny.

The first increment must not change verdict selection, user confirmation, or GitHub mutation behavior. The daemon must not issue an approval in the initial runtime.

### Current increment

The typed interactive increment derives one closed `InteractiveCollationDecision/v1` from a complete, exact-identity terminal receipt. Capability terminal state—not provider silence—now governs coverage, approval eligibility, effective-event precedence, and the input shown at the existing human confirmation gate. Required gaps impose a COMMENT ceiling, while confirmed blockers still produce REQUEST_CHANGES. A required transient failure receives exactly one retry and then an evidence-bound manual fallback opportunity.

`KC_PR_FLOW_REVIEW_TYPED=on` is sampled once before dispatch. Only that exact value selects typed authority for the fresh invocation; unset, off, and unknown values retain the legacy path. An enabled typed run that is invalid, incomplete, stale, or unsupported fails closed to an explicit COMMENT decision for that invocation rather than silently switching to legacy behavior. Neither mode bypasses confirmation or posts to GitHub.

Terminal rehydration validates the complete lifecycle, exact repository/PR/base/head/config/run identity, and every evidence pointer and content hash before rebuilding the decision in memory. It never appends, resumes, repairs, recovers locks, retains state, authorizes a payload, or contacts a remote service. The safe-I/O and metadata-only quarantine contracts from the shadow increment remain in force.

The paired scorer evaluates promotion in fixed G1–G5 order: valid bound inputs, complete required capability coverage, external behavior parity, zero lost expected must-fix findings, then one of the two efficiency branches above. Later efficiency evidence cannot repair an earlier safety or recall failure. Local-cost observations must bind a recomputed closed decision to the exact terminal receipt and explicitly prove a fresh collator-only invocation with zero model and remote calls.

Increment 2.3 remains the owner of crash-safe lock recovery and PID-reuse handling, verified predecessor lineage, append/compaction performance, resume and retention, once-only posting, remote reconciliation, and daemon mutation.

### Non-goals

- Rewriting reviewer intelligence or prompts before the runtime contract is measurable.
- Persisting full diffs, prompts, evidence excerpts, or raw provider output.
- Adding a server, database, dashboard, or MCP service for local review state.
- Removing the human confirmation gate from interactive review.
- Enabling daemon auto-approval or auto-merge.
