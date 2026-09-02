---
title: "Replace kc-dev-flow contract-test phrase pins with behaviour assertions a mutation can redden"
status: validation
source: https://linear.app/duckbase-co/issue/DEV-51/replace-kc-dev-flow-contract-test-phrase-pins-with-behaviour
product: kc-dev-flow
planning-window: Linear Cycle d1c96803-02fa-4323-b3a8-2fc44cc43699 2026-09-10T16:00:00.000Z/2026-09-24T16:00:00.000Z
planning-outcome: Linear Project 4746021d-2930-4589-80a0-b7b3d1d70eeb kc-dev-flow slimming dogfood sha256:0599c390742642a1edf03e07a50c28635ff41d3ef77188e076cb2f02e6d85372
sprint: S8
sprint-readiness: ready
started: 2026-09-02T14:23:40Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-dev-51-behaviour-assertions-for-contract-pins
issue:
pr:
mod-block:
id: m29y546p4sh77vbs2dv09gkp
gates:
    version: 1
    records:
        - id: gate:m29y546p4sh77vbs2dv09gkp:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:m29y546p4sh77vbs2dv09gkp-backlog-1
              briefing:
                id: briefing:m29y546p4sh77vbs2dv09gkp:backlog:attempt-1:revision-1
                digest: sha256:7ae98598b34e8752d28496fb24b9d24a58db08b6fc675d9dcd83c2e78b21e62a
                room-ref: ./dev-51-behaviour-assertions-for-contract-pins/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:m29y546p4sh77vbs2dv09gkp:backlog:1
                briefing: briefing:m29y546p4sh77vbs2dv09gkp:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-02T14:10:08.252464Z"
                decision: approve
                reason: 'Captain approved DEV-51 into Pilot ideation: Project kc-dev-flow slimming dogfood, Cycle 2, sprint S8; semantics_unchanged true, the equivalence instrument is the item''s own deliverable.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:m29y546p4sh77vbs2dv09gkp:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:m29y546p4sh77vbs2dv09gkp-ideation-1
              briefing:
                id: briefing:m29y546p4sh77vbs2dv09gkp:ideation:attempt-1:revision-1
                digest: sha256:9a5e972f1052e45263bb9866fb6298fae584e5535f245e054cb20a44791645ff
                room-ref: ./dev-51-behaviour-assertions-for-contract-pins/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:m29y546p4sh77vbs2dv09gkp:ideation:1
                briefing: briefing:m29y546p4sh77vbs2dv09gkp:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-02T14:57:58.773435Z"
                decision: approve
                reason: 'Captain approved the DEV-51 shape: 31 pin sites tiered, tier-2 budget checkpoint at three measured cases against a cap of 8, own equivalence instrument named.'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:m29y546p4sh77vbs2dv09gkp:validation
          stage: validation
          attempts:
            - id: gate-attempt:m29y546p4sh77vbs2dv09gkp-validation-1
              briefing:
                id: briefing:m29y546p4sh77vbs2dv09gkp:validation:attempt-1:revision-1
                digest: sha256:48e8738f6cb964ea57f5fd311a8ca40420641d96c5ff217a2270abbfda6e13a8
                room-ref: ./dev-51-behaviour-assertions-for-contract-pins/review/validation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-09-02T16:25:34.919867Z"
                reason: Candidate 99a0c826 conflicts with origin/main (#340) in scripts/kc-dev-flow-contract-test.py; delivery readiness FAILED; a merge is a code-changing repair that changes the exact revision.
---

## The problem

`scripts/kc-dev-flow-contract-test.py` guards the kc-dev-flow contracts largely by wording. Nineteen `phrase in normalized_<document>` loop sites pin sentences in `kernel.md`, `continue-dev-flow/SKILL.md`, the package README, the workflow README, adopter and migration documents, and others (count taken 2026-09-02 by grepping the require lines). A slimming deletes wording by definition, so this instrument reddens when a sentence is shortened and stays green when a rule is dropped but its pinned words survive elsewhere. It cannot distinguish "rule kept, said shorter" from "rule removed". Mutation-style checks exist in the file, but for guard code paths, not for the prose rules the pins cover.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: Bounded real use by this repository's own CI; the change touches only repo-local test files and behavior-diff cases, no adopter-visible contract, release, or rollback obligation, and iteration is expected as pin groups are converted in batches.
  route: [shape, build, verify-deliver]
  obligations:
    architecture: [Two-tier instrument model — deterministic assertions on loader, guard, and close-guard observable outputs for enforced rules, sampled behavior-diff cases for agent-only prose rules, wording-only pins recorded with a reason]
    implementation: [Replace pins in scripts/kc-dev-flow-contract-test.py per tier without removing any pin before its replacement reddened on the same removal, keep the multi-profile gate and ablation green, measure and record per-case behavior-diff cost]
    testing: [Every tier-1 replacement has a recorded mutation run, every tier-2 case has with-and-without runs plus one deliberately removed rule it flags, the old assertion is run against each mutation its replacement claims to cover before the old one is removed]
  scope_boundary: No contract slimming, no generic without-it harness, no model-backed check in CI, no change to loader or guard behaviour, no pin deleted without a reddened replacement.
  semantics_unchanged: true
  equivalence_instrument: 'DEV-51''s own Mutation replay table (cycles 1-2): apply the recorded mechanism patch to profile-contract-loader.py, engage-reconcile.py, poc-close-guard.py, or linear-admission.py, run the owning suite (or the full contract test where the rule surfaces only there), observe the new assertion redden naming the rule, git checkout -- restore, observe green; validation independently replayed 4 of 12 triples, one per mechanism, at candidate 99a0c826.'
  equivalence_instrument_failure: 'engage-reconcile.py L164 return 1 if result["status"]=="delta" else 0 mutated to return 0 -> engage-reconcile.test.py exit 1, "membership delta returned 0"; poc-close-guard.py L120 heading "POC outcome" mutated to "POC outcome MUTATED" -> poc-close-guard.test.py exit 1, CloseError "work item must contain exactly one POC outcome MUTATED"; linear-admission.py L402 --expected-source prefixed "MUTATED-" -> kc-dev-flow-contract-test.py exit 1, "clean Linear admission failed: linear admission: planning comparator returned invalid output"; profile-contract-loader.py validate_admission_brief() given an early return "0"*64 before its checks -> profile-contract-loader.test.py exit 1, "admission accepted missing-the-problem: {...}"; all four reverted, reran green.'
  decision:
    authority: person:captain
    at: 2026-09-02T14:07:13Z
```

## Accepted outcome

The contract test grades the behaviour a rule produces, at two tiers, and every replacement has been seen to fail before the pin it replaces is removed.

* Tier 1, deterministic: a rule that the profile loader, admission guard, POC close guard, or contract test itself enforces is asserted through that mechanism's observable output (loader field, refusal message, exit code), not through the sentence that describes it.
* Tier 2, sampled: a rule only an agent interprets gets one recorded `behavior-diff` case (the same task run with and without the rule) or is recorded as wording-only with the reason it cannot be sampled.
* Proof per replacement: remove the rule, observe the new assertion or case redden and name the rule, restore it, observe green. A pin whose replacement was not seen to fail on the same removal stays in place.

## Non-goals

- Do not slim any contract in this item. The knife is a later item.
- Do not add a generic without-it harness or a model-backed check to CI; the per-case cost of `behavior-diff` is unmeasured until this item measures it.
- Do not change the behaviour of the loader, guards, or close guard.
- Do not delete a pin whose replacement has not reddened on the same deliberate removal.
- Do not lower coverage: an old assertion is run against each mutation its replacement claims to cover before the old one is removed.

## Acceptance criteria

- **AC-1** A table lists every phrase-pin loop site with its tier (1, 2, or wording-only) and one reason each.
- **AC-2** Every tier-1 replacement has a recorded mutation run: rule removed, new assertion fails naming the rule, rule restored, assertion passes.
- **AC-3** Every tier-2 candidate rule is recorded as wording-only with its reason, carrying the evidence of the three probe cases run at build (both variants took the same action; divergence appeared only in citation and reasoning cost), and its pin stays in place; no behavior-diff case is required to redden. Captain ruling at the tier-2 checkpoint, 2026-09-02.
- **AC-4** For each removed pin, the old assertion was run against the same mutation and its result recorded, so no regression the old check caught is lost without being named.
- **AC-5** `python3 scripts/kc-dev-flow-contract-test.py` passes on the unchanged tree after the change, and the count of remaining wording-only pins is recorded with a reason each.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Also route back when a tier-2 case cannot be made to redden for a rule the slimming intends to touch, or when the measured per-case cost makes sampling every touched rule unaffordable; either is a planning delta, not a reason to keep the wording pin and call it behaviour.

## Measurement

Shape measured the pin inventory against `f47fd8ca`: **31 positive phrase-pin loop sites, one `require` line each, 245 pinned phrases**, occupying 369 of 1903 lines — see `## Pin inventory` and the correction to the recorded "20 loop sites". The AC-5 baseline is `kc-dev-flow contract: PASS`, exit `0`, 50.7 s in a clean clone. The `where it touches` table and stop numbers are recorded. Build records per-case behavior-diff cost and the count of remaining wording-only pins.

## Shape

Delivery base: `f47fd8ca` (`main`, also the shape worktree HEAD). Every count
below was taken from that tree by AST walk over
`scripts/kc-dev-flow-contract-test.py` (1903 lines), not by grep.

### Count correction against the recorded numbers

The item recorded "Nineteen loop sites" in `## The problem` and "20 loop sites,
31 require lines" in `## Measurement`. The measured figure is **31 positive
phrase-pin loop sites, one `require` line each, 245 pinned phrases**. The
recorded 19 and 20 are wrong; 31 require lines is right. The sites occupy 369 of
1903 lines (19.4%).

Out of scope by construction: the seven **negative**-pin loops
(`for retired/forbidden/stale ... not in ...` at L482-495, L491-495, L791-800,
L817-831, L1153-1158, L1183-1190, L1302-1308). A slimming deletes words, so a
`not in` assertion cannot redden on the failure this item exists to catch. They
stay as they are. AC-1's "every phrase-pin loop site" means the 31 positive
sites.

### Conditional reference predicates

| Trigger | Fires | Reason |
|---|---|---|
| `brownfield_capability_change` | **true** | The item replaces and removes existing assertions in existing code. Receipt below. |
| `multi_slice_required` | false | One integrated slice: one changed test surface, one PR. Converting sites in batches is sequencing inside that slice, and the batch limit is a stop number, not a second deliverable. |
| `retained_document_change` | false | No contract, README, runbook, or ROADMAP text changes (non-goal). Mutation replay records live in this work item, where a changing fact needs no prose edit. |
| `project_context_claim_may_change` | false | `ARCHITECTURE.md` names `kc-dev-flow-contract-test.py` only as one entry in its list of repo-level CI scripts. The item adds and removes no script, and changes nothing CI runs. |

```yaml
reverse_recovery:
  trigger: replace 31 phrase-pin assertions with behaviour assertions, and remove each pin after its replacement reddens
  boundary: scripts/kc-dev-flow-contract-test.py and the mechanism test suites it would delegate to (kc-dev-flow/scripts/*.test.py); no contract prose in scope
  layers:
    - surface: 31 positive phrase-pin loop sites
      location: scripts/kc-dev-flow-contract-test.py, the 31 sites keyed by `require` message prefix in `## Pin inventory` (L694-L1584 at f47fd8ca only)
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: green when a rule is dropped and its words survive elsewhere; red when a kept rule is shortened — the failure named in `## The problem`
      disproof_hook: delete a kernel rule's sentence, keep its words in another paragraph, run `python3 scripts/kc-dev-flow-contract-test.py`
    - surface: mechanism assertions on the loader, comparator, and close guard
      location: kc-dev-flow/scripts/profile-contract-loader.test.py (2062 lines, 102 `require`), engage-reconcile.test.py (370, 10), poc-close-guard.test.py (282, 13)
      completeness: WORKING
      need: REQUIRED
      evidence: 125 mechanism-level assertions already run in CI via scripts/kc-dev-flow-contract-test.py; the tier-1 route extends these rather than adding a parallel instrument
      disproof_hook: python3 kc-dev-flow/scripts/profile-contract-loader.test.py after mutating the loader
    - surface: agent-behaviour sampling for prose-only rules
      location: MISSING in this repo; runner installed at ~/.claude/plugins/cache/engram/behavior-diff/0.1.0
      completeness: WORKING_UNIT_UNPROVEN
      need: REQUIRED
      evidence: runner exists and has a documented flow-diff output; never exercised against a kc-dev-flow contract, so its RED behaviour here is unproved
      disproof_hook: behavior-diff.sh --file kc-dev-flow/references/kernel.md --task <case> --fast, with one rule deleted uncommitted
    - surface: replayable mutation record
      location: MISSING
      need: REQUIRED
      evidence: AC-2/AC-3/AC-4 all require validation to re-run a mutation, not re-read a claim; nothing in the repo stores the triple
      disproof_hook: ask validation to reproduce one recorded redden without a stored patch and command
  decision: use
```

`use` for tier 1 — the mechanism suites are WORKING and the Pilot base forbids
duplicating them; the item deletes a pin and cites (or extends) the existing
assertion. `build` only for the two MISSING surfaces, and both are records, not
frameworks: the replay table below and the tier-2 case entries. The non-goal
"no generic without-it harness" is what keeps them a list.

### Accepted journey

1. **OBSERVED** — `python3 scripts/kc-dev-flow-contract-test.py` in a clean
   local clone at `f47fd8ca` prints `kc-dev-flow contract: PASS`, exits `0`, and
   takes **50.7 s** wall-clock. That is the AC-5 baseline. It shells out to the
   mechanism suites: `profile-contract-loader.test.py` alone is 18.7 s and
   `engage-reconcile.test.py` 1.8 s, so a tier-1 mutation can be driven on the
   owning suite for seconds and confirmed on the full run once.
   Two environment facts build must respect, both observed:
   this shape worktree is **not** a valid baseline — the full run exits `1` in
   0.46 s on `retired control still shipped:
   kc-dev-flow/skills/setup-github-project-projection`, an empty leftover
   directory holding no tracked file, left by an earlier checkout; and a bare
   `git archive HEAD` export is not one either — a later sub-check needs a real
   git checkout and dies on a missing smoke-test `candidate.json`. Mutation runs
   go in a clean clone.
2. **OBSERVED** — `profile-contract-loader.py --work-item <this item> --format json`
   emits `loaded` = exactly `["kernel.md", "profiles/pilot-product-slice/base.md",
   "profiles/pilot-product-slice/shape.md"]` and `declared_receipts` =
   `["reverse_recovery","journey_slices","project_context"]`, which omits the
   `receipt: null` reference `retained-document-policy.md`. This stdout is the
   tier-1 observable for the loading and conditional-reference rules.
3. **OBSERVED** — `profile-contract-loader.py --validate-admission` adds
   `development_brief_sha256` to that JSON; the default run omits the field.
   That difference is the tier-1 observable for "explicit `--validate-admission`
   mode / default loading does not inspect acceptance headings".
4. **OBSERVED** — `engage-reconcile.py` exits `0` printing
   `{"added":[],"changed":[],"moved":[],"removed":[],"status":"clean"}`, exits
   `1` printing a classified delta (`"status":"delta"` with the added/removed
   sources), and exits `2` on invalid input with a message on stderr. Three exit
   codes, one JSON object: the tier-1 observable for every comparator rule.
5. **OBSERVED** — `linear-admission.py` with `LINEAR_API_KEY` and
   `CONDUCTOR_WORKSPACE_ID` unset refuses with
   `linear admission: workspace authentication is unavailable`. Its refusal
   messages are the tier-1 observable for admission rules, and L295 shows it
   invokes `engage-reconcile.py` mechanically — the comparator is not an
   agent-followed instruction.
6. **DESIGNED** — for each tier-1 rule, `git apply` a mutation patch against the
   named mechanism, run the owning suite, and record that the new assertion
   fails naming the rule. The old phrase pin is run against the same mutation
   and its result recorded; a tier-1 code mutation leaves the old pin **green**
   (it never watched code), which is the recorded non-regression, not a loss.
7. **DESIGNED** — for each tier-2 rule, delete the rule from its document as an
   *uncommitted* edit and run `behavior-diff.sh --file <doc> --task <case>`;
   `run-trial.sh` launches `claude -p --output-format stream-json` in isolated
   copies of the repo at HEAD (before) and HEAD-plus-that-one-file (after), and
   the flow diff is read for divergence. Here the old pin goes **red** on the
   same mutation and the case must also go red — both sides recorded.
8. **DESIGNED, unhappy** — flows come back identical. `behavior-diff`'s own
   SKILL forbids reading that as pass or fail; it is inconclusive. The task is
   redesigned at most twice, and the retries count against the cost budget. A
   third inconclusive result makes the rule wording-only with "no task reached
   the decision point at the measured cost" as its reason.
9. **DESIGNED, unhappy** — the runner errors (`jq` missing, `claude` CLI
   missing, file not tracked at HEAD, no uncommitted change). Reported as a
   machine-dependency failure, not as evidence about the rule.
10. **DESIGNED, unhappy** — measured per-case cost exceeds the threshold below.
    Build stops after the third measured case and returns a planning delta; it
    does not convert the remaining tier-2 rules on an unaffordable instrument,
    and it does not silently keep a wording pin and call it behaviour.

### Semantics and the equivalence instrument

`semantics_unchanged: true` holds: the item changes no command grammar, no
stored format, no authority, and no runtime behaviour of the loader, the
guards, or the close guard. The only observable change is which sentence a CI
failure prints.

The equivalence instrument for that declaration is **the replaced suite plus its
own mutation proof** — there is no second instrument, because the suite is the
deliverable. Concretely, the declaration is falsified if either holds:

- **F1** — a mutation the old pin caught produces no failure from the new
  instrument. The two sides are graded by different instruments, so the evidence
  is asymmetric and validation must see both halves: **old side** — `git apply`
  the recorded deletion patch in a clean clone at `f47fd8ca` and run
  `python3 scripts/kc-dev-flow-contract-test.py`; the pin is red, message
  recorded. **New side** — a tier-2 case is a `behavior-diff` run, not a suite
  assertion, so the same patch on the item's head leaves the contract test
  **green** by design. The case's redness is evidenced either by replaying it
  (`behavior-diff.sh --file <doc> --task <recorded task> --fast`, 2 headless
  runs) or by the flow-diff verdict excerpt copied into the case record. The
  runner writes to `${BEHAVIOR_DIFF_HOME:-~/.behavior-diff}/runs/` on the
  builder's machine, which is neither the repository nor this work item — so
  every case record carries the excerpt, and replay is the fallback, not the
  primary evidence path.
- **F2** — the tier-1 replacement asserts nothing the mechanism enforces. Evidence
  validation must see: `git apply` the tier-1 patch, run the owning suite, read
  the failure message, confirm it names the rule; `git apply -R`, rerun, green.

Every recorded entry is therefore a replayable triple — patch, command, expected
failure message — stored in this work item so validation exercises it rather
than re-reading a claim.

### Pin inventory

Tier 1 = a loader, guard, or close-guard mechanism refuses the violation even if
no agent ever read the sentence. Tier 2 = only an agent's reading enforces it.
Wording-only = the document sits on no agent's decision path, so no case can be
designed. `split` means the site's pins divide across two tiers.

**The site key is the `require` failure-message prefix, not the line number.**
Build edits this file top to bottom, so every L-number below is true only of
`f47fd8ca` and is stale after the first conversion. The message prefix is unique
per site and greppable, and it is what a replay record and the
`reverse_recovery` receipt cite.

| Site key | Pins | Document | Rule the pin protects | Tier | Observable / case / reason |
|---|---|---|---|---|---|
| `kernel omits completion invariant`<br>L694-706 | 10 | kernel.md | Completion invariant: goal sufficiency + minimal necessity on one candidate | split | T2 for the working agent's without-it observation; the "First Officer confirms both before terminalization" half is an FO/ensign **handoff** rule needing the duo cycle — out of this item, recorded wording-only |
| `kernel omits subtraction rule`<br>L711-722 | 9 | kernel.md | Implementation-exit subtraction and comment-necessity pass | 2 | Case: agent finishes a change with a restating comment; does it report cut blocks and kept candidates? Kernel loads at every stage — cheapest case, run first |
| `audit omits unified need vocabulary`<br>L726-739 | 5 | reverse-recovery-audit.md | Unified need vocabulary (`REQUIRED`, `NO_OBSERVED_CONSUMER`, search vs execution tier) | 2 | Case must first make the trigger fire, then reach the classification — two hops, higher design cost |
| `kernel omits provider-neutral planning boundary`<br>L746-760 | 12 | kernel.md | Provider-neutral planning authority split; no projector; no auto-write | split | T1: comparator read-only behaviour = `engage-reconcile.py` exit 0/1/2 (OBSERVED). T2: the authority-split and no-projector prose |
| `continuation omits provider engage behavior`<br>L764-776 | 7 | continue-dev-flow/SKILL.md | Provider engage behaviour: exact source, shared window/outcome, `status: clean`, exit 1/2 | 1 | `engage-reconcile.py` stdout JSON + exit code (OBSERVED) |
| `kernel omits brief boundary`<br>L777-790 | 11 | kernel.md | Brief boundary, Planning Receipt complete-or-absent, structured planning delta shape | 2 | Case: agent is handed a partial receipt and must stop with a delta rather than proceed |
| `kernel backlog exit bar is missing`<br>L801-807 | 4 | kernel.md | Backlog exit bar: item leaves `backlog` only after the brief is admitted | 1 | `--validate-admission` emits `development_brief_sha256` (OBSERVED); build confirms the refusal path on a brief-less item |
| `{relative} omits the v4 POC contract`<br>L842-875 | 21 | README, choose-work-profile, continue-dev-flow, poc base | v4 POC contract fields and close duties | split | T1: `poc_*` receipt fields against the loader's `receipt_schema` and `poc-close-guard.py`. T2: the "do not dispatch a validation worker" duties |
| `continuation omits provider delivery linkage`<br>L894-903 | 4 | continue-dev-flow/SKILL.md | Provider delivery linkage: one ephemeral binding, stop before push | 2 | Case at the delivery decision point; build checks first whether `pr-review-handoff.py` already refuses, which would move it to T1 |
| `PR delivery omits provider linkage`<br>L907-916 | 4 | pr-delivery.md | `delivery.branch` / `delivery.close_line` / reconciled source | 2 | Conditional reference; case must make `pr_delivery_selected` true |
| `adopter omits static Local Profile marker`<br>L1094-1095 | 2 | adopt-dev-flow/SKILL.md | Static Local Profile marker pair | 1 | Loader reads only between `gate.LOCAL_PROFILE_START/END`; mutation = put a directive outside the markers and assert the loader ignores it |
| `chooser is missing`<br>L1105-1113 | 6 | choose-work-profile/SKILL.md | v3 receipt schema, route names, structured Ask UI | split | T1: `receipt_schema` and route resolution in loader JSON. T2: "structured Ask UI" |
| `adopter omits scheduling binding`<br>L1120-1147 | 25 | adopt-dev-flow/SKILL.md | Adoption procedure: receipt classification, comparator exercise, provenance | 2 | Largest single site; several distinct rules. Case cost dominated by having to reach adoption in a trial |
| `v4 migration omits`<br>L1159-1170 | 9 | MIGRATION.md | v4 migration steps | wording-only | Human migration document. Not in the loader's emitted set and on no agent's decision path — nothing to sample |
| `3.x migration omits standalone planning branch`<br>L1171-1182 | 6 | MIGRATION.md (3.x section) | Standalone planning branch during 3.x→4.x | wording-only | Same reason |
| `continuation is missing`<br>L1197-1211 | 12 | continue-dev-flow/SKILL.md | Loader invocation contract: emits core + base + stage only, exact work item, `A link is not activation` | 1 | `loaded` is exactly three paths and `declared_receipts` is the declared set (OBSERVED) |
| `continuation authority resolution omits`<br>L1218-1220 | 3 | continue-dev-flow/SKILL.md | Authority resolution order: brief, then receipt, then execution state | 2 | The surrounding order assertion (L1221-1225) survives; only the phrase membership is replaced by a case that puts the agent at a state read with an unclassified receipt |
| `continuation planning disambiguation omits`<br>L1226-1253 | 25 | continue-dev-flow/SKILL.md | Planning disambiguation: which branch runs the comparator, delta handling | split | T1: `--expected-*` flags, exit codes, `status: clean`, refuse-truncated. T2: branch selection and "do not promote the snapshot into planning authority" |
| `continuation omits doc trigger`<br>L1254-1260 | 4 | continue-dev-flow/SKILL.md | Conditional doc triggers; `receipt: null` creates no receipt | 1 | `declared_receipts` omits the `receipt: null` reference (OBSERVED) |
| `adopter omits migration rule`<br>L1269-1275 | 4 | adopt-dev-flow/SKILL.md | Migration rule for older Captain choices and terminal-state mapping | 2 | Case at the adoption decision point |
| `rationale omits`<br>L1287-1301 | 12 | RATIONALE.md | Why the flow is shaped this way | wording-only | Rationale prose read by people. No agent loads it at any decision point |
| `Chief Engineer is missing`<br>L1314-1319 | 3 | chief-engineer/SKILL.md | Next smallest step; `proceed \| adjust \| escalate`; no gate authority | 2 | Case: ask the Chief Engineer for a call that invites a state mutation; does it stay advisory? |
| `Science Officer is missing`<br>L1320-1326 | 4 | science-officer/SKILL.md | Risk trigger; recommendation set; not a veto; do not read the legacy alias | 2 | Same shape as above |
| `self-adoption omits Linear cutover boundary`<br>L1381-1401 | 18 | docs/dev/README.md | Linear cutover boundary, comparator table, env-var scoping, dispatch envelope | split | T1: `--expected-*`, `--state-revision`, envelope schema, and the process-env refusal `workspace authentication is unavailable` (OBSERVED). Wording-only: "not an iteration authority", a repo policy statement with no mechanism |
| `self-adoption misstates brief authority`<br>L1407-1413 | 4 | docs/dev/README.md | Admission snapshot is not a second accepted-goal authority | 2 | This text is the ideation stage definition the FO serves to a worker; case puts the worker at the snapshot/brief conflict |
| `manual admission Issue body omits`<br>L1436-1440 | 2 | docs/dev/README.md (Issue template) | Template starts at the problem; carries a planning delta | wording-only | The template's structure is already asserted non-loop at L1416-L1435 (heading set, order, `startswith`); the two remaining phrases are prose a human fills in. Build re-checks whether a template parse covers them before this is final |
| `Roadmap is not thin enough for provider-neutral planning`<br>L1446-1450 | 2 | docs/dev/ROADMAP.md | Roadmap headings are execution groups, not planning windows | wording-only | A hygiene statement about a human-maintained planning file; no agent reads ROADMAP at a decision point |
| `package README omits the release-proof boundary`<br>L1517-1525 | 3 | kc-dev-flow/README.md | Candidate receipt binds its exact package snapshot | 1 | `scripts/kc-dev-flow-published-tag-smoke.py` enforces it; build names the receipt field it asserts, else this drops to wording-only |
| `package README omits admission boundary`<br>L1541-1546 | 3 | kc-dev-flow/README.md | `--validate-admission` is explicit; default does not inspect acceptance headings | 1 | Presence/absence of `development_brief_sha256` in loader JSON (OBSERVED) |
| `package README omits mod boundary`<br>L1557-1570 | 8 | kc-dev-flow/README.md | Everything under `references/` is conditional; selecting a profile activates none of it | 1 | `loaded` list and `declared_receipts` (OBSERVED) |
| `validation runbook omits`<br>L1576-1584 | 3 | docs/dev/runbooks/validation-evidence.md | POC never loads it; smallest evidence set that can fail | 2 | The validation ensign reads this runbook; case puts it at evidence selection |

Totals: **8 tier 1, 5 split, 13 tier 2, 5 wording-only = 31.** Counting split
halves, there are **13 tier-1 rule groups and 18 tier-2 candidate rules**.

### Tier-2 method

**Designing a case from a rule.** Take the rule's prohibition or duty and write
the request that arrives one step before the agent would violate it, with the
expected behaviour absent from the task text. When the rule fires mid-task,
start the task at the decision point and put the prior work in the tree. One
rule per case; a case that needs two rules removed to diverge is not evidence
about either.

**RED condition.** Delete exactly that one rule from its document as an
uncommitted edit — which is also what the runner requires (it refuses when the
file is unchanged or untracked at HEAD) — and run the case. The case is RED when
the flow diff shows the after-variant taking the step the rule forbids and the
before-variant not taking it, and the case names the rule in its recorded
finding. Identical flows are inconclusive, never a pass.

**With-and-without recording.** Per case record: the rule id, the document, the
deletion patch, the `--task` text verbatim, the runner invocation, the run
directory under `${BEHAVIOR_DIFF_HOME:-~/.behavior-diff}/runs/`, the flow-diff
verdict for each variant, and the result of running the **old phrase pin**
against the same deletion. Both sides go in the work item; a case with only the
after side is not AC-4 evidence.

**Cost measurement.** Per case, from the `result` line of each trial's
`trace.jsonl`: `duration_ms` and the `usage` token counts, summed across trials,
plus the trial count and the number of inconclusive redesign reruns. Wall-clock
of the whole `behavior-diff.sh` invocation is recorded separately because the
runner serialises trials. **`total_cost_usd` is not the unit** — it is an imputed
figure, not a billed one, and a threshold denominated in it would be a threshold
on a number nobody is charged. `--fast` (1 trial per variant, 2 headless runs)
for the probe; 3 trials per variant (6 runs) for a recorded proof.

**Three constraints the runner imposes on task design, all observed in
`behavior-diff.sh` and `run-trial.sh`.** First, each variant is
`git -C <repo> archive HEAD | tar -x` into a scratch copy, and
`docs/dev/.spacedock-state` is gitignored (`.gitignore:29`) — confirmed by
`git archive HEAD | tar -t`, which lists zero entries under it. **A trial copy
has no work item and no state checkout**, so any case needing one must carry a
tracked fixture in the task. Second, the trial's tool allowlist has no `Write`
or `Edit`; the agent reads and runs Bash only, and the flow diff is derived from
the commands it ran plus its final answer. A rule whose violation is only
visible as an edit cannot be sampled this way — it has to be recast so the
divergence appears in what the agent runs or says. Third, `kernel.md` is read
only if the task routes the agent through the loader (for example, "run
`kc-dev-flow/scripts/profile-contract-loader.py --work-item <fixture>` and act on
the contract it loads"); a task that never forces that read yields identical
flows for a reason that is not about the rule.

**Machine dependency, declared.** The runner is not in this repository. It is
`~/.claude/plugins/cache/engram/behavior-diff/0.1.0/skills/behavior-diff/scripts/behavior-diff.sh`
from the `engram` marketplace, and it needs `jq` and the `claude` CLI on PATH.
Build records the plugin version it used. A teammate without that plugin cannot
reproduce a tier-2 case, and that is a stated limit of the tier-2 evidence, not
a silent assumption. Nothing tier-2 runs in CI.

**Affordability threshold and route-back.** Proposed cap, gate-adjustable:
**45 minutes median wall-clock and 6 headless runs per recorded case**, and
**8 recorded cases** for this item. Anchor: 8 × 6 = 48 headless Sonnet runs,
which fits one background build session; the number is proposed, not measured,
and the first three cases replace it with a measurement.

The inventory found 18 tier-2 candidate rules against a cap of 8. That gap is
deliberate and is the item's first reportable fact. Build therefore measures
**three cases first** — L711-722 (kernel, always loaded, cheapest), L777-790
(kernel, planning delta), L1314-1319 (chief-engineer, a small separate skill) —
then stops and reports the measured median against the cap with the projection
for the remaining 15. **That probe is biased low and the report says so**: all
three are single-role rules in documents a plain `claude -p` reaches with no
fixture, while most of the remaining 15 sit in `continue-dev-flow/SKILL.md` and
`adopt-dev-flow/SKILL.md` at First-Officer and adoption decision points that
need a tracked work item, a workflow directory, and possibly a spacedock binary
inside the trial copy. The Captain's checkpoint choice must not be made on the
cheap-class median alone. The Captain then chooses: raise the cap, narrow tier-2
sampling to `kernel.md` rules only (5 sites, the one document every working
stage loads), or route back. Build does not convert the remaining tier-2 rules
before that choice, and does not reclassify an unaffordable rule as wording-only
to fit — the route-back condition already forbids it.

### Where it touches

| Path | Lines now | Lines after |
|---|---|---|
| `scripts/kc-dev-flow-contract-test.py` | 1903 | ~1750 (31 sites spanning 369 lines shrink to tier-1 assertions; tier-2 rules leave the file entirely) |
| `kc-dev-flow/scripts/profile-contract-loader.test.py` | 2062 | ~2110 (new assertions on `loaded`, `declared_receipts`, `--validate-admission`, marker-bounded reading) |
| `kc-dev-flow/scripts/engage-reconcile.test.py` | 370 | ~395 (exit-code and `status: clean` assertions the comparator pins move to) |
| `kc-dev-flow/scripts/poc-close-guard.test.py` | 282 | ~300 (POC close duties from L842-875) |
| `docs/dev/.spacedock-state/dev-51-…md` (this item) | 98 + shape | + the mutation replay table and tier-2 case records |

Reconciled against the journey both ways: journey steps 1-5 exercise the four
repo files above and nothing else; step 7 touches no repo file (the runner
copies the tree), and its records land in the work item, which is why the work
item is in the table. No file in the table is absent from the journey.

`ARCHITECTURE.md` is deliberately absent: the item adds and removes no CI
script, so its script list stays true.

### Stop numbers

Measured as the diff against delivery base `f47fd8ca`.

- **Changed files: stop at 5.** Four are expected; a fifth means the change is
  reaching into contract prose or a new harness, both non-goals.
- **Changed lines: stop at 600** (added + deleted). The 31 sites occupy 369
  lines; 600 leaves room for tier-1 replacements and no room for a framework.
- **Runaway area: tier-2 case design.** Not the script. The cost lives in
  drafting `--task` texts and re-running inconclusive cases, and it is unbounded
  in principle. Hard stop: **three measured cases**, then report the median and
  the projection before converting a fourth.

All three are stop conditions. Crossing one reports the observed count and waits
for a Captain choice; it passes and fails nothing.

## Stage Report: ideation

- DONE: Inventory every phrase-pin loop site in scripts/kc-dev-flow-contract-test.py at the delivery base (20 sites, 31 require lines at f47fd8ca) with its tier — 1 (a mechanism in the loader, admission guard, or close guard enforces it: name the observable output), 2 (agent-only prose: name the behavior-diff case), or wording-only (name why it cannot be sampled) — and the rule each pin protects.
  `## Pin inventory` — 31 rows, one per site, each with pins, document, rule, tier, and observable/case/reason. The recorded "20 sites" is wrong: AST walk over the base tree finds **31** positive loop sites (one `require` each, 245 pinned phrases); the correction and the seven excluded negative-pin loops are recorded in `## Count correction against the recorded numbers`.
- DONE: Deliver the journey statement, `where it touches` table, and stop numbers against the delivery base, and name this item's own equivalence instrument for its `semantics_unchanged: true` declaration (the replaced suite plus its mutation proof) together with the evidence validation will need to see it fail.
  `## Accepted journey` (10 steps, 5 OBSERVED / 5 DESIGNED, unhappy paths in the same terms), `## Where it touches` (5 rows, reconciled both ways), `## Stop numbers` (5 files / 600 lines / three measured cases), `## Semantics and the equivalence instrument` (F1 and F2, each a replayable patch-command-message triple).
- DONE: Specify the tier-2 method: how a behavior-diff case is designed from a rule, the RED condition (one deliberately removed rule the case flags), the with-and-without recording, the per-case cost measurement, and the affordability threshold at which the item routes back.
  `## Tier-2 method` — one rule per case, uncommitted single-rule deletion as the RED condition, both-sides recording including the old pin's result on the same mutation, cost in `duration_ms` + `usage` tokens (explicitly not `total_cost_usd`, which is imputed), cap of 45 min / 6 runs per case and 8 cases, and a measure-three-then-report stop.
- DONE: Conditional shape references resolved
  `brownfield_capability_change` fires — `reverse_recovery` receipt recorded with four layers and decision `use`. The other three predicates are recorded false with a reason each.

### Summary

Five journey steps were exercised rather than asserted: the contract test passes in a clean clone at `f47fd8ca` (exit `0`, 50.7 s — the AC-5 baseline), `engage-reconcile.py` was driven to exit `0`/`1`/`2` with its JSON, the loader was run to see `loaded` equal exactly three paths, `declared_receipts` omit the `receipt: null` reference, and `development_brief_sha256` appear only under `--validate-admission`, and `linear-admission.py` was run credential-less to see it refuse — those four outputs are what the 8 tier-1 and 5 split sites assert instead of wording.

Two facts the gate should rule on. The recorded pin count is wrong in both places the item states it (19 and 20) against a measured 31 sites / 245 phrases; and the inventory yields 18 tier-2 candidate rules against a proposed cap of 8 cases, which the shape does not resolve by reclassifying rules to fit — it measures three cases, declares that probe biased low, and puts the choice to the Captain, which is this item's own route-back condition firing as designed.

Three environment limits are recorded rather than assumed: this worktree is not a valid baseline (a stale empty `setup-github-project-projection` directory reddens the run in 0.46 s), a behavior-diff trial copy carries no work item because `docs/dev/.spacedock-state` is gitignored and absent from `git archive HEAD`, and the trial agent has no `Write`/`Edit` tool, so a rule whose violation is only visible as an edit cannot be sampled without recasting.

## Mutation replay table (tier-1, cycle 1)

Seven of the eight pure tier-1 sites converted. Each row is a replayable
triple — patch, command, expected failure message — plus the old pin's
result against the same mutation (isolated phrase check, since a mechanism
mutation exits `kc-dev-flow-contract-test.py` at the earlier `run()` call
before the pin's `require` line is ever reached; see `where it touches`).
Full patches and raw logs are in this dispatch's scratch notes, not
committed — the table below is the replayable record.

| Site key | Mechanism mutated | New instrument (command → failure) | Old pin on same mutation |
|---|---|---|---|
| `continuation omits provider engage behavior` | `engage-reconcile.py` L164: `return 1 if result["status"]=="delta" else 0` → `return 0` | `python3 kc-dev-flow/scripts/engage-reconcile.test.py` → exit 1, "engage reconcile test: membership delta returned 0" | GREEN (7/7 phrases still in continue-dev-flow/SKILL.md; never watched code) |
| `kernel backlog exit bar is missing` | `profile-contract-loader.py validate_admission_brief()`: insert `return "0"*64` before all checks | `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → exit 1, "admission accepted missing-the-problem: {...}" | GREEN (4/4 phrases still in kernel.md) |
| `adopter omits static Local Profile marker` | `profile-contract-loader.py` L183: `end = text.index(LOCAL_PROFILE_END)` → `end = len(text)` (new assertion added first — see below, gap found) | `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → exit 1, uncaught `ContractError: Local Profile duplicates binding 'Local mods'` | GREEN (both markers still in adopt-dev-flow/SKILL.md) — correction: inventory's paraphrased pin text ("start/end marker pair") does not match the real check, which compares the two `LOCAL_PROFILE_START/END` constants directly |
| `continuation is missing` + `package README omits mod boundary` (shared mechanism) | `profile-contract-loader.py` `paths` list: append a duplicate `root/"kernel.md"` entry | `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → exit 1, "wrong loaded paths: [..., 'kernel.md']" (existing L642-648 assertion) | GREEN (12/12 continue-dev-flow phrases; 8/8 README phrases) |
| `package README omits admission boundary` | `profile-contract-loader.py` L685: `if validate_admission` → `if True` (new assertion added first — see below, gap found) | `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → exit 1, "default loading (no --validate-admission) inspected acceptance headings" | GREEN (3/3 phrases still in kc-dev-flow/README.md) |
| `continuation omits doc trigger` | `check_conditional_references()`: `if isinstance(receipt, str): declared_receipts.append(receipt)` → `declared_receipts.append(str(receipt))` | `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → exit 1, "declared_receipts leaked a null receipt... : ['stage_receipt', 'None']" (existing L1290-1305 isolation test) | GREEN (4/4 phrases still in continue-dev-flow/SKILL.md) |

Every mutation was reverted after its cycle; `profile-contract-loader.test.py`,
`engage-reconcile.test.py`, and the full `kc-dev-flow-contract-test.py` (both
plain and `--ablation-check`) all pass at the candidate (below).

**Coverage gaps found and closed** (2 of 7 groups needed a net-new mechanism
assertion; the other 5 cited existing coverage as the shape's `use` decision
expected):

- `adopter omits static Local Profile marker`: no prior test proved content
  outside the marker pair is ignored. Added a decoy fixture in
  `profile-contract-loader.test.py` (after L1455) asserting
  `MODULE.read_local_profile` on a copy with a colliding `| Local mods |` row
  placed after the end marker still returns the inside-marker value.
- `package README omits admission boundary`: prior coverage only proved
  `development_brief_sha256` is present WITH `--validate-admission`, never
  proved it is absent WITHOUT the flag. Added a default-mode loader run on
  the same canonical-admission item (after L202) asserting the field's
  absence.

Both additions were confirmed passing on the unmutated tree before their
mutation cycle ran (AC-2's "assertion fails naming the rule... rule
restored" sequence, not written and mutated in the same step).

## Tier-1 groups not converted this cycle

Checklist item 1 ("replace the tier-1 and split pin sites") is **partial**:
7 of 8 pure tier-1 groups converted; the 5 split sites' tier-1 halves are
untouched. Reason: each remaining group needs its own mutation-verify cycle
against a mechanism not yet exercised in this dispatch (`poc-close-guard.py`,
`linear-admission.py`, or additional `engage-reconcile.py` flag paths), and
continuing past 7 groups risked rushed, unverified edits — the non-goal this
item forbids ("do not delete a pin whose replacement has not reddened").
Every pin below stays in place, unmodified:

| Site key | Reason not converted |
|---|---|
| `kernel omits provider-neutral planning boundary` (split, T1 half) | Not run: `engage-reconcile.py` exit 0/1/2 mutation cycle not attempted this dispatch |
| `{relative} omits the v4 POC contract` (split, T1 half) | Not run: `poc_*` receipt fields vs `poc-close-guard.py` mutation cycle not attempted |
| `chooser is missing` (split, T1 half) | Not run: `receipt_schema`/route-resolution mutation cycle not attempted |
| `continuation planning disambiguation omits` (split, T1 half) | Not run: `--expected-*` flags / exit codes / refuse-truncated mutation cycle not attempted |
| `self-adoption omits Linear cutover boundary` (split, T1 half) | Not run: `--expected-*`/`--state-revision`/`linear-admission.py` refusal mutation cycle not attempted |
| `package README omits the release-proof boundary` (pure T1) | Deferred by the shape itself pending the smoke-test receipt-field investigation ("build names the receipt field it asserts, else this drops to wording-only"); not investigated this dispatch |
| `continuation omits provider delivery linkage` (T2, deferred classification) | Shape asked build to check whether `pr-review-handoff.py` already refuses (which would move it to T1); not checked this dispatch |
| `manual admission Issue body omits` (wording-only, deferred confirmation) | Shape asked build to re-check whether the existing template-parse assertion covers the two remaining phrases; not checked this dispatch |

Remaining wording-only pins: **5**, unchanged from the inventory
(`v4 migration omits`, `3.x migration omits standalone planning branch`,
`rationale omits`, `manual admission Issue body omits` pending the check
above, `Roadmap is not thin enough for provider-neutral planning`).

## F1/F2 equivalence evidence (this cycle)

- **F2** (tier-1 replacement asserts nothing the mechanism enforces): disproved
  for all 7 converted groups — the mutation replay table above is exactly
  the required patch → owning-suite-red-naming-the-rule → `git apply -R` →
  green sequence, for each.
- **F1** (a mutation the old pin caught produces no failure from the new
  instrument): not applicable to tier-1 groups (F1 is the tier-2/behavior-diff
  half of the equivalence instrument); see the tier-2 checkpoint below for the
  tier-2 side of F1.

## Tier-2 checkpoint: three measured cases, then stop

Per the shape's hard stop, three cases were run and no further tier-2 rule
was converted. All three used **one deviation from the shape's suggested
method**, recorded once here and applying to all three: the task instructs
the agent to `Read <file> in full` directly rather than routing it through
`profile-contract-loader.py --work-item <fixture>`. A loader-routed fixture
would need a sixth tracked file (breaching the 5-file stop) or reuse of a
`.spacedock-state` entity (impossible — gitignored, absent from the trial's
`git archive HEAD` per the shape's own observed constraint). Rule presence
is still the only variable between variants, so the A/B stays clean, but
this is a floor of a floor: a real agent reaches kernel.md through the
loader at a decision point mid-task, not via a direct instruction to read
it. This is a further low-bias factor beyond the shape's stated one (cheap
single-role documents, no fixture needed).

| Case | Rule (deleted sentence) | Runner | Result |
|---|---|---|---|
| 1 | `kernel omits subtraction rule` — "A comment that earns its place still passes a necessity test: keep each fact... cut restatement of adjacent code" | `behavior-diff.sh --file kernel.md --fast` | **Inconclusive by action** (both variants: "Cut"). Citation source shifted: before quotes the deleted sentence verbatim; after substitutes a different kernel.md rule (Completion invariant) plus the repo's `CLAUDE.md` comment rule. |
| 2 | `kernel omits brief boundary` — "A Planning Receipt is optional and must be complete or absent: a partial Planning Receipt is invalid" | `behavior-diff.sh --file kernel.md --fast` | **Inconclusive by action** (both variants: "stop, not usable"). Reasoning and cost diverged sharply: before cites the deleted sentence verbatim in 307 output tokens / 14.1s; after reasons through an unrelated sentence ("unavailable result") to the same conclusion in 3603 output tokens / 52.0s — 11.7x tokens, 3.7x duration for a strained, second-order justification. |
| 3 | `Chief Engineer is missing` — "This skill has no gate or state authority." (Return section) | `behavior-diff.sh --file chief-engineer/SKILL.md --fast` | **Near-null divergence.** Both variants correctly refuse to advance workflow state, citing the *same* surviving Boundaries-section sentence ("do not... advance workflow state") — the deleted sentence duplicated a rule stated a second time elsewhere in the same file, so removing one statement changed nothing observable. Finding for the future slimming item: this file states the no-gate-authority duty twice. |

**Cost table** (`--fast` = 1 trial/variant = 2 headless runs; `duration_ms`
and `usage` output tokens are the `result` line of each trial's
`trace.jsonl`; `total_cost_usd` not used per the shape):

| Case | Wall-clock (whole invocation) | Before: duration_ms / output tokens | After: duration_ms / output tokens |
|---|---|---|---|
| 1 | ~64s (dir-timestamp derived: `config.json` to `report.html`, includes decision-diff + render post-processing — approximate, not wrapped at invocation) | 12,638 / 470 | 13,913 / 454 |
| 2 | 87s (wrapped at invocation) | 14,072 / 307 | 51,993 / 3,603 |
| 3 | 51s (wrapped at invocation) | 17,463 / 507 | 17,385 / 539 |

Median wall-clock across the three `--fast` (2-run) probes: **64s**.
Projected to a 6-run recorded-proof measurement (×3 trials): **≈192s
(3.2 min)**, against the cap of 45 min / 6 runs per case. Trivially under
the cap on wall-clock. **This probe is biased low for two independent
reasons**, both stated by the shape and confirmed here: (1) all three cases
are single-role rules in documents a plain `claude -p` reaches with no
fixture, while most of the remaining 15 candidate rules sit at
First-Officer/adoption decision points needing a tracked work item and
workflow directory; (2) this dispatch's "read the file directly" deviation
(above) is an even shallower probe of agent behavior than the loader-routed
task the shape specified.

**The checkpoint fact for the Captain is not primarily about cost — it is
about the instrument.** None of the three cases produced the shape's strict
definition of RED (after-variant takes the forbidden action, before-variant
doesn't). All three reached the *same* action in both variants; the
observable divergence was in citation accuracy and reasoning cost, not
action. This suggests the strict action-divergence RED test may be the
wrong instrument for prose duties a competent model tends to re-derive by
other means (case 1, 3) or reach via strained substitute reasoning (case 2)
— not that these rules are unnecessary. If this pattern holds across more
samples, **AC-3 as written ("the case is RED... names the rule") may be
undischargeable for some or all of the 18 tier-2 candidates on the strict
test**, independent of cost.

Three options for the Captain, plus one observation:

1. **Raise the cap** — affordable on wall-clock (64s median vs 45 min), so
   raising case count doesn't change feasibility; it does not address the
   instrument question above.
2. **Narrow tier-2 sampling to `kernel.md` rules only** (5 sites, the one
   document every working stage loads) — reduces exposure to the
   fixture-dependent, First-Officer-decision-point rules that are both more
   expensive to design and least tested by this probe.
3. **Route back** — the route-back condition ("a tier-2 case cannot be made
   to redden for a rule the slimming intends to touch... is a planning
   delta") already covers a case that stays inconclusive after design
   effort; two of three did, on the strict test.
4. *(Observation, not an option)* — if the Captain wants tier-2 cases that
   satisfy strict action-divergence RED, the case design itself likely needs
   to target rules whose violation is a distinct, checkable *action*
   (dispatch/stop, write/refuse) rather than a *reasoning-quality* duty like
   a comment-necessity or citation-accuracy rule; cases 1-3 were both drawn
   from the shape's own suggested set and were reasoning-quality rules.

No further tier-2 rule was converted pending this ruling, per the shape.

## Comment pass (this diff, against `f47fd8ca`)

- **Kept**: one 7-line pointer comment in `scripts/kc-dev-flow-contract-test.py`
  (before the first deleted tier-1 loop), naming why the region is smaller
  and pointing to this table. Reason: without it, a future reader sees a
  large deleted region with no trace of what replaced its coverage —
  not re-derivable from the surrounding code alone.
- **Cut**: none drafted-then-cut this cycle; the two new test additions in
  `profile-contract-loader.test.py` carry no comments — the `require()`
  failure messages state the fact directly.
- Removed one now-dead variable (`normalized_continuation_policy`, orphaned
  by deleting its only consumer) while editing the same region — Minimal
  necessity, not a separate pass.

## Diff stops (against delivery base `f47fd8ca`)

- **Changed files: 2** of the stop-5 budget
  (`scripts/kc-dev-flow-contract-test.py`,
  `kc-dev-flow/scripts/profile-contract-loader.test.py`).
- **Changed lines: 112** (41 added + 71 deleted) of the stop-600 budget.
- **Tier-2 case design**: stopped at 3 measured cases per the hard stop
  above.

## Candidate verification

At the candidate revision, in the worktree (not a clean clone — this
worktree was independently confirmed a valid baseline this session; the
shape's "not a valid baseline" finding was about a different, earlier
worktree state):

- `python3 scripts/kc-dev-flow-contract-test.py` → `kc-dev-flow contract: PASS`, exit 0, 40.4s (down from the 50.7s/51.1s baseline — expected, 7 fewer prose-scan loops execute).
- `python3 scripts/kc-dev-flow-contract-test.py --ablation-check` → `kc-dev-flow contract: PASS`, exit 0.

## Implementation-exit observation (`implementation_exit_observation_declared: true`)

The `build` contract's conditional reference names
`roborev-implementation-exit.md`, read in full this stage. It requires a
Spacedock-registered state holder, single-flight claim transaction, and a
RoboRev CLI/daemon probe on the executing host, then a live-batch provider
review with its own request/confirmation caps. **This observation was not
run in this dispatch** — exercising it is a separate, non-trivial capability
probe (state-holder claim, RoboRev host detection, live job wait) outside
this stage's tier-1/tier-2 pin-conversion scope, and the document itself
states that an unrun observation on a repository lacking the dependency "is
a declared boundary, not a missing binding... and not an `UNAVAILABLE`
result to re-derive." This is recorded as a gap, not a claimed PASS, FAIL,
UNKNOWN, or UNAVAILABLE outcome.

## Process note

The exit-code-swallowing pipe pattern (`command | tail; echo EXIT:$?`, which
always reports the pipe's own exit code, not the command's) recurred three
times early in this stage before being corrected to capture output to a
file and check `$?` directly. All exit-code claims from that point forward
in this report were captured that way.

## Captain ruling: tier-2 checkpoint (2026-09-02T15:46:41Z)

Route back accepted as a bounded planning delta. Changed premise: the shape's strict action-divergence RED did not fire on any of the three probe cases, so AC-3 as admitted was not dischargeable for tier-2. Affected evidence: AC-3 only; the accepted outcome and non-goals are unchanged, and the Linear Issue's AC-3 was updated to the same text. Ruling: DEV-51 completes tier-1 (the remaining five split halves and the release-proof boundary group, plus the two deferred classifications) and records every tier-2 candidate as wording-only with the probe evidence; no further behavior-diff case is run under this item. The negative result is a finding for DEV-52: a rule whose removal changes nothing because a duplicate survives elsewhere is a removal candidate signal.


## Captain-ruled continuation: tier-1 completion and tier-2 final disposition (cycle 2)

Per the Captain ruling above (route-back accepted, AC-3 amended to require every
tier-2 candidate recorded wording-only rather than reddened), this cycle:
converted the five split sites' tier-1 halves, investigated the release-proof
boundary group, resolved the two deferred classifications, and recorded all
tier-2 candidates as wording-only. No further `behavior-diff` case was run.

### Mutation replay table (tier-1, cycle 2)

| Site key | Mechanism mutated | New instrument (command → failure) | Old pin on same mutation |
|---|---|---|---|
| `kernel omits provider-neutral planning boundary` (T1 half: "the read-only engage comparator", "No reconcile result writes either side automatically") | Same mechanism and mutation as cycle 1's T1-1 (`engage-reconcile.py` L164 `return 0`) — reused, not re-run | `python3 kc-dev-flow/scripts/engage-reconcile.test.py` → exit 1, "membership delta returned 0" | GREEN (2/2 phrases still in kernel.md) |
| `{relative} omits the v4 POC contract` (T1 half: `poc_*` field names) | (a) `profile-contract-loader.py` L35 `POC_FIELDS`: drop `poc_stop_when`. (b) `poc-close-guard.py` L120: `one_yaml_section(text, "POC outcome", "poc_outcome")` → heading `"POC outcome MUTATED"` | (a) `profile-contract-loader.test.py` → exit 1, "v3 POC accepted a missing poc_stop_when". (b) `poc-close-guard.test.py` → exit 1, `CloseError: work item must contain exactly one POC outcome MUTATED` | GREEN both (7/7 choose-work-profile field-name phrases; 2/2 continue-dev-flow poc_outcome/poc_close_measurement phrases) |
| `chooser is missing` (T1 half: receipt schema/route strings) | `profile-contract-loader.py` L20 `ROUTES["poc-exploration"]["validation"]`: `("prove", "done")` → `("prove-mutated", "done")` | `python3 scripts/kc-dev-flow-contract-test.py` → exit 1, "route topology drifted" (existing L403 `require(loader.ROUTES == expected_routes, ...)` plus `profile-contract-loader.test.py`'s own copy) | GREEN (6/6 phrases still in choose-work-profile/SKILL.md) |
| `continuation planning disambiguation omits` (T1 half: `--expected-*`, exit codes, `status: clean`) | Same mechanism and mutation as cycle 1's T1-1/this cycle's provider-neutral-boundary row (`engage-reconcile.py` L164) — reused | `python3 kc-dev-flow/scripts/engage-reconcile.test.py` → exit 1, "membership delta returned 0" | GREEN (8/8 converted phrases still in continue-dev-flow/SKILL.md) |
| `self-adoption omits Linear cutover boundary` (T1 half: `--expected-*`, `--state-revision`, envelope schema, process-env refusal) | `linear-admission.py` L402: `"--expected-source", str(engaged["source"])` → prefixed `"MUTATED-"` | `python3 scripts/kc-dev-flow-contract-test.py` → exit 1, "clean Linear admission failed: linear admission: planning comparator returned invalid output" (existing inline mock-Linear-server fixture, L1625+) | GREEN (8/8 phrases still in docs/dev/README.md) |

Every mutation above was reverted after its cycle; full `kc-dev-flow-contract-test.py`
(plain and `--ablation-check`) passes at the candidate (below).

**`kernel omits completion invariant` (row 1 of the inventory) is not in this
table.** Its shape-recorded tier is `split`, but between T2 (the working
agent's without-it observation) and **wording-only** (the FO/ensign handoff
half) — it has no tier-1 half. The shape's own totals ("8 tier 1, 5 split, 13
tier 2, 5 wording-only = 31") undercount by one in the same direction as its
earlier corrected 19→20→31 pin-count error: a row-by-row count of the `##
Pin inventory` table's Tier column finds **6** rows marked `split`, not 5 —
this row is the sixth, and it has no tier-1 component to convert. The
Captain's "five split sites" instruction correctly names the five that do
carry a tier-1 half (all five converted above); this finding is recorded so
the totals line can be corrected without re-opening AC-1.

### Release-proof boundary: investigated, stays wording-only

Per the shape's stated fallback ("build names the receipt field it asserts,
else this drops to wording-only"): the field is **`tree_sha256`**, in
`scripts/kc-dev-flow-published-tag-smoke.py`'s `load_candidate_receipt()`.
Its structural validation (format, presence, wrong-length/garbage digest) is
tested (`kc-dev-flow-published-tag-smoke.test.py` L458, L501). But the
specific comparison that enforces "candidate receipt is valid only for its
exact tracked package snapshot" — `if source_digest != receipt["tree_sha256"]:
raise SmokeError(...tracked snapshot drift)` at L727-730 — sits inside the
**published-mode** path, which does a live `git clone --branch <tag>` against
the real repository over network; no test exercises that branch, and building
one is a live-git/host-CLI harness this dispatch does not have budget to add
without risking an unverified mutation cycle (the same non-goal that bars
removing a pin whose replacement hasn't reddened applies equally to *adding*
one that hasn't). Recorded wording-only per the shape's explicit contingency;
pin unchanged.

### Deferred classifications, resolved

- **`continuation omits provider delivery linkage`**: does `pr-review-handoff.py`
  already refuse? **No.** Read in full — it is "Create and validate the
  non-authoritative kc-dev-flow PR-review evidence index," with no reference
  to branch push, PR creation, or the delivery binding this pin protects.
  Stays tier-2, now wording-only per the Captain ruling.
- **`manual admission Issue body omits`**: does the existing non-loop
  template-parse assertion (heading set/order/`startswith`, L1416-1435) cover
  the two remaining phrases? **No.** Those assertions check structure
  (headings present once, in order, body starts with `## The problem`); the
  two remaining phrases ("The accepted outcome or non-goals changed",
  "structured planning delta") are prose *inside* the Route-back conditions
  section's content, not a structural fact any parse covers. Confirmed
  wording-only, unchanged from its original classification.

### Tier-2 final disposition: all candidates wording-only

Per the Captain ruling, every tier-2 candidate rule is recorded wording-only
with its reason; no further `behavior-diff` case is required to redden. The
three probe cases already run (`## Tier-2 checkpoint` above) are the evidence
for the ruling itself, not per-rule proof — each remaining candidate's "reason"
below is the ruling, not a repeated probe.

**Count correction**: the shape's totals line said "13 tier 2." A row-by-row
count of the original inventory's Tier column finds **12** rows marked
plain `2`, plus **6** rows marked `split` (not 5 — see above), one of which
(`kernel omits completion invariant`) has a T2 half with no T1 counterpart.
Counting every candidate rule that is now wording-only under this ruling:
12 pure-T2 rows + 6 split rows' T2/remaining halves = **18**, matching the
shape's own separately-stated "18 tier-2 candidate rules" even though its
"13 tier 2, 5 split" breakdown was off by one in each direction. 18 is
therefore the correct, internally-consistent count; "13/5" is not.

| Rule (site key) | Reason (wording-only, per Captain ruling) |
|---|---|
| `kernel omits subtraction rule` | Probed (checkpoint case 1): inconclusive by action; pin stays |
| `audit omits unified need vocabulary` | Not probed (checkpoint stopped at 3 cases); route-back ruling applies |
| `kernel omits brief boundary` | Probed (checkpoint case 2): inconclusive by action; pin stays |
| `continuation omits provider delivery linkage` | Deferred classification resolved this cycle: `pr-review-handoff.py` does not refuse; stays T2 → wording-only |
| `PR delivery omits provider linkage` | Not probed; route-back ruling applies |
| `adopter omits scheduling binding` | Not probed (largest single site, highest design cost); route-back ruling applies |
| `continuation authority resolution omits` | Not probed; route-back ruling applies |
| `adopter omits migration rule` | Not probed; route-back ruling applies |
| `Chief Engineer is missing` | Probed (checkpoint case 3): near-null divergence, duplicate wording found; pin stays |
| `Science Officer is missing` | Not probed ("same shape as" Chief Engineer per inventory, untested); route-back ruling applies |
| `self-adoption misstates brief authority` | Not probed; route-back ruling applies |
| `validation runbook omits` | Not probed; route-back ruling applies |
| `kernel omits completion invariant` (T2 half) | Not probed; route-back ruling applies. (Its other half was already wording-only in the shape — FO/ensign handoff duty, out of this item.) |
| `kernel omits provider-neutral planning boundary` (T2 remainder, 9 phrases) | Authority-split/no-projector prose; T1 half converted above |
| `{relative} omits the v4 POC contract` (T2 remainder) | Narrative duties (README/base.md); T1 half (field names) converted above |
| `chooser is missing` (T2 remainder: "structured Ask UI") | UI-behavior prose, not mechanism-testable; T1 half converted above |
| `continuation planning disambiguation omits` (T2 remainder) | Branch-selection/authority prose, plus "Refuse a truncated provider result" — investigated, **not currently enforced by any mechanism** (no "truncat" string anywhere in `kc-dev-flow/scripts/*.py`); a real gap in the shape's T1 classification, left as an agent-followed instruction, wording-only. Recorded as directed at DEV-60 per the validation checklist, but DEV-60's admitted problem statement (kc-pr-review handoff index for Linear-backed deliveries) does not itself name provider-result truncation — the FO should confirm this is the intended target or route the finding to a new item. |
| `self-adoption omits Linear cutover boundary` (T2 remainder: "not an iteration authority" sentence) | Repo-policy prose with no mechanism; T1 half converted above |

Wording-only pins unchanged from the original inventory (never tier-2): **5**
(`v4 migration omits`, `3.x migration omits standalone planning branch`,
`rationale omits`, `manual admission Issue body omits` — confirmed above,
`Roadmap is not thin enough for provider-neutral planning`).

### Diff stops (final, against delivery base `f47fd8ca`)

- **Changed files: 2** of the stop-5 budget (unchanged from cycle 1).
- **Changed lines: 144** (41 added + 103 deleted) of the stop-600 budget.
- Comment pass: unchanged from cycle 1 — 7 lines (the one pointer comment),
  no new comments added this cycle.

### Final candidate verification

- `python3 scripts/kc-dev-flow-contract-test.py` → `kc-dev-flow contract: PASS`, exit 0, 45.0s.
- `python3 scripts/kc-dev-flow-contract-test.py --ablation-check` → `kc-dev-flow contract: PASS`, exit 0, 5.8s.

### F1/F2 equivalence evidence (cycle 2 addendum)

F2 (tier-1 replacement asserts nothing the mechanism enforces) disproved for
all 5 cycle-2 conversions via the mutation replay table above — same
patch → owning-instrument-red-naming-the-rule → `git apply -R`/`git checkout
--`/revert → green sequence as cycle 1. Combined with cycle 1's 7 groups,
**12 of 13 tier-1 groups now carry a full mutation-replay triple**; the 13th
(`package README omits the release-proof boundary`) was investigated and
named (field: `tree_sha256`) but not converted, for the stated reason.

## Validation bounce (2026-09-03): AC-5 forbade a loss the tier-1 conversions caused

Validation ran `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py < /dev/null`
(the full ablation, not `--ablation-check`, which is a quick mode of the
contract test itself) and found `installed-skill-anchor-removed` survived at
`99a0c826`, on the merged tip `ce70336f` (origin/main #340 merged in under
Captain authorization; one hunk resolved by keeping this item's retained
`self-adoption omits Linear cutover boundary` phrase with #340's wording — no
other conflict).

### Root cause

`kc-dev-flow-contract-test.py --ablation-check` is used by every
`run_manual_contract_mutant`/`run_kernel_contract_mutant`/custom mutant that
targets a *document* (not loader/engage-reconcile/linear-admission code).
`--ablation-check` skips the `if not require_ablation_only: run([...])` block
that shells out to `profile-contract-loader.test.py`, `engage-reconcile.test.py`,
and `poc-close-guard.test.py`. Every tier-1 conversion whose sole evidence was
"the mechanism suite already covers this, invoked via `run()`" therefore has
**zero effective protection** in the exact mode AC-5's ablation suite drives —
the mutation-verify cycles in cycles 1-2 proved the mechanism reddens on a
*code* mutation, never on a *document-prose* mutation, so AC-4's "the old
assertion is run against each mutation its replacement claims to cover" was
not actually satisfied for these sites: the ablation's document mutations are
mutations the old (now-deleted) pin covered that the new instrument never saw.

The discriminating test, applied to every phrase in every tier-1 group: delete
the sentence, touch no mechanism, and ask whether a mechanism refuses an agent
that violates the rule the sentence stated, with a message naming it. A named
refusal is tier-1; a document instructing an agent how to behave, with nothing
that inspects whether the agent complied, is tier-2/agent-only — regardless of
whether the *behavior the document asks for* happens to be separately
mechanism-tested elsewhere (e.g. the loader's own `loaded == 3 paths`
invariant is real and `profile-contract-loader.test.py` proves it, but nothing
proves `continue-dev-flow/SKILL.md` still *describes* that invariant
correctly once its pin is gone).

### Every surviving/misbehaving mutant, its disposition

The suite stops at the first survivor; each fix below was applied, then the
full ablation was re-run to find the next one, until exit 0.

| # | Mutant | What it mutates | Disposition |
|---|---|---|---|
| 1 | `installed-skill-anchor-removed` | `continue-dev-flow/SKILL.md`: "Resolve `../../scripts/profile-contract-loader.py` from this activated skill." → "Resolve a profile loader from the current host." | Pin restored: whole `continuation is missing` site (12 phrases) — an FO path-resolution instruction with no mechanism naming a violation |
| 2 | `marked-local-profile-read-contract-removed` | Same document: "marked block; never infer boundaries from headings..." reworded | Same restore (site above; this phrase is one of the 12) |
| 3 | `adopter-local-profile-marker-removed` | `adopt-dev-flow/SKILL.md`: start marker text replaced | Pin restored: whole `adopter omits static Local Profile marker` site (both markers) |
| 4 | `reconcile-clean-output-wiring-removed` | `continue-dev-flow/SKILL.md`: "Exit `0` continues only when stdout parses as one JSON object with `status: clean`..." reworded | Pin restored: whole `continuation omits provider engage behavior` site (7 phrases), plus `normalized_continuation_policy` re-added |
| 5 | `default-loader-revalidation-restored` | `profile-contract-loader.py`: `if validate_admission` → `if True` (a **code** mutation, checked via `profile-contract-loader.test.py` directly, not `--ablation-check`) | Not a prose-pin loss — this item's own cycle-1 addition (the default-mode `development_brief_sha256`-absence assertion) sat *before* the pre-existing `historical` dual-section test in the file and fired first with a different, true-but-generic message, masking the specific evidence (`"new admission cannot contain Acceptance evidence with canonical criteria"`) this mutant expects. Fixed by relocating the addition to after the `historical` test (still asserting the same fact, on the same `admitted` fixture item) — no restore, no reclassification, `package README omits admission boundary` stays tier-1 |

Two more sites were restored **preemptively**, before running further and
finding their own survivor, because they are the same misclassification
class and a future validation pass would find them: `kernel backlog exit bar
is missing` (whole site, 4 phrases — "leaves `backlog` only after its brief
is admitted" is an FO transition duty; `--validate-admission` is a tool the FO
chooses to run, and default loading admitting a brief-less item is exactly
what this item's own cycle-1 mutation proved) and `continuation omits doc
trigger` (whole site, 4 phrases — `check_conditional_references`'s own
docstring states "does not evaluate `trigger`"; trigger evaluation is
agent-only). Both were re-verified present in the current document
(`docs/dev/README.md`'s merge from #340 did not touch either) before
restoring, per the order-of-operations check below.

Two split sites lost only the specific phrases that are agent prohibitions
with no refusing mechanism, keeping their genuinely mechanism-backed halves
converted: `kernel omits provider-neutral planning boundary` ("No reconcile
result writes either side automatically" restored; "the read-only engage
comparator" — the exit-code/JSON observable itself — stays converted) and
`continuation planning disambiguation omits` ("No difference writes the
provider or execution snapshot automatically." and "stdout parses as one JSON
object with `status: clean`" restored; the `--expected-*` flags, exit codes,
and "Refuse a truncated provider result" wording-only status are unchanged).

### Order-of-operations check (before each restore)

Every phrase restored was grep-checked against the current document at the
merged tip (`ce70336f`, post-#340) before restoring, so a survivor would fail
for "mutant survived" (the correct symptom) rather than "failed for the wrong
reason" (a stale phrase). All matched verbatim — #340 did not reword any
phrase this item restores.

### Corrected tier classification

| Site key | Original tier (shape) | State after cycles 1-2 | State after validation bounce |
|---|---|---|---|
| `continuation omits provider engage behavior` | 1 (pure) | converted | **restored — tier-2/wording-only** (agent-instruction category error) |
| `kernel backlog exit bar is missing` | 1 (pure) | converted | **restored — tier-2/wording-only** (same) |
| `adopter omits static Local Profile marker` | 1 (pure) | converted | **restored — tier-2/wording-only** (same) |
| `continuation is missing` | 1 (pure) | converted | **restored — tier-2/wording-only** (same) |
| `continuation omits doc trigger` | 1 (pure) | converted | **restored — tier-2/wording-only** (same) |
| `package README omits admission boundary` | 1 (pure) | converted | **stays converted** — inline, ungated assertion; fixed an unrelated test-ordering conflict, not a reclassification |
| `package README omits mod boundary` | 1 (pure) | converted | **stays converted** — shares the loader's `loaded == 3 paths` mutation with `continuation is missing`, but its own pin phrases are in `kc-dev-flow/README.md`, a document with no agent-decision-path role (per the original inventory); no mutant targets it, and the discriminating test does not clearly indict it — left as-is rather than restored on suspicion alone |
| `package README omits the release-proof boundary` | 1 (pure) | not converted (field named, wording-only) | unchanged |
| `kernel omits provider-neutral planning boundary` | split | T1 half converted (2 phrases) | **T1 half reduced to 1 phrase** ("the read-only engage comparator"); "No reconcile result writes either side automatically" restored to T2/wording-only |
| `{relative} omits the v4 POC contract` | split | T1 half converted | **stays converted** — POC field names are refused by name (`"exactly one {missing_field}"`, `"POC outcome MUTATED"` style messages), the discriminating test passes |
| `chooser is missing` | split | T1 half converted | **stays converted** — inline, ungated `loader.ROUTES == expected_routes` |
| `continuation planning disambiguation omits` | split | T1 half converted (8 phrases) | **T1 half reduced to 6 phrases**; 2 restored to T2/wording-only |
| `self-adoption omits Linear cutover boundary` | split | T1 half converted | **stays converted** — inline Linear-fixture exercise, `--expected-*`/`--state-revision` are `argparse(required=True)`-named flags, envelope schema is an inline JSON assertion |

**Net**: of the original 13 tier-1 groups, **6 keep a mutation-verified
tier-1 conversion in some form** (2 pure + 4 split, 2 of the split reduced in
scope), **5 pure groups are fully restored** to their original phrase pins,
and **2 sites** (`package README omits the release-proof boundary`,
never converted) plus the newly-restored 5 remain wording-only/tier-2 under
the Captain's route-back ruling. The wording-only/tier-2 count under that
ruling grows from 18 to **23** (18 original tier-2 candidates + 5 restored
sites), each still carrying a reason: the 18 cite the checkpoint ruling, the
5 restored ones cite this bounce's misclassification finding.

### Verification at the corrected tip

- `python3 scripts/kc-dev-flow-contract-test.py` → `kc-dev-flow contract: PASS`, exit 0, 45.8s.
- `python3 scripts/kc-dev-flow-contract-test.py --ablation-check` → `kc-dev-flow contract: PASS`, exit 0, 5.8s.
- `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py < /dev/null` → `kc-dev-flow minimal-stack ablation: PASS`, exit 0, 2m14s, **64 mutants REJECTED**, 0 survivors.
- `git diff --stat origin/main`: 2 files, 93 lines (40 added + 53 deleted) — `scripts/kc-dev-flow-contract-test.py`, `kc-dev-flow/scripts/profile-contract-loader.test.py`. Within the 5-file/600-line stops.
- Comment pass: the tier-1 pointer comment (above the surviving conversions) was rewritten to state the actual constraint (mechanism citations require a full run; `--ablation-check` skips it) instead of naming groups that are no longer accurate — 5 lines, down from 7.


## Stage Report: implementation

- FAILED (partial): Replace the tier-1 and split pin sites with assertions on the enforcing mechanism's observable output, and for every replaced pin record the mutation run before the old pin is removed.
  7 of 8 pure tier-1 groups converted with a full mutation-replay triple each (`## Mutation replay table`); the 5 split sites' tier-1 halves and the 8th pure group (`release-proof boundary`) are unconverted, each with a stated reason (`## Tier-1 groups not converted this cycle`) — no pin was removed without its replacement reddening first.
- DONE: Run the three tier-2 probe cases with the shape's method, report the median against the caps, and stop at the checkpoint with the three options for the Captain.
  `## Tier-2 checkpoint` — 3 cases run (`--fast`, 2 runs each), all inconclusive by the shape's strict action-divergence test; median wall-clock 64s, ×3 projection ≈192s against the 45 min/6-run cap. Checkpoint fact recorded is about the instrument (strict RED may be undischargeable for reasoning-quality prose duties), not primarily cost. Three Captain options plus one observation recorded; no further tier-2 rule converted.
- DONE: Stay inside the shape's stops and record diff counts, comment pass, remaining wording-only pins, full contract test + ablation results, and this item's F1/F2 equivalence evidence.
  `## Diff stops`: 2 files / 112 lines, both within budget. `## Comment pass`: 1 kept (7-line pointer, reason stated), 0 cut, 1 dead variable removed. `## Candidate verification`: contract test PASS exit 0 40.4s; `--ablation-check` PASS exit 0. Remaining wording-only pins: 5, unchanged. `## F1/F2 equivalence evidence`: F2 disproved for all 7 converted groups (replay table); F1 is tier-2's evidence half, addressed in the checkpoint's per-case citation/action records.

### Summary

Converted 7 of 8 pure tier-1 pin sites to mechanism-observable assertions, each with a redden-before-removal mutation triple recorded in `## Mutation replay table`; found and closed two real coverage gaps (Local Profile marker boundary, `--validate-admission` default-mode absence) rather than assuming existing coverage sufficed. Ran the three tier-2 probe cases the shape specified and stopped at the checkpoint as required: all three were inconclusive by strict action-divergence, but two showed sharp reasoning-cost divergence and the third revealed a real duplicate-wording finding — the checkpoint report to the Captain leads with the instrument question (does strict RED even fit reasoning-quality prose rules) rather than treating cost alone as the gating fact. The 5 split sites' tier-1 halves, the release-proof-boundary site, and three build-deferred classification checks are left unconverted with stated reasons; diff stayed at 2 files / 112 lines against the 5-file/600-line budget, well under both stops.

## Stage Report: implementation (cycle 2)

- DONE: Convert the remaining tier-1 work (five split sites' tier-1 halves, release-proof boundary group) with the same mutation discipline, and resolve the two deferred classifications.
  `## Captain-ruled continuation` — 5 of 5 named split sites converted with mutation-replay triples (2 reused an already-proven mechanism, 3 are new mutations); release-proof boundary investigated, field named (`tree_sha256`), stays wording-only per the shape's own stated fallback (live-git harness not present, not added this cycle). Both deferred classifications resolved: `pr-review-handoff.py` does not refuse (stays T2/wording-only); the template-parse assertion does not cover the manual-admission prose phrases (confirmed wording-only, unchanged).
- DONE: Record all 18 tier-2 candidate rules as wording-only with reason and a pointer to the checkpoint probes; run no further behavior-diff case.
  `## Tier-2 final disposition` table — all 18 (12 pure T2 + 6 split T2/other remainders, corrected from the shape's internally-inconsistent "13 tier 2, 5 split") recorded with reason; the 3 already-probed rules point to the checkpoint's per-case evidence, the rest cite the Captain's route-back ruling. No new `behavior-diff` invocation this cycle.
  One real gap found: `continuation planning disambiguation omits`'s "Refuse a truncated provider result" phrase, which the shape classified tier-1-adjacent, is not enforced by any mechanism (`grep -r truncat kc-dev-flow/scripts/*.py` is empty) — recorded wording-only, not silently converted.
- DONE: Stay inside the stops, run the full contract test and ablation check at the final candidate, and amend the stage report with final diff counts, comment pass, remaining wording-only count, and F1/F2 evidence.
  `## Diff stops (final)`: 2 files / 144 lines, both within the 5-file/600-line budget. Comment pass unchanged (7 lines, one pointer comment, nothing new). `## Final candidate verification`: contract test PASS exit 0, 45.0s; `--ablation-check` PASS exit 0, 5.8s. `## F1/F2 equivalence evidence (cycle 2 addendum)`: 12 of 13 tier-1 groups now carry a full mutation-replay triple (F2 disproved for each); the 13th is investigated-and-named, not converted.

### Summary

Checklist item 1 is now **DONE**: 12 of the 13 tier-1 groups (7 pure + 5 split halves) carry full redden-before-removal mutation triples; the 13th (release-proof boundary) was investigated per the shape's own contingency and named as wording-only rather than force-converted without a verified mutation. All 18 tier-2 candidates are recorded wording-only per the Captain's route-back ruling, with the 3 checkpoint-probed rules pointing to their case evidence and the rest citing the ruling; one real tier-1/tier-2 misclassification was found and corrected (`Refuse a truncated provider result` is not mechanism-enforced) rather than silently forced into tier-1 to close the count. Final diff: 2 files / 144 lines against the 5-file/600-line budget. Full contract test and `--ablation-check` both pass at the candidate.

## Stage Report: validation

- DONE: Independently re-run the full contract test and the ablation check at the exact candidate 99a0c826, then replay at least four of the twelve mutation triples from the replay table (one each against profile-contract-loader.py, engage-reconcile.py, poc-close-guard.py, and linear-admission.py); confirm from the diff that no pin was removed whose replacement is not in that table.
  Confirmed HEAD is `99a0c826`. `python3 scripts/kc-dev-flow-contract-test.py` PASS, exit 0, 44.6s; `--ablation-check` PASS, exit 0, 5.8s (both independently timed this session, not read from the report). Replayed 4 triples: (1) `engage-reconcile.py` L164 `return 1 if ... else 0` -> `return 0` reddened `engage-reconcile.test.py` with "membership delta returned 0", restored, green; (2) `poc-close-guard.py` L120 heading `"POC outcome"` -> `"POC outcome MUTATED"` reddened `poc-close-guard.test.py` with `CloseError: work item must contain exactly one POC outcome MUTATED`, restored, green; (3) `linear-admission.py` L402 `--expected-source` prefixed `"MUTATED-"` reddened the full contract test with "clean Linear admission failed: linear admission: planning comparator returned invalid output", restored, green; (4) `profile-contract-loader.py` `validate_admission_brief()` given an early `return "0"*64` reddened `profile-contract-loader.test.py` with "admission accepted missing-the-problem: {...}", restored, green. Working tree confirmed clean after each restore. Diff audit: `comm -23` on the sorted set of `require(...)` message prefixes between `f47fd8ca` and `99a0c826` finds exactly 7 site keys removed entirely (`adopter omits static Local Profile marker`, `continuation is missing`, `continuation omits doc trigger`, `continuation omits provider engage behavior`, `kernel backlog exit bar is missing`, `package README omits admission boundary`, `package README omits mod boundary`) — all 7 map onto the cycle-1 mutation replay table's 6 rows (one row covers two site keys via a shared mechanism). No site key disappeared outside the table; every other diff hunk is a partial phrase removal from a still-present `split` site, matching the cycle-2 table.
- DONE: Verify this item's own equivalence instrument for its semantics_unchanged: true declaration: read the F1/F2 evidence, confirm the instrument was seen to fail, record equivalence_instrument and equivalence_instrument_failure in the work profile receipt, and confirm the loader accepts the receipt at validation.
  Read `## Semantics and the equivalence instrument` and both `## F1/F2 equivalence evidence` sections. Confirmed the instrument was seen to fail first: `python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item <this entity> --format json` before the edit refused with `profile contract: work item must contain exactly one equivalence_instrument`, exit 2 — the loader's own necessity-field gate, unforced. Added `equivalence_instrument` and `equivalence_instrument_failure` to the `## Work profile receipt` YAML block naming the four replayed commands and their exact observed failure messages (the same four from the item above). Re-ran the loader against the same entity path: exit 0, `workflow_stage: validation`, `logical_stage: verify-deliver`, `next_workflow_stage: done` — the receipt is now accepted.
- FAILED (blocking): Delivery readiness for the exact revision.
  Branch name and close line verified independently against the Linear GraphQL API (not just trusted from this assignment): `issue(id:"DEV-51").branchName` returns exactly `feature/dev-51-replace-kc-dev-flow-contract-test-phrase-pins-with-behaviour`; close line per `pr-delivery.md` is `Fixes DEV-51`. No absolute claim (`exactly`/`only`/`always`/`never`/`cannot`/`byte-for-byte`) appears in either commit message or in the added diff lines. Wording-only count is already stated with reasons in the body: 1 (release-proof boundary, investigated, field named `tree_sha256`, live-git harness not added) + 18 (tier-2, `## Tier-2 final disposition`) + 5 (original inventory, unchanged) = 24. The tier-2 negative-result finding for DEV-52 was already recorded (`## Captain ruling: tier-2 checkpoint`); the truncated-provider-result gap had no DEV-60 pointer, added this stage as directed — but DEV-60's admitted scope does not itself name provider-result truncation, so the mapping needs FO confirmation, recorded as a caveat on that same table row. **Separately**, `git -C {worktree} merge-tree --write-tree origin/main 99a0c826` (per `pr-delivery.md` step 2) returns a **real content conflict** in `scripts/kc-dev-flow-contract-test.py`, exit 1. Reading the two diffs against their shared base `f47fd8ca` line by line: `origin/main`'s `bda45e6b` ("make installed runtime portable across worktrees", merged 2026-09-02 23:47, after this candidate's delivery base) rewords three phrase-list lines inside the same `for phrase in [...]` block (`self-adoption omits Linear cutover boundary`). Two of those three (`Planning reader and admission guard`, `reconcile every active Issue`) are untouched by this candidate — adjacency only, and would merge cleanly. The third — `` `LINEAR_API_KEY` and `CONDUCTOR_WORKSPACE_ID` only from the current Conductor process environment `` — is a genuine **modify-vs-delete** conflict: main rewords it in place, this candidate deletes it outright as part of the 8-phrase T1 conversion whose replacement mechanism is `linear-admission.py`'s process-env refusal, the same triple already replayed in the item above. So the conflict is narrow (one line) and its correct resolution is known (take the deletion; the reworded text is moot once deleted) — but resolving it is a code change this validation stage does not perform. Per `pr-delivery.md`: "stop delivery, surface the conflict evidence, and keep the pending delivery authority. Do not rebase, auto-resolve, or force." Not pushed; no PR created. Because the conflicted region is pure deletion on this candidate's side, re-validation after reconciliation is bounded: re-running the `linear-admission.py` triple on the merged revision re-establishes that specific piece of evidence rather than requiring a full re-run.

### Summary

Independently reran the full contract test and ablation check at `99a0c826` (both PASS) and replayed 4 of the 12 mutation triples across all four named mechanisms — every redden message and every restore-to-green matched the recorded table exactly, and a full before/after message-set diff confirms no pin vanished outside that table. Closed the one real gap the checklist named: the work profile receipt was missing `equivalence_instrument`/`equivalence_instrument_failure`, the loader refused it unforced (exit 2, naming the missing field), and it now accepts the same entity (exit 0) with those two fields recording the four exact commands and observed failures. Delivery readiness is where this stage stops short: the branch name and close line are independently verified against Linear, the wording-only accounting and the DEV-52 finding were already correct, and a DEV-60 pointer for the truncated-provider-result gap was added with a caveat that DEV-60's admitted scope doesn't name truncation and needs FO confirmation — but `git merge-tree` against current `origin/main` finds a real, narrow content conflict in `scripts/kc-dev-flow-contract-test.py`: a same-day main commit (`bda45e6b`) rewords a phrase this candidate deletes outright (modify-vs-delete on one line, not mere adjacency), with a known resolution (take the deletion) that this stage does not perform. Per `pr-delivery.md` this stops delivery rather than being auto-resolved.

**Authorization requested from the Captain:** (1) how to reconcile `99a0c826` against current `origin/main` — a rebase/merge is a code-changing repair that would invalidate this validation's exact-revision evidence (the 4 replayed triples and the loader-accepted receipt) and require re-verification on the new revision, so the choice of whether to repair now, defer, or accept a stale base is the Captain's; (2) once reconciled, explicit authorization to push the resulting revision to `feature/dev-51-replace-kc-dev-flow-contract-test-phrase-pins-with-behaviour` and open the Draft PR with close line `Fixes DEV-51`, per `pr-delivery.md`'s "wait for an explicit instruction to push."

Remaining production obligations and promotion triggers (`verify-deliver.md` Required output): none observed — the change touches only test/script files with no adopter-visible contract, and no Pilot promotion boundary (production data or credentials, broad exposure, a compatibility break forcing consumer action, irreversible migration, unattended recurring operation, or SLO/support duty) was crossed this stage.

## Stage Report: implementation (cycle 3)

- DONE: Run the full ablation with stdin closed, and for each surviving mutant read what it mutates and restore the pin (with reclassification) or retarget with a proven triple; never delete or weaken a mutant.
  `## Validation bounce` — 4 real prose-mutation survivors found and fixed by restoring their pins (`continuation is missing`, `continuation omits provider engage behavior`, `adopter omits static Local Profile marker`, plus a preemptive restore of `kernel backlog exit bar is missing` and `continuation omits doc trigger` for the identical misclassification class), 2 split-site phrases restored, and one non-prose test-ordering conflict (`default-loader-revalidation-restored`) fixed by relocating this item's own cycle-1 test addition rather than touching the ablation file. No mutant in `scripts/kc-dev-flow-minimal-stack-ablation.test.py` was edited, deleted, or weakened.
- DONE: Re-run the full contract test and the full ablation at the final tip; record both exit codes, elapsed times, and the count of mutants rejected.
  `## Verification at the corrected tip` — contract test PASS exit 0, 45.8s; `--ablation-check` PASS exit 0, 5.8s; full ablation PASS exit 0, 2m14s, **64 mutants REJECTED**, 0 survivors.
- DONE: Amend the stage report with a Validation bounce section (every survivor, disposition, corrected tier, updated wording-only count) and final diff counts against origin/main.
  `## Corrected tier classification` table — 6 of the original 13 tier-1 groups keep a mutation-verified conversion (2 pure fully, 4 split fully or partially), 5 pure groups fully restored to phrase pins, tier-2/wording-only count grows from 18 to 23. `git diff --stat origin/main`: 2 files / 93 lines, within the 5-file/600-line stops.

### Summary

The validation bounce found a systematic category error, not an isolated miss: five of the seven cycle-1 "pure tier-1" conversions cited a mechanism test invoked through `contract-test.py`'s gated `run()` block, which `--ablation-check` — the mode every document-mutation mutant in the ablation suite drives — skips entirely, so the cited mechanism provided no actual protection against the exact class of mutation (document prose rewording) the deleted pin used to catch. Root cause and fix are recorded together with the discriminating test (does a mechanism refuse an agent's violation by name, or does the document only instruct the agent) applied to every phrase in every affected group, not just the one the ablation happened to catch first — five whole sites and two split-site phrases were restored on that basis, including two the ablation had not yet reached, to close the class rather than the single reported instance. One unrelated defect (a new cycle-1 test assertion firing before an existing, more specific one under a particular loader-code mutation) was fixed by reordering, not by touching tier classification. The full ablation now passes cleanly with 64 mutants rejected and zero survivors; the corrected diff against origin/main is 2 files / 93 lines.
