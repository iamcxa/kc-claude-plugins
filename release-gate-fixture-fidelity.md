---
title: Restore release-gate ablation fixture fidelity
status: validation
source: "Release Please PR #258 run 32929119727: release-state-restored rejected for missing review.md before reaching would-strand evidence"
product: kc-dev-flow
sprint: S3
sprint-readiness: ready
started: 2026-08-26T04:30:41Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-release-gate-fixture-fidelity
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
        - id: gate:cmdbanvhg3enbwaf26ma6wzk:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:cmdbanvhg3enbwaf26ma6wzk-ideation-1
              briefing:
                id: briefing:cmdbanvhg3enbwaf26ma6wzk:ideation:attempt-1:revision-1
                digest: sha256:cf2ab982d9efa819dd3b734b928c6d5cae65f3d361b63210ecb6a45902195998
                request-digest: sha256:694c7f9453a3f96e56fb672f8bda20870788ad335ad152182e0aaac1347057f4
                room-ref: ./release-gate-fixture-fidelity/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:cmdbanvhg3enbwaf26ma6wzk:ideation:1
                briefing: briefing:cmdbanvhg3enbwaf26ma6wzk:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-26T04:40:41.835538Z"
                decision: approve
                reason: Captain approved the bounded two-test fixture repair after ideation review.
              application:
                target-stage: implementation
                state: consumed
        - id: gate:cmdbanvhg3enbwaf26ma6wzk:validation
          stage: validation
          attempts:
            - id: gate-attempt:cmdbanvhg3enbwaf26ma6wzk-validation-1
              briefing:
                id: briefing:cmdbanvhg3enbwaf26ma6wzk:validation:attempt-1:revision-1
                digest: sha256:7524f0d23c14be6987a6a312d85855fe610260ab6ad0807001110319dd85dd54
                request-digest: sha256:e5b5487e9f8f3bb2db4343446df0a9c16a25c75d8b6cc386eb9ebbb4bd13e229
                room-ref: ./release-gate-fixture-fidelity/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:cmdbanvhg3enbwaf26ma6wzk:validation:1
                briefing: briefing:cmdbanvhg3enbwaf26ma6wzk:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-26T05:17:05.434417Z"
                decision: approve
                reason: Captain approved exact candidate d339ba2 for Draft PR delivery after fresh pinned-pre8 validation.
              application:
                target-stage: done
                state: superseded
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

## Stage Report: implementation

- DONE: Reproduce the two false preconditions from PR #258 evidence, then change only the two accepted test files.
  The unmodified pre8 run failed first on missing `repo/review.md`; the absolute-path-only run then failed on missing `candidate.json`, before commit d339ba2 changed only the two allowed test files.
- DONE: Initialize each copied repository fixture with deterministic Git identity and a committed HEAD before candidate smoke.
  `scripts/kc-dev-flow-minimal-stack-ablation.test.py:60-66` initializes Git, stages the copied fixture, and commits it as `fixture <fixture@example.test>`; removing this makes the published-tag smoke lose `candidate.json`.
- DONE: Pass the committed review artifact to Spacedock as an absolute resolved path.
  `kc-dev-flow/scripts/profile-contract-loader.test.py:1046` passes `artifact.resolve()`; restoring the relative path makes pre8 search for the nonexistent `repo/review.md`.
- DONE: Run focused loader/contract tests, Python compilation, and the exact Spacedock 0.27.0-pre8 ablation: baseline PASS, 10/10 named mutants rejected, release-state-restored reaches would-strand.
  Loader and contract tests passed with pre8, both changed files compiled, and the live ablation exited 0 with baseline PASS plus 10/10 refusals; its `reject(..., "would strand")` check would fail on any earlier reason.
- DONE: Map each changed line to AC-1 through AC-3, enforce the 2-file/25-line/20-Git-line stop numbers, remove unnecessary additions, write the Stage Report, and commit only the two scoped files.
  AC-1 and AC-2 map to Git fixture lines 60-66 and absolute artifact line 1046; AC-3 maps to the unchanged evidence-matching ablation path. Final scope is 2 files, 9 gross changed lines, and 7 Git-fixture lines in commit d339ba2.

### Summary

Commit d339ba2 removes both false preconditions without changing production code, CI, dependencies, or the pinned runtime. The exact pre8 path now distinguishes the intended release-state guard from missing fixture evidence and preserves all ten mutant refusals.

