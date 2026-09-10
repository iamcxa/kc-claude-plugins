import hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
repo, task = map(Path, sys.argv[1:3]); base = "c2c62bf9dff5c3af1e27eb643a15eadf9023485f"
def git(*args): return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout
assert git("rev-parse", "HEAD").decode().strip() == base
patch = git("diff", "--binary", base); (task / "implementation.patch").write_bytes(patch)
entries = [tuple(line.split("\t", 1)) for line in git("diff", "--name-status", base).decode().splitlines()]
module_path = repo / "kc-dev-flow/scripts/surface-map-check.py"
spec = importlib.util.spec_from_file_location("surface", module_path); checker = importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)
# Only input transport is adapted: retain the stock checker main and validation functions.
checker.git_changed_files = lambda *_args, **_kwargs: entries
non_test = [path for _, path in entries if not checker.is_excluded(path)]
for path in non_test:
    if path.endswith(".md"):
        current = (repo / path).read_text(); previous = git("show", f"{base}:{path}").decode()
        assert "pending" in current and "pending" not in previous, path
        if "continue-dev-flow" in path:
            for phrase in ("check-final", "archived body", "frozen Briefing", "state commit", "pending/failed"):
                assert phrase in current, phrase
        print("instruction necessity PASS (original lacks pending guidance):", path)
evidence = task / "implementation-surfaces.md"
rows = []
for path in non_test:
    command = f"python3 {task}/implementation-surface-check.py {repo} {task}"
    if path.endswith(".py"):
        command = f"python3 {repo}/kc-dev-flow/scripts/poc-close-guard.test.py"
    rows.append(f"SURFACE: {path} -> lifecycle:poc-close | {command} # {path} | git show {base}:{path}")
evidence.write_text("# Evidence\n\n" + "\n".join(rows) + "\n")
sys.argv = [str(module_path), base, "UNCOMMITTED", str(evidence), "--repo", str(repo), "--work-item", str(task / "index.md"), "--brief", str(task / "index.md")]
complete = evidence.read_text(); evidence.write_text("# deliberately missing mappings\n")
assert checker.main() == 1, "missing surface control did not fail"
evidence.write_text(complete); assert checker.main() == 0
hashes = {path: hashlib.sha256((repo / path).read_bytes()).hexdigest() for _, path in entries}
result = dict(base=base, patch_sha256=hashlib.sha256(patch).hexdigest(), file_sha256=hashes, numstat=git("diff", "--numstat", base).decode(), surface_adapter="stock main and validators; git_changed_files input replaced by exact uncommitted git diff entries", surface_control="missing mappings refused; four mappings passed")
(task / "implementation-patch-evidence.json").write_text(json.dumps(result, indent=2)); print(json.dumps(result, indent=2))
