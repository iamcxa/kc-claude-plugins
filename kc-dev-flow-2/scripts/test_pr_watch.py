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

gate_spec = importlib.util.spec_from_file_location("delivery_gate", Path(__file__).with_name("delivery_gate.py"))
gate = importlib.util.module_from_spec(gate_spec)
gate_spec.loader.exec_module(gate)

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

    def test_the_codex_reader_names_an_unrecognized_comment_without_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            fake = Path(d, "codex_review.py")
            fake.write_text("print('not recognized on aaa: \"x\"; unrecognized=comment:31 at t')\nraise SystemExit(5)\n")
            old, watch.CODEX = watch.CODEX, fake
            try:
                self.assertEqual(watch.codex("o/r", "1"), ("unrecognized(comment:31)", "-"))
            finally:
                watch.CODEX = old
        self.assertFalse(watch.outcome("codex", "not-reviewed", "unrecognized(comment:31)"))

    def test_the_codex_reader_names_a_stalled_review_by_its_start_and_it_is_no_outcome(self):
        with tempfile.TemporaryDirectory() as d:
            fake = Path(d, "codex_review.py")
            fake.write_text("print('stalled: the Codex code review of aaa shows running with no update; stalled=2026-10-10T10:00:00Z')\nraise SystemExit(6)\n")
            old, watch.CODEX = watch.CODEX, fake
            try:
                self.assertEqual(watch.codex("o/r", "1"), ("stalled(2026-10-10T10:00:00Z)", "-"))
            finally:
                watch.CODEX = old
        self.assertFalse(watch.outcome("codex", "running", "stalled(2026-10-10T10:00:00Z)"))
        self.assertEqual(watch.facts(REF, snap(codex="stalled(t)", **{"watch-codex": True})), f"fact: {REF} OPEN draft=False checks=green codex=stalled(t)")

    def test_wait_asks_for_one_re_request_then_names_codex_unread_once_per_head(self):
        stalled = lambda since, head="aaaaaaaaa": snap(codex=f"stalled({since})", head=head, **{"watch-codex": True})
        clean = snap(codex="clean", **{"codex-evidence": "summary:5"})
        asks, unread = "next: comment `@codex review` on o/r#1 once", "codex not run: review stalled twice on aaaaaaaaa"
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            code, first, slept = self.wait_with_clock(state, [stalled("t1")] * 40, 60)
            self.assertEqual((code, slept), (0, 0))
            self.assertIn(asks, first)
            self.assertNotIn("stalled twice", first)
            code, again, slept = self.wait_with_clock(state, [stalled("t1")] * 2 + [clean], 60)
            self.assertNotIn(asks, again)
            self.assertNotIn("stalled twice", again)
            self.assertEqual(slept, 2)
            code, second, slept = self.wait_with_clock(state, [stalled("t2")] * 40, 60)
            self.assertIn(unread, second)
            self.assertIn("the Captain decides", second)
            self.assertNotIn(asks, second)
            code, third, slept = self.wait_with_clock(state, [stalled("t3")] * 2 + [clean], 60)
            self.assertNotIn("stalled twice", third)
            self.assertNotIn(asks, third)
            code, other, slept = self.wait_with_clock(state, [stalled("t4", "bbbbbbbbb")] * 40, 60)
            self.assertIn(asks, other)
            self.assertNotIn("stalled twice", other)
        mine = lambda text: [line for line in text.splitlines() if "codex=stalled(" in line or line.startswith("next:")]
        self.assertEqual((len(mine(first)), len(mine(second))), (2, 2))
        self.assertLessEqual(sum(len(line.split()) for line in mine(first)), 26)
        self.assertLessEqual(sum(len(line.split()) for line in mine(second)), 37)

    def test_a_stalled_review_gives_an_unread_line_the_gate_pattern_accepts(self):
        self.assertTrue(gate.NOT_RUN.search("codex not run: review stalled twice on abc123"))
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            looks = lambda since: [snap(codex=f"stalled({since})", **{"watch-codex": True})] * 40
            self.wait_with_clock(state, looks("t1"), 60)
            code, out, slept = self.wait_with_clock(state, looks("t2"), 60)
            self.assertTrue(gate.NOT_RUN.search(out))
            self.assertNotIn("evidence=", out)

    def wait_with_clock(self, state, looks, step):
        seq, now, slept = iter(looks), [0], []
        def clock():
            return now[0]
        def sleep(seconds):
            slept.append(seconds)
            now[0] += step
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = watch.main(["--state", str(state), "wait", "60"], look=lambda ref, **kw: next(seq), sleep=sleep, clock=clock)
        return code, out.getvalue(), len(slept)

    def test_wait_gives_up_on_two_unrecognized_reads_three_minutes_apart_once_and_names_the_comment(self):
        odd = snap(codex="unrecognized(comment:31)", **{"watch-codex": True})
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            code, out, slept = self.wait_with_clock(state, [odd] * 40, 60)
            self.assertEqual((code, slept), (0, 3))
            self.assertIn("o/r#1 codex=unrecognized(comment:31): not recognized on two reads 180s apart", out)
            self.assertIn("gh api repos/o/r/issues/comments/31 --jq .body", out)
            self.assertIn("raw text", out)
            self.assertIn("never clean", out)
            self.assertIn("in the merge ask as Codex unread", out)
            self.assertIn("the Captain decides", out)
            self.assertIn("kc-dev-flow-2 problem, report it upstream", out)
            self.assertIn("`peers` is listed and a kc-dev-flow-2 maintainer FO is reachable, send it through `peers`", out)
            self.assertIn("otherwise draft the issue and ask the Captain whether to file it", out)
            code, out, slept = self.wait_with_clock(state, [odd] * 5 + [snap(codex="clean", **{"codex-evidence": "summary:5"})], 300)
            self.assertNotIn("report it upstream", out)
            self.assertIn("codex unrecognized(comment:31) -> clean", out)
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            code, out, slept = self.wait_with_clock(state, [odd] * 40, 300)
            self.assertEqual(slept, 1)
            self.assertIn("report it upstream", out)

    def test_the_upstream_line_has_the_package_repository_file_a_backlog_task_and_the_others_use_peers_or_an_issue(self):
        odd = snap(codex="unrecognized(comment:31)", **{"watch-codex": True})
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            code, out, slept = self.wait_with_clock(state, [odd] * 40, 60)
            line = [row for row in out.splitlines() if "report it upstream" in row]
            self.assertEqual(len(line), 1)
            self.assertIn("in the repository that holds kc-dev-flow-2 itself, file a backlog task; elsewhere, if `peers`", line[0])
            for part in ("file a backlog task", "`peers`", "draft the issue"):
                self.assertIn(part, line[0])
            self.assertLess(line[0].index("file a backlog task"), line[0].index("`peers`"))
            self.assertLess(line[0].index("`peers`"), line[0].index("draft the issue"))

    def test_a_recognized_verdict_before_the_second_read_wakes_wait_without_the_report(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            looks = [snap(codex="unrecognized(comment:31)")] * 2 + [snap(codex="clean", **{"codex-evidence": "summary:5"})]
            code, out, slept = self.wait_with_clock(state, looks, 60)
            self.assertIn("codex unrecognized(comment:31) -> clean", out)
            self.assertNotIn("report it upstream", out)

    def test_only_consecutive_unrecognized_reads_of_one_comment_count_and_silence_never_ends_a_wait(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            looks = [snap(codex="unrecognized(comment:31)"), snap(codex="unrecognized(comment:32)"),
                     snap(codex="unrecognized(comment:32)")]
            code, out, slept = self.wait_with_clock(state, looks, 300)
            self.assertEqual(slept, 2)
            self.assertIn("comment:32", out)
            self.assertNotIn("comment:31", out)
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            looks = [snap(codex="unrecognized(comment:31)"), snap(codex="running"),
                     snap(codex="unrecognized(comment:31)"), snap(mergeable="CONFLICTING")]
            code, out, slept = self.wait_with_clock(state, looks, 300)
            self.assertEqual(slept, 3)
            self.assertNotIn("report it upstream", out)
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            code, out, slept = self.wait_with_clock(state, [snap(codex="not-reviewed")] * 30 + [snap(mergeable="CONFLICTING")], 300)
            self.assertEqual(slept, 30)
            self.assertNotIn("report it upstream", out)

    def test_a_look_that_fails_is_not_a_second_unrecognized_read(self):
        odd = snap(codex="unrecognized(comment:31)")
        failed = RuntimeError("gh: api rate limit")

        def wait_through(state, looks):
            seq, now, slept = iter(looks), [0], []

            def look(ref, **kw):
                item = next(seq)
                if isinstance(item, Exception):
                    raise item
                return item

            def sleep(seconds):
                slept.append(seconds)
                now[0] += 60
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = watch.main(["--state", str(state), "wait", "60"], look=look, sleep=sleep, clock=lambda: now[0])
            return code, out.getvalue(), len(slept)
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            code, out, slept = wait_through(state, [odd, failed, failed, failed, snap(mergeable="CONFLICTING")])
            self.assertEqual(slept, 4)
            self.assertNotIn("report it upstream", out)
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, "w.json")
            self.run_main(["add", REF], [snap(codex="not-reviewed")], state)
            code, out, slept = wait_through(state, [odd, failed, failed, failed, odd])
            self.assertEqual(slept, 4)
            self.assertIn("o/r#1 codex=unrecognized(comment:31): not recognized on two reads 180s apart", out)

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
if args[:2] == ["api", "repos/o/r/pulls/7/comments"] and os.environ.get("GH_COMMENT_LOG"):
    open(os.environ["GH_COMMENT_LOG"], "a").write("read\\n")
answer = table.get(" ".join(args[:3] if args[:2] == ["pr", "view"] else args[:2]))
if answer is None:
    sys.stderr.write("stub gh: no answer for " + " ".join(args))
    sys.exit(1)
print(json.dumps(answer))
"""
SD_STUB = """#!/usr/bin/env python3
import os, sys
if sys.argv[1:] != ["status", "--workflow-dir", os.environ["SD_DIR"], "--next", "--json"]:
    sys.stderr.write("stub spacedock: unexpected " + " ".join(sys.argv[1:]))
    sys.exit(2)
if os.environ.get("SD_LOG"):
    open(os.environ["SD_LOG"], "a").write("call\\n")
text = open(os.environ["SD_NEXT"]).read()
if text == "FAIL":
    sys.stderr.write("stub spacedock: down")
    sys.exit(3)
print(text)
"""
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}


def view(state="OPEN", draft=False, checks="SUCCESS", mergeable="MERGEABLE"):
    return {"state": state, "isDraft": draft, "mergeable": mergeable, "headRefOid": "a" * 40,
            "statusCheckRollup": [{"conclusion": checks}], "title": "feat: x"}


# Sanitized path/PR manifest at state revision 1158adc584637bdbf1b2f347b91a4c63844d6c00.
ARCHIVE_MANIFEST = [['_archive/adr-protected-path-guard.md', 'pr-merge:712'],
 ['_archive/agent-reads-governing-adr.md', 'pr-merge:698'],
 ['_archive/amendment-form-check.md', 'pr-merge:650'],
 ['_archive/board-optout.md', 'pr-merge:543'],
 ['_archive/canvas-document-popup.md', 'pr-merge:468'],
 ['_archive/captain-question-load.md', 'pr-merge:675'],
 ['_archive/chat-only-evidence-observer-blind.md', 'pr-merge:679'],
 ['_archive/codex-reader-counts-code-review-only.md', 'pr-merge:702'],
 ['_archive/codex-reader-reads-receipt-marker.md', 'pr-merge:693'],
 ['_archive/codex-review-hang-detected.md', 'pr-merge:722'],
 ['_archive/codex-review-round3-followups.md', ''],
 ['_archive/commissioned-by-names-spacedock.md', 'pr-merge:685'],
 ['_archive/copilot-quota-refusal-is-not-a-review.md', 'pr-merge:630'],
 ['_archive/db-surface-without-migrations.md', 'pr-merge:686'],
 ['_archive/delivery-gate-candidate-followups.md', ''],
 ['_archive/delivery-gate-reads-folder-tasks.md', 'pr-merge:720'],
 ['_archive/delivery-gate-settles-skipped-checks-followups.md', ''],
 ['_archive/delivery-gate-settles-skipped-checks.md', 'pr-merge:680'],
 ['_archive/delivery-gate-verdict-form.md', 'pr-merge:647'],
 ['_archive/design-director-runs-ui-design-review.md', 'pr-merge:708'],
 ['_archive/dev2-laws-check.md', 'pr-merge:651'],
 ['_archive/dispatch-and-report-hygiene.md', 'pr-merge:535'],
 ['_archive/extension-defaults-and-install-choice.md', 'pr-merge:716'],
 ['_archive/extension-instruction-reaches-dispatch.md', 'pr-merge:652'],
 ['_archive/fo-batch-sittings.md', 'pr-merge:689'],
 ['_archive/fo-lifecycle-mod.md', 'pr-merge:643'],
 ['_archive/fo-record-checks.md', 'pr-merge:640'],
 ['_archive/fo-write-checks-followups.md', ''],
 ['_archive/fo-write-checks.md', 'pr-merge:671'],
 ['_archive/fo-write-rules-checked.md', 'pr-merge:687'],
 ['_archive/fo-written-lines-checked-before-dispatch.md', 'pr-merge:724'],
 ['_archive/followup-dispatch-records-checked.md', 'pr-merge:642'],
 ['_archive/followup-dispatch-records-round3-followups.md', ''],
 ['_archive/ideation-gaps.md', 'pr-merge:537'],
 ['_archive/idle-names-failing-seeds.md', 'pr-merge:694'],
 ['_archive/journey-map-dev2-contract.md', 'pr-merge:628'],
 ['_archive/journey-render-keeps-annotations.md', 'pr-merge:558'],
 ['_archive/kc-adr-format-source.md', 'pr-merge:710'],
 ['_archive/kc-adr-tools-with-dev2-copy.md', 'pr-merge:713'],
 ['_archive/kc-decision-log-cli.md', 'pr-merge:695'],
 ['_archive/kc-decision-log-p1/index.md', ''],
 ['_archive/laws-check-followups.md', ''],
 ['_archive/learn-delivery-follow-through.md', 'pr-merge:639'],
 ['_archive/learn-delivery-round3-followups.md', ''],
 ['_archive/learning-serialize-evaluation.md', 'pr-merge:473'],
 ['_archive/merge-ask-holds-missing-clauses.md', 'pr-merge:703'],
 ['_archive/merge-gatekeeper-followups.md', ''],
 ['_archive/merge-gatekeeper.md', 'pr-merge:666'],
 ['_archive/migration-and-number-guards.md', 'pr-merge:533'],
 ['_archive/names-check-before-dispatch.md', 'pr-merge:649'],
 ['_archive/new-work-starts-from-a-story-map.md', 'pr-merge:705'],
 ['_archive/number-guards-readme-shrink-followups.md', ''],
 ['_archive/number-guards-readme-shrink.md', 'pr-merge:670'],
 ['_archive/observer-before-merge-guard.md', 'pr-merge:632'],
 ['_archive/observer-check-round3-followups.md', ''],
 ['_archive/override-reaches-gate-and-criteria-wait.md', ''],
 ['_archive/patch-0102.md', 'pr-merge:549'],
 ['_archive/patch-0103.md', 'pr-merge:553'],
 ['_archive/poc-no-migrations.md', 'pr-merge:555'],
 ['_archive/pr-watch-round3-followups.md', ''],
 ['_archive/pr-watch-state-per-session.md', 'pr-merge:646'],
 ['_archive/pr-watch-tasks-round3-followups.md', ''],
 ['_archive/prod-security-review-gates.md', 'pr-merge:656'],
 ['_archive/prod-security-validation-gate-followups.md', ''],
 ['_archive/prod-security-validation-gate.md', 'pr-merge:659'],
 ['_archive/read-adr-reporting-rule-followup.md', 'pr-merge:706'],
 ['_archive/reflow-order.md', 'pr-merge:544'],
 ['_archive/release-acceptance/index.md', 'pr-merge:709'],
 ['_archive/release-please-exclude-paths.md', 'pr-merge:467'],
 ['_archive/release-review-staleness-held-at-dispatch.md', 'pr-merge:711'],
 ['_archive/release-review.md', 'pr-merge:540'],
 ['_archive/release-walk-picky-reviewers-and-director.md', 'pr-merge:714'],
 ['_archive/replay-control-arm-round3-followups.md', ''],
 ['_archive/review-cadence.md', 'pr-merge:536'],
 ['_archive/review-followups-0102.md', ''],
 ['_archive/role-triggers-owe-ce-on-review-drift.md', 'pr-merge:719'],
 ['_archive/special-role-calls-fire-when-needed.md', 'pr-merge:682'],
 ['_archive/special-role-triggers-followups.md', ''],
 ['_archive/special-role-triggers.md', 'pr-merge:664'],
 ['_archive/stage-report-correction-path.md', 'pr-merge:721'],
 ['_archive/ui-design-review-in-ideation.md', 'pr-merge:663'],
 ['_archive/ui-design-review-round3-followups.md', ''],
 ['_archive/worker-completion-goes-to-main.md', 'pr-merge:633'],
 ['_archive/worker-loads-declared-package.md', 'pr-merge:661'],
 ['_archive/workflow-budget-ratchet-followups.md', ''],
 ['_archive/workflow-budget-ratchet.md', 'pr-merge:658'],
 ['_archive/workflow-checkout-must-match-trunk-readme.md', 'pr-merge:631'],
 ['_archive/workflow-gaps-from-qnow-1270.md', '']]
ARCHIVE_JOB_KEYS = ['03768d7afea14ec480f55b049e7a8c5807dfcca54ee980adb4b58b1f62607247',
 '0519f142d8ce26351f82de8f6a1737e435f6f6833a2240d0f433227d1cf33c15',
 '08fcffef857b105eb2ce9a84e87250cfea604636f0a9764672fd2faeee12d3dc',
 '119eb47ef655b2d418c3968fecb24b73233d064e9b14062d6309a02fb43ff71a',
 '12af920036eed5d6d577773b877b42c697cef3b64de387346da66673f9f0b556',
 '197d9c21df78b3027a569e1bf660d539da864df18b0b7f22ed98764673cc04ce',
 '1c25da09e5c89306d382f4648ae49679102d5e36d816eed57b4d84800e821a24',
 '1dff94d268e11724aeb16a55beeac230dd77b29c93e92141207377e92966a0b8',
 '1fecd3653070ada6ea9f5128e6896334ca3d903f4d9479fc35926c42d09241ad',
 '229f31f6bcedba12c9b6dc9b4383239b154afcf292f33714d0715ac074fbc6a8',
 '25e51433345d9189e4443a8d8a66c8803e8e3f5e75f60aae4eb082dd0ed8b865',
 '275120f832382be70c21ab848312ce86d7d43226bbbeded67126ec44fd6e12b0',
 '28c47203d5ddc515c985658b9af36e93a618b07ab798a94975ec3e7f888d92b1',
 '294809442c66bb39baba36ad475526b2935671f0462766d26b74c5b9c1974fe7',
 '3d6a684bb18106c8add21026e71c2be3769be66feeafec598e39ed350d18b255',
 '3ddcc1a3f15a9da51b0b2596e6dce3a4f5cc10da0b47a317dafe2f95832cfdbb',
 '441fe280d07513b3bfa7c1cd29444490994538c6e7fe6202b76d177129a67303',
 '49a91123986e0bc6d7d4c1e20e88df598cb3d2c2719b191a514977d0617e8865',
 '4a1a751ff2ca64298bd17643e6d4f003ceddfd88a3d1477e11999a91a2588371',
 '525727f4a28a21f439db6aa14dd2b4569fe39680ed1c0254f962ae7d1d968a9e',
 '590050db5006bb295881d588f99c54f8dbdd75088d8a526414f73b2dc395cfaa',
 '5d9d53163b93e2a21c7054e7ec97a58334e8c72e393d1c70a8e921b087fa07b9',
 '5df3940db9be34289535af9ebd3b14e7a2fc7257e326f110cf842770ab81e96e',
 '7c9058e89ee59439423e240748c24e5693773de309e8015e374ef9a25074277c',
 '863804ad3c7ab702bb7c4b3eae3ac86ff6a063628dbfcf0419350863a8ad569f',
 '8b56b9c500211d3bfd7337f335944d2cb86e2424c44af42de3f37df4622fe4fc',
 '8bc3d55097b0142bdc4fe9ec22ac7765b187d60bcf167d50aa7d360ec7dd9322',
 '90dba82771bcf1ea1e635b503b6a2cff0afd575f2e3cd005e6885985c837a63d',
 '91a95ca9ead7f5feb1fbd33ff3cf883e77d5079e8e92a235a567489d4984d4bc',
 '92da235be7f7d7e06554be0903fd9c2fc9dd5708588c69c4820a82d112293937',
 'a22107a3d634a30e0fe25ab8bd82409f7d943841be697417087197caa3d23c5d',
 'a23d0a84798616cf1dc2a2b3ee4276eda6563f6222eb2e7774585a5795beee79',
 'ad929ab91b38657a02102a12f2c5c14f75e36934d8f83631ae5a94d9e65f04d5',
 'b183ebfaf87286e43c4c31b22611f8745450393f3315d28905609ec8c1338514',
 'b513bb7c0c5448c1a42943f81a3ce46ca0361ac482f258eee68da2c00c911115',
 'be495105d8e52dd6ff08e4c35a71d278934536d89f72533184b77ca86b123c19',
 'be609ffc0af1f8d10ce78f5404078db17304c867faa1337876800078e382b24f',
 'c0eba66706da2852f069b26704d2d06de62bf00fe3db04c7497251a4764b2939',
 'caa9b488ed7dcf10cd3f54d5f9268967102963d97e8cb5173bc0f416e96d338b',
 'cb9bfddbc8c1e236ad39ca3f27ca0d3df807c6910e3bd8b73673a8be687d2259',
 'cf7529a150be092197ebc6c22725a03faf94a8d5cb6ae317249ffcb41f85dd70',
 'd208c1e1e7801df668a41fa13f48bc83d6537d9964d7826eb831e553fded820e',
 'd761c4cc077d5ff46081cecb8b902443443a07f90040bdbc6fc5b402eafc4704',
 'd829872c2ba7e3e7ee8d4959f55d1447fe80038165a88731d5566dc460bf84b9',
 'dbe9895e1982889ac0e9781e3685df11aff26318e56b57273d36bee0be162bf9',
 'dc30682c6438230fc9667d7f20de96f0d7a528fc10a4479fc89def41917a0767',
 'e3f45b766abad5658438796705b45886afc2359d727024e92677b0c472ed8b68',
 'ea9e586dcefd513f3ffe44c1a357dfb2db603e75eae19278781b1f2adb348aa7',
 'ecce2c7e736707dfa1206327c6c783a42b6f79f1a1f83021aa072dcf40ccaf0a',
 'ed2d3ee114280792035b9f231a95202d61ce3360dddf3bc31a84955474b1d28e',
 'efee0619799d0c728a8fd9bd41ecc5fdcd97fbbfb4c8df6b326efa5c53c2b78a',
 'f365864cf47f1aaa6e3af779acbdb23f03795067ca45de283a4a362b19072b77',
 'f37c7420ecbbfbc662148641dc11f86d1df4abc1930c6a0c19288207e6840fbd']
BACKFILLED = ['codex-review-hang-detected',
 'delivery-gate-reads-folder-tasks',
 'design-director-runs-ui-design-review',
 'extension-defaults-and-install-choice',
 'fo-written-lines-checked-before-dispatch',
 'kc-adr-tools-with-dev2-copy',
 'release-acceptance',
 'release-review-staleness-held-at-dispatch',
 'release-walk-picky-reviewers-and-director',
 'role-triggers-owe-ce-on-review-drift',
 'stage-report-correction-path']


class TasksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "bin").mkdir()
        stub = self.root / "bin/gh"
        stub.write_text(GH_STUB)
        stub.chmod(0o755)
        sd = self.root / "bin/spacedock"
        sd.write_text(SD_STUB)
        sd.chmod(0o755)
        self.next = self.root / "next.json"
        self.next.write_text(json.dumps({"ready_gates": []}))
        self.repo = self.root / "repo"
        self.workflow = self.repo / "docs/dev2"
        self.state = self.workflow / ".spacedock-state"
        self.state.mkdir(parents=True)
        self.git(self.repo, "init", "-q", "-b", "main")
        self.git(self.state, "init", "-q", "-b", "main")
        (self.state / "README.md").write_text("state\n")
        self.watch = self.root / "watch.json"
        self.log_calls = False

    def git(self, where, *args):
        done = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True, env={**os.environ, **IDENTITY})
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def readme(self, extensions):
        (self.workflow / "README.md").write_text(f"---\nentity-type: task\nextensions: [{extensions}]\nstate: .spacedock-state\n---\n")

    def task(self, slug, pr="", worktree=True, branch="feat-x", status="validation", folder=False, body=b"body\n"):
        where = self.repo / ".worktrees" / slug
        if worktree and not where.exists():
            where.mkdir(parents=True)
            self.git(where, "init", "-q", "-b", branch)
            self.git(where, "remote", "add", "origin", "https://github.com/o/r.git")
        lines = ["---", f"title: {slug}", f"status: {status}", f"pr: {pr}"] + ([f"worktree: .worktrees/{slug}"] if worktree else []) + ["---"]
        target = self.state / (f"{slug}/index.md" if folder else f"{slug}.md")
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(("\n".join(lines) + "\n").encode() + body)
        self.git(self.state, "add", "-A")
        self.git(self.state, "commit", "-qm", f"task {slug}")

    def report(self, slug, text="ok | rule: x\n"):
        (self.state / slug).mkdir(exist_ok=True)
        (self.state / slug / "observer.md").write_text(text)
        self.git(self.state, "add", "-A")
        self.git(self.state, "commit", "-qm", "report")

    def sd_env(self):
        return {"SPACEDOCK_BIN": str(self.root / "bin/spacedock"), "SD_NEXT": str(self.next), "SD_DIR": str(self.workflow.resolve()),
                **({"SD_LOG": str(self.root / "sd.log")} if self.log_calls else {})}

    def gates(self, *rows):
        self.next.write_text(json.dumps({"ready_gates": [
            {"id": slug, "slug": slug, "current": stage, "readiness": readiness} for slug, stage, readiness in rows]}))

    def tasks(self, answers, look=None, clock=None):
        table = self.root / "gh.json"
        quiet = {f"api repos/o/r/pulls/{n}/comments": [[]] for n in (7, 8, 9)}
        table.write_text(json.dumps({"repo view": {"nameWithOwner": "o/r"}, **quiet, **answers}))
        env = {"PATH": f"{self.root / 'bin'}{os.pathsep}{os.environ['PATH']}", "GH_STUB": str(table), "GH_COMMENT_LOG": str(self.root / "comments.log"), **self.sd_env()}
        out = io.StringIO()
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(out):
            code = watch.main(["--state", str(self.watch), "tasks", str(self.workflow)], **({"look": look} if look else {}), **({"clock": clock} if clock else {}))
        return code, out.getvalue().splitlines()

    def watched(self):
        return json.loads(self.watch.read_text()) if self.watch.exists() else {}

    def archive(self, slug, pr="pr-merge:7", folder=False, commit=True, extra=""):
        path = self.state / "_archive" / (f"{slug}/index.md" if folder else f"{slug}.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nstatus: done\npr: {pr}\n{extra}---\n")
        if commit:
            self.git(self.state, "add", "_archive")
            self.git(self.state, "commit", "-qm", "archive fixture")
        return path

    def learn(self, *args):
        done = subprocess.run([sys.executable, "-B", str(watch.SCRIPTS / "learning.py"),
                               "--repo", str(self.repo), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return json.loads(done.stdout)

    def claim_archive(self, slug, **changes):
        value = {"schema_version": 1, "workflow": "docs/dev2", "task_id": slug,
                 "variant": "kc-dev-flow-2", "profile": "pilot", "closed": True, "merged": True,
                 "verdict": "passed", "learning_task": False, "closure_revision": "a" * 40,
                 "landed_revision": "b" * 40, "pr": "o/r#7", "evidence": ["fixture"],
                 "learning": [], "project_rules": [], **changes}
        pack = self.root / "pack.json"
        pack.write_text(json.dumps(value))
        return self.learn("claim", "--input", pack, "--owner", "fixture")

    def notice_run(self, notices):
        actual = subprocess.run
        calls = []
        def run(argv, **kw):
            if len(argv) > 1 and argv[1] == str(watch.SCRIPTS / "learning.py"):
                calls.append(argv)
                return subprocess.CompletedProcess(argv, 0, json.dumps(notices), "")
            return actual(argv, **kw)
        return calls, mock.patch.object(watch.subprocess, "run", side_effect=run)

    def test_archive_shapes_are_sorted_deduplicated_and_guarded(self):
        self.readme("learn")
        self.archive("z-flat")
        self.archive("a-folder", folder=True)
        self.archive("both", pr="o/r#9")
        self.archive("both", folder=True)
        self.archive(".hidden")
        self.archive("_mods", folder=True)
        self.archive("sidecar/observer")
        self.archive("pending", commit=False)
        code, lines = self.tasks({}, look=lambda *a, **k: self.fail("archive used live reader"))
        self.assertEqual((code, lines), (0, [f"next: run kc-dev-flow-2:learn for {s}."
                                           for s in ("a-folder", "both", "z-flat")]))
        self.assertFalse(self.watch.exists())
        self.assertFalse((self.repo / ".git/kc-dev-flow-2").exists())
        self.readme("")
        calls, patch = self.notice_run({"notices": []})
        with patch:
            self.assertEqual(self.tasks({}), (0, []))
        self.assertEqual(calls, [])

    def test_real_claim_completed_acknowledged_and_released_jobs_suppress_repeats(self):
        self.readme("learn")
        self.archive("one", extra="id: unrelated-id\n")
        expected = (0, ["next: run kc-dev-flow-2:learn for one."])
        before = self.git(self.state, "status", "--porcelain")
        state_bytes = {str(p.relative_to(self.state)): watch.hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in self.state.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.assertEqual(self.tasks({}), expected)
        self.assertEqual(self.tasks({}), expected)
        claim = self.claim_archive("one")
        home = self.repo / ".git/kc-dev-flow-2/learning"
        def snapshot():
            return {str(p.relative_to(home)): p.read_bytes() for p in home.rglob("*") if p.is_file()}
        pending = snapshot()
        self.assertEqual(self.tasks({}), (0, []))
        self.assertEqual(snapshot(), pending)
        result = self.root / "result.json"
        result.write_text(json.dumps({"schema_version": 1, "decisions": [
            {"action": "no-change", "entry": None, "reason": "fixture", "evidence": []}]}))
        self.learn("complete", "--job", claim["job"], "--token", claim["token"], "--result", result)
        self.assertEqual(self.tasks({}), (0, []))
        notice = self.learn("notices", "--all")["notices"][0]
        self.learn("ack", "--job", claim["job"], "--expected", notice["notice_digest"])
        self.assertEqual(self.learn("notices")["notices"], [])
        self.assertEqual(self.tasks({}), (0, []))
        self.assertEqual({str(p.relative_to(self.state)): watch.hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in self.state.rglob("*") if p.is_file() and ".git" not in p.parts}, state_bytes)
        self.archive("released")
        state_bytes = {str(p.relative_to(self.state)): watch.hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in self.state.rglob("*") if p.is_file() and ".git" not in p.parts}
        claim = self.claim_archive("released")
        result.write_text(json.dumps({"schema_version": 1, "decisions": [
            {"action": "add", "entry": {"Applicability": "fixture", "Practice": "fixture", "Evidence": "fixture"},
             "reason": "fixture", "evidence": ["fixture"]}]}))
        self.learn("complete", "--job", claim["job"], "--token", claim["token"], "--result", result)
        notice = next(n for n in self.learn("notices", "--all")["notices"] if n["job"] == claim["job"])
        self.learn("release", "--job", claim["job"], "--owner", "fixture", "--reason", "fixture settled",
                   "--expected", notice["notice_digest"])
        released = snapshot()
        self.assertEqual(self.tasks({}), (0, []))
        self.assertEqual(snapshot(), released)
        self.assertEqual(self.git(self.state, "status", "--porcelain"), before)
        self.assertEqual({str(p.relative_to(self.state)): watch.hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in self.state.rglob("*") if p.is_file() and ".git" not in p.parts}, state_bytes)
        self.assertFalse(self.watch.exists())
        other = self.repo / "docs/other"
        other.mkdir()
        (other / "README.md").write_text("---\nextensions: [learn]\nstate: ../dev2/.spacedock-state\n---\n")
        self.workflow = other
        self.assertEqual(self.tasks({}), (0, expected[1] + ["next: run kc-dev-flow-2:learn for released."]))

    def test_keyed_uncertain_notices_without_input_are_inspected_and_malformed_lists_hold(self):
        self.readme("learn")
        self.archive("one")
        key = watch.job_key({"workflow": "docs/dev2", "task_id": "one"})
        calls, patch = self.notice_run({"notices": [{"job": key, "state": "uncertain"}]})
        with patch:
            self.assertEqual(self.tasks({}), (0, [f"next: inspect learn job {key} for one; its record is uncertain."]))
        self.assertEqual(calls, [[sys.executable, str(watch.SCRIPTS / "learning.py"), "--repo",
                                 str(self.repo.resolve()), "notices", "--all"]])
        self.task("live", pr="o/r#8", worktree=False)
        for bad in ({}, {"notices": {}}, {"notices": [None]}, {"notices": [{"job": "bad"}]},
                    {"notices": [{"job": key, "state": "invalid"}]}):
            with self.subTest(bad=bad):
                _, patch = self.notice_run(bad)
                with patch:
                    code, lines = self.tasks({"pr view 8": view()})
                self.assertEqual(code, 2, lines)
                self.assertTrue(any(line.startswith("fact: o/r#8 OPEN") for line in lines), lines)
                self.assertTrue(any(line.startswith("next: report missing learn jobs to the Captain:") for line in lines), lines)
                self.assertFalse(any("run kc-dev-flow-2:learn" in line for line in lines), lines)

    def test_failed_notice_command_and_invalid_json_are_errors_never_absence(self):
        self.readme("learn")
        self.archive("one")
        actual = subprocess.run
        for status, stdout in ((1, "unreadable store"), (0, "not JSON")):
            def run(argv, **kw):
                if len(argv) > 1 and argv[1] == str(watch.SCRIPTS / "learning.py"):
                    return subprocess.CompletedProcess(argv, status, stdout, "")
                return actual(argv, **kw)
            with mock.patch.object(watch.subprocess, "run", side_effect=run):
                code, lines = self.tasks({})
            self.assertEqual(code, 2, lines)
            self.assertEqual(len(lines), 1, lines)
            self.assertTrue(lines[0].startswith("next: report missing learn jobs to the Captain:"))

    def test_inline_workflow_and_external_definition_and_missing_origin(self):
        self.readme("learn")
        self.archive("one")
        outside = self.root / "outside.md"
        outside.write_bytes((self.workflow / "README.md").read_bytes())
        (self.workflow / "README.md").unlink()
        (self.workflow / "README.md").symlink_to(outside)
        code, lines = self.tasks({})
        self.assertEqual(code, 2, lines)
        self.assertFalse(any("run kc-dev-flow-2:learn" in line for line in lines))
        (self.workflow / "README.md").unlink()
        self.readme("learn")
        linked = self.repo / "docs/linked"
        external = self.root / "external"
        external.mkdir()
        self.git(external, "init", "-q", "-b", "main")
        (external / "README.md").write_bytes((self.workflow / "README.md").read_bytes())
        (external / ".spacedock-state").symlink_to(self.state)
        linked.symlink_to(external, target_is_directory=True)
        original_workflow = self.workflow
        self.workflow = linked
        code, lines = self.tasks({})
        self.assertEqual(code, 2, lines)
        self.assertFalse(any("run kc-dev-flow-2:learn" in line for line in lines))
        self.workflow = original_workflow
        self.archive("bare", pr="7")
        code, lines = self.tasks({})
        self.assertEqual(code, 2, lines)
        self.assertIn("next: run kc-dev-flow-2:learn for one.", lines)
        self.assertTrue(any("report bare to the Captain:" in line for line in lines))
        inline = self.repo / "docs/inline"
        (inline / "_archive").mkdir(parents=True)
        (inline / "README.md").write_text("---\nextensions: [learn]\n---\n")
        (inline / "_archive/one.md").write_text("---\npr: pr-merge:7\n---\n")
        self.git(self.repo, "add", "docs/inline")
        self.git(self.repo, "commit", "-qm", "inline workflow")
        self.workflow = inline
        self.assertEqual(self.tasks({}), (0, ["next: run kc-dev-flow-2:learn for one."]))
        done = subprocess.run([sys.executable, "-B", str(watch.SCRIPTS / "pr_watch.py"),
                               "--state", str(self.watch), "tasks", str(inline)],
                              capture_output=True, text=True, env={**os.environ, **self.sd_env()})
        self.assertEqual((done.returncode, done.stdout), (0, "next: run kc-dev-flow-2:learn for one.\n"))

    def test_archive_provider_reads_only_state_and_preserves_qualified_repository(self):
        self.readme("learn")
        self.git(self.repo, "remote", "add", "origin", "https://github.com/o/r.git")
        for slug, pr in (("bare", "#7"), ("qualified", "else/where#8"), ("open", "o/r#9"),
                         ("closed", "o/r#10"), ("local", "local-merge:abc"), ("sentinel", "pr-merge:11"),
                         ("failure", "o/r#12")):
            self.archive(slug, pr)
        calls = []
        def ask(*args):
            calls.append(args)
            if args[:2] == ("repo", "view"):
                self.assertIn("https://github.com/o/r.git", args)
                return {"nameWithOwner": "o/r"}
            self.assertEqual(args[:2], ("pr", "view"))
            self.assertEqual(args[-2:], ("--json", "state"))
            if args[2] == "12":
                raise RuntimeError("provider unavailable")
            return {"state": {"7": "MERGED", "8": "MERGED", "9": "OPEN", "10": "CLOSED"}[args[2]]}
        with mock.patch.object(watch, "gh", side_effect=ask):
            out = io.StringIO()
            with mock.patch.dict(os.environ, self.sd_env()), contextlib.redirect_stdout(out):
                code = watch.main(["--state", str(self.watch), "tasks", str(self.workflow)], ask=ask,
                                  look=lambda *a, **k: self.fail("full archive review"))
        lines = out.getvalue().splitlines()
        self.assertEqual(code, 2, lines)
        self.assertEqual([s for s in lines if "run kc-dev-flow-2:learn" in s],
                         [f"next: run kc-dev-flow-2:learn for {s}." for s in ("bare", "qualified", "sentinel")])
        self.assertIn(("pr", "view", "8", "--repo", "else/where", "--json", "state"), calls)
        self.assertTrue(any("report failure to the Captain: provider unavailable" in s for s in lines))
        self.assertFalse(self.watch.exists())

    def test_committed_archive_snapshot_ignores_disk_changes_and_missing_archive_is_empty(self):
        self.readme("learn")
        self.task("empty", worktree=False)
        calls, patch = self.notice_run({"notices": []})
        with patch:
            self.assertEqual(self.tasks({}), (0, []))
        self.assertEqual(calls, [])
        path = self.archive("committed")
        path.write_text("---\npr: o/r#8\n---\n")
        self.archive("untracked", commit=False)
        self.assertEqual(self.tasks({}), (0, ["next: run kc-dev-flow-2:learn for committed."]))
        actual = watch.git
        def failed(*args):
            if "show" in args:
                raise RuntimeError("tracked blob unreadable")
            return actual(*args)
        with mock.patch.object(watch, "git", side_effect=failed):
            code, lines = self.tasks({})
        self.assertEqual(code, 2, lines)
        self.assertTrue(any("tracked blob unreadable" in s for s in lines))

    def test_frozen_archive_replay_recovers_all_eleven_and_suppresses_backfilled_jobs(self):
        self.readme("learn")
        for path, pr in ARCHIVE_MANIFEST:
            target = self.state / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"---\nstatus: done\npr: {pr}\n---\n")
        self.git(self.state, "add", "_archive")
        self.git(self.state, "commit", "-qm", "frozen 88-entity manifest")
        target_keys = {watch.job_key({"workflow": "docs/dev2", "task_id": s}) for s in BACKFILLED}
        self.assertEqual((len(ARCHIVE_MANIFEST), len(ARCHIVE_JOB_KEYS), len(target_keys)), (88, 53, 11))
        for backfilled in (False, True):
            notices = [{"job": k, "state": "completed", "unread": False} for k in ARCHIVE_JOB_KEYS
                       if backfilled or k not in target_keys]
            _, patch = self.notice_run({"notices": notices})
            with patch:
                code, lines = self.tasks({})
            self.assertEqual(code, 0, lines)
            for slug in BACKFILLED:
                self.assertEqual(f"next: run kc-dev-flow-2:learn for {slug}." in lines, not backfilled, slug)

    def test_ineligible_learn_hold_leaves_no_job_and_next_idle_repeats_the_name(self):
        self.readme("learn")
        self.archive("old-profile")
        line = "next: run kc-dev-flow-2:learn for old-profile."
        self.assertEqual(self.tasks({}), (0, [line]))
        self.assertEqual(self.claim_archive("old-profile", profile="legacy"),
                         {"state": "ineligible", "reasons": ["profile"]})
        self.assertEqual(self.learn("notices", "--all"), {"notices": []})
        self.assertEqual(self.tasks({}), (0, [line]))
        self.assertEqual(len(line.split()), 5)

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

    def test_peers_and_the_journey_extensions_add_no_line_while_a_pr_is_open(self):
        self.task("some-task", pr="o/r#7")
        outputs = []
        for listed in ("", "peers, journey-map, release-acceptance"):
            self.watch.unlink(missing_ok=True)
            self.readme(listed)
            outputs.append(self.tasks({"pr view 7": view()}))
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[0][0], 0)

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

    def fourth_repair(self, slug, extra="", archived=False, commit=True):
        reports = "".join(f"\n## Stage Report: implementation{suffix}\n\n- DONE: x\n" for suffix in ("", *(f" (cycle {n})" for n in (2, 3, 4, 5))))
        text = f"---\ntitle: {slug}\nstatus: validation\npr:\n---\n## FO alignment\n{extra}\n{reports}"
        target = self.state / ("_archive" if archived else "") / f"{slug}.md"
        target.parent.mkdir(exist_ok=True)
        target.write_text(text)
        if commit:
            self.git(self.state, "add", "-A")
            self.git(self.state, "commit", "-qm", "task")

    def test_a_live_task_owing_a_role_call_prints_the_line_until_it_is_recorded(self):
        self.readme("roborev")
        self.fourth_repair("some-task")
        code, lines = self.tasks({})
        self.assertEqual(code, 0, lines)
        self.assertEqual(len(lines), 1, lines)
        self.assertRegex(lines[0], r"^next: some-task has 4 repair passes; dispatch kc-dev-flow-2:chief-engineer ")
        self.assertLessEqual(len(lines[0].split()), 60)
        self.fourth_repair("some-task", extra="Reviewer: kc-dev-flow-2:chief-engineer not run: Captain ordered it")
        self.assertEqual(self.tasks({}), (0, []))

    def test_an_archived_task_owing_a_role_call_prints_nothing(self):
        self.readme("roborev")
        self.fourth_repair("some-task", archived=True)
        self.assertEqual(self.tasks({}), (0, []))

    def test_a_task_the_role_check_cannot_read_is_reported_with_exit_2(self):
        self.readme("roborev")
        self.fourth_repair("some-task", commit=False)
        code, lines = self.tasks({})
        self.assertEqual(code, 2)
        self.assertRegex(lines[0], r"^next: report some-task to the Captain: cannot tell whether a chief-engineer")

    def comments(self, *review_ids):
        page = [{"pull_request_review_id": rid} for rid in review_ids]
        return {"api repos/o/r/pulls/7/comments": [page[:1], page[1:]] if page else [[]]}

    def test_two_review_ids_with_inline_comments_on_an_open_task_pr_owe_chief_engineer(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        code, lines = self.tasks({"pr view 7": view(), **self.comments(11, 11, 12)})
        self.assertEqual(code, 0, lines)
        roles = [line for line in lines if "chief-engineer" in line]
        self.assertEqual(len(roles), 1, lines)
        self.assertRegex(roles[0], r"^next: some-task has 2 review rounds; dispatch kc-dev-flow-2:chief-engineer ")
        self.assertLessEqual(len(roles[0].split()), 60)

    def dated(self, *rounds):
        page = [{"pull_request_review_id": rid, "created_at": at} for rid, at in rounds]
        return {"api repos/o/r/pulls/7/comments": [page[:1], page[1:]]}

    def call_recorded(self, date):
        text = (self.state / "some-task.md").read_text() + f"## FO alignment\nReviewer: kc-dev-flow-2:chief-engineer opus {date} — q\n"
        (self.state / "some-task.md").write_text(text)
        self.git(self.state, "add", "-A")
        self.git(self.state, "commit", "-qm", "call")

    def test_a_call_older_than_the_newest_review_round_leaves_the_line_and_names_its_date(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        self.call_recorded("2026-10-23")
        rounds = self.dated((5636050872, "2026-10-24T01:13:27Z"), (5636392914, "2026-10-24T02:18:49Z"), (5636428225, "2026-10-24T02:30:30Z"))
        code, lines = self.tasks({"pr view 7": view(), **rounds})
        roles = [line for line in lines if "chief-engineer" in line]
        self.assertEqual((code, len(roles)), (0, 1), lines)
        self.assertRegex(roles[0], r"^next: some-task has 3 review rounds, the newest on 2026-10-24; dispatch kc-dev-flow-2:chief-engineer ")
        self.assertLessEqual(len(roles[0].split()), 56)
        self.assertEqual((self.root / "comments.log").read_text(), "read\n")
        self.call_recorded("2026-10-24")
        code, lines = self.tasks({"pr view 7": view(), **rounds})
        self.assertEqual((code, [line for line in lines if "chief-engineer" in line]), (0, []))

    def test_one_review_id_with_many_comments_and_no_comments_owe_nothing(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        for name, comments in (("one id, nine comments", self.comments(*[11] * 9)), ("no comments", self.comments())):
            with self.subTest(name):
                code, lines = self.tasks({"pr view 7": view(), **comments})
                self.assertEqual(code, 0, lines)
                self.assertFalse([line for line in lines if "chief-engineer" in line], lines)

    def test_a_recorded_call_clears_the_review_round_line(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        text = (self.state / "some-task.md").read_text() + "## FO alignment\nReviewer: kc-dev-flow-2:chief-engineer opus 2026-10-18 — q\n"
        (self.state / "some-task.md").write_text(text)
        self.git(self.state, "add", "-A")
        self.git(self.state, "commit", "-qm", "call")
        code, lines = self.tasks({"pr view 7": view(), **self.comments(11, 12)})
        self.assertEqual(code, 0, lines)
        self.assertFalse([line for line in lines if "chief-engineer" in line], lines)

    def test_a_merged_pr_is_not_read_for_review_rounds(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        code, lines = self.tasks({"pr view 7": view("MERGED"), "api repos/o/r/pulls/7/comments": None})
        self.assertEqual((code, [line for line in lines if "chief-engineer" in line]), (0, []))

    def test_a_failed_comment_read_is_reported_to_the_captain_with_exit_2(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        code, lines = self.tasks({"pr view 7": view(), "api repos/o/r/pulls/7/comments": None})
        self.assertEqual(code, 2)
        self.assertRegex(lines[0], r"^next: report some-task to the Captain: stub gh: no answer for api repos/o/r/pulls/7/comments")

    def test_a_task_without_a_pr_is_judged_without_review_rounds(self):
        self.readme("roborev")
        self.fourth_repair("some-task")
        code, lines = self.tasks({})
        self.assertEqual(code, 0, lines)
        self.assertIn("has 4 repair passes; dispatch kc-dev-flow-2:chief-engineer", lines[0])

    def sitting_lines(self, lines):
        return [line for line in lines if " await the Captain at " in line]

    def list_lines(self, lines):
        return [line for line in lines if line.startswith("next: before asking, list each open decision")]

    def test_gates_awaiting_the_captain_at_one_stage_print_one_sitting_line_naming_every_slug(self):
        self.readme("roborev")
        self.gates(("a", "ideation", "awaiting-captain"), ("b", "ideation", "awaiting-captain"), ("c", "ideation", "awaiting-captain"))
        code, lines = self.tasks({})
        self.assertEqual((code, len(lines)), (0, 2), lines)
        self.assertEqual(lines[0], "next: 3 gates await the Captain at ideation (a, b, c); unless already presented, "
                                   "present them in one message and record each with his one answer.")
        self.assertEqual(len(lines[0].split()), 26)
        self.assertEqual(lines[1], watch.LIST_LINE)
        self.assertEqual(len(lines[1].split()), 52)

    def test_one_awaiting_gate_prints_no_sitting_line(self):
        self.readme("roborev")
        self.gates(("a", "ideation", "awaiting-captain"), ("b", "validation", "awaiting-captain"))
        self.assertEqual(self.tasks({}), (0, []))

    def test_gates_still_needing_preparation_are_not_counted_in_a_sitting(self):
        self.readme("roborev")
        self.gates(*[(f"n{i}", "backlog", "needs-preparation") for i in range(15)],
                   ("a", "backlog", "awaiting-captain"), ("b", "backlog", "awaiting-captain"))
        code, lines = self.tasks({})
        self.assertEqual((len(self.sitting_lines(lines)), len(self.list_lines(lines))), (1, 1), lines)
        self.assertIn("2 gates await the Captain at backlog (a, b);", lines[0])
        self.assertNotIn("n0", lines[0])

    def test_each_stage_with_two_awaiting_gates_gets_its_own_line_and_only_validation_names_the_merge_order(self):
        self.readme("roborev")
        self.gates(("a", "ideation", "awaiting-captain"), ("b", "ideation", "awaiting-captain"),
                   ("c", "validation", "awaiting-captain"), ("d", "validation", "awaiting-captain"))
        code, lines = self.tasks({})
        self.assertEqual(code, 0, lines)
        self.assertEqual(len(lines), 4, lines)
        self.assertIn("at ideation (a, b);", lines[0])
        self.assertIn("at validation (c, d);", lines[2])
        self.assertEqual([lines[1], lines[3]], [watch.LIST_LINE] * 2)
        merge = "Name the merge order and each shared file from Batch overlap."
        self.assertEqual([line.endswith(merge) for line in (lines[0], lines[2])], [False, True])
        self.assertEqual([len(line.split()) for line in (lines[0], lines[2])], [25, 36])

    def test_the_line_grows_by_one_word_per_slug(self):
        self.readme("roborev")
        self.gates(*[(f"t{i}", "ideation", "awaiting-captain") for i in range(5)])
        code, lines = self.tasks({})
        self.assertEqual(len(lines[0].split()), 28, lines)

    def test_the_sitting_line_comes_before_the_wait_lines(self):
        self.readme("roborev")
        self.task("some-task", pr="o/r#7")
        self.gates(("a", "ideation", "awaiting-captain"), ("b", "ideation", "awaiting-captain"))
        code, lines = self.tasks({"pr view 7": view()})
        self.assertEqual(code, 0, lines)
        self.assertIn(" await the Captain at ideation", lines[-4])
        self.assertEqual(lines[-3], watch.LIST_LINE)
        self.assertTrue(lines[-2].startswith("next: run `python3 "), lines)

    def test_a_failed_or_misshapen_status_call_is_reported_to_the_captain_with_exit_2(self):
        self.readme("roborev")
        for name, body in (("exit 3", "FAIL"), ("no ready_gates", json.dumps({"dispatchable": []})),
                           ("a gate without a stage", json.dumps({"ready_gates": [{"slug": "a", "readiness": "awaiting-captain"}]})),
                           ("not json", "oops")):
            with self.subTest(name):
                self.next.write_text(body)
                code, lines = self.tasks({})
                self.assertEqual(code, 2, lines)
                self.assertEqual(len(lines), 1, lines)
                self.assertRegex(lines[0], r"^next: report the awaiting gates to the Captain: ")

    def test_a_missing_spacedock_executable_is_reported_to_the_captain_with_exit_2(self):
        self.readme("roborev")
        table = self.root / "gh.json"
        table.write_text("{}")
        env = {"GH_STUB": str(table), **self.sd_env(), "SPACEDOCK_BIN": str(self.root / "bin/absent")}
        out = io.StringIO()
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(out):
            code = watch.main(["--state", str(self.watch), "tasks", str(self.workflow)])
        self.assertEqual(code, 2)
        self.assertRegex(out.getvalue(), r"^next: report the awaiting gates to the Captain: ")

    def test_the_sitting_line_writes_no_file(self):
        self.readme("roborev")
        self.tasks({})

        def tree():
            return {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.gates(("a", "ideation", "awaiting-captain"), ("b", "ideation", "awaiting-captain"))
        before = tree()
        lines = self.tasks({})[1]
        self.assertEqual((len(self.sitting_lines(lines)), len(self.list_lines(lines))), (1, 1))
        self.assertEqual(tree(), before)

    def ideation_readme(self):
        (self.workflow / "README.md").write_text(
            "---\nentity-type: task\nextensions: [roborev]\nstate: .spacedock-state\nstages:\n  states:\n"
            "    - name: backlog\n    - name: ideation\n---\n")

    def backlog(self, slug, surfaces="none", visible="none", heading=True):
        record = f"## FO alignment\n\nSurfaces: {surfaces}\nVisible change: {visible}\n" if heading else "## Scope\n\nnothing\n"
        self.task(slug, status="backlog", worktree=False, body=record.encode())

    def seed_lines(self, lines):
        return [line for line in lines if line.startswith("next: the seed check fails")]

    def counting_seed(self):
        log = self.root / "seed.log"
        stub = self.root / "seed_stub.py"
        stub.write_text(f"import sys\nopen({str(log)!r}, 'a').write(sys.argv[-1] + '\\n')\nprint('stub: refused')\nsys.exit(1)\n")
        patch = mock.patch.object(watch, "SEED", stub)
        patch.start()
        self.addCleanup(patch.stop)
        return lambda: log.read_text().splitlines() if log.exists() else []

    def test_a_backlog_task_the_seed_check_refuses_is_named_in_one_line_and_an_accepted_one_is_not(self):
        self.ideation_readme()
        self.backlog("bad", visible="a change you can see")
        self.backlog("fine")
        self.gates(("bad", "backlog", "needs-preparation"), ("fine", "backlog", "needs-preparation"))
        code, lines = self.tasks({})
        self.assertEqual(code, 0, lines)
        self.assertEqual(len(lines), 1, lines)
        self.assertEqual(lines[0], "next: the seed check fails for these backlog tasks (bad); before preparing the gate of one, "
                                   f"fix its ## FO alignment and run `python3 {watch.SEED} check --seed <task>`.")
        self.assertEqual(len(lines[0].split()), 28)

    def test_the_seed_line_names_every_slug_once_one_word_each_and_writes_no_file(self):
        self.ideation_readme()
        slugs = [f"t{i}" for i in range(6)]
        for slug in slugs:
            self.backlog(slug, visible="shown")
        self.gates(*[(slug, "backlog", "needs-preparation") for slug in slugs])
        self.tasks({})

        def tree():
            return {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file() and ".git" not in p.parts}
        before = tree()
        code, lines = self.tasks({})
        self.assertEqual((code, len(lines)), (0, 1), lines)
        self.assertTrue(lines[0].startswith("next: the seed check fails for these backlog tasks (t0, t1, t2, t3, t4, t5); "), lines)
        self.assertEqual(len(lines[0].split()), 33)
        self.assertEqual(tree(), before)

    def test_a_record_with_no_profile_is_named_before_its_gate_is_prepared(self):
        self.ideation_readme()
        self.backlog("early", visible="shown")
        self.gates(("early", "backlog", "needs-preparation"))
        self.assertIn("(early)", self.tasks({})[1][0])

    def test_a_failing_record_is_not_named_from_another_readiness_stage_route_or_a_missing_file(self):
        runs = self.counting_seed()
        cases = (("approved-awaiting-advance", "backlog", "approved-awaiting-advance", True),
                 ("stage", "ideation", "needs-preparation", True),
                 ("no ideation stage in README", "backlog", "needs-preparation", False),
                 ("no task file", "backlog", "needs-preparation", True))
        for name, stage, readiness, ideation in cases:
            with self.subTest(name):
                (self.ideation_readme if ideation else lambda: self.readme("roborev"))()
                self.backlog(f"kept-{len(name)}")
                self.gates(("ghost" if name == "no task file" else f"kept-{len(name)}", stage, readiness))
                code, lines = self.tasks({})
                self.assertEqual((code, lines), (0, []))
                self.assertEqual(runs(), [])

    def test_a_task_with_no_alignment_section_is_not_named_and_the_seed_check_does_not_run_for_it(self):
        runs = self.counting_seed()
        self.ideation_readme()
        self.backlog("unseeded", heading=False)
        self.backlog("seeded")
        self.gates(("unseeded", "backlog", "needs-preparation"), ("seeded", "backlog", "needs-preparation"))
        code, lines = self.tasks({})
        self.assertEqual(code, 0, lines)
        self.assertIn("(seeded)", lines[0])
        self.assertNotIn("unseeded", lines[0])
        self.assertEqual([Path(r).name for r in runs()], ["seeded.md"])

    def test_tasks_makes_one_status_call_and_a_crash_in_the_seed_check_is_reported_beside_the_sitting_line(self):
        self.ideation_readme()
        self.backlog("broken")
        (self.state / "broken.md").write_bytes(b"---\nstatus: backlog\n---\n## FO alignment\n\xff\n")
        self.gates(("broken", "backlog", "needs-preparation"), ("a", "ideation", "awaiting-captain"), ("b", "ideation", "awaiting-captain"))
        self.log_calls = True
        code, lines = self.tasks({})
        self.assertEqual(code, 2, lines)
        self.assertEqual(len(self.sitting_lines(lines)), 1, lines)
        self.assertEqual(self.seed_lines(lines), [])
        self.assertEqual(len([line for line in lines if line.startswith("next: report broken to the Captain: ")]), 1, lines)
        self.assertEqual((self.root / "sd.log").read_text().splitlines(), ["call"])

    def test_the_seed_line_comes_after_the_sitting_line_and_before_the_wait_lines(self):
        self.ideation_readme()
        self.task("some-task", pr="o/r#7")
        self.backlog("bad", visible="shown")
        self.gates(("bad", "backlog", "needs-preparation"), ("a", "ideation", "awaiting-captain"), ("b", "ideation", "awaiting-captain"))
        code, lines = self.tasks({"pr view 7": view()})
        self.assertEqual(code, 0, lines)
        self.assertIn(" await the Captain at ideation", lines[-5])
        self.assertEqual(lines[-4], watch.LIST_LINE)
        self.assertTrue(lines[-3].startswith("next: the seed check fails"), lines)
        self.assertTrue(lines[-2].startswith("next: run `python3 "), lines)

    def test_a_failed_status_call_names_no_seed_task(self):
        self.ideation_readme()
        self.backlog("bad", visible="shown")
        self.next.write_text("FAIL")
        code, lines = self.tasks({})
        self.assertEqual(code, 2, lines)
        self.assertEqual(self.seed_lines(lines), [])

    R4_MARK = "Release: j/r4. Signal 1 (task filed into a release by the Captain's ruling).\n"

    def aligned(self, slug, lines, status="implementation", extra="journey: j\n", heading="## FO alignment"):
        body = f"\nbody\n\n{heading}\n\n{lines}Surfaces: none\n"
        target = self.state / f"{slug}.md"
        target.write_text(f"---\ntitle: {slug}\nstatus: {status}\n{extra}---\n{body}")
        self.git(self.state, "add", "-A")
        self.git(self.state, "commit", "-qm", f"task {slug}")

    def held_slugs(self):
        code, lines = self.tasks({})
        self.assertEqual(code, 0, lines)
        held = [line for line in lines if line.startswith("next: hold the first implementation dispatch of ")]
        self.assertLessEqual(len(held), 1, lines)
        return held[0].split(" of ", 1)[1].split(":", 1)[0].split(", ") if held else []

    def test_the_record_shape_of_a_release_changed_task_with_no_review_line_is_held_by_name(self):
        self.readme("roborev")
        self.aligned("r4", self.R4_MARK)
        code, lines = self.tasks({})
        self.assertEqual(code, 0, lines)
        self.assertEqual(lines, ["next: hold the first implementation dispatch of r4: each ## FO alignment marks a release changed by "
                                 "signal 1 or 2 with no Release review: line after it. Dispatch kc-journey-map's review-release, write its "
                                 "Release review: line (or Release review: not needed: <reason>) under ## FO alignment, then run this again."])
        self.assertEqual(len(lines[0].split()), 50)

    def test_only_a_documented_review_line_after_the_last_mark_clears_the_hold(self):
        self.readme("roborev")
        cleared = {
            "a later review at a commit": self.R4_MARK + "Release review: j/r4 at abc1234\n",
            "a later not-needed review": self.R4_MARK + "Release review: not needed: map unchanged\n",
            "a later review quoting a signal": self.R4_MARK + "Release review: j/r4 at abc1234 (covers signal 1)\n",
        }
        held = {
            "a review before the mark": "Release review: j/r4 at abc1234\n" + self.R4_MARK,
            "a review-looking line that is a mark": self.R4_MARK + "Release review: j/r4 changed (signal 2).\n",
            "a not-needed review with no reason": self.R4_MARK + "Release review: not needed:\n",
            "a review with no commit": self.R4_MARK + "Release review: j/r4 at\n",
            "a new mark after the review": self.R4_MARK + "Release review: j/r4 at abc1234\nSignal 2 (goal reworded).\n",
        }
        for index, (name, lines) in enumerate({**cleared, **held}.items()):
            self.aligned(f"c{index}", lines)
        got = self.held_slugs()
        for index, name in enumerate({**cleared, **held}):
            with self.subTest(name):
                self.assertEqual(f"c{index}" in got, name in held)

    def test_every_mark_form_seen_in_adopter_history_holds(self):
        self.readme("roborev")
        forms = [
            "Release: j/r4. Signal 1 (task filed).\n",
            "Release r4 marked changed (signal 1: new story membership).\n",
            "Release review: r4 is marked changed by signal 1 (admitted).\n",
            "Release review: j/r4 changed (signal 2).\n",
            "Release review: signal 1, new membership proposed.\n",
            "Release review: signal 1 \u2014 admitted into a story.\n",
            "marked changed: signal 1 (admitted) and signal 2 (goal reworded).\n",
        ]
        for index, text in enumerate(forms):
            self.aligned(f"f{index}", text)
        self.assertEqual(self.held_slugs(), [f"f{index}" for index in range(len(forms))])

    def test_a_task_outside_the_first_implementation_dispatch_or_with_no_mark_is_not_held(self):
        self.readme("roborev")
        self.aligned("backlog-task", self.R4_MARK, status="backlog")
        self.aligned("validation-task", self.R4_MARK, status="validation")
        self.aligned("worktree-task", self.R4_MARK, extra="journey: j\npr: o/r#7\nworktree: .worktrees/worktree-task\n")
        self.aligned("recorded", self.R4_MARK)
        self.record("recorded", "## Checklist\n\nnothing\n")
        self.aligned("no-section", self.R4_MARK, heading="## Scope")
        self.aligned("no-mark", "Needed at ideation: none.\n")
        self.aligned("later-signals", "Signal 3 (UAT failure).\nsignal 4 (batch checkpoint).\n")
        self.aligned("shorter", "Signals 12 and signal 10 are not marks.\n")
        (self.state / "other-heading.md").write_text(
            "---\ntitle: x\nstatus: implementation\n---\n## FO alignment\n\nSurfaces: none\n\n## Notes\n\n" + self.R4_MARK)
        self.git(self.state, "add", "-A")
        self.git(self.state, "commit", "-qm", "other heading")
        code, lines = self.tasks({"pr view 7": view()})
        self.assertEqual(code, 0, lines)
        self.assertEqual([line for line in lines if "hold the first implementation dispatch" in line], [])

    def test_the_hold_names_every_held_slug_in_one_line_after_the_seed_line_and_before_the_wait_lines(self):
        self.ideation_readme()
        self.task("some-task", pr="o/r#7")
        self.backlog("bad", visible="shown")
        self.aligned("one", self.R4_MARK)
        self.aligned("two", "Signal 2 (goal reworded).\n")
        self.gates(("bad", "backlog", "needs-preparation"))
        code, lines = self.tasks({"pr view 7": view()})
        self.assertEqual(code, 0, lines)
        self.assertTrue(lines[-4].startswith("next: the seed check fails"), lines)
        self.assertTrue(lines[-3].startswith("next: hold the first implementation dispatch of one, two: "), lines)
        self.assertTrue(lines[-2].startswith("next: run `python3 "), lines)
        self.assertEqual(len(lines[-3].split()), 51)

    def test_the_hold_still_prints_when_the_status_call_fails_and_writes_no_file(self):
        self.readme("roborev")
        self.aligned("r4", self.R4_MARK)
        self.tasks({})
        self.next.write_text("FAIL")

        def tree():
            return {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file() and ".git" not in p.parts}
        before = tree()
        code, lines = self.tasks({})
        self.assertEqual(code, 2, lines)
        self.assertEqual(len([line for line in lines if line.startswith("next: hold the first implementation dispatch of r4: ")]), 1, lines)
        self.assertEqual(len([line for line in lines if line.startswith("next: report the awaiting gates")]), 1, lines)
        self.assertEqual(tree(), before)

    def test_an_unreadable_task_file_is_reported_to_the_captain_beside_the_held_one(self):
        self.readme("roborev")
        self.aligned("r4", self.R4_MARK)
        line, errors = watch.holds([("ghost", self.state / "ghost.md"), ("r4", self.state / "r4.md")], self.state)
        self.assertEqual(len(errors), 1)
        self.assertRegex(errors[0], r"^next: report ghost to the Captain: ")
        self.assertTrue(line[0].startswith("next: hold the first implementation dispatch of r4: "), line)

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
        table.write_text(json.dumps({"repo view": {"nameWithOwner": "o/r"}, "pr view 7": view(),
                                     "api repos/o/r/pulls/7/comments": [[]]}))
        env = {"PATH": f"{tasks.root / 'bin'}{os.pathsep}{os.environ['PATH']}", "GH_STUB": str(table),
               "HOME": str(self.home), "CLAUDE_CODE_SESSION_ID": "S", **tasks.sd_env()}
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
