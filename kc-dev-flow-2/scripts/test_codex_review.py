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
T1, T2 = "2026-10-10T10:00:00Z", "2026-10-10T11:00:00Z"


def marker(sha, status, repo="o/r", pr=1, lead="<!-- codex-pull-request-review-summary -->\n", at=T1, user=BOT):
    meta = f'{{"headSha":"{sha}","status":"{status}","repository":"{repo}","pullRequestNumber":{pr}}}'
    return {"id": 9, "user": user, "created_at": at, "updated_at": at,
            "body": f"{lead}<!-- codex-security-review:v1 {meta} -->\n## Codex Review Summary"}


def said(sha, at=T1, ident=7, user=BOT, lead="Codex Review: Didn't find any major issues."):
    return {"id": ident, "user": user, "created_at": at, "body": f"{lead}\n\n**Reviewed commit:** `{sha}`\n"}


def review(sha, at=T1, ident=5, body="### Codex Review"):
    return {"id": ident, "user": BOT, "commit_id": sha, "submitted_at": at, "body": body}


def finding(original, badge="P2", review_id=5, at=T1, ident=11):
    return {"id": ident, "user": BOT, "original_commit_id": original, "commit_id": HEAD, "created_at": at,
            "pull_request_review_id": review_id,
            "body": f"**<sub><sub>![{badge} Badge](https://img.shields.io/badge/{badge}-yellow)</sub></sub> fix it**"}


def fake(reactions=(), inline=(), reviews=(), comments=(), heads=(HEAD,)):
    seen = iter(list(heads) + [heads[-1]] * 5)

    def call(*args):
        return {"headRefOid": next(seen)}

    def pages(path):
        if path.endswith("/reactions"):
            return list(reactions)
        if path.endswith("/reviews"):
            return list(reviews)
        return list(comments) if "/issues/" in path else list(inline)
    return call, pages


