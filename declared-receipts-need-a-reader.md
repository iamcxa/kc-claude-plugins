---
id: k69wjs5ttme3z11hph3sy45d
title: continue-dev-flow states the stage's declared receipts to the working agent
status: validation
source: residual named at every gate of declared-receipt-has-no-reader (#256) and ruled on by the Captain, 2026-08-20 — ship the reader before the emitted field repeats the defect it was added to answer
product: kc-dev-flow
sprint:
started: 2026-08-21T07:24:22Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-declared-receipts-need-a-reader
issue:
pr: 264
mod-block:
gates:
    version: 1
    records:
        - id: gate:k69wjs5ttme3z11hph3sy45d:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:k69wjs5ttme3z11hph3sy45d-backlog-1
              briefing:
                id: briefing:k69wjs5ttme3z11hph3sy45d:backlog:attempt-1:revision-1
                digest: sha256:3a819626edd78e0af363c7505c85917b0a412b12425b73720ccfa7903d155150
                request-digest: sha256:442ee4660c5f499688d44ea995dcbaeb5e470769933ce0787495eebc7d514fac
                room-ref: ./declared-receipts-need-a-reader/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:k69wjs5ttme3z11hph3sy45d:backlog:1
                briefing: briefing:k69wjs5ttme3z11hph3sy45d:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-21T07:23:24.930534Z"
                decision: approve
                reason: 'Captain approved scheduling with the Pilot work profile. The task ships the first reader for declared_receipts so the emitted field does not repeat the defect #256 reported one layer up. Pilot rather than Production because this changes what a skill tells an agent, not an output contract adopters read at a pinned tag, so it carries no release or rollback obligation. Delivery base stays stacked on PR #262''s branch per delivery-branch-base.md: #262 is an open artifact sharing this candidate''s lineage through declared_receipts.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:k69wjs5ttme3z11hph3sy45d:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:k69wjs5ttme3z11hph3sy45d-ideation-1
              briefing:
                id: briefing:k69wjs5ttme3z11hph3sy45d:ideation:attempt-1:revision-1
                digest: sha256:7a2bc5c6d9a414b5244a7a99879279e458c427a96ae6270493286cc978339700
                request-digest: sha256:f929090cd0081edfc02658bc368623065f9cca364948954f769b390d8255d088
                room-ref: ./declared-receipts-need-a-reader/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:k69wjs5ttme3z11hph3sy45d:ideation:1
                briefing: briefing:k69wjs5ttme3z11hph3sy45d:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-21T07:31:05.140044Z"
                decision: approve
                reason: Captain approved the ideation shape. It names the exact replaced sentence pair and the exact replacement text, worded so it says the stage declares receipts behind an agent-evaluated trigger and never that it owes one, and it corrected the FO's own line citation (:40-41 to :41-42) by reading the file rather than copying. Check 1 is verified RED on this branch today (grep -rl declared_receipts kc-dev-flow returns nothing), which also proves the stacked base is a requirement rather than a preference. Approved with the FO condition that check 2 be satisfied by a one-time inspection recorded in the stage report and never committed as a standing presence-grep.
              application:
                target-stage: implementation
                state: consumed
        - id: gate:k69wjs5ttme3z11hph3sy45d:validation
          stage: validation
          attempts:
            - id: gate-attempt:k69wjs5ttme3z11hph3sy45d-validation-1
              briefing:
                id: briefing:k69wjs5ttme3z11hph3sy45d:validation:attempt-1:revision-1
                digest: sha256:29a72bc3154e8764e4c6977e3549992c582732bc1017ea125a197d7b423f7dcc
                request-digest: sha256:16dd612dc3c290d931235d7d33e5e046a0a14f7010d9c209a392691a3713df92
                room-ref: ./declared-receipts-need-a-reader/review/validation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-08-21T07:50:47.511073Z"
                reason: 'Captain inserted an integration check before this gate closes: the file-level evidence proves the skill says the right sentence, not that an agent following it sees the field. Replacement briefing follows that probe.'
            - id: gate-attempt:k69wjs5ttme3z11hph3sy45d-validation-2
              briefing:
                id: briefing:k69wjs5ttme3z11hph3sy45d:validation:attempt-2:revision-1
                digest: sha256:c97cf356dd80e14722b27ac88701d34c1d64f2eb46bde462da953802cb7d316d
                request-digest: sha256:2b6ca2f2e19b2a9c450485d02435d89409ede23cc800e09e62956b6cd309d1c1
                room-ref: ./declared-receipts-need-a-reader/review/validation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:k69wjs5ttme3z11hph3sy45d:validation:2
                briefing: briefing:k69wjs5ttme3z11hph3sy45d:validation:attempt-2:revision-1
                by: person:captain
                at: "2026-08-21T08:04:49.003582Z"
                decision: approve
                reason: 'Captain approved verify-deliver at f351f440 after the inserted integration check. A blind agent following the edited skill reached declared_receipts through the documented default text invocation rather than re-parsing the conditional-references block, and volunteered that the four null receipts correctly did not appear; its blindness conditions (neutral work item containing the field name zero times, field name absent from its prompt, reporting a break declared a valid answer) are recorded. Check 1 separately proven by a positive/negative loader pair against origin/main. One-file verbatim prose diff, loader and both vendored copies untouched, no standing grep committed. Two prose defects the probe surfaced are pre-existing and dispositioned out of scope. PR #264 Draft, based on #262''s branch because the change cannot function without it. Mark-ready and merge remain the Captain''s actions.'
              application:
                target-stage: release
                state: pending
---

## Problem

`declared-receipt-has-no-reader` (#256, PR #262) makes the profile loader emit
`declared_receipts` — the receipt names the selected stage contract declares.
Nothing reads it. That is the same shape as the defect #256 reported, moved one
layer up: a field that names an obligation, emitted in machine-readable output,
consumed by nobody.

`continue-dev-flow` is the natural reader. It already invokes the loader and
already tells the working agent to "Record a named receipt in the existing work
item" (`skills/continue-dev-flow/SKILL.md:62`), but the agent learns *which*
receipt only by parsing the contract's `kc-dev-flow-conditional-references/v1`
JSON block itself (`SKILL.md:40-41`). The loader has already parsed, validated
and hash-bound that block; handing the list up front replaces a re-parse with a
read.

What this buys is visibility at the moment of action, not a guarantee. `trigger`
stays prose the agent evaluates, so the strongest true statement the skill can
make is "this stage declares these receipts, each behind a trigger you must
evaluate" — never "this stage owes X".

## Verification boundary (decided before the work starts)

Two layers, and only one is verifiable here:

- **Verifiable:** `declared_receipts` reaches the skill's documented invocation
  and the skill's instruction reads it. A check can fail on this.
- **Not verifiable in this repository today:** whether agents that read the
  instruction record receipts more often. That is a behavioural A/B comparison,
  and the entity that would build the instrument — `skill-ablation-harness`
  (`5b5gp68f2aq0bdrcf3q28jgg`, "Cutting prose from a skill has no failure signal
  — build one before cutting") — records its review driver as MISSING and its
  materiality verdict as EXISTS_BROKEN. It is a larger entity than this one.

Do not attempt the behavioural measurement here, and do not claim the
instruction is effective. Claim only what the first layer proves.

## Closing #256

When this lands, `#256` closes with a bounded note: the ambiguity is gone (the
loader emits the declared names, `continue-dev-flow` reads them, and the
docstring records the exact boundary), and the obligation is still unverified by
design — no evaluable `trigger`, no stage-exit check. Option 2 gets no
speculative issue; the first observed case of a receipt that should have been
produced and was not is what opens it.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: "Changes what one skill tells a working agent, not an output contract adopters read at a pinned tag. No runtime, no operational commitment, no rollback surface; the loader's emitted shape is unchanged by this task. A real slice with a real user (the dispatched agent), so not POC."
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - "Read the receipt names from the loader's already-parsed, hash-bound output; do not add a second parse of the conditional-references block alongside the existing one."
      - "The skill may state that a stage declares a receipt behind a trigger the agent must evaluate; it may never state that a stage owes one, because `trigger` stays prose."
    implementation:
      - "Replace the instruction that sends the agent to parse the JSON block itself, rather than layering a second instruction beside it."
      - "Keep the loader and both vendored copies untouched — this task changes skill prose only."
    testing:
      - "A check that fails when the documented invocation stops surfacing declared_receipts to the skill, and one that fails when the skill's instruction no longer references it."
      - "No behavioural measurement of the prose's effect on agents; that instrument does not exist here."
  scope_boundary: "Excludes evaluable triggers, any stage-exit receipt check, any change to the loader or the contracts, and any claim that the instruction changes agent behaviour."
  promote_when:
    - "The reader is asked to block or gate on a missing receipt, which would make it enforcement rather than visibility."
    - "An adopter outside this repository is asked to depend on the skill's wording as a contract."
  decision:
    authority: person:captain
    at: 2026-08-21T07:23:52Z
```

## Accepted outcome and non-goals

**Instruction replaced.** In `kc-dev-flow/skills/continue-dev-flow/SKILL.md`,
"Load one route", the sentence pair that currently sends the working agent to
discover a stage's receipt names only by parsing the stage contract's own
`kc-dev-flow-conditional-references/v1` block (current text, verified at
SKILL.md:41-42 — one line later than this entity's earlier :40-41 citation
because an unrelated intervening RoboRev edit shifted the file by one line):

> A selected stage may emit a `kc-dev-flow-conditional-references/v1` block.
> For each entry, resolve `path` relative to the selected stage contract and
> read it only when its named `trigger` is true; otherwise leave it unread.

is REPLACED by:

> A selected stage may emit a `kc-dev-flow-conditional-references/v1` block;
> the loader's output already parses that block into `declared_receipts` — the
> receipt names this stage declares, each behind a trigger you evaluate. Read
> `declared_receipts` for those names instead of re-parsing the block for
> `receipt`. For each entry, still resolve `path` relative to the selected
> stage contract and read it only when its named `trigger` is true; otherwise
> leave it unread.

This sentence is sayable truthfully while `trigger` stays prose: it says the
stage *declares* receipts behind a trigger the agent evaluates, and it never
says the stage *owes* one. The paragraph's remaining sentences (trigger
semantics, `retained_document_change`, `project_context_claim_may_change`,
`delivery_artifact_review`, `pr_delivery_selected`,
`implementation_exit_observation_declared`, and "Record a named receipt in the
existing work item; `receipt: null` creates no receipt." at SKILL.md:62-63) are
unchanged — this task edits only the one replaced sentence pair, not the
trigger-resolution or receipt-recording instructions around it.

**Non-goals:** no evaluable `trigger` (stays prose the agent evaluates); no
stage-exit check that blocks on a missing receipt; no change to the loader,
either vendored copy, or any stage/profile contract — this task is prose-only
in one skill file; no second parse added beside the existing one (the replaced
sentence removes the receipt-parsing need, it does not add a parallel one); no
claim, anywhere in this entity or the eventual diff, that the instruction
changes what a working agent records.

**Persistence, recovery, data-safety boundaries:** none apply. This is a
documentation edit to one skill file — no persisted state, no runtime data
path, no schema, nothing to recover. The loader's emitted contract shape is
unchanged by this task (obligation already recorded in the work profile
receipt above); only the prose that reads one already-emitted field changes.

**Task-specific acceptance checks (falsify the slice):**

1. **Loader-surfaces-the-field check.** Run the canonical loader invocation
   documented at SKILL.md:66-72 against a stage contract whose own
   `kc-dev-flow-conditional-references/v1` block declares a non-null `receipt`.
   Assert the JSON output's top-level `declared_receipts` array contains that
   receipt's name. This check FAILS if `declared_receipts` is absent, empty, or
   omits a declared non-null receipt — i.e., it fails if the documented
   invocation stops surfacing the field, which is exactly what this task's
   testing obligation requires be falsifiable.
2. **Skill-reads-the-field check.** Inspect `SKILL.md`'s "Load one route"
   section for a sentence that reads `declared_receipts` from the loader's
   output, in place of the removed instruction to discover receipt names by
   parsing the raw block. This check FAILS if no such sentence exists, or if
   the sentence asserts the stage *owes* a receipt rather than *declares* one
   behind an agent-evaluated trigger — i.e., it fails if the instruction
   reverts to the pre-change parse-it-yourself shape, or oversteps `trigger`'s
   prose status.

No third check attempts a behavioural measurement. See Measurement.

## Acceptance evidence

Both checks above sit entirely on the verifiable layer named in "Verification
boundary": (1) the documented loader invocation surfaces `declared_receipts` to
the skill's input, and (2) the skill's instruction reads that field instead of
re-parsing the block. Neither check inspects, samples, or infers a working
agent's behaviour; both are checkable by direct execution (check 1) and direct
text inspection (check 2), independent of who or what reads the resulting
prose.

**Explicitly not asserted:** no acceptance criterion here — and none should be
added at build or verify-deliver — claims that this wording change causes a
working agent to record receipts more often or more accurately. That is a
behavioural A/B comparison between agents that read the old prose and agents
that read the new prose, and no instrument exists in this repository to run
it. The entity that would build that instrument,
`skill-ablation-harness` (`5b5gp68f2aq0bdrcf3q28jgg`, "Cutting prose from a
skill has no failure signal — build one before cutting"), records its own
review driver as MISSING and its materiality verdict as EXISTS_BROKEN; it is a
larger, separate entity than this one and is not a dependency of this task's
acceptance.

## Measurement

**Delivery base, with evidence, not preference.** This candidate stacks on PR
#262 (`spacedock-ensign/declared-receipt-has-no-reader`), not on `main`.
Verified directly:

- `git diff main origin/spacedock-ensign/declared-receipt-has-no-reader --
  kc-dev-flow` shows `declared_receipts` introduced only on that branch, in the
  vendored loader's `check_conditional_references`, `load_contracts`, and
  `render_text` functions (`kc-dev-flow/references/profile_loader.py` per the
  diff).
- `grep -rl declared_receipts kc-dev-flow` against this checkout's current
  `main`-tracking tree returns no match — the key does not exist anywhere in
  the vendored loader on `main` today.

Because the key the replaced sentence tells the agent to read does not exist in
the loader `main` ships, an edit landing on `main` alone would document a field
the loader never emits — the SKILL.md instruction would not function until the
loader that emits `declared_receipts` is itself merged. That non-existence on
`main`, not a stacking preference recorded in `delivery-branch-base.md`, is why
this candidate's base is #262's branch: #262 is the open artifact that shares
this candidate's lineage through `declared_receipts`, per the backlog gate's
resolution reason already recorded above.

## Stage Report: ideation

- DONE: Load the selected `shape` contract and produce its required output — one accepted journey and explicit non-goals, persistence/recovery/data-safety boundaries, and task-specific falsifiable acceptance checks.
  `kc-dev-flow/references/profiles/pilot-product-slice/shape.md` loaded; "Accepted outcome and non-goals" section written with the exact replaced sentence, the exact replacement sentence, non-goals, and boundaries.
- DONE: Record the accepted outcome naming the exact wording change — which instruction is replaced (SKILL.md:41-42, not the entity's earlier :40-41 — file drifted one line via commit 4609abe0) and the exact sentence that replaces it, sayable truthfully while `trigger` stays prose.
  Verified current SKILL.md text via `grep -n '' kc-dev-flow/skills/continue-dev-flow/SKILL.md`; quoted both sentences verbatim in "Accepted outcome and non-goals".
- DONE: Record acceptance evidence naming a check that fails only on the verifiable layer (loader surfaces `declared_receipts`, skill reads it), stating explicitly that no criterion asserts behavioural change and why that instrument is absent.
  "Acceptance evidence" section names two checks and cites `skill-ablation-harness` (5b5gp68f2aq0bdrcf3q28jgg) as the missing instrument, out of scope here.
- DONE: Record the stacked delivery base with evidence, not preference — the vendored loader on `main` carries no `declared_receipts` key, verified against PR #262's branch.
  `git diff main origin/spacedock-ensign/declared-receipt-has-no-reader -- kc-dev-flow` shows `declared_receipts` added only on #262's branch (`references/profile_loader.py`); `grep -rl declared_receipts kc-dev-flow` against this checkout's `main`-tracking tree returns no match (exit 1). "Measurement" section records both commands and their results.

### Summary

Wrote the Pilot shape's required output for `declared-receipts-need-a-reader`: the exact SKILL.md sentence pair being replaced and its exact replacement, non-goals, persistence/data-safety boundaries (none apply — prose-only), two falsifiable acceptance checks scoped to the verifiable layer only, and the delivery-base evidence tying this candidate to PR #262. No code was changed in this stage — ideation is shape-only; the SKILL.md edit itself belongs to the build stage.

## Stage Report: implementation

- DONE: Fix the delivery base — re-point the branch at PR #262's branch before editing.
  `git reset --hard origin/spacedock-ensign/declared-receipt-has-no-reader` (branch moved from `--stamp` tip `679b1614` to `10edd0a4`). Confirmed: pre-reset `grep -rl declared_receipts kc-dev-flow/` returned nothing; post-reset it returns `kc-dev-flow/scripts/profile-contract-loader.py` and `kc-dev-flow/scripts/profile-contract-loader.test.py`.
- DONE: Make the one prose edit named in "Accepted outcome and non-goals" — replace the sentence pair at SKILL.md:41-42 with the exact replacement text, verbatim, and nothing else in the file.
  `git diff -- kc-dev-flow/skills/continue-dev-flow/SKILL.md` shows exactly the 2-sentence removal / 4-sentence replacement at the cited location (7 insertions, 3 deletions, 1 file). Trigger-resolution sentences, "Record a named receipt…", the loader, and both vendored copies (`kc-dev-flow/scripts/profile-contract-loader.py`, `docs/dev/_mods/profile-contract-loader.py`) are untouched — confirmed via `git status --short` showing only the one SKILL.md path. Committed as `f351f440` on `spacedock-ensign/declared-receipts-need-a-reader`.
- DONE: Satisfy check 1 — run the canonical documented loader invocation against a contract declaring a non-null receipt, paste `declared_receipts` output.
  Built a real work item (`/tmp/check1-work-item.md`, frontmatter `status: implementation`, `Work profile receipt` block selecting `pilot-product-slice`) and ran the documented invocation against the real contracts root:
  `python3 kc-dev-flow/scripts/profile-contract-loader.py --contracts-root kc-dev-flow/references --work-item /tmp/check1-work-item.md --format json`
  resolves `logical_stage: "build"` (`kc-dev-flow/references/profiles/pilot-product-slice/build.md`, which declares `"receipt": "project_context"` at line 39). Output: `"declared_receipts": ["project_context"]` — the field surfaces the non-null declared receipt name, satisfying check 1.
- DONE: Satisfy check 2 — one-time inspection recorded in the stage report; no standing presence-grep, lint rule, or committed check over SKILL.md's own wording.
  Manual inspection of the "Load one route" section post-edit (SKILL.md:41-46): the new sentence "the loader's output already parses that block into `declared_receipts` — the receipt names this stage declares, each behind a trigger you evaluate. Read `declared_receipts` for those names instead of re-parsing the block for `receipt`." reads the field by name, replaces the removed parse-it-yourself instruction, and uses "declares" (never "owes") — trigger stays prose the agent still evaluates per the retained following sentence. This inspection is not committed as a script, grep, or CI check; only its result is recorded here, per the entity's instruction that a presence-grep over prose just written proves nothing.

### Summary

Reset the worktree branch onto PR #262's branch (`spacedock-ensign/declared-receipt-has-no-reader`) so `declared_receipts` exists to document; made the single prose replacement at SKILL.md:41-42 exactly as specified in "Accepted outcome and non-goals," touching no other line, the loader, or either vendored copy; verified check 1 by running the real vendored loader against a real pilot-product-slice contract with a non-null declared receipt (`project_context`) and observing it in `declared_receipts`; verified check 2 by one-time manual inspection of the edited sentence, recorded here rather than as a standing check. Commit `f351f440` on `spacedock-ensign/declared-receipts-need-a-reader`.

## Stage Report: validation

- DONE: Prove check 1 discriminates against a real shipped contract, not a fixture, on both sides.
  Built a real work item (`/tmp/check1-work-item.md`, frontmatter `status: implementation`, a real `## Work profile receipt` block selecting `pilot-product-slice`) and ran the documented invocation `python3 kc-dev-flow/scripts/profile-contract-loader.py --contracts-root kc-dev-flow/references --work-item /tmp/check1-work-item.md --format json` on this branch (contains #262's loader). Output: `"declared_receipts": ["project_context"]` — resolved from the real `profiles/pilot-product-slice/build.md` contract's own `"receipt": "project_context"` entry, not a synthetic fixture. Then fetched the pre-#262 loader and contracts tree from `origin/main` via `git show origin/main:kc-dev-flow/scripts/profile-contract-loader.py` and `git archive origin/main -- kc-dev-flow/references`, and ran the identical invocation and identical work item against that main-tracking copy: `grep -c declared_receipts` on the main loader script returns `0`, and its JSON output carries no `declared_receipts` key at all. Same work item, same contracts shape, one loader emits the field and the other cannot — the check discriminates on the loader version, not on fixture construction.
- DONE: Confirm the edit is verbatim and isolated.
  `git diff origin/spacedock-ensign/declared-receipt-has-no-reader HEAD --stat` shows exactly one file, `kc-dev-flow/skills/continue-dev-flow/SKILL.md`, `7 insertions(+), 3 deletions(-)`. The replacement text in the diff matches "Accepted outcome and non-goals" word for word. Read SKILL.md:41-63 post-edit: the trigger-resolution sentences (`retained_document_change`, `project_context_claim_may_change`, `delivery_artifact_review`, `pr_delivery_selected`, `implementation_exit_observation_declared`) and "Record a named receipt in the existing work item; `receipt: null` creates no receipt." are byte-identical to pre-edit. `git diff origin/spacedock-ensign/declared-receipt-has-no-reader HEAD -- kc-dev-flow/scripts/profile-contract-loader.py docs/dev/_mods/profile-contract-loader.py` is empty — loader and both vendored copies untouched. `git diff origin/spacedock-ensign/declared-receipt-has-no-reader HEAD | grep -iE "SKILL\.md"` returns only the diff header lines for the one edited file itself — no new grep, lint, or check over SKILL.md's own wording exists anywhere in the branch diff.
- DONE: Deliver a Draft PR based on PR #262's branch, not main.
  Verified mergeability first: `git merge-tree --write-tree $(git rev-parse origin/spacedock-ensign/declared-receipt-has-no-reader) $(git rev-parse HEAD)` returned a clean tree, exit 0 (candidate is a fast-forward descendant of the base, so this is a trivial clean merge). Pushed the exact candidate revision by SHA refspec: `git push origin f351f440841c98587e4bedd086b53dbeeabb060b:refs/heads/spacedock-ensign/declared-receipts-need-a-reader`. Opened [PR #264](https://github.com/iamcxa/kc-claude-plugins/pull/264) via `gh pr create --draft --base spacedock-ensign/declared-receipt-has-no-reader --head spacedock-ensign/declared-receipts-need-a-reader`, body from a mode-0600 temp file removed after submission. Confirmed via `gh pr view 264 --json baseRefName,isDraft`: `baseRefName: "spacedock-ensign/declared-receipt-has-no-reader"`, `isDraft: true`. The PR body records the stacked-base evidence (`declared_receipts` absent from `origin/main`'s vendored loader entirely), both acceptance checks with their output, and the explicit statement that no claim is made about this wording changing what a working agent records, naming `skill-ablation-harness` (5b5gp68f2aq0bdrcf3q28jgg) as the absent instrument. Left as Draft — not marked ready, per the Captain's reserved action.

### Summary

Re-verified both acceptance checks with fresh evidence rather than trusting the implementation stage's record: check 1 now has an explicit negative control (the pre-#262 `main` loader, fetched and run standalone, has no `declared_receipts` key at all) proving the check discriminates on the loader version, not merely on the fixture. Check 2's verbatim/isolation claim was independently re-confirmed by diffing against the stacked base directly (`git diff origin/spacedock-ensign/declared-receipt-has-no-reader HEAD`), which also proves no standing check over SKILL.md wording exists in the branch. Delivered [PR #264](https://github.com/iamcxa/kc-claude-plugins/pull/264), Draft, based on `spacedock-ensign/declared-receipt-has-no-reader` (#262), carrying commit `f351f440` and the required evidence in its body. Not marked ready.

## Stage Report: validation (cycle 2)

- DONE: Record the integration probe — a blind agent reaches `declared_receipts` through the documented default invocation, not by re-parsing the conditional-references block.
  Evidence, two sources: (a) first-hand — `skill-wiring-probe` (the agent that ran the probe; it wrote no file, per its own dispatch, and returned its report as inline text to its caller) pasted its report directly to me; (b) second-hand — the FO's own record at `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.context/probe/result.md`, written by the FO from the same probe's returned report. The two agree on every fact checked (invocation run, header line read, defects found); where the FO's file and the probe's own words could conflict, the probe's inline text is first-hand and would govern, but no conflict exists. A general-purpose agent with no knowledge of this task was pointed at the worktree's `continue-dev-flow/SKILL.md` and asked only "which receipt names does the selected stage declare?" It ran the DEFAULT TEXT invocation (no `--format json` — the path the skill actually documents): `python3 <worktree>/docs/dev/_mods/profile-contract-loader.py --contracts-root <worktree>/docs/dev/_mods --work-item <repo>/.context/probe/work-item.md`, and read `declared_receipts` directly off the loader's header line (`{"declared_receipts": ["project_context"], "logical_stage": "build", ...}`), citing the newly added sentence as what told it where to look. Unprompted, it also noted the conditional-references block lists five entries of which four carry `receipt: null` and correctly do not appear in `declared_receipts` — i.e. it did not fall back to re-parsing that block.
- DONE: Name why the probe's blindness matters.
  Three conditions, all confirmed by both sources: (1) the work item it was given (`.context/probe/work-item.md`) contains the string `declared_receipts` zero times; (2) its prompt never mentioned that field name — it was asked only for the receipt names, not told where to look; (3) it was told that reporting a break in the instructions is a valid answer. Without all three, an agent answering "yes, I read the field" would prove nothing — it could be pattern-matching the question back at the interviewer rather than actually following the skill's wiring. With them, the passing answer is evidence the wiring (skill prose to `declared_receipts` header) holds for an agent that has no reason to already know the answer and no penalty for reporting failure.
- DONE: Record the two prose defects the probe surfaced, with disposition.
  Both in `kc-dev-flow/skills/continue-dev-flow/SKILL.md`, "Load one route" section, both pre-existing: (1) "invoke the loader declared in `## Local Profile`" without stating where that section lives — the probe had to reach into the separate "Resolve authority before policy" step to resolve it; (2) the canonical invocation template's `<profile-loader>` placeholder has no resolution rule stated in that same section. Both sentences are untouched by this task's diff (`git diff origin/spacedock-ensign/declared-receipt-has-no-reader HEAD -- kc-dev-flow/skills/continue-dev-flow/SKILL.md` shows only the conditional-references sentence pair replaced; neither defect's text appears in the diff hunks). Observed cost: three extra tool calls for the probe to resolve the forward reference. The FO ruled both too small to file as their own task and out of this task's declared scope. Not fixed here.
- DONE: Re-confirm the delivery is unchanged by this stage.
  `gh pr view 264 --json baseRefName,isDraft,headRefOid,files` (run independently of the probe, which ran no git commands and made no claim about PR state): `isDraft: true`, `baseRefName: "spacedock-ensign/declared-receipt-has-no-reader"`, `headRefOid: "f351f440841c98587e4bedd086b53dbeeabb060b"`, `files: [{"path": "kc-dev-flow/skills/continue-dev-flow/SKILL.md", "additions": 7, "deletions": 3}]` — the sole diffed file, matching the pre-probe state recorded in cycle 1. No file in the branch diff changed while the probe ran.

### Summary

The Captain-requested integration probe closes the gap the file-level checks left open: a blind agent, primed only with a neutral work item and no mention of the field name, followed the edited SKILL.md through its documented default-text invocation and read the receipt names off `declared_receipts` rather than re-parsing the conditional-references block — end-to-end wiring holds. Two pre-existing, out-of-diff prose gaps surfaced as a side effect (unresolved `## Local Profile` forward reference, bare `<profile-loader>` placeholder); both are recorded with disposition (too small to file, out of scope) and left unfixed. PR #264 re-confirmed unchanged: Draft, based on `spacedock-ensign/declared-receipt-has-no-reader`, head `f351f440`, single-file diff.
