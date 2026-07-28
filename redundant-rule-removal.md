---
title: The skill's tail restates rules it already stated
status: validation
source: cross-model review of the kit, 2026-07-27 — the lowest-risk cut available
design: required
id: tmn8fgqy8390zepcp019td74
lane: main
started: 2026-07-28T16:32:16Z
worktree: .worktrees/spacedock-ensign-redundant-rule-removal
---

## Problem

`kc-pr-flow/skills/kc-pr-review/SKILL.md` ends with a 41-bullet `## Rules` section. Many bullets
repeat normative instructions already present in the ordered workflow or a reference that the
workflow explicitly tells the reviewer to read. Repeating them makes the prompt longer and creates
a second edit site where the two copies can drift.

The original task treated the entire tail as redundant and made implementation depend on
`skill-ablation-harness` (5b). Static inspection falsifies both assumptions:

- The 41 bullets are not one equivalence class. Ten contain a unique clause, a stronger trigger,
  or a conflict with the alleged survivor.
- A paid/model ablation cannot prove textual information preservation more directly than a
  clause-complete source mapping. For this pure-restatement cut, the mapping is the proof.

Scope questions are skipped because the captain supplied a single-file, no-information-removal
scope, explicitly parked 5b, and prohibited paid experiments. There is no unresolved product
choice to ask back.

## Scope and appetite

In scope:

- Reshape only the `## Rules` tail in
  `kc-pr-flow/skills/kc-pr-review/SKILL.md`.
- Delete a bullet only when every normative clause has a surviving authoritative statement.
- Treat an explicitly linked reference as authoritative only when the main workflow requires that
  reference at the relevant step.
- Retain any unmatched, stronger, conditional, or contradictory bullet unchanged.

Out of scope:

- `skill-ablation-harness` (5b), paid model calls, eval runs, and ablation experiments.
- `presentation-renderer` (fa), `reference-progressive-load` (sk), or any other slimming entity.
- Rewriting or consolidating the surviving authorities.
- Resolving pre-existing contradictions found by the audit.

Appetite: 30 minutes for the implementation edit and mechanical validation, with a 15-minute
tolerance (one bounded repair round). Paid/model appetite is exactly zero. If the target skill has
drifted enough that the approved map no longer resolves, or any required local suite remains red
after one repair, stop and return the task for re-cut; do not widen scope or substitute thinner
proof.

## Options considered

1. **Clause-complete allowlist deletion (chosen).** Freeze the implementation head, re-resolve the
   map below, delete only the 31 fully mapped bullets, and retain the ten fail-closed bullets.
   This is the fastest path that satisfies the no-information-removal claim and the smallest safe
   cut.
2. **Delete the entire `## Rules` section.** Fastest edit, rejected: ten bullets do not have a
   substantively complete, non-conflicting survivor.
3. **Normalize all rules into a new canonical reference, then replace the tail with one pointer.**
   More thorough, rejected for this task: it rewrites authority boundaries and therefore becomes a
   behavior-bearing prompt refactor rather than a pure restatement cut.

Taking the cheap path: a static semantic-equivalence audit plus existing local contract suites.
The more thorough model-ablation path is not needed because no candidate is admitted on behavioral
similarity; admission requires surviving text that already carries every clause.

## Design determination

`design: required`. This changes the shape of an agent instruction contract. Before: a 41-bullet
tail mixes duplicates with unique or conflicting rules. After: the ordered workflow and its
explicit references remain authoritative, while `## Rules` retains only the ten bullets for
which this audit cannot prove full equivalence. There is no new runtime interface or schema.

Reverse-recovery audit is not applicable: the task removes duplicate prose and builds no
abstraction. The brownfield recovery proof is the surviving-authority map itself.

## Static semantic-equivalence audit

Line numbers below are from the ideation head. Implementation must bind the audit to the exact
target blob and re-resolve section anchors if line numbers move. A row is removable only when all
of its clauses are covered by the cited survivor.

### Approved deletion allowlist

