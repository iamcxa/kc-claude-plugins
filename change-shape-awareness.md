---
title: Integrate outcome-first subtraction with change-shape awareness
status: validation
source: Captain-approved kc-dev-flow/S1 extension after Fable 5 challenge, 2026-08-11
product: kc-dev-flow
sprint: S1
design: required
lane: main
started: 2026-08-11T03:53:06Z
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-change-shape-awareness
pr:
id: 5ecpkp81k2p7gh0sss3w9qxn
pr_artifact_v1: eyJhdWRpdF9saW5rIjoiWzVlXSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvMmNiMjk0MWYyMzM0NzYzZDRjNjU1YjQ0YzMxMWQ0MTY5ZmQ5MjcwMS9jaGFuZ2Utc2hhcGUtYXdhcmVuZXNzLm1kKSIsImJhc2UiOiJtYWluIiwiYmFzZV9vaWQiOiIxZGI3ZTc3Mjk1OTViMDkwNzE1OTQzZGE1NDRhMGY4MzI3OTEyYzA1IiwiYm9keSI6IkV4cG9zZSBvbmUgcG9zdC1pbXBsZW1lbnRhdGlvbiBzdWJ0cmFjdGlvbiBxdWVzdGlvbiB3aXRob3V0IGxldHRpbmcgbGluZSBjb3VudHMgZ292ZXJuIGRlbGl2ZXJ5LlxuXG4jIyBXaGF0IGNoYW5nZWRcblxuLSBPcmRlciBicm93bmZpZWxkIHdvcmsgZnJvbSBhY2NlcHRlZCBvdXRjb21lIHRocm91Z2ggZnJlc2ggdmFsaWRhdGlvbi5cbi0gRGVmaW5lIG1pbmltdW0gYnkgbGlmZWN5Y2xlIHJlc3BvbnNpYmlsaXR5LCBub3QgbGluZXMuXG4tIFJlY29yZCBncm9zcyBjaGFuZ2Ugc2hhcGUgYXMgb2JzZXJ2ZS1vbmx5IGV2aWRlbmNlLlxuLSBFeGVyY2lzZSBwcmVjZWRlbmNlLCBhbnRpLWdhbWluZyBib3VuZGFyaWVzLCBhbmQga2VybmVsIHBhcml0eS5cblxuIyMgRXZpZGVuY2VcblxuLSA0LzQgYWNjZXB0YW5jZSBjcml0ZXJpYSBwYXNzZWQgYXQgYDU0ZjM5NGRgLlxuLSA1LzUgcmVxdWlyZWQgcmVwb3NpdG9yeSBjaGVja3MgcGFzc2VkOyBPcHVzIEhpZ2ggZm91bmQgMCBNYXRlcmlhbCBpc3N1ZXMuXG5cbi0tLVxuWzVlXSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvMmNiMjk0MWYyMzM0NzYzZDRjNjU1YjQ0YzMxMWQ0MTY5ZmQ5MjcwMS9jaGFuZ2Utc2hhcGUtYXdhcmVuZXNzLm1kKVxuIiwiYm9keV9zaGEyNTYiOiIzOWZhNjBmZGM1NzE2YTBiM2ViZWU1MDY3NzVjMDQ5MWY4NzcxMzcwNjUxNDY0OTQwYmU2MmEwODAzNjM0NWMwIiwiZGlmZl9zaGEyNTYiOiJiZmRjYzA3MzdkZWRjMDBjNzc0NWEwMDhjMDQzYWVkOTdjNDdiYWYxNDI5YjdkYTFmZDRjNWIwNTFjNzZlMjU0IiwiaGVhZCI6InNwYWNlZG9jay1lbnNpZ24vY2hhbmdlLXNoYXBlLWF3YXJlbmVzcyIsImhlYWRfb2lkIjoiNTRmMzk0ZGVkMmZlOTA0ODFjMTdkYjQ0NjZjNGNkZDZlMzYwMWZiYyIsImxpdmVfcGF0aCI6ImNoYW5nZS1zaGFwZS1hd2FyZW5lc3MubWQiLCJyZXBvIjoiaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zIiwidGl0bGUiOiJmZWF0KGtjLWRldi1mbG93KTogYWRkIGNoYW5nZS1zaGFwZSBvYnNlcnZhdGlvbiJ9
mod-block: pr-merge:product-draft:v1:121f56ca827524e419653507d75ff5c4c5b305cc2653db6a3e6b5a534e982a04
---

kc-dev-flow already governs accepted outcomes, reverse recovery, bounded subtraction, and without-it validation, but it does not expose removable mass inside AC-mapped files after implementation. Integrate these principles in one unambiguous order and trial categorized gross change shape as observation only, so agents ask what can still be removed without optimizing LOC at the expense of correctness, tests, clarity, or accepted value.

## Problem

The shipped kernel has all of the necessary decisions, but they are distributed:
accepted outcomes are defined before the subtractive rule, reverse recovery is a
separate audit, RED/GREEN lives in implementation, and changed-file-to-AC
mapping happens before validation. A worker can therefore obey each clause and
still read the sequence as greenfield decomposition followed by additive
implementation. After the diff exists, the workflow exposes no independent
question about a large responsibility hidden inside an otherwise AC-mapped file.

The correction must not turn line counts into a goal. A smaller diff can be
less correct, a test or assertion can be the most valuable part of a change,
and gross deletion does not cancel gross addition. The accepted experiment is a
questioning aid after implementation, not another delivery authority.

