# Independent validation of PR #868

Verdict: **REJECTED pending F1 disposition**. Candidate `2661da44a77c2b2f93991a3968fb1515bb4e7132`; base `bfc53d82510006b52baf41569c1e25176e99d87a`; frozen public task state `92c5db58613592dd25ae54f1184249fafbb3899d`. Started 2026-11-13 23:27:19 Asia/Taipei (clock.curr_time UTC converted +08:00). This is an independent validation; no candidate product edit, product push, review request, PR comment or worktree metadata creation/removal.

## Outcome and disposition

All ten named acceptance criteria pass at this candidate (`acceptance.json`). Decisions D1–D5 match the Captain's exact ideation-gate approval: added grammar and unchanged legacy parsing; Pilot default two with no implicit Prod cap; budget-only design preflight; ADR 0085 extends 0077/0080/0084; round results use gate outcomes or the following boundary. The changed mechanisms are sufficient for the replay and fixture journey and each retained scope part maps to those decisions or its required tests/ADR. The -2 workflow-word cut is enforced, not slack. No new production obligation was introduced.

F1 is **Needs decision**, not a claim that POC stage routing broke. Released user and normal workflow: an FO derives a POC README from the shared template and runs the repository CI suite. Observable harm: this candidate's CI unit-test job exits 1 on the new approved budget wording, so a green delivery claim is unavailable. Affected boundary: `contract[kc-dev-flow-2/scripts/test_poc_readme.py#DeriveTests.test_the_source_derives_to_four_stages_that_never_route_through_ideation]` checks four POC stages plus absence of stray ideation wording. Trigger: `test_poc_readme.py` passes 9/9 at base and fails 1/9 at candidate; its four-stage assertion still passes, while the blanket textual assertion at line 88 rejects `[N ideation, ]`. Hosted run https://github.com/iamcxa/kc-claude-plugins/actions/runs/43452561375/job/131978235065 reports the same failure. The test/compatibility repair may touch a file outside the approved ten-file list; FO owns the disposition and repair authorization. No repair was performed.

## Checks and falsifiers

The four requested suites used their direct unittest entry points, as CI does: role 63, dispatch 56, timeline 13, design 234; **366 run, 362 passed, four existing optional historical-corpus skips**. The authoritative dispatch result is `logs/suite-dispatch-worktree.log`, run unadapted after FO explicitly allowed the assigned candidate worktree; before/after porcelain files are empty. The other three ran from the exact git archive. `tests.json`, the four suite logs and `candidate-sha256.json` bind those claims to bytes.

The six real archived-task replays return 0/1/0/0/1/1. A bound of two holds pending ideation-3; three allows it. A legacy Pilot budget allows the second and holds the third; the real dispatch test also proves Prod permits the third and unbuilt held records are removed without invoking the builder. Removing the grammar/default independently permits the same third dispatch (`logs/replay-no-grammar.log`, `logs/replay-no-default.log`). Four legacy grammar dictionaries are unchanged from base, as printed in `logs/captain-acceptance.log`.

The real three-round timeline is 43.6/562.2/97.0 minutes with withdrawn/revise/approve and concrete starts/ends (`logs/timeline-replay.log`). The refreshed public corpus has 249 tasks, 24 text changes, zero exit changes (`logs/base-comparison.log`). Across 170 archived tasks, 192 ideation rounds match dispatch counts; no round lacks an end, and three late-committed rounds have zero minutes (`logs/rounds-census.log`). These are current reruns, not copied ideation/implementation totals.

Ten targeted source mutations each fail the corresponding criterion's check (`mutations.json`, `logs/verified-mutation-*.log`), with passing dispatch/lint/ADR controls. Every mutation targets changed code or wording. The corpus comparator detects 15 changed exits under the over-holding mutation; removing round output yields 144 count mismatches; restoring the prose hold produces 6101 vs 6097 words; removing an ADR pointer fails the linter. The three dispatch mutation checks use copied tests with only their fixture Package-root note mapped to the candidate worktree, as required by the existing temporary-path policy; all three positive controls pass first. Their assertions and tested mutated executables are retained for reproduction.

## Commands rerun

In these historical command spellings, `C` is the exact candidate archive, `B` the base archive, `S` the frozen state clone, `V` this evidence directory, `X` the dispatched scratch, `WT` the assigned candidate worktree and `P` `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts`. Temporary roots were removed after retaining evidence; use the acceptance command below for a durable replay. `commands.json` holds absolute argv, exit and output paths.

