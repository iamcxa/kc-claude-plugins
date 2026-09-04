#!/usr/bin/env python3
"""Forge Phase 2 clean runner — the one interface Phase 2 calls for every RED/GREEN run.

Usage: skill-runner.py <cloud|bare> <scenario-file> <scenario-id> <red|green> <plugin-dir>
Prints: outcome=<pass|fail|error> runner=<cloud|bare> model=<pin> scratch=<dir>
See reference/skill-scenarios.md for the scenario format and refusals enforced before any API call.
"""
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_MODEL = "sonnet-4-6"  # the pin this runner falls back to when a scenario carries none
DEFAULT_EFFORT = "low"
TOKEN_BUDGET_S = 480
POLL_INTERVAL_S = 15
ABS_SCRATCH_LITERAL = re.compile(r"/tmp/(?!\{SCRATCH\})\S|/var/folders/\S")


def outcome_line(status, runner, model, scratch):
    print(f"outcome={status} runner={runner} model={model or 'unpinned'} scratch={scratch}")


def die(status, runner, model, scratch, reason):
    outcome_line(status, runner, model, scratch)
    print(f"reason={reason}", file=sys.stderr)
    sys.exit(2 if status == "error" else 1)


def load_yaml(path):
    try:
        import yaml
    except ImportError:
        die("error", "n/a", "n/a", "n/a",
            "missing machine dependency: PyYAML (pip install pyyaml)")
    if not Path(path).exists():
        die("error", "n/a", "n/a", "n/a", f"scenario file not found: {path}")
    return yaml.safe_load(Path(path).read_text())


def validate_scenario(data, scen, path):
    for key in ("adversarial", "setup"):
        if key not in scen:
            die("error", "n/a", "n/a", "n/a",
                f"scenario {scen.get('id')} missing required key '{key}:' in {path}")
    has_assert, has_judge = "assert" in scen, "judge" in scen
    if has_assert == has_judge:
        die("error", "n/a", "n/a", "n/a",
            f"scenario {scen.get('id')} must carry exactly one of assert:/judge: in {path}")
    blob = (scen.get("setup") or "") + "\n" + (scen.get("prompt") or "")
    if ABS_SCRATCH_LITERAL.search(blob):
        die("error", "n/a", "n/a", "n/a",
            f"scenario {scen.get('id')} carries a literal absolute scratch path "
            f"(/tmp/... or /var/folders/...) — use {{SCRATCH}} in {path}")


def resolve_model(data, scen):
    model = scen.get("model") or data.get("model") or DEFAULT_MODEL
    if not model:
        die("error", "n/a", "n/a", "n/a",
            "no model pin resolved — scenario, file, and default constant are all empty")
    return model


def bare_model_id(pin):
    """claude --bare wants a full model id; Conductor session --model wants the
    bare pin. Observed 2026-09-03, not re-verified since (residual 3)."""
    return pin if pin.startswith("claude-") else f"claude-{pin}"


def assertion_paths(scen):
    cated = []
    for a in scen.get("assert", []):
        (k, v), = a.items()
        if k == "file_matches":
            cated.append(v["path"])
        elif k == "frontmatter_field":
            cated.append(v["path"])
    return cated


def build_epilogue(cated, token):
    # First give the normal spoken answer the prompt above asked for — an
    # epilogue phrased as "your final action" was observed to make the model
    # treat the epilogue itself as the whole final turn, emitting nothing but
    # the token and leaving output_contains with no text to match against.
    lines = ["", "First give your normal answer to the prompt above, in your own words, "
                 "exactly as it asked. Only after that, as an additional last step, "
                 "also run this and show its output:"]
    for p in cated:
        lines.append(f'echo "===FORGE-FILE-START {p}==="; cat "{p}" 2>/dev/null; echo "===FORGE-FILE-END {p}==="')
    lines.append(f"Then, in that same final message, restate your answer to the prompt above in one "
                 f"sentence and print exactly: TOKEN: {token}")
    return "\n".join(lines)


