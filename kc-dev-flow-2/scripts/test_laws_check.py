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
TEMPLATE = SCRIPTS.parent / "references/sd/state-laws.workflow.yml"
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

    def judge(self, repo, before, after=None, *extra, readme=None, **kw):
        return laws(repo.path, "--before", before, *(["--after", after] if after else []), "--readme", readme or self.learn,
                    *extra, **kw)

    def violating(self, name="v"):
        repo = Repo(self.tmp / name)
        before = repo.commit("base", keep="x")
        repo.commit("task", t=task())
        repo.commit("sentinel without a report", t=task("pr-merge:7"))
        return repo, before


class RegistryTest(unittest.TestCase):
    def test_laws_file_matches_registry(self):
        sys.path.insert(0, str(SCRIPTS))
        import laws_check
        registered = {f"{law_id} {name}" for law_id, (name, _) in laws_check.LAWS.items()}
        headings = set(re.findall(r"^## (L\d+ [\w-]+)$", LAWS_FILE.read_text(), re.M))
        self.assertEqual(registered, headings)


class WorkflowTemplateTest(unittest.TestCase):
    def test_template_has_no_concurrency_block_that_could_cancel_a_push_run(self):
        lines = [line for line in TEMPLATE.read_text().splitlines() if not line.lstrip().startswith("#")]
        self.assertEqual([line for line in lines if re.match(r"\s*(concurrency|cancel-in-progress)\s*:", line)], [])


