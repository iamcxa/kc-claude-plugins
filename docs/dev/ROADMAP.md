# kc-pr-flow Development Roadmap

This document records sprint plans, strategy shifts, and sprint boundaries for kc-pr-flow development. Each sprint is sequenced to respect file collision constraints (split-root worktree discipline: entities editing the same file cannot run in parallel) and blocking dependencies between entities.

## Sprint: prescan-review-consolidation (2026-07-26 to ~2026-08-09)

**Completed in Prior Session:**
- Entity `sv` (reconcile-degraded-mode-symmetry) — merged PR #63, archive/ledger recorded

**This Sprint: 5 Entities**

### Phase 1: Prerequisite (Non-Parallel)
**Entity:** prescan-coverage-honesty (id: 2tpagghhkaqzfkq4wvs7f1nh)
- **Purpose:** Wire typed-runtime payload shape for pre-scan reporting. Prerequisite for Phase 3.
- **Impact:** Enables invisible-skip detection; unblocks two follow-on entities.
- **Size:** Medium (3-4 AC)
- **Files:** `skills/kc-pr-review/SKILL.md` (Step 4.5), `scripts/review-runtime.sh`, `reference/review-runtime.md`
- **Risk:** Payload schema locked in after this lands — Phase 3 entities depend on final shape.

### Phase 2: Defect-Lane Parallelization (3 Entities Run in Parallel)
**Entity:** review-post-suite-cost (id: qhr529c1ha214hbef794dm6v)
- **Purpose:** Cut python3 overhead (565ms per launch × 65 per operation = 6-7 min per job). CI cap hit on recent commits.
- **Impact:** Buys back ~6 minutes of CI headroom. Helps all future test-heavy PRs.
- **Size:** Small (measured root cause, mechanical fix)
- **Files:** `scripts/review-post.sh`, `.github/workflows/review-runtime-tests.yml`
- **Defect-lane eligible:** YES (root cause identified with measurements, mechanical AC, single seam)
- **Risk:** Low (runtime performance improvement, fail-safe direction)

**Entity:** reconcile-list-element-shape (id: 11785c6he7dv034qb970tqm0)
- **Purpose:** Restore jq type-safety boundary in list reconciliation.
- **Impact:** Prevents silent data shape divergence in daemon-posting edge cases.
- **Size:** Small (identified seam, 1-2 AC)
- **Files:** `kc-pr-flow/scripts/review-post.sh`
- **Defect-lane eligible:** YES (root cause identified, mechanical AC, single seam)
- **Risk:** Low (jq type-check hardening, fail-safe)

**Entity:** gh-list-adapter-pagination (id: n9xjhpeza7q0hk3sepc6rxhc)
- **Purpose:** Remove silent pagination failures in gh CLI adapter.
- **Impact:** Gh-based queries now fail overtly if pagination misbehaves, not silently drop rows.
- **Size:** Small (root cause known, needs test fixture)
- **Files:** `scripts/gh-list-adapter.sh`, `.github/workflows/review-runtime-tests.yml` (new gh fixture)
- **Defect-lane eligible:** YES (root cause identified, mechanical AC, single seam)
- **Risk:** Low (failure-mode hardening, gh-specific test harness)

**Parallelization note:** All three defect-lane entities touch `scripts/review-post.sh` but at different semantic boundaries (post-cost is performance, reconcile is data shape, pagination is adapter behavior). Verify git diff segments to confirm no line-level collision; if none, safe to parallelize.

### Phase 3: Implementation Follow-On (Sequential, Blocks Next Sprint)
**Entity:** learned-pattern-selection (id: v52dgtngxnthwah7tvbeawsz)
- **Purpose:** Add trigger metadata index to 104 learned patterns; select by relevance instead of reading all.
- **Impact:** ~50% context reduction on typical reviews (measured in cross-vendor pass).
- **Size:** Medium (3-4 AC including migration)
- **Files:** `reference/learned-patterns.md`, `skills/kc-pr-review/SKILL.md` (Step 8), `skills/kc-pr-review-resolve/SKILL.md`
- **Blocking:** Must sequence AFTER prescan-coverage-honesty (different sections of SKILL.md, but payload shape dependency)
- **Risk:** Medium (index schema is a new construct; fallback to whole-file read on index corruption)
- **Gates to next:** learned-pattern-append-bound cannot start until metadata schema is stable

**Sequencing rationale:** prescan-coverage-honesty lands first to set payload shape. Then 3 defect-lane entities run in parallel (no SKILL.md collision). Then learned-pattern-selection can safely modify Step 8 of SKILL.md without conflicting with Phase 1's Step 4.5 changes.

## Future Sprint Slate (Out of This Sprint)

**Held for Design Decision (attended-pr-review-wait, 4p):**
- once-only-daemon-preauth-gate (slice 2 of daemon arc) — ceiling source location TBD by captain
- daemon-preauth-freshness-coverage (slice 3, depends on slice 2)

**Blocked by learned-pattern-selection Stability:**
- learned-pattern-append-bound — depends on selection's metadata schema, implements write-side dedup

**Blocked by prescan-coverage-honesty Shape:**
- reviewer-return-contract — inherits finding representation from prescan payload
- review-citation-verifier — depends on return-contract finding model

**Post-Implementation (Measurement/Verification Tasks):**
- benchmark-full-rerun-control — token-savings measurement (currently unproven replay vs. full re-run)
- cross-model-arbitration-e2e — E2E proof of arbitration wiring (path has never reached verdict end-to-end)
- executable-diff-coverage-ratchet — open question: worth building vs. adversarial spot-check?
- corpus-fixture-for-reproducible-acs — open question: fixture fidelity vs. simplicity trade-off

**Low-Priority Independent (Typically Deferred):**
- once-only-retention-sweeper — mechanical boundary for state retention window
- pr-merge-audit-link-split-root — split-root workflow audit link
- structural-check-hardening — minor validation improvements

## Sprint Strategy Notes

**File Collision Enforcement:**
- `skills/kc-pr-review/SKILL.md` is the hottest file. Edits segment by step (4.5, 8, etc.) but occupy same file. Sequential ordering of prescan → learned-pattern maintains isolation.
- `reference/learned-patterns.md` has a chain: selection (read-side index) → append-bound (write-side dedup). Must sequence sequentially.
- Defect-lane parallelization in Phase 2 requires git diff inspection before concurrent worktree dispatch.

**Defect-Lane Criteria (All 3 Phase-2 Entities Meet All 4):**
1. Root cause identified in current codebase (measured, not speculative)
2. AC are mechanical and single-seam (no scattered refactor)
3. No design decision pending (shape/strategy fixed)
4. Bounded scope (fix doesn't cascade into adjacent areas)

**Baseline Measurement Requirement:**
All entities touching `skills/kc-pr-review/SKILL.md` must re-measure suite baseline before starting. Main has moved past the 920/0 baseline recorded 2026-07-26 following PR #60, #61 merges. Use CI's pinned ShellCheck v0.9.0 (lint parity commands in `kc-pr-flow/CLAUDE.md`).

**Known Risks:**
- Daemon arc (Phase 4) may face scope change if captain's 4p decision favors removing unattended-caller path entirely.
- Measurement tasks (benchmark-control, cross-model-e2e) produce proof only; do not count as implementation velocity.
