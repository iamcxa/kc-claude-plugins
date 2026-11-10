import sys, subprocess, importlib.util
from pathlib import Path
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
old, new = load("old", sys.argv[1]), load("new", sys.argv[2])
for root in sys.argv[3:]:
    files = subprocess.run(["git","-C",root,"ls-tree","-r","--name-only","HEAD"],capture_output=True,text=True).stdout.split()
    files = [f for f in files if f.endswith(".md") and (f.count("/")==0 or (f.startswith("_archive/") and f.count("/")==1) or f.endswith("/index.md") and f.count("/")<=2)]
    n=diff=0
    for f in files:
        if f in ("README.md",) or f.endswith("/README.md"): continue
        text = subprocess.run(["git","-C",root,"show",f"HEAD:{f}"],capture_output=True,text=True).stdout
        try: reps = old.validation_reports(text)
        except Exception: continue
        if not reps or not old.open_decisions(reps[-1]): continue
        n+=1; res=[]
        for m in (old,new):
            try: c,ok = m.later_captain_ruling(Path(root), Path(root)/f, text, reps); res.append("cleared" if ok else "needs-ruling")
            except m.RulingHistoryError as e: res.append(str(e))
        if res[0]!=res[1]: diff+=1; print(" ", Path(root).name, f, res)
    print(Path(root).name, "open-decision tasks:", n, "changed:", diff)
