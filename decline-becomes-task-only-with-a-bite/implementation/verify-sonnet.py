import json
import re
from pathlib import Path
root = Path(__file__).resolve().parent
runs = json.loads((root / "sonnet-runs.json").read_text())
rows = []
for run in runs:
    d = json.loads((root / run["activity_file"]).read_text())["structuredContent"]
    text = d["content"]
    verdicts = dict(re.findall(r"^([A-D]) \| (violation|ok) \|", text, re.M))
    row = dict(name=run["name"], agent=run["agentId"], requested_model=run["model"],
               prompt=run["prompt_file"], activity=run["activity_file"], archived=run["archived"])
    if run["name"].startswith(("candidate-", "missing-bite-")) or run["name"] == "base":
        assert d["updateCount"] == 2, (run["name"], "tools or extra messages in a no-tools run")
        assert set(verdicts) == set("ABCD")
        row["verdicts"] = verdicts
        if run["name"].startswith("candidate-"):
            assert verdicts == dict(A="ok", B="ok", C="ok", D="violation")
        if run["name"] == "base":
            assert all(verdicts[x] == "violation" for x in "ABC")
        if run["name"].startswith("missing-bite-"):
            assert verdicts["D"] == "violation"
            row["status"] = "failed: falsifier confounded"
    row["step5_taskless_decline_violation"] = bool(re.search(
        r"^violation \| rule: .*files it as a new backlog task", text, re.M))
    if run["name"] == "observer-bounded-base":
        assert row["step5_taskless_decline_violation"]
        assert "4455001433" in text
    if run["name"] in ("observer-candidate", "observer-bounded-candidate"):
        assert not row["step5_taskless_decline_violation"]
    if run["name"] == "observer-base":
        assert "step-5 decline check was not run" in text
        row["status"] = "untested: observer omitted the target check"
    rows.append(row)
(root / "sonnet-results.json").write_text(json.dumps(rows, indent=2) + "\n")
summary = [
    dict(name="AC-1 wording and word budget", status="passed"),
    dict(name="AC-2 wording pins and native dispatch", status="passed"),
    dict(name="AC-3 archived gate declines and bracket falsifier", status="passed"),
    dict(name="AC-4 candidate twice and base once", status="passed"),
    dict(name="AC-4 falsifier confounded", status="failed",
         message="Both independent clause-deletion runs still classify D as a Material/P1 violation; FO message-4 routes this to the Captain."),
    dict(name="AC-5 bounded candidate/base observer replay", status="passed",
         message="Initial full-window base observer omitted the target check; both initial reports retained, then repeated with explicit FROM."),
    dict(name="AC-6 ADR ruling and supersession", status="passed"),
]
(root / "acceptance-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print("Primary Sonnet readings and bounded observer contrast verified; AC-4 falsifier remains failed.")
