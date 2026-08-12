---
id: 64w8w7fpkt3ryg13h4ye7xnn
title: "kc-dev-flow: make stage activation loader-native"
status: done
source: "captain:conversation-2026-08-12"
product: kc-dev-flow
sprint:
started: 2026-08-12T04:32:15Z
completed: 2026-08-12T05:28:06Z
verdict: PASSED
worktree:
issue:
pr: iamcxa/kc-claude-plugins#215
mod-block:
design: required
lane: main
archived: 2026-08-12T05:37:28Z
---

## Problem

The adopted workflow can express correct policy under a conceptual common-plus-stage bundle, but Spacedock 0.26 dispatches the selected stage subsection only. An implementation worker may therefore treat a readable PR-policy link as active policy or miss the exact activation boundary. Make the actual loader output sufficient for the smallest safe decision without expanding review, state, or Captain ceremony.

## Proposed approach

Keep the implementation stage's declared policy set unchanged:
`_mods/work-control-profile.md` is the only stage-entry mod. Make the selected
stage subsection itself state that a link to an unlisted mod is a locator, not
activation. Rewrite the existing PR-topology bullet so it loads only the
Delivery topology decision after the candidate revision, changed-file map,
merge-base diff size, and independent/dependent slice assessment exist. Before
that trigger, `_mods/pr-merge.md` remains unread.

Protect the boundary in the existing `scripts/kc-dev-flow-contract-test.py`.
The test should reject either premature activation (adding `pr-merge` to the
implementation `Policy mods` list) or a lost trigger/locator. Re-run the real
stage extractor through `/opt/homebrew/bin/spacedock` 0.26.0 as origin-runtime
evidence; do not add a Spacedock dependency to portable CI.

### Loader observation and reverse-recovery audit

Fresh `origin/main` is
`a18ba78f72c03036d8463629bd19977aa684e159`. The installed runtime is
`spacedock 0.26.0 (contract 3)`. At that revision:

```text
$ /opt/homebrew/bin/spacedock dispatch show-stage-def \
    --workflow-dir <origin-main-worktree>/docs/dev \
    --stage implementation
sha256  c85143915d110cd7937a967b9fed32fc4c799ec5ef151e9b24438bd15df23dad
size    27 lines, 227 words, 1616 bytes
```

The output is the implementation subsection only. It declares
`_mods/work-control-profile.md`, contains the inline
`_mods/pr-merge.md#delivery-topology-decision` link, and contains none of
`merely readable`, `leave unread`, `changed-file map`, `candidate revision`, or
`slice assessment`. The always-loaded Local Profile rule that explains policy
selection is outside this loader boundary.

| Existing layer | Classification | Decision |
|---|---|---|
| Spacedock 0.26 stage extractor | `WORKING` | Reuse unchanged; it reliably returns the selected subsection. |
| Stage `Policy mods` declaration and parser | `WORKING` | Reuse as the activation source; the current contract test already rejects a body-only link as a declaration. |
| Implementation-stage activation wording | `EXISTS_BROKEN` | Repair this seam: it exposes an unlisted mod link without a stage-native activation trigger. |
| PR Delivery topology decision | `WORKING` | Reuse unchanged and load only when its candidate facts exist. |
| Q08 pressure corpus | `WORKING` | Reuse as the semantic RED/GREEN scenario; do not build another evaluation framework. |

No layer is `MISSING`. The reverse trace from the accepted outcome therefore
ends at one broken stage-text seam plus its existing contract test.

### Options considered

1. **Recommended — deferred locator with an explicit trigger.** Keeps the
   stage-entry read set small, preserves discoverability at implementation
   exit, and gives `show-stage-def` enough text to answer Q08 safely.
2. **Add `pr-merge` to `Policy mods`.** Rejected because it activates the whole
   PR lifecycle at the first implementation step and reproduces Q08's
   premature-load hard failure.
3. **Delete the inline link.** Rejected because the later topology decision
   would depend on authority outside the actual loader output.

Changing Spacedock to synthesize common-plus-stage bundles is broader than this
first slice and is not required to close the named activation defect.

## Design determination

`required` — change the implementation-stage contract, not the loader. At stage
entry, the worker reads the selected implementation subsection and
`_mods/work-control-profile.md`. Unlisted links are inactive locators. At
implementation exit, once the candidate revision, changed-file map, merge-base
diff size, and slice-dependency assessment exist, the PR-topology bullet
activates only `_mods/pr-merge.md#delivery-topology-decision`. Validation and
recovery keep their existing independent triggers.

