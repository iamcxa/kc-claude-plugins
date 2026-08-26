---
id: 8hyzngaw0frz3f0rzp2fvpxm
title: Derive release-smoke identity from the tracked package, not ignored worktree files
status: validation
source: "kc-dev-flow-v2.5.0 post-publication incident: candidate receipt included two ignored __pycache__ files, Captain-approved next-release blocker on 2026-08-15"
product: kc-dev-flow
sprint: S3
sprint-readiness: ready
started: 2026-08-26T02:40:07Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-release-smoke-tracked-package-identity
issue:
pr:
mod-block:
design: required
lane: main
gates:
    version: 1
    records:
        - id: gate:8hyzngaw0frz3f0rzp2fvpxm:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:8hyzngaw0frz3f0rzp2fvpxm-backlog-1
              briefing:
                id: briefing:8hyzngaw0frz3f0rzp2fvpxm:backlog:attempt-1:revision-1
                digest: sha256:e85deb11de4048026c63b1031495ccd48b1ca985dc73c4c09c8ec63e1684d5de
                request-digest: sha256:76579829b469b33a865e4573082c96f9291918ea6df1cdf452a36688295368a7
                room-ref: ./release-smoke-tracked-package-identity/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:8hyzngaw0frz3f0rzp2fvpxm:backlog:1
                briefing: briefing:8hyzngaw0frz3f0rzp2fvpxm:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-26T02:34:50.623078Z"
                decision: approve
                reason: Captain approved the tracked-snapshot release-smoke direction and asked to continue into Production ideation.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:8hyzngaw0frz3f0rzp2fvpxm:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:8hyzngaw0frz3f0rzp2fvpxm-ideation-1
              briefing:
                id: briefing:8hyzngaw0frz3f0rzp2fvpxm:ideation:attempt-1:revision-1
                digest: sha256:9ea4c714b93f4c9691b7c9de1fed7c9c4e709bc395b1bfc7b79c73bddc1ad8c7
                request-digest: sha256:9b907b4fb8c69b919bdd493c8bab75376ab3265105dda86ba356ad292e9aa9a9
                room-ref: ./release-smoke-tracked-package-identity/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:8hyzngaw0frz3f0rzp2fvpxm:ideation:1
                briefing: briefing:8hyzngaw0frz3f0rzp2fvpxm:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-26T02:51:02.218331Z"
                decision: approve
                reason: Captain approved the exact-revision git-archive design and asked to continue into implementation.
              application:
                target-stage: implementation
                state: consumed
---

The `kc-dev-flow-v2.5.0` candidate smoke hashed and locally installed the ambient `kc-dev-flow/` directory. Two ignored Python bytecode files created before receipt generation entered that digest even though the clean release tag contained the exact same tracked Git subtree. Published mode then correctly refused the preserved receipt after release, producing a false artifact-drift signal and requiring a Captain-approved recovery.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  recommended: production
  basis: >-
    This changes the identity, installation, rollback, and published-release
    evidence for an existing public plugin. A false candidate receipt can block
    release closeout for every adopter, while a weak fix can admit untracked
    bytes into the package boundary; that compatibility and release ownership
    requires Production.
  route: [shape, build, verify]
  obligations:
    architecture:
      - Derive candidate digest and installation from one exact tracked Git snapshot.
      - Keep candidate and published modes on the same package-byte boundary.
      - Preserve the v2.5.0 failed receipt as immutable incident evidence.
    implementation:
      - Exclude ignored and untracked worktree files without cleaning or mutating the worktree.
      - Keep genuine revision, version, digest, and installed-tree mismatches fail closed.
      - Reuse the existing release-smoke mechanism without adding another artifact ledger.
    testing:
      - Reproduce ignored bytecode contamination and prove it cannot change candidate identity.
      - Prove a tracked-byte change still changes both digest and installed candidate tree.
      - Compare the exact candidate revision with a clean tag-equivalent checkout and retain mismatch negatives.
  scope_boundary: >-
    No v2.5.0 republish, model call, worktree cleanup, silent receipt rewrite,
    retry loop, provider change, or generalized packaging framework.
  promote_when:
    - No higher profile exists; stop for new Captain scope if the fix needs release publication, provider mutation, a new ledger, or a compatibility exception.
  decision:
    authority: Kent (Captain)
    at: 2026-08-26T00:36:37Z
