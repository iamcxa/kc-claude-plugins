---
title: "kc-dev-flow ships the adopter contract test and its CI recipe; adopters keep a wrapper, not a copy"
status: validation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r3
sprint-readiness: ready
started: 2026-09-14T13:49:19Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-adopter-contract-test-ships-with-the-package
issue:
pr: 450
mod-block:
id: t12w6e29mdcnrc4chs9ps27e
gates:
    version: 1
    records:
        - id: gate:t12w6e29mdcnrc4chs9ps27e:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:t12w6e29mdcnrc4chs9ps27e-backlog-1
              briefing:
                id: briefing:t12w6e29mdcnrc4chs9ps27e:backlog:attempt-1:revision-1
                digest: sha256:3d1f9b27facc41f36f170d81c8312ec4a4e04292928f68ec23ac543682889968
                room-ref: ./adopter-contract-test-ships-with-the-package/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:t12w6e29mdcnrc4chs9ps27e:backlog:1
                briefing: briefing:t12w6e29mdcnrc4chs9ps27e:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T13:45:26.633386Z"
                decision: approve
                reason: 'batch admission: the Captain approved the five-task r3 batch; ship FO records on the batch conn'
                conn:
                    quote: 准
                    source: Captain chat 2026-09-14, approving the ship-cloud-wrapper-r3 batch of five (pilot profile)
              application:
                target-stage: ideation
                state: consumed
        - id: gate:t12w6e29mdcnrc4chs9ps27e:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:t12w6e29mdcnrc4chs9ps27e-ideation-1
              briefing:
                id: briefing:t12w6e29mdcnrc4chs9ps27e:ideation:attempt-1:revision-1
                digest: sha256:6c052a4dd49d892d7c47c762e2b174c4874df25c113ca8a9aa4324f5de3a5d30
                room-ref: ./adopter-contract-test-ships-with-the-package/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:t12w6e29mdcnrc4chs9ps27e:ideation:1
                briefing: briefing:t12w6e29mdcnrc4chs9ps27e:ideation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T14:02:46.749846Z"
                decision: approve
                reason: 'ideation read by the ship FO: profile reconciled to pilot per batch conn; AC-1..4 as verified-by/falsified-by pairs. Enter implementation.'
                conn:
                    quote: 准
                    source: Captain chat 2026-09-14, approving the ship-cloud-wrapper-r3 batch of five (pilot profile)
              application:
                target-stage: implementation
                state: consumed
        - id: gate:t12w6e29mdcnrc4chs9ps27e:validation
          stage: validation
          attempts:
            - id: gate-attempt:t12w6e29mdcnrc4chs9ps27e-validation-1
              briefing:
                id: briefing:t12w6e29mdcnrc4chs9ps27e:validation:attempt-1:revision-1
                digest: sha256:3ed91701ff3a02cd6b7c8a2960bc6b0f483522396d459d11b959ddab95046620
                room-ref: ./adopter-contract-test-ships-with-the-package/review/validation/briefing-1
---