| Tail line | Rule | Surviving authority |
|---:|---|---|
| 1844 | PR Summary first and evidence-based | `SKILL.md` Step 2.6 (141-164) and §6-pre (941-971) |
| 1845 | Confirm before posting | `SKILL.md` §6c (1723-1754) |
| 1846 | Diagrams opt-in, preview-first, post only via 5/6 | `SKILL.md` §6b-arch (1116-1141) and §6c |
| 1847 | Diagram validation before preview and posting | `SKILL.md` 1128-1131 and Step 7 at 1824 |
| 1848 | Dynamic repository detection | `SKILL.md` Step 1 (98-102) and Step 3 (166-179) |
| 1849 | Ownership-scoped personal rules | `SKILL.md` Step 3 (166-189) |
| 1850 | Temp JSON plus `--input`, not `--raw-field` | required `reference/gh-api-patterns.md` 105-129 and 294 |
| 1851 | One batched review submission | required `reference/gh-api-patterns.md` 129 and 298 |
| 1853 | CODE/DOC/NEW classification and CODE-only inline posting | `SKILL.md` Step 5 (788-792) and Step 6 (935-1020) |
| 1855 | Pre-emit quoted-source gate | `SKILL.md` §6a (973-988) |
| 1856 | Source-set reconciliation, not silence-as-evidence | `SKILL.md` Step 4-Codex (417) and §5.5 (794-824) |
| 1857 | Material-dispute arbitration and uncapped contradictions | `SKILL.md` §5.5c (826-844) |
| 1858 | Fail-open arbitration with visible, human-gated demotion | `SKILL.md` §5.6b-c (898-927) and §6b-cm (1108-1114) |
| 1859 | Homogenized-lens convergence caveat | `SKILL.md` 929-933 and §6b-cm (1094-1105) |
| 1861 | Comment-analyzer always runs | required `reference/review-triage.md` 122-185 |
| 1862 | Discover skills as references; do not invoke | required `reference/compliance-audit.md` 39-64 |
| 1863 | Fetch and tag the PR author | `SKILL.md` Step 2 (104-108), Step 7 (1824), and required `reference/gh-api-patterns.md` 107/299 |
| 1865 | Refactor behavioral equivalence before style | required `reference/review-triage.md` 182-191 |
| 1868 | Refactor stale-reference audit | required `reference/review-triage.md` 182-191 |
| 1871 | D2 threshold plus user gate | Step 8 (1832-1840) and required `reference/knowledge-capture.md` 38-60/93-108 |
| 1872 | Surgical knowledge edits | required `reference/knowledge-capture.md` 128-134 |
| 1873 | Project-scoped `.claude/review-lessons.md` | required `reference/knowledge-capture.md` 38-71/83-91 |
| 1874 | Separate D2 knowledge commit | required `reference/knowledge-capture.md` 110-115 |
| 1875 | Specific, testable knowledge only | required `reference/knowledge-capture.md` 53-60/128-130 |
| 1876 | Step 8 cannot be deferred for an interruption | `SKILL.md` Step 8 (1828-1840) |
| 1877 | Tests precede verdict when available | `SKILL.md` §4.5t (730-752) and required `reference/compliance-audit.md` 160 |
| 1878 | Test failures override a clean static pass | `SKILL.md` 743-750 and required `reference/test-execution.md` 125-131 |
| 1880 | Worktree cleanup after tests | required `reference/test-execution.md` 36-40 |
| 1882 | Probe evidence must match A/B/C/D level | required `skills/break-point-probe/SKILL.md` 89-105/148-155 |
| 1883 | Residual uncertainty required below complete D | required `skills/break-point-probe/SKILL.md` 148-152 |
| 1884 | External-system A/B probe defaults to COMMENT | `SKILL.md` Step 4.5p (754-784) and §6b¾ (1061) |

### Fail-closed retention set

| Tail line | Rule | Why it stays |
|---:|---|---|
| 1852 | Severity labels | No earlier authority states the complete five-label vocabulary as a normative closed set. |
| 1854 | DOC/NEW advisory action | Step 6 preserves non-posting, but not the full “separate issue or CLAUDE.md” action. |
| 1860 | Tested cross-model helper | The tail says four functions; the test header says three deterministic functions. The alleged survivors are not equivalent. |
| 1864 | PR-facing English | The top language rule survives, but draft-time application and the edited-comment consequence are unique. |
| 1866 | Refactor consumer audit | The reference requires import-graph correctness but not the exhaustive original-module grep procedure. |
| 1867 | Refactor API-surface audit | The deleted rule requires listing every symbol that became newly public, then flagging unintentional exposure. Its cited survivor, `reference/review-triage.md:182-191`, tells agents to detect/flag accidental or unintentional API-surface widening, but never requires an exhaustive list of all newly public symbols. |
| 1869 | Completed verification matrix in review body | The deleted rule requires the completed matrix table to appear in the review body and says it replaces ad-hoc prose. Its cited survivor, `SKILL.md:121-139`, only says to build an initial matrix and that each concern must be "addressed in the review body"; it does not require the completed table to be rendered there and does not exclude ad-hoc prose. |
| 1870 | D1 auto-append | Step 8 names the public `reference/learned-patterns.md`; the required reference says LOCAL-only. Conflicting destinations cannot prove equivalence. |
| 1879 | Eval failure confirmation | Earlier text requires two or more runs, but the four-consecutive-failures threshold is unique. |
| 1881 | Break-point activation | The tail says any bugfix; Step 4.5p requires a bugfix spanning at least two layers. The tail is stronger. |

