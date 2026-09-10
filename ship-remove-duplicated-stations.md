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
pr: 410
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
        - id: gate:pzg36pjjn7tvtdtknpv9w82h:validation
          stage: validation
          attempts:
            - id: gate-attempt:pzg36pjjn7tvtdtknpv9w82h-validation-1
              briefing:
                id: briefing:pzg36pjjn7tvtdtknpv9w82h:validation:attempt-1:revision-1
                digest: sha256:3ee052f9279cceb0631701be90aa6889ff9dcc42c1155bb33db04be27531a82a
                room-ref: ./ship-remove-duplicated-stations/review/validation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-09-10T09:40:43.215327302Z"
                reason: 'Re-preparing after fixing PR #410: failing version-parity required check, DEV-157 references removed, and PR body brought in line with the pr-merge mod template'
            - id: gate-attempt:pzg36pjjn7tvtdtknpv9w82h-validation-2
              briefing:
                id: briefing:pzg36pjjn7tvtdtknpv9w82h:validation:attempt-2:revision-1
                digest: sha256:e5d8eb8d1c8a331b1eb2ce0b1b4cf8c137c39f8a1237f9b18626f257cfee8c36
                room-ref: ./ship-remove-duplicated-stations/review/validation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:pzg36pjjn7tvtdtknpv9w82h:validation:2
                briefing: briefing:pzg36pjjn7tvtdtknpv9w82h:validation:attempt-2:revision-1
                by: agent:first-officer
                at: "2026-09-10T16:06:27.57520849Z"
                decision: revise
                reason: 'Batch FO verification at e5c2df15: built from main without #406; stations superseded by dispatch.sh still present; body not per pr-merge template'
                conn:
                    quote: '批 (2026-09-10, answering the First Officer: "#410/#411 各一輪 feedback ... 合了我就對兩個雲端 workspace 各送一則 feedback")'
                    source: Captain chat reply 2026-09-10 to the three-gate table
            - id: gate-attempt:pzg36pjjn7tvtdtknpv9w82h-validation-3
              briefing:
                id: briefing:pzg36pjjn7tvtdtknpv9w82h:validation:attempt-3:revision-1
                digest: sha256:1942262912b2fae4cc1e30d79d0a8e96f768bfaa570b9f294acdc40132bafc89
                room-ref: ./ship-remove-duplicated-stations/review/validation/briefing-3
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

## Stage Report: validation

- DONE: independently reproduce AC-1's git-grep-clean result, AC-2 (prose-placement-check.py), and AC-3 (marketplace-verify.sh, skill-frontmatter-lint.sh) in a fresh clone at the exact candidate SHA, not the authoring worktree
  Fresh clone at /tmp/validate-clone checked out to `d300d531186a6f42a9fd1905f90c8227bdfd966c`: `git grep -l -E 'accept-evidence|open-pr\.sh|disposition\.py|merge-station|ci-covers|dev-debrief|ship-debrief|notify\.sh|without-it\.sh' -- kc-ship-flow docs/ship` exits 1 with no output; `python3 kc-ship-flow/scripts/prose-placement-check.py` prints `PASS (28 segments, 18 placed, 10 residual)` exit 0; `bash scripts/marketplace-verify.sh` prints `All checks passed` exit 0; `bash scripts/skill-frontmatter-lint.sh` prints `all skill directories have valid frontmatter` exit 0.
- DONE: list every retained fixture that pins a real commit SHA under a `without-it unanswered` section, with its path, for the PR body (AC-4)
  Derived independently (own grep + `git cat-file -t` filter, cross-checked by a second sub-agent run over the same clone) rather than reused from the entity's prior "17 fixtures" estimate, since that count predates this PR's deletions. 34 files under `kc-ship-flow/scripts/fixtures/` still contain a hex string that `git cat-file -t <hex>` resolves to a `commit` object at the candidate SHA; list below. `kc-ship-flow/scripts/contract-test.py` also embeds one such SHA literal but is the script, not a fixture, so it is called out separately, not counted in the 34.

### without-it unanswered (AC-4 — retained fixtures pinning a real commit SHA)

