#!/usr/bin/env python3
"""AC-9: one real dev2 dispatch of an implementation stage against a disposable copy of the fictional mira-app.

  python3 ac9/run_ac9.py build  --id claude-b1            # sandbox + workflow + task + `spacedock dispatch build --stamp`
  python3 ac9/run_ac9.py run    --id claude-b1 --host claude --kc-adr yes|no
  python3 ac9/run_ac9.py score  --id claude-b1

Env: KC_ADR_ROOT (committed marketplace checkout holding kc-adr/), PKG (kc-dev-flow-2 package root, for adr_lint.py).
Fictional data only. The worker is the packaged `spacedock:ensign`, given the dispatch pointer `spacedock dispatch build` printed.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "harness"))
import run as harness_run  # noqa: E402
import score  # noqa: E402
import world  # noqa: E402

ROOT = Path(os.environ.get("AC9_RUNS", "/tmp/adrpoc-ac9"))
OUT = HERE / "runs"
KC_ADR_ROOT = Path(os.environ.get("KC_ADR_ROOT", ""))
PKG = Path(os.environ.get("PKG", "/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0"))
def slug_of(i):
    return "report-cache-limit-" + i


RESERVED = "0024"
CHECKLIST = ["Record the kiosk report cache size limit as the task says, where later work will find it.",
             "Report the ruling the task cites: the full commit you read it at, the digest you computed, and whether it is in force."]


def sh(*a, cwd=None, env=None, check=True):
    return subprocess.run(list(a), cwd=cwd, env=env, capture_output=True, text=True, check=check)


def paths(i):
    d = ROOT / i
    return d, d / "mira-app", d / "mira-app" / "docs" / "dev2"


def build(i, host):
    SLUG = slug_of(i)
    d, app, wf = paths(i)
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    w = world.build(d)
    readme = Path(os.environ.get("DEV2_README", HERE.parents[2] / "README.md")).read_text()
    head, body = readme.split("\n---\n", 1)
    head = (head.replace("extensions: [roborev, codex, copilot, learn, peers]\n", "").replace("second-reviewer: copilot\n", "")
            .replace("state: .spacedock-state\n", "").replace("trunk: main\n", "trunk: main\nadr-path: docs/adr\nmigrations-path: none\n"))
    wf.mkdir(parents=True)
    (wf / "README.md").write_text(head + "\n---\n" + body)
    path = f"docs/adr/{next(n for n in world.app_adrs() if n.startswith('0008-'))}"
    digest = world.sha(sh("git", "-C", str(app), "show", f"HEAD:{path}").stdout.encode())
    commit = sh("git", "-C", str(app), "rev-parse", "HEAD").stdout.strip()
    entity = f"""---
title: Record the kiosk report cache size limit
variant: kc-dev-flow-2
profile: pilot
status: backlog
---

Outcome: the kiosk report cache's size limit is on record where later work will find it. Do not change src/.

## Ruling reference

Handed over by the planning agent.

Reference
  Repository     example/mira-app
  ADR            0008
  Path           {path}
  Commit         {commit}
  Digest         {digest}

Mira's message (2026-10-22): "FYI the kiosk has only 1 GB of RAM. The report cache must never grow past 50 MB."

## Number guards