`kc-dev-flow/MIGRATION.md` speaks of `scripts/kc-dev-flow-contract-test.py` as if every adopter
has one, but the package ships none; kc-claude-plugins' own script is a 1500-line plugin-development
suite, not an adopter check. The first outside adopter to refit (qnow, PR #1184, 2026-09-12/13)
hand-wrote a 251-line copy plus a CI job, took three Codex/FO correction rounds on it, and the
Captain then removed it (「拿掉」 2026-09-13): a guard that belongs to the package must not be
maintained per product repository, and the installed loader already fails closed at dispatch.

## Accepted outcome

The package ships `scripts/adopter-contract-test.py` as a runtime resource: read-only, checks the
adopter's marked Local Profile rows against `kc-dev-flow-local-profile/v1`, the `_mods/pr-merge.md`
extension block byte-for-byte against `references/pr-merge-extension.md`, the released body
against the per-mod-version pin table (see `pr-merge-released-body-pin-per-mod-version`), and
leftover byte-identical copies under `docs/dev`. `adopt-dev-flow` documents a CI recipe
(pinned-tag sparse clone of this repository, `KC_DEV_FLOW_ROOT`, one job wired into the adopter's
required gate) and a three-line adopter wrapper. MIGRATION.md's reference is corrected to the
installed script.

## Non-goals

* Running the package's own test suites from an adopter.
* Editing any Spacedock file.
* Any Linear read or write.

## Acceptance criteria

**AC-1 — `python3 <installed>/scripts/adopter-contract-test.py --repo <fixture adopter>` exits 0 on a conforming fixture and non-zero naming the row/block/body on three mutated fixtures.**
Verified by: running the script against a checked-in conforming fixture adopter directory and asserting exit 0; then against three separately mutated copies of that fixture — one with a marked Local Profile row edited, one with the `_mods/pr-merge.md` extension block diverged from `references/pr-merge-extension.md`, one with the released body diverged from its `pr-merge-released-body-pin-per-mod-version` entry — each asserting non-zero exit and a failure message that names the specific row, block, or body that diverged. Falsified by: any of the four runs producing an exit code that does not match its fixture's conformance, or a non-zero exit whose message does not name the diverged artifact.

**AC-2 — Running it against this repository's own `docs/dev` exits 0.**
Verified by: invoking the installed script against this repository's own `docs/dev` checkout and asserting exit 0 — proving kc-claude-plugins itself conforms to the shape the shipped check enforces on outside adopters. Falsified by: a non-zero exit against this repository's current `docs/dev`.

**AC-3 — The adopt-dev-flow recipe, followed verbatim in a fixture adopter, yields a CI job whose failure is a hard input to the adopter's required gate.**
Verified by: standing up a fixture adopter repository, following the documented recipe exactly as written (pinned-tag sparse clone of this repository, `KC_DEV_FLOW_ROOT`, one CI job) with no undocumented step, then mutating a marked Local Profile row and observing the CI job fail with the fixture adopter's required-gate/branch-protection status reflecting that failure — noting the bootstrap caveat for path-classified pipelines where the job cannot itself be required before it first runs. Falsified by: the recipe as documented producing a CI job that does not exist, does not fail on the mutation, or fails without being wired into the adopter's required gate.

**AC-4 — `kc-dev-flow-contract-test.py` and `pr-merge-portable-delivery.test.py` exit 0; the manifest lists the new resource.**
Verified by: running both existing test suites after `adopter-contract-test.py` is added and asserting exit 0 for each — proving the new script does not regress existing package guarantees — and reading the contract manifest to confirm it lists `scripts/adopter-contract-test.py` as a shipped resource. Falsified by: either suite regressing to non-zero, or the manifest omitting the new resource.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: Reconciled to the Captain's batch conn (Captain chat 2026-09-14, approving the ship-cloud-wrapper-r3 batch of five, pilot profile). The shipped check is not a disposable experiment — every adopter depends on it at refit time and it persists across the fleet; the first outside adopter's refit (qnow, PR #1184) already showed real use and iteration pressure (three correction rounds on a hand-copied version) before the Captain ordered it removed and centralized.
  obligations:
    architecture: [Package-owned check; adopter carries a wrapper and a CI job only]
    implementation: [adopter-contract-test.py; manifest entry; adopt-dev-flow recipe; MIGRATION fix]
    testing: [AC-1..AC-4]
  scope_boundary: No Spacedock edit; no adopter-side copies; no Linear.
  semantics_unchanged: false
  decision:
    authority: Captain (batch conn, ship-cloud-wrapper-r3 batch of five, pilot profile; recorded by agent:first-officer, gate:t12w6e29mdcnrc4chs9ps27e:backlog)
    at: "2026-09-14T13:45:26.633386Z"
```

## Stage Report: ideation

- DONE: Reconcile the Work profile receipt to pilot-product-slice per the Captain's batch conn ("pilot profile", Captain chat 2026-09-14) and record it via the existing safe transaction.
  Receipt rewritten in-place: `selected`/`recommended` -> `pilot-product-slice`, `route` -> `[shape, build, verify-deliver]` (matches `ROUTES["pilot-product-slice"]["ideation"] = (shape, implementation)` in `kc-dev-flow/scripts/profile-contract-loader.py`), poc_* fields dropped, `decision.authority`/`decision.at` added citing the backlog gate resolution already recorded on the entity (`gate:t12w6e29mdcnrc4chs9ps27e:backlog`, approved 2026-09-14T13:45:26.633386Z); obligations/scope_boundary/semantics_unchanged preserved unchanged since scope did not move.
- DONE: Record task-specific acceptance evidence (AC-1..AC-4 shape) as execution evidence for the shape stage.
  Rewrote `## Acceptance criteria` from flat bullets to the AC-N bold-heading + "Verified by: ... Falsified by: ..." shape (matching the pattern used in `prescan-coverage-honesty.md`), naming for each AC the concrete fixture/mutation exercised and the exact non-pass condition that would falsify it.

### Summary

Reconciled the stale POC-exploration receipt to Pilot/Product-slice per the Captain's already-recorded batch approval, and turned the four flat acceptance-criteria bullets into falsifiable execution evidence (Verified-by/Falsified-by pairs) so the `shape` stage has a concrete target rather than a checklist. No code, script, or manifest changes were made in this ideation pass; scope, obligations, and non-goals are unchanged from the original admission.

## Stage Report: implementation

- DONE: Ship scripts/adopter-contract-test.py (read-only) checking marked Local Profile rows, `_mods/pr-merge.md` extension-block byte parity, released-body pin, and leftover docs/dev copies.
  `kc-dev-flow/scripts/adopter-contract-test.py`; AC-1: `python3 kc-dev-flow/scripts/adopter-contract-test.test.py` exits 0, driving the conforming fixture plus 4 mutated copies (row, block, body, leftover-copy), each asserting non-zero exit and a stderr message naming the diverged artifact (`LOCAL_PROFILE`/`PR_MERGE_BLOCK`/`PR_MERGE_BODY`/`LEFTOVER_COPY`). AC-2: `python3 kc-dev-flow/scripts/adopter-contract-test.py --repo .` against this repository's own `docs/dev` exits 0 (commit c82ec84d).
- DONE: Document the adopt-dev-flow CI recipe (pinned-tag sparse clone, `KC_DEV_FLOW_ROOT`, one required-gate job) and a three-line adopter wrapper; correct MIGRATION.md's reference to the installed script.
  New `## CI recipe` section in `kc-dev-flow/skills/adopt-dev-flow/SKILL.md` (bullet list, not numbered, to avoid colliding with the contract test's whole-file adopter-step sequence check) names the sparse-clone command, `KC_DEV_FLOW_ROOT` export, required-gate wiring with the path-classified-job bootstrap caveat, and the 3-line wrapper. `kc-dev-flow/MIGRATION.md`'s 2026-08-21 note no longer implies every adopter has `scripts/kc-dev-flow-contract-test.py` (this repository's own 2630-line plugin-development suite); it now cites `load_installed_package()`'s `contract_digest` and the shipped `adopter-contract-test.py`'s leftover-copy check.
- DONE: Add scripts/adopter-contract-test.py to the contract manifest; kc-dev-flow-contract-test.py and pr-merge-portable-delivery.test.py exit 0.
  `kc-dev-flow/contract-manifest.json` `resources` gains `scripts/adopter-contract-test.py` and a new `pr_merge_released_body_pin_per_mod_version` table keyed by the pr-merge mod's own frontmatter `version:` (currently `"0.12.3"`, same sha256/bytes as the existing single pin) so a future mod-version bump is checked against its own pin rather than one frozen value. `scripts/kc-dev-flow-contract-test.py`'s script-role classification and manifest-resource-set assertion updated to include the two new files. `python3 scripts/kc-dev-flow-contract-test.py` -> `kc-dev-flow contract: PASS`; `python3 scripts/pr-merge-portable-delivery.test.py` -> `portable-delivery:PASS` (both exit 0, verified after installing the pre-existing missing `jsonschema` dependency the first suite's plan-flow check needs, unrelated to this change).

### Summary

Shipped the installed, read-only `adopter-contract-test.py` covering all four checks named in the Accepted outcome, reusing `profile-contract-loader.py`'s own `read_local_profile` for the row check so the two paths cannot drift. The released-body pin moved from a single frozen sha256 to a per-mod-version table, closing the gap the entity's own fixture exposed (the local mod's frontmatter already reads `0.12.3` while the extension prose still narrates `0.12.2`). Documented the CI recipe and wrapper in `adopt-dev-flow/SKILL.md` as a bullet list rather than a numbered one after the contract test's whole-file step-sequence check flagged a numbered list collision. Work committed on `spacedock-ensign/adopter-contract-test-ships-with-the-package` at c82ec84d; no Spacedock file touched, no Linear read or write.

## Stage Report: validation

- DONE: Re-run AC-1, AC-2, AC-4's regression suites at the exact candidate revision and record exit codes.
  At c82ec84d: `adopter-contract-test.test.py` -> `adopter-contract-test:PASS (1 conforming fixture + 4 mutation cases)` exit 0; `adopter-contract-test.py --repo .` against this repo's own `docs/dev` -> `ADOPTER_CONTRACT_OK` exit 0; `kc-dev-flow-contract-test.py` -> `kc-dev-flow contract: PASS` exit 0; `pr-merge-portable-delivery.test.py` -> `portable-delivery:PASS` exit 0 (all 4 REJECTED-labelled cases inside that suite are its own negative-fixture assertions, all correctly rejected).
- DONE: AC-3 — stand up a fixture adopter repo, follow the adopt-dev-flow CI recipe verbatim, mutate a marked Local Profile row, observe the CI job fail as a hard input to the required gate.
  Pushed the released conforming fixture (copied from `kc-dev-flow/scripts/fixtures/adopter-contract-test/conforming`) plus a wrapper (`scripts/kc-dev-flow-check.sh`, byte-identical to the recipe's documented wrapper) and a GitHub Actions job (sparse-clone + `KC_DEV_FLOW_ROOT`, no path filter) to a disposable orphan branch (`fixture/adopter-contract-r3`, now deleted) on this same public repo, since the sandbox's `gh` token cannot create a new repository (`GraphQL: Resource not accessible by integration`). Real run https://github.com/iamcxa/kc-claude-plugins/actions/runs/34861859207 passed on the conforming commit; after mutating `Installed contract interface` from `kc-dev-flow-local-profile/v1` to `.../v2`, real run https://github.com/iamcxa/kc-claude-plugins/actions/runs/34861970754 failed with the job log showing `LOCAL_PROFILE: LOCAL_PROFILE_REFIT_REQUIRED: ... Installed contract interface must be kc-dev-flow-local-profile/v1` and a `check-runs` API read on that commit confirming `{"name":"adopter-contract-test","conclusion":"failure"}` — the exact context name a branch-protection `required_status_checks` entry would reference. Since the sparse-clone pins a branch ref rather than a released tag (this change is not yet tagged) and per the task's own constraint no real SHA of this repository is embedded in the fixture, only the pre-release branch name is referenced, noted inline in the workflow file as a documented substitution. Residual: could not flip the check to "required" via API (`403 Resource not accessible by integration` on `PUT .../branches/.../protection` — the installed GitHub App lacks `administration:write`); the check-run mechanism that a required-gate setting would key off is verified end-to-end, the one-time admin toggle is not.
- DONE: Open the Draft PR through the pr-merge mod, citing the Captain's batch conn as Draft-creation authorization.
  See the Draft PR linked from this entity's `pr` field; body built via the mod's split-root-corrected canonical Draft delivery unit (release-body byte parity untouched by this stage).

### Summary

Re-ran all three regression suites plus the manifest read at revision c82ec84d — all exit 0, unchanged from implementation. Exercised AC-3 for real: a disposable branch on this same public repo (no throwaway repo could be created with the sandbox's token) ran the documented recipe's GitHub Actions job, passing on a conforming fixture and failing with the exact diverged-row message on a mutated one; the one piece not exercised is flipping "required" in branch protection, blocked by the token's missing admin scope rather than by any gap in the recipe or the check itself. Opened the Draft PR under the Captain's already-recorded batch conn.
