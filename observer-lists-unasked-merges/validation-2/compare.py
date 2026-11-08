"""Compare an immutable native observer report with a direct audit receipt.
Usage: python3 -B compare.py DIRECT_STDOUT DIRECT_EXECUTION_JSON REPORT OUT
"""
import hashlib,json,pathlib,re,sys
direct_path,receipt_path,report_path,out = map(pathlib.Path,sys.argv[1:])
direct,raw = direct_path.read_text(),report_path.read_text()
receipt=json.loads(receipt_path.read_text())
expected_exit=receipt["tool_result"]["exit_code"]
lines=[s.strip().removeprefix("- ").replace(chr(96),"").replace("**","") for s in raw.splitlines()]
audit_exit_lines=[s for s in lines if re.search(r"(merge.?audit|saved exit status)",s,re.I) and re.search(r"\bexit(?: status)?(?:\s*[:=]|\s+)",s,re.I)]
exit_numbers=[]
for s in audit_exit_lines:
    positive=re.sub(r"\bnot\s+exit(?: status)?\s*[:=]?\s*[012]\b","",s,flags=re.I)
    exit_numbers.extend(int(n) for n in re.findall(r"\bexit(?: status)?\s*(?:[:=]\s*)?([012])\b",positive,re.I))
checks=[{"name":"audit exit status","status":"passed" if exit_numbers and set(exit_numbers)=={expected_exit} else "failed",
         "detail":{"expected":expected_exit,"reported":exit_numbers,"lines":audit_exit_lines}}]
direct_lines=[s for s in direct.splitlines() if re.match(r"^(carried|release|sync|learning|head differs|no ask record):",s)]
for expected in direct_lines:
    if expected.endswith(": none"): continue
    kind=expected.split(":",1)[0]
    token=re.match(r"(?:no ask record|head differs): #\d+ head [0-9a-f]{12}",expected)
    found=[s for s in lines if (token[0] if token else expected) in s and re.match(r"^(ok|observed|violation|can't tell) \|",s)]
    verdict="can't tell" if kind=="no ask record" else "violation" if kind=="head differs" else "ok" if kind=="carried" else "observed"
    okay=len(found)==1 and found[0].startswith(verdict+" |") and "| evidence:" in found[0]
    if token:
        okay=okay and "| rule:" in found[0] and expected in found[0] and bool(re.search(r"\((?:gh pr list|state refs|merge_audit)[^)]*\)",found[0]))
    elif kind in ("release","sync","learning"):
        okay=okay and "(gh pr list)" in found[0]
    checks.append({"name":token[0] if token else expected,"status":"passed" if okay else "failed","detail":found})
result={"direct_exit":expected_exit,"piped":receipt["piped"],"report_sha256":hashlib.sha256(report_path.read_bytes()).hexdigest(),
        "report_words":len(raw.split()),"checks":checks,"passed":all(x["status"]=="passed" for x in checks),
        "exit_status_passed":checks[0]["status"]=="passed","format_passed":all(x["status"]=="passed" for x in checks[1:])}
out.write_text(json.dumps(result,indent=2))
print(json.dumps({"passed":result["passed"],"checks":len(checks),"failed":[x["name"] for x in checks if x["status"]=="failed"]}))
sys.exit(0 if result["passed"] else 1)
