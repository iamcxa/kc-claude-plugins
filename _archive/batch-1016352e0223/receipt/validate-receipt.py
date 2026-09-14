#!/usr/bin/env python3
"""Validate a kc-plan-receipt v1 (and optionally its approval): schema, canonical hash, DAG, order, body hashes, distinct sentences.
usage: validate-receipt.py <receipt.json> [approval.json]   exit 0 ok, 1 invalid, 2 usage"""
import json, sys, hashlib, re, collections, pathlib
HERE = pathlib.Path(__file__).resolve().parent
def canon(o): return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
def fail(msg): print("INVALID:", msg); sys.exit(1)
try:
    import jsonschema
except ImportError:
    jsonschema = None
if len(sys.argv) < 2: print(__doc__); sys.exit(2)
r = json.load(open(sys.argv[1]))
if jsonschema:
    jsonschema.validate(r, json.load(open(HERE / "kc-plan-receipt.v1.schema.json")))
else:
    print("note: jsonschema not installed; structural checks only")
core = dict(r); core.pop("receipt_sha256", None)
if hashlib.sha256(canon(core)).hexdigest() != r["receipt_sha256"]: fail("receipt_sha256 does not match canonical content")
for k, i in r["issues"].items():
    if hashlib.sha256(i["body"].encode()).hexdigest() != i["body_sha256"]: fail(f"{k} body_sha256 mismatch")
    if i["close_line"] != f"Fixes {k}": fail(f"{k} close_line mismatch")
    if not re.search(rf"(^|[/_-]){re.escape(k)}(\b|[/_-])", i["branch"], re.I): fail(f"{k} branch does not bind the issue")
ids = set(r["issues"]); order = r["dispatch_order"]
if set(order) != ids or len(order) != len(ids): fail("dispatch_order must list every issue exactly once")
pos = {k: n for n, k in enumerate(order)}; indeg = collections.Counter(); adj = collections.defaultdict(list)
for a, b in r["edges"]:
    if a not in ids or b not in ids: fail(f"edge references unknown issue {a}->{b}")
    if pos[a] >= pos[b]: fail(f"dispatch_order violates edge {a}->{b}")
    adj[a].append(b); indeg[b] += 1
seen = 0; q = [k for k in ids if indeg[k] == 0]
while q:
    n = q.pop(); seen += 1
    for b in adj[n]:
        indeg[b] -= 1
        if indeg[b] == 0: q.append(b)
if seen != len(ids): fail("edges contain a cycle")
p = r["project"]
if p["user_value"].strip() == p["hypothesis"].strip() or p["user_value"].strip() == p["name"].strip(): fail("user_value must differ from hypothesis and name")
if p["name"].lower().startswith("if we"): fail("project name must be a headline, not the hypothesis")
if len(p["user_value"].split()) > 30: fail("user_value over 30 words")
ms = {m["id"] for m in r["milestones"]}
for k, i in r["issues"].items():
    if i["milestone"] is not None and i["milestone"] not in ms: fail(f"{k} names an unknown milestone")
if ms and any(i["milestone"] is None for i in r["issues"].values()): fail("milestones exist but an issue has none")
if len(sys.argv) > 2:
    a = json.load(open(sys.argv[2]))
    if jsonschema: jsonschema.validate(a, json.load(open(HERE / "kc-plan-approval.v1.schema.json")))
    if a["receipt_sha256"] != r["receipt_sha256"]: fail("approval does not bind this receipt")
    if a["decision"] != "go": fail(f"approval decision is {a['decision']}; no dispatch authority")
    if a["max_workspaces"] < len(ids): print(f"note: max_workspaces {a['max_workspaces']} < {len(ids)} issues; ship-flow will batch")
print("OK", r["receipt_sha256"][:16], len(ids), "issues", len(r["edges"]), "edges")

# ---- close receipt (optional third argument: close.json) ----
if len(sys.argv) > 3:
    c = json.load(open(sys.argv[3]))
    if jsonschema: jsonschema.validate(c, json.load(open(HERE / "kc-ship-close-receipt.v1.schema.json")))
    cc = dict(c); cc.pop("close_sha256", None)
    if hashlib.sha256(canon(cc)).hexdigest() != c["close_sha256"]: fail("close_sha256 does not match canonical content")
    if c["plan_receipt_sha256"] != r["receipt_sha256"]: fail("close receipt does not bind this plan receipt")
    if set(c["issues"]) != ids: fail("close receipt must report every issue in the plan receipt exactly once")
    if len(sys.argv) > 2:
        aa = dict(json.load(open(sys.argv[2])))
        if hashlib.sha256(canon(aa)).hexdigest() != c["approval_receipt_sha256"]: fail("close receipt does not bind this approval")
        if c["totals"]["workspaces_created"] > aa["max_workspaces"]: fail("more workspaces created than approved")
    print("CLOSE OK", c["close_sha256"][:16], {k: v["outcome"] for k, v in c["issues"].items()})