Any implementation-head drift changes this from an allowlist into a mandatory re-audit: do not
delete a row merely because its old line number still exists.

## Implementation plan

1. Record the implementation-head blob SHA for `SKILL.md` and inventory the exact 41 tail bullet
   titles. If it differs from this audit, re-resolve every affected row before editing.
2. Create an exact-text deletion allowlist from the 31 approved rows. Split compound bullets into
   normative clauses during review; a row is admitted only if every clause maps.
3. Delete only allowlisted bullets. Keep the `## Rules` heading and the ten retained bullets
   byte-for-byte unless a separate task later resolves them.
4. Compare `git diff --unified=0` against the allowlist. Fail if the diff deletes any retained
   title, changes an earlier authority, or contains any product change outside this one skill.
5. Run the exact local evidence suite below. Do not run 5b, evals, model calls, or E2E.

One worker session is sufficient: one behavior surface, one file, one dependent edit. No spike is
needed; the mechanism is Markdown deletion plus existing static/contract tests.

## Required mechanical evidence

Implementation is not complete until all commands exit 0 from the repository root:

```bash
bash scripts/skill-frontmatter-lint.sh
bash kc-pr-flow/scripts/cross-model.test.sh
bash kc-pr-flow/scripts/review-architecture-diagrams.test.sh
bash kc-pr-flow/scripts/review-shadow.test.sh
```

These are the existing suites that read or constrain this `SKILL.md`. Runtime, post, benchmark,
paid eval, and ablation suites are outside the changed seam. E2E is skipped because this is a
prompt-document de-duplication with no user-visible wiring claim.

No published `PRODUCT.md` or `ARCHITECTURE.md` behavior changes, so no separate doc diff is
proposed. The edited skill is itself the only published instruction surface affected.

## Acceptance criteria

**AC-1 — Removed rules retain complete authority.**
Verified by: the implementation `git diff --unified=0`, the frozen `kc-pr-flow/skills/kc-pr-review/SKILL.md` blob SHA, and direct reads of every survivor cited in the allowlist table (beginning at `SKILL.md:98`) showing that each deleted normative clause remains in a workflow or explicitly required reference at the exact implementation head. Falsified by one deleted clause with no survivor, a weaker/conditional survivor, a survivor inside the deleted region, or conflicting survivors.

**AC-2 — Unique and stronger rules remain.**
Verified by: an exact-title comparison of the post-edit `SKILL.md:Rules` section against the ten-title retention set at ideation lines 1852, 1854, 1860, 1864, 1866, 1867, 1869, 1870, 1879, and 1881, plus the implementation diff. Falsified by a missing retained title, a semantic rewrite hidden inside this deletion task, or a revised map not approved after implementation-head drift.

**AC-3 — The cut is measurably smaller without information removal.**
Verified by: before/after bullet counts from `git show <base>:kc-pr-flow/skills/kc-pr-review/SKILL.md` and the worktree `SKILL.md:Rules` section showing 41 to 10 bullets at the audited head, plus `git diff --numstat` and the AC-1 map showing exactly 31 mapped restatements deleted and no earlier authority or required reference changed. Falsified by a non-31 deletion count without a documented head re-audit, added replacement prose, or a changed authority.

**AC-4 — Existing skill contracts remain green.**
Verified by: captured zero exit statuses from `bash scripts/skill-frontmatter-lint.sh`, `bash kc-pr-flow/scripts/cross-model.test.sh`, `bash kc-pr-flow/scripts/review-architecture-diagrams.test.sh`, and `bash kc-pr-flow/scripts/review-shadow.test.sh` at the implementation `SKILL.md:Rules` head. Falsified by any failure, skipped command, or test adjustment made only to accommodate the deletion.

**AC-5 — The zero-paid boundary is preserved.**
Verified by: the implementation command log containing only static inspection, the `kc-pr-flow/skills/kc-pr-review/SKILL.md:Rules` edit, and the four named local suites. Falsified by invoking any paid/model/eval/ablation path or claiming 5b acceptance.

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a hidden assumption: an
earlier `Read →` reference is not actually loaded in a runtime path where the deleted tail bullet
previously supplied the only in-context instruction.

### Summary

Replaced the 5b dependency with a zero-paid, clause-complete semantic audit; approved 31
restatement deletions, retained ten unmatched or conflicting rules, and specified exact
single-file validation evidence and stop conditions.

## Stage Report: ideation (cycle 1 — superseded by cycle 2)

- DONE: Replaced the hard dependency on 5b with a bounded, fail-closed semantic-equivalence
  proof. The implementation allowlist contains 33 tail bullets, each mapped to surviving workflow
  or explicitly required reference authority.
