#!/usr/bin/env python3
import contextlib
import importlib.util
import io
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("copilot_review", Path(__file__).with_name("copilot_review.py"))
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)

HEAD = "a" * 40
OLD = "b" * 40
REPO, PR = "o/r", "7"
ICON = '<img src="x.png" alt="{} severity" width="62">'
CLEAN = "<!-- ccr-overview-v2 -->\n\n### 🟢 Approval recommended\n\n版本一致。\n\n**0 open findings**\n"
FINDINGS = ("<!-- ccr-overview-v2 -->\n\n### 🟡 Changes recommended\n\n<details open>\n"
            "<summary><strong>2 open findings</strong></summary>\n\n- " + ICON.format("High")
            + " ordering\n- " + ICON.format("Medium") + " quota\n</details>\n")
LEGACY_CLEAN = "## Pull request overview\n\nCopilot reviewed 19 out of 19 changed files and generated no comments.\n"


def review(rid, body, commit=HEAD, at="2026-10-12T08:21:29Z"):
    return {"id": rid, "user": {"login": cr.BOT}, "body": body, "commit_id": commit, "submitted_at": at}


def line(cid, review_id):
    return {"id": cid, "user": {"login": "Copilot"}, "pull_request_review_id": review_id, "body": "x"}


def asked(at):
    return {"event": "review_requested", "created_at": at, "requested_reviewer": {"login": "Copilot"}}


class CopilotReviewTest(unittest.TestCase):
    def run_state(self, reviews=(), lines=(), timeline=(), heads=(HEAD, HEAD)):
        seq = iter(heads)
        call = lambda *a: {"headRefOid": next(seq)}
        data = {f"repos/{REPO}/pulls/{PR}/reviews": list(reviews),
                f"repos/{REPO}/pulls/{PR}/comments": list(lines),
                f"repos/{REPO}/issues/{PR}/timeline": list(timeline)}
        return cr.state(REPO, PR, call=call, pages=lambda path: data[path])

    def test_zero_open_findings_on_the_head_is_clean(self):
        code, out = self.run_state([review(1, CLEAN)], timeline=[asked("2026-10-12T08:19:28Z")])
        self.assertEqual(code, 0)
        self.assertIn("evidence=review:1", out)

    def test_open_findings_count_high_as_the_top_level(self):
        code, out = self.run_state([review(2, FINDINGS)], [line(10, 2), line(11, 2)])
        self.assertEqual(code, 1)
        self.assertIn("2 open finding(s), 1 at High or above", out)

    def test_a_line_comment_on_a_zero_count_review_is_still_a_finding(self):
        self.assertEqual(self.run_state([review(1, CLEAN)], [line(10, 1)])[0], 1)

    def test_the_older_overview_format(self):
        self.assertEqual(self.run_state([review(3, LEGACY_CLEAN)])[0], 0)
        self.assertEqual(self.run_state([review(3, LEGACY_CLEAN.replace("no comments", "2 comments"))])[0], 1)

    def test_an_unknown_shape_is_never_clean(self):
        self.assertEqual(self.run_state([review(4, "Looks good to me!")])[0], 4)
        self.assertEqual(self.run_state([review(4, "Looks good to me!")], [line(10, 4)])[0], 1)

    def test_a_review_of_an_older_commit_does_not_cover_the_head(self):
        code, out = self.run_state([review(1, CLEAN, commit=OLD)])
        self.assertEqual(code, 4)
        self.assertIn("no Copilot review covers", out)

    def test_a_request_after_the_last_review_is_running(self):
        code, _ = self.run_state([review(1, CLEAN, at="2026-10-12T08:00:00Z")],
                                 timeline=[asked("2026-10-12T08:05:00Z")])
        self.assertEqual(code, 3)

    def test_the_latest_review_of_the_head_decides(self):
        reviews = [review(1, FINDINGS, at="2026-10-12T08:00:00Z"), review(2, CLEAN, at="2026-10-12T09:00:00Z")]
        self.assertEqual(self.run_state(reviews, [line(10, 1)])[0], 0)

    def test_a_head_that_moves_while_reading_is_not_reviewed(self):
        self.assertEqual(self.run_state([review(1, CLEAN)], heads=(HEAD, OLD))[0], 4)

    def test_bad_arguments_are_a_configuration_error(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cr.main(["no-slash", "1"]), 2)


if __name__ == "__main__":
    unittest.main()
