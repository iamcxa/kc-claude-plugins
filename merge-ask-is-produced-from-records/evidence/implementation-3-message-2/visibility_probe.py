from pathlib import Path
import io, json, os, sys, unittest
from unittest import mock

WT = Path(os.environ["PRODUCT_WORKTREE"])
OUT = Path(__file__).parent
sys.path.insert(0, str(WT / "kc-dev-flow-2/scripts"))
import test_delivery_gate as tests

name = "test_nonpublic_or_unknown_visibility_saves_no_record"
positive = "test_question_only_records_observed_facts_and_no_manual_summary"
log = io.StringIO()
result = unittest.TextTestRunner(stream=log, verbosity=2).run(
    unittest.TestSuite([tests.ObservedFactsTests(name), tests.ObservedFactsTests(positive)]))
(OUT / "visibility-controls.log").write_text(log.getvalue())
assert result.wasSuccessful(), log.getvalue()

mutant = tests.variant_of(
    'json.loads(gh("repo", "view", repo, "--json", "visibility"))["visibility"] != "PUBLIC"',
    'json.loads(gh("repo", "view", repo, "--json", "isPrivate"))["isPrivate"] is not False')
log = io.StringIO()
with mock.patch.object(tests, "gate", mutant):
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(tests.ObservedFactsTests(name))
(OUT / "visibility-reverse-mutation.log").write_text(log.getvalue())
assert len(result.failures) == 1 and not result.errors, log.getvalue()
(OUT / "visibility-proof.json").write_text(json.dumps(dict(
    controls="Existing PRIVATE, missing and one added INTERNAL/isPrivate=false case all exit 2 and save no record; existing PUBLIC record test saves and binds observations.",
    added_cases=1, added_test_methods=0, reverse_mutation="Restore isPrivate false as the public criterion in an isolated in-memory module.",
    reverse_mutation_failures=len(result.failures), reverse_mutation_errors=len(result.errors),
    public_control=positive, negative_control=name,
    limits="Repository API responses use the existing gh test double; no live provider or publication action was performed."
), indent=2) + "\n")
print("PUBLIC control passes; PRIVATE/missing/INTERNAL save nothing; old boolean criterion fails the adjusted existing test")
