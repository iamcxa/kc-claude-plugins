---
title: "pr-merge extension text matches Spacedock 0.27: drop the 0.26 clause that forbids gate consume and merge guard --rework"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r4
sprint-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: jyq89ta78a5kjbn2ffcc7kxs
---

`kc-dev-flow/references/pr-merge-extension.md` (canonical since #414, synced byte-for-byte into
every adopter's `_mods/pr-merge.md`) still says "This extension backports only the parts
executable by installed Spacedock 0.26. Do not use the 0.27-only commands named `spacedock gate
consume` or `merge guard --rework`". Every adopter in the fleet runs Spacedock 0.27.x (this
repository 0.27.2; qnow's Conductor image requires 0.27.2), this repository's own first officer
uses `gate consume` daily, and the released 0.27 hook's closed-PR recovery requires `--rework`.
Codex flagged the contradiction on iamcxa/qnow#1184 (2026-09-12); the adopter cannot edit the
block because its contract test enforces byte identity.

## Accepted outcome

The extension names the Spacedock version range it is written for (0.27.x), removes the 0.26
prohibition and the pre3 backport framing, keeps every override that still applies, and states
the closed-PR recovery path as the released hook defines it. The synced block in this repository
and the portable-delivery test are updated together; `kc-dev-flow-contract-test.py` still passes.

## Non-goals

* Editing any Spacedock file or the released body.
* Changing the Residuals / without-it sections.
* Any Linear read or write.

## Acceptance criteria

* **AC-1** `grep -n -E '0\.26|do not use the 0\.27-only' kc-dev-flow/references/pr-merge-extension.md` prints nothing; the file names 0.27 as the supported range.
* **AC-2** `python3 scripts/kc-dev-flow-contract-test.py` and `python3 scripts/pr-merge-portable-delivery.test.py` exit 0; block==resource byte-for-byte.
* **AC-3** A fixture adopter on Spacedock 0.27.0 (qnow-shaped released body) renders the extension without a 0.26 clause.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: Text defect in a canonical resource found by the first non-kc adopter's review; falsifier is the grep and the two tests.
  obligations:
    architecture: [Resource text only; overrides unchanged in effect]
    implementation: [edit resource; sync block; update tests]
    testing: [AC-1..AC-3]
  scope_boundary: No Spacedock edit; no section changes; no Linear.
  semantics_unchanged: false
  poc_decision: whether the extension can be stated for 0.27.x without losing any override
  poc_falsifier: an override that only exists because of the 0.26 backport framing turns out to be load-bearing
  poc_budget: one worker, one PR
  poc_stop_when: AC-1..AC-3 pass at one commit
  poc_artifact: retained
  poc_safety_boundary: kc-dev-flow/references, docs/dev/_mods/pr-merge.md, scripts/ tests
  poc_decision_ready_minutes: 15
```