class ExitContractTest(Base):
    def test_held_exits_0_and_violated_exits_1(self):
        repo = Repo(self.tmp / "ok")
        before = repo.commit("base", keep="x")
        repo.commit("task", t=task())
        repo.commit("report", t__observer="report")
        repo.commit("sentinel", t=task("pr-merge:7"))
        code, out = self.judge(repo, before)
        self.assertEqual((code, "1 events judged" in out), (0, True), out)
        bad, bad_before = self.violating()
        code, out = self.judge(bad, bad_before)
        self.assertEqual(code, 1, out)
        self.assertIn("violation: L1 observer-before-sentinel task=t", out)

    def test_no_before_exits_2(self):
        repo, _ = self.violating()
        code, out = laws(repo.path, "--readme", self.learn)
        self.assertEqual(code, 2)
        self.assertIn("--before", out)

    def test_before_all_zeros_exits_2(self):
        repo, _ = self.violating()
        code, out = self.judge(repo, "0" * 40)
        self.assertEqual(code, 2)
        self.assertIn(f"--before {'0' * 40} names no commit", out)

    def test_before_or_after_that_is_not_a_commit_exits_2(self):
        repo, before = self.violating()
        code, out = self.judge(repo, "deadbeef")
        self.assertEqual((code, "--before deadbeef names no commit" in out), (2, True), out)
        code, out = self.judge(repo, before, "no-such-rev")
        self.assertEqual((code, "--after no-such-rev names no commit" in out), (2, True), out)

    def test_a_range_commit_with_no_parent_in_the_clone_exits_2(self):
        repo = Repo(self.tmp / "deep")
        root = repo.commit("base", keep="x")
        git(repo.path, "checkout", "-q", "-b", "side")
        side = repo.commit("side", other="y")
        git(repo.path, "checkout", "-q", "main")
        repo.commit("task", t=task())
        repo.commit("report", t__observer="report")
        repo.commit("sentinel", t=task("pr-merge:7"))
        shallow = self.tmp / "shallow"
        subprocess.run(["git", "clone", "-q", "--depth", "2", "--no-single-branch", f"file://{repo.path}", str(shallow)],
                       check=True, env={**os.environ, **IDENTITY})
        code, out = laws(shallow, "--before", side, "--after", "origin/main", "--readme", self.learn)
        self.assertEqual(code, 2, out)
        self.assertRegex(out, r"cannot judge: [0-9a-f]{12} has no parent here")
        self.assertNotIn("events judged", out)
        self.assertNotEqual(root, side)

    def test_missing_script_exits_2(self):
        repo, before = self.violating()
        for omit in ("observer_check.py", "decision_ledger.py"):
            code, out = self.judge(repo, before, runner=sandbox(self.tmp / f"no-{omit}", omit=(omit,)))
            self.assertEqual(code, 2, out)
            self.assertRegex(out, rf"script missing: \S*pkg/scripts/{omit}")

    def test_check_exiting_2_exits_2_naming_the_cause(self):
        repo, before = self.violating()
        stub = "import sys\nprint('cannot tell: stub')\nsys.exit(2)\n"
        code, out = self.judge(repo, before, runner=sandbox(self.tmp / "s2", override={"observer_check.py": stub}))
        self.assertEqual(code, 2)
        self.assertIn("observer_check.py exited 2: cannot tell: stub", out)

    def test_check_printing_a_traceback_exits_2_not_1(self):
        repo, before = self.violating()
        stub = "raise RuntimeError('stub boom')\n"
        code, out = self.judge(repo, before, runner=sandbox(self.tmp / "tb", override={"observer_check.py": stub}))
        self.assertEqual(code, 2)
        self.assertIn("observer_check.py crashed: RuntimeError: stub boom", out)

    def test_check_exiting_1_with_an_unparseable_line_exits_2(self):
        repo, before = self.violating()
        stub = "import sys\nprint('something new')\nsys.exit(1)\n"
        code, out = self.judge(repo, before, runner=sandbox(self.tmp / "up", override={"observer_check.py": stub}))
        self.assertEqual(code, 2)
        self.assertIn("output this runner does not parse", out)

    def test_check_exiting_1_with_no_stdout_exits_2(self):
        repo, before = self.violating()
        stub = "import sys\nprint('crash note', file=sys.stderr)\nsys.exit(1)\n"
        code, out = self.judge(repo, before, runner=sandbox(self.tmp / "q1", override={"observer_check.py": stub}))
        self.assertEqual(code, 2, out)
        self.assertIn("observer_check.py exited 1 with no output: crash note", out)

    def test_l2_check_exiting_1_with_no_stdout_exits_2_in_either_mode(self):
        repo = Repo(self.tmp / "q2")
        before = repo.commit("base", keep="x")
        repo.commit("record", t__dispatch__a=record())
        for mode, argv_test in (("folder", "'--names' not in sys.argv"), ("names", "'--names' in sys.argv")):
            stub = ("import sys\nif " + argv_test + ":\n    print('crash note', file=sys.stderr)\n    sys.exit(1)\n"
                    "sys.exit(0)\n")
            runner = sandbox(self.tmp / f"q2-{mode}", override={"dispatch_records.py": stub})
            code, out = self.judge(repo, before, runner=runner)
            self.assertEqual(code, 2, f"{mode}: {out}")
            self.assertIn("dispatch_records.py exited 1 with no output: crash note", out)

    def test_l1_without_readme_exits_2(self):
        repo, before = self.violating()
        code, out = laws(repo.path, "--before", before)
        self.assertEqual(code, 2)
        self.assertIn("L1 needs --readme", out)

    def test_exit_2_wins_over_a_violation_and_both_print(self):
        repo, before = self.violating()
        code, out = self.judge(repo, before, runner=sandbox(self.tmp / "no-dr", omit=("dispatch_records.py",)))
        self.assertEqual(code, 2)
        self.assertIn("violation: L1", out)
        self.assertIn("L2 dispatch-record-complete: cannot judge", out)


