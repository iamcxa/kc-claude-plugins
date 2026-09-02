---
title: "Replace kc-dev-flow contract-test phrase pins with behaviour assertions a mutation can redden"
status: ideation
source: https://linear.app/duckbase-co/issue/DEV-51/replace-kc-dev-flow-contract-test-phrase-pins-with-behaviour
product: kc-dev-flow
planning-window: Linear Cycle d1c96803-02fa-4323-b3a8-2fc44cc43699 2026-09-10T16:00:00.000Z/2026-09-24T16:00:00.000Z
planning-outcome: Linear Project 4746021d-2930-4589-80a0-b7b3d1d70eeb kc-dev-flow slimming dogfood sha256:0599c390742642a1edf03e07a50c28635ff41d3ef77188e076cb2f02e6d85372
sprint: S8
sprint-readiness: ready
started: 2026-09-02T14:23:40Z
completed:
verdict:
worktree:
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
- **AC-3** Every tier-2 case has a recorded run with and without the rule, plus one deliberately removed rule that the case flags; the wall-clock and token cost per case is measured and recorded.
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
