---
title: "kc-dev-flow ships the adopter contract test and its CI recipe; adopters keep a wrapper, not a copy"
status: ideation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r3
sprint-readiness: ready
started: 2026-09-14T13:49:19Z
completed:
verdict:
worktree:
issue:
pr:
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
