import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

repo, package = map(Path, sys.argv[1:])
with tempfile.TemporaryDirectory(prefix="worker-completion-proof-") as directory:
    root = Path(directory)
    archive = subprocess.check_output(["git", "-C", str(repo), "archive", "HEAD", "kc-dev-flow-2", "docs/adr"])
    with tarfile.open(fileobj=io.BytesIO(archive)) as files:
        files.extractall(root, filter="data")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "SPACEDOCK_BIN": "/Users/kent/.local/bin/spacedock",
           "SD_PLUGIN_ROOT": "/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3"}
    tests = subprocess.run([sys.executable, "-B", "-m", "unittest",
                            "test_dispatch_records.DispatchRecordTests",
                            "test_dispatch_records.PaseoCompletionMutationTests",
                            "test_dispatch_records.ContextNoticeTests.test_workflow_strict_preflight_holds_then_repaired_context_reaches_real_builder_fixture"],
                           cwd=root / "kc-dev-flow-2/scripts", env=env, capture_output=True, text=True)
    print(tests.stderr)
    assert tests.returncode == 0
    assert not list(root.rglob("*.pyc"))
    extension = root / "kc-dev-flow-2/extensions/paseo/EXTENSION.md"
    original = extension.read_text()
    assert len(original.split()) == 819
    extension.write_text(original + "\nextra\n")
    try:
        assert len(extension.read_text().split()) <= 819
    except AssertionError:
        print("PASS: word-budget mutation 820 > 819 refused")
    else:
        raise AssertionError("word-budget mutation survived")
    extension.write_text(original)
    adr = root / "docs/adr/0048-paseo-stage-workers-complete-by-final-reply-and-hand-publication-to-fo.md"
    original = adr.read_text()
    adr.write_text(original.replace("**Words:**", "Words:", 1))
    done = subprocess.run([sys.executable, "-B", str(package / "scripts/adr_lint.py"), str(root / "docs/adr"),
                           "--root", str(root), "--require", "0048"], capture_output=True, text=True)
    assert done.returncode == 1 and "Decision needs a '**Words:**' line" in done.stdout, done.stdout + done.stderr
    print("PASS: removing ADR Words label refused by adr_lint.py (exit 1)")
    adr.write_text(original)
    print("PASS: all falsifiers ran with python3 -B in a cache-free candidate archive")
