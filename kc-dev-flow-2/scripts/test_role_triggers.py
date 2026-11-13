#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from role_triggers import review_facts  # noqa: E402

SCRIPT = Path(__file__).with_name("role_triggers.py")
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
SLUG = "some-task"
CE, ER = "kc-dev-flow-2:chief-engineer", "kc-dev-flow-2:engineering-reviewer"
MECHANISM = "what single mechanism produces these findings, and what one change closes that class?"
UNRELATED = "unrelated: F1 explicit home exit keeps the draft; F2 late 201 response after Back"


def git(where, *args):
    done = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True, env={**os.environ, **IDENTITY})
    assert done.returncode == 0, f"git {args}: {done.stderr}"
    return done.stdout.strip()


def run(*args):
    done = subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)], capture_output=True, text=True,
                          env={**os.environ, **IDENTITY})
    return done.returncode, done.stdout


def task(repairs=0, amendments=(), extra="", after="", profile="pilot", reports=None):
    body = ["---", "title: t", f"profile: {profile}", "status: validation", "---", "", "## FO alignment", "", "Surfaces: none", extra, ""]
    if amendments:
        body += ["## Captain amendments", ""]
        for number, date, supersedes, design in amendments:
            body += [f"### Amendment {number} — {date}, chat", "Captain: 「ok」 (chat)", f"Supersedes: {supersedes}",
                     f"Design: {design}", ""]
    for n in range(repairs + 1 if reports is None else reports):
        body += ["## Stage Report: implementation" + (f" (cycle {n + 1})" if n else ""), "", "- DONE: x", ""]
    if after:
        body += ["## Stage Report: validation", "", after, ""]
    return "\n".join(body) + "\n"


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / "state"
        self.state.mkdir()
        git(self.state, "init", "-q", "-b", "main")

    def put(self, text, where=f"{SLUG}.md"):
        path = self.state / where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        git(self.state, "add", "-A")
        git(self.state, "commit", "-qm", "task")

    def owed(self, rev="HEAD"):
        code, out = run(self.state, SLUG, "--rev", rev)
        self.assertEqual(code, 1 if out.startswith("next:") else 0, out)
        return code, [line for line in out.splitlines() if line.startswith("next:")]


def call(agent, model, date, question="q"):
    return f"Reviewer: {agent} {model} {date} — {question}"


