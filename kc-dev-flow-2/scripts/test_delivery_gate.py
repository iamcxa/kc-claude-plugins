import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("delivery_gate", Path(__file__).with_name("delivery_gate.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

HEAD40 = "40c714a6" + "0" * 32


def report(heading, verdict_line):
    return f"## Stage Report: {heading}\n\n- DONE: Verdict\n  {verdict_line}\n\n### Summary\n\nok\n"


TASK = "# task\n\n" + report("ideation", "Verdict PASSED at 1111111a") + report("validation", "Verdict PASSED at 0830a3be (detached)") \
    + report("validation (cycle 2)", "Verdict PASSED at d127ec71 (base 9e68eb87)") \
    + report("validation (cycle 3)", f"Verdict PASSED at {HEAD40} (all checks pass)")

COPILOT_UNSTATED = ("Deliver #627 head 22d9cc94? Codex round 1 review:5500046230 found one P1. "
                    "Second reviewer: copilot because the change touches review rules; not requested: Copilot refused for quota.")
COPILOT_NOT_RUN = COPILOT_UNSTATED.replace("not requested:", "copilot not run:")


class DeliveryGateTests(unittest.TestCase):
    def check(self, task=TASK, text="", head="40c714a6", gh=None, pr="o/r#9"):
        with tempfile.TemporaryDirectory() as d:
            task_file, text_file = Path(d, "task.md"), Path(d, "gate.txt")
            task_file.write_text(task)
            text_file.write_text(text)
            argv = ["check", str(task_file), "--pr", pr, "--text-file", str(text_file)] + (["--head", head] if head else [])
            out = io.StringIO()
            with contextlib.redirect_stdout(out), mock.patch.object(gate, "run_gh", gh or mock.Mock(side_effect=AssertionError("gh called"))):
                code = gate.main(argv)
            return code, out.getvalue()

    def test_the_latest_passing_report_names_the_candidate(self):
        self.assertEqual(gate.validated_candidate(TASK), HEAD40)
        first = report("validation", "Verdict PASSED at 0830a3be") + report("validation (cycle 2)", "Verdict REJECTED at d127ec71")
        self.assertEqual(gate.validated_candidate(first), "0830a3be")

    def test_the_candidate_is_the_sha_after_the_verdict_within_160_characters(self):
        for line, sha in (("Verdict PASSED, candidate 0830a3be checked out", "0830a3be"),
                          ("Verdict PASSED. Candidate #631 head 085e28aa30872fbdf6341640a8ae16b8504c4083 (Draft), base 9e68eb87",
                           "085e28aa30872fbdf6341640a8ae16b8504c4083"),
                          ("Verdict PASSED; defaced decade 2026-10-13 abc123 then aff49ab3", "aff49ab3"),
                          ("Verdict PASSED " + "x" * 150 + " aff49ab3", "aff49ab3")):
            with self.subTest(line):
                self.assertEqual(gate.validated_candidate(report("validation", line)), sha)
        for line in ("Verdict PASSED with one finding; diff is 12 files", "aff49ab3 earlier. Verdict PASSED",
                     "Verdict PASSED " + "x" * 161 + " aff49ab3", "Verdict PASSED at aff49ab34Z"):
            with self.subTest(line):
                self.assertIsNone(gate.validated_candidate(report("validation", line)))

    def test_every_accepted_verdict_form_names_its_candidate(self):
        relay = "Verdict: PASSED, recommended. Artifact: candidate 985200258eebc7aad832716fa8e4b8b57518921f (branch b, base 1234567), unmodified"
        relay_repaired = relay.replace("Verdict:", "Verdict", 1)
        for line, sha in ((relay, "985200258eebc7aad832716fa8e4b8b57518921f"),
                          (relay_repaired, "985200258eebc7aad832716fa8e4b8b57518921f"),
                          ("Verdict PASSED at 0830a3be (base 1234567)", "0830a3be"),
                          ("Verdict: PASSED, recommended. Artifact: candidate 0830a3be", "0830a3be"),
                          ("Verdict recommended: PASSED. No Material finding. Candidate 0830a3be", "0830a3be"),
                          ("Verdict recommendation: PASSED, with one finding. Candidate 0830a3be", "0830a3be"),
                          ("Verdict: recommend PASSED. Candidate 0830a3be", "0830a3be"),
                          ("**Verdict: PASSED.** Candidate HEAD 0830a3be", "0830a3be"),
                          ("**Verdict:** PASSED at 0830a3be", "0830a3be")):
            with self.subTest(line):
                self.assertEqual(gate.validated_candidate(report("validation", line)), sha)

    def test_the_relay_report_that_held_passes_at_the_same_head(self):
        sha = "985200258eebc7aad832716fa8e4b8b57518921f"
        for line in (f"Verdict: PASSED, recommended. Artifact: candidate {sha} (branch b, base 1234567), unmodified",
                     f"Verdict PASSED, recommended. Artifact: candidate {sha} (branch b, base 1234567), unmodified"):
            with self.subTest(line):
                code, out = self.check(task=report("validation", line), head=sha)
                self.assertEqual(code, 0, out)
                self.assertIn("equals validated candidate", out)

    def test_forms_outside_the_family_name_no_candidate(self):
        for line in ("PASSED. HEAD 0830a3be, merge-base 1234567", "Recommend PASSED. Candidate 0830a3be",
                     "Independent verdict: PASSED. Candidate 0830a3be",
                     "Verdict PASSED" + " " + "x" * 159 + " 0830a3be",
                     "Verdict PASSED with one finding",
                     "Verdict PASSED or REJECTED naming head 84de8242",
                     "Verdict PASSED/REJECTED naming head 84de8242"):
            with self.subTest(line):
                code, out = self.check(task=report("validation", line), head="84de8242")
                self.assertEqual(code, 2, out)
                self.assertIn("names a candidate SHA", out)

    def test_a_rejected_or_verdictless_report_holds_even_when_it_quotes_an_earlier_passed(self):
        rejected = "Verdict REJECTED at 1111111a: one Material finding."
        cases = {
            "rejected": rejected,
            "rejected quoting an earlier passed": rejected + "\n  Cycle 1 read Verdict PASSED at 2222222b.",
            "rejected, then a counting passed line": rejected + "\n  Verdict PASSED at 2222222b (the withdrawn cycle 1).",
            "rejected, recommended spelling": "Verdict: REJECTED, recommended. Cycle 1 read Verdict: PASSED at 2222222b.",
            "no verdict word": "all checks pass at 2222222b",
        }
        for label, line in cases.items():
            with self.subTest(label):
                code, out = self.check(task=report("validation", line), head="2222222b")
                self.assertEqual(code, 2, out)
                self.assertIn("names a candidate SHA", out)

    def test_a_qualified_or_quoted_verdict_is_not_the_verdict(self):
        for label, line in {
            "independent label then rejection": "Independent Verdict: PASSED at 2222222b. Verdict REJECTED at 3333333c.",
            "prior label then rejection": "Prior Verdict: PASSED at 2222222b\n  Verdict REJECTED at 3333333c.",
            "quote only": "Cycle 1 read Verdict PASSED at 2222222b and was withdrawn.",
            "word then label": "the earlier Verdict: PASSED, recommended at 2222222b",
        }.items():
            with self.subTest(label):
                self.assertEqual(self.check(task=report("validation", line), head="2222222b")[0], 2)
        for line in ("All ACs hold. Verdict: PASSED at 2222222b", "1. Verdict PASSED at 2222222b",
                     "### Verdict: PASSED at 2222222b",
                     "Cycle 1 read Verdict REJECTED at 1111111a. Verdict PASSED at 2222222b"):
            with self.subTest(line):
                self.assertEqual(self.check(task=report("validation", line), head="2222222b")[0], 0)

    def test_a_template_line_naming_both_outcomes_is_skipped_not_decisive(self):
        echo = ("## Stage Report: validation\n\n- DONE: Verdict PASSED or REJECTED naming the head\n"
                "  Verdict PASSED at 2222222b\n\n### Summary\n\nok\n")
        self.assertEqual(self.check(task=echo, head="2222222b")[0], 0)
        rejected = echo.replace("Verdict PASSED at 2222222b", "Verdict REJECTED at 2222222b")
        self.assertEqual(self.check(task=rejected, head="2222222b")[0], 2)

    def test_two_rejected_sections_hold_and_a_rejected_latest_does_not_supply_its_own_quote(self):
        rejected = report("validation", "Verdict REJECTED at 1111111a") \
            + report("validation (cycle 2)", "Verdict REJECTED at 3333333c. Cycle 1 read Verdict PASSED at 2222222b.")
        self.assertEqual(self.check(task=rejected, head="2222222b")[0], 2)
        older_passed = report("validation", "Verdict PASSED at 1111111a") \
            + report("validation (cycle 2)", "Verdict REJECTED at 3333333c. Cycle 1 read Verdict PASSED at 2222222b.")
        self.assertEqual(gate.validated_candidate(older_passed), "1111111a")
        self.assertEqual(self.check(task=older_passed, head="2222222b")[0], 1)

    def test_equal_or_prefix_equal_heads_pass_and_a_different_head_fails_naming_both(self):
        for head in ("40c714a6", HEAD40, "40c714a"):
            with self.subTest(head):
                self.assertEqual(self.check(head=head)[0], 0)
        code, out = self.check(head="7679ab7a")
        self.assertEqual(code, 1)
        self.assertIn(f"7679ab7a differs from validated candidate {HEAD40}", out)

    def test_taking_the_first_passing_report_would_be_caught(self):
        self.assertEqual(self.check(head="0830a3be")[0], 1)

    def test_the_head_comes_from_gh_when_not_given(self):
        gh = mock.Mock(return_value=HEAD40.upper())
        self.assertEqual(self.check(head=None, gh=gh)[0], 0)
        gh.assert_called_once_with("o/r", "9")
        self.assertEqual(self.check(head=None, gh=mock.Mock(return_value="7679ab7a"))[0], 1)

    def test_gh_runs_pr_view_for_the_head_oid(self):
        done = subprocess.CompletedProcess([], 0, stdout='{"headRefOid": "abc1234"}', stderr="")
        with mock.patch.object(gate.subprocess, "run", return_value=done) as run:
            self.assertEqual(gate.run_gh("o/r", "9"), "abc1234")
        self.assertEqual(run.call_args.args[0], ["gh", "pr", "view", "9", "--repo", "o/r", "--json", "headRefOid"])

    def test_cases_that_cannot_compare_exit_2_and_say_why(self):
        cases = {
            "no candidate": dict(task=report("validation", "Verdict PASSED with no sha")),
            "no report": dict(task="# task\n"),
            "gh fails": dict(head=None, gh=mock.Mock(side_effect=RuntimeError("gh pr view exited 1: not found"))),
            "gh missing": dict(head=None, gh=mock.Mock(side_effect=FileNotFoundError("gh"))),
            "bad gh json": dict(head=None, gh=mock.Mock(side_effect=ValueError("bad json"))),
            "bad head": dict(head="main"),
            "bad pr": dict(pr="nonsense"),
        }
        for label, kwargs in cases.items():
            with self.subTest(label):
                code, out = self.check(**kwargs)
                self.assertEqual(code, 2)
                self.assertTrue(out.strip())
        self.assertIn("no passing validation report", self.check(**cases["no candidate"])[1])
        self.assertIn("cannot read the head of o/r#9", self.check(**cases["gh fails"])[1])

    def test_a_missing_input_file_exits_2(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gate.main(["check", "/nonexistent/task.md", "--pr", "o/r#9", "--text-file", "/nonexistent/t.txt"]), 2)

    def test_a_second_reviewer_without_a_stated_outcome_fails_even_if_another_reviewer_has_a_token(self):
        code, out = self.check(text=COPILOT_UNSTATED)
        self.assertEqual(code, 1)
        self.assertIn("second reviewer copilot has no stated outcome", out)

    def test_a_stated_outcome_passes(self):
        cases = {
            "not run with a reason": COPILOT_NOT_RUN,
            "a review token in a sentence naming it": "Second reviewer: copilot because it touches merge. Copilot review:5500046231 had no P1.",
            "a comment token": "Second reviewer: Copilot because it touches merge; copilot left comment:123 in one sentence.",
            "not triggered": "Second reviewer: not triggered (Surfaces none).",
            "no such line": "Deliver #1 head 40c714a6. Codex review:5500046230.",
            "empty text": "",
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assertEqual(self.check(text=text), (0, mock.ANY))

    def test_a_not_run_with_no_reason_or_a_token_for_another_name_does_not_count(self):
        for text in ("Second reviewer: copilot because merge path; copilot not run:\n",
                     "Second reviewer: copilot because merge path. Codex review:5500046230."):
            with self.subTest(text):
                self.assertEqual(self.check(text=text)[0], 1)

    def test_both_problems_are_printed_and_exit_1_wins_over_exit_2(self):
        code, out = self.check(text=COPILOT_UNSTATED, head="7679ab7a")
        self.assertEqual(code, 1)
        self.assertIn("differs from validated candidate", out)
        self.assertIn("second reviewer copilot", out)
        code, out = self.check(task="# task\n", text=COPILOT_UNSTATED)
        self.assertEqual(code, 1)
        self.assertIn("no passing validation report", out)

    def test_each_exit_ends_with_the_next_line_for_the_ask(self):
        cases = (
            (0, dict(), ["next: ask for merge with this text."]),
            (1, dict(head="7679ab7a"), ["next: hold the ask; revalidate this head or tell the Captain the difference."]),
            (1, dict(text=COPILOT_UNSTATED), ["next: hold the ask until each second reviewer has an outcome."]),
            (1, dict(head="7679ab7a", text=COPILOT_UNSTATED),
             ["next: hold the ask; revalidate this head or tell the Captain the difference.",
              "next: hold the ask until each second reviewer has an outcome."]),
            (2, dict(task="# task\n"), ["next: hold the ask and show the Captain these lines."]),
        )
        for expected, kwargs, nexts in cases:
            with self.subTest(kwargs=kwargs):
                code, out = self.check(**kwargs)
                self.assertEqual(code, expected, out)
                self.assertEqual([line for line in out.splitlines() if line.startswith("next:")], nexts, out)
                self.assertTrue(out.splitlines()[-1].startswith("next:"), out)


if __name__ == "__main__":
    unittest.main()
