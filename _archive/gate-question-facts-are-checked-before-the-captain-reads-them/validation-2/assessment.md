# Independent validation, cycle 2

Verdict: **PASSED** at PR #855 head `8d083d3b9b2c48c10e32cee3e5ef693b374c6183`. This fresh validator reran the commands and falsifiers; the earlier reports were inputs, not proof. The prior rejection is resolved by an actual listing replay at PR #856 head `455846c6d30d4ab650c1c4503bc591722231586d`. No product bytes changed.

Started: 2026-11-12 19:13 Asia/Taipei. Completion time is recorded in cleanup.json.
Profile: Pilot; independent assessment only. Gate, review, readiness, merge, release and adoption remain FO/Captain work.

## Identity and scope

The owned diff is four files relative to prerequisite PR #853 head `d79053d0836c558a9269f9cf1ba222933935b820`; origin/main observed locally was `8ce0eb6050c889b21baccf50fec35231bc888d66`. The main-to-head diff also contains the prerequisite's changes and is not attributed to this task. `identity.json` verifies exported, pinned and clean-worktree bytes for every owned file. Both PRs were freshly read and remain open Drafts at their dispatched heads (`pr-status.json`, `sibling-pr-status.json`).

Product executions use git archive exports. AC-1 initializes a standalone fixture repository inside the export only because the listing also asks Git for its scratch namespace; its inert local origin is confined to that fixture. No linked worktree, shared configuration, source branch, installed binary or live state was modified.

## Acceptance

- **AC-1 PASSED:** `ac1/result.json` and `captain-ac1/result.json` show the real native query and sibling listing both recognizing 5/5 held offers at the first pinned state, and 0/5 at the control state. Both listing processes exit 0; the criterion's flag adapter exits 1 and 0. The scratch-only hold-removal mutant still reads five native held rows, prints zero held offers, and is rejected by the unchanged acceptance assertion (exit 1). All ten original task files are byte-identical to their historical state blobs.
- **AC-2 PASSED:** `captain-replay.json` records one new mark for each false merge question through actual question subprocesses, with and without summary; the runner also asserts that the matched sentence is the specified false claim. Exit 0 matches the prerequisite. English-only matching loses the mark. The two contradicting primary records were reread directly at the recorded historical states; their text is not retained here.
- **AC-3 PASSED:** the recorded true controls add 0, 1 and 0 marks. The one true but uncited title deliberately remains marked until its saved existing output is cited; missing-file citation is marked, an existing unverified marker is not duplicated, and repeated writes are identical. Removing the file-existence check makes the bad citation pass and fails acceptance. This is the approved false-positive tradeoff, not a truth guarantee.
- **AC-4 PASSED for the accepted corpus behavior:** 111 questions produce 11 matches in 9 questions, including all four known false occurrences. English-only matching catches 0/4. The prototype counts 505 spans; the approved shared sentence splitter counts 549. Candidate output must be reported as 549, not 505. This denominator difference does not change the matching or false-claim results and follows expansion item 3.

The four original deterministic criterion commands and supplied evidence runners were rerun, including original prototype commands. `replay.json` describes the historical prototype separately; the actual dependent listing is `ac1/result.json`. `implementation-rerun.json` retains the supplied older runner's historical not-run label; it is not this validation's AC-1 verdict. The follow-up helper is rerun as `run-ac1.py`, with archive/fixture setup replacing its clone setup; its observed assertions and mutation are preserved.

## Findings and disposition

No new rejection finding. Previous F1 was **Needs decision, kind evidence or form**: the required sibling replay was absent, with no demonstrated owned build defect. Captain amendment 2 retained AC-1 and authorized this recheck; the now-executed listing and falsifier close that finding. No aim or scope, design, build, or evidence or form rejection remains.

The initial replay setup failed because PATH Python lacked the prototype's PyYAML dependency, then the archive-only listing lacked the Git root/origin required by an unrelated scratch inventory. The final fixture supplies that metadata in its own standalone repository and uses declared system Python for the historical prototype. No expected product result was relaxed. `setup-limits.json` and setup error logs preserve these environment failures without private source text.

## Sufficiency, necessity and limits