class RoleTriggersTest(Fixture):
    def test_repair_and_review_only_events_keep_the_smallest_next_step_question(self):
        for repairs, rounds in ((4, 0), (0, 2)):
            self.put(task(repairs=repairs))
            code, out = run(self.state, SLUG, "--review-rounds", rounds)
            self.assertEqual(code, 1, out)
            self.assertIn('with the question "what is the smallest next step, given the findings so far?"', out)
            self.assertNotIn(MECHANISM, out)
            self.assertNotIn("unrelated:", out)
            self.put(task(repairs=repairs, extra=f"Reviewer: {CE} not run: Captain ordered it"))
            self.assertEqual(run(self.state, SLUG, "--review-rounds", rounds)[0], 0)

    def test_four_repair_passes_owe_chief_engineer_in_every_record_shape(self):
        self.put(task(repairs=3))
        self.assertEqual(self.owed()[0], 0)
        self.put(task(repairs=4))
        code, lines = self.owed()
        self.assertEqual(code, 1)
        self.assertEqual(len(lines), 1)
        self.assertIn(f"dispatch {CE} on opus or gpt-6-astra ", lines[0])
        self.assertIn(f"Reviewer: {CE} <model> <date>", lines[0])
        self.assertIn("has 4 repair passes", lines[0])
        self.assertLessEqual(len(lines[0].split()), 60)
        pr_lines = "".join(f"- PR #{n} merged\n" for n in (1, 2))
        self.put(task(repairs=4, after="") + f"\n## Feedback Cycles\n\n{pr_lines}")
        self.assertEqual(self.owed()[0], 1)
        self.put(task(reports=0, extra="```\n" + "## Stage Report: implementation\n" * 5 + "```"))
        self.assertEqual(self.owed()[0], 0)

    def test_only_level_two_implementation_reports_are_repair_passes(self):
        self.put(task(repairs=3) + "\n### Stage Report: implementation (cycle 9)\n\n## Stage Report: validation (cycle 9)\n")
        self.assertEqual(self.owed()[0], 0)

    def test_the_repair_count_is_read_at_the_named_revision(self):
        self.put(task(repairs=3))
        self.put(task(repairs=4))
        self.assertEqual(run(self.state, SLUG, "--rev", "HEAD~1")[0], 0)
        self.assertEqual(run(self.state, SLUG)[0], 1)

    def test_two_review_rounds_owe_chief_engineer_only_when_the_caller_passes_them(self):
        self.put(task(repairs=1))
        self.assertEqual(run(self.state, SLUG)[0], 0)
        self.assertEqual(run(self.state, SLUG, "--review-rounds", 1)[0], 0)
        code, out = run(self.state, SLUG, "--review-rounds", 2)
        self.assertEqual((code, out.count("next:")), (1, 1))
        self.assertIn("has 2 review rounds", out)
        self.put(task(repairs=4))
        self.assertIn("has 4 repair passes and 2 review rounds", run(self.state, SLUG, "--review-rounds", "2")[1])
        self.put(task(repairs=1, extra=call(CE, "opus", "2026-10-18")))
        self.assertEqual(run(self.state, SLUG, "--review-rounds", 3)[0], 0)
        for bad in ("-1", "x", ""):
            self.assertEqual(run(self.state, SLUG, "--review-rounds", bad)[0], 2, bad)

    def test_the_newest_review_round_dates_the_call_that_must_clear_it(self):
        def comment(rid, at):
            return {"pull_request_review_id": rid, "created_at": at}
        recorded = {
            "three rounds on one day-pair": ([comment(5636050872, "2026-10-24T01:13:27Z"), comment(5636392914, "2026-10-24T02:18:49Z"),
                                              comment(5636428225, "2026-10-24T02:30:30Z")], (3, "2026-10-24")),
            "a round of two comments": ([comment(5610899867, "2026-10-22T07:53:41Z"), comment(5612546695, "2026-10-22T10:09:03Z"),
                                         comment(5612786931, "2026-10-22T10:30:11Z"), comment(5612786931, "2026-10-22T10:30:12Z")],
                                        (3, "2026-10-22")),
            "two rounds": ([comment(5569526052, "2026-10-19T09:33:52Z"), comment(5569986438, "2026-10-19T10:08:56Z")], (2, "2026-10-19")),
            "one round": ([comment(5628565363, "2026-10-23T13:01:09Z")], (1, None)),
            "ids out of time order": ([comment(20, "2026-10-20T08:00:00Z"), comment(10, "2026-10-22T08:00:00Z")], (2, "2026-10-22")),
            "a round dated by its earliest comment": ([comment(1, "2026-10-20T08:00:00Z"), comment(2, "2026-10-21T23:59:00Z"),
                                                       comment(2, "2026-10-22T00:01:00Z")], (2, "2026-10-21")),
            "no timestamps": ([{"pull_request_review_id": 1}, {"pull_request_review_id": 2}], (2, None)),
            "no comments": ([], (0, None)),
        }
        for name, (comments, expected) in recorded.items():
            with self.subTest(name):
                self.assertEqual(review_facts(comments), expected)

    def test_a_call_or_waiver_older_than_the_newest_round_leaves_the_rounds_owed(self):
        def judged(extra, *more):
            self.put(task(repairs=1, extra=extra))
            return run(self.state, SLUG, "--review-rounds", 3, "--drift-date", "2026-10-24", *more)
        code, out = judged("")
        self.assertEqual((code, out.count("next:")), (1, 1))
        self.assertIn("has 3 review rounds, the newest on 2026-10-24;", out)
        self.assertIn("`Reviewer: kc-dev-flow-2:chief-engineer not run <date>: <reason>`", out)
        self.assertLessEqual(len(out.split()), 60)
        cleared = {"a call on the round's date": call(CE, "opus", "2026-10-24"), "a call after it": call(CE, "opus", "2026-10-25"),
                   "a dated waiver on it": f"Reviewer: {CE} not run 2026-10-24: Captain ordered it"}
        left = {"a call the day before": call(CE, "opus", "2026-10-23"), "an undated waiver": f"Reviewer: {CE} not run: Captain ordered it",
                "a dated waiver the day before": f"Reviewer: {CE} not run 2026-10-23: Captain ordered it"}
        for name, line in cleared.items():
            with self.subTest(name):
                self.assertEqual(judged(line)[0], 0)
        for name, line in left.items():
            with self.subTest(name):
                self.assertEqual(judged(line)[0], 1)

    def test_without_a_drift_date_any_call_still_clears_and_a_repair_call_never_needs_a_date(self):
        self.put(task(repairs=1, extra=call(CE, "opus", "2026-10-18")))
        self.assertEqual(run(self.state, SLUG, "--review-rounds", 3)[0], 0)
        self.put(task(repairs=4, extra=call(CE, "opus", "2026-10-18")))
        code, out = run(self.state, SLUG, "--review-rounds", 3, "--drift-date", "2026-10-24")
        self.assertEqual(code, 1)
        self.assertIn("has 3 review rounds, the newest on 2026-10-24;", out)
        self.assertNotIn("repair passes", out)
        self.assertEqual(run(self.state, SLUG, "--review-rounds", 1, "--drift-date", "2026-10-24")[0], 0)
        for bad in ("2026-10", "x", ""):
            self.assertEqual(run(self.state, SLUG, "--review-rounds", 3, "--drift-date", bad)[0], 2, bad)

    def test_wording_does_not_decide_whether_a_call_counts_but_its_heading_does(self):
        self.put(task(repairs=4, extra=call(CE, "opus", "2026-10-18", "repair again, or narrow the PR?")))
        self.assertEqual(self.owed()[0], 0)
        self.put(task(repairs=4, extra=f"Reviewer: {CE} not run: Captain ordered the passes"))
        self.assertEqual(self.owed()[0], 0)
        self.put(task(repairs=4, extra=f"Reviewer: {CE} not run 2026-10-18: Captain ordered the passes"))
        self.assertEqual(self.owed()[0], 0)
        self.put(task(repairs=4, after=call(CE, "opus", "2026-10-18")))
        code, lines = self.owed()
        self.assertEqual((code, len(lines)), (1, 2))
        self.assertIn('under "## Stage Report: validation"', lines[1])
        self.assertLessEqual(len(lines[1].split()), 60)

    def test_a_line_that_is_not_a_call_clears_nothing(self):
        cases = {
            "wrong agent": call(ER, "opus", "2026-10-16"),
            "other seat": call("design-reviewer", "opus", "2026-10-16"),
            "blank reason": f"Reviewer: {CE} not run:",
            "no reason text": f"Reviewer: {CE} not run: ( )",
            "no date": f"Reviewer: {CE} opus — what next?",
            "no question": f"Reviewer: {CE} opus 2026-10-16 —",
            "prose": f"FO considered {call(CE, 'opus', '2026-10-16')}",
            "plan line": "Reviewer: one run per design when the Captain asks",
        }
        for name, line in cases.items():
            with self.subTest(name):
                self.put(task(repairs=4, extra=line))
                self.assertEqual(self.owed()[0], 1)

    def test_a_task_with_five_replacing_amendments_prints_one_line_listing_them(self):
        self.put(task(amendments=[(1, "2026-10-15", "AC-4", "none"), (2, "2026-10-15", "none", "the whole design"),
                                  (3, "2026-10-15", "none (no replacement: widened)", "none"),
                                  (4, "2026-10-16", "AC-9", "none"), (5, "2026-10-16", "AC-1", "x"),
                                  (6, "2026-10-16", "none", "x")]))
        code, lines = self.owed()
        self.assertEqual((code, len(lines)), (1, 2))
        self.assertIn("has 3 replacing amendments", lines[0])
        self.assertIn("has replacing amendments 1, 2, 4, 5, 6", lines[1])
        self.assertIn(f"Reviewer: {ER} <model> <date>", lines[1])
        self.assertIn(f"dispatch {ER} on opus or gpt-6-astra ", lines[1])
        self.assertLessEqual(len(lines[1].split()), 60)

    def test_an_amendment_is_cleared_by_a_call_or_a_dated_waiver_no_earlier_than_it(self):
        amendments = [(n, date, "AC-4", "none") for n, date in ((1, "2026-10-15"), (2, "2026-10-15"), (3, "2026-10-16"),
                                                                 (4, "2026-10-17"), (5, "2026-10-17"))]
        listed = lambda lines: re.search(r"has replacing amendments? ([\d, ]+)", "\n".join(lines)).group(1)
        cleared_ce = call(CE, "opus", "2026-10-16") + "\n"
        self.put(task(amendments=amendments, extra=call(ER, "opus", "2026-10-16")))
        self.assertEqual(listed(self.owed()[1]), "4, 5")
        self.put(task(amendments=amendments, extra=f"Reviewer: {ER} not run 2026-10-16: widened scope only"))
        self.assertEqual(listed(self.owed()[1]), "4, 5")
        self.put(task(amendments=amendments, extra=f"Reviewer: {ER} not run: widened scope only"))
        self.assertEqual(listed(self.owed()[1]), "1, 2, 3, 4, 5")
        self.put(task(amendments=amendments, extra=cleared_ce + call(ER, "opus", "2026-10-17")))
        self.assertEqual(self.owed()[0], 0)
        self.put(task(amendments=amendments[:1], extra=call(ER, "opus", "2026-10-15", "an unrelated question about a bridge")))
        self.assertEqual(self.owed()[0], 0)

    def test_calls_made_before_the_amendment_leave_it_owed(self):
        self.put(task(amendments=[(1, "2026-10-17", "AC-4", "none")],
                      extra=call(ER, "opus", "2026-10-15") + "\n" + call(ER, "opus", "2026-10-16")))
        self.assertEqual(self.owed()[0], 1)

    def test_a_replacing_amendment_names_the_model_the_profile_or_surface_requires(self):
        amendment = [(1, "2026-10-15", "AC-4", "none")]
        cases = (("prod", "none", "on fable or gpt-6-astra (profile prod)"), ("pilot", "db", "on fable or gpt-6-astra (Surfaces db)"),
                 ("prod", "db", "on fable or gpt-6-astra (profile prod, Surfaces db)"), ("pilot", "none", "on opus or gpt-6-astra "),
                 ("pilot", "ui, db", "on fable or gpt-6-astra (Surfaces db)"))
        for profile, surfaces, expected in cases:
            with self.subTest(profile=profile, surfaces=surfaces):
                self.put(task(amendments=amendment, profile=profile).replace("Surfaces: none", f"Surfaces: {surfaces}"))
                lines = self.owed()[1]
                self.assertIn(f"dispatch {ER} {expected}", lines[0])
                self.assertLessEqual(len(lines[0].split()), 60)
        self.put(task(amendments=amendment, extra="```\nSurfaces: db\n```"))
        self.assertIn("on opus or gpt-6-astra ", self.owed()[1][0])
        self.put(task(repairs=4))
        self.assertNotIn("fable", self.owed()[1][0])

    def test_a_call_below_the_required_model_does_not_clear(self):
        amendment = [(1, "2026-10-15", "AC-4", "none")]
        cases = (("pilot", "sonnet", 1), ("pilot", "haiku", 1), ("pilot", "opus", 0), ("pilot", "Opus", 0),
                 ("pilot", "opus-5.5", 0), ("pilot", "fable", 0), ("pilot", "mystery", 1), ("pilot", "5.5", 1),
                 ("prod", "opus", 1), ("prod", "opus-5.5", 1), ("prod", "fable", 0), ("prod", "sonnet", 1))
        for profile, model, expected in cases:
            with self.subTest(profile=profile, model=model):
                self.put(task(amendments=amendment, profile=profile, extra=call(ER, model, "2026-10-18")))
                code, lines = self.owed()
                self.assertEqual(code, expected)
                if expected:
                    self.assertIn(f"on {'fable' if profile == 'prod' else 'opus'}", lines[0])
        cases = (("pilot", "gpt-6-astra", 0), ("pilot", "claude-opus-5-5", 0),
                 ("pilot", "gpt-6.1-sol", 1), ("pilot", "gpt-6.1-terra", 1), ("pilot", "gpt-6-luna", 1),
                 ("pilot", "claude-sonnet-5-5", 1), ("prod", "gpt-6-astra", 0), ("prod", "fable", 0),
                 ("prod", "claude-fable-5-1", 0), ("prod", "opus", 1), ("prod", "claude-opus-5-5", 1))
        for profile, model, expected in cases:
            with self.subTest(profile=profile, model=model):
                self.put(task(amendments=amendment, profile=profile, extra=call(ER, model, "2026-10-18")))
                self.assertEqual(self.owed()[0], expected)
        self.put(task(amendments=amendment, profile="prod", extra=f"Reviewer: {ER} not run 2026-10-18: widened only"))
        self.assertEqual(self.owed()[0], 0)

    def test_chief_engineer_floor_applies_to_repairs_and_review_rounds(self):
        for model, expected in (("sonnet", 1), ("gpt-6.1-sol", 1), ("opus", 0), ("gpt-6-astra", 0)):
            for repairs, flags in ((4, ()), (0, ("--review-rounds", 2, "--drift-date", "2026-10-24"))):
                with self.subTest(model=model, repairs=repairs):
                    self.put(task(repairs=repairs, extra=call(CE, model, "2026-10-24")))
                    self.assertEqual(run(self.state, SLUG, *flags)[0], expected)
        for repairs, flags in ((4, ()), (0, ("--review-rounds", 2, "--drift-date", "2026-10-24"))):
            self.put(task(repairs=repairs, extra=f"Reviewer: {CE} not run 2026-10-24: Captain waived"))
            self.assertEqual(run(self.state, SLUG, *flags)[0], 0)

    def test_astra_amendment_calls_clear_the_peer_policy_shape_without_its_waiver(self):
        amendments = [(n, "2026-10-30", f"AC-{n}", "none") for n in (1, 2, 3)]
        for model, expected in (("gpt-6-astra", 0), ("gpt-6.1-sol", 1)):
            self.put(task(amendments=amendments, extra=call(CE, "opus", "2026-10-30") + "\n" + call(ER, model, "2026-10-30")))
            self.assertEqual(self.owed()[0], expected)

    def test_fenced_text_is_not_an_event_and_a_fenced_line_clears_nothing(self):
        fence = "".join(f"## Stage Report: implementation\n" for _ in range(6))
        fixture = (f"```md\n{fence}```\n\n```md\n## Captain amendments\n"
                   "### Amendment 1 — 2026-10-16, chat\nSupersedes: AC-2\n```\n")
        self.put(task(extra=fixture))
        self.assertEqual(self.owed()[0], 0)
        self.put(task(repairs=4, extra=f"```\n{call(CE, 'opus', '2026-10-16')}\n```"))
        self.assertEqual(self.owed()[0], 1)

    def test_only_the_fo_alignment_section_can_clear_an_event(self):
        line, waiver = call(CE, "opus", "2026-10-16"), f"Reviewer: {CE} not run: Captain ordered the passes"
        for name, line in (("call", line), ("waiver", waiver)):
            with self.subTest(name + " in another section"):
                self.put(task(repairs=4, after=line))
                self.assertEqual(self.owed()[0], 1)
            with self.subTest(name + " in FO alignment"):
                self.put(task(repairs=4, extra=line))
                self.assertEqual(self.owed()[0], 0)
            with self.subTest(name + " under a subheading of FO alignment"):
                self.put(task(repairs=4, extra=f"### Roles\n\n{line}"))
                self.assertEqual(self.owed()[0], 0)

    def test_it_judges_committed_bytes_and_leaves_the_checkout_unchanged(self):
        self.put(task(repairs=4))
        (self.state / f"{SLUG}.md").write_text(task(repairs=4, extra=f"Reviewer: {CE} not run: busy"))
        before = git(self.state, "status", "--porcelain")
        self.assertEqual(run(self.state, SLUG)[0], 1)
        self.assertEqual(run(self.state, SLUG, "--rev", "HEAD")[0], 1)
        self.assertEqual(git(self.state, "status", "--porcelain"), before)
        git(self.state, "add", "-A")
        git(self.state, "commit", "-qm", "waiver")
        self.assertEqual(run(self.state, SLUG)[0], 0)
        self.assertEqual(run(self.state, SLUG, "--rev", "HEAD~1")[0], 1)
        self.assertEqual(git(self.state, "status", "--porcelain"), "")

    def test_it_reports_what_it_cannot_tell_with_exit_2(self):
        self.put(task())
        for args in ((self.state, SLUG, "--rev", "nope"), (self.state, "absent"), (self.tmp.name, SLUG), (self.state,),
                     (self.state, "a/b"), (self.state, SLUG, "--rev")):
            with self.subTest(args=args):
                code, out = run(*args)
                self.assertEqual(code, 2)
                self.assertIn("cannot tell", out)

    def test_an_archived_or_folder_task_is_read_under_its_own_name(self):
        self.put(task(repairs=4), f"_archive/{SLUG}.md")
        self.assertEqual(self.owed()[0], 1)
        git(self.state, "rm", "-q", f"_archive/{SLUG}.md")
        self.put(task(repairs=4), f"{SLUG}/index.md")
        self.assertEqual(self.owed()[0], 1)


