"""Run named falsifiers in disposable script copies, never changing the candidate."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

source, scratch, output = map(Path, sys.argv[1:])
scripts = source / "kc-dev-flow-2/scripts"
original = (scripts / "dispatch_records.py").read_text()
prefix = "test_dispatch_records.RepairedRulingHistoryTests."
changes = [
    ("remove-historical-catch", "except (RulingHistoryError, ValueError) as error:", "except () as error:",
     ["test_repaired_amendment_after_report_clears"]),
    ("identity-always-absent", "def may_hold(snapshot, key):\n", "def may_hold(snapshot, key):\n    return False\n",
     ["test_pre_report_broken_text_carrying_clearing_identity_holds"]),
    ("drop-after-report-filter", "if (c == report_commit or not ancestor(report_commit, c)) and may_hold(snapshot, key)]",
     "if may_hold(snapshot, key)]", ["test_repaired_amendment_after_report_clears", "test_ruling_then_later_heading_typo_repaired_clears"]),
    ("every-pre-report-break-blocks", "and may_hold(snapshot, key)]", "]",
     ["test_pre_report_broken_text_without_clearing_identity_clears"]),
    ("catch-only-ruling-history-error", "except (RulingHistoryError, ValueError) as error:", "except RulingHistoryError as error:",
     ["test_bad_quoted_gate_scalar_repaired_before_report_clears"]),
    ("raise-any-stored-error", "    blocked = None\n", "    if unparsed:\n        raise next(iter(unparsed.values()))[0]\n    blocked = None\n",
     ["test_repaired_history_without_later_ruling_needs_ruling"]),
    ("accept-two-task-paths", "    if len(present) > 1:\n        raise RulingHistoryError(\"ambiguous-task-paths\")\n", "",
     ["test_two_historical_task_paths_stay_held"]),
    ("ignore-hidden-report-gap", "    if any(ancestor(report_commit, commit) for commit in absent):\n        raise RulingHistoryError(\"discontinuous-report-history\")\n", "",
     ["test_historical_fence_hiding_report_stays_held"]),
    ("replace-undecodable-bytes", "done = subprocess.run([\"git\", \"-C\", str(root), *args], capture_output=True, text=True)",
     "done = subprocess.run([\"git\", \"-C\", str(root), *args], capture_output=True, text=True, errors=\"replace\")",
     ["test_undecodable_historical_bytes_stay_held"]),
]
results = []
variants = [("baseline", (scratch / "tag/kc-dev-flow-2/scripts/dispatch_records.py").read_text(), ["test_dispatch_records.RepairedRulingHistoryTests"])]
for name, old, new, tests in changes:
    assert original.count(old) == 1, (name, original.count(old))
    variants.append((name, original.replace(old, new), [prefix + t for t in tests]))
relaxed = original
for variable, value in [("current", "text"), ("committed", "pinned")]:
    line = f"    _, {variable} = captain_records({value}, slug)\n"
    relaxed = relaxed.replace(line, f"    try:\n        _, {variable} = captain_records({value}, slug)\n    except (RulingHistoryError, ValueError):\n        {variable} = set()\n")
variants.append(("swallow-current-and-pinned-errors", relaxed, [prefix + "test_unrepaired_current_or_pinned_text_stays_held"]))
for name, text, tests in variants:
    root = scratch / "mutations" / name
    shutil.copytree(scripts, root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (root / "dispatch_records.py").write_text(text)
    done = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests], cwd=root,
                          capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    log = output / ("mutation-" + name + ".log")
    log.write_text(done.stdout + done.stderr)
    killed = done.returncode == 1 and "FAIL:" in done.stderr and "ERROR:" not in done.stderr
    results.append({"name": name, "exit": done.returncode, "killed": killed, "tests": tests, "log": str(log)})
    print(name, done.returncode, "killed" if killed else "UNEXPECTED", flush=True)
(output / "mutations.json").write_text(json.dumps(results, indent=2) + "\n")
sys.exit(0 if all(r["killed"] for r in results) else 1)