- DONE: AC-1 — every approved deletion has a clause-complete survivor mapping in the static audit.
- DONE: AC-2 — eight unmatched, stronger, or conflicting bullets are an explicit retention set.
- DONE: AC-3 — the baseline and end value are measurable: 41 tail bullets become 8 by deleting
  exactly 33 mapped restatements at the audited head.
- DONE: AC-4 — the four existing SKILL-coupled local contract suites are named as mandatory
  zero-exit evidence.
- DONE: AC-5 — zero paid/model/eval/ablation work is both the appetite and a falsification
  boundary; 5b acceptance is not claimed.
- DONE: Recorded a zero-paid/model/eval/ablation appetite, a 30-minute implementation budget with
  15-minute tolerance, `design: required`, one-worker sizing, scope exclusions, pre-mortem, and
  stop/re-cut conditions.
- DONE: Named the exact local evidence suite:
  `skill-frontmatter-lint.sh`, `cross-model.test.sh`,
  `review-architecture-diagrams.test.sh`, and `review-shadow.test.sh`.
- SKIPPED: Reverse-recovery and E2E. This is a single-file duplicate-prose removal that builds no
  abstraction and makes no wiring claim; its load-bearing proof is direct source equivalence plus
  the existing SKILL-coupled contract tests.
- SKIPPED: 5b acceptance and paid experiments. They remain explicitly parked and are not needed or
  claimed by this entity.

## Stage Report: implementation

### Summary

Removed exactly the 33 approved restatement bullets from
`kc-pr-flow/skills/kc-pr-review/SKILL.md` and preserved the eight-rule retention set
byte-for-byte. No authority, reference, test, harness, or other product file changed.

### Exact-head and diff evidence

- DONE: Froze implementation head
  `b87171c40d595c7c60d4efa3ee16d0b4249cd9d1` and target blob
  `45ba8359f866f8d4b41c960b805230b3e7283579` before editing.
- DONE: The live tail still contained the audited 41 bullets at ideation lines 1844-1884, with all
  33 deletion titles and eight retention titles unchanged. Direct reads re-resolved the cited
  workflow and required-reference survivor anchors at that head; no implementation-head drift
  invalidated the allowlist.
- DONE: The pre-edit retained-count contract failed for the intended reason:
  `expected retained Rules bullets=8, actual=41` (`exit 1`).
- DONE: Code commit
  `ee127c1f6a33c8e31eebacfc75619efb4d9fad7a` on
  `spacedock-ensign/redundant-rule-removal` produces target blob
  `b8b87caea8c188615bae04dc7af39c30a9b22285`.
- DONE: `git diff --unified=0` contains deletion hunks only inside `## Rules`;
  `git diff --numstat` is exactly
  `0  33  kc-pr-flow/skills/kc-pr-review/SKILL.md`.
- DONE: Before/after Rules bullet count is exactly 41 to 8. The post-edit retained-count contract
  reports `expected retained Rules bullets=8, actual=8` (`exit 0`).
- DONE: A base-vs-worktree exact-line comparison produced no diff for the retained titles:
  `Severity labels`, `DOC/NEW findings are advisory`,
  `Cross-model logic lives in a tested helper`, `PR-facing artifacts in English`,
  `Refactoring PRs — consumer audit`, `D1 auto-append`,
  `Eval tests need double confirmation`, and `Break-point probe for bugfix/cross-stack`.
- DONE: `git diff --check` exited 0, and the committed code worktree is clean.

### Required local contract suites

All commands ran from the repository root and exited 0:

- DONE: `bash scripts/skill-frontmatter-lint.sh` — checked 35 `SKILL.md` files; all skill
  directories have valid frontmatter.
- DONE: `bash kc-pr-flow/scripts/cross-model.test.sh` — 68 passed, 0 failed.
- DONE: `bash kc-pr-flow/scripts/review-architecture-diagrams.test.sh` — 43 passed, 0 failed.
- DONE: `bash kc-pr-flow/scripts/review-shadow.test.sh` — 213 passed, 0 failed.

### Acceptance and stop outcome

- DONE: AC-1 — all 33 deleted clauses retain the approved workflow or required-reference
  authority at the frozen implementation head.
- DONE: AC-2 — all eight unique, stronger, or conflicting rules remain byte-for-byte.
- DONE: AC-3 — the cut is exactly 33 deletions with zero replacement prose and no earlier
  authority or required-reference change.
- DONE: AC-4 — all four required local contract suites exited 0 without test adjustment.
- DONE: AC-5 — the command log contains static inspection, the single allowlisted Markdown edit,
  and the four named local suites only.
