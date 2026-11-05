#!/usr/bin/env python3
import importlib.util
import contextlib
import io
import json
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


class ReasonTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "reason.txt"
        self.addCleanup(self.tmp.cleanup)

    def check(self, reason):
        self.path.write_text(reason, encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = dl.main(["--reason", str(self.path)])
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
            self.assertEqual(dl.main(["--reason", str(self.path.parent / "missing")]), 2)
            self.assertEqual(dl.main(["--reason", str(self.path.parent)]), 2)
            self.path.write_bytes(b"\xff")
            self.assertEqual(dl.main(["--reason", str(self.path)]), 2)

    def test_malformed_override_and_followed_typo_hold(self):
        for reason in ("Recommendation followed", "Override: recommended A; Captain chose B"):
            with self.subTest(reason=reason):
                self.assertEqual(self.check(reason)[0], 1)


if __name__ == "__main__":
    unittest.main()
