#!/usr/bin/env bash
# read-evidence.sh <session-id> -> prints last Evidence block (via conductor sql) or exits 1
SID=$1; conductor sql "SELECT transcript FROM session_transcripts_view WHERE session_id='$SID'" --json 2>/dev/null | python3 -c '
import json,sys; rows=json.load(sys.stdin).get("rows",[]); t=rows[0]["transcript"] if rows else ""
import re; ms=list(re.finditer(r"## Evidence\nCANDIDATE_SHA: [0-9a-f]{40}\n", t)); i=ms[-1].start() if ms else -1; 
if i<0 or "CANDIDATE_SHA:" not in t[i:]: print("no evidence block"); sys.exit(1)
j=t.find("BLOCKER:", i); k=t.find("\n", j) if j>0 else -1; print(t[i:k if k>0 else None].strip())'
