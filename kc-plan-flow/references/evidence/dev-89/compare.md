# Compare — Run A (borrowed) vs. Run B (fallback) vs. Run C (refusal)

## Issue cut diff (Run A vs. Run B)

| | Run A (borrowed) | Run B (fallback) |
|---|---|---|
| Issue count | 3 | 3 |
| Titles | 1. Write the three ship-flow contract sentences into the runtime README<br>2. Pin the three contract sentences to a contract test<br>3. Confirm Kent stops re-asking the three questions across 3 PRs | identical |
| blockedBy edges | 1→(none), 2→1, 3→{1,2} | identical |

**No diff.** Both runs converge on the same 3-issue workflow-step split with the same blockedBy graph. Neither
run's Project would fail a lint rule the other passed on issue-cut grounds alone — the underlying decomposition
is the same regardless of which path produced it.

## Per-field verbatim-vs-rewritten diff

| Brief field | Run A rewritten/new sentences | Run B rewritten sentences |
|---|---|---|
| `## The problem` | 1 rewritten (because/impact, grounded from station 2) + 1 new (repo-history framing) | 0 |
| `User value:` | 0 rewritten + 1 new (the one-line reduction) | 0 (reused unchanged) |
| `## Accepted outcome` + `Falsifier:` | 2 rewritten (Tiny-Acts + Validation-Measures collapsed) + 1 new (`Falsifier:` line) | 0 |
| Issue cut (titles/count/blockedBy) | 0 | 0 |
| Issue *body template* (not an AC-1 field, tracked for completeness) | wholesale substitution: skill's As-a/Given-When-Then template discarded entirely for this repo's Brief shape | no competing template ever produced — fallback questions target Brief shape directly |

## Falsifier evaluation

- **poc_falsifier ("a borrowed output needs more than one sentence rewritten to fit its field"):** hit twice in
  Run A — `## The problem` (1 rewritten + 1 new = 2 changes) and `## Accepted outcome` + `Falsifier:` (2
  rewritten + 1 new = 3 changes) both exceed "more than one sentence." `User value:` and the Issue cut stay at
  or under the threshold (0–1 change each). **Run A: falsifier hit on 2 of 4 fields.**
- **poc_falsifier ("the fallback Project fails a lint rule the borrowed one passed"):** not evaluable by the
  worker directly — `plan-lint.py` runs on Linear Projects the FO writes, which is outside the worker's seat.
  On content alone, Run B's Project is issue-cut-identical to Run A's and every field required 0 rewritten
  sentences, so there is no known content difference that would make Run B fail a rule Run A passes. **No
  falsifier hit observable from the worker's seat; the FO's `plan-lint.py` run against both Linear Projects is
  the authoritative check.**
- **Input B / refusal falsifier ("input B reaches a Project, a profile, or a receipt"):** not hit — Run C
  produced a refusal with three named gaps and one discovery assignment, no Project/profile/Issue/receipt. See
  `run-C.md`.

## Why the two paths diverge

`problem-statement`, `epic-hypothesis`, and `user-story-splitting` each carry a downstream output template
(empathy narrative bullets; if/then + Tiny-Acts + Validation-Measures; As-a/Given-When-Then) that was designed
for a different artifact than this repository's Development Brief prose. Filling a Brief field from those
templates costs a template-to-prose conversion every time, which is exactly where Run A's rewritten and new
sentences appear. The fallback questions in `kc-plan-flow/references/dialectic.md` were authored with the
Brief's own prose shape as their direct target, so a fallback answer lands in its field with no conversion step.
The *decomposition logic* (which pattern, how many pieces, where the boundaries are) is identical either way —
the difference is entirely in output-template shape, not in analytical content.

## Receipts

No `sha256` receipts are recorded here: `plan-lint.py` and the Linear Project writes for both runs are the First
Officer's seat (see the work item's Seat split), not the worker's. This file and `run-A.md` / `run-B.md` /
`run-C.md` are the worker's markdown deliverable for the FO to write, lint, and record receipts against.
