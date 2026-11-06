#!/usr/bin/env python3
"""Exercise merge authorization, disk discovery, and record refusals."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("merge_guard.py")
spec = importlib.util.spec_from_file_location("merge_guard", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
HEAD = "1234567890abcdef1234567890abcdef12345678"
OTHER = "a" * 40
PR = "owner/repo#672"


class MergeGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = self.root / "state"
        self.state.mkdir()
        self.command = f"gh pr merge 672 --repo owner/repo --squash --match-head-commit {HEAD}"

    def saved(self, task="task", number=1, head=HEAD, pr=PR, root=None):
        path = (root or self.state) / task / "merge" / f"ask-{number}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"pr": pr, "head": head}))
        return path

    def verdict(self, command=None):
        return guard.verdict(command or self.command, self.root, [self.state])[0]

    def test_carried_full_and_prefix(self):
        self.saved()
        for head in (HEAD, HEAD[:7]):
            self.assertEqual(self.verdict(self.command.replace(HEAD, head)), "pass")

    def test_newest_record_supersedes_older(self):
        self.saved(number=2)
        self.saved(number=10, head=OTHER)
        self.assertEqual(self.verdict(), "stop")

    def test_other_pr_repo_and_invalid_saved_head(self):
        for pr, head in (("owner/repo#673", HEAD), ("other/repo#672", HEAD), (PR, HEAD[:8])):
            with self.subTest(pr=pr, head=head):
                self.saved(pr=pr, head=head)
                self.assertEqual(self.verdict(), "stop")

    def test_missing_short_nonhex_or_long_command_head(self):
        self.saved()
        commands = [self.command.split(" --match-head-commit")[0]]
        commands += [self.command.replace(HEAD, h) for h in (HEAD[:6], "z" * 40, HEAD + "a")]
        for command in commands:
            self.assertEqual(self.verdict(command), "stop", command)

    def test_two_merges_stop(self):
        self.saved()
        self.assertEqual(self.verdict(self.command + " && " + self.command), "stop")

    def test_flag_url_and_shell_sequence_forms(self):
        self.saved()
        forms = [self.command.replace("--repo owner/repo", "-R owner/repo"),
                 self.command.replace("--repo owner/repo", "--repo=owner/repo"),
                 self.command.replace("672 --repo owner/repo", "https://github.com/owner/repo/pull/672"),
                 self.command.replace("--match-head-commit ", "--match-head-commit="),
                 self.command.replace("gh pr", "/tmp/bin/gh pr"),
                 "pwd && " + self.command, self.command + " > /tmp/merge.log"]
        for command in forms:
            self.assertEqual(self.verdict(command), "pass", command)

    def assert_guarded_form(self, command):
        self.assertEqual(guard.verdict(command, self.root, [])[0], "stop", command)
        self.saved()
        self.assertEqual(self.verdict(command), "pass", command)
        self.assertEqual(self.verdict(command.replace(HEAD, OTHER)), "stop", command)

    def test_global_short_repo_before_subcommand(self):
        self.assert_guarded_form(f"gh -R owner/repo pr merge 672 --squash --match-head-commit {HEAD}")
        self.assertEqual(self.verdict("gh -R owner/repo pr merge 672 --squash"), "stop")

    def test_global_long_repo_before_subcommand(self):
        self.assert_guarded_form(f"gh --repo owner/repo pr merge 672 --match-head-commit {HEAD}")

    def test_global_equals_repo_before_subcommand(self):
        self.assert_guarded_form(f"gh --repo=owner/repo pr merge 672 --match-head-commit {HEAD}")

    def test_attached_and_interleaved_repo_flags(self):
        for option in ("-Rowner/repo", "-R=owner/repo"):
            self.assert_guarded_form(f"gh {option} pr --repo owner/repo merge 672 --match-head-commit {HEAD}")

    def test_env_wrapper(self):
        self.assert_guarded_form(f"env -- gh -R owner/repo pr merge 672 --match-head-commit {HEAD}")

    def test_command_wrapper(self):
        self.assert_guarded_form(f"command -p -- gh -R owner/repo pr merge 672 --match-head-commit {HEAD}")

    def test_absolute_gh_with_global_flags(self):
        self.assert_guarded_form(f"/opt/homebrew/bin/gh --repo=owner/repo pr merge 672 --match-head-commit {HEAD}")

    def test_quoted_words(self):
        self.assert_guarded_form(f"'gh' '-R' 'owner/repo' 'pr' 'merge' '672' '--match-head-commit' '{HEAD}'")

    def test_shell_spelling_of_gh(self):
        for executable in (r"g\h", 'g""h', '"g"h'):
            self.assert_guarded_form(f"{executable} -R owner/repo pr merge 672 --match-head-commit {HEAD}")

    def test_rest_merge_endpoint_stops_even_with_record(self):
        self.saved()
        for endpoint in ("repos/owner/repo/pulls/672/merge", "/repos/owner/repo/pulls/672/merge",
                         "https://api.github.com/repos/owner/repo/pulls/672/merge",
                         "repos/{owner}/{repo}/pulls/672/merge", "repos/owner/repo/pulls/672/%6derge",
                         "repos/owner/repo/pulls/1/../672/merge", "repos/owner/repo/pulls//672/merge"):
            command = f"gh api -X PUT {endpoint} -f sha={HEAD}"
            self.assertEqual(self.verdict(command), "stop", command)
        self.assertEqual(self.verdict("gh api --method=GET repos/owner/repo/pulls/672/merge"), "stop")

    def test_graphql_and_opaque_api_stops(self):
        self.saved()
        for command in ("gh api graphql -f 'query=mutation {mergePullRequest(input:{pullRequestId:\"x\"}){clientMutationId}}'",
                        "gh api graphql -f 'query=mutation {enablePullRequestAutoMerge(input:{pullRequestId:\"x\"}){clientMutationId}}'",
                        "gh api graphql --input request.json", "gh api graphql -F query=@query.graphql",
                        'gh api "$ENDPOINT" -X PUT --input request.json'):
            self.assertEqual(self.verdict(command), "stop", command)

    def test_ambiguous_wrappers_options_and_shell_text_stop(self):
        self.saved()
        merge = f"gh -R owner/repo pr merge 672 --match-head-commit {HEAD}"
        for command in ("env GH_HOST=other.example " + merge,
                        "env -C /tmp " + merge, "sudo " + merge,
                        "bash -c '" + merge + "'", "echo '" + merge + "'",
                        merge.replace("-R owner/repo", "--unknown value"), merge + " '",
                        f"gh -R owner/repo pr merge 672 --match-head-commit {HEAD} && " + merge):
            self.assertEqual(self.verdict(command), "stop", command)

    def test_unknown_gh_alias_or_dynamic_subcommand_stops(self):
        for command in ("gh my-merge 672", "gh extension exec merge-helper 672", 'gh "$ACTION" 672'):
            self.assertEqual(self.verdict(command), "stop", command)

    def test_implicit_repo_after_shell_context_change_stops(self):
        self.saved()
        with patch.object(guard, "git", return_value="https://github.com/owner/repo.git"):
            self.assertEqual(self.verdict(f"cd /another/repo && gh pr merge 672 --match-head-commit {HEAD}"), "stop")

    def test_readonly_gh_commands_pass(self):
        for command in ("gh -R owner/repo pr view 672", "gh api repos/owner/repo/pulls/672",
                        "gh api -X GET repos/owner/repo/pulls/672", "gh issue list", "gh --version"):
            self.assertEqual(self.verdict(command), "pass", command)

    def test_origin_fallback(self):
        self.saved()
        command = self.command.replace(" --repo owner/repo", "")
        for remote in ("https://github.com/owner/repo.git", "git@github.com:owner/repo.git",
                       "ssh://git@github.com/owner/repo.git"):
            with patch.object(guard, "git", return_value=remote):
                self.assertEqual(self.verdict(command), "pass")

    def test_archived_newest(self):
        self.saved(task="_archive/task", number=2)
        self.assertEqual(self.verdict(), "pass")
        self.saved(task="_archive/task", number=3, head=OTHER)
        self.assertEqual(self.verdict(), "stop")

    def test_merges_folder_newest(self):
        self.saved(task="_merges/owner-repo-672")
        self.assertEqual(self.verdict(), "pass")
        self.saved(task="_merges/owner-repo-672", number=2, head=OTHER)
        self.assertEqual(self.verdict(), "stop")

    def test_nonmerge_passes_but_mentions_or_unparseable_stop(self):
        self.saved()
        self.assertEqual(self.verdict("git status --short"), "pass")
        for command in ("echo '" + self.command + "'", "echo " + self.command,
                        self.command + " '", self.command.replace("--squash", "--repo other/repo")):
            self.assertEqual(self.verdict(command), "stop", command)

    def test_unreadable_invalid_or_exception_stops_even_beside_match(self):
        self.saved()
        bad = self.saved(task="bad")
        bad.write_text("not JSON")
        self.assertEqual(self.verdict(), "stop")
        bad.write_text("[]")
        self.assertEqual(self.verdict(), "stop")
        with patch.object(guard, "newest_records", side_effect=PermissionError("unreadable")):
            self.assertEqual(self.verdict(), "stop")

    def test_host_outputs(self):
        for host, decision in (("claude", "ask"), ("codex", "deny")):
            payload = json.dumps({"cwd": str(self.root), "tool_input": {"command": self.command}})
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), host], input=payload,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            out = json.loads(result.stdout)["hookSpecificOutput"]
            self.assertEqual(out["permissionDecision"], decision)
            if host == "codex":
                self.assertIn("merge_guard.py record", out["permissionDecisionReason"])
        self.saved()
        with patch.object(guard, "state_roots", return_value=[self.state]), patch.object(sys, "argv", [str(SCRIPT), "codex"]), patch.object(sys, "stdin", io.StringIO(payload)), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(guard.main(), 0)
        self.assertEqual(out.getvalue(), "")

    def test_linked_worktree_discovery_reads_uncommitted_disk(self):
        repo = self.root / "repo"
        repo.mkdir()
        def git(*args):
            return subprocess.run(["git", "-C", str(repo), *args], check=True,
                                  capture_output=True, text=True).stdout
        git("init", "-q")
        git("-c", "user.name=Merge Test", "-c", "user.email=merge@example.invalid", "commit", "--allow-empty", "-qm", "fixture")
        linked = self.root / "linked state"
        git("worktree", "add", "-qb", "spacedock-state/x", str(linked))
        self.saved(root=linked)
        self.assertIn("?? task/", subprocess.check_output(["git", "-C", str(linked), "status", "--short"], text=True))
        self.assertEqual(guard.verdict(self.command, repo)[0], "pass")
        subprocess.run(["git", "-C", str(linked), "switch", "-qc", "other"], check=True)
        self.assertEqual(guard.verdict(self.command, repo)[0], "stop")


class RecordTests(unittest.TestCase):
    setUp = MergeGuardTests.setUp
    saved = MergeGuardTests.saved
    verdict = MergeGuardTests.verdict

    def record(self, question=None, head=HEAD, answer="准"):
        question_file = self.root / "question.txt"
        question_file.write_text(question if question is not None else f"Merge #672 at {HEAD[:7]}?")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = guard.record([str(self.state), "--pr", PR, "--head", head,
                                 "--question-file", str(question_file), "--answer", answer])
        return code, output.getvalue()

    def test_record_saves_next_number_and_guard_reads_it(self):
        self.saved(task="_merges/owner-repo-672", number=9, head=OTHER)
        self.assertEqual(self.record()[0], 0)
        path = self.state / "_merges/owner-repo-672/merge/ask-10.json"
        data = json.loads(path.read_text())
        self.assertEqual((data["pr"], data["head"], data["answer"]), (PR, HEAD, "准"))
        self.assertEqual(self.verdict(), "pass")
        self.assertEqual(self.record(f"Merge https://github.com/owner/repo/pull/672 at {HEAD[:7]}?")[0], 0)
        self.assertTrue(path.with_name("ask-11.json").exists())

    def test_record_refuses_missing_number_digit_suffix_head_answer_and_invalid_head(self):
        for kwargs in ({"question": f"Merge at {HEAD[:7]}?"},
                       {"question": f"Merge #6720 at {HEAD[:7]}?"},
                       {"question": "Merge #672?"}, {"answer": "  "}, {"head": HEAD[:8]}):
            with self.subTest(kwargs=kwargs):
                code, output = self.record(**kwargs)
                self.assertEqual(code, 1)
                self.assertTrue(output.strip())
                self.assertFalse((self.state / "_merges").exists())

    def test_record_reports_each_problem_and_caps_saved_text(self):
        code, output = self.record(question="wrong", head="z" * 40, answer="")
        self.assertEqual(code, 1)
        self.assertEqual(len(output.splitlines()), 4)
        self.assertEqual(self.record(f"Merge #672 at {HEAD[:7]}? " + "x" * 700, answer="a" * 300)[0], 0)
        data = json.loads(next((self.state / "_merges").glob("*/merge/ask-*.json")).read_text())
        self.assertEqual((len(data["question"]), len(data["answer"])), (600, 200))


if __name__ == "__main__":
    unittest.main()
