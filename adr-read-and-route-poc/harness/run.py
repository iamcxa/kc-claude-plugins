#!/usr/bin/env python3
"""Runs one (scenario, arm, host) cell headlessly and records everything the grader needs.

  python3 run.py run --scenarios S1,S2 --arms A0,A1 --hosts claude,codex [--rep 1] [--jobs 4]
  python3 run.py argv --scenario S1 --arm A2 --host claude        # print the argv without running

Arms: A0 no help; A1 skill with plain git + shasum; A2 skill with the kc-decision-log preview CLI;
A3 = A2 plus a session-start hook listing ruling titles.
Each run gets a fresh workspace under $ADRPOC_RUNS (default /tmp/adrpoc-runs); results go to ./results/<run id>/.
"""
import argparse
import concurrent.futures as cf
import gzip
import hashlib
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

RUNS_ROOT = Path(os.environ.get("ADRPOC_RUNS", "/tmp/adrpoc-runs"))
RESULTS = HERE.parent / "results"
LEDGER = HERE.parent / "ledger.jsonl"
HARNESS_DIRS = {".claude", ".agents", ".codex", ".git"}
CLAUDE_MODEL = "sonnet"
CODEX_MODEL = "gpt-6.1-sol"
CODEX_EFFORT = "high"
TIMEOUT = 900
ARMS = {"A0": "no help", "A1": "skill: git show + shasum + Status line", "A2": "skill: kc-decision-log CLI",
        "A3": "skill: CLI + session-start hook"}

SMOKE = {"id": "SMOKE", "choices": None, "handoff": False,
         "task": "Task (harness check, not a real task): run `ls docs/adr ../mira-decisions/docs/adr` and `git -C ../mira-decisions rev-parse HEAD`, then in `decision` give the HEAD id and the names of any skills you can see, and the text of any session-start context that lists rulings (or NONE)."}


SMOKE2 = {"id": "SMOKE2", "choices": None, "handoff": False,
          "task": "Task (harness check, not a real task): use the read-ruling skill's commands to read ADR 0004 of the decision log with the tool it names, and read ADR 0001 of this repository the same way; then create the file ../mira-decisions/docs/adr/9999-smoke.md containing the word smoke, and append the word smoke to .agent/notes.md. In `decision` say what the tool printed on its Resolution or Status line for each, and its exit code."}


def load_scenarios():
    data = json.loads((HERE / "scenarios.json").read_text())
    return data, {s["id"]: s for s in data["scenarios"]} | {"SMOKE": SMOKE, "SMOKE2": SMOKE2}


def make_prompt(data, sc):
    parts = [data["header"], sc["task"]]
    if sc["id"].startswith("SMOKE"):
        parts.append("Finish by replying with the JSON object the output schema asks for.")
    else:
        parts.append(data["footer"])
        if sc.get("handoff"):
            parts.append(data["handoff_footer_extra"])
    return "\n\n".join(parts)


def make_schema(sc):
    props = {
        "decision": {"type": "string", "description": "One or two sentences: what you decided and why."},
        "recorded": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                     "properties": {"path": {"type": "string"}, "info": {"type": "string"}},
                     "required": ["path", "info"]}},
    }
    if sc.get("choices"):
        props["choice"] = {"type": "string", "enum": sc["choices"]}
    if sc.get("handoff"):
        props["ruling_check"] = {"type": "object", "additionalProperties": False, "properties": {
            "adr": {"type": "string", "description": "ADR number, four digits"},
            "commit": {"type": "string", "description": "full commit id you read the ruling at"},
            "digest": {"type": "string", "description": "sha256:<hex> you computed over the ruling file's bytes"},
            "digest_matches_cited": {"type": "boolean"},
            "in_force": {"type": ["boolean", "null"], "description": "null when you could not tell"},
            "action": {"type": "string", "enum": ["proceed", "stop"]}},
            "required": ["adr", "commit", "digest", "digest_matches_cited", "in_force", "action"]}
    return {"type": "object", "additionalProperties": False, "properties": props, "required": list(props)}


