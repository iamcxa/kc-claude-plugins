---
title: Restore release-gate ablation fixture fidelity
status: ideation
source: "Release Please PR #258 run 32929119727: release-state-restored rejected for missing review.md before reaching would-strand evidence"
product: kc-dev-flow
sprint: S3
sprint-readiness: ready
started: 2026-08-26T04:30:41Z
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
              resolution:
                type: Resolution
                id: resolution:spacedock:cmdbanvhg3enbwaf26ma6wzk:backlog:1
                briefing: briefing:cmdbanvhg3enbwaf26ma6wzk:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-26T04:29:07.204115Z"
                decision: approve
                reason: Captain approved the Production two-test fixture repair to enter ideation without changing runtime flow, CI triggers, or the Spacedock pin.
              application:
                target-stage: ideation
                state: consumed
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

## Stage Report: ideation

- DONE: Bind the shape to PR #258 head 43dfeea and run 32929119727, recording the observed wrong-reason chain and the exact temporary pre8 experiment that restored 10/10 expected mutant refusals.
  GitHub recheck bound PR #258 to `43dfeea0bd3bc9904384350b7075e39ef82efa00` and run `32929119727`: `release-state-restored` entered the contract test, then the loader route test, then `gate prepare poc-item/backlog`, where relative `review.md` resolved as missing `/tmp/.../repo/review.md`; changing only that call to `str(artifact.resolve())` exposed the next false failure, a missing `candidate.json` during published-tag smoke because the copied fixture had no committed Git repository. A detached `43dfeea` temporary checkout then added `git init`, `git add -A`, and a deterministic fixture commit in `copy_repository_fixture`, retained the absolute committed review artifact, and ran `SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock.bak-0.27.0-pre8 ./scripts/kc-dev-flow-minimal-stack-ablation.test.py`: baseline passed, all ten named mutants rejected, `release-state-restored` reached `would strand`, and the runner exited 0.
- DONE: Define the accepted two-file journey, owners, failure policy, rollback, and non-goals; confirm this is direct recovery of a named broken fixture, so no reverse-recovery receipt or extra slice is needed.
  Build owner repairs only `copy_repository_fixture` in `scripts/kc-dev-flow-minimal-stack-ablation.test.py` and artifact selection in `kc-dev-flow/scripts/profile-contract-loader.test.py`; verify owner reruns the focused loader/contract suites, compilation, diff limits, and live pre8 ablation. Any wrong-reason rejection, surviving mutant, third file, runtime/CI/pin change, or stop-number breach fails closed to the Captain. Rollback is one two-file commit revert, which restores the known blocked release gate without changing runtime behavior. Non-goals are runtime flow, CI workflow, Spacedock pin, release metadata, docs, project context, PR #258 body, merge, and release. This directly restores the named broken fixture, so the reverse-recovery condition and multi-slice guard do not fire.
- DONE: Map AC-1 through AC-3 to falsifiable checks and declare implementation stop numbers no larger than 2 files, 25 gross changed lines, and 20 gross lines of Git-fixture setup.
  AC-1 is falsified unless the exact-head runner exits 0 and `release-state-restored: REJECTED` contains `would strand`, not missing artifact/receipt/Git evidence. AC-2 is falsified unless the copied fixture has a resolvable committed `HEAD` before candidate smoke and the readable tracked review artifact is passed by absolute path, with no third file. AC-3 is falsified unless pre8 reports baseline PASS plus all ten expected named refusals through the live Spacedock path. Stop at more than 2 files, more than 25 gross changed lines, or more than 20 gross lines devoted to Git-fixture setup; the temporary proof measured 2 files, 9 gross changed lines, and 7 Git-fixture setup lines.

### Summary

The accepted shape is one reversible two-file fixture repair on exact PR #258 code, with the intended `would strand` evidence preserved and no production behavior change. The temporary pre8 exercise removed both false preconditions and restored the complete 10/10 mutant refusal proof within the declared stop numbers.
