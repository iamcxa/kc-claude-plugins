---
id: 8hyzngaw0frz3f0rzp2fvpxm
title: Derive release-smoke identity from the tracked package, not ignored worktree files
status: backlog
source: "kc-dev-flow-v2.5.0 post-publication incident: candidate receipt included two ignored __pycache__ files, Captain-approved next-release blocker on 2026-08-15"
product: kc-dev-flow
sprint: S3
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane: main
---

The `kc-dev-flow-v2.5.0` candidate smoke hashed and locally installed the ambient `kc-dev-flow/` directory. Two ignored Python bytecode files created before receipt generation entered that digest even though the clean release tag contained the exact same tracked Git subtree. Published mode then correctly refused the preserved receipt after release, producing a false artifact-drift signal and requiring a Captain-approved recovery.

## Intended outcome

Candidate identity and candidate installation must use an exact tracked snapshot of the candidate revision—the same package surface a clean tag clone can publish—rather than ambient ignored or untracked worktree files. Keep the original v2.5.0 failed receipt and recovery evidence as the regression fixture; do not republish or rewrite that release.

## Acceptance criteria

**AC-1 — Ignored worktree artifacts cannot enter candidate identity.**
Verified by: adding ignored `__pycache__/*.pyc` files beneath `kc-dev-flow/` does not change the candidate package digest or installed candidate tree, while changing a tracked package byte does.
Falsified by: any ignored or untracked file changes the receipt or installed tree, or a tracked byte fails to change it.

**AC-2 — Candidate and published modes measure the same package surface.**
Verified by: an exact candidate revision and its clean tag-equivalent checkout produce equal package digests and equal isolated Claude/Codex installed trees without deleting or mutating the developer worktree.
Falsified by: either mode hashes a different file population, depends on cleanup, or installs from ambient files outside the measured snapshot.

**AC-3 — The v2.5.0 incident is mechanically reproducible.**
Verified by: a regression fixture recreates the two ignored-file contamination shape, demonstrates the old filesystem walk would diverge, and demonstrates the corrected mechanism remains equal to a clean checkout.
Falsified by: coverage only asserts prose or a constant, cannot fail under the old mechanism, or discards the preserved failure shape.

**AC-4 — Published closeout remains bounded and no-model.**
Verified by: published mode still rejects genuine tag/version/tracked-tree/install mismatches, invokes no model, and emits evidence distinguishing artifact drift from local measurement contamination.
Falsified by: the correction weakens mismatch refusal, silently rewrites receipts, adds a retry, invokes a model, or treats the v2.5.0 failed receipt as PASS.

## Delivery boundary

This is a Production-profile release-safety fix and must merge before the next `kc-dev-flow` release candidate. It does not require or authorize republishing `kc-dev-flow-v2.5.0`; that release retains its explicit failed receipt plus Captain-approved recovery addendum.
