#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("merge_audit.py")
A, B = "a" * 40, "b" * 40
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}


def git(where, *args, env=None):
    done = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True,
                          env={**os.environ, **IDENTITY, **(env or {})})
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def pr(number, head=A, branch="feature", title="feat(x): change", at="2026-01-01T00:00:05Z"):
    return {"number": number, "headRefOid": head, "headRefName": branch, "title": title, "mergedAt": at}


class MergeAuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root / "workflow/state"
        self.state.mkdir(parents=True)
        (self.state.parent / "README.md").write_text("---\ntrunk: 'main' # integration branch\n---\n")
        self.remote = self.root / "o/r.git"
        self.remote.parent.mkdir()
        git(self.root, "init", "--bare", str(self.remote))
        git(self.state, "init", "-b", "spacedock-state/a")
        git(self.state, "remote", "add", "origin", str(self.remote))
        self.tick = 0
        self.write("task.md", "---\npr: pr-merge:7\n---\n")
        self.born = self.commit()
        self.write("task.md", "---\npr: pr-merge:7\n---\nfinished\n")
        self.end = self.commit()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.fixture = self.root / "prs.json"
        self.fixture.write_text("[]")
        self.trace = self.root / "gh-args.json"
        (self.bin / "gh").write_text(
            "#!" + sys.executable + "\nimport os,sys,pathlib,json\n"
            "pathlib.Path(os.environ['GH_TRACE']).write_text(json.dumps(sys.argv[1:]))\n"
            "print(pathlib.Path(os.environ['GH_FIXTURE']).read_text())\n"
            "sys.exit(int(os.environ.get('GH_EXIT', '0')))\n")
        (self.bin / "gh").chmod(0o755)

    def write(self, path, text):
        target = self.state / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self):
        time = f"2026-01-01T00:00:{self.tick:02d}Z"
        self.tick += 10
        git(self.state, "add", "-A")
        git(self.state, "commit", "-m", "state", env={"GIT_AUTHOR_DATE": time, "GIT_COMMITTER_DATE": time})
        return git(self.state, "rev-parse", "HEAD")

    def record(self, number=7, head=A, path="_archive/x/merge/ask-1.json", repo="o/r"):
        self.write(path, json.dumps({"pr": f"{repo}#{number}", "head": head}))
        return self.commit()

    def audit(self, prs, *args, env=None, rev=None):
        self.fixture.write_text(json.dumps(prs))
        done = subprocess.run([sys.executable, "-B", str(SCRIPT), str(self.state), "task",
                               "--rev", rev or self.end, *args], capture_output=True, text=True,
                              env={**os.environ, **IDENTITY, "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
                                   "GH_FIXTURE": str(self.fixture), "GH_TRACE": str(self.trace), **(env or {})})
        return done.returncode, done.stdout + done.stderr

    def test_matching_head_is_carried_and_different_head_is_a_finding(self):
        self.record()
        code, out = self.audit([pr(7)])
        self.assertEqual(code, 0, out)
        self.assertIn("carried: 1 of 1", out)
        code, out = self.audit([pr(7, B)])
        self.assertEqual(code, 1, out)
        self.assertIn(f"head differs: #7 head {B[:12]}", out)
        self.assertIn("_archive/x/merge/ask-1.json", out)

    def test_seven_hex_prefix_and_any_record_can_carry_the_head(self):
        self.record(head=B)
        self.record(head=A[:7].upper(), path="nested/_merges/o-r-7/merge/ask-2.json")
        code, out = self.audit([pr(7)])
        self.assertEqual(code, 0, out)
        self.assertIn("carried: 1 of 1", out)

    def test_short_or_non_hex_record_is_incomplete_evidence(self):
        for head in (A[:6], "not-a-sha"):
            with self.subTest(head=head):
                self.record(head=head)
                code, out = self.audit([pr(7)])
                self.assertEqual(code, 2, out)
                self.assertIn("invalid ask head", out)

    def test_records_from_another_repository_do_not_carry_a_merge(self):
        self.record(repo="other/r")
        code, out = self.audit([pr(7)])
        self.assertEqual(code, 1, out)
        self.assertIn("no ask record: #7", out)
        self.assertIn("spacedock-state/a:task.md", out)

    def test_producer_names_and_a_renamed_release(self):
        code, out = self.audit([
            pr(1, branch="release-please--branches--main--components--x"),
            pr(2, branch="release-please--branches--main--groups--x"),
            pr(3, branch="learning/" + A + A[:24]),
            pr(4, title="chore(dev2): sync workflow to kc-dev-flow-2 v0.35.0"),
            pr(5, branch="chore/release-main"),
            pr(6, branch="learning/" + A)])
        self.assertEqual(code, 1, out)
        self.assertIn("release: #1 #2", out)
        self.assertIn("learning: #3", out)
        self.assertIn("sync: #4", out)
        self.assertIn("no ask record: #5", out)
        self.assertIn("no ask record: #6", out)

    def test_recorded_release_reads_carried_before_kind(self):
        self.record()
        code, out = self.audit([pr(7, branch="release-please--branches--main")])
        self.assertEqual(code, 0, out)
        self.assertIn("carried: 1 of 1", out)
        self.assertIn("release: none", out)

    def test_fetch_reads_a_remote_only_state_branch_at_its_tip(self):
        git(self.state, "switch", "-c", "spacedock-state/peer")
        tip = self.record(path="_merges/o-r-7/merge/ask-1.json")
        git(self.state, "push", "origin", "HEAD:refs/heads/spacedock-state/peer")
        git(self.state, "switch", "spacedock-state/a")
        git(self.state, "branch", "-D", "spacedock-state/peer")
        code, out = self.audit([pr(7)])
        self.assertEqual(code, 0, out)
        self.assertIn("carried: 1 of 1", out)
        self.assertRegex(out, rf"read: refs/remotes/origin/spacedock-state/peer {tip} 2026-01-01T00:00:20(?:Z|\+00:00)")

    def test_fetch_failure_warns_and_reads_local_refs(self):
        tip = self.record()
        git(self.state, "remote", "set-url", "origin", str(self.root / "missing/o/r.git"))
        code, out = self.audit([pr(7)])
        self.assertEqual(code, 0, out)
        self.assertIn("warning: state fetch failed", out)
        self.assertIn(f"read: refs/heads/spacedock-state/a {tip}", out)

    def test_record_committed_after_to_is_carried_but_uncommitted_record_is_not(self):
        self.write("task/merge/ask-1.json", json.dumps({"pr": "o/r#7", "head": A}))
        code, out = self.audit([pr(7)])
        self.assertEqual(code, 1, out)
        self.assertIn("no ask record: #7", out)
        tip = self.commit()
        self.assertNotEqual(tip, self.end)
        code, out = self.audit([pr(7)])
        self.assertEqual(code, 0, out)
        self.assertIn("carried: 1 of 1", out)

    def test_exact_window_excludes_from_and_includes_to_with_utc_search_dates(self):
        code, out = self.audit([pr(1, at="2026-01-01T00:00:00Z"),
                                pr(2, at="2026-01-01T08:00:10+08:00"),
                                pr(3, at="2026-01-01T00:00:11Z")])
        self.assertEqual(code, 1, out)
        self.assertIn(f"window: {self.born}..{self.end}", out)
        self.assertIn("no ask record: #2", out)
        self.assertNotIn("no ask record: #1", out)
        self.assertNotIn("no ask record: #3", out)
        args = json.loads(self.trace.read_text())
        self.assertEqual(args[args.index("--repo") + 1], "o/r")
        self.assertEqual(args[args.index("--base") + 1], "main")
        self.assertEqual(args[args.index("--search") + 1], "merged:2026-01-01..2026-01-01")

    def test_archived_task_uses_its_original_creation_commit(self):
        git(self.state, "mv", "task.md", "saved.md")
        (self.state / "_archive").mkdir()
        git(self.state, "mv", "saved.md", "_archive/task.md")
        archived = self.commit()
        code, out = self.audit([pr(7)], rev=archived)
        self.assertEqual(code, 1, out)
        self.assertIn(f"window: {self.born}..{archived}", out)

    def test_repeats_collapse_only_from_another_committed_report_at_to(self):
        token = f"no ask record: #9 head {A[:12]}"
        self.write("_archive/x/observer.md", f"can't tell | evidence: {token}\n")
        code, out = self.audit([pr(9)])
        self.assertEqual(code, 1, out)
        report_rev = self.commit()
        code, out = self.audit([pr(9)], rev=report_rev)
        self.assertEqual(code, 0, out)
        self.assertIn("already reported: #9", out)
        self.assertNotIn(token, out)
        (self.state / "_archive/x/observer.md").unlink()
        deleted = self.commit()
        code, out = self.audit([pr(9)], rev=deleted)
        self.assertEqual(code, 1, out)
        self.assertIn(token, out)

    def test_own_report_does_not_hide_a_finding_on_a_rerun(self):
        self.write("task/observer.md", f"no ask record: #9 head {A[:12]}\n")
        code, out = self.audit([pr(9)], rev=self.commit())
        self.assertEqual(code, 1, out)
        self.assertIn("no ask record: #9", out)

    def test_head_difference_repeats_also_collapse(self):
        self.record()
        self.write("_archive/x/observer.md", f"head differs: #7 head {B[:12]}\n")
        code, out = self.audit([pr(7, B)], rev=self.commit())
        self.assertEqual(code, 0, out)
        self.assertIn("already reported: #7", out)

    def test_task_owner_is_frontmatter_not_body_and_accepts_quotes_and_comments(self):
        self.write("_archive/owner/index.md", '---\npr: "pr-merge:9" # merged\n---\n')
        self.write("_archive/other.md", "---\ntitle: other\n---\npr: pr-merge:10\n")
        self.commit()
        code, out = self.audit([pr(9), pr(10)])
        self.assertEqual(code, 1, out)
        self.assertIn("_archive/owner/index.md)", out)
        self.assertIn(f"no ask record: #10 head {A[:12]} merged 2026-01-01T00:00:05Z (no task in readable state)", out)

    def test_gh_failure_result_limit_bad_records_and_no_origin_hold(self):
        code, out = self.audit([], env={"GH_EXIT": "1"})
        self.assertEqual(code, 2, out)
        self.assertIn("gh pr list", out)
        code, out = self.audit([pr(n + 1) for n in range(1000)])
        self.assertEqual(code, 2, out)
        self.assertIn("1000", out)
        code, out = self.audit([{"number": 7}])
        self.assertEqual(code, 2, out)
        self.assertIn("incomplete", out)
        git(self.state, "remote", "remove", "origin")
        code, out = self.audit([])
        self.assertEqual(code, 2, out)
        self.assertIn("origin", out)

    def test_invalid_ref_no_state_refs_and_bad_json_hold(self):
        code, out = self.audit([], rev="missing")
        self.assertEqual(code, 2, out)
        self.assertIn("missing", out)
        self.write("task/merge/ask-1.json", "{")
        self.commit()
        code, out = self.audit([])
        self.assertEqual(code, 2, out)
        self.assertIn("can't tell:", out)
        git(self.state, "switch", "-c", "main")
        git(self.state, "branch", "-D", "spacedock-state/a")
        code, out = self.audit([])
        self.assertEqual(code, 2, out)
        self.assertIn("no readable spacedock-state", out)


if __name__ == "__main__":
    unittest.main()
