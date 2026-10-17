import tempfile
import types
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("validation_security.py")
HEAD = "1c5b1870" + "a" * 32
OTHER = "b" * 40

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
FENCED = "```yaml\n" + REPORT + "```"
ZERO = "tob_security_review:\n  pr: 555\n  findings: []\n"
REFUSAL = "I can't help with this request."
REVIEW = f"Security review (validation): security/validation-1.yaml at {HEAD}\n"
LINES = (
    "Security finding (validation 1) 1: Needs decision: cap sessions per room now, or file a task\n"
    "Security finding (validation 1) 2: Needs decision: add the untrusted-document sentence\n"
    "Security finding (validation 1) 3: declined: declared identity is stated unverified\n"
)


def load(old=None, new=None):
    source = SCRIPT.read_text()
    if old is not None:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    module = types.ModuleType("validation_security_variant")
    module.__file__ = str(SCRIPT)
    exec(compile(source, str(SCRIPT), "exec"), module.__dict__)
    return module


def run(module, profile="prod", review=REVIEW, lines=LINES, report=REPORT, candidates=(HEAD,), folder_form=False, outside=False):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        if outside:
            (root / "validation-1.yaml").write_text(report)
        folder = root / "task"
        (folder / "security").mkdir(parents=True)
        if report is not None:
            (folder / "security" / "validation-1.yaml").write_text(report)
        task = folder / "index.md" if folder_form else root / "task.md"
        task.write_text(f"---\ntitle: x\nprofile: {profile}\nstatus: validation\n---\n\n## Stage Report: validation\n\n{review}{lines}")
        try:
            return module.check_task(task, list(candidates))
        except Exception as error:
            return "raised", type(error).__name__


CASES = {
    "pass, every finding disposed": {},
    "pass on a report with markdown fences": dict(report=FENCED),
    "pass on a zero-finding report": dict(report=ZERO, lines=""),
    "pass for a folder task": dict(folder_form=True),
    "pilot task skipped": dict(profile="pilot", review="", lines="", report=None),
    "no review line": dict(review=""),
    "not run": dict(review="Security review (validation): not run: reviewer returned no report (sonnet)\n", report=None),
    "review at another head": dict(review=REVIEW.replace(HEAD, OTHER)),
    "short head": dict(review=REVIEW.replace(HEAD, HEAD[:8])),
    "path leaves the task folder": dict(review=REVIEW.replace("security/validation-1.yaml", "../validation-1.yaml"), outside=True),
    "report is not a file": dict(report=None),
    "refusal text saved as the report": dict(report=REFUSAL),
    "report severity not on the scale": dict(report=REPORT.replace("severity: LOW", "severity: SEVERE")),
    "finding with no line": dict(lines=LINES.rsplit("\n", 2)[0] + "\n"),
    "declined HIGH": dict(lines=LINES.replace("1: Needs decision: cap sessions per room now, or file a task", "1: declined: accepted")),
    "open Material": dict(lines=LINES.replace("1: Needs decision: cap sessions per room now, or file a task", "1: Material: cap sessions per room")),
    "extra finding line": dict(lines=LINES + "Security finding (validation 1) 4: declined: x\n"),
}

REASONS = {
    "no review line": "needs a 'Security review (validation):' line",
    "not run": "validation security review not run",
    "review at another head": "no 'Security review (validation):' line has the form",
    "short head": "no 'Security review (validation):' line has the form",
    "path leaves the task folder": "no 'Security review (validation):' line has the form",
    "report is not a file": "is not a file in the task folder",
    "refusal text saved as the report": "is not a tob_security_review report",
    "report severity not on the scale": "not one of",
    "finding with no line": "finding 3 of security/validation-1.yaml has no",
    "declined HIGH": "finding 1 of security/validation-1.yaml has no",
    "open Material": "is Material and open at this head",
    "extra finding line": "'Security finding (validation 1) 4:' has no finding",
}

