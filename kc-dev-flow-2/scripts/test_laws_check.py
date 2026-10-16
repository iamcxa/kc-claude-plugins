#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
RUNNER = SCRIPTS / "laws_check.py"
LAWS_FILE = SCRIPTS.parent / "references/sd/laws.md"
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
SHA = "a" * 40


def git(where, *args):
    done = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True, env={**os.environ, **IDENTITY})
    assert done.returncode == 0, f"git {args}: {done.stderr}"
    return done.stdout.strip()


def task(pr="", body=""):
    return f"---\ntitle: t\nstatus: implementation\npr: {pr}\n---\n{body}\n"


def record(*, checklist="- do the work", root="/pkg", completion=True):
    scope = f"Package root: {root}\n" + ("Send the completion message to `main`.\n" if completion else "")
    return f"Dispatched: 2026-10-16 {SHA}\nModel: sonnet\n\n## Checklist\n\n{checklist}\n\n## Scope notes\n\n{scope}"


class Repo:
    def __init__(self, base):
        self.path = Path(base)
        self.path.mkdir(parents=True)
        git(self.path, "init", "-b", "main")

    def commit(self, message, **files):
        for name, text in files.items():
            path = self.path / (name.replace("__", "/") + ".md")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        git(self.path, "add", "-A")
        git(self.path, "commit", "-m", message)
        return git(self.path, "rev-parse", "HEAD")


def sandbox(base, omit=(), override=None):
    pkg = Path(base) / "pkg"
    (pkg / "scripts").mkdir(parents=True)
    for name in ("laws_check.py", "decision_ledger.py", "observer_check.py", "dispatch_records.py"):
        if name not in omit:
            shutil.copy(SCRIPTS / name, pkg / "scripts" / name)
    for name, text in (override or {}).items():
        (pkg / "scripts" / name).write_text(text)
    return pkg / "scripts" / "laws_check.py"


def laws(state, *args, runner=RUNNER):
    done = subprocess.run([sys.executable, "-B", str(runner), str(state), *map(str, args)], capture_output=True, text=True,
                          env={**os.environ, **IDENTITY})
    return done.returncode, done.stdout + done.stderr


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.learn = self.tmp / "readme-learn.md"
        self.learn.write_text("---\nextensions: [roborev, learn]\n---\n")
        self.plain = self.tmp / "readme-plain.md"
        self.plain.write_text("---\nextensions: [roborev]\n---\n")

    def l1(self, repo, anchor, *extra, readme=None, **kw):
        return laws(repo.path, "--readme", readme or self.learn, "--anchor", f"L1={anchor}", *extra, **kw)

    def violating(self, name="v"):
        repo = Repo(self.tmp / name)
        anchor = repo.commit("base", keep="x")
        repo.commit("task", t=task())
        repo.commit("sentinel without a report", t=task("pr-merge:7"))
        return repo, anchor


class RegistryTest(unittest.TestCase):
    def test_laws_file_matches_registry(self):
        sys.path.insert(0, str(SCRIPTS))
        import laws_check
        registered = {f"{law_id} {name}" for law_id, (name, _) in laws_check.LAWS.items()}
        headings = set(re.findall(r"^## (L\d+ [\w-]+)$", LAWS_FILE.read_text(), re.M))
        self.assertEqual(registered, headings)


