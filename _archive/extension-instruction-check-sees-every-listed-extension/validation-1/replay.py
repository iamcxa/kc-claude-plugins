import ast, collections, importlib.util, io, json, os, pathlib, re, subprocess, sys, tarfile
ROOT=pathlib.Path(os.environ.get("PR787_CODE_ROOT","/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-extension-instruction-check-sees-every-listed-extension/.context/validation-pr787"))
OUT=pathlib.Path("/tmp/pr787-validation")
STATE=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
PKG=pathlib.Path("/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0")
TASKS=["second-round-prompts-a-step-back","claims-name-their-source","release-walk-due-trigger","fo-tries-what-it-asks-the-captain","diagnosis-rounds-count-toward-step-back","fo-answers-own-worker-permissions-by-listed-id","model-roster-question-needs-both-families","release-walk-off-production-before-release","validation-gate-requires-the-question-check","rewritten-criteria-checked-against-captain-words","worker-completion-reaches-fo-on-paseo","special-roles-follow-the-model-table"]
def snapshot(rev,name):
 target=OUT/name
 if target.exists(): return target
 target.mkdir()
 data=subprocess.check_output(["git","-C",str(STATE),"archive",rev])
 with tarfile.open(fileobj=io.BytesIO(data)) as archive: archive.extractall(target,filter="data")
 return target
def mod(path,name):
 sys.path.insert(0,str(path.parent))
 spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def counts(lines):
 c=collections.Counter()
 for line in lines:
  match=re.search(r": ([\w-]+) worker instruction",line)
  if match:c[match[1]]+=1
 return dict(c)
def batch():
 pinned=json.loads((OUT/"identity.json").read_text())
 snap=OUT/"state"
 runs=[]; totals={}
 for name,path in [("baseline",PKG/"scripts/dispatch_records.py"),("candidate",ROOT/"kc-dev-flow-2/scripts/dispatch_records.py")]:
  lines=[]
  for task in TASKS:
   args=["python3","-B",str(path),"--readme",str(OUT/"README.md"),str(snap/"_archive"/task)]
   p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"))
   hit=[l for l in p.stdout.splitlines() if " worker instruction " in l]
   lines+=hit
   runs.append(dict(version=name,task=task,command=args,exit=p.returncode,stdout=p.stdout,stderr=p.stderr))
  totals[name]={"counts":counts(lines),"records":lines}
 output={"identity":pinned,"tasks":TASKS,"totals":totals,"runs":runs}
 (OUT/("batch-replay"+("-mutation" if "--mutation" in sys.argv else "")+".json")).write_text(json.dumps(output,indent=2))
 for task in TASKS:
  pair=[r for r in runs if r["task"]==task]
  other=lambda r:[l for l in r["stdout"].splitlines() if " worker instruction " not in l and " dispatch record(s) complete" not in l]
  assert other(pair[0])==other(pair[1]),task
 assert totals["baseline"]["counts"]=={},totals["baseline"]
 assert totals["candidate"]["counts"]=={"paseo":30,"roborev":7},totals["candidate"]["counts"]
 lines=totals["candidate"]["records"]
 assert not any(l.startswith("validation-") or "-message-" in l for l in lines)
 assert sum(l.startswith("ideation-") and ": paseo " in l for l in lines)==16
 assert sum(l.startswith("implementation-") and ": paseo " in l for l in lines)==14
 print("Batch 12/13: baseline 0; candidate paseo 30 (16 ideation, 14 implementation), roborev 7; no validation/message extension diagnostics.")