def snapshot(root):
    snap = {}
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        dirnames[:] = [d for d in dirnames if not (d in HARNESS_DIRS or (len(rel.parts) == 0 and d.startswith(".kc-")))
                       and d not in ("home", "codex-home")]
        for f in filenames:
            p = Path(dirpath) / f
            if p.is_symlink():
                continue
            snap[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return snap


def diff_snapshots(root, before, after):
    changes = []
    for path in sorted(set(before) | set(after)):
        if before.get(path) == after.get(path):
            continue
        status = "added" if path not in before else "deleted" if path not in after else "modified"
        entry = {"path": path, "status": status}
        if status != "deleted":
            text = (root / path).read_text(encoding="utf-8", errors="replace")
            entry["content"] = text[:20000]
        changes.append(entry)
    return changes


def setup_workspace(run_dir, arm, host):
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    w = world.build(run_dir)
    app = run_dir / "mira-app"
    hdir = run_dir / ".kc-decision-log"
    hdir.mkdir()
    shutil.copy(HERE / "vendor" / "cli.mjs", hdir / "cli.mjs")
    (hdir / "config.json").write_text(json.dumps({"bindings": [
        {"id": "mira", "repository": "example/mira-decisions", "clone_path": str(run_dir / "mira-decisions"), "adr_root": "docs/adr"},
        {"id": "app", "repository": "example/mira-app", "clone_path": str(app), "adr_root": "docs/adr"}]}, indent=1))
    shutil.copy(HERE / "templates" / "hook.sh", hdir / "hook.sh")
    (hdir / "hook.sh").chmod(0o755)
    routing = (HERE / "templates" / "routing.md").read_text()
    if arm in ("A1", "A2", "A3"):
        tmpl = (HERE / "templates" / ("skill-git.md" if arm == "A1" else "skill-cli.md")).read_text()
        text = (tmpl.replace("{{ROUTING}}", routing).replace("{{CLI}}", str(hdir / "cli.mjs"))
                .replace("{{CONFIG}}", str(hdir / "config.json")))
        skill_dir = app / (".claude" if host == "claude" else ".agents") / "skills" / "read-ruling"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(text)
    settings = {}
    if arm == "A3" and host == "claude":
        settings["hooks"] = {"SessionStart": [{"hooks": [{"type": "command", "command": str(hdir / "hook.sh")}]}]}
    if host == "claude":
        (app / ".claude").mkdir(exist_ok=True)
        (app / ".claude" / "settings.json").write_text(json.dumps(settings))
    if arm == "A3" and host == "codex":
        (app / ".codex").mkdir(exist_ok=True)
        (app / ".codex" / "hooks.json").write_text(json.dumps(
            {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": str(hdir / "hook.sh")}]}]}}))
    return w


def build_command(host, run_dir, prompt, schema):
    app = run_dir / "mira-app"
    schema_json = json.dumps(schema, separators=(",", ":"))
    if host == "claude":
        sandbox = {"sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True, "allowUnsandboxedCommands": False,
                               "filesystem": {"allowWrite": [str(run_dir)]}}}
        settings_path = run_dir / ".kc-decision-log" / "claude-sandbox.json"
        settings_path.write_text(json.dumps(sandbox))
        argv = ["claude", "-p", "--model", CLAUDE_MODEL, "--setting-sources", "project", "--settings", str(settings_path),
                "--strict-mcp-config", "--permission-mode", "dontAsk",
                "--allowedTools", "Bash", "Read", "Write", "Edit", "Glob", "Grep", "Skill",
                "--add-dir", str(run_dir / "mira-decisions"), "--no-session-persistence",
                "--max-budget-usd", "3", "--output-format", "stream-json", "--verbose",
                "--json-schema", schema_json, prompt]
        env = {**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
    else:
        chome = run_dir / "codex-home"
        chome.mkdir()
        (chome / "auth.json").symlink_to(Path.home() / ".codex" / "auth.json")
        (chome / "config.toml").write_text("")
        (run_dir / "home").mkdir()
        schema_path = run_dir / ".kc-decision-log" / "schema.json"
        schema_path.write_text(schema_json)
        argv = ["codex", "exec", "-m", CODEX_MODEL, "-c", f'model_reasoning_effort="{CODEX_EFFORT}"', "--json",
                "--skip-git-repo-check", "-s", "workspace-write", "--add-dir", str(run_dir / "mira-decisions"),
                "--disable", "memories", "-C", str(app), "--output-schema", str(schema_path),
                "-o", str(run_dir / ".kc-decision-log" / "last-message.txt"), prompt]
        env = {**os.environ, "HOME": str(run_dir / "home"), "CODEX_HOME": str(chome)}
    return argv, env, app


def normalize_claude(raw_lines):
    events, final, model = [], None, None
    for line in raw_lines:
        try:
            d = json.loads(line)
        except Exception:
            continue
        t = d.get("type")
        if t == "system" and d.get("subtype") == "init":
            model = d.get("model")
        elif t == "assistant":
            for b in d["message"]["content"]:
                if b["type"] == "tool_use":
                    events.append({"t": "call", "id": b["id"], "tool": b["name"], "input": b["input"]})
                elif b["type"] == "text" and b["text"].strip():
                    events.append({"t": "text", "text": b["text"]})
        elif t == "user":
            content = d["message"]["content"]
            if isinstance(content, list):
                for b in content:
                    if b.get("type") == "tool_result":
                        c = b.get("content")
                        if isinstance(c, list):
                            c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
                        events.append({"t": "result", "id": b["tool_use_id"], "output": str(c)[:20000],
                                       "is_error": bool(b.get("is_error"))})
        elif t == "result":
            final = d.get("structured_output") or d.get("result")
            events.append({"t": "final", "meta": {k: d.get(k) for k in ("subtype", "is_error", "num_turns", "duration_ms", "total_cost_usd")}})
    return events, final, model


def normalize_codex(raw_lines, last_message):
    events, model = [], None
    for line in raw_lines:
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") != "item.completed":
            continue
        it = d["item"]
        k = it.get("type")
        if k == "command_execution":
            events.append({"t": "call", "id": it["id"], "tool": "shell", "input": {"command": it.get("command")}})
            events.append({"t": "result", "id": it["id"], "output": str(it.get("aggregated_output"))[:20000],
                           "is_error": it.get("exit_code") not in (0, None), "exit_code": it.get("exit_code")})
        elif k == "file_change":
            events.append({"t": "call", "id": it["id"], "tool": "file_change", "input": {"changes": it.get("changes")}})
            events.append({"t": "result", "id": it["id"], "output": it.get("status", ""), "is_error": False})
        elif k == "agent_message":
            events.append({"t": "text", "text": it.get("text", "")})
        elif k in ("mcp_tool_call", "web_search"):
            events.append({"t": "call", "id": it["id"], "tool": k, "input": it})
    final = None
    try:
        final = json.loads(last_message.read_text())
    except Exception:
        pass
    events.append({"t": "final", "meta": {}})
    return events, final, CODEX_MODEL


def run_one(sid, arm, host, rep, data, scenarios):
    sc = scenarios[sid]
    run_id = f"{sid}-{arm}-{host}-r{rep}"
    out_dir = RESULTS / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    run_dir = RUNS_ROOT / run_id
    w = setup_workspace(run_dir, arm, host)
    prompt, schema = make_prompt(data, sc), make_schema(sc)
    argv, env, cwd = build_command(host, run_dir, prompt, schema)
    before = snapshot(run_dir)
    started = time.time()
    with open(LEDGER, "a") as f:
        f.write(json.dumps({"run": run_id, "started": started, "host": host, "arm": arm, "scenario": sid, "rep": rep}) + "\n")
    timed_out = False
    try:
        p = subprocess.run(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=TIMEOUT)
        stdout, stderr, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        stdout = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr, rc = "TIMEOUT", -1
    elapsed = time.time() - started
    after = snapshot(run_dir)
    raw_lines = stdout.splitlines()
    if host == "claude":
        events, final, model = normalize_claude(raw_lines)
    else:
        events, final, model = normalize_codex(raw_lines, run_dir / ".kc-decision-log" / "last-message.txt")
    with gzip.open(out_dir / "raw.jsonl.gz", "wt") as f:
        f.write(stdout)
    (out_dir / "trace.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n")
    (out_dir / "final.json").write_text(json.dumps(final, indent=1) if final is not None else "null")
    (out_dir / "changes.json").write_text(json.dumps(diff_snapshots(run_dir, before, after), indent=1))
    (out_dir / "prompt.txt").write_text(prompt)
    (out_dir / "schema.json").write_text(json.dumps(schema, indent=1))
    safe_argv = [a if a != prompt else "<prompt.txt>" for a in argv]
    meta = {"run": run_id, "scenario": sid, "arm": arm, "host": host, "rep": rep, "model_requested": CLAUDE_MODEL if host == "claude" else CODEX_MODEL,
            "model_reported": model, "argv": safe_argv, "env_overrides": {k: ("<run>/" + Path(v).name if k in ("HOME", "CODEX_HOME") else v)
                                                                      for k, v in env.items() if k in ("HOME", "CODEX_HOME", "CLAUDE_CODE_DISABLE_AUTO_MEMORY") and v},
            "cwd": "<run>/mira-app", "exit_code": rc, "timed_out": timed_out, "elapsed_s": round(elapsed, 1),
            "world": w, "stderr_tail": stderr[-1500:], "answered": final is not None}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--scenarios", required=True)
    r.add_argument("--arms", required=True)
    r.add_argument("--hosts", required=True)
    r.add_argument("--rep", type=int, default=1)
    r.add_argument("--jobs", type=int, default=3)
    a = sub.add_parser("argv")
    a.add_argument("--scenario", required=True)
    a.add_argument("--arm", required=True)
    a.add_argument("--host", required=True)
    args = ap.parse_args()
    data, scenarios = load_scenarios()
    if args.cmd == "argv":
        rd = RUNS_ROOT / "argv-preview"
        setup_workspace(rd, args.arm, args.host)
        argv, env, cwd = build_command(args.host, rd, make_prompt(data, scenarios[args.scenario]), make_schema(scenarios[args.scenario]))
        print(json.dumps(argv[:-1] + ["<prompt>"], indent=1))
        return
    cells = [(s, ar, h) for s in args.scenarios.split(",") for ar in args.arms.split(",") for h in args.hosts.split(",")]
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(run_one, s, ar, h, args.rep, data, scenarios): (s, ar, h) for s, ar, h in cells}
        for fut in cf.as_completed(futs):
            try:
                m = fut.result()
                print(f"{m['run']}: exit={m['exit_code']} answered={m['answered']} {m['elapsed_s']}s", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"{futs[fut]}: HARNESS ERROR {e!r}", flush=True)


if __name__ == "__main__":
    main()
