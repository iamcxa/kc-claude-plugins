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


def record(*, checklist="- do the work", root="/pkg", completion=True, candidate=False):
    scope = f"Package root: {root}\n" + ("Send the completion message to `main`.\n" if completion else "")
    return f"Dispatched: 2026-10-16 {SHA}\nModel: sonnet\n{f'Candidate: {SHA}' + chr(10) if candidate else ''}\n## Checklist\n\n{checklist}\n\n## Scope notes\n\n{scope}"


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
    for name in ("laws_check.py", "decision_ledger.py", "observer_check.py", "dispatch_records.py", "design_surfaces.py"):
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

    def test_missing_design_adr_is_an_event_violation_even_after_later_repair(self):
        for index in (False, True):
            with self.subTest(index=index):
                repo = Repo(self.tmp / f"l2-design-adr-{index}")
                before = repo.commit("base", keep="x")
                path = "t__index" if index else "t"
                text = "---\nprofile: pilot\n---\n\n## Design\ndocs/adr/<reserved number>-a.md\n"
                event = repo.commit("unreserved dispatch", **{path: text, "t__dispatch__implementation-1": record()})
                initial = self.judge(repo, before, event)
                code, out = initial
                self.assertEqual(code, 1, out)
                self.assertRegex(out, rf"record=t/dispatch/implementation-1\.md commit={event[:12]} design ADR placeholder has no reserved ADR")
                self.assertNotIn("cannot judge", out)
                repo.commit("reservation recovery", **{path: text + "\n## Number guards\nADR: 0020\n",
                                                       "t__dispatch__implementation-1": record() + "ADR: 0020\n"})
                self.assertEqual(self.judge(repo, before, event), initial)
                current = self.judge(repo, before)
                self.assertEqual(current[0], 1, current[1])
                self.assertEqual([line for line in current[1].splitlines() if line.startswith("violation:")],
                                 [line for line in initial[1].splitlines() if line.startswith("violation:")])
                repo.commit("reserved continuation", **{"t__dispatch__implementation-2": record()})
                self.assertEqual(self.judge(repo, event)[0], 0)

    def test_live_ruling_predicate_is_skipped_by_real_historical_snapshot_caller(self):
        repo = Repo(self.tmp / "l2-live-ruling")
        before = repo.commit("base", keep="x")
        body = "\n## Stage Report: validation\n\n- F1 Needs decision: Captain must choose.\n"
        repo.commit("open decision", t=task(body=body))
        repo.commit("validation record", **{"t__dispatch__validation-2": record(candidate=True)})
        code, out = self.judge(repo, before)
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"L2 dispatch-record-complete: 1 events judged in [^\n]+, 0 violated")
        self.assertNotIn("cannot judge", out)
        self.assertNotIn("validation rerun", out)
        self.assertNotIn("history-context", out)
        before = git(repo.path, "rev-parse", "HEAD")
        repo.commit("bare script", **{"t__dispatch__validation-3": record(candidate=True, checklist="- run observer_check.py")})
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertIn("bare package script name observer_check.py", out)
        self.assertNotIn("output this runner does not parse", out)

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

    def test_a_reserved_line_and_an_amendment_the_record_leaves_out_are_l2_violations_with_the_task_file_beside_them(self):
        guards = "\n## Number guards\n\nADR: 0020\n"
        amended = "\n## Captain amendments\n\n### Amendment 1 \u2014 2026-10-17, chat\nCaptain: x\nSupersedes: none\n"
        repo = Repo(self.tmp / "l2-facts")
        before = repo.commit("base", keep="x")
        reserved = repo.commit("first record", t=task(body=guards), **{"t__dispatch__implementation-1": record()})
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, rf"record=t/dispatch/implementation-1\.md commit={reserved[:12]} .*reserved line 'ADR: 0020' missing from scope notes")
        repo.commit("amend", t=task(body=amended))
        second = repo.commit("next record", **{"t__dispatch__implementation-2": record()})
        code, out = self.judge(repo, reserved)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, rf"record=t/dispatch/implementation-2\.md commit={second[:12]} .*Captain amendment 1 named in no dispatch checklist")
        repo.commit("named", **{"t__dispatch__implementation-3": record(checklist="- Captain amendment 1: do it")})
        self.assertEqual(self.judge(repo, second)[0], 0)

    def test_an_ideation_record_whose_task_owes_a_result_line_is_an_l2_violation_and_the_result_clears_it(self):
        needed = "\n## FO alignment\n\nAlignment: needed before ideation: which checks run where.\n"
        repo = Repo(self.tmp / "l2-result")
        before = repo.commit("base", keep="x")
        bare = repo.commit("record", t=task(body=needed), **{"t__dispatch__ideation-1": record()})
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, rf"record=t/dispatch/ideation-1\.md commit={bare[:12]} .*records alignment as needed with no 'Result:' line")
        repo.commit("result", t=task(body=needed + "Result: aligned by his answer.\n"), **{"t__dispatch__ideation-2": record()})
        self.assertEqual(self.judge(repo, bare)[0], 0)

    def test_a_backslash_quote_on_an_amendment_line_is_an_l2_violation(self):
        amended = '\n## Captain amendments\n\n### Amendment 1 — 2026-10-17, chat\nCaptain: x\nAsked: \\"half a question\n'
        repo = Repo(self.tmp / "l2-backslash")
        before = repo.commit("base", keep="x")
        repo.commit("record", t=task(body=amended), **{"t__dispatch__implementation-1": record(checklist="- Captain amendment 1: do it")})
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"record=t/dispatch/implementation-1\.md .*Captain amendment 1 Asked line holds a backslash-quote")

    def test_a_backslash_quote_on_a_design_or_continuation_line_is_no_l2_event_and_does_not_abort_the_runner(self):
        for line in ('Design: the \\"old\\" paragraph.\n', 'a continuation with \\"x\\"\n'):
            with self.subTest(line):
                amended = "\n## Captain amendments\n\n### Amendment 1 \u2014 2026-10-17, chat\nCaptain: x\nSupersedes: none\nAsked: y\n" + line
                repo = Repo(self.tmp / f"l2-other-{abs(hash(line))}")
                before = repo.commit("base", keep="x")
                repo.commit("record", t=task(body=amended), **{"t__dispatch__implementation-2": record(checklist="- Captain amendment 1: do it")})
                code, out = self.judge(repo, before)
                self.assertEqual(code, 0, out)

    def test_mutation_reverting_the_runner_pattern_makes_the_new_lines_unjudgeable(self):
        scripts = self.tmp / "reverted"
        shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__", "test_*"))
        source = (scripts / "laws_check.py").read_text()
        reverted = re.sub(r"\|\"\n\s+r\"'## FO alignment'.*?from JSON\)", ")", source, flags=re.S)
        self.assertNotEqual(reverted, source)
        (scripts / "laws_check.py").write_text(reverted)
        needed = "\n## FO alignment\n\nAlignment: needed before ideation: x.\n"
        repo = Repo(self.tmp / "l2-reverted")
        before = repo.commit("base", keep="x")
        repo.commit("record", t=task(body=needed), **{"t__dispatch__ideation-1": record()})
        self.assertEqual(self.judge(repo, before)[0], 1)
        code, out = self.judge(repo, before, runner=scripts / "laws_check.py")
        self.assertEqual(code, 2, out)
        self.assertIn("output this runner does not parse", out)

    def test_dispatch_records_printing_a_new_names_shape_exits_2_not_1(self):
        repo = Repo(self.tmp / "l2-shape")
        before = repo.commit("base", keep="x")
        repo.commit("record", t__dispatch__a=record())
        stub = ("import sys\nif '--names' in sys.argv:\n    print(sys.argv[-1] + ':1: some future check; fix it')\n    sys.exit(1)\n"
                "sys.exit(0)\n")
        code, out = self.judge(repo, before, runner=sandbox(self.tmp / "l2-shape-run", override={"dispatch_records.py": stub}))
        self.assertEqual(code, 2, out)
        self.assertIn("dispatch_records.py --names exited 1 with output this runner does not parse", out)

    def test_a_validation_record_without_a_candidate_line_is_an_l2_violation_not_an_unjudgeable_run(self):
        repo = Repo(self.tmp / "l2-candidate")
        before = repo.commit("base", keep="x")
        repo.commit("records", **{"t__dispatch__validation-1": record(), "t__dispatch__validation-2": record(candidate=True)})
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"violation: L2 dispatch-record-complete record=t/dispatch/validation-1\.md .*Candidate")
        self.assertNotIn("validation-2.md", out)
        self.assertNotIn("does not parse", out)

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

    def extension_records(self):
        repo = Repo(self.tmp / "l2-ext")
        before = repo.commit("base", keep="x")
        added = repo.commit(
            "first implementation records",
            **{"t__dispatch__implementation-1": record(),
               "u__dispatch__implementation-1": record(checklist="- run <package>/extensions/roborev/roborev_gate.py")})
        return repo, before, added

    def test_a_first_record_missing_a_listed_extensions_instruction_is_a_violation_naming_both(self):
        repo, before, added = self.extension_records()
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertIn("2 events judged", out)
        self.assertIn("2 violated", out)
        self.assertRegex(out, rf"record=t/dispatch/implementation-1\.md commit={added[:12]} roborev worker instruction is absent")
        self.assertRegex(out, r"record=u/dispatch/implementation-1\.md .*roborev worker instruction has an unsubstituted <package>")

    def test_the_readme_supplied_decides_whether_the_instruction_is_required(self):
        trunk = Repo(self.tmp / "trunk")
        trunk.commit("before roborev", readme="---\nextensions: [learn]\n---\nbody\n")
        without = git(trunk.path, "rev-parse", "HEAD")
        trunk.commit("lists roborev", readme="---\nextensions: [learn, roborev]\n---\nbody\n")
        repo, before, _ = self.extension_records()
        verdicts = {}
        for name in ("without", "with"):
            sha = without if name == "without" else "HEAD"
            readme = self.tmp / f"readme-at-{name}.md"
            readme.write_text(git(trunk.path, "show", f"{sha}:readme.md"))
            verdicts[name] = self.judge(repo, before, readme=readme)
        self.assertEqual(verdicts["without"][0], 0, verdicts["without"][1])
        self.assertIn("2 events judged", verdicts["without"][1])
        self.assertEqual(verdicts["with"][0], 1, verdicts["with"][1])

    def test_with_no_readme_the_not_checked_note_is_skipped_and_other_parts_are_still_judged(self):
        repo = Repo(self.tmp / "l2-noreadme")
        before = repo.commit("base", keep="x")
        repo.commit("record", **{"t__dispatch__implementation-1": record(completion=False)})
        code, out = laws(repo.path, "--before", before)
        self.assertEqual(code, 2, out)
        self.assertRegex(out, r"record=t/dispatch/implementation-1\.md .*completion recipient")
        self.assertNotIn("L2 dispatch-record-complete: cannot judge", out)


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