class L1Test(Base):
    def test_observer_before_the_sentinel_is_held_and_none_is_violated(self):
        repo = Repo(self.tmp / "a")
        before = repo.commit("base", keep="x")
        repo.commit("task", t=task())
        repo.commit("report", t__observer="report")
        after = repo.commit("sentinel", t=task("pr-merge:7"))
        self.assertEqual(self.judge(repo, before)[1].splitlines()[0],
                         f"L1 observer-before-sentinel: 1 events judged in {before[:12]}..{after[:12]}, 0 violated")
        bad, bad_before = self.violating()
        out = self.judge(bad, bad_before)[1]
        self.assertIn("1 events judged", out)
        self.assertIn("1 violated", out)

    def test_a_report_committed_after_the_sentinel_is_violated_though_the_tip_passes(self):
        repo, before = self.violating("late")
        repo.commit("late report", t__observer="report")
        tip = subprocess.run([sys.executable, str(SCRIPTS / "observer_check.py"), str(repo.path), "t"], capture_output=True)
        self.assertEqual(tip.returncode, 0)
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertIn("observer report not committed", out)

    def test_a_task_body_quoting_the_sentinel_is_not_an_event(self):
        repo = Repo(self.tmp / "prose")
        before = repo.commit("base", keep="x")
        repo.commit("task", t=task(body="Example:\npr: pr-merge:7\n"))
        code, out = self.judge(repo, before)
        self.assertEqual(code, 0, out)
        self.assertIn("0 events judged", out)

    def test_a_sentinel_written_in_an_earlier_push_is_not_judged(self):
        repo = Repo(self.tmp / "old")
        repo.commit("base", keep="x")
        repo.commit("task", t=task())
        sentinel = repo.commit("sentinel", t=task("pr-merge:7"))
        repo.commit("later", other="y")
        self.assertIn("0 events judged", self.judge(repo, sentinel)[1])

    def test_a_task_edited_after_its_sentinel_is_no_new_event(self):
        repo, before = self.violating("edit")
        sentinel = git(repo.path, "rev-parse", "HEAD")
        repo.commit("edit the body", t=task("pr-merge:7", body="more"))
        self.assertIn("0 events judged", self.judge(repo, sentinel)[1])
        self.assertIn("1 events judged", self.judge(repo, before)[1])

    def test_a_readme_without_learn_judges_nothing(self):
        repo, before = self.violating("nolearn")
        code, out = self.judge(repo, before, readme=self.plain)
        self.assertEqual(code, 0, out)
        self.assertIn("0 events judged (README lists no learn)", out)

    def test_an_archive_move_that_leaves_the_sentinel_unchanged_is_no_event(self):
        repo, _ = self.violating("arch")
        sentinel = git(repo.path, "rev-parse", "HEAD")
        (repo.path / "_archive").mkdir()
        git(repo.path, "mv", "t.md", "_archive/t.md")
        git(repo.path, "commit", "-q", "-m", "archive")
        code, out = self.judge(repo, sentinel)
        self.assertEqual(code, 0, out)
        self.assertIn("0 events judged", out)

    def test_a_task_deleted_later_in_the_same_push_is_still_judged(self):
        repo, before = self.violating("gone")
        git(repo.path, "rm", "-q", "t.md")
        git(repo.path, "commit", "-q", "-m", "delete the task")
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertIn("1 events judged", out)
        self.assertIn("task=t", out)

    def test_a_rework_that_clears_pr_and_a_second_sentinel_is_judged_again(self):
        repo = Repo(self.tmp / "rework")
        before = repo.commit("base", keep="x")
        repo.commit("task", t=task())
        repo.commit("sentinel without a report", t=task("pr-merge:7"))
        repo.commit("rework clears pr", t=task("7"))
        repo.commit("report", t__observer="report")
        repo.commit("second sentinel", t=task("pr-merge:7"))
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertIn("2 events judged", out)
        self.assertIn("1 violated", out)
        self.assertEqual(out.count("violation: L1"), 1)


