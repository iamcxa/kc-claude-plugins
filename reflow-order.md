---
title: A repair's validation recheck waits for the repair, and a failed push does not freeze a migration
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:reflow-order:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:reflow-order-backlog-1
              briefing:
                id: briefing:reflow-order:backlog:attempt-1:revision-1
                digest: sha256:4b628894a916d1e6843597f002039f255bfe88cef4d8ff8a7aadb33d28755137
                room-ref: ./reflow-order/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:reflow-order:backlog:1
                briefing: briefing:reflow-order:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-30T15:58:47.656068Z"
                decision: approve
                reason: 'Captain 2026-09-30: 「同意」 — fix both in the package, release 0.10.1, re-sync the two adopter READMEs'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:reflow-order:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:reflow-order-ideation-1
              briefing:
                id: briefing:reflow-order:ideation:attempt-1:revision-1
                digest: sha256:b17defe01321c47b4a4ad8ddd0a62394b848784d792a962b6c02b1efaa2ac8bf
                room-ref: ./reflow-order/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:reflow-order:ideation:1
                briefing: briefing:reflow-order:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-30T16:04:10.713944Z"
                decision: approve
                reason: 'Captain 2026-10-01: 「ok」 — design approved with a failed push replacing its Applied at line by ''Not applied: <env> <sha> - <evidence>'''
              application:
                target-stage: implementation
                state: consumed
started: 2026-09-30T15:58:54Z
worktree: .worktrees/spacedock-ensign-reflow-order
---

Two wording defects in kc-dev-flow-2 0.10.0 `references/sd/workflow.md`, found by an external review of an adopter's workflow sync (qnow PR #1248, 2026-09-30).

## Scope

Captain 2026-09-30: 「同意」 to the FO's proposal: fix both in the package, release 0.10.1, then re-sync the two adopter workflow READMEs (kc-claude-plugins #542, qnow #1248, both held).
Evidence (origin/main c3b3d5ad, `references/sd/workflow.md`):
- P1, `## Stages` lane paragraph: "A feedback-reflow repair, the validation recheck of that repair, and an FO fix authorized under Review-finding disposition step 3 are dispatched at once in the entity's own worktree". Read as "concurrently", a validator can inspect a pre-repair or partly written checkout and pass bytes the repair then changes. Intended meaning (review-cadence design): none of them waits for another entity's worker; the recheck is dispatched after the repair has completed and committed its candidate.
- P2, `## Number guards` Applied bullet: "Before any push of a candidate to a persistent shared environment ... FO records `Applied at:`". If the push is rejected or the deploy never runs, nothing was applied but the migration is frozen, and a renumber then needs a Captain-authorized branch reset. Direction: keep recording before the push (a record forgotten after a successful push is the undetected case), and let FO remove that one `Applied at:` line when the push or deploy is confirmed not to have run, stating the evidence.
Non-goals: any Spacedock change; any change to `number_guards.py` beyond what the wording requires; other sections.

## Acceptance criteria

**AC-1** The `## Stages` lane paragraph no longer lists the validation recheck among what is "dispatched at once"; it says the recheck of a repair or fix is dispatched only after that repair or fix has completed and committed its candidate. Evidence: `test_sd_dispatch.py` asserts the new sentence is present and the 0.10.0 clause "the validation recheck of that repair, and an FO fix" is absent; falsifier: the same check run on a fixture holding the 0.10.0 paragraph reports both gaps.

**AC-2** The lane still does not make a repair, an FO fix or their recheck wait for another entity's worker in the same stage. Evidence: the two existing `LANE_RULE` phrases stay asserted and the existing feedback-reflow build while another entity holds the only `implementation` slot still passes; falsifier: deleting the "they do not wait" clause from a fixture fails the phrase check.

**AC-3** The `## Number guards` Applied bullet keeps "Before any push ... FO records `Applied at:`" and adds: when the push is rejected or the deploy is confirmed not to have run for that commit, FO replaces that one line with `Not applied: <environment> <sha> - <evidence>` and the migration is no longer frozen; without that confirmation the line stays. Evidence: `test_sd_dispatch.py` asserts those phrases; falsifier: a fixture holding the 0.10.0 bullet reports the gap.