## Captain-authored outcome and boundaries

The dispatch and Fable 5 challenge answer the stage scope questions:

- **Protected value:** non-trivial brownfield work reaches the accepted outcome
  through recovered seams and justified lifecycle responsibilities, then gets
  one last chance to discover a real subtraction before fresh validation.
- **Keep if cut:** the accepted outcome, value ACs, constraints, non-goals,
  tests, safety, clarity, and fresh exact-revision validation.
- **Explicit non-goals:** LOC targets or bands, variance triggers, soft or hard
  numeric gates, agent/PR ranking, addition/deletion offsets, cross-change
  competition, a new control framework, and number-driven deletion.
- **Assumption most likely to be wrong:** existing reverse recovery plus
  changed-file-to-AC mapping may already ask every useful subtraction question,
  making post-diff change shape redundant.
- **Trial appetite:** three comparable non-trivial brownfield changes,
  observe-only. If about five comparable changes reveal no new question beyond
  existing AC mapping, retire the mechanism as redundant.

Implementation is sized as one documentation/contract worker: estimate 60
minutes with a 30-minute tolerance. Stop and re-cut at 90 minutes, on any need
for a new file or capability, or when the five-file candidate set cannot carry
the contract. Do not extend the budget by weakening RED/GREEN or validation.

## End value

kc-dev-flow states and exercises one order:

1. **Accepted outcome.** Name the end value, value-level ACs, constraints, and
   non-goals. Decompose from this contract without assuming the implementation
   is absent or that the task is a greenfield rebuild.
2. **Recover the existing seam.** Against fresh `origin/main`, classify the
   existing abstraction and repair the cheapest compatible `EXISTS_BROKEN` or
   `STUB` seam. Only evidence-backed absence supports `MISSING`.
3. **Prove subtraction or bypass.** For the candidate surfaces, try the cheapest
   reversible without-it instrument. A named AC failure can bound retention of
   an existing surface. Green evidence with closed need and observation
   boundaries creates a captain-owned removal candidate. `UNKNOWN` preserves an
   existing surface and proves neither necessity nor removability.
4. **Authorize only necessary addition.** A proposed new responsibility can
   advance when its absence fails a named AC and the recorded simpler route is
   insufficient. Green or `UNKNOWN` returns the proposal.
5. **Run RED/GREEN.** Demonstrate the accepted behavior failing before the
   minimum implementation and passing after it. A subtraction prompted later
   returns through the same without-it and GREEN evidence; numbers do not
   authorize it.
6. **Observe post-diff change shape.** At the implemented revision, retain
   mechanically sourced gross additions and gross deletions as separate facts,
   then ask unconditionally: **“If the largest added responsibility is removed,
   which named AC fails?”** Counts may focus inspection; they do not choose the
   responsibility or supply the answer.
7. **Validate fresh.** Re-run the accepted evidence against the final exact
   revision after any resulting subtraction. Prior evidence does not bind a
   changed head.

Here, **minimum** means the fewest independently maintained lifecycle
responsibilities sufficient for the accepted outcome, not the fewest files or
lines. **Simple** means the direct sufficient route with the least lifecycle and
maintenance obligation, not dense code. **Change shape** is post-diff evidence,
not a forecast, budget, score, or gate.

## Reverse recovery against fresh `origin/main`

Audit revision: `54913dda3e5e66841e043025bf646e0ad2493bc9` fetched on
2026-08-11.

| Existing surface | Completeness | Need | Evidence and decision |
|---|---|---|---|
| Portable outcome/subtraction contract | `WORKING_UNIT_UNPROVEN` | `REQUIRED` | `kc-dev-flow/references/kernel.md:112-152` already owns accepted outcomes, reverse recovery, and tri-state without-it decisions. Extend this clause in place; a new mod would duplicate authority. |
| Reverse-recovery audit | `WORKING` | `REQUIRED` | `kc-dev-flow/references/reverse-recovery-audit.md:26-98` already owns completeness, need, bounded absence, and captain disposal. Reuse unchanged. |
| Installed runtime route | `WORKING` | `REQUIRED` | `kc-dev-flow/skills/continue-dev-flow/SKILL.md:14-30` loads the adopted kernel and stage-selected local mods. No skill edit or loader is needed. |
| Local stage contract | `EXISTS_BROKEN` | `REQUIRED` | `docs/dev/README.md:187-200,215-229,257-262` has pre-add subtraction, RED/GREEN, AC mapping, and validation re-challenge, but no post-diff observation or trial packet. Repair those existing stage seams. |
| Contract enforcement | `WORKING_UNIT_UNPROVEN` | `REQUIRED` | `scripts/kc-dev-flow-contract-test.py:635-704` checks kernel invariants, the absolutes registry, and canonical/vendor byte identity. Extend the existing assertions; do not add a checker. |
| Product and architecture summaries | `WORKING` | `REQUIRED` | `PRODUCT.md:40-44` and `ARCHITECTURE.md:7-15,36-39` remain accurate without a diff. They do not describe stage-level subtraction or observation, so changing them would not make an AC pass. |

Disproof hook: if fresh `origin/main` gains a complete ordered sequence and
post-diff observe trial before implementation starts, the premise collapses and
the worker returns to ideation rather than layering duplicate wording.

