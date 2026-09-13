---
title: "pr-merge extension: separate canonical overrides from kc-claude-plugins' local delivery policy, and fix the five defects Codex found on an adopter"
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
id: f9gct7j0trfpg78x9nqj76rb
---

#414 made the whole `docs/dev/_mods/pr-merge.md` extension of kc-claude-plugins canonical
(`references/pr-merge-extension.md`, synced byte-for-byte into adopters). That block carries
kc-claude-plugins' own delivery topology policy (native `gh stack` stacks, parallel Draft PRs,
`gh pr checks --required` completion proof, base approval by SHA) next to the overrides every
adopter needs (Draft delivery, split-root audit link, Residuals/without-it). Codex reviewed the
first outside adopter's sync (iamcxa/qnow#1184, 2026-09-13) and found five defects in that
policy as it lands there: (1) `gh stack` is not installed in the Conductor cloud image the
adopter targets, yet the block forbids merging a layer individually; (2) layers are created
`--draft` and then wait for CI, but the adopter's CI only classifies non-draft PRs, so readiness
deadlocks; (3) `gh pr checks --required` on a sibling-based layer can return an empty required
set, so a red layer passes completion; (4) parallel independent PRs are mandated while the entity
stores one scalar `pr`; (5) nothing re-validates the approved base SHA against the remote branch
tip before `gh pr create --base <branch>`.

## Accepted outcome

`references/pr-merge-extension.md` contains only the overrides every adopter needs (Draft
delivery, split-root audit link, Residuals / without-it sections, Spacedock 0.27 recovery path);
the delivery topology policy moves to a kc-claude-plugins-local extension file outside the synced
block, and the five defects are fixed where that policy is kept: readiness before CI wait, an
explicit `ci-gate` status query per exact layer head, a durable multi-PR receipt or the removal
of the parallel-PR row, base re-resolution immediately before PR creation, and a documented
fallback when `gh stack` is absent. The synced block in this repository, the portable-delivery
test and the contract test are updated together.

## Non-goals

* Editing Spacedock's released body.
* Changing adopters' local policy for them.
* Any Linear read or write.

## Acceptance criteria

* **AC-1** `git grep -n -E 'gh stack|stack layer|parallel Draft PRs|--required' kc-dev-flow/references/pr-merge-extension.md` prints nothing; those rules exist only in the kc-claude-plugins-local file.
* **AC-2** A fixture adopter with a draft-only-classifies CI reaches merge readiness following the local policy (readiness first, then exact-head `ci-gate`); a red sibling-based layer fails completion by name.
* **AC-3** `scripts/kc-dev-flow-contract-test.py` and `scripts/pr-merge-portable-delivery.test.py` exit 0; block==resource byte-for-byte after the sync.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: Five verified defects reported by a reviewer on the first outside adopter; falsifier is the fixture adopter passing and the red layer failing by name.
  obligations:
    architecture: [Canonical block = shared overrides only; local policy stays local]
    implementation: [split the resource; fix the five defects in the local policy; update tests and sync]
    testing: [AC-1..AC-3]
  scope_boundary: No Spacedock edit; no adopter edits; no Linear.
  semantics_unchanged: false
  poc_decision: whether the canonical extension can be reduced to shared overrides without losing any adopter-facing rule
  poc_falsifier: an adopter-facing rule turns out to depend on the delivery topology policy
  poc_budget: one worker, one PR
  poc_stop_when: AC-1..AC-3 pass at one commit
  poc_artifact: retained
  poc_safety_boundary: kc-dev-flow/references, docs/dev/_mods, scripts/ tests
  poc_decision_ready_minutes: 15
```
