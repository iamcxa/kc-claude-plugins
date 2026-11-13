#!/usr/bin/env python3
"""Exercise the approved falsifiers on disposable source mirrors, not the candidate."""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--code", type=Path, required=True)
    p.add_argument("--scratch", type=Path, required=True)
    a = p.parse_args()
    evidence = Path(__file__).parent
    scripts = a.code / "kc-dev-flow-2/scripts"
    source = {name: (scripts / name).read_text() for name in
              ["observer_check.py", "pr_watch.py", "laws_check.py", "test_laws_check.py"]}
    mirrors = a.scratch / "mutations"
    if mirrors.exists():
        shutil.rmtree(mirrors)
    mirrors.mkdir(parents=True, exist_ok=True)
    # All disposable source paths stay inside the assigned worktree.
    assert mirrors.resolve().is_relative_to(a.code.resolve())
    for cache in a.code.glob("kc-dev-flow-2/**/__pycache__"):
        shutil.rmtree(cache)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cases = []

    def add(name, script, changes, mode, test=None):
        root = mirrors / name
        folder = root / "kc-dev-flow-2/scripts"
        folder.mkdir(parents=True)
        for item in scripts.iterdir():
            if item.is_file():
                (folder / item.name).symlink_to(item)
        for link in ["extensions", "references"]:
            (folder.parent / link).symlink_to(a.code / "kc-dev-flow-2" / link)
        text = source[script]
        for old, new in changes:
            assert old in text, (name, old)
            text = text.replace(old, new, 1)
        target = folder / script
        target.unlink()
        target.write_text(text)
        # Resolve the tested module beside its mutant rather than through a symlink.
        if test and test[0] != script:
            target_test = folder / test[0]
            target_test.unlink()
            target_test.write_bytes((scripts / test[0]).read_bytes())
        if mode in ["fixtures", "real"]:
            argv = [sys.executable, "-B", evidence / "probe.py", mode,
                    "--code", root, "--scratch", a.scratch]
            if mode == "real":
                argv += ["--workflow", "/Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2"]
        elif mode == "watch-runtime":
            # Bypass the old string pin to reach the actual post-archive execution.
            runner = root / "run.py"
            runner.write_text("import importlib.util, unittest\n"
                              "s=importlib.util.spec_from_file_location('cases', " + repr(str(folder / test[0])) + ")\n"
                              "m=importlib.util.module_from_spec(s); s.loader.exec_module(m)\n"
                              "t=m.TasksTests('" + test[1].split('.', 1)[1] + "')\n"
                              "t.assertRegex=lambda *a, **k: None\n"
                              "r=unittest.TextTestRunner().run(unittest.TestSuite([t]))\n"
                              "raise SystemExit(0 if r.wasSuccessful() else 1)\n")
            argv = [sys.executable, "-B", runner]
        else:
            argv = [sys.executable, "-B", folder / test[0], test[1]]
        cases.append((name, argv))

    add("AC1-unconditional-learn", "observer_check.py",
        [('return "learn" in readme_extensions(readme)', 'return True')], "fixtures")
    add("AC2-delete-notice", "observer_check.py",
        [('"next: send learn\'s notice, then the observer report unedited, in one message; answer none of its findings."', '""')], "fixtures")
    add("AC2-reorder-steps", "observer_check.py",
        [('] if archived and learn_enabled(state, readme) else []', '][::-1] if archived and learn_enabled(state, readme) else []')], "fixtures")
    add("AC2-read-report-from-disk", "observer_check.py",
        [('code, out = git(state, "show", f"{rev}:./{path}")',
          'code, out = (0, (state / path).read_text()) if (state / path).is_file() else (1, "")')],
        "unit", ("test_observer_check.py", "ObserverCheckTest.test_the_committed_tree_decides_not_the_disk"))
    add("AC2-print-learn-live", "observer_check.py",
        [('if archived and learn_enabled(state, readme) else []', 'if learn_enabled(state, readme) else []'),
         ('(learn if archived else [])', 'learn')],
        "unit", ("test_observer_check.py", "ObserverCheckTest.test_an_archived_report_prints_the_learn_steps_and_a_live_one_does_not"))
    add("AC3-omit-printed-readme", "pr_watch.py",
        [('f"--readme {shlex.quote(str(workflow / \'README.md\'))}")', '"")')],
        "watch-runtime", ("test_pr_watch.py", "TasksTests.test_a_merged_task_pr_with_the_report_committed_lets_pr_merge_record_it_and_names_the_steps_after"))
    add("AC4-unexpected-verdict-output", "observer_check.py",
        [('observer report committed:', 'observer report checked:')], "real")
    add("AC5-omit-parser-fixture", "test_laws_check.py",
        [('\"decision_ledger.py\", \"workflow_extensions.py\", \"observer_check.py\"',
          '\"decision_ledger.py\", \"observer_check.py\"')],
        "unit", ("test_laws_check.py", "ExitContractTest.test_exit_2_wins_over_a_violation_and_both_print"))

    prior_laws = subprocess.run(["git", "-C", str(a.code), "show", "17eccdda05fde54e6dff66f4989787864219ef43:kc-dev-flow-2/scripts/laws_check.py"], capture_output=True, text=True, check=True).stdout
    add("round3-restore-laws-parser", "laws_check.py", [(source["laws_check.py"], prior_laws)],
        "unit", ("test_laws_check.py", "L1Test.test_l1_uses_the_shared_extension_list_forms_and_ignores_comment_words"))
    add("round3-restore-watcher-parser", "pr_watch.py",
        [('listed = set(readme_extensions(workflow / "README.md"))', 'listed = set(re.findall(r"[\\w-]+", readme.get("extensions", "")))')],
        "unit", ("test_pr_watch.py", "TasksTests.test_extension_list_forms_use_the_shared_reader_and_ignore_comment_words"))

    # Test the document-identity falsifier on copied documents, preserving approved source scope.
    docs = mirrors / "AC6-governing-document-edit"
    for relative in ["references/sd/workflow.md", "references/sd/mods/kc-dev-flow-2.md",
                     "extensions/learn/EXTENSION.md", "scripts/pr_watch.py"]:
        dest = docs / "kc-dev-flow-2" / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((a.code / "kc-dev-flow-2" / relative).read_bytes())
    changed = docs / "kc-dev-flow-2/references/sd/workflow.md"
    changed.write_text(changed.read_text() + "\nMutation fixture.\n")
    cases.append(("AC6-governing-document-edit", [sys.executable, "-B", evidence / "words.py", docs]))

    def execute(case):
        name, argv = case
        done = subprocess.run(list(map(str, argv)), cwd=a.code, env=env, capture_output=True, text=True, timeout=180)
        suffix = ".json" if name.startswith(("AC1", "AC4")) or name in ["AC2-delete-notice", "AC2-reorder-steps"] else ".log"
        path = evidence / (name + suffix)
        path.write_text(done.stdout + (done.stderr if suffix == ".log" else ""))
        if suffix == ".json":
            assert not done.stderr, name
        return {"name": name, "command": list(map(str, argv)), "exit": done.returncode,
                "detected": done.returncode == 1, "output": path.name}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(execute, cases))
    summary = {"python_bytecode_disabled": True, "existing_caches_cleared": True,
               "mutations": rows, "detected": sum(r["detected"] for r in rows), "total": len(rows)}
    (evidence / "mutations.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"detected": summary["detected"], "total": summary["total"]}))
    return 0 if all(row["detected"] for row in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