def substitute(text, scratch, skill_path):
    return text.replace("{SCRATCH}", scratch).replace("{SKILL_PATH}", skill_path)


def build_prompt(data, scen, variant, scratch, token):
    setup = substitute(scen["setup"], scratch, data.get("skill_path", ""))
    body = substitute(scen["prompt"], scratch, data.get("skill_path", ""))
    cated = [substitute(p, scratch, "") for p in assertion_paths(scen)]
    epilogue = build_epilogue(cated, token)
    parts = [setup, body] if setup else [body]
    if variant == "green":
        preamble = substitute(data.get("green_preamble", ""), scratch, data.get("skill_path", ""))
        parts = [preamble] + parts
    parts.append(epilogue)
    return "\n\n".join(p for p in parts if p)


def extract(messages):
    """-> (file_bodies, terminal_result). Reads the epilogue's FORGE-FILE
    markers from tool_use_result stdout, and the terminal result only from
    the subtype:success payload — output_contains must never see the
    epilogue's own cat, or it would satisfy itself trivially."""
    bodies, result = {}, None
    file_re = re.compile(r"===FORGE-FILE-START (\S+)===\n(.*?)\n===FORGE-FILE-END \1===", re.S)
    for m in messages:
        rp = (m.get("content") or {}).get("rawPayload") or m  # cloud vs bare-stream shape
        tur = rp.get("tool_use_result")
        stdout = tur.get("stdout", "") if isinstance(tur, dict) else ""
        if not stdout and isinstance(tur, str):
            stdout = tur
        for path, body in file_re.findall(stdout):
            bodies[path] = body
        if rp.get("subtype") == "success" or rp.get("type") == "result":
            result = rp.get("result") or result
    return bodies, result


def score(scen, bodies, result, remote_scratch):
    """bodies is keyed by the real remote-substituted path (what the epilogue
    actually printed); scen['assert'] values still carry the raw {SCRATCH}
    template, so every path lookup here canonicalizes first."""
    out = []
    if "judge" in scen:
        return "judged", []
    for a in scen["assert"]:
        (k, v), = a.items()
        if k == "file_matches":
            path = substitute(v["path"], remote_scratch, "")
            ok = bool(re.search(v["pattern"], bodies.get(path, "")))
        elif k == "frontmatter_field":
            path = substitute(v["path"], remote_scratch, "")
            body = bodies.get(path, "")
            m = re.match(r"---\n(.*?)\n---", body, re.S)
            ok = bool(m) and re.search(rf"^{v['field']}:\s*{v['equals']}\s*$", m.group(1), re.M) is not None
        elif k == "output_contains":
            ok = v in (result or "")
        elif k == "output_not_contains":
            ok = v not in (result or "")
        else:
            die("error", "n/a", "n/a", "n/a", f"unknown assertion type '{k}'")
        out.append((k, ok))
    return ("pass" if all(ok for _, ok in out) else "fail"), out


def run_bare(prompt, model, plugin_dir, scratch, transcript_path):
    key_ready = os.environ.get("ANTHROPIC_API_KEY")
    forge_config = Path.home() / ".claude/kc-plugins-config/forge.yaml"
    if not key_ready and forge_config.exists():
        for line in forge_config.read_text().splitlines():
            if line.startswith("api_key_file:"):
                key_file = Path(line.split(":", 1)[1].strip())
                if key_file.exists():
                    for kline in key_file.read_text().splitlines():
                        if "ANTHROPIC_API_KEY" in kline and "=" in kline:
                            os.environ["ANTHROPIC_API_KEY"] = kline.split("=", 1)[1].strip().strip('"\'')
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None, None, "ANTHROPIC_API_KEY not found (env or forge.yaml api_key_file)"
    script = HERE / "clean-profile-test.sh"
    env = dict(os.environ, SKILL_RUNNER_MODEL=bare_model_id(model), SKILL_RUNNER_STREAM_JSON=str(transcript_path))
    proc = subprocess.run(["bash", str(script), plugin_dir, prompt, "300"], env=env, capture_output=True, text=True)
    if proc.returncode == 2 or not transcript_path.exists():
        return None, None, f"clean-profile-test.sh execution error: {proc.stdout.strip() or proc.stderr.strip()}"
    messages = [json.loads(l) for l in transcript_path.read_text().splitlines() if l.strip()]
    return messages, None, None


