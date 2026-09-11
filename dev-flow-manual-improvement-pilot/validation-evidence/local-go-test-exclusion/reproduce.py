import hashlib, json, pathlib, subprocess, sys, shutil, datetime, tempfile
W=pathlib.Path(sys.argv[1]); D=W/".context/independent-go-review"; E=pathlib.Path(sys.argv[2]); E.mkdir(parents=True,exist_ok=True)
BASE="0ec3380f590cbaf5b01ee1c325eb222da99a3c5a"
records=[]
def run(args, expected=None):
 r=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=60)
 records.append(dict(argv=[str(x) for x in args],stdout=r.stdout,stderr=r.stderr,exit=r.returncode))
 if expected is not None: assert r.returncode==expected, records[-1]
 return r
sha=lambda b:hashlib.sha256(b).hexdigest()
patch=run(["git","-C",W,"diff","--binary",BASE],0).stdout.encode()
assert sha(patch)=="c1d7ed2b15b237450dea31c6ca1de0fb288986d49516b311d544560d83cdd21c"
checker=W/"kc-dev-flow/scripts/surface-map-check.py"; loader=checker.with_name("profile-contract-loader.py")
variants={"candidate":checker}
for label in ["baseline","overbroad","bypass"]:
 dest=D/label;dest.mkdir(exist_ok=True);shutil.copyfile(loader,dest/loader.name)
 source=run(["git","-C",W,"show",f"{BASE}:kc-dev-flow/scripts/surface-map-check.py"],0).stdout if label=="baseline" else checker.read_text()
 if label=="overbroad":source=source.replace('"_test.go"','".go"')
 if label=="bypass":source=source.replace(" and path not in surface_map", "")
 (dest/checker.name).write_text(source);variants[label]=dest/checker.name
repo=pathlib.Path(tempfile.mkdtemp(prefix="fixture-",dir=D));run(["git","init",repo],0)
(repo/"seed").write_text("seed\n")
def commit(path):
 run(["git","-C",repo,"add",path],0);run(["git","-C",repo,"-c","user.name=review-fixture","-c","user.email=review@example.test","-c","core.hooksPath=/dev/null","commit","-m",path],0)
 return run(["git","-C",repo,"rev-parse","HEAD"],0).stdout.strip()
base=commit("seed"); (repo/"internal").mkdir()
wi=W/"kc-dev-flow/scripts/fixtures/surface-map/dev-66-work-item-fixture.md"
evidence=D/"evidence.md"; checks=[]
def check(name, variant, b,c, content,expected,diagnostic,extra=()):
 evidence.write_text(content)
 r=run([sys.executable,variants[variant],b,c,evidence,"--repo",repo,"--work-item",wi,"--brief",wi,*extra],expected)
 assert diagnostic in r.stdout,(name,r.stdout)
 checks.append(dict(name=name,variant=variant,base=b,candidate=c,evidence=content,expected=expected,diagnostic=diagnostic,record_index=len(records)-1))
p="internal/task_test.go"; (repo/p).write_text("package internal\n"); testcommit=commit(p)
check("baseline reproduces defect","baseline",base,testcommit,"",1,"missing SURFACE line")
check("same-case candidate repairs defect","candidate",base,testcommit,"",0,"excluded: "+p)
check("strict checks test file","candidate",base,testcommit,"",1,"missing SURFACE line",["--no-exclude"])
invalid=f"SURFACE: {p} -> AC-999 | go test {p} | git restore {p}\n"
check("explicit unknown target refused","candidate",base,testcommit,invalid,1,"unknown AC")
check("explicit stub refused","candidate",base,testcommit,f"SURFACE: {p} -> AC-1 | true | true\n",1,"without-it pair does not bind")
check("explicit valid map enforced","candidate",base,testcommit,f"SURFACE: {p} -> AC-1 | go test {p} | git restore {p}\n",0,"1 files checked")
check("explicit-map bypass mutant detected","bypass",base,testcommit,invalid,0,"excluded: "+p)
for filename in ["task.go","contest.go","task_test.go.bak"]:
 p="internal/"+filename;(repo/p).write_text("package internal\n");c=commit(p)
 check("ordinary/non-suffix path enforced: "+filename,"candidate",testcommit,c,"",1,"missing SURFACE line: "+p)
 if filename=="task.go":check("overbroad mutant detected","overbroad",testcommit,c,"",0,"excluded: "+p)
 testcommit=c
# Independently re-run the exact producer fixture bytes, without changing it.
I=E.parent.parent/"implementation-evidence/local-go-test-exclusion"
prior=json.loads((I/"after.json").read_text())
for label,expected in [("baseline",1),("candidate",0)]:
 args=prior["commands"][0]["argv"].copy();args[0]=sys.executable;args[1]=str(variants[label]);r=run(args,expected)
 assert ("missing SURFACE" if expected else "excluded:") in r.stdout
run(["git","-C",W,"diff","--check"],0)
status=run(["git","-C",W,"status","--short","--branch"],0).stdout
assert sha(run(["git","-C",W,"diff","--binary",BASE],0).stdout.encode())==sha(patch)
out=dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),runtime=sys.version,executable=sys.executable,base=BASE,candidate_commit=None,patch_sha256=sha(patch),status=status,checks=checks,records=records,variant_hashes={k:sha(v.read_bytes()) for k,v in variants.items()},reviewer_usage=dict(input=None,cached_input=None,output=None,reasoning=None,reason="Existing host reviewer ran; unique attributable usage source unavailable. Inherited root thread ID not used."),result="PASS local candidate; baseline, overbroad and explicit-map-bypass mutants detected. Mutant checker exits zero are expected evidence of defects, never readiness.")
(E/"independent-results.json").write_text(json.dumps(out,indent=2)+"\n")
shutil.copyfile(__file__,E/"reproduce.py")
print(json.dumps({"result":out["result"],"checks":len(checks),"commands":len(records),"patch_sha256":sha(patch)},indent=2))