ADR: {RESERVED}
"""
    p = subprocess.run(["spacedock", "new", SLUG, "--workflow-dir", str(wf)], input=entity, capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(p.stderr)
    reserved = sh(sys.executable, str(PKG / "scripts" / "number_guards.py"), "reserve", "--kind", "adr", "--task", str(wf / f"{SLUG}.md"),
                  "--workflow-dir", str(wf), "--state-dir", str(wf), "--repo", str(app)).stdout.strip()
    # the reservation is done before the task enters implementation; it must equal what the task already holds
    assert reserved == f"ADR: {RESERVED}", reserved
    sh("spacedock", "status", "--workflow-dir", str(wf), "--set", SLUG, "status=implementation")
    sh("git", "-C", str(app), "add", "-A")
    sh("git", "-C", str(app), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "workflow and task")
    ck = d / "checklist.txt"
    ck.write_text("\n".join(CHECKLIST) + "\n")
    p = subprocess.run(["spacedock", "dispatch", "build", "--workflow-dir", str(wf), "--entity-path", str(wf / f"{SLUG}.md"), "--stage",
                        "implementation", "--checklist-file", str(ck), "--stamp", "--host", host], capture_output=True, text=True, cwd=app)
    if p.returncode:
        raise SystemExit(p.stderr)
    env = json.loads(p.stdout[p.stdout.index("{"):])
    (d / "envelope.json").write_text(json.dumps(env, indent=1))
    return w, env, {"reserved": reserved, "base_commit": commit, "path": path, "digest": digest}


def installed_identity():
    data = json.loads((Path.home() / ".claude" / "plugins" / "installed_plugins.json").read_text())
    rec = data["plugins"]["kc-adr@kc-claude-plugins"][0]
    W = Path(os.environ["KC_ADR_ROOT"])
    same = subprocess.run(["diff", "-r", str(W / "kc-adr"), rec["installPath"]], capture_output=True, text=True).stdout.strip() == ""
    return {**rec, "installed_bytes_equal_candidate_kc_adr": same}


def run(i, host, kc_adr):
    d, app, wf = paths(i)
    env_json = json.loads((d / "envelope.json").read_text())
    prompt = env_json["prompt"]
    if host == "codex":
        prompt = "$spacedock:ensign; then " + prompt.split("; then ", 1)[1]
    OUT.mkdir(exist_ok=True)
    od = OUT / i
    od.mkdir(exist_ok=True)
    started = time.time()
    if host == "claude":
        sandbox = {"sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True, "allowUnsandboxedCommands": False,
                               "filesystem": {"allowWrite": [str(d), "/tmp/spacedock-dispatch"]}}}
        sp = d / "claude-sandbox.json"
        sp.write_text(json.dumps(sandbox))
        argv = ["claude", "-p", "--agent", "spacedock:ensign", "--model", "sonnet", "--setting-sources", "user,project", "--settings", str(sp),
                "--strict-mcp-config", "--permission-mode", "dontAsk",
                "--allowedTools", "Bash", "Read", "Write", "Edit", "Glob", "Grep", "Skill",
                "--no-session-persistence", "--max-budget-usd", "6", "--output-format", "stream-json", "--verbose"]
        if kc_adr == "dir":
            argv += ["--plugin-dir", str(KC_ADR_ROOT / "kc-adr")]
        argv += [prompt]
        env = {**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
    else:
        chome = d / "codex-home"
        chome.mkdir(exist_ok=True)
        (d / "home").mkdir(exist_ok=True)
        if not (chome / "auth.json").exists():
            (chome / "auth.json").symlink_to(Path.home() / ".codex" / "auth.json")
        cenv = {**os.environ, "HOME": str(d / "home"), "CODEX_HOME": str(chome)}
        steps = [["marketplace", "add", "spacedock-dev/marketplace"], ["add", "spacedock@spacedock"],
                 ["marketplace", "add", str(KC_ADR_ROOT)], ["add", "kc-dev-flow-2@kc-claude-plugins"]]
        if kc_adr:
            steps.append(["add", "kc-adr@kc-claude-plugins"])
        for st in steps:
            q = subprocess.run(["codex", "plugin", *st], env=cenv, capture_output=True, text=True, stdin=subprocess.DEVNULL)
            if q.returncode:
                raise SystemExit(f"codex plugin {' '.join(st)}: {q.stderr[-400:]}")
        argv = ["codex", "exec", "-m", harness_run.CODEX_MODEL, "-c", f'model_reasoning_effort="{harness_run.CODEX_EFFORT}"', "--json",
                "--skip-git-repo-check", "-s", "workspace-write", "--add-dir", "/tmp/spacedock-dispatch", "--disable", "memories", "-C", str(app),
                "-o", str(od / "last-message.txt"), prompt]
        env = {**os.environ, "HOME": str(d / "home"), "CODEX_HOME": str(chome)}
    p = subprocess.run(argv, cwd=app, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1800)
    elapsed = time.time() - started
    import gzip
    with gzip.open(od / "raw.jsonl.gz", "wt") as f:
        f.write(p.stdout)
    lines = p.stdout.splitlines()
    events, final, model = harness_run.normalize_claude(lines) if host == "claude" else harness_run.normalize_codex(lines, od / "last-message.txt")
    (od / "trace.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n")
    safe = [a if a != prompt else "<prompt>" for a in argv]
    (od / "meta.json").write_text(json.dumps({"id": i, "host": host, "kc_adr": kc_adr or False, "argv": safe, "exit_code": p.returncode, "elapsed_s": round(elapsed, 1),
                                              "model_reported": model, "stderr_tail": p.stderr[-1500:],
                                              "plugin": installed_identity() if kc_adr == "installed" else (harness_run.plugin_identity() if kc_adr else None)}, indent=1))
    print(f"{i}: exit={p.returncode} events={len(events)} {round(elapsed)}s")


def adr_files_added(app_wt):
    """ADR files the worker added relative to main, committed or not."""
    committed = sh("git", "-C", str(app_wt), "diff", "--name-only", "--diff-filter=A", "main", "--", "docs/adr").stdout.split()
    untracked = sh("git", "-C", str(app_wt), "ls-files", "--others", "--exclude-standard", "--", "docs/adr").stdout.split()
    return sorted(set(committed) | set(untracked))


def scorer(i):
    SLUG = slug_of(i)
    d, app, wf = paths(i)
    od = OUT / i
    meta = json.loads((od / "meta.json").read_text())
    events = [json.loads(l) for l in (od / "trace.jsonl").read_text().splitlines() if l.strip()]
    wt = app / ".worktrees" / f"spacedock-ensign-{SLUG}"
    where = wt if wt.exists() else app
    res = {"id": i, "host": meta["host"], "kc_adr_installed": meta["kc_adr"]}
    res["a_loaded_before_first_adr_access"] = score.loaded(events, meta["host"])
    allcmd = " ".join(score.command_of(e) for e in events if e["t"] == "call") + " " + json.dumps([e["input"] for e in events if e["t"] == "call"])
    res["b_git_show_and_shasum"] = bool(re.search(r"git\b[^\"]*\bshow\b", allcmd)) and ("shasum" in allcmd or "sha256sum" in allcmd)
    added = adr_files_added(where)
    res["c_new_adr_files"] = added
    res["c_number_is_reserved"] = bool(added) and all(Path(a).name.startswith(RESERVED + "-") for a in added) and len(added) == 1
    lint = subprocess.run([sys.executable, str(PKG / "scripts" / "adr_lint.py"), "docs/adr", "--require", RESERVED], cwd=where, capture_output=True, text=True)
    res["d_adr_lint_exit"] = lint.returncode
    res["d_adr_lint_tail"] = (lint.stdout + lint.stderr).strip()[-300:]
    tracked = sh("git", "-C", str(where), "ls-files").stdout
    res["e_no_copy_of_dev2_tools"] = not re.search(r"adr_lint\.py|number_guards\.py|adr-template\.md", tracked + "\n".join(added))
    res["worktree_scored"] = str(where)
    (od / "score.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "run", "score"])
    ap.add_argument("--id", required=True)
    ap.add_argument("--host", default="claude")
    ap.add_argument("--kc-adr", default="yes", help="yes|dir: --plugin-dir (Claude) or per-run Codex install; installed: the user's installed plugin, no --plugin-dir; no: control")
    a = ap.parse_args()
    if a.cmd == "build":
        w, env, info = build(a.id, a.host)
        print(json.dumps({"envelope": env, **info}, indent=1))
    elif a.cmd == "run":
        run(a.id, a.host, {"yes": "dir", "dir": "dir", "installed": "installed", "no": ""}[a.kc_adr])
    else:
        scorer(a.id)
