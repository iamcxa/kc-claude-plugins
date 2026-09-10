import hashlib, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path
repo, task, source, sd = map(Path, sys.argv[1:5])
ns = {"__file__": str(repo / "kc-dev-flow/scripts/poc-close-guard.test.py")}
exec(Path(ns["__file__"]).read_text().split('with tempfile.TemporaryDirectory(prefix="poc-close-guard-") as temporary:')[0], ns)
root = Path(tempfile.mkdtemp(prefix="poc-real-snapshot-"))
original = source.read_bytes(); digest = hashlib.sha256(original).hexdigest()
(root / "original-snapshot.md").write_bytes(original)
ns["native_regressions"](root, sd)
body = original.decode()
a = body.index("## POC close measurement"); b = body.index("\n## ", a + 3)
body = body[:b] + "\n```yaml\npoc_close_measurement:\n  captain_wait_seconds: pending\n  terminal_cleanup_seconds: pending\n  cleanup_status: pending\n```\n" + body[b:]
# Retain the complete original above; remove native identity/checkout bindings only in the synthetic copy.
front, rest = body[4:].split("\n---\n", 1)
front = re.sub(r"^gates:.*?(?=^started:)", "", front, flags=re.MULTILINE | re.DOTALL)
front = re.sub(r"^worktree:.*\n?", "", front, flags=re.MULTILINE)
body = "---\n" + front + "\n---\n" + rest
fixture = root / "pending-snapshot.md"; fixture.write_text(body)
base = subprocess.run(["git", "-C", str(repo), "show", "c2c62bf9:kc-dev-flow/scripts/poc-close-guard.py"], text=True, capture_output=True, check=True).stdout
baseline = {"__file__": str(repo / "kc-dev-flow/scripts/poc-close-guard.py"), "__name__": "baseline"}; exec(compile(base, baseline["__file__"], "exec"), baseline)
try:
    baseline["validate"](fixture, "review")
    raise AssertionError("original guard unexpectedly accepted pending real snapshot")
except baseline["CloseError"] as error:
    original_failure = str(error)
assert "non-negative integer" in original_failure, original_failure
probe = root / "real"
(probe / "repo/docs/dev/evidence-attempt-2").mkdir(parents=True)
for name in ("cloud-final.md", "cloud-events.json", "sha256.json"):
    shutil.copyfile(source.parent / "evidence-attempt-2" / name, probe / "repo/docs/dev/evidence-attempt-2" / name)
result = ns["lifecycle_regressions"](probe, sd, body=body)
assert source.read_bytes() == original
result.update(original_sha256=digest, original_path=str(source), original_failure=original_failure, preserved_snapshot=str(root / "original-snapshot.md"), fixture=str(fixture), normalization="test-only native ID/gate/worktree bindings removed; full body retained plus pending measurement YAML", cloud_runs=0, cloud_case_coverage="owner-reported only, not independently rerun")
(task / "implementation-native-evidence.json").write_text(json.dumps(result, indent=2))
print(json.dumps({k:v for k,v in result.items() if k != "commands"}, indent=2))
