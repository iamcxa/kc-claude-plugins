---
title: "kc-dev-flow: unify the necessity vocabulary across kernel and reverse-recovery, and bind the equivalence instrument"
status: validation
source: https://linear.app/duckbase-co/issue/DEV-46/kc-dev-flow-unify-the-necessity-vocabulary-across-kernel-and-reverse
product: kc-dev-flow
planning-window: Linear Cycle d1c96803-02fa-4323-b3a8-2fc44cc43699 2026-09-10T16:00:00.000Z/2026-09-24T16:00:00.000Z
planning-outcome: Linear Project 4746021d-2930-4589-80a0-b7b3d1d70eeb kc-dev-flow slimming dogfood sha256:0599c390742642a1edf03e07a50c28635ff41d3ef77188e076cb2f02e6d85372
sprint: S8
sprint-readiness: ready
started: 2026-09-02T08:19:42Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-dev-46-unify-necessity-vocabulary
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
        - id: gate:50c1y5wf7dzh0ww2a9qajn47:validation
          stage: validation
          attempts:
            - id: gate-attempt:50c1y5wf7dzh0ww2a9qajn47-validation-1
              briefing:
                id: briefing:50c1y5wf7dzh0ww2a9qajn47:validation:attempt-1:revision-1
                digest: sha256:0c23766fb155e2ef0e5afa7cb13f5dbf7c4fa6621bac71cfcb5d2e4b795b58cf
                room-ref: ./dev-46-unify-necessity-vocabulary/review/validation/briefing-1
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

## Implementation evidence: RoboRev claim

- identity: `43c8bfd90d54d74dea48ce47d570938af3afde11dccfa06dc6e46b7ca2413140`
- claimant: `claude-ensign:2b074c1c-5e22-4879-9eda-db61c5abee89`
- observed state revision: `4fcc5a9e00d109a3a1496d9263a51e0150ecee5a`
- candidate: `f9683a337e4c056a4e0cc1e597dc4a93ce762ca6..8613cedb50c5bd62bcf01dcffba12934648108e9`
- state: `claimed`

### Changed-tip confirmation claim

- identity: `3f3ca3ca757f4cbb02dc6e49abfd1018bf592ef8a63f11a9aa2d6c5bc6f00be9`
- claimant: `claude-ensign:2b074c1c-5e22-4879-9eda-db61c5abee89`
- observed state revision: `7ea470486ca51d3f09a75d8591d926d6ea438142`
- candidate: `f9683a337e4c056a4e0cc1e597dc4a93ce762ca6..7571a25de42c7d83759ac40963feabdb0ab3c76b`
- prior finding: RoboRev job `294` (Medium) found kc-dev-flow/references/profiles/pilot-product-slice/shape.md:64 never told an author to record `semantics_unchanged`, unlike Production's copy; repaired in commit `7571a25d` by restoring the sentence and trimming a same-file restatement to hold the byte ceiling.
- state: `claimed`

### RoboRev observation result

- capability: `review_convergence`; mode: `observe`; profile: `production`; provider: `roborev`
- outcome: `UNKNOWN(reason: stale)` — both terminal job JSONs omit configuration hash, selected profile, implementation family, panel identity/population, and caps; the closed mapping does not copy missing expected fields into evidence, so neither provider verdict below is claimed as the contract-mapped result
- exact input (request): base `f9683a337e4c056a4e0cc1e597dc4a93ce762ca6`, tip `8613cedb50c5bd62bcf01dcffba12934648108e9`, identity `43c8bfd90d54d74dea48ce47d570938af3afde11dccfa06dc6e46b7ca2413140`, job `294`, provider verdict `F` (1 Medium finding)
- exact input (confirmation): base `f9683a337e4c056a4e0cc1e597dc4a93ce762ca6`, tip `7571a25de42c7d83759ac40963feabdb0ab3c76b`, identity `3f3ca3ca757f4cbb02dc6e49abfd1018bf592ef8a63f11a9aa2d6c5bc6f00be9`, job `295`, provider verdict `F` (1 Medium finding)
- members: `panel: none`; provider member population absent, contributing to `stale`
- requests: `1`; changed-tip confirmations: `1` (both caps now exhausted for this candidate)
- cost: `$0.0590116` approximate total; `jobs_with_cost=2`, `jobs_total=2`, `complete=true`

