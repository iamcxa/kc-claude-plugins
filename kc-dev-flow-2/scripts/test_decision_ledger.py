#!/usr/bin/env python3
import importlib.util
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
                                   "overrides": 1, "amended_after": 1})
        self.assertEqual(s["ui, db"]["fo_delegated"], 1)

    def test_missing_directory_is_a_usage_error(self):
        self.assertEqual(dl.main([str(self.state / "nope")]), 2)


if __name__ == "__main__":
    unittest.main()
