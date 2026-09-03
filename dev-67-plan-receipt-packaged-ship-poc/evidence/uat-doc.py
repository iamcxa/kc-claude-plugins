#!/usr/bin/env python3
"""Build the package UAT document from per-layer receipts + PR numbers. usage: uat-doc.py <out.md> ISSUE=PR ..."""
import json,sys,os
out=sys.argv[1]; prs=dict(a.split("=") for a in sys.argv[2:]); r=json.load(open("/tmp/poc2/plan-receipt.json"))
L=[f"# UAT: {r['project']['name']}\n", f"Plan receipt `{r['receipt_sha256'][:16]}` · Project `{r['project']['id']}` · dispatch order {' -> '.join(r['dispatch_order'])}\n", "Each layer is one Draft PR at one pinned candidate. Layer N+1 was dispatched on layer N's candidate SHA, so merge bottom to top. All Linear state is untouched by the FO.\n"]
stuck=[]
for i,idn in enumerate(r["dispatch_order"],1):
    p=f"/tmp/poc2/{idn}/receipt.json"; it=r["issues"][idn]
    if not os.path.exists(p): stuck.append((idn,"no receipt: not verified")); continue
    rc=json.load(open(p))
    if not rc["pass"]: stuck.append((idn,f"acceptance failed: retained={rc['without_it']['retained_exit']} removed={rc['without_it']['removed_exit']} contract={rc['contract_test_exit']} preflight={rc['preflight_exit']}")); continue
    pr=prs.get(idn,"(no PR yet)")
    L.append(f"\n## Layer {i}: {idn} — {it['title']}\n")
    L.append(f"- PR: {pr} · candidate `{rc['candidate'][:12]}` · base `{rc['base'][:12]}` · branch `{rc['branch']}`")
    L.append(f"- Without-it (worker's line, FO ran verbatim): retained exit {rc['without_it']['retained_exit']}, removed exit {rc['without_it']['removed_exit']}")
    L.append(f"  - `{rc['without_it']['command']}`")
    L.append(f"- Contract test exit {rc['contract_test_exit']} · merge-tree preflight vs main `{rc['preflight_main'][:12]}` exit {rc['preflight_exit']}")
    L.append("- How to verify: check out the candidate, run the without-it line (expect 0), apply the removed variant, run it again (expect non-zero). ACs and their evidence are in the PR body.")
if stuck:
    L.append("\n## Not handed off\n"); L += [f"- {a}: {b}" for a,b in stuck]
open(out,"w").write("\n".join(L)+"\n"); print(out, "layers", len(r["dispatch_order"])-len(stuck), "stuck", len(stuck))
