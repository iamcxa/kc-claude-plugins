import json
import os
from pathlib import Path
import subprocess
import sys

root, out = map(Path, sys.argv[1:])
checks = [(f"extension-{name}", [sys.executable, "-B", f"kc-dev-flow-2/extensions/{name}/{test}"])
          for name, test in [("codex", "test_codex_review.py"), ("roborev", "test_roborev_gate.py"),
                             ("copilot", "test_copilot_review.py"), ("journey-map", "test_map_footprint.py"),
                             ("release-acceptance", "test_release_acceptance.py")]]
checks += [
    ("sd-dispatch", [sys.executable, "-B", "kc-dev-flow-2/scripts/test_sd_dispatch.py", "--sd-plugin-root",
                     "/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3"]),
    ("observer-recovery", [sys.executable, "-B", "kc-dev-flow-2/scripts/test_observer_recovery.py"]),
    ("version-parity", ["bash", "scripts/version-parity-check.sh"]),
]
results = []
env = dict(os.environ, TMPDIR="/tmp", SPACEDOCK_BIN="/Users/kent/.local/bin/spacedock", PYTHONDONTWRITEBYTECODE="1")
for name, command in checks:
    log = out / (name + ".log")
    with log.open("w") as stream:
        run_env = dict(env, GIT_DIR=subprocess.check_output(["git", "-C", "/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-gate-ignores-url-paths-and-data-fences", "rev-parse", "--absolute-git-dir"], text=True).strip(), GIT_WORK_TREE=str(root)) if name == "version-parity" else env
        result = subprocess.run(command, cwd=root, env=run_env, stdout=stream, stderr=subprocess.STDOUT)
    results.append(dict(name=name, status="passed" if result.returncode == 0 else "failed", exit=result.returncode,
                        command=command, log=str(log)))
    (out / "extra-checks.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"{name}: exit {result.returncode}", flush=True)
raise SystemExit(any(result["exit"] for result in results))