def validations(*findings):
    return "".join(f"\n## Stage Report: validation (cycle {n})\n\n{finding}\n\n### Summary\n\nresult\n"
                   for n, finding in enumerate(findings, 1))


class StepBackTest(Fixture):
    questions = ("which Captain words does this serve", "what breaks without it",
                 "which single premise would make the task unneeded, and what cheap test checks it now?")
    failed = "- F1 Material: gap\n- F2 Needs decision: another gap"
    amendments = [(n, f"2026-10-{15 + n}", "AC-1", "none") for n in (1, 2, 3, 4)]

    def assert_questions(self, out):
        for question in self.questions:
            self.assertIn(question, out)

    def test_two_failed_reports_count_once_each_and_passing_reports_do_not_count(self):
        for findings, expected in (((), False), ((self.failed,), False),
                                   ((self.failed, "- DONE: passed", "- DONE: passed"), False),
                                   ((self.failed, self.failed), True)):
            with self.subTest(findings=findings):
                self.put(task() + validations(*findings))
                code, out = run(self.state, SLUG)
                self.assertEqual(code, 0, out)
                self.assertEqual("before the next step" in out, expected, out)
                if expected:
                    self.assertEqual(len(out.splitlines()), 1)
                    self.assert_questions(out)
                    self.assertEqual(len(out.split()), 46)

    def test_fenced_findings_and_nonblocking_findings_do_not_count(self):
        for finding in (f"```md\n{self.failed}\n```", "- F2 Deferred risk: later", "- F3 Polish: wording"):
            self.put(task() + validations(self.failed, finding))
            self.assertNotIn("before the next step", run(self.state, SLUG)[1])

    def test_only_superseding_amendments_count_and_the_two_counts_stay_separate(self):
        er = call(ER, "opus", "2026-10-20")
        for amendments, findings, expected in ((self.amendments[:2], (), True),
                ((self.amendments[0], (2, "2026-10-17", "none", "a different design")), (), False),
                (self.amendments[:1], (self.failed,), False)):
            self.put(task(amendments=amendments, extra=er) + validations(*findings))
            code, out = run(self.state, SLUG)
            self.assertEqual(code, 0, out)
            self.assertEqual("before the next step" in out, expected, out)
            if expected:
                self.assert_questions(out)

    def test_third_failure_owes_one_mechanism_call_even_with_repairs_and_rounds(self):
        self.put(task(repairs=4) + validations(*([self.failed] * 3)))
        code, out = run(self.state, SLUG, "--review-rounds", 2)
        self.assertEqual((code, len(out.splitlines())), (1, 1), out)
        self.assertIn("4 repair passes and 2 review rounds and 3 validations", out)
        self.assertIn(MECHANISM, out)
        self.assertIn("not run <date>: unrelated: <finding> <its own cause>; <finding> <its own cause>", out)
        for question in self.questions:
            self.assertNotIn(question, out)
        self.assertNotIn("before the next step", out)

    def test_two_replacements_still_remind_after_validation_event_is_cleared(self):
        extra = call(CE, "gpt-6-astra", "2026-01-01") + "\n" + call(ER, "opus", "2026-10-20")
        for count in (3, 4):
            self.put(task(amendments=self.amendments[:2], extra=extra) + validations(*([self.failed] * count)))
            code, out = run(self.state, SLUG)
            self.assertEqual(code, 0, out)
            self.assertEqual(len(out.splitlines()), 1, out)
            self.assertIn("before the next step", out)
            self.assert_questions(out)

    def test_two_failed_validations_still_remind_after_replacement_event_is_cleared(self):
        extra = call(CE, "gpt-6-astra", "2026-10-20") + "\n" + call(ER, "opus", "2026-10-20")
        for count in (3, 4):
            self.put(task(amendments=self.amendments[:count], extra=extra) + validations(self.failed, self.failed))
            code, out = run(self.state, SLUG)
            self.assertEqual(code, 0, out)
            self.assertEqual(len(out.splitlines()), 1, out)
            self.assertIn("before the next step", out)
            self.assert_questions(out)

    def test_a_third_findings_or_amendment_call_suppresses_the_second_event_reminder(self):
        for failures, replacements in ((3, 2), (2, 3)):
            self.put(task(amendments=self.amendments[:replacements], extra=call(ER, "opus", "2026-10-20"))
                     + validations(*([self.failed] * failures)))
            code, out = run(self.state, SLUG)
            self.assertEqual((code, len(out.splitlines())), (1, 1), out)
            if failures == 3:
                self.assertIn(MECHANISM, out)
                for question in self.questions:
                    self.assertNotIn(question, out)
            else:
                self.assert_questions(out)
                self.assertNotIn(MECHANISM, out)
                self.assertIn("not run <date>: <reason>", out)
            self.assertIn(f"dispatch {CE}", out)
            self.assertNotIn("before the next step", out)
        self.put(task(repairs=4) + validations(self.failed, self.failed))
        code, out = run(self.state, SLUG)
        self.assertEqual((code, len(out.splitlines())), (1, 2), out)
        self.assertIn("has 4 repair passes", out)
        self.assertIn("before the next step", out)
        self.assertEqual(out.count(self.questions[0]), 1, out)

    def test_failure_calls_need_the_model_floor_but_no_date_floor_and_reasoned_waivers_clear(self):
        for extra, expected in (("", 1), (call(CE, "sonnet", "2026-10-20"), 1),
                (call(CE, "gpt-6-astra", "2026-01-01"), 0), (call(CE, "opus", "2026-01-01"), 0),
                (f"Reviewer: {CE} not run: Captain waived", 1), (f"Reviewer: {CE} not run 2026-01-01: waived", 1),
                (f"Reviewer: {CE} not run: {UNRELATED}", 0), (f"Reviewer: {CE} not run 2026-01-01: {UNRELATED}", 0)):
            self.put(task(extra=extra) + validations(*([self.failed] * 3)))
            code, out = run(self.state, SLUG)
            self.assertEqual(code, expected, out)
            if expected:
                self.assertIn(MECHANISM, out)
                self.assertLessEqual(len(out.split()), 77)

    def test_third_replacement_dates_the_call_or_waiver_and_fourth_owes_no_second_call(self):
        er = call(ER, "opus", "2026-10-20") + "\n"
        for extra, expected in (("", 1), (call(CE, "opus", "2026-10-17"), 1),
                (call(CE, "sonnet", "2026-10-18"), 1), (call(CE, "gpt-6-astra", "2026-10-18"), 0),
                (call(CE, "opus", "2026-10-19"), 0), (f"Reviewer: {CE} not run: waived", 1),
                (f"Reviewer: {CE} not run 2026-10-17: waived", 1), (f"Reviewer: {CE} not run 2026-10-18: waived", 0)):
            for count in (3, 4):
                with self.subTest(extra=extra, count=count):
                    self.put(task(amendments=self.amendments[:count], extra=er + extra))
                    code, out = run(self.state, SLUG)
                    self.assertEqual(code, expected, out)
                    self.assertNotIn("before the next step", out)
                    if expected:
                        self.assert_questions(out)
                        self.assertEqual(len(out.splitlines()), 1)
                        self.assertLessEqual(len(out.split()), 68)