class ExitContractTest(Base):
    def test_held_exits_0_and_violated_exits_1(self):
        repo = Repo(self.tmp / "ok")
        anchor = repo.commit("base", keep="x")
        repo.commit("task", t=task())
        repo.commit("report", t__observer="report")
        repo.commit("sentinel", t=task("pr-merge:7"))
        code, out = self.l1(repo, anchor)
        self.assertEqual((code, "1 events judged" in out), (0, True), out)
        bad, bad_anchor = self.violating()
        code, out = self.l1(bad, bad_anchor)
        self.assertEqual(code, 1, out)
        self.assertIn("violation: L1 observer-before-sentinel task=t", out)

    def test_no_anchor_exits_2(self):
        repo, _ = self.violating()
        code, out = laws(repo.path)
        self.assertEqual(code, 2)
        self.assertIn("no anchor given", out)

    def test_unknown_law_exits_2(self):
        repo, anchor = self.violating()
        code, out = laws(repo.path, "--anchor", f"L9={anchor}")
        self.assertEqual(code, 2)
        self.assertIn("unknown law L9", out)

    def test_shallow_history_exits_2(self):
        repo, anchor = self.violating()
        shallow = self.tmp / "shallow"
        subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{repo.path}", str(shallow)], check=True,
                       env={**os.environ, **IDENTITY})
        code, out = laws(shallow, "--readme", self.learn, "--anchor", f"L1={anchor}")
        self.assertEqual(code, 2)
        self.assertIn("history is shallow", out)

    def test_rev_that_is_not_a_commit_exits_2(self):
        repo, anchor = self.violating()
        code, out = self.l1(repo, anchor, "--rev", "no-such-rev")
        self.assertEqual(code, 2)
        self.assertIn("--rev no-such-rev names no commit", out)

    def test_anchor_that_is_not_a_commit_exits_2(self):
        repo, _ = self.violating()
        code, out = self.l1(repo, "deadbeef")
        self.assertEqual(code, 2)
        self.assertIn("is not a commit", out)

    def test_anchor_that_is_not_an_ancestor_exits_2(self):
        repo, anchor = self.violating()
        git(repo.path, "checkout", "-q", "-b", "side", anchor)
        side = repo.commit("side", other="y")
        git(repo.path, "checkout", "-q", "main")
        code, out = self.l1(repo, side)
        self.assertEqual(code, 2)
        self.assertIn("is not an ancestor of", out)

    def test_missing_script_exits_2(self):
        repo, anchor = self.violating()
        for omit in ("observer_check.py", "decision_ledger.py"):
            code, out = self.l1(repo, anchor, runner=sandbox(self.tmp / f"no-{omit}", omit=(omit,)))
            self.assertEqual(code, 2, out)
            self.assertRegex(out, rf"script missing: \S*pkg/scripts/{omit}")

    def test_check_exiting_2_exits_2_naming_the_cause(self):
        repo, anchor = self.violating()
        stub = "import sys\nprint('cannot tell: stub')\nsys.exit(2)\n"
        code, out = self.l1(repo, anchor, runner=sandbox(self.tmp / "s2", override={"observer_check.py": stub}))
        self.assertEqual(code, 2)
        self.assertIn("observer_check.py exited 2: cannot tell: stub", out)

    def test_check_printing_a_traceback_exits_2_not_1(self):
        repo, anchor = self.violating()
        stub = "raise RuntimeError('stub boom')\n"
        code, out = self.l1(repo, anchor, runner=sandbox(self.tmp / "tb", override={"observer_check.py": stub}))
        self.assertEqual(code, 2)
        self.assertIn("observer_check.py crashed: RuntimeError: stub boom", out)

    def test_check_exiting_1_with_an_unparseable_line_exits_2(self):
        repo, anchor = self.violating()
        stub = "import sys\nprint('something new')\nsys.exit(1)\n"
        code, out = self.l1(repo, anchor, runner=sandbox(self.tmp / "up", override={"observer_check.py": stub}))
        self.assertEqual(code, 2)
        self.assertIn("output this runner does not parse", out)

    def test_check_exiting_1_with_no_stdout_exits_2(self):
        repo, anchor = self.violating()
        stub = "import sys\nprint('crash note', file=sys.stderr)\nsys.exit(1)\n"
        code, out = self.l1(repo, anchor, runner=sandbox(self.tmp / "q1", override={"observer_check.py": stub}))
        self.assertEqual(code, 2, out)
        self.assertIn("observer_check.py exited 1 with no output: crash note", out)

    def test_l2_check_exiting_1_with_no_stdout_exits_2_in_either_mode(self):
        repo = Repo(self.tmp / "q2")
        anchor = repo.commit("base", keep="x")
        repo.commit("record", t__dispatch__a=record())
        for mode, argv_test in (("folder", "'--names' not in sys.argv"), ("names", "'--names' in sys.argv")):
            stub = ("import sys\nif " + argv_test + ":\n    print('crash note', file=sys.stderr)\n    sys.exit(1)\n"
                    "sys.exit(0)\n")
            runner = sandbox(self.tmp / f"q2-{mode}", override={"dispatch_records.py": stub})
            code, out = laws(repo.path, "--anchor", f"L2={anchor}", runner=runner)
            self.assertEqual(code, 2, f"{mode}: {out}")
            self.assertIn("dispatch_records.py exited 1 with no output: crash note", out)

    def test_l1_without_readme_exits_2(self):
        repo, anchor = self.violating()
        code, out = laws(repo.path, "--anchor", f"L1={anchor}")
        self.assertEqual(code, 2)
        self.assertIn("L1 needs --readme", out)

    def test_exit_2_wins_over_a_violation_and_both_print(self):
        repo, anchor = self.violating()
        code, out = laws(repo.path, "--readme", self.learn, "--anchor", f"L1={anchor}", "--anchor", "L2=deadbeef")
        self.assertEqual(code, 2)
        self.assertIn("violation: L1", out)
        self.assertIn("L2 dispatch-record-complete: cannot judge", out)


