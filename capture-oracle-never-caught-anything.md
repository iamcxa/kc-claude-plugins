---
title: "capture-oracle.cjs never caught anything, so it fails the retention rule it was kept under"
status: validation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: dev-flow-pr-merge-adopter-seam
sprint-readiness: ready
started: 2026-09-14T06:35:34.73052Z
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

## Stage Report: implementation (cycle 2)

- DONE: AC-1 — `git grep -n capture-oracle` over the tracked tree returns nothing
  commit 13543f3c removed the four-line dead regeneration-command block (`Re-derive after any release-please version bump...` through the `node .../capture-oracle.cjs > ...` command) from `release-please-verdicts.tsv`'s header comment, per the Captain's amended AC-3. `git grep -n capture-oracle` now exits 1 (no matches).
- DONE: AC-2 — unchanged from cycle 1, re-verified at the new candidate
  `python3 scripts/kc-dev-flow-contract-test.py` → PASS in its own bounded invocation.
- DONE: AC-3 (amended) — checker untouched; all 13 verdict rows byte-identical to `origin/main`; the header comment no longer names a deleted command
  `python3 kc-dev-flow/scripts/check-pr-title.test.py` → PASS (13 fixture rows + 3 boundary cases); `git diff origin/main -- kc-dev-flow/scripts/check-pr-title.py` empty; `diff` of the 13 non-comment rows against `origin/main`'s copy is empty.
- DONE: AC-4 — unchanged from cycle 1, re-verified at the new candidate
  recomputed released-body sha256 = `ea187ab4d1771ce3cb549c2619278a77bc904e39c0fb2b61770ed94d12f5cf57` / 10551 bytes, matching `contract-manifest.json`'s pin unchanged.

### Summary

Addressed the Captain's amendment: removed the dead `capture-oracle.cjs` regeneration command from `release-please-verdicts.tsv`'s header comment (commit 13543f3c), leaving the 13 verdict rows and the capture/agreement provenance untouched. All four acceptance criteria now pass at the new candidate, each check run as its own bounded invocation. Total diff across both cycles: 6 files, 10 added lines (within the amended `poc_budget`).

## POC outcome

```yaml
poc_outcome:
  direction: change
  admitted_at: 2026-09-14T06:35:34.73052Z
  decision_ready_at: 2026-09-14T07:03:34.73052Z
  decision_ready_elapsed_seconds: 1680
  captain_interventions_before_decision_ready: 1
  evidence: All four AC checks green at candidate 13543f3c. kc-dev-flow-contract-test.py PASS exit 0; check-pr-title.test.py PASS exit 0 (13 fixture rows + 3 boundary cases); git grep -n capture-oracle exit 1 over the tracked tree, against 8 hits in 6 files on origin/main; the 13 verdict rows diff empty against origin/main; released body sha256 ea187ab4d1771ce3cb549c2619278a77bc904e39c0fb2b61770ed94d12f5cf57 at 10551 bytes recomputed independently and matching the manifest pin; synced extension block byte-identical to the resource at the contract test's own marker boundary (27515 == 27515 chars).
  strongest_limit: The deletion is sound; direction is change because the experiment left its POC envelope, not because the candidate is wrong. Decision-ready took 1680s against a 15-minute limit and the Captain intervened mid-flight to amend AC-3 and poc_stop_when, which the receipt anticipated as overrulable to Pilot at the cost of one stage. Second limit - re-derivation was not exercised here, so "re-deriving remains possible" rests on scripts/fixtures/release-please-runtime being byte-unchanged from the revision that produced three agreeing runs, not on a fresh run.
  reversal_fact: git show origin/main:kc-dev-flow/scripts/fixtures/pr-title/capture-oracle.cjs restores the deleted tool verbatim, including the three facts that left the shipped surface with it - the build/src/commit.js parseConventionalCommits import path, the quiet-logger workaround for release-please's default debug logger, and the {sha, message, files, pullRequest} commit shape the parser expects.
  cleanup_status_at_decision: complete
```

## POC close measurement

```yaml
poc_close_measurement:
  captain_wait_seconds: pending
  terminal_cleanup_seconds: pending
  cleanup_status: pending
```

## Stage Report: validation

- DONE: Record one `poc_outcome`: direction, exact evidence, strongest limit, reversal fact, and cleanup
  `## POC outcome` above, direction `change`. Verified parseable by the shipped consumer: `poc-close-guard.py`'s `parse_outcome` returns `change`, and `validate_measurements(final=False)` accepts the `## POC close measurement` block. Falsifiers seen to fail on the same harness — flipping to `direction: proceed` raises `budget exhaustion or Captain intervention requires direction change`; deleting `reversal_fact` raises `work item must contain exactly one reversal_fact`.
