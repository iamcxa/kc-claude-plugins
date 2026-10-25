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
    def test_four_repair_passes_owe_chief_engineer_in_every_record_shape(self):
        self.put(task(repairs=3))
        self.assertEqual(self.owed()[0], 0)
        self.put(task(repairs=4))
        code, lines = self.owed()
        self.assertEqual(code, 1)
        self.assertEqual(len(lines), 1)
        self.assertIn(f"dispatch {CE} ", lines[0])
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
        self.assertLessEqual(len(out.split()), 56)
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
        self.assertEqual((code, len(lines)), (1, 1))
        self.assertIn("has replacing amendments 1, 2, 4, 5, 6", lines[0])
        self.assertIn(f"dispatch {ER} on opus ", lines[0])
        self.assertLessEqual(len(lines[0].split()), 60)

    def test_an_amendment_is_cleared_by_a_call_or_a_dated_waiver_no_earlier_than_it(self):
        amendments = [(n, date, "AC-4", "none") for n, date in ((1, "2026-10-15"), (2, "2026-10-15"), (3, "2026-10-16"),
                                                                 (4, "2026-10-17"), (5, "2026-10-17"))]
        listed = lambda lines: re.search(r"amendments? ([\d, ]+)", lines[0]).group(1)
        self.put(task(amendments=amendments, extra=call(ER, "opus", "2026-10-16")))
        self.assertEqual(listed(self.owed()[1]), "4, 5")
        self.put(task(amendments=amendments, extra=f"Reviewer: {ER} not run 2026-10-16: widened scope only"))
        self.assertEqual(listed(self.owed()[1]), "4, 5")
        self.put(task(amendments=amendments, extra=f"Reviewer: {ER} not run: widened scope only"))
        self.assertEqual(listed(self.owed()[1]), "1, 2, 3, 4, 5")
        self.put(task(amendments=amendments, extra=call(ER, "opus", "2026-10-17")))
        self.assertEqual(self.owed()[0], 0)
        self.put(task(amendments=amendments[:1], extra=call(ER, "opus", "2026-10-15", "an unrelated question about a bridge")))
        self.assertEqual(self.owed()[0], 0)

    def test_calls_made_before_the_amendment_leave_it_owed(self):
        self.put(task(amendments=[(1, "2026-10-17", "AC-4", "none")],
                      extra=call(ER, "opus", "2026-10-15") + "\n" + call(ER, "opus", "2026-10-16")))
        self.assertEqual(self.owed()[0], 1)

    def test_a_replacing_amendment_names_the_model_the_profile_or_surface_requires(self):
        amendment = [(1, "2026-10-15", "AC-4", "none")]
        cases = (("prod", "none", "on fable (profile prod)"), ("pilot", "db", "on fable (Surfaces db)"),
                 ("prod", "db", "on fable (profile prod, Surfaces db)"), ("pilot", "none", "on opus "),
                 ("pilot", "ui, db", "on fable (Surfaces db)"))
        for profile, surfaces, expected in cases:
            with self.subTest(profile=profile, surfaces=surfaces):
                self.put(task(amendments=amendment, profile=profile).replace("Surfaces: none", f"Surfaces: {surfaces}"))
                lines = self.owed()[1]
                self.assertIn(f"dispatch {ER} {expected}", lines[0])
                self.assertLessEqual(len(lines[0].split()), 60)
        self.put(task(amendments=amendment, extra="```\nSurfaces: db\n```"))
        self.assertIn("on opus ", self.owed()[1][0])
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
        self.put(task(amendments=amendment, profile="prod", extra=f"Reviewer: {ER} not run 2026-10-18: widened only"))
        self.assertEqual(self.owed()[0], 0)

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


if __name__ == "__main__":
    unittest.main()
