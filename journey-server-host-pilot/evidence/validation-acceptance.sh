#!/usr/bin/env bash
set -euo pipefail
WT='/Users/kent/Documents/Codex/2026-10-11/tldraw-tldraw-gpt-plugin/work/kc-jmap-host-pilot/.worktrees/spacedock-ensign-journey-server-host-pilot'
TASK='/Users/kent/Documents/Codex/2026-10-11/tldraw-tldraw-gpt-plugin/work/kc-jmap-host-pilot/docs/dev2/.spacedock-state/journey-server-host-pilot'

echo 'STEP 1 — Confirm exact candidate and installed prerequisites'
rtk proxy python3 - "$WT" <<'PY'
import json, pathlib, shutil, subprocess, sys
w = pathlib.Path(sys.argv[1]); p = w / "kc-journey-map"
for tool in ("node", "git", "python3", "rtk"):
    assert shutil.which(tool), f"missing prerequisite: {tool}"
head = subprocess.check_output(["git", "-C", str(w), "rev-parse", "HEAD"], text=True).strip()
assert head == "4f678cd88eddbcc171df7e2037dd19d2fbf4065b", head
assert not subprocess.check_output(["git", "-C", str(w), "status", "--porcelain"], text=True).strip()
version = subprocess.check_output(["node", "--version"], text=True).strip()
assert tuple(map(int, version[1:].split(".")[:2])) >= (22, 13), version
lock = json.loads((p / "package-lock.json").read_text())
for name in ("@tldraw/sync-core", "tsx", "vite", "playwright", "ws", "esbuild", "miniflare"):
    actual = json.loads((p / "node_modules" / name / "package.json").read_text())["version"]
    assert actual == lock["packages"]["node_modules/" + name]["version"], name
print(f"PASS candidate {head[:9]} clean; {version}; locked runtime dependencies present")
PY

echo 'STEP 2 — Exercise Node cookie isolation, recovery, revocation and expiry'
rtk proxy python3 "$TASK/evidence/validation-probe.py" "$WT" node

echo 'STEP 3 — Exercise Cloudflare-local with the same client contract'
rtk proxy python3 "$TASK/evidence/validation-probe.py" "$WT" cloudflare-local

echo 'STEP 4 — Confirm unchanged product and stopped validation servers'
rtk proxy python3 - "$WT" <<'PY'
import pathlib, subprocess, sys
w = pathlib.Path(sys.argv[1])
assert subprocess.check_output(["git", "-C", str(w), "rev-parse", "HEAD"], text=True).strip() == "4f678cd88eddbcc171df7e2037dd19d2fbf4065b"
assert not subprocess.check_output(["git", "-C", str(w), "status", "--porcelain"], text=True).strip()
processes = subprocess.check_output(["ps", "-axo", "pid=,command="], text=True)
owned = [line for line in processes.splitlines() if str(w) in line and any(name in line for name in ("server/canvas-server.ts", ".host-check/validation-transport-probe.mjs", "/workerd"))]
assert not owned, "\n".join(owned)
print("PASS product unchanged; no validation server/emulator remains")
print("LOCAL ONLY: this is not deployment approval or hosted/provider evidence")
PY
