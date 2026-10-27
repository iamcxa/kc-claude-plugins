# PR #737 independent revalidation, Cycle 1

Candidate: aa0f280f8e94f8b5549b4a8cd26fe30560a9842c
Comparison base: 8bf4f3582411e8e4238f19fbadda8ddeca6767be (merge-base with observed origin/main 4b78f020c2e4b5e8cdfa9e8a7e0133f63e9dd2d0).
Profile: pilot. Verdict: PASSED against AC-1 through AC-7 and AC-9 under Captain amendment 2.

## Previous finding resolved

Validation-1 F1 was a Needs decision finding: Amendment 1's accepted no-repeat wording conflicted with AC-8 and the original implementation. Amendment 2 explicitly authorizes skipping archived tasks rejected by variant/profile only, in the same three files, with no new record; other ineligibility reasons may still repeat. The old AC-8 text is preserved verbatim under Amendment 2 and is replaced by freshly numbered AC-9, as ADR 0005 and ADR 0016 require.

The repaired watcher checks variant/profile before interpreting or querying the archived PR. Its 35-case matrix derives expected eligibility from the actual learning.py function, covering missing/empty values, unsupported variants/profiles, case sensitivity, and all three accepted profiles. Unsupported fixtures point to an unavailable provider, so querying them would fail the assertion. Two repeated scans preserve task bytes and create neither watch-cache nor learning-store records.

A real legacy-profile claim returns ineligible/profile and notices --all remains empty. A subprocess of pr_watch.py prints no idle reminder before or after that hold; adding an eligible task prints its exact reminder. A verdict-only hold still repeats, matching the Captain's accepted limit. F1 is resolved; there are no new Material, Deferred risk, Polish or Needs decision findings.

## Five-step acceptance script

