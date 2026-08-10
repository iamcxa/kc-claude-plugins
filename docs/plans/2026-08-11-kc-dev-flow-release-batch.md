# KC Dev Flow Release Batch Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Validate the published Science Officer runtime, halve the accepted-work-to-first-integrated-slice delay, reduce the local workflow README to 700 lines, and pilot bounded subtraction before one kc-dev-flow release.

**Architecture:** Preserve the existing Spacedock work-item, iteration, and delivery authorities. Run the v2.1.0 smoke as a one-off exact-tag experiment before adding any persistent harness; make one fresh EM the only required judgment seat at ideation and validation; split always-loaded authority from trigger-loaded recovery and validation detail; then require non-trivial brownfield additions to survive a bounded without-it challenge. Keep each work item and logical change independently reviewable even when they share the release batch.

**Ideation EM ruling:** `narrow / high`. Treat the completed v2.1.0 experiment as the decision receipt, retain one release-closeout dual-host smoke rather than a per-PR matrix, make multi-model review optional, and delete repeated README prose instead of relocating it. The captain's earlier instruction still controls delivery: finish the batch before opening a PR.

**Tech Stack:** Markdown workflow contracts, Claude Code and Codex plugin CLIs, Python contract tests, Bash verification scripts, Spacedock split-root state.

### Task 1: Schedule the accepted batch

**Files:**
- Modify: `docs/dev/ROADMAP.md`
- Modify through Spacedock state authority: `docs/dev/.spacedock-state/kc-dev-flow-published-tag-smoke-review.md`
- Modify through Spacedock state authority: `docs/dev/.spacedock-state/halve-dev-flow-cycle-time.md`
- Modify through Spacedock state authority: `docs/dev/.spacedock-state/workflow-readme-runtime-budget.md`

1. Add `kc-dev-flow/S1` with the smoke review before cycle-time work.
2. Add `repo-platform/S1` with the README budget dependent on `kc-dev-flow/S1`.
3. Set the three task `sprint` fields through `spacedock status --set` and commit each transaction root explicitly.
4. Run product-filtered `spacedock status` and verify the recorded order and fields.

### Task 2: Review the published-tag smoke before retaining a harness

**Files:**
- Create: `scripts/kc-dev-flow-published-tag-smoke.py`
- Modify: `scripts/kc-dev-flow-contract-test.py`
- Modify: `CLAUDE.md`

1. Preserve the completed v2.1.0 receipt at commit `a024b254e236f521d8438d567ade36d779a52d11`: both hosts installed and invoked; existing marketplace verification did not cover exact tags, Codex, OAuth runtime, or the full report contract.
2. Add a release-only command that clones the exact published tag, isolates plugin state while reusing operator authentication, invokes both hosts, and validates the full compatibility record.
3. Keep report validation directly testable without provider calls; reject missing fields, invalid enums, and mismatched duplicated values.
4. Document the smoke after tag creation and before local install sync. Do not add it to per-PR CI.

### Task 3: Make EM mandatory at the two judgment stages and multi-model optional

**Files:**
- Modify: `kc-dev-flow/skills/continue-dev-flow/SKILL.md`
- Modify: `kc-dev-flow/skills/science-officer-em/SKILL.md`
- Modify: `docs/dev/README.md`
- Modify: `scripts/kc-dev-flow-contract-test.py`
- Modify if an absolute block changes: `kc-dev-flow/references/absolutes.registry`

1. Add failing contract assertions that ideation and validation each require one EM verdict, implementation opens no review loop, the next-higher-tier rule has a highest-tier fallback, and multi-model review is not a universal gate.
2. Run `python3 scripts/kc-dev-flow-contract-test.py` and capture RED on the current `judgment-heavy` and mandatory cross-model wording.
3. Change `continue-dev-flow` so every entered ideation and validation stage gets one fresh EM verdict; a bounded defect route that skips ideation still gets validation EM.
4. Change `science-officer-em` to prefer the next higher available capability tier and fall back to the highest available tier in fresh context with high reasoning. Do not hard-code provider or model names.
5. Replace mandatory validation cross-model review with an EM recommendation: `recommended` only for contested, irreversible, low-confidence, or unresolved calls; otherwise `not_needed`. Ask the captain only on `recommended`; no response is not approval.
6. Record the observed baseline (including the 235-second Opus validation and implementation-time review waits) and compare a fixed route scenario before/after. The accepted change must remove at least half the blocking reviewer waits before the first integrated slice without weakening the validation predicate.
7. Run contract, frontmatter, parity, marketplace installability, and changed-file sanitize checks; obtain one fresh high-reasoning EM validation.

