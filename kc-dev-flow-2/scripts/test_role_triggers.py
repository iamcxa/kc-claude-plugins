#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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


def task(cycles=(), amendments=(), extra="", after=""):
    body = ["---", "title: t", "status: validation", "---", "", "## FO alignment", "", "Surfaces: none", extra, ""]
    if amendments:
        body += ["## Captain amendments", ""]
        for number, date, supersedes, design in amendments:
            body += [f"### Amendment {number} — {date}, chat", "Captain: 「ok」 (chat)", f"Supersedes: {supersedes}",
                     f"Design: {design}", ""]
    if cycles:
        body += ["### Feedback Cycles", ""] + [f"- Cycle {n} (FO, 2026-10-15): round {n}." for n in cycles] + [""]
    if after:
        body += ["## Stage Report: validation", "", after, ""]
    return "\n".join(body) + "\n"


class RoleTriggersTest(unittest.TestCase):
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

    def test_the_third_cycle_owes_chief_engineer_and_the_second_does_not(self):
        self.put(task(cycles=(1, 1, 2)))
        self.assertEqual(self.owed()[0], 0)
        self.put(task(cycles=(1, 2, 3)))
        code, lines = self.owed()
        self.assertEqual(code, 1)
        self.assertEqual(len(lines), 1)
        self.assertIn(f"dispatch {CE} ", lines[0])
        self.assertLessEqual(len(lines[0].split()), 52)

    def test_each_replacing_amendment_owes_engineering_reviewer_and_none_does_not(self):
        self.put(task(amendments=[(1, "2026-10-15", "AC-4", "none"), (2, "2026-10-15", "none", "the whole design"),
                                  (3, "2026-10-15", "none (no replacement: widened)", "none"),
                                  (4, "2026-10-16", "none", "none")]))
        code, lines = self.owed()
        self.assertEqual(code, 1)
        self.assertEqual([re.search(r"amendment (\d+)", line).group(1) for line in lines], ["1", "2"])
        self.assertIn(f"dispatch {ER} ", lines[0])
        self.assertLessEqual(len(lines[0].split()), 63)

    def test_fenced_text_is_not_an_event_and_a_fenced_line_clears_nothing(self):
        fixture = ("```bash\n### Feedback Cycles\n- Cycle 3 (FO): x\n```\n\n```md\n## Captain amendments\n"
                   "### Amendment 1 — 2026-10-16, chat\nSupersedes: AC-2\n```\n")
        self.put(task(extra=fixture))
        self.assertEqual(self.owed()[0], 0)
        self.put(task(cycles=(3,), extra=f"```\nReviewer: {CE} opus 2026-10-16 — Cycle 3: q\n```"))
        self.assertEqual(self.owed()[0], 1)

    def test_a_call_or_a_waiver_naming_the_event_clears_it(self):
        for line in (f"Reviewer: {CE} opus 2026-10-16 — Cycle 3: what next?",
                     f"- Reviewer: {CE} opus 2026-10-16 - Cycle 3: what next?",
                     f"Reviewer: {CE} not run: Captain ordered the cycles. Cycle 3"):
            with self.subTest(line=line):
                self.put(task(cycles=(3,), extra=line))
                self.assertEqual(self.owed()[0], 0)
        for line in (f"Reviewer: {ER} opus 2026-10-15 — Amendment 1: q",
                     f"Reviewer: {ER} not run: only widened scope (Amendment 1)"):
            with self.subTest(line=line):
                self.put(task(amendments=[(1, "2026-10-15", "AC-4", "none")], extra=line))
                self.assertEqual(self.owed()[0], 0)

    def test_each_near_miss_leaves_the_event_owed(self):
        cases = {
            "wrong agent": f"Reviewer: {ER} opus 2026-10-16 — Cycle 3: q",
            "other seat": "Reviewer: design-reviewer opus 2026-10-16 — Cycle 3: q",
            "blank reason": f"Reviewer: {CE} not run: Cycle 3",
            "no reason text": f"Reviewer: {CE} not run: ( ) Cycle 3",
            "no token": f"Reviewer: {CE} opus 2026-10-16 — what next?",
            "waiver no token": f"Reviewer: {CE} not run: busy",
            "Cycle 30": f"Reviewer: {CE} opus 2026-10-16 — Cycle 30: q",
            "prose": f"FO considered Reviewer: {CE} opus 2026-10-16 — Cycle 3: q",
        }
        for name, line in cases.items():
            with self.subTest(name):
                self.put(task(cycles=(3,), extra=line))
                self.assertEqual(self.owed()[0], 1)

    def test_an_amendment_call_naming_another_number_is_owed(self):
        for line in (f"Reviewer: {ER} opus 2026-10-15 — Amendment 10: q", f"Reviewer: {ER} opus 2026-10-15 — Amendment 2: q"):
            with self.subTest(line=line):
                self.put(task(amendments=[(1, "2026-10-15", "AC-4", "none")], extra=line))
                self.assertEqual(self.owed()[0], 1)

    def test_an_amendment_call_dated_no_earlier_than_the_entry_clears_it(self):
        amendment = [(1, "2026-10-15", "AC-4", "none")]
        for date, owed in (("2026-10-15", 0), ("2026-10-17", 0), ("2026-10-14", 1)):
            with self.subTest(date=date):
                self.put(task(amendments=amendment, extra=f"Reviewer: {ER} opus {date} — Amendment 1: q"))
                self.assertEqual(self.owed()[0], owed)

    def test_only_the_fo_alignment_section_can_clear_an_event(self):
        call, waiver = f"Reviewer: {CE} opus 2026-10-16 — Cycle 3: q", f"Reviewer: {CE} not run: Captain ordered Cycle 3"
        for name, line in (("call", call), ("waiver", waiver)):
            with self.subTest(name + " in another section"):
                self.put(task(cycles=(3,), after=line))
                self.assertEqual(self.owed()[0], 1)
            with self.subTest(name + " in FO alignment"):
                self.put(task(cycles=(3,), extra=line))
                self.assertEqual(self.owed()[0], 0)
            with self.subTest(name + " under a subheading of FO alignment"):
                self.put(task(cycles=(3,), extra=f"### Roles\n\n{line}"))
                self.assertEqual(self.owed()[0], 0)

    def test_it_judges_committed_bytes_and_leaves_the_checkout_unchanged(self):
        self.put(task(cycles=(3,)))
        (self.state / f"{SLUG}.md").write_text(task(cycles=(3,), extra=f"Reviewer: {CE} not run: busy Cycle 3"))
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
        self.put(task(cycles=(3,)), f"_archive/{SLUG}.md")
        self.assertEqual(self.owed()[0], 1)
        git(self.state, "rm", "-q", f"_archive/{SLUG}.md")
        self.put(task(cycles=(3,)), f"{SLUG}/index.md")
        self.assertEqual(self.owed()[0], 1)


if __name__ == "__main__":
    unittest.main()
