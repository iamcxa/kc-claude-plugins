---
title: "capture-oracle.cjs never caught anything, so it fails the retention rule it was kept under"
status: implementation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: dev-flow-pr-merge-adopter-seam
sprint-readiness: ready
started:
completed:
verdict:
worktree: .worktrees/spacedock-ensign-capture-oracle-never-caught-anything
issue:
pr:
mod-block:
id: 1s5dc7neg6fvv1vskbq195hg
gates:
    version: 1
    records:
        - id: gate:1s5dc7neg6fvv1vskbq195hg:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:1s5dc7neg6fvv1vskbq195hg-backlog-1
              briefing:
                id: briefing:1s5dc7neg6fvv1vskbq195hg:backlog:attempt-1:revision-1
                digest: sha256:8451943bb1d44e2eb6f39ae76814c9a7538199589fa31ad5f3ee55d08a88568b
                room-ref: ./capture-oracle-never-caught-anything/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:1s5dc7neg6fvv1vskbq195hg:backlog:1
                briefing: briefing:1s5dc7neg6fvv1vskbq195hg:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T06:35:34.73052Z"
                decision: approve
                reason: 'Captain instructed in chat 2026-09-14: 開移除單且立即執行 — open the removal task and run it immediately, after the FO produced the usage record showing three runs and zero bites and withdrew its own keep recommendation. The FO selected poc-exploration under that instruction and records it as overrulable to Pilot at the cost of one stage.'
              application:
                target-stage: ideation
                state: consumed
---

PR #433 shipped `kc-dev-flow/scripts/fixtures/pr-title/capture-oracle.cjs` as a
canonical manifest resource. Its recorded history is three runs, all of them
confirmations: it generated `release-please-verdicts.tsv` from release-please
`17.3.0` during implementation, and validation re-derived the same 13 rows twice —
once against `17.3.0` and once against `17.11.1` — finding no disagreement either
time. The measured disagreement that motivated the whole design, release-please
accepting `feat(): x` where a hand-written grammar would not, was found at the
ideation stage by requiring the parser directly out of
`scripts/fixtures/release-please-runtime`, before this file existed. The single
argument recorded for keeping it is that a coordinated edit to both a fixture row
and the checker's grammar would pass the self-test and the process test, and only a
live re-derive would catch it. That failure has never occurred. The Captain's
retention rule is that a kept artifact must have bitten someone with evidence, and
"it might be useful" is not evidence. Under that rule this file goes. The FO
recommended keeping it one turn earlier and was wrong: it credited this file with a
bite delivered by five lines of `require()` at a stage where the file did not exist.

## Accepted outcome

`capture-oracle.cjs` and every reference to it are gone from the shipped surface,
and the contract test still passes. Re-deriving the fixture remains possible for
whoever needs it — the release-please runtime under
`scripts/fixtures/release-please-runtime` is unchanged, and reaching its parser is
the same `require()` the ideation stage used — but no 82-line file is retained
against a failure nobody has seen.

## Non-goals

- Changing `check-pr-title.py`, its self-test, or any row of `release-please-verdicts.tsv`.
- Changing the version-skew stop condition itself: an adopter on skew still stops and reports upstream.
- Removing `scripts/fixtures/release-please-runtime` or its lockfile.
- Any change to the released pr-merge body or its pinned sha256.

## Acceptance criteria

- **AC-1** `git grep -n capture-oracle` over the tracked tree returns nothing, and
  `kc-dev-flow/scripts/fixtures/pr-title/capture-oracle.cjs` is absent.
- **AC-2** `python3 scripts/kc-dev-flow-contract-test.py` exits 0, with the path
  removed from both the manifest `resources` list and the test's own expected-resource
  sets. Re-adding the path to either side without the file exits non-zero.
- **AC-3** `python3 kc-dev-flow/scripts/check-pr-title.test.py` exits 0 unchanged;
  `git diff origin/main -- kc-dev-flow/scripts/check-pr-title.py` is empty; and every
  one of the 13 verdict rows in `release-please-verdicts.tsv` is byte-identical to
  `origin/main`. The file's header comment is not a verdict row: the lines naming the
  deleted regeneration command are removed with it, because a shipped file telling a
  reader to run a command that no longer exists is a false claim, not a stale one.
  **Amended by the Captain on 2026-09-14** after the implementation stage reported
  that AC-1 and AC-3 as first written were mutually exclusive on that header. The
  original wording said the whole file; its intent was always the data the tool
  produced.