- DONE: No stop/re-cut trigger fired: the head/title map had not drifted, every survivor mapping
  remained complete, the deletion count was exactly 33, no retained title changed, and every
  required suite passed on the first run. No repair round or scope expansion was used.
- SKIPPED: Paid models, model calls, evals, E2E, runtime/post suites, benchmarks, the 5b ablation
  harness, fa, and sk, as required by the zero-paid and single-seam scope boundary.

## Stage Report: validation

### TL;DR

**REJECTED** at code commit `ee127c1f6a33c8e31eebacfc75619efb4d9fad7a`.
The committed patch and all four required local suites are mechanically clean, and all eight
retained rules are byte-for-byte unchanged. However, two of the 33 deleted bullets contain
normative clauses that their cited survivors do not preserve. That fails AC-1 and therefore AC-3.
No product file was modified during validation.

### Evidence block

- Lenses: Markdown-only instruction-contract diff. Correctness **FAIL** (2 findings);
  manifest/back-compat **FAIL** (the same 2 information-loss findings). Security, silent-failure,
  type-design, concurrency, and resource-lifecycle did not fire because the diff changes no auth,
  error-handling, type, async/shared-state, process/handle, or executable surface.
- Diff coverage: N/A — prose-only diff, no executable surface.
- Adversarial: N/A — no executable behavioral guard to mutate; the stage-specific dispatch also
  prohibits the parked 5b ablation harness, evals, runtime/post suites, and E2E.
- Cross-model: NOT RUN — the stage-specific zero-paid boundary expressly prohibits model calls.
  The required deterministic `cross-model.test.sh` contract suite ran and passed 68/68; no
  cross-model or 5b acceptance is claimed.
- E2E: N/A — ideation explicitly excludes E2E for this prompt-only de-duplication with no wiring
  claim, and validation dispatch prohibits it.

### Findings for feedback-to implementation

1. **Restore `Verification matrix in review body` (parent `SKILL.md:1869`) or return the entity to
   ideation for a smaller allowlist.** The deleted rule requires the completed matrix table to
   appear in the review body and says it replaces ad-hoc prose. Its cited survivor,
   `SKILL.md:121-139`, only says to build an initial matrix and that each concern must be
   "addressed in the review body"; it does not require the completed table to be rendered there
   and does not exclude ad-hoc prose. A direct
   `rg -n 'Verification Matrix|verification matrix' kc-pr-flow/skills/kc-pr-review/SKILL.md`
   finds no other surviving authority for those clauses.
2. **Restore `Refactoring PRs — API surface diff` (parent `SKILL.md:1867`) or return the entity to
   ideation for a smaller allowlist.** The deleted rule requires listing every symbol that became
   newly public, then flagging unintentional exposure. Its cited survivor,
   `reference/review-triage.md:182-191`, tells agents to detect/flag accidental or unintentional
   API-surface widening, but never requires an exhaustive list of all newly public symbols.

Restoring these exact two bullets is the bounded product fix for the information loss. Because
that would change the measured cut from 33 deletions to 31, the current AC-3 exact-33 requirement
must also be re-cut in ideation; adding replacement authority elsewhere is outside this
deletion-only task and would violate the zero-addition criterion.

### Acceptance criteria

- **FAIL — AC-1, "Removed rules retain complete authority."** Direct reads at exact code head
  `ee127c1` resolved 31 deletion rows to clause-complete survivors, but the two findings above
  failed their cited mappings. One failed survivor is an explicit falsifier for AC-1.
- **PASS — AC-2, "Unique and stronger rules remain."** The parent/head retained-line extraction
  diff was empty for all eight titles. The retained lines at `ee127c1` hash to
  `f5fd3ecf29e68cd79efcf6b37a36bff1b1375d8d8e63b81c072390c18a69b7ae`.
- **FAIL — AC-3, "The cut is measurably smaller without information removal."** Mechanical size
  evidence passes: Rules count is `41 -> 8`; commit stat is exactly one file with
  `0 additions / 33 deletions`; `git diff --check` exits 0. The "without information removal"
  half fails with the two AC-1 findings, so the criterion is not satisfied.
- **PASS — AC-4, "Existing skill contracts remain green."** Fresh exact-head runs from the code
  worktree exited 0: `skill-frontmatter-lint.sh` checked 35 skills; `cross-model.test.sh` reported
  68 passed / 0 failed; `review-architecture-diagrams.test.sh` reported 43 passed / 0 failed;
  `review-shadow.test.sh` reported 213 passed / 0 failed.
- **PASS — AC-5, "The zero-paid boundary is preserved."** Validation used static git/source
  inspection and the four named local suites only. It invoked no paid/model/eval/ablation,
  runtime/post, benchmark, or E2E path and makes no 5b acceptance claim. The committed code diff
  contains only the one `SKILL.md` deletion patch and no harness/test addition.