## Design determination

`required` — this decides the order and meaning of a portable workflow contract,
the local stage at which post-diff observation runs, and the evidence envelope
handed to fresh validation. It adds no interface, schema, or runtime component.

## Proposed contract diff

- **Portable kernel, before:** outcome, reverse recovery, subtraction, and
  validation are individually normative but not named as one ordered route;
  post-diff responsibility inspection is absent. **After:** one sequence states
  the seven decisions above and a bounded observation paragraph defines separate
  gross counts, the unconditional question, and the no-verdict boundary.
- **Local README, before:** implementation ends with RED/GREEN and changed-file
  AC mapping; validation re-challenges retained additions. **After:** the
  three-change cohort records its raw post-diff packet between GREEN and fresh
  validation, and any resulting edit returns through without-it proof and GREEN.
- **Existing contract test, before:** kernel invariants and byte identity are
  enforced, but removing or reordering the new route would remain green.
  **After:** position-sensitive assertions RED on a missing/reordered step and
  assert the question, observe-only boundary, trial outcomes, and local stage.

## Approach decision

### Chosen — extend the existing kernel, local stage contract, and contract test

This is the smallest route that serves both portable adopters and this
repository's first observe-only trial. It adds no runtime component and uses the
same files already loaded or checked by the product.

### Rejected — local README-only trial

This is the fastest edit, but it leaves the portable kernel's sequence
ambiguous and makes the learned rule local to one adopter. AC-1 would fail for a
new adopter even if this repository's trial worked.

### Rejected — change-shape mod, script, schema, gate, store, or runbook

An explicit subsystem could collect and compare numbers, but no accepted AC
requires persistent metrics or delivery enforcement. It creates a lifecycle
responsibility whose absence is currently green and increases the exact
number-management risk the trial is meant to detect.

Taking the cheap path: amend existing documentation and its existing mechanical
contract; do not build a change-shape capability.

## Exact candidate file set and without-it results

| Proposed file change | Responsibility | Without-it result |
|---|---|---|
| `kc-dev-flow/references/kernel.md` | State the portable ordered sequence, operational definitions, observation boundary, and unconditional question. | Existing `continue-dev-flow` consumers receive no portable post-diff rule; an adopter can complete AC mapping without answering the question. AC-1 and AC-2 fail. |
| `docs/dev/_mods/kernel.md` | Keep this repository's adopted kernel byte-identical to the canonical package reference. | The existing contract test fails canonical/vendor identity, and this repository does not run the newly accepted kernel. AC-1 and AC-4 fail. |
| `docs/dev/README.md` | Bind the three-change observe trial to implementation/validation, its evidence packet, return path after a subtraction, and number-management stop conditions. | The kernel has portable semantics but no local stage records the trial cohort or forces the post-diff question. AC-2 and AC-3 fail. |
| `scripts/kc-dev-flow-contract-test.py` | RED-before-GREEN assertions for the ordered invariant, observe-only prohibitions, required question, local stage placement, and canonical/vendor identity. | The current suite stays green when the new clauses are removed or reordered; the durability claim has no mechanical falsifier. AC-1 through AC-4 fail. |
| `kc-dev-flow/references/absolutes.registry` | Re-disposition the edited kernel block and correct every shifted `kernel.md:<line>` locator required by the existing absolute-claim contract. | Editing the existing absolute-bearing block makes `absolutes-check.py` fail with a missing digest and stale digest; leaving shifted locators would make its review notes false. AC-4 fails. |

No other file is authorized. In particular, without changes to
`reverse-recovery-audit.md`, `kc-dev-flow/README.md`, `continue-dev-flow`,
`PRODUCT.md`, `ARCHITECTURE.md`, CI, or a new artifact, all named ACs still have
a sufficient consumer and falsifier. Those edits are returned as unnecessary.

## Observe-only trial contract

For each of three comparable non-trivial brownfield changes, after RED/GREEN and
before fresh validation, retain this bounded packet in the existing work-item
report:

