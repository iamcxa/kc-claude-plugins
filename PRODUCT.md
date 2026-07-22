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
4. Efficiency claims use only comparable, provider-reported usage from the same provider family and measurement scope. Missing usage is unknown, never zero.
5. Interrupted and ambiguous runs recover without stale-head reuse or duplicate posting.

No numeric improvement threshold is implied until the paired-run corpus provides a trustworthy baseline.

### Delivery boundary

The capability ships in three reversible increments:

1. A shadow receipt and paired-run baseline, with no behavioral authority.
2. A typed interactive lifecycle, guarded by recall and fallback gates.
3. Safe resume and once-only posting, with daemon mutation defaulting to deny.

The first increment must not change verdict selection, user confirmation, or GitHub mutation behavior. The daemon must not issue an approval in the initial runtime.

### Current increment

The shadow increment provides an off-by-default, fail-open observer over a local typed exact-head event log. Maintainers can validate, replay, summarize, and compare sanitized paired receipts across provider-neutral lanes. The paired report puts expected-finding recall first, then capability coverage, external behavior parity, stability/disagreement, and strictly comparable provider-reported usage.

The observer accepts one closed `ShadowObservation/v1` (`kc-pr-flow.shadow-observation/v1`) projection after legacy collation. A complete observation records every declared lane, evidence-bound candidates and findings, synthesis, six hashes of the frozen legacy behavior, and a terminal run event. Unknown fields and raw values cannot enter accepted state: same-major extensions are closed hash-only metadata, and rejected append input creates a metadata-only quarantine record containing its reason, hash, byte count, and timestamp rather than the rejected bytes.

The receipt runtime's event, observation, pointer, and usage file ingestion uses a Python 3.8+ fail-closed safe-I/O boundary before parsing: one no-follow regular-file descriptor, a bounded read, stable pre/post file identity, and a new private mode-0600 snapshot. Missing support, path replacement, concurrent mutation, or oversize input cannot mutate accepted state. The production observer remains fail open only with respect to the legacy review: it reports a typed non-observation and the byte-identical legacy flow continues.

The paired scorer accepts only closed serialized corpus records whose exact-head review key, candidate/evidence identities, receipt content hash, and receipt ID recompute successfully. Recall is therefore measured from bound evidence rather than unverified labels. This increment is measurement infrastructure, not an adaptive reviewer. It does not change lane selection, model routing, finding synthesis authority, the confirmation gate, or GitHub output. Disabling the gate stops new observation while preserving existing receipts for inspection and comparison.

Increment 2.3 remains the owner of crash-safe lock recovery and PID-reuse handling, verified predecessor lineage, append/compaction performance, resume and retention, once-only posting, remote reconciliation, and daemon mutation. None of those capabilities are implied by the shadow receipt.

### Non-goals

- Rewriting reviewer intelligence or prompts before the runtime contract is measurable.
- Persisting full diffs, prompts, evidence excerpts, or raw provider output.
- Adding a server, database, dashboard, or MCP service for local review state.
- Removing the human confirmation gate from interactive review.
- Enabling daemon auto-approval or auto-merge.
