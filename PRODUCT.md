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

### Non-goals

- Rewriting reviewer intelligence or prompts before the runtime contract is measurable.
- Persisting full diffs, prompts, evidence excerpts, or raw provider output.
- Adding a server, database, dashboard, or MCP service for local review state.
- Removing the human confirmation gate from interactive review.
- Enabling daemon auto-approval or auto-merge.
