#!/usr/bin/env python3
"""Launch Claude Code with Conductor's stream-json flags, send one user message, then stay idle.

Every stdout line is appended to --out with a UTC timestamp; stdin gets no further user input.
Permission requests on the stdio prompt channel are allowed. Stops after --seconds.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ALLOW = {"behavior": "allow"}


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", required=True)
    p.add_argument("--wake", choices=["hook", "shell"], required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--model", default="haiku")
    p.add_argument("--claude", default=os.environ.get("CLAUDE_BIN", "claude"))
    p.add_argument("--cwd", default="/tmp")
    p.add_argument("--seconds", type=float, default=300)
    a = p.parse_args()

    cmd = [
        a.claude, "--output-format", "stream-json", "--verbose", "--input-format", "stream-json",
        "--thinking", "adaptive", "--thinking-display", "summarized", "--effort", "high",
        "--max-turns", "1000", "--model", a.model, "--permission-prompt-tool", "stdio",
        "--disallowedTools", "AskUserQuestion", "--setting-sources=user,project,local",
        "--permission-mode", "bypassPermissions", "--session-mirror",
        "--plugin-dir", os.path.join(HERE, "plugin"),
    ]
    env = dict(os.environ, AGENT_BOARD_DB=a.db, AGENT_BOARD_WAKE=a.wake)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=open(a.out + ".stderr", "a"), text=True, cwd=a.cwd, env=env)
    out = open(a.out, "a", buffering=1)
    send_lock = threading.Lock()

    def send(obj):
        with send_lock:
            proc.stdin.write(json.dumps(obj) + "\n")
            proc.stdin.flush()

    def pump():
        for line in proc.stdout:
            out.write(f"{stamp()}\t{line}")
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            if msg.get("type") == "control_request" and msg["request"].get("subtype") == "can_use_tool":
                send({"type": "control_response", "response": {
                    "subtype": "success", "request_id": msg["request_id"],
                    "response": dict(ALLOW, updatedInput=msg["request"].get("input", {}))}})

    t = threading.Thread(target=pump, daemon=True)
    t.start()
    signal.signal(signal.SIGTERM, lambda *_: (proc.terminate(), sys.exit(0)))
    out.write(f"{stamp()}\tREPLICA sent user message: {json.dumps(a.prompt)}\n")
    send({"type": "user", "message": {"role": "user", "content": a.prompt}})
    time.sleep(a.seconds)
    out.write(f"{stamp()}\tREPLICA stopping after {a.seconds}s\n")
    proc.terminate()
    proc.wait(timeout=20)
    return 0


if __name__ == "__main__":
    sys.exit(main())