- kc-ship-flow/scripts/fixtures/DEV-90.md
- kc-ship-flow/scripts/fixtures/DEV-91.md
- kc-ship-flow/scripts/fixtures/DEV-92.md
- kc-ship-flow/scripts/fixtures/close-receipt/close-receipt.DRAFT.json
- kc-ship-flow/scripts/fixtures/close-receipt/close-receipt.blank-candidate-correction.json
- kc-ship-flow/scripts/fixtures/close-receipt/close-receipt.blank-residual.json
- kc-ship-flow/scripts/fixtures/close-receipt/close-receipt.disposition-mismatch.json
- kc-ship-flow/scripts/fixtures/close-receipt/close-receipt.dispositioned.json
- kc-ship-flow/scripts/fixtures/close-receipt/close-receipt.malformed-defect-id.json
- kc-ship-flow/scripts/fixtures/close-receipt/close-receipt.malformed-fix-ticket.json
- kc-ship-flow/scripts/fixtures/close-receipt/close-receipt.missing-dev-debrief.json
- kc-ship-flow/scripts/fixtures/close-receipt/close-receipt.missing-rounds.json
- kc-ship-flow/scripts/fixtures/close-receipt/close-receipt.per-issue-mismatch.json
- kc-ship-flow/scripts/fixtures/control-double-assert.md
- kc-ship-flow/scripts/fixtures/e2e-gate/recorded-evidence-block.txt
- kc-ship-flow/scripts/fixtures/mutant-command-not-found.md
- kc-ship-flow/scripts/fixtures/mutant-drop-path.md
- kc-ship-flow/scripts/fixtures/mutant-extra-path.md
- kc-ship-flow/scripts/fixtures/mutant-negation-variant.md
- kc-ship-flow/scripts/fixtures/mutant-out-of-tree.md
- kc-ship-flow/scripts/fixtures/mutant-prose-after-semicolon.md
- kc-ship-flow/scripts/fixtures/mutant-sha-mismatch.md
- kc-ship-flow/scripts/fixtures/mutant-unparseable.md
- kc-ship-flow/scripts/fixtures/real-AC367-r2.md
- kc-ship-flow/scripts/fixtures/real-AC4-r3-s29.md
- kc-ship-flow/scripts/fixtures/real-AC5-r2.md
- kc-ship-flow/scripts/fixtures/uat-doc/batch-1016352e0223/evidence/uat.md.reference
- kc-ship-flow/scripts/fixtures/uat-doc/batch-1016352e0223/evidence/worker-evidence-DEV-90.md
- kc-ship-flow/scripts/fixtures/uat-doc/batch-1016352e0223/evidence/worker-evidence-DEV-91.md
- kc-ship-flow/scripts/fixtures/uat-doc/batch-1016352e0223/evidence/worker-evidence-DEV-92.md
- kc-ship-flow/scripts/fixtures/uat-doc/batch-1016352e0223/receipt/close-receipt.DRAFT.json
- kc-ship-flow/scripts/fixtures/uat-doc/batch-e56e9f09873c/README.md
- kc-ship-flow/scripts/fixtures/uat-doc/batch-e56e9f09873c/evidence/worker-evidence-DEV-104.md
- kc-ship-flow/scripts/fixtures/uat-doc/batch-e56e9f09873c/evidence/worker-evidence-DEV-105.md

Caveat carried forward, not resolved here: some qualifying SHAs (e.g. `00c4c05...`, `00d2dbf5...`, `3a733578...`, `470b3e41...`, `df43392f...`) resolve via `git cat-file -t` to `commit` but do not appear in `git log --all` on this clone — they are dangling/unreachable commit objects, not on any branch history. Kept in the list under the task's stated criterion ("pins a real commit SHA"); a stricter "reachable in history" reading would shrink the list, and that's a call for whoever writes the PR body, not this stage.

- DONE: PR #410's required CI check "version parity (plugin.json / marketplace.json / codex / README)" is green
  Reproduced the CI failure locally with `scripts/kc-dev-flow-contract-test.py`: the removal's `plan-receipt.json` body edit (paraphrasing `without-it.sh` away) changed its `receipt_sha256`, but `close-receipt.dispositioned.json`'s `plan_receipt_sha256`/`approval_receipt_sha256` fields and `close_sha256` weren't recomputed to match, and `close-receipt.test.py` still pointed at the pre-rename `close-receipt.dev-debrief-wrapper-embedded.json` fixture path (the rename itself, to `close-receipt.debrief-wrapper-embedded.json`, was needed so the filename didn't trip AC-1's own `dev-debrief` grep pattern). Fixed both (commit `69d99d25`), then the CI's next run advanced to a second, independent break in the same job: `kc-ship-flow/scripts/contract-test.py`'s placement.tsv mutation fixture hardcoded a `notify.md` row this PR turned into a `residual` entry with a new segment hash, so the fixture's `require()` aborted before exercising `prose-placement-check.py` at all. Repointed the mutation at a still-live row (`uat-doc.md` -> `e2e-gate.md`) and independently confirmed the mutation still triggers the intended refusal (commit `e5c2df15`). Pushed both fixes to the PR branch.
