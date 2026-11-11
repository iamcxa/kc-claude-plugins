#!/usr/bin/env python3
"""Run one chain: six tasks, each by a fresh headless worker, in one tidepool repository.

  run.py chain --arm A|B|C --host codex|claude --rep N [--steps 1,2]   # run and store
  run.py argv --arm A --host codex                                     # print the argv, run nothing
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import world  # noqa: E402

RUNS = Path(os.environ.get("DOCPOC_RUNS", "/tmp/docpoc-runs"))
RESULTS = HERE.parent / "results"
LEDGER = HERE.parent / "ledger.jsonl"
CLAUDE_MODEL, CODEX_MODEL, CODEX_EFFORT = "sonnet", "gpt-6.1-sol", "xhigh"
TIMEOUT = 1500

PROMPT = ("You are an implementation worker in the repository in your working directory. "
          "Read `.flow/README.md` first and work as it says.\n\nTask from the coordinator:\n\n{task}\n")

STEPS = [
    ("cancel-window", "Shops asked for a shorter free-cancellation window. A customer now gets the deposit back "
     "only when cancelling 18 hours or more before the appointment, instead of 36."),
    ("no-show", "Add a no-show outcome. When a customer does not turn up, staff mark the booking `no_show`. "
     "Only a confirmed booking can be marked, and the shop keeps the deposit."),
    ("ruling", "The owner, Mira, wrote this morning (2026-11-11): 「From now on nobody gets the deposit back "
     "inside the window. No exceptions, Harbor Club included.」 Make the system follow it."),
    ("reminder", "Send the reminder 44 hours before the appointment instead of 20. Mira also mentioned that "
     "someday customers should be able to move an appointment by replying to an SMS. Not now; she only "
     "does not want the idea lost."),
    ("refactor", "`tidepool/slots.py` computes when a hold ends in two places. Extract one helper and use it in "
     "both. No behaviour change."),
    ("waitlist", "Add a waitlist. When a slot is taken a customer can join its waitlist. When the slot frees up, "
     "the first person who joined is offered it and has 25 minutes to accept before the offer passes to "
     "the next person."),
]


def build_command(host, run_dir, ws, prompt):
    if host == "claude":
        settings = run_dir / "claude-sandbox.json"
        settings.write_text(json.dumps({"sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True,
                                                    "allowUnsandboxedCommands": False,
                                                    "filesystem": {"allowWrite": [str(ws)]}}}))
        argv = ["claude", "-p", "--model", CLAUDE_MODEL, "--setting-sources", "project", "--settings", str(settings),
                "--strict-mcp-config", "--permission-mode", "dontAsk",
                "--allowedTools", "Bash", "Read", "Write", "Edit", "Glob", "Grep",
                "--no-session-persistence", "--max-budget-usd", "4", "--output-format", "stream-json", "--verbose", prompt]
        env = {**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
    else:
        chome, home = run_dir / "codex-home", run_dir / "home"
        if not chome.exists():
            chome.mkdir()
            (chome / "auth.json").symlink_to(Path.home() / ".codex" / "auth.json")
            (chome / "config.toml").write_text("")
            home.mkdir()
        argv = ["codex", "exec", "-m", CODEX_MODEL, "-c", f'model_reasoning_effort="{CODEX_EFFORT}"', "--json",
                "--skip-git-repo-check", "-s", "workspace-write", "--disable", "memories", "-C", str(ws),
                "-o", str(run_dir / "last-message.txt"), prompt]
        env = {**os.environ, "HOME": str(home), "CODEX_HOME": str(chome)}
    return argv, env


def git(ws, *args, check=True):
    return subprocess.run(["git", "-C", str(ws), "-c", "user.name=harness", "-c", "user.email=harness@example.invalid",
                           *args], check=check, capture_output=True, text=True).stdout


def usage_of(host, raw):
    total = {}
    for line in raw.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        use = ev.get("usage") if host == "claude" and ev.get("type") == "result" else (
            ev.get("usage") if host == "codex" and ev.get("type") == "turn.completed" else None)
        for key, val in (use or {}).items():
            if isinstance(val, int):
                total[key] = total.get(key, 0) + val
    return total


def chain(arm, host, rep, only=None):
    chain_id = f"{arm}-{host}-r{rep}"
    run_dir, out = RUNS / chain_id, RESULTS / chain_id
    ws = run_dir / "tidepool"
    if only is None or not ws.exists():
        shutil.rmtree(run_dir, ignore_errors=True)
        run_dir.mkdir(parents=True)
        world.build(ws, arm)
    out.mkdir(parents=True, exist_ok=True)
    for n, (slug, task) in enumerate(STEPS, 1):
        if only and n not in only:
            continue
        prompt = PROMPT.format(task=task)
        argv, env = build_command(host, run_dir, ws, prompt)
        start = time.time()
        try:
            p = subprocess.run(argv, cwd=ws, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=TIMEOUT)
            raw, rc, timed_out = p.stdout, p.returncode, False
        except subprocess.TimeoutExpired as e:
            raw, rc, timed_out = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), -1, True
        elapsed = round(time.time() - start, 1)
        git(ws, "add", "-A")
        git(ws, "commit", "-q", "--allow-empty", "-m", f"step {n}: {slug}")
        git(ws, "tag", "-f", f"step-{n}")
        tests = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"], cwd=ws,
                               capture_output=True, text=True)
        (out / f"step-{n}.raw.jsonl").write_text(raw)
        final = run_dir / "last-message.txt"
        meta = {"chain": chain_id, "step": n, "slug": slug, "arm": arm, "host": host, "rep": rep,
                "model": CLAUDE_MODEL if host == "claude" else CODEX_MODEL,
                "effort": None if host == "claude" else CODEX_EFFORT, "exit_code": rc, "timed_out": timed_out,
                "elapsed_s": elapsed, "usage": usage_of(host, raw), "tests_pass": tests.returncode == 0,
                "files_changed": git(ws, "diff", "--name-only", f"step-{n - 1}", f"step-{n}").split(),
                "final": final.read_text() if host == "codex" and final.exists() else None,
                "argv": [a if a != prompt else "<prompt>" for a in argv]}
        (out / f"step-{n}.meta.json").write_text(json.dumps(meta, indent=1))
        with LEDGER.open("a") as f:
            f.write(json.dumps({k: meta[k] for k in ("chain", "step", "exit_code", "timed_out", "elapsed_s", "tests_pass")}) + "\n")
        print(f"{chain_id} step {n} {slug}: rc={rc} {elapsed}s tests={'ok' if meta['tests_pass'] else 'FAIL'} files={len(meta['files_changed'])}", flush=True)
    if only is None:
        git(ws, "bundle", "create", str(out / "tidepool.bundle"), "--all")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("chain", "argv"):
        s = sub.add_parser(name)
        s.add_argument("--arm", required=True, choices=sorted(world.ARMS))
        s.add_argument("--host", required=True, choices=["codex", "claude"])
        s.add_argument("--rep", type=int, default=1)
        s.add_argument("--steps")
    a = ap.parse_args()
    if a.cmd == "argv":
        print(json.dumps(build_command(a.host, Path("/tmp/x"), Path("/tmp/x/tidepool"), "<prompt>")[0]))
        return
    chain(a.arm, a.host, a.rep, {int(x) for x in a.steps.split(",")} if a.steps else None)


if __name__ == "__main__":
    main()
