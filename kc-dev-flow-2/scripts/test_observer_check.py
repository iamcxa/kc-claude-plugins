#!/usr/bin/env python3
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("observer_check.py")
PACKAGE = SCRIPT.parents[1]
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
SLUG = "some-task"
# Every text an FO reads on the way to the sentinel must name the check.
NAMES_THE_CHECK = ("extensions/learn/EXTENSION.md", "references/sd/mods/observe-merged.md", "skills/dev/SKILL.md")


def git(where, *args):
    done = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True, env={**os.environ, **IDENTITY})
    assert done.returncode == 0, f"git {args}: {done.stderr}"
    return done.stdout.strip()


def check(*args):
    done = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True,
                          env={**os.environ, **IDENTITY})
    return done.returncode, done.stdout


class ObserverCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / "state"
        self.state.mkdir()
        git(self.state, "init", "-b", "main")
        (self.state / SLUG).mkdir()
        (self.state / f"{SLUG}.md").write_text("---\ntitle: t\npr: pr-merge:7\n---\nbody\n")
        for n in range(20):
            (self.state / SLUG / f"dispatch-{n}.md").write_text(f"dispatch {n}\n")
        self.live = self.commit("task with 20 dispatch files and a merged sentinel")

    def commit(self, message):
        git(self.state, "add", "-A")
        git(self.state, "commit", "-m", message)
        return git(self.state, "rev-parse", "HEAD")

    def archive(self):
        (self.state / "_archive").mkdir(exist_ok=True)
        git(self.state, "mv", f"{SLUG}.md", f"_archive/{SLUG}.md")
        git(self.state, "mv", SLUG, f"_archive/{SLUG}")
        return self.commit("archive")

    def write_report(self, text, archived=False):
        folder = self.state / ("_archive" if archived else "") / SLUG
        (folder / "observer.md").write_text(text)

    def test_the_miss_of_a_merged_task_without_a_report_fails_before_and_after_the_archive(self):
        for rev in (self.live, self.archive()):
            code, out = check(self.state, SLUG, "--rev", rev)
            self.assertEqual(code, 1, out)
            self.assertIn("kc-dev-flow-2:observer", out)
            self.assertIn(f"{SLUG}/observer.md", out)

    def test_a_committed_report_passes_before_the_archive_and_the_commit_before_it_failed(self):
        self.write_report("ok | rule: x\n")
        reported = self.commit("report")
        self.assertEqual(check(self.state, SLUG)[0], 0)
        self.assertEqual(check(self.state, SLUG, "--rev", self.live)[0], 1)
        self.assertEqual(check(self.state, SLUG, "--rev", reported)[0], 0)

    def test_a_committed_report_passes_after_the_archive_too(self):
        self.write_report("ok | rule: x\n")
        self.commit("report")
        self.archive()
        code, out = check(self.state, SLUG)
        self.assertEqual(code, 0, out)
        self.assertIn(f"_archive/{SLUG}/observer.md", out)

    def test_a_late_report_committed_in_the_archive_folder_passes(self):
        archived = self.archive()
        self.assertEqual(check(self.state, SLUG)[0], 1)
        self.write_report("late | rule: x\n", archived=True)
        self.commit("late report")
        self.assertEqual(check(self.state, SLUG)[0], 0)
        self.assertEqual(check(self.state, SLUG, "--rev", archived)[0], 1)

    def test_the_committed_tree_decides_not_the_disk(self):
        self.write_report("ok | rule: x\n")
        self.assertEqual(check(self.state, SLUG)[0], 1)
        self.commit("report")
        self.assertEqual(check(self.state, SLUG)[0], 0)

    def test_a_staged_but_uncommitted_report_does_not_pass(self):
        self.write_report("ok | rule: x\n")
        git(self.state, "add", f"{SLUG}/observer.md")
        self.assertEqual(check(self.state, SLUG)[0], 1)

    def test_an_empty_or_blank_report_fails(self):
        for text in ("", "\n  \n"):
            with self.subTest(text=text):
                self.write_report(text)
                self.commit("blank report")
                code, out = check(self.state, SLUG)
                self.assertEqual(code, 1, out)
                self.assertIn("blank", out)

    def test_an_observer_not_run_line_passes_and_is_printed(self):
        self.write_report("observer not run: agent could not be dispatched\n")
        self.commit("waiver")
        code, out = check(self.state, SLUG)
        self.assertEqual(code, 0)
        self.assertIn("observer not run: agent could not be dispatched", out)

    def test_a_state_checkout_that_is_a_subdirectory_of_the_repository_is_read_from_there(self):
        sub = Path(self.tmp.name) / "code"
        (sub / "docs/.state").mkdir(parents=True)
        git(sub, "init", "-b", "main")
        (sub / "docs/.state" / f"{SLUG}.md").write_text("x\n")
        (sub / "docs/.state" / SLUG).mkdir()
        (sub / "docs/.state" / SLUG / "observer.md").write_text("ok\n")
        git(sub, "add", "-A")
        git(sub, "commit", "-m", "x")
        self.assertEqual(check(sub / "docs/.state", SLUG)[0], 0)
        self.assertEqual(check(sub / "docs/.state", "other")[0], 2)

    def test_what_cannot_be_read_is_exit_2_with_the_cause(self):
        missing = Path(self.tmp.name) / "missing"
        cases = (
            ("not a git work tree", (missing, SLUG)),
            ("names no commit", (self.state, SLUG, "--rev", "no-such-rev")),
            ("no task file or folder", (self.state, "mistyped-slug")),
            ("usage", (self.state,)),
            ("usage", (self.state, SLUG, "--rev")),
            ("usage", (self.state, "../escape")),
        )
        for cause, args in cases:
            with self.subTest(cause=cause, args=args[1:]):
                code, out = check(*args)
                self.assertEqual(code, 2, out)
                self.assertIn("cannot tell", out)
                self.assertIn(cause, out)

    def test_a_directory_that_is_not_a_work_tree_inside_a_repository_is_not_a_pass(self):
        code, out = check(self.state / ".git", SLUG)
        self.assertEqual(code, 2, out)