## Implementation evidence

```json
{
  "schema": "kc-dev-flow-implementation-evidence/v1",
  "review_convergence_claim": {
    "state": "claimed",
    "identity": "sha256:9a65f00d28bf4141a990d9b4da1191f1f6cf6ac56f7373c3a0955da625a692e1",
    "claimant": "codex-worker:spacedock-ensign-release-gate-fixture-fidelity-implementation",
    "observed_state_revision": "d431a7b6b7995fc23243c0601a4a4f2e1384aa53",
    "exact_input": {
      "repository": "github.com/iamcxa/kc-claude-plugins",
      "base": "e20d13b5b1cf06921db58b6a0f132401dfc1fe9d",
      "tip": "d339ba2e982d71742d4223fead69e5a31fd4744a",
      "provider_version": "v0.62.0",
      "json_contract": ["list --json", "show --json"],
      "configuration": "e816dfd221a307eee460f0404e4870d464ec7b66",
      "profile": "production",
      "implementation_family": "openai",
      "agent": "claude-code",
      "model": "sonnet",
      "reasoning": "thorough",
      "minimum_severity": "medium",
      "live_batch_timeout_seconds": 1200,
      "request_cap": 1,
      "repair_confirmation_cap": 1,
      "panel": "none",
      "member_identities": ["claude-code:sonnet"],
      "member_count": 1
    }
  }
}
```

```json
{
  "schema": "kc-dev-flow-observation/v1",
  "capability": "review_convergence",
  "mode": "observe",
  "provider": "roborev",
  "trigger": "implementation_exit",
  "candidate_revision": "d339ba2e982d71742d4223fead69e5a31fd4744a",
  "base_revision": "e20d13b5b1cf06921db58b6a0f132401dfc1fe9d",
  "selected_profile": "production",
  "implementation_family": "openai",
  "outcome": "UNKNOWN",
  "reason": "state_unknown",
  "identity_hash": "sha256:9a65f00d28bf4141a990d9b4da1191f1f6cf6ac56f7373c3a0955da625a692e1",
  "configuration_object_sha": "e816dfd221a307eee460f0404e4870d464ec7b66",
  "reviewer": {
    "agent": "claude-code",
    "model": "sonnet",
    "reasoning": "thorough",
    "minimum_severity": "medium",
    "panel": "none"
  },
  "capability_evidence": {
    "cli_contract": "PASS: roborev v0.62.0 with review, list --json, and show --json",
    "execution_state": "PASS: daemon healthy",
    "agent_authentication": "PASS: claude-code check-agents produced output",
    "local_command_bridge": "not_required"
  },
  "job": {
    "id": 272,
    "uuid": "930f4415-d01b-4370-ab6b-7e6af3e7962e",
    "git_ref": "e20d13b5b1cf06921db58b6a0f132401dfc1fe9d..d339ba2e982d71742d4223fead69e5a31fd4744a",
    "status": "running",
    "correlation": "ambiguous",
    "missing_json_identity_fields": [
      "repository_identity",
      "configuration",
      "selected_profile",
      "implementation_family",
      "provider_version",
      "json_contract",
      "live_batch_timeout_seconds",
      "request_cap",
      "repair_confirmation_cap",
      "panel",
      "member_identities",
      "member_count"
    ]
  },
  "member_states": [],
  "member_population_complete": false,
  "live_batch_timeout_seconds": 1200,
  "request_count": 1,
  "request_cap": 1,
  "confirmation_count": 0,
  "repair_confirmation_cap": 1,
  "cost_coverage": {
    "approximate_total_usd": 0,
    "jobs_with_cost": 0,
    "jobs_total": 0,
    "complete": false,
    "exact_ceiling": null
  },
  "authority": "observation_only"
}
```

## Stage Report: validation

- DONE: Bind exact base e20d13b5b1cf06921db58b6a0f132401dfc1fe9d and candidate d339ba2; inspect the exact two-file diff and map AC-1 through AC-3 to falsifiers.
  HEAD is d339ba2e982d71742d4223fead69e5a31fd4744a with sole parent e20d13b5b1cf06921db58b6a0f132401dfc1fe9d; AC-1 fails on any non-`would strand` refusal, AC-2 on any extra file or missing committed/absolute-path precondition, and AC-3 on baseline failure, a surviving mutant, or wrong-reason evidence.
