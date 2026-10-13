# FO validation acceptance receipt

Recorded at 2026-10-13T11:14:07.505625+00:00

Candidate: `4f678cd88eddbcc171df7e2037dd19d2fbf4065b`.

This is a process receipt, not an edit to the independent stage report. The FO executed the committed four-step acceptance script unchanged in a fresh shell, exit 0. Product tree remained clean and test services stopped. All fixtures and grants were synthetic.

## Exact script

```bash
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
```

## Observed stdout

```text
STEP 1 — Confirm exact candidate and installed prerequisites
PASS candidate 4f678cd88 clean; v24.18.0; locked runtime dependencies present
STEP 2 — Exercise Node cookie isolation, recovery, revocation and expiry
PASS room isolation: cookie MCP/assets deny B reading or replacing A; same-ID bytes remain separate
PASS recovery: export includes latest associated bytes; populated/invalid restore refused; fresh restore survives restart
PASS revocation: a live cookie socket receives authorized edits, then loses read/write across all transports before close event
PASS expiry: parent deadline denies existing cookie HTTP/MCP/assets/socket admission and no live data reaches the expired socket
LOCAL ONLY: hosted deployment, provider hibernation, billing and licensing NOT RUN
Evidence: /Users/kent/Documents/Codex/2026-10-11/tldraw-tldraw-gpt-plugin/work/kc-jmap-host-pilot/.worktrees/spacedock-ensign-journey-server-host-pilot/kc-journey-map/.host-check/run-qFXFZU/validation-result.json
STEP 3 — Exercise Cloudflare-local with the same client contract
PASS room isolation: cookie MCP/assets deny B reading or replacing A; same-ID bytes remain separate
PASS recovery: export includes latest associated bytes; populated/invalid restore refused; fresh restore survives restart
PASS revocation: a live cookie socket receives authorized edits, then loses read/write across all transports before close event
PASS expiry: parent deadline denies existing cookie HTTP/MCP/assets/socket admission and no live data reaches the expired socket
LOCAL ONLY: hosted deployment, provider hibernation, billing and licensing NOT RUN
Evidence: /Users/kent/Documents/Codex/2026-10-11/tldraw-tldraw-gpt-plugin/work/kc-jmap-host-pilot/.worktrees/spacedock-ensign-journey-server-host-pilot/kc-journey-map/.host-check/run-SM0TbD/validation-result.json
STEP 4 — Confirm unchanged product and stopped validation servers
PASS product unchanged; no validation server/emulator remains
LOCAL ONLY: this is not deployment approval or hosted/provider evidence
```

## Gate assessment

Checklist accounting from the independent report: 10 DONE, 3 SKIPPED, 0 FAILED. The report's synchronization skip is historical: the FO verified the authenticated repository owner and inspected the synthetic-only payload, then recovered publication using `spacedock state commit journey-server-host-pilot` on the existing state branch, exit 0. No product branch was published.

Goal sufficiency: the same candidate's route evidence establishes the accepted shared core, Node local and Cloudflare-emulated private transports, unchanged document behavior and recoverable fresh storage. It does not establish hosted Node/Cloudflare access or actual provider hibernation in AC-1 and AC-4.

Minimal necessity: reviewed responsibilities in validation-review.md map to shared operations, private admission, platform lifecycle, associated asset persistence, explicit capability differences and recovery. No room-switching UI, changed concurrency rule, new rendering/schema contract, API-v1 or unrelated hosting integration is retained.

Full task-aware number guard remains SKIPPED/NOT PASS under the committed no-migration disposition; ADR reservation and actual no-SQL diff were independently checked.

Recommendation: hold full hosted delivery acceptance; preserve the clean local candidate and request a separately scoped hosted verification decision. This receipt authorizes no deployment, PR, merge or provisioning.
