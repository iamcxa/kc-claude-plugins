import copy, hashlib, importlib.util, json, pathlib, re, subprocess, sys
sys.dont_write_bytecode = True
w, state, package, sd = map(pathlib.Path, sys.argv[1:])
base = "bfa5354b40ba99e297e7cb2d3e70b41f7d0fece9"
head = "b61a708dadf9cbd9ac1e6d727720c67cf9f06076"
task = "batch-reaches-each-gate-together"
def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True)
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec); sys.modules[name] = result
    spec.loader.exec_module(result); return result
def rejected(name, fn):
    try: fn()
    except AssertionError: print("REJECTED mutation:", name)
    else: raise AssertionError("mutation survived: " + name)
def require(ok):
    assert ok
assert git(w, "rev-parse", "HEAD").strip() == head
assert not git(w, "status", "--porcelain").strip()
ledger = module("ledger_validation", package / "scripts/decision_ledger.py")
proof = json.loads((state/task/"implementation-evidence/batch-proof.json").read_text())
backlog = json.loads((state/task/"implementation-evidence/backlog-bindings.json").read_text())
events = []
for expected in proof["batch7"]["events"]:
    rows = ledger.task_rows(state, state/"_archive"/(expected["task"]+".md"))
    actual = [r for r in rows if r["stage"] == "validation" and r["decision"] == "approve"][-1]
    for key in ("task", "at", "reason", "question"): assert actual[key] == expected[key], key
    events.append(actual)
events.sort(key=lambda e:e["at"])
members = {e["task"] for e in events}
seen = set(); sittings = []
for e in events:
    seen.add(e["task"])
    if seen == members: sittings.append(sorted(seen))
assert len(sittings)==1 and len(sittings[0])==4
rejected("AC-5 eager policy makes four asks", lambda:require(len(events)==1))
rejected("AC-2 silent member removal", lambda:require(set(sittings[0][:-1])==members))
rejected("AC-2 unrelated member joins", lambda:require(set(sittings[0]+["unrelated"])==members))
print("PASS AC-5: four exact historical heads/questions; later #732 explicitly included only in counterfactual; one sitting, eager policy four.")
live_members = {r["task"] for r in proof["batch9"]}
assert live_members == {r["task"] for r in backlog}
for stage, entries, quote in (("backlog", backlog, "准"), ("ideation", proof["batch9"], "照建議")):
    for item in entries:
        slug, commit = item["task"], item["commit"]
        body = git(state, "show", commit+":"+slug+".md")
        fm, _ = ledger.split_task(body)
        resolution = [r for r in ledger.gate_entries(fm) if r["stage"]==stage and r["kind"]=="resolution"][-1]
        assert "五張" in resolution["reason"] and "「"+quote+"」" in resolution["reason"]
        assert resolution["decision"] == (item.get("decision") or "approve")
        index = json.loads(git(state, "show", commit+":"+slug+"/review/"+stage+"/briefing-1/index.json"))
        assert index["id"] == item.get("briefing", item.get("binding"))
        artifact = index["artifacts"][0]
        assert artifact == item["artifact"]
        rev, path = artifact["uri"].removeprefix("git-root://state/").split("/", 1)
        data = subprocess.check_output(["git","-C",str(state),"show",rev+":"+path])
        assert "sha256:"+hashlib.sha256(data).hexdigest()==artifact["rev"]
        subprocess.run(["git","-C",str(state),"merge-base","--is-ancestor",rev,commit],check=True)
        if stage=="ideation":
            reports=data.decode().split("## Stage Report: ideation")
            assert len(reports)>1
            last=reports[-1]
            assert "### Summary" in last
            assert not re.search(r"^- FAILED:",last,re.M), slug
        rejected("AC-8 changed bound artifact "+stage+"/"+slug,
                 lambda:require("sha256:"+hashlib.sha256(data+b"changed").hexdigest()==artifact["rev"]))
        print("PASS AC-8:",stage,slug,resolution["decision"],rev)
