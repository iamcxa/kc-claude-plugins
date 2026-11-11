# Budget implementation — completed local candidate

Candidate: 5bf7cf78866a2f0f6376c15b59fc400519c5ffeb (filled after the local commit).
Base: e8664a72b0f904e5dda3c391d52ab3abaca876b4.
Branch: spacedock-ensign/budget-overrun-holds-and-findings-meet-non-goals.
Commands and measurements: 2026-11-11. The prior implementation-1 evidence is
preserved as the earlier, held round; this folder supersedes its acceptance claims.
No product push, PR, RoboRev, hosted CI, merge, version edit or release was run.
FO owns those delivery steps. CI cost was not measured; no CI trigger was changed.

## What changed and what remains outside

The original two cycle forms remain. A total cap accepts `at most N dispatches
total` (singular dispatch too), with digits or English one to ten, or `最多 N 次派工`
with digits. A numeric minutes clause may precede the countable part, separated
by comma or semicolon including Chinese punctuation. Mixed minutes remain visible
with `minutes not counted`; no time accounting is implemented.

`budget_dispatches` is the single counting rule: plain ideation, implementation
and validation records count once; a follow-up counts only if its out-of-fence
header names a symptom. Case/space-normalized `none`, empty and missing headers
do not count; body/fenced lines are not headers. A symptom beginning with the
letters none is still a named symptom. Special-role records do not count. A
pending saved record is replaced in place, not appended twice. At the cap is
allowed; the next record beyond it holds before build and is removed.

A hold defaults to keeping results, reporting remaining work and stopping
additions, unless the Captain replaces this outcome. Existing results survive
the actual dispatch fixture. Backlog presents Budget; ideation presents worth
answers. AC-7 is verbatim under amendment 4's Superseded text; AC-10 replaces it.
AC-11/12 cover amendment 3; AC-13 covers amendment 5.

## Verification and reproduction

`final-checks.py <assigned-worktree>` extracts all 28 Python run commands from
the unchanged `.github/workflows/kc-dev-flow-2-tests.yml`, uses Python -B and
PYTHONDONTWRITEBYTECODE=1, saves unpiped exits and logs, and asserts that the
base-to-candidate patch did not change during the run. `final/test-identity.json`
and `final/tested.patch` bind the tested bytes; identity-at-commit.json confirms
the final commit has those same bytes. The full final run is in final/;
earlier aborted or failed development runs are not acceptance evidence.

The local binary reports Spacedock 0.27.2; the declared installed plugin root is
/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3. Hosted CI pins both
the binary and plugin root to 0.27.2. The local transport tests exercised the real installed command; they
do not claim a hosted CI pass or the CI-pinned plugin-root execution. Test suite skips and
explicit Not run lines remain in the raw logs; none is promoted to a pass.

For a different machine, supply its actual checkout to the runner and replace
the declared binary/plugin paths with that installation. No provider login is
required for stubbed delivery/provider seams. `merge-transition-probe.py` runs
the real delivery_gate role check with existing external-provider stubs: an
old first record passes the merge ask, a newly admitted overrun holds without
writing the ask. This is AC-6 boundary evidence, not real GitHub state evidence.

`mutations.py <assigned-worktree>` caught 24 deliberate faults, each as an
assertion failure without errors in a fresh directory, bytecode disabled.
They cover forwarding, off-by-one, latest amendment/authority, old-record
admission, countable/uncountable reminders, Worth/seed requirements, total-form
parsing, all/no/body/prefix symptom counting, highest-cycle-as-total, mixed
minutes/notice, default/override, duplicate pending, omitted ideation, and the
workflow word count off by one either way. mutations.json names each test and
the mutation-*.log files preserve failures. red.log and nonempty-red.log show
new behavior failing before its corresponding implementation; nonempty-green.log
and the full final suites show the corrected behavior.

The laws suite is unchanged from base; its missing-import failures were fixed
only by deferring the new role_triggers imports to their check functions inside
the already authorized design_surfaces.py. No law fixture was changed.

## Test data and expected text — lines for independent validation

Captain amendments 4 and 6 authorize these intentional-behavior fixture updates.
Every existing test/function, assertion and negative case remains. The audit
JSON records original assertion counts/kinds and exact base/candidate hunks;
the retained assertions were also reviewed in the full diff. New acceptance
tests add coverage; they do not replace the older negative cases.

- test_pr_watch.py: 756 and 1583 replace old worth-question text; 1779 replaces
  the synthetic `one task` Budget with `one cycle per stage`; 1798 updates its
  deletion matcher, retaining the missing-Budget negative assertion. These four
  lines represent three failing tests; the seed write and delete are one fixture.
- test_delivery_gate.py: 2587 replaces the old worth-question prefix. This is
  the fourth failing test covered by amendment 4. Both product modules unchanged.
- test_sd_dispatch.py: 819/989/1049 change synthetic `one fixture` Budgets to
  `one cycle per stage`; 994 adds the required synthetic Design/Worth section to
  the shared parity fixture; 1063 updates the missing-Budget deletion matcher.
  All 171 existing assertions remain, including malformed/missing criteria,
  placeholders, missing Budget and native task transport negatives.
