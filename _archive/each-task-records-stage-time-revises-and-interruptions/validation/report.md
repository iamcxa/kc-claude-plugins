# Independent validation of task stage timing

Verdict: **REJECTED**. PR #852 candidate `a3266ec91c7d46d36864c471c0cc26b389130b3c`; base `8ce0eb6050c889b21baccf50fec35231bc888d66`. The clean candidate was run from a Git archive export and remains unchanged. `identity.json`, `candidate-files.json` and `archive-state-stability.json` bind the code and public corpus. Start: 2026-11-12 17:42:50 Asia/Taipei.

## Material finding

**F1 — Material; kind: build.** At `kc-dev-flow-2/scripts/task_timeline.py:130`, elapsed time covers every dispatch segment but after-gate time starts only at the latest gate close. Earlier decision-to-next-dispatch time becomes before-gate time. Compute the split per active segment before accumulating it; keep the approved counter definitions.

- Released user and normal workflow: a First Officer reads an archived task with a revised gate and second dispatch using the documented timeline command.
- Observable harm: public task `denied-command-denies-only-that-command` has 23.2 minutes between its first revise decision and second validation dispatch. Only the final 7.1 minutes appear after-gate, instead of the per-segment total 30.3. `real-cycle-split.json` preserves author-date commit IDs, raw gate timestamps and arithmetic; the CLI output is in `denied-command-denies-only-that-command-timeline.json`.
- Affected value: `value-ac[AC-1]` accurate stage timing, under the accepted Design PRFAQ's dispatch-to-room, room-to-decision and decision-to-next-dispatch definitions. The misattribution corrupts the accepted workflow-improvement measurement.
- Trigger evidence: independent `probe_repeated_stage.py` reuses the candidate's disposable Git fixture for two ordinary validation cycles, with revise, repair and approval. Expected before/wait/after is 20/20/40 minutes; actual is 50/20/10. `probe-repeated-stage.log` and fresh-shell `acceptance.log` show exit 1. No repair was made.

## Acceptance evidence

- AC-1: original finished-task evidence reran (`ac1-finished.log`, `ac1-human.log`, `ac1-hand-log.log`). Independent raw Git comparison on three archives matches nine worker-stage start/end/duration rows (`archived-comparison.json`); archive-removal and committer-date mutations fail (`mutation-ac1-*.log`). F1 means the approved timing split is not accepted in full.
- AC-2: 62 comparable archives match the budget counter; two no-record cases are separate (`ac2-compare-spent.log`). Counting files instead of highest record number fails (`mutation-ac2-count-files.log`).
- AC-3: UTC persistence, stage attribution and empty-input refusal pass (`ac3-ask-smoke.log`, `tests.log`). Ignoring asks and deleting stage attribution fail (`mutation-ac3-ignore-asks.log`, `mutation-ask-wrong-stage.log`). No asks file still means unknown.
- AC-4: 159 archives read, 136 have a timed stage, and all other 23 independently lack both a started stamp and dispatch folder (`ac4-sweep.log`, `ac4-untimed.json`). Unreadable history, unreadable frontmatter and ignoring folder-form tasks are caught (`mutation-ac4-unreadable-history.log`, `tests.log`, `mutation-sweep-ignore-folders.log`). This is readable coverage, not physical elapsed-time proof.
- AC-5: running stage has no end and positive minutes to now (`ac5-running.log`, `tests.log`); zeroing running duration fails (`mutation-ac5-zero-running-time.log`).

The four suites total 144 passes: 11 helper, 47 lint, 23 ledger, 63 role. All nine candidate-source mutants fail (`suite-totals.json`, `summary.json`, `commands.json`). Existing tests miss F1. The original POC falsifier command was also rerun: its archive mutation is stale and its running-stage grep selects now-finished ideation (`legacy-falsifiers.log`). Its exit 0 does not prove those cases; the current candidate-source mutations above do. Trace is compressed as `legacy-falsifiers-trace.log.gz`.

A supplemental scan found four negative-duration rows: three before-gate and one Captain-wait (`negative-durations.json`). Their history includes delayed recording and gates overlapping dispatch segments. These limit interpreting historical commits as physical timing; the independent F1 rejection does not depend on these irregular rows. No private repository was read or copied.

## Scope, rulings and checks

Design Expansion item 1 and Batch overlap explicitly list `.github/workflows/kc-dev-flow-2-tests.yml`. The six changed paths are the five design paths plus amendment 1's ADR 0080 (`candidate-files.json`). The reader reuses the ledger and counter; tests and CI cover its behavior, the workflow sentence records asks, its budget step is required by the existing equality check, and the ADR is authorized. No version change or unrelated product addition.

ADR 0080's approval quote and timing portion of the bound question match the ideation record and briefing. It records only the accepted revise definition, outside-gate ask recording, reporting without refusal and +25 workflow words. No new decision was added. Startup count is 6008 to 6033; idle, archive and merge-ask passages are unchanged (`reading.json`, `lint-skills.log`). Added comments were read; non-ADR notes explain dispatch/room timing semantics.

ADR lint with `--since 8ce0eb6050c889b21baccf50fec35231bc888d66 --require 0080`, number guards, comment ratio, document impact, dispatch records and whitespace checks all exit 0 (`required-checks.json`, corresponding logs). Comment ratio is 7/405 = 1.7%, within 5% (`comment-ratio.log`). Design surfaces and role triggers exit 0 (`design-surfaces.log`, `role-check.log`). All eight affected documents have explicit, independently reviewed dispositions (`doc-impact.json`, `doc-dispositions.json`).

## Not provable now: current judgments

`limits.json` judges every design item. The three post-release hand-timing comparisons, real Codex First Officer records, and complete ask-before-question behavior remain **still not provable** here. Historic comparisons and fixtures do not meet the Stop condition. The implementation's corresponding limits stand. The CI/lint item is **proven now**: hosted run 43193806094 completed successfully on the exact head (`ci-run.json`) and local lint passes.

The new CI step took 1 second in one hosted PR run, at GitHub's one-second timestamp resolution; local single-run duration was approximately 3.47 seconds (`ci-cost.json`). Monetary cost per PR was not measured. Repeat workflow runs can add cost, so this is added per-run time, not a guaranteed per-PR total. Existing package/workflow path filters remain unchanged; no new trigger or job. These observations supersede only the implementation's prior CI-not-run/unmeasured limits. PR #852 is open and Draft (`pr.json`), not merged or released.

## Captain acceptance

Run `bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/each-task-records-stage-time-revises-and-interruptions/validation/acceptance.sh`.

Four steps: export pinned candidate; run its 11 helper tests; compare three public archives with raw author dates; check two-cycle split. Run exactly as written in fresh bash: first checks pass, final split fails 50/20/10 versus 20/20/40, exit 1 (`acceptance-result.json`, `acceptance.log`). Its trap removes its scratch. This substitutes observable CLI output for UI: no UI changed. It does not establish release, adoption, host parity or complete ask recording.

FO owns the separate finding disposition and any repair dispatch, gate and delivery. No product push, PR comment, review request, merge or task-frontmatter change was made. Cleanup roots are in `cleanup-plan.json`; the post-commit receipt will be `cleanup.json`.

