import re, subprocess, sys
WT, BASE = sys.argv[1], sys.argv[2]
FILES = {"workflow": "kc-dev-flow-2/references/sd/workflow.md", "mod": "kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md"}
PASSAGES = [
    ("authority", "workflow", "Project and Captain authority", "explicit choice."),
    ("head", "workflow", "Before the merge ask", "what it printed."),
    ("extensions", "workflow", "A merge ask names", "not named as unread."),
    ("review-findings", "workflow", "Authority, a gate approval, a merge", "`Precedent:` line."),
]
def text(which, key):
    if which == "candidate":
        return open(f"{WT}/{FILES[key]}").read()
    return subprocess.run(["git", "-C", WT, "show", f"{BASE}:{FILES[key]}"], capture_output=True, text=True, check=True).stdout
for which in ("base", "candidate"):
    total = 0
    for name, key, start, end in PASSAGES:
        t = text(which, key)
        a = t.index(start)
        b = t.index(end, a) + len(end)
        n = len(t[a:b].split())
        total += n
        print(f"{which} passage {name}: {n}")
    print(f"{which} passages: {total}; workflow.md words: {len(text(which, 'workflow').split())}")