def forms(heading, trailing=True):
    spelled = {"uppercase": heading.upper(), "lowercase": heading.lower(), "leading space": " " + heading,
               "leading tab": "\t" + heading, "leading no-break space": "\xa0" + heading}
    if trailing:
        spelled["trailing no-break space"] = heading + "\xa0"
    return spelled


class SpaceClassTest(unittest.TestCase):
    def test_the_space_class_is_the_one_design_surfaces_uses(self):
        def constant(path, name):
            return re.search(rf'^{name} = "(.*)"$', path.read_text(), re.M).group(1)
        self.assertEqual(constant(SCRIPT, "SPACE"), constant(SCRIPT.with_name("design_surfaces.py"), "GO_SPACE"))


class HeadingFormsTest(Fixture):
    def read_as(self, text, heading, spelled, expected):
        self.put(text.replace(heading, spelled, 1))
        self.assertEqual(self.owed()[0], expected)

    def test_a_captain_amendments_heading_in_any_form_design_surfaces_accepts_is_read(self):
        text = task(amendments=[(1, "2026-10-15", "AC-4", "none")])
        for name, spelled in forms("## Captain amendments").items():
            with self.subTest(name):
                self.read_as(text, "## Captain amendments", spelled, 1)

    def test_an_amendment_entry_heading_in_any_form_design_surfaces_accepts_is_read(self):
        text = task(amendments=[(1, "2026-10-15", "AC-4", "none")])
        for name, spelled in forms("### Amendment 1", trailing=False).items():
            with self.subTest(name):
                self.read_as(text, "### Amendment 1", spelled, 1)

    def test_an_implementation_report_heading_in_any_form_design_surfaces_accepts_is_counted(self):
        text = task(repairs=4)
        for name, spelled in forms("## Stage Report: implementation").items():
            with self.subTest(name):
                self.read_as(text, "## Stage Report: implementation", spelled, 1)

    def test_an_fo_alignment_heading_in_any_form_design_surfaces_accepts_holds_the_call(self):
        text = task(repairs=4, extra=call(CE, "opus", "2026-10-16"))
        for name, spelled in forms("## FO alignment").items():
            with self.subTest(name):
                self.read_as(text, "## FO alignment", spelled, 0)

    def test_an_indented_sibling_heading_ends_each_section(self):
        cases = {
            "FO alignment": (task(repairs=4, after=call(CE, "opus", "2026-10-16")), 1),
            "Captain amendments": (task(amendments=[(1, "2026-10-15", "none", "none")], after="Supersedes: AC-4"), 0),
        }
        for name, (text, expected) in cases.items():
            for how, spelled in forms("## Stage Report: validation", trailing=False).items():
                if how in ("uppercase", "lowercase"):
                    continue
                with self.subTest(f"{name}, {how}"):
                    self.read_as(text, "## Stage Report: validation", spelled, expected)


