#!/usr/bin/env python3
"""plan-flow lint v0: eight rules over one Linear Project; emits a plan receipt. Exit 0 = all pass, 1 = any FAIL, 2 = input error."""
import json, os, sys, urllib.request, hashlib, re, importlib.util, collections
PID=sys.argv[1]; OUT=sys.argv[2] if len(sys.argv)>2 else None
def gql(q, v=None):
    req = urllib.request.Request("https://api.linear.app/graphql", data=json.dumps({"query": q, "variables": v or {}}).encode(), headers={"Authorization": os.environ["LINEAR_API_KEY"], "Content-Type": "application/json"})
    try: r=json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e: print("GQL", e.read().decode()[:300]); sys.exit(2)
    if "errors" in r: print("GQL", json.dumps(r["errors"])[:300]); sys.exit(2)
    return r["data"]
d = gql("""query($p:String!){ project(id:$p){ id name content initiatives{nodes{id}} projectMilestones{nodes{id name}} issues(first:50){nodes{id identifier url description branchName cycle{id} projectMilestone{id} state{type} inverseRelations{nodes{type issue{identifier}}} }} } }""", {"p": PID})["project"]
here=os.path.dirname(os.path.abspath(__file__)); guard=os.path.join(os.getcwd(),"kc-dev-flow/scripts/linear-admission.py")
spec = importlib.util.spec_from_file_location("la",guard); la = importlib.util.module_from_spec(spec); spec.loader.exec_module(la)
fails=[]; results=[]
def rule(name, ok, why=""):
    results.append({"rule":name,"pass":bool(ok),"why":why}); print(("PASS " if ok else "FAIL ")+name+(": "+why if why else "")); ok or fails.append(name)
m = re.search(r"^## User value\n\n(.+?)\n\n", d["content"] or "", re.S); uv = m.group(1) if m else ""
rule("L1 one-line User value", bool(uv) and "\n" not in uv.strip(), repr(uv[:60]))
cyc = {i["cycle"]["id"] if i["cycle"] else None for i in d["issues"]["nodes"]}
rule("L2 one cycle", len(cyc)==1 and None not in cyc, str(cyc))
ms = d["projectMilestones"]["nodes"]
rule("L3 milestone membership", (not ms) or all(i["projectMilestone"] for i in d["issues"]["nodes"]), "no milestones -> implicit single MS" if not ms else "")
for i in d["issues"]["nodes"]:
    try: item=la.live_item(i); la.delivery_binding(i, i["url"], 5.0); ok=True; why=f"{len(item['non-goals'])} non-goals"
    except Exception as e: ok=False; why=str(e)
    rule(f"L4 admission {i['identifier']}", ok, why)
rule("L5 initiative when >1 project", True, "single project; not triggered")
# blockedBy: an inverseRelation of type 'blocks' on X means (issue) blocks X
edges=[(r["issue"]["identifier"], i["identifier"]) for i in d["issues"]["nodes"] for r in i["inverseRelations"]["nodes"] if r["type"]=="blocks"]
ids=sorted(i["identifier"] for i in d["issues"]["nodes"]); indeg={k:0 for k in ids}; adj=collections.defaultdict(list)
for a,b in edges: adj[a].append(b); indeg[b]+=1
order=[]; q=sorted(k for k in ids if indeg[k]==0)
while q:
    n=q.pop(0); order.append(n)
    for b in sorted(adj[n]):
        indeg[b]-=1
        if indeg[b]==0: q.append(b)
rule("L6 blockedBy is a DAG", len(order)==len(ids), f"blocker->blocked {edges}; order {order}")
forked=any(len(v)>1 for v in adj.values()); rule("L7 split advisory (warn only)", True, f"{len(ids)} issues, forked={forked}" + ("; consider Milestones" if (len(ids)>=4 or forked) else ""))
AC=re.compile(r"^[-*] \*\*AC-\d+\s*\*\*")
for i in d["issues"]["nodes"]:
    acs=[l for l in i["description"].splitlines() if AC.match(l)]
    rule(f"L8 e2e-able AC {i['identifier']}", bool(acs) and any(re.search(r"exit|script|log|run|prints", a) for a in acs), f"{len(acs)} ACs")
snap={"schema":"kc-plan-receipt/v0","project":{"id":PID,"name":d["name"],"outcome_hash":"sha256:"+hashlib.sha256((d["name"]+"\n"+(d["content"] or "")).encode()).hexdigest()},"cycle":next(iter(cyc)),"milestones":[x["id"] for x in ms],"dispatch_order":order,"edges":edges,"lint":results,
      "issues":{i["identifier"]:{"id":i["id"],"url":i["url"],"branch":i["branchName"],"close_line":f"Fixes {i['identifier']}","body_sha256":hashlib.sha256(i["description"].encode()).hexdigest(),"description":i["description"]} for i in d["issues"]["nodes"]}}
core=json.loads(json.dumps(snap)); core.pop("lint"); [v.pop("description") for v in core["issues"].values()]
snap["receipt_sha256"]=hashlib.sha256(json.dumps(core,sort_keys=True).encode()).hexdigest()
if OUT: json.dump(snap, open(OUT,"w"), indent=1)
print("LINT", "FAIL" if fails else "PASS", "| receipt", snap["receipt_sha256"][:16], "| order", order); sys.exit(1 if fails else 0)