# each rule's source text, the replacement that removes it, and the one case that must change
MUTATIONS = {
    "the prod-only rule": ('if not profile or profile.group(1) != "prod":', "if False:", "pilot task skipped"),
    "the missing-review rule": ("if not reviews:", "if False:", "no review line"),
    "the not-run rule": ('if last.lower().startswith("not run"):', "if False:", "not run"),
    "the head-binding rule": ("m.group(3) in candidates", "m", ["review at another head", "short head"]),
    "the report-path rule": (r"^(security/validation-(\d+)\.yaml) at", r"^(.*?validation-(\d+)\.yaml) at", "path leaves the task folder"),
    "the missing-report rule": ("if not report.is_file():", "if False:", "report is not a file"),
    "the report-shape rule": ("problems = [f\"{name}: '{path}' {p}\" for p in report_shape(body)]", "problems = []", "refusal text saved as the report"),
    "the severity-scale rule": ("if bad:", "if False:", "report severity not on the scale"),
    "the open-Material rule": (r'if re.match(r"Material:\s*\S", entry):', "if False:", "open Material"),
    "the declined-HIGH rule": (' and severity in ("MEDIUM", "LOW")', "", "declined HIGH"),
    "the undisposed-finding rule": ("        else:\n            errors.append(f\"{name}: finding {n} of {path} has no", "        elif False:\n            errors.append(f\"{name}: finding {n} of {path} has no", ["finding with no line", "declined HIGH"]),
    "the extra-line rule": ("for n in sorted(set(lines) - set(range(1, len(severities) + 1))):", "for n in []:", "extra finding line"),
    "the folder-task rule": ('task.parent if task.name == "index.md" else task.parent / task.stem', "task.parent / task.stem", "pass for a folder task"),
}


class ValidationSecurityTests(unittest.TestCase):
    base = load()

    def test_the_passing_shapes_print_one_short_line(self):
        for label, expect in (("pass, every finding disposed", "3 findings, 1 declined, 2 decisions"),
                              ("pass on a report with markdown fences", "3 findings, 1 declined, 2 decisions"),
                              ("pass on a zero-finding report", "0 findings, 0 declined, 0 decisions")):
            with self.subTest(label):
                errors, note = run(self.base, **CASES[label])
                self.assertEqual(errors, [])
                self.assertEqual(note, f"validation security review security/validation-1.yaml: {expect}")
        self.assertEqual(run(self.base, **CASES["pass for a folder task"])[0], [])

    def test_a_pilot_task_returns_nothing_to_say(self):
        self.assertEqual(run(self.base, **CASES["pilot task skipped"]), ([], None))

    def test_each_hole_is_refused_with_its_own_reason(self):
        for label, reason in REASONS.items():
            with self.subTest(label):
                errors, _ = run(self.base, **CASES[label])
                self.assertEqual(len([e for e in errors if reason in e]), 1, errors)

    def test_removing_each_rule_changes_exactly_its_own_case(self):
        before = {label: run(self.base, **kwargs) for label, kwargs in CASES.items()}
        for rule, (old, new, own) in MUTATIONS.items():
            variant = load(old, new)
            with self.subTest(rule):
                changed = [label for label, kwargs in CASES.items() if run(variant, **kwargs) != before[label]]
                self.assertEqual(changed, own if isinstance(own, list) else [own])

    def test_the_command_runs_from_another_directory_and_under_isolated_mode(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "task" / "security").mkdir(parents=True)
            (root / "task" / "dispatch").mkdir()
            (root / "task" / "dispatch" / "validation-1.md").write_text(f"# v\n\nCandidate: {HEAD}\n\n## Checklist\n")
            (root / "task" / "security" / "validation-1.yaml").write_text(REPORT)
            (root / "task.md").write_text(f"---\nprofile: prod\n---\n\n{REVIEW}{LINES}")
            for flags in ([], ["-I"]):
                done = subprocess.run([sys.executable, "-B", *flags, str(SCRIPT), "check", str(root / "task.md")],
                                      capture_output=True, text=True, cwd=d)
                self.assertEqual((done.returncode, done.stderr), (0, ""), done.stdout)
                self.assertIn("3 findings", done.stdout)


if __name__ == "__main__":
    unittest.main()
