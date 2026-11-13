#!/usr/bin/env python3
"""Reproduce this task's bounded evidence; private reads emit counts only."""
import argparse
import atexit
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest import mock

BASE = "8125e6d516d32abbf79c6772de10cde2c20900a8"
HERE = Path(__file__).resolve().parent
NAMES = ("journey-server-host-pilot", "pr-review-lite-value-pilot")
TEMPORARY = []


def audit(event, args):
    if event == "tempfile.mkdtemp":
        TEMPORARY.append(str(args[0]))


sys.addaudithook(audit)


def load(repo, base=False):
    scripts = repo / "kc-dev-flow-2/scripts"
    sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location("probe_tests", scripts / "test_pr_watch.py")
    tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tests)
    if base:
        source = subprocess.check_output(["git", "-C", os.environ.get("PR_WATCH_SOURCE_REPO", str(repo)), "show", BASE + ":kc-dev-flow-2/scripts/pr_watch.py"], text=True)
        watch = types.ModuleType("baseline_pr_watch")
        watch.__file__ = str(scripts / "pr_watch.py")
        exec(compile(source, watch.__file__, "exec"), watch.__dict__)
        tests.watch = watch
    return tests


def unit(tests, methods):
    suite = unittest.TestSuite(tests.TasksTests(name) for name in methods)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def real_cases(tests, workflow, baseline=False, sd_binary="spacedock"):
    watch = tests.watch
    state = workflow / watch.front(workflow / "README.md").get("state", ".")
    selected = [(slug, path) for slug, path in watch.entities(state) if slug in NAMES]
    assert len(selected) == 2, "both Scope cases must be present"
    metadata = []
    for slug, path in selected:
        meta = watch.front(path)
        assert not meta.get("pr"), "Scope case now has a PR: reassess before relying on old evidence"
        assert meta.get("worktree") and not (watch.toplevel(workflow) / meta["worktree"]).is_dir()
        metadata.append({"slug": slug, "entity": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "status": meta["status"], "worktree": meta["worktree"], "pr": meta.get("pr", "")})
    case = tests.TasksTests("test_an_empty_pr_whose_worktree_is_gone_is_a_fact_and_one_with_no_worktree_field_stays_silent")
    case.setUp()
    try:
        def no_provider(*args, **kwargs):
            raise AssertionError("a missing-worktree case must not query GitHub")
        output = io.StringIO()
        with mock.patch.object(watch, "entities", return_value=selected), \
             mock.patch.object(watch, "archived_learning", return_value=([], [])), \
             mock.patch.object(watch, "release_walks_due", return_value=([], [])), \
             mock.patch.dict(os.environ, {"SPACEDOCK_BIN": sd_binary}), \
             contextlib.redirect_stdout(output):
            code = watch.main(["--state", str(case.watch), "tasks", str(workflow)], ask=no_provider, look=no_provider)
        lines = output.getvalue().splitlines()
        assert code == 0, output.getvalue()
        for slug in NAMES:
            expected = (f"next: record {slug}'s PR with status --set {slug} pr=<owner/repo>#<N>; its worktree is not on this machine."
                        if baseline else f"fact: {slug} has no recorded PR; its worktree is not on this machine.")
            assert expected in lines, (slug, lines)
            if not baseline:
                assert not any(line.startswith(f"next: record {slug}'s PR") or
                               (line.startswith("next:") and f"--set {slug} pr=" in line) for line in lines)
        assert not case.watch.exists(), "no PR may be added to the watch list"
        print(json.dumps({"mode": "base" if baseline else "probe", "scope_cases": metadata,
                          "task_selection": "only the two Scope cases; original files read in place",
                          "native_status": [sd_binary, "status", "--workflow-dir", str(workflow), "--next", "--json"],
                          "unrelated_archive_and_release_scans": "disabled; no provider queries permitted",
                          "exit": code, "watch_created": False, "output": lines}, indent=2))
        return lines
    finally:
        case.doCleanups()


def counts(tests, roots):
    watch = tests.watch
    rows = []
    for index, root in enumerate(roots, 1):
        workflow = root / "docs/dev2"
        state = workflow / watch.front(workflow / "README.md").get("state", ".")
        assert state.is_dir(), "state checkout unavailable; do not report an empty corpus"
        row = dict(adopter=index, tasks=0, recorded_pr=0, missing_worktree_without_pr=0,
                   local_worktree_without_pr=0, no_worktree_without_pr=0)
        selected = []
        for slug, path in watch.entities(state):
            meta = watch.front(path)
            if "status" not in meta:
                continue
            row["tasks"] += 1
            if meta.get("pr"):
                row["recorded_pr"] += 1
            elif meta.get("worktree"):
                local = (root / meta["worktree"]).is_dir()
                row["local_worktree_without_pr" if local else "missing_worktree_without_pr"] += 1
                if not local:
                    selected.append((slug, path))
            else:
                row["no_worktree_without_pr"] += 1
        row["tracked_pr_watch_copies"] = len(subprocess.check_output(
            ["git", "-C", str(root), "ls-files", "*pr_watch.py"], text=True).splitlines())
        if selected:
            case = tests.TasksTests("test_an_empty_pr_whose_worktree_is_gone_is_a_fact_and_one_with_no_worktree_field_stays_silent")
            case.setUp()
            try:
                def no_provider(*args, **kwargs):
                    raise AssertionError("foreign-worktree branch unexpectedly queried a provider")
                output = io.StringIO()
                with mock.patch.object(watch, "entities", return_value=selected), \
                     mock.patch.object(watch, "ready_rows", return_value=[]), \
                     mock.patch.object(watch, "archived_learning", return_value=([], [])), \
                     mock.patch.object(watch, "release_walks_due", return_value=([], [])), \
                     contextlib.redirect_stdout(output):
                    code = watch.main(["--state", str(case.watch), "tasks", str(workflow)], ask=no_provider, look=no_provider)
                lines = output.getvalue().splitlines()
                row["probe_exit"] = code
                row["fact_lines"] = sum(f"fact: {slug} has no recorded PR; its worktree is not on this machine." in lines for slug, _ in selected)
                row["record_pr_actions"] = sum(any(line.startswith(f"next: record {slug}'s PR") or
                    (line.startswith("next:") and f"--set {slug} pr=" in line) for line in lines) for slug, _ in selected)
                assert code == 0 and row["fact_lines"] == len(selected) and row["record_pr_actions"] == 0
                assert not case.watch.exists()
            finally:
                case.doCleanups()
        rows.append(row)
    print(json.dumps({"read_only": True, "private_content": "counts only", "counts": rows}, indent=2))