- `python3 -B "$C/kc-dev-flow-2/scripts/test_role_triggers.py"` — exit 0; 63 tests.
- `SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B kc-dev-flow-2/scripts/test_dispatch_stage.py` from `WT` — exit 0; 56 tests; clean before and after. `TMPDIR` was the assigned scratch's `tmp/`.
- `python3 -B "$C/kc-dev-flow-2/scripts/test_task_timeline.py"` — exit 0; 13 tests.
- `python3 -B "$C/kc-dev-flow-2/scripts/test_design_surfaces.py"` — exit 0; 234 tests, four optional historical skips.
- `bash "$V/replay.sh" "$C/kc-dev-flow-2/scripts" "$X" merge-ask-holds-missing-clauses "<budget>" <round>` — the six exact budget/round arguments and exits are in `logs/replay-1.json` through `logs/replay-6.json`.
- `python3 -B "$C/kc-dev-flow-2/scripts/task_timeline.py" "$S" merge-ask-holds-missing-clauses` — exit 0; three timed design rounds.
- `python3 -B "$V/compare_budgets.py" "$B/kc-dev-flow-2/scripts" "$C/kc-dev-flow-2/scripts" "$S"` — exit 0; no exit changes.
- `python3 -B "$V/rounds_census.py" "$C/kc-dev-flow-2/scripts" "$S"` — exit 0; no mismatched counts or missing ends.
- `python3 -B "$C/kc-dev-flow-2/scripts/lint-skills.py"` — exit 0; 6097 of 6097 words.
- `python3 -B "$V/word_counts.py" "$X"` from the candidate archive — exit 0; `logs/word-counts.log` records each reading moment: whitespace workflow -2, normalized startup -2, design-definition -4, Pilot build/check output +6, design output +23, timeline growth per actual example.
- `python3 "$P/adr_lint.py" docs/adr --since bfc53d82510006b52baf41569c1e25176e99d87a --require 0085` from `WT` — exit 0; 78 ADRs checked.
- `python3 "$P/number_guards.py" check --repo "$WT" --workflow-dir "$STATE/.." --task "$STATE/budget-form-counts-ideation-rounds-and-times-each-round.md" --head 2661da44a77c2b2f93991a3968fb1515bb4e7132` — exit 0 after an authorized narrow state-ref fetch, no stale-ref warning; initial sandbox warning retained separately.
- `python3 "$P/comment_ratio.py" bfc53d82510006b52baf41569c1e25176e99d87a 2661da44a77c2b2f93991a3968fb1515bb4e7132 --workflow-dir "$STATE/.."` — exit 0; 117 code/3 ADR-pointer comment lines, 2.6% within 5%; all added comments read.
- `python3 "$P/doc_impact.py" bfc53d82510006b52baf41569c1e25176e99d87a 2661da44a77c2b2f93991a3968fb1515bb4e7132 --json` — exit 0; all 18 documents have implementation dispositions. Source template updated; adopted copies and historical ADRs retained as scoped.
- `python3 "$P/dispatch_records.py" "$STATE/budget-form-counts-ideation-rounds-and-times-each-round"` — exit 0; four complete records; implementation requirements trace to accepted decisions/criteria.
- `python3 -B "$X/mutations.py"` from the candidate archive — exit 0; ten expected negative checks; the script's commands and controls are retained.
- `python3 -B "$C/kc-dev-flow-2/scripts/test_poc_readme.py"` and the same command under `B` — candidate exit 1, base exit 0. This one additional suite is justified by the observed CI failure; no other unrelated suite was run.
- `gh pr view 868 --repo iamcxa/kc-claude-plugins --json number,url,state,isDraft,headRefOid,baseRefName,statusCheckRollup` and `gh run view 43452561375 --repo iamcxa/kc-claude-plugins --log-failed` — read-only; PR remains OPEN/Draft at the candidate, unit-test check fails; `pr.json` and `logs/ci-failed.log`.

## Captain steps

No user-visible screen changes. Run this one command from any working directory. It depends on this public state checkout's existing candidate/base Git objects, Git and Python 3, not the product worktree or deleted validator scratch. It creates and removes a private temporary subdirectory under this evidence folder; no shared worktree/config writes.

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/budget-form-counts-ideation-rounds-and-times-each-round/evidence/validation-1/acceptance.sh
```

The unchanged final script was run in a fresh Bash shell. Step 1 exports and prints the pinned candidate; step 2 checks legacy parsing and six expected replay exits; step 3 checks three recorded timed results; step 4 checks 6097 words and ADR 0085; step 5 requires all nine POC-derivation tests to pass. **Observed: steps 1–4 pass, step 5 fails once, overall exit 1**, reproducing F1. Output: `logs/captain-acceptance.log`. The script does not stand for full corpus, real dispatch-suite, hosted checks, or released-live validation.

## Limits and unsuccessful attempts retained

The original unadapted dispatch run from `/tmp` fails at an existing scratch-path guard, before intended behavior: `logs/suite-dispatch_stage.log`, 84 failed subtest assertions and three errors across 56 tests. A narrow diagnosis reproduces that cause. An initial mapping wrapper ran zero tests (exit 5); a corrected wrapper completed with one path-assertion failure in an unchanged test. Those are invalid acceptance evidence and are retained only as failed environment/harness attempts. FO then explicitly authorized the authoritative unadapted worktree run, which passes all 56 tests with empty status before/after. The exported product bytes remain unchanged. The first Captain script used `--require` on an ADR file rather than the ADR directory and stopped at step 4; `logs/captain-acceptance-initial.log` preserves it. The corrected final script was rerun exactly and reaches F1 at step 5.

Implementation limits judged: four optional historical-corpus tests remain skipped; the current all-task/census checks do not substitute for those unrelated historical fixtures. Per-round results are closed gates/following boundaries, not worker success reports; the three zero-minute historical records remain genuine limits. Times include waiting and are not worker-only or speed measurements. Released-live third-dispatch behavior remains unproven. No UI surfaces require screenshot or rendering; no retained diagram changed. RoboRev is FO-owned and not rerun; hosted CI was read and is failing as stated. CI files unchanged; cost per PR not measured. No merge, release or adoption is claimed. Sibling workflow/lint changes still require an exact merged-candidate check; preserve this task's -2 word delta.
