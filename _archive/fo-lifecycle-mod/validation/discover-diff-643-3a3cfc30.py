#!/usr/bin/env python3
"""Differential: pr_watch.entities() vs `spacedock status --json` on one scratch state dir with many shapes. Usage: discover-diff-643-3a3cfc30.py <kc-dev-flow-2 dir>"""
import importlib.util, json, os, subprocess, sys, tempfile
from pathlib import Path
pkg = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("pr_watch", pkg/"scripts/pr_watch.py"); m = importlib.util.module_from_spec(spec); sys.dont_write_bytecode = True; spec.loader.exec_module(m)
tmp = Path(tempfile.mkdtemp(prefix="disc-")); wf = tmp/"wf"; st = wf/".spacedock-state"; st.mkdir(parents=True)
(wf/"README.md").write_text("---\nentity-type: task\nid-style: sequential\nstate: .spacedock-state\nstages:\n  defaults:\n    worktree: false\n  states:\n    - name: validation\n      initial: true\n    - name: done\n      terminal: true\n---\n")
_n=[0]
def F(extra=""):
    _n[0]+=1; return f"---\nid: \"{_n[0]:03d}\"\ntitle: t\nstatus: validation\n{extra}---\nbody\n"
def w(rel, text=None):
    p = st/rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(F() if text is None else text)
w("flat.md"); w("folder/index.md")
w("sidecar.md"); (st/"sidecar/dispatch").mkdir(parents=True); w("sidecar/dispatch/note.md")
w("_archive/a.md"); w("_archive/b/index.md"); w("_mods/m/index.md"); w("_mods/m.md"); w(".hidden/index.md"); w(".dot.md")
w("nofence.md", "no frontmatter here\n"); w("nofencedir/index.md", "no frontmatter here\n")
w("bom.md", "﻿" + F()); w("blank.md", "\n" + F())
w("README2.txt"); w("notes.txt"); w("folderfile.md/index.md")
(st/"README.md").write_text("readme\n")
ext = tmp/"ext"; (ext/"d").mkdir(parents=True); (ext/"f.md").write_text(F()); (ext/"d/index.md").write_text(F())
os.symlink(ext/"f.md", st/"linkflat.md"); os.symlink(ext/"d", st/"linkdir")
out = subprocess.run(["spacedock", "status", "--workflow-dir", str(wf), "--json"], capture_output=True, text=True)
print("spacedock rc", out.returncode, out.stderr.strip()[:300])
try:
    d = json.loads(out.stdout); rows = d if isinstance(d, list) else d.get("entities", d)
    sd = sorted(r["slug"] for r in rows)
except Exception as e:
    print("could not parse spacedock output:", e, out.stdout[:400]); sys.exit(2)
mine_all = [(s, str(p.relative_to(st))) for s, p in m.entities(st)]
mine = sorted(s for s, p in m.entities(st) if "status" in m.front(p))
print("spacedock  :", sd); print("entities() :", [s for s, _ in mine_all]); print("with status:", mine)
only_sd = sorted(set(sd) - set(mine)); only_me = sorted(set(mine) - set(sd))
print("only spacedock:", only_sd); print("only entities():", only_me)
known = {"blank", "bom"}
ok = not only_me and set(only_sd) <= known and {"flat", "folder", "sidecar"} <= set(mine) and not {"_archive", "a", "b", "m", "hidden", "nofence", "nofencedir"} & set(mine)
print("PASS: tasks reads the same task files as spacedock status (flat, folder form, sidecar folder, symlinks; _archive, _mods, dot entries skipped); only spacedock's BOM and leading-blank-line tolerance is not shared (ruled out of scope)" if ok else "FAIL: entities() and spacedock status disagree")
sys.exit(0 if ok else 1)
