---
title: "kc-dev-flow pins the released pr-merge body per Spacedock mod version, not one repository's copy"
status: implementation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r3
sprint-readiness: ready
started: 2026-09-14T13:47:42Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-pr-merge-released-body-pin-per-mod-version
issue:
pr:
mod-block:
id: thvp8qgzr3eb1va9st822n2d
gates:
    version: 1
    records:
        - id: gate:thvp8qgzr3eb1va9st822n2d:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:thvp8qgzr3eb1va9st822n2d-backlog-1
              briefing:
                id: briefing:thvp8qgzr3eb1va9st822n2d:backlog:attempt-1:revision-1
                digest: sha256:094d0d0043b8f7db3324312bbfa869599c3e2ad136d97ebe266277a0cdac9258
                room-ref: ./pr-merge-released-body-pin-per-mod-version/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:thvp8qgzr3eb1va9st822n2d:backlog:1
                briefing: briefing:thvp8qgzr3eb1va9st822n2d:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T13:45:33.005725Z"
                decision: approve
                reason: 'batch admission: the Captain approved the five-task r3 batch; ship FO records on the batch conn'
                conn:
                    quote: 准
                    source: Captain chat 2026-09-14, approving the ship-cloud-wrapper-r3 batch of five (pilot profile)
              application:
                target-stage: ideation
                state: consumed
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

## Stage Report: implementation

- DONE: Add pr_merge_released_bodies table to kc-dev-flow/contract-manifest.json keyed by Spacedock mod version (at least 0.12.3 and 0.27.0), each entry hashed from the mod exactly as Spacedock released it, never an adopter's edited copy.
  commit 44d478f8; 0.12.3 hash reused unchanged from the retired singular pin; 0.27.0 hash computed from the cached spacedock plugin's pristine `mods/pr-merge.md` (version: 0.27.0, no adopter marker present) at `/home/vercel-sandbox/.claude/plugins/cache/spacedock/spacedock/0.27.2/mods/pr-merge.md`.
- DONE: Change the adopter contract-test recipe to read the adopter mod's frontmatter version: and enforce that row, failing by name ("mod version X not pinned by kc-dev-flow Y; add its released hash") when the version is absent from the table, instead of skipping; update adopt-dev-flow docs and references/pr-merge-extension.md to name the table as the enforcement point.
  `check_pr_merge_released_body()` in scripts/kc-dev-flow-contract-test.py reads `version:` from the mod's own frontmatter and looks up that row; a manual run against the unpinned fixture printed exactly `kc-dev-flow contract: mod version 9.9.9 not pinned by kc-dev-flow 4.5.0; add its released hash` and exited 1. `references/pr-merge-extension.md` and `docs/dev/_mods/pr-merge.md`'s synced block (byte-identical, per the existing drift check) now name `pr_merge_released_bodies`; `adopt-dev-flow/SKILL.md` documents adding a version row and the `--check-pr-merge-released-body` recipe.
- DONE: Add fixtures for both pinned mod versions (0.12.3 and 0.27.0); python3 scripts/kc-dev-flow-contract-test.py and pr-merge-portable-delivery.test.py both exit 0, and a one-word edit to either released body fails naming the body and version.
  Fixtures at scripts/fixtures/pr-merge-released-body/{adopter-0.12.3,adopter-0.27.0,adopter-unpinned}-pr-merge.md. A new self-test block in kc-dev-flow-contract-test.py runs `--check-pr-merge-released-body` (the adopter recipe, via subprocess) against each: both pinned fixtures pass; a `" the "→" teh "` one-word mutant of each released-body prefix fails with `released Spacedock pr-merge body ... at version {0.12.3|0.27.0}`; the unpinned fixture (version 9.9.9) fails with the not-pinned message. Both `python3 scripts/kc-dev-flow-contract-test.py` and `python3 scripts/pr-merge-portable-delivery.test.py` exit 0 (verified locally after `pip install jsonschema`, a pre-existing unrelated environment dependency the close-receipt sub-suite needs).

### Summary

Replaced the single `pr_merge_released_body.sha256` pin with a `pr_merge_released_bodies` table keyed by Spacedock mod version, so kc-claude-plugins' own 0.12.3 copy and any other adopter's version (0.27.0 confirmed via the cached Spacedock 0.27.2 plugin's pristine mod) are each guarded by their own released-body hash instead of one value describing the whole fleet. The contract test now fails by name on an unpinned version rather than skipping, and a new `--check-pr-merge-released-body ROOT` mode is the documented, fixture-tested adopter recipe for verifying that row standalone.
