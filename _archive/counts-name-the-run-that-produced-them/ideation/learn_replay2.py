"""Read-only: count tokens (N of M, N/M, N <noun>) in completed learn add entries' Evidence; is each number in the
decision's referenced pack evidence, elsewhere in the pack only, or nowhere."""
import json, glob, re, sys
NOUN = r"(?:cells?|runs?|tests?|files?|findings?|words?|lines?|PRs?|tasks?|commits?|cases?|records?|steps?|rounds?|tokens?|briefings?|attempts?|skips?|passes|passed|failures?|comments?|items?|entries|sessions?|times)"
COUNT = re.compile(rf"\b(\d[\d,]*)\s*(?:of|/)\s*(\d[\d,]*)\b|\b(\d[\d,]*)\s+(?:\w+\s)?{NOUN}\b")
def has(n, s): return re.search(rf"(?<![\d,]){re.escape(n)}(?![\d,])", s) is not None
for c in sys.argv[1:]:
    t = dict(entries=0, with_count=0, counts=0, in_refs=0, pack_only=0, nowhere=0); show = []
    for f in sorted(glob.glob(c + "/kc-dev-flow-2/learning/*/record.json")):
        try: r = json.load(open(f))
        except Exception: continue
        if r.get("state") != "completed": continue
        pack = "\n".join(r["input"]["evidence"])
        for d in (r.get("evaluation") or {}).get("decisions") or []:
            if d.get("action") != "add": continue
            t["entries"] += 1; refs = "\n".join(d["evidence"]); ev = d["entry"]["Evidence"]
            ms = list(COUNT.finditer(ev)); t["with_count"] += bool(ms)
            for m in ms:
                ns = [x for x in m.groups() if x]; t["counts"] += 1
                if all(has(x, refs) for x in ns): t["in_refs"] += 1
                elif all(has(x, pack) for x in ns): t["pack_only"] += 1; show.append(("pack_only", f.split("/")[-2][:8], m.group(0)))
                else: t["nowhere"] += 1; show.append(("nowhere", f.split("/")[-2][:8], m.group(0), ev[max(0, m.start()-80):m.end()+40]))
    print(json.dumps({"store": c.split("/.git")[0].split("/")[-1], **t}))
    for s in show: print("  ", s)
