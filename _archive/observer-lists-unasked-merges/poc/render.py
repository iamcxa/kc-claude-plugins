"""Disposable: python3 -B render.py (run from the state checkout). Renders the observer lines the design
specifies for each dev2 archive since 2026-10-24 and counts them with str.split()."""
import json, re, subprocess, datetime as dt, statistics
def g(*a): return subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
P = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
D = "observer-lists-unasked-merges/poc/"
prs = {p["number"]: p for p in json.load(open(D + "merged-window.json"))}
v, note = {}, {}
for l in open(D + "replay-output.txt"):
    m = re.match(r"^([a-z ]+) \| #(\d+) \| merged (\S+) head (\w+) \| (.*)$", l.strip())
    if m: v[int(m.group(2))] = m.group(1); note[int(m.group(2))] = (m.group(3), m.group(4), m.group(5))
RULE = '"merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it" (Delivery authority)'
CAVEAT = "Coverage: a merge with no ask record may have been approved in chat or recorded in a state checkout this run cannot read; neither shows here."
def render(ins, reported):
    out = [f'ok | rule: {RULE} | evidence: "carried: {sum(v[n] == "carried" for n in ins)} of {len(ins)} merged PRs" (gh pr list, state refs)']
    for k in ("release", "sync", "learning"):
        ns = [n for n in ins if v[n] == k]
        if ns: out.append(f'observed | {k} PRs carry no task ask | evidence: "{k}: ' + " ".join(f"#{n}" for n in ns) + '" (gh pr list)')
    rep, gap = [], False
    for n in ins:
        if v[n] in ("no ask record", "head differs"):
            if n in reported: rep.append(n); continue
            m, h, o = note[n]; gap = True
            word = "can't tell" if v[n] == "no ask record" else "violation"
            out.append(f'{word} | rule: {RULE} | evidence: "{v[n]}: #{n} head {h} merged {m} ({o})" (gh pr list, state refs)')
    if rep: out.append('observed | already in an earlier observer report | evidence: "' + " ".join(f"#{n}" for n in rep) + '"')
    if gap: out.append(CAVEAT)
    return out
log = g("log", "--diff-filter=A", "--format=C %cI", "--name-only", "--since=2026-10-24", "--", "_archive/*.md").split("\n")
arch, cur = [], None
for l in log:
    if l.startswith("C "): cur = l[2:]
    elif l.startswith("_archive/") and l.count("/") == 1: arch.append((P(cur), l[9:-3]))
arch.sort(); reported = set(); on, off = [], []
for t, slug in arch:
    born = g("log", "--diff-filter=A", "--format=%cI", "--reverse", "--", f"{slug}.md").split("\n")[0]
    if not born: continue
    ins = sorted(n for n, p in prs.items() if P(born) < P(p["mergedAt"]) <= t)
    a, b = render(ins, reported), render(ins, set())
    reported.update(n for n in ins if v[n] in ("no ask record", "head differs"))
    on.append((sum(len(x.split()) for x in a), slug, a)); off.append(sum(len(x.split()) for x in b))
big = max(on)
print(f"# {len(on)} archives; added words per observer report, collapse on: median {statistics.median(x[0] for x in on)}, max {big[0]} ({big[1]}); collapse off: median {statistics.median(off)}, max {max(off)}")
print(f"# lines for {big[1]}:"); print("\n".join(big[2]))
