#!/usr/bin/env python3
"""Validate a kc-plan-flow contract document against its schema and the rules a
schema cannot state: the archaeologist's proof of absence for every MISSING, the
re-verified line's freedom from colons and issue identifiers, and plan-value's
project block being liftable into kc-plan-receipt/v1.

Usage: validate-contract.py <document.json>

The document's own "schema" field selects the check. Runs on the standard
library alone; if `jsonschema` is importable it is used for structural
validation, and if it is not the required-field and pattern checks below still
run.
"""
import json, sys, re, pathlib

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(2)

HERE = pathlib.Path(__file__).parent
doc = json.load(open(sys.argv[1]))
name = doc.get("schema")
if not name:
    print("INVALID: document has no schema field")
    sys.exit(1)

schema_file = HERE / (name.replace("/", ".") + ".schema.json")
if not schema_file.exists():
    print(f"INVALID: unknown schema {name}")
    sys.exit(1)
schema = json.load(open(schema_file))

problems = []

try:
    import jsonschema
    for e in jsonschema.Draft202012Validator(schema).iter_errors(doc):
        problems.append("/".join(str(p) for p in e.path) + ": " + e.message)
except ImportError:
    for field in schema.get("required", []):
        if field not in doc:
            problems.append(f"missing required field {field}")

if name == "kc-archaeology-report/v1":
    for i, f in enumerate(doc.get("findings", [])):
        if f.get("classification") == "MISSING" and not doc.get("absence_proof"):
            problems.append(f"findings/{i}: MISSING without absence_proof")
        if "/" in f.get("subject", "") and "." in f.get("subject", ""):
            problems.append(f"findings/{i}: subject looks like a path; name the symbol, route or behaviour")

if name == "kc-plan-value/v1":
    # Every claim the project block makes needs a moment it is judged. One measured plan
    # carried three exit conditions and no milestone claiming any of them, so the project
    # could go green with a condition unmet and nothing would have said so.
    claimed = {e for m in doc.get("milestones", []) for e in m.get("satisfies_exit", [])}
    for e in doc.get("project", {}).get("exit", []):
        if e not in claimed:
            problems.append(f"no milestone claims this exit condition: {e[:60]!r}")
    # "In the data, independence and inattention are the same absence" -- the skill says so and
    # nothing checked it, so a plan could stay silent about why nothing blocks an issue.
    blocked = {e.get("blocked") for e in doc.get("dependencies", [])}
    for i, issue in enumerate(doc.get("issues", [])):
        if issue.get("title") not in blocked and not issue.get("independent_because"):
            problems.append(f"issues/{i}: nothing blocks it and it does not say why")
    for i, m in enumerate(doc.get("milestones", [])):
        d = m.get("description", "")
        if len(d) > 140:
            problems.append(f"milestones/{i}: description is {len(d)} characters, bound is 140")
    seen = {i.get("title") for i in doc.get("issues", [])}
    for i, issue in enumerate(doc.get("issues", [])):
        if issue.get("kind") in ("defect", "measurement"):
            p = issue.get("protects")
            if not p:
                problems.append(f"issues/{i}: {issue['kind']} must name the value issue it protects")
            elif p not in seen:
                problems.append(f"issues/{i}: protects names no issue in this document")

if name == "kc-plan-detail/v1":
    for i, s in enumerate(doc.get("sub_issues", [])):
        rv = s.get("re_verified", "")
        if ":" in rv:
            problems.append(f"sub_issues/{i}: re_verified contains a colon; plan-lint splits on it and reads the last word as the date")
        if re.search(r"\b[A-Z]{2,5}-\d+\b", rv, re.I):
            problems.append(f"sub_issues/{i}: re_verified names an issue; the tracker rewrites that into a link whose URL carries colons")
        for j, ac in enumerate(s.get("acceptance", [])):
            if not ac.startswith("- **AC-"):
                problems.append(f"sub_issues/{i}/acceptance/{j}: no bullet marker; plan-lint reads this as zero criteria")

if problems:
    print("INVALID:")
    for p in problems:
        print("  " + p)
    sys.exit(1)

print(f"VALID: {name}")
