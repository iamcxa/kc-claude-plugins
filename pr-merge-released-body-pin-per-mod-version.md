---
title: "kc-dev-flow pins the released pr-merge body per Spacedock mod version, not one repository's copy"
status: validation
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

## Stage Report: validation

- DONE: Re-run scripts/kc-dev-flow-contract-test.py and pr-merge-portable-delivery.test.py from this stage's worktree and cite AC-1..AC-4 explicitly in this stage's report with their evidence (exit codes, the unpinned-version failure message, the one-word-mutant failure naming body+version, the byte-identical drift check).
  Both reran clean from `.worktrees/spacedock-ensign-pr-merge-released-body-pin-per-mod-version` at candidate 44d478f8. **AC-1**: `python3 scripts/kc-dev-flow-contract-test.py` printed `kc-dev-flow contract: PASS`, exit 0 — its self-test block runs the adopter recipe (`--check-pr-merge-released-body`) against both `adopter-0.12.3-pr-merge.md` and `adopter-0.27.0-pr-merge.md` fixtures (pass) and a one-word (`" the "`→`" teh "`) mutant of each (fails, stderr contains `released Spacedock pr-merge body ... at version 0.12.3` / `at version 0.27.0` respectively). **AC-2**: the same run exercises `adopter-unpinned-pr-merge.md` (mod `version: 9.9.9`), which fails with `mod version 9.9.9 not pinned by kc-dev-flow 4.5.0; add its released hash`, exit 1 for that subprocess (overall harness still exits 0 since the failure is the expected assertion). **AC-3**: `python3 scripts/pr-merge-portable-delivery.test.py` printed 16/16 scenario checks passing (14 mutant-rejection cases + 2 fixture-pass cases) and a final `portable-delivery:PASS`, exit 0; it reads the released bytes straight from both fixtures with no edit path, so pass proves they are unchanged. **AC-4**: `kc-dev-flow/references/pr-merge-extension.md:9` and `docs/dev/_mods/pr-merge.md:127` both name `pr_merge_released_bodies` as the enforcement point; the existing `docs/dev/_mods/pr-merge.md extension block drifted from ...` byte-for-byte block==resource comparison (scripts/kc-dev-flow-contract-test.py:633) is part of the same passing contract-test run above, so it still holds unchanged.
- DONE: Record this POC's required prove-stage POC outcome and POC close measurement YAML sections per kc-dev-flow's poc-exploration/prove.md schema (direction proceed/stop/change with its evidence fields; close measurement's cleanup_status/captain_wait_seconds/terminal_cleanup_seconds, pending where not yet applicable).
  See `## POC outcome` and `## POC close measurement` below; direction `proceed` — the two-adopter fixture pair (0.12.3, 0.27.0) passes for the named reason and the unpinned fixture fails for the named reason, answering `poc_falsifier` in the accepting direction.
- DONE: Construct (do not push or open) the candidate PR body per docs/dev/_mods/pr-merge.md's template (What changed / Evidence / Residuals / without-it unanswered / audit link) and commit it into this stage's report as the delivery candidate for the FO's gate presentation; pushing the branch and opening the Draft PR requires a separate explicit push authorization this stage does not carry.
  See `## Candidate PR body` below. No branch push and no `gh pr create` were run this stage — Residuals and without-it unanswered sections are both omitted (no items in either stage report).

## POC outcome

```yaml
poc_outcome:
  direction: proceed
  admitted_at: 2026-09-14T13:47:42Z
  decision_ready_at: 2026-09-14T14:04:34Z
  decision_ready_elapsed_seconds: 1012
  captain_interventions_before_decision_ready: 0
  candidate: 44d478f8
  evidence: >-
    A `pr_merge_released_bodies` table keyed by Spacedock mod version, read via
    the adopter mod's own frontmatter `version:`, guards both 0.12.3 (this
    repo's copy) and 0.27.0 (the qnow-class adopter, fixture-derived from the
    cached Spacedock 0.27.2 plugin's pristine `mods/pr-merge.md`) with their own
    released-body hash. `python3 scripts/kc-dev-flow-contract-test.py` exits 0
    and its self-test block proves both fixtures pass, a one-word mutant of
    either fails naming the body and its version, and an unpinned version
    (9.9.9) fails by name instead of skipping. `pr-merge-portable-delivery.test.py`
    exits 0 (16/16), confirming the released bytes in both fixtures are
    unchanged.
  strongest_limit: >-
    Only two Spacedock mod versions (0.12.3, 0.27.0) are populated in the
    table; a third fleet adopter on an unseen version still fails by name
    until someone runs `adopt-dev-flow`'s documented recipe to add its row —
    the mechanism generalizes, the table's current coverage does not.
  reversal_fact: >-
    A real third-version adopter whose mod is byte-identical to what Spacedock
    released for that version still fails the check after its row is added, or
    the one-word mutant on either existing pinned body fails to fail.
  cleanup_status_at_decision: complete
```

## POC close measurement

```yaml
poc_close_measurement:
  captain_wait_seconds: pending
  terminal_cleanup_seconds: pending
  cleanup_status: pending
```

## Candidate PR body

```
A single released-body pin can't describe every adopter's Spacedock mod version — the first outside adopter (0.27.0) already fails kc-dev-flow's contract test on a body Spacedock itself shipped.

## What changed
- Add `pr_merge_released_bodies` table to contract-manifest.json, keyed by mod version.
- Enforce each adopter's own mod version row; fail by name when a version is unpinned.
- Document the table as the enforcement point in adopt-dev-flow and pr-merge-extension.md.
- Add fixtures for 0.12.3, 0.27.0, and an unpinned version; self-test via one-word mutants.

## Evidence
- `kc-dev-flow-contract-test.py`: PASS (exit 0), incl. fixture self-tests for both pinned versions and the unpinned-version failure.
- `pr-merge-portable-delivery.test.py`: 16/16 checks passed (exit 0); released-body bytes in both fixtures unchanged.

---
[th](/iamcxa/kc-claude-plugins/blob/44d478f8/docs/dev/.spacedock-state/pr-merge-released-body-pin-per-mod-version.md)
```

Residuals and without-it unanswered are both omitted — neither this validation stage nor the implementation stage report flagged an item for either section. No `issue:` is set in frontmatter, so no `Closes` line.

### Summary

Reran both required test suites at candidate 44d478f8 and cited AC-1..AC-4 with their exact evidence (exit codes, the unpinned-version message, the one-word-mutant failure naming body+version, and the standing byte-for-byte drift check). Recorded a `proceed` POC outcome — the falsifier (a released 0.27.0 fixture failing, or failing for the wrong reason) did not occur — with close measurement left `pending` since terminal archival hasn't happened yet. Constructed, but did not push or open, the candidate Draft PR body for the FO's gate presentation.