def corpus():
 current=mod(ROOT/"kc-dev-flow-2/scripts/dispatch_records.py","candidate_records")
 previous=mod(PKG/"scripts/dispatch_records.py","baseline_records")
 allrows=[]
 for snap in [OUT/"state",OUT/"state-d4"]:
  rows=[]
  for dispatch in sorted(snap.glob("**/dispatch")):
   if not dispatch.is_dir() or not list(dispatch.glob("*.md")) or len(dispatch.relative_to(snap).parts)>3:continue
   folder=dispatch.parent
   old=previous.extension_errors(folder,OUT/"README.md",PKG)
   new=current.extension_errors(folder,OUT/"README.md",ROOT/"kc-dev-flow-2")
   rows.append(dict(task=str(folder.relative_to(snap)),before=old,after=new,added=sorted(set(new)-set(old)),removed=sorted(set(old)-set(new))))
  live=[r for r in rows if not r["task"].startswith("_archive/")]
  added=[x for r in rows for x in r["added"]]
  live_added=[x for r in live for x in r["added"]]
  summary=dict(snapshot=snap.name,folders=len(rows),changed=sum(r["before"]!=r["after"] for r in rows),added=counts(added),removed=sum(len(r["removed"]) for r in rows),live_before=counts([x for r in live for x in r["before"]]),live_after=counts([x for r in live for x in r["after"]]),live_added=counts(live_added))
  allrows.append({"summary":summary,"rows":rows})
  print(json.dumps(summary))
  assert all(re.match(r"^(ideation|implementation|validation)-[1-9][0-9]*\.md:",x) for x in added)
  assert not any(r["removed"] for r in rows)
  if snap.name=="state-d4":
   assert summary["live_before"]=={"roborev":1},summary
   assert summary["live_after"]=={"paseo":6,"roborev":6},summary
   assert summary["live_added"]=={"paseo":6,"roborev":5},summary
 (OUT/"corpus.json").write_text(json.dumps(allrows,indent=2))
def words():
 baseline=subprocess.check_output(["git","-C",str(ROOT),"show","d37c6dc653e0f45d6ca630c2faa6121c0863a57e:kc-dev-flow-2/scripts/dispatch_records.py"],text=True)
 candidate=(ROOT/"kc-dev-flow-2/scripts/dispatch_records.py").read_text()
 def wc(text):return int(subprocess.check_output(["wc","-w"],input=text,text=True).strip())
 docs=[ast.get_docstring(ast.parse(t)) for t in [baseline,candidate]]
 data={"docstrings":[wc(t) for t in docs],"extension_paragraphs":[wc(t[t.index(prefix):t.index("\n\nUsage:")]) for t,prefix in zip(docs,["When the workflow README lists an extension", "For extensions listed in the workflow README"])]}
 m=mod(ROOT/"kc-dev-flow-2/scripts/dispatch_records.py","word_records")
 record=OUT/"word-record.md";record.write_text("Package root: /pkg\n")
 paseo=m.instruction_error(record,"paseo","Start in the assigned worktree; verify pwd and git root before edits.")
 robo=m.instruction_error(record,"roborev",["extensions/roborev/roborev_gate.py"])
 data.update(paseo_diagnostic=wc(paseo),roborev_diagnostic=wc(robo),paseo_sentence=wc("Start in the assigned worktree; verify pwd and git root before edits."))
 (OUT/"words.json").write_text(json.dumps(data,indent=2));print(json.dumps(data))
 assert data["docstrings"]==[771,824]
 assert (data["paseo_diagnostic"],data["roborev_diagnostic"],data["paseo_sentence"])==(24,30,12)
if __name__=="__main__":
 if not (OUT/"identity.json").exists():
  rev=subprocess.check_output(["git","-C",str(STATE),"rev-parse","HEAD"],text=True).strip()
  (OUT/"identity.json").write_text(json.dumps(dict(candidate="272721000cce947c8f2dcdd3a40c22cdf11dee09",base="d37c6dc653e0f45d6ca630c2faa6121c0863a57e",state=rev,d4="962a430f0"),indent=2))
  snapshot(rev,"state");snapshot("962a430f0","state-d4")
  (OUT/"README.md").write_bytes((STATE.parent/"README.md").read_bytes())
 if "--batch-only" in sys.argv:batch()
 else:batch();corpus();words()

