# Budget implementation handback — held

Candidate: `0243d34829634a218c3ba3302f3f6def7ea87b62`.
Base: `e8664a72b0f904e5dda3c391d52ab3abaca876b4` (fetched origin/main before editing).
Branch: `spacedock-ensign/budget-overrun-holds-and-findings-meet-non-goals`.
All measurements and commands below were run on 2026-11-11. No product push, PR,
RoboRev, hosted CI, merge, version edit or release was performed. CI cost was not
measured; no CI workflow or trigger was changed.

## Why held

1. AC-5 owes existing `test_pr_watch.py` and `test_delivery_gate.py` suites green.
   They produce four intentional-behavior fixture failures: three assertions use
   the old step-back questions; one seed fixture still says `Budget: one task`.
   Those files are absent from the design's allowed files. The dispatch says to
   stop and return to FO before adding a file; no changes were made to them.
   `pr_watch-final.log` and `delivery_gate-final.log` preserve the exact failures.
2. AC-7 says worth answers in backlog Gate content; the approved design explicitly
   says no backlog-gate addition and forces them at ideation. FO was asked before
   dependent document edits. Neither gate-content paragraph was altered; the
   record needs the Captain/FO's resolution before completion.

This is a saved partial candidate, not a passed implementation or deliverable PR.
The prepared PR text is `/tmp/impl-budget-overrun-holds-and-findings-meet-non-goals-pr.md`.

## Checks and limits

`checks.py <assigned-worktree>` runs the repository's five regression suites,
repository lint and installed ADR linter, saving unpiped exits in `checks.json`.
Observed: role 56 passed; design 222 ran, four skipped; dispatch 43 passed;
delivery 208 ran, one failed and one skipped; watch 135 ran, three failed.
After the final first-record ordering and combined-budget-heading adjustment,
`PYTHONPATH=kc-dev-flow-2/scripts python3 -B -m unittest test_role_triggers.BudgetTest`
passed eight focused tests (`budget-final.log`). The full regression run started
before those last adjustments, so it is not presented as a complete exact-candidate
rerun. Re-run it after scope authorization and the consumer fixture updates.

`python3 -B kc-dev-flow-2/scripts/lint-skills.py` and the installed 0.38.1
`adr_lint.py docs/adr --since <base> --require 0077` passed after the final edits
(`lint-at-commit.log`, `adr-at-commit.log`). At the committed candidate,
`number_guards.py check --workflow-dir <workflow> --task <entity>` passed with a
successful state fetch (`number-guards.log`), and
`comment_ratio.py <base> HEAD --workflow-dir <workflow>` measured 289 code lines,
11 comment lines, 3.8%, within the 5% maximum (`comment-ratio.log`).
`doc-impact.json` and `doc-impact-verdicts.jsonl` map all twelve listed documents.
All commands use Python `-B` and `PYTHONDONTWRITEBYTECODE=1` where spawned by a
runner; mutation directories are fresh and no bytecode is reused.

## Falsifiers

`python3 -B mutations.py <assigned-worktree>` caught eleven deliberate faults
(`mutations.json` plus named raw logs): lost budget forwarding (both forms), an
inclusive off-by-one hold, ignoring an amendment, ignoring admission by the first
record, retaining the countable reminder, losing the uncountable reminder,
inventing amendment authority, allowing a missing Worth section, allowing a
non-countable new seed, and README count off by either one word. Each changed
behavior fails a named existing/new acceptance test; errors do not count as kills.

## Pinned replays

`pins.json` names the four source clones and full commits. `export.py` extracts
only committed task bodies and dispatch records to `/tmp/budget-implementation/corpus-md`;
it deliberately excludes large unrelated artifacts. `replay.py <assigned-worktree>
<task/ideation-1>` imports the shipped candidate and saved base script, and explicitly
adds a Budget header to historical records to model admission after the release.
It does not edit live task records. Every relay revision is read with `--rev`;
the pending dispatch is overlaid as a throwaway record at that revision.

`relay-replay.json` confirms the first candidate budget hold at relay
`42317d0c14d24228ddf08b6dd51f6575fc139bf4`, implementation-2. Its Symptom is
`PR #491 CI red at 20b316da plus contract additions since implementation-1`.
The saved base returns 0 there and has no role hold before `d85ce152`.

`archive-replay.json` explains every broad-parser/fixed-form difference:
- qnow: broad 7 held / 7 countable; fixed 0 / 0. All seven budgets use passes,
  ideation-prefixed prose or a single implementation dispatch, not either fixed form.
- relay: broad 11 / 23; fixed 10 / 21. `review-keyword-invocations` begins with
  `one ideation, ...` and accounts for the missing hold; `llms-teaches-versions`
  says implementation/validation rounds and was never over its broad bound.
- web: broad 5 / 20; fixed 0 / 0. All twenty use rounds, ideation-prefixed prose
  or lack the required final cycle unit; five had exceeded the broad parser's bound.
- this workflow: 0 held, no fixed or broad cycle bounds, across 58 actual budget
  records with implementation/validation dispatches. The ideation survey's 60
  included two non-budget matches: a fenced placeholder in
  `_archive/seed-check-requires-schema-fields.md` and a stage-report `Budget:`
  sentence in `_archive/release-acceptance/index.md`. Neither can hold. This is a
  correction to the survey denominator, separate from narrower fixed syntax.

`corpus-check.py <assigned-worktree>` compares base/candidate `check_task` in both
seed and default modes over every exported committed task body in all four pins.
`corpus-check.json` records each verdict and new diagnostic. Every changed message
is one of the intended two new checks; no prior diagnostic disappears. Historical
new refusals are compatibility observations, not claims of past operator fault.
Artifact exclusions affect both arms; this is a checker verdict comparison, not
reacceptance of historical designs or their UI artifacts.

## Reading cost

`word-count.py <assigned-worktree>` independently compares `wc -w` and nonspace
regex token counts; `word-count.json` includes the actual sampled output.
Startup/resume: 5939 to 5973 words (+34). A countable dispatch sample adds 11;
an uncountable sample adds 14. A held `failure 2` sample adds 71, including its
budget summary; a longer Symptom adds its own words. The idle/merge forwarded
reminder on a countable task drops 51 to 0. Ideation worker principles grow
643 to 687 (+44). These replace the design's approximate drafted costs, not a
claim that all lifecycle costs fell. The one +34 workflow-budget entry quotes
the bound ideation gate and names loaded moments; gate-content resolution may
require recounting it.

## Additional exact-candidate merge boundary probe

`python3 -B merge-transition-probe.py <assigned-worktree>` ran the real
`delivery_gate.py` role-check path at 0243d34829634a218c3ba3302f3f6def7ea87b62,
with the existing external-provider stubs. The same committed countable task
past its implementation bound passes the merge ask when its first record lacks
Budget, and holds it without an ask when the first record carries Budget
(`merge-transition-probe.json`). This exercises AC-6 directly; it does not settle
the four AC-5 fixture expectations or establish real hosted-provider facts.
