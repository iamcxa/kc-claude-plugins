Title: fix(kc-dev-flow-2): the merge check holds on CI and base, lists points for the Captain and records each ask

FO's merge-ask check now holds on CI, draft, conflict, wrong base and an incomplete file list, prints pointers for the Captain, and records every ask. FO still only asks: it never merges by itself.

## What changes

- `kc-dev-flow-2/scripts/delivery_gate.py` `check` gains the holds, `point:` lines (at most 12, escaped bounded tokens), a `class:` line (allowlist: never, docs-only, script-with-test, other; a never list of instruction, hook, release, gate and workflow paths), and the saved `merge/ask-<N>.json` (head, class, rule verdict, points, PR, UTC time). The `next:` line is always the ask line.
- `references/sd/workflow.md` falls 29 words (5447 to 5418) with a matching cut step in `lint-skills.py`; the merge-ask moment FO reads is 390 words against 415 (limit 404).
- No ADR lands. The grant, merge-line, recheck and calibrate code that earlier heads carried is removed; it stays reachable at 3fd84178, named in POC task `merge-grant-need-poc`, which measures first how many PRs a grant would cover and whether pre-authorised merge already gives the effect.

## Evidence (head b97068de)

- `test_delivery_gate.py`: 44 tests pass. They run the real script against a stub `gh` on `PATH` (pagination, argv and JSON parsing exercised) and assert `check` never calls `gh pr merge`.
- 45 mutations of `delivery_gate.py` (python3 -B, caches cleared), each against the whole suite: 44 RED, 1 survived. The survivor removes `status == "COMPLETED"` from the check-run clause; it is equivalent, because GitHub reports a null conclusion until a run completes, so the `conclusion == "SUCCESS"` clause still holds a pending run.
- All 23 package test files pass locally (`test_sd_dispatch.py` with a 0.27.0 plugin root and the 0.27.2 binary); `lint-skills.py` exit 0 (5418 of 5418); `comment_ratio.py` 0 comment lines added; `number_guards.py check` PASS.
- CI on b97068de: all four checks green (`unit tests (python3)` 1m37s; `test_delivery_gate.py` step 16 s).
- roborev: `findings on b97068de1; evidence=roborev:855`, one High: the documented command omits `--workflow-dir`, so the README cannot be found. Disproved for the split-root layout it names: `find_readme` falls back to the task's parent and grandparent, and a read-only run of `check` on the merge-gatekeeper task in this repository's state checkout reached the PR checks (it held on "the PR is a draft") with no "cannot find the workflow README" line.

## Residuals (known limits)

- Replay over the 32 archived dev2 tasks with a merged PR (`validation/replay-1.txt`, run on 3fd84178; the hold, point and class code is unchanged since): all class `never`, rule verdict merge on 0 of 32.
- `docs/dev2/README.md` and `docs/dev2-poc/README.md` copies of `workflow.md` update by the sync PR after release.

## without-it unanswered

- `point: second-reviewer` source (not in the design list).
- `point: more: N not shown` cap at 12.
- `--workflow-dir` option on `check`.
- The `verdict` field in each record (a rule verdict no consumer reads until the POC task).
- The `model: "not run"` field in each record (the model arm was dropped).

CI cost: `test_delivery_gate.py` took 16 s of the 1m37s `unit tests (python3)` job on b97068de.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
