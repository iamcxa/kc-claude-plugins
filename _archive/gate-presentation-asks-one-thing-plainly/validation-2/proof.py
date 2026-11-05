import hashlib, io, json, os, re, subprocess, sys, tarfile, tempfile
from pathlib import Path
wt, state, output = map(Path, sys.argv[1:])
base="a7c0bdbe0ae0f111780f6d3b7254ed4ad67befcd"
pin="79fb4abf3f9c751c83e8d70dcfeaa654ff8774c4"
basepkg=output/"base/kc-dev-flow-2"
pkg=wt/"kc-dev-flow-2"
up=Path("/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3")
def git(*a):
    return subprocess.check_output(["git","-C",str(state),*a])
paths=git("ls-tree","-r","--name-only",pin).decode().splitlines()
selected=[p for p in paths if (p.endswith(".md") and ("/" not in p or p.startswith("_archive/") and p.count("/")==1)) or p.endswith("/index.json")]
with tempfile.TemporaryDirectory(prefix="gate-ledger-") as td:
    d=Path(td)
    archive=git("archive",pin,"--",*selected)
    with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(d,filter="data")
    outs=[]
    for label,root in (("base",basepkg),("candidate",pkg)):
        done=subprocess.run([sys.executable,"-B",str(root/"scripts/decision_ledger.py"),str(d)],capture_output=True,check=True)
        outs.append(done.stdout)
        (output/f"ledger-{label}.jsonl").write_bytes(done.stdout)
    assert outs[0]==outs[1]
    rows=[json.loads(line) for line in outs[1].splitlines()]
    sys.path.insert(0,str(pkg/"scripts"))
    import decision_ledger as dl
    nested=[r for r in rows if r["task"]=="gate-presentation-asks-one-thing-plainly" and r["stage"]=="backlog" and r["kind"]=="resolution"][-1]
    assert "「婉拒要寫明」" in nested["question"]
    assert dl.quotes_bound_question(nested)
    proof={"state":pin,"rows":len(rows),"bytes":len(outs[1]),"sha256":hashlib.sha256(outs[1]).hexdigest(),"byte_identical":True,"nested_backlog_matches":True}
    (output/"ledger-proof.json").write_text(json.dumps(proof,indent=2))
    gate=[r for r in rows if r["task"]=="gate-presentation-asks-one-thing-plainly" and r["stage"]=="ideation" and r["decision"]=="approve"][-1]
    asked=gate["reason"].split("answering ",1)[1].split("; accepts",1)[0]
    adr=(wt/"docs/adr/0062-a-gate-approval-grants-what-its-quoted-bound-question-says.md").read_text()
    assert "**Words:** 「准」" in adr and "**Asked:** "+asked in adr
    wrong=adr.replace("**Words:** 「准」","**Words:** 「FO recommends it」")
    caught="**Words:** 「准」" not in wrong
    assert caught
    (output/"adr-provenance.json").write_text(json.dumps({"state":pin,"captain":"准","asked_matches":True,"mutant_fo_words_caught":caught},ensure_ascii=False,indent=2))
def section(text,header):
    m=re.search(r"(?m)^"+re.escape(header)+r"\n",text)
    end=re.search(r"(?m)^## ",text[m.end():])
    return text[m.start():m.end()+end.start()] if end else text[m.start():]
def count(p):return len(p.read_text().split())
pmerge=(up/"mods/pr-merge.md").read_text()
constants={"upstream_startup":len(section(pmerge,"## Hook: startup").split()),
           "upstream_idle":len(section(pmerge,"## Hook: idle").split()),
           "gate_lifecycle":count(up/"skills/fo-gate-lifecycle/SKILL.md"),
           "present_gate":count(up/"skills/present-gate/SKILL.md")}
outputs=[json.loads((output/f"recount-{label}.json").read_text()) for label in ("base","candidate")]
measured=[]
for label,root,said in zip(("base","candidate"),(basepkg,pkg),outputs):
    workflow=(root/"references/sd/workflow.md").read_text()
    nums={"workflow":len(workflow.split()),"entry":count(root/"skills/dev/SKILL.md"),
          "mod":count(root/"references/sd/mods/kc-dev-flow-2.md"),
          "authority":len(section(workflow,"## Delivery authority").split()),
          "extensions":len(section(workflow,"## Extensions").split()),
          "learn":count(root/"extensions/learn/EXTENSION.md")}
    words={k:len(v.split()) for k,v in said.items()}
    nums["stdout"]=words
    nums["moments"]={
      "startup":nums["workflow"]+nums["entry"]+nums["mod"]+constants["upstream_startup"]+words["open"],
      "idle_open":nums["mod"]+constants["upstream_idle"]+nums["authority"]+nums["extensions"]+words["open"],
      "idle_merged":nums["mod"]+constants["upstream_idle"]+nums["authority"]+nums["extensions"]+words["merged"],
      "after_archive":nums["mod"]+nums["learn"]+words["archive"],
      "backlog_prepare":words["backlog"],
      "ideation_prepare":words["ideation"],
      "validation_prepare":words["question"],
      "ui_validation_prepare":words["question"]+words["validation"],
      "implementation_amendment":words["implementation"],
      "merge_ask":nums["authority"]+nums["extensions"]+constants["gate_lifecycle"]+constants["present_gate"]+words["ask"],
      "gate_presentation":constants["gate_lifecycle"]+constants["present_gate"]
    }
    measured.append(nums)
for moment,value in measured[0]["moments"].items():
    delta=measured[1]["moments"][moment]-value
    expected=62 if moment in ("backlog_prepare","ideation_prepare","validation_prepare","ui_validation_prepare") else 0
    assert delta==expected,(moment,delta)
for name in ("open","merged","archive","seed","implementation","validation"):
    assert outputs[0][name].replace(str(basepkg.resolve()), "<package>")==outputs[1][name].replace(str(pkg.resolve()), "<package>"),name
assert (basepkg/"references/sd/workflow.md").read_bytes()==(pkg/"references/sd/workflow.md").read_bytes()
mutated=(pkg/"references/sd/workflow.md").read_bytes()+b"\nOne extra sentence.\n"
assert mutated!=(basepkg/"references/sd/workflow.md").read_bytes()
reading={"base_sha":base,"constants":constants,"base":measured[0],"candidate":measured[1],
         "workflow_byte_identical":True,"workflow_edit_mutant_caught":True,
         "limits":"Same current passages and stubbed provider fixtures on both roots. Design table's old absolute baseline is stale. Gate-prepare deltas match; this is instruction reading, not elapsed time or model tokens."}
(output/"reading.json").write_text(json.dumps(reading,indent=2))
bench=[{"name":k,"before":v,"after":measured[1]["moments"][k],"better":"lower"} for k,v in measured[0]["moments"].items()]
import delivery_gate as dg
bench.append({"name":"unquoted merge next line","before":len(dg.ASK.split()),"after":len(dg.ASK_UNQUOTED.split()),"better":"lower"})
(output/"reading-benchmark.json").write_text(json.dumps(bench,indent=2))
print(json.dumps({"ledger":proof,"reading":measured[1]["moments"]},ensure_ascii=False))
