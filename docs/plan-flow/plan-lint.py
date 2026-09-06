#!/usr/bin/env python3
"""plan-flow lint v0: eight rules over a Linear Project snapshot; supports fetch and offline lint modes."""
import json, os, sys, urllib.request, hashlib, re, importlib.util, collections
if len(sys.argv) < 2:
    print("Usage: plan-lint.py fetch <project-id> <snapshot.json> | plan-lint.py lint <snapshot.json> [receipt.json]")
    sys.exit(2)
mode = sys.argv[1]
if mode == "fetch":
    if len(sys.argv) < 4: print("fetch requires <project-id> <snapshot.json>"); sys.exit(2)
    PID, SNAP_OUT = sys.argv[2], sys.argv[3]
    def gql(q, v=None):
        req = urllib.request.Request("https://api.linear.app/graphql", data=json.dumps({"query": q, "variables": v or {}}).encode(), headers={"Authorization": os.environ["LINEAR_API_KEY"], "Content-Type": "application/json"})
        try: r=json.load(urllib.request.urlopen(req))
        except urllib.error.HTTPError as e: print("GQL", e.read().decode()[:300]); sys.exit(2)
        if "errors" in r: print("GQL", json.dumps(r["errors"])[:300]); sys.exit(2)
        return r["data"]
    d = gql("""query($p:String!){ project(id:$p){ id name content initiatives{nodes{id}} projectMilestones{nodes{id name}} issues(first:50){nodes{id identifier url description branchName cycle{id} projectMilestone{id} state{type} inverseRelations{nodes{type issue{identifier}}} }} } }""", {"p": PID})["project"]
    snap = {"schema":"kc-plan-receipt/v0", "project": d}
    json.dump(snap, open(SNAP_OUT, "w"), indent=1)
    print(f"Snapshot written to {SNAP_OUT}")
    sys.exit(0)
