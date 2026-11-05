"""Collect every validation briefing's question and summary, with the task text at the commit the briefing binds.

Usage: corpus.py OUT.json name=<state checkout> ...   (measured with kc, relay, qnow and web dev2 state checkouts)
"""
import json, glob, os, subprocess, re
import sys
ROOTS = dict(a.split("=", 1) for a in sys.argv[2:])
out, miss = [], 0
for repo, root in ROOTS.items():
    head = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    for idx in sorted(glob.glob(f"{root}/**/review/validation/briefing-*/index.json", recursive=True)):
        rel = os.path.relpath(idx, root); parts = rel.split("/")
        folder = os.path.join(root, *parts[:parts.index("review")])
        d = json.load(open(idx))
        text = d.get("question", "") + "\n" + "\n".join(a.get("summary", "") or "" for a in d.get("artifacts", []))
        task_text = None
        for a in d.get("artifacts", []):
            m = re.match(r"git-root://state/([0-9a-f]{40})/(.+)$", a.get("uri", ""))
            if m:
                r = subprocess.run(["git", "-C", root, "show", f"{m.group(1)}:{m.group(2)}"], capture_output=True, text=True)
                if r.returncode == 0: task_text = r.stdout; break
        if task_text is None: miss += 1; continue
        out.append({"repo": repo, "head": head, "brief": rel, "folder": folder, "text": text, "task_text": task_text})
json.dump(out, open(sys.argv[1], "w"))
from collections import Counter
print(len(out), "gate-time texts;", miss, "briefings without a readable bound task revision;", Counter(o["repo"] for o in out))
print({r: o["head"][:12] for r, o in {o["repo"]: o for o in out}.items()})
