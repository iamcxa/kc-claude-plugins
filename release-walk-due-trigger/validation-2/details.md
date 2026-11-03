# Independent validation, second run

Verdict: **PASSED under Captain amendments 1 and 2**. Consumer PR #775 is a3d9b00211929469c3b8cd8ccf63f95d2e261274; producer PR #774 is b026e0d7e497f7dc0ae0bae03fb1558810a36db3. No new Material, Deferred risk, Polish or Needs decision finding. This is scoped validation, not merge or deployment approval.

## Identity, authority and evidence boundary

- Assigned branch: spacedock-ensign/release-walk-due-trigger at a3d9b00211929469c3b8cd8ccf63f95d2e261274; detached probes below the assigned absolute worktree /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger.
- PR #772 remains OPEN at 606781cbec3f684af5e7f9a74c90026e49c3e0a1. Per amendment 2, AC-16 and number guards use that exact stack parent now; origin/main must be checked after #772 merges. Local and remotely read main remain e1bee223c47a1cd534a665a47776b683375b34fc.
- Producer branch head is unchanged, with own base 713d4e6ed6381e65fa6d8305e08b282ceb56a8fb. Amendment 1 authorizes its three registration files and requires producer-first merge.
- Loaded skills: spacedock:ensign and kc-dev-flow-2:validation, Pilot. Package scripts come from /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0 as the loaded skill resolves, per the dispatch-facts package rule. The dispatch also spells the same version under .claude; that other install was not substituted for the loaded one.
- Native CLI observed: /Users/kent/.local/bin/spacedock 0.27.2, contract 3, Codex runtime; the design's 0.27.3 was not the executed binary. Live parser, archive, selected-executable and persistence seams below all passed on the observed binary.
- All implementation dispatches and prior stage reports read, along with applicable ADRs and learning about config isolation, lifecycle reading and script-output consumers. No subagents, product repairs, repository config writes, pushes, PR comments, review requests, ready or merge actions.

## Prior finding dispositions

- F1 Material, fixed: status: done # completed now yields two reminders matching two producer-pending releases. Fresh-shell acceptance step 4 and full native quoted-field tests pass. Restoring raw Task fields fails the reported status case and all-four-fields quoting control (F1-F2-raw-fields.log).
- F2 Material, fixed: release-acceptance: book-pickup/r1 # already filed now suppresses r1 while retaining r2. Spacedock reads the same claim; raw-field mutation repeats r1 and fails. Archived folder, escaping, and a literal hash inside quotes were also exercised.
- F3 Needs decision, settled for this stage by amendment 2: stack-parent AC-16 and number guards pass. Literal origin/main still imports prerequisite EXTENSION.md and ADR 0053 and number_guards exits 1. This remains a required later integration check, not an implicit main PASS.
- F4 Needs decision, settled by amendment 2 as a record-format issue: the unchanged implementation-1-message-1.md still produces the known completion-scope diagnostic and dispatch_records exits 1. No new diagnostic or changed trigger was found; no record repaired or finding reopened.

## Criteria, both candidates and falsifiers