AMENDED = task(body="\n## Captain amendments\n\n### Amendment 1 — 2026-10-29, chat\nCaptain: words\nSupersedes: none\nDesign:\n````md\nold fenced text\n````\n")
MOVED = "\nSuperseded text:\n\n**AC-1**: old outcome.\n"


class L3Test(Base):
    def history(self, body=AMENDED, name="t", label="l3"):
        repo = Repo(self.tmp / label)
        before = repo.commit("base", **{name: body})
        return repo, before

    def test_metadata_fences_payload_and_final_content_spaces_are_protected(self):
        for n, (old, new, field) in enumerate((
                (AMENDED, AMENDED.replace("Captain: words", "Captain: changed"), "metadata"),
                (AMENDED, AMENDED.replace("2026-10-29", "2026-10-28"), "header"),
                (AMENDED, AMENDED.replace("old fenced text", "new fenced text"), "metadata"),
                (AMENDED + MOVED, AMENDED + MOVED.replace("old outcome", "new outcome"), "Superseded text"),
                (AMENDED + "last  \n", AMENDED + "last\n", "metadata"))):
            repo, before = self.history(old, label=f"edit-{n}")
            event = repo.commit("rewrite", t=new)
            code, out = self.judge(repo, before)
            self.assertEqual(code, 1, out)
            self.assertIn(f"amendment=1 commit={event[:12]} {field}", out)

    def test_entry_and_structural_worker_appends_are_allowed_but_metadata_extensions_are_not(self):
        repo, before = self.history()
        repo.commit("separator blanks", t=AMENDED + "\n\n")
        moved = repo.commit("worker", t=AMENDED + MOVED)
        extra = MOVED.replace("AC-1", "AC-2")
        appended = AMENDED + MOVED + "\n" + extra.split("Superseded text:\n", 1)[1]
        repo.commit("worker second block", t=appended)
        repo.commit("new entry", t=appended + "\n### Amendment 2 — 2026-10-30\nCaptain: two\nSupersedes: none\n")
        self.assertEqual(self.judge(repo, before)[0], 0)
        for n, text in enumerate((AMENDED + "Asked: new metadata\n", AMENDED + "\nSuperseded text:\nFO prose\n")):
            bad, base = self.history(label=f"bad-append-{n}")
            bad.commit("invalid append", t=text)
            self.assertEqual(self.judge(bad, base)[0], 1)
        self.assertNotEqual(before, moved)

    def test_delete_renumber_reorder_and_remove_entry_are_reported(self):
        two = AMENDED + "\n### Amendment 2 — 2026-10-30\nCaptain: two\nSupersedes: none\n"
        prefix, first = two.split("### Amendment 1", 1)
        one, second = first.split("### Amendment 2", 1)
        swapped = prefix + "### Amendment 2" + second + "\n### Amendment 1" + one
        for n, text in enumerate((swapped, AMENDED.replace("Amendment 1", "Amendment 8"),
                                  two.split("### Amendment 1", 1)[0] + two.split("### Amendment 2", 1)[1],
                                  task(), "\n## Captain amendments\n" + two.split("### Amendment 2", 1)[0].split("## Captain amendments", 1)[1])):
            repo, before = self.history(two, label=f"remove-{n}")
            repo.commit("rewrite", t=text)
            self.assertEqual(self.judge(repo, before)[0], 1)
        repo, before = self.history(label="deleted")
        git(repo.path, "rm", "t.md")
        git(repo.path, "commit", "-m", "delete")
        code, out = self.judge(repo, before)
        self.assertEqual(code, 1, out)
        self.assertIn("old=t.md new=(deleted)", out)
        self.assertIn("task deleted", out)

    def test_layout_archive_and_git_rename_moves_preserve_bytes_and_changes_still_fail(self):
        for n, dest in enumerate(("t/index.md", "_archive/t.md", "_archive/t/index.md", "other.md")):
            repo, before = self.history(label=f"move-{n}")
            target = repo.path / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            git(repo.path, "mv", "t.md", dest)
            git(repo.path, "commit", "-m", "move")
            self.assertEqual(self.judge(repo, before)[0], 0)
            target.write_text(AMENDED.replace("Captain: words", "Captain: changed"))
            git(repo.path, "add", dest)
            git(repo.path, "commit", "-m", "edit moved")
            self.assertEqual(self.judge(repo, before)[0], 1)

    def test_delete_add_layout_pair_without_git_rename_and_ambiguous_identity(self):
        repo, before = self.history()
        git(repo.path, "rm", "t.md")
        repo.commit("convert", t__index=AMENDED + "\n## Notes\n" + "Unrelated new text.\n" * 100)
        code, out = self.judge(repo, before)
        self.assertEqual(code, 0, out)
        self.assertIn("L3 amendment-append-only: 1 events judged", out)
        repo.commit("edit index", t__index=AMENDED.replace("Captain: words", "Captain: changed"))
        self.assertEqual(self.judge(repo, before)[0], 1)
        ambiguous, base = self.history(label="ambiguous")
        git(ambiguous.path, "rm", "t.md")
        ambiguous.commit("ambiguous layout", t__index=AMENDED + "a" * 10000,
                         _archive__t=AMENDED + "b" * 10000)
        code, out = self.judge(ambiguous, base)
        self.assertEqual(code, 2, out)
        self.assertIn("L3 amendment-append-only: cannot judge", out)
        self.assertIn("ambiguous task correspondence", out)
        self.assertIn("L1 observer-before-sentinel:", out)

    def test_working_copy_tip_readme_and_later_repair_do_not_change_fixed_range_result(self):
        repo, before = self.history()
        event = repo.commit("bad", t=AMENDED.replace("Captain: words", "Captain: changed"))
        initial = self.judge(repo, before, event)
        (repo.path / "t.md").write_text(AMENDED)
        self.assertEqual(self.judge(repo, before, event), initial)
        repaired = repo.commit("repair", t=AMENDED)
        git(repo.path, "mv", "t.md", "archived.md")
        git(repo.path, "commit", "-m", "rename")
        self.plain.write_text("---\nextensions: []\n---\n")
        self.assertEqual([s for s in self.judge(repo, before, event, readme=self.plain)[1].splitlines() if "L3" in s],
                         [s for s in initial[1].splitlines() if "L3" in s])
        self.assertEqual(self.judge(repo, before)[0], 1)
        tip = git(repo.path, "rev-parse", "HEAD")
        repo.commit("clean push", keep="new")
        self.assertEqual(self.judge(repo, tip)[0], 0)
        self.assertEqual(self.judge(repo, repaired)[0], 0)
        (repo.path / "archived.md").write_text("working copy removed amendment")
        self.assertEqual(self.judge(repo, tip)[0], 0)
        (repo.path / "archived.md").write_text(AMENDED)
        git(repo.path, "rm", "archived.md")
        git(repo.path, "commit", "-m", "delete later in range")
        self.assertEqual(self.judge(repo, before)[0], 1)
        self.assertEqual(self.judge(repo, before, event), initial)

    def test_invalid_supersedes_remains_extractable_and_unmatched_fence_is_bounded(self):
        old = AMENDED.replace("Supersedes: none", "Supersedes: AC-1 to AC-3")
        repo, before = self.history(old)
        repo.commit("rewrite invalid metadata", t=old.replace("AC-1 to AC-3", "AC-1, AC-2 and AC-3"))
        self.assertEqual(self.judge(repo, before)[0], 1)
        broken = AMENDED.rsplit("````", 1)[0]
        repo, before = self.history(broken, label="broken")
        repo.commit("known prefix edited", t=broken.replace("Captain: words", "Captain: changed"))
        self.assertEqual(self.judge(repo, before)[0], 1)
        repo, before = self.history(broken, label="uncertain")
        repo.commit("uncertain span", t=broken + "extra\n")
        code, out = self.judge(repo, before)
        self.assertEqual(code, 2, out)
        self.assertIn("ambiguous protected spans", out)

    def test_l2_classifies_new_forms_and_materializes_index_task(self):
        for n, name in enumerate(("t", "t__index")):
            repo = Repo(self.tmp / f"l2-form-{n}")
            before = repo.commit("base", keep="x")
            repo.commit("dispatch", **{name: AMENDED.replace("Supersedes: none", "Supersedes: summary AC-1"),
                                       "t__dispatch__implementation-2": record(checklist="- Captain amendment 1")})
            code, out = self.judge(repo, before)
            self.assertEqual(code, 1, out)
            self.assertIn("violation: L2", out)
            self.assertRegex(out, r"Captain amendment form at (?:t|index)\.md:[0-9]+:")
            self.assertNotIn("does not parse", out)

    def test_missing_parent_object_is_not_a_green_law_and_other_results_print(self):
        sys.path.insert(0, str(SCRIPTS))
        import laws_check as lc
        repo, before = self.history()
        event = repo.commit("change", t=AMENDED + "\n")
        ctx = lc.Context(repo.path, "fixed", [(event, [("M", "missing.md", "t.md")])], self.plain)
        with self.assertRaisesRegex(lc.Cannot, "git show .* failed"):
            lc.l3_amendment_append_only(ctx)

    def test_crlf_worker_payload_append_preserves_raw_bytes(self):
        initial = AMENDED.replace("\n", "\r\n")
        repo, before = self.history(initial, label="crlf")
        repo.commit("worker append", t=initial + MOVED.replace("\n", "\r\n"))
        self.assertEqual(self.judge(repo, before)[0], 0)

    def test_unreadable_blob_returns_law_specific_cannot_judge(self):
        repo, before = self.history(label="invalid-utf8")
        (repo.path / "t.md").write_bytes(AMENDED.encode() + b"\xff")
        git(repo.path, "add", "t.md")
        git(repo.path, "commit", "-m", "unreadable blob")
        code, out = self.judge(repo, before)
        self.assertEqual(code, 2, out)
        self.assertIn("L3 amendment-append-only: cannot judge", out)
        self.assertIn("unreadable UTF-8 blob", out)
        self.assertIn("L1 observer-before-sentinel:", out)

    def test_removing_the_law_or_l2_form_classification_breaks_event_controls(self):
        repo, before = self.history()
        repo.commit("rewrite", t=AMENDED.replace("old fenced text", "new fenced text"))
        for label, old, new, expected in (
                ("no-law", '    "L3": ("amendment-append-only", l3_amendment_append_only),', "", 0),
                ("strip-fences", 'elif entry.metadata != current.metadata:',
                 'elif entry.prefix != current.prefix:', 0)):
            source = RUNNER.read_text()
            self.assertIn(old, source)
            runner = sandbox(self.tmp / label, override={"laws_check.py": source.replace(old, new)})
            self.assertEqual(self.judge(repo, before, runner=runner)[0], expected)
            self.assertEqual(self.judge(repo, before)[0], 1)