class L2Test(Base):
    def test_records_added_by_this_push_are_judged_by_part_and_earlier_ones_are_not(self):
        repo = Repo(self.tmp / "l2")
        repo.commit("base", keep="x")
        repo.commit("old bad", t__dispatch__old_bad=record(completion=False))
        before = repo.commit("old bad two", t__dispatch__moved_bad=record(completion=False))
        repo.commit(
            "records",
            t__dispatch__complete=record(),
            t__dispatch__no_main=record(completion=False),
            t__dispatch__no_root=record(root="pkg"),
            t__dispatch__bare=record(checklist="- run observer_check.py"),
            t__dispatch__pointer=record(checklist="Same checklist as complete."),
        )
        code, out = self.judge(repo, before)
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

    def test_a_record_corrected_in_a_later_commit_of_the_same_push_is_still_judged_as_added(self):
        repo = Repo(self.tmp / "l2-fixed")
        before = repo.commit("base", keep="x")
        added = repo.commit("bad record", t__dispatch__a=record(completion=False))
        repo.commit("corrected", t__dispatch__a=record())
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, rf"record=t/dispatch/a\.md commit={added[:12]} .*completion recipient")

    def test_a_record_deleted_later_in_the_same_push_is_still_judged_as_added(self):
        repo = Repo(self.tmp / "l2-gone")
        before = repo.commit("base", keep="x")
        repo.commit("bad record", t__dispatch__a=record(completion=False), t__dispatch__b=record())
        git(repo.path, "rm", "-q", "t/dispatch/a.md")
        git(repo.path, "commit", "-q", "-m", "delete")
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertIn("2 events judged", out)
        self.assertIn("record=t/dispatch/a.md", out)

    def test_a_record_deleted_and_added_again_is_judged_at_every_add(self):
        repo = Repo(self.tmp / "l2-readd")
        before = repo.commit("base", keep="x")
        first = repo.commit("bad record", t__dispatch__a=record(completion=False))
        git(repo.path, "rm", "-q", "t/dispatch/a.md")
        git(repo.path, "commit", "-q", "-m", "delete")
        repo.commit("corrected record at the same path", t__dispatch__a=record())
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertIn("2 events judged", out)
        self.assertRegex(out, rf"record=t/dispatch/a\.md commit={first[:12]} .*completion recipient")

    def test_a_pointer_is_judged_against_the_folder_at_the_commit_that_added_it(self):
        repo = Repo(self.tmp / "l2-sibling")
        before = repo.commit("base", keep="x")
        repo.commit("records", t__dispatch__a=record(), t__dispatch__b=record(checklist="Same checklist as a."))
        git(repo.path, "rm", "-q", "t/dispatch/a.md")
        git(repo.path, "commit", "-q", "-m", "delete the sibling")
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"record=t/dispatch/b\.md .*needs a checklist of its own")

    def test_an_archive_move_and_a_task_folder_rename_are_no_events(self):
        repo = Repo(self.tmp / "l2-move")
        repo.commit("base", keep="x")
        before = repo.commit("bad record", t__dispatch__a=record(completion=False))
        git(repo.path, "mv", "t", "u")
        git(repo.path, "commit", "-q", "-m", "rename the task folder")
        (repo.path / "_archive").mkdir()
        git(repo.path, "mv", "u", "_archive/u")
        git(repo.path, "commit", "-q", "-m", "archive")
        code, out = self.judge(repo, before)
        self.assertEqual(code, 0, out)
        self.assertIn("0 events judged", out)