class L1Test(Base):
    def test_observer_before_the_sentinel_is_held_and_none_is_violated(self):
        repo = Repo(self.tmp / "a")
        anchor = repo.commit("base", keep="x")
        repo.commit("task", t=task())
        repo.commit("report", t__observer="report")
        repo.commit("sentinel", t=task("pr-merge:7"))
        self.assertEqual(self.l1(repo, anchor)[1].splitlines()[0],
                         f"L1 observer-before-sentinel: 1 events judged after {anchor[:12]}, 0 violated")
        bad, bad_anchor = self.violating()
        self.assertIn("1 events judged", self.l1(bad, bad_anchor)[1])
        self.assertIn("1 violated", self.l1(bad, bad_anchor)[1])

    def test_a_report_committed_after_the_sentinel_is_violated_though_the_tip_passes(self):
        repo, anchor = self.violating("late")
        repo.commit("late report", t__observer="report")
        tip = subprocess.run([sys.executable, str(SCRIPTS / "observer_check.py"), str(repo.path), "t"], capture_output=True)
        self.assertEqual(tip.returncode, 0)
        code, out = self.l1(repo, anchor)
        self.assertEqual(code, 1, out)
        self.assertIn("observer report not committed", out)

    def test_a_task_body_quoting_the_sentinel_is_not_an_event(self):
        repo = Repo(self.tmp / "prose")
        anchor = repo.commit("base", keep="x")
        repo.commit("task", t=task(body="Example:\npr: pr-merge:7\n"))
        code, out = self.l1(repo, anchor)
        self.assertEqual(code, 0, out)
        self.assertIn("0 events judged", out)

    def test_a_sentinel_at_or_before_the_anchor_is_not_judged(self):
        repo = Repo(self.tmp / "old")
        repo.commit("base", keep="x")
        repo.commit("task", t=task())
        sentinel = repo.commit("sentinel", t=task("pr-merge:7"))
        repo.commit("later", other="y")
        self.assertIn("0 events judged", self.l1(repo, sentinel)[1])

    def test_a_readme_without_learn_judges_nothing(self):
        repo, anchor = self.violating("nolearn")
        code, out = self.l1(repo, anchor, readme=self.plain)
        self.assertEqual(code, 0, out)
        self.assertIn("0 events judged (README lists no learn)", out)

    def test_a_task_archived_after_its_sentinel_keeps_its_sentinel_commit(self):
        repo, anchor = self.violating("arch")
        git(repo.path, "mv", "t.md", "_archive_t.md")
        (repo.path / "_archive").mkdir()
        git(repo.path, "mv", "_archive_t.md", "_archive/t.md")
        git(repo.path, "commit", "-q", "-m", "archive")
        code, out = self.l1(repo, anchor)
        self.assertEqual(code, 1, out)
        self.assertIn("task=t", out)