class AmendmentMutationTests(Base):
    def test_each_named_regression_fails_its_behavioral_test_with_caches_absent(self):
        import json
        cases = (
            ("first-section-only", "design_surfaces.py", 'if not AMENDMENTS_HEADING.match(owner or ""):', 'if False:',
             "test_design_surfaces.AmendmentStructureTests.test_section_ownership_duplicate_sections_numbers_and_malformed_headings"),
            ("substring-ids", "design_surfaces.py", 'if not SUPERSEDES_VALUE.fullmatch(value.strip()):', 'if False:',
             "test_design_surfaces.AmendmentStructureTests.test_whole_value_grammar_and_unique_ids"),
            ("generic-headings", "design_surfaces.py", 'if AMENDMENT_START.match(line):', 'if line.startswith("### "):',
             "test_design_surfaces.AmendmentStructureTests.test_feedback_and_fenced_examples_end_or_hide_entries"),
            ("no-fences", "design_surfaces.py", 'marker = AMENDMENT_FENCE.match(line)', 'marker = None',
             "test_design_surfaces.AmendmentStructureTests.test_mismatched_fences_and_moved_metadata_are_not_live"),
            ("tip-only", "laws_check.py", 'str(ctx.state), "show", f"{rev}:{path}"', 'str(ctx.state), "show", f"HEAD:{path}"',
             "test_laws_check.L3Test.test_working_copy_tip_readme_and_later_repair_do_not_change_fixed_range_result"),
            ("ignore-deletion", "laws_check.py", 'if not before:', 'if not before or new is None:',
             "test_laws_check.L3Test.test_delete_renumber_reorder_and_remove_entry_are_reported"),
            ("skip-index", "laws_check.py", 'return slug if slug != "README" else None', 'return slug if slug != "README" and not path.endswith("/index.md") else None',
             "test_laws_check.L3Test.test_layout_archive_and_git_rename_moves_preserve_bytes_and_changes_still_fail"),
            ("strip-fenced-metadata", "laws_check.py", 'elif entry.metadata != current.metadata:', 'elif entry.prefix != current.prefix:',
             "test_laws_check.L3Test.test_metadata_fences_payload_and_final_content_spaces_are_protected"),
            ("unknown-l2-form", "laws_check.py", 'r"Captain amendment form at [^:]+:\\d+: .+|"', 'r"unrecognized-form|"',
             "test_laws_check.L3Test.test_l2_classifies_new_forms_and_materializes_index_task"),
            ("missing-evidence-green", "laws_check.py", 'if unavailable:', 'if False:',
             "test_laws_check.L3Test.test_missing_parent_object_is_not_a_green_law_and_other_results_print"))
        results = []
        for label, file, old, new, target in cases:
            with self.subTest(mutation=label):
                dest = self.tmp / label / "scripts"
                shutil.copytree(SCRIPTS, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                path = dest / file
                source = path.read_text()
                self.assertIn(old, source)
                path.write_text(source.replace(old, new, 1))
                self.assertEqual(list(dest.rglob("*.pyc")), [])
                done = subprocess.run([sys.executable, "-B", "-m", "unittest", target], cwd=dest, capture_output=True, text=True,
                                      env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **IDENTITY})
                self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                self.assertIn("FAIL:", done.stderr)
                self.assertNotIn("ERROR:", done.stderr)
                results.append({"mutation": label, "target": target, "exit": done.returncode, "output": done.stdout + done.stderr})
        if os.environ.get("DEV2_AMENDMENT_EVIDENCE"):
            Path(os.environ["DEV2_AMENDMENT_EVIDENCE"], "mutations.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    unittest.main()