def words(repo):
    before, after = load(repo, True), load(repo)
    static = repo / "kc-dev-flow-2/references/sd/workflow.md"
    mod = repo / "kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md"
    for source in (static, mod):
        original = subprocess.check_output(["git", "-C", os.environ.get("PR_WATCH_SOURCE_REPO", str(repo)), "show", BASE + ":" + str(source.relative_to(repo))])
        assert source.read_bytes() == original, "the common lifecycle passage changed; recount its actual loading"
    common = len(static.read_text().split()) + len(mod.read_text().split())
    rows = []
    for moment in ("startup", "idle-open-pr", "idle-merged-pr", "after-archive", "merge-ask"):
        values = []
        for tests in (before, after):
            case = tests.TasksTests("test_a_pr_a_worker_opened_is_recorded_with_two_commands_and_then_watched")
            case.setUp()
            try:
                case.readme("roborev")
                case.task("foreign-one")
                case.task("foreign-two")
                import shutil
                shutil.rmtree(case.repo / ".worktrees/foreign-one")
                shutil.rmtree(case.repo / ".worktrees/foreign-two")
                answers = {}
                if moment == "idle-open-pr":
                    case.task("one", pr="o/r#7")
                    answers = {"pr view 7": tests.view()}
                elif moment == "idle-merged-pr":
                    case.task("one", pr="o/r#7")
                    answers = {"pr view 7": tests.view("MERGED")}
                elif moment == "after-archive":
                    case.task("archived", worktree=False)
                    (case.state / "_archive").mkdir()
                    (case.state / "archived.md").rename(case.state / "_archive/archived.md")
                code, lines = case.tasks(answers)
                assert code == 0, lines
                output_words = len("\n".join(lines).split())
                values.append({"common_workflow_and_mod_words": common, "tasks_output_words": output_words,
                               "bounded_total": common + output_words, "output": lines})
            finally:
                case.doCleanups()
        assert values[1]["bounded_total"] <= values[0]["bounded_total"]
        rows.append({"moment": moment, "before": values[0], "after": values[1]})
    print(json.dumps({"counter": "str.split whitespace words", "common_sources": [str(static), str(mod)],
                      "limit": "paired bounded scenarios with two absent-worktree tasks; not full-fleet totals; merge-ask does not rerun tasks, so its tasks output is the carried idle result; unchanged observer/review/delivery passages have zero delta and are not included",
                      "rows": rows}, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("criterion", choices=["AC-1", "AC-2", "AC-3", "AC-4", "adopters"])
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--workflow", type=Path)
    p.add_argument("--base", action="store_true")
    p.add_argument("--sd-bin", default=os.environ.get("SPACEDOCK_BIN", "spacedock"))
    p.add_argument("--adopter", type=Path, action="append", default=[])
    args = p.parse_args()
    def save_cleanup():
        rows = [{"path": path, "exists_after_command": Path(path).exists()} for path in TEMPORARY]
        (HERE / ("scratch-" + args.criterion + ("-base" if args.base else "-probe") + ".json")).write_text(json.dumps(rows, indent=2) + "\n")
    atexit.register(save_cleanup)
    tests = load(args.repo, args.base)
    if args.criterion == "AC-1":
        return unit(tests, ["test_an_empty_pr_whose_worktree_is_gone_is_a_fact_and_one_with_no_worktree_field_stays_silent"])
    if args.criterion == "AC-2":
        return unit(tests, ["test_a_pr_a_worker_opened_is_recorded_with_two_commands_and_then_watched",
                            "test_a_branch_whose_only_pr_is_closed_records_nothing",
                            "test_a_bare_pr_is_resolved_from_the_workflow_checkout_when_its_worktree_is_gone"])
    if args.criterion == "AC-3":
        real_cases(tests, args.workflow, args.base, args.sd_bin)
    elif args.criterion == "AC-4":
        words(args.repo)
    else:
        counts(tests, args.adopter)
    return 0


if __name__ == "__main__":
    sys.exit(main())
