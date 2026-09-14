---
title: "The POC close path has never been walked end to end, and two defects sit on it"
status: done
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: dev-flow-poc-close-path
sprint-readiness: ready
started:
completed: 2026-09-14T10:37:42Z
verdict: PASSED
worktree: .worktrees/spacedock-ensign-poc-close-path-never-walked
issue:
pr: pr-merge:443
mod-block:
id: xve5t292zy54mncx0xm6m3v0
gates:
    version: 1
    records:
        - id: gate:xve5t292zy54mncx0xm6m3v0:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:xve5t292zy54mncx0xm6m3v0-backlog-1
              briefing:
                id: briefing:xve5t292zy54mncx0xm6m3v0:backlog:attempt-1:revision-1
                digest: sha256:428b3078ab6c5b24debe880d41a5fbe352e745e8b981d87cef75bd5e73592ad2
                room-ref: ./poc-close-path-never-walked/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:xve5t292zy54mncx0xm6m3v0:backlog:1
                briefing: briefing:xve5t292zy54mncx0xm6m3v0:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T07:48:37.215439Z"
                decision: approve
                reason: Captain approved in chat 2026-09-14 after the FO presented both defects with their reproductions, the reason for one task rather than two, and the Pilot selection justified by the previous POC selection on this path running past budget and needing a mid-flight amendment.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:xve5t292zy54mncx0xm6m3v0:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:xve5t292zy54mncx0xm6m3v0-ideation-1
              briefing:
                id: briefing:xve5t292zy54mncx0xm6m3v0:ideation:attempt-1:revision-1
                digest: sha256:7a09dc39e762c5d2d2646d8b5bcc18be148a058470d2d61aa2445fbe59042c4f
                room-ref: ./poc-close-path-never-walked/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:xve5t292zy54mncx0xm6m3v0:ideation:1
                briefing: briefing:xve5t292zy54mncx0xm6m3v0:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T08:07:06.807083Z"
                decision: approve
                reason: 'Captain approved in chat 2026-09-14 ("按建議") on the FO gate presenting shape ruling (b): the two POC outcome headings leave the accepted-authority projection by exact heading. (c) was eliminated because bind_stage_pin also makes validation non-re-enterable once the prove worker writes, so no worker could record the direction it depends on; (a) collapses into (b) or leaves same-stage re-entry broken. Defect 2 refuses by name at the admitted_at comparison. The Captain also took the recommendation to keep the missing iamcxa/kc-claude-plugins docs/architecture.md out of this slice and admit it as its own item, with build proceeding against root ARCHITECTURE.md.'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:xve5t292zy54mncx0xm6m3v0:validation
          stage: validation
          attempts:
            - id: gate-attempt:xve5t292zy54mncx0xm6m3v0-validation-1
              briefing:
                id: briefing:xve5t292zy54mncx0xm6m3v0:validation:attempt-1:revision-1
                digest: sha256:cf53ae5690a14e8c3ebbde43852e5947c95bde0833d797b1407120e559c86420
                room-ref: ./poc-close-path-never-walked/review/validation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-09-14T08:54:26.879129Z"
                reason: 'Captain asked why a test that cannot fail is not simply deleted. He is right and the gate question is now wrong: it offered to record poc_non_goals_refused as a residual, which contradicts the retention rule this repository just spent two pull requests establishing. Returning to implementation to delete the case, then re-validating and re-presenting.'
            - id: gate-attempt:xve5t292zy54mncx0xm6m3v0-validation-2
              briefing:
                id: briefing:xve5t292zy54mncx0xm6m3v0:validation:attempt-2:revision-1
                digest: sha256:88054d3590b9c05c5ca4e3b7be2e2ad4e11e8a3dd4b0ad61fe5108dc6ec4c5b9
                room-ref: ./poc-close-path-never-walked/review/validation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:xve5t292zy54mncx0xm6m3v0:validation:2
                briefing: briefing:xve5t292zy54mncx0xm6m3v0:validation:attempt-2:revision-1
                by: person:captain
                at: "2026-09-14T10:11:19.74465Z"
                decision: approve
                reason: 'Captain approved in chat 2026-09-14 on the FO gate presenting candidate 21a6ffeb: cycle 2 confirmed his ruled deletion of poc_non_goals_refused broke nothing, both fixes were re-falsified and re-passed independently of the build and of the FO, and no residual was carried forward. The gate question also authorized the Draft PR.'
              application:
                target-stage: done
                state: consumed
archived: 2026-09-14T10:37:42Z
---

Running a POC to close surfaced two defects on the same path, neither of which any
existing test reaches. Both were found by driving the path, not by reading it, on
the work item `capture-oracle-never-caught-anything` (archived, 2026-09-14).

**A correction round cannot be pinned after a POC prove stage.**
`poc-close-guard.py` reads `## POC outcome` and `## POC close measurement` as
top-level sections of the work item (`one_yaml_section(text, "POC outcome",
"poc_outcome")`), so the prove stage must write them there.
`profile-contract-loader.py`'s `work_item_authority` retains every `##` section
except one matching `^## Stage Report`, so both land inside the accepted-authority
hash. A `kc-dev-flow-feedback/v1` context compares the current authority against
the rejected pin's, so after any prove stage the two can never be equal and the
loader answers `FEEDBACK_CONTEXT_MISMATCH: rejected work item or authority
changed`. Reproduced on the real item. The Captain had ruled two prose findings
should be fixed; the First Officer had to route that pass as an ordinary build
attempt authorized by a section in the work item, because the designed mechanism
was structurally unavailable.

**`poc-close-guard.py` silently misreads an empty `started:`.** Line 63 is
`re.findall(r"^started:\s*([^\n#]+?)\s*$", frontmatter, re.MULTILINE)`. The `\s*`
after the colon matches the newline, so on an empty field the capture group begins
on the following line and returns that key. Reproduced standalone against the
frontmatter shape `spacedock new` emits: the match is `'completed:'`. The guard
then rejects a correct close with `admitted_at must equal frontmatter started`,
naming a comparison the reader cannot see is against the literal string
`completed:`. Nothing errors; the field is simply read as something else.