**AC-4** `number_guards.py check` treats a `Not applied:` line as no record: an edit to a migration that a `Not applied:` line names passes (exit 0), and the same edit with an `Applied at:` line fails R2 (exit 1). Evidence: one new test in `test_number_guards.py` beside the existing recorded/unrecorded test; falsifier: loosening the `Applied at:` pattern in `number_guards.py` to match `Not applied:` makes it fail. `number_guards.py` itself is unchanged.

**AC-5** ADR 0004's Decision states the corrected lane rule and its Consequences carry one dated amendment line; ADR 0002 is unchanged. Evidence: `python3 <package>/scripts/adr_lint.py docs/adr` exits 0 and validation reads back the 0004 sentence against the `workflow.md` sentence (not mechanically enforced; stated as a limit).

**AC-6** Scope holds: the candidate touches only `kc-dev-flow-2/references/sd/workflow.md`, `kc-dev-flow-2/scripts/test_sd_dispatch.py`, `kc-dev-flow-2/scripts/test_number_guards.py` and `docs/adr/0004-*.md`; no Spacedock change and no other `workflow.md` section. Evidence: `git diff --stat <base> <candidate>` at validation; `comment_ratio.py` exits 0.

## FO alignment

Needed at ideation: exact replacement wording for both passages; whether `test_sd_dispatch.py`'s asserted lane phrase changes with it; what evidence a confirmed failed push must carry before the `Applied at:` line is removed, and whether `number_guards.py` needs any change.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none

## Design

### What this changes, in plain words

Two sentences in the workflow template told FO something other than what was meant. A validator could be started at the same moment as the repair it checks, and a failed push could freeze a migration that never reached a database. The fix is two rewritten passages, two test assertions and one ADR sentence. No new tool, no new state.

### Chain check (origin/main `c3b3d5ad`, read 2026-10-01)

- Spacedock 0.27.2 has no slot check on a reflow dispatch and no migration concept (ADR 0002 and 0004 Context); nothing upstream to reuse.
- `number_guards.py` already ignores an absent record: its pattern is line-anchored (`^Applied at:`), and `test_number_guards.py` already shows recorded commit exit 1, unrecorded exit 0. The P2 fix needs no code. Ran `python3 scripts/test_number_guards.py`: 17 tests OK. Ran `test_sd_dispatch.py` on Spacedock 0.27.2: all PASS lines, so the baseline is green.
- Both suites already run in CI (`.github/workflows/kc-dev-flow-2-tests.yml`); no CI cost is added.

### PRFAQ

Press line: FO reads one rule per hazard. A recheck starts after the repair it checks has committed, and a push that did not happen does not lock a migration.

- Q: Why not dispatch the recheck at once? A: The validator reads the worktree; a half-written repair passes, then changes. Codex reproduced this on qnow #1248 (P1).
- Q: Why keep recording before the push? A: A record forgotten after a successful push is the undetected case (ADR 0002 Consequences); a record kept after a failed push is the recoverable one.
- Q: Why replace the line instead of deleting it? A: A silent deletion leaves no evidence that the thaw was earned. `Not applied: <environment> <sha> - <evidence>` is free text `number_guards.py` does not read; the Captain's direction was to remove the line "stating the evidence".
- Q: What if FO cannot confirm the push did not run? A: The `Applied at:` line stays and Renumber holds for the Captain as today.

### Flow

```mermaid
flowchart TD
  F[Feedback route needs a repair or FO fix] --> D[FO dispatches repair in the entity's own worktree, no wait for another entity]
  D --> C{Repair completed and candidate committed?}
  C -- no --> W[Recheck is not dispatched]
  C -- yes --> R[FO dispatches validation recheck, no wait for another entity]
  P[FO pushes candidate to a shared environment] --> A[FO records Applied at BEFORE the push]
  A --> Q{Push accepted and deploy ran?}
  Q -- yes --> K[Line stays: migration frozen]
  Q -- unknown --> K
  Q -- "confirmed no: push rejected or no deploy of that sha" --> N[FO replaces the line with Not applied plus evidence: migration free]
```

### Exact replacement text

`references/sd/workflow.md`, `## Stages`, replacing from "A feedback-reflow repair," to "in the same stage." (the rest of the paragraph, "A repair that outgrows what its assignment names returns to FO as a scope change.", is unchanged):

