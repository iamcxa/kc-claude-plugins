import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import types
import unittest
from unittest import mock

root = Path(sys.argv[1]).resolve()
out = Path(__file__).resolve().parent
scripts = root / "kc-dev-flow-2/scripts"
shutil.rmtree(scripts / "__pycache__", ignore_errors=True)
sys.path.insert(0, str(scripts))
spec = importlib.util.spec_from_file_location("test_delivery_gate", scripts / "test_delivery_gate.py")
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
filtering = '    text = "\\n".join("" if normalized(line) in ATTRIBUTION else line for line in text.splitlines())\n'
variants = {
    "no-line-exemption": tests.variant_of(filtering, ""),
    "url-wide-exemption": tests.variant_of(filtering, '    text = text.replace("https://claude.com/claude-code", "")\n'),
    "substring-exemption": tests.variant_of(filtering, '    text = "\\n".join("" if any(value in normalized(line) for value in ATTRIBUTION) else line for line in text.splitlines())\n'),
}
targets = {
    "no-line-exemption": ["test_pr_body_attribution_line_needs_no_recorded_link_step", "test_pr_body_other_url_still_needs_a_recorded_link_step"],
    "url-wide-exemption": ["test_attribution_url_elsewhere_needs_a_recorded_link_step"],
    "substring-exemption": ["test_attribution_line_with_more_text_keeps_its_links"],
}
results = []
for name, module in variants.items():
    suite = unittest.TestSuite(tests.CaptainStepsTests(method) for method in targets[name])
    stream = io.StringIO()
    with mock.patch.object(tests, "gate", module):
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    (out / (name + ".log")).write_text(stream.getvalue())
    assert not result.wasSuccessful() and not result.errors, stream.getvalue()
    results.append({"name": "Mutation caught: " + name, "status": "passed", "message": stream.getvalue()})
(out / "mutations.json").write_text(json.dumps(results, indent=2))

attribution = "🤖 Generated with [Claude Code](https://claude.com/claude-code)"
fixture = tests.TaskFolderCaptainTests()
fixture.setUp()
try:
    card = fixture.folder / "review/pr-body.md"
    card.parent.mkdir()
    def question(module, content):
        card.write_text(content + "\n")
        fixture.run_question(message="Review this candidate. Read review/pr-body.md")
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            code = module.main(["question", str(fixture.task), "--text-file", str(fixture.message), "--workflow-dir", str(fixture.state)])
        return code, capture.getvalue()
    base = variants["no-line-exemption"]
    word_rows = []
    for name, content in (("pr-body", attribution), ("pr-body-spaces", " \t" + attribution + "  "), ("captain-link", "Open https://preview.example.test/owner")):
        before = question(base, content)
        after = question(tests.gate, content)
        for label, value in (("base", before), ("candidate", after)):
            (out / (name + "-question-" + label + ".log")).write_text(value[1])
        if name.startswith("pr-body"):
            assert before[0] == 1 and after[0] == 0, (before, after)
            assert "S5" in before[1] and "S5" not in after[1]
            assert "gate text complete" in after[1] and tests.gate.ASK_FORM in after[1]
        else:
            assert before == after and before[0] == 1, (before, after)
        word_rows.append({"moment": name + " question", "before": len(before[1].split()), "after": len(after[1].split()), "before_exit": before[0], "after_exit": after[0]})
finally:
    fixture.doCleanups()

base_root = Path(sys.argv[2]).resolve()
base_source = (base_root / "kc-dev-flow-2/scripts/delivery_gate.py").read_text()
base_module = types.ModuleType("delivery_gate_base")
base_module.__file__ = tests.gate.__file__
exec(compile(base_source, tests.gate.__file__, "exec"), base_module.__dict__)
help_words = []
for label, module in (("base", base_module), ("candidate", tests.gate)):
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        try:
            module.main(["--help"])
        except SystemExit as error:
            assert error.code == 0
    (out / ("help-" + label + ".log")).write_text(capture.getvalue())
    help_words.append(len(capture.getvalue().split()))
word_rows.append({"moment": "--help", "before": help_words[0], "after": help_words[1]})
for path in ("kc-dev-flow-2/README.md", "kc-dev-flow-2/references/sd/workflow.md"):
    before = (base_root / path).read_bytes()
    assert before == (root / path).read_bytes(), path
    word_rows.append({"moment": "startup " + path, "before": len(before.split()), "after": len(before.split())})
check_before = base_source[base_source.index("def check("):base_source.index("def summary_round_problems(")]
check_source = tests.SOURCE[tests.SOURCE.index("def check("):tests.SOURCE.index("def summary_round_problems(")]
assert check_before == check_source
for label, module in (("base", base), ("candidate", tests.gate)):
    with mock.patch.object(tests, "gate", module):
        checked = tests.run_check()
    code, output = checked.code, checked.out
    assert code == 0, output
    # The fixture's temporary checkout changes its path on every run.
    normalized = [line for line in output.splitlines() if not line.startswith("record:")]
    if label == "base":
        base_check = normalized
    else:
        assert normalized == base_check, (base_check, normalized)
    (out / ("merge-check-" + label + ".log")).write_text(output)
(out / "words.json").write_text(json.dumps(word_rows, indent=2))
print("Three mutations caught; question routes, startup bytes and merge-check output verified.")