## Accepted outcome

A POC that reaches its prove stage can be corrected and closed without the First
Officer inventing a route, and `poc-close-guard.py` either reads an empty `started`
as absent or refuses it by name. Which of those two the guard should do, and
whether the POC route gets a correction path at all or the outcome sections move
out of the authority region, are the questions the shape stage answers — both
defects are reported here with their reproductions, not with their fixes.

## Non-goals

- Changing what `## POC outcome` or `## POC close measurement` must contain.
- Changing the `kc-dev-flow-feedback/v1` schema's fields.
- Reopening the archived `capture-oracle-never-caught-anything` item.
- Any change to `spacedock-dev/subspace-relay`.

## Acceptance criteria

- **AC-1** A fixture POC work item that has passed a prove stage accepts a
  `kc-dev-flow-feedback/v1` correction context, or the route it must take instead is
  stated in the POC profile contract where a First Officer will read it. Whichever
  shape is chosen, driving it on the fixture succeeds and the previous behaviour is
  shown to fail.
- **AC-2** `poc-close-guard.py` on a work item whose `started:` is empty either
  reports the field as absent or refuses with a message naming the empty field. It
  does not capture the following frontmatter key. A regression test covers the empty
  field, a populated field, and an absent field; mutating the fix reddens it.
- **AC-3** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 and the existing
  `poc-close-guard.test.py` still passes unchanged, or its change is named and
  justified in the stage report.
