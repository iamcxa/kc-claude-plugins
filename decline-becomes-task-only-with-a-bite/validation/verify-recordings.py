#!/usr/bin/env python3
"""Check retained independent model evidence; this does not launch a new model."""
import json, re, sys
from pathlib import Path
out=Path(__file__).resolve().parent
c=json.loads((out/"context.json").read_text())
state=Path(c["state"]); task=state/"decline-becomes-task-only-with-a-bite.md"
body=task.read_text(); criteria=body.split("## Acceptance criteria\n",1)[1].split("## Decisions for the Captain",1)[0]
amendment=body.split("### Amendment 1",1)[1].split("## Stage Report",1)[0]
old=out.parent/"implementation/amendment-1"
moves=json.loads((old/"criteria-move.json").read_text())
assert "**AC-4**" not in criteria and "**AC-7**" in criteria
assert "Superseded text:\n"+moves["original_block"] in amendment
assert moves["replacement_block"] in criteria
record=(old/"record-e.md").read_text()
for name,previous in [("candidate","candidate-1.prompt.md"),("base","base.prompt.md"),("mutation","missing-bite-1.prompt.md")]:
    expected=(old.parent/previous).read_text()
    for before,after in [("four records below","five records below"),("four requested lines","five requested lines"),("four decline records from four tasks","five decline records from five tasks"),("For each record A to D","For each record A to E")]:
        expected=expected.replace(before,after)
    assert (out/(name+".prompt.md")).read_text()==expected.rstrip()+"\n"+record
runs=json.loads((out/"sonnet-runs.json").read_text())
assert len(runs)==5 and len({r["agentId"] for r in runs})==5
results=[]
for run in runs:
    assert run["provider"]=="claude/sonnet" and run["model"]=="sonnet" and run["archivedAt"]
    d=json.loads((out/run["activity"]).read_text())
    assert d["updateCount"]==2
    lines=re.findall(r"^([A-E]) \| (violation|ok) \| (.+)$",d["content"],re.M)
    assert len(lines)==5
    verdict={letter:v for letter,v,quote in lines}; quotes={letter:q for letter,v,q in lines}
    if run["name"].startswith("candidate"):
        assert verdict==dict(A="ok",B="ok",C="ok",D="violation",E="violation")
        assert "observed failure naming who it hurts" in quotes["D"]
        assert "a repeat in a later round or task" in quotes["E"]
    elif run["name"].startswith("mutation"):
        assert verdict["E"]=="ok"
    else:
        assert all(verdict[x]=="violation" for x in "ABC")
    results.append(dict(name=run["name"],status="passed",verdicts=verdict,readings=quotes))
(out/"model-results.json").write_text(json.dumps(results,indent=2)+"\n")
print("PASS: AC-7 primary readings; E requires task in 2/2 candidate and 0/2 mutation readings; A-D retained.")
print("LIMIT: mutation-1 reads C violation; mutation-2 reads C ok. The accepted falsifier is E; this variability is retained.")
if "--without-observer" not in sys.argv:
    for name in ["candidate","base"]:
        text=(out/("observer-"+name+".report.md")).read_text()
        lines=[x for x in text.splitlines() if x.startswith(("violation |","ok |","can't tell |","observed |")) and ("4455001433" in x or ("step 5" in x.lower() and "declin" in x.lower()))]
        assert lines, (name,"observer omitted the target decline")
        if name=="candidate":
            assert any(x.startswith("ok |") for x in lines) and not any(x.startswith("violation |") for x in lines),lines
        else:
            assert any(x.startswith("violation |") for x in lines),lines
    print("PASS: AC-5 observer candidate clears the target decline; base reports its step-5 violation.")
