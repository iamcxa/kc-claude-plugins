import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("codex_review", Path(__file__).with_name("codex_review.py"))
codex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codex)

HEAD, OLD = "a" * 40, "b" * 40
BOT, PERSON = {"login": codex.BOT}, {"login": "someone"}


def marker(sha, status, repo="o/r", pr=1, lead="<!-- codex-pull-request-review-summary -->\n"):
    meta = f'{{"headSha":"{sha}","status":"{status}","repository":"{repo}","pullRequestNumber":{pr}}}'
    return f"{lead}<!-- codex-security-review:v1 {meta} -->\n## Codex Review Summary"


def fake(reactions=(), inline=(), reviews=(), comments=(), head_date="2026-10-10T10:00:00Z"):
    def call(*args):
        if args[0] == "pr":
            return {"headRefOid": HEAD}
        return {"commit": {"committer": {"date": head_date}}}

    def pages(path):
        if path.endswith("/reactions"):
            return list(reactions)
        if path.endswith("/reviews"):
            return list(reviews)
        return list(comments) if "/issues/" in path else list(inline)
    return call, pages


def finding(original, badge="P2"):
    return {"user": BOT, "original_commit_id": original, "commit_id": HEAD,
            "body": f"**<sub><sub>![{badge} Badge](https://img.shields.io/badge/{badge}-yellow)</sub></sub> fix it**"}


class CodexReviewTests(unittest.TestCase):
    def check(self, **kw):
        call, pages = fake(**kw)
        return codex.state("o/r", "1", call=call, pages=pages)

    def test_eyes_means_running(self):
        self.assertEqual(self.check(reactions=[{"user": BOT, "content": "eyes", "created_at": "2026-10-10T11:00:00Z"}])[0], 3)

    def test_findings_made_on_the_head_count_and_carried_ones_do_not(self):
        code, line = self.check(inline=[finding(HEAD, "P1"), finding(HEAD), finding(OLD)])
        self.assertEqual(code, 1)
        self.assertIn("2 line comment(s), 1 at P0/P1", line)
        self.assertEqual(self.check(inline=[finding(OLD)])[0], 4)

    def test_a_codex_review_on_the_head_is_a_finding(self):
        self.assertEqual(self.check(reviews=[{"user": BOT, "commit_id": HEAD}])[0], 1)
        self.assertEqual(self.check(reviews=[{"user": BOT, "commit_id": OLD}])[0], 4)

    def test_clean_needs_evidence_that_covers_the_head(self):
        self.assertEqual(self.check(comments=[{"user": BOT, "body": marker(HEAD, "completed")}])[0], 0)
        self.assertEqual(self.check(comments=[{"user": BOT, "body": marker(OLD, "completed")}])[0], 4)
        self.assertEqual(self.check(comments=[{"user": BOT, "body": marker(HEAD, "running")}])[0], 4)

    def test_a_marker_outside_codex_summary_or_for_another_pr_is_ignored(self):
        quoted = "Suggested change:\n" + marker(HEAD, "completed", lead="")
        self.assertEqual(self.check(comments=[{"user": BOT, "body": quoted}])[0], 4)
        self.assertEqual(self.check(comments=[{"user": BOT, "body": marker(HEAD, "completed", pr=2)}])[0], 4)
        self.assertEqual(self.check(comments=[{"user": BOT, "body": marker(HEAD, "completed", repo="x/y")}])[0], 4)
        below = "<!-- codex-pull-request-review-summary -->\n## Codex Review Summary\n" + marker(HEAD, "completed", lead="")
        self.assertEqual(self.check(comments=[{"user": BOT, "body": below}])[0], 4)
        self.assertEqual(self.check(comments=[{"user": PERSON, "body": marker(HEAD, "completed")}])[0], 4)
        self.assertEqual(self.check(reactions=[{"user": BOT, "content": "+1", "created_at": "2026-10-10T11:00:00Z"}])[0], 0)
        self.assertEqual(self.check(reactions=[{"user": BOT, "content": "+1", "created_at": "2026-10-10T09:00:00Z"}])[0], 4)

    def test_a_failed_gh_call_or_bad_arguments_is_a_configuration_error(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(codex.main(["no-slash", "1"]), 2)
            with mock.patch.object(codex, "state", side_effect=RuntimeError("gh: not logged in")):
                self.assertEqual(codex.main(["o/r", "1"]), 2)


if __name__ == "__main__":
    unittest.main()
