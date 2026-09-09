#!/usr/bin/env python3
"""Validate a kc-plan-receipt v1 (and optionally its approval, and optionally
a kc-ship-close-receipt v1): schema, canonical hash, DAG, order, body hashes,
distinct sentences; on a close receipt: every defect has a non-blank
fix_ticket or accepted_residual, dev_debrief and ship_debrief carry their
minimum non-blank fields, dev_debrief.per_issue matches the plan receipt's
issue set, and ship_debrief.defects_disposition ids match defects_returned
ids. Every close-receipt check above runs in plain Python whether or not
the `jsonschema` package is installed (`python3 -S` drops it from
sys.path without touching the stdlib this script otherwise needs).
usage: validate-receipt.py <receipt.json> [approval.json] [close.json]
exit 0 ok, 1 invalid (see the INVALID: line for what and why), 2 usage or a
missing/unparseable input file (uncaught OSError/JSONDecodeError)."""
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
    approval_schema = json.load(open(HERE / "kc-plan-approval.v1.schema.json"))
    if jsonschema:
        jsonschema.validate(a, approval_schema)
    else:
        # structural checks when jsonschema unavailable
        if "defaults" not in a: fail("defaults block is required")
        defaults = a["defaults"]
        required_fields = {"findings_outside_brief", "minimal_necessity_fail", "moved_base", "worker_blocker", "empty_reviewer", "pr_creation"}
        for field in required_fields:
            if field not in defaults: fail(f"defaults block missing required field: {field}")
        for key in defaults:
            if key not in required_fields: fail(f"defaults block has unexpected field: {key}")
    if a["receipt_sha256"] != r["receipt_sha256"]: fail("approval does not bind this receipt")
    if a["decision"] != "go": fail(f"approval decision is {a['decision']}; no dispatch authority")
    if a["max_workspaces"] < len(ids): print(f"note: max_workspaces {a['max_workspaces']} < {len(ids)} issues; ship-flow will batch")
print("OK", r["receipt_sha256"][:16], len(ids), "issues", len(r["edges"]), "edges")

# ---- close receipt (optional third argument: close.json) ----
# Every check below runs whether or not `jsonschema` is installed, and all of
# them run before jsonschema.validate() -- so a name-the-field refusal fires
# first even when jsonschema is present (a ValidationError traceback does not
# name a defect id the way `fail()` does).
DEFECT_ID_RE = re.compile(r"^S[0-9]+$")
FIX_TICKET_RE = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]+$")


def nonblank(v):
    """A disposition, decision, or correction counts only if it has a
    non-whitespace character; "   " is the same as absent."""
    return isinstance(v, str) and v.strip() != ""


if len(sys.argv) > 3:
    c = json.load(open(sys.argv[3]))

    defect_ids = set()
    undispositioned = []
    for d in c.get("defects_returned", []):
        did = d.get("id")
        if not (isinstance(did, str) and DEFECT_ID_RE.match(did)): fail(f"defects_returned entry has a malformed id (want S<n>): {did!r}")
        defect_ids.add(did)
        fix_ticket = d.get("fix_ticket")
        has_fix = False
        if fix_ticket is not None and nonblank(fix_ticket):
            if not FIX_TICKET_RE.match(fix_ticket.strip()): fail(f"{did} fix_ticket is not a valid issue id: {fix_ticket!r}")
            has_fix = True
        if not has_fix and not nonblank(d.get("accepted_residual")):
            undispositioned.append(did)
    if undispositioned: fail(f"defects_returned missing fix_ticket or accepted_residual: {', '.join(undispositioned)}")

    if "dev_debrief" not in c: fail("close receipt missing dev_debrief")
    dev_debrief = c["dev_debrief"]
    for field in ("per_issue", "candidate_correction"):
        if field not in dev_debrief: fail(f"dev_debrief missing required field: {field}")
    if not nonblank(dev_debrief.get("candidate_correction")): fail("dev_debrief.candidate_correction is blank")
    per_issue = dev_debrief["per_issue"]
    if set(per_issue) != ids: fail(f"dev_debrief.per_issue issues {sorted(per_issue)} do not match the plan receipt's issues {sorted(ids)}")
    for issue_id, entry in per_issue.items():
        for field in ("rounds", "evidence_refusals", "code_refusals"):
            if field not in entry: fail(f"dev_debrief.per_issue.{issue_id} missing required field: {field}")

    if "ship_debrief" not in c: fail("close receipt missing ship_debrief")
    ship_debrief = c["ship_debrief"]
    for field in ("defaults_decisions", "defects_disposition", "minutes_per_station", "candidate_correction"):
        if field not in ship_debrief: fail(f"ship_debrief missing required field: {field}")
    if not nonblank(ship_debrief.get("candidate_correction")): fail("ship_debrief.candidate_correction is blank")
    for dd in ship_debrief["defaults_decisions"]:
        if not nonblank(dd.get("decision")): fail(f"ship_debrief.defaults_decisions entry has a blank decision: {dd!r}")
    disposition_ids = set()
    for dd in ship_debrief["defects_disposition"]:
        did = dd.get("id")
        if not (isinstance(did, str) and DEFECT_ID_RE.match(did)): fail(f"ship_debrief.defects_disposition entry has a malformed id (want S<n>): {did!r}")
        if not nonblank(dd.get("disposition")): fail(f"ship_debrief.defects_disposition.{did} disposition is blank")
        disposition_ids.add(did)
    if disposition_ids != defect_ids: fail(f"ship_debrief.defects_disposition ids {sorted(disposition_ids)} do not match defects_returned ids {sorted(defect_ids)}")

    close_schema_path = HERE.parents[2] / "kc-ship-flow" / "schemas" / "kc-ship-close-receipt.v1.schema.json"
    if not close_schema_path.is_file(): fail(f"close-receipt schema not installed: {close_schema_path}")
    if jsonschema: jsonschema.validate(c, json.load(open(close_schema_path)))
    cc = dict(c); cc.pop("close_sha256", None)
    if hashlib.sha256(canon(cc)).hexdigest() != c["close_sha256"]: fail("close_sha256 does not match canonical content")
    if c["plan_receipt_sha256"] != r["receipt_sha256"]: fail("close receipt does not bind this plan receipt")
    if set(c["issues"]) != ids: fail("close receipt must report every issue in the plan receipt exactly once")
    if len(sys.argv) > 2:
        aa = dict(json.load(open(sys.argv[2])))
        if hashlib.sha256(canon(aa)).hexdigest() != c["approval_receipt_sha256"]: fail("close receipt does not bind this approval")
        if c["totals"]["workspaces_created"] > aa["max_workspaces"]: fail("more workspaces created than approved")
    print("CLOSE OK", c["close_sha256"][:16], {k: v["outcome"] for k, v in c["issues"].items()})
