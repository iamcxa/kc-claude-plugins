#!/usr/bin/env python3
"""Fixture-repo cases for scripts/adr-path-check.py; each asserts the printed reason."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "adr-path-check.py"
GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
}
TRUNK_REASON = "point at the file on the trunk"
MISSING_FILE = "no such file in the tree"
MISSING_DIR = "directory missing or holds no NNNN-*.md"


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=GIT_ENV)


def run_check(root: Path) -> tuple[int, str]:
    done = subprocess.run(
        [sys.executable, "-B", "-I", str(SCRIPT), "--root", str(root)],
        capture_output=True, text=True, env=GIT_ENV, timeout=30,
    )
    return done.returncode, done.stdout + done.stderr


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        git(self.root, "init", "-q", "-b", "main")

    def put(self, name: str, text: str = "x\n", track: bool = True) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        if track:
            git(self.root, "add", name)

    def adr(self) -> None:
        self.put("docs/adr/0001-first-decision.md")

    def commit(self) -> None:
        git(self.root, "commit", "-q", "-m", "fixture")


class PathCases(Fixture):
    def test_existing_trunk_path_and_bare_dir_pass(self) -> None:
        self.adr()
        self.put("AGENTS.md", "Read `docs/adr/0001-first-decision.md`, or `ls docs/adr`.\n")
        self.assertEqual(run_check(self.root), (0, ""))

    def test_missing_path_fails_naming_it(self) -> None:
        self.adr()
        self.put("CLAUDE.md", "Read docs/adr/0009-gone.md first.\n")
        code, out = run_check(self.root)
        self.assertEqual(code, 1)
        self.assertIn("CLAUDE.md:1: docs/adr/0009-gone.md: " + MISSING_FILE, out)

    def test_untracked_file_does_not_count(self) -> None:
        self.adr()
        self.put("docs/adr/0002-only-on-disk.md", track=False)
        self.put("AGENTS.md", "Read docs/adr/0002-only-on-disk.md.\n")
        code, out = run_check(self.root)
        self.assertEqual(code, 1)
        self.assertIn("docs/adr/0002-only-on-disk.md: " + MISSING_FILE, out)

    def test_removed_directory_fails_with_reason_not_a_traceback(self) -> None:
        self.put("AGENTS.md", "ADRs live in `docs/adr/`.\n")
        code, out = run_check(self.root)
        self.assertEqual(code, 1)
        self.assertIn("AGENTS.md:1: docs/adr: " + MISSING_DIR, out)
        self.assertNotIn("Traceback", out)

    def test_directory_without_numbered_adr_fails(self) -> None:
        self.put("docs/adr/README.md")
        self.put("AGENTS.md", "ADRs live in `docs/adr/`.\n")
        code, out = run_check(self.root)
        self.assertEqual(code, 1)
        self.assertIn(MISSING_DIR, out)

    def test_placeholders_are_not_paths(self) -> None:
        self.adr()
        self.put("AGENTS.md", "Files are `docs/adr/NNNN-<title>.md`, see `docs/adr/*.md` and docs/adr/<name>.md.\n")
        self.assertEqual(run_check(self.root), (0, ""))

    def test_nested_instruction_file_is_read(self) -> None:
        self.adr()
        self.put("plugin/CLAUDE.md", "See docs/adr/0042-nope.md.\n")
        code, out = run_check(self.root)
        self.assertEqual(code, 1)
        self.assertIn("plugin/CLAUDE.md:1: docs/adr/0042-nope.md: " + MISSING_FILE, out)

    def test_other_markdown_files_are_not_read(self) -> None:
        self.adr()
        self.put("README.md", "See docs/adr/0042-nope.md.\n")
        self.assertEqual(run_check(self.root), (0, ""))

    def test_outside_a_git_repository_is_a_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as bare:
            code, out = run_check(Path(bare))
        self.assertEqual(code, 2)
        self.assertIn("cannot list tracked files", out)


class RefCases(Fixture):
    STALE = (
        "Read it before proposing a new app:\n\n"
        "```\ngit show docs/some-adr-branch:docs/adr/0001-first-decision.md\n```\n\n"
        "The ADR lives on the `docs/some-adr-branch` branch.\n"
    )

    def refused(self, out: str, ref: str) -> None:
        self.assertIn(f"names ref `{ref}`; {TRUNK_REASON}", out)

    def test_ref_form_is_refused_when_branch_exists_only_locally(self) -> None:
        self.adr()
        self.commit()
        git(self.root, "branch", "docs/some-adr-branch")
        self.put("AGENTS.md", self.STALE)
        code, out = run_check(self.root)
        self.assertEqual(code, 1)
        self.refused(out, "docs/some-adr-branch")
        self.assertIn("AGENTS.md:4: ", out)

    def test_ref_form_is_refused_when_branch_exists_on_origin(self) -> None:
        self.adr()
        self.commit()
        with tempfile.TemporaryDirectory() as origin:
            git(Path(origin), "init", "-q", "--bare", "-b", "main")
            git(self.root, "remote", "add", "origin", origin)
            git(self.root, "push", "-q", "origin", "main:refs/heads/docs/some-adr-branch")
            self.put("AGENTS.md", self.STALE)
            code, out = run_check(self.root)
        self.assertEqual(code, 1)
        self.refused(out, "docs/some-adr-branch")

    def test_ref_form_is_refused_when_branch_exists_nowhere(self) -> None:
        self.adr()
        self.put("AGENTS.md", self.STALE)
        code, out = run_check(self.root)
        self.assertEqual(code, 1)
        self.refused(out, "docs/some-adr-branch")

    def test_other_ref_forms_are_refused(self) -> None:
        self.adr()
        self.put("AGENTS.md", "`git show HEAD:docs/adr/0001-first-decision.md`\n`origin/next:docs/adr/`\n`git show <branch>:docs/adr/NNNN-x.md`\n")
        code, out = run_check(self.root)
        self.assertEqual(code, 1)
        for ref in ("HEAD", "origin/next", "<branch>"):
            self.refused(out, ref)

    def test_no_remote_is_contacted(self) -> None:
        self.adr()
        git(self.root, "remote", "add", "origin", "/nonexistent/origin.git")
        self.put("AGENTS.md", "Read `docs/adr/0001-first-decision.md`.\n")
        self.assertEqual(run_check(self.root), (0, ""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
