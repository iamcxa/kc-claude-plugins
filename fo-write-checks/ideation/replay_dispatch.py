"""Replay K2 (reserved line in implementation-1 scope notes), K3 (amendment named in a checklist) and a K5 probe
over every dispatch record add in a state checkout's history. Usage: python3 -I replay_dispatch.py <state checkout>"""
import re, subprocess, sys
STATE = sys.argv[1]
def git(*a):
    r = subprocess.run(["git", "-C", STATE, "-c", "core.quotepath=off", *a], capture_output=True)
    return r.stdout.decode("utf-8", "replace")
def show(c, p):
    r = subprocess.run(["git", "-C", STATE, "show", f"{c}:{p}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None
def section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""
def unfence(t):
    out, inside = [], False
    for l in t.split("\n"):
        if re.match(r"^[ \t]*```", l):
            inside = not inside
            continue
        if not inside:
            out.append(l)
    return "\n".join(out)
def named_numbers(text):
    nums = set()
    for m in re.finditer(r"amendments?[ \t]+((?:\d+(?:[ \t]*(?:,|and|&|to|-)[ \t]*)?)+)", text, re.I):
        nums |= {int(k) for k in re.findall(r"\d+", m.group(1))}
    return nums
adds, cur = [], None
for line in git("log", "--reverse", "--no-merges", "-M", "--name-status", "--format=\x01%H %cs", "--diff-filter=AR").splitlines():
    if line.startswith("\x01"):
        cur = line[1:].split()
    elif line:
        st, *paths = line.split("\t")
        m = re.match(r"^(?:_archive/)?([^/]+)/dispatch/([^/]+\.md)$", paths[-1])
        if m and not (st[0] == "R" and re.search(r"/dispatch/", paths[0])):
            adds.append((cur[0], cur[1], m.group(1), m.group(2), paths[-1]))
rows = fixes = fix_token = every = 0
k2_hits, k3_hits, k2_pass = [], [], []
for c, date, slug, name, path in adds:
    task = next((t for p in (f"{slug}.md", f"_archive/{slug}.md") if (t := show(c, p)) is not None), None)
    rec = show(c, path)
    if task is None or rec is None:
        continue
    recs = {}
    for base in (f"{slug}/dispatch/", f"_archive/{slug}/dispatch/"):
        for n in git("ls-tree", "--name-only", c, base).split("\n"):
            if n.endswith(".md"):
                recs[n.rsplit("/", 1)[1]] = show(c, n)
    rows += 1
    guards = section(task, "Number guards")
    reserved = [("ADR", int(n)) for n in re.findall(r"^ADR:[ \t]*(\d+)[ \t]*$", guards, re.M)] + \
               [("Migration", int(n)) for n in re.findall(r"^Migration:[ \t]*(\d+)[ \t]*$", guards, re.M)]
    every += any(not re.search(rf"\b{k}:[ \t]*0*{n}\b", section(rec, "Scope notes")) for k, n in reserved)
    if name == "implementation-1.md" and reserved:
        miss = [f"{k}: {n:04d}" for k, n in reserved if not re.search(rf"\b{k}:[ \t]*0*{n}\b", section(rec, "Scope notes"))]
        (k2_hits if miss else k2_pass).append((slug, date, c[:8], miss or [f"{k}: {n:04d}" for k, n in reserved]))
    amend = [int(n) for n in re.findall(r"^### Amendment (\d+)", section(unfence(task), "Captain amendments"), re.M)]
    unnamed = [n for n in amend if not any(n in named_numbers(section(r, "Checklist")) for r in recs.values())]
    if unnamed:
        k3_hits.append((slug, name, date, c[:8], unnamed))
    if re.search(r"fix authori[sz]ation", rec, re.I):
        fixes += 1
        fix_token += bool(re.search(r"value-ac\[|captain-ruling\[|contract\[", rec))
print(f"{rows} dispatch-record adds replayed")
print(f"K2 implementation-1 records whose task reserved a line: {len(k2_hits) + len(k2_pass)}; flagged {len(k2_hits)}")
for h in k2_hits: print("  FLAG", *h)
for h in k2_pass: print("  pass", *h)
print(f"K2 applied to every record instead: {every} records flagged")
print(f"K3 record adds that left an amendment named in no checklist: {len(k3_hits)}")
for h in k3_hits: print("  FLAG", *h)
print(f"K5 probe: {fixes} records contain 'fix authorization'; {fix_token} carry value-ac[/captain-ruling[/contract[")
