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
APPROVAL = "<!-- ccr-overview-v2 -->\n\n### 🟢 Approval recommended\n\n版本一致。\n\n**0 open findings**\n"
CHANGES = "<!-- ccr-overview-v2 -->\n\n### 🟡 Changes recommended\n\n<summary><strong>2 open findings</strong></summary>\n"
LEGACY = "## Pull request overview\n\nCopilot reviewed 19 out of 19 changed files and generated no comments.\n"


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

    def test_an_answer_on_the_head_names_the_review_its_heading_and_line_comments(self):
        code, out = self.run_state([review(2, CHANGES)], [line(10, 2), line(11, 2), line(12, 9)],
                                   timeline=[asked("2026-10-12T08:19:28Z")])
        self.assertEqual(code, 0)
        self.assertIn('"🟡 Changes recommended", 2 line comment(s); evidence=review:2', out)

    def test_the_answer_is_reported_the_same_whatever_copilot_found(self):
        self.assertIn('"🟢 Approval recommended"', self.run_state([review(1, APPROVAL)])[1])
        self.assertIn('"Pull request overview"', self.run_state([review(3, LEGACY)])[1])
        self.assertIn('"no heading"', self.run_state([review(4, "Looks good")])[1])

    def test_a_heading_cannot_carry_its_own_evidence_id(self):
        body = "<!-- ccr-overview-v2 -->\n\n### 🟢 Approval evidence=review:999\n"
        out = self.run_state([review(2, body)])[1]
        self.assertEqual(out.count("evidence="), 1)
        self.assertIn("evidence=review:2", out)

    def test_the_latest_review_of_the_head_is_named(self):
        reviews = [review(1, CHANGES, at="2026-10-12T08:00:00Z"), review(2, APPROVAL, at="2026-10-12T09:00:00Z")]
        self.assertIn("evidence=review:2", self.run_state(reviews)[1])

    def test_a_request_after_the_head_review_is_still_waiting(self):
        code, _ = self.run_state([review(1, APPROVAL, at="2026-10-12T08:00:00Z")],
                                 timeline=[asked("2026-10-12T08:05:00Z")])
        self.assertEqual(code, 3)

    def test_an_answered_request_on_an_older_head_is_not_still_pending(self):
        reviews = [review(1, CHANGES, commit=OLD, at="2026-10-12T08:10:00Z")]
        code, out = self.run_state(reviews, timeline=[asked("2026-10-12T08:05:00Z")])
        self.assertEqual(code, 4)
        self.assertIn("no Copilot review covers", out)

    def test_a_review_of_an_older_commit_does_not_cover_the_head(self):
        code, out = self.run_state([review(1, APPROVAL, commit=OLD)])
        self.assertEqual(code, 4)
        self.assertNotIn("evidence=", out)

    def test_a_head_that_moves_while_reading_is_not_reviewed(self):
        self.assertEqual(self.run_state([review(1, APPROVAL)], heads=(HEAD, OLD))[0], 4)

    def test_bad_arguments_are_a_configuration_error(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cr.main(["no-slash", "1"]), 2)


if __name__ == "__main__":
    unittest.main()
