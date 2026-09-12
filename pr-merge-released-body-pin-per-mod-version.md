---
title: "kc-dev-flow pins the released pr-merge body per Spacedock mod version, not one repository's copy"
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
id: thvp8qgzr3eb1va9st822n2d
---

`kc-dev-flow/contract-manifest.json` (4.4.0, #414) pins `pr_merge_released_body.sha256` to one
value: the released Spacedock pr-merge body as it sits in kc-claude-plugins' own
`docs/dev/_mods/pr-merge.md` (mod frontmatter `version: 0.12.3`, 10551 bytes). The first other
adopter to sync the extension (qnow, 2026-09-12, task `refit-kc-dev-flow-4-4-0` on its state
branch) carries the released mod at `version: 0.27.0` (16640 bytes); its adopter contract test
fails on the pin although its body is exactly what Spacedock shipped. One sha cannot describe
"the released body" across adopters on different Spacedock mod versions; the qnow test now skips
the check with a named residual when versions differ, which leaves that adopter's body unguarded.

## Accepted outcome

The manifest pins a table `pr_merge_released_bodies: {"<mod version>": {"sha256", "bytes"}}`
holding every Spacedock pr-merge mod version an adopter in the fleet runs (at least 0.12.3 and
0.27.0, each hashed from the mod as Spacedock released it, not from an adopter's edited copy);
the adopter contract-test recipe reads the adopter mod's frontmatter `version:` and enforces that
row, failing by name when the version is absent from the table ("mod version X not pinned by
kc-dev-flow Y; add its released hash") rather than skipping. `adopt-dev-flow` documents how to add
a version. The prose in `references/pr-merge-extension.md` names the table as the enforcement point.

## Non-goals

* Editing any Spacedock file or the released mod bodies.
* Changing the extension block's content.
* Any Linear read or write.

## Acceptance criteria

* **AC-1** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 in kc-claude-plugins (mod 0.12.3) and, run through the documented adopter recipe against a fixture adopter carrying the released 0.27.0 body, exits 0; a one-word edit in either body fails naming the body and its version.
* **AC-2** A fixture adopter whose mod `version:` is absent from the table fails with the "not pinned" message and exits non-zero.
* **AC-3** `pr-merge-portable-delivery.test.py` exits 0; the released bodies' bytes in both fixtures are unchanged.
* **AC-4** `references/pr-merge-extension.md` and the synced adopter block name the table; block==resource byte-for-byte still holds.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: Defect found by the first non-kc adopter to sync the 4.4.0 extension; falsifier is the two-adopter fixture pair passing and failing for the named reason.
  obligations:
    architecture: [Pin table keyed by mod version; adopter test reads the mod's own version]
    implementation: [manifest table; recipe change; adopt-dev-flow doc; fixtures for 0.12.3 and 0.27.0]
    testing: [AC-1..AC-4 at the candidate]
  scope_boundary: No Spacedock edit; no extension content change; no Linear.
  semantics_unchanged: false
  poc_decision: whether one manifest can guard the released body for every adopter in the fleet
  poc_falsifier: a released 0.27.0 body fixture still fails or passes for the wrong reason
  poc_budget: one worker, one PR
  poc_stop_when: AC-1..AC-4 pass at one commit
  poc_artifact: retained
  poc_safety_boundary: kc-dev-flow/, docs/dev/_mods/pr-merge.md, scripts/ tests only
  poc_decision_ready_minutes: 15
```
