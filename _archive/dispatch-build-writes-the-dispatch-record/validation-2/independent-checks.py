import importlib.util, json, os, re, subprocess, sys
from pathlib import Path
root=Path("/tmp/pr812-validation2.gfsHcD/candidate")
out=Path("/tmp/pr812-validation2.gfsHcD/evidence")
task=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record.md")
base=subprocess.check_output(["git","-C","/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record","show","334d91e3165953b2ca7191e3308d80b6c02c4a99:kc-dev-flow-2/references/sd/workflow.md"],text=True)
head=(root/"kc-dev-flow-2/references/sd/workflow.md").read_text()
norm=lambda x:" ".join(x.split())
approved=[line[2:] for line in task.read_text().splitlines() if line.startswith("> ")]
assert len(approved)==3
assert all(norm(p) in norm(head) for p in approved)
b=norm(base)
b1=b.split("FO saves those scope notes",1)[1].split("A follow-up message",1)[0]
b1="FO saves those scope notes"+b1
b2="A follow-up message"+b.split("A follow-up message",1)[1].split("After each worker report",1)[0]
b3="Before `dispatch build`"+b.split("Before `dispatch build`",1)[1].split(" When `status --set`",1)[0]
rows=[dict(name="Startup and resume",before=len(base.split()),after=len(head.split())),
dict(name="Fresh dispatch incl successful checker output",before=len((b1+b3).split())+4,after=len((approved[0]+" "+approved[2]).split())),
dict(name="Follow-up incl successful checker output",before=len((b1+b2+b3).split())+4,after=len((approved[1]+" "+approved[2]).split())+4)]
(out/"lifecycle-words.json").write_text(json.dumps(rows,indent=2)+"\n")
affected=json.loads((out/"doc-impact.log").read_text())
dispositions=json.loads(Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/implementation/repair-1/doc-impact-verdicts.json").read_text())
assert {x["doc"] for x in affected}=={x["doc"] for x in dispositions}
for row in dispositions:
 p=root/row["doc"]
 if row["verdict"]=="unaffected":
  old=subprocess.check_output(["git","-C","/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record","show","334d91e3165953b2ca7191e3308d80b6c02c4a99:"+row["doc"]])
  assert p.read_bytes()==old,row["doc"]
 row["independent_check"]="Reviewed referenced claim and unchanged bytes" if row["verdict"]=="unaffected" else "Read ADR 0070 and matched decision to approved gate and wrapper"
(out/"doc-impact-verdicts.json").write_text(json.dumps(dispositions,indent=2)+"\n")
sys.path.insert(0,str(root/"kc-dev-flow-2/scripts"))
spec=importlib.util.spec_from_file_location("seam",root/"kc-dev-flow-2/scripts/test_dispatch_stage.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
case=m.DispatchStageTests("test_stamp_commits_complete_record_and_exact_inputs");case.setUp()
try:
 result=case.call([m.BINARY,"dispatch","build","--stamp","--workflow-dir",case.workflow,"--entity-path",case.entity,"--stage","ideation","--host","codex","--checklist-file",case.checklist,"--scope-notes-file",case.notes])
 assert not case.record().exists()
 wrapped=case.build()
 case.assert_committed(case.record(),f"dispatch: {case.slug} entering ideation")
 (out/"without-writer.json").write_text(json.dumps(dict(direct_exit=result.returncode,direct_has_record=False,wrapper_exit=wrapped.returncode,wrapper_commits_record=True),indent=2)+"\n")
finally:case.doCleanups()
print(json.dumps(dict(passages_match=True,doc_count=len(dispositions),lifecycle=rows)))