- AC-11 PASS: real producer emits two pending releases; due emits two lines, real split-root spacedock new/status --set/state commit preserves the claim, and the claimed line disappears. Removing the claim restores it. Missing producer prints the exact required diagnostic. Listed-only integration passes. real-seams.json, acceptance.log and release-tests.log.
- AC-12 PASS: live/archive, flat/folder, empty claims all exercised; native archive-folder case passes. Omitting --archived from the native listing makes that real case fail (AC-12-archive-omitted.log). The old manual-glob falsifier no longer targets this implementation because task discovery now belongs to Spacedock.
- AC-13 PASS: real producer and committed recorded output agree on done-but-live and no-done example workflows. No-done skips producer after the task query; all-done retains due releases. Requiring status archived instead of done fails (AC-13-archived-only.log). F1's valid-YAML case now passes independently.
- AC-14 PASS: identical unlisted output versus origin/main on the same shipped fixture; listed map emits one line with explicit argv, no-map skips due. Removing the extension gate fails (AC-14-unconditional.log). New mode output consumers searched: pr_watch tasks is human-facing through the workflow mod; no additional production parser found in the package.
- AC-15 PASS: producer exit 2, non-JSON, wrong major, non-null diagnostic, malformed rows, missing executable and timeout diagnose without due lines; exit 1 succeeds. Non-map silent; selected CLI alias/argv/PATH and cleanup checked. Producer timeout specifically injected after a successful task query (producer-timeout.log), since the full-suite generic timeout can now hit the earlier query. Rejecting exit 1, ignoring diagnostic, reverting map identity or dropping the alias each fails its test. Incomplete/malformed task-query results also diagnose.
- AC-16 PASS at authorized stack base: exactly seven consumer files; workflow and EXTENSION.md byte-identical, 5781 and 529 words. README joining cell names idle; no version, CI or producer file in consumer delta. Producer has exactly the three amendment-approved registration files. 601 extra extension words fail the cap test. Sanitize rules applied read-only to 33 public files: 0 BLOCK/REJECT, 2 unchanged WARN lines (conditional pass, not zero-warning clean).
- AC-17 PASS: commands, cwd, outputs, exit and monotonic durations recorded in timings.json; one observation per current unmapped and five-task mapped workflow, on this machine during this validation. The stronger due read adds one task query even when the producer is skipped. Removing command provenance is rejected (AC-17-no-command.log). No large-map, isolated benchmark, or CI-per-PR cost inferred; CI cost unmeasured, triggers unchanged.
- Amendment 1 PASS in producer scope: eight schemas tests; unversioned table edits and changed pending-label semantics both fail. Actual progress.mjs bytes match both candidates, and cross-PR real-seam commands explicitly use the producer checkout. AC-11–15 and 17 exercise the unchanged producer plus new consumer together; these behaviors were not separately added by #774. No producer workflow/version edits.
- Retention/minimal necessity: all 116 previous test names retained, six added; Task/state_tasks/cmd_accepted ASTs match the prerequisite. The absent due subcommand on #772 exits 2, while the candidate achieves the goal. The seven consumer files each implement, document or test the accepted reminder; producer's table/version/tests are required by amendment 1. Eleven behavioral mutations rejected; claim-removal and missing-provenance counterexamples also run. No new proof framework or product changes.

## Commands and observed exits

Consumer tests: python3 -B kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py (122, no skips, exit 0); python3 -B kc-dev-flow-2/scripts/test_pr_watch.py (133, exit 0). Producer: node --test kc-journey-map/lib/schemas.test.mjs (8, no skips, exit 0). Logs are retained beside this report.