- DONE: Independently run focused profile-loader and kc-dev-flow contract tests plus Python compilation at the exact candidate.
  With `/Users/kent/.local/bin/spacedock.bak-0.27.0-pre8`, `profile-contract-loader.test.py` reported route mechanism PASS and overall PASS, `kc-dev-flow-contract-test.py` reported PASS, and `py_compile` passed for both changed files; removing either fixture repair makes these paths fail before the intended guard.
- DONE: Independently run the live Spacedock 0.27.0-pre8 ablation; require baseline PASS, all ten named mutants rejected, and release-state-restored evidence containing would strand.
  The live runner exited 0 with baseline PASS, all ten named mutants REJECTED, and `release-state-restored: REJECTED`; its unchanged `reject(..., "would strand")` matcher fails closed if that mutant stops on missing file, receipt, Git, or other evidence.
- DONE: Verify no runtime, CI workflow, dependency pin, release metadata, documentation, or third-file change; confirm rollback is the one candidate commit.
  `git diff --name-only` contains only the two accepted test files, `git diff --check` is clean, the candidate range contains one commit, and rollback is a revert of d339ba2; the candidate worktree remained clean.
- DONE: Disposition RoboRev UNKNOWN(state_unknown) as non-authoritative provider evidence, record material residuals, write the validation Stage Report, and do not modify or commit product files.
  Job 272 remains UNKNOWN(state_unknown) and was not queried or reinterpreted; no GitHub PR exists, so provider CI and PR feedback remain unproven, and Draft PR creation plus Release Please PR #258 rerun remain delivery residuals outside validation.

### Summary

Validation passes locally at exact candidate d339ba2: the two-file fixture repair preserves baseline behavior and rejects all ten mutants for their intended evidence on pinned Spacedock 0.27.0-pre8. Product files were not changed during validation; hosted PR, provider CI, and the Release Please rerun remain separate delivery proof.

PR feedback: {"scheme":"github-pr-feedback/v1","repository":"iamcxa/kc-claude-plugins","pr_number":295,"layer":"single","head":"d339ba2e982d71742d4223fead69e5a31fd4744a","fingerprint":"sha256:a7bf6f78a2488cf49141b0bc8215b4ce5d9ca8f1ca72fd3ed68192d062d12e51","dispositions":[]}

## Stage Report: implementation (cycle 2)

- DONE: Bind exact current branch d339ba2, remote branch d339ba2, and fresh origin/main 31207d6. Rebase the product branch onto origin/main; resolve the sole loader-test conflict by keeping origin/main because PR #299 already supplies the required absolute artifact path.
  Local and remote heads both matched d339ba2 before rebase; the sole conflict was resolved to origin/main, whose absolute route artifact passed the focused live loader test.
- DONE: Preserve only the unique seven-line committed-Git initialization in scripts/kc-dev-flow-minimal-stack-ablation.test.py. Final origin/main diff must be exactly one file and seven added lines; no other product, workflow, CI, dependency, pin, metadata, documentation, or authority change.
  Commit 0e9d613 changes exactly one file by seven additions; removing them leaves copied fixtures without the committed HEAD required by candidate smoke.
- DONE: Prove origin/main already contains the absorbed absolute artifact-path behavior. Run the focused loader test, complete kc-dev-flow contract gate, Python compilation, diff-check, and the pinned Spacedock 0.27.0-pre8 minimal-stack ablation with baseline PASS, 10/10 named mutants rejected, and release-state-restored reaching would strand.
  Loader route mechanism and full contract gate passed, both Python files compiled, diff-check was clean, and pinned pre8 reported baseline PASS plus 10/10 named refusals; the unchanged release-state matcher fails unless the evidence contains `would strand`.
- DONE: Do not rerun the spent RoboRev implementation-exit request; carry its explicit UNKNOWN(state_unknown) residual. Do not push the product branch or update PR #295. Append one implementation rework Stage Report, commit only the rebased one-file repair, and sync only state.
  RoboRev was not rerun, its UNKNOWN(state_unknown) residual remains explicit, and neither the product branch nor PR #295 was updated from this implementation worker.

### Summary

The rebase drops the now-redundant loader-test hunk and retains only the seven-line Git fixture precondition in 0e9d613. Fresh local proof is green on pinned Spacedock 0.27.0-pre8; product push, PR update, validation, and delivery remain First Officer work.
