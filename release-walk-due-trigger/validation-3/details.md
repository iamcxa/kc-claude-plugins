# Independent validation, third run

Verdict: **PASSED for both candidate products under Captain amendments 1 and 2, with one new FO-owned Needs decision finding about this dispatch record.** Every accepted criterion passes against the post-merge main base. This is not delivery approval or a clean dispatch-record verdict.

## Identity and authority

Candidate: bbf65bb3a621ad1c664698e0d50af8b4f4e0f1ec — consumer PR #775; seven approved changed files.
Candidate: b026e0d7e497f7dc0ae0bae03fb1558810a36db3 — producer PR #774; unchanged registration head, three approved changed files.
Base: origin/main at 2bda2e98304261d46b0ae7205a29ddc9038d2b4d, fetched this run. It is an ancestor of the consumer; producer merge-base remains 713d4e6ed6381e65fa6d8305e08b282ceb56a8fb.
PR #772 is MERGED at 2c76cb53ecbe1c6843d189137ebfd6bf734310b1 (2026-11-04T00:42:17Z). Amendment 2's post-merge main check now passes. Amendment 1 still requires #774 before #775.

Both detached validation worktrees were created below the assigned absolute worktree and pinned to these heads. No product repair, branch change, config write, frontmatter edit, prior-report edit, subagent, product push, PR comment, review request, ready or merge action.

Loaded spacedock:ensign and kc-dev-flow-2:validation, Pilot. Scripts use the loaded Codex package /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0. The explicitly requested .claude-path ADR command also exited 0. Native CLI observed: /Users/kent/.local/bin/spacedock 0.27.2, contract 3; the design's 0.27.3 is not the tested binary.

## Criteria and falsifiers, both heads

- AC-11 PASS: real producer emits two pending releases; due emits two reminders. Real split-root spacedock new/status --set/state commit persists a claim, which suppresses its line. Removing it restores the line. Missing producer yields the exact required diagnostic; listed-only integration passes. Evidence: real-seams.json, release-tests.log, acceptance.log.
- AC-12 PASS: live/archive flat/folder and empty claims pass; quoted archived-folder claim uses real Spacedock. Omitting --archived fails the native case (AC-12-archive-omitted.log). Native discovery replaces the earlier manual-glob mechanism.
- AC-13 PASS: done-live and no-done cases agree with real producer output; the normalized fixture equals live output. No-done skips the producer. Requiring archived instead of done fails (AC-13-archived-only.log). Both prior YAML defects pass; reverting parsed fields fails three tests (F1-F2-raw-fields.log).
- AC-14 PASS: unlisted fixture output is byte-identical to current origin/main; listed map yields one line with explicit argv; no map skips due. Removing the listing gate fails (AC-14-unconditional.log).
- AC-15 PASS: exit 2, non-JSON, wrong schema, diagnostic, malformed rows, missing executable and timeout diagnose without reminders; exit 1 succeeds. Nonmaps are silent. Selected CLI argv/PATH, renamed executable and alias cleanup pass. Independently injected producer timeout after a successful task query passes (producer-timeout.log). Exit-1 rejection, ignored diagnostic, raw map identity and omitted alias mutations fail. Incomplete native listings diagnose.
- AC-16 PASS against origin/main: exactly seven consumer files; workflow/EXTENSION.md are byte-identical, 5836/529 words. README joining cell names idle; no consumer version, CI or producer edit. Producer changes only three registration files authorized by amendment 1. Over-budget extension mutation fails. Sanitize is CONDITIONAL PASS: 0 BLOCK/REJECT, 2 unchanged heuristic WARNs, not zero-warning clean.
- AC-17 PASS: exact argv, cwd, outputs, exit and monotonic timing recorded for one unmapped workflow and one mapped five-task workflow. Removing command provenance is rejected. Timings are single observations, not scale proof. CI cost per PR unmeasured; triggers unchanged.

Producer amendment 1: all eight schema tests pass; changing the pending label or editing the table without a version update fails. Cross-PR native integration explicitly calls #774's producer; progress implementation bytes match the consumer. AC-11–15 and 17 concern their combined behavior, not a separately added due feature in #774.

