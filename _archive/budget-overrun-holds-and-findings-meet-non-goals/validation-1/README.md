# Independent validation of PR 841

Verdict: **REJECTED** at `5bf7cf78866a2f0f6376c15b59fc400519c5ffeb`.
AC-9 has two reproduced missing-section bypasses. All other active criteria pass
at their stated boundary. No product bytes were edited. FO owns disposition and
any repair authorization; this report authorizes neither repair nor delivery.

## Identity and method

- Candidate exported with `git archive` from the assigned worktree into
  `/tmp/budget-validation-841/candidate`; no repository worktree created/removed.
- Base is common ancestor `e8664a72b0f904e5dda3c391d52ab3abaca876b4`.
  Observed `origin/main` was `546a136386c94c58e430c91a6f3457b38bd73880`;
  its later sibling changes are not deletions by this PR. `candidate.patch` is
  the pinned base-to-head diff. `export-integrity.json` matches all 1589 regular
  exported files to their Git blob hashes after execution.
- Reused the implementation's existing test/replay/mutation tools, independently
  ran them with fresh output paths, and checked their assumptions. Reproduction
  scripts beside this README retain those path-only adaptations. Git reads in
  the test runner and recount use the pinned source repository; executed Python
  comes from the exported candidate. `source-identity.json`, `full/test-identity.json`.
- `full-summary.json`: all 28 commands in the unchanged CI workflow exited 0.
  Skips remain: delivery gate 1, laws 1, dispatch records 1, release acceptance 4.
  `test_sd_dispatch.py` explicitly does not exercise model workers, human gates,
  delivery hook bodies or remote merge. Green command exits do not cover F1/F2.
- Local binary: Spacedock 0.27.2; plugin root 0.27.3. Hosted workflow pins both
  to 0.27.2. `pr-final.json` independently observes the exact head still OPEN and
  draft, with unit tests SUCCESS; docs deploy is SKIPPED. This is a provider
  observation, not execution of every hosted scenario or release evidence.
- No CI change; cost per PR was not measured. No product push, PR comment,
  review request, merge, version edit, provider model invocation or release.

## Findings

### F1 Material: a YAML comment bypasses the ideation section check

Released user and normal workflow: a pilot FO prepares an ideation design using
valid YAML `status: ideation # ready for review` and the supported PRFAQ layout.
The real Spacedock `status --read --json` reports `status: ideation`.
Observable harm: the candidate reports `stage is unknown, not ideation`, exits 0,
and calls a design with no Worth questions presentable. The plain-status control
exits 1. The user can reach the design gate without the promised required section.
Protected value: `value-ac[AC-9]` requires missing ideation Worth questions to
refuse; the approved ideation ruling says the check blocks the omission.
Trigger evidence: `worth-counterexamples.json` contains the complete inputs,
actual native reader outputs and candidate CLI exits; `worth-counterexamples.log`.
Source: `kc-dev-flow-2/scripts/design_surfaces.py:1104`, using the raw status
regex at line 49. The stage predicate is new in this candidate, although that
regex has older consumers. No `## Design` wrapper is required for the pilot
`Surfaces: none` PRFAQ route by the approved stage principles.

### F2 Material: an HTML comment supplies the supposedly present section

Released user and normal workflow: an ideation author leaves an HTML-commented
section scaffold in an otherwise presentable Markdown PRFAQ.
Observable harm: adding only `<!--\n### Worth questions\n-->` changes the missing
section's refusal (exit 1) to `design surfaces presentable` (exit 0), while the
rendered design still has no such section. This tests existence, not answer truth.
Protected value: `value-ac[AC-9]` requires a real missing section to refuse;
commented text is not the required visible design section.
Trigger evidence: the hidden-heading case in `worth-counterexamples.json` and
step 5 of `acceptance.sh`; the visible-heading control passes as expected.
Source: `kc-dev-flow-2/scripts/design_surfaces.py:1102-1105` calls
`outside_fences(text)` without excluding HTML comments before matching the heading.
No candidate correction was made for either finding.

## Criterion evidence and falsifiers

Each path below is relative to this validation-1 evidence folder.

- AC-1 PASS: real dispatch tests print exact Budget values and pending spent counts;
  `full/kc-dev-flow-2__scripts__test_dispatch_stage.py.log` and
  `mutation-forward-budget.log` (removing stdout forwarding fails both tests).
- AC-2 PASS: boundary, overrun and covering amendment recovery run through the real
  binary. `mutation-off-by-one.log` and `mutation-ignore-amendment.log` fail.
  Failed dispatch leaves no pending record and never calls the build spy.