elif mode == "lint":
    if len(sys.argv) < 3: print("lint requires <snapshot.json> [receipt.json]"); sys.exit(2)
    SNAP_IN = sys.argv[2]
    RECEIPT_OUT = sys.argv[3] if len(sys.argv) > 3 else None
    try: snap_data = json.load(open(SNAP_IN))
    except (FileNotFoundError, json.JSONDecodeError) as e: print(f"Error reading snapshot: {e}"); sys.exit(2)
    d = snap_data.get("project") or snap_data
    guard=os.path.join(os.getcwd(),"kc-dev-flow/scripts/linear-admission.py")
    spec = importlib.util.spec_from_file_location("la",guard); la = importlib.util.module_from_spec(spec); spec.loader.exec_module(la)
    fails=[]; results=[]
    def rule(name, ok, why=""):
        results.append({"rule":name,"pass":bool(ok),"why":why}); print(("PASS " if ok else "FAIL ")+name+(": "+why if why else "")); ok or fails.append(name)
    m = re.search(r"^## User value\n\n(.+?)\n\n", d["content"] or "", re.S); uv = m.group(1) if m else ""
    rule("L1 one-line User value", bool(uv) and "\n" not in uv.strip(), repr(uv[:60]))
    def is_active(issue):
        st = issue.get("state") or {}
        return st.get("type") not in ("completed", "canceled")
    active_issues = [i for i in d["issues"]["nodes"] if is_active(i)]
    admitted_cycles = {i["cycle"]["id"] for i in active_issues if i["cycle"]}
    unadmitted = sum(1 for i in active_issues if not i["cycle"])
    rule("L2 one cycle", len(admitted_cycles) <= 1, f"{admitted_cycles}; unadmitted: {unadmitted}")
    ms = d["projectMilestones"]["nodes"]
    rule("L3 milestone membership", (not ms) or all(i["projectMilestone"] for i in d["issues"]["nodes"]), "no milestones -> implicit single MS" if not ms else "")
    for i in d["issues"]["nodes"]:
        try: item=la.live_item(i); la.delivery_binding(i, i["url"], 5.0); ok=True; why=f"{len(item['non-goals'])} non-goals"
        except Exception as e: ok=False; why=str(e)
        rule(f"L4 admission {i['identifier']}", ok, why)
    rule("L5 initiative when >1 project", True, "single project; not triggered")
    edges=[(r["issue"]["identifier"], i["identifier"]) for i in d["issues"]["nodes"] for r in i["inverseRelations"]["nodes"] if r["type"]=="blocks"]
    ids=sorted(i["identifier"] for i in d["issues"]["nodes"]); indeg={k:0 for k in ids}; adj=collections.defaultdict(list)
    for a,b in edges: adj[a].append(b); indeg[b]+=1
    order=[]; q=sorted(k for k in ids if indeg[k]==0)
    while q:
        n=q.pop(0); order.append(n)
        for b in sorted(adj[n]):
            indeg[b]-=1
            if indeg[b]==0: q.append(b)
    dag_ok = len(order)==len(ids); rule("L6 blockedBy is a DAG", dag_ok, f"blocker->blocked {edges}; order {order}")
    # L6 (replaced): verify blocks-edge direction matches an independent signal of intended order
    if dag_ok:
        l6_intent = sorted(ids)
        l6_violations = []
        for a, b in edges:
            a_idx = l6_intent.index(a) if a in l6_intent else -1
            b_idx = l6_intent.index(b) if b in l6_intent else -1
            if a_idx >= b_idx and a_idx >= 0 and b_idx >= 0:
                l6_violations.append(f"({a}, {b})")
        l6_ok = not l6_violations
        rule("L6 blockedBy direction agrees with identifier order", l6_ok, f"intent order {l6_intent}; violations {', '.join(l6_violations) if l6_violations else 'none'}")
    forked=any(len(v)>1 for v in adj.values()); rule("L7 split advisory (warn only)", True, f"{len(ids)} issues, forked={forked}" + ("; consider Milestones" if (len(ids)>=4 or forked) else ""))
    AC=re.compile(r"^[-*] \*\*AC-\d+\s*\*\*")
    for i in d["issues"]["nodes"]:
        acs=[l for l in i["description"].splitlines() if AC.match(l)]
        rule(f"L8 e2e-able AC {i['identifier']}", bool(acs) and any(re.search(r"exit|script|log|run|prints", a) for a in acs), f"{len(acs)} ACs")
    # L9: for every Issue after the first, at least one claimed surface must be unique to it
    l9_ok = True; l9_violations = []
    def extract_surfaces(desc):
        surfaces = set()
        if not desc: return surfaces
        for match in re.finditer(r'`([^`]*(?:\.(py|md|sh|json|txt|yml|yaml|js|ts|tsx|jsx)|/)[^`]*)`', desc):
            text = match.group(1)
            for path_match in re.finditer(r'(?:^|[^\w/])([a-zA-Z_][a-zA-Z0-9_-]*(?:/[a-zA-Z_][a-zA-Z0-9_./\-]*)+\.[a-zA-Z0-9]+)', text):
                surfaces.add(path_match.group(1))
            if re.match(r'^(?:docs|scripts|kc-dev-flow|kc-pr-flow|evidence)/', text):
                surfaces.add(text.split()[0] if ' ' in text else text)
        return surfaces
    claimed_surfaces = {}
    for i in d["issues"]["nodes"]:
        claimed_surfaces[i['identifier']] = extract_surfaces(i.get('description') or '')
    active_ids = {i['identifier'] for i in active_issues}
    l9_order = [x for x in order if x in active_ids]
    for idx, issue_id in enumerate(l9_order):
        if idx > 0:
            current_surfaces = claimed_surfaces.get(issue_id, set())
            prior_surfaces = set().union(*(claimed_surfaces.get(l9_order[j], set()) for j in range(idx)))
            unique_to_current = current_surfaces - prior_surfaces
            if not unique_to_current:
                non_unique = current_surfaces & prior_surfaces
                first_claimer = None
                for j in range(idx):
                    if non_unique & claimed_surfaces.get(l9_order[j], set()):
                        first_claimer = l9_order[j]
                        break
                violation_msg = f"{issue_id}: only surface {', '.join(sorted(non_unique)[:1])} already claimed by {first_claimer}" if first_claimer else issue_id
                l9_violations.append(violation_msg)
                l9_ok = False
    rule("L9 by-product Issue check", l9_ok, f"issues with no unique surface: {'; '.join(l9_violations) if l9_violations else 'none'}")
    # L10: every Issue must have a Re-verified line with command, exit code, and recent date
    from datetime import datetime, timedelta
    l10_ok = True; l10_violations = []
    today = datetime.utcnow().date()
    for i in d["issues"]["nodes"]:
        desc = i.get('description') or ''
        reverified_lines = [l for l in desc.split('\n') if l.strip().startswith('Re-verified:')]
        if not reverified_lines:
            l10_violations.append(f"{i['identifier']}: no Re-verified line")
            l10_ok = False
        else:
            line = reverified_lines[0]
            try:
                parts = line.split(':')[1].strip().split()
                if len(parts) < 3:
                    l10_violations.append(f"{i['identifier']}: Re-verified format invalid")
                    l10_ok = False
                else:
                    date_str = parts[-1]
                    rv_date = datetime.fromisoformat(date_str).date()
                    age_days = (today - rv_date).days
                    if age_days > 14:
                        l10_violations.append(f"{i['identifier']}: Re-verified date too old ({age_days} days)")
                        l10_ok = False
            except (ValueError, IndexError):
                l10_violations.append(f"{i['identifier']}: Re-verified date parse error")
                l10_ok = False
    rule("L10 re-verified presence and age", l10_ok, f"14-day bound; violations: {', '.join(l10_violations) if l10_violations else 'none'}")
    snap={"schema":"kc-plan-receipt/v0","project":d,"lint":results,"dispatch_order":order,"edges":edges}
    core=json.loads(json.dumps(snap)); core.pop("lint",None); core["project"].pop("content",None); [v.pop("description",None) for v in d["issues"]["nodes"]]
    snap["receipt_sha256"]=hashlib.sha256(json.dumps(core,sort_keys=True).encode()).hexdigest()
    if RECEIPT_OUT: json.dump(snap, open(RECEIPT_OUT,"w"), indent=1)
    print("LINT", "FAIL" if fails else "PASS", "| receipt", snap["receipt_sha256"][:16], "| order", order); sys.exit(1 if fails else 0)
else:
    print(f"Unknown mode: {mode}. Use 'fetch' or 'lint'"); sys.exit(2)
