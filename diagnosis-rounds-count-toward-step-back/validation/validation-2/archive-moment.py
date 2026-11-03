import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(os.environ["DIAGNOSIS_CODE_ROOT"]) / "kc-dev-flow-2/scripts"))
import test_pr_watch
case = test_pr_watch.TasksTests()
case.setUp()
try:
    case.readme("")
    case.task("diagnosis", worktree=False)
    dispatch = case.state / "diagnosis/dispatch"
    dispatch.mkdir(parents=True)
    for n in (2, 3, 4):
        (dispatch / f"implementation-{n}.md").write_text("Dispatched: 2026-11-03\nSymptom: page freeze\n")
    case.task("diagnosis", worktree=False)
    live = case.tasks({})
    assert live[0] == 0 and any('3 implementation dispatches on symptom "page freeze"' in line for line in live[1])
    (case.state / "_archive").mkdir()
    case.git(case.state, "mv", "diagnosis.md", "_archive/diagnosis.md")
    case.git(case.state, "mv", "diagnosis", "_archive/diagnosis")
    case.git(case.state, "commit", "-qm", "archive")
    archived = case.tasks({})
    assert archived == (0, [])
    Path(os.environ["DIAGNOSIS_EVIDENCE_DIR"], "archive-moment.json").write_text(json.dumps({"live": live, "archived": archived}, indent=2))
    print("After archive: real pr_watch tasks emits zero lines for the previously owed symptom.")
finally:
    case.doCleanups()
