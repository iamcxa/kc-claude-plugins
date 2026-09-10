---
title: "ship-flow POC: remove every station that duplicates a kc-dev-flow or Spacedock mechanism"
status: implementation
source:
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper
sprint-readiness: ready
started: 2026-09-10T08:58:02Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-ship-remove-duplicated-stations
issue:
pr:
mod-block:
id: pzg36pjjn7tvtdtknpv9w82h
gates:
    version: 1
    records:
        - id: gate:pzg36pjjn7tvtdtknpv9w82h:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:pzg36pjjn7tvtdtknpv9w82h-backlog-1
              briefing:
                id: briefing:pzg36pjjn7tvtdtknpv9w82h:backlog:attempt-1:revision-1
                digest: sha256:186f1b0de69b5ee65c483bf030a7d9a60e164a6154d5835f3c90395a691628f2
                room-ref: ./ship-remove-duplicated-stations/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:pzg36pjjn7tvtdtknpv9w82h:backlog:1
                briefing: briefing:pzg36pjjn7tvtdtknpv9w82h:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T08:49:44.707214Z"
                decision: approve
                reason: 'Captain approved in chat: approve 2026-09-10'
              application:
                target-stage: ideation
                state: consumed
---

Under the Captain's 2026-09-10 ruling (design:
`docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md`, section "What leaves
kc-ship-flow"), anything kc-dev-flow or Spacedock already does per task leaves kc-ship-flow.
Today the plugin carries per-task acceptance (`accept-evidence.sh`, `without-it.sh`), PR opening
(`open-pr.sh`), review disposition (`disposition.py`, `ci-covers.sh`), merging
(`merge-station.sh`), two debrief writers, a channel notifier, per-station pins and the fixtures
and contract-test cases that exercise them.

## Accepted outcome

The scripts, station docs, fixtures, schema files and `contract-test.py` cases named in the
spec's removal table are deleted in one PR; `kc-ship-flow/references/kernel.md`,
`references/placement.tsv` and `docs/ship/README.md` describe only the five remaining stages;
what stays is `e2e-gate.py`, `e2e-cli.sh`, `uat-doc.py`, the claim fence, the close-receipt
schema, `local-profile-check.py`, `pin.py` (batch-level only) and the two scripts from the
dispatch-and-watch task. Every `## Ship-flow runtime` prose segment still has a destination or
an explicit residual.

## Non-goals

* Slimming `uat-doc.py` or the close receipt (third task).
* Touching kc-dev-flow, kc-pr-flow or Spacedock.
* Deleting the 17 fixtures that pin real SHAs without listing each under `without-it unanswered`
  in the PR body when its station survives.

## Acceptance criteria

* **AC-1** `python3 kc-ship-flow/scripts/contract-test.py` exits 0 at the candidate SHA, and `git grep -l -E 'accept-evidence|open-pr\.sh|disposition\.py|merge-station|ci-covers|dev-debrief|ship-debrief|notify\.sh|without-it\.sh' -- kc-ship-flow docs/ship` prints nothing.
* **AC-2** `python3 kc-ship-flow/scripts/prose-placement-check.py` exits 0 at the candidate SHA.
* **AC-3** `bash scripts/marketplace-verify.sh` and `bash scripts/skill-frontmatter-lint.sh` exit 0 at the candidate SHA.
* **AC-4** The PR body lists under `without-it unanswered` every retained fixture that pins a real commit SHA, with its path.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [shape, build, verify-deliver]
  basis: Removal PR inside the fifth ship-flow POC; the falsifier is that nothing remaining re-implements a dev-flow mechanism, checked by grep and by the remaining contract tests. Delivered through the cloud wrapper itself as its first real batch.
  obligations:
    architecture: [Deletion only plus the prose that names the five stages; no new mechanism]
    implementation: [One PR; removal table from the spec applied verbatim; placement.tsv rows re-pointed or marked residual]
    testing: [AC-1 to AC-3 at the candidate SHA; AC-4 read from the PR body]
  scope_boundary: No change to what the remaining scripts do; no kc-dev-flow edit; no Linear.
  semantics_unchanged: false
```