class CodexReviewTests(unittest.TestCase):
    def check(self, **kw):
        call, pages = fake(**kw)
        return codex.state("o/r", "1", call=call, pages=pages)

    def test_eyes_means_running(self):
        self.assertEqual(self.check(reactions=[{"user": BOT, "content": "eyes"}], comments=[said(HEAD[:10])])[0], 3)

    def test_findings_made_on_the_head_count_and_carried_ones_do_not(self):
        code, line = self.check(reviews=[review(HEAD)], inline=[finding(HEAD, "P1"), finding(HEAD, ident=12), finding(OLD, review_id=4)])
        self.assertEqual(code, 1)
        self.assertIn("2 line finding(s), 2 badge(s), 1 at P0/P1", line)
        self.assertIn("evidence=review:5", line)
        self.assertEqual(self.check(inline=[finding(OLD, review_id=4)])[0], 4)
        self.assertEqual(self.check(reviews=[review(OLD)])[0], 4)

    def test_clean_needs_evidence_that_names_the_head(self):
        self.assertEqual(self.check(comments=[said(HEAD[:10])])[0], 0)
        self.assertEqual(self.check(comments=[said(OLD[:10])])[0], 4)
        self.assertEqual(self.check(comments=[said(HEAD[:10], user=PERSON)])[0], 4)
        self.assertEqual(self.check(comments=[said(HEAD[:10], lead="Quoting an old note:")])[0], 4)
        self.assertEqual(self.check(comments=[marker(HEAD, "completed")])[0], 0)
        self.assertEqual(self.check(comments=[marker(OLD, "completed")])[0], 4)
        self.assertEqual(self.check(comments=[marker(HEAD, "running")])[0], 4)
        self.assertEqual(self.check(comments=[marker(HEAD, "completed", user=PERSON)])[0], 4)
        self.assertEqual(self.check(reactions=[{"user": BOT, "content": "+1"}])[0], 4)

    def test_a_marker_outside_codex_summary_or_for_another_pr_is_ignored(self):
        self.assertEqual(self.check(comments=[marker(HEAD, "completed", lead="Suggested change:\n")])[0], 4)
        self.assertEqual(self.check(comments=[marker(HEAD, "completed", pr=2)])[0], 4)
        self.assertEqual(self.check(comments=[marker(HEAD, "completed", repo="x/y")])[0], 4)
        below = marker(HEAD, "completed", lead="<!-- codex-pull-request-review-summary -->\n## Codex Review Summary\n")
        self.assertEqual(self.check(comments=[below])[0], 4)

    def test_the_latest_result_on_one_head_decides_and_names_itself(self):
        code, line = self.check(reviews=[review(HEAD, at=T1)], inline=[finding(HEAD)], comments=[said(HEAD[:10], at=T2)])
        self.assertEqual(code, 0)
        self.assertIn("evidence=comment:7", line)
        self.assertEqual(self.check(reviews=[review(HEAD, at=T2)], inline=[finding(HEAD)], comments=[said(HEAD[:10], at=T1)])[0], 1)
        self.assertIn("evidence=comment:7", self.check(comments=[said(HEAD[:10], at=T1, ident=7)])[1])
        self.assertIn("evidence=comment:8", self.check(comments=[said(HEAD[:10], at=T1, ident=7), said(HEAD[:10], at=T2, ident=8)])[1])

    def test_only_the_latest_reviews_own_findings_are_counted(self):
        code, line = self.check(reviews=[review(HEAD, at=T1, ident=5), review(HEAD, at=T2, ident=6)],
                                inline=[finding(HEAD, "P1", review_id=5), finding(HEAD, review_id=6, ident=12)])
        self.assertIn("1 line finding(s), 1 badge(s), 0 at P0/P1; evidence=review:6", line)

    def test_a_completed_summary_after_findings_is_not_clean(self):
        self.assertEqual(self.check(reviews=[review(HEAD, at=T1)], inline=[finding(HEAD)], comments=[marker(HEAD, "completed", at=T2)])[0], 1)
        self.assertEqual(self.check(reviews=[review(HEAD, at=T2)], inline=[finding(HEAD)], comments=[marker(HEAD, "completed", at=T1)])[0], 1)
        self.assertEqual(self.check(reviews=[review(HEAD, at=T1)], inline=[finding(HEAD)],
                                    comments=[marker(HEAD, "completed", at=T2), said(HEAD[:10], at="2026-10-10T12:00:00Z")])[0], 0)

    def test_every_codex_output_shape_with_a_badge_blocks_and_only_no_issues_is_clean(self):
        p1 = "![P1 Badge](https://img.shields.io/badge/P1-orange) body finding"
        code, line = self.check(reviews=[review(HEAD, body=p1)])
        self.assertEqual(code, 1)
        self.assertIn("1 at P0/P1", line)
        self.assertEqual(self.check(reviews=[review(HEAD, body="Codex Review: Didn't find any major issues.")])[0], 0)
        self.assertEqual(self.check(reviews=[review(HEAD, body="no badge, no verdict text")])[0], 1)
        self.assertEqual(self.check(reviews=[review(HEAD, body="Codex Review: Didn't find any major issues. " + p1)])[0], 1)
        self.assertEqual(self.check(comments=[said(HEAD[:10], lead="Codex Review: here is a note.")])[0], 4)
        named = {"id": 3, "user": BOT, "created_at": T1, "body": f"{p1}\n\n**Reviewed commit:** `{HEAD[:10]}`"}
        loose = {"id": 4, "user": BOT, "created_at": T1, "body": p1}
        other = {"id": 6, "user": BOT, "created_at": T1, "body": f"{p1}\n\n**Reviewed commit:** `{OLD[:10]}`"}
        self.assertEqual(self.check(comments=[named])[0], 1)
        self.assertEqual(self.check(comments=[loose])[0], 1)
        self.assertEqual(self.check(comments=[other])[0], 4)
        self.assertEqual(self.check(comments=[named, marker(HEAD, "completed", at=T2)])[0], 1)

    def test_a_head_that_moves_while_reading_has_no_verdict(self):
        self.assertEqual(self.check(comments=[said(HEAD[:10])], heads=(HEAD, OLD))[0], 4)

    def test_a_failed_gh_call_or_bad_arguments_is_a_configuration_error(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(codex.main(["no-slash", "1"]), 2)
            with mock.patch.object(codex, "state", side_effect=RuntimeError("gh: not logged in")):
                self.assertEqual(codex.main(["o/r", "1"]), 2)


if __name__ == "__main__":
    unittest.main()