```

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

## Ideation: accepted Production shape

Delivery base: `origin/main` at `844edfa75a021cc6c013186bb88fba81f598f912`.

### Accepted journey and observable semantics

1. **OBSERVED — current candidate boundary.** `run_candidate_smoke` resolves `HEAD`, but `git status --porcelain` hides ignored files; `tree_digest` then walks ambient `kc-dev-flow/`, and both installers receive that same ambient checkout. At the delivery base, adding the incident's two ignored `.pyc` paths changed the walk digest from `6f5a6e6d696dec8711a0af91d3c629a8d5820e8ebfff4f9b3b3fc3f0ac8a3d32` to `df5139c5f03706e24f416022ada99adb43c854c6f03ad3961e4d639c7238f3c1` while the Git revision stayed fixed.
2. **DESIGNED — candidate snapshot.** Candidate mode resolves exact `HEAD`, refuses tracked worktree changes with `git status --porcelain --untracked-files=no`, then runs `git archive --format=tar <revision> -- .claude-plugin kc-dev-flow` and safely extracts it under the existing temporary root. Ignored and untracked bytes remain untouched in the developer worktree and cannot enter the snapshot.
3. **DESIGNED — one measured and installed source.** `package_identity`, Claude installation, and Codex installation all receive that one extracted snapshot path. The existing post-install digest checks remain the readback proof; no second manifest or ledger is introduced.
4. **DESIGNED — published parity.** Published mode still clones and verifies the exact tag, then materializes the same two pathspecs with the same snapshot helper before digesting and installing. A source mismatch is reported as tracked-snapshot drift, distinct from the mechanically excluded ambient contamination class.
5. **DESIGNED — unhappy paths.** Archive failure, unsafe archive members, tracked dirt, manifest/version disagreement, tag mismatch, candidate-receipt mismatch, or either installed-tree mismatch stops before a receipt or success result. No cleanup, retry, receipt rewrite, republish, provider mutation, or model invocation is added.

The CLI grammar and candidate/published receipt schemas do not change. Candidate mode's only intentional observable change is that ignored and untracked files no longer block or affect a run; tracked modifications still fail closed, and a committed tracked package-byte change produces a new snapshot digest and installed tree.

### Selected mechanism, ownership, and boundary

The selected mechanism is one temporary **tracked-package snapshot**: the `.claude-plugin` marketplace metadata and `kc-dev-flow` plugin tree emitted by `git archive` for an exact revision. The release-smoke script owns snapshot creation and deletion through its existing temporary-directory lifecycle; Git owns revision/path selection; Claude and Codex installers consume the extracted directory; `tree_digest` remains the source/install readback contract; the release owner retains receipt and publication authority.

This is recovery of the existing release-smoke seam, not a packaging framework. The v2.5.0 failed receipt, recovery receipt, incident verdict, and clean-tag evidence remain immutable. Release Please pull request #258's ablation-fixture failure, continuous integration jobs, documentation, provider behavior, worktree cleanup, additional ledgers, and v2.5.0 publication are non-goals.

Rollback is a revert of the implementation commit before any later release candidate receipt is accepted. Reverting restores the known ambient-walk defect, so release ownership must reinstate the next-release block; it must not rewrite either v2.5.0 receipt or reinterpret the recorded failure. Forward recovery is preferred if a later installer exposes an archive-compatibility issue: repair the single snapshot helper while keeping receipt schemas and mismatch refusal unchanged.

```yaml
reverse_recovery:
  trigger: "replace ambient candidate identity and installation input with tracked-revision input"
  boundary: "candidate and published paths in scripts/kc-dev-flow-published-tag-smoke.py at base 844edfa75a021cc6c013186bb88fba81f598f912"
  layers:
    - surface: "candidate entry and revision fence"
      location: "scripts/kc-dev-flow-published-tag-smoke.py:479-493"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "ignored files bypass status but enter package_identity(ROOT)"
      disproof_hook: "repeat the two-.pyc probe and require ambient and archived digests to remain equal"
    - surface: "package identity walk"
      location: "scripts/kc-dev-flow-published-tag-smoke.py:278-312"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "rglob hashes every ambient file; the base probe changed the digest at fixed revision"
      disproof_hook: "run the focused regression with the old ROOT input and require it to pass"
    - surface: "Claude and Codex candidate installation"
      location: "scripts/kc-dev-flow-published-tag-smoke.py:315-378,510-519,569-579"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "both installers consume the same ambient checkout that was hashed"
      disproof_hook: "assert either candidate installer source is the repository root rather than the extracted snapshot"
    - surface: "candidate receipt contract"
      location: "scripts/kc-dev-flow-published-tag-smoke.py:449-476,606-617"
      completeness: WORKING
      need: REQUIRED
      evidence: "closed v1 receipt preserves exact revision, version, digest, and dual-host PASS"
      disproof_hook: "existing extra-field, wrong-revision, wrong-version, wrong-digest, and wrong-report negatives"
    - surface: "published tag binding and install readback"
      location: "scripts/kc-dev-flow-published-tag-smoke.py:620-688"
      completeness: WORKING
      need: REQUIRED
      evidence: "it correctly rejected v2.5.0 source drift and retains tag/version/source/install refusal without models"
      disproof_hook: "existing tag, version, source, Claude-tree, Codex-tree, and no-host-invocation negatives"
  decision: recover
