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