- test_design_surfaces.py: 86/329/354-355/361/364-375/379/394/406/435-436/1545
  replace synthetic Budget data and matching removal strings. 96-98/157-159/
  757-759/1233-1235/1553-1557/2180-2182 add required synthetic Worth/design data.
  Original seed-impostor/fence/placeholder and other negative assertions remain.
  255-279 are added acceptance tests, not fixture replacements.
- test_dispatch_stage.py: 288-289/348 expect the new stage Budget header, while
  preserving special-role bytes; 515-516 update the three expected questions.
  117-168 are new real-dispatch acceptance cases.
- test_role_triggers.py: 355-356 update the expected questions, 376 updates the
  measured expected word count from 51 to 46; 758-954 add Budget acceptance cases.

`test-fixture-audit.json` has all changed hunks at the final candidate. No test
assertion was removed or weakened and no negative case was dropped under this
permission. The laws, delivery_gate and pr_watch product modules have zero diff.

## Pinned state replays

pins.json identifies four exact state commits. `export.py` in the previous
implementation-1 folder exports committed task bodies and dispatch records;
the replay scripts use that export at /tmp/budget-implementation-2/corpus-md
(a link to /tmp/budget-implementation/corpus-md here). Large unrelated artifacts
are excluded identically from both checker arms. Re-export those pinned commits
on a fresh machine; do not substitute current mutable task files.

`replay.py <assigned-worktree> <task/ideation-1>` imports the current parser and
the saved base parser, injects Budget headers into throwaway historical records
to model admission after release, and overlays the pending record at each
committed revision. It does not change live history. First relay hold remains
implementation-2 at 42317d0c14d24228ddf08b6dd51f6575fc139bf4, naming
`PR #491 CI red at 20b316da plus contract additions since implementation-1`.
The base exits 0 there and has no role hold before d85ce152.

Archived fixed-form held/countable versus ideation's broad survey:
qnow 0/0 versus 7/7; relay 10/21 versus 11/23; web 0/0 versus 5/20.
The fixed forms exclude rounds, passes, ideation-prefixed prose, and missing
cycle units. Relay excludes review-keyword-invocations (the missing hold) and
llms-teaches-versions (never over its broad bound). This workflow holds zero
and has no countable cycles in 58 actual Budget-record tasks; the survey's 60
also counted a fenced placeholder and a stage-report Budget sentence. Every
difference is named in archive-replay.json; no unexplained denominator change.

`corpus-check.py` compares base and candidate over the exported four pins in
seed/default modes; corpus-check.json records all verdicts. No earlier diagnostic
is lost; every addition is the intended Worth or fixed-Budget check. These are
compatibility observations, not reacceptance of historical designs or artifacts.

`message-counts.py <worktree> <state> <revision>` uses the actual counting rule.
At amendment-5 dispatch commit 40cfa1ae5ca80069f6451ad1fda52397b8e886bd,
archived amendment-checked-when-written counts **5**, not FO's earlier 7: five
ordinary stages, six none messages, and two excluded special-role dispatches.
At that same pin release-rollout-reaches-adopters-and-laws-pin counts **7**:
two ordinary stages plus five named-symptom messages of nine total messages.
At ba7d022e180e160ec5b6fbeaa8da950f62317dee its added validation-1 raises
the latter count to **8** (three stages plus the same five named messages).
Both pinned JSON files include record names, normalized symptoms, body digests
and excluded special-role paths. This factual correction was sent to FO; no
counting rule was changed to force agreement with the earlier report.

## Reading cost and retained documents

word-count.py independently agrees with wc -w using a regex token count.
Workflow startup/resume grows 5939 to 6008 (+69), one quoted budget step.
Countable cycle dispatch adds 11 sampled words; uncountable adds 14; total-cap
dispatch adds 15 and the mixed Chinese minutes/cap sample adds 17. The sampled
overrun with `failure 2` adds 88 including summary/default. Longer Budget and
Symptom text has its own cost. Countable idle/merge forwarded reminder drops
51 to zero; ideation principles grow 643 to 687 (+44). word-count.json retains
samples. These are sampled lifecycle costs, not a claim of universal reduction.

Required ADR, number, comment and lint checks all exit 0 after the commit: 68 ADRs;
workflow 6008/6008 words; comments 12/422 (2.8%, maximum 5%); fresh state fetch
without the stale-reference warning on the final number-guard run.
doc-impact.json and doc-impact-verdicts.jsonl give each listed document a reasoned
updated/unaffected verdict; no independent second rule was added elsewhere.
ADR 0077 quotes the bound gate and amendments; ADR 0026 has its amendment link.

## This task predates its new design check

The installed 0.38.1 checker presents this already-approved task; the candidate
checker exits 1 because its existing Design has no literal `### Worth questions`
heading. Both outputs are saved as task-check-installed.log and
task-check-candidate.log. This is an additional historical compatibility refusal,
not a passed check or a product repair: no backfill of approved historical
designs was assigned. AC-9 is established by the missing/present-section fixtures;
the full local suites passed. FO should keep this old-task observation visible
when validating or choosing a later design backfill, rather than infer that all
historical designs were reaccepted.
