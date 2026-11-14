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
from datetime import datetime, timezone, timedelta
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
        self.assertEqual(row["rounds"], [dict(round=1, start=self.stamp(10), end=self.stamp(50),
                                             minutes=40.0, result="withdrawn, approve")])

    def test_three_design_dispatches_have_separate_times_and_results(self):
        (self.state / "_archive").mkdir()
        for number, start, outcome in ((1, 10, "withdrawn"), (2, 30, "revise"), (3, 60, "approve")):
            self.dispatch("ideation", number, start, entering=number == 1)
            self.room("ideation", number, start + 5)
            self.gates("ideation", [(n, kind, minute + 8) for n, minute, kind in
                       ((1, 10, "withdrawn"), (2, 30, "revise"), (3, 60, "approve")) if n <= number])
            self.commit(f"gate {number} {outcome}", start + 8)
        self.dispatch("implementation", 1, 90, entering=True)
        self.finish(100)
        row = json.loads(self.cli("demo", "--json").stdout)["stages"][0]
        self.assertEqual(row["dispatches"], 3)
        self.assertEqual(row["rounds"], [
            dict(round=1, start=self.stamp(10), end=self.stamp(30), minutes=20.0, result="withdrawn"),
            dict(round=2, start=self.stamp(30), end=self.stamp(60), minutes=30.0, result="revise"),
            dict(round=3, start=self.stamp(60), end=self.stamp(90), minutes=30.0, result="approve")])
        output = self.cli("demo").stdout
        for r in row["rounds"]:
            self.assertIn(f"round {r['round']}: {r['start']} -> {r['end']}  {r['minutes']} min; {r['result']}", output)

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
            run = self.cli("demo", "ask", question, "--holds", "task", "--by", "test FO")
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
                tt.record_ask(self.state, "demo", f"question {minute}", tt.when(self.stamp(minute)), holds="task", by="test FO")
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


    def ask(self, **fields):
        return tt.write_event(self.state, "demo", "ask", dict(asked="Proceed?", asked_at="now",
                              channel="chat", by="test FO", holds="acceptance", **fields))

    def event(self, event, key="demo#1", **fields):
        return tt.write_event(self.state, "demo", event, {"key": key, **fields})

    def test_contract_v2_six_events_and_revision_fields_persist(self):
        first = self.ask(options=[dict(id="yes", text="Proceed", effect="Start work")], recommend="yes",
                         approve_means="yes", tasks=["other"], refs=[dict(kind="file", ref="design.md", ready=False)])
        self.assertEqual((first["key"], first["v"], first["asked_at"]), ("demo#1", 1, first["at"]))
        self.event("reask", channel="review", briefing="briefing:one")
        self.event("revise", revision=2, asked="Proceed now?", holds="task", reason="New scope")
        self.event("answer", channel="review", revision=1, words=None, option=None, resolution="resolution:one")
        self.event("acted", what="Started work")
        second = self.ask()
        self.event("withdraw", key=second["key"], reason="No longer needed")
        entries = tt.read_asks(self.state / "demo/asks.jsonl")
        self.assertEqual([e["event"] for e in entries], ["ask", "reask", "revise", "answer", "acted", "ask", "withdraw"])
        q = tt.fold_question(entries[:5])
        self.assertEqual((q["state"], q["answer"]["option"], q["interruptions"]), ("done", "yes", 2))
        self.assertIsNone(q["tasks"])
        self.assertEqual(q["revisions"][1]["options"][0]["effect"], "Start work")
        self.assertEqual(q["revisions"][1]["tasks"], ["other"])
        self.assertEqual(tt.open_rows(self.state), [])

    def test_contract_writer_refuses_unknown_event(self):
        with self.assertRaisesRegex(ValueError, "unknown event"):
            tt.write_event(self.state, "demo", "invent", {})
        self.assertFalse((self.state / "demo/asks.jsonl").exists())

    def test_contract_writer_refuses_every_event_after_closing_except_one_acted(self):
        for closed in ("answer", "withdraw"):
            for event in ("reask", "revise", "answer", "withdraw", "acted"):
                with self.subTest(closed=closed, event=event):
                    (self.state / "demo/asks.jsonl").unlink(missing_ok=True)
                    self.ask()
                    self.event(closed, **(dict(channel="chat", words="yes", option=None, resolution=None)
                                           if closed == "answer" else dict(reason="Stop")))
                    if closed == "answer" and event == "acted":
                        self.event("acted", what="Done")
                    saved = (self.state / "demo/asks.jsonl").read_bytes()
                    with self.assertRaisesRegex(ValueError, "after closing"):
                        self.event(event, channel="chat", revision=1, asked="Again", holds="task",
                                   reason="Again", words="yes", option=None, resolution=None, what="Done")
                    self.assertEqual((self.state / "demo/asks.jsonl").read_bytes(), saved)

    def test_contract_writer_refuses_acted_without_answer(self):
        self.ask()
        with self.assertRaisesRegex(ValueError, "acted needs an answer"):
            self.event("acted", what="Done")

    def test_contract_writer_refuses_wordless_answer_without_approve_means(self):
        self.ask(options=[dict(id="a", text="A")])
        with self.assertRaisesRegex(ValueError, "wordless answer needs approve_means"):
            self.event("answer", channel="chat", words=None, option="a", resolution=None)

    def test_contract_writer_refuses_recommendation_outside_options(self):
        with self.assertRaisesRegex(ValueError, "recommend must name an option"):
            self.ask(options=[dict(id="a", text="A")], recommend="missing")
        self.assertFalse((self.state / "demo/asks.jsonl").exists())

    def test_contract_writer_refuses_revision_not_previous_plus_one(self):
        self.ask()
        with self.assertRaisesRegex(ValueError, r"revision must be previous \+ 1"):
            self.event("revise", revision=3, asked="Changed", holds="task", reason="Change")

    def test_contract_writer_refuses_answer_that_does_not_match_last_channel_showing(self):
        self.ask()
        self.event("revise", revision=2, asked="Changed", holds="task", reason="Change")
        with self.assertRaisesRegex(ValueError, "latest showing"):
            self.event("answer", channel="chat", revision=2, words="Yes", option=None, resolution=None)
        self.event("answer", channel="chat", revision=1, words="Yes", option=None, resolution=None)

    def test_missing_owner_prints_complete_command_without_writing(self):
        result = self.cli("demo", "ask", "May I continue?", "--holds", "acceptance", "--recommend", "yes", "--option", "yes=Proceed")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--by '<session>'", result.stderr)
        self.assertIn("'May I continue?' --holds acceptance --recommend yes --option yes=Proceed --channel chat", result.stderr)
        self.assertFalse((self.state / "demo/asks.jsonl").exists())

    def test_review_escalation_after_three_showings_and_unknown_wait_bound(self):
        tt.write_event(self.state, "demo", "ask", dict(asked="Proceed?", asked_at=None,
                       channel="chat", by="test FO", holds="nothing"), tt.when(self.stamp(10)))
        for minute in (15, 20):
            tt.write_event(self.state, "demo", "reask", dict(key="demo#1", channel="chat", briefing=None), tt.when(self.stamp(minute)))
        row = tt.open_rows(self.state, tt.when(self.stamp(30)))[0]
        self.assertEqual((row["waiting_since"], row["waiting_min"], row["waiting_bound"], row["holds"]), (None, 20, "at least", "nothing"))
        self.assertTrue(row["publish_review"])
        tt.write_event(self.state, "demo", "reask", dict(key="demo#1", channel="review", briefing="briefing:one"), tt.when(self.stamp(25)))
        self.assertFalse(tt.open_rows(self.state, tt.when(self.stamp(30)))[0]["publish_review"])

    def test_mixed_legacy_ask_reask_answer_counts_only_showings_in_text_and_json(self):
        self.dispatch("ideation", 1, 0, entering=True)
        self.write("demo/asks.jsonl", json.dumps(dict(at=self.stamp(5), asked="Legacy")) + "\n")
        ask = tt.write_event(self.state, "demo", "ask", dict(asked="New", asked_at="now", channel="chat", by="test FO", holds="task"), tt.when(self.stamp(10)))
        self.assertEqual(ask["key"], "demo#1")
        tt.write_event(self.state, "demo", "reask", dict(key=ask["key"], channel="chat", briefing=None), tt.when(self.stamp(20)))
        tt.write_event(self.state, "demo", "answer", dict(key=ask["key"], channel="chat", words="Yes", option=None, resolution=None), tt.when(self.stamp(30)))
        result = self.cli("demo", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["asks_outside_gate"], 3)
        self.assertEqual(self.cli("demo").returncode, 0)
        self.assertIn("shown again: demo#1", self.cli("demo").stdout)
        self.assertEqual(tt.open_rows(self.state), [])

    def test_reader_ignores_unknown_and_pre_ask_events_and_does_not_reopen_closed_key(self):
        first = self.ask()
        events = [dict(v=1, event="reask", key="demo#1"), first,
                  dict(v=1, event="future", key="demo#1"), first,
                  dict(v=1, event="withdraw", key="demo#1", reason="Stop"),
                  dict(v=1, event="reask", key="demo#1")]
        self.assertEqual((tt.fold_question(events)["state"], tt.fold_question(events)["interruptions"]), ("withdrawn", 1))
        future = dict(v=2, event="answer", key="demo#1")
        for events in ([first, future], [future, first], [future]):
            self.assertEqual(tt.fold_question(events)["state"], "unknown")

    def test_replayed_fourteen_questions_at_declared_synthetic_times(self):
        for i, fixture in enumerate(REPLAY_2026_11_13):
            slug, question, answered = fixture
            self.assertEqual(datetime.fromisoformat(answered).date().isoformat(), "2026-11-13", slug)
            (self.state / f"{slug}.md").write_text("---\ntitle: Replay\n---\n")
            answer_time = tt.when(answered)
            ask_time = answer_time - timedelta(minutes=10 + i)
            entry = tt.write_event(self.state, slug, "ask", dict(asked=question, asked_at="now", channel="chat", by="replay FO", holds=("task", "acceptance", "nothing")[i % 3]), ask_time)
            tt.write_event(self.state, slug, "answer", dict(key=entry["key"], channel="chat", words="Recorded answer", option=None, resolution=None), answer_time)
        clocks = sorted({tt.when(t) + delta for _, _, t in REPLAY_2026_11_13 for delta in (timedelta(minutes=-30), timedelta(minutes=-5), timedelta(), timedelta(minutes=5))})
        self.assertEqual(len(REPLAY_2026_11_13), 14)
        for clock in clocks:
            expected = {f"{slug}#1": (i, tt.when(t) - timedelta(minutes=10 + i)) for i, (slug, _, t) in enumerate(REPLAY_2026_11_13)
                        if tt.when(t) - timedelta(minutes=10 + i) <= clock < tt.when(t)}
            run = self.cli("--open", "--json", "--as-of", tt.iso(clock))
            self.assertEqual(run.returncode, 0, run.stderr)
            actual = {r["key"]: r for r in json.loads(run.stdout)}
            self.assertEqual(set(actual), set(expected), tt.iso(clock))
            for key, (i, since) in expected.items():
                self.assertEqual((actual[key]["by"], actual[key]["waiting_since"], actual[key]["waiting_min"], actual[key]["interruptions"], actual[key]["state"], actual[key]["holds"]),
                                 ("replay FO", tt.iso(since), tt.mins(since, clock), 1, "open", ("task", "acceptance", "nothing")[i % 3]))

    def test_readme_plain_open_entrance_and_mixed_gate_rows_have_question_text(self):
        ask = self.cli("demo", "ask", "Proceed?", "--holds", "acceptance", "--by", "test FO")
        self.assertEqual(ask.returncode, 0, ask.stderr)
        key = "briefing:demo:ideation:1"
        self.task.write_text('---\ntitle: Demo\ngates:\n  records:\n    - stage: ideation\n      attempts:\n        - id: gate-attempt:demo:1\n          briefing:\n            id: ' + key + '\n            room-ref: demo/review/ideation/briefing-1\n---\n')
        self.write("demo/review/ideation/briefing-1/index.json", json.dumps(dict(question="Gate question?")))
        self.commit("prepare native gate", 10)
        plain = self.cli("--open")
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertIn("Proceed?", plain.stdout)
        for flags in (("--open", "--json"), ("--open", "--gates", "--json")):
            run = self.cli(*flags)
            self.assertEqual(run.returncode, 0, run.stderr)
            rows = json.loads(run.stdout)
            self.assertEqual({r["kind"]: r["question"] for r in rows},
                             {"question": "Proceed?", **({"gate": "Gate question?"} if "--gates" in flags else {})})
        mixed = self.cli("--open", "--gates")
        self.assertEqual(mixed.returncode, 0, mixed.stderr)
        self.assertIn("Proceed?", mixed.stdout)
        self.assertIn("Gate question?", mixed.stdout)

    def test_gate_wait_uses_first_naming_commit_after_archive_moves_room(self):
        (self.state / "_archive").mkdir()
        key = "briefing:demo:ideation:1"
        self.task.write_text('---\ntitle: Demo\ngates:\n  records:\n    - stage: ideation\n      attempts:\n        - id: gate-attempt:demo:1\n          briefing:\n            id: ' + key + '\n            room-ref: demo/review/ideation/briefing-1\n---\n')
        self.write("demo/review/ideation/briefing-1/index.json", json.dumps(dict(question="Proceed?")))
        self.commit("first names briefing", 10)
        self.task.write_text(self.task.read_text().replace("---\n", "---\n", 1).replace("\n---\n", '\n          resolution:\n            at: "' + self.stamp(30) + '"\n            decision: approve\n---\n'))
        self.commit("resolve", 30)
        self.finish(50)
        row = tt.open_rows(self.state, tt.when(self.stamp(20)), gates=True)[0]
        self.assertEqual((row["key"], row["waiting_since"], row["waiting_min"], row["waiting_bound"], row["question"]),
                         (key, self.stamp(10), 10, "at least", "Proceed?"))
        self.assertEqual(tt.open_rows(self.state, tt.when(self.stamp(30)), gates=True), [])
        self.assertEqual(tt.open_rows(self.state, gates=True), [])
        self.assertEqual(tt.open_rows(self.state, tt.when(self.stamp(5)), gates=True), [])



