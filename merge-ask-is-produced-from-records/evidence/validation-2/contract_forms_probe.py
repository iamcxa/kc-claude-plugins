from pathlib import Path
import contextlib, io, json, os, re, sys, unittest
from unittest import mock

WT = Path(os.environ["PRODUCT_WORKTREE"])
OUT = Path(__file__).parent
sys.path.insert(0, str(WT / "kc-dev-flow-2/scripts"))
import test_delivery_gate as tests

original_read = Path.read_text
contract = tests.CONTRACT.read_text()
test_name = "test_contract_examples_supply_the_forms_required_by_the_shared_guards"
rows = []
for name, pattern in [
    ("positive second reviewer", r"(?m)^Second reviewer:.*\n"),
    ("legacy round count", r"(?m)^External rounds:.*\n"),
    ("legacy reviewer outcome", r"(?m)^Copilot review:.*\n"),
    ("legacy Captain steps", r"(?m)^Captain steps:.*\n"),
]:
    damaged, count = re.subn(pattern, "", contract)
    assert count == 1, (name, count)
    def read(path, *args, **kwargs):
        return damaged if path == tests.CONTRACT else original_read(path, *args, **kwargs)
    log = io.StringIO()
    with mock.patch.object(Path, "read_text", read):
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(tests.ObservedFactsTests(test_name))
    output = name.replace(" ", "-") + "-mutation.log"
    (OUT / output).write_text(log.getvalue())
    assert len(result.failures) == 1 and not result.errors, log.getvalue()
    rows.append(dict(name=name, detected=True, failures=len(result.failures), errors=len(result.errors),
                     output=output, mutation_scope="Only the contract read is changed in memory; the product files and guards are unchanged."))
(OUT / "contract-form-mutations.json").write_text(json.dumps(rows, indent=2) + "\n")

declaration = re.search(r"(?m)^Second reviewer:[^\n]+", contract)[0] + "\n"
rows = []
for name, value in [("omitted", ""), ("contract example", declaration)]:
    pair = tests.RecordRouteParityTests().paired(declaration=value)
    observed = {route: {k: pair[route][k] for k in ("check", "question")} for route in pair}
    expected = 1 if name == "omitted" else 0
    assert all(code == expected for result in observed.values() for code in result.values()), observed
    rows.append(dict(case=name, declaration=value, routes=observed))
(OUT / "missing-declaration-fixed.json").write_text(json.dumps(rows, indent=2) + "\n")
print("four required-form deletions caught by the single new test; both routes hold without the declaration and pass with the contract example")