- DONE: observed journey result and artifact revision
  Candidate `13543f3c`, worktree clean (`git diff HEAD --stat` empty after both mutations reverted). AC-1: `git grep -n capture-oracle` and `git grep -niE 'capture.?oracle'` both exit 1; the same grep on `origin/main` returns 8 hits across 6 files, so the instrument fires. AC-2: `kc-dev-flow-contract-test.py` PASS exit 0. AC-3: `check-pr-title.test.py` PASS exit 0 (13 fixture rows + 3 boundary cases); `git diff origin/main -- kc-dev-flow/scripts/check-pr-title.py` empty; the 13 non-comment verdict rows `diff` empty against `origin/main`, with the 4 removed header lines being exactly the dead regeneration command. AC-4: released body recomputed independently at sha256 `ea187ab4d1771ce3cb549c2619278a77bc904e39c0fb2b61770ed94d12f5cf57` / 10551 bytes, matching the pin; synced block byte-identical to the resource (27515 == 27515) at the contract test's own marker-inclusive boundary.
- DONE: result of the critical-risk check
  The receipt's `poc_falsifier` is that the contract test cannot pass without the path in its expected-resource sets. Both sides were mutated and each reddened with a *distinct* message, proving two separate check paths rather than one reached twice: re-adding to `contract-manifest.json` `resources` gave `profile contract: installed resource missing: scripts/fixtures/pr-title/capture-oracle.cjs` exit 1; re-adding to `kc-dev-flow-contract-test.py`'s `expected_manifest_resources` gave `installed manifest does not bind the exact canonical runtime surface` exit 1. Each run was its own bounded invocation; both reverted, tree clean before the green run. Falsifier not hit — the contract test passes with the path gone from both sides.
- DONE: cleanup status
  `complete` at decision. The experiment's product is the deletion itself; no scaffolding, flag, shim, or transitional duplicate was created. `scripts/fixtures/release-please-runtime` untouched (`git diff origin/main --stat` empty), satisfying its non-goal. Terminal cleanup durations stay `pending` in `## POC close measurement` per the profile's "never fabricated zero".
- DONE: unproved limits and any promotion trigger
  Promotion trigger observed and it is why direction is `change`: decision-ready at 1680s against the receipt's 15-minute limit, plus one Captain intervention before decision-ready (the 2026-09-14 amendment of AC-3 and `poc_stop_when`). The receipt anticipated this as "overrulable to Pilot at the cost of one stage". Three further limits below.

### Findings

- **F1 — blocks the close path, needs the FO.** Frontmatter `started:` is empty, so `poc-close-guard.py` resolves `receipt["started"]` to the literal string `completed:` and rejects any `admitted_at` with `admitted_at must equal frontmatter started`. Reproduced against the real entity; the block parses once `started` carries a value. The FO must set `started: 2026-09-14T06:35:34.73052Z` — the backlog gate's resolution `at`, compared as an exact string, so the `.73052` suffix must match. Root cause isolated to `\s*` crossing the newline in the guard's `^started:\s*([^\n#]+?)\s*$` when the field is empty, which silently captures the next frontmatter key instead of erroring; that is a latent guard defect, out of this item's scope.
- **F2 — one reference to the deleted tool survives, and AC-1's grep cannot see it.** `kc-dev-flow/scripts/fixtures/pr-title/release-please-verdicts.tsv:7` still reads `not re-derived by this file's capture command.` — a dangling referent to `capture-oracle.cjs` phrased without the literal string. AC-1 passes as written and AC-3's amendment drew its line at *false instructions* ("telling a reader to run a command that no longer exists"), which this is not; but the accepted outcome says "every reference to it are gone". Proposed one-clause fix: `not part of this file's capture.` The receipt's one correction was spent at cycle 2, so spending another is the Captain's call — recorded, not repaired.
- **F3 — path-root ambiguity, cosmetic.** The rewritten stop condition names `scripts/fixtures/release-please-runtime` (repo root) four lines below `scripts/fixtures/pr-title/release-please-verdicts.tsv` (kc-dev-flow package relative) in the same section. Both true, different roots, no disambiguator now that the deleted file's "repo root, not under kc-dev-flow/" note is gone. Proposed: prefix the first with `this repository's root-level`.

### Summary

All four acceptance criteria pass at `13543f3c` and the deletion is sound — nothing in the candidate is wrong. Direction is `change` because the experiment left its POC envelope, not because the work failed: `poc-close-guard.py` itself refuses `direction: proceed` on this item, citing budget exhaustion and the Captain's mid-flight amendment. On the FO's scepticism question, the version-skew stop condition stays coherent for the adopter — their action was and remains "stop and report upstream", and the old prose already said an adopter checkout could not run the tool; what degraded is the maintainer's cost of answering, since the `build/src/commit.js` `parseConventionalCommits` path, the quiet-logger workaround, and the `{sha, message, files, pullRequest}` commit shape now live only in `git show origin/main:...capture-oracle.cjs`. That is the cost the Captain accepted on the three-runs-zero-bites record, and I read the shipped prose the same way. Re-derivation was not exercised: no direction turns on its result, and the runtime is byte-unchanged from the revision that produced three agreeing runs.

## Captain ruling — fix F2 and F3, 2026-09-14

The Captain instructed 改 after the FO presented validation's F2 and F3 with the
recommendation to fix and the cost of a second correction pass. The item returns to
`implementation` for those two prose edits and is proved again.

**Recorded because the route was not the designed one.** A
`kc-dev-flow-feedback/v1` correction context cannot bind after a POC prove stage:
the prove stage writes `## POC outcome` and `## POC close measurement`, both
non-report sections, into the accepted-authority region, so the current authority
hash can never equal the rejected pin's and the loader answers
`FEEDBACK_CONTEXT_MISMATCH`. Reproduced here before the FO changed approach. The
POC profile's answer to findings is its `poc_outcome` direction, not a correction
round — which is consistent, and is one more reason this item should have been
Pilot. Raised as an upstream observation, not repaired here.

