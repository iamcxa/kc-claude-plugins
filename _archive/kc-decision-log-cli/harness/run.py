#!/usr/bin/env python3
"""Runs one (scenario, arm, host) cell headlessly and records everything the grader needs.

  python3 run.py run --scenarios S1,S2 --arms A0,B1 --hosts claude,codex [--rep 1] [--jobs 4]
  python3 run.py argv --scenario S1 --arm B1 --host claude        # print the argv without running

Arms: A0 no help; B1 the shipped kc-adr plugin (skill read-adr), installed from $KC_ADR_ROOT, a git checkout
of the marketplace repository whose kc-adr/ tree is committed (the run refuses a dirty tree).
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
RESULTS = Path(os.environ.get("ADRPOC_RESULTS", HERE.parent / "results"))
LEDGER = RESULTS.parent / ("ledger-probes.jsonl" if RESULTS.name == "probes" else "ledger.jsonl")
HARNESS_DIRS = {".claude", ".agents", ".codex", ".git"}
CLAUDE_MODEL = "sonnet"
CODEX_MODEL = "gpt-6.1-sol"
CODEX_EFFORT = "high"
TIMEOUT = 900
ARMS = {"A0": "no help", "B1": "plugin kc-adr (skill read-adr)"}
KC_ADR_ROOT = Path(os.environ.get("KC_ADR_ROOT", ""))

SMOKE = {"id": "SMOKE", "choices": None, "handoff": False,
         "task": "Task (harness check, not a real task): run `ls docs/adr ../mira-decisions/docs/adr` and `git -C ../mira-decisions rev-parse HEAD`, then in `decision` give the HEAD id and the names of any skills you can see, and the text of any session-start context that lists rulings (or NONE)."}


SMOKE3 = {"id": "SMOKE3", "choices": None, "handoff": False,
          "task": "Task (harness check, not a real task): in `decision` list the names of every skill you can see, with the plugin prefix if it has one (or NONE). Do not change any file."}


def load_scenarios():
    data = json.loads((HERE / "scenarios.json").read_text())
    return data, {s["id"]: s for s in data["scenarios"]} | {"SMOKE3": SMOKE3}


def plugin_identity():
    """The committed kc-adr tree the run uses; refuses a dirty tree so the bytes are provable."""
    git = ["git", "-C", str(KC_ADR_ROOT)]
    if subprocess.run(git + ["status", "--porcelain", "--", "kc-adr"], capture_output=True, text=True, check=True).stdout.strip():
        raise SystemExit("kc-adr has uncommitted changes; commit before running arm B1")
    return {"commit": subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(),
            "kc_adr_tree": subprocess.run(git + ["rev-parse", "HEAD:kc-adr"], capture_output=True, text=True, check=True).stdout.strip()}


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
    (run_dir / ".kc-decision-log").mkdir()
    if host == "claude":
        (app / ".claude").mkdir(exist_ok=True)
        (app / ".claude" / "settings.json").write_text("{}")
    return w


def install_codex_plugin(run_dir):
    """Per-run CODEX_HOME with kc-adr and kc-dev-flow-2 (the writing tools the skill points at) installed the way a user would."""
    chome = run_dir / "codex-home"
    env = {**os.environ, "HOME": str(run_dir / "home"), "CODEX_HOME": str(chome)}
    for cmd in (["codex", "plugin", "marketplace", "add", str(KC_ADR_ROOT)], ["codex", "plugin", "add", "kc-dev-flow-2@kc-claude-plugins"], ["codex", "plugin", "add", "kc-adr@kc-claude-plugins"]):
        p = subprocess.run(cmd, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if p.returncode != 0:
            raise SystemExit(f"{' '.join(cmd)} failed: {p.stderr[-500:]}")


def build_command(host, run_dir, prompt, schema, arm):
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
        if arm == "B1":
            argv[argv.index("--no-session-persistence"):argv.index("--no-session-persistence")] = ["--plugin-dir", str(KC_ADR_ROOT / "kc-adr")]
        env = {**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
    else:
        chome = run_dir / "codex-home"
        chome.mkdir()
        (chome / "auth.json").symlink_to(Path.home() / ".codex" / "auth.json")
        (chome / "config.toml").write_text("")
        (run_dir / "home").mkdir()
        if arm == "B1":
            install_codex_plugin(run_dir)
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
    if arm == "B1":
        plugin_identity()
    w = setup_workspace(run_dir, arm, host)
    prompt, schema = make_prompt(data, sc), make_schema(sc)
    argv, env, cwd = build_command(host, run_dir, prompt, schema, arm)
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
            "world": w, "plugin": plugin_identity() if arm == "B1" else None, "stderr_tail": stderr[-1500:], "answered": final is not None}
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
        argv, env, cwd = build_command(args.host, rd, make_prompt(data, scenarios[args.scenario]), make_schema(scenarios[args.scenario]), args.arm)
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