- **AC-4** Both defects are reproduced against their pre-fix behaviour at the
  candidate revision, so the tests are seen to fail before they are seen to pass.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: >
    Two coupled defects on one path, with a real design question the First Officer
    must not settle alone: whether the POC route gets a correction path, or the
    outcome sections move out of the authority region, or a POC's answer to findings
    is only its direction and the contract should say so. Pilot rather than POC
    because a shape stage is exactly what that question needs — and because the
    previous item on this path selected POC, ran past its budget, needed a Captain
    amendment mid-flight, and closed with direction `change` for those reasons.
    Selecting POC again would repeat a measured mistake.
  obligations:
    architecture: [No change to the feedback schema's fields or to what the POC outcome sections must contain; the fix lands in the contract or the loader's authority rule, not in an adopter]
    implementation: [scripts/poc-close-guard.py; the POC profile contract or scripts/profile-contract-loader.py depending on shape's ruling; a regression test for the started field]
    testing: [AC-1 to AC-4 at the candidate SHA; both defects reproduced pre-fix]
  scope_boundary: >
    No change to the kc-dev-flow-feedback/v1 schema fields, to the required contents
    of the POC outcome sections, to the archived capture-oracle item, or to
    spacedock-dev/subspace-relay.
  semantics_unchanged: false
```

## Stage Report: ideation

- DONE: read `docs/architecture.md` before exploration; bootstrap a useful missing map before implementation, following `project-context-maintenance.md`
  Repo-root `docs/architecture.md` is absent; the bound authority is root `ARCHITECTURE.md` (workflow README Local Profile, `Project context` row), read at its `## kc-dev-flow profile-native loading` section. The map gap is raised as a Captain decision below, not absorbed.
- DONE: one accepted journey and explicit non-goals
  `### Accepted journey` below; non-goals stand as admitted in `## Non-goals` and are unchanged.
- DONE: persistence, recovery, and data-safety boundaries
  `### Persistence, recovery, and data safety` below.
- DONE: task-specific acceptance checks able to falsify the slice
  `### Acceptance checks` below binds each admitted AC to one command and one mutation that reddens it.
- DONE: a file-level `where it touches` table
  `### Where it touches` below; every `lines now` counted with `wc -l` in the current tree at `7b103a10`.
- DONE: the stop numbers implementation halts on
  `### Stop numbers` below, measured as the diff against `7b103a10`.
- DONE: The one ruling this stage owes — pick exactly one and say what it costs
  `### Ruling` selects (b) and states its cost. (a) and (c) were rejected on evidence gathered this stage, recorded below.
- DONE: whether an empty `started` should read as absent or refuse by name
  Refuse by name. `### Defect 2` states why "read as absent" has no safe downstream behaviour.
- SKIPPED: full `kc-dev-flow-contract-test.py` run
  Shape owes no suite run, and the FO recorded a ten-hour hang under load; AC-3 binds it to build.

### Ruling

**(b) — `## POC outcome` and `## POC close measurement` leave the accepted-authority region, by exact heading, the same way `## Stage Report` already does.**

Two facts gathered this stage removed (a) and (c).

*(c) is not implementable.* It needs a worker to re-record `direction: change` after a
rejection, and no worker can be dispatched at `validation` again. `bind_stage_pin`'s
same-stage branch compares `work_item_authority_sha256` exactly, so once a prove worker
writes `## POC outcome` the stage refuses even report-only continuation with the same
attempt. (c) would leave the First Officer hand-editing the work item — the
route-inventing this task exists to end. Separately, the guard's existing intervention
check (`captain_interventions_before_decision_ready`) fires only on interventions
*before* decision-ready, so a gate rejection after the outcome is written is not covered
by it; (c) would be a new rule needing a new enforcement point, not the naming of an old
one.

*(a) collapses into (b) or removes the protection.* Any tolerance narrow enough to be
safe is an exception list for the same two headings, written inside
`read_feedback_context` instead of inside the projection — so it fixes feedback re-entry
and leaves same-stage re-entry broken. A blanket tolerance drops the comparison the
mechanism exists for.

**The seam.** `work_item_authority` excludes `^## Stage Report(?:: [^\n]+)?$` and retains
everything else. `poc-close-guard.py`'s `one_yaml_section` is the only consumer that
requires a validation-stage worker to write a non-report body section into the work item;
it is checked by `grep -n '`## ' kc-dev-flow/references/profiles/*/*.md
kc-dev-flow/references/pr-merge-extension.md kc-dev-flow/references/roborev-implementation-exit.md`,
whose only hits are PR-body headings. That single asymmetry, not the feedback schema, is
the defect.

**What it costs.**

- The answer to "what else does that let move under a worker" is: exactly two
  column-zero, exact-match headings outside a code fence, matched with the same
  discipline as `## Stage Report`. `The problem`, `Accepted outcome`, `Non-goals`,
  `Acceptance criteria`, `Route-back conditions`, and `## Work profile receipt` stay
  bound. A near-miss heading (`## POC outcomes`) stays bound, and that is the mutation
  that reddens the test.
- No dispatch boundary loses a detection it has today. First feedback entry still
  compares the full-document `rejected_work_item_sha256`; the gate resolution binds the
  briefing digest of what the Captain approved; `poc-close-guard.py` reads the live text
  at `review`, `consume`, and `check-final`.
- Migration: a POC pin at `validation` whose item already carries those sections gets a
  different authority digest. Those items are unresumable today by any mechanism, so the
  flip is the repair, not a break. A legacy pin without `work_item_authority_sha256`
  compares whole-document bytes and is not reached by this change — it stays stranded and
  keeps needing its separately recorded Captain-authorized migration.
- The published package changes `contract_digest`. In-flight items on other tasks resume
  their active stage on the installed 4.5.0 package and take the new digest at their next
  boundary — the designed upgrade path, and it only starts when the plugin is published
  and installed, not when this branch merges.
- Residual this ruling does not fix: the class. Any future contract that requires a
  worker to write a body section outside `## Stage Report` strands its item the same way.
  This slice fixes the two instances the contracts require today and names the trap in
  `MIGRATION.md`; it adds no general guard, because the guard's removal condition cannot
  be written.

### Defect 2

`[ \t]` replaces `\s` in the `started` pattern. Probed on the frontmatter shape
`spacedock new` emits: the present pattern returns `['completed:']` for an empty field
and the `[ \t]` form returns `[]`, matching the absent case, while a populated field is
unchanged.

That makes empty and absent indistinguishable, and neither sets `receipt["started"]`,
so `parse_outcome`'s `admitted_at != receipt["started"]` raises `KeyError` — an uncaught
traceback at exit 1, not the guard's named refusal at exit 2. "Read as absent" therefore
has no safe downstream behaviour: `admitted_at` is the POC's binding to its own admission
time and cannot be checked against nothing.

So: **refuse by name**, and the refusal belongs at the comparison in `parse_outcome`, not
in `read_work_item` — a no-artifact POC returns early before `started` is consumed and
must not be refused for a field it never reads.

`read_work_item`'s `^id:\s*` shares the pattern shape. It is dormant because `spacedock
new` always populates `id`, and the loader's own callers already use `[ \t]`. Fix both in
the same substitution rather than leaving one known-wrong instance in the same function.

### Accepted journey

Actor and carrier named per step; OBSERVED means someone drove it on the real components.

1. **OBSERVED** — a First Officer runs `profile-contract-loader.py --write-stage-pin` for
   a POC at `implementation`; the pin sidecar JSON records
   `work_item_authority_sha256`.
2. **OBSERVED** — the POC advances to `validation`; the prove worker writes
   `## POC outcome` and `## POC close measurement` into the work item, because
   `poc-close-guard.py`'s `one_yaml_section` reads them as top-level sections.
3. **OBSERVED** — `work_item_authority` over that text returns a digest different from the
   pin's. Probed directly against this repository's loader: appending
   `## Stage Report: …` leaves the digest identical; appending `## POC outcome` changes it.
4. **OBSERVED** — the Captain rejects at the close gate. The First Officer builds a
   `kc-dev-flow-feedback/v1` receipt and re-runs the loader with `--feedback-context`.
   `read_feedback_context` answers `FEEDBACK_CONTEXT_MISMATCH: rejected work item or
   authority changed`, naming an edit to the brief that never happened.
5. **OBSERVED** — on `capture-oracle-never-caught-anything` (archived 2026-09-14) the First
   Officer routed the Captain's two prose findings as an ordinary build attempt authorized
   by a section in the work item, because the designed mechanism was unavailable.
6. **DESIGNED** — with the two headings excluded, step 4's loader run emits the `build`
   contract with `workflow_stage: implementation` and `recorded_workflow_stage: validation`,
   and same-stage report-only continuation at `validation` also stops refusing.
7. **DESIGNED (unhappy path)** — a worker edits `## Accepted outcome` or `## Non-goals`
   during a correction round: `read_feedback_context` still refuses, because those sections
   remain inside the projection. This is the mutation AC-1 uses.
8. **DESIGNED (unhappy path)** — a POC work item reaches the close guard with an empty
   `started:`. The guard refuses at exit 2 with a message naming the empty field, instead
   of comparing `admitted_at` against the literal string `completed:`.

`semantics_unchanged: false` stands as recorded: the observable semantics this work
changes are the `work_item_authority` projection's exclusion set and the close guard's
refusal surface. No command grammar, stored format, or authority assignment moves.

### Persistence, recovery, and data safety

- The only persisted artifacts are the state-owned stage-pin sidecar JSON and the work
  item text. Neither is rewritten by this slice; the projection over the work item changes,
  so existing pins are re-interpreted, never edited. Do not repin an active record to clear
  a refusal.
- Recovery for an item stranded by this defect is: install the fixed package, re-run the
  ordinary pin command at the same attempt. No hand edit, no pin deletion.
- Data safety: the change only widens what is *excluded* from a hash. It cannot cause a
  changed brief to pass, because every section the brief occupies stays retained, and the
  first feedback entry still compares full-document bytes.
- The state checkout is shared and unbranched; build commits path-scoped.

### Acceptance checks

The admitted `## Acceptance criteria` stand unchanged. Each is bound here to one command
and the mutation that reddens it.

- **AC-1** — a fixture POC at `validation` carrying `## POC outcome`, driven through
  `profile-contract-loader.py --feedback-context`, in
  `kc-dev-flow/scripts/profile-contract-loader.test.py` beside the existing
  report/authority/correction regressions. Falsifier kind `mutation`: revert the exclusion
  and the fixture returns `FEEDBACK_CONTEXT_MISMATCH`; separately, edit `## Non-goals` in
  the same fixture and it must still refuse. Add the same-stage report-only re-entry case,
  which the ruling shows is broken today and which no admitted AC named.
- **AC-2** — `kc-dev-flow/scripts/poc-close-guard.test.py` covers empty, populated, and
  absent `started`. Falsifier kind `refusal`: drive the guard and read exit 2 with the
  named message. Mutating `[ \t]` back to `\s` must make the empty case report
  `completed:`; removing the named refusal must make empty and absent traceback.
- **AC-3** — `python3 scripts/kc-dev-flow-contract-test.py` exits 0, in its own bounded
  invocation, never chained with a mutate-and-revert. `poc-close-guard.test.py` passes
  unchanged except for the added cases.
- **AC-4** — each test above is run against the unfixed tree first and its failure text
  recorded in the build report, before the fix lands.

### Where it touches

`lines now` counted with `wc -l` in the current tree at `7b103a10`. `lines after` is this
item's estimate.

| path | lines now | lines after |
|---|---|---|
| `kc-dev-flow/scripts/profile-contract-loader.py` | 1119 | ~1124 |
| `kc-dev-flow/scripts/poc-close-guard.py` | 366 | ~370 |
| `kc-dev-flow/scripts/profile-contract-loader.test.py` | 2550 | ~2600 |
| `kc-dev-flow/scripts/poc-close-guard.test.py` | 586 | ~612 |
| `kc-dev-flow/MIGRATION.md` | 506 | ~511 |
| `ARCHITECTURE.md` | 270 | ~271 |

Reconciled against the journey in both directions. `MIGRATION.md` carries the projection's
exclusion list as a factual claim and goes false without an edit (journey step 6).
`ARCHITECTURE.md` line 39 states "ordinary report updates do not change that authority",
the bound project-context claim this slice changes. Two files the journey touches and the
table deliberately omits: `kc-dev-flow/references/profiles/poc-exploration/prove.md` (55
lines) and `kc-dev-flow/skills/continue-dev-flow/SKILL.md` (259 lines) — under (b) the
correction path becomes uniform across profiles and `continue-dev-flow`'s existing
profile-agnostic sentence routing feedback to `MIGRATION.md#stage-pin-continuation`
already covers POC. Nothing breaks without an edit there, so neither is edited.

### Stop numbers

Measured as the diff against `7b103a10`, not against the table.

- changed files: **8**
- changed lines: **160**
- named runaway area: **`kc-dev-flow/scripts/profile-contract-loader.test.py`** — the
  correction-regression fixtures are the largest block in that suite, and the POC variant
  needs a `poc-exploration` fixture at `validation` that does not exist there yet. Stop at
  **90 added lines** in that file alone.

Crossing one stops work and reports the observed count; it passes and fails nothing.

### Reverse-recovery receipt

```yaml
reverse_recovery:
  trigger: "claim that a correction path after a POC prove stage is missing"
  boundary: "POC close journey from prove-stage write to correction re-entry; searched kc-dev-flow/scripts, kc-dev-flow/references, kc-dev-flow/skills, kc-dev-flow/MIGRATION.md"
  layers:
    - surface: "validation-to-implementation correction mechanism"
      location: "kc-dev-flow/scripts/profile-contract-loader.py read_feedback_context"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "present and exercised for Pilot/Production in profile-contract-loader.test.py; fails for POC only because the authority digest moved"
      disproof_hook: "drive the loader with --feedback-context on a POC fixture at validation carrying ## POC outcome"
    - surface: "same-stage re-entry at validation"
      location: "kc-dev-flow/scripts/profile-contract-loader.py bind_stage_pin same-stage branch"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "compares work_item_authority_sha256 exactly, so report-only continuation at the same attempt refuses once ## POC outcome exists"
      disproof_hook: "re-run the ordinary pin command at the same attempt after appending ## POC outcome"
    - surface: "accepted-authority projection"
      location: "kc-dev-flow/scripts/profile-contract-loader.py work_item_authority"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "excludes ## Stage Report and retains ## POC outcome; probed against this repository's loader, the Stage Report append leaves the digest identical and the POC outcome append changes it"
      disproof_hook: "call work_item_authority on the same text with each section appended and compare digests"
    - surface: "frontmatter started reader"
      location: "kc-dev-flow/scripts/poc-close-guard.py:63"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "\\s* spans the newline; an empty field captures the following key, and the [ \\t] form leaves receipt['started'] unset, which KeyErrors at the admitted_at comparison"
      disproof_hook: "re.findall the present and repaired patterns against frontmatter whose started is empty, populated, and absent"
    - surface: "rule that a POC answers findings only through its direction"
      location: MISSING
      need: NO_OBSERVED_CONSUMER
      completeness: MISSING
      evidence: "grep for 'feedback' across kc-dev-flow/skills, references and agents returns only the profile-agnostic MIGRATION pointer; the guard's intervention check covers interventions before decision-ready, not a gate rejection after it"
      disproof_hook: "grep -rn 'intervention\\|direction' kc-dev-flow/references/profiles/poc-exploration"
  decision: recover
```

### Project context receipt

```yaml
project_context:
  classification: update
  bound_authority: "root ARCHITECTURE.md, per the workflow README Local Profile Project context row"
  stale_claim: "'ordinary report updates do not change that authority' in ## kc-dev-flow profile-native loading — true for report bytes, and it is the sentence a reader uses to conclude a prove-stage outcome is safe"
  replacement: "name the POC prove stage's recorded outcome sections alongside report updates as bytes that do not change accepted authority"
```

Retained-document note: this slice adds and removes no retained document, so the shape
obligation is the classification above; `MIGRATION.md` and `ARCHITECTURE.md` are repaired
in place under Rule 8, and build owes Rules 1-3 and 6-8 on both.

### Captain decision

One decision is open and belongs to the Captain, not to build.

Repo-root `docs/architecture.md` does not exist. `project-context-maintenance.md` requires
it for every Pilot and Production route and states that root `ARCHITECTURE.md` does not
waive it, while this workflow's Local Profile binds project context to root
`ARCHITECTURE.md`, `PRODUCT.md`, and `CLAUDE.md`. Bootstrapping the map is a new
repository-wide artifact, larger than the two defects, and outside this item's recorded
`scope_boundary`.

Recommendation: keep it out of this slice and admit it as its own item. Build proceeds
against root `ARCHITECTURE.md` as the bound authority. The cost of deferring is that every
Pilot and Production item in this repository keeps carrying the same unmet obligation.

### Summary

Ruled (b): the two POC outcome headings leave the accepted-authority projection, matched
by exact heading the way `## Stage Report` already is. (c) was rejected because
`bind_stage_pin`'s same-stage branch makes `validation` non-re-enterable once the prove
worker writes, so no worker could record the `change` direction (c) depends on; (a) was
rejected because a safe tolerance is the same exclusion list written in a place that fixes
only one of the two broken re-entries. Defect 2 refuses by name at the comparison, because
the `[ \t]` repair alone converts a wrong answer into an uncaught `KeyError`. This report
is written inside the Stage Report rather than as body sections: the same projection was
probed against this item and a new top-level section changes its boundary digest, which
would have stranded this item's own advance to implementation.

## Stage Report: implementation

- DONE: AC-1 — correction context or stated route, driven on a fixture, previous behaviour shown to fail
  `work_item_authority` (`kc-dev-flow/scripts/profile-contract-loader.py`) now excludes exact-match `## POC outcome`
  and `## POC close measurement` the same way `## Stage Report` is excluded. Pre-fix red, isolated to
  `read_feedback_context`: raises `FEEDBACK_CONTEXT_MISMATCH: rejected work item or authority changed` against a
  POC fixture at validation carrying `## POC outcome`; post-fix the same call accepts it. `bind_stage_pin`'s
  same-stage branch was pre-fix red with `ACTIVE_STAGE_PIN_MISMATCH` on the same fixture, post-fix pinned
  unchanged. Regression tests in `profile-contract-loader.test.py` (poc_same_stage, poc_corrected,
  near_miss_drift, poc_non_goals_refused) cover: same-stage report-only re-entry, the feedback correction path,
  a near-miss `## POC outcomes` heading staying bound (redder when the exclusion regex is widened to `POC
  outcome\w*` — confirmed), and an added `## Non-goals` still refusing.
- DONE: AC-2 — empty `started` reads as absent or refuses by name; regression covers empty/populated/absent; mutation reddens
  `poc-close-guard.py`'s `started`/`id` frontmatter readers changed `\s*` to `[ \t]*` after the colon (matching
  every other reader in this codebase); `parse_outcome` now refuses `"frontmatter started must not be empty"`
  when `started` is absent from the receipt, at the point that consumes it — a no-artifact POC returns before
  that point and is unaffected. Pre-fix red: empty case raised the wrong `admitted_at must equal frontmatter
  started` refusal (comparing against the literal string `completed:`); absent case raised an uncaught
  `KeyError: 'started'`. Both now raise the named refusal; populated case unchanged (`direct` fixture).
