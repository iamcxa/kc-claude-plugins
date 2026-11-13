import importlib,json,os,subprocess,sys
from pathlib import Path
root,source=map(Path,sys.argv[1:])
sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
import pr_watch
rows=pr_watch.held_rows(root/'docs/dev2')
def taskpath(base,slug):
    p=base/(slug+'.md'); return p if p.exists() else base/slug/'index.md'
found={r['slug']:taskpath(root/'docs/dev2/.spacedock-state',r['slug']) for r in rows}
lines=pr_watch.held_lines(rows,found)
words=len(lines[0].split());bound=3*len(rows)+6
print(f'CURRENT held={len(rows)} words={words} maximum={bound} result={"PASS" if words<=bound else "FAIL"}')
assert len(rows)==14 and words==32 and words<=bound
one=pr_watch.held_rows(root/'one/docs/dev2')
one_found={r['slug']:root/'one/docs/dev2/.spacedock-state'/(r['slug']+'.md') for r in one}
one_lines=pr_watch.held_lines(one,one_found)
count=len(one_lines[0].split());maximum=3*len(one)+6
print(f'ONE held={len(one)} words={count} maximum={maximum} result={"PASS" if count<=maximum else "FAIL"}')
print('Current dataset passes; the same formula fails for a workflow with one held task.')
sys.exit(0 if count<=maximum else 1)