# Public 2026-11-13 replay; asking times and replay owner are synthetic in the test.
REPLAY_2026_11_13 = [('replay-1',
  '#854、#856 要不要各加一次驗證預算？ 同意即接受：兩張預算改成 1 implementation and 3 validation cycles；修正交回原 '
  'worker；第三次驗證前先請獨立審查者看一次；第三次再被退回就停下來回到你這裡。',
  '2026-11-13T10:40:43+08:00'),
 ('replay-2',
  '#859（做新東西前先查既有的）第一次驗證因「缺一項獨立行為證明」被退回，成品本身沒查到缺陷。要不要用預算內剩下的那一次驗證，派一位新的驗證者只補這一項證明？我建議要。核准等於同意不改成品、不改驗收條件，只重做這項觀察；這次再不過就停下來。',
  '2026-11-13T02:22:34+08:00'),
 ('replay-3',
  '有一件事現在就可以順手做：那張設計中的任務，我可以把你這段話原文交給設計 worker，要它把措辭設計成「引用 POC 的規則」而不是另寫一套，這樣第 3 '
  '步之後會省很多。這不改任務範圍，只是多一個設計方向。要不要這樣做由你決定。',
  '2026-11-13T14:49:47+08:00'),
 ('replay-4',
  '#864（Pilot '
  '設計階段先做試作）第一次驗證被退回，有兩個發現，要怎麼處理？我建議修完再驗一次。兩個發現會一起決定剩下那一次驗證怎麼用，所以放在同一題：一、第三條驗收條件的檢查指令寫錯了（會把檢查工具「成功」的訊息也當成重複），成品其實符合條件，驗證者用正確的指令跑過；要你同意把指令改成只算失敗訊息。二、驗證者找了一個沒有背景的 '
  'worker 讀新版派工：它確實先做試作才寫設計，而且發現那張任務的前提已不成立；但三條驗收條件裡有一條沒照規定記下指令、結束代碼和輸出位置。同意即接受：用掉預算裡最後一次驗證；第二次觀察也只是一個 '
  'worker 跑一次，再不過我就停下來回到你這裡。',
  '2026-11-13T16:01:58+08:00'),
 ('replay-5', '要不要開「Pilot 流程改動」的任務（你上一則問的後續，我建議開，拆成先進套件的和維持逐批授權的兩段）。', '2026-11-13T14:42:40+08:00'),
 ('replay-6',
  '「自動觸發 Codex 審查」這張要怎麼走？ 同意第一個選項即接受：這張的範圍從「程式自動觸發」改成「在 Codex 擴充的說明加一句：FO 把 PR 標成可審查時同時留言請 Codex '
  '審查一次」，我自己的出貨腳本現在就照做；記成這張的修正案，原本「恰好一次」的停止條件作廢。變差的是：仍然靠 FO 記得做（但和標成可審查是同一個動作）；偶爾會讓 Codex 對同一版多審一次，我沒量過這個成本。',
  '2026-11-13T21:57:48+08:00'),
 ('replay-7', '下一輪顧問試跑要不要現在開始準備，以及是否把「合併前這一段」的三個摩擦點各開一張任務。', '2026-11-13T10:24:54+08:00'),
 ('replay-8',
  'Pilot 試作的設計回來了，核准前要先定一件會改變範圍的事：試作輪數的預算要怎麼管？我建議分兩步。設計查到：現有的預算寫法（N implementation and M validation '
  'cycles）只會算實作和驗證，不會算設計階段的輪數；時間工具會算設計階段派了幾次、整個階段多久，但不會列出每一輪各自的起訖和結果。\n'
  'Chosen option: 這張先用一句規則：試作一輪就是一次設計派工，第三次派工前我要停下來問你。另開一張小任務把預算寫法擴成「N ideation, N implementation and M '
  'validation cycles」由程式檢查，並讓時間工具列出每一輪。',
  '2026-11-13T15:14:02+08:00'),
 ('replay-9',
  '要不要開「待決定事項紀錄」這張任務？\n'
  'Stated scope: 兩個專案的 FO 今天都轉述你要改善「等你決定的事」的呈現方式。開任務等於接受：我把它放進待辦，寫成「關卡以外問你的每一題是一筆紀錄，答案記錄前都算待決定」；因為寫的是 '
  'dev2、讀的是 Bridge 和 Review，會先定格式合約再實作；Spacedock 本身和任何畫面都不在範圍內。',
  '2026-11-13T14:45:53+08:00'),
 ('replay-10',
  "「#866 這張要怎麼走？」 with FO's recommendation 「選第三條，#866 "
  '留著不合併也不再修。接下來要做的「邊界合約先行」那幾張，設計階段都會用到新規則，我每張記下「幾條驗收條件、幾條記齊」。如果五張裡漏記出現兩次以上，再開任務做第二條（結構化紀錄）；如果沒有，就不需要這道關卡。會變差的是：這段期間規則仍只靠文字，而且已經花在這張上的三個小時大部分沒有產出。」',
  '2026-11-13T20:22:30+08:00'),
 ('replay-11',
  '一、把 Pilot 試作補完整｜這版的兩條規則只靠文字：每條驗收條件要記齊、試作最多兩輪｜驗證時兩個測試 worker 一個漏記；顧問明說只有檢查程式擋得住｜兩張小任務，其中一張已在待辦',
  '2026-11-13T17:51:53+08:00'),
 ('replay-12',
  '#854（派工結束時封存證據、刪暫存）的本機審查報了一個高嚴重度問題：封存時沒有機械檢查證據是不是公開的，私有內容若被 worker 放進證據資料夾就會留在公開分支。要不要先放行這一項、另開任務處理，讓 '
  '#854 進第三次驗證？我建議放行。獨立審查者判定：這不是實作缺陷，是你當初核准的做法（私有證據靠派工文字要求 worker '
  '不封存）本來就沒有機械檢查；這次改動沒有新增任何自動上傳的路徑，也沒有發現實際外漏。放行等於接受：這個缺口暫時留著，我開一張任務「證據進公開分支前要先聲明是公開的」。',
  '2026-11-13T11:45:10+08:00'),
 ('replay-13',
  "「這張要怎麼走？」 with FO's recommended option 「改成：檢查結果存成紀錄，拿掉手寫摘要（建議）」 and its stated cost "
  '「每次合併會多一份檔案寫進公開的狀態分支，內容是 PR 編號、版本、檢查結果，不含私有內容。以及關卡紀錄裡給人讀的那段文字會變成工具輸出的格式，沒那麼好讀。」',
  '2026-11-13T22:18:20+08:00'),
 ('replay-14',
  "「合併檢查存紀錄這張，要不要做成邊界合約？」 with FO's recommended option 「做成合約：一份定義，其他地方引用並刪掉抄本（建議）」 and its stated cost "
  '「比單純改三個檔多一份合約文件和一些重寫，今晚做不完的機率比較高；而且「其他地方改成引用」是在刪文字，要小心別刪到只有那裡才有的規則。」',
  '2026-11-13T23:51:21+08:00')]

if __name__ == "__main__":
    unittest.main()
