---
title: "kc-dev-flow: unify the necessity vocabulary across kernel and reverse-recovery, and bind the equivalence instrument"
status: implementation
source: https://linear.app/duckbase-co/issue/DEV-46/kc-dev-flow-unify-the-necessity-vocabulary-across-kernel-and-reverse
product: kc-dev-flow
planning-window: Linear Cycle d1c96803-02fa-4323-b3a8-2fc44cc43699 2026-09-10T16:00:00.000Z/2026-09-24T16:00:00.000Z
planning-outcome: Linear Project 4746021d-2930-4589-80a0-b7b3d1d70eeb kc-dev-flow slimming dogfood sha256:0599c390742642a1edf03e07a50c28635ff41d3ef77188e076cb2f02e6d85372
sprint: S8
sprint-readiness: ready
started: 2026-09-02T08:19:42Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: 50c1y5wf7dzh0ww2a9qajn47
gates:
    version: 1
    records:
        - id: gate:50c1y5wf7dzh0ww2a9qajn47:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:50c1y5wf7dzh0ww2a9qajn47-backlog-1
              briefing:
                id: briefing:50c1y5wf7dzh0ww2a9qajn47:backlog:attempt-1:revision-1
                digest: sha256:f1859f26f2cbee8a9efef1ba17b3efef81d24bebb5aa447e01e20a0cbf0a55fd
                room-ref: ./dev-46-unify-necessity-vocabulary/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:50c1y5wf7dzh0ww2a9qajn47:backlog:1
                briefing: briefing:50c1y5wf7dzh0ww2a9qajn47:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-02T08:17:26.673155Z"
                decision: approve
                reason: 'Captain approved DEV-46 into Production ideation: Project kc-dev-flow slimming dogfood, Cycle 2, sprint S8; shape must name the AC-4 enforcement point.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:50c1y5wf7dzh0ww2a9qajn47:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:50c1y5wf7dzh0ww2a9qajn47-ideation-1
              briefing:
                id: briefing:50c1y5wf7dzh0ww2a9qajn47:ideation:attempt-1:revision-1
                digest: sha256:7fe68121b9d8a7ec8a278ee920de82c8d8d8a4cc9ea42db0c289424ded98196b
                room-ref: ./dev-46-unify-necessity-vocabulary/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:50c1y5wf7dzh0ww2a9qajn47:ideation:1
                briefing: briefing:50c1y5wf7dzh0ww2a9qajn47:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-02T08:44:54.909102Z"
                decision: approve
                reason: 'Captain approved the DEV-46 shape: AC-4 bound as a loader-required field (declaration at ideation, evidence scalars at validation), 13 files / ~340 lines single slice against f9683a33, stops 16/500/180, reverse-recovery decision redesign.'
              application:
                target-stage: implementation
                state: consumed
---

## The problem

Two contracts grade the same question — does a surface earn its place — in two
disjoint vocabularies, and no sentence says how the two readings compose.

`reverse-recovery-audit.md` classifies need as `REQUIRED`,
`NO_OBSERVED_CONSUMER`, or `UNKNOWN`, established by search and justified by a
named consumer or contract. `kernel.md`'s minimal-necessity condition maps a
surface to the accepted goal, a named falsifier, a safety boundary, or a
required lifecycle obligation, established by execution. A safety-boundary
surface is therefore `NO_OBSERVED_CONSUMER` under the audit and mapped under the
kernel at the same time, and nothing states which reading wins.

Two further consequences of the same split: the audit's `disproof_hook` and the
kernel's without-it observation are the same evidence primitive under two names
at two cost tiers, and the kernel's implementation-exit comparison enumerates
only added files, dependencies, abstractions, tests, and comments — no clause
grades a removal, although a removal is a change whose necessity claim is
identical in form.

Separately, a change may declare at shape that it changes no observable
semantics. Goal sufficiency binds that declaration to the accepted goal only
through the Development Brief's `AC-N`, and no contract requires that a
declared-unchanged change carry an equivalence instrument, nor that the
instrument have been seen to fail. A behaviour-preserving refactor can pass with
no instrument capable of detecting a behaviour change.

