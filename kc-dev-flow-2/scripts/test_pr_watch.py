import contextlib
import importlib.util
import io
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("pr_watch", Path(__file__).with_name("pr_watch.py"))
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)

REF = "o/r#1"


def snap(**kw):
    base = {"state": "OPEN", "draft": False, "mergeable": "MERGEABLE", "checks": "green",
            "head": "aaaaaaaaa", "title": "feat: x", "codex": "-", "codex-evidence": "-", "copilot": "-", "copilot-evidence": "-"}
    return {**base, **kw}


class PrWatchTests(unittest.TestCase):
    def run_main(self, args, looks, state):
        seq = iter(looks)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = watch.main(["--state", str(state), *args], look=lambda ref, **kw: next(seq), sleep=lambda s: None)
        return code, out.getvalue()

    def test_checks_rollup_reads_failing_pending_green_and_none(self):
        self.assertEqual(watch.checks([{"conclusion": "SUCCESS"}, {"conclusion": "FAILURE"}]), "failing")
        self.assertEqual(watch.checks([{"conclusion": "SUCCESS"}, {"status": "IN_PROGRESS", "conclusion": None}]), "pending")
        self.assertEqual(watch.checks([{"state": "SUCCESS"}, {"conclusion": "SKIPPED"}]), "green")
        self.assertEqual(watch.checks([]), "none")

    def test_a_change_is_reported_once_and_a_merged_pr_is_then_dropped(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.assertEqual(self.run_main(["add", REF], [snap()], state)[0], 0)
            code, out = self.run_main(["check"], [snap()], state)
            self.assertIn("no change since the last look", out)
            code, out = self.run_main(["check"], [snap(state="MERGED", codex="-")], state)
            self.assertIn("state OPEN -> MERGED", out)
            self.assertIn(REF, json.loads(state.read_text()))
            self.run_main(["check"], [snap(state="MERGED", codex="-")], state)
            self.assertEqual(json.loads(state.read_text()), {})

    def test_wait_returns_on_the_first_change_and_names_it(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap()], state)
            code, out = self.run_main(["wait", "1"], [snap(), snap(), snap(mergeable="CONFLICTING")], state)
            self.assertEqual(code, 0)
            self.assertIn("mergeable MERGEABLE -> CONFLICTING", out)
            watch.update(state, put={REF: {**snap(codex="clean", **{"codex-evidence": "comment:1"}), "watch-codex": True}})
            code, out = self.run_main(["wait", "1"], [snap(mergeable="CONFLICTING", codex="findings")], state)
            self.assertIn("codex clean -> findings", out)

    def test_wait_ignores_a_start_and_wakes_on_its_outcome(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(checks="none", codex="not-reviewed")], state)
            code, out = self.run_main(["wait", "1"], [snap(checks="pending", codex="running"),
                                                       snap(checks="green", codex="running")], state)
            self.assertIn("checks pending -> green", out)
            self.assertNotIn("none -> pending", out)
            code, out = self.run_main(["wait", "1"], [snap(codex="running", head="bbbbbbbbb"),
                                                       snap(codex="findings", head="bbbbbbbbb")], state)
            self.assertIn("codex running -> findings", out)
            self.assertEqual(watch.outcome("mergeable", "CONFLICTING", "UNKNOWN"), True)
            self.assertEqual(watch.outcome("mergeable", "MERGEABLE", "UNKNOWN"), False)
            self.assertEqual(watch.outcome("mergeable", "UNKNOWN", "MERGEABLE"), False)
            self.assertEqual(watch.outcome("mergeable", "MERGEABLE", "CONFLICTING"), True)

    def test_a_new_codex_verdict_with_the_same_word_still_wakes_wait(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="clean", **{"codex-evidence": "comment:1"})], state)
            code, out = self.run_main(["wait", "1"], [snap(codex="running", **{"codex-evidence": "-"}),
                                                       snap(**{"codex-evidence": "comment:2"})], state)
            self.assertIn("codex-evidence - -> comment:2", out)

    def test_the_codex_reader_is_found_in_its_extension(self):
        self.assertTrue(watch.CODEX.exists(), watch.CODEX)

    def test_wait_on_an_empty_list_ends_and_a_bad_ref_is_a_configuration_error(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.assertIn("watch list is empty", self.run_main(["wait"], [], state)[1])
            self.assertEqual(self.run_main(["add", "not-a-ref"], [], state)[0], 2)

    def test_a_pr_that_cannot_be_read_stays_watched(self):
        def fail(ref, **kw):
            raise RuntimeError("gh: not found")
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap()], state)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                watch.main(["--state", str(state), "check"], look=fail)
            self.assertIn("not read", out.getvalue())
            self.assertIn(REF, json.loads(state.read_text()))

    def test_look_reads_codex_only_for_an_open_pr(self):
        def view(state):
            return lambda *a: {"state": state, "isDraft": False, "mergeable": "MERGEABLE", "headRefOid": "a" * 40,
                               "statusCheckRollup": [{"conclusion": "SUCCESS"}], "title": "feat: x"}
        asked = []
        review = lambda repo, n: asked.append((repo, n)) or ("findings", "review:5")
        self.assertEqual(watch.look(REF, view=view("OPEN"), review=review, with_codex=True)["codex"], "findings")
        self.assertEqual(watch.look(REF, view=view("MERGED"), review=review, with_codex=True)["codex"], "-")
        self.assertEqual(watch.look(REF, view=view("OPEN"), review=review)["codex"], "-")
        self.assertEqual(asked, [("o/r", "1")])
        self.assertEqual(watch.look(REF, view=view("OPEN"), review_copilot=review)["copilot"], "-")
        self.assertEqual(asked, [("o/r", "1")])
        self.assertEqual(watch.look(REF, view=view("OPEN"), review_copilot=review, with_copilot=True)["copilot"], "findings")

    def test_codex_is_read_only_for_a_pr_added_with_codex(self):
        calls = []

        def look(ref, with_codex=False, **kw):
            calls.append((ref, with_codex))
            return {**snap(codex="clean" if with_codex else "-"), "watch-codex": with_codex}
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            with contextlib.redirect_stdout(io.StringIO()):
                watch.main(["--state", str(state), "add", REF], look=look)
                watch.main(["--state", str(state), "add", "--codex", "o/r#2"], look=look)
                watch.main(["--state", str(state), "check"], look=look)
            self.assertEqual(calls, [(REF, False), ("o/r#2", True), (REF, False), ("o/r#2", True)])

    def test_copilot_is_read_only_for_a_pr_added_with_copilot_and_its_verdict_wakes(self):
        calls = []

        def look(ref, with_copilot=False, **kw):
            calls.append((ref, with_copilot))
            self.assertLess(len(calls), 10, "wait never woke on the new Copilot evidence")
            return {**snap(), "copilot": "answered" if with_copilot else "-",
                    "copilot-evidence": ("review:1" if len(calls) < 3 else "review:9") if with_copilot else "-",
                    "watch-copilot": with_copilot}
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                watch.main(["--state", str(state), "add", REF], look=look)
                watch.main(["--state", str(state), "add", "--copilot", "o/r#2"], look=look)
                watch.update(state, put={"o/r#2": {**json.loads(state.read_text())["o/r#2"],
                                                   "copilot": "answered", "copilot-evidence": "review:1"}})
                code = watch.main(["--state", str(state), "wait", "1"], look=look, sleep=lambda s: None)
            self.assertEqual(calls[:2], [(REF, False), ("o/r#2", True)])
            self.assertEqual(calls[2:4], [(REF, False), ("o/r#2", True)])
            self.assertEqual(code, 0)
            self.assertIn("copilot-evidence review:1 -> review:9", out.getvalue())

    def test_adding_a_watched_pr_again_keeps_its_reviewer_flags(self):
        calls = []

        def look(ref, with_codex=False, with_copilot=False, **kw):
            calls.append((with_codex, with_copilot))
            return {**snap(), "watch-codex": with_codex, "watch-copilot": with_copilot}
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            with contextlib.redirect_stdout(io.StringIO()):
                watch.main(["--state", str(state), "add", "--codex", REF], look=look)
                watch.main(["--state", str(state), "add", "--copilot", REF], look=look)
                watch.main(["--state", str(state), "add", REF], look=look)
                watch.main(["--state", str(state), "add", "o/r#2"], look=look)
            self.assertEqual(calls, [(True, False), (True, True), (True, True), (False, False)])

    def test_a_sweep_keeps_keys_its_own_look_does_not_return(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            state.write_text(json.dumps({REF: {**snap(), "watch-later": True}}))
            with contextlib.redirect_stdout(io.StringIO()):
                watch.main(["--state", str(state), "check"], look=lambda ref, **kw: snap())
            self.assertTrue(json.loads(state.read_text())[REF]["watch-later"])

    def test_an_entry_saved_before_the_codex_flag_keeps_reading_codex(self):
        calls = []

        def look(ref, with_codex=False, **kw):
            calls.append(with_codex)
            return snap()
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            state.write_text(json.dumps({REF: snap()}))
            with contextlib.redirect_stdout(io.StringIO()):
                watch.main(["--state", str(state), "check"], look=look)
            self.assertEqual(calls, [True])

    def test_a_pr_added_while_a_sweep_runs_stays_watched(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap()], state)

            def look_and_add(ref, **kw):
                watch.update(state, put={"o/r#2": snap(title="added meanwhile")})
                return snap()
            with contextlib.redirect_stdout(io.StringIO()):
                watch.main(["--state", str(state), "check"], look=look_and_add)
            self.assertEqual(set(json.loads(state.read_text())), {REF, "o/r#2"})

    def test_a_reviewer_flag_set_while_a_sweep_runs_survives_the_sweep(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            state.write_text(json.dumps({REF: {**snap(), "watch-copilot": False}}))

            def look_and_enable(ref, **kw):
                watch.update(state, put={REF: {**snap(), "watch-copilot": True}})
                return {**snap(), "watch-copilot": False}
            with contextlib.redirect_stdout(io.StringIO()):
                watch.main(["--state", str(state), "check"], look=look_and_enable)
            self.assertTrue(json.loads(state.read_text())[REF]["watch-copilot"])

    def test_an_add_that_read_the_list_earlier_does_not_turn_a_flag_off(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            state.write_text(json.dumps({REF: {**snap(), "watch-copilot": False}}))

            def look_while_another_add_enables(ref, **kw):
                watch.update(state, put={REF: {**snap(), "watch-copilot": True}}, keep_flags=True)
                return {**snap(), "watch-copilot": False}
            with contextlib.redirect_stdout(io.StringIO()):
                watch.main(["--state", str(state), "add", REF], look=look_while_another_add_enables)
            self.assertTrue(json.loads(state.read_text())[REF]["watch-copilot"])

    def test_the_copilot_reader_reports_an_answer_not_a_verdict(self):
        with tempfile.TemporaryDirectory() as d:
            fake = Path(d, "copilot_review.py")
            fake.write_text("print('answered on aaa: x evidence=review:9; evidence=review:5 at t')\nraise SystemExit(0)\n")
            old, watch.COPILOT = watch.COPILOT, fake
            try:
                self.assertEqual(watch.copilot("o/r", "1"), ("answered", "review:5"))
            finally:
                watch.COPILOT = old

    def test_a_copilot_refusal_is_not_run_not_a_reader_error_and_wakes_wait(self):
        with tempfile.TemporaryDirectory() as d:
            fake = Path(d, "copilot_review.py")
            fake.write_text("print('not a review of aaa: \"quota limit\"; answer=review:5 at t')\nraise SystemExit(5)\n")
            old, watch.COPILOT = watch.COPILOT, fake
            try:
                self.assertEqual(watch.copilot("o/r", "1"), ("not-run", "-"))
            finally:
                watch.COPILOT = old
        self.assertTrue(watch.outcome("copilot", "requested", "not-run"))

    def test_a_copilot_refusal_already_there_when_the_pr_is_added_wakes_wait_once(self):
        refused = snap(copilot="not-run", **{"watch-copilot": True})
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            code, out = self.run_main(["add", "--copilot", REF], [refused], state)
            self.assertIn(f"{REF}: copilot not-run already", out)
            code, out = self.run_main(["wait", "1"], [refused], state)
            self.assertIn("copilot - -> not-run", out)

    def test_a_codex_verdict_already_there_when_the_pr_is_added_wakes_wait(self):
        done = snap(codex="clean", **{"codex-evidence": "comment:1", "watch-codex": True})
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            code, out = self.run_main(["add", "--codex", REF], [done], state)
            self.assertIn(f"{REF}: codex clean already", out)
            code, out = self.run_main(["wait", "1"], [done], state)
            self.assertIn("codex - -> clean", out)

    def test_adding_a_pr_again_after_wait_reported_its_outcome_stays_quiet(self):
        refused = snap(copilot="not-run", **{"watch-copilot": True})
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", "--copilot", REF], [refused], state)
            self.run_main(["wait", "1"], [refused], state)
            code, out = self.run_main(["add", REF], [refused], state)
            self.assertNotIn("already", out)
            code, out = self.run_main(["check"], [refused], state)
            self.assertIn("no change since the last look", out)

    def test_a_non_outcome_or_unwatched_reading_at_add_is_stored_as_read(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            code, out = self.run_main(["add", "--copilot", REF], [snap(copilot="requested", **{"watch-copilot": True})], state)
            self.assertNotIn("already", out)
            self.assertEqual(json.loads(state.read_text())[REF]["copilot"], "requested")

    def test_a_save_keeps_fields_another_writer_added_meanwhile(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            state.write_text(json.dumps({REF: snap()}))

            def look_while_a_newer_watcher_writes(ref, **kw):
                watch.update(state, put={REF: {**snap(), "future-field": "kept"}}, keep_flags=True)
                return snap()
            with contextlib.redirect_stdout(io.StringIO()):
                watch.main(["--state", str(state), "check"], look=look_while_a_newer_watcher_writes)
            self.assertEqual(json.loads(state.read_text())[REF]["future-field"], "kept")

    def test_a_slow_sweep_does_not_roll_back_a_newer_observation(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            state.write_text(json.dumps({REF: snap(copilot="requested", **{"copilot-evidence": "-"})}))

            def slow_look(ref, **kw):
                newer = snap(copilot="answered", **{"copilot-evidence": "review:9"})
                watch.update(state, put={REF: newer}, keep_flags=True)
                return snap(copilot="requested", **{"copilot-evidence": "-"})
            with contextlib.redirect_stdout(io.StringIO()):
                watch.main(["--state", str(state), "check"], look=slow_look)
            self.assertEqual(json.loads(state.read_text())[REF]["copilot-evidence"], "review:9")

    def test_a_state_file_named_like_the_lock_keeps_its_list(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "watch.lock")
            self.run_main(["add", REF], [snap()], state)
            self.run_main(["add", "o/r#2"], [snap(title="second")], state)
            self.assertEqual(set(json.loads(state.read_text())), {REF, "o/r#2"})

    def test_help_exits_zero(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(watch.main(["--help"]), 0)
            self.assertEqual(watch.main(["no-such-command"]), 2)

    def test_codex_column_is_a_dash_without_the_sibling_reader(self):
        missing = Path(tempfile.gettempdir(), "no-such-codex-review.py")
        old, watch.CODEX = watch.CODEX, missing
        try:
            self.assertEqual(watch.codex("o/r", "1"), ("-", "-"))
        finally:
            watch.CODEX = old


GH_STUB = """#!/usr/bin/env python3
import json, os, sys
table = json.load(open(os.environ["GH_STUB"]))
args = sys.argv[1:]
answer = table.get(" ".join(args[:3] if args[:2] == ["pr", "view"] else args[:2]))
if answer is None:
    sys.stderr.write("stub gh: no answer for " + " ".join(args))
    sys.exit(1)
print(json.dumps(answer))
"""
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}


def view(state="OPEN", draft=False, checks="SUCCESS", mergeable="MERGEABLE"):
    return {"state": state, "isDraft": draft, "mergeable": mergeable, "headRefOid": "a" * 40,
            "statusCheckRollup": [{"conclusion": checks}], "title": "feat: x"}


class TasksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "bin").mkdir()
        stub = self.root / "bin/gh"
        stub.write_text(GH_STUB)
        stub.chmod(0o755)
        self.repo = self.root / "repo"
        self.workflow = self.repo / "docs/dev2"
        self.state = self.workflow / ".spacedock-state"
        self.state.mkdir(parents=True)
        self.git(self.repo, "init", "-q", "-b", "main")
        self.git(self.state, "init", "-q", "-b", "main")
        (self.state / "README.md").write_text("state\n")
        self.watch = self.root / "watch.json"

    def git(self, where, *args):
        done = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True, env={**os.environ, **IDENTITY})
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def readme(self, extensions):
        (self.workflow / "README.md").write_text(f"---\nentity-type: task\nextensions: [{extensions}]\nstate: .spacedock-state\n---\n")

    def task(self, slug, pr="", worktree=True, branch="feat-x", status="validation", folder=False):
        where = self.repo / ".worktrees" / slug
        if worktree and not where.exists():
            where.mkdir(parents=True)
            self.git(where, "init", "-q", "-b", branch)
            self.git(where, "remote", "add", "origin", "https://github.com/o/r.git")
        lines = ["---", f"title: {slug}", f"status: {status}", f"pr: {pr}"] + ([f"worktree: .worktrees/{slug}"] if worktree else []) + ["---", "body"]
        target = self.state / (f"{slug}/index.md" if folder else f"{slug}.md")
        target.parent.mkdir(exist_ok=True)
        target.write_text("\n".join(lines) + "\n")
        self.git(self.state, "add", "-A")
        self.git(self.state, "commit", "-qm", f"task {slug}")

    def report(self, slug, text="ok | rule: x\n"):
        (self.state / slug).mkdir(exist_ok=True)
        (self.state / slug / "observer.md").write_text(text)
        self.git(self.state, "add", "-A")
        self.git(self.state, "commit", "-qm", "report")

    def tasks(self, answers, look=None, clock=None):
        table = self.root / "gh.json"
        table.write_text(json.dumps({"repo view": {"nameWithOwner": "o/r"}, **answers}))
        env = {"PATH": f"{self.root / 'bin'}{os.pathsep}{os.environ['PATH']}", "GH_STUB": str(table)}
        out = io.StringIO()
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(out):
            code = watch.main(["--state", str(self.watch), "tasks", str(self.workflow)], **({"look": look} if look else {}), **({"clock": clock} if clock else {}))
        return code, out.getvalue().splitlines()

    def watched(self):
        return json.loads(self.watch.read_text()) if self.watch.exists() else {}

    def test_a_pr_a_worker_opened_is_recorded_with_two_commands_and_then_watched(self):
        self.readme("roborev")
        self.task("some-task")
        code, lines = self.tasks({"pr list": [{"number": 7, "state": "OPEN"}], "pr view 7": view()})
        self.assertEqual(code, 0, lines)
        self.assertEqual(lines[0], f"next: run `spacedock status --workflow-dir {self.workflow.resolve()} --set some-task pr=o/r#7`.")
        self.assertEqual(lines[1], f"next: run `spacedock state commit some-task --workflow-dir {self.workflow.resolve()}`.")
        self.assertEqual(list(self.watched()), ["o/r#7"])

    def test_a_branch_whose_only_pr_is_closed_records_nothing(self):
        self.readme("roborev")
        self.task("some-task")
        code, lines = self.tasks({"pr list": [{"number": 7, "state": "CLOSED"}], "pr view 7": view("CLOSED")})
        self.assertEqual((code, lines, self.watched()), (0, [], {}))
        code, lines = self.tasks({"pr list": [{"number": 8, "state": "OPEN"}, {"number": 7, "state": "CLOSED"}], "pr view 8": view()})
        self.assertIn("pr=o/r#8", lines[0])

    def test_a_merged_task_pr_without_a_report_is_kept_out_of_pr_merge_and_shows_the_observer_steps(self):
        self.readme("roborev, learn")
        self.task("some-task", pr="o/r#7")
        code, lines = self.tasks({"pr view 7": view("MERGED")})
        self.assertEqual(code, 0, lines)
        self.assertEqual(lines[0], "next: keep some-task out of pr-merge's scan in this pass.")
        self.assertTrue(lines[1].startswith("observer report not committed: some-task/observer.md"), lines)
        self.assertEqual(lines[-1], "next: run the idle hooks again.")
        self.assertFalse(any("let pr-merge" in line for line in lines))

    def test_a_merged_task_pr_with_the_report_committed_lets_pr_merge_record_it_and_names_the_steps_after(self):
        self.readme("learn")
        self.task("some-task", pr="o/r#7")
        self.report("some-task")
        code, lines = self.tasks({"pr view 7": view("MERGED")})
        self.assertEqual(code, 0, lines)
        self.assertEqual(lines[0], "next: let pr-merge record some-task.")
        self.assertEqual(len(lines), 3, lines)
        self.assertRegex(lines[1], r"^after pr-merge: run `python3 \S+observer_check\.py \S+ some-task`\.$")
        self.assertEqual(lines[2], "after pr-merge: do each next: line it prints.")
        command = lines[1].split("`")[1].split()
        done = subprocess.run(command, capture_output=True, text=True, env={**os.environ, **IDENTITY})
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_without_learn_listed_a_merged_pr_prints_no_observer_line(self):
        self.readme("roborev, codex")
        self.task("some-task", pr="o/r#7")
        self.assertEqual(self.tasks({"pr view 7": view("MERGED")}), (0, []))

    def test_codex_and_copilot_are_added_with_their_watch_columns_only_when_listed(self):
        self.task("some-task", pr="o/r#7")
        for listed, expected in (("codex, copilot", (True, True)), ("codex", (True, False)), ("roborev", (False, False))):
            with self.subTest(listed=listed):
                self.watch.unlink(missing_ok=True)
                self.readme(listed)

                def fake(ref, with_codex=False, with_copilot=False, **kw):
                    return {**snap(), "watch-codex": with_codex, "watch-copilot": with_copilot}
                self.tasks({}, look=fake)
                entry = self.watched()["o/r#7"]
                self.assertEqual((entry["watch-codex"], entry["watch-copilot"]), expected)

    def unchecked(self, now, merge_state="CLEAN", head="a", **view_kw):
        read = {**view(**view_kw), "statusCheckRollup": [], "mergeStateStatus": merge_state, "headRefOid": head * 40}
        return self.tasks({"pr view 7": read}, clock=lambda: now)

    GATE = ("delivery_gate.py", "do not ask", "merge ask")

    def settled(self, lines):
        return any("unchecked=settled" in line for line in lines if line.startswith("fact:"))

    def ready_lines(self, lines):
        return [line for line in lines if "mark o/r#7" in line]

    def test_a_pr_with_no_check_runs_settles_only_after_sixty_quiet_seconds(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        self.assertFalse(self.settled(self.unchecked(1000)[1]))
        self.assertFalse(self.settled(self.unchecked(1059)[1]))
        code, lines = self.unchecked(1060)
        self.assertEqual(code, 0, lines)
        self.assertTrue(self.settled(lines), lines)
        self.assertEqual(self.watched()["o/r#7"]["unchecked"], "settled")

    def test_a_draft_with_no_check_runs_is_marked_ready_after_sixty_quiet_seconds(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        self.unchecked(1000, draft=True)
        self.assertEqual(self.ready_lines(self.unchecked(1059, draft=True)[1]), [])
        self.assertEqual(self.ready_lines(self.unchecked(1060, draft=True)[1]), ["next: mark o/r#7 ready if Delivery authority allows."])

    def test_a_blocked_pr_with_no_check_runs_does_not_settle_until_it_is_not_blocked(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        self.unchecked(1000, merge_state="BLOCKED")
        self.assertFalse(self.settled(self.unchecked(1100, merge_state="BLOCKED")[1]))
        self.assertTrue(self.settled(self.unchecked(1101, merge_state="CLEAN")[1]))

    def test_a_new_head_or_a_ready_flip_restarts_the_quiet_sixty_seconds(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        self.unchecked(1000, draft=True)
        self.assertFalse(self.settled(self.unchecked(1060, draft=False)[1]))
        self.assertFalse(self.settled(self.unchecked(1119, draft=False)[1]))
        self.assertTrue(self.settled(self.unchecked(1120, draft=False)[1]))
        self.assertFalse(self.settled(self.unchecked(1180, head="b")[1]))
        self.assertFalse(self.settled(self.unchecked(1239, head="b")[1]))
        self.assertTrue(self.settled(self.unchecked(1240, head="b")[1]))

    def test_an_open_pr_prints_its_facts_and_the_kept_step_then_keeps_one_wait_running(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        cases = (
            (view(draft=True), "fact: o/r#7 OPEN draft=True checks=green", ["next: mark o/r#7 ready if Delivery authority allows."]),
            (view(), "fact: o/r#7 OPEN draft=False checks=green", []),
            (view(checks="FAILURE"), "fact: o/r#7 OPEN draft=False checks=failing", ["next: tell the Captain o/r#7 has failing CI."]),
            (view(mergeable="CONFLICTING"), "fact: o/r#7 OPEN draft=False checks=green", ["next: tell the Captain o/r#7 has a conflict."]),
            (view(checks="PENDING"), "fact: o/r#7 OPEN draft=False checks=pending", []),
        )
        for answer, fact, steps in cases:
            with self.subTest(fact=fact, steps=steps):
                code, lines = self.tasks({"pr view 7": answer})
                self.assertEqual(code, 0, lines)
                self.assertEqual(lines[:-2], [fact] + steps, lines)
                self.assertEqual(lines[-2], f"next: run `python3 {watch.SCRIPTS / 'pr_watch.py'} --state {self.watch} wait` in the background, unless one is running.")
                self.assertEqual(lines[-1], "next: when it exits, do the next: lines it prints.")

    def reviewed(self, **columns):
        def fake(ref, with_codex=False, with_copilot=False, **kw):
            return {**snap(**columns), "watch-codex": with_codex, "watch-copilot": with_copilot}
        return fake

    def test_no_snapshot_prints_a_merge_ask_or_hold_line(self):
        self.readme("codex, copilot")
        self.task("some-task", pr="o/r#7")
        cases = (dict(), dict(codex="clean", copilot="not-run"), dict(codex="running"), dict(codex="not-reviewed"), dict(codex="error"),
                 dict(copilot="requested"), dict(copilot="not-reviewed"), dict(copilot="error"),
                 dict(codex="findings", **{"codex-evidence": "review:1"}), dict(copilot="answered", **{"copilot-evidence": "review:2"}),
                 dict(checks="none"))
        for columns in cases:
            with self.subTest(columns=columns):
                self.watch.unlink(missing_ok=True)
                for now in (1000, 1060):
                    code, lines = self.tasks({}, look=self.reviewed(**columns), clock=lambda now=now: now)
                    self.assertEqual(code, 0, lines)
                    self.assertFalse([line for line in lines if any(word in line for word in self.GATE)], lines)

    def test_the_facts_line_names_each_listed_reviewer_outcome_with_its_review_id(self):
        self.readme("codex, copilot")
        self.task("some-task", pr="o/r#7")
        cases = ((dict(codex="findings", **{"codex-evidence": "review:5515174091"}), "fact: o/r#7 OPEN draft=False checks=green codex=findings review:5515174091 copilot=-"),
                 (dict(copilot="answered", **{"copilot-evidence": "review:2"}), "fact: o/r#7 OPEN draft=False checks=green codex=- copilot=answered review:2"),
                 (dict(codex="running", copilot="requested"), "fact: o/r#7 OPEN draft=False checks=green codex=running copilot=requested"))
        for columns, expected in cases:
            with self.subTest(columns=columns):
                self.watch.unlink(missing_ok=True)
                code, lines = self.tasks({}, look=self.reviewed(**columns))
                self.assertEqual(lines[0], expected, lines)

    def test_a_reviewer_the_readme_does_not_list_is_not_in_the_facts_line(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        code, lines = self.tasks({}, look=self.reviewed(codex="running", copilot="requested"))
        self.assertEqual(lines[0], "fact: o/r#7 OPEN draft=False checks=green", lines)

    def test_a_bare_pr_is_resolved_from_the_workflow_checkout_when_its_worktree_is_gone(self):
        self.readme("roborev")
        self.git(self.repo, "remote", "add", "origin", "https://github.com/o/r.git")
        for slug, pr in (("hash", "#7"), ("number", "7")):
            self.task(slug, pr=pr)
            shutil.rmtree(self.repo / ".worktrees" / slug)
        self.task("no-field", pr="#7", worktree=False)
        code, lines = self.tasks({"pr view 7": view()})
        self.assertEqual(code, 0, lines)
        self.assertEqual(list(self.watched()), ["o/r#7"])
        self.assertEqual(lines[0], "fact: o/r#7 OPEN draft=False checks=green", lines)

    def test_an_empty_pr_whose_worktree_is_gone_says_to_record_it_and_one_with_no_worktree_field_stays_silent(self):
        self.readme("roborev")
        self.task("gone")
        shutil.rmtree(self.repo / ".worktrees/gone")
        self.task("bare", worktree=False)
        code, lines = self.tasks({})
        self.assertEqual((code, lines), (0, ["next: record gone's PR with status --set gone pr=<owner/repo>#<N>; its worktree is not on this machine."]))

    def test_a_sentinel_and_a_task_without_a_pr_or_worktree_print_nothing(self):
        self.readme("learn")
        self.task("sentinel", pr="pr-merge:7")
        self.task("bare", worktree=False)
        self.task("qualified-without-worktree", pr="o/r#9", worktree=False)
        self.assertEqual(self.tasks({"pr view 9": view("CLOSED")}), (0, []))

    def test_a_pr_that_cannot_be_read_is_reported_and_exits_2(self):
        self.readme("learn")
        self.task("some-task", pr="o/r#7")
        self.task("other", pr="o/r#8")
        code, lines = self.tasks({"pr view 8": view("MERGED")})
        self.assertEqual(code, 2, lines)
        self.assertTrue(any(line.startswith("next: report some-task to the Captain: ") for line in lines), lines)
        self.assertTrue(any("keep other out of pr-merge's scan" in line for line in lines), lines)

    def test_a_task_filed_as_a_folder_index_is_read_like_a_flat_one(self):
        self.readme("roborev")
        self.task("some-task", folder=True)
        code, lines = self.tasks({"pr list": [{"number": 7, "state": "OPEN"}], "pr view 7": view()})
        self.assertEqual(code, 0, lines)
        self.assertEqual(lines[0], f"next: run `spacedock status --workflow-dir {self.workflow.resolve()} --set some-task pr=o/r#7`.")
        self.assertEqual(list(self.watched()), ["o/r#7"])

    def test_a_sidecar_folder_without_an_index_beside_a_flat_task_adds_no_second_scan(self):
        self.readme("roborev")
        self.task("some-task")
        self.report("some-task")
        (self.state / "some-task/dispatch").mkdir()
        (self.state / "some-task/dispatch/note.md").write_text("---\nstatus: x\npr: o/r#9\n---\n")
        code, lines = self.tasks({"pr list": [{"number": 7, "state": "OPEN"}], "pr view 7": view()})
        self.assertEqual(code, 0, lines)
        self.assertEqual(sum("--set some-task " in line for line in lines), 1, lines)
        self.assertEqual(list(self.watched()), ["o/r#7"])

    def test_a_task_in_both_forms_is_read_once_from_the_folder(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#8")
        self.task("some-task", pr="o/r#7", folder=True)
        code, lines = self.tasks({"pr view 7": view()})
        self.assertEqual(code, 0, lines)
        self.assertEqual(list(self.watched()), ["o/r#7"])
        self.assertEqual(sum(line.startswith("fact: ") for line in lines), 1, lines)

    def test_archived_hidden_and_mod_folders_are_not_tasks(self):
        self.readme("roborev")
        for reserved in ("_archive", "_mods", ".hidden"):
            self.task(reserved, pr="o/r#7", folder=True)
        self.assertEqual(self.tasks({"pr view 7": view()}), (0, []))
        self.assertEqual(self.watched(), {})

    def test_a_merged_folder_task_reaches_the_observer_check_under_its_folder_name(self):
        self.readme("learn")
        self.task("some-task", pr="o/r#7", folder=True)
        code, lines = self.tasks({"pr view 7": view("MERGED")})
        self.assertEqual(code, 0, lines)
        self.assertEqual(lines[0], "next: keep some-task out of pr-merge's scan in this pass.")
        self.assertTrue(lines[1].startswith("observer report not committed: some-task/observer.md"), lines)

    def record(self, slug, text, commit=True):
        path = self.state / slug / "dispatch" / "implementation-1.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        if commit:
            self.git(self.state, "add", "-A")
            self.git(self.state, "commit", "-qm", "record")
        return path

    def test_a_newest_record_naming_a_bare_script_prints_one_next_line_even_without_a_pr(self):
        self.readme("roborev")
        self.task("some-task", worktree=False)
        path = self.record("some-task", "## Checklist\n\nRun adr_lint.py and lint-skills.py, then adr_lint.py\n")
        code, lines = self.tasks({})
        self.assertEqual(code, 0, lines)
        self.assertEqual(len(lines), 1, lines)
        self.assertRegex(lines[0], rf"^next: some-task's newest dispatch record {re.escape(str(path.resolve()))} names adr_lint\.py, lint-skills\.py without a directory; ")
        self.assertLess(len(lines[0].split()), 50)

    def test_clean_or_absent_records_leave_the_output_as_it_was(self):
        self.readme("roborev")
        self.task("some-task", worktree=False)
        before = self.tasks({})
        self.record("some-task", "## Checklist\n\nRun /abs/pkg/scripts/adr_lint.py\n")
        self.assertEqual((before, self.tasks({})), ((0, []), (0, [])))

    def test_an_unreadable_state_with_a_dispatch_folder_is_reported_with_exit_2(self):
        self.readme("roborev")
        self.task("some-task", worktree=False)
        self.record("some-task", "## Checklist\n\nRun adr_lint.py\n", commit=False)
        shutil.rmtree(self.state / ".git")
        shutil.rmtree(self.repo / ".git")
        code, lines = self.tasks({})
        self.assertEqual(code, 2)
        self.assertRegex(lines[0], r"^next: report some-task to the Captain: .*git cannot read the dispatch records")

    def test_tasks_needs_one_workflow_directory(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(watch.main(["--state", str(self.watch), "tasks"]), 2)


class DefaultStateTests(unittest.TestCase):
    """No --state: each caller (FO session and its workers) keeps its own list under HOME."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.pending = {}
        self.sleeps = 0

    def stores(self):
        return self.home / ".local/state/kc-dev-flow-2"

    def call(self, session, *args, cwd=None, stop=False):
        out = io.StringIO()

        def look(ref, **kw):
            return self.pending[ref]

        def sleep(seconds):
            self.sleeps += 1
            if stop:
                raise StopIteration

        with mock.patch.dict(os.environ, {"HOME": str(self.home)}), contextlib.redirect_stdout(out), contextlib.ExitStack() as stack:
            if session is None:
                os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
            else:
                os.environ["CLAUDE_CODE_SESSION_ID"] = session
            if cwd:
                stack.enter_context(mock.patch("os.getcwd", return_value=str(cwd)))
            code = watch.main(list(args), look=look, sleep=sleep)
        return code, out.getvalue()

    def watch_both(self, ref=REF):
        self.pending[ref] = snap(checks="pending")
        for session in ("A", "B"):
            self.assertEqual(self.call(session, "add", ref)[0], 0)
        self.pending[ref] = snap(checks="green")

    def test_two_callers_watching_one_pr_each_see_a_change_the_other_already_read(self):
        self.watch_both()
        self.assertIn("o/r#1 feat: x: checks pending -> green", self.call("A", "wait", "1")[1])
        self.assertIn("o/r#1 feat: x: checks pending -> green", self.call("B", "check")[1])

    def test_a_waiting_caller_still_wakes_on_a_change_the_other_already_read(self):
        self.watch_both()
        self.call("A", "wait", "1")
        code, out = self.call("B", "wait", "1", stop=True)
        self.assertEqual(code, 0)
        self.assertIn("checks pending -> green", out)
        self.assertEqual(self.sleeps, 0)

    def test_one_sessions_wait_does_not_consume_another_sessions_pr(self):
        relay, mine = "spacedock-dev/subspace-relay#368", "iamcxa/kc-claude-plugins#643"
        self.pending.update({relay: snap(checks="pending"), mine: snap(checks="pending")})
        self.call("B", "add", relay)
        self.call("A", "add", mine)
        self.pending[relay] = snap(checks="green")
        self.assertNotIn("subspace-relay#368", self.call("A", "check")[1])
        self.assertNotIn("subspace-relay#368", (self.stores() / "pr-watch/A.json").read_text())
        self.assertIn("subspace-relay#368 feat: x: checks pending -> green", self.call("B", "wait", "1")[1])

    def test_the_default_file_is_keyed_by_session_id_else_by_working_directory(self):
        self.pending[REF] = snap()
        self.call("S", "add", REF)
        self.assertEqual(sorted(p.name for p in (self.stores() / "pr-watch").glob("*.json")), ["S.json"])
        one, two = Path(self.tmp.name, "one"), Path(self.tmp.name, "two")
        one.mkdir()
        two.mkdir()
        for where in (one, one, two):
            self.call(None, "add", REF, cwd=where)
        keyed = sorted(p.name for p in (self.stores() / "pr-watch").glob("cwd-*.json"))
        self.assertEqual(len(keyed), 2)
        self.assertTrue(all(re.fullmatch(r"cwd-[0-9a-f]{12}\.json", n) for n in keyed), keyed)

    def test_an_unusable_session_id_falls_to_the_working_directory_and_writes_nothing_outside(self):
        self.pending[REF] = snap()
        for bad in ("../x", "a/b", "", ".", "..", "-x", "a" * 129):
            with self.subTest(session=bad):
                self.call(bad, "add", REF)
        written = {p for p in self.home.rglob("*.json")}
        self.assertEqual({p.parent for p in written}, {self.stores() / "pr-watch"})
        self.assertTrue(all(p.name.startswith("cwd-") for p in written), written)

    def test_an_explicit_state_file_wins(self):
        self.pending[REF] = snap()
        chosen = Path(self.tmp.name, "chosen.json")
        self.call("S", "--state", str(chosen), "add", REF)
        self.assertTrue(chosen.exists())
        self.assertFalse((self.stores() / "pr-watch").exists())

    def test_the_old_shared_file_is_neither_read_nor_changed_and_a_new_caller_starts_empty(self):
        old = self.stores() / "pr-watch.json"
        old.parent.mkdir(parents=True)
        old.write_text(json.dumps({"x/y#1": snap(), "x/y#2": snap()}))
        before = old.read_bytes()
        self.pending.update({"x/y#1": snap(), "x/y#2": snap(), REF: snap()})
        self.assertEqual(self.call("S", "check")[1], "no change since the last look\n")
        self.call("S", "add", REF)
        out = self.call("S", "check")[1]
        self.assertIn(REF, out)
        self.assertNotIn("x/y#", out)
        self.assertEqual(old.read_bytes(), before)

    def test_tasks_refills_the_new_callers_list_and_prints_no_state_flag(self):
        tasks = TasksTests("test_a_pr_a_worker_opened_is_recorded_with_two_commands_and_then_watched")
        tasks.setUp()
        self.addCleanup(tasks.tmp.cleanup)
        old = self.stores() / "pr-watch.json"
        old.parent.mkdir(parents=True)
        old.write_text(json.dumps({"x/y#1": snap()}))
        before = old.read_bytes()
        tasks.readme("roborev")
        tasks.task("some-task", pr="o/r#7")
        table = tasks.root / "gh.json"
        table.write_text(json.dumps({"repo view": {"nameWithOwner": "o/r"}, "pr view 7": view()}))
        env = {"PATH": f"{tasks.root / 'bin'}{os.pathsep}{os.environ['PATH']}", "GH_STUB": str(table),
               "HOME": str(self.home), "CLAUDE_CODE_SESSION_ID": "S"}
        out = io.StringIO()
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(out):
            code = watch.main(["tasks", str(tasks.workflow)])
        lines = out.getvalue().splitlines()
        self.assertEqual(code, 0, lines)
        self.assertEqual(lines[0], "fact: o/r#7 OPEN draft=False checks=green")
        self.assertEqual(lines[-2], f"next: run `python3 {watch.SCRIPTS / 'pr_watch.py'} wait` in the background, unless one is running.")
        self.assertEqual(list(json.loads((self.stores() / "pr-watch/S.json").read_text())), ["o/r#7"])
        self.assertEqual(old.read_bytes(), before)


class WaitNextTests(unittest.TestCase):
    def wait(self, then, first=None, **flags):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                watch.main(["--state", str(state), "add", REF], look=lambda ref, **kw: snap(**(first or {})))
                code = watch.main(["--state", str(state), "wait", "1"], look=lambda ref, **kw: then, sleep=lambda s: None)
            self.assertEqual(code, 0)
            return [line for line in out.getvalue().splitlines() if line.startswith("next:")]

    def test_each_decisive_change_is_followed_by_the_step_it_calls_for(self):
        cases = {
            "merged": (snap(state="MERGED"), None, ["next: run the idle hooks now."]),
            "closed": (snap(state="CLOSED"), None, ["next: run the idle hooks now."]),
            "green draft": (snap(draft=True), dict(draft=True, checks="pending"), [f"next: mark {REF} ready if Delivery authority allows."]),
            "green and ready": (snap(), dict(checks="pending"), []),
            "failing": (snap(checks="failing"), None, [f"next: tell the Captain {REF} has failing CI."]),
            "conflict": (snap(mergeable="CONFLICTING"), None, [f"next: tell the Captain {REF} has a conflict."]),
            "codex": (snap(codex="findings", **{"codex-evidence": "review:1"}), None, ["next: read the codex round review:1 as FO steps: review findings say."]),
            "copilot": (snap(copilot="answered", **{"copilot-evidence": "review:2"}), None, ["next: read the copilot round review:2 as FO steps: review findings say."]),
        }
        for label, (then, first, expected) in cases.items():
            with self.subTest(label):
                self.assertEqual(self.wait(then, first), expected)

    def test_no_wait_exit_prints_a_merge_ask_or_hold_line(self):
        watched = {"watch-codex": True, "watch-copilot": True}
        cases = {
            "all clear": dict(codex="clean", copilot="not-run"),
            "codex running": dict(codex="running"),
            "codex not reviewed": dict(codex="not-reviewed"),
            "copilot requested": dict(copilot="requested"),
            "codex findings in the same sweep": dict(codex="findings", **{"codex-evidence": "review:1"}),
        }
        for label, columns in cases.items():
            with self.subTest(label):
                lines = self.wait(snap(**columns, **watched), dict(checks="pending", **watched))
                self.assertFalse([line for line in lines if "delivery_gate.py" in line or "do not ask" in line or "merge ask" in line], lines)

    def test_findings_and_green_in_one_sweep_print_the_review_step_once(self):
        watched = {"watch-codex": True}
        lines = self.wait(snap(codex="findings", **{"codex-evidence": "review:1"}, **watched), dict(checks="pending", **watched))
        self.assertEqual(lines, ["next: read the codex round review:1 as FO steps: review findings say."])

    def test_an_answered_copilot_is_the_review_step_even_when_the_codex_reader_is_absent(self):
        watched = {"watch-codex": True, "watch-copilot": True}
        lines = self.wait(snap(copilot="answered", **{"copilot-evidence": "review:2"}, **watched), dict(checks="pending", **watched))
        self.assertEqual(lines, ["next: read the copilot round review:2 as FO steps: review findings say."])

    def test_wait_ends_when_a_pr_with_no_check_runs_has_been_quiet_for_sixty_seconds(self):
        clock = iter([1000, 1000, 1030, 1030, 1060, 1060, 1060])
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                watch.main(["--state", str(state), "add", REF], look=lambda ref, **kw: snap(checks="none"), clock=lambda: next(clock))
                code = watch.main(["--state", str(state), "wait", "30"], look=lambda ref, **kw: snap(checks="none"),
                                  sleep=lambda s: None, clock=lambda: next(clock))
        self.assertEqual(code, 0)
        lines = out.getvalue().splitlines()
        self.assertIn(f"{REF} feat: x: unchecked - -> settled", lines)
        self.assertEqual([line for line in lines if line.startswith("next:")], [])

    def test_a_start_that_is_not_an_outcome_prints_no_next_line(self):
        class Stopped(Exception):
            pass

        def stop(seconds):
            raise Stopped

        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                watch.main(["--state", str(state), "add", REF], look=lambda ref, **kw: snap(checks="none"))
                with self.assertRaises(Stopped):
                    watch.main(["--state", str(state), "wait", "1"], look=lambda ref, **kw: snap(checks="pending"), sleep=stop)
            self.assertNotIn("next:", out.getvalue())


if __name__ == "__main__":
    unittest.main()
