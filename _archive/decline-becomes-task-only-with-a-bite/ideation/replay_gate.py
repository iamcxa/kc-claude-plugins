"""Replay delivery_gate.text_problems decline lines on the three batch 12/13 validation briefing texts.

Usage: replay_gate.py STATE PACKAGE_SCRIPTS
Each text is briefing-1's question and summaries; the task text is the task file at the state commit the
briefing artifact binds. Prints the decline-related problem lines per task (none = the decline rules pass).
"""
import json, re, subprocess, sys
STATE, SCRIPTS = sys.argv[1], sys.argv[2]
sys.path.insert(0, SCRIPTS); import delivery_gate as g
show = lambda spec: subprocess.run(["git", "-C", STATE, "show", spec], capture_output=True, text=True, check=True).stdout
for slug in ("fo-tries-what-it-asks-the-captain", "model-roster-question-needs-both-families",
             "rewritten-criteria-checked-against-captain-words"):
    d = json.loads(show(f"HEAD:_archive/{slug}/review/validation/briefing-1/index.json"))
    sha, path = re.match(r"git-root://state/([0-9a-f]{40})/(.+)$", d["artifacts"][0]["uri"]).groups()
    text = d["question"] + "\n" + "\n".join(a.get("summary", "") for a in d["artifacts"])
    problems, _ = g.text_problems(show(f"{sha}:{path}"), text)
    decl = [p for p in problems if "declin" in p.lower()]
    print(f"{slug} (bound {sha[:12]}): {len(g.declined_items(text))} declined items, decline problems {decl or 'none'}")