- exact merge base and implemented head;
- raw per-file output from `git diff --numstat <base>...<head>` (or the
  provider's equivalent mechanically sourced gross additions/deletions), with
  additions and deletions separate and no net score;
- the existing changed-file-to-AC mapping;
- the unconditional question and the named AC/failure instrument in the answer;
- disposition: new subtraction/question, defense already established by AC
  mapping, or `UNKNOWN`; and
- any number-management incident, its concrete diff evidence, and stop action.

The worker or reviewer identifies an independently maintained responsibility
from the diff and Route discipline; line count does not select it. A prompted
deletion of a test, assertion, safety check, or clarifying code needs the same
without-it failure evidence as any other deletion.

The trial has these falsifiable outcomes:

- **Success:** at least one concrete subtraction is attributable to the
  post-diff question and was not already found by reverse recovery or
  changed-file-to-AC mapping, with zero number-management incidents.
- **No incremental value:** two of the three changes produce only defenses of
  decisions already demanded by existing AC mapping.
- **Immediate stop/removal:** any confirmed incident where a count caused
  padding, compression, responsibility splitting/relabeling, unsafe deletion,
  test/assertion/clarity deletion without without-it proof, addition/deletion
  offsetting, or avoidance of a necessary addition.
- **Redundancy retirement:** if roughly five comparable changes yield no new
  question beyond existing AC mapping, retire the observation as redundant.
  This is a policy-review decision, not a delivery result for the fifth change.

Numbers can trigger the one question. They cannot PASS/FAIL a change, rank an
agent or PR, offset additions with deletions, redefine accepted value, or
override necessary tests, safety, clarity, and maintenance obligations. Trial
rows are not compared competitively across changes.

## Acceptance criteria

**AC-1 — Brownfield work follows one outcome-first order.**

The adopted contract orders accepted outcome, fresh reverse recovery,
reversible subtraction or bypass, evidence-backed necessary addition,
RED/GREEN, post-diff observation, and fresh validation. `UNKNOWN` preserves an
existing surface but cannot retain a proposed addition or prove irreducibility.
Verified by: RED/GREEN mutations in `scripts/kc-dev-flow-contract-test.py` that
remove or reorder each required clause, canonical/vendor byte identity, and a
fresh exact-revision reviewer walking an existing broken seam plus a proposed
new responsibility. Falsified by: either scenario reaching addition before the
prior evidence, or by a green/`UNKNOWN` absence retaining the proposal.

**AC-2 — Change shape asks one question and owns no verdict.**

After the implemented diff exists, the packet records mechanically sourced
gross additions and deletions separately and asks “If the largest added
responsibility is removed, which named AC fails?” Counts do not gate, rank,
offset, forecast, or override accepted value, tests, safety, or clarity.
Verified by: contract-test mutations removing the question or one prohibition,
plus adversarial packets for a necessary large addition, a deletion-heavy diff,
and a test-heavy diff. Falsified by: a number changing a delivery verdict or
authorizing a deletion without the normal without-it evidence.

**AC-3 — The bounded trial can prove value or redundancy.**

The existing work-item authority can record three comparable trials, attribute
a newly found subtraction, identify two-of-three defense-only failure, stop on
one confirmed number-management incident, and retire after roughly five
changes with no question beyond existing AC mapping. None becomes a per-change
delivery gate.
Verified by: a fresh reviewer evaluates four synthetic cohort tables against
the local README: success, defense-only failure, immediate incident stop, and
redundancy retirement. Falsified by: an ambiguous cohort disposition, a missing
attribution boundary, or a trial outcome blocking an otherwise accepted change.

**AC-4 — The first implementation stays on existing contract surfaces.**

The diff is limited to the five files above, creates no runtime/store/schema/job
or new documentation surface, keeps the two kernel copies byte-identical,
preserves accurate absolute-registry locators, and leaves necessary tests and
clarity outside numeric optimization.
Verified by: `git diff --name-status <base>...<head>`, the full existing
`scripts/kc-dev-flow-contract-test.py`, `absolutes-check.py`, byte comparison,
`git diff --check`, and a fresh changed-file-to-AC review. Falsified by: an
unmapped sixth file, a new capability, mirror drift, a stale locator, or a
count-motivated deletion without without-it evidence.

## RED/GREEN and validation plan

1. Add existing-contract-test assertions for the canonical order, observation
   boundary, unconditional question, trial outcomes, and local stage placement.
   Record the pre-doc RED failures.
2. Amend the canonical kernel and local README, copy the kernel byte-for-byte to
   the adopted mod, and update the standing absolutes registry. Record GREEN on
   the focused contract test.
3. Run the complete kc-dev-flow contract and existing relevant repository
   checks, then prove the exact five-file diff and separate gross additions and
   deletions mechanically.
4. Have a fresh exact-revision reviewer exercise the existing-seam/new-surface
   sequence and the four cohort packets. Text matching proves the contract is
   present; the fresh adversarial exercise judges that its decision boundaries
   are coherent.

E2E is not applicable: this is a documentation/contract-level observe trial
with no user-visible or full-stack runtime claim. No PRODUCT/ARCHITECTURE diff
is proposed because both current summaries remain true; the behavioral wording
lands in the kernel and workflow README that own it.

No spike is needed. `git diff --numstat`, the existing changed-file-to-AC
mapping, kernel mirror check, and contract mutation pattern are already exercised
repository mechanisms. The trial tests whether the question adds value, not
whether Git can produce counts.

One implementation worker owns the complete RED→GREEN slice. Splitting tests,
kernel wording, and mirror/registry maintenance across workers would separate
one behavior from its proof and pay unnecessary cold starts.

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is the
hidden assumption that a post-diff numeric prompt reveals responsibilities that
fresh reverse recovery and changed-file-to-AC mapping do not already expose.

## Fable 5 challenge disposition

Fresh challenge session `d34c72a5-0306-4929-b302-4038812ea7f4` returned
`narrow`. This design retains its mechanically sourced diff evidence and the
unconditional largest-responsibility question. It rejects LOC bands, variance
triggers, soft/hard gates, cross-change competition, and all number-driven
deletion. The observe trial and immediate incident stop are the disproof path.

## Stage Report: ideation

- DONE: AC-1 defines one order from accepted outcome through reverse recovery,
  subtraction proof, necessary addition, RED/GREEN, post-diff observation, and
  fresh exact-revision validation.
- DONE: AC-2 bounds change shape to separate mechanically sourced gross additions and
  deletions plus one unconditional question; it cannot gate, rank, offset, or
  redefine accepted value.
- DONE: AC-3 defines a three-change observe-only trial with success, two-of-three
  no-value failure, immediate number-management stop, and roughly-five-change
  redundancy retirement.
- DONE: AC-4 is grounded in reverse recovery at fresh `origin/main`, which found
  a five-file existing contract route and rejected every new mod, script, schema,
  capability, CI job, store, runbook, and metric surface.
- DONE: Each proposed file has a named without-it AC failure; every omitted or
  rejected file remains sufficient without a change.
- DONE: Four falsifiable ACs preserve necessary tests, safety, clarity, and
  fresh validation while letting the trial disprove its own incremental value.

### Summary

Proceed with a five-existing-file documentation/contract observe trial. Ask the
largest-responsibility question after RED/GREEN, apply normal without-it proof
to any resulting subtraction, and let no number own a delivery decision.

## Stage Report: implementation

- DONE: Implemented the accepted five-file contract slice on
  `spacedock-ensign/change-shape-awareness` at exact head
  `fb0ae44e7f06bc6ea3e0e9f52c268a25c5dfad2b` from merge base
  `54913dda3e5e66841e043025bf646e0ad2493bc9`.
- DONE: The portable kernel now orders accepted outcome, reverse recovery,
  reversible subtraction or bypass, necessary addition, RED/GREEN, post-diff
  observation, and fresh validation. Existing `UNKNOWN` preserves a surface;
  green or `UNKNOWN` returns a proposed addition.
- DONE: The local implementation stage records separate gross additions and
  deletions, the unconditional largest-responsibility question, observe-only
  boundaries, the three-change cohort, and unambiguous outcome precedence.
- DONE: A fresh review of the first head found overlapping Success and
  No-incremental-value predicates. The corrected exact head makes a confirmed
  incident win first, then an attributable subtraction win Success, then two
  defense-only rows yield No incremental value. Fresh re-review returned no
  findings and AC-3 `PASS`.

### RED and GREEN

- Pre-contract RED: the new fail-collecting contract case exited `1` and
  reported the missing seven-step order, unconditional question, observe-only
  boundaries, implementation placement, and four cohort outcomes in one run.
  Its behavior assertions were all reached; no later assertion was hidden by
  the first failure.
- Mutation RED at the corrected contract: reordering RED/GREEN and observation,
  removing the question, weakening the numeric-authority prohibition, removing
  the Success outcome, and removing mixed-cohort precedence each exited `1`
  with the corresponding contract failure.
- Review-fix RED: before the README precedence edit, the contract exited `1`
  for all three missing precedence statements. After the edit it returned
  `kc-dev-flow contract: PASS`.
- Final GREEN at exact head:
  `python3 scripts/kc-dev-flow-contract-test.py` returned
  `kc-dev-flow contract: PASS`.
- Old-behavior arrangement audit: the existing contract had no fixture that
  arranged post-diff change-shape behavior. The new assertions add a new
  contract case and do not repurpose or narrow an existing scenario.

### Changed file to AC mapping

| Changed file | Accepted responsibility | AC |
|---|---|---|
| `kc-dev-flow/references/kernel.md` | Portable ordered route, operational definitions, question, and observe-only boundary | AC-1, AC-2 |
| `docs/dev/_mods/kernel.md` | Adopt the same portable contract; byte identity is checked by the contract test and `cmp` | AC-1, AC-4 |
| `docs/dev/README.md` | Local packet, stage placement, cohort results, and outcome precedence | AC-2, AC-3 |
| `scripts/kc-dev-flow-contract-test.py` | Position-sensitive and mutation-capable falsifiers for the route, question, boundaries, stage placement, outcomes, and precedence | AC-1, AC-2, AC-3, AC-4 |
| `kc-dev-flow/references/absolutes.registry` | Fresh disposition hashes and corrected `kernel.md` locators for the edited normative blocks | AC-4 |

### Post-diff change-shape packet

- Merge base: `54913dda3e5e66841e043025bf646e0ad2493bc9`
- Implemented head: `fb0ae44e7f06bc6ea3e0e9f52c268a25c5dfad2b`
- Mechanically sourced raw `git diff --numstat <base>...<head>`:

  ```text
  46  0   docs/dev/README.md
  51  24  docs/dev/_mods/kernel.md
  16  14  kc-dev-flow/references/absolutes.registry
  51  24  kc-dev-flow/references/kernel.md
  81  0   scripts/kc-dev-flow-contract-test.py
  ```

- Gross additions: `245`.
- Gross deletions: `62`.
- Question: **If the largest added responsibility is removed, which named AC
  fails?**
- Answer: the largest independently maintained added responsibility is the
  contract-test enforcement block. Removing it makes the ordered-route,
  question, observe-boundary, cohort, and precedence mutations lose their
  mechanical falsifier, failing AC-1, AC-2, AC-3, and AC-4. The mutation runs
  are the without-it failure instrument, so the responsibility remains.
- Disposition: defense established by the AC mapping; no subtraction was
  authorized. Counts focused inspection but neither chose the responsibility
  nor supplied the answer.
- Number-management incidents: none observed. No test, assertion, clarity, or
  necessary contract wording was deleted or compressed because of a count.

### Validation-ready evidence

- Exact five-file scope: `git diff --name-only <base>...<head>` matched the
  authorized set; no sixth file or new capability is present.
- `python3 kc-dev-flow/scripts/absolutes-check.py ...` returned
  `absolutes-check:PASS:70 dispositioned`.
- A locator audit recomputed the kernel block hashes and returned
  `kernel registry locators: PASS:25`.
- `cmp kc-dev-flow/references/kernel.md docs/dev/_mods/kernel.md` returned `0`.
- `git diff --check <base>...<head>` returned `0`.
- The code worktree was clean on the named branch and exact head after the final
  checks.
- Fresh exact-head reviewer verdict: no findings; AC-1 through AC-4 pass, and
  the existing-seam, proposed-addition, and four synthetic cohort exercises are
  coherent at the corrected revision.
- E2E: not applicable because the diff changes documentation and its mechanical
  contract only; it adds no user-visible or full-stack runtime behavior.
- CI delta: the diff adds text-contract assertions without an OS, libc, locale,
  clock, CI-pinned-tool, or material timeout dependency. Exact-head required CI
  remains delivery authority.

### Summary

Implemented and mechanically falsified the outcome-first change-shape contract
at `fb0ae44e7f06bc6ea3e0e9f52c268a25c5dfad2b`. The exact five-file revision is
ready for fresh validation; change-shape numbers remain observation only.

## Stage Report: validation

**DECISION: PROCEED.** Fresh exact-revision validation supports AC-1 through
AC-4 from base `1db7e7729595b090715943da544a0f8327912c05` to product head
`54f394ded2fe90481c17db4466c4cdd6e3601fbc` with no material finding, and the
required state-context control passes when bound to that exact product worktree.

- DONE: At exact head `54f394ded2fe90481c17db4466c4cdd6e3601fbc`, exercised the ordered route with a recovered seam and proposed responsibility plus success, defense-only, incident, retirement, and mixed-precedence cohorts.
- DONE: Confirmed the required marketplace, parity, contract, frontmatter, absolutes, locator, kernel-identity, exact-five-file, and diff checks pass, with claim-breaking route and precedence mutations RED.
- DONE: Returned a fresh `proceed` recommendation for AC-1 through AC-4 with the complete evidence block and Claude Opus High outside-voice disposition `PROCEED`; no further multi-model pass is needed.

### Exact-revision AC verdicts

**AC-1 — PASS.** The canonical and adopted kernels state the seven decisions in
one order, and the local implementation stage places observation after RED/GREEN
and changed-file-to-AC mapping.

- Recovered-seam walk: (1) the accepted value is a brownfield path that protects
  the named outcome and constraints; (2) the pre-change local stage contract in
  `docs/dev/README.md` was `EXISTS_BROKEN`, because it already owned RED/GREEN and
  AC mapping but lacked post-diff observation; (3) bypassing that existing stage
  loses the local packet and cohort authority, failing AC-2 and AC-3; (4) the
  compatible repair therefore extends that seam rather than adding a new mod,
  store, job, or schema; (5) the exact-head contract is GREEN and order mutations
  are RED; (6) the post-diff question identifies the assertion block as the
  largest added responsibility and its without-it evidence supports retention;
  (7) every final check below is bound to the exact head.
- Proposed-responsibility walk: the assertion block inside the existing contract
  test is proposed only after the existing checker is recovered. At base
  `1db7e7729595b090715943da544a0f8327912c05`, the existing pre-release smoke
  assertions were present while the seven-step route was absent, so the simpler
  pre-change checker was insufficient and AC-1/AC-4's mechanical falsifier
  failed without the responsibility. At the implemented head, reversing
  RED/GREEN with observation exits `1` for
  `ordered route is out of sequence`; removing required route, question,
  boundary, outcome, precedence, and delivery-authority clauses also exits `1`.
  A separate collector/store responsibility still returns at step 4 because all
  ACs have a sufficient existing-file route without it.
- Falsifier: a route or stage-order mutation stays green; an existing `UNKNOWN`
  is removed as irreducible; or green/`UNKNOWN` absence retains a proposed
  responsibility.

**AC-2 — PASS.** The exact-head packet keeps mechanically sourced additions and
deletions separate, asks the unconditional question, and assigns numbers no
delivery authority. Fresh synthetic packets exercised the adversarial edges:

| Packet | Exercise | Result |
|---|---|---|
| Necessary large addition | `180/4`; the independently maintained compatibility responsibility fails a named AC under its without-it instrument | Retain on AC evidence; the count supplies no verdict |
| Deletion-heavy | `6/190`; inspect the six added lines independently and do not offset them with deletions | Ask the question; no net score and no delivery change |
| Test-heavy | `140/3`; the largest added responsibility is a regression-test block | Keep when removal loses the named AC falsifier; count cannot authorize test deletion |

The composite contract mutation removed the question and an observe-only
prohibition and exited `1` with both named failures. Falsifier: a count passes or
fails a change, chooses a responsibility, offsets additions and deletions, or
authorizes deletion without normal without-it evidence.

**AC-3 — PASS.** The local stage contract resolves every required synthetic
cohort without making an outcome a per-change delivery gate:

| Cohort | Rows / condition | Applied disposition |
|---|---|---|
| Success | one newly attributable subtraction, one defense, one `UNKNOWN`; no incident | Success |
| Defense-only | three defenses already required by AC mapping; no subtraction or incident | No incremental value |
| Incident | one attributable subtraction, one defense, one confirmed count-caused unsafe deletion | Immediate stop/removal wins before Success |
| Retirement | five comparable defense-only changes with no new question | Redundancy retirement at policy review; fifth delivery result is unchanged |
| Mixed precedence | one attributable subtraction plus two defenses; no incident | Success, not No incremental value |

Removing a cohort outcome or precedence statement in the scratch artifact exits
`1`. Falsifier: any row maps to competing dispositions, attribution to the
post-diff question is not distinguishable from prior AC mapping, or a cohort
outcome blocks an otherwise accepted change.

**AC-4 — PASS.** Fresh checks at the exact head returned:

- marketplace verification, version parity, skill frontmatter, and the full
  `scripts/kc-dev-flow-contract-test.py` -> PASS;
- absolutes and independent registry locator audits -> PASS, with the edited
  normative blocks dispositioned and locators current;
- canonical/adopted kernel identity -> PASS;
- exact-scope audit -> the five authorized files and no sixth file or new
  capability;
- `git diff --check 1db7e7729595b090715943da544a0f8327912c05...54f394ded2fe90481c17db4466c4cdd6e3601fbc`
  -> PASS;
- raw `git diff --numstat` -> `46/0`, `51/24`, `16/14`, `51/24`, and
  `79/0` for the five mapped files, totaling gross `+243/-62`; and
- code worktree -> clean on `spacedock-ensign/change-shape-awareness` at the
  named head `54f394ded2fe90481c17db4466c4cdd6e3601fbc`.

The changed-file responsibilities remain mapped exactly as implementation
reported: portable contract (AC-1/2), adopted mirror (AC-1/4), local packet and
cohorts (AC-2/3), mechanical falsifier (AC-1 through AC-4), and absolute
dispositions/locators (AC-4). Falsifier: a sixth file, runtime/store/schema/job,
mirror drift, stale locator, whitespace error, or count-motivated removal of a
necessary test or clarity surface.

### Mutation and coverage evidence

- Exact head GREEN: contract exit `0`.
- Base `1db7e7729595b090715943da544a0f8327912c05` retained its pre-release smoke
  assertions while the seven-step route was absent, demonstrating the distinct
  enforcement responsibility without weakening the base coverage.
- Scratch mutation A, extracted from the exact head: removed a route obligation,
  the question, an observe-only boundary, stage placement, retirement outcome,
  incident precedence, and delivery boundary; exit `1` with all seven named
  contract failures.
- Scratch mutation B, extracted from the exact head: reversed route and local
  stage placement; exit `1` with `ordered route is out of sequence` and
  `implementation stage does not place change-shape observation after RED/GREEN
  and AC mapping`.
- Exact-head GREEN and claim-breaking mutation RED cover `100%` of the changed
  executable assertion lines; the base pre-release smoke assertions remain
  present and enforced.

### Workflow evidence block

- `Lenses: PASS —` Diff classification is prose plus one executable contract
  assertion block. Correctness fired (`0` findings) and manifest/back-compat
  fired (`0` findings) because installed `continue-dev-flow` consumers read the
  adopted kernel. Read exact revision `54f394ded2fe90481c17db4466c4cdd6e3601fbc`
  at the five changed paths plus `kc-dev-flow/skills/continue-dev-flow/SKILL.md`;
  this line would fail on a qualifying regression, an unresolved consumer path,
  or an existing install no longer resolving the adopted contract. Security,
  silent-failure, type-design, concurrency, and resource-lifecycle did not fire:
  the diff touches no auth/trust/shell workflow, error/fallback contract, type,
  shared state, or owned resource surface.
- `Diff coverage: PASS —` The executable delta is limited to the contract
  assertion block; exact-head GREEN plus claim-breaking mutation RED cover
  `100%` of its changed executable lines, while the rebased pre-release smoke
  assertions stay present. This line would fail if a changed assertion branch
  were unexercised or the base smoke assertions were weakened or absent.
- `Adversarial: PASS —` The recovered seam, proposed responsibility, three
  change-shape edge packets, and five cohort tables were exercised against the
  exact revision; two scratch mutation artifacts exited `1` with the expected
  order, boundary, outcome, and precedence failures. This line would fail if an
  addition advanced before without-it evidence, a number supplied a verdict, or
  a cohort had ambiguous precedence.
- `Cross-model: PASS —` Safe-mode read-only Claude Opus High outside-voice
  session `e93d42b5-c787-4956-80e9-645d09abec17` read base
  `1db7e7729595b090715943da544a0f8327912c05`, exact head
  `54f394ded2fe90481c17db4466c4cdd6e3601fbc`, the five-file diff, governing ACs,
  and check receipts, and returned `PROCEED` with `No Material findings`. It
  confirmed the ordered route; incident-first, then any-subtraction Success,
  then two-defense-only No incremental value precedence; non-gating anti-gaming
  safeguards; coexistence with base smoke assertions; kernel parity; and the
  registry dispositions. This line fails if a base smoke assertion is weakened
  or absent, the precedence paragraph is missing or placed after the outcomes,
  or a required registry entry is stale or missing.
- `E2E: N/A —` Ideation scoped the change to documentation and its mechanical
  contract, with no user-visible or full-stack runtime claim. Read the exact
  five-file diff; this line would fail if a changed path introduced runtime
  behavior or an AC required a real-runtime observation.
- `Origin re-observation: N/A — no accepted claim originated in consumer or
  external runtime behavior.` Read the accepted problem, ACs, and exact diff;
  this line would fail if the accepted claim were grounded in a consumer/runtime
  report without same-kind re-observation.

### Corrected state-control evidence

The required `bound_field_validation` rerun kept the split-root task path and
bound both repository inputs to the exact product worktree at
`54f394ded2fe90481c17db4466c4cdd6e3601fbc`:

- marketplace:
  `.worktrees/spacedock-ensign-change-shape-awareness/.claude-plugin/marketplace.json`;
- ROADMAP:
  `.worktrees/spacedock-ensign-change-shape-awareness/docs/dev/ROADMAP.md`; and
- task: `docs/dev/.spacedock-state/change-shape-awareness.md`.

It returned `PASS` with zero findings at
`input_revision dba5465df1baedaee3e3d0e629fd9a31d98ecc7b8887bf76b4dbb9770a5519ca`.
The earlier `sprint_unregistered` FAIL bound marketplace and ROADMAP to the stale
captain-workspace branch, not the exact product worktree/trunk authority, and
carries no gate verdict.

### Fresh EM advisory record

```yaml
science_officer_em_upward_report:
  em_judgment: AC-1 through AC-4 are supported at exact head 54f394ded2fe90481c17db4466c4cdd6e3601fbc with no material finding, and correctly bound state-context validation is PASS.
  evidence_synthesis: The exact five-file +243/-62 diff from base 1db7e7729595b090715943da544a0f8327912c05 preserves the base smoke assertions, passes marketplace, parity, contract, frontmatter, absolutes, locator, kernel-identity, scope, and diff checks, reddens under claim-breaking mutations, and received a safe-mode Claude Opus High PROCEED with No Material findings plus a zero-finding bound-field PASS.
  risk_tradeoff_call: The benefit is one coherent brownfield subtraction route and a falsifiable observe-only trial; the residual risk is redundant prompting, while the durable cost is limited to existing documentation and one assertion block; the alternative is to omit observation and retain the proven ambiguity.
  recommendation: Proceed to the existing validation gate owner for its authorized verdict and delivery workflow; the completed Opus outside-voice pass leaves no need for another model pass.
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: The First Officer retains orchestration and gate-transition authority; this advisory does not advance state or deliver the change.
  engineering_judgment:
    question: Whether the exact five-file outcome-first change-shape contract from base 1db7e7729595b090715943da544a0f8327912c05 satisfies AC-1 through AC-4 and should proceed.
    revision: 54f394ded2fe90481c17db4466c4cdd6e3601fbc
    evidence_synthesis: The exact five-file +243/-62 diff from base 1db7e7729595b090715943da544a0f8327912c05 preserves the base smoke assertions, passes marketplace, parity, contract, frontmatter, absolutes, locator, kernel-identity, scope, and diff checks, reddens under claim-breaking mutations, and received a safe-mode Claude Opus High PROCEED with No Material findings plus a zero-finding bound-field PASS.
    adjudications:
      - finding: AC-1 ordered brownfield route
        disposition: supported
        basis: Exact kernel order, recovered-seam/proposed-responsibility walks, preserved base smoke assertions, exact-head GREEN, and order-mutation RED.
      - finding: AC-2 observation without numeric verdict authority
        disposition: supported
        basis: Necessary-addition, deletion-heavy, and test-heavy packets plus question/prohibition mutation RED.
      - finding: AC-3 bounded cohort outcomes and precedence
        disposition: supported
        basis: Success, defense-only, incident, retirement, and mixed-cohort exercises plus mutation RED; Opus independently confirmed incident first, then any subtraction Success, then two defense-only No incremental value.
      - finding: AC-4 existing five-file contract surface
        disposition: supported
        basis: Exact-five-file +243/-62 scope, marketplace, parity, contract, frontmatter, absolutes, locator, byte-identity, diff-check, clean-head, and justified-registry evidence.
      - finding: Required bound-field validation for the live work item
        disposition: supported
        basis: The exact-worktree marketplace and ROADMAP at 54f394ded2fe90481c17db4466c4cdd6e3601fbc plus split-root task returned PASS with zero findings at input revision dba5465df1baedaee3e3d0e629fd9a31d98ecc7b8887bf76b4dbb9770a5519ca.
    risk_tradeoff: The benefit is one coherent brownfield subtraction route and a falsifiable observe-only trial; the residual risk is redundant prompting, while the durable cost is limited to existing documentation and one assertion block; the alternative is to omit observation and retain the proven ambiguity.
    recommendation: Proceed to the existing validation gate owner for its authorized verdict and delivery workflow; the completed Opus outside-voice pass leaves no need for another model pass.
    route: proceed
    confidence: high
    dissent: ""
    disproof_condition: Weaken or remove any base smoke assertion, remove or move the precedence paragraph after the outcomes, or leave any required absolutes-registry entry stale or missing; any such result changes the recommendation to return.
    authority_boundary: Captain retains scope and irreversibility; First Officer and Spacedock retain gate and stage transitions; work-item and delivery authorities retain status, merge, and terminalization.
```

### Summary

Fresh exact-head validation found no defect and recommends `proceed`. The
five-file `+243/-62` change at `54f394ded2fe90481c17db4466c4cdd6e3601fbc`
satisfies AC-1 through AC-4, preserves the base smoke assertions, reddens under
claim-breaking mutations, and has a correctly bound state-context PASS. Claude
Opus High session `e93d42b5-c787-4956-80e9-645d09abec17` returned `PROCEED` with
`No Material findings`; no additional multi-model review is needed.
