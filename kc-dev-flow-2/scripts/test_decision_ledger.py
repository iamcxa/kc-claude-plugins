#!/usr/bin/env python3
import importlib.util
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "decision_ledger", Path(__file__).resolve().parent / "decision_ledger.py")
dl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dl)

TASK = """---
title: A sample task
status: done
gates:
    version: 1
    records:
        - id: gate:sample:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:sample-backlog-1
              briefing:
                id: briefing:sample:backlog:attempt-1:revision-1
                room-ref: ./sample/review/backlog/briefing-1
              resolution:
                type: Resolution
                by: person:captain
                at: "2026-10-01T01:00:00Z"
                decision: approve
                reason: 'Captain 2026-10-01: 「准」 — the FO''s proposal, wrapped
                    onto a second line'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:sample:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:sample-ideation-1
              briefing:
                room-ref: ./sample/review/ideation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-10-02T01:00:00Z"
                reason: superseded by a new cycle
            - id: gate-attempt:sample-ideation-2
              briefing:
                room-ref: ./sample/review/ideation/briefing-2
              resolution:
                type: Resolution
                by: person:captain
                at: "2026-10-03T01:00:00Z"
                decision: revise
                reason: 'Override: recommended option A; Captain chose option B; area: db'
        - id: gate:sample:validation
          stage: validation
          attempts:
            - id: gate-attempt:sample-validation-1
              briefing:
                room-ref: ./sample/review/validation/briefing-1
              resolution:
                type: Resolution
                by: agent:first-officer
                at: "2026-10-05T01:00:00Z"
                decision: approve
                reason: repair passed under the delivery grant
                conn:
                    quote: 照這樣修
                    source: 'Captain chat 2026-10-04, answering the FO''s proposal'
              application:
                target-stage: done
started: 2026-10-01T00:00:00Z
---

## FO alignment

Surfaces: ui, db

## Captain amendments

### Amendment 1 — 2026-10-04, chat
Captain: 「改一下」
"""


class BoundQuestionTests(unittest.TestCase):
    def test_whole_question_with_nested_brackets_and_whitespace(self):
        question = "決定：這批五張都用 Pilot，其中「婉拒要寫明」照三項範圍，可以嗎？"
        row = {"question": question, "reason": "Captain 「准」, answering 「" + question + "」; Override: none"}
        self.assertTrue(dl.quotes_bound_question(row))
        row["reason"] = row["reason"].replace("Pilot", "Pi\n lot").replace("這批", "這\t批")
        self.assertTrue(dl.quotes_bound_question(row))
        row["reason"] = "answering 「決定：這批五張都用 Pilot」"
        self.assertFalse(dl.quotes_bound_question(row))

    def test_missing_question_reason_or_answering_marker_does_not_match(self):
        for row in ({}, {"question": ""}, {"question": "Approve?"},
                    {"question": "Approve?", "reason": "Captain 「准」"},
                    {"question": "Approve?", "reason": "「Approve?」"},
                    {"question": "Approve? And merge.", "reason": "answering 「Approve?」"}):
            with self.subTest(row=row):
                self.assertFalse(dl.quotes_bound_question(row))


