#!/usr/bin/env python3
"""Check the approved before/wait/after split across two valid validation cycles."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(sys.argv[1]) / "kc-dev-flow-2/scripts"))
from test_task_timeline import TimelineTests
import task_timeline

fixture = TimelineTests()
fixture.setUp()
try:
    (fixture.state / "_archive").mkdir()
    fixture.dispatch("validation", 1, 10, entering=True)
    fixture.room("validation", 1, 20)
    fixture.gates("validation", [(1, "revise", 30)])
    fixture.commit("gate: record demo validation revise", 30)
    fixture.dispatch("implementation", 1, 60, entering=True)
    fixture.dispatch("validation", 2, 80)
    fixture.room("validation", 2, 90)
    fixture.gates("validation", [(1, "revise", 30), (2, "approve", 100)])
    fixture.commit("gate: record demo validation approve", 100)
    fixture.finish(110)
    actual = next(r for r in task_timeline.timeline(fixture.state, "demo")["stages"] if r["stage"] == "validation")
    expected = {"elapsed_min": 80.0, "before_gate_min": 20.0, "captain_wait_min": 20.0, "after_gate_min": 40.0}
    observed = {k: actual[k] for k in expected}
    print(json.dumps({"intervals": ["10..20 before, 20..30 Captain wait, 30..60 after", "80..90 before, 90..100 Captain wait, 100..110 after"], "expected": expected, "observed": observed, "fixture": str(fixture.state)}, indent=2))
    assert observed == expected, "Earlier post-gate time must remain post-gate across a repair cycle"
finally:
    fixture.doCleanups()