class L2Test(Base):
    def test_records_after_the_anchor_are_judged_by_part_and_older_ones_are_not(self):
        repo = Repo(self.tmp / "l2")
        repo.commit("base", keep="x")
        repo.commit("old bad", t__dispatch__old_bad=record(completion=False))
        repo.commit("moved bad", t__dispatch__moved_bad=record(completion=False))
        anchor = repo.commit("anchor", other="y")
        repo.commit(
            "records",
            t__dispatch__complete=record(),
            t__dispatch__no_main=record(completion=False),
            t__dispatch__no_root=record(root="pkg"),
            t__dispatch__bare=record(checklist="- run observer_check.py"),
            t__dispatch__pointer=record(checklist="Same checklist as complete."),
        )
        git(repo.path, "mv", "t", "_t")
        (repo.path / "_archive").mkdir()
        git(repo.path, "mv", "_t", "_archive/t")
        git(repo.path, "commit", "-q", "-m", "archive")
        code, out = laws(repo.path, "--anchor", f"L2={anchor}")
        self.assertEqual(code, 1, out)
        self.assertIn("5 events judged", out)
        self.assertIn("4 violated", out)
        for name, part in (("no_main", "completion recipient"), ("no_root", "'Package root:'"),
                           ("bare", "bare package script name observer_check.py"),
                           ("pointer", "needs a checklist of its own")):
            self.assertRegex(out, rf"record=t/dispatch/{name}\.md .*{re.escape(part)}")
        self.assertNotIn("old_bad", out)
        self.assertNotIn("moved_bad", out)
        self.assertNotIn("dispatch/complete.md", out)

    def test_a_record_corrected_after_it_was_added_is_still_judged_as_added(self):
        repo = Repo(self.tmp / "l2-fixed")
        anchor = repo.commit("base", keep="x")
        added = repo.commit("bad record", t__dispatch__a=record(completion=False))
        repo.commit("corrected", t__dispatch__a=record())
        code, out = laws(repo.path, "--anchor", f"L2={anchor}")
        self.assertEqual(code, 1, out)
        self.assertRegex(out, rf"record=t/dispatch/a\.md commit={added[:12]} .*completion recipient")

    def test_a_record_deleted_after_it_was_added_is_still_judged_as_added(self):
        repo = Repo(self.tmp / "l2-gone")
        anchor = repo.commit("base", keep="x")
        repo.commit("bad record", t__dispatch__a=record(completion=False), t__dispatch__b=record())
        git(repo.path, "rm", "-q", "t/dispatch/a.md")
        git(repo.path, "commit", "-q", "-m", "delete")
        code, out = laws(repo.path, "--anchor", f"L2={anchor}")
        self.assertEqual(code, 1, out)
        self.assertIn("2 events judged", out)
        self.assertIn("record=t/dispatch/a.md", out)

    def test_a_pointer_is_judged_against_the_folder_at_the_commit_that_added_it(self):
        repo = Repo(self.tmp / "l2-sibling")
        anchor = repo.commit("base", keep="x")
        repo.commit("records", t__dispatch__a=record(), t__dispatch__b=record(checklist="Same checklist as a."))
        git(repo.path, "rm", "-q", "t/dispatch/a.md")
        git(repo.path, "commit", "-q", "-m", "delete the sibling")
        code, out = laws(repo.path, "--anchor", f"L2={anchor}")
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"record=t/dispatch/b\.md .*needs a checklist of its own")

    def test_a_record_without_a_commit_that_added_it_cannot_be_judged(self):
        repo = Repo(self.tmp / "l2-none")
        anchor = repo.commit("base", keep="x")
        repo.commit("record", t__dispatch__a=record())
        stub = (SCRIPTS / "laws_check.py").read_text().replace('"--diff-filter=A"', '"--diff-filter=D"')
        code, out = laws(repo.path, "--anchor", f"L2={anchor}", runner=sandbox(self.tmp / "nr", override={"laws_check.py": stub}))
        self.assertEqual(code, 2)
        self.assertIn("no commit found that added", out)


if __name__ == "__main__":
    unittest.main()