> A feedback-reflow repair and an FO fix authorized under Review-finding disposition step 3 are dispatched at once in the entity's own worktree, after the existing overlap check against running worktrees; they do not wait for another entity's worker in the same stage. The validation recheck of that repair or fix does not wait for another entity's worker either, but it is dispatched only after the repair or fix has completed and committed its candidate, so the validator reads the bytes that will be delivered.

`## Number guards`, the `- **Applied.**` bullet, replacing the whole bullet:

> - **Applied.** Before any push of a candidate to a persistent shared environment (a non-production database branch), FO records `Applied at: <environment> <sha>` for the commit being pushed. A migration in that commit is then frozen for the task: edit, delete and renumber fail `check`. When the push is rejected or the deploy is confirmed not to have run for that commit (the push's non-zero output, or the environment's own deploy record showing no deploy of it), FO replaces that one line with `Not applied: <environment> <sha> - <evidence>` and the migration is no longer frozen. Without that confirmation the line stays and Renumber holds for the Captain. Git cannot see what a database applied, so an unrecorded deploy is not detected.

The line-wrapping of the existing file is kept; tests normalise whitespace.

### Where each rule lives

| Rule | Home | Enforced by |
| --- | --- | --- |
| Recheck after the repair commits | `workflow.md` `## Stages` | FO prose; phrase asserted in `test_sd_dispatch.py` |
| Record `Applied at:` before push; replace on confirmed no-run | `workflow.md` `## Number guards` | FO prose; phrases asserted; effect of the replaced line by `test_number_guards.py` |
| A `Not applied:` line thaws the migration | `number_guards.py` (existing pattern) | one new test |
| Corrected rule in the decision record | ADR 0004 | `adr_lint.py` format only |

### Test and script decisions

- `test_sd_dispatch.py`: the asserted phrase "are dispatched at once in the entity's own worktree" still occurs in the new text, and "`concurrency` limits only what `status --next` proposes" is untouched, so neither existing phrase must change. But neither catches the defect. The implementation adds to `LANE_RULE` the phrase "is dispatched only after the repair or fix has completed and committed its candidate", adds a forbidden phrase "the validation recheck of that repair, and an FO fix", and adds Applied-bullet phrases ("replaces that one line with `Not applied:", "Without that confirmation the line stays"). Falsifier: one helper returns the missing and forbidden phrases; it is run on the real template (empty result) and on a fixture with the 0.10.0 paragraph and bullet (non-empty), in the style of the existing `trimmed` fixture. It asserts wording, not behaviour; the behaviour is FO's and this is the strongest check available for prose.
- `number_guards.py`: no change. The regex is anchored on `Applied at:` so `Not applied: ...` is not matched.
- `test_number_guards.py`: one test, "a `Not applied:` line in place of the record leaves the edit unfrozen".

### ADR

- ADR 0004 (Decision restates the lane rule, "its validation recheck ... dispatched at once"): edit that sentence in place to the corrected rule and add one line to Consequences: "Amended <landing date>: the validation recheck is dispatched after the repair completes and commits, not at once with it (`workflow.md` Stages)." Per the retained-documents rule, an affected claim is updated with the approved change. The Captain's quoted words in 0004 are untouched.
- ADR 0002: none. Its Decision says what `check` refuses, not when the record is written; "a deploy nobody recorded" stays true. No number to reserve, no new ADR.

### Failure modes

- FO removes the line on a guess: the wording requires stated evidence and otherwise leaves the line; not mechanically enforced (prose), reopen if a wrongly thawed migration reaches a checksum failure.
- A push partly ran: "unknown" keeps the line, the Captain-authorized reset path applies.
- Rewording drifts from the adopters' synced README copies: the adopter re-sync (kc-claude-plugins #542, qnow #1248, held) happens after release; not part of this task.

### Profile and release notes

Pilot stays: wording and a test only, no new obligation. Commit type `fix(kc-dev-flow-2): ...`; release-please proposes the version (a fix gives a patch release); no hand bump.

### Needs the Captain

Nothing. One point for FO awareness, not a decision: replacing the line with `Not applied: ...` rather than deleting it is a small addition to the Captain's 「同意」 wording ("remove that one line ... stating the evidence"); it is the evidence's home. Say if you would rather have a plain deletion.

