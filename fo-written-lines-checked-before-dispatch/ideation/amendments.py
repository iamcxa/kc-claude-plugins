import re, subprocess, json, sys
from pathlib import Path
HOME = Path.home() / "conductor"
CH = {
 "kcp": "workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state",
 "qnow": "repos/qnow-adopt-dev2/docs/dev2/.spacedock-state",
 "relay": "workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state",
 "web": "workspaces/subspace-web/dev2-fo/docs/dev2/.spacedock-state"}
def tasks(state):
    files = subprocess.run(["git","-C",str(state),"ls-files","*.md"],capture_output=True,text=True).stdout.split()
    return [f for f in files if "/" not in f.replace("_archive/","",1) and f != "README.md"]
def norm(s): return " ".join(s.split())
rows=[]
for name, rel in CH.items():
    st = HOME/rel
    for f in tasks(st):
        t=(st/f).read_text(errors="replace")
        m=re.search(r"(?m)^## Captain amendments\s*$",t)
        if not m: continue
        body=t[m.end():]
        nxt=re.search(r"(?m)^## ",body); body=body[:nxt.start()] if nxt else body
        folder=(st/f).with_suffix("")
        qs=[]
        for ix in folder.glob("review/*/briefing-*/index.json"):
            try: qs.append(norm(json.loads(ix.read_text())["question"]))
            except Exception: pass
        for e in re.split(r"(?m)^(?=### )",body)[1:]:
            cap=re.search(r"(?m)^Captain:(.*)$",e); ask=re.search(r"(?m)^Asked:(.*(?:\n(?![A-Z][a-z ]+:|###).*)*)",e)
            row={"id":f"{name}/{f}:{e.splitlines()[0][:20]}","cap":cap.group(1).strip() if cap else None,"ask":ask.group(1).strip() if ask else None,"qs":qs,"entry":e}
            rows.append(row)
print(len(rows),"entries")
esc=[r for r in rows if re.search(r'\\"|\\n|\\\\',r["entry"])]
print("json-escape entries:",len(esc),[r["id"] for r in esc][:10])
nocap=[r for r in rows if not r["cap"]]
print("no Captain line:",len(nocap))
import collections
tail=collections.Counter()
for r in rows:
    if not r["cap"]: continue
    c=r["cap"]; i=c.rfind("」")
    t=c[i+1:].strip() if i>=0 else None
    w=len(t.split()) if t is not None else -1
    tail[(w if w<=8 else (9 if w<=15 else 16))]+=1
print("captain tail word-count distribution (-1=no quote):",sorted(tail.items()))
long=[r for r in rows if r["cap"] and "」" in r["cap"] and len(r["cap"][r["cap"].rfind("」")+1:].split())>12]
for r in long: print("LONGTAIL",r["id"],r["cap"][r["cap"].rfind("」")+1:][:200])
noq=[r for r in rows if r["cap"] and "「" not in r["cap"]]
print("captain line w/o 「」:",len(noq)); 
for r in noq[:8]: print("  ",r["id"],r["cap"][:150])
# asked
nask=[r for r in rows if not r["ask"]]
print("no Asked:",len(nask))
inq=0;whole=0;prefix=0
for r in rows:
    if not r["ask"]: continue
    a=norm(r["ask"]).strip('"').strip("「」").strip()
    if any(a in q for q in r["qs"]): inq+=1
    if any(a==q for q in r["qs"]): whole+=1
    if any(q.startswith(a[:40]) for q in r["qs"]): prefix+=1
print("asked substring of a briefing question:",inq,"equal:",whole,"start-matches:",prefix)

print("---- key survey")
KEYS=("Captain:","Asked:","Supersedes:","Design:","Superseded text:")
cnt=collections.Counter(); ex={}
for r in rows:
    inmove=False
    for ln in r["entry"].splitlines()[1:]:
        if not ln.strip(): continue
        if ln.startswith(KEYS):
            inmove = ln.startswith("Superseded text:")
            cnt[ln.split(":")[0]]+=1; continue
        if inmove or ln.startswith((" ","\t")): cnt["(continuation/moved)"]+=1; continue
        cnt["OTHER"]+=1; ex.setdefault(r["id"],[]).append(ln[:100])
print(cnt)
for k,v in list(ex.items())[:12]: print(k,v[:2])
for r in esc:
    for ln in r["entry"].splitlines():
        if re.search(r'\\"|\\n|\\\\',ln): print("ESC",r["id"],ln[:160])

print("---- headings")
pl=collections.Counter()
for r in rows:
    h=r["entry"].splitlines()[0]
    m=re.match(r"### Amendment \d+ — \d{4}-\d{2}-\d{2}(?:,\s*(.*))?$",h)
    pl[(m.group(1) or "").split(",")[0][:30] if m else "NOHEAD:"+h[:40]]+=1
print(pl.most_common(30))
for r in rows:
    h=r["entry"].splitlines()[0]
    if "gate" in h.lower() and r["ask"]:
        a=norm(r["ask"]); print("GATE",r["id"],"|",h[-30:],"| ask:",a[:140],"| inq",any(norm(r['ask']).strip('"「」 ') in q for q in r['qs']))
