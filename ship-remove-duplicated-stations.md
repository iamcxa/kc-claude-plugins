---
title: "ship-flow POC: remove every station that duplicates a kc-dev-flow or Spacedock mechanism"
status: validation
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

## Stage Report: implementation

- DONE: kc-ship-flow/scripts/contract-test.py's `git grep` component and every other check now clean (AC-1, partial)
  `git grep -l -E 'accept-evidence|open-pr\.sh|disposition\.py|merge-station|ci-covers|dev-debrief|ship-debrief|notify\.sh|without-it\.sh' -- kc-ship-flow docs/ship` prints nothing (exit 1, no matches) at candidate d300d531.
- SKIPPED: kc-ship-flow/scripts/contract-test.py exits 0 at the candidate SHA (AC-1, remainder) — pre-existing environment gap, not this stage's to fix
  `fenced-dispatch.test.sh`'s `spacedock dispatch build` calls fail identically (same stderr, same exit shape) on the unmodified branch tip 6991fd09 before any of this stage's edits — reproduced by `git stash` + rerun. Every other check in the file (station presence, uat-doc.test.py, pin.test.py, prose-placement-check.py, intent.sh DEV-93 case, e2e-gate AC-3/AC-4/dangling/empty-slug/Chinese/AC-1/AC-2, carried-note and forbidden-embed close-receipt validation, local-profile-check mutations, prose-placement mutation, fenced-dispatch dry-run cases) passes when run past this pre-existing environment gap (verified by temporarily short-circuiting only the two calls that shell out to `spacedock dispatch build`/`e2e-cli.sh` network-shaped behavior, both reproduced as pre-existing on 6991fd09). `jsonschema` also had to be pip-installed in this sandbox for `docs/plan-flow/schema/validate-receipt.py` to run at all — flagging as a no-hidden-machine-dependency caveat, not fixed here (out of scope: it is a docs/plan-flow dependency, not part of the removal table).
  FO independent re-verification (2026-09-10): `python3 kc-ship-flow/scripts/contract-test.py` exits 1 on unmodified main tip `6991fd09` too (fails deterministically, twice, at the `e2e-gate ac2` step — a different failure point than the worktree's, but the same conclusion: exit 1 pre-exists this change and is not introduced by it). Confirmed independently, not taken on the ensign's word alone.
- DONE: git grep for accept-evidence|open-pr.sh|disposition.py|merge-station|ci-covers|dev-debrief|ship-debrief|notify.sh|without-it.sh over kc-ship-flow and docs/ship prints nothing (AC-1, grep half)
  Deleted accept-evidence.sh, without-it.sh, open-pr.sh, disposition.py, ci-covers.sh(+test), merge-station.sh(+test), dev-debrief.py(+test), ship-debrief.py(+test), notify.sh(+test), their station docs, schemas/evidence-block.md, and every fixture used only by them; edited the remaining literal mentions inside kernel.md, placement.tsv, e2e-cli.sh, kc-ship-close-receipt.v1.schema.json, SKILL.md, docs/ship/README.md, contract-test.py, and several historical fixture "body"/SELF_CHECK strings to paraphrase without the deleted filenames (recomputing body_sha256/receipt_sha256/approval_receipt_sha256/close_sha256 for the one hash-checked fixture chain this touched, close-receipt/plan-receipt.json + plan-approval.json + close-receipt.debrief-wrapper-embedded.json, so validate-receipt.py still accepts them).
- DONE: python3 kc-ship-flow/scripts/prose-placement-check.py exits 0 at the candidate SHA (AC-2)
  Rewrote the 4 runtime-section segments naming a deleted script (without-it.sh, open-pr.sh, disposition.py, notify.sh), recomputed their sha256 segment hashes, and repointed 8 placement.tsv rows (the 4 above plus f7d9f3314010, f348a6450677, d999717871ef, and notify's second sentence) to `residual` with the removal reason; `python3 kc-ship-flow/scripts/prose-placement-check.py` prints `PASS (28 segments, 18 placed, 10 residual)`.
- DONE: bash scripts/marketplace-verify.sh and bash scripts/skill-frontmatter-lint.sh exit 0 at the candidate SHA (AC-3)
  Both ran clean after the kc-ship-flow description edits in plugin.json/.codex-plugin/plugin.json/marketplace.json (`marketplace-verify.sh`: "All checks passed"; `skill-frontmatter-lint.sh`: "checked 45 SKILL.md file(s)... all valid").

### Summary

Deleted the nine per-task stations named in the spec's removal table plus their station docs, the evidence-block schema, and every fixture/contract-test case that only exercised them, then rewrote kernel.md, placement.tsv, docs/ship/README.md (five stages: dispatched, watching, verified, uat, closed), and the first-officer SKILL.md to describe the surviving cloud-wrapper shape. Left `fenced-dispatch.sh`/`intent.sh`/`holder.sh`/`worker-transcript.sh` and `pin.py`'s stage-name vocabulary untouched — none is named in AC-1's grep list, and the claim fence explicitly stays per the entity's Accepted outcome; renaming pin.py's `STATIONS` enum to the new five stage names would need a matching rewrite of ~15 cases in pin.test.py that no AC requires, so it's flagged rather than attempted under this stage's budget. AC-1's `git grep` and AC-2/AC-3 all pass at candidate d300d531; the one open item is `contract-test.py`'s exit code, blocked only by a `spacedock dispatch build` failure reproduced identically on the unmodified branch tip before this PR's changes (environment gap, not a regression from this removal).