### Captain acceptance script (after delivery; `$PKG` is a checkout of the merged code)

```
cd $PKG/kc-dev-flow-2
sed -n '/^## Stages/,/^FO resolves/p' references/sd/workflow.md   # read: the recheck is dispatched only after the repair commits; nothing waits for another entity
sed -n '/\*\*Applied\.\*\*/,/\*\*Check\.\*\*/p' references/sd/workflow.md   # read: record before push; replace with Not applied plus evidence only when confirmed
python3 scripts/test_number_guards.py                              # expect OK; includes the Not-applied test
SPACEDOCK_BIN=$(command -v spacedock) python3 scripts/test_sd_dispatch.py --sd-plugin-root <activated spacedock root>   # expect PASS lines
python3 scripts/adr_lint.py ../docs/adr                            # expect 6 ADR file(s) checked, exit 0
```
Falsifier by hand: in a scratch copy, put the 0.10.0 sentence back (`git show c3b3d5ad:kc-dev-flow-2/references/sd/workflow.md`) and rerun `test_sd_dispatch.py`; it must fail naming the missing lane phrase.

### Cost

No new CI job or runtime; the two suites already run per kc-dev-flow-2 PR. Not measured beyond a local baseline run.

## Stage Report: ideation

- DONE: Exact replacement text for the `## Stages` lane paragraph (repair and FO fix dispatch at once; recheck after the repair completes and commits)
  `## Design` § Exact replacement text; the recheck no longer sits in the "at once" list and does not wait for another entity's worker either.
- DONE: Exact replacement text for the `## Number guards` Applied bullet (record before push; FO replaces that one line with `Not applied: <env> <sha> - <evidence>` when the push or deploy is confirmed not to have run)
  `## Design` § Exact replacement text; without confirmation the line stays and Renumber holds for the Captain.
- DONE: Whether `test_sd_dispatch.py`'s asserted phrases change and whether `number_guards.py` needs any change
  Existing `LANE_RULE` phrases still occur but do not catch the defect, so phrases are added (plus one forbidden phrase); `number_guards.py` unchanged, its `^Applied at:` pattern ignores `Not applied:`; baseline `test_number_guards.py` 17 OK and `test_sd_dispatch.py` PASS on Spacedock 0.27.2 at c3b3d5ad.
- DONE: AC-1 lane paragraph says the recheck follows the repair's commit
  Plan: phrase asserted in `test_sd_dispatch.py`, falsifier a fixture with the 0.10.0 paragraph; not yet run, nothing implemented.
- DONE: AC-2 the lane still waits for no other entity's worker
  Existing `LANE_RULE` phrases plus the existing reflow build while another entity holds the only implementation slot (passed at baseline today); falsifier by deleting the clause in a fixture is planned.
- DONE: AC-3 Applied bullet keeps record-before-push and adds the confirmed-no-run replacement
  Plan: phrases asserted with a 0.10.0-bullet fixture as falsifier; not yet run.
- DONE: AC-4 `number_guards.py check` treats `Not applied:` as no record
  Plan: one new test in `test_number_guards.py` beside the recorded/unrecorded test (existing recorded-exit-1 / unrecorded-exit-0 passes today); mutation: loosen the pattern.
- DONE: AC-5 ADR 0004 corrected and amended once; ADR 0002 unchanged
  Decision in `## Design` § ADR; `adr_lint.py docs/adr` exits 0 today (6 files); read-back of 0004 against workflow.md is not mechanically enforced.
- DONE: AC-6 scope holds to four files, no Spacedock or other-section change
  Plan: `git diff --stat` at validation and `comment_ratio.py`; not yet verified.
- DONE: ADR need, and the Captain-run minimal acceptance script
  `## Design` § ADR (amend 0004 in place, none for 0002, no number reserved) and § Captain acceptance script (five commands plus a by-hand falsifier); `design_surfaces.py check` exits 0 ("design surfaces presentable").

### Summary

Two wording fixes, four files, no new mechanism. Only detail beyond the Captain's 「同意」 is that the replaced line becomes `Not applied: ... - <evidence>` rather than a silent deletion; FO may ask the Captain, otherwise a plain deletion is a one-line change. Nothing else needs a Captain ruling; nothing was implemented or committed to the repository.
