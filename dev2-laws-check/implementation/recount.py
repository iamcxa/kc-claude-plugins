#!/usr/bin/env python3
"""FO-read word recount, base against candidate, for the five moments of the dev2-laws-check design.

Usage: recount.py <candidate>/kc-dev-flow-2 <base export>/kc-dev-flow-2
Export the base with: git archive origin/main kc-dev-flow-2 | tar -x -C <dir>
Counts every passage and script output FO reads at each moment with len(text.split()), the same way for both,
runs the scripts on a scratch workflow behind a stub gh, and exits 1 when a candidate moment exceeds its base moment.
Adapted from the shipped half of fo-lifecycle-mod's recount.py to the 0.23.0 passages; not part of the package."""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

NEW = Path(sys.argv[1])
OLD = Path(sys.argv[2])
PRMERGE = Path("/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0/mods/pr-merge.md")
TITLE = "feat: owner sees feedback room"
STUB = '''#!/usr/bin/env python3
import json, os, sys
a = sys.argv[1:]
mode = open(os.environ["GH_MODE"]).read().strip()
if a[:2] == ["repo", "view"]: print(json.dumps({"nameWithOwner": "o/r"}))
elif a[:2] == ["pr", "list"]: print(json.dumps([{"number": 362, "state": "OPEN"}]))
elif a[:2] == ["pr", "view"]:
    base = {"state": "OPEN", "isDraft": True, "mergeable": "MERGEABLE", "headRefOid": "a"*40, "statusCheckRollup": [{"status": "IN_PROGRESS", "conclusion": None}], "title": os.environ["GH_TITLE"]}
    if mode == "green-draft": base["statusCheckRollup"] = [{"conclusion": "SUCCESS"}]
    if mode == "green-ready": base.update(isDraft=False, statusCheckRollup=[{"conclusion": "SUCCESS"}])
    if mode == "merged": base.update(state="MERGED", mergeable="UNKNOWN")
    print(json.dumps(base))
else: sys.exit(1)
'''
words = lambda t: len(t.split())

def section(text, start, end):
    a = text.index(start); b = text.index(end, a) + len(end)
    return text[a:b]

def passages(root):
    wf = (root / "references/sd/workflow.md").read_text()
    learn = (root / "extensions/learn/EXTENSION.md").read_text()
    return dict(
        authority=section(wf, "Project and Captain authority constrain hook", "explicit choice."),
        merge=section(wf, "Under the Captain's grant quoted in its dispatch", "references/sd/mods/`."),
        head=section(wf, "Before the merge ask, a head other than", "what it printed."),
        ask=section(wf, "A merge ask names each listed reviewer", "is not named as unread."),
        learn=section(learn, "- **FO step:**", "\n- **Read:**").rsplit("\n- **Read:**", 1)[0])

def prmerge(hook):
    t = PRMERGE.read_text()
    a = t.index(f"## Hook: {hook}")
    b = t.index("\n## ", a + 5)
    return t[a:b].strip()

def run(args, env, cwd=None):
    d = subprocess.run(args, capture_output=True, text=True, env=env, cwd=cwd)
    return d.returncode, d.stdout

def fixture(root_pkg, learn=True):
    tmp = Path(tempfile.mkdtemp())
    (tmp / "bin").mkdir(); (tmp / "bin/gh").write_text(STUB); (tmp / "bin/gh").chmod(0o755)
    repo = tmp / "repo"; wf = repo / "docs/dev2"; st = wf / ".spacedock-state"; st.mkdir(parents=True)
    ident = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    env = {**os.environ, **ident, "PATH": f"{tmp/'bin'}{os.pathsep}{os.environ['PATH']}", "GH_MODE": str(tmp / "mode"), "HOME": str(tmp / "home"), "GH_TITLE": TITLE}
    g = lambda w, *a: subprocess.run(["git", "-C", str(w), *a], check=True, capture_output=True, env=env)
    g_init = lambda w: g(w, "init", "-q", "-b", "main")
    repo.mkdir(exist_ok=True); g_init(repo); g_init(st)
    (wf / "README.md").write_text(f"---\nextensions: [roborev{', learn' if learn else ''}]\nstate: .spacedock-state\n---\n")
    wt = repo / ".worktrees/some-task"; wt.mkdir(parents=True); g_init(wt); g(wt, "remote", "add", "origin", "https://github.com/o/r.git")
    (st / "some-task.md").write_text("---\ntitle: t\nstatus: validation\npr: o/r#362\nworktree: .worktrees/some-task\n---\n")
    g(st, "add", "-A"); g(st, "commit", "-qm", "task")
    return dict(tmp=tmp, env=env, wf=wf, st=st, g=g, mode=lambda m: (tmp / "mode").write_text(m), watch=tmp / "watch.json")