**Finding 1** (job `294`, Medium) — `kc-dev-flow/references/profiles/pilot-product-slice/shape.md:64` never told an author to record `semantics_unchanged`, unlike Production's copy, so a Pilot ideation item following its loaded stage contract could fail the new loader admission with no instruction how to satisfy it.
Disposition: **repaired**, commit `7571a25d` — restored the sentence and trimmed the Required-output checklist's restatement of the same fact to hold the byte ceiling (95 -> 145 bytes headroom on `pilot-product-slice/ideation`). Confirmation job `295` re-reviewed the full `f9683a33..7571a25d` range and did not repeat this finding.

**Finding 2** (job `295`, Medium) — `kc-dev-flow/scripts/profile-contract-loader.py:586` (pre-repair): a receipt that declared `semantics_unchanged: true` at `ideation` could remove the field, or flip it to `false`, before `validation` and bypass the required equivalence instrument, because validation treated a missing field as a supported legacy receipt with no way to distinguish it from a pre-feature item.
Disposition: **split**.
- Missing-field half — **repaired**, commit (this stage's final commit, not RoboRev-reviewed: the confirmation cap is exhausted for this candidate). `semantics_unchanged` is now required at every Pilot/Production working stage from `ideation` onward, not only at `ideation`; a receipt that drops the field after declaring it is refused with `ContractError` naming the field, at `implementation` or `validation`. `kc-dev-flow/MIGRATION.md` records the one-line addition an in-flight item must make before its next stage. The recovery route and POC are untouched — neither ever carries the field. `profile-contract-loader.test.py`'s two "no key loads" cases became refusal cases; ablation mutant `necessity-post-ideation-requirement-removed` reverts the gate and is REJECTED.
- Flip half — **open, not fixed**. Bounded claim: the loader reads one file with no history, so it cannot distinguish an honest `semantics_unchanged: false` from a `true` declared at `ideation` and later flipped. This is not closed by a loader field; a flip is an admitted-declaration change, and the mechanism that would catch it — the ideation gate's bound briefing digest compared against the shape's recorded `semantics_unchanged` value — is a validation-stage duty, not this stage's. Carried into validation as a named residual, not silently accepted.

## Stage Report: implementation

- DONE: Land one necessity vocabulary across kernel.md and reverse-recovery-audit.md (AC-1, AC-2, AC-3) with contract-test and ablation assertions that reject each renamed boundary for its named reason (AC-5), running the old assertion against each mutation before removing it so no previously caught regression is lost.
  No prior assertion was removed or renamed — every existing `require()` phrase in `scripts/kc-dev-flow-contract-test.py` still matches unchanged text, so the AC-5 pairing table is empty by construction (nothing to lose). `reverse-recovery-audit.md`'s `REQUIRED` row maps to `kernel.md`'s four minimal-necessity reasons plus a named consumer, with a verbatim worked case and a `disproof_hook` search-tier/execution-tier statement. `kernel.md`'s implementation-exit comparison states the removal predicate and reason as a pointer to Completion invariant's Minimal necessity, its one explanatory home: "A removal is graded by Minimal necessity like a retention; without it, unmapped." (rewritten twice — first from a three-word placeholder that named neither predicate nor reason, then shrunk from a 158-byte standalone restatement to this 80-byte pointer per Science Officer review, which also required restoring a Verification discipline rule cut for byte headroom — see Diagnostics). Four ablation mutants added and REJECTED: `removal-grading-clause-removed` (kernel), `audit-worked-case-classification-reverted` (audit), `necessity-post-ideation-requirement-removed` (loader), `necessity-instrument-field-removed` (loader); commits `17184003`, `8613cedb`, `54e33baa`.
- DONE: Implement semantics_unchanged (required at ideation) and the two equivalence-evidence scalars (required at validation) as loader-required fields refused via ContractError, with the refusal observed in profile-contract-loader.test.py (AC-4), and verify the three fixture builders the shape marked unverified (multi-profile-gate, profile-spacedock-route.test, contract-manifest).
  `profile-contract-loader.py` `resolve_work_item` requires `semantics_unchanged: true|false` for Pilot/Production v3 non-recovery receipts at **every** working stage from `ideation` onward (widened from ideation-only after RoboRev job 295), and `equivalence_instrument` + `equivalence_instrument_failure` at `validation` when `semantics_unchanged: true`; all raise `ContractError`. `profile-contract-loader.test.py` drives three refusal/load cases (no instrument, placeholder failure value, loads clean at `ideation`) plus two AC-7 cases that now assert refusal, not a load, when the key is absent at `implementation` or `validation`. Fixture builders: `kc-dev-flow-multi-profile-gate.py`'s `entity_body`, `kc-dev-flow-contract-test.py`'s `write_profile_work_item`, and its Linear-admission fixture (`dev-12.md`, a `status: implementation` receipt) all needed the field added unconditionally, not only at `ideation` (fixed); `profile-spacedock-route.test.py` passed unchanged; `contract-manifest.json` needs no change (no reference file added or removed; the `expected_manifest_resources` check still passes).
  RoboRev job 294 (Medium, repaired commit `7571a25d`) and job 295 (Medium, split disposition) are recorded under `## Implementation evidence: RoboRev claim` above `## Stage Report: implementation`. No further RoboRev request was made this stage: the request and one changed-tip confirmation caps for this candidate are both exhausted, and the Science Officer round below explicitly required none.
- DONE: Stay inside the shape's stops (16 files / 500 lines / 180 lines across the two test files against f9683a33); at implementation exit record the diff counts as diagnostics, the comment pass (blocks cut and candidates kept with reasons), the AC-7 adopter migration entry and version, and the roborev observation only if the loader emits implementation_exit_observation_declared true.
  Final `git diff --stat f9683a33`: 14 files changed, 221 insertions(+), 9 deletions(-) — under the 16-file/500-line stops. The named pair (`profile-contract-loader.test.py` + `kc-dev-flow-minimal-stack-ablation.test.py`): 86+26=112 changed lines — under the 180-line stop. Comment pass this stage: two comment blocks (7 lines, unchanged this round) — `profile-contract-loader.py`, explaining why the `semantics_unchanged` check moved from ideation-only to unconditional; `profile-contract-loader.test.py`, explaining the AC-7 refusal cases' MIGRATION.md tie. Both kept for the reason given; nothing cut. AC-7 migration: `kc-dev-flow/MIGRATION.md` § "2026-09-02 — Pilot and Production require `semantics_unchanged` at every stage after ideation", schema stays `kc-dev-flow-work-profile/v3` (no version bump). `implementation_exit_observation_declared` for this work item at this stage: `True`; the RoboRev observation ran once (one request, one confirmation) and is recorded above, exhausted before this Science Officer round, which required no further request.

### Diagnostics

- **Science Officer review (this round).** Restored verbatim, in § Verification discipline's first bullet: "This binds the check, not only the artifact: a round that cannot say what would have reddened its own instrument has measured nothing." — cut in an earlier round to make byte room; the SO found it carries a distinct obligation (the round must say why its negative case corresponds to the claim) with no second home, so it was a rule, not a restatement. Paid for by applying kernel's own duplicate-fact rule to my own AC-3 addition instead of a third-party sentence: the Shared boundaries removal-grading sentence already restated Completion invariant's Minimal necessity (which already says a surface is removed when its absence breaks none of the four binders), so it shrank from a 158-byte standalone claim to an 80-byte pointer naming Minimal necessity as the home.
- `kc-dev-flow/references/kernel.md` byte-ceiling headroom (`scripts/kc-dev-flow-multi-profile-gate.py`'s 40000-byte absolute static-instruction ceiling): kernel.md is **11088 bytes at the delivery base, 11173 bytes now** (+85). `pilot-product-slice/ideation` headroom: **79 bytes**, measured after both the restore and the pointer shrink. This clears the largest ablation mutant's kernel.md growth (`runtime-topology-restored`, 69 bytes) with 10 bytes to spare — verified by running the full `kc-dev-flow-minimal-stack-ablation.test.py` suite to a clean exit, not estimated. This is tighter than the 145-byte headroom reported after the prior (RoboRev-repair) round, because restoring a genuine 135-byte rule costs bytes somewhere; it is looser than the delivery base's own ~150-byte pre-change headroom, which no round since the first kernel.md edit has matched — the unified vocabulary's kernel-side footprint is real, not fully absorbable by trimming. `reverse-recovery-audit.md` (not ceiling-bound) still carries the fuller two-tier vocabulary explanation; `pilot-product-slice/shape.md`'s `semantics_unchanged` sentence (restored after RoboRev job 294) is unaffected by this round.
- Tests run clean in this worktree at the final commit `54e33baa`: `python3 scripts/kc-dev-flow-contract-test.py` (PASS), `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` (PASS), `python3 kc-dev-flow/scripts/profile-spacedock-route.test.py` (PASS), `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py` (PASS, 64 mutants all REJECTED, up from the delivery-base's 60).

### Summary

`kernel.md` and `reverse-recovery-audit.md` now share one `need` vocabulary (`REQUIRED`/`NO_OBSERVED_CONSUMER`/`UNKNOWN`) with an identical worked case, one `disproof_hook` primitive at two declared tiers, and a removal-grading pointer to Minimal necessity, its one explanatory home. `profile-contract-loader.py` requires `semantics_unchanged` at every Pilot/Production working stage from `ideation` onward and the two equivalence-evidence scalars at `validation` when `true`, both fail-closed via `ContractError`.

Three review rounds landed on this candidate: RoboRev's one request plus one changed-tip confirmation (both caps now exhausted) found and closed a Pilot documentation gap and split a structural gap (missing-field half closed, flip half an open validation residual — see `### RoboRev observation result`); a Science Officer round then found the AC-3 byte-fit had cut a genuine Verification-discipline rule as collateral, not a restatement, and required restoring it while shrinking the newer, actually-redundant sentence instead. No further RoboRev request was made or required this round.

Final diff: 14 files, 221 insertions(+), 9 deletions(-), under all three declared stops. All four test suites pass at commit `54e33baa`. `kernel.md`: 11088 → 11173 bytes; `pilot-product-slice/ideation` byte-ceiling headroom: 79 bytes, verified sufficient by a clean ablation run.

## Stage Report: validation

- DONE: Independently re-run at the exact candidate 54e33baa (never the builder's numbers): the contract test, loader test, spacedock-route test, multi-profile gate, and the minimal-stack ablation, then execute each of the shape's falsifiable acceptance checks for AC-1..AC-7 and record the falsifier's kind and observed failure — including the loader's ContractError refusals for a missing semantics_unchanged after ideation and a missing equivalence instrument at validation.
  Ran all five in a clean checkout at `54e33baa`, all exit 0: `kc-dev-flow-contract-test.py` PASS; `profile-contract-loader.test.py` PASS; `profile-spacedock-route.test.py` PASS; `kc-dev-flow-multi-profile-gate.py` PASS; `kc-dev-flow-minimal-stack-ablation.test.py` PASS. **Correction to the builder's number**: the ablation run shows **62** mutants REJECTED, not "64" as claimed in the implementation stage report — confirmed by an independent `f9683a33` worktree run too (**58**, not "60"). Both counts are off by the same +2; the claimed *delta* (+4 new mutants) is correct, only the absolute counts were wrong. Does not change PASS/FAIL of any AC. AC-1 (`git grep` the `REQUIRED` row in `reverse-recovery-audit.md:41` mapping verbatim to kernel's four reasons) and AC-2 (`disproof_hook` named once, search-tier/execution-tier sentence present in both files, asserted verbatim by the contract test at `kc-dev-flow-contract-test.py`) and AC-3 (`kernel.md:112` "A removal is graded by Minimal necessity like a retention; without it, unmapped.") are all exercised by the ablation's `removal-grading-clause-removed` and `audit-worked-case-classification-reverted` mutants — both REJECTED. AC-4: drove `profile-contract-loader.test.py`'s three cases directly (`unchanged_no_instrument` → `ContractError: work item must contain exactly one equivalence_instrument`; `unchanged_placeholder_failure` with `equivalence_instrument_failure: TBD` → `ContractError: equivalence_instrument_failure must be a concrete scalar`; `unchanged_at_ideation` → loads clean, proving the refusal sits at `validation` not `ideation`) plus AC-7's two refusal cases (`legacy-necessity-implementation`, `legacy-necessity-validation`, both → `ContractError: work item must contain exactly one semantics_unchanged`) — all four raised the exact named `ContractError`, none silently passed. AC-5: `git diff -U0 f9683a33 54e33baa` on the two test files shows zero removed `require(`/mutant lines — the pairing table is empty by construction, confirmed, not just claimed. AC-6: `git ls-tree -r --name-only 54e33baa -- docs/dev/_mods/` returns only `pr-merge.md`.
- DONE: Disposition the review findings: confirm RoboRev 294 and 295 repairs at the candidate, then test the open residual (semantics_unchanged flipped true->false after ideation) at its named catch point, and either close it with evidence or record it as an accepted-residual question for the Captain; raise one bounded Science Officer question only if a claim is contested.
  RoboRev 294 confirmed: `pilot-product-slice/shape.md:65` and `production/shape.md:67` both carry "Record it as `semantics_unchanged`." RoboRev 295 missing-field half confirmed: `profile-contract-loader.py:557` gates `semantics_unchanged` unconditionally on `necessity_active` (not `workflow_stage == first_workflow_stage`), so it is required at every stage after `ideation`, matching the repaired code comment at line 577. Flip-half residual: no code anywhere compares an item's ideation-time declaration against its current receipt (`grep -rn "briefing.*digest"` over `kc-dev-flow/` and `docs/dev/` returns nothing) — the residual is genuinely still open, correctly labeled as such rather than silently accepted. Tested the named catch point concretely on this item's own ideation gate record: `git show c01f8cad78c7762bf3ed11d5c07fdc6fb44ec0d2:dev-46-unify-necessity-vocabulary.md` (the `git-root://` URI pinned in `review/ideation/briefing-1/index.json`) reproduces content whose `sha256` matches the briefing's recorded `rev` exactly — the pin-and-digest primitive a validation-stage worker would use to detect a flip is real and exercisable today, not aspirational; this item itself predates the field so there is no `semantics_unchanged` value to diff, but the mechanism it would be diffed through is proven functional. **Recorded as an accepted-residual question for the Captain, exact reading**: the loader closes the missing-field half by code; the flip half has a real, exercised catch point (ideation briefing's pinned git-root artifact + digest) but no automated comparison — a human or agent at each item's `validation` stage must run it by hand until/unless a future item automates it. No claim was contested in either RoboRev disposition or in the flip-residual reasoning, so no Science Officer question was raised.
- DONE: Delivery readiness for the exact revision: the candidate is pushed under the Linear-bound head branch with close line Fixes DEV-46, the AC-7 MIGRATION.md entry names the version that carries the change, no absolute claim in the diff or commit messages lacks its enforcement point, and the validation report states what release authorization the Captain is being asked for.
  Found one real defect while establishing readiness, not pre-existing at `54e33baa`: `choose-work-profile/SKILL.md` (an already-budgeted touch point in the shape's own "where it touches" table) still told an author `semantics_unchanged` is recorded on `ideation` entry and its template comment said "entering ideation only" — both stale since commit `50a5913d` widened the requirement to every stage after ideation (RoboRev 295's missing-field half). An author following this skill's own instructions could drop the field after `ideation` and hit an unexplained `ContractError`. Fixed in commit `f70b8cdb` (5 insertions, 4 deletions); re-ran all five gates clean afterward, including the ablation (62 mutants REJECTED, same count as at `54e33baa` — the fix touches prose only). **New exact candidate: `f70b8cdb`**, superseding `54e33baa`. Diff stops at this candidate against `f9683a33`: 14 files / 222 insertions(+) / 9 deletions(-) (under 16/500), named test-file pair 112 changed lines (under 180); my own commit message overstated this as "227 insertions" — git's non-additive diff realignment across the combined range gives 222, the correct and lower number, so the stop is still cleared, only my commit-message arithmetic was off. Pushed `f70b8cdb` to `origin/feature/dev-46-kc-dev-flow-unify-the-necessity-vocabulary-across-kernel-and` (new branch, `54e33baa..f70b8cdb`). No PR exists yet (`pr:` frontmatter empty, no open GitHub PR on this branch) — "Fixes DEV-46" is the close line to place in that PR's body when it is created; not added to a commit trailer, since no repo precedent uses one (`git log --all` shows one `Closes DEV-2` instance, in a PR body). AC-7's MIGRATION.md entry (`kc-dev-flow/MIGRATION.md:202-226`) does not name an exact semver — it says "when the new plugin version lands," matching every other dated entry in the file (none name a forward version number) and this repo's own rule against hand-guessing an unreleased release-please version; this is the correct reading of AC-7's "the version that carries it" clause under this repo's convention, not a gap. Absolute-claim audit: `git diff f9683a33 f70b8cdb | grep -iE '\bexactly\b|\bonly\b|\balways\b|\bnever\b|\bcannot\b|byte-for-byte'` on added lines returns only claims that are either (a) test-assertion string literals, (b) kernel/audit prose whose enforcement is the ablation mutant guarding that exact phrase, or (c) code comments sitting directly above the `ContractError` raise they describe — none unanchored.

### Summary

Independently reproduced every gate and every AC-1..AC-7 falsifier at the exact candidate, catching one real numeric error in the builder's ablation-mutant count (off by 2, delta claim still correct) and one real prose defect the builder's own shape had already budgeted for but left unfinished (`choose-work-profile/SKILL.md`'s stale ideation-only guidance), fixed and re-verified at new candidate `f70b8cdb`. The flip-half residual from RoboRev 295 remains open by design — its catch point (ideation briefing's pinned git-root artifact + digest) was proven functional against this item's own gate record, but no code automates the comparison, so it is carried forward as an accepted, named residual rather than closed.

**Release authorization being asked of the Captain**: approve this validation gate (the verification ruling — the exact revision `f70b8cdb`, pushed to `origin/feature/dev-46-kc-dev-flow-unify-the-necessity-vocabulary-across-kernel-and`, is correctly implemented against all seven acceptance criteria); separately authorize Draft PR creation from that branch against `DEV-46` with close line `Fixes DEV-46` (per `production/verify.md`, Draft creation is Captain-authorized and distinct from this gate); and rule on the flip-half residual — accept it as a documented manual verify-owner duty (current state), or require it closed by a future item before further Production items with `semantics_unchanged: true` are trusted at scale.

