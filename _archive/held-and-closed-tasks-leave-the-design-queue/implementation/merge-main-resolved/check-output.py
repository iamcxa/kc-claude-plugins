#!/usr/bin/env python3
"""Check base absence or candidate exact held names, including duplicate detection."""
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("kind",choices=("legacy","candidate"));p.add_argument("output",type=Path);p.add_argument("rows",type=Path)
a=p.parse_args();out=a.output.read_text()
if a.kind=="legacy":
 names=a.rows.read_text().split();ok=not any(n in out for n in names)
else:
 names=[r["slug"] for r in json.loads(a.rows.read_text())["entities"]]
 lines=[s for s in out.splitlines() if s.startswith("fact: held by the Captain, not waiting:")]
 ok=len(lines)==1 and all(lines[0].count(n)==1 for n in names)
 if ok:
  listed=lines[0].removeprefix("fact: held by the Captain, not waiting: ").split("; each ## Held section")[0]
  got=[n.strip() for group in listed.split("; ") for n in group.split(" ",1)[1].split(", ")]
  ok=len(got)==len(names) and set(got)==set(names)
print(json.dumps(dict(kind=a.kind,passed=ok,names=len(names),words=len(out.split()))))
raise SystemExit(0 if ok else 1)
