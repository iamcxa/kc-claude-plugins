#!/usr/bin/env python3
"""Acceptance probe for #643 at 5e10c355: pr_watch.py tasks on scratch fixtures (temp dir, stub gh first on PATH, scratch HOME, no real workflow, no network).
Usage: probe-643-5e10c355.py <candidate>/kc-dev-flow-2. Exits 1 when an expectation fails."""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path
PKG = Path(sys.argv[1])
STUB = '''#!/usr/bin/env python3
import json, os, sys
a = sys.argv[1:]; d = json.load(open(os.environ["GH_DATA"]))
if a[:2] == ["repo", "view"]: print(json.dumps({"nameWithOwner": "o/r"}))
elif a[:2] == ["pr", "list"]: print(json.dumps(d.get("list", [])))
elif a[:2] == ["pr", "view"]: print(json.dumps(d["view"]))
else: sys.exit(1)
'''
def view(**kw):
    base = {"state": "OPEN", "isDraft": True, "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "headRefOid": "a"*40,
            "statusCheckRollup": [{"conclusion": "SUCCESS"}], "title": "t"}
    base.update(kw); return base
def build(readme_ext="[roborev, learn]", pr="", worktree=True, wt_dir=True, status="validation"):
    tmp = Path(tempfile.mkdtemp(prefix="probe-")); (tmp/"bin").mkdir(); g = tmp/"bin/gh"; g.write_text(STUB); g.chmod(0o755)
    ident = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    env = {**os.environ, **ident, "PATH": f"{tmp/'bin'}{os.pathsep}{os.environ['PATH']}", "GH_DATA": str(tmp/"gh.json"), "HOME": str(tmp/"home")}
    git = lambda w, *a: subprocess.run(["git", "-C", str(w), *a], check=True, capture_output=True, env=env)
    repo = tmp/"repo"; wf = repo/"docs/dev2"; st = wf/".spacedock-state"; st.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main") if repo.exists() else None
    git(st, "init", "-q", "-b", "main") if False else subprocess.run(["git", "-C", str(st), "init", "-q", "-b", "main"], check=True, env=env)
    (wf/"README.md").write_text(f"---\nextensions: {readme_ext}\nstate: .spacedock-state\n---\n")
    fm = f"---\ntitle: t\nstatus: {status}\n" + (f"pr: {pr}\n" if pr else "pr:\n") + ("worktree: .worktrees/some-task\n" if worktree else "") + "---\n"
    (st/"some-task.md").write_text(fm)
    wt = repo/".worktrees/some-task"
    if wt_dir:
        wt.mkdir(parents=True); subprocess.run(["git", "-C", str(wt), "init", "-q", "-b", "task-branch"], check=True, env=env)
        git(wt, "remote", "add", "origin", "https://github.com/o/r.git")
    git(st, "add", "-A"); git(st, "commit", "-qm", "task")
    return dict(tmp=tmp, env=env, wf=wf, st=st, git=git, watch=tmp/"watch.json", data=lambda d: (tmp/"gh.json").write_text(json.dumps(d)))
def run(f, *args, timeout=60):
    d = subprocess.run([sys.executable, "-B", str(PKG/"scripts/pr_watch.py"), "--state", str(f["watch"]), *args], capture_output=True, text=True, env=f["env"], timeout=timeout)
    return d.returncode, d.stdout.strip()
def show(title, rc, out):
    print(f"--- {title}\nexit {rc}"); print(out if out else "(no output)")
def tasks(f): return run(f, "tasks", str(f["wf"]))


import re
BAN = re.compile(r"ask for merge|ask to merge|do not ask|hold the ask|merge ask|delivery_gate", re.I)
bad = []
def check(label, out, want=(), refuse=()):
    print(f"[{label}]"); print("\n".join("    " + l for l in (out.splitlines() or ["(no output)"])))
    for w in want:
        if not any(w in l for l in out.splitlines()): bad.append(f"{label}: missing {w!r}")
    for r in refuse:
        if any(r in l for l in out.splitlines()): bad.append(f"{label}: unexpected {r!r}")
    for l in out.splitlines():
        if BAN.search(l): bad.append(f"{label}: merge-ask or hold line: {l}")
# 1 a green, ready PR with the second reviewers listed (the case that used to print the merge-ask line)
f = build(readme_ext="[roborev, codex, copilot, learn]", pr="o/r#7"); f["data"]({"view": view(isDraft=False)})
rc, out = tasks(f); check("green ready PR, codex and copilot listed", out, want=("fact: o/r#7 OPEN draft=False checks=green",), refuse=("next: mark",))
# 2 a green draft
f["data"]({"view": view()}); rc, out = tasks(f); check("green draft", out, want=("next: mark o/r#7 ready if Delivery authority allows.",))
# 3 a draft with no check runs, quiet 100 s
f = build(pr="o/r#7"); f["data"]({"view": view(statusCheckRollup=[])}); tasks(f)
w = json.loads(f["watch"].read_text()); ref = next(iter(w)); w[ref]["none-since"] = time.time() - 100; f["watch"].write_text(json.dumps(w))
rc, out = tasks(f); check("no CI runs, quiet 100 s", out, want=("unchecked=settled", "next: mark o/r#7 ready"))
# 4 merged PR, learn listed, no observer report
f = build(pr="o/r#7"); f["data"]({"view": view(state="MERGED", mergeable="UNKNOWN")})
rc, out = tasks(f); check("merged PR, no observer report", out, want=("next: keep some-task out of pr-merge's scan in this pass.", "observer not run:"))
# 5 the same with the report committed
(f["st"]/"some-task").mkdir(); (f["st"]/"some-task/observer.md").write_text("ok | rule: x\n"); f["git"](f["st"], "add", "-A"); f["git"](f["st"], "commit", "-qm", "r")
rc, out = tasks(f); check("merged PR, report committed", out, want=("next: let pr-merge record some-task.", "after pr-merge: run"))
# 6 a task with an empty pr whose branch has an open PR
f = build(); f["data"]({"list": [{"number": 7, "state": "OPEN"}], "view": view()})
rc, out = tasks(f); check("empty pr, branch has an OPEN PR", out, want=("--set some-task pr=o/r#7", "spacedock state commit some-task"))
print("\n".join(["FAIL: " + b for b in bad]) if bad else "PASS: tasks prints facts and the kept steps, and no merge-ask or hold line, in all six cases")
sys.exit(1 if bad else 0)
