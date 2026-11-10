"""Read-only replay of the proposed count scan over committed validation briefing summaries.
A count sentence is checked when it names a file under its task folder (or the state root) that exists at the
state revision read and holds every number of the sentence's count tokens; otherwise it is unchecked.
Usage: scan_replay.py <state checkout> <label> <cut ISO time>; reads HEAD of the checkout with git show only."""
import json, re, subprocess, sys
repo, label, cut = sys.argv[1:4]
NOUN = r"(?:cells?|runs?|tests?|files?|findings?|words?|lines?|PRs?|tasks?|commits?|cases?|records?|steps?|rounds?|tokens?|briefings?|attempts?|skips?)"
COUNT = re.compile(rf"\b(\d[\d,]*)\s*(?:of|/)\s*(\d[\d,]*)\b|\b(\d[\d,]*)\s+{NOUN}\b")
PATH = re.compile(r"(?<![\w/.-])((?:[\w.-]+/)+[\w.-]+\.(?:json|log|md|txt|jsonl|csv|out))\b")
def git(*a): return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout
rev = git("rev-parse", "HEAD").strip()
names = git("ls-tree", "-r", "--name-only", rev).split()
present = set(names)
briefs = [f for f in names if re.search(r"review/validation/briefing-\d+/index\.json$", f)]
out = {k: dict(briefings=0, briefings_with_count=0, count_sentences=0, checked=0, cited_but_unchecked=0, unchecked=0) for k in ("before", "after")}
samples = []
for f in briefs:
    when = git("log", "-1", "--format=%cI", "--diff-filter=A", rev, "--", f).strip()
    k = "after" if when >= cut else "before"
    try: d = json.loads(git("show", f"{rev}:{f}"))
    except Exception: continue
    task = f.split("/review/")[0]
    text = "\n".join(a.get("summary", "") for a in d.get("artifacts", []))
    sents = [s for s in re.split(r"(?<=[.;])\s+|\n", text) if COUNT.search(s)]
    o = out[k]; o["briefings"] += 1; o["briefings_with_count"] += bool(sents)
    for s in sents:
        o["count_sentences"] += 1
        nums = {n.replace(",", "") for m in COUNT.finditer(s) for n in m.groups() if n}
        bodies = []
        for p in PATH.findall(s):
            for cand in (f"{task}/{p}", f"{task.rsplit('/', 1)[0]}/{p}" if "/" in task else p, p):
                if cand in present:
                    bodies.append(git("show", f"{rev}:{cand}")); break
        if bodies and all(re.search(rf"(?<!\d){n}(?!\d)", "\n".join(bodies)) for n in nums): o["checked"] += 1
        else:
            o["unchecked"] += 1
            if bodies: o["cited_but_unchecked"] += 1; samples.append((task.split("/")[-1], s[:160]))
print(json.dumps({"checkout": label, "revision": rev[:9], "cut": cut, **out}))
for s in samples[:5]: print("  cited_but_unchecked:", s)