- lint: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B kc-dev-flow-2/scripts/lint-skills.py` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 0; lint.log
- adr: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since 606781cbec3f684af5e7f9a74c90026e49c3e0a1 --require 0056` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 0; adr.log
- adr-literal-main: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since origin/main --require 0056` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 0; adr-literal-main.log
- numbers-stacked: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/number_guards.py check --repo /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger.md --base 606781cbec3f684af5e7f9a74c90026e49c3e0a1` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 0; numbers-stacked.log
- numbers-literal-main: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/number_guards.py check --repo /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger.md --base origin/main` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 1; numbers-literal-main.log
- comments: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/comment_ratio.py 606781cbec3f684af5e7f9a74c90026e49c3e0a1 HEAD --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 0; comments.log
- doc-impact: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/doc_impact.py 606781cbec3f684af5e7f9a74c90026e49c3e0a1 HEAD` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 0; doc-impact.log
- design-surfaces: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/design_surfaces.py check /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger.md` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 0; design-surfaces.log
- dispatch: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/dispatch_records.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 1; dispatch.log
- diff-check: `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer diff --check 606781cbec3f684af5e7f9a74c90026e49c3e0a1 HEAD` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 0; diff-check.log
- scope-stacked: `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer diff --name-only 606781cbec3f684af5e7f9a74c90026e49c3e0a1 HEAD` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 0; scope-stacked.log
- scope-main: `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer diff --name-only origin/main...HEAD` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-consumer` → exit 0; scope-main.log
- producer-adr: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since origin/main` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-producer` → exit 0; producer-adr.log
- producer-comments: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/comment_ratio.py origin/main HEAD --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-producer` → exit 0; producer-comments.log
- producer-doc-impact: `/Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/doc_impact.py origin/main HEAD` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-producer` → exit 0; producer-doc-impact.log
- producer-diff-check: `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-producer diff --check origin/main...HEAD` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-producer` → exit 0; producer-diff-check.log
- producer-scope: `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-producer diff --name-only origin/main...HEAD` in `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-2-producer` → exit 0; producer-scope.log

## Documents, cost and limits

- doc_impact names ADR 0053 and 0056. ADR 0053 unaffected: its environment and accepted-walk logic remains the prerequisite's identical AST; its imported changes are outside this task. ADR 0056 updated as the new ruling, unchanged by the parser repair; its producer/claim semantics match behavior. Producer doc_impact lists none. No changed product diagram; no rendered-diagram claim.
- All added comments read: the single ADR pointer explains the rule source; comment_ratio 1/491 = 0.2%, maximum 5%, exit 0. Producer 0/73, exit 0. No new narrative or provenance comments.
- Startup, filing, gates, merge ask and archive reading unchanged against #772. Due line 25 words; missing-producer line 6; unlisted idle unchanged. Word counts and byte comparisons are in word-counts.json. The README row is the changed discovery entry.
- Sanitize conditional pass: README.md line 37 and skills/evaluate-learning/SKILL.md line 78 are existing heuristic WARN lines; both strings occur verbatim in the base, although line positions can differ. No config edit, publication approval or contextual-privacy guarantee claimed.
- Hosted evidence refreshed: exact #774 and #775 heads, five SUCCESS checks each, both OPEN/Draft. #772 OPEN. Existing RoboRev attempts recorded daemon unavailability; no current review verdict exists in this proof, and validation neither reran it nor inferred approval. FO retains review disposition and delivery authority.
- Design limits retained: highest cached sibling need not be the enabled version; checkout discovery is not a trunk guarantee; maps outside docs/journey are not discovered; claims persist through archive/decline; no re-walk trigger, cache, map acceptance field, production rollout, human release walk or large-workflow performance proof. This Surfaces:none change has a CLI surface, with actual output captured; no application screen or screenshot claimed.
- Evidence-tool corrections: the reused persistence harness initially selected its own fake CLI; it was corrected to select from the live-producer PATH before the successful replay. The sanitize replay used the declared Node YAML dependency because Python PyYAML was absent. A baseline feature probe required an explicit package scripts PYTHONPATH. These were evidence harness setup failures, not product verdicts. Only successful final runs support the claims above.

Timing observations (seconds, one sample each; exact commands/output in timings.json):
- Unmapped current workflow: producer: 7.5095 s, exit 1.
- Unmapped current workflow: due: 3.004 s, exit 0.
- Mapped five-task scratch: producer: 0.2777 s, exit 0.
- Mapped five-task scratch: due: 0.5217 s, exit 0.

## Captain acceptance: four exact steps

Prerequisites: the named repository with both commit objects; git, Python 3, Node, npm and Spacedock on PATH; npm registry access if lockfile dependencies are not cached. No credential or configuration write is needed. This is CLI acceptance, not an application screen. Step 1 exports only the exact revisions into an owned temporary directory and removes it on exit. Run the following unchanged in a fresh Bash shell; acceptance.sh contains exactly this text.

Expected: eight producer contract tests, 18 due tests and three idle integration tests pass with no skips, followed by PASS status comment and PASS claim comment; exit 0. Does not replace full suites, mutations, future main-base checks, local review, provider CI, large-map performance or delivery authority.

```bash
#!/bin/bash
set -euo pipefail
# 1. Export both exact candidates into disposable directories; require git, Python 3, Node, npm and spacedock on PATH.
repo='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger'
scratch=$(mktemp -d "$repo/.acceptance.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT
mkdir "$scratch/consumer" "$scratch/producer"
git -C "$repo" archive a3d9b00211929469c3b8cd8ccf63f95d2e261274 | tar -x -C "$scratch/consumer"
git -C "$repo" archive b026e0d7e497f7dc0ae0bae03fb1558810a36db3 | tar -x -C "$scratch/producer"
export VALIDATION_CONSUMER="$scratch/consumer" VALIDATION_PRODUCER="$scratch/producer"
printf 'Exact consumer a3d9b00211929469c3b8cd8ccf63f95d2e261274; producer b026e0d7e497f7dc0ae0bae03fb1558810a36db3 exported\n'
# 2. Install the declared producer dependencies and check its contract; expect 8 passing tests.
(cd "$scratch/producer/kc-journey-map" && npm ci --ignore-scripts --no-audit --no-fund > "$scratch/npm.log" 2>&1)
ln -s "$scratch/producer/kc-journey-map/node_modules" "$scratch/consumer/kc-journey-map/node_modules"
(cd "$scratch/producer" && node --test kc-journey-map/lib/schemas.test.mjs)
# 3. Check the existing due and idle integration cases; expect 18 and 3 passing tests, no skips.
(cd "$scratch/consumer" && python3 -B kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py DueTests)
(cd "$scratch/consumer" && python3 -B kc-dev-flow-2/scripts/test_pr_watch.py TasksTests.test_release_walk_due_is_gated_by_listing_and_map_presence TasksTests.test_release_walk_due_errors_are_reported TasksTests.test_progress_locator_prefers_direct_then_highest_cached_version)
# 4. Check valid YAML comments; the candidate prints PASS twice. Expect PASS twice and exit 0.
python3 -B - <<'PY'
import importlib.util,json,os,subprocess,sys
from pathlib import Path
c=Path(os.environ["VALIDATION_CONSUMER"]); p=Path(os.environ["VALIDATION_PRODUCER"])/"kc-journey-map/lib/journey-progress.mjs"
s=importlib.util.spec_from_file_location("checks",c/"kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py");m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
failures=0
for kind in ("status","claim"):
 t=m.DueTests();t.setUp()
 try:
  node,_,env=t.live_producer()
  if kind=="status":
   for path in t.state.glob("*.md"):path.write_text(path.read_text().replace("status: done\n","status: done # completed\n"))
  else:
   claim=t.state/"accept.md";claim.write_text("---\ntitle: existing walk\nrelease-acceptance: book-pickup/r1 # already filed\n---\n")
   read=subprocess.run(["spacedock","status","--workflow-dir",str(t.wf),"--read",str(claim),"--json"],env=env,capture_output=True,text=True,check=True)
   assert json.loads(read.stdout)["frontmatter"]["release-acceptance"]=="book-pickup/r1"
  observed=subprocess.run([node,str(p),str(t.map),"--workflow-dir",str(t.wf)],env=env,capture_output=True,text=True)
  document=json.loads(observed.stdout);assert document["diagnostic"] is None
  pending=sum(row["acceptance"]=="pending delivery acceptance" for row in document["releases"]);assert pending==2
  due=subprocess.run([sys.executable,"-B",str(c/"kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py"),"due","--workflow-dir",str(t.wf),"--progress",str(p),str(t.map)],env=env,capture_output=True,text=True,check=True)
  actual=due.stdout.count("next:");expected=2 if kind=="status" else 1
  ok=actual==expected;failures+=not ok
  print(f"{'PASS' if ok else 'FAIL'} {kind} comment: producer pending={pending}, due reminders={actual}, expected={expected}")
 finally:t.doCleanups()
sys.exit(1 if failures else 0)
PY

```

Observed command: /bin/bash --noprofile --norc acceptance.sh; exit 0.

```text
Exact consumer a3d9b00211929469c3b8cd8ccf63f95d2e261274; producer b026e0d7e497f7dc0ae0bae03fb1558810a36db3 exported
✔ the table and version print and the recorded hash binds them (47.604792ms)
✔ an edited table with an unchanged version exits 1 naming the schema (48.423875ms)
✔ a bumped version with no recorded hash exits 1 (53.32425ms)
✔ the printed history pointers name files that exist and a runnable command (151.014417ms)
✔ release-walk prints its table and version, and an edited table with an unchanged version exits 1 (106.79175ms)
✔ journey-progress registers its printed table and refuses an unversioned shape edit (113.27275ms)
✔ the progress producer preserves the registered keys and acceptance meanings (734.3135ms)
✔ the README and SKILL.md send a reader to the schema command, the CHANGELOG and the ADR, and say when (0.886458ms)
ℹ tests 8
ℹ suites 0
ℹ pass 8
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 1326.447
..................
----------------------------------------------------------------------
Ran 18 tests in 8.289s

OK
...
----------------------------------------------------------------------
Ran 3 tests in 1.114s

OK
PASS status comment: producer pending=2, due reminders=2, expected=2
PASS claim comment: producer pending=2, due reminders=1, expected=1
```

## Cleanup and handoff

The two detached candidate worktrees and owned support directory are removed after evidence capture; no source repair or candidate commit. Assigned branch remains at the consumer head. Stage report and evidence are committed through the requested entity-scoped Spacedock state command; no product push. Remaining delivery work: producer first, #772 integration then main-based AC-16/number checks on the actual landing head, FO local review disposition and gate decision. The task remains validation, and its open PRs are not closed by this report.