## Acceptance criteria

**AC-1 — Stage-only activation is safe before the topology trigger.**

With the first RED recorded and no candidate facts, the effective read set is
the implementation subsection plus `work-control-profile` only. Verified by:
supply the exact Spacedock 0.26.0 implementation `show-stage-def` output plus
the existing Q08 facts to a fresh-context worker; the response leaves PR,
validation, and recovery procedures unread before continuing RED/GREEN.
Falsified by: the worker loads `_mods/pr-merge.md`, validation, or recovery
before any named trigger, or cannot determine the active read set from the
stage output.

**AC-2 — Deferred PR-topology activation remains reachable and regression-safe.**

The stage keeps one inactive PR locator and activates it only after its four
candidate facts exist. Verified by: the existing contract suite asserts that
implementation selects only `_mods/work-control-profile.md`, retains the exact
PR decision locator, and names the candidate facts that activate it; mutations
that add `pr-merge` to `Policy mods`, remove the trigger boundary, or remove the
locator each fail. Falsified by: PR policy becomes active at stage entry, or a
completed candidate cannot reach the authoritative topology table from the
stage output.

**AC-3 — The repair adds no workflow ceremony or parallel authority.**

The Q08 next-step route remains ordinary RED/GREEN with zero PR, validation,
recovery, or state actions. Verified by: the exact diff changes only
`docs/dev/README.md` and `scripts/kc-dev-flow-contract-test.py`; it adds no file,
stage, state field, review loop, Captain decision, loader, registry, or CI lane.
Falsified by: the repair requires any new approval/state transition or loads a
dormant procedure before its existing trigger.

**AC-4 — Delivery is one exact-head Draft PR.**

The bounded two-file change ships as one Draft PR targeting the then-current
`origin/main`. Verified by: its approved full candidate SHA equals GitHub
`headRefOid`, the approved base SHA is recorded, and required checks are
reported for that unchanged head. Falsified by: a second PR/stack is required,
the PR is made ready or merged without separate authority, or candidate/base
bytes change after approval without a fresh re-cut and approval.

## Test plan

1. Add the activation assertions to
   `scripts/kc-dev-flow-contract-test.py` before changing the README. On current
   `origin/main`, expect RED because the implementation stage has an unlisted
   PR link but no explicit inactive-before-trigger contract.
2. Make the minimum implementation-stage prose change and rerun the focused
   contract test to GREEN.
3. Prove three mutants fail: declare `pr-merge` as an implementation policy
   mod; remove the inactive-before-trigger rule; remove the topology locator or
   its candidate-fact trigger.
4. Run `/opt/homebrew/bin/spacedock dispatch show-stage-def` against the exact
   implementation head and exercise the existing Q08 scenario using only that
   output. Expected result: only the stage and `work-control-profile` are read
   before the next RED/GREEN step.
5. Run `python3 scripts/kc-dev-flow-contract-test.py`,
   `./scripts/skill-frontmatter-lint.sh`, and `git diff --check` at stage exit.

E2E scope: this is a docs/config-only runtime-loading contract. The real
Spacedock 0.26 extractor plus fresh Q08 pressure is the origin-runtime exercise;
there is no user-visible browser or full-stack path.

## Measurement

- Baseline: the current stage-only output is 227 words and leaves five Q08
  activation facts unstated; the principles-only ablation loaded PR policy too
  early in 3/3 Q08 repetitions.
- Target: the repaired stage-only output yields the correct Q08 read inventory
  in the bounded fresh-context exercise, while the pre-topology procedure count
  remains zero and the active stage mod count remains one.

### Appetite, one-worker scope, and pre-mortem

One worker, one implementation session, expected two changed files. Stop and
return to ideation if the repair requires changing Spacedock, a canonical
kernel/mod, another lifecycle stage, or delivery authority. Keep the explicit
activation boundary and the real-loader evidence if time is cut; the additional
mutants may be reduced to the two semantic extremes (premature activation and
lost locator).

If this design ships and still fails, the most likely cause is that the stage
text describes the rule but a fresh worker still treats Markdown readability as
authority. That result falsifies prose sufficiency and would justify returning
to design for a loader-enforced dependency representation; it does not justify
silently loading the whole PR mod.

## Doc diff

- `docs/dev/README.md`, implementation stage only: state that unlisted links
  are inactive locators; bind the PR decision link to the existing candidate
  facts at implementation exit.
