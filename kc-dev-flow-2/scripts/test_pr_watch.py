import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("pr_watch", Path(__file__).with_name("pr_watch.py"))
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)

REF = "o/r#1"


def snap(**kw):
    base = {"state": "OPEN", "draft": False, "mergeable": "MERGEABLE", "checks": "green",
            "head": "aaaaaaaaa", "title": "feat: x", "codex": "clean"}
    return {**base, **kw}


class PrWatchTests(unittest.TestCase):
    def run_main(self, args, looks, state):
        seq = iter(looks)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = watch.main(["--state", str(state), *args], look=lambda ref: next(seq), sleep=lambda s: None)
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

    def test_wait_on_an_empty_list_ends_and_a_bad_ref_is_a_configuration_error(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.assertIn("watch list is empty", self.run_main(["wait"], [], state)[1])
            self.assertEqual(self.run_main(["add", "not-a-ref"], [], state)[0], 2)

    def test_a_pr_that_cannot_be_read_stays_watched(self):
        def fail(ref):
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
        review = lambda repo, n: asked.append((repo, n)) or "findings"
        self.assertEqual(watch.look(REF, view=view("OPEN"), review=review)["codex"], "findings")
        self.assertEqual(watch.look(REF, view=view("MERGED"), review=review)["codex"], "-")
        self.assertEqual(asked, [("o/r", "1")])

    def test_codex_column_is_a_dash_without_the_sibling_reader(self):
        missing = Path(tempfile.gettempdir(), "no-such-codex-review.py")
        old, watch.CODEX = watch.CODEX, missing
        try:
            self.assertEqual(watch.codex("o/r", "1"), "-")
        finally:
            watch.CODEX = old


if __name__ == "__main__":
    unittest.main()
