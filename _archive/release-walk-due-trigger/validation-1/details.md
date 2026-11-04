# Independent validation of the release-walk reminder

Verdict: **REJECTED** for the combined task. Consumer PR #775 at 442cfef4f4b9dca4046a128586b423cb95e521fd fails two supported task-frontmatter cases. Producer PR #774 at b026e0d7e497f7dc0ae0bae03fb1558810a36db3 passes its registration scope. These are validation recommendations, not gate or merge authority.

## Artifact and authority

- Assigned code worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger; unchanged branch spacedock-ensign/release-walk-due-trigger.
- Detached candidates: .validation-775 and .validation-774 below that root, removed after capture.
- Local and remotely read main: e1bee223c47a1cd534a665a47776b683375b34fc; triple-dot merge base 713d4e6ed6381e65fa6d8305e08b282ceb56a8fb.
- Authorized stack parent / PR #772: 606781cbec3f684af5e7f9a74c90026e49c3e0a1, independently read OPEN. No implicit substitution for origin/main.
- Amendment 1 authorizes three producer files and two PRs; #774 merges first. No version bump or CI trigger change.
- Loaded validation skill package: /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0; the dispatch's explicit .claude ADR-lint path also passed.
- Prior reports and all implementation dispatch messages read. No subagent, product repair, product push, PR comment, requested review, ready or merge action.

## Findings

### F1: Material: valid status comments hide pending release walks

F1. A user maintaining valid YAML task frontmatter can write status: done # completed. Spacedock and the real producer read done and report two pending releases; the new prefilter emits no line. value-ac[AC-13]: the scan never hides a due release; also AC-11. Trigger: yaml-status.json and acceptance.log.

Location: kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py:212. Route: Route through implementation feedback; make the scan preserve Spacedock's YAML field semantics and retain this real-producer regression.

### F2: Material: valid claim comments repeat an already claimed walk

F2. An acceptance task with release-acceptance: book-pickup/r1 # already filed is read by Spacedock as book-pickup/r1, but due prints its reminder again. value-ac[AC-11]: a live or archived claiming task must silence its release. Trigger: yaml-claim.json and acceptance.log.

Location: kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py:215. Route: Use the same field semantics for claims; do not treat the YAML comment as part of the claim.

### F3: Needs decision: literal main comparison conflicts with stacked validation

F3. AC-16 names origin/main, currently e1bee223c47a. That diff includes the prerequisite's EXTENSION.md and ADR 0053, and number_guards exits 1 for unreserved 0053. The explicitly authorized #772 stack at 606781cbe has no extension change and its number check passes. The validator cannot silently replace the literal criterion.

Location: kc-dev-flow-2/extensions/release-acceptance/EXTENSION.md:1. Route: FO must disposition the prerequisite/base boundary; rerun on the final integrated candidate or obtain the required scope ruling.

### F4: Needs decision: an earlier dispatch record fails the required checker

F4. dispatch_records.py exits 1: needs a scope-notes line naming main as the completion recipient. The record says final-reply completion but omits the recognized Done line; later implementation records have it. No product symptom is established.

Location: release-walk-due-trigger/dispatch/implementation-1-message-1.md:13. Route: FO owns the dispatch-record correction/disposition; preserve the Paseo final-reply completion route.

## Commands rerun

Consumer cwd: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-775; producer cwd: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-774. Python bytecode disabled. Real CLI: /Users/kent/.local/bin/spacedock; fixture git identities supplied through environment only, with no repository config writes.

- python3 -B kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py → exit 0; [release-tests.log](release-tests.log).

- python3 -B kc-dev-flow-2/scripts/test_pr_watch.py → exit 0; [watch-tests.log](watch-tests.log).

- node --test kc-journey-map/lib/schemas.test.mjs → exit 0; [contract-tests.log](contract-tests.log).