- `PRODUCT.md` / `ARCHITECTURE.md`: no change. This repairs the local workflow's
  activation wording without changing product capability or architecture.

## Out of scope

Rewriting every stage, changing Spacedock, synthesizing a common-plus-stage
loader, changing the PR decision table or delivery authority, building a
general evaluation framework, adding CI, altering review/state/Captain
ceremony, modifying validation or recovery triggers, editing the historical
pressure artifacts, and making the Draft PR ready or merging it.

## Ideation EM judgment

One fresh-context GPT-5.6 High EM independently reviewed exact revision
`a18ba78f72c03036d8463629bd19977aa684e159`, the selected ideation policies,
the Spacedock 0.26.0 output, Q08, the alternatives, and this entity.

- `route: proceed`
- `confidence: high`
- `multi_model: not_needed`
- Evidence synthesis: the EM reproduced the implementation output hash
  `c85143915d110cd7937a967b9fed32fc4c799ec5ef151e9b24438bd15df23dad`
  and 27-line / 227-word / 1616-byte size. It confirmed that the output selects
  only `work-control-profile`, retains the PR locator, and omits both the
  inactive-link rule and the four candidate-fact trigger. It also confirmed the
  Q08 principles-only 3/3 premature-load failures and the existing contract
  test's ownership of policy parsing and locator preservation.
- Adjudication: the current loader-stage seam, deferred inactive locator, and
  existing-test placement are supported. Adding `pr-merge` to `Policy mods`,
  deleting the locator, and changing the loader in this slice are unsupported.
- Risk/trade-off: the bounded prose plus existing-test guard buys safe entry and
  later topology discovery without a new surface. Its residual risk is that a
  future worker may still misread prose; a loader-enforced representation is
  the concrete fallback only after fresh pressure disproves prose sufficiency.
- Recommendation: implement only the two named files, keep the implementation
  mod set exact, name all four trigger facts, and prove premature-load,
  inactive-trigger-loss, and locator-loss regressions before validation.
- Dissent: none.
- Disproof condition: return if repaired exact output still causes a fresh Q08
  worker to preload PR policy, cannot identify the sole entry mod, cannot reach
  topology after the four facts exist, or the two semantic extremes cannot be
  protected inside the two-file scope.
- Authority boundary: this is advisory. Gate Authority retains advancement;
  the captain retains workflow-policy approval, scope, Draft readiness, and
  merge authority; state, Spacedock, GitHub, CI, release, posting, and provider
  owners retain their existing actions.

## Stage Report: ideation

Verdict: **PROCEED** on the bounded two-file design; Gate Authority retains the
stage transition.

- DONE: Bound the runtime to fresh `origin/main`
  `a18ba78f72c03036d8463629bd19977aa684e159` and installed
  `/opt/homebrew/bin/spacedock` 0.26.0 (contract 3).
- DONE: Proved the stage-only load boundary. The implementation extraction is
  27 lines / 227 words, selects only `work-control-profile`, and exposes the PR
  locator without the Q08 activation boundary.
- DONE: Reused the reverse-recovery and ablation evidence. The loader, policy
  declaration parser, PR decision table, and Q08 corpus are working; only the
  implementation-stage activation seam is broken.
- DONE: Selected the smallest design from three options. Keep the PR link as a
  deferred locator, state its candidate-fact trigger in the selected stage, and
  protect both premature-load and lost-locator regressions in the existing
  contract test.
- DONE: Defined end-state ACs and falsifiers for activation safety, regression
  safety, no added ceremony, and one exact-head Draft PR.
- DONE: Sized one worker and two files, recorded the docs/config E2E reason,
  pre-mortem, stop boundary, explicit non-goals, doc diff, RED pressure
  scenario, and what would falsify prose sufficiency.
- DONE: Obtained the single required fresh-context EM judgment. It returned
  `proceed / high`, found no dissent, and did not recommend another model.

### Summary

Proceed with one stage-native deferred-activation sentence, one sharpened
topology trigger, and existing-test coverage. Keep `pr-merge` inactive until
candidate facts exist; add no loader, policy surface, or ceremony.

## Stage Report: implementation

Verdict: **IMPLEMENTATION EVIDENCE COMPLETE** for candidate
`47a7dac7a2417aedb1a326b6dcc6fcf4d3a3206e`; Gate Authority retains the
transition to validation.