Run:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/idle-hook-names-merged-tasks-without-learn/validation-cycle1/acceptance.sh
```

The script contains five exact steps with expected output. It opens aa0f280f in a disposable checkout, runs six focused tests including the 35-case matrix, shows real recorder/watcher CLI behavior, runs ADR lint against the pinned base, then removes that checkout. It was run unchanged with bash --noprofile --norc; exit 0, six tests in 25.002 seconds; full stdout/stderr in acceptance.log.

Expected and observed highlights:

```text
Ran 6 tests in 25.002s
OK
idle before hold: <empty>
{"state": "ineligible", "reasons": ["profile"]}
{"notices": []}
idle after hold: <empty>
eligible task: next: run kc-dev-flow-2:learn for eligible.
PASS: rejected profile skipped; eligible task named; no record or task mutation
39 ADR file(s) checked, 0 legacy
adr_lint exit=0
cleanup complete
```

Prerequisites are declared in the script: the dispatched local repository and installed Codex 0.32.0 package, Git, Python 3 and Bash. No secret or network dependency. The fixture scheduler/provider interfaces are controlled; Git commits, filesystem state, recorder, and watcher subprocess are real. No graphical surface is changed. This script does not prove live GitHub, native FO decision-making, install/adoption, merge or delivery.

## Commands, outputs and counterexamples

- all-tests.json lists all exact commands and exit codes for 25 independently rerun package test files: 894 unittest cases, including 124 watcher cases, plus native dispatch/recovery checks; all final exits are 0. The recorded run_all.py runner accepts candidate and evidence directories as its two arguments and discovers the 25 files.
- One initial validation-runner invocation mistakenly passed --sd-plugin-root to test_observer_recovery.py, which accepts no such flag. Its argument-error output and all-tests-initial.json remain retained. The corrected command `PYTHONDONTWRITEBYTECODE=1 SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B kc-dev-flow-2/scripts/test_observer_recovery.py` passed with exit 0; test_observer_recovery-corrected.log holds the result. No candidate edit was required. run_all.py now passes that flag only to test_sd_dispatch.py.
- Native checks used Spacedock CLI 0.27.2 and plugin 0.27.3. Their own logs disclose that real skill discovery/worker behavior and remote merge are not proved.
- checks.json records repository lint plus installed-package ADR lint, number guards, comment ratio, document impact, design surfaces and dispatch-record checks: all exit 0. ADR lint checks 39 files; six dispatch records are complete; comment ratio is 1/515 = 0.2%, maximum 5%; workflow reading budget remains 5565/5565; no additional impacted document was listed; diff --check is clean.
- Copy mutate.py to .context/idle-evidence/cycle1/ in a fresh candidate checkout, then run `PYTHONDONTWRITEBYTECODE=1 python3 -B .context/idle-evidence/cycle1/mutate.py`. The validator ran it: all 16 mutated copies exited 1 with assertion failures, with no import/fixture errors. It changes only its disposable copy and restores originals between cases.
- previous-head-falsifier.log applies the prior 207c0a7e watcher bytes to a disposable copy while retaining the new tests: both eligibility-parity and legacy-profile tests fail by assertion, exit 1. The repaired candidate passes both.
- historical-replay.json verifies every frozen row's path, PR, variant and profile against committed state 1158adc584637bdbf1b2f347b91a4c63844d6c00: 88/88 exact. The reconstructed job projection yields 29 reminders including all 11 target tasks before restoration, then 18 reminders with none of the 11 targets after restoration; folder-form release-acceptance is included.
- Copy recount.py to .context/idle-evidence/ in a fresh candidate checkout, then run `PYTHONDONTWRITEBYTECODE=1 python3 -B .context/idle-evidence/recount.py`. The validator reran it with exit 0; recount.json and recount.log retain full emitted output. A second extraction/recount independently checks the same passages and actual stdout in independent-recount.json.
- Per-moment before/after words: startup 1344/1342; idle OPEN 1039/1037; idle MERGED 572/570; after archive 358/356; merge ask 680/680; empty recovery 552/550. Each missing reminder adds 5 words on every unresolved pass; uncertainty/malformed examples add 11; new learn/framework loading can add 2918 + 3067 = 5985 words plus evidence.
- Only pr_watch.py, test_pr_watch.py and extensions/learn/EXTENSION.md differ from the base. learning.py, skills/learn/SKILL.md, ADRs, root instructions and root learning.md remain unchanged. The extension keeps the existing observer pointer and names the new field restriction in the same 33-word bullet. The sole added comment documents frozen source provenance; no new repair comment was introduced.
- All implementation evidence limits remain accurate: duplicated eligibility logic is bounded by a parity test, not shared implementation; non-field eligibility holds can still repeat; historical notice keys are reconstructed rather than recovered original store bytes; provider calls are exercised through controlled fixtures, not fresh GitHub reads. No new record, version, ADR, schema, CI trigger or suppression marker.
- FO-supplied external evidence: clean RoboRev evidence=roborev:1271 and CI 4/4 pass on aa0f280f8 (2026-10-28). Neither was independently queried. CI cost per PR is not measured. No code push, PR mutation, review request or merge was performed.

## Falsifier coverage and necessity

| Criterion | Proof and failing mutation |
| --- | --- |
| AC-1 | Exact sorted guarded flat/folder/dedup output; archive exclusion, folder omission and removed extension guard fail. |
| AC-2 | One supported all-notices read and workflow-qualified keys; unread-only, wrong workflow, wrong repository and uncertain-input mutations fail. |
| AC-3 | Frozen 88-row replay includes/suppresses all 11 targets; archive exclusion fails. |
| AC-4 | State-only repository-bound reads and diagnostic exit 2 preserving live output; full-review-query and malformed-as-empty mutations fail. |
| AC-5 | Unchanged state/store bytes and no cache/store creation; real pending claim suppresses; injected archive-cache write fails. |
| AC-6 | Existing live/hook/observer behavior and all package tests pass; missing observer pointer fails. |
| AC-7 | Actual stdout plus independent passage recount; longer reminder fails. |
| AC-9 | 35-case real-eligibility parity, legacy-profile no-reminder and accepted verdict-only repetition; removing either field filter or changing learn eligibility to accept legacy fails. Prior-head watcher fails both new repair tests. |

Goal sufficiency: eligible archived merged tasks with missing jobs are recovered; the newly accepted field-only exclusions are silent and read-only. Minimal necessity: the two-line field filter is the complete runtime repair; parity/negative fixtures defend its duplicated rule, historical field data preserves meaningful replay, and the retained extension bullet explains the changed scan. No retained change or deletion falls outside the three-file approved scope.

Both detached validation and acceptance checkouts were removed after verification. Candidate code remains unchanged and the assigned source worktree is clean at aa0f280f. This evidence supersedes the previous head's validation result only; the validation gate, delivery decision and adoption remain with FO and the Captain.
