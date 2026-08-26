---
title: Restore release-gate ablation fixture fidelity
status: backlog
source: "Release Please PR #258 run 32929119727: release-state-restored rejected for missing review.md before reaching would-strand evidence"
product: kc-dev-flow
sprint: S3
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane: main
id: cmdbanvhg3enbwaf26ma6wzk
gates:
    version: 1
    records:
        - id: gate:cmdbanvhg3enbwaf26ma6wzk:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:cmdbanvhg3enbwaf26ma6wzk-backlog-1
              briefing:
                id: briefing:cmdbanvhg3enbwaf26ma6wzk:backlog:attempt-1:revision-1
                digest: sha256:59b48d09b5f81f971fb0cf80355bfc375e7d0bfbbbbe99563195447492ecd00c
                request-digest: sha256:0201d507687663edd4c0fbe386a35d1035c2646f0857bcbbf7cab1130100ce16
                room-ref: ./release-gate-fixture-fidelity/review/backlog/briefing-1
---

Repair the release-state ablation fixture so PR #258 tests the intended flow guard instead of failing on missing Git or artifact-path preconditions.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  recommended: production
  basis: >-
    This is a persistent release-boundary test for kc-dev-flow v4. It changes no
    runtime behavior, but it must preserve exact failure reasons and rollback-safe
    release authorization evidence across the pinned Spacedock runtime.
  route: [shape, build, verify]
  obligations:
    architecture:
      - Keep the existing release-state guard and CI trigger unchanged.
      - Repair fixture preconditions rather than weakening expected failure evidence.
    implementation:
      - Initialize the copied repository fixture as a committed Git repository.
      - Pass the committed gate artifact by absolute path across Spacedock versions.
    testing:
      - Reproduce the current wrong-reason failure at PR #258 head 43dfeea.
      - Prove baseline PASS and all ten without-it mutants reject for their expected reasons on Spacedock 0.27.0-pre8.
      - Run the focused loader and contract suites plus Python compilation and diff check.
  scope_boundary: >-
    Only scripts/kc-dev-flow-minimal-stack-ablation.test.py and
    kc-dev-flow/scripts/profile-contract-loader.test.py; no runtime flow,
    workflow trigger, Spacedock version, release metadata, or PR #258 body change.
  promote_when:
    - No higher profile exists; stop for Captain scope if a runtime, CI workflow, dependency pin, or third file must change.
  decision:
    authority: Kent (Captain)
    at: 2026-08-26T04:27:21Z
```

## Intended outcome

The release-state-restored ablation reaches and rejects the intended `would strand` flow defect on the pinned release runtime, while the unmodified gate remains green.

## Acceptance criteria

**AC-1 — The fixture reaches the intended guard.**
Verified by: exact PR #258 code with the two fixture repairs reports `release-state-restored: REJECTED` and the whole ablation runner exits zero.
Falsified by: the mutant fails first on a missing file, missing receipt, Git lookup, or any evidence other than `would strand`.

**AC-2 — The two preconditions are real and minimal.**
Verified by: the copied repository has a committed HEAD before candidate smoke, and the gate review artifact is a readable committed file selected by absolute path.
Falsified by: production code, CI workflow, dependency pin, or a third file must change.

**AC-3 — The release proof remains discriminating.**
Verified by: baseline passes and all ten named without-it mutants are rejected for their expected evidence on Spacedock 0.27.0-pre8.
Falsified by: a mutant survives, a wrong-reason failure is accepted, or the fix bypasses the live Spacedock path.

## Delivery boundary

Deliver as one Draft PR to `main`, then let Release Please update and rerun PR #258. Merge and release remain Captain-owned.