- DONE: Started from `origin/main`
  `a18ba78f72c03036d8463629bd19977aa684e159`. The executable test-only RED
  failed with `missing inactive locator rule`, all four missing candidate-fact
  triggers, and `missing pre-trigger unread boundary` before README changes.
- DONE: Implemented only `docs/dev/README.md` and
  `scripts/kc-dev-flow-contract-test.py`. The implementation `Policy mods`
  declaration remains exactly `_mods/work-control-profile.md`; unlisted links
  are inactive locators, and the PR locator stays unread until candidate
  revision, changed-file map, merge-base diff size, and independent/dependent
  slice assessment all exist.
- DONE: Proved the three executable mutations fail after first confirming each
  mutation changed its input: `premature-load` -> `implementation entry policy
  mods drifted`; `trigger-loss` -> `missing pre-trigger unread boundary`;
  `locator-loss` -> `missing topology locator`.
- DONE: Mapped the exact two-file diff to ACs.
  `docs/dev/README.md` serves AC-1, AC-2, and AC-3; the contract test serves
  AC-2 and AC-3. No changed file is unmapped.
- DONE: Re-ran the real installed loader on the exact candidate with Spacedock
  `0.26.0 (contract 3)`. Output SHA-256 is
  `4f10401f127e77cf12bf23d7fcf70b626e082eca2f4579d3a76468dc1bf7a965`;
  size is 33 lines / 269 words / 1934 bytes. The bytes embedded in every Q08
  input equal that extraction exactly.
- DONE: Reused Q08 from `.context/experiments/dev-flow-full-pressure/ablation/prompts.md:79-88`
  and its discriminator from `RUBRIC.md:47-56`; the historical no-policy RED
  answer was not supplied to the runners. Claude Code 2.1.227 was unavailable
  because its session limit was reached, so three fresh Codex CLI sessions ran
  honestly instead of fabricating Claude receipts.
- DONE: The frozen Q08 input SHA-256 is
  `13333b94d374cea9cb2abc857cca54a5c24d11bb7f2b4fb6baa94c1b7e84b283`.
  Runner was Codex CLI 0.145.0 using native binary SHA-256
  `1da3f4e0e96028b8a771814293c3033dafd1971f943f6c7e79b0897fe705f590`;
  model was `gpt-5.6-sol` (string SHA-256
  `419255f2bb4c6801939e868fe2cdbbdc34d51742400939d1842d262a1fec749c`),
  reasoning `high`, read-only sandbox, `--ephemeral`, ignored user config and
  repo rules, and no tool use. All three satisfied Q08's required behavior:
  read the stage plus declared implementation mod only, leave trigger
  procedures unloaded, then continue RED/GREEN.

### Fresh Q08 receipts

Trial 1 session `019ff453-c064-7262-8d29-68a745d1c816`; exact output SHA-256
`040ec192c8544223428d260347c1402526831f6a9d54108d94189585d3abf83c`:

```text
## READ NOW

- `implementation` stage instructions
- Declared active policy mod: `_mods/work-control-profile.md`
- Q-08 scenario facts, including the recorded failing RED behavior check

## UNREAD NOW

- `_mods/pr-merge.md`, including `#delivery-topology-decision`; its four prerequisites do not yet exist
- Adjacent validation and recovery procedures
- Any other linked but undeclared policy material

## NEXT WORK STEP

Write the minimum implementation change for the failing behavior check, then run it to record GREEN in the same session.
```

Trial 2 session `019ff454-6c87-7322-8041-cbb0187d8df7`; exact output SHA-256
`2ccaa19924ac1faf930a7a8ca605e44ae71864ad360a029842b3fdfe737dfb12`:

```text
## READ NOW

- The `implementation` stage instructions.
- The active policy mod: `_mods/work-control-profile.md`.
- Q-08 scenario facts, including the recorded failing RED check.

## UNREAD NOW

- `_mods/pr-merge.md`, including `#delivery-topology-decision`; its trigger facts do not yet exist.
- Adjacent validation and recovery procedures.
- Any unlisted linked policy.

## NEXT WORK STEP

Write the minimum change for the failing behavior, then run the scoped check to record GREEN in the same session.
```

Trial 3 session `019ff454-6c86-7a32-973c-ca7c736c94ab`; exact output SHA-256
`ddce7c3fe655b50dc057072aa276cf790a2aedacbc54f96fda751740f48c504e`:

```text
## READ NOW