### Exact-head and scope evidence

- Code worktree branch: `spacedock-ensign/redundant-rule-removal`; exact clean head:
  `ee127c1f6a33c8e31eebacfc75619efb4d9fad7a`.
- Commit parent/target skill blobs:
  `45ba8359f866f8d4b41c960b805230b3e7283579` ->
  `b8b87caea8c188615bae04dc7af39c30a9b22285`.
- `git diff-tree --name-status` reports only
  `M kc-pr-flow/skills/kc-pr-review/SKILL.md`; `git diff --numstat` reports
  `0  33  kc-pr-flow/skills/kc-pr-review/SKILL.md`.
- Changed-file mapping: the sole changed file serves AC-1 through AC-4 by removing the audited
  Rules bullets while preserving authorities and retained rules. No changed file is unmapped.

### Recommendation

**REJECTED — feedback-to implementation, with an ideation re-cut required before another
implementation can satisfy the numeric AC.** Restore the two bullets named above byte-for-byte;
do not add replacement prose or widen the task.

### Feedback Cycles

- Cycle 1: REJECTED — fresh validation; surface 17m implementation plus mechanical validation vs estimate 30m (57%); AC narrowed: deletion allowlist 33 -> 31 after two incomplete survivor mappings

**Design reset — 2026-07-29.** Return to ideation and re-cut the allowlist, baseline, AC-1, and
AC-3 to the 31 clause-complete deletions. Restore `Verification matrix in review body` and
`Refactoring PRs — API surface diff` byte-for-byte. This is the captain-approved fail-closed
boundary, not added scope: no replacement prose, paid/model path, 5b claim, fa, or sk work is
authorized.

## Stage Report: ideation (cycle 2 — design reset)

- DONE: Verified both validation findings against exact rejected code head `ee127c1`. The
  completed verification-matrix table requirement and the exhaustive newly-public API symbol
  listing lack clause-complete surviving authority.
- DONE: AC-1 — re-cut the deletion allowlist to the 31 rows whose normative clauses have complete
  surviving workflow or explicitly required-reference authority.
- DONE: AC-2 — moved parent lines 1867 and 1869 into the fail-closed retention table, making ten
  retained rules; implementation must restore those two bullets byte-for-byte with the original
  eight.
- DONE: AC-3 — changed the governing end-value baseline from `41 -> 8` / 33 deletions to
  `41 -> 10` / exactly 31 deletions, with non-31 deletion count remaining an explicit falsifier
  unless fresh head drift is re-audited and approved.
- DONE: AC-4 — preserved the same four SKILL-coupled local contract suites; no test, runtime, post,
  benchmark, or replacement-authority work was added.
- DONE: AC-5 — preserved the zero-paid/model/eval/ablation boundary and made no 5b acceptance
  claim.
- DONE: Kept the 30-minute implementation appetite plus 15-minute tolerance. Validation found the
  original implementation used 17 minutes and the new cut is narrower, so the estimate is not
  invalidated.
- DONE: This correction narrows rather than expands the captain-approved task: two proposed
  deletions are withdrawn, two original bullets are restored, and no new prose or authority is
  introduced. fa, sk, and 5b remain parked.
- SKIPPED: Product edits in this ideation turn. The rejected product commit remains evidence for
  the next implementation correction; this stage changed only the split-root entity.

### Summary

Re-cut the pure-restatement plan from 33 deletions/eight retained rules to 31 deletions/ten
retained rules after fresh validation proved two survivor mappings incomplete. The zero-paid,
single-file, no-replacement-prose scope and the original 30-minute plus 15-minute appetite remain
unchanged.

## Stage Report: implementation (cycle 2)

### Summary

Corrected rejected commit `ee127c1` narrowly by restoring the original
`Refactoring PRs — API surface diff` and `Verification matrix in review body` bullets
byte-for-byte. The final branch diff against `origin/main` changes only
`kc-pr-flow/skills/kc-pr-review/SKILL.md`: 41 Rules bullets become ten through exactly 31
deletions and zero additions.

### RED/GREEN and exact-head evidence

- DONE: Re-anchored the edit on the cycle-2 allowlist, ten-rule retention set, AC-1 through AC-5,
  and the original no-information-removal boundary before editing.
- DONE: The corrected pre-edit contract failed for the intended reasons at `ee127c1`:
  `current Rules bullets=8`, `numstat=0 33`, and both validator-named retained titles were
  missing (`exit 1`). No test or contract file was added or changed.