So this pass is authorized by the Captain's ruling recorded in this section rather
than by a feedback context, and is pinned as an ordinary `implementation-3`
attempt. Scope is exactly validation's two proposals and nothing else.

- **F2** `kc-dev-flow/scripts/fixtures/pr-title/release-please-verdicts.tsv` line 7:
  replace `not re-derived by this file's capture command.` with `not part of this
  file's capture.` No verdict row moves; the capture provenance and the `17.11.1`
  agreement note stay.
- **F3** `kc-dev-flow/references/pr-merge-extension.md`: prefix the repo-root path
  `scripts/fixtures/release-please-runtime` with `this repository's root-level`, so
  it is not read against the package-relative path four lines above. Re-sync the
  identical bytes into the mod's marked block rather than hand-editing the mod.

Out of scope: no acceptance criterion is re-argued, no verdict row changes, and no
edit to `check-pr-title.py`, the released pr-merge body or its pin,
`scripts/fixtures/release-please-runtime`, or `spacedock-dev/subspace-relay`.

## Stage Report: implementation (cycle 3)

- DONE: F2 — reword the dangling referent in the fixture header
  commit eca4eb82; `kc-dev-flow/scripts/fixtures/pr-title/release-please-verdicts.tsv:7` now reads `not part of this file's capture.`, naming no deleted command. No verdict row moved: 13 non-comment rows diff empty against `origin/main`.
- DONE: F3 — disambiguate the repo-root path from the package-relative path
  same commit; `kc-dev-flow/references/pr-merge-extension.md` now reads `this repository's root-level scripts/fixtures/release-please-runtime`, and the identical bytes are re-synced into `docs/dev/_mods/pr-merge.md`'s marked extension block (not hand-edited).
- DONE: re-verify all four acceptance criteria at the new candidate, each its own bounded run
  `git grep capture-oracle` exit 1 (AC-1); `python3 scripts/kc-dev-flow-contract-test.py` → PASS exit 0 (AC-2); `python3 kc-dev-flow/scripts/check-pr-title.test.py` → PASS exit 0, `git diff origin/main -- kc-dev-flow/scripts/check-pr-title.py` empty, 13 verdict rows diff empty against `origin/main` (AC-3); recomputed released-body sha256 `ea187ab4d1771ce3cb549c2619278a77bc904e39c0fb2b61770ed94d12f5cf57`/10551 bytes matches the manifest pin, and the mod's extension block is byte-identical to the resource, 27522 == 27522 chars (AC-4).
- DONE: state whether "every reference is gone" now holds literally
  `git grep -niE 'capture.oracle|capture-oracle|capture oracle'` over the tracked tree exits 1 (zero hits), including F2's prior dangling referent. The accepted outcome's "every reference to it are gone from the shipped surface" now holds literally, not just under AC-1's literal-string grep.

### Summary

Applied exactly validation's two proposed prose edits (commit eca4eb82) under the Captain's ruling, out-of-scope items untouched: `check-pr-title.py`, every verdict row, the released body and its pin, and `scripts/fixtures/release-please-runtime` all diff empty against `origin/main`. All four acceptance criteria re-verified green at the new candidate, and the broader case-insensitive/paraphrase grep now also returns zero — the accepted outcome's "every reference is gone" clause holds literally, closing F2 and F3.