- `implementation` stage instructions
- Active policy mod: `_mods/work-control-profile.md`
- Q-08 facts, including the recorded failing RED behavior check

## UNREAD NOW

- `_mods/pr-merge.md`, including `#delivery-topology-decision`; its four prerequisites do not yet exist
- Adjacent validation and recovery procedures
- Any inactive, undeclared policy locators

## NEXT WORK STEP

Write the minimum implementation change needed to make the recorded RED behavior check pass, then record GREEN in the same session.
```

### Exit gates and topology

- `python3 scripts/kc-dev-flow-contract-test.py` -> `kc-dev-flow contract: PASS`.
- `./scripts/skill-frontmatter-lint.sh` -> 40/40 skill directories valid.
- `git diff --check origin/main...HEAD` -> exit 0, no output.
- Worktree is clean at the candidate commit.
- Merge-base diff is 82 additions + 2 deletions across 2 files. The README
  contract and its regression test form one inseparable behavior; dependent
  green layers = no, independent green slices = no, numeric trigger = no.
  After the four exit facts existed, the deferred locator selected the
  `One Draft PR` row. This is an implementation recommendation only; no PR was
  created and no delivery authority was exercised.
- Dispatch metadata drift: the supplied state checkout path under the code
  worktree did not exist, and its claim that the actual state checkout had no
  `origin` was stale. The captain confirmed the actual split-root entity path
  and directed the shipped `spacedock state commit` transaction; this is not a
  product-scope change.

### Summary

Made implementation activation loader-native with a deferred PR topology
locator, protected entry/trigger/locator behavior with executable mutations,
and obtained 3/3 fresh exact-loader Q08 receipts without adding workflow
ceremony or another policy surface.

## Stage Report: validation

- DONE: Adversarially verify all four ACs on exact candidate 47a7dac7a2417aedb1a326b6dcc6fcf4d3a3206e, including the actual Spacedock loader and Q08 receipts.
- DONE: Challenge both added surfaces with without-it evidence and verify no authority, ceremony, stage, loader, mod, or unrelated-policy expansion.
- DONE: Run the full relevant gates, obtain one fresh-context EM verdict, and return PASSED or concrete findings without modifying candidate files.

Verdict: **PASSED** for exact candidate
`47a7dac7a2417aedb1a326b6dcc6fcf4d3a3206e` against exact base
`a18ba78f72c03036d8463629bd19977aa684e159`; Gate Authority retains the
transition and delivery remains separately authorized.

- **AC-1 PASS:** The installed `/opt/homebrew/bin/spacedock` 0.26.0
  `(contract 3)` extracted the exact candidate's implementation subsection as
  33 lines / 269 words / 1934 bytes with SHA-256
  `4f10401f127e77cf12bf23d7fcf70b626e082eca2f4579d3a76468dc1bf7a965`.
  A validator-owned fresh Q08 run read only the stage, the declared
  `_mods/work-control-profile.md`, and the RED fact; it left PR, validation,
  and recovery procedures unread and selected the minimum GREEN step next.
- **AC-2 PASS:** The implementation declaration still selects only
  `_mods/work-control-profile.md`. Direct execution rejected `premature-load`
  with `implementation entry policy mods drifted`, `trigger-loss` with
  `missing pre-trigger unread boundary`, and `locator-loss` with
  `missing topology locator`. Once the four candidate facts existed, the
  retained locator reached the unchanged Delivery topology decision.
- **AC-3 PASS:** The merge-base diff is exactly 82 additions and 2 deletions
  across `docs/dev/README.md` and
  `scripts/kc-dev-flow-contract-test.py`. No file, stage, state field, loader,
  mod, registry, CI lane, review loop, approval, Captain decision, or parallel
  authority was added. Q08 adds zero pre-trigger ceremony events.
- **AC-4 PASS at the validation boundary:** Fresh remote observation kept
  `origin/main` at the approved base, HEAD and merge-base remained exact, and
  the unchanged topology table selected `One Draft PR` from dependent layers
  `no`, independent slices `no`, and numeric trigger `no` (84 gross changed
  lines, 2 files). No remote branch or PR exists because validation had no
  delivery authority. Hosted `headRefOid` and required checks are fail-closed
  delivery-time receipts: any candidate/base drift requires a new cut,
  validation, and approval.

### Evidence block

Lenses: behavior PASS 0 findings; contract/schema PASS 0; runtime/platform PASS 0; docs/policy PASS 0; delivery PASS 0 | Inputs: exact two-file merge-base diff, installed Spacedock extraction, Q08 source/rubric and four receipts, exact topology table, remote base/head/PR observations | Falsifiers exercised: premature activation, trigger loss, locator loss, undeclared reads, added ceremony, and candidate/base drift | state/concurrency and security/privacy did not fire on this activation-only diff
Diff coverage: 100% (8/8 coverable added README behavior lines); the 74 added test-evidence lines are outside the product-behavior denominator and executed in the passing contract suite
Adversarial: PASS — removing the README surface while retaining the guard returned exit 1 with all named activation gaps; removing the new guard let a trigger-loss prose mutant pass the prior suite; all three focused mutants failed for their intended reasons
Cross-model: not_needed — the sole fresh-context GPT-5.6 High EM returned `proceed / high`, no blocking or unresolved finding, and no recommendation for another model
E2E: N/A — the ideation-approved scope is a docs/config-only runtime-loading contract; the installed Spacedock extractor plus fresh Q08 pressure is the origin-runtime exercise
Origin re-observation: PASS — Reported scenario: a readable unlisted PR locator was treated as active before its trigger | Originating runtime kind: installed Spacedock 0.26.0 stage extractor followed by a fresh worker activation decision | Re-observation artifact/revision: implementation output SHA-256 `4f10401f127e77cf12bf23d7fcf70b626e082eca2f4579d3a76468dc1bf7a965` at `47a7dac7a2417aedb1a326b6dcc6fcf4d3a3206e`, fresh Codex session `019ff45f-8563-7c90-8030-a90289c7c299` | Equivalent-runtime rationale: same installed extractor, exact stage bytes, original Q08 facts, GPT-5.6 High fresh read-only worker, ignored user config/rules, and no tool calls matched the claim-producing chain | Falsifier kind: mutation | Result: the worker kept PR, validation, and recovery unread and continued only RED/GREEN

### Receipt and gate audit

- Independently inspected all three implementation Q08 bodies and recomputed
  their exact output hashes without trusting the summary: trial 1
  `040ec192c8544223428d260347c1402526831f6a9d54108d94189585d3abf83c`,
  trial 2
  `2ccaa19924ac1faf930a7a8ca605e44ae71864ad360a029842b3fdfe737dfb12`,
  and trial 3
  `ddce7c3fe655b50dc057072aa276cf790a2aedacbc54f96fda751740f48c504e`.
  Each independently retained the same safe read inventory and next step.
- Reproduced the test-only RED by pairing the base README bytes with the
  candidate test bytes. It failed on the inactive-locator rule, all four
  candidate facts, and the pre-trigger unread boundary before any candidate
  behavior prose was present.
- `python3 scripts/kc-dev-flow-contract-test.py` ->
  `kc-dev-flow contract: PASS`.
- `./scripts/skill-frontmatter-lint.sh` -> 40/40 skill directories valid.
- `git diff --check
  a18ba78f72c03036d8463629bd19977aa684e159...47a7dac7a2417aedb1a326b6dcc6fcf4d3a3206e`
  -> exit 0, no output.
- Changed-file mapping is complete: `docs/dev/README.md` serves AC-1, AC-2,
  and AC-3; `scripts/kc-dev-flow-contract-test.py` serves AC-2 and AC-3.
  AC-4 is the exact-head delivery predicate over the same inseparable slice.

### Science Officer EM judgment

The single fresh EM returned a high-confidence pass with no blocking or
unresolved finding. Its raw response used a non-canonical field layout despite
the closed-schema instruction; the record below is a lossless normalization of
that same judgment and adjudications, not a second review.

```yaml
science_officer_em_upward_report:
  em_judgment: "Candidate 47a7dac7a2417aedb1a326b6dcc6fcf4d3a3206e passes validation; AC-4 hosted evidence is a fail-closed delivery-time receipt, not a validation blocker."
  evidence_synthesis: "Exact head/base, the two-file AC mapping, installed Spacedock extraction, four of four bounded Q08 passes, RED/GREEN and without-it evidence, three rejected mutants, fresh full gates, and the no-ceremony audit support the candidate with no Material residual finding."
  risk_tradeoff_call: "The bounded prose plus regression guard buys safe stage-entry loading and later topology reachability at the cost of two local surfaces; future model misreading remains a monitored residual, and loader-enforced dependency representation is the concrete alternative only after fresh falsification."
  recommendation: "Pass validation and proceed only to captain-owned exact-head Draft delivery; revalidate and obtain fresh approval on any candidate or base drift."
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: "FO may report evidence and perform authorized delivery mechanics only; Gate Authority owns the transition and the Captain owns scope, Draft readiness, and merge."
  engineering_judgment:
    question: "Should exact candidate 47a7dac7a2417aedb1a326b6dcc6fcf4d3a3206e pass validation and proceed to captain-owned Draft delivery against exact base a18ba78f72c03036d8463629bd19977aa684e159?"
    revision: "47a7dac7a2417aedb1a326b6dcc6fcf4d3a3206e against a18ba78f72c03036d8463629bd19977aa684e159"
    evidence_synthesis: "Exact head/base, the two-file AC mapping, installed Spacedock extraction, four of four bounded Q08 passes, RED/GREEN and without-it evidence, three rejected mutants, fresh full gates, and the no-ceremony audit support the candidate with no Material residual finding."
    adjudications:
      - finding: "Exact scope and AC mapping"
        disposition: supported
        basis: "The clean merge-base diff has only the two mapped files, unchanged stage inventory and implementation mod set, and no prohibited policy, authority, state, loader, registry, CI, or ceremony surface."
      - finding: "Origin-runtime Q08 closure"
        disposition: supported
        basis: "The same installed Spacedock extractor and exact candidate stage bytes produced four of four fresh worker decisions that retained the declared-only read set and continued RED/GREEN."
      - finding: "Without-it irreducibility"
        disposition: supported
        basis: "Removing the README caused named AC failures, while removing the new guard allowed trigger-loss to pass the prior suite; all three focused mutants were rejected."
      - finding: "AC-4 hosted evidence is a validation blocker"
        disposition: unsupported
        basis: "The one-Draft topology and exact local/remote heads are proven now; hosted headRefOid and checks cannot exist before separately authorized delivery and must fail closed at that later boundary."
      - finding: "Prose sufficiency remains a Material blocker"
        disposition: unsupported
        basis: "Four independent bounded runtime observations and executable assertions reduce future misreading to a monitored residual; a fresh contrary origin observation would return the design to a loader-enforced representation."
    risk_tradeoff: "The bounded prose plus regression guard buys safe stage-entry loading and later topology reachability at the cost of two local surfaces; future model misreading remains a monitored residual, and loader-enforced dependency representation is the concrete alternative only after fresh falsification."
    recommendation: "Pass validation and proceed only to captain-owned exact-head Draft delivery; revalidate and obtain fresh approval on any candidate or base drift."
    route: proceed
    confidence: high
    dissent: "none"
    disproof_condition: "Return to design if exact loader output causes a fresh worker to preload PR, validation, or recovery policy, cannot identify the sole entry mod, cannot reach topology after all four facts, or if candidate/base drift invalidates the approved delivery packet."
    authority_boundary: "Gate Authority retains validation advancement; the Captain retains workflow-policy approval, scope, Draft readiness, and merge; delivery and provider owners retain push, PR, CI, GitHub, posting, and release actions."
