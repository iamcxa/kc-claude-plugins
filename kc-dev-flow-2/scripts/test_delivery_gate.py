import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("delivery_gate", Path(__file__).with_name("delivery_gate.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

HEAD40 = "40c714a6" + "0" * 32
S1, S2 = HEAD40, "7679ab7a" + "1" * 32


def record(*heads, body="## Checklist\n\n- one\n"):
    lines = "".join(f"Candidate: {h}\n" for h in heads)
    return f"# validation dispatch\n\nDispatched: {'a' * 40}\nModel: sonnet\n{lines}\n{body}"


TASK = "---\nprofile: pilot\n---\n\n# task\n"
RECORDS = {"validation-1.md": record(HEAD40)}

COPILOT_UNSTATED = ("Deliver #627 head 22d9cc94? Codex round 1 review:5500046230 found one P1. "
                    "Second reviewer: copilot because the change touches review rules; not requested: Copilot refused for quota.")
COPILOT_NOT_RUN = COPILOT_UNSTATED.replace("not requested:", "copilot not run:")


class DeliveryGateTests(unittest.TestCase):
    def check(self, task=TASK, text="", head="40c714a6", gh=None, pr="o/r#9", records=RECORDS):
        with tempfile.TemporaryDirectory() as d:
            task_file, text_file = Path(d, "task.md"), Path(d, "gate.txt")
            task_file.write_text(task)
            text_file.write_text(text)
            if records is not None:
                Path(d, "task", "dispatch").mkdir(parents=True)
                for name, content in records.items():
                    Path(d, "task", "dispatch", name).write_text(content)
            argv = ["check", str(task_file), "--pr", pr, "--text-file", str(text_file)] + (["--head", head] if head else [])
            out = io.StringIO()
            with contextlib.redirect_stdout(out), mock.patch.object(gate, "run_gh", gh or mock.Mock(side_effect=AssertionError("gh called"))):
                code = gate.main(argv)
            return code, out.getvalue()

    def test_a_head_no_validation_was_dispatched_on_exits_1_naming_both(self):
        records = {"validation-1.md": record(S1)}
        code, out = self.check(head=S2, records=records)
        self.assertEqual(code, 1)
        self.assertIn(S1, out)
        self.assertIn(S2, out)
        self.assertIn("next: hold the ask; revalidate this head or tell the Captain the difference.", out)
        for head in (S1, S1[:7], S1.upper()):
            with self.subTest(head):
                self.assertEqual(self.check(head=head, records=records)[0], 0)

    def test_a_record_without_the_one_form_holds_and_prints_the_form(self):
        cases = {
            "no dispatch folder": None,
            "no validation record": {"ideation-1.md": record(S1)},
            "no line": {"validation-1.md": record()},
            "8-character sha": {"validation-1.md": "Candidate: 40c714a6\n"},
            "text after the sha": {"validation-1.md": f"Candidate: {S1} (branch x)\n"},
            "relay form": {"validation-1.md": f"Candidate: spacedock {S1}; marketplace {S2}\n"},
            "line under the first heading": {"validation-1.md": f"# r\n\n## Scope notes\n\nCandidate: {S1}\n"},
            "valid line only in an older record": {"validation-1.md": record(S1), "validation-2.md": record()},
        }
        for label, records in cases.items():
            with self.subTest(label):
                code, out = self.check(head=S1, records=records)
                self.assertEqual(code, 2, out)
                self.assertIn("Candidate: <40-hex head>", out)

    def test_the_highest_numbered_record_decides_and_a_record_may_name_several_heads(self):
        records = {"validation-2.md": record(S1), "validation-10.md": record(S2)}
        self.assertEqual(self.check(head=S2, records=records)[0], 0)
        code, out = self.check(head=S1, records=records)
        self.assertEqual(code, 1)
        self.assertIn(S2, out)
        both = {"validation-1.md": record(S1, S2)}
        for head, expected in ((S1, 0), (S2, 0), ("3" * 40, 1)):
            with self.subTest(head):
                self.assertEqual(self.check(head=head, records=both)[0], expected)

    def test_the_check_reads_no_validation_report_and_claims_no_verdict(self):
        rejected = f"{TASK}\n## Stage Report: validation\n\nVerdict REJECTED at {S1}\n"
        for label, task in (("a REJECTED report", rejected), ("no report", TASK)):
            with self.subTest(label):
                self.assertEqual(self.check(task=task, head=S1)[0], 0)
        outputs = [self.check(head=S1)[1], self.check(head=S2)[1], self.check(head=S1, records=None)[1],
                   self.check(head=S1, text=COPILOT_UNSTATED)[1]]
        for out in outputs:
            self.assertNotIn("passed", out.lower())

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
            "no line": dict(records={"validation-1.md": record()}),
            "no record folder": dict(records=None),
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
        self.assertIn("Candidate: <40-hex head>", self.check(**cases["no line"])[1])
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
        self.assertIn("differs from dispatched candidate", out)
        self.assertIn("second reviewer copilot", out)
        code, out = self.check(records=None, text=COPILOT_UNSTATED)
        self.assertEqual(code, 1)
        self.assertIn("Candidate: <40-hex head>", out)

    def test_each_exit_ends_with_the_next_line_for_the_ask(self):
        cases = (
            (0, dict(), ["next: ask for merge with this text."]),
            (1, dict(head="7679ab7a"), ["next: hold the ask; revalidate this head or tell the Captain the difference."]),
            (1, dict(text=COPILOT_UNSTATED), ["next: hold the ask until each second reviewer has an outcome."]),
            (1, dict(head="7679ab7a", text=COPILOT_UNSTATED),
             ["next: hold the ask; revalidate this head or tell the Captain the difference.",
              "next: hold the ask until each second reviewer has an outcome."]),
            (2, dict(head="main"), ["next: hold the ask and show the Captain these lines."]),
            (2, dict(records=None), ["next: hold the ask; dispatch validation of this head with a Candidate line, or tell the Captain."]),
        )
        for expected, kwargs, nexts in cases:
            with self.subTest(kwargs=kwargs):
                code, out = self.check(**kwargs)
                self.assertEqual(code, expected, out)
                self.assertEqual([line for line in out.splitlines() if line.startswith("next:")], nexts, out)
                self.assertTrue(out.splitlines()[-1].startswith("next:"), out)


REPORT = """tob_security_review:
  pr: 347
  findings:
    - file: "public/llms.txt"
      severity: HIGH
      title: "first"
    - file: "public/llms.txt"
      severity: MEDIUM
      title: "second"
    - file: "public/llms.txt"
      severity: LOW
      title: "third"
"""
SECURITY = (f"Security review (validation): security/validation-1.yaml at {HEAD40}\n"
            "Security finding (validation 1) 1: Needs decision: cap sessions\n"
            "Security finding (validation 1) 2: Needs decision: add the sentence\n"
            "Security finding (validation 1) 3: declined: stated unverified\n")
PILOT_OUT = (f"PR head {HEAD40[:8]} equals dispatched candidate {HEAD40[:8]}; no second reviewer outcome is missing\n"
             "next: ask for merge with this text.\n")


class ProdSecurityReviewTests(unittest.TestCase):
    def run_gate(self, profile="prod", review=SECURITY, report=REPORT, records=RECORDS, head=HEAD40[:8]):
        with tempfile.TemporaryDirectory() as d:
            task_file, text_file = Path(d, "task.md"), Path(d, "gate.txt")
            task_file.write_text(f"---\ntitle: x\nprofile: {profile}\n---\n\n## Stage Report: validation\n\n{review}")
            text_file.write_text("Merge ask.")
            Path(d, "task", "security").mkdir(parents=True)
            Path(d, "task", "dispatch").mkdir()
            for name, content in records.items():
                Path(d, "task", "dispatch", name).write_text(content)
            if report is not None:
                Path(d, "task", "security", "validation-1.yaml").write_text(report)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = gate.main(["check", str(task_file), "--pr", "o/r#9", "--text-file", str(text_file), "--head", head])
            return code, out.getvalue().replace(d, "<tmp>")

    def test_a_pilot_task_prints_exactly_what_it_printed_before(self):
        self.assertEqual(self.run_gate(profile="pilot", review="", report=None), (0, PILOT_OUT))

    def test_a_prod_task_with_a_disposed_review_gets_one_more_line_of_ten_words(self):
        code, out = self.run_gate()
        self.assertEqual(code, 0, out)
        added = out.replace(PILOT_OUT.splitlines()[0] + "\n", "").replace(PILOT_OUT.splitlines()[1] + "\n", "")
        self.assertEqual(added, "validation security review security/validation-1.yaml: 3 findings, 1 declined, 2 decisions\n")
        self.assertEqual(len(added.split()), 10)
        self.assertEqual(len(out.split()) - len(PILOT_OUT.split()), 10)

    def test_a_prod_task_with_a_hole_in_its_review_exits_1_and_holds_the_ask(self):
        cases = {
            "no review": (dict(review=""), "needs a 'Security review (validation):' line"),
            "not run": (dict(review="Security review (validation): not run: reviewer returned no report (sonnet)\n", report=None),
                        "validation security review not run"),
            "refusal saved as the report": (dict(report="I can't help with this request."), "is not a tob_security_review report"),
            "open Material": (dict(review=SECURITY.replace("1: Needs decision: cap sessions", "1: Material: cap sessions")),
                              "is Material and open at this head"),
            "another head": (dict(review=SECURITY.replace(HEAD40, "b" * 40)), "no 'Security review (validation):' line has the form"),
        }
        hold = "next: hold the ask; run the validation security review at this head, or tell the Captain."
        for label, (kwargs, why) in cases.items():
            with self.subTest(label):
                code, out = self.run_gate(**kwargs)
                self.assertEqual(code, 1, out)
                self.assertIn(why, out)
                self.assertEqual(out.splitlines()[-1], hold)

    def test_a_prod_task_with_no_dispatched_candidate_still_exits_2(self):
        code, out = self.run_gate(records={"validation-1.md": record()})
        self.assertEqual(code, 2, out)
        self.assertNotIn("Security review", out)

    def test_the_review_must_be_at_the_candidate_the_pr_head_equals(self):
        both = {"validation-1.md": record(HEAD40, S2)}
        for label, head, review, expected in (
                ("review at the other candidate", S2[:8], SECURITY, 1),
                ("review at the pr head", S2[:8], SECURITY.replace(HEAD40, S2), 0),
                ("review at the first candidate", HEAD40[:8], SECURITY, 0),
                ("pr head equals no candidate", "3" * 8, SECURITY, 1)):
            with self.subTest(label):
                code, out = self.run_gate(records=both, head=head, review=review)
                self.assertEqual(code, expected, out)
        code, out = self.run_gate(records=both, head=S2[:8])
        self.assertIn("no 'Security review (validation):' line has the form", out)

    def test_a_task_whose_profile_cannot_be_read_holds_the_ask(self):
        for label, task in (("no frontmatter", "# task\n"), ("a commented profile", "---\nprofile: prod # x\n---\n")):
            with self.subTest(label), tempfile.TemporaryDirectory() as d:
                Path(d, "task", "dispatch").mkdir(parents=True)
                Path(d, "task", "dispatch", "validation-1.md").write_text(record(HEAD40))
                Path(d, "task.md").write_text(task)
                Path(d, "gate.txt").write_text("Merge ask.")
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = gate.main(["check", str(Path(d, "task.md")), "--pr", "o/r#9", "--text-file", str(Path(d, "gate.txt")), "--head", HEAD40[:8]])
                self.assertEqual(code, 1, out.getvalue())
                self.assertIn("cannot read a 'profile:'", out.getvalue())

    def test_mutations_of_the_security_wiring_each_change_their_own_case(self):
        source = Path(gate.__file__).read_text()
        cases = {
            "pass": dict(),
            "no review": dict(review=""),
            "no candidate": dict(records={"validation-1.md": record()}),
            "review at the other candidate": dict(records={"validation-1.md": record(HEAD40, S2)}, head=S2[:8]),
        }
        mutations = {
            "dropping the call": ("security_errors, security_note = security_check(task, at_head)", "pass", ["pass", "no review", "review at the other candidate"]),
            "dropping the candidate guard": ("    if at_head:\n        try:\n            from validation_security", "    if True:\n        try:\n            from validation_security", ["no candidate"]),
            "dropping the head binding": ("at_head = [c for c in candidates if head and c.startswith(head)]", "at_head = list(candidates)", ["review at the other candidate"]),
            "dropping the note": ("    if security_note:\n        print(security_note)\n", "", ["pass"]),
        }
        before = {label: self.run_gate(**kwargs) for label, kwargs in cases.items()}
        for name, (old, new, own) in mutations.items():
            with self.subTest(name):
                self.assertEqual(source.count(old), 1, old)
                variant = types.ModuleType("delivery_gate_variant")
                variant.__file__ = gate.__file__
                exec(compile(source.replace(old, new), gate.__file__, "exec"), variant.__dict__)
                with mock.patch.dict(globals(), gate=variant):
                    changed = [label for label, kwargs in cases.items() if self.run_gate(**kwargs) != before[label]]
                self.assertEqual(changed, own)


if __name__ == "__main__":
    unittest.main()