- DONE: Restored only the two validator-named parent lines, in their original order and text. An
  exact retained-line comparison against `origin/main` is empty for all ten rules; their extracted
  lines hash to
  `7e4563ed329506102d6a84262a5ade3fa2c6eee8420f30e41fdc593fb7faa30f`.
- DONE: The corrected contract is GREEN: baseline/current Rules count is exactly `41 -> 10`;
  `git diff --numstat origin/main...HEAD` is exactly
  `0  31  kc-pr-flow/skills/kc-pr-review/SKILL.md`; `git diff --check` exits 0.
- DONE: Final code commit is
  `ab2a6f6c98f5660bf3d81f5cf3718ea5992678ce` on
  `spacedock-ensign/redundant-rule-removal`. The baseline/target skill blobs are
  `45ba8359f866f8d4b41c960b805230b3e7283579` ->
  `8efe01ae3f89552fb3b24ad4a72ad8b9db71d090`.
- DONE: Final name-status contains only
  `M kc-pr-flow/skills/kc-pr-review/SKILL.md`; the committed code worktree is clean.

### Prior-finding disposition

- DONE: CLOSED — `Refactoring PRs — API surface diff` is restored byte-for-byte, so the
  exhaustive newly-public-symbol inventory and unintentional-exposure clauses remain explicit.
- DONE: CLOSED — `Verification matrix in review body` is restored byte-for-byte, so the completed
  matrix-table and replaces-ad-hoc-prose clauses remain explicit.
- DONE: No replacement prose, authority rewrite, or other rule edit was introduced.

### Required local contract suites

All four commands ran from the code worktree repository root and exited 0:

- DONE: `bash scripts/skill-frontmatter-lint.sh` — checked 35 `SKILL.md` files; all valid.
- DONE: `bash kc-pr-flow/scripts/cross-model.test.sh` — 68 passed, 0 failed.
- DONE: `bash kc-pr-flow/scripts/review-architecture-diagrams.test.sh` — 43 passed, 0 failed.
- DONE: `bash kc-pr-flow/scripts/review-shadow.test.sh` — 213 passed, 0 failed.

### Acceptance and stop outcome

- DONE: AC-1 — the cycle-2 allowlist contains only the 31 clause-complete deletions; the two
  incomplete-survivor rows are no longer deleted, and no surviving authority or reference changed.
- DONE: AC-2 — all ten fail-closed rules match their parent lines byte-for-byte.
- DONE: AC-3 — the final cut is exactly 41 to ten Rules bullets and `0 additions / 31 deletions`
  in one `SKILL.md`.
- DONE: AC-4 — all four required local contract suites exited 0 without test adjustment.
- DONE: AC-5 — implementation used static source/git inspection, the two-line restore, and the
  four named deterministic local suites only.
- DONE: No stop condition fired: the two exact restores satisfy the corrected plan without scope
  expansion.
- SKIPPED: Paid models, model calls, evals, E2E, runtime/post suites, benchmarks, 5b, fa, and sk,
  as required.

## Stage Report: validation (cycle 2)

### TL;DR

**PASSED** at exact code commit
`ab2a6f6c98f5660bf3d81f5cf3718ea5992678ce`.
No findings. Both prior material findings are **CLOSED**, all 31 remaining deletions have
clause-complete surviving authority, all ten fail-closed rules match `origin/main`
byte-for-byte, and the four required deterministic suites exited 0. No product file was
modified during validation.

### Evidence block

- Lenses: Markdown-only installed skill-instruction contract. Correctness **PASS** (0 findings);
  manifest/back-compat **PASS** (0 findings). Security, silent-failure, type-design, concurrency,
  and resource-lifecycle did not fire because the diff changes no auth/trust boundary, error or
  input handling, type, async/shared-state, process/handle, or executable surface.
- Diff coverage: N/A — prose-only diff, no executable surface.
- Adversarial: N/A — this deletion-only prose diff has no executable behavioral guard to break;
  the stage-specific dispatch also prohibits model/eval/ablation, runtime/post, and E2E paths.
- Cross-model: NOT RUN — the stage-specific zero-paid boundary prohibits model calls. The required
  deterministic `cross-model.test.sh` contract suite ran and passed 68/68; no cross-model or 5b
  acceptance is claimed.
- E2E: N/A — ideation excludes E2E for this prompt-document de-duplication with no wiring claim,
  and the stage-specific dispatch prohibits it.

### Prior-finding disposition

- **CLOSED — `Refactoring PRs — API surface diff`.** The full retained line from `origin/main`
  and `ab2a6f6` has identical SHA-256
  `3e20ddff950359e6edcecfc14028169a9f81806dfa577fc71849f4441bf57173`.
  The exhaustive newly-public-symbol inventory and unintentional-exposure clauses are present
  without replacement prose.
