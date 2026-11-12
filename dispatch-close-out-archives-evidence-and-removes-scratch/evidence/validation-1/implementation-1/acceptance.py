"""Usage: python3 -B acceptance.py CODE_REPO SPACEDOCK_BINARY OWNED_OUTPUT_FOLDER.
Uses the task's ../s4_repro.py and candidate tests; requires git and Python stdlib.
"""
import json, os, pathlib, subprocess, sys, unittest
scripts=pathlib.Path(sys.argv[1]).resolve()/"kc-dev-flow-2/scripts"
binary=pathlib.Path(sys.argv[2]).resolve(strict=True)
out=pathlib.Path(sys.argv[3]).resolve(); out.mkdir(parents=True,exist_ok=True)
(out/"tmp").mkdir(exist_ok=True)
os.environ.update(TMPDIR=str(out/"tmp"),SPACEDOCK_BIN=str(binary),PYTHONDONTWRITEBYTECODE="1")
sys.path.insert(0,str(scripts))
assert not list(scripts.rglob("*.pyc")), "clear candidate Python caches before verification"
rows=[]
class Results(unittest.TextTestResult):
    def addSuccess(self,test):
        super().addSuccess(test); rows.append(dict(name=test.id(),status="passed"))
    def addFailure(self,test,error):
        super().addFailure(test,error); rows.append(dict(name=test.id(),status="failed",message=self._exc_info_to_string(error,test)))
    def addError(self,test,error):
        super().addError(test,error); rows.append(dict(name=test.id(),status="failed",message=self._exc_info_to_string(error,test)))
names=["test_scratch.ScratchTests", "test_dispatch_stage.DispatchStageTests.test_scratch_in_record_and_real_dispatch_artifact_without_changing_input", "test_dispatch_stage.DispatchStageTests.test_scope_notes_outside_scratch_refuse_before_record_and_build", "test_dispatch_stage.DispatchStageTests.test_scope_notes_inside_scratch_are_kept", "test_pr_watch.TasksTests.test_scratch_sweep_prompts_old_and_archived_roots_and_leaves_current_and_unknown", "test_pr_watch.TasksTests.test_merged_scratch_prompt_precedes_merge_record", "test_pr_watch.TasksTests.test_post_archive_removal_record_preserves_learn_and_observer_results"]
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in names)
with (out/"acceptance.log").open("w") as log:
    result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Results).run(suite)
repro=pathlib.Path(__file__).resolve().parent.parent/"s4_repro.py"
done=subprocess.run([sys.executable,"-B",str(repro),str(scripts)],capture_output=True,text=True)
(out/"s4.log").write_text(done.stdout+done.stderr)
rows.append(dict(name="AC2 removed report path and missing FO-message path",status="passed" if done.returncode==0 else "failed"))
(out/"acceptance.json").write_text(json.dumps(rows,indent=2))
sys.exit(not result.wasSuccessful() or done.returncode!=0)