- AC-3 PASS: `relay-replay.json`, `history-audit.json` independently bind the first
  hold to implementation-2 at `42317d0c14d24228ddf08b6dd51f6575fc139bf4`, with its
  actual Symptom. Base has no hold before `d85ce1527cbaa44d285e89e0c4f99a211e4ba964`.
  The base at the candidate first hold exits 0, the required negative control.
- AC-4 PASS: `broad-replay.log` reproduces the original denominators and
  `archive-replay.json` the fixed-form results. QNow 7/7 becomes 0/0; Relay 11/23
  becomes 10/21; Web 5/20 becomes 0/0. This workflow stays at zero held and has
  58 actual Budget records versus the broad survey's 60. `budget-line-impostors.json`
  identifies the release-acceptance stage-report sentence and the seed-check
  fenced placeholder. Every excluded budget is listed in `archive-replay.json`:
  rounds/passes, prefixed prose and absent cycle units are intentionally excluded.
  Relay's excluded review-keyword-invocations accounts for the one lost hold;
  llms-teaches-versions accounts for the other excluded countable task.
- AC-5 PASS: role, delivery and PR-watch suites pass; countable reminders disappear
  and uncountable reminders/other role events persist. Mutations retaining a
  countable reminder or losing the uncountable reminder fail their existing tests.
- AC-6 PASS: `merge-transition-probe.json` exercises real role checking inside the
  delivery checker with existing provider stubs: legacy headerless first record
  passes, new-admission overrun blocks the ask. Later headers do not enroll a
  legacy task. `mutation-ignore-first-header.log` fails on that negative case.
- AC-8 PASS: `adr.log` exits 0, 68 ADRs checked, including reserved 0077 and the
  ADR 0026 amendment. Exact command is in `required-checks.json`; read-only
  `GIT_DIR` and `GIT_WORK_TREE` bind `--since` to the export and source metadata.
  `adr-falsifier.log` is the base export with `--require 0077`, exit 1:
  `required ADR 0077 does not exist`.
- AC-9 FAIL: missing/present and fenced-heading fixtures pass, and the optional-
  section mutation fails, but F1/F2 are real additional false passes. The
  same-entry amendment Budget authority half passes, including invented text,
  mismatched case, wrong entry and fenced Budget controls
  (`mutation-invent-amendment-bound.log`).
- AC-10 PASS: workflow backlog presents Budget and ideation presents worth answers;
  the one +69 budget step quotes its accepted gate and later amendments and names
  loaded moments. `word-count.json` independently compares `wc -w` to regex counts:
  workflow 5939 -> 6008, ideation principles 643 -> 687; the exact sampled output
  strings and other lifecycle numbers are preserved. Both +/-1 word falsifiers
  are in `mutations.json`. Counts are sample costs, not a universal reduction.
- AC-11 PASS: English/Chinese totals, explicit mixed minutes, cap and cap+1,
  named messages, special-role exclusion and pending replacement run in the
  Budget tests. Total-form, inclusive-bound, highest-cycle, omitted-ideation,
  double-pending and lost-minutes mutants each fail (`mutations.json`).
- AC-12 PASS: default preserve/report/stop and Captain replacement clauses are
  exercised; real dispatch preserves the pre-existing result and removes only
  its pending record. Both missing-clause mutants fail; `acceptance.log` step 3.
- AC-13 PASS: named header counts; absent/empty/normalized-none/body/fenced headers
  do not. All/no/body/none-prefix mutants fail. Independent committed-state replay
  confirms archived amendment-checked-when-written = 5 and release-rollout = 7 at
  `40cfa1ae5ca80069f6451ad1fda52397b8e886bd`; the latter = 8 after validation-1 at
  `ba7d022e180e160ec5b6fbeaa8da950f62317dee`. See both message-counts JSON files.
  The implementation's correction of FO's earlier archived count of 7 is valid.

## Six amendments and test permission

Amendments 1/2 reframe the original question and fold the same worth questions
into this task. The later approved D1-D3 explicitly choose no extra Material-
finding event. Amendment 3 adds total caps and the hold default while deferring
minutes; amendment 5 resolves how its follow-ups count. Amendment 4 corrects the
obsolete backlog wording to the already-approved ideation gate. Amendment 6
allows stale synthetic data/expected strings to follow those rules; it does not
authorize dropping assertions or expanding product scope. No contradiction was
found between these rulings. Allowing the cap and holding the next dispatch
implements the approved first-overrun rule; the quoted default describes what
happens when the hold occurs.

`history-audit.json` verifies AC-7 moved byte-for-byte from state revision
`e4e16fda1e100e555490527acb1a0582cf9fa6d8` into amendment 4, appears there once,
and AC-10 is its fresh marked replacement. AC-11/12 and AC-13 have fresh ids and
name amendments 3 and 5. Installed design/amendment checker exits 0. New total-
cap syntax and exclusion details are the implementation choices explicitly
requested by the recorded follow-up checklist; they do not rewrite old criteria.