- DONE: AC-3 — full contract suite exits 0; guard test passes with its addition named
  `python3 scripts/kc-dev-flow-contract-test.py` exit 0, own bounded invocation (timeout 300s, ~70s actual).
  `poc-close-guard.test.py` passes with 2 added lines-of-assertion (empty/absent `started`); no existing
  assertion changed.
- DONE: AC-4 — each test run against the unfixed tree first, failure recorded before the fix landed
  Evidence above per defect; reproduced again standalone via direct module calls against
  `git show e3cca913:kc-dev-flow/scripts/profile-contract-loader.py` for `read_feedback_context`.
- DONE: runnable integrated slice
  Commits `4dc230ac` (fix + AC-1/AC-2 core tests) and `6d340208` (added Non-goals coverage) on
  `spacedock-ensign/poc-close-path-never-walked`, cut from `e3cca913`.
- DONE: focused tests for owned logic and seam behavior
  Same commits; no new production dependency, no new abstraction.
- SKIPPED: diagnostics and bounded retry/recovery
  No new runtime surface introduced; the fix narrows an existing hash exclusion and a regex, neither owns
  retry/recovery behavior.
- DONE: implementation-exit surface-map-check, every non-test changed file
  `python3 kc-dev-flow/scripts/surface-map-check.py e3cca913 HEAD <evidence> --work-item <this file> --brief
  <this file> --repo .` → `surface-map-check: OK (4 files checked)`, 2 test files excluded by the fixed
  pattern. Evidence block below.