REASONS = {
    'gate-attempt:model-roster-question-needs-both-families-backlog-1': (
        'The Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering the batch 12 sitting 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」; approves Pilot, this outcome and these bounds, with the stated change.'),
    'gate-attempt:special-roles-follow-the-model-table-backlog-1': (
        'The Captain 「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 (chat, 2026-11-02), answering the batch 12 sitting 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」; approves Pilot, this outcome and these bounds, with the stated change.'),
    'gate-attempt:release-walk-due-trigger-ideation-1': (
        'The Captain 「可以」 (chat, 2026-11-03), answering 「決定：七張設計照建議進實作，但驗收到期提醒的 D7 改成『在 kc-journey-map 登記 journey-progress/v1，預算放寬為兩個 PR，kc-journey-map 那個先合併』，可以嗎？」; accepts every recommendation each design states for its decisions, with the stated change to release-walk-due-trigger D7.'),
    'gate-attempt:commissioned-by-names-spacedock-validation-1': (
        'Captain 「同意合併」 (chat, 2026-10-20, batch-4 sitting, question 18), after asking what the two declined points were and being shown both: approve validation and merge iamcxa/kc-claude-plugins#685 at head 187f93a534f4792f6d747288947e2e43af589ce8, as recommended.'),
}
OVERRIDE = "Override: recommended option A; Captain chose option B; area: model policy"


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name)
        (self.state / "_archive").mkdir()
        (self.state / "_archive" / "sample.md").write_text(TASK)
        (self.state / "README.md").write_text("---\nentity-type: task\n---\n")
        room = self.state / "_archive" / "sample" / "review" / "backlog" / "briefing-1"
        room.mkdir(parents=True)
        (room / "index.json").write_text(json.dumps({"question": "Admit the sample task?"}))
        self.rows = dl.ledger(self.state)

    def tearDown(self):
        self.tmp.cleanup()

    def test_every_resolution_and_withdrawal_is_a_row(self):
        self.assertEqual([(r["stage"], r["kind"]) for r in self.rows], [
            ("backlog", "resolution"), ("ideation", "withdrawal"),
            ("ideation", "resolution"), ("validation", "resolution")])
        self.assertTrue(all(r["archived"] and r["task"] == "sample" for r in self.rows))

    def test_wrapped_single_quoted_reason_is_folded_and_unescaped(self):
        self.assertEqual(self.rows[0]["reason"],
                         "Captain 2026-10-01: 「准」 — the FO's proposal, wrapped onto a second line")

    def test_question_comes_from_the_briefing_room(self):
        self.assertEqual(self.rows[0]["question"], "Admit the sample task?")
        self.assertIsNone(self.rows[2]["question"])

    def test_override_sets_area_and_others_fall_back_to_surfaces(self):
        self.assertEqual(self.rows[2]["override"],
                         {"rec": "option A", "chose": "option B", "area": "db"})
        self.assertEqual(self.rows[2]["area"], "db")
        self.assertEqual(self.rows[0]["area"], "ui, db")

    def test_delegated_decision_keeps_its_grant(self):
        fo = self.rows[3]
        self.assertEqual((fo["by"], fo["conn_quote"]), ("agent:first-officer", "照這樣修"))
        self.assertEqual(fo["conn_source"], "Captain chat 2026-10-04, answering the FO's proposal")
        self.assertIsNone(self.rows[0]["conn_quote"])

    def test_amendment_counts_only_against_earlier_rulings(self):
        self.assertEqual([r["amended_after"] for r in self.rows], [1, 1, 1, 0])

    def test_summary_counts_resolutions_per_area(self):
        s = dl.summary(self.rows)
        self.assertEqual(s["db"], {"rulings": 1, "captain": 1, "fo_delegated": 0,
                                   "overrides": 1, "followed": 0, "amended_after": 1})
        self.assertEqual(s["ui, db"]["fo_delegated"], 1)

    def test_missing_directory_is_a_usage_error(self):
        self.assertEqual(dl.main([str(self.state / "nope")]), 2)


    def test_followed_survives_the_ledger_and_summary(self):
        path = self.state / "_archive" / "sample.md"
        path.write_text(TASK.replace("onto a second line'", "onto a second line. Recommendation: followed'"))
        rows = dl.ledger(self.state)
        self.assertEqual([r["followed"] for r in rows], [True, False, False, False])
        self.assertEqual(dl.summary(rows)["ui, db"]["followed"], 1)

    def test_followed_without_colon_is_not_a_declaration(self):
        path = self.state / "_archive" / "sample.md"
        path.write_text(TASK.replace("onto a second line'", "onto a second line. Recommendation followed'"))
        self.assertFalse(any(r["followed"] for r in dl.ledger(self.state)))


class OpenAttemptReasonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.task = self.root / "sample.md"
        self.reason = self.root / "reason.txt"
        self.task.write_text(TASK.replace("              resolution:\n                type: Resolution\n                by: agent:first-officer", "              pending:\n                type: Resolution\n                by: agent:first-officer"))
        for stage, number, question in (("backlog", 1, "X"), ("ideation", 2, "X"), ("validation", 1, "Y")):
            room = self.root / f"sample/review/{stage}/briefing-{number}"
            room.mkdir(parents=True)
            (room / "index.json").write_text(json.dumps({"question": question}))

    def cli(self, quote="Y", extra=None):
        self.reason.write_text(f"Recommendation: followed; answering 「{quote}」")
        return subprocess.run([sys.executable, "-B", dl.__file__, "--reason", str(self.reason),
                               *(extra if extra is not None else ["--task", str(self.task)])],
                              capture_output=True, text=True)

    def test_only_the_open_attempts_question_passes(self):
        self.assertEqual((self.cli().returncode, self.cli().stdout), (0, "reason: followed\n"))
        run = self.cli("X")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertIn("reason: does not quote the bound question\nnext:", run.stdout)
        self.assertIn("sample/review/validation/briefing-1/index.json", run.stdout)

    def test_newer_resolved_attempt_does_not_replace_the_open_question(self):
        self.task.write_text(self.task.read_text().replace("              pending:", "              resolution:", 1)
                             .replace("              resolution:\n                type: Resolution\n                by: person:captain", "              pending:\n                type: Resolution\n                by: person:captain", 1))
        self.assertEqual(self.cli("X").returncode, 0)
        self.assertEqual(self.cli("Y").returncode, 1)

    def test_missing_task_zero_two_open_attempts_and_unreadable_room_are_exit_two(self):
        run = self.cli(extra=[])
        self.assertEqual(run.returncode, 2)
        self.assertIn("--task", run.stderr)
        original = self.task.read_text()
        for text in (TASK, original.replace("              withdrawal:", "              pending:")):
            self.task.write_text(text)
            run = self.cli()
            self.assertEqual(run.returncode, 2)
            self.assertIn(str(self.task), run.stderr)
        self.task.write_text(original)
        index = self.root / "sample/review/validation/briefing-1/index.json"
        for content in (None, "{", '{}', '[]', '{"question": 1}'):
            if content is None:
                index.unlink()
            else:
                index.write_text(content)
            run = self.cli()
            self.assertEqual(run.returncode, 2)
            self.assertIn(str(index), run.stderr)

    def test_folder_task_and_whitespace_ignored(self):
        self.task.rename(self.root / "sample/index.md")
        self.task = self.root / "sample/index.md"
        self.task.write_text(self.task.read_text().replace("./sample/", "./"))
        self.assertEqual(self.cli(" Y\n ", ["--task", str(self.task.parent)]).returncode, 0)


class ReasonTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "reason.txt"
        self.addCleanup(self.tmp.cleanup)
        self.task = self.path.parent / "sample.md"
        self.task.write_text(TASK.replace("              resolution:\n                type: Resolution\n                by: agent:first-officer", "              pending:\n                type: Resolution\n                by: agent:first-officer"))
        room = self.path.parent / "sample/review/validation/briefing-1"
        room.mkdir(parents=True)
        (room / "index.json").write_text('{"question": "Approve?"}')

    def check(self, reason):
        self.path.write_text(reason + ("; answering 「Approve?」" if reason.strip() else ""), encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = dl.main(["--reason", str(self.path), "--task", str(self.task)])
        return code, out.getvalue(), err.getvalue()

    def test_flagged_reasons_hold_and_pass_with_override(self):
        for attempt, reason in list(REASONS.items())[:3]:
            with self.subTest(attempt=attempt):
                code, out, _ = self.check(reason)
                self.assertEqual(code, 1)
                self.assertIn("missing declaration", out)
                self.assertEqual(out.count("next:"), 1)
                code, out, _ = self.check(reason + "\n" + OVERRIDE)
                self.assertEqual((code, out), (0, "reason: override (area: model policy)\n"))

    def test_agreement_needs_the_followed_declaration(self):
        reason = list(REASONS.values())[3]
        self.assertEqual(self.check(reason)[0], 1)
        self.assertEqual(self.check(reason + "\nRecommendation: followed")[:2],
                         (0, "reason: followed\n"))

    def test_followed_is_a_declaration_not_a_truth_check(self):
        for reason in REASONS.values():
            with self.subTest(reason=reason):
                self.assertEqual(self.check(reason + "\nRecommendation: followed")[0], 0)

    def test_both_declarations_hold(self):
        code, out, _ = self.check(OVERRIDE + "\nRecommendation: followed")
        self.assertEqual(code, 1)
        self.assertIn("both declarations", out)
        self.assertEqual(out.count("next:"), 1)

    def test_placeholder_recommendations_hold(self):
        for value in ("<option>", ".", "...", "…"):
            with self.subTest(value=value):
                self.assertEqual(self.check(OVERRIDE.replace("option A", value))[0], 1)

    def test_empty_and_unreadable_files_are_input_errors(self):
        for value in ("", " \n\t"):
            with self.subTest(value=value):
                self.assertEqual(self.check(value)[0], 2)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(dl.main(["--reason", str(self.path.parent / "missing"), "--task", str(self.task)]), 2)
            self.assertEqual(dl.main(["--reason", str(self.path.parent), "--task", str(self.task)]), 2)
            self.path.write_bytes(b"\xff")
            self.assertEqual(dl.main(["--reason", str(self.path), "--task", str(self.task)]), 2)

    def test_malformed_override_and_followed_typo_hold(self):
        for reason in ("Recommendation followed", "Override: recommended A; Captain chose B"):
            with self.subTest(reason=reason):
                self.assertEqual(self.check(reason)[0], 1)


if __name__ == "__main__":
    unittest.main()
