# Product Contracts

This document records durable product outcomes for repository capabilities. It is written for contributors who need to change a capability without rediscovering its purpose from implementation details.

## Repository plugin catalog

This monorepo publishes seven plugins through the `kc-claude-plugins`
marketplace (`.claude-plugin/marketplace.json`). Each entry states the
outcome the plugin exists to deliver and who it serves; full skill lists
live in each plugin's own `README.md`. `kc-pr-flow`'s agent-native review
runtime has its own deep-dive entry below this catalog.

- **`e2e-pipeline`** — Map, generate, verify, and run browser/CLI E2E flows
  without hand-maintained selectors, with an LLM-judgment fallback when
  compiled matching can't resolve a step. Serves teams testing a web app
  end-to-end who need both a fast CI-friendly compiled path and
  human-in-the-loop exploration.
- **`kc-plugin-forge`** — One command validates plugin structure, TDD-tests
  skills under pressure, audits `SKILL.md` frontmatter, and smoke-tests in
  an isolated profile before publish. Serves plugin authors in this
  monorepo who want automated quality assurance instead of manual review.
- **`kc-nightwatch`** — Autonomous nightly cycle that runs forge
  validation, harvests improvement signals from journal/Sentry/E2E/git,
  and proposes north-star-aligned changes. Serves maintainers who want
  continuous quality monitoring without manually triggering it.
- **`kc-hyperfocus`** — Detects context pressure, enforces session
  handoff/resume, and caches codebase insight in a local SQLite lake so
  agents don't re-explore from zero. Serves agents (and their operators)
  running long or multi-session work that needs durable cross-session
  context.
- **`kc-team-ops`** — EM triage with a strategic lens, project pulse
  updates, issue decomposition, and structured Linear management, plus an
  on-demand cross-model second opinion via Gemini/`agy`. Serves
  engineering managers running Linear-based triage and reporting.
- **`kc-pr-flow`** — End-to-end PR lifecycle (create → review → resolve →
  announce) with tiered multi-agent review. Serves contributors who want a
  one-command PR workflow with consistent review quality across model
  providers. Its agent-native review runtime is detailed in the dedicated
  entry below.
- **`kc-dev-flow`** — Portable authority and evidence kernel that adopts an
  existing repository's tracker, sprint model, workflow runtime, and delivery
  provider, then continues approved sprint work without unnecessary captain
  pauses. Serves teams that need one lean workflow across Claude Code and Codex
  without duplicating repository truth.

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

`KC_PR_FLOW_REVIEW_TYPED=on` is sampled once before dispatch. Only that exact value selects typed authority for the fresh invocation; unset, off, and unknown values retain the legacy path. A valid closed decision remains primary authority. Invalid decision production without a valid independently confirmed exact-identity `confirmed-blocker-evidence/v1` receipt fails closed to COMMENT rather than silently switching to legacy behavior; a valid receipt preserves REQUEST_CHANGES, while evidence inconsistent with a valid decision invalidates the whole typed confirmation. Neither mode bypasses confirmation or posts to GitHub.

Terminal rehydration validates the complete lifecycle, exact repository/PR/base/head/config/run identity, and every evidence pointer and content hash before rebuilding the decision in memory. It never appends, resumes, repairs, recovers locks, retains state, authorizes a payload, or contacts a remote service. The safe-I/O and metadata-only quarantine contracts from the shadow increment remain in force.

The paired scorer evaluates promotion in fixed G1–G5 order: valid bound inputs, complete required capability coverage, external behavior parity, zero lost expected must-fix findings, then one of the two efficiency branches above. Later efficiency evidence cannot repair an earlier safety or recall failure. A local-cost pair must pre-bind the raw terminal artifact, recomputed decision, and a captured designed-full-rerun control receipt. The executable producer invokes only fresh terminal collation, applies `canonical-artifact-bytes/v1` to the decision and the control's bound sanitized full-review artifact, and records zero model and remote calls. The scorer rechecks that complete binding; a caller-resealed number or self-hash is not evidence.

Increment 2.3 remains the owner of crash-safe lock recovery and PID-reuse handling, verified predecessor lineage, append/compaction performance, resume and retention, once-only posting, remote reconciliation, and daemon mutation.

### Non-goals

- Rewriting reviewer intelligence or prompts before the runtime contract is measurable.
- Persisting full diffs, prompts, evidence excerpts, or raw provider output.
- Adding a server, database, dashboard, or MCP service for local review state.
- Removing the human confirmation gate from interactive review.
- Enabling daemon auto-approval or auto-merge.
