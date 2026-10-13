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


if __name__ == "__main__":
    unittest.main()