This revisits a decision that already had evidence. The completed item
`subtractive-first-bounded-irreducibility` (PR #199, verdict passed) decided to
place the subtractive predicate in the kernel and leave the reverse-recovery mod
unchanged, on the stated basis that it "already owns the three need outcomes and
the removal authority boundary." The removal-authority half of that decision
stands and is a non-goal below. The new evidence is only that the two
vocabularies were never shown to compose, and the three consequences above are
what that costs.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  recommended: production
  basis: Both contracts are vendored by external adopters (subspace-relay, carlove-v1); renaming the reverse_recovery need axis is consumer-visible and may need a migration, and no evidence yet shows adopters absorb it by taking the new version.
  route: [shape, build, verify]
  obligations:
    architecture: [One necessity predicate named once with two instrument tiers and one removal authority, removal graded by the same predicate as retention, an equivalence-instrument requirement bound at a named enforcement point]
    implementation: [Edit kernel.md and reverse-recovery-audit.md canonical copies and keep the loader-served copies identical, rewrite contract-test and ablation assertions per renamed boundary without losing a regression they caught, record any adopter migration with the version that carries it]
    testing: [Contract test and minimal-stack ablation reject each renamed boundary for its named reason, a safety-boundary surface with no observed consumer classifies identically under both contracts, a declared-unchanged change without an instrument is refused at the named enforcement point and the refusal is observed]
  scope_boundary: No merge of the two contracts, no change to the removal authority boundary, no aggregate minimality gate, no new receipt or harness, no routing or gate-authority change, no fourth profile.
  decision:
    authority: person:captain
    at: 2026-09-02T07:48:50Z
```

## Accepted outcome

One necessity predicate, named once, with two instruments at two cost tiers and
one removal authority. A reader of either contract reaches the same
classification for the same surface. A removal is graded by the same predicate
as a retention. A change that declares its observable semantics unchanged names
the equivalence instrument that would have caught a change, and that instrument
has been seen to fail before it is trusted.

## Non-goals

- Do not merge `reverse-recovery-audit.md` into `kernel.md`, or fold either into
- Do not change the removal authority boundary. A search result stays a removal
- Do not make aggregate minimality a gate. LOC and file counts stay diagnostic
- Do not add a new receipt, registry, script, CI job, reviewer loop, or generic
- Do not change profile routing, stage order, gate authority, or the
- Do not add a fourth work profile for refactor-shaped work.

## Acceptance criteria

- **AC-1** The need axis of `reverse-recovery-audit.md` and the mapping targets
  of the kernel's minimal-necessity condition use one vocabulary, and a
  safety-boundary surface with no observed consumer classifies identically under
  both contracts.
- **AC-2** The audit's `disproof_hook` and the kernel's without-it observation
  are one named primitive with two declared tiers, and each contract states
  which tier it uses and what that tier can and cannot conclude.
- **AC-3** The kernel's implementation-exit comparison grades removed surfaces
  by the same predicate as retained surfaces, and a removal with no necessity
  claim is rejected for that named reason.
- **AC-4** A change that declares its observable semantics unchanged is refused
  at its verification boundary until it names an equivalence instrument and
  supplies evidence that the instrument was observed to fail against a case it
  must flag.
- **AC-5** `scripts/kc-dev-flow-contract-test.py` and the minimal-stack ablation
  test reject each renamed boundary for its named reason; no assertion that
  previously caught a semantic regression is lost in the rename.
- **AC-6** Canonical `kc-dev-flow/references/` and self-adopted
  `docs/dev/_mods/` copies of both contracts stay byte-identical, or the
  installed-plugin resolution has already removed the vendored pair.
- **AC-7** Every adopter-visible rename is reachable by taking the new plugin
  version, or the item records the exact migration an adopter must run and the
  version that carries it.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning
delta that names the changed premise, affected acceptance evidence, and
recommended change or stop.

Also route back when: a single unified vocabulary cannot express both a
search-tier and an execution-tier conclusion without weakening the removal
authority boundary; an adopter is found to parse the current `need` enum in a
way no plugin version can migrate; or the equivalence requirement cannot be
bound at a verification boundary without adding a new receipt or harness.

## Measurement

Not yet measured. Shape records the `where it touches` table and stop numbers against the delivery base; build records the diff counts as diagnostics.

## Shape

### Delivery base

`origin/main` = `f9683a33`. Recorded because the working checkout `133e869d` is
behind `main` and still carries a `docs/dev/_mods/` tree that `main` deleted, so
any `lines now` counted in this checkout for a vendored file is a phantom. All
counts below are `git show f9683a33:<path> | wc -l`.

### AC-6 is already satisfied at the delivery base

`git ls-tree -r --name-only f9683a33 -- docs/dev/_mods/` returns exactly one
path, `docs/dev/_mods/pr-merge.md`. The vendored contract pair is gone; the
loader resolves from `PACKAGE_ROOT / "references"` against
`kc-dev-flow/contract-manifest.json`. AC-6's second branch — "the
installed-plugin resolution has already removed the vendored pair" — holds, and
its enforcement point is the `obsolete_adopter_copies` set in
`scripts/kc-dev-flow-contract-test.py`, which refuses the pair's return. This
item adds nothing for AC-6.

### Journey

Accepted journey. Each step names the acting program. `OBSERVED` here means the
step was exercised in a clean `f9683a33` worktree this session by two runs, both
exit 0:

- `python3 scripts/kc-dev-flow-contract-test.py` — `kc-dev-flow contract: PASS`.
  Drives the loader against generated receipts at each route stage and asserts
  the contract prose, observing steps 1, 2, 3, 4, and 6.
- `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py` — `kc-dev-flow
  minimal-stack ablation: PASS`, 60 mutants all `REJECTED`. This is the run that
  makes the marks mean something: it establishes that the checks above have been
  seen to fail, so their silence on the candidate will carry information.

Neither runs an adopter's real shape audit. A step's `OBSERVED` mark covers the
mechanism, not a field use in production.

1. OBSERVED — `choose-work-profile` (agent, reading its SKILL.md template)
   returns a `work_profile` receipt into the work item. The Captain selects.
2. OBSERVED — `kc-dev-flow/scripts/profile-contract-loader.py` reads the work
   item, validates the receipt, and renders the kernel plus the selected
   profile's base and current stage contract. It raises `ContractError` and
   emits nothing on an invalid receipt.
3. OBSERVED — a shape worker reads `reverse-recovery-audit.md` when
   `brownfield_capability_change` fires and writes a `reverse_recovery` receipt
   classifying each layer on completeness and need.
4. OBSERVED — at implementation exit and at completion, a worker reads
   `kernel.md` and maps each retained surface to the accepted goal, a named
   falsifier, a safety boundary, or a required lifecycle obligation.
5. DESIGNED — a worker declares `semantics_unchanged` at shape (`ideation`).
   When it declared `true`, the same worker reaching the `validation` stage must
   carry an equivalence instrument and the case that instrument was observed to
   flag; the loader refuses the `validation` stage load without them. The
   refusal sits at the verification boundary, not at shape, because the
   observed-failure evidence does not exist until build has run.
6. OBSERVED — `scripts/kc-dev-flow-contract-test.py` asserts the kernel and
   contract phrases; `scripts/kc-dev-flow-minimal-stack-ablation.test.py`
   mutates each and requires rejection. `.github/workflows/kc-dev-flow-release-gate.yml`
   runs both.

Unhappy paths, same terms. A worker who never fires
`brownfield_capability_change` reads no audit and reaches step 4 with the
kernel vocabulary only — the split this item closes. A worker who declares
unchanged semantics today passes step 5 with nothing, because nothing exists to
refuse it (`grep -rn -iE "equivalence|semantics_unchanged" kc-dev-flow/` at
`f9683a33` returns no match). A loader `ContractError` stops the stage; it does
not degrade to a warning.

**Observable semantics this work may change.** Stored format: the `work_profile`
receipt gains one required and two conditional scalars. Runtime behaviour: the
loader refuses a receipt it previously accepted. Command grammar and authority:
unchanged. Contract prose that agents read: changed, which is the point.

### AC-4 enforcement point

**A loader-required field, not a prose-only bounded claim.** The constraint that
decides it is this item's own testing obligation — "a declared-unchanged change
without an instrument is refused at the named enforcement point and the refusal
is observed." A prose-only claim has no observable refusal; its only available
check is a substring assertion that the sentence is present, and the kernel's
own verification discipline names `refusal` as driving the system and reading
its rejection. Only `ContractError` produces a rejection to read.

Named point: `resolve_work_item` in
`kc-dev-flow/scripts/profile-contract-loader.py`, fail-closed — the stage
contract does not render.

Fields, on schema `kc-dev-flow-work-profile/v3` (no version bump; see below).
They are gated at two different stages, because AC-4 refuses at the
**verification** boundary and the evidence it demands does not exist before
build has run:

- `semantics_unchanged: true | false` — required for `pilot-product-slice` and
  `production` when `workflow_stage` equals the route's first working stage
  (`ideation`). Precedent: the existing `if workflow_stage ==
  first_workflow_stage` sprint check. This adds no new obligation in substance:
  both `shape.md` contracts already require the author to "declare alongside it
  the observable semantics this work may change ... or state that it changes
  none." The field makes that existing declaration machine-readable.
- `equivalence_instrument` and `equivalence_instrument_failure` — required, and
  rejected as placeholders through the existing `is_placeholder_scalar`, when
  `workflow_stage` is `validation` (the `verify` and `verify-deliver` working
  stages, per `ROUTES`) **and** the receipt carries `semantics_unchanged: true`.
  They are not required at `ideation`: at shape, "the instrument was observed to
  fail" can only be a promise, and a field that can only hold a promise is a
  placeholder the loader would be pretending to check.

**The bounded half.** The loader enforces presence and non-placeholder
concreteness. It cannot verify that the named instrument exists, ran, or
failed. That half is a duty on the verify owner, written as a required-output
line in `production/verify.md` and `pilot-product-slice/verify-deliver.md` — a
prohibition assigned to a named authority, which the kernel's classify-by-falsifier
rule permits without a mechanism. Both halves get written; neither is claimed to
be the other.

**Non-goal ruling: a required field inside the existing `work_profile` receipt
is not a new receipt.** The scope boundary bans "a new receipt or harness" and
the non-goals ban "a new receipt, registry, script, CI job, reviewer loop". The
`work_profile` receipt already exists, is already loader-validated, and already
carries conditionally-required scalars under exactly this pattern (`POC_FIELDS`,
`RECOVERY_FIELDS`). No new YAML block, file, script, or CI job. The route-back
condition "the equivalence requirement cannot be bound at a verification
boundary without adding a new receipt or harness" therefore does not fire.

**Why v3 and not v4.** `kc-dev-flow-work-profile/v3` appears in ten files at the
delivery base (`RATIONALE.md`, `README.md`, `MIGRATION.md`,
`profile-spacedock-route.test.py`, `profile-contract-loader.py`,
`poc-close-guard.py`, `profile-contract-loader.test.py`,
`poc-close-guard.test.py`, `choose-work-profile/SKILL.md`, `docs/dev/README.md`).
A bump is mechanical churn across all ten and buys nothing the stage gate does
not. Only the recovery route has a strict key allowlist
(`recovery_keys != expected_recovery_keys`); the normal route has none, so a new
key on a v3 receipt does not break existing validation.

**The recovery route needs no allowlist change.** Production recovery's
`[build, verify]` route enforces an exact key set, but the check reads
`set(re.findall(r"^  (recovery_[a-z0-9_]+|review_risks):", block, re.MULTILINE))`
— `semantics_unchanged`, `equivalence_instrument`, and
`equivalence_instrument_failure` match neither alternation, never enter
`recovery_keys`, and cannot trip the comparison. Run against a fixture block
carrying all four keys, the pattern returns `{'review_risks',
'recovery_failure'}` only. A recovery route also has no `ideation` stage, so it
is never asked for `semantics_unchanged`; a recovery repairs a named
`recovery_failure` and normally does change behaviour.

**Unverified, checked at build:** whether adding a key to a recovery receipt
disturbs the loader's hash-binding of that receipt to the recovery eligibility
record. This is a build-time check, not a decision.

### Where it touches

| path | lines now | lines after |
|---|---|---|
| `kc-dev-flow/references/kernel.md` | 181 | ~196 |
| `kc-dev-flow/references/reverse-recovery-audit.md` | 81 | ~93 |
| `kc-dev-flow/references/profiles/production/shape.md` | 91 | ~95 |
| `kc-dev-flow/references/profiles/production/verify.md` | 65 | ~72 |
| `kc-dev-flow/references/profiles/pilot-product-slice/shape.md` | 90 | ~94 |
| `kc-dev-flow/references/profiles/pilot-product-slice/verify-deliver.md` | 48 | ~55 |
| `kc-dev-flow/references/profiles/poc-exploration/build.md` | 84 | ~87 |
| `kc-dev-flow/scripts/profile-contract-loader.py` | 886 | ~935 |
| `kc-dev-flow/scripts/profile-contract-loader.test.py` | 1976 | ~2045 |
| `kc-dev-flow/skills/choose-work-profile/SKILL.md` | 129 | ~135 |
| `kc-dev-flow/MIGRATION.md` | 301 | ~316 |
| `scripts/kc-dev-flow-contract-test.py` | 1869 | ~1918 |
| `scripts/kc-dev-flow-minimal-stack-ablation.test.py` | 873 | ~928 |

Reconciled journey to table: every step's acting file appears above except four,
each named with why it does not change.

- `.github/workflows/kc-dev-flow-release-gate.yml` — step 6 depends on it; it
  runs both tests by path and no path changes.
- `kc-dev-flow/contract-manifest.json` (41) — step 2 resolves through it; this
  item adds no reference file, so the resource set is unchanged. Verify at build.
- `scripts/kc-dev-flow-multi-profile-gate.py` (541) — builds `work_profile`
  fixtures at line 246. Unchanged only if its Pilot and Production fixtures sit
  at a stage past `ideation` and none reaches `validation` with
  `semantics_unchanged: true`; **unverified**, checked at build.
- `kc-dev-flow/scripts/profile-spacedock-route.test.py` — carries the v3 schema
  string and may build Pilot/Production fixtures at `ideation`, which under this
  design need `semantics_unchanged`; **unverified**, checked at build. Same
  class as the two fixture builders above, and the reason
  `kc-dev-flow-contract-test.py`'s `lines after` allows for its own fixture
  builder gaining the field.

Reconciled table to journey: `kc-dev-flow/MIGRATION.md` and
`choose-work-profile/SKILL.md` appear in the table but not as journey steps —
they are AC-7's adopter-visible surface, which the journey deliberately does not
run.

Not in either, and why: `docs/dev/_mods/kernel.md` and
`docs/dev/_mods/reverse-recovery-audit.md` do not exist at `f9683a33`.
`kc-dev-flow/references/roborev-implementation-exit.md` (210) carries none of the
necessity vocabulary — AC-3's clause lives only in `kernel.md`
(`grep -n -i remov kc-dev-flow/references/kernel.md` at `f9683a33` shows the
implementation-exit clause grading only retention).

### Stop numbers

Measured as `git diff --stat f9683a33 <candidate>`.

- changed files: stop at **16** (estimate 13).
- changed lines: stop at **500** (estimate ~340).
- named runaway area: `profile-contract-loader.test.py` plus
  `kc-dev-flow-minimal-stack-ablation.test.py` together — stop at **180**
  changed lines across the pair. Named because AC-4 and AC-5 both land there and
  an ablation mutant is cheap to add and hard to stop adding.

Crossing any of the three stops work and reports; it passes and fails nothing.

### Rollback policy

Forward-recovery. Every change is contract prose plus a loader field guarded by
deterministic tests already in the release gate; a bad revision is reverted by
`git revert` of the single delivery commit. No migration, no stored state, no
external mutation. The one irreversible-shaped risk is an adopter that took the
new version and wrote `semantics_unchanged` into a receipt: a revert makes that
field unread, not invalid, because the normal route has no key allowlist.

### Reverse-recovery receipt

```yaml
reverse_recovery:
  trigger: replacement of two disjoint need vocabularies with one, replacement of two names for one evidence primitive, and a missing equivalence-instrument requirement
  boundary: journey = an author classifies whether a surface earns its place, and a verify owner refuses a declared-unchanged change without an instrument; search boundary = kc-dev-flow/ and scripts/kc-dev-flow* at f9683a33, excluding .context/ scratch, CHANGELOGs, and adopter repositories not checked out here
  layers:
    - surface: reverse-recovery need axis (REQUIRED / NO_OBSERVED_CONSUMER / UNKNOWN)
      location: kc-dev-flow/references/reverse-recovery-audit.md:38-45
      completeness: WORKING
      need: REQUIRED
      evidence: three conditional-reference blocks declare receipt reverse_recovery (production/shape.md, pilot-product-slice/shape.md, poc-exploration/build.md) and the contract test asserts all three
      disproof_hook: delete the receipt key from production/shape.md, then python3 scripts/kc-dev-flow-contract-test.py
    - surface: disproof_hook receipt field
      location: kc-dev-flow/references/reverse-recovery-audit.md:76
      completeness: WORKING_UNIT_UNPROVEN
      need: NO_OBSERVED_CONSUMER under the audit and REQUIRED under the kernel — the instance of AC-1 appearing inside its own receipt, recorded as evidence for AC-1 rather than as a finding
      evidence: two searches — repo-wide grep for disproof_hook across kc-dev-flow/ and scripts/ returns one line, and the loader's declared-receipt return path reads receipt names only, never fields
      disproof_hook: grep -rn disproof_hook kc-dev-flow/ scripts/ at f9683a33 returns only reverse-recovery-audit.md:76
    - surface: kernel minimal-necessity mapping targets
      location: kc-dev-flow/references/kernel.md:123-128
      completeness: WORKING
      need: REQUIRED
      evidence: contract test requires the verbatim phrase "the accepted goal, a named falsifier, a safety boundary, or a required lifecycle obligation"; the ablation drives run_kernel_contract_mutant against the same file
      disproof_hook: mutate the phrase in kernel.md, then python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py
    - surface: kernel implementation-exit comparison
      location: kc-dev-flow/references/kernel.md:100-113
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: fails at the seam AC-3 names — it enumerates added files, dependencies, abstractions, tests, and comments and grades no removal; grep -n -i remov over kernel.md at f9683a33 shows every hit grading retention or scaffolding, none grading a removal's own necessity claim
      disproof_hook: grep -n -i remov kc-dev-flow/references/kernel.md at f9683a33
    - surface: equivalence-instrument requirement for a declared-unchanged change
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: two searches — grep -rn -iE "equivalence|semantics_unchanged|behaviour-preserving" over kc-dev-flow/ and docs/dev/ returns no match, and both verify contracts' Required output lists were read in full and name no instrument; boundary stops at this repository, excluding subspace-relay and carlove-v1
      disproof_hook: grep -rn -iE "equivalence|semantics_unchanged" kc-dev-flow/ scripts/ at f9683a33
    - surface: loader conditional required-field machinery
      location: kc-dev-flow/scripts/profile-contract-loader.py:35-48,513-540
      completeness: WORKING
      need: REQUIRED
      evidence: driven by profile-contract-loader.test.py and by the ablation's run_poc_entry_mutant, which deletes poc_decision from POC_FIELDS and requires the loader test to reject
      disproof_hook: python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py
    - surface: vendored docs/dev/_mods/{kernel,reverse-recovery-audit}.md
      location: MISSING
      completeness: MISSING
      need: NO_OBSERVED_CONSUMER
      evidence: two searches — git ls-tree -r --name-only f9683a33 -- docs/dev/_mods/ returns only pr-merge.md, and the contract test's obsolete_adopter_copies set names both paths as forbidden; boundary is the delivery base tree
      disproof_hook: restore docs/dev/_mods/kernel.md, then python3 scripts/kc-dev-flow-contract-test.py
  decision: redesign
```

Per-layer split behind the single `decision`: the vocabulary layers are a
redesign of two incompatible existing contracts; layer five is `build`; layer
six is `use` — the AC-4 field composes onto existing loader machinery rather
than adding a mechanism.

### multi_slice_required: false

`journey-slicing.md` was read and not loaded as a receipt. The change is ~340
lines across 13 files at the delivery base, under every stop number, and
delivers as one integrated slice. No piece needs to land before another to be
demonstrable: the vocabulary rename and the loader field are each observable on
their own, and neither blocks the other.

Other conditional references: `retained_document_change` fires —
`kernel.md` and `reverse-recovery-audit.md` are retained documents and the
policy carries no receipt, so its rules bind the prose without a record here.
`project_context_claim_may_change` is false: `kc-dev-flow/README.md:194`
describes the audit's trigger, not its need vocabulary, and no bound
project-context document states a described behaviour this item changes.

### Falsifiable acceptance checks

Each names the change that would make it fail.

- **AC-1** — the ablation gains a `run_kernel_contract_mutant` restoring the old
  mapping-target phrase and a `run_manual_contract_mutant` restoring
  `NO_OBSERVED_CONSUMER` in `reverse-recovery-audit.md`; both must be rejected by
  `kc-dev-flow-contract-test.py --ablation-check`. The audit prose carries one
  worked case — a safety-boundary surface with no observed consumer — asserted
  verbatim by the contract test. *Fails if* either old phrase survives the
  rename, because then the mutant is a no-op and the ablation reports a survivor.
- **AC-2** — the contract test requires, in both files, the one primitive name
  plus each contract's declared tier and that tier's stated limit. *Fails if* the
  primitive is named in `kernel.md` only: the reverse-recovery phrase assertion
  finds nothing.
- **AC-3** — the contract test requires an implementation-exit clause naming
  removed surfaces; an ablation mutant restores the added-only enumeration and
  must be rejected. *Fails if* removals are graded in new prose while the
  asserted phrase still matches the old added-only sentence.
- **AC-4** — `profile-contract-loader.test.py` drives the loader at
  `workflow_stage: validation` with a Production receipt carrying
  `semantics_unchanged: true` and no `equivalence_instrument`, and reads the
  `ContractError`; a second case supplies `TBD` for
  `equivalence_instrument_failure` and reads the same refusal; a third drives the
  same receipt at `ideation` and observes it load, proving the refusal sits at
  the verification boundary and not at shape. The ablation adds a
  `run_loader_admission_mutant` deleting the field from the required tuple.
  *Fails if* the `raise` is removed or downgraded: the expected rejection does
  not arrive and the case errors as an unexpected success. *Also fails if* the
  gate is bound at `ideation` instead: the third case's expected load becomes a
  refusal.
- **AC-5** — build records a pairing table over
  `git diff f9683a33 -- scripts/kc-dev-flow-contract-test.py scripts/kc-dev-flow-minimal-stack-ablation.test.py`,
  matching every removed `require(` or mutant to a replacement asserting the same
  class. *Fails if* any removal is unmatched.
- **AC-6** — `git ls-tree -r --name-only <candidate> -- docs/dev/_mods/` returns
  only `pr-merge.md` and the contract test passes. *Fails if* either vendored
  file returns: `obsolete_adopter_copies` rejects it.
- **AC-7** — the loader test drives a v3 Production receipt at `implementation`
  with no `semantics_unchanged` and observes it load, and a second at
  `validation` with no `semantics_unchanged` key at all and observes it load;
  `MIGRATION.md` records the one-line addition an item at or re-entering shape must
  make. *Fails if* the requirement is made unconditional, which turns both
  expected successes into refusals.

### Residual and scaffolding record

A pre-change item carries no `semantics_unchanged` key, so its `validation` load
has nothing to check and proceeds. That is the AC-7 carve-out, and it is
deliberate: a new item entering `ideation` is refused without the declaration,
so the gate holds for everything shaped after this lands. Removal condition:
none needed; this is not scaffolding but the stage gate itself. The
`MIGRATION.md` line is the migration AC-7 requires — it applies to any item at or
re-entering `ideation` when the new version lands, not only one that re-enters —
and it is one line because no
stored value changes shape.

Bounded claim, stated once: the loader refuses an absent or placeholder
instrument. It does not and cannot establish that the named instrument was run
or that it failed. Nothing in this item makes that claim enforceable; it is a
verify-owner duty and is written as one.

## Stage Report: ideation

- DONE: Name the enforcement point for AC-4 (a declared-unchanged change is refused until it names an equivalence instrument seen to fail): loader-required field or prose-only bounded claim, and record whether a required loader field counts as a receipt under the non-goals.
  `## Shape` § AC-4 enforcement point — `ContractError` in `resolve_work_item`, `kc-dev-flow/scripts/profile-contract-loader.py`, gated at the `validation` stage for the two evidence scalars and at `ideation` for the declaration; the non-goal ruling is that a field inside the existing `work_profile` receipt is not a new receipt, because `POC_FIELDS` and `RECOVERY_FIELDS` already carry conditionally-required scalars there.
- DONE: Deliver the `where it touches` table and stop numbers against the delivery base, reconciled both ways with the journey, covering kernel.md, reverse-recovery-audit.md, the contract test, the minimal-stack ablation test, and the loader-served copies.
  `## Shape` § Where it touches — 13 files, `lines now` from `git show f9683a33:<path>`; reconciled both directions with four journey files named as unchanged and two table files named as outside the journey.
- DONE: Record the reverse_recovery receipt for this brownfield change (need-axis rename, disproof_hook unification, removal grading) and decide multi_slice_required with falsifiable acceptance checks mapped to AC-1..AC-7.
  `## Shape` § Reverse-recovery receipt (7 layers, `decision: redesign`), § multi_slice_required: false, § Falsifiable acceptance checks (AC-1..AC-7, each naming its falsifying change).

### Summary

Both delivery-base gates were run this session in a clean `f9683a33` worktree
and pass: the contract test exit 0, and the ablation exit 0 with 60 mutants all
rejected. The ablation run is what lets the shape claim its acceptance checks can
fail rather than merely exist.

The delivery base moved the ground under two checklist items. `origin/main`
(`f9683a33`) already deleted the vendored `docs/dev/_mods/` contract pair — only
`pr-merge.md` survives — so AC-6 is satisfied by its own escape clause with the
contract test's `obsolete_adopter_copies` set as the enforcement point, and this
item does zero work for it. The working checkout is behind main and still
carries those files, so every count was taken from `f9683a33`, not from disk.

AC-4 lands as a loader-required field rather than prose because the testing
obligation demands an observed refusal, and only `ContractError` produces a
rejection to read. The declaration is required at `ideation` and the two evidence
scalars at `validation`, because AC-4 refuses at the verification boundary and
"the instrument was observed to fail" cannot be anything but a promise before
build has run. The loader half is bounded to presence and non-placeholder
concreteness; "seen to fail" is a verify-owner duty. A v4 schema bump was
rejected — the v3 string appears in ten files and buys nothing a stage gate does
not. The Production recovery route needs no change: its exact-key regex matches
only `recovery_*` and `review_risks`, verified by running the pattern against a
fixture block carrying all four keys.

One thing the Captain owns: the entity's `## Non-goals` bullets are truncated
mid-sentence in the admitted body. The shape was written against the complete
`scope_boundary` line in the work-profile receipt, and the snapshot was not
rewritten.
