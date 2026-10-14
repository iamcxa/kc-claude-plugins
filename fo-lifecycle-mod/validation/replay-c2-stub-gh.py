#!/usr/bin/env python3
import json, subprocess, sys, os, datetime
args = sys.argv[1:]
log = os.environ.get("GH_STUB_LOG", "/tmp/replay-c2/gh-calls.log")
with open(log, "a") as f:
    f.write(f"{datetime.datetime.utcnow().isoformat()} gh {' '.join(args)}\n")
OWNER = "spacedock-dev/subspace-relay"
HEAD = "79ef8e75601e259379ba8177d60657104223cc90"
MODE = os.environ.get("GH_STUB_MODE", "merged")
PR = {"number": 362, "state": "MERGED" if MODE == "merged" else "OPEN", "isDraft": False, "mergeable": "UNKNOWN" if MODE == "merged" else "MERGEABLE", "headRefOid": HEAD,
      "headRefName": "spacedock-ensign/owner-sees-all-feedback-room", "baseRefName": "main",
      "title": "feat: owner Room shows all feedback", "mergedAt": "2026-10-13T15:55:28Z" if MODE == "merged" else None, "closedAt": "2026-10-13T15:55:28Z" if MODE == "merged" else None,
      "url": f"https://github.com/{OWNER}/pull/362", "statusCheckRollup": [] if MODE == "merged" else [{"name": "ci", "status": "COMPLETED", "conclusion": "SUCCESS"}], "reviews": [], "comments": [],
      "mergeCommit": {"oid": "1111111111111111111111111111111111111111"} if MODE == "merged" else None, "mergeStateStatus": "UNKNOWN" if MODE == "merged" else "CLEAN",
      "reviewDecision": "", "author": {"login": "stub"}}
def flag(name):
    return args[args.index(name) + 1] if name in args else None
def emit(obj):
    jq = flag("--jq") or flag("-q")
    raw = json.dumps(obj)
    if jq:
        p = subprocess.run(["jq", "-r", jq], input=raw, capture_output=True, text=True)
        sys.stdout.write(p.stdout); sys.stderr.write(p.stderr); sys.exit(p.returncode)
    print(raw); sys.exit(0)
def fields(obj):
    j = flag("--json")
    if not j: return obj
    return {k: obj.get(k) for k in j.split(",")}
if args[:2] == ["pr", "view"]:
    n = args[2] if len(args) > 2 and not args[2].startswith("-") else None
    repo = flag("--repo")
    if n in (None, "362") and repo in (None, OWNER):
        emit(fields(PR))
elif args[:2] == ["pr", "list"]:
    repo = flag("--repo")
    if repo in (None, OWNER) and "owner-sees-all-feedback-room" in (flag("--head") or ""):
        emit([fields(PR)])
    emit([])
elif args[:2] == ["repo", "view"]:
    emit({"nameWithOwner": OWNER, "url": f"https://github.com/{OWNER}"})
elif args[:2] == ["pr", "checks"]:
    emit([])
elif args[:2] == ["auth", "status"]:
    print("stub gh: logged in"); sys.exit(0)
sys.stderr.write("stub gh: unsupported or out-of-fixture call: gh " + " ".join(args) + "\n")
sys.exit(1)