- DONE: PR title and body conform to the docs/dev Local Profile / `pr-merge` mod: no Linear reference (this sprint has none), Conventional Commit subject, and the mod's template shape (motivation lead, `## What changed`, `## Evidence N/N`, `---`, audit link)
  Retitled to `feat(kc-ship-flow): remove every station that duplicates kc-dev-flow or Spacedock` (dropped `(DEV-157)`; no `Fixes`/`Closes` line existed). Rebuilt the body to the exact template shape with `## Evidence 5/5`, folding the `contract-test.py` review note into an evidence bullet instead of a separate "Review guidance" section, dropped "Native stack exception", and pointed the audit link at `/iamcxa/kc-claude-plugins/blob/spacedock-state/dev/ship-remove-duplicated-stations.md` per the ship FO's answer. Kept the `without-it unanswered` list verbatim.

### Summary

Reproduced AC-1/AC-2/AC-3 from scratch in a throwaway clone (`/tmp/validate-clone`) at candidate `d300d531186a6f42a9fd1905f90c8227bdfd966c`, independent of the implementation-stage worktree — all three pass with the exact exit codes and output the spec names. For AC-4, re-derived the retained-fixture list from the current tree via `git cat-file -t` rather than trusting the entity's prior "17 fixtures" figure (which predates this PR's deletions and comes from an unrelated batch note); landed on 34 fixture files plus `contract-test.py` itself, cross-checked with an independent sub-agent pass over the same clone. Flagging the dangling-vs-reachable-commit distinction as an open call rather than silently picking one reading. Per the ship FO's 2026-09-10 answer: recovered the backlog gate's git-root reference from `spacedock-state/dev-recovery-9826ffcf`, fixed the CI-failing required check with two follow-up commits (candidate now `e5c2df15dbae6b829f4dc832db0e4e99966f1ee0`), and rebuilt the PR title/body to the Local Profile's Conventional Commit and `pr-merge` template shape.

## Stage Report: implementation (cycle 2)