```

`multi_slice_required`, `retained_document_change`, and `project_context_claim_may_change` remain false: the accepted route is one script plus its existing focused test, with no retained-document or project-context claim change.

### Acceptance and release checks

| Criterion | Falsifiable test | File-level touch point |
|---|---|---|
| AC-1 | In a temporary Git fixture, record the clean snapshot digest and fake-installed Claude/Codex trees; add the two ignored incident `.pyc` files plus one untracked file and require all three identities unchanged. Commit one tracked plugin-byte change and require the snapshot digest and both installed trees to change. Reusing ambient `ROOT` must fail this test. | `scripts/kc-dev-flow-published-tag-smoke.py`; `scripts/kc-dev-flow-published-tag-smoke.test.py` |
| AC-2 | Run candidate and tag-equivalent published paths against the same committed package paths; require both snapshot helper calls, equal digests, equal isolated installed trees, no developer-worktree mutation, and refusal of tracked dirt. Bypassing the helper for either digest or install must fail. | Same two files |
| AC-3 | Preserve the exact two `skills/setup-github-project-projection/assets/__pycache__/*.cpython-314.pyc` fixture paths; assert the old ambient walk diverges while the new snapshot equals the clean checkout. Removing either old-mechanism divergence or new-mechanism equality must fail. | Focused test only |
| AC-4 | Retain all existing receipt, tag, version, source, Claude-tree, and Codex-tree negatives; assert published mode records zero host/model invocations and its source-mismatch diagnostic names tracked-snapshot drift. Weakening any refusal or invoking a host must fail. | Same two files |

Release checks are `python3 scripts/kc-dev-flow-published-tag-smoke.test.py`, the existing `scripts/kc-dev-flow-contract-test.py` caller, Python compilation, and `git diff --check`. They are local no-model checks; no continuous-integration trigger or provider-cost change is proposed, so per-pull-request cost is unchanged and not remeasured here.

### Where it touches and stop numbers

| Path | Lines now | Lines after | Purpose |
|---|---:|---:|---|
| `scripts/kc-dev-flow-published-tag-smoke.py` | 760 | about 800 | Add one safe exact-revision snapshot helper and route both modes' identity/install inputs through it. |
| `scripts/kc-dev-flow-published-tag-smoke.test.py` | 432 | about 550 | Add the incident regression, tracked-change positive control, shared-source assertions, and preserve mismatch/no-model negatives. |

Implementation stops and reports if the diff against `844edfa75a021cc6c013186bb88fba81f598f912` exceeds **2 changed files**, **180 gross changed lines**, or **120 gross changed lines in snapshot-fixture/FakeSmokeRuntime scaffolding**, the named runaway area. It also stops immediately if a receipt schema, documentation, Release Please fixture, continuous-integration workflow, provider call, or third production file becomes necessary.

## Stage Report: ideation

- DONE: Select one exact tracked-Git snapshot mechanism shared by candidate digest and installation, and show why the ambient directory walk fails.
  Selected exact-revision `git archive` for `.claude-plugin` plus `kc-dev-flow`; a fixed-base two-file probe changed only the ambient-walk digest (`6f5a6e6d...` to `df5139c5...`).
- DONE: Classify the existing release-smoke layers with a reverse-recovery receipt, preserving the v2.5.0 incident and defining rollback without a new ledger.
  The bounded receipt chooses `recover`; working receipt/tag/readback refusal stays, broken candidate identity/install input is replaced, and rollback reinstates the release block without rewriting v2.5.0 evidence.
- DONE: Map AC-1 through AC-4 to falsifiable tests, file-level touch points, and stop numbers for one minimal integrated slice.
  All criteria map to the existing smoke script and focused test; implementation halts beyond 2 files, 180 gross lines, or 120 fixture/runtime-scaffolding lines.

### Summary

Ideation accepts one temporary tracked-package snapshot shared by candidate and published digest plus installation. The two-file slice preserves receipt schemas, mismatch refusal, the v2.5.0 incident, and no-model published closeout while excluding ambient ignored and untracked bytes without cleaning the worktree.

### RoboRev observation claim

- identity: `b1e86e9dbf100f2c84d2ae71ae30023c46baf1a12e5ecd4c1f92a436d6b193c3`
- claimant: `spacedock-ensign-release-smoke-tracked-package-identity-implementation`
- observed-state-revision: `ab06f28a67f89e505228ebde06585522b1fb917b`
- state: `claimed`

## Implementation evidence

```yaml
review_convergence:
  schema: kc-dev-flow-observation/v1
  capability: review_convergence
  mode: observe
  selected_profile: production
  provider: roborev
  outcome: PASS
  reason: passed
  exact_base: 844edfa75a021cc6c013186bb88fba81f598f912
  exact_tip: 278095b3015a25bb7140e7dd2b09482d96fc412a
  implementation_provider_family: openai
  reviewer: {agent: claude-code, model: sonnet, reasoning: thorough, minimum_severity: medium, panel: none}
  identity_hash: b1e86e9dbf100f2c84d2ae71ae30023c46baf1a12e5ecd4c1f92a436d6b193c3
  config_object_sha: e816dfd221a307eee460f0404e4870d464ec7b66
  job_identity: {id: 266, uuid: c0b65a8c-90a6-4717-9be4-38f38e2f2ca6}
  member_states: []
  request_count: 1
  confirmation_count: 0
  cost_coverage: {approximate_total_usd: 0.5685936, jobs_with_cost: 1, jobs_total: 1, complete: true}
```

RoboRev job 266 completed at the exact product tip with verdict PASS and output `SEVERITY_THRESHOLD_MET`; this observation is evidence only and does not replace fresh validation or delivery authority.

## Stage Report: implementation

- DONE: Replace ambient package walking with one exact-revision tracked snapshot shared by candidate and published digest plus installation.
  Commit `278095b` routes candidate and published identity plus both installers through one safely extracted `git archive`; bypassing the snapshot would fail the shared-source assertions.
- DONE: Add the v2.5.0 ignored-file regression, tracked-byte positive control, candidate/published parity, and retained mismatch/no-model negatives.
  The focused test recreates both `*.cpython-314.pyc` paths, proves the old ambient digest diverges, proves tracked-byte changes alter snapshot identity, and would fail if either mode installs outside `snapshot` or published mode invokes a host.
- DONE: Run the focused and contract suites, report the exact diff against the 2-file/180-line/120-scaffolding stop numbers, and commit only task-owned files.
  Exact tip `278095b` passes the focused smoke, contract suite, Python compilation, and `git diff --check`; the diff is 2 files, 180 gross lines, and 99 gross test/FakeSmokeRuntime scaffolding lines.

### Summary

Candidate and published release smoke now derive digest and installation from the same exact-revision tracked package snapshot, leaving ignored and untracked worktree bytes untouched and excluded. The two task-owned files are committed at `278095b`; receipt schemas, mismatch refusals, provider behavior, and v2.5.0 evidence remain unchanged.

## Stage Report: validation

- DONE: Independently bind base 844edfa75a021cc6c013186bb88fba81f598f912 and candidate 278095b3015a25bb7140e7dd2b09482d96fc412a, inspect the exact two-file diff, and map AC-1 through AC-4 to falsifiers.
  Candidate `278095b` is one commit atop base `844edfa`; the 2-file/180-line diff stays within scope. AC-1 fails on ignored-byte influence or tracked-byte insensitivity; AC-2 on non-snapshot digest/install input or parity drift; AC-3 on loss of ambient divergence or snapshot equality; AC-4 on an accepted mismatch or published host/model invocation.
- DONE: Run the focused and contract suites plus Python compilation and git diff check, including the ignored-file old-mechanism negative control, tracked-byte positive control, candidate/published parity, mismatch refusals, and zero model invocation.
  Focused smoke and `kc-dev-flow-contract-test.py` passed; `py_compile` and exact-range `git diff --check` exited 0. The focused suite would fail if the two incident bytecode files stopped changing the ambient walk, a tracked byte stopped changing snapshot identity, either mode bypassed `snapshot`, a mismatch passed, or published mode invoked a host; an independent archive listing also matched all 53 tracked package files.
- DONE: Record review disposition, material residuals, rollback or forward-recovery readiness, operational ownership, provider-feedback state, and whether the exact candidate is ready for Captain release authorization; write the validation Stage Report without modifying product files.
  Deterministic-only review is sufficient because Git archive, byte identity, install readback, mismatch refusal, and archive-traversal safety are directly exercised; no material residual remains in scope. Revert `278095b` plus reinstate the release block is rollback, snapshot-helper repair is forward recovery, and the release owner owns receipt/install-drift monitoring. RoboRev job 266 is corroborating PASS evidence only; no PR exists for this head, so no PR provider feedback is pending. Exact candidate `278095b` is ready for Captain release authorization, which has not yet been granted; CI cost is unchanged and was not remeasured.

### Summary

Fresh Production validation passed at exact candidate `278095b` against base `844edfa` with no product-file changes or material residuals. The candidate is ready for the Captain's release-authorization gate; publication, merge, and terminalization remain deliberately unperformed.
