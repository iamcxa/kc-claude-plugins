#!/usr/bin/env python3
"""Exercise timelines through real state commits, persisted asks and the CLI."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import task_timeline as tt


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="timeline-test-")
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name)
        self.git("init", "-q")
        self.task = self.state / "demo.md"
        self.task.write_text("---\ntitle: demo\nstatus: ideation\n---\n\n## Scope\n")

    def git(self, *args, env=None):
        return subprocess.run(["git", "-C", str(self.state), "-c", "user.name=Test",
                               "-c", "user.email=test@example.invalid", "-c", "core.hooksPath=/dev/null",
                               *args], env=env, text=True, capture_output=True, check=True).stdout

    def commit(self, subject, minute, committer=None):
        self.git("add", "--all")
        env = {**os.environ, "GIT_AUTHOR_DATE": self.stamp(minute),
               "GIT_COMMITTER_DATE": self.stamp(minute if committer is None else committer)}
        self.git("commit", "-qm", subject, env=env)

    @staticmethod
    def stamp(minute):
        return f"2026-01-01T{minute // 60:02}:{minute % 60:02}:00Z"

    def write(self, relative, text="record\n"):
        path = self.state / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def dispatch(self, stage, number, minute, entering=False, committer=None):
        self.write(f"demo/dispatch/{stage}-{number}.md")
        self.commit(f"dispatch: demo entering {stage}" if entering else "record repeat dispatch",
                    minute, committer)

    def gates(self, stage, attempts):
        lines = ["gates:", "    version: 1", "    records:", f"        - stage: {stage}", "          attempts:"]
        for number, kind, minute in attempts:
            lines += [f"            - id: gate-attempt:demo-{stage}-{number}"]
            if kind:
                key = "withdrawal" if kind == "withdrawn" else "resolution"
                lines += [f"              {key}:", f"                at: \"{self.stamp(minute)}\""]
                if key == "resolution":
                    lines += [f"                decision: {kind}"]
        self.task.write_text("---\ntitle: demo\nstatus: ideation\n" + "\n".join(lines) + "\n---\n")

    def room(self, stage, number, minute):
        self.write(f"demo/review/{stage}/briefing-{number}/index.json", "{}")
        self.commit("prepare gate", minute)

    def finish(self, minute):
        self.git("mv", "demo.md", "_archive/demo.md")
        if (self.state / "demo").exists():
            self.git("mv", "demo", "_archive/demo")
        self.task = self.state / "_archive/demo.md"
        self.commit("archive demo (merge guard)", minute)

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", tt.__file__, str(self.state), *args],
                              capture_output=True, text=True)

    def test_finished_boundaries_use_author_dates_even_after_rebase(self):
        (self.state / "_archive").mkdir()
        self.dispatch("ideation", 1, 10, entering=True, committer=100)
        self.dispatch("implementation", 1, 30, entering=True, committer=110)
        self.finish(60)
        run = self.cli("demo", "--json")
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["done"], self.stamp(60))
        self.assertEqual([(r["start"], r["end"], r["elapsed_min"]) for r in result["stages"]],
                         [(self.stamp(10), self.stamp(30), 20.0), (self.stamp(30), self.stamp(60), 30.0)])

    def test_repeat_without_entering_uses_highest_record_number_and_excludes_messages(self):
        self.dispatch("implementation", 1, 10, entering=True)
        self.dispatch("implementation", 3, 20)
        self.write("demo/dispatch/implementation-3-message-1.md")
        self.commit("follow-up message", 25)
        self.dispatch("validation", 1, 40, entering=True)
        row = tt.timeline(self.state, "demo")["stages"][0]
        self.assertEqual((row["dispatches"], row["repeat_dispatches"], row["dispatch_records"]), (3, 2, 2))
        self.assertEqual((row["end"], row["elapsed_min"]), (self.stamp(40), 30.0))

    def test_withdrawn_then_approved_gate_has_each_open_close_and_wait(self):
        self.dispatch("ideation", 1, 10, entering=True)
        self.room("ideation", 1, 20)
        self.room("ideation", 2, 30)
        self.gates("ideation", [(1, "withdrawn", 25), (2, "approve", 40)])
        self.commit("gate: record demo ideation approve", 40)
        self.dispatch("implementation", 1, 50, entering=True)
        result = tt.timeline(self.state, "demo")
        row = result["stages"][0]
        self.assertEqual([(a["opened"], a["closed"], a["outcome"]) for a in row["gate_attempts"]],
                         [(self.stamp(20), self.stamp(25), "withdrawn"),
                          (self.stamp(30), self.stamp(40), "approve")])
        self.assertEqual((row["before_gate_min"], row["captain_wait_min"], row["after_gate_min"]), (15.0, 15.0, 10.0))
        self.assertEqual((result["withdrawn_gate_attempts"], result["gate_revise_decisions"]), (1, 0))

    def test_repeated_stage_preserves_each_cycles_after_gate_time(self):
        (self.state / "_archive").mkdir()
        self.dispatch("validation", 1, 10, entering=True)
        self.room("validation", 1, 20)
        self.gates("validation", [(1, "revise", 30)])
        self.commit("gate: record demo validation revise", 30)
        self.dispatch("implementation", 1, 60, entering=True)
        self.dispatch("validation", 2, 80)
        self.room("validation", 2, 90)
        self.gates("validation", [(1, "revise", 30), (2, "approve", 100)])
        self.commit("gate: record demo validation approve", 100)
        self.finish(110)
        result = json.loads(self.cli("demo", "--json").stdout)
        row = next(r for r in result["stages"] if r["stage"] == "validation")
        self.assertEqual({key: row[key] for key in (
            "elapsed_min", "before_gate_min", "captain_wait_min", "after_gate_min")},
            {"elapsed_min": 80.0, "before_gate_min": 20.0,
             "captain_wait_min": 20.0, "after_gate_min": 40.0})

    def test_gate_only_stage_has_no_before_gate_minutes(self):
        self.room("backlog", 1, 0)
        self.room("backlog", 2, 10)
        self.gates("backlog", [(1, "withdrawn", 2), (2, "approve", 12)])
        self.commit("gate: record demo backlog approve", 12)
        row = tt.timeline(self.state, "demo")["stages"][0]
        self.assertEqual((row["before_gate_min"], row["captain_wait_min"], row["after_gate_min"]), (0.0, 4.0, 8.0))

    def test_gate_close_matches_attempt_number_even_with_missing_room(self):
        self.room("backlog", 2, 10)
        self.gates("backlog", [(1, "withdrawn", 2), (2, "revise", 12)])
        self.commit("gate close", 12)
        result = tt.timeline(self.state, "demo")
        self.assertEqual(result["stages"][0]["gate_attempts"][0]["closed"], self.stamp(12))
        self.assertEqual(result["gate_revise_decisions"], 1)

    def test_running_stage_minutes_reach_now(self):
        self.dispatch("implementation", 1, 10, entering=True)
        with patch.object(tt, "datetime", wraps=datetime) as clock:
            clock.now.return_value = tt.when(self.stamp(40))
            row = tt.timeline(self.state, "demo")["stages"][0]
        self.assertIsNone(row["end"])
        self.assertEqual(row["elapsed_min"], 30.0)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            tt.show({**tt.timeline(self.state, "demo"), "stages": [row]})
        self.assertIn("running  30.0 min", output.getvalue())

    def test_folder_form_archived_task_is_in_sweep(self):
        self.task.unlink()
        self.task = self.state / "_archive/demo/index.md"
        self.write("_archive/demo/index.md", "---\ntitle: demo\nstatus: done\n---\n")
        self.commit("advance: demo entering validation", 20)
        self.write("_archive/demo/result.txt")
        self.commit("archive demo", 30)
        self.assertEqual(tt.timeline(self.state, "demo")["stages"][0]["elapsed_min"], 10.0)
        run = self.cli("--all")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("archived tasks: 1; at least one stage timed: 1", run.stdout)

    def test_ask_cli_appends_utc_questions_and_rejects_empty_without_write(self):
        self.dispatch("ideation", 1, 0, entering=True)
        self.assertIsNone(tt.timeline(self.state, "demo")["asks_outside_gate"])
        before = datetime.now(timezone.utc).replace(microsecond=0)
        for question in ("May I continue?", "要先處理哪件事？"):
            run = self.cli("demo", "ask", question)
            self.assertEqual(run.returncode, 0, run.stderr)
        path = self.state / "demo/asks.jsonl"
        saved = path.read_bytes()
        self.assertEqual(self.cli("demo", "ask", "  ").returncode, 2)
        self.assertEqual(path.read_bytes(), saved)
        entries = [json.loads(line) for line in saved.decode().splitlines()]
        self.assertEqual([e["asked"] for e in entries], ["May I continue?", "要先處理哪件事？"])
        self.assertTrue(all(e["at"].endswith("Z") and before <= tt.when(e["at"]) <= datetime.now(timezone.utc) for e in entries))
        result = tt.timeline(self.state, "demo")
        self.assertEqual(result["asks_outside_gate"], 2)
        self.assertEqual(result["stages"][0]["asks_outside_gate"], 2)

    def test_asks_are_attributed_to_running_segment_with_boundary_on_next_stage(self):
        self.dispatch("ideation", 1, 10, entering=True)
        self.dispatch("implementation", 1, 30, entering=True)
        with contextlib.redirect_stdout(io.StringIO()):
            for minute in (5, 15, 30):
                tt.record_ask(self.state, "demo", f"question {minute}", tt.when(self.stamp(minute)))
        result = tt.timeline(self.state, "demo")
        self.assertEqual([r["asks_outside_gate"] for r in result["stages"]], [1, 1])
        self.assertEqual(len(result["unassigned_asks"]), 1)
        run = self.cli("demo")
        self.assertIn(f"{self.stamp(30)}: question 30", run.stdout)

    def test_sweep_reports_missing_stage_start_without_refusing(self):
        self.gates("validation", [(1, "approve", 10)])
        self.write("_archive/demo.md", self.task.read_text())
        self.task.unlink()
        self.commit("import legacy task", 0)
        run = self.cli("--all")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("no stage timed: demo", run.stdout)
        self.assertIn("stages without start: demo: validation", run.stdout)

    def test_unreadable_frontmatter_stops_sweep_with_error(self):
        self.task.unlink()
        self.write("_archive/demo.md", "---\ntitle: unclosed\n")
        self.commit("import broken task", 0)
        run = self.cli("--all")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("missing or unclosed frontmatter", run.stderr)


if __name__ == "__main__":
    unittest.main()