- python3 -B kc-dev-flow-2/scripts/lint-skills.py → exit 0; [lint.log](lint.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since origin/main --require 0056 → exit 0; [adr.log](adr.log).

- python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since origin/main --require 0056 → exit 0; [adr-dispatch-path.log](adr-dispatch-path.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/number_guards.py check --repo /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-775 --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger.md --base origin/main → exit 1; [numbers.log](numbers.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/comment_ratio.py origin/main HEAD --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 → exit 0; [comments.log](comments.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/doc_impact.py origin/main HEAD → exit 0; [doc-impact.log](doc-impact.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/number_guards.py check --repo /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-775 --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger.md --base 606781cbec3f684af5e7f9a74c90026e49c3e0a1 → exit 0; [numbers-stacked.log](numbers-stacked.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/comment_ratio.py 606781cbec3f684af5e7f9a74c90026e49c3e0a1 HEAD --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 → exit 0; [comments-stacked.log](comments-stacked.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/doc_impact.py 606781cbec3f684af5e7f9a74c90026e49c3e0a1 HEAD → exit 0; [doc-impact-stacked.log](doc-impact-stacked.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/design_surfaces.py check /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger.md → exit 0; [design-surfaces.log](design-surfaces.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/dispatch_records.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger → exit 1; [dispatch.log](dispatch.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since origin/main → exit 0; [producer-adr.log](producer-adr.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/comment_ratio.py origin/main HEAD --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 → exit 0; [producer-comments.log](producer-comments.log).

- python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/doc_impact.py origin/main HEAD → exit 0; [producer-doc-impact.log](producer-doc-impact.log).

- git diff --check passed on both candidates. Producer changes exactly lib/contract-versions.json, lib/schemas.mjs, lib/schemas.test.mjs. Consumer own range changes seven design-named files. scope-origin-main.txt, scope-stacked.txt and word-counts.json preserve the wider boundary.

## Criterion and falsifier evidence

- AC-11: actual real-producer release lines; real spacedock new, status --set, state commit, status --archived --all-fields --json and git show HEAD:r1-acceptance.md preserve a claim; removing it restores the line. Commands/output: real-seams.json. An initial disposable fixture used an invalid state branch and was discarded; completed proof uses spacedock-state/workflow. F2 is an additional valid-YAML counterexample.

- AC-12: live/archive flat/folder and empty claims exercised. AC-12-flat-only.log catches removing the folder glob.

- AC-13: shipped done/live and unbuilt cases run through real producer/CLI without skips; AC-13-archived-only.log catches the narrowed scanner. F1 demonstrates the additional task-value failure missed by those controls.

- AC-14: actual old/new unlisted output equality from the shipped fixture in unlisted-base-comparison.json. Listed/no-map argv checks pass; AC-14-unconditional.log catches removal of the gate.

- AC-15: exit 2, malformed JSON, wrong major, diagnostic, timeout, missing producer, non-map and selected-CLI cases run; AC-15-exit-one.log, AC-15-ignore-diagnostic.log, yaml-literal-id.log and spacedock-alias-removed.log each reject its injected error. Timeout is injected, not a 60-second wall-clock hang. Real map-scalar/renamed-CLI regressions also pass.

- AC-16: literal main boundary fails F3; own stack passes. AC-16-word-cap.log rejects 601 extra words. Read-only sanitize-check skill rules cover its 33 public files using the configured rules file: conditional pass, zero BLOCK/REJECT, two unchanged WARNs (README:37, evaluate-learning skill:78). No policy or public file edited.

- AC-17: timings.json carries exact argv/stdout/stderr/exit/monotonic time for current unmapped and mapped five-task workflows, one observation each. AC-17-no-command.log rejects missing argv provenance. CI cost per PR remains unmeasured; no CI workflow changed.

- Amendment 1: 8 schema tests pass; producer-table-unversioned.log and producer-pending-label.log reject changing the table or actual pending label. Consumer and producer progress.mjs bytes are identical; real seam probes use the producer PR checkout. Merge order is a pending delivery obligation.

- Merge retention: retained-tests.json compares ASTs: 113 consumer + 104 prerequisite methods, 116 distinct methods, every body unchanged.

## Document and implementation-limit disposition

- ADR 0056 is the updated task ruling. ADR 0053 is unchanged relative to #772 and belongs to that prerequisite; origin/main includes its environment/production changes, so the narrow implementation 'unaffected' disposition applies only to its own range. All added comments read: one task ruling pointer, two imported invariant explanations, no process narration.

- Hosted publication/checks independently read in pr-774.json and pr-775.json: exact assigned heads, five SUCCESS checks each, draft/open. PR #772 is open at 606781cbe. Hosted success does not establish release/adoption or negate these defects.

- Recorded local RoboRev attempts lack a verdict (daemon not running); no current review inferred or requested, FO retains it. External-round-1 map-YAML and renamed-CLI repairs survive reverse mutations, but do not cover task-frontmatter YAML.

- Accepted limits retained: highest cached producer need not be enabled; discovery reads checkout rather than guaranteed trunk; no maps outside docs/journey, re-walk trigger, cache, map acceptance field, production rollout or large-map performance claimed. Small mapped/current unmapped timings are observations only.

- No application screen exists for this Surfaces:none task; actual CLI output is the changed surface. No screenshot or human release walk claimed.

## Captain acceptance: four exact steps

Prerequisites: named repository and git objects, git, Python 3, Node, npm and Spacedock on PATH. Step 2 installs lockfile dependencies only in the disposable export. Run unchanged in a fresh Bash shell; acceptance.sh is the identical text. Expected on this rejected head: exit 1 after 8, 12 and 3 passing control tests, then two FAIL lines. A repaired candidate must print PASS twice. This does not cover the full suite, all mutations, main-base guards, hosted review/CI, large-map costs or delivery.

```bash
#!/bin/bash
set -euo pipefail
# 1. Export both exact candidates into disposable directories; require git, Python 3, Node, npm and spacedock on PATH.
repo='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger'
scratch=$(mktemp -d "$repo/.acceptance.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT
mkdir "$scratch/consumer" "$scratch/producer"
git -C "$repo" archive 442cfef4f4b9dca4046a128586b423cb95e521fd | tar -x -C "$scratch/consumer"
git -C "$repo" archive b026e0d7e497f7dc0ae0bae03fb1558810a36db3 | tar -x -C "$scratch/producer"
export VALIDATION_CONSUMER="$scratch/consumer" VALIDATION_PRODUCER="$scratch/producer"
printf 'Exact consumer 442cfef4f4b9dca4046a128586b423cb95e521fd; producer b026e0d7e497f7dc0ae0bae03fb1558810a36db3 exported\n'
# 2. Install the declared producer dependencies and check its contract; expect 8 passing tests.
(cd "$scratch/producer/kc-journey-map" && npm ci --ignore-scripts > "$scratch/npm.log" 2>&1)
ln -s "$scratch/producer/kc-journey-map/node_modules" "$scratch/consumer/kc-journey-map/node_modules"
(cd "$scratch/producer" && node --test kc-journey-map/lib/schemas.test.mjs)
# 3. Check the existing due and idle integration cases; expect 12 and 3 passing tests, no skips.
(cd "$scratch/consumer" && python3 -B kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py DueTests)
(cd "$scratch/consumer" && python3 -B kc-dev-flow-2/scripts/test_pr_watch.py TasksTests.test_release_walk_due_is_gated_by_listing_and_map_presence TasksTests.test_release_walk_due_errors_are_reported TasksTests.test_progress_locator_prefers_direct_then_highest_cached_version)
# 4. Check valid YAML comments; a correct candidate prints PASS twice. This rejected head prints FAIL twice and exits 1.
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

Observed from /bin/bash --noprofile --norc acceptance.sh (exit 1):

```text
Exact consumer 442cfef4f4b9dca4046a128586b423cb95e521fd; producer b026e0d7e497f7dc0ae0bae03fb1558810a36db3 exported
✔ the table and version print and the recorded hash binds them (43.929084ms)
✔ an edited table with an unchanged version exits 1 naming the schema (47.387ms)
✔ a bumped version with no recorded hash exits 1 (44.472292ms)
✔ the printed history pointers name files that exist and a runnable command (128.681ms)
✔ release-walk prints its table and version, and an edited table with an unchanged version exits 1 (90.507666ms)
✔ journey-progress registers its printed table and refuses an unversioned shape edit (93.489875ms)
✔ the progress producer preserves the registered keys and acceptance meanings (688.969542ms)
✔ the README and SKILL.md send a reader to the schema command, the CHANGELOG and the ADR, and say when (0.621417ms)
ℹ tests 8
ℹ suites 0
ℹ pass 8
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 1195.600084
............
----------------------------------------------------------------------
Ran 12 tests in 5.767s

OK
...
----------------------------------------------------------------------
Ran 3 tests in 1.154s

OK
FAIL status comment: producer pending=2, due reminders=0, expected=2
FAIL claim comment: producer pending=2, due reminders=2, expected=1
```