- DONE: implementation-exit observation (RoboRev, Pilot: one request, no confirmation needed)
  Capability probes green: CLI `v0.62.0` with `review`/`list --json`/`show --json`; daemon up 464h, `list
  --json` resolved this repo; `codex` authenticated (`check-agents`). One request issued
  (`roborev review e3cca913 4dc230ac --agent codex --model gpt-5.6-terra --reasoning medium --min-severity
  medium --panel none --wait`); daemon's range semantics treated the start arg as exclusive, so the actual
  diff reviewed was `da3f287f..4dc230ac` (includes the prior merged commit `e3cca913`, not just this slice) —
  job 502, verdict `P`, output `SEVERITY_THRESHOLD_MET` (no medium+ finding) → `PASS(reason: passed)`.
  request_count=1, confirmation_count=0. Residual: the later test-only commit `6d340208` was not
  re-observed (no repair, no production-code change, request budget already spent).
- DONE: stop numbers, measured against `e3cca913`
  6 files changed (cap 8), 90 insertions + 9 deletions = 99 changed lines (cap 160),
  `profile-contract-loader.test.py` 76 added lines (cap 90). No threshold crossed.
- DONE: retained-document-policy Rules 1-3 and 6-8 on MIGRATION.md and ARCHITECTURE.md
  Both repaired in place (Rule 8), present-tense factual claims only (Rule 1), the added MIGRATION.md
  sentence ties to the exclusion-list rule rather than standing as a free log (Rule 2), no new heading or
  provenance language added (Rule 6), no diagram touched (Rule 7); Rule 3's checks are the same grep/read
  path the surrounding untouched prose in both files already relies on, unchanged by this edit. Rule 4/5 not
  triggered — repair, not addition or deletion of a retained document. No duplicate of the edited claim found
  elsewhere (`grep` across non-archived `.md`).
