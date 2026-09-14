---
title: "capture-oracle.cjs never caught anything, so it fails the retention rule it was kept under"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: dev-flow-pr-merge-adopter-seam
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: 1s5dc7neg6fvv1vskbq195hg
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
- **AC-3** `python3 kc-dev-flow/scripts/check-pr-title.test.py` exits 0 unchanged, and
  `git diff origin/main -- kc-dev-flow/scripts/check-pr-title.py kc-dev-flow/scripts/fixtures/pr-title/release-please-verdicts.tsv`
  is empty — the checker and every fixture row are untouched.
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
  poc_budget: One implementation pass and one validation pass; at most 6 changed files and 60 gross changed lines.
  poc_stop_when: Any edit would be needed inside check-pr-title.py, release-please-verdicts.tsv, the released pr-merge body, or scripts/fixtures/release-please-runtime.
  poc_artifact: retained
  poc_safety_boundary: The delivery ceremony's title refusal must keep working; the checker and its fixture are untouched, so the refusal path is not in scope.
  scope_boundary: No change to the checker, the fixture rows, the released body or its pin, the release-please runtime, or spacedock-dev/subspace-relay.
  semantics_unchanged: false
```