def resolve_project_id(plugin_dir):
    try:
        remote = subprocess.check_output(["git", "-C", plugin_dir, "remote", "get-url", "origin"],
                                          text=True, stderr=subprocess.DEVNULL).strip()
        projects = json.loads(subprocess.check_output(["conductor", "project", "list", "--json"]))
    except Exception as e:
        return None, f"could not resolve git remote or conductor project list: {e}"
    norm = remote.rstrip("/").removesuffix(".git")
    for p in projects.get("data", []):
        if p.get("gitRemote") and p["gitRemote"].rstrip("/").removesuffix(".git") == norm:
            return p["id"], None
    return None, f"no Conductor project matches remote {remote}"


def reconcile_workspace(project_id, model):
    """One workspace per Phase2 invocation; concurrent callers race on an
    O_CREAT|O_EXCL lock file. Every path — lock winner, lock loser, and fast-
    path reuse — waits for status == ready before returning (residual 1)."""
    state = Path(tempfile.gettempdir()) / f"forge-cloud-ws-{hashlib.sha256(project_id.encode()).hexdigest()[:12]}.json"
    ws_id = None
    for _ in range(40):
        try:
            fd = os.open(state, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            try:
                data = json.loads(state.read_text() or "{}")
                if data.get("workspaceId"):
                    ws_id = data["workspaceId"]
                    break
            except Exception:
                pass
            time.sleep(3)
    else:
        return None, "timed out waiting for a peer to finish creating the shared workspace"
    if ws_id is None and state.stat().st_size > 0:
        ws_id = json.loads(state.read_text())["workspaceId"]
    if ws_id is None:
        hello = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        hello.write("Hello. Reply with the single word READY and nothing else.\n")
        hello.close()
        try:
            out = json.loads(subprocess.check_output([
                "conductor", "workspace", "create", "--project-id", project_id, "--branch", "main",
                "--name", f"forge-phase2-{secrets.token_hex(3)}", "--agent", "claude", "--model", model,
                "--effort", DEFAULT_EFFORT, "--message-file", hello.name, "--json"]))
        except subprocess.CalledProcessError as e:
            return None, f"conductor workspace create failed: {e}"
        ws_id = out.get("workspaceId") or out.get("id")
        state.write_text(json.dumps({"workspaceId": ws_id}))
    for _ in range(40):
        st = json.loads(subprocess.run(["conductor", "workspace", "status", ws_id, "--json"],
                                        capture_output=True, text=True).stdout or "{}")
        if st.get("status") == "ready":
            break
        time.sleep(10)
    return ws_id, None


def run_cloud(prompt, model, plugin_dir, scratch, transcript_path, scenario_id, variant):
    if not os.environ.get("CONDUCTOR_API_KEY"):
        return None, "cloud", "CONDUCTOR_API_KEY not set"
    project_id, reason = resolve_project_id(plugin_dir)
    if not project_id:
        return None, "cloud", reason
    ws_id, reason = reconcile_workspace(project_id, model)
    if not ws_id:
        return None, "cloud", reason
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(prompt)
        prompt_file = f.name
    try:
        sess = json.loads(subprocess.check_output([
            "conductor", "session", "create", "--workspace", ws_id, "--agent", "claude",
            "--model", model, "--effort", DEFAULT_EFFORT, "--name", f"{scenario_id}-{variant}",
            "--message-file", prompt_file, "--json"]))
    except subprocess.CalledProcessError as e:
        return None, "cloud", f"conductor session create failed: {e}"
    sid = sess.get("sessionId") or sess.get("id")
    return sid, "cloud", None


def page_until_token(sid, token, budget_s):
    """Pages --offset/--limit (never the sql transcript view, which elides
    the middle of a run) until TOKEN appears or the budget expires.
    -> (messages, acked, stall_reason). idle counts as a stall only once at
    least one agent-originated message has been seen — residual 1: a session
    still waking from `sleeping` reports idle before its first turn."""
    messages, offset, deadline, agent_seen = [], 0, time.time() + budget_s, 0
    while time.time() < deadline:
        page = json.loads(subprocess.run(
            ["conductor", "session", "message", sid, "--offset", str(offset), "--limit", "10", "--json"],
            capture_output=True, text=True).stdout or "{}")
        batch = page.get("data") or []
        messages.extend(batch)
        offset += len(batch)
        # The token also appears in the prompt we sent (the instruction that asks
        # for it back) — search only agent-originated events, or the first page
        # (which always carries our own userMessage) matches before any run happens.
        agent_batch = [m for m in batch if m.get("type") != "userMessage"]
        agent_seen += len(agent_batch)
        if f"TOKEN: {token}" in json.dumps(agent_batch):
            return messages, True, None
        if not page.get("hasMore"):
            status = json.loads(subprocess.run(["conductor", "session", "status", sid, "--json"],
                                                capture_output=True, text=True).stdout or "{}")
            if status.get("status") == "idle" and agent_seen > 0:
                _, result = extract(messages)
                return messages, False, f"session went idle without printing the token; last result: {result!r}"
            time.sleep(POLL_INTERVAL_S)
    return messages, False, f"token not observed within {budget_s}s"


def main():
    if len(sys.argv) != 6:
        die("error", "n/a", "n/a", "n/a", "usage: skill-runner.py <cloud|bare> <scenario-file> <scenario-id> <red|green> <plugin-dir>")
    runner_req, scenario_file, scenario_id, variant, plugin_dir = sys.argv[1:]
    if runner_req not in ("cloud", "bare") or variant not in ("red", "green"):
        die("error", "n/a", "n/a", "n/a", "runner must be cloud|bare, variant must be red|green")

    data = load_yaml(scenario_file)
    scen = next((s for s in data.get("scenarios", []) if s.get("id") == scenario_id), None)
    if scen is None:
        die("error", "n/a", "n/a", "n/a", f"scenario {scenario_id} not found in {scenario_file}")
    validate_scenario(data, scen, scenario_file)
    model = resolve_model(data, scen)

    host_scratch = tempfile.mkdtemp(prefix="forge-host-")
    remote_scratch = f"/tmp/forge-{secrets.token_hex(4)}"
    token = f"FORGE{secrets.token_hex(4)}"
    prompt = build_prompt(data, scen, variant, remote_scratch, token)
    transcript_path = Path(host_scratch) / f"{scenario_id}-{variant}.json"

    runner_used = runner_req
    messages, sid, reason = None, None, None
    if runner_req == "cloud":
        sid, runner_used, reason = run_cloud(prompt, model, plugin_dir, remote_scratch, transcript_path, scenario_id, variant)
        if sid:
            messages, acked, stall_reason = page_until_token(sid, token, TOKEN_BUDGET_S)
            transcript_path.write_text(json.dumps(messages, indent=2))
            if not acked:
                die("error", "cloud", model, host_scratch, stall_reason)
        else:
            runner_used = f'bare (cloud unavailable: {reason})'
            runner_req = "bare"
    if runner_req == "bare":
        messages, _, reason = run_bare(prompt, model, plugin_dir, remote_scratch, transcript_path)
        if messages is None:
            die("error", runner_used, model, host_scratch, reason or "bare execution failed")
        transcript_path.write_text(json.dumps(messages, indent=2))  # normalize stream-jsonl -> one JSON array

    bodies, result = extract(messages)
    status, detail = score(scen, bodies, result, remote_scratch)
    outcome_line(status, runner_used, model, host_scratch)
    sys.exit(0 if status in ("pass", "judged") else 1)


if __name__ == "__main__":
    main()
