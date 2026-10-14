#!/usr/bin/env python3
"""AC-12 recount: words FO reads at each moment, today (origin/main) against the candidate.

Usage: recount.py <candidate>/kc-dev-flow-2 <origin/main export>/kc-dev-flow-2
Export today's package with: git archive origin/main kc-dev-flow-2 | tar -x -C <dir>
Runs both script sets on a scratch workflow behind a stub gh (HOME is a scratch directory, no real watch file),
counts with len(text.split()), prints each moment against the design column, exits 1 when a moment is over."""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

NEW = Path(sys.argv[1])               # worktree root
OLD = Path(sys.argv[2])               # origin/main export root
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
    out = {}
    out["authority"] = section(wf, "Project and Captain authority constrain hook", "explicit choice.")
    out["extensions_ask"] = section(wf, "A merge ask names each listed reviewer", "is not named as unread.")
    out["learn_step"] = section((root / "extensions/learn/EXTENSION.md").read_text(), "- **FO step:**", "\n- **Read:**").rsplit("\n- **Read:**", 1)[0]
    return out

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

def main():
    nx, ol = passages(NEW), passages(OLD)
    oldwf = (OLD / "references/sd/workflow.md").read_text()
    newwf = (NEW / "references/sd/workflow.md").read_text()
    pm_start, pm_idle = words(prmerge("startup")), words(prmerge("idle"))
    mod = words((NEW / "references/sd/mods/kc-dev-flow-2.md").read_text())
    print("constants: pr-merge startup", pm_start, "idle", pm_idle, "authority old/new", words(ol["authority"]), words(nx["authority"]),
          "ext ask old/new", words(ol["extensions_ask"]), words(nx["extensions_ask"]), "mod", mod)
    old_done = section(oldwf, "An archived task's state is publish-only", "runs before the sentinel.")
    old_use = section(oldwf, "Use SD's pending terminal approval", "do not prove merge.")
    old_head = section(oldwf, "A PR delivers only the commit on its head.", "difference told to him first.")
    old_adds = section(oldwf, "FO adds each PR it opens or pushes to", "instead of waiting to be told.")
    new_use = section(newwf, "Under the Captain's grant quoted in its dispatch", "references/sd/mods/`.")
    new_head = section(newwf, "A PR delivers only the commit on its head;", "told to the Captain.")
    dev_old = section((OLD / "skills/dev/SKILL.md").read_text(), "When the README lists `learn` and a task's PR is merged", "hook does.")
    cx = lambda r, n: (r / f"extensions/{n}/EXTENSION.md").read_text()
    watch_c = section(cx(OLD, "codex"), "- **Watch:**", "without\n  `--codex` the watcher does not read Codex.")
    watch_p = section(cx(OLD, "copilot"), "- **Watch:**", "when Copilot answers.")
    P = dict(dev=words(dev_old), adds=words(old_adds), wc=words(watch_c), wp=words(watch_p), done=words(old_done), use=words(old_use), head=words(old_head),
             learn_old=words(ol["learn_step"]), learn_new=words(nx["learn_step"]), new_use=words(new_use), new_head=words(new_head))
    print("passages:", P)

    results = {}
    for tag, pkg in (("today", OLD), ("shipped", NEW)):
        s = pkg / "scripts"
        py = lambda script, *a: [sys.executable, str(s / script), *a]
        f = fixture(pkg)
        e = f["env"]
        w = []
        print(f"== {tag} script output")
        # moment 1: startup, one open PR, checks pending
        f["mode"]("pending")
        if tag == "today":
            m1 = count_out("add", run(py("pr_watch.py", *w, "add", "o/r#362"), e)[1])
        else:
            m1 = count_out("tasks (pending)", run(py("pr_watch.py", *w, "tasks", str(f["wf"])), e)[1])
        # moment 2: idle on open PR; wait exit green draft
        Path(f["env"]["HOME"], ".local/state/kc-dev-flow-2/pr-watch.json").unlink(missing_ok=True)
        run(py("pr_watch.py", *w, "add", "o/r#362"), e)
        f["mode"]("green-draft")
        wait2 = count_out("wait green draft", run(py("pr_watch.py", *w, "wait", "1"), e)[1])
        t2 = 0; t2g = 0
        if tag == "shipped":
            Path(f["env"]["HOME"], ".local/state/kc-dev-flow-2/pr-watch.json").unlink(missing_ok=True); f["mode"]("pending")
            t2 = count_out("tasks (pending)", run(py("pr_watch.py", *w, "tasks", str(f["wf"])), e)[1])
            f["mode"]("green-draft")
            t2g = count_out("tasks (green draft)", run(py("pr_watch.py", *w, "tasks", str(f["wf"])), e)[1])
        # moment 5: wait exit green and ready, then delivery_gate exit 0
        Path(f["env"]["HOME"], ".local/state/kc-dev-flow-2/pr-watch.json").unlink(missing_ok=True); f["mode"]("green-draft")
        run(py("pr_watch.py", *w, "add", "o/r#362"), e)
        f["mode"]("green-ready")
        wait5 = count_out("wait green ready", run(py("pr_watch.py", *w, "wait", "1"), e)[1])
        task = f["tmp"] / "task.md"; head = "a1a1a1a1a1"
        task.write_text(f"## Stage Report: validation\n\n- DONE: v\n  Verdict PASSED at {head[:9]}1 (x)\n")
        task.write_text(f"## Stage Report: validation\n\n- DONE: v\n  Verdict PASSED at a1a1a1a1a1\n")
        ask = f["tmp"] / "ask.txt"; ask.write_text("Deliver. Codex review:1 clean.")
        code, gout = run(py("delivery_gate.py", "check", str(task), "--pr", "o/r#362", "--text-file", str(ask), "--head", head), e)
        gate0 = count_out(f"delivery_gate exit {code}", gout)
        # moment 3: merged, no report
        Path(f["env"]["HOME"], ".local/state/kc-dev-flow-2/pr-watch.json").unlink(missing_ok=True); f["mode"]("green-draft")
        run(py("pr_watch.py", *w, "add", "o/r#362"), e)
        f["mode"]("merged")
        wait3 = count_out("wait merged", run(py("pr_watch.py", *w, "wait", "1"), e)[1])
        if tag == "today":
            code, o = run(py("observer_check.py", str(f["st"]), "some-task"), e); miss = count_out(f"observer_check exit {code}", o); tasks_miss = miss
        else:
            Path(f["env"]["HOME"], ".local/state/kc-dev-flow-2/pr-watch.json").unlink(missing_ok=True)
            code, o = run(py("pr_watch.py", *w, "tasks", str(f["wf"])), e); tasks_miss = count_out(f"tasks, report missing (exit {code})", o)
        (f["st"] / "some-task").mkdir(); (f["st"] / "some-task/observer.md").write_text("ok | rule: x\n")
        f["g"](f["st"], "add", "-A"); f["g"](f["st"], "commit", "-qm", "report")
        if tag == "today":
            code, o = run(py("observer_check.py", str(f["st"]), "some-task"), e); rerun = count_out(f"rerun exit {code}", o)
        else:
            code, o = run(py("pr_watch.py", *w, "tasks", str(f["wf"])), e); rerun = count_out(f"tasks rerun (exit {code})", o)
        # moment 4: archived
        f["g"](f["st"], "mv", "some-task.md", "_archive/some-task.md") if (f["st"] / "_archive").mkdir(exist_ok=True) is None else None
        f["g"](f["st"], "mv", "some-task", "_archive/some-task"); f["g"](f["st"], "commit", "-qm", "archive")
        code, o = run(py("observer_check.py", str(f["st"]), "some-task"), e); arch = count_out(f"archived observer_check exit {code}", o)
        results[tag] = dict(m1=m1, wait2=wait2, t2=t2, t2g=t2g, wait5=wait5, gate0=gate0, wait3=wait3, miss=tasks_miss, rerun=rerun, arch=arch)
    T, S = results["today"], results["shipped"]
    after_lines = 12 + 15   # mod step 3 + two after lines, recounted below
    # recount the after lines from the shipped tasks output
    f = fixture(NEW); e = f["env"]
    f["mode"]("merged"); (f["st"] / "some-task").mkdir(); (f["st"] / "some-task/observer.md").write_text("ok\n"); f["g"](f["st"], "add", "-A"); f["g"](f["st"], "commit", "-qm", "r")
    out = run([sys.executable, str(NEW / "scripts/pr_watch.py"), "--state", str(f["watch"]), "tasks", str(f["wf"])], e)[1]
    afters = "\n".join(l for l in out.splitlines() if l.startswith("after pr-merge:"))
    step3 = words("3. After the `pr-merge` hook, do each `after pr-merge:` line it printed.")
    rows = [
        ("1 startup, one open PR", pm_start + P["dev"] + P["adds"] + P["wc"] + P["wp"] + T["m1"], 513, pm_start + mod + S["m1"], 436),
        ("2 idle, open PR, green draft (tasks pending)", pm_idle + P["adds"] + P["wc"] + P["wp"] + words(ol["authority"]) + T["wait2"], 427,
         pm_idle + mod + S["t2"] + words(nx["authority"]) + S["wait2"], 404),
        ("2b same, tasks run on the green draft", None, None, pm_idle + mod + S["t2g"] + words(nx["authority"]) + S["wait2"], 412),
        ("3 idle, merged PR, no report, rerun", pm_idle + P["use"] + P["done"] + P["learn_old"] + T["wait3"] + T["miss"] + T["rerun"], 458,
         pm_idle + mod + P["new_use"] + P["learn_new"] + S["wait3"] + S["miss"] + S["rerun"], 389),
        ("4 after the archive", P["learn_old"] + T["arch"], 211, step3 + words(afters) + S["arch"], 60),
        ("5 merge ask", words(ol["authority"]) + P["head"] + words(ol["extensions_ask"]) + T["wait5"] + T["gate0"], 423,
         words(nx["authority"]) + P["new_head"] + words(nx["extensions_ask"]) + S["wait5"] + S["gate0"], 396),
    ]
    tt = ts = 0
    print("\nmoment | today measured (design today) | shipped (design column) | verdict")
    ok = True
    for name, t, td, s_, sd in rows:
        verdict = "OK" if s_ <= sd and (t is None or s_ < t) else "OVER"
        ok &= verdict == "OK"
        print(f"{name}: today {t} ({td}) | shipped {s_} ({sd}) | {verdict}")
        if t is not None and not name.startswith("2b"):
            tt += t; ts += s_
    print(f"total today {tt} (2032) shipped {ts} (1685) {'OK' if ts <= 1685 and ts < tt else 'OVER'}")
    sys.exit(0 if ok and ts < tt else 1)
main()