- **CLOSED — `Verification matrix in review body`.** The full retained line from `origin/main`
  and `ab2a6f6` has identical SHA-256
  `d17678ce34ecb0d0b933f8777a54d169a301494486dd227c5f88449183d071c1`.
  The completed-matrix-table and replaces-ad-hoc-prose clauses are present without replacement
  prose.
- **OPEN: none. NEW: none.**

### Acceptance criteria

- **PASS — AC-1, "Removed rules retain complete authority."** Fresh direct reads independently
  re-resolved all 31 rows. The surviving groups are:
  - main workflow: PR Summary (`Step 2.6` + `§6-pre`), confirmation (`§6c`), diagram opt-in and
    validation (`§6b-arch` + Step 7), dynamic repo detection (Steps 1/3), ownership (Step 3),
    CODE/DOC/NEW classification (Steps 5/6), cross-model reconciliation/arbitration/convergence
    (`Step 4-Codex`, `§5.5`, `§5.6`, `§6b-cm`), non-deferrable learning (Step 8), tests as
    verdict evidence (`§4.5t`), and external-system A/B COMMENT default (`§4.5p` + `§6b¾`);
  - required `gh-api-patterns.md`: temp JSON with `--input`, one batched submission, and PR-author
    tagging;
  - required `review-triage.md`: always-dispatched comment analyzer, refactor behavioral
    equivalence, and stale-reference audit;
  - required `compliance-audit.md` / `learned-patterns.md`: skills-as-reference-only and the
    zero-agent pre-emit gate plus at-most-one whole-diff adversarial pass;
  - required `knowledge-capture.md`: D2 threshold/confirmation, surgical edits,
    project-scoped `.claude/review-lessons.md`, separate D2 commit, and specific/testable rules;
  - required `test-execution.md`: failure-to-event mapping and mandatory worktree cleanup;
  - required `break-point-probe/SKILL.md`: evidence level, residual uncertainty, and honest
    degradation requirements.
  No cited survivor is weaker, conditional relative to the deleted rule, inside the deleted
  region, or changed by this branch.
- **PASS — AC-2, "Unique and stronger rules remain."** Baseline and target extraction found all
  ten retained titles and compared each full line exactly. Both ordered ten-line sets hash to
  `7e4563ed329506102d6a84262a5ade3fa2c6eee8420f30e41fdc593fb7faa30f`.
- **PASS — AC-3, "The cut is measurably smaller without information removal."** Fresh
  `origin/main...ab2a6f6` evidence is one file,
  `0 additions / 31 deletions`; Rules bullets are exactly `41 -> 10`; `git diff --check` exits 0.
  Baseline/target skill blobs are
  `45ba8359f866f8d4b41c960b805230b3e7283579` ->
  `8efe01ae3f89552fb3b24ad4a72ad8b9db71d090`.
- **PASS — AC-4, "Existing skill contracts remain green."** Fresh runs from the exact code
  worktree exited 0: `skill-frontmatter-lint.sh` checked 35 skills;
  `cross-model.test.sh` reported 68 passed / 0 failed;
  `review-architecture-diagrams.test.sh` reported 43 passed / 0 failed; and
  `review-shadow.test.sh` reported 213 passed / 0 failed.
- **PASS — AC-5, "The zero-paid boundary is preserved."** Validation used static git/source
  inspection and the four named deterministic local suites only. It invoked no paid/model/eval/
  ablation, runtime/post, benchmark, E2E, 5b, fa, or sk path and makes no 5b acceptance claim.

### Exact-head and scope evidence

- Code worktree branch: `spacedock-ensign/redundant-rule-removal`; clean exact head:
  `ab2a6f6c98f5660bf3d81f5cf3718ea5992678ce`.
- Fresh `origin/main` and merge base:
  `b87171c40d595c7c60d4efa3ee16d0b4249cd9d1`.
- `git diff-tree --name-status` reports only
  `M kc-pr-flow/skills/kc-pr-review/SKILL.md`; `git diff --numstat` reports
  `0  31  kc-pr-flow/skills/kc-pr-review/SKILL.md`.
- Changed-file mapping: the sole changed file serves AC-1 through AC-4. No changed file is
  unmapped; no test, harness, authority, reference, or other product surface changed.

### Recommendation

**PASSED.** Advance from validation. The corrected implementation closes both prior material
findings without new findings or residual product risk inside the authorized zero-paid,
single-file scope.

### Feedback Cycles

- Cycle 1: REJECTED — two incomplete survivor mappings; design reset from 33 deletions/eight
  retained rules to 31 deletions/ten retained rules.
- Cycle 2: PASSED — `2 closed / 0 open / 0 new`; no further correction round requested.