def count_out(label, out):
    print(f"    [{label}] {words(out)} words: " + " | ".join(out.strip().splitlines()))
    return words(out)

def measure(pkg):
    P = passages(pkg)
    mod = words((pkg / "references/sd/mods/kc-dev-flow-2.md").read_text())
    s = pkg / "scripts"
    py = lambda script, *a: [sys.executable, str(s / script), *a]
    f = fixture(pkg); e = f["env"]; watch = Path(e["HOME"], ".local/state/kc-dev-flow-2/pr-watch.json")
    mode = f["mode"]
    mode("pending"); tasks_pending = words(run(py("pr_watch.py", "tasks", str(f["wf"])), e)[1])
    watch.unlink(missing_ok=True); run(py("pr_watch.py", "add", "o/r#362"), e)
    mode("green-draft"); wait_draft = words(run(py("pr_watch.py", "wait", "1"), e)[1])
    watch.unlink(missing_ok=True); mode("pending"); tasks_p = tasks_pending
    mode("green-draft"); tasks_green = words(run(py("pr_watch.py", "tasks", str(f["wf"])), e)[1])
    watch.unlink(missing_ok=True); run(py("pr_watch.py", "add", "o/r#362"), e)
    mode("green-ready"); wait_ready = words(run(py("pr_watch.py", "wait", "1"), e)[1])
    task = f["tmp"] / "task.md"
    task.write_text("## Stage Report: validation\n\n- DONE: v\n  Verdict PASSED at a1a1a1a1a1\n")
    (f["tmp"] / "task/dispatch").mkdir(parents=True); (f["tmp"] / "task/dispatch/validation-1.md").write_text("Candidate: " + "a" * 40 + "\n")
    ask = f["tmp"] / "ask.txt"; ask.write_text("Deliver. Codex review:1 clean.")
    gate = words(run(py("delivery_gate.py", "check", str(task), "--pr", "o/r#362", "--text-file", str(ask), "--head", "a" * 40), e)[1])
    watch.unlink(missing_ok=True); mode("green-draft"); run(py("pr_watch.py", "add", "o/r#362"), e)
    mode("merged"); wait_merged = words(run(py("pr_watch.py", "wait", "1"), e)[1])
    watch.unlink(missing_ok=True); miss = words(run(py("pr_watch.py", "tasks", str(f["wf"])), e)[1])
    (f["st"] / "some-task").mkdir(); (f["st"] / "some-task/observer.md").write_text("ok | rule: x\n")
    f["g"](f["st"], "add", "-A"); f["g"](f["st"], "commit", "-qm", "report")
    rerun = words(run(py("pr_watch.py", "tasks", str(f["wf"])), e)[1])
    afters = "\n".join(l for l in run(py("pr_watch.py", "tasks", str(f["wf"])), e)[1].splitlines() if l.startswith("after pr-merge:"))
    (f["st"] / "_archive").mkdir(exist_ok=True)
    f["g"](f["st"], "mv", "some-task.md", "_archive/some-task.md"); f["g"](f["st"], "mv", "some-task", "_archive/some-task")
    f["g"](f["st"], "commit", "-qm", "archive")
    arch = words(run(py("observer_check.py", str(f["st"]), "some-task"), e)[1])
    step3 = words("3. After the `pr-merge` hook, do each `after pr-merge:` line it printed.")
    start, idle = words(prmerge("startup")), words(prmerge("idle"))
    w = lambda k: words(P[k])
    return {
        "1 startup, one open task PR": start + mod + tasks_p,
        "2 idle on an open PR, green draft": idle + mod + tasks_p + w("authority") + wait_draft,
        "3 idle on a merged PR, no report, rerun": idle + mod + w("merge") + w("learn") + wait_merged + miss + rerun,
        "4 after the archive": step3 + words(afters) + arch,
        "5 the merge ask": w("authority") + w("head") + w("ask") + wait_ready + gate,
    }

old, new = measure(OLD), measure(NEW)
over = False
for name in old:
    flag = "OVER" if new[name] > old[name] else "ok"
    over |= flag == "OVER"
    print(f"{name}: base {old[name]} candidate {new[name]} {flag}")
print(f"total: base {sum(old.values())} candidate {sum(new.values())}")
sys.exit(1 if over else 0)
