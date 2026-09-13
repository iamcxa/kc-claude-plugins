---
title: "kc-dev-flow ships the adopter contract test and its CI recipe; adopters keep a wrapper, not a copy"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r3
sprint-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: t12w6e29mdcnrc4chs9ps27e
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

* **AC-1** `python3 <installed>/scripts/adopter-contract-test.py --repo <fixture adopter>` exits 0 on a conforming fixture and non-zero naming the row/block/body on three mutated fixtures.
* **AC-2** Running it against this repository's own `docs/dev` exits 0.
* **AC-3** The adopt-dev-flow recipe, followed verbatim in a fixture adopter, yields a CI job whose failure is a hard input to the adopter's required gate (documented check, with the bootstrap caveat for path-classified pipelines).
* **AC-4** `kc-dev-flow-contract-test.py` and `pr-merge-portable-delivery.test.py` exit 0; the manifest lists the new resource.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: Gap exposed by the first outside adopter's refit; falsifier is the fixture adopter passing and failing for the named reasons with only a three-line wrapper.
  obligations:
    architecture: [Package-owned check; adopter carries a wrapper and a CI job only]
    implementation: [adopter-contract-test.py; manifest entry; adopt-dev-flow recipe; MIGRATION fix]
    testing: [AC-1..AC-4]
  scope_boundary: No Spacedock edit; no adopter-side copies; no Linear.
  semantics_unchanged: false
  poc_decision: whether one package-shipped check can replace per-adopter copies across the fleet
  poc_falsifier: an adopter needs repository-specific logic the shipped check cannot express
  poc_budget: one worker, one PR
  poc_stop_when: AC-1..AC-4 pass at one commit
  poc_artifact: retained
  poc_safety_boundary: kc-dev-flow/, scripts/ tests, fixtures
  poc_decision_ready_minutes: 15
```