The bounded outcome is automatic disclosure on the two command paths plus visible held-task facts from the sibling listing. The prerequisite adds no scope mark; candidate adds one at the same exit in both ask and PR-body probes. `count-necessity.json` independently measures zero Chinese count sentences in the base and four in the candidate. The two source files, focused tests and authorized decision record each serve accepted behavior.

The listing fixtures contain only the five offered original tasks per snapshot; unrelated extensions are disabled while stage/gate configuration is preserved. Native query and actual listing processes are unmocked. Other task-list duties, all historical tasks, and live operator behavior are not accepted by this replay. Question commands use generic valid gate metadata; the check-path test uses the existing read-only GitHub fixture, not a live merge request.

A second independent corpus and effects on Captain answers remain **not verified**. Plain dialogs still bypass these commands; the accepted design relies on consulting the listing. The model reader is excluded by approval and was not rerun. The seven true matched corpus sentences remain an accepted limitation. File existence proves neither citation relevance nor truth. No hosted-required-check settlement, merge, release, adopter rollout or installed runtime behavior is claimed.

## Checks and retained documents

`tests.json`: delivery 230 discovered (229 passed, one optional historical-presentation skip), learning 50 passed, ADR-documentation nine passed. These are the three selected affected suites, not the whole repository suite. The Captain script additionally runs nine scope tests. The optional skip is separate from the fully executed AC-1 listing replay.

`checks.json`: repository lint, ADR lint, number guards, comment ratio, design surfaces, dispatch records, document impact and diff check all exit 0. `number-guards-fresh.log` supersedes the initial stale-ref warning with an authorized successful refresh. ADR lint checks 72 files, zero legacy, with --since d79053d0836c558a9269f9cf1ba222933935b820 --require 0082. The installed Codex package used here has identical checked script bytes to the dispatch's Claude install (`identity.json`).

All seven document dispositions were checked against the rerun scan: 0082 updated; 0044 optional summary, 0051 round hold, 0062 quoted approval, 0071 bound check, 0072 prior disclosure, and 0078 prerequisite merge-result behavior unaffected for their recorded reasons (`doc-verdicts.json`). ADR 0082 matches the approved question and amendment 1; amendment 2 changes budget, not product semantics. Both added comments point to that ADR. Comment ratio: 2/163, 1.2%, under 5% (`comments.log`).

No-match check output remains 89 words; one matched claim changes 89 to 98 (`captain-replay.json`). Startup, idle and archive text is unchanged. CI cost per PR was not measured; no CI definition changed. RoboRev and delivery remain FO-owned.

## Captain acceptance: four steps

Prerequisites: the named clean candidate checkout and historical Git objects, this committed state evidence, Python 3.11 on PATH, /usr/bin/python3 3.9.6 with PyYAML 6.0.1 for the historical prototype, Git/tar, the named installed package, and /Users/kent/.local/bin/spacedock 0.27.2. No login, model call or network is required. There is no changed graphical screen; observable command output substitutes for a screenshot.

Run unchanged in a fresh Bash shell, from any directory:

```bash
/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/gate-question-facts-are-checked-before-the-captain-reads-them/validation-2/acceptance.sh /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/gate-question-facts-are-checked-before-the-captain-reads-them/validation-2 /tmp/gate-facts-validation2-ghuxn5s7/captain
```

1. Pin and export. Expected: `Step 1: pinned candidate; three source exports ready`.
2. Disclosure replay and falsifiers. Expected: `Step 2: disclosure replay passed; 4 of 4 known false claims marked`.
3. Real sibling listing and hold-removal falsifier. Expected: `Step 3: held listing 5 of 5; control 0 of 5; hold-removal mutant rejected`.
4. Focused tests and authorized decision record. Expected: `Step 4: nine scope tests and required ADR lint passed`.

Run exactly as above, exit 0; observed output is `captain-acceptance.log`. It completes in under five minutes and deliberately retains scratch until evidence is committed. After committing the output, remove only the exact owned root shown in `scratch.json`; this validator's removal and verified absence are in `cleanup.json`. A later rerun creates fresh scratch at the same absent path and owes its own cleanup.

Public evidence contains aggregate observations, public source identities, test output and reproducible helpers only. Original private task names, titles, rulings and raw runtime output stay outside this task folder and are deleted with owned scratch. `privacy-check.json` is a narrow identifier check, not proof against every possible disclosure.