All changed test files, candidate line ranges, and individual permission verdicts:

- `test_pr_watch.py:756,1583,1779,1798`: expected worth wording and synthetic seed
  value/removal matcher only. No assertion weakened/removed; missing-Budget and
  role-event negative cases retained.
- `test_delivery_gate.py:2587`: expected worth prefix only. No assertion weakened/
  removed; downstream ask-order and refusal cases retained.
- `test_sd_dispatch.py:819,989,994,1049,1063`: synthetic seed values, Worth scaffold,
  and corresponding missing-Budget removal matcher only. All 164 Python `assert`
  statements compare identically as syntax trees; no assertion or negative case
  weakened/removed. The implementation's 171 is a different assertion-counting
  convention; the unchanged assertions, not that aggregate, establish retention.
- `test_design_surfaces.py:86,96-98,157-159,329,354-355,361,364-375,379,394,406,
  435-436,757-759,1233-1235,1545,1553-1557,2180-2182`: approved synthetic Budget/
  Worth data and matching removal strings. No old assertion weakened/removed,
  including placeholder/quote/fence/impostor negatives. Lines 255-279 add tests.
- `test_dispatch_stage.py:288-289,348,515-516`: expected stage-only Budget header
  and new worth wording. Existing exact-byte assertions and special-role cases
  remain. No assertion or negative case weakened/removed. Lines 117-168 add tests.
- `test_role_triggers.py:355-356,376`: expected questions and their word count.
  No old assertion/negative case weakened/removed. Lines 758-954 add Budget tests.

`test-audit.json` contains the exact diff hunks and each original test's assertion
sequence. Manual review checked meaning as well as counts. `test_laws_check.py`
and the delivery/pr-watch product modules have no diff. Laws runs 84 tests with
its existing one skip. Dispatch message 4 explicitly allows deferring the new
imports inside the already-owned design_surfaces.py; that is not extra product
scope taken under the fixture-only permission.

## Compatibility and implementation limits

The missing Worth heading on this already-approved task is reproducible:
`design-installed.log` exits 0; `design-candidate.log` exits 1. Four frozen corpora
in `corpus-check.json` add only the approved fixed-Budget/Worth diagnostics and
lose none of the older diagnostics. New design refusals: dev2 124, QNow 15,
Relay 38, Web 12, with per-file evidence in that JSON. These are historical
checker observations, not reacceptance of old tasks or proof of new-work flow.

This compatibility limit is real and consistent with AC-9's universal section
requirement: only the Budget hold was explicitly grandfathered, not the Worth
section check. It is not itself a new code-repair finding. It does mean old
approved designs can no longer pass this checker after an adopter upgrades;
FO must show that consequence when presenting delivery. Historical backfill,
revised old designs or a new exemption require their own authorized route and
were not performed here. F1/F2 independently reject this candidate regardless.

The parser checks fixed syntactic bounds and section existence, not truth of
Captain quotes, value of answers, actual work inside one dispatch, or elapsed
agent minutes. Those limits were explicitly selected. Total caps count ideation
records when the implementation/validation check runs; per-stage forms count
only implementation/validation numbers. Model execution and adopter delivery
remain outside this validation. The 14 doc-impact rows have a checked disposition
in `doc-impact-verdicts.jsonl`; comments measure 12/422 (2.8%) below 5% and every
added comment was read. Number guards pass after a network-enabled rerun; the
initial sandbox warning is preserved separately, not treated as a product fault.

## Captain acceptance script

Prerequisites: this machine's named repository contains the pinned candidate;
Python 3, Git, Bash, and `/Users/kent/.local/bin/spacedock` 0.27.2 plus the installed
0.38.1 ADR checker exist. The script creates only temporary exports and synthetic
repositories. There is no product screen; the observable surface is the CLI.

Run unchanged in a fresh shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/budget-overrun-holds-and-findings-meet-non-goals/validation-1/acceptance.sh
```

The file contains five exact steps: export pinned candidate; three budget boundary
tests; two real dispatch tests; missing-section/control plus lint/ADR; two missing-
section counterexamples. Expected for a corrected candidate is exit 0 and both
counterexamples held with exit 1. Observed on this head: steps 1-4 pass, both step-5
checks incorrectly exit 0, and the overall script exits 1. `acceptance.log` is
raw output and `acceptance-result.json` records the command and elapsed time.
The initial four-step script/log are retained with `-initial` names and are
superseded: their pass did not cover the newly reproduced boundaries.

This short script is not the full historical replay, hosted CI, model execution,
review, merge or adopter delivery proof. All acceptance and rejection evidence is
bound to this candidate, not future rebases or repairs.