class SymptomRoundsTest(Fixture):
    def dispatch(self, number, symptom="page freeze", stage="implementation", date="2026-11-03", base="", message=None):
        suffix = f"-message-{message}" if message is not None else ""
        path = self.state / f"{base}{SLUG}/dispatch/{stage}-{number}{suffix}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"Dispatched: {date} {'a' * 40}\nSymptom: {symptom}\n## Checklist\nwork\n")
        return path

    def test_worker_start_holds_the_three_recorded_states_until_both_calls_are_committed(self):
        amendments = [(n, "2026-11-09" if n == 6 else "2026-11-08", "AC-1" if n == 1 else "none", "revised design")
                      for n in range(1, 7)]
        ce, er = call(CE, "opus", "2026-11-09"), call(ER, "opus", "2026-11-09")
        for reports, failures, rounds in ((3, 1, 3), (4, 2, 4), (5, 2, 5)):
            for stage, count in (("implementation", rounds), ("validation", failures)):
                for n in range(1, count + 1):
                    self.dispatch(n, stage=stage, date="2026-11-09")
            for extra, expected in (("", 1), (ce, 1), (ce + "\n" + er, 0),
                                    (er + f"\nReviewer: {CE} not run 2026-11-09: the outcome is unchanged; the gap is testable now", 1)):
                with self.subTest(reports=reports, extra=extra):
                    body = task(reports=reports, amendments=amendments, extra=extra) + validations(*([StepBackTest.failed] * failures))
                    self.put(body)
                    code, out = run(self.state, SLUG)
                    self.assertEqual(code, expected, out)
                    if not extra:
                        self.assertIn(f"dispatch {CE}", out)
                        self.assertIn(f"dispatch {ER}", out)
            misplaced = task(reports=reports, amendments=amendments).replace("## FO alignment", "## Scope\n" + ce + "\n" + er + "\n\n## FO alignment")
            self.put(misplaced)
            self.assertEqual(run(self.state, SLUG)[0], 1)
            self.entity = self.state / f"{SLUG}.md"
            self.entity.write_text(task(reports=reports, amendments=amendments, extra=ce + "\n" + er))
            self.assertEqual(run(self.state, SLUG)[0], 1)

    def test_pending_third_record_holds_and_the_committed_worker_read_agrees(self):
        for n in (1, 2):
            self.dispatch(n)
        self.put(task())
        self.assertEqual(run(self.state, SLUG)[0], 0)
        pending = self.dispatch(3)
        code, out = run(self.state, SLUG, "--pending", pending)
        self.assertEqual(code, 1, out)
        self.assertIn("3 implementation dispatches", out)
        self.assertEqual(run(self.state, SLUG)[0], 0)
        self.put(task())
        self.assertEqual(run(self.state, SLUG), (code, out))
        self.assertEqual(run(self.state, SLUG, "--pending", pending), (code, out))

    def test_pending_replaces_one_record_and_does_not_read_the_task_from_disk(self):
        for n in (1, 2, 3):
            self.dispatch(n)
        self.put(task())
        pending = self.dispatch(3, symptom="another failure")
        (self.state / f"{SLUG}.md").write_text(task(extra=call(CE, "opus", "2026-11-03")))
        self.assertEqual(run(self.state, SLUG)[0], 1)
        code, out = run(self.state, SLUG, "--pending", pending)
        self.assertEqual(code, 0, out)
        self.assertIn("2 implementation dispatches", out)
        for bad in (pending.parent / "absent.md", pending.parent):
            self.assertEqual(run(self.state, SLUG, "--pending", bad)[0], 2)

    def test_one_plain_and_two_message_records_remind_then_owe_a_dated_call(self):
        self.dispatch(2)
        self.put(task())
        self.assertNotIn("next:", run(self.state, SLUG)[1])
        self.dispatch(2, message=1)
        self.put(task())
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 0, out)
        self.assertIn('2 implementation dispatches on symptom "page freeze"', out)
        self.dispatch(2, message=2, date="2026-11-05")
        self.assertEqual(run(self.state, SLUG), (code, out))
        self.put(task())
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 1, out)
        self.assertIn('3 implementation dispatches on symptom "page freeze"', out)
        self.assertIn(MECHANISM, out)
        self.put(task(extra=call(CE, "opus", "2026-11-04")))
        self.assertEqual(run(self.state, SLUG)[0], 1)
        self.put(task(extra=call(CE, "opus", "2026-11-05")))
        self.assertEqual(run(self.state, SLUG)[0], 0)

    def test_message_numbers_order_the_third_round_date_numerically(self):
        self.dispatch(2, date="2026-11-01")
        self.dispatch(2, message=10, date="2026-11-10")
        self.dispatch(2, message=2, date="2026-11-02")
        self.put(task(extra=call(CE, "opus", "2026-11-09")))
        self.assertEqual(run(self.state, SLUG)[0], 1)
        self.put(task(extra=call(CE, "opus", "2026-11-10")))
        self.assertEqual(run(self.state, SLUG)[0], 0)

    def test_second_advises_third_owes_and_only_committed_records_count(self):
        self.dispatch(2)
        self.put(task())
        self.assertNotIn("next:", run(self.state, SLUG)[1])
        self.dispatch(3)
        self.put(task())
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 0)
        self.assertIn('next: some-task has 2 implementation dispatches on symptom "page freeze"', out)
        self.dispatch(4)
        self.assertEqual(run(self.state, SLUG), (code, out))
        self.put(task())
        code, out = run(self.state, SLUG)
        self.assertEqual((code, out.count("next:")), (1, 1))
        self.assertIn('3 implementation dispatches on symptom "page freeze"', out)
        self.assertIn(MECHANISM, out)
        self.assertIn("not run <date>: unrelated: <finding> <its own cause>; <finding> <its own cause>", out)
        self.assertEqual(run(self.state, SLUG, "--rev", "HEAD~1")[0], 0)
        for path in (self.state / SLUG / "dispatch").iterdir():
            path.unlink()
        self.assertEqual(run(self.state, SLUG), (code, out))

    def test_date_model_and_waiver_clear_the_third_record_once(self):
        for number in (2, 3, 4, 5):
            self.dispatch(number, date="2026-11-04" if number == 5 else "2026-11-03")
        for line, expected in ((call(CE, "opus", "2026-11-02"), 1), (call(CE, "sonnet", "2026-11-03"), 1),
                               (call(CE, "opus", "2026-11-03"), 0), (call(CE, "gpt-6-astra", "2026-11-04"), 0),
                               (f"Reviewer: {CE} not run: reason", 1),
                               (f"Reviewer: {CE} not run 2026-11-02: reason", 1),
                               (f"Reviewer: {CE} not run 2026-11-03: reason", 1),
                               (f"Reviewer: {CE} not run: {UNRELATED}", 1),
                               (f"Reviewer: {CE} not run 2026-11-02: {UNRELATED}", 1),
                               (f"Reviewer: {CE} not run 2026-11-03: {UNRELATED}", 0)):
            with self.subTest(line=line):
                self.put(task(extra=line))
                self.assertEqual(run(self.state, SLUG)[0], expected)
                if not expected:
                    self.assertNotIn("next:", run(self.state, SLUG)[1])
        self.dispatch(4, date="")
        self.put(task(extra=f"Reviewer: {CE} not run: {UNRELATED}"))
        self.assertEqual(run(self.state, SLUG)[0], 0)

    def test_groups_normalize_but_keep_stages_and_symptoms_separate(self):
        from role_triggers import symptom_rounds
        rows = [("implementation-2.md", "Symptom: Validation-1  F1 Page freeze\n"),
                ("implementation-10.md", "Symptom: validation-1 f1 page freeze\n"),
                ("validation-3.md", "Symptom: validation-1 f1 page freeze\n"),
                ("implementation-3.md", "Symptom: B\n"),
                ("implementation-4.md", "Symptom: None: new work\n"),
                ("implementation-5.md", "```\nSymptom: B\n```\n"),
                ("implementation-6.md", "## Checklist\nSymptom: B\n"),
                ("implementation-7.md", "Symptom: C\nSymptom: B\n"),
                ("implementation-8-message-1.md", "Symptom: B\n")]
        groups = symptom_rounds(reversed(rows))
        self.assertEqual(groups[("implementation", "validation-1 f1 page freeze")], [(2, None), (10, None)])
        self.assertEqual(groups[("validation", "validation-1 f1 page freeze")], [(3, None)])
        self.assertEqual(groups[("implementation", "b")], [(3, None), (8, None)])
        self.assertEqual(len(groups), 4)

    def test_archived_folder_records_and_nested_state_checkout(self):
        for number in (2, 3, 4):
            self.dispatch(number, base="_archive/")
        self.put(task(), f"_archive/{SLUG}/index.md")
        self.assertEqual(run(self.state, SLUG)[0], 1)
        nested = self.state / "nested"
        nested.mkdir()
        git(self.state, "mv", "_archive", "nested/_archive")
        git(self.state, "commit", "-qm", "nested state")
        self.assertEqual(run(nested, SLUG)[0], 1)

    def test_cleared_symptom_cannot_mask_another_second_event_and_owed_questions_are_not_duplicated(self):
        for number in (2, 3, 4):
            self.dispatch(number)
        report = "\n## Stage Report: validation\n- F1 Material: gap\n"
        self.put(task(extra=call(CE, "opus", "2026-11-03")) + report * 2)
        self.assertIn("before the next step", run(self.state, SLUG)[1])
        for number in (5, 6):
            self.dispatch(number, symptom="new failure")
        self.put(task(extra=call(CE, "opus", "2026-11-03")))
        self.assertIn('2 implementation dispatches on symptom "new failure"', run(self.state, SLUG)[1])
        self.put(task() + report * 2)
        out = run(self.state, SLUG)[1]
        self.assertEqual(out.count(MECHANISM), 1)
        for question in StepBackTest.questions:
            self.assertEqual(out.count(question), 0)

    def test_both_findings_events_require_distinct_causes_in_the_decline(self):
        reasons = ((UNRELATED, 0),
                   ("Unrelated: F1 home exit; F2 late response; F3 slot removed", 0),
                   ("the outcome is unchanged; the gap is testable now", 1),
                   ("unrelated: F1 home exit", 1),
                   ("unrelated: F1 exit; F2 late response", 1),
                   ("unrelated: F1 late async write; F2 late async write", 1),
                   ("unrelated: F1 LATE  async WRITE; F2 late async write", 1),
                   ("unrelated: F1 home exit; F2 late response;", 1))
        for event in ("failures", "symptom"):
            if event == "symptom":
                for n in (1, 2, 3):
                    self.dispatch(n)
            for reason, expected in reasons:
                with self.subTest(event=event, reason=reason):
                    body = task(extra=f"Reviewer: {CE} not run 2026-11-03: {reason}")
                    if event == "failures":
                        body += validations(*([StepBackTest.failed] * 3))
                    self.put(body)
                    code, out = run(self.state, SLUG)
                    self.assertEqual(code, expected, out)
                    if expected:
                        self.assertIn(MECHANISM, out)

    def test_recorded_outcome_answers_leave_both_findings_calls_owed(self):
        answers = (
            "My answer is yes. The original problem is fixed: a first-time owner chooses the car only once, can see the plate-number step, and has a back button. The last few rounds dealt with smaller defects found in review, not a drift in direction.",
            "These two bugs are in the booking draft we're delivering. Tests can reproduce them now, and if we deleted those two acceptance criteria, the release would ship data loss.",
            "The goal is still the original one: an owner picks the car once and can always see how to finish the booking. The remaining gaps can all be tested now.",
            "the outcome is unchanged; the gap is testable now",
        )
        for event in ("failures", "symptom"):
            if event == "symptom":
                for n in (1, 2, 3):
                    self.dispatch(n)
            for answer in answers:
                with self.subTest(event=event, answer=answer):
                    body = task(extra=f"Reviewer: {CE} not run 2026-11-09: {answer}")
                    if event == "failures":
                        body += validations(*([StepBackTest.failed] * 3))
                    self.put(body)
                    code, out = run(self.state, SLUG)
                    self.assertEqual(code, 1, out)
                    self.assertIn(MECHANISM, out)


