import json
from pathlib import Path
import shutil
import sys
import unittest

root, out = map(Path, sys.argv[1:])
for path in (root / "kc-dev-flow-2").rglob("__pycache__"):
    shutil.rmtree(path)
sys.path.insert(0, str(root / "kc-dev-flow-2/scripts"))
import test_delivery_gate as tests

observations = []
def capture(cls, name):
    original = getattr(cls, name)
    def wrapped(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        module = kwargs.get("module", args[2] if name == "run_steps" and len(args) > 2 else None)
        observations.append(dict(test=self.id(), variant=bool(module), exit=result[0], output=result[1]))
        return result
    setattr(cls, name, wrapped)

capture(tests.CaptainStepFixture, "run_steps")
capture(tests.QuestionTests, "ask")
names = [
    "CaptainStepsTests.test_site_and_elided_paths_are_not_files_without_a_real_top_level_directory",
    "CaptainStepsTests.test_braced_namespace_uri_is_not_a_link_but_plain_urls_still_hold",
    "CaptainStepsTests.test_named_cards_require_shell_and_untagged_fences_but_skip_data",
    "CaptainStepsTests.test_yaml_message_and_missing_paths_keep_their_holds",
    "QuestionTests.test_question_accepts_named_yaml_cards_and_holds_real_steps_and_paths",
]
suite = unittest.defaultTestLoader.loadTestsFromNames(names, tests)
result = unittest.TextTestRunner(verbosity=2).run(suite)
(out / "mutation-observations.json").write_text(json.dumps(observations, indent=2) + "\n")
raise SystemExit(not result.wasSuccessful())