Full relevant suites: 122 release-acceptance, 134 idle integration and eight producer tests pass, no skips. Eleven independent mutations rejected. All 104 main-base release test bodies retained unchanged; Task/state_tasks/cmd_accepted ASTs unchanged. Base lacks due and exits 2, while candidate achieves the goal. Seven consumer files implement/document/test the accepted reminder; three producer files satisfy amendment 1. No retained change lacks a scoped purpose.

## Finding disposition

Prior F1/F2 Material defects are fixed, with native YAML replay and reverse mutations. F3's base ambiguity is settled by amendment 2, and current-main checks now pass. F4's unchanged implementation-1-message-1.md completion-format diagnostic remains accepted by amendment 2 and is not reopened.

- F5 Needs decision, new: validation-3.md lacks Symptom:. Released user/workflow: First Officer preparing this validation gate. Observable effect: required dispatch_records.py exits 1 and names this new record as well as accepted F4; no product loss established. Boundary: contract[kc-dev-flow-2/skills/validation/principles.md#validation-principles] requires checking incomplete dispatch records and returning findings to FO. Trigger: dispatch.log and release-walk-due-trigger/dispatch/validation-3.md:1. FO owns disposition before the gate; validator did not edit the record. This is not Material and not covered by the older F4 ruling.

No new Material, Deferred risk or Polish product finding. Product verdict PASSED; F5's workflow disposition stays open.

## Documents, costs and limits

doc_impact.py names ADR 0053 and 0056. ADR 0053 unaffected: production and accepted-walk logic remain main's identical AST. ADR 0056 updated as the candidate's added ruling, matching exercised discovery/claim/contract semantics. Producer doc impact lists none. No changed product diagram or application screen; Surfaces:none CLI output is captured in acceptance.log.

Only added comment: the ADR rule-source pointer. Consumer comment ratio 1/491 (0.2%), within 5%; producer 0/73. Startup, filing, gates, merge ask and archive reading unchanged against current main. Idle adds a 25-word due line or six-word missing-producer line. Current workflow 5836 words differs from earlier stacked evidence because main advanced, but current base and candidate match.

Repository sanitize-check skill applied read-only with existing rules to 33 public files: 0 BLOCK/REJECT, 2 WARNs; both warned lines occur verbatim in current main (sanitize-baseline.log). No contextual privacy or zero-warning guarantee.

Hosted snapshots bind to these heads: #775 six SUCCESS and one SKIPPED documentation deploy; #774 six SUCCESS. Both OPEN, non-draft. Prior RoboRev daemon failures prove no current review verdict. Validation did not start/retry RoboRev; FO retains current-review and delivery disposition.

Retained implementation/design limits: highest cached sibling may differ from enabled; checkout map may differ from trunk; maps outside docs/journey undiscovered; claims persist through archive/decline; no re-walk, cache, map acceptance field, production rollout, human release walk, enabled-cache activation, large-workflow performance or compatibility beyond observed CLI. Due always pays one native listing, even when it filters the map. A diagnostic's accepted 120-character preview can truncate a long timeout argv before its timeout suffix.

Harness corrections: the supplementary timeout initially required "timed out" after a long argv that consumed the accepted preview; the final short "node" injection after a successful listing passes. No product bytes changed. Read-only GitHub snapshot capture and removal of only the two owned worktrees' Git metadata completed through approved escalations. No config or shell workaround.

## Timing observations

One observation each, seconds; exact commands/output in timings.json.

- Unmapped current workflow: producer: 4.7761 seconds; exit 1.
- Unmapped current workflow: due: 2.3549 seconds; exit 0.
- Mapped five-task scratch: producer: 0.2802 seconds; exit 0.
- Mapped five-task scratch: due: 0.4952 seconds; exit 0.

## Exact audit commands and exits

- lint: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B kc-dev-flow-2/scripts/lint-skills.py -> exit 0; lint.log
- adr: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since origin/main --require 0056 -> exit 0; adr.log
- adr-dispatch-path: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since origin/main --require 0056 -> exit 0; adr-dispatch-path.log
- numbers-main: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/number_guards.py check --repo /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger.md --base origin/main -> exit 0; numbers-main.log
- comments: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/comment_ratio.py origin/main HEAD --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 -> exit 0; comments.log
- doc-impact: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/doc_impact.py origin/main HEAD -> exit 0; doc-impact.log
- design-surfaces: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/design_surfaces.py check /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger.md -> exit 0; design-surfaces.log
- dispatch: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/dispatch_records.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/release-walk-due-trigger -> exit 1; dispatch.log
- diff-check: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer && git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer diff --check origin/main...HEAD -> exit 0; diff-check.log
- scope-main: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer && git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-consumer diff --name-only origin/main...HEAD -> exit 0; scope-main.log
- producer-adr: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-producer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since origin/main -> exit 0; producer-adr.log
- producer-comments: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-producer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/comment_ratio.py origin/main HEAD --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 -> exit 0; producer-comments.log
- producer-doc-impact: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-producer && /Users/kent/.pyenv/versions/3.11.14/bin/python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/doc_impact.py origin/main HEAD -> exit 0; producer-doc-impact.log
- producer-diff-check: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-producer && git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-producer diff --check origin/main...HEAD -> exit 0; producer-diff-check.log
- producer-scope: cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-producer && git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger/.validation-3-producer diff --name-only origin/main...HEAD -> exit 0; producer-scope.log

Producer number guard used the same loaded package and arguments with --repo .validation-3-producer and --base origin/main; exit 0 (producer-numbers-main.log). Migration checks skip because no migrations-path is declared; ADR checks ran. Consumer ADR lint: 53 records, no legacy.

## Captain acceptance: four exact steps

Prerequisites: named repository with both commit objects; Git, Python 3, Node, npm and Spacedock on PATH; npm registry access if dependencies are uncached. No secret/config write. This is CLI acceptance. Run unchanged in a fresh Bash shell; acceptance.sh contains this exact text. Expected: eight producer tests, 18 due tests, three idle tests, two YAML-comment PASS lines, no skips, exit 0. Does not replace full suites, mutations, guards, local review, CI, scale proof or delivery approval.

```bash
#!/bin/bash
set -euo pipefail
# 1. Export both exact candidates into disposable directories; require git, Python 3, Node, npm and spacedock on PATH.
repo='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-walk-due-trigger'
scratch=$(mktemp -d "$repo/.acceptance.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT
mkdir "$scratch/consumer" "$scratch/producer"
git -C "$repo" archive bbf65bb3a621ad1c664698e0d50af8b4f4e0f1ec | tar -x -C "$scratch/consumer"
git -C "$repo" archive b026e0d7e497f7dc0ae0bae03fb1558810a36db3 | tar -x -C "$scratch/producer"
export VALIDATION_CONSUMER="$scratch/consumer" VALIDATION_PRODUCER="$scratch/producer"
printf 'Exact consumer bbf65bb3a621ad1c664698e0d50af8b4f4e0f1ec; producer b026e0d7e497f7dc0ae0bae03fb1558810a36db3 exported\n'
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

Observed command: /bin/bash --noprofile --norc /tmp/release-walk-due-trigger-validation-3/acceptance.sh; exit 0.

```text
Exact consumer bbf65bb3a621ad1c664698e0d50af8b4f4e0f1ec; producer b026e0d7e497f7dc0ae0bae03fb1558810a36db3 exported
✔ the table and version print and the recorded hash binds them (44.557ms)
✔ an edited table with an unchanged version exits 1 naming the schema (43.845709ms)
✔ a bumped version with no recorded hash exits 1 (44.535084ms)
✔ the printed history pointers name files that exist and a runnable command (152.1385ms)
✔ release-walk prints its table and version, and an edited table with an unchanged version exits 1 (97.000083ms)
✔ journey-progress registers its printed table and refuses an unversioned shape edit (89.51275ms)
✔ the progress producer preserves the registered keys and acceptance meanings (672.909834ms)
✔ the README and SKILL.md send a reader to the schema command, the CHANGELOG and the ADR, and say when (0.862959ms)
ℹ tests 8
ℹ suites 0
ℹ pass 8
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 1202.601959
..................
----------------------------------------------------------------------
Ran 18 tests in 8.685s

OK
...
----------------------------------------------------------------------
Ran 3 tests in 1.487s

OK
PASS status comment: producer pending=2, due reminders=2, expected=2
PASS claim comment: producer pending=2, due reminders=1, expected=1

```

## Cleanup and handoff

Both detached probe worktrees and the owned support directory were removed. Assigned branch remains bbf65bb3a621ad1c664698e0d50af8b4f4e0f1ec with a clean tree. Task remains validation. Only the entity report and validation-3 evidence are committed through the entity-scoped state command. No push. FO retains F5 disposition, current review evidence and producer-first delivery.