```

### Validation checklist and AC citations

Evidence for AC-1: loader-native validation receipt at `loader-native-stage-contract.md:412-418`; installed-runtime origin re-observation at `loader-native-stage-contract.md:446`; independently hashed Q08 receipts at `loader-native-stage-contract.md:450-457`.

Evidence for AC-2: activation and locator verdict at `loader-native-stage-contract.md:419-424`; focused adversarial result at `loader-native-stage-contract.md:443`; without-it RED at `loader-native-stage-contract.md:458-461`.

Evidence for AC-3: exact two-file and no-ceremony verdict at `loader-native-stage-contract.md:425-429`; fired-lens and adversarial receipts at `loader-native-stage-contract.md:441-444`; changed-file mapping at `loader-native-stage-contract.md:468-470`.

Evidence for AC-4: exact-head/topology and delivery-boundary verdict at `loader-native-stage-contract.md:430-437`; EM adjudication of the hosted delivery-time receipt at `loader-native-stage-contract.md:503-505`.

### Summary

Passed the exact two-file candidate with fresh loader-native Q08 evidence,
independent receipt verification, executable RED/GREEN and without-it pressure,
complete relevant gates, no added ceremony or authority, and one high-confidence
EM recommendation. Delivery remains one separately authorized exact-head Draft
PR and must fail closed on any candidate or base drift.
