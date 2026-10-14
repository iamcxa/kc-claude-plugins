import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
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

    def task(self, slug, pr="", worktree=True, branch="feat-x", status="validation"):
        where = self.repo / ".worktrees" / slug
        if worktree and not where.exists():
            where.mkdir(parents=True)
            self.git(where, "init", "-q", "-b", branch)
            self.git(where, "remote", "add", "origin", "https://github.com/o/r.git")
        lines = ["---", f"title: {slug}", f"status: {status}", f"pr: {pr}"] + ([f"worktree: .worktrees/{slug}"] if worktree else []) + ["---", "body"]
        (self.state / f"{slug}.md").write_text("\n".join(lines) + "\n")
        self.git(self.state, "add", "-A")
        self.git(self.state, "commit", "-qm", f"task {slug}")

    def report(self, slug, text="ok | rule: x\n"):
        (self.state / slug).mkdir(exist_ok=True)
        (self.state / slug / "observer.md").write_text(text)
        self.git(self.state, "add", "-A")
        self.git(self.state, "commit", "-qm", "report")

    def tasks(self, answers, look=None):
        table = self.root / "gh.json"
        table.write_text(json.dumps({"repo view": {"nameWithOwner": "o/r"}, **answers}))
        env = {"PATH": f"{self.root / 'bin'}{os.pathsep}{os.environ['PATH']}", "GH_STUB": str(table)}
        out = io.StringIO()
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(out):
            code = watch.main(["--state", str(self.watch), "tasks", str(self.workflow)], **({"look": look} if look else {}))
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

    def test_an_open_pr_prints_the_step_its_snapshot_calls_for_then_keeps_one_wait_running(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        task_file = str((self.state / "some-task.md").resolve())
        cases = (
            (view(draft=True), "next: mark o/r#7 ready if Delivery authority allows."),
            (view(), f"next: run `python3 {watch.SCRIPTS / 'delivery_gate.py'} check {task_file} --pr o/r#7 --text-file <merge ask>`."),
            (view(checks="FAILURE"), "next: tell the Captain o/r#7 has failing CI."),
            (view(mergeable="CONFLICTING"), "next: tell the Captain o/r#7 has a conflict."),
            (view(checks="PENDING"), None),
        )
        for answer, expected in cases:
            with self.subTest(expected=expected):
                code, lines = self.tasks({"pr view 7": answer})
                self.assertEqual(code, 0, lines)
                self.assertEqual(lines[:-2], [expected] if expected else [], lines)
                self.assertEqual(lines[-2], f"next: run `python3 {watch.SCRIPTS / 'pr_watch.py'} --state {self.watch} wait` in the background, unless one is running.")
                self.assertEqual(lines[-1], "next: when it exits, do the next: lines it prints.")

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

    def test_tasks_needs_one_workflow_directory(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(watch.main(["--state", str(self.watch), "tasks"]), 2)


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
        gate = f"next: run `python3 {watch.SCRIPTS / 'delivery_gate.py'} check <task file> --pr {REF} --text-file <merge ask>`."
        cases = {
            "merged": (snap(state="MERGED"), None, ["next: run the idle hooks now."]),
            "closed": (snap(state="CLOSED"), None, ["next: run the idle hooks now."]),
            "green draft": (snap(draft=True), dict(draft=True, checks="pending"), [f"next: mark {REF} ready if Delivery authority allows."]),
            "green and ready": (snap(), dict(checks="pending"), [gate]),
            "failing": (snap(checks="failing"), None, [f"next: tell the Captain {REF} has failing CI."]),
            "conflict": (snap(mergeable="CONFLICTING"), None, [f"next: tell the Captain {REF} has a conflict."]),
            "codex": (snap(codex="findings", **{"codex-evidence": "review:1"}), None, ["next: read the codex round as FO steps: review findings say."]),
            "copilot": (snap(copilot="answered", **{"copilot-evidence": "review:2"}), None, ["next: read the copilot round as FO steps: review findings say."]),
        }
        for label, (then, first, expected) in cases.items():
            with self.subTest(label):
                self.assertEqual(self.wait(then, first), expected)

    def test_a_start_that_is_not_an_outcome_prints_no_next_line(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                watch.main(["--state", str(state), "add", REF], look=lambda ref, **kw: snap(checks="none"))
                watch.main(["--state", str(state), "wait", "1"], look=lambda ref, **kw: snap(checks="pending"), sleep=lambda s: (_ for _ in ()).throw(StopIteration))
            self.assertNotIn("next:", out.getvalue())


if __name__ == "__main__":
    unittest.main()