class NamedWhereFoReadsTest(unittest.TestCase):
    def test_each_text_on_the_path_to_the_sentinel_names_the_check(self):
        for relative in NAMES_THE_CHECK:
            with self.subTest(file=relative):
                self.assertIn("scripts/observer_check.py", (PACKAGE / relative).read_text())

    def test_the_observer_skill_reads_both_path_pairs_of_an_archived_task(self):
        text = " ".join((PACKAGE / "skills/observer/SKILL.md").read_text().split())
        self.assertIn("_archive/<TASK>.md _archive/<TASK>", text)
        self.assertIn("both path pairs", text)


class DocumentedInvocationTest(unittest.TestCase):
    INSTRUCTION_FILES = ("extensions/learn/EXTENSION.md", "references/sd/mods/observe-merged.md", "skills/dev/SKILL.md",
                         "skills/observer/SKILL.md")
    NAMED = re.compile(r"<package>/scripts/([a-z_]+\.py)")

    def read(self, relative):
        return " ".join((PACKAGE / relative).read_text().split())

    def test_every_instruction_runs_a_script_through_python3_unless_it_is_executable(self):
        for relative in self.INSTRUCTION_FILES:
            text = self.read(relative)
            found = [m for m in self.NAMED.finditer(text) if (PACKAGE / "scripts" / m.group(1)).exists()]
            self.assertTrue(found, f"{relative} names no package script")
            for match in found:
                if os.access(PACKAGE / "scripts" / match.group(1), os.X_OK):
                    continue
                with self.subTest(file=relative, script=match.group(1)):
                    self.assertTrue(text[:match.start()].endswith("python3 "),
                                    f"{relative} names {match.group(0)} without python3 and the file is not executable")

    def test_the_documented_observer_check_command_runs_as_written(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        state = Path(tmp.name) / "state"
        state.mkdir()
        git(state, "init", "-b", "main")
        (state / f"{SLUG}.md").write_text("---\ntitle: t\n---\n")
        git(state, "add", "-A")
        git(state, "commit", "-m", "task")
        pattern = re.compile(r"(?:python3 )?<package>/scripts/observer_check\.py <state> <slug>")
        for relative in self.INSTRUCTION_FILES:
            for written in pattern.findall(self.read(relative)):
                with self.subTest(file=relative, command=written):
                    command = (written.replace("<package>", shlex.quote(str(PACKAGE)))
                               .replace("<state>", shlex.quote(str(state))).replace("<slug>", SLUG))
                    done = subprocess.run(shlex.split(command), capture_output=True, text=True,
                                          env={**os.environ, **IDENTITY})
                    self.assertEqual(done.returncode, 1, f"{written}: {done.stdout}{done.stderr}")
                    self.assertIn("observer report not committed", done.stdout)


class RecoveryCommandQuotingTest(unittest.TestCase):
    def test_the_printed_late_report_commands_run_when_the_state_path_has_whitespace(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        state = Path(tmp.name) / "my state dir"
        (state / "_archive" / SLUG).mkdir(parents=True)
        git(state, "init", "-b", "main")
        (state / "_archive" / f"{SLUG}.md").write_text("---\ntitle: t\n---\n")
        git(state, "add", "-A")
        git(state, "commit", "-m", "archived task")
        code, out = check(state, SLUG)
        self.assertEqual(code, 1, out)
        span = re.search(r"`(git -C .*?)` and", out).group(1)
        words = shlex.split(span)
        steps = [[]]
        for word in words:
            steps.append([]) if word == "&&" else steps[-1].append(word)
        steps = [[("late report" if w == "<message>" else w) for w in step] for step in steps]
        self.assertEqual(len(steps), 2, steps)
        for step in steps:
            self.assertEqual(step[:3], ["git", "-C", str(state)], step)
        (state / "_archive" / SLUG / "observer.md").write_text("ok\n")
        for step in steps:
            done = subprocess.run(step, capture_output=True, text=True, env={**os.environ, **IDENTITY})
            self.assertEqual(done.returncode, 0, f"{step}: {done.stderr}")
        code, out = check(state, SLUG)
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