class RangeTest(Base):
    def test_each_push_is_judged_on_its_own_range_and_adoption_starts_green(self):
        repo = Repo(self.tmp / "pushes")
        repo.commit("old violation", t__dispatch__old=record(completion=False))
        p0_before = git(repo.path, "rev-parse", "HEAD")
        p0 = repo.commit("add the workflow file", **{".github__workflows__dev2-laws": "on: push\n"})
        p1 = repo.commit("bad record", t__dispatch__p1=record(completion=False))
        p2 = repo.commit("complete record", t__dispatch__p2=record())
        p3 = repo.commit("nothing a law judges", other="z")
        code, out = self.judge(repo, p0_before, p0)
        self.assertEqual(code, 0, out)
        self.assertIn("L1 observer-before-sentinel: 0 events judged", out)
        self.assertIn("L2 dispatch-record-complete: 0 events judged", out)
        code, out = self.judge(repo, p0, p1)
        self.assertEqual(code, 1, out)
        self.assertEqual(out.count("violation:"), 1)
        self.assertRegex(out, rf"record=t/dispatch/p1\.md commit={p1[:12]} ")
        code, out = self.judge(repo, p1, p2)
        self.assertEqual(code, 0, out)
        self.assertIn("L2 dispatch-record-complete: 1 events judged", out)
        code, out = self.judge(repo, p2, p3)
        self.assertEqual(code, 0, out)
        self.assertIn("L2 dispatch-record-complete: 0 events judged", out)

    def test_a_force_push_judges_the_commits_new_to_the_branch(self):
        repo = Repo(self.tmp / "force")
        base = repo.commit("base", keep="x")
        dropped = repo.commit("bad record that the force push drops", t__dispatch__a=record(completion=False))
        git(repo.path, "reset", "-q", "--hard", base)
        after = repo.commit("a complete record", t__dispatch__b=record())
        self.assertEqual(git(repo.path, "merge-base", dropped, after), base)
        code, out = self.judge(repo, dropped, after)
        self.assertEqual(code, 0, out)
        self.assertIn("L2 dispatch-record-complete: 1 events judged", out)

    def test_a_merge_commit_holds_no_event_and_its_side_commits_are_judged(self):
        repo = Repo(self.tmp / "merge")
        before = repo.commit("base", keep="x")
        git(repo.path, "checkout", "-q", "-b", "side")
        side = repo.commit("bad record on a side branch", t__dispatch__a=record(completion=False))
        git(repo.path, "checkout", "-q", "main")
        repo.commit("other work", other="y")
        git(repo.path, "merge", "-q", "--no-ff", "-m", "merge", "side")
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertIn("L2 dispatch-record-complete: 1 events judged", out)
        self.assertRegex(out, rf"record=t/dispatch/a\.md commit={side[:12]} ")


class LaterHistoryTest(Base):
    def history(self):
        repo = Repo(self.tmp / "h")
        before = repo.commit("base", keep="x")
        repo.commit("bad task", t=task())
        repo.commit("sentinel without a report", t=task("pr-merge:7"))
        repo.commit("good task", u=task())
        repo.commit("report", u__observer="report")
        repo.commit("sentinel after a report", u=task("pr-merge:8"))
        repo.commit("records", x__dispatch__a=record(completion=False), x__dispatch__b=record(),
                    x__dispatch__c=record(checklist="Same checklist as b."))
        after = repo.commit("a record in another folder", y__dispatch__d=record(root="pkg"))
        return repo, before, after

    def test_commits_appended_after_the_range_do_not_change_its_verdict(self):
        repo, before, after = self.history()
        baseline = self.judge(repo, before, after)
        self.assertEqual(baseline[0], 1, baseline[1])
        self.assertIn("L1 observer-before-sentinel: 2 events judged", baseline[1])
        self.assertIn("task=t", baseline[1])
        self.assertIn("L2 dispatch-record-complete: 4 events judged", baseline[1])
        files = git(repo.path, "ls-files").split("\n")
        self.assertEqual(len(files), 8, files)

        def edit(where, path):
            text = task(body="edited") if path in ("t.md", "u.md") else record(checklist=f"- edited {path}") if "/dispatch/" in path else "edited\n"
            (where / path).write_text(text)

        def delete(where, path):
            (where / path).unlink()

        def archive(where, path):
            (where / "_archive" / path).parent.mkdir(parents=True, exist_ok=True)
            (where / path).rename(where / "_archive" / path)

        for name, action in (("edit", edit), ("delete", delete), ("archive", archive)):
            copy = self.tmp / f"h-{name}"
            shutil.copytree(repo.path, copy)
            for path in files:
                action(copy, path)
            git(copy, "add", "-A")
            git(copy, "commit", "-q", "-m", f"{name} every file")
            self.assertEqual(laws(copy, "--before", before, "--after", after, "--readme", self.learn), baseline, name)


if __name__ == "__main__":
    unittest.main()
