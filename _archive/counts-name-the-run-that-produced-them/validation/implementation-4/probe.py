"""Exercise amendment 2 through fresh learning claims and gate callers."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(sys.argv[1])
fixture_path = Path(sys.argv[2])
baseline = "--baseline" in sys.argv[3:]
sys.path.insert(0, str(root / "kc-dev-flow-2/scripts"))
import test_learning as learning_test
import test_delivery_gate as gate_test
from count_tokens import count_sentences, numbers
import delivery_gate

record_bytes = fixture_path.read_bytes()
decision = next(d for d in json.loads(record_bytes)["evaluation"]["decisions"] if d["action"] == "add")
observed = []
fixture = learning_test.LearningTests()
fixture.setUp()
try:
    fixture.pack["evidence"] = decision["evidence"]
    fixture.write_pack()
    claim = fixture.claim()
    result = fixture.complete(claim, fixture.result_file([decision]), code=1 if baseline else 0)
    saved = fixture.cli("read", "--job", claim["job"])
    assert saved["state"] == ("pending" if baseline else "completed"), saved
    if baseline:
        assert "in no referenced evidence item" in result["error"], result
        assert any("Cycle 1 FO line" in sentence and "1" in values
                   for sentence, values in count_sentences(decision["entry"]["Evidence"]))
    else:
        assert saved["evaluation"]["decisions"] == [decision], saved
    observed.append(dict(name="ed2d3ee1 historical entry unchanged", status="passed",
                         completion_exit=1 if baseline else 0, state=saved["state"],
                         evidence_sha256=hashlib.sha256(decision["entry"]["Evidence"].encode()).hexdigest()))
finally:
    fixture.doCleanups()

fixture = learning_test.LearningTests()
fixture.setUp()
try:
    fixture.pack["evidence"] = ["3 cells"]
    fixture.write_pack()
    claim = fixture.claim()
    item = dict(learning_test.NEW, Evidence="2 cells")
    plain = dict(fixture.decision("add", item), evidence=["3 cells"])
    refused = fixture.complete(claim, fixture.result_file([plain]), code=1)
    assert "2 cells" in refused["error"], refused
    assert fixture.cli("read", "--job", claim["job"])["state"] == "pending"
    item["Evidence"] = "3 cells"
    done = fixture.complete(claim, fixture.result_file([plain]))
    assert done["state"] == "completed", done
    observed.append(dict(name="unsupported 2 cells refused; same token correctable", status="passed",
                         refusal_exit=1, refusal_state="pending", correction_exit=0, correction_state="completed"))
finally:
    fixture.doCleanups()

if not baseline:
    for label in ("Cycle", "Round", "Batch", "Step", "Stage", "Amendment", "Attempt", "Phase"):
        for spelling in (label, label.lower(), label.upper()):
            assert not count_sentences(f"{spelling} 1 FO line"), spelling
            assert count_sentences(f"{spelling} 1 FO line, 2 cells") == [(f"{spelling} 1 FO line, 2 cells", {"2"})]
            assert count_sentences(f"{spelling} 2 3 tests") == [(f"{spelling} 2 3 tests", {"3"})]
            fixture = learning_test.LearningTests()
            fixture.setUp()
            try:
                fixture.pack["evidence"] = ["P1 S1 source identifiers"]
                fixture.write_pack()
                claim = fixture.claim()
                item = dict(learning_test.NEW, Evidence=f"{spelling} 1 FO line")
                ordinal = dict(fixture.decision("add", item), evidence=fixture.pack["evidence"])
                assert fixture.complete(claim, fixture.result_file([ordinal]))["state"] == "completed"
            finally:
                fixture.doCleanups()
        observed.append(dict(name=label + " identifiers and adjacent real count", status="passed"))
    assert count_sentences("motorcycle 1 FO line") == [("motorcycle 1 FO line", {"1"})]
    assert count_sentences("3 of 6; 1,000 tests") == [("3 of 6;", {"3", "6"}), ("1,000 tests", {"1000"})]
    assert not count_sentences("cycle 2, round 2")
    assert not numbers("P1 S1")
    with tempfile.TemporaryDirectory(dir=root / ".context") as temporary:
        folder = Path(temporary)
        (folder / "cells.txt").write_text("3 cells")
        assert delivery_gate.count_problems(folder, "Cycle 1 FO line (cells.txt)") == (0, [])
        assert delivery_gate.count_problems(folder, "2 cells (cells.txt)") == (0, ["2 cells (cells.txt)"])
        assert delivery_gate.count_problems(folder, "3 cells (cells.txt)") == (1, [])
    for summary, expected in (("Cycle 1 FO line.", 0), ("Cycle 1 FO line; 2 cells (validation/cells.txt).", 1)):
        saved = {}
        code, text = gate_test.QuestionTests().ask("Admit it?", summary=summary,
                                                  cards={"validation/cells.txt": "3 cells"}, saved=saved, cli=True)
        assert code == 0, text
        assert f"Unchecked counts: {expected}\n" in saved["summary"], saved
    observed.append(dict(name="gate source check and automatic disclosure preserved", status="passed"))

print(json.dumps(dict(fixture_sha256=hashlib.sha256(record_bytes).hexdigest(),
                     mode="baseline" if baseline else "amended", tests=observed), indent=2))