- DONE: comment pass
  0 comment lines added, 0 cut — confirmed by diffing added `+` lines against the code changes; the only `#`
  characters added are inside regex character classes (`[^\n#]`), not comments.

### Evidence

```
SURFACE: kc-dev-flow/scripts/profile-contract-loader.py -> AC-1 | python3 kc-dev-flow/scripts/profile-contract-loader.test.py | git checkout e3cca913 -- kc-dev-flow/scripts/profile-contract-loader.py
SURFACE: kc-dev-flow/scripts/poc-close-guard.py -> AC-2 | python3 kc-dev-flow/scripts/poc-close-guard.test.py | git checkout e3cca913 -- kc-dev-flow/scripts/poc-close-guard.py
SURFACE: kc-dev-flow/MIGRATION.md -> AC-1 | python3 kc-dev-flow/scripts/profile-contract-loader.test.py | git checkout e3cca913 -- kc-dev-flow/MIGRATION.md
SURFACE: ARCHITECTURE.md -> AC-1 | python3 kc-dev-flow/scripts/profile-contract-loader.test.py | git checkout e3cca913 -- ARCHITECTURE.md
```

### Summary

Fixed both defects as ruled in ideation: `work_item_authority` now excludes `## POC outcome` and
`## POC close measurement` by exact heading, restoring same-stage re-entry and the
`kc-dev-flow-feedback/v1` correction path after a POC prove stage; `poc-close-guard.py` refuses an empty or
absent `started` by name instead of comparing against a captured `completed:` or crashing with `KeyError`.
All four ACs reproduced red before green. Surface-map-check and the full contract suite pass at `6d340208`.
RoboRev's one authorized Pilot request came back `PASS` with no findings against a slightly wider range than
requested (daemon's inclusive-range semantics); no confirmation was needed or spent. Repaired MIGRATION.md
and ARCHITECTURE.md in place under the retained-document policy; no other file in the "Where it touches"
table needed an edit.

### Cycle 2 — `poc_non_goals_refused` deleted on the Captain's ruling

- DONE: delete `poc_non_goals_refused`, one pass, nothing else
  Removed the 12-line case (commit `21a6ffeb`) — the fixture setup, the `## Non-goals` append, the
  refusal assertion, and the restore. `poc_corrected` now runs directly against the item as left by
  `poc_same_stage`. Independently verified the validation finding before deleting: swapping the
  appended heading for `## Stage Report: extra` (an explicitly excluded heading) still leaves the
  suite green at HEAD — a first, non-resuming feedback entry compares full document bytes
  (`receipt["sha256"] != feedback["rejected_work_item_sha256"]`) before the authority projection, so
  any appended byte refuses there regardless of what the heading is. `near_miss_drift` was not
  touched.
- DONE: `profile-contract-loader.test.py` exits 0 with the case gone
  Own bounded run, tail: `profile contract loader test: PASS`.
- DONE: `kc-dev-flow-contract-test.py` exits 0
  Own bounded invocation (300s cap), `EXIT:0`, `kc-dev-flow contract: PASS`.
- DONE: `near_miss_drift` still present and passing
  Present at its original lines; suite PASS above includes it.
- DONE: reverting the exclusion reddens the surviving coverage — checked against both loader forms
  Reverting `profile-contract-loader.py` whole-file to `e3cca913` reddens the suite, but at
  `poc_same_stage` (the earlier assertion), before the script reaches `near_miss_drift` — a full
  revert removes the same-stage re-entry fix first, masking any later assertion. A direct
  `work_item_authority` probe on the reverted module shows why: pre-fix, nothing POC-related is
  excluded, so the near-miss heading changes the digest too and `near_miss_drift`'s own
  `returncode == 2` assertion would still hold — a bare revert does not exercise what makes
  `near_miss_drift` discriminating. Its real falsifier, re-confirmed here: widen the exclusion match
  to `POC outcome\w*` (so the near-miss heading is wrongly excluded) — the suite reddens exactly at
  `near_miss_drift`: `a near-miss '## POC outcomes' heading was excluded from accepted authority`.
  Restored; tree clean both times.
- DONE: stop numbers re-measured against the merge-base
  Base `e3cca913` (`git merge-base HEAD origin/main`, unchanged from build). 6 files changed, 90
  insertions + 9 deletions = 99 changed lines (cap 160), `profile-contract-loader.test.py` 64 added
  lines (cap 90) — identical to the original build measurement, since this cycle's net change to
  that file is zero (12 lines added then removed).

### Summary (cycle 2)

Deleted `poc_non_goals_refused` per the Captain's ruling after independently reproducing why it
cannot fail for the reason its name gives. `near_miss_drift` is untouched and remains the
discriminating proof for the exclusion set, re-confirmed here against its actual falsifier
(over-broad matching), not against a whole-file revert that reddens a different, earlier check
first. Both suites pass at `21a6ffeb`; stop numbers unchanged from the original build measurement.

## Stage Report: validation

- DONE: exact-revision journey evidence
  Candidate `6d340208`, worktree clean, branch `spacedock-ensign/poc-close-path-never-walked`.
  `origin/main` is exactly `e3cca913`, so the candidate already sits on trunk and the ceremony's
  rebase is a no-op; no commit has touched `kc-dev-flow/scripts/`, `kc-dev-flow/MIGRATION.md`, or
  `ARCHITECTURE.md` on trunk since the cut. Journey steps 6 and 8 driven below.
- DONE: AC-1 — POC correction context accepted, previous behaviour shown to fail
  `profile-contract-loader.test.py` PASS at HEAD; reverting only `profile-contract-loader.py` to
  `e3cca913` reddens it with `same-stage re-entry refused once the prove worker wrote POC outcome:
  ... ACTIVE_STAGE_PIN_MISMATCH`. Instrument seen to fail, then restored (tree clean).
- DONE: AC-2 — empty `started` refuses by name; the refusal sits at the comparison
  `poc-close-guard.test.py` PASS at HEAD; reverting only `poc-close-guard.py` to `e3cca913` reddens
  it with `wrong refusal for 'frontmatter started must not be empty': admitted_at must equal
  frontmatter started`. Falsifier kind `refusal`, driven and read. Restored (tree clean).
- DONE: AC-3 — full contract suite exits 0
  `python3 scripts/kc-dev-flow-contract-test.py` → `kc-dev-flow contract: PASS`, `EXIT=0`, own
  bounded invocation (900s cap, background+poll, load average 10-19, never chained with a mutate).
- DONE: AC-4 — both defects reproduced against pre-fix behaviour at the candidate revision
  The two reverts above are that reproduction, re-run by this stage rather than taken from the build
  report.
- DONE: first officer item 2 — the `started` refusal sits at the `admitted_at` comparison, and a
  no-artifact POC still closes
  Driven, not read: `parse_outcome` called with a receipt carrying neither `poc_artifact` nor
  `started`, against a work item whose frontmatter `started:` is empty, returns `stop`. The refusal
  is reached only after the `poc_artifact` early return.
- DONE: first officer item 3 — the `MIGRATION.md` and `ARCHITECTURE.md` edits are true of the
  shipped bytes
  Twelve direct `work_item_authority` probes at HEAD, each claim to one probe: `## Stage Report:`,
  `## POC outcome` and `## POC close measurement` excluded; `## POC outcomes`, `## POC outcome
  extra`, a three-space-indented copy, a `###` copy and `## Non-goals` all stay bound; the exclusion
  spans its body and stops at the next level-one and level-two heading; a fenced copy starts no
  exclusion. All twelve pass. `ARCHITECTURE.md`'s clause is probes 2 and 3.
- DONE: first officer item 1 — whether the RoboRev range leaves a shipped line unreviewed
  `roborev show 502 --json` gives `git_ref` `da3f287f..4dc230ac` and a prompt reading `Reviewing 2
  commits: e3cca91, 4dc230a`. The reviewed set is a superset of this slice: every non-test line lives
  in `4dc230ac`. Unobserved: the 12 added lines of `6d340208`, all in
  `profile-contract-loader.test.py`. Zero production lines unreviewed. The build report's
  "exclusive"/"inclusive" wording contradicts itself; the `git_ref` above is the fact.
- DONE: retry/recovery, duplicate, diagnostic, and data-safety results that apply
  Recovery: the documented repair for a stranded item ("re-run the ordinary pin command at the same
  attempt") is `poc_same_stage`, green. Data safety: first feedback entry compares full document
  bytes — `receipt["sha256"]` is `sha256(raw)` over the whole file at `resolve_work_item`, and the
  authority projection is a second, separate comparison; the probes above show every brief-bearing
  section stays retained. No new runtime surface, so no retry, duplicate, or diagnostic result
  applies.
- DONE: base decision under `delivery-branch-base.md`
  Trunk. `#321` is the only open artifact sharing a file (`profile-contract-loader.py`,
  `profile-contract-loader.test.py`, `MIGRATION.md`) and shares no lineage: its loader hunk is
  `validate_admission_brief` (~L159) against this slice's `work_item_authority` (~L590), its test
  hunk ~L230 against ~L1820. The Local Profile's base policy is dependency-aware and
  `delivery-base-trunk-test-conflates-file-and-lineage` records the same ruling with precedent.
- DONE: remaining production obligations and promotion triggers
  No promotion trigger: consumers absorb this by taking the new version, none must migrate. Release
  obligation met — the `MIGRATION.md` entry exists and release-please owns the version. Verified,
  not assumed: `contract_digest` changes `a7fdd4d3…` → `45f43089…` (all three edited package files
  are declared manifest resources), and no expected digest is pinned anywhere in the tree.
- SKIPPED: the named `equivalence_instrument` observed to fail
  The work profile receipt declares `semantics_unchanged: false`, so no equivalence instrument is
  owed.
- SKIPPED: provider feedback disposition when a delivery artifact exists
  No PR exists (`pr:` empty). RoboRev is observation, not provider feedback or delivery authority,
  per the workflow README.

### Finding: `poc_non_goals_refused` cannot fail for the reason it names

Not blocking, and it is a test-only finding; the shipped behaviour it describes is correct.

`poc_non_goals_refused` (the whole of `6d340208`) appends `## Non-goals` after
`rejected_work_item_sha256` was taken, then asserts exit 2. On a first, non-resuming feedback entry
the loader compares full document bytes before it compares the authority projection, so *any* append
refuses there. Driven: replacing the appended `## Non-goals` with `## Stage Report: extra` — an
explicitly excluded heading — leaves the suite green. The test therefore proves nothing about the
exclusion set. Restored; tree clean.

The property it was meant to hold is already proven twice over, discriminatingly: by `near_miss_drift`
(a bound heading appended, same-stage re-pin, exit 2) and by this stage's direct probe. Repair
options, for the Captain: move the append onto the same-stage re-pin path where the authority
comparison is the only discriminator, or delete the case as a removal candidate. Not repaired here —
a test file is code, and a code repair returns to implementation for one final re-verification.

### Feedback Cycles

- Cycle 1: REJECTED by the Captain's ruling rather than by the reviewer. Validation
  at `6d340208` raised `poc_non_goals_refused` as one non-blocking finding and the FO
  presented it as a residual to record. The Captain asked why a test that cannot fail
  is not simply deleted. **He is right and the FO's recommendation was both looser and
  more expensive than his rule**: recording it costs a later item — backlog, gate,
  build, verify, delivery — where deleting it now costs one build pass and one verify
  on an item already at the gate. The validation gate was withdrawn because its
  question offered the wrong disposition. Routed to `implementation`: delete the case.
  The property it was meant to hold stays proven by `near_miss_drift` and by
  validation's own direct probe, both of which discriminate where this case does not.

### Residuals

- `started:` followed by a space or tab captures that whitespace and takes the old `admitted_at must
  equal frontmatter started` refusal rather than the named one. No observed producer: across the 90
  state entities present on 2026-09-14, 67 carry a bare `started:`, 12 carry a timestamp, and none
  carry a whitespace-only value (`grep -lE '^started:[ \t]+$' *.md` returns nothing). A narrower
  capture group would close it.
- An absent `started` is refused with `frontmatter started must not be empty`. Ideation ruled empty
  and absent indistinguishable on purpose; recorded as known, not a defect.
- `poc_corrected` asserts `workflow_stage` only. `recorded_workflow_stage` is set at the
  `feedback_context is not None` branch independently of profile and is already asserted by the Pilot
  correction case, so journey step 6 holds by construction.

### Summary

Both fixes hold at `6d340208` and both instruments were seen to fail in this stage, not quoted from
the build. Every claim the slice writes into `MIGRATION.md` and `ARCHITECTURE.md` was exercised
against the shipped loader rather than read. Nothing blocks the gate: the one finding is a test that
cannot fail for the reason its name gives, covering a property two other checks already prove, and it
is exactly the 12 lines RoboRev never observed. No PR was created — local verification is complete,
the base is trunk, and the delivery ceremony is the first officer's with the Captain's approval.

## Stage Report: validation (cycle 2)

- DONE: confirm the diff since cycle 1's approved candidate is exactly the deletion the Captain ruled
  `git diff 6d340208 21a6ffeb --stat` → `profile-contract-loader.test.py | 12 -------`, 1 file
  changed, 12 deletions, nothing else. Matches the FO's description; re-verified rather than taken on
  trust.
- DONE: confirm the deletion removed nothing load-bearing
  Read the surrounding test body: `poc_corrected` now runs directly against `poc_correction_item` as
  left by `poc_same_stage` (which already wrote `## POC outcome` and is asserted to persist). No
  fixture state the removed block produced was consumed downstream; `near_miss_drift` is a separate
  item untouched by the deletion.
- DONE: AC-1 still holds at `21a6ffeb`
  `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → PASS. Falsifier re-driven:
  `git checkout e3cca913 -- kc-dev-flow/scripts/profile-contract-loader.py` then re-run → reddens with
  `same-stage re-entry refused once the prove worker wrote POC outcome: ... ACTIVE_STAGE_PIN_MISMATCH`.
  Restored via `git checkout HEAD --`; tree clean.
- DONE: AC-2 still holds at `21a6ffeb`
  `python3 kc-dev-flow/scripts/poc-close-guard.test.py` → PASS. Falsifier re-driven:
  `git checkout e3cca913 -- kc-dev-flow/scripts/poc-close-guard.py` then re-run → reddens with
  `wrong refusal for 'frontmatter started must not be empty': admitted_at must equal frontmatter
  started`. Restored; tree clean.
- DONE: independently re-drive the real falsifier for the deleted finding, rather than accept the
  FO's quoted result
  Widened the exclusion regex in `profile-contract-loader.py` (`POC outcome` →
  `POC outcome\w*|POC close measurement`), re-ran the loader test: exit 1,
  `a near-miss '## POC outcomes' heading was excluded from accepted authority` — same message and
  same discriminating check (`near_miss_drift`) the FO reported. Confirms the property the deleted
  case claimed to hold is still proven by a check that can actually fail for that reason. Restored;
  `git status --short` empty both before and after.
- DONE: `python3 scripts/kc-dev-flow-contract-test.py` exits 0
  Own bounded invocation (900s cap, background+poll, not chained with a mutate). Tail:
  `kc-dev-flow contract: PASS`, `EXIT:0`.
- SKIPPED: re-litigating cycle 1's other findings (base decision, migration/architecture claims,
  RoboRev disposition, promotion triggers, residuals)
  Per the FO's scoping note: the only change since the cycle-1-approved candidate is the 12-line
  test deletion, confirmed above. None of those findings reference the deleted lines or any file this
  cycle touched; `git diff 6d340208 21a6ffeb` is the evidence they are unaffected. Re-confirmed one
  live fact anyway since it costs nothing to check: `gh pr view 321` is still `OPEN`, so the trunk base
  decision's "no shared lineage" reasoning is unchanged.

### Summary

Cycle 2 fixes nothing new; it confirms the Captain-ruled deletion of `poc_non_goals_refused` cost
exactly what cycle 1's build reported and broke nothing. Both defect fixes (AC-1, AC-2) were
re-falsified and re-passed at `21a6ffeb`, independent of the build's and the FO's own re-runs. The
full contract suite passes. Candidate `21a6ffeb`, worktree clean, no PR. Nothing blocks the gate.