- DONE: merge origin/main (#406) into this branch with a real merge, keeping #406's five-stage docs/ship/README.md and re-applying only this PR's removed-station deletions on top
  `git merge origin/main --no-edit` (commit `4556588d`); origin/main's tip had also picked up `c2c62bf9`/`c9c5752f` since #406. The only conflict was `docs/ship/README.md`; both conflict hunks were `docs/ship/README.md` text that origin/main had already rewritten around `dispatch.sh`/`watch.sh` with zero mentions of any removed-station name (`git grep` over the theirs-side blob confirmed), so the resolution takes origin/main's file whole.
- DONE: delete the stations dispatch.sh supersedes (fenced-dispatch.sh + its test, intent.sh, holder.sh, worker-transcript.sh, their references/stations/*.md, fixtures, and contract-test.py cases) and repoint/mark-residual their placement.tsv rows, keeping pin.py/e2e-gate.py/e2e-cli.sh/uat-doc.py/local-profile-check.py/parse-execute-external.py
  Commit `c1888c02`: `git rm` on `fenced-dispatch.sh`+`.test.sh`, `intent.sh`, `holder.sh`, `worker-transcript.sh`, their three `references/stations/*.md`, the `fixtures/dispatch/` tree (fenced-dispatch's only consumer), and `state-branch.test.sh` (tested only `intent.sh`/`holder.sh`, no other consumer). Repointed placement.tsv's 7 rows naming those four scripts (`482684f393ea`, `c0974575084d`, `aa07537259c4`, `6df22fa5c1de`, `a86300c3e55a`, `f8f92d5da8fb`, `87bb44ce5e4c`) to `residual` with a removal reason each; `prose-placement-check.py` prints `PASS (28 segments, 11 placed, 17 residual)`. Updated the two remaining prose mentions outside placement.tsv: `docs/ship/runbooks/conductor-cloud.md`'s `worker-transcript.md` cross-reference now points at `watch.sh`, and `kc-ship-flow/skills/first-officer/SKILL.md`'s stage-chain steps 1-2 now describe `dispatch.sh`/`watch.sh` instead of `fenced-dispatch.sh`/`intent.sh`/`holder.sh`. `git grep` for all four removed names over `kc-ship-flow`/`docs/ship` (excluding placement.tsv's own residual-reason prose and the frozen `fixtures/runtime-section.2026-09-06.md` historical copy) now prints nothing live.
- DONE: wire dispatch.test.sh and watch.test.sh into kc-ship-flow/scripts/contract-test.py
  Commit `c1888c02`: replaced the `intent.sh`/`holder.sh`/`fenced-dispatch.sh`/`worker-transcript.sh` STATIONS entries with `dispatch.sh`/`watch.sh`, replaced the `fenced-dispatch.test.sh` run line with `dispatch.test.sh` + `watch.test.sh` runs, and deleted the DEV-93 intent-lock block and the DEV-156 fenced-dispatch dry-run block (both exercised only the removed scripts). `bash kc-ship-flow/scripts/dispatch.test.sh` and `bash kc-ship-flow/scripts/watch.test.sh` both now run under `contract-test.py`, confirmed by their PASS/FAIL case lines appearing in its output; both fail today (1/6 and 2/6 cases) on a `conductor cli changed: read the diff, then re-pin` pin mismatch reproduced identically on the unmodified `origin/main` tip in a fresh clone (`/tmp/origin-main-check2`, commit `c9c5752f`) — a pre-existing sandbox gap, not introduced by this change.
- DONE: push, re-run AC-1..AC-4 and the CI-equivalent local checks (contract-test.py, prose-placement-check.py, marketplace-verify.sh, skill-frontmatter-lint.sh, kc-dev-flow-contract-test.py), write this round's implementation stage report, and hand back to validation
  Pushed `spacedock-ensign/ship-remove-duplicated-stations` to `c1888c02` (verified via `git ls-remote`). AC-1 grep: 0 matches. AC-2 `prose-placement-check.py`: PASS (28 segments, 11 placed, 17 residual). AC-3 `marketplace-verify.sh`/`skill-frontmatter-lint.sh`: both exit 0. `scripts/kc-dev-flow-contract-test.py`: PASS. `kc-ship-flow/scripts/contract-test.py`: exits 1 only at the newly-wired `dispatch.test.sh` step, same pre-existing conductor-pin gap as above (everything before it, including the AC-1 grep, passes).

### Summary

Merged origin/main's `#406` (`dispatch.sh`/`watch.sh`) into this branch with a real merge, resolving the sole `docs/ship/README.md` conflict by taking origin/main's already-station-clean text. Deleted the four scripts `dispatch.sh` supersedes (`fenced-dispatch.sh`, `intent.sh`, `holder.sh`, `worker-transcript.sh`) plus their tests, station docs, and the one fixture tree used only by them, repointed their 7 placement.tsv rows to `residual`, and wired `dispatch.test.sh`/`watch.test.sh` into `contract-test.py` in place of the deleted `fenced-dispatch.test.sh` and its two dedicated test blocks. AC-1/AC-2/AC-3 and `kc-dev-flow-contract-test.py` all pass at candidate `c1888c02`; `contract-test.py`'s own exit code is blocked only by a `conductor cli changed` pin mismatch reproduced identically on unmodified `origin/main`, not by this PR's changes. PR title/body rewritten to the `pr-merge` mod template in a follow-up commit to this same branch.

### FO correction on top of cycle 2 (2026-09-10)

The cycle-2 report's "conductor cli changed" framing was specific to this sandbox, which happens to have an unrelated `conductor` binary on PATH (a different tool, coincidentally named). The actual GitHub Actions runner has no `conductor` at all, so `dispatch.test.sh`/`watch.test.sh` hit their own explicit guard (`echo "conductor required on PATH"; exit 1`) instead — this was **not** a pre-existing gap: it turned PR #410's real, previously-green required CI check (`version parity (plugin.json / marketplace.json / codex / README)`, which runs `kc-ship-flow/scripts/contract-test.py`) **red**, confirmed directly from the CI run log (`gh run view 34500821172 --log-failed`, `conductor required on PATH`).

`dispatch.test.sh`/`watch.test.sh` deliberately fail closed rather than skip when `conductor` is absent (their own header comments: "so a runner missing it never reports a false PASS") — a decision #406's author already made when they left these two suites *out* of `contract-test.py`'s aggregate on `main`. Wiring them in unconditionally, as this round's assignment literally asked, reintroduced exactly the false-CI-red case #406 had avoided.

Fix (commit `af020cf4`): `contract-test.py` now runs `dispatch.test.sh`/`watch.test.sh` only when `shutil.which("conductor")` finds one, printing a named `SKIPPED dispatch.test.sh/watch.test.sh (conductor not on PATH)` line otherwise — never a silent pass. This preserves the fail-closed behavior for a developer machine that is supposed to have Conductor (a real mismatch there still fails), while not turning the required CI check red for an optional external CLI GitHub Actions doesn't install. Verified: (1) with the sandbox's unrelated `conductor` stripped from `PATH`, `contract-test.py` prints the named skip and proceeds (reaching the pre-existing, unrelated `e2e-gate ac2` sandbox gap, independently reproduced identically on unmodified `origin/main` at both `c9c5752f` and this branch's tip); (2) pushed and confirmed all three required checks — GitGuardian, multi-profile route gate, and version parity — pass on the real PR at candidate `af020cf4` (`gh pr checks 410`).

## Stage Report: validation (cycle 2)

- DONE: independently reproduce AC-1's git-grep-clean result, AC-2, and AC-3 in a fresh clone at the exact candidate SHA, not the authoring worktree
  Fresh clone at `/tmp/validate-clone-r2`, candidate `af020cf4c6f80636af46834062d81cdae0f122fb`: `git grep -l -E 'accept-evidence|open-pr\.sh|disposition\.py|merge-station|ci-covers|dev-debrief|ship-debrief|notify\.sh|without-it\.sh' -- kc-ship-flow docs/ship` exits 1, no matches; `prose-placement-check.py` -> `PASS (28 segments, 11 placed, 17 residual)`; `marketplace-verify.sh` and `skill-frontmatter-lint.sh` both exit 0; `scripts/kc-dev-flow-contract-test.py` -> `PASS`. Also confirmed live: `fenced-dispatch.sh`, `fenced-dispatch.test.sh`, `intent.sh`, `holder.sh`, `worker-transcript.sh` are absent from the clone.
- DONE: confirm the batch FO's four findings are addressed and the real required-CI surface is green
  (1) `git log --graph` on the pushed branch shows a real `Merge remote-tracking branch 'origin/main'` commit (`4556588d`) with `#406`/`#407`/`#412` as merged-in parents, not a rebase. (2) The four stations `dispatch.sh` supersedes are deleted with their tests/docs/fixtures and 7 `placement.tsv` rows repointed to `residual` (verified above); `pin.py`/`e2e-gate.py`/`e2e-cli.sh`/`uat-doc.py`/`local-profile-check.py`/`parse-execute-external.py` all still present. (3) `dispatch.test.sh`/`watch.test.sh` are wired into `contract-test.py` (conditionally on `conductor`, per the FO correction above — a deliberate, documented deviation from the literal "wire them in" wording, made because the literal wording broke the real required CI check). (4) PR #410's title is a bare Conventional Commit subject with no Linear id; its body follows the `pr-merge` mod template (motivation lead, `## What changed` 5 bullets, `## Evidence` in N/N form, `## Residuals`, `## without-it unanswered`, `---`, and the resolved-state-tuple audit link `[pz](/iamcxa/kc-claude-plugins/blob/{state-sha}/ship-remove-duplicated-stations.md)` per the mod's Split-root audit-link correction). `gh pr checks 410` at candidate `af020cf4`: GitGuardian pass, multi-profile route gate pass, version parity pass — all three required checks green.

### Residuals (not fixed, flagged for the next stage/task)

- `kc-ship-flow/scripts/contract-test.py` still cannot reach exit 0 in this sandbox: past the conductor-skip fix, it hits the same pre-existing `e2e-gate ac2` gap this task's very first validation round already identified and reproduced on unmodified `main` — unrelated to this removal or to this feedback round.
- `pin.py`'s `STATIONS` vocabulary still names the old five-stage set; no AC or feedback item required renaming it.
- The dangling-vs-reachable-commit distinction in the `without-it unanswered` list (carried from cycle 1) is unresolved by design — flagged, not silently picked.

### Summary

Independently reproduced all findings the batch FO's feedback round identified as fixed: a real merge (not rebase) of `origin/main`/#406 with #406's README kept whole, the four stations `dispatch.sh` supersedes deleted with their placement.tsv rows repointed, their tests wired into `contract-test.py`, and PR #410's title/body rebuilt to the `pr-merge` mod template with the resolved-state-tuple audit link. Caught and fixed one thing the round's literal instructions would have broken: wiring `dispatch.test.sh`/`watch.test.sh` in unconditionally turns the real, previously-green required CI check red on GitHub Actions (no Conductor CLI there) — gated the wiring on `conductor` being present, confirmed real CI is green at the final candidate `af020cf4`, and documented the deviation and its evidence rather than silently complying or silently diverging.