- **AC-4** The `### The title rule's oracle` section and its synced copy in
  `docs/dev/_mods/pr-merge.md` still state the version-skew stop condition and no
  longer name a re-derivation script; the synced block remains byte-identical to the
  resource and the released body still matches `pr_merge_released_body.sha256`.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: >
    Captain instructed removal and immediate execution in chat 2026-09-14 after the
    FO produced the usage record showing three runs and zero bites. POC rather than
    Pilot because the design question is already answered — this is a deletion with a
    known shape and eight tracked references — so an ideation stage would shape
    nothing. The FO selected the profile under the Captain's "immediately" instruction
    and records it as overrulable to Pilot at the cost of one stage.
  poc_decision: Remove capture-oracle.cjs from the shipped surface, or keep it if removal cannot leave the contract test green and the stop condition intact.
  poc_falsifier: The contract test cannot pass without the path in its expected-resource sets, or removing the file forces a change to check-pr-title.py or any fixture row.
  poc_budget: One implementation pass, one correction, and one validation pass; at most 6 changed files and 60 ADDED lines. Amended by the Captain on 2026-09-14: the original 60 gross changed lines was impossible from the moment it was written, because the core act is deleting an 82-line file. Deletions are the outcome, not the spend.
  poc_stop_when: Any edit would be needed inside check-pr-title.py, any verdict row of release-please-verdicts.tsv, the released pr-merge body, or scripts/fixtures/release-please-runtime. Amended with AC-3 on 2026-09-14; the file's header comment is outside this boundary.
  poc_artifact: retained
  poc_safety_boundary: The delivery ceremony's title refusal must keep working; the checker and its fixture are untouched, so the refusal path is not in scope.
  scope_boundary: No change to the checker, the fixture rows, the released body or its pin, the release-please runtime, or spacedock-dev/subspace-relay.
  semantics_unchanged: false
```

## Stage Report: implementation

- DONE: AC-2 — contract test exits 0 with the path removed from both the manifest resources list and the test's own expected-resource sets; re-adding it to one side exits non-zero
  commit 0e82f386; `python3 scripts/kc-dev-flow-contract-test.py` → PASS; re-adding the entry to one expected set alone reproduced `missing kc-dev-flow/scripts/fixtures/pr-title/capture-oracle.cjs` exit 1, then reverted with `git diff --stat` showing 0 residual lines before commit.
- DONE: AC-3 — checker and every fixture row untouched
  `python3 kc-dev-flow/scripts/check-pr-title.test.py` → PASS (13 fixture rows + 3 boundary cases); `git diff origin/main -- kc-dev-flow/scripts/check-pr-title.py kc-dev-flow/scripts/fixtures/pr-title/release-please-verdicts.tsv` is empty.
- DONE: AC-4 — oracle section states the version-skew stop condition without naming a re-derivation script; synced block byte-identical; released body pin unchanged
  edited `kc-dev-flow/references/pr-merge-extension.md`'s stop-condition paragraph and re-synced the identical bytes into `docs/dev/_mods/pr-merge.md`'s marked extension block (script-free sync per `kc-dev-flow-contract-test.py`'s own note that this copy is prose, not scripted); contract test's block-drift check passed in the same PASS run; recomputed sha256 of the released body independently = `ea187ab4d1771ce3cb549c2619278a77bc904e39c0fb2b61770ed94d12f5cf57` / 10551 bytes, matching `contract-manifest.json`'s pin unchanged.
- FAILED: AC-1 — `git grep -n capture-oracle` over the tracked tree returns nothing
  one hit remains: `kc-dev-flow/scripts/fixtures/pr-title/release-please-verdicts.tsv:10`, the regeneration-command comment in the file's own header. Editing it would break AC-3's requirement that this file's diff against `origin/main` stay empty, and crosses this work item's own `poc_stop_when: ... release-please-verdicts.tsv`. AC-1 and AC-3 conflict on this one line as literally written; left the file untouched pending a Captain/FO ruling on whether AC-1 excludes this header comment or the stale reference is an accepted residual. Cost of leaving it: the comment now names a regeneration command (`node .../capture-oracle.cjs`) that no longer exists.

### Summary

Removed `capture-oracle.cjs` and seven of its eight tracked references (manifest, both contract-test expected-resource sets, the oracle section's resource and synced mod), keeping the checker, every fixture row, and the released-body pin byte-for-byte unchanged; all four independently-runnable checks pass. The eighth reference — the regeneration-command comment inside `release-please-verdicts.tsv`'s own header — cannot be removed without violating AC-3's untouched-file requirement, so AC-1 fails on that single line; committed at `0e82f386` and escalating for a ruling. Diff also crossed the receipt's declared `poc_budget` (5 files / 107 gross lines vs. 6 files / 60 lines), driven almost entirely by the mandatory 82-line file deletion itself — flagged, not a reason to have stopped short of the accepted outcome.