### Task 4: Cut the runtime README to at most 700 lines

**Files:**
- Modify: `docs/dev/README.md`
- Create: `docs/dev/runbooks/state-recovery.md`
- Create: `docs/dev/runbooks/validation-evidence.md`
- Create: `docs/dev/history/workflow-cost-record.md`
- Modify: `scripts/kc-dev-flow-contract-test.py`

1. Classify every current README section as always-loaded authority, stage-triggered procedure, failure-triggered recovery, example, or history; record current line count and retained owner/enforcement mappings in the task.
2. Add failing contract assertions for the 700-line ceiling, required Local Profile and Gate Authority clauses, stage `Policy mods`, EM selection/fallback, and trigger-specific links.
3. Keep authority identity, lifecycle entry/exit, stage policy selection, and captain/EM/FO boundaries in the README.
4. Move crash recovery details to `state-recovery.md`, read only after the clean-holder prerequisite fails or a state transaction is interrupted.
5. Move validation recipes and lens detail to `validation-evidence.md`, read only on entering validation; keep the validation predicate and required evidence names in the README.
6. Move observation history to `workflow-cost-record.md`; it remains non-authoritative and is not read during ordinary continuation.
7. Delete superseded examples and repeated rationale instead of relocating them. Verify the total mandatory reading path is smaller for backlog, ideation, implementation, and validation separately.
8. Run contract, frontmatter, parity, marketplace installability, link/path checks, and a fresh high-reasoning EM validation against the exact diff.

### Task 5: Pilot bounded subtraction before adding brownfield surfaces

**Files:**
- Modify: `kc-dev-flow/references/kernel.md`
- Modify byte-identically: `docs/dev/_mods/kernel.md`
- Modify: `kc-dev-flow/references/absolutes.registry`
- Modify: `docs/dev/README.md`
- Modify: `docs/dev/ROADMAP.md`

1. Trace candidate surfaces backward from the accepted outcome and record a
   without-it instrument against the exact revision and observed runtime.
2. For existing surfaces, distinguish bounded retention, captain-owned removal
   candidate, and `UNKNOWN`; preserve `UNKNOWN` without claiming irreducibility.
3. Return a proposed new surface on green or `UNKNOWN`; retain it only when the
   without-it result names a failed AC and the simpler alternative is
   insufficient.
4. Keep known-cause single-seam defects lean. Add no script, registry mechanism,
   Work Control capability, reviewer loop, or per-edit behavioral gate.
5. Default to one independently deliverable minimal PR to `main`; use a stack
   only for dependent, independently reviewable and verifiable working slices
   when waiting for the lower merge blocks useful work.
6. Exercise bounded-retention, removal-candidate, `UNKNOWN`, and stack/no-stack
   packets; run contract, frontmatter, parity, marketplace, line-budget, link,
   and exact-diff checks; obtain one fresh high-reasoning EM validation.

### Task 6: Deliver one release after all work items validate

**Files:**
- No manual version edits; release-please owns manifests, tags, and changelog.

1. Present each logical commit set for captain confirmation; stage only named files.
2. Create Draft feature PRs only after all four tasks are locally validated, or one bounded batch PR if exact delivery-to-work-item coverage remains unambiguous.
3. Wait for required checks and merge authorized feature PRs; do not merge the generated kc-dev-flow Release PR early.
4. Merge the single updated Release PR after `kc-dev-flow/S1` and `repo-platform/S1` are terminal, then verify the published tag and local Claude/Codex sync.