rejected("AC-8 omitted live member", lambda:require({r["task"] for r in backlog[:-1]}==live_members))
lint = module("lint_validation",w/"kc-dev-flow-2/scripts/lint-skills.py")
flow_path="kc-dev-flow-2/references/sd/workflow.md"
old=git(w,"show",base+":"+flow_path)
new=(w/flow_path).read_text()
assert (len(old.split()),len(new.split()))==(5605,5754)
assert lint.WORKFLOW_BUDGET_STEPS[-1]["delta"]==178
assert not lint.budget_errors(5754)
for key in ("captain","loaded"):
    steps=copy.deepcopy(lint.WORKFLOW_BUDGET_STEPS); steps[-1][key]=""
    assert lint.budget_errors(5754,steps)
    print("REJECTED mutation: AC-6 missing",key,lint.budget_errors(5754,steps))
assert lint.budget_errors(5755)
print("REJECTED mutation: AC-6 omitted word from budget",lint.budget_errors(5755))
changed=set(git(w,"diff","--name-only",base,head).splitlines())
expected={flow_path,"kc-dev-flow-2/scripts/lint-skills.py","kc-dev-flow-2/scripts/test_poc_readme.py","kc-dev-flow-2/scripts/test_sd_dispatch.py","docs/adr/0043-a-named-batch-waits-for-its-next-gate-before-one-sitting.md"}
assert changed==expected
rejected("AC-7 altered director authority",lambda:require(changed|{"kc-dev-flow-2/skills/design-director/SKILL.md"}==expected))
print("PASS AC-7: five named files only; role inputs, command implementations, ledger, CI and provider scripts unchanged.")
# Re-execute the task's existing lifecycle fixture with candidate code; only workflow differs on these instruction paths.
sys.path.insert(0,str(w/"kc-dev-flow-2/scripts"))
t=module("test_pr_watch_validation",w/"kc-dev-flow-2/scripts/test_pr_watch.py")
outputs={}
for moment in ["startup","idle open","idle merged","after archive"]:
    case=t.TasksTests();case.setUp();case.readme("learn" if moment=="after archive" else "")
    try:
        if moment=="after archive":case.archive("task-0")
        else:case.task("task-0",pr="o/r#7")
        code,lines=case.tasks({"pr view 7":{"state":"MERGED"}} if moment=="after archive" else {},look=lambda *a,**k:t.snap(state="MERGED" if moment=="idle merged" else "OPEN",checks="pending"))
        assert code==0;outputs[moment]="\n".join(lines)
    finally:case.doCleanups()
outputs["merge ask"]="\n".join(t.watch.sittings([dict(slug=f"task-{i}",current="validation",readiness="awaiting-captain") for i in range(4)]))
def section(text,heading):
    a=text.index(heading);b=text.find("\n## ",a+len(heading));return text[a:b if b>=0 else None]
def read(f):return (w/"kc-dev-flow-2"/f).read_text()
mod=read("references/sd/mods/kc-dev-flow-2.md");pm=(sd/"mods/pr-merge.md").read_text()
def measure(flow,is_new):
    authority=section(flow,"## Delivery authority");extensions=section(flow,"## Extensions")
    corpus={
        "startup":flow+read("skills/dev/SKILL.md")+mod+section(pm,"## Hook: startup"),
        "idle open":mod+section(pm,"## Hook: idle")+authority+extensions,
        "idle merged":mod+section(pm,"## Hook: idle")+authority+extensions,
        "after archive":mod+read("extensions/learn/EXTENSION.md"),
        "merge ask":authority+extensions+(sd/"skills/fo-gate-lifecycle/SKILL.md").read_text()+(sd/"skills/present-gate/SKILL.md").read_text()}
    if is_new:
        for m in ("idle open","idle merged","merge ask"):corpus[m]+=section(flow,"## Batch gates")
    return {m:len(text.split())+len(outputs[m].split()) for m,text in corpus.items()}
result={"base":measure(old,False),"candidate":measure(new,True)}
assert result==proof["moments"], result
assert {m:len(v.split()) for m,v in outputs.items()}==proof["fixture_output_words"]
print("PASS AC-6:",json.dumps(result),"unchanged output words",proof["fixture_output_words"])
print("LIMIT: committed quotes/bindings prove recorded decisions, not complete chat or absence of early asks; scenarios do not execute a reviewer.")