class BudgetTest(Fixture):
    def record(self, stage, number, header=True, commit=True):
        path = self.state / f"{SLUG}/dispatch/{stage}-{number}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {stage}-{number}\nDispatched: 2026-11-11\n"
                        + ("Budget: One cycle per stage.\n" if header else "")
                        + f"Symptom: failure {number}\n## Checklist\nwork\n")
        if commit:
            self.put(self.body)
        return path

    def seed(self, value="One cycle per stage.", extra=""):
        self.body = task() + f"\n## Budget\n- {value}\n" + extra
        self.put(self.body)

    def test_fixed_forms_are_narrow_and_case_insensitive(self):
        from role_triggers import budget_bound, budget_text
        for value, expected in (("ONE cycle per stage.", (1, 1)),
                ("10 cycles per stage; bounded work", (10, 10)),
                ("two implementation and three validation cycles", (2, 3)),
                ("one implementation and 1 validation cycle.", (1, 1)),
                ("2 ideation, 1 implementation and 2 validation cycles", (2, 1, 2)),
                ("two ideation, one implementation and two validation cycles, in one package PR.", (2, 1, 2)),
                ("One ideation, one implementation and one validation cycle", (1, 1, 1))):
            self.assertEqual(tuple(budget_bound(value).values()), expected)
        for value in ("one round per stage", "one package PR", "at most 3 days", "eleven cycles per stage",
                      "one cycle per stagecoach", "one implementation and two validation cyclesextra"):
            self.assertIsNone(budget_bound(value), value)
        self.assertEqual(budget_text("## Budget and stop condition\nBudget: one cycle per stage.\n"),
                         "one cycle per stage.")

    def test_total_dispatch_cap_counts_stages_and_named_followups_once(self):
        self.seed("at most 4 dispatches total")
        self.record("ideation", 1)
        self.record("implementation", 1)
        self.record("validation", 1)
        self.record("implementation", "1-message-1")
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 0, out)
        self.assertIn("total dispatches 4", out)
        pending = self.record("implementation", 2, commit=False)
        code, out = run(self.state, SLUG, "--pending", pending)
        self.assertEqual(code, 1, out)
        self.assertIn("budget exceeded", out)
        self.assertIn("total dispatches 5", out)
        self.put(self.body)
        self.assertEqual(run(self.state, SLUG, "--pending", pending), run(self.state, SLUG))

    def test_total_cap_counts_only_messages_with_a_named_header_symptom(self):
        self.seed("at most 1 dispatch total")
        self.record("implementation", 1)
        message = self.record("implementation", "1-message-1", commit=False)
        for body in ("Symptom: none\n## Checklist\nanswer\n",
                     "Symptom:  NoNe  \n## Checklist\nanswer\n",
                     "Symptom: \n## Checklist\nanswer\n",
                     "## Checklist\nanswer without a header\n",
                     "## Checklist\nSymptom: body text is not a header\n",
                     "```\nSymptom: fenced example\n```\nSymptom: NoNe\n"):
            message.write_text("Budget: at most 1 dispatch total\n" + body)
            code, out = run(self.state, SLUG, "--pending", message)
            self.assertEqual(code, 0, out)
            self.assertIn("total dispatches 1", out)
        message.write_text("Budget: at most 1 dispatch total\nSymptom: booking draft lost\n## Checklist\nrepair\n")
        code, out = run(self.state, SLUG, "--pending", message)
        self.assertEqual(code, 1, out)
        self.assertIn("total dispatches 2", out)
        self.assertIn("Symptom: booking draft lost", out)
        message.write_text("Symptom: nonempty draft lost\n## Checklist\nrepair\n")
        self.assertEqual(run(self.state, SLUG, "--pending", message)[0], 1)

    def test_total_cap_uses_record_count_not_the_highest_cycle_number(self):
        self.seed("最多 2 次派工，含一輪修正")
        self.record("implementation", 9)
        self.record("validation", 4)
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 0, out)
        self.assertIn("total dispatches 2", out)
        self.record("validation", "4-message-1")
        self.assertEqual(run(self.state, SLUG)[0], 1)

    def test_total_cap_ignores_special_role_records_and_legacy_tasks_stay_exempt(self):
        self.seed("at most one dispatch total")
        self.record("implementation", 1, header=False)
        self.record("chief-engineer", 1)
        self.record("engineering-reviewer", 1)
        self.record("implementation", 2)
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 0, out)
        self.assertIn("total dispatches 2", out)
        self.assertNotIn("budget exceeded", out)

    def test_countable_part_survives_an_explicit_minutes_clause(self):
        for index, value in enumerate(("240 cumulative agent-minutes, at most 2 dispatches total",
                      "240 累計代理分鐘、最多 2 次派工，含一輪修正",
                      "at most 2 dispatches total; 240 agent-minutes")):
            self.seed(value)
            if index == 0:
                self.record("implementation", 1)
                self.record("validation", 1)
            code, out = run(self.state, SLUG)
            self.assertEqual(code, 0, out)
            self.assertIn("Budget: " + value, out)
            self.assertIn("total dispatches 2", out)
            self.assertIn("minutes not counted", out)
            pending = self.record("implementation", 2, commit=False)
            self.assertEqual(run(self.state, SLUG, "--pending", pending)[0], 1)
            pending.unlink()

    def test_hold_states_the_preserve_report_stop_default_and_captain_override(self):
        self.seed()
        self.record("implementation", 2)
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 1, out)
        self.assertIn("keep the results, report the remaining work and stop adding", out)
        self.assertIn("unless the Captain replaces this outcome", out)

    def test_pending_overrun_holds_and_an_amendment_clears_it(self):
        self.seed()
        self.record("ideation", 1)
        self.record("implementation", 1)
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 0, out)
        self.assertIn("Budget: One cycle per stage.; spent ideation 1 of 2 by default, implementation 1, validation 0", out)
        pending = self.record("implementation", 2, commit=False)
        code, out = run(self.state, SLUG, "--pending", pending)
        self.assertEqual(code, 1, out)
        self.assertIn("budget exceeded; hold for the Captain", out)
        self.assertIn("Symptom: failure 2", out)
        for q in StepBackTest.questions:
            self.assertIn(q, out)
        self.assertEqual(run(self.state, SLUG)[0], 0)
        self.put(self.body)
        self.assertEqual(run(self.state, SLUG)[0], 1)
        self.body += ("\n## Captain amendments\n### Amendment 1 — 2026-11-11, chat\n"
                      "Captain: 「approved」\nAsked: approve two cycles per stage\n"
                      "Budget: two cycles per stage\nSupersedes: none\n")
        self.put(self.body)
        self.assertEqual(run(self.state, SLUG)[0], 0)
        self.assertIn("Budget: two cycles per stage; spent ideation 1 of 2 by default, implementation 2", run(self.state, SLUG)[1])

    def test_amendment_needs_the_same_entry_verbatim_words(self):
        self.seed()
        self.record("implementation", 2)
        for fields in ("Asked: more work\nBudget: two cycles per stage", "Asked: TWO cycles per stage\nBudget: two cycles per stage",
                       "Design: two cycles per stage\nBudget: two cycles per stage",
                       "Asked: two cycles per stage\n```\nBudget: two cycles per stage\n```",
                       "Asked: two cycles per stage\n### Amendment 2 — 2026-11-11, chat\nBudget: two cycles per stage"):
            body = self.body + "\n## Captain amendments\n### Amendment 1 — 2026-11-11, chat\nCaptain: 「ok」\n" + fields
            self.put(body)
            self.assertEqual(run(self.state, SLUG)[0], 1, fields)
        self.put(self.body + "\n## Captain amendments\n### Amendment 1 — 2026-11-11, chat\n"
                 "Budget: two cycles per stage\nCaptain: 「two cycles per stage」\nSupersedes: none\n")
        self.assertEqual(run(self.state, SLUG)[0], 0)

    def test_old_first_stage_record_never_opts_in_with_later_headers(self):
        self.seed()
        self.record("ideation", 1, header=False)
        self.record("implementation", 2)
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 0, out)
        self.assertIn("spent ideation 1 of 2 by default, implementation 2", out)
        self.assertNotIn("budget exceeded", out)

    def test_stage_bounds_and_followups_are_independent(self):
        self.seed("two implementation and one validation cycle")
        self.record("implementation", 2)
        self.record("validation", 1)
        self.record("implementation", "2-message-9")
        self.assertEqual(run(self.state, SLUG)[0], 0)
        self.record("validation", 2)
        self.assertEqual(run(self.state, SLUG)[0], 1)

    def test_first_record_is_chronological_and_pending_keeps_its_slot(self):
        self.seed()
        first = self.record("implementation", 1, header=False)
        self.record("ideation", 1)
        self.record("implementation", 2)
        self.assertEqual(run(self.state, SLUG)[0], 0)
        self.assertEqual(run(self.state, SLUG, "--pending", first)[0], 0)

    def test_uncountable_budget_prints_but_does_not_hold(self):
        self.seed("at most 3 days")
        self.record("implementation", 9)
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 0, out)
        self.assertIn("Budget: at most 3 days; spent implementation 9, validation 0; states no cycles", out)

    def test_countable_budget_removes_advisory_but_preserves_role_calls(self):
        self.seed("ten cycles per stage")
        self.put(self.body + validations(StepBackTest.failed, StepBackTest.failed))
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 0, out)
        self.assertNotIn("before the next step", out)
        self.put(self.body + validations(*([StepBackTest.failed] * 3)))
        code, out = run(self.state, SLUG)
        self.assertEqual(code, 1, out)
        self.assertIn(MECHANISM, out)
        self.assertNotIn("budget exceeded", out)


if __name__ == "__main__":
    unittest.main()
