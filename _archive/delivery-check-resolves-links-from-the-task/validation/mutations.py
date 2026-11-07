import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

wt = Path(sys.argv[1])
out = Path(sys.argv[2] if len(sys.argv) > 2 else Path(__file__).resolve().parent)
scripts = wt / "kc-dev-flow-2/scripts"
source = (scripts / "delivery_gate.py").read_text()
mutations = [
    ("AC-1 cwd-based Markdown", "named_file(folder, re.sub", "Path(re.sub",
     "TaskFolderCaptainTests.test_question_reads_task_card_from_repository_state_and_task_directories"),
    ("AC-2 drop slug base", '(folder.parent if path.parts[:1] == (folder.name,) else folder) / path', 'folder / path',
     "TaskFolderCaptainTests.test_question_reads_slug_prefixed_markdown_from_task_folder"),
    ("AC-3 steps use cwd", "record.resolve().parent.parent)", "Path.cwd())",
     "CaptainStepsTests.test_relative_markdown_card_is_read_by_the_real_cli"),
    ("AC-4 reports reenter S4", "for path in absolute_paths(asked_paths):", "for path in absolute_paths(path_text):",
     "TaskFolderCaptainTests.test_report_routes_do_not_hide_missing_message_or_asked_paths"),
    ("AC-7 report prose links count", "if path.resolve() in own:", "if True:",
     "TaskFolderCaptainTests.test_report_only_cards_require_fences_and_fo_named_cards_also_require_links"),
    ("AC-6 alter emitted text", 'emit("gate text complete", ASK_FORM)', 'emit("gate text altered", ASK_FORM)',
     "CaptainGateTests.test_relay_412_holds_without_record_or_at_later_head_and_passes_at_dispatched_head"),
]
results = []
for n, (name, old, new, test) in enumerate(mutations, 1):
    assert source.count(old) == 1, old
    with tempfile.TemporaryDirectory(prefix="delivery-link-mutant-") as temp:
        package = Path(temp) / "kc-dev-flow-2"
        shutil.copytree(wt / "kc-dev-flow-2", package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        target = package / "scripts/delivery_gate.py"
        target.write_text(source.replace(old, new))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        run = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_delivery_gate." + test],
                             cwd=target.parent, env=env, capture_output=True, text=True)
        log = out / f"mutation-{n}.log"
        log.write_text(run.stdout + run.stderr)
        killed = run.returncode == 1 and "FAIL:" in run.stderr and "ERROR:" not in run.stderr
        results.append({"name": name, "status": "passed" if killed else "failed",
                        "message": f"mutant exit={run.returncode}; assertion {'failed as required' if killed else 'did not falsify'}; {log}"})
(out / "mutations.json").write_text(json.dumps(results, indent=2))
for row in results:
    print(row["name"], row["status"], row["message"])
sys.exit(0 if all(r["status"] == "passed" for r in results) else 1)

