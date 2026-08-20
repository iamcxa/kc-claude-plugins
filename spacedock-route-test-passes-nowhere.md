---
id: 2nwpze64kkr5qeg6d8tm4g4p
title: The Spacedock route test skips in CI and fails locally, so it passes nowhere
status: backlog
source: found by the FO while verifying the implementation stage of declared-receipt-has-no-reader, 2026-08-20 — the worker reported it as a pre-existing unrelated failure, and confirming that claim surfaced the wider gap
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## Problem

`kc-dev-flow/scripts/profile-spacedock-route.test.py` is the live-CLI half of
`scripts/kc-dev-flow-contract-test.py`, which `.github/workflows/marketplace-parity.yml`
runs as a required check. It passes in neither environment it can run in.

In CI it always skips: the test resolves the binary with `shutil.which("spacedock")` and
prints `SKIP (spacedock unavailable)` when that returns nothing, and the workflow never
installs Spacedock. So the route assertions have zero enforcement on the branch protection
that is supposed to hold them.

On a developer machine with a current binary it fails. Line 93 asserts
`"verdict: passed" in updated`, but Spacedock 0.27.0-pre8 writes `verdict: PASSED` —
verified today on `_archive/issue189.md`, terminalized by that binary through
`merge guard`. The archive carries both casings (26 lowercase, 19 uppercase), so the
binary's output changed under a test that hardcoded the old casing.

The compound effect is what makes this worth filing rather than a one-line casing fix: the
failure is not isolated to its own assertion. It exits `kc-dev-flow-contract-test.py`
non-zero before the rest of the script reports, so the byte-identical parity assertions
between `kc-dev-flow/scripts/*` and `docs/dev/_mods/*` get no local attention either — a
developer's only way to see them pass is to remove `spacedock` from `PATH`, which restores
the skip that already hides the problem in CI.

Reproduced on a tree without any unrelated local change: same failure, same symptom.

## Work profile receipt

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
