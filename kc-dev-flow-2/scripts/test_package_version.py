#!/usr/bin/env python3
import base64
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("package_version", Path(__file__).with_name("package_version.py"))
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)


class PackageVersionTest(unittest.TestCase):
    def run_on(self, text, loaded=(0, 18, 1)):
        with tempfile.TemporaryDirectory() as d:
            readme = Path(d, "README.md")
            readme.write_text(text)
            old, pv.loaded = pv.loaded, lambda: loaded
            out = io.StringIO()
            try:
                with contextlib.redirect_stdout(out):
                    return pv.main([str(readme)]), out.getvalue()
            finally:
                pv.loaded = old

    def line(self, version):
        return f"# Development workflow\n<!-- kc-dev-flow-2 {version} x-release-please-version -->\n"

    def test_an_older_loaded_package_holds(self):
        code, out = self.run_on(self.line("0.18.1"), loaded=(0, 17, 0))
        self.assertEqual(code, 1)
        self.assertIn("older than the README's 0.18.1", out)

    def test_versions_compare_as_numbers_not_text(self):
        self.assertEqual(self.run_on(self.line("0.9.0"), loaded=(0, 10, 0))[0], 0)
        self.assertEqual(self.run_on(self.line("0.10.0"), loaded=(0, 9, 0))[0], 1)

    def test_a_matching_or_newer_package_passes(self):
        self.assertIn("matches", self.run_on(self.line("0.18.1"))[1])
        code, out = self.run_on(self.line("0.18.0"))
        self.assertEqual(code, 0)
        self.assertIn("re-sync it", out)

    def test_a_readme_without_the_line_passes_and_says_so(self):
        code, out = self.run_on("# Development workflow\n")
        self.assertEqual(code, 0)
        self.assertIn("no kc-dev-flow-2 release line", out)

    def test_the_package_template_carries_the_line_and_matches_its_manifest(self):
        template = pv.PACKAGE / "references/sd/workflow.md"
        found = pv.MARK.search(template.read_text())
        self.assertIsNotNone(found)
        self.assertEqual(tuple(int(n) for n in found.groups()), pv.loaded())

    def test_usage_error(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(pv.main([]), 2)
            self.assertEqual(pv.main(["/no/such/README.md"]), 2)


class RolloutTest(unittest.TestCase):
    repo = "iamcxa/kc-claude-plugins"
    old = "1" * 40
    latest = "2" * 40
    workflow = "kc-dev-flow-2/references/sd/workflow.md"
    laws = ("kc-dev-flow-2/scripts/laws_check.py", "kc-dev-flow-2/references/sd/laws.md",
            "kc-dev-flow-2/references/sd/state-laws.workflow.yml")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.responses = {}
        self.rows = []
        self.reply(["api", f"repos/{self.repo}/git/matching-refs/tags/kc-dev-flow-2-v"], [
            {"ref": "refs/tags/kc-dev-flow-2-v0.38.0", "object": {"sha": self.old, "type": "commit"}},
            {"ref": "refs/tags/kc-dev-flow-2-v0.38.1", "object": {"sha": self.latest, "type": "commit"}}])
        for ref, version in ((self.old, "0.38.0"), (self.latest, "0.38.1")):
            self.content(self.repo, self.workflow, ref, self.readme(version) + "A rule.\n")
            for path in self.laws:
                self.content(self.repo, path, ref, "same laws\n")
        self.search([])
        fake = self.root / "gh"
        fake.write_text("#!" + sys.executable + "\n" +
                        "import json, os, sys\n" +
                        "data=json.load(open(os.environ['GH_FIXTURE']))\n" +
                        "key=json.dumps(sys.argv[1:])\n" +
                        "result=data.get(key, {'code': 97, 'stderr': 'unexpected gh: '+key})\n" +
                        "sys.stdout.write(json.dumps(result.get('data')) if 'data' in result else '')\n" +
                        "sys.stderr.write(result.get('stderr', ''))\n" +
                        "sys.exit(result.get('code', 0))\n")
        fake.chmod(0o755)

    def readme(self, version, trunk="main"):
        return f"---\ntrunk: {trunk}\n---\n<!-- kc-dev-flow-2 {version} x-release-please-version -->\n"

    def reply(self, args, data=None, error=None):
        self.responses[json.dumps(args)] = ({"code": 1, "stderr": error} if error else {"data": data})

    def content(self, repo, path, ref, text=None, error=None):
        from urllib.parse import quote
        endpoint = f"repos/{repo}/contents/{quote(path, safe='/')}?ref={quote(ref, safe='')}"
        data = {"encoding": "base64", "content": base64.b64encode((text or "").encode()).decode()}
        self.reply(["api", endpoint], data, error)

    def search(self, data=None, error=None):
        self.reply(["search", "code", "x-release-please-version", "--owner", "iamcxa",
                    "--owner", "spacedock-dev", "--filename", "README.md", "--limit", "1000",
                    "--json", "repository,path"], data, error)

    def row(self, name, version="0.38.0", pin=None, directory="docs/dev2", branch=None, trunk="main"):
        repo = f"fleet/{name}"
        self.rows.append(f"{repo} {directory}" + (f" {branch}" if branch else ""))
        self.reply(["api", f"repos/{repo}"], {"default_branch": "main"})
        self.content(repo, f"{directory}/README.md", "main", self.readme(version, trunk))
        if trunk != "main":
            self.content(repo, f"{directory}/README.md", trunk, self.readme(version, trunk))
        state = branch or "spacedock-state/" + Path(directory).name
        if pin is None:
            self.content(repo, ".github/workflows/dev2-laws.yml", state, error="Not Found (HTTP 404)")
            from urllib.parse import quote
            self.reply(["api", f"repos/{repo}/branches/{quote(state, safe='')}"], {"name": state})
        else:
            self.content(repo, ".github/workflows/dev2-laws.yml", state,
                         f"steps:\n  - uses: actions/checkout@abc\n    with:\n      repository: {self.repo}\n      ref: \"{pin}\"\n")
        return repo

    def run_rollout(self):
        fixture = self.root / "fixture.json"
        fixture.write_text(json.dumps(self.responses))
        listing = self.root / "adopters.md"
        listing.write_text("# Approved adopters\n\n" + "\n".join(self.rows) + "\n")
        return subprocess.run([sys.executable, "-B", str(Path(pv.__file__)), "rollout", str(listing)],
                              env={**os.environ, "PATH": str(self.root) + os.pathsep + os.environ['PATH'],
                                   "GH_FIXTURE": str(fixture)}, capture_output=True, text=True)

    def test_each_row_keeps_its_own_release_sync_and_laws_status(self):
        self.row("one", pin=self.old)
        self.row("two", "0.38.1", directory="docs/dev2-poc")
        self.row("three", "0.38.1", pin=self.latest, branch="records", trunk="develop")
        run = self.run_rollout()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(run.stdout.splitlines(), [
            f"fleet/one docs/dev2 README:0.38.0 released:0.38.1 no sync owed; laws: {self.old} no pin owed",
            "fleet/two docs/dev2-poc README:0.38.1 released:0.38.1 no sync owed; laws: not installed",
            f"fleet/three docs/dev2 README:0.38.1 released:0.38.1 no sync owed; laws: {self.latest} no pin owed"])

    def test_unreadable_readme_quotes_error_and_fails_without_hiding_other_rows(self):
        repo = self.row("missing")
        self.row("readable")
        self.content(repo, "docs/dev2/README.md", "main", error="Not Found (HTTP 404)")
        run = self.run_rollout()
        self.assertEqual(run.returncode, 1)
        self.assertIn('fleet/missing docs/dev2 unreadable: "Not Found (HTTP 404)"', run.stdout)
        self.assertIn("fleet/readable docs/dev2 README:", run.stdout)

    def test_release_line_only_does_not_owe_sync_but_a_changed_sentence_does(self):
        self.row("one")
        self.assertEqual(self.run_rollout().returncode, 0)
        self.content(self.repo, self.workflow, self.latest, self.readme("0.38.1") + "Changed rule.\n")
        run = self.run_rollout()
        self.assertEqual(run.returncode, 1)
        self.assertIn("sync owed;", run.stdout)
        self.assertNotIn("no sync owed", run.stdout)

    def test_each_laws_file_change_owes_pin_and_identical_laws_do_not(self):
        self.row("one", pin=self.old)
        self.assertEqual(self.run_rollout().returncode, 0)
        for path in self.laws:
            with self.subTest(path=path):
                self.content(self.repo, path, self.latest, "changed laws\n")
                run = self.run_rollout()
                self.assertEqual(run.returncode, 1, run.stdout)
                self.assertIn(f"laws: {self.old} pin owed", run.stdout)
                self.content(self.repo, path, self.latest, "same laws\n")

    def test_unknown_pin_is_owed_and_missing_install_is_not(self):
        self.row("unknown", pin="3" * 40)
        self.row("uninstalled")
        run = self.run_rollout()
        self.assertEqual(run.returncode, 1)
        self.assertIn("pin unrecognised", run.stdout)
        self.assertIn("laws: not installed", run.stdout)
        self.rows.pop(0)
        self.assertEqual(self.run_rollout().returncode, 0)

    def test_non_commit_pin_is_printed_as_unrecognised(self):
        self.row("one", pin="main")
        run = self.run_rollout()
        self.assertEqual(run.returncode, 1)
        self.assertIn("laws: main pin unrecognised", run.stdout)

    def test_missing_state_branch_and_forbidden_laws_are_unreadable(self):
        from urllib.parse import quote
        repo = self.row("one")
        self.reply(["api", f"repos/{repo}/branches/{quote('spacedock-state/dev2', safe='')}"],
                   error="Not Found (HTTP 404)")
        self.assertEqual(self.run_rollout().returncode, 1)
        self.content(repo, ".github/workflows/dev2-laws.yml", "spacedock-state/dev2", error="Forbidden (HTTP 403)")
        run = self.run_rollout()
        self.assertEqual(run.returncode, 1)
        self.assertIn('unreadable: "Forbidden (HTTP 403)"', run.stdout)

    def test_search_reports_unlisted_and_failed_search_without_changing_exit(self):
        self.row("listed")
        self.reply(["api", "repos/fleet/unlisted"], {"default_branch": "main"})
        self.content("fleet/unlisted", "docs/dev2/README.md", "main", self.readme("0.38.0"))
        self.search([{"repository": {"nameWithOwner": "fleet/unlisted"}, "path": "docs/dev2/README.md"},
                     {"repository": {"nameWithOwner": "fleet/listed"}, "path": "docs/dev2/README.md"}])
        run = self.run_rollout()
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertIn("unlisted: fleet/unlisted docs/dev2/README.md", run.stdout)
        self.assertEqual(run.stdout.count("unlisted:"), 1)
        self.search(error="search quota exceeded")
        run = self.run_rollout()
        self.assertEqual(run.returncode, 0)
        self.assertIn('search: unavailable "search quota exceeded"', run.stdout)
        self.content(self.repo, self.workflow, self.latest, self.readme("0.38.1") + "Changed rule.\n")
        self.assertEqual(self.run_rollout().returncode, 1)

    def test_annotated_release_tag_resolves_to_its_commit(self):
        tags = self.responses[json.dumps(["api", f"repos/{self.repo}/git/matching-refs/tags/kc-dev-flow-2-v"])]["data"]
        tags[-1]["object"] = {"type": "tag", "sha": "a" * 40}
        self.reply(["api", f"repos/{self.repo}/git/tags/{'a' * 40}"],
                   {"object": {"type": "commit", "sha": self.latest}})
        self.row("one", pin=self.latest)
        self.assertEqual(self.run_rollout().returncode, 0)

    def test_missing_or_unreadable_local_list_fails(self):
        for listing in (self.root / "absent.md", self.root):
            with self.subTest(listing=str(listing)):
                run = subprocess.run([sys.executable, "-B", str(Path(pv.__file__)), "rollout", str(listing)],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, 1)
                self.assertIn("rollout: unreadable", run.stdout)
                self.assertNotIn("no sync owed", run.stdout)

    def test_missing_marker_and_package_read_failures_never_pass(self):
        repo = self.row("one")
        self.content(repo, "docs/dev2/README.md", "main", "---\ntrunk: main\n---\nNo marker\n")
        self.assertEqual(self.run_rollout().returncode, 1)
        self.content(repo, "docs/dev2/README.md", "main", self.readme("0.38.0"))
        self.content(self.repo, self.workflow, self.old, error="Not Found (HTTP 404)")
        self.assertEqual(self.run_rollout().returncode, 1)


if __name__ == "__main__":
    unittest.main()
