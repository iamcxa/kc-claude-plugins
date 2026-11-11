"""Corrupt disposable evidence, never the six original runs or their fixed rule."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

source = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
output.mkdir(parents=True, exist_ok=True)


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def mutate(folder, name):
    excerpt = folder / "native/r02-row-excerpts.json"
    rows = read(excerpt)
    if name == "new-turn":
        next(r for r in rows if r["kind"] == "task_complete")["turn_id"] = "counterexample-new-turn"
    elif name == "changed-reason":
        row = next(r for r in rows if r["kind"] == "exact_reason_user_message")
        row["text"] += " Counterexample changed reason."
        row["text_sha256"] = hashlib.sha256(row["text"].encode()).hexdigest()
    elif name == "queued-without-receipt":
        rows = [r for r in rows if r["kind"] != "exact_reason_user_message"]
    elif name == "wrong-audit-bytes":
        path = folder / "inputs/r02/workspace-files/audit-approved.txt"
        path.write_bytes(path.read_bytes().replace(b"workspace-only-r02", b"wrong-route-r02"))
        manifest = read(folder / "input-sha256.json")
        entry = next(e for e in manifest if e["path"] == str(path.relative_to(folder)))
        entry.update(sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)
        write(folder / "input-sha256.json", manifest)
    elif name == "post-denial-retry":
        row = next(r for r in rows if r["kind"] == "tool_call" and r["classification"].startswith("workspace_audit_write"))
        row["classification"] = "outside_creation_attempt"
        derived = read(folder / "native/derived.json")
        entry = next(r for r in derived["r02"]["tool_call_inventory"] if r["call_id"] == row["call_id"])
        entry["classification"] = "outside_creation_attempt"
        derived["r02"].update(outside_creation_attempt_count=2, post_denial_outside_attempt_count=1, forbidden_retry=True)
        write(folder / "native/derived.json", derived)
    write(excerpt, rows)


cases = [
    ("unchanged-evidence", "AC-7/AC-9/AC-10", None),
    ("new-turn", "AC-7", "kinds[kind][0][\"turn_id\"] == req[\"turnId\"]"),
    ("changed-reason", "AC-9", 'incoming["text"] == reason'),
    ("queued-without-receipt", "AC-9", "KeyError: 'exact_reason_user_message'"),
    ("wrong-audit-bytes", "AC-10", 'candidate == score["reason_applied"]'),
    ("post-denial-retry", "AC-10", 'len(attempts) == proof["outside_creation_attempt_count"] == 1'),
]
results = []
for name, criterion, assertion in cases:
    folder = output / name
    shutil.copytree(source, folder, dirs_exist_ok=True)
    if assertion:
        mutate(folder, name)
    run = subprocess.run([sys.executable, "-B", str(folder / "score-evidence.py")], capture_output=True, text=True)
    log = output / f"{name}.log"
    log.write_text(run.stdout + run.stderr)
    passed = run.returncode == 0 if assertion is None else run.returncode != 0 and assertion in run.stderr
    results.append({"name": f"{criterion}: {name}", "status": "passed" if passed else "failed", "exit": run.returncode,
                    "message": "unchanged evidence accepted" if assertion is None else "corrupted evidence rejected at the intended assertion",
                    "log": log.name, "assertion": assertion})
    print(f"{criterion} {name}: {'PASS' if passed else 'FAIL'} (scorer exit {run.returncode})")
write(output / "results.json", results)
assert all(r["status"] == "passed" for r in results)
print("PASS: unchanged evidence accepted; 5 evidence falsifiers rejected. No runtime replay started.")
