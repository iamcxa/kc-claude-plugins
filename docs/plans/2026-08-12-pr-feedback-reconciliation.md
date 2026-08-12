# PR Feedback Reconciliation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make PR-pending dev-flow work detect and disposition external GitHub review feedback before readiness, merge, or terminalization.

**Architecture:** Keep PR lifecycle mechanics in the repository-local `pr-merge` extension and keep validation semantics in the portable kernel plus the adopter workflow. The existing startup/idle hooks take repository-explicit, exact-head snapshots of unresolved inline threads and substantive PR-level reviews, route non-empty feedback to `kc-pr-review-resolve`, and fail closed on unavailable evidence. No new stage, daemon, GitHub Action, or delivery authority is introduced.

**Tech Stack:** Markdown policy contracts, `gh` CLI, GitHub GraphQL/REST APIs, Python contract tests.

### Task 1: Add the RED contract

**Files:**
- Modify: `scripts/kc-dev-flow-contract-test.py`

1. Require the portable kernel to treat provider review feedback as validation evidence and invalidate validation when a fix changes the exact revision.
2. Require the adopter validation and done sections to name the PR feedback snapshot, per-item dispositions, and fail-closed completion condition.
3. Require the local `pr-merge` extension to query exact PR identity, unresolved GraphQL review threads, substantive REST PR-level reviews, and required checks without hard-coding a check name.
4. Require startup/idle re-entry, resolver routing, head-change invalidation, and `UNKNOWN` behavior on incomplete/API-failed observations.
5. Run `python3 scripts/kc-dev-flow-contract-test.py` and confirm it fails because the feedback contract is absent.

### Task 2: Add portable validation semantics

**Files:**
- Modify: `kc-dev-flow/references/kernel.md`
- Modify: `docs/dev/_mods/kernel.md`
- Modify: `docs/dev/README.md`

1. Add the conditional rule for delivery providers that expose review feedback after initial validation.
2. Require technical verification and a recorded `fixed`, `rejected-with-reason`, or `out-of-scope-and-filed` disposition for each observed item.
3. Bind the snapshot and disposition to the exact PR head; a code-changing resolution invalidates prior validation.
4. Add the adopter validation re-entry and done-gate clauses.
5. Keep the two kernel copies byte-identical.

### Task 3: Add restartable PR-pending detection

**Files:**
- Modify: `docs/dev/_mods/pr-merge.md`
- Modify: `kc-pr-flow/skills/kc-pr-review-resolve/SKILL.md`

1. Extend only the trailing kc-dev-flow local extension; preserve the released Spacedock 0.12.2 body hash.
2. On startup, idle, readiness, and pre-merge checkpoints, resolve explicit `PR_REPO`, `PR_NUMBER`, PR author, and `headRefOid`.
3. Fetch unresolved inline threads through GraphQL and substantive PR-level reviews through REST. Include bot reviewers; exclude only the PR author's own responses from external-feedback detection.
4. Route observed feedback through `kc-pr-flow:kc-pr-review-resolve`; do not accept or modify code based on identity alone.
5. Require reconciliation mode to disposition every detector-retained review and thread ID, including items its normal interactive filtering would exclude.
6. Reconcile every native-stack layer independently; a top-PR snapshot does not cover lower layers.
7. Keep the PR pending on feedback, required-check pending/failure, head drift, pagination ambiguity, missing tools, or API failure.
8. Allow readiness only after a clean snapshot and captain authorization.

### Task 4: Verify and review

**Files:**
- Test: `scripts/kc-dev-flow-contract-test.py`
- Test: `scripts/pr-merge-portable-delivery.test.py`

1. Run the focused contract and portable-delivery tests.
2. Add table and mutation tests for feedback-before-state-mutation ordering and per-layer stack coverage.
3. Run version parity, skill frontmatter lint, and marketplace verification.
4. Ask a fresh Science Officer (EM) to review the exact diff and return the closed advisory report.
5. Address supported findings with another RED/GREEN cycle.
6. Present the final file list and proposed commit message to the captain; do not commit until explicitly approved.
