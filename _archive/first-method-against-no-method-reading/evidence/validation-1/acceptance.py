#!/usr/bin/env python3
"""Reproduce the first reading locally without changing its repository or grades.

Run this file with Python 3. It prompts for the private repository, the blind
packet and its separate key. Optional positional arguments supply those paths.
Exit 1 is expected for this candidate: the blind grade disagreement is reproduced.
No network, credential, model run, or private output is written to the state tree.
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime

CANDIDATE = "fe2a94c5fdd26b3328f29fa81f1f8d9cb6513fb5"
READING = "a63e6634ae033748c112b44be6c69b8e09da4a6b"
RECORD_SHA256 = "8b29c484b1bf14addb54603cb1af43bd1a79575342f8750f7ede0191bec9d940"
CELL = "method-against-no-method"
BLIND = dict(A="FAIL", B="FAIL", C="FAIL", D="FAIL", E="PASS", F="FAIL")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?")
    parser.add_argument("packet", nargs="?")
    parser.add_argument("key", nargs="?")
    parser.add_argument("--scratch", help="Parent directory for temporary files")
    args = parser.parse_args()
    repo = Path(args.repository or input("Private repository path: ")).expanduser().resolve()
    packet = Path(args.packet or input("Blind packet directory: ")).expanduser().resolve()
    key = json.loads(Path(args.key or input("Separate blind key file: ")).expanduser().read_text())
    assert hashlib.sha256((packet / "RECORD.md").read_bytes()).hexdigest() == RECORD_SHA256
    git = lambda *a: subprocess.check_output(["git", "-C", str(repo), *a])
    subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", READING, CANDIDATE], check=True)
    committed_at = datetime.fromisoformat(git("show", "-s", "--format=%cI", READING).decode().strip())
    with tempfile.TemporaryDirectory(dir=args.scratch) as temporary:
        work = Path(temporary)
        source = work / "source"
        source.mkdir()
        with tarfile.open(fileobj=io.BytesIO(git("archive", CANDIDATE, "behaviour"))) as archive:
            archive.extractall(source, filter="data")
        script = source / "behaviour/run_cell.py"
        spec = importlib.util.spec_from_file_location("reading_candidate", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cell = module.load_cell(source / "behaviour/cells" / CELL)
        results = source / "behaviour/results" / CELL
        checks = {}
        env = dict(os.environ, TMPDIR=str(work), PYTHONDONTWRITEBYTECODE="1")
        for label, command in (
            ("selfcheck", [str(script), "selfcheck", str(cell["dir"])]),
            ("mutation_proof", [str(source / "behaviour/mutation_proof.py"), str(cell["dir"])]),
        ):
            run = subprocess.run([sys.executable, "-B", *command], env=env, capture_output=True, text=True)
            checks[label] = run.returncode
            assert run.returncode == 0, label
        rows = []
        for letter in sorted(BLIND):
            run = results / key[letter]
            manifest = module.load_json(run / "manifest.json")
            grade = module.grade_run(run, cell)
            events = list(module.events(module.stream_of(run)))
            first = min(datetime.fromisoformat(e["timestamp"]) for _, e in events if e.get("timestamp"))
            assert committed_at < first
            scan = module.scan_run(run)
            calls = [b for _, e in events for b in module.tool_uses(e) if b.get("name") in ("Agent", "Task")]
            children = [p for p in module.subagent_streams(run) if "subagents" in p.parts]
            assert len(calls) == len(children)
            rows.append(dict(packet=letter, arm=manifest["arm"], blind=BLIND[letter], script=grade["verdict"],
                             extra_agents=len(children), contaminated=bool(scan["breaches"]),
                             unscanned=scan["unscanned"], secret_touches=len(scan["secrets"])))
        for name, include_blind in (("original", False), ("with-blind", True)):
            view = work / name
            view.mkdir()
            for run in module.run_dirs(results):
                (view / run.name).symlink_to(run, target_is_directory=True)
            for filename in ("safety-scans.md", "limits-applied.md"):
                (view / filename).write_bytes((results / filename).read_bytes())
            if include_blind:
                (view / "blind.json").write_text(json.dumps({key[k]: v for k, v in BLIND.items()}))
            done = subprocess.run([sys.executable, "-B", str(script), "table", str(cell["dir"]), "--results", str(view)],
                                  env=env, capture_output=True, text=True)
            assert done.returncode == 0
            if not include_blind:
                assert (view / "table.md").read_bytes() == (results / "table.md").read_bytes()
        table = (work / "with-blind/table.md").read_text()
        disagreement = [r["packet"] for r in rows if r["blind"] != r["script"]]
        report = dict(candidate=CANDIDATE, record_unchanged=True, reading_precedes_every_run=True,
                      checks=checks, stored_table_byte_match=True, runs=rows,
                      blind_disagreements=disagreement,
                      script_with_blind=[line for line in table.splitlines() if line.startswith(("reading,", "verdict:"))],
                      committed_prose_result="cannot discriminate: blind grades disagree" if disagreement else "no blind disagreement")
        print(json.dumps(report, indent=2))
        return 1 if disagreement else 0


if __name__ == "__main__":
    sys.exit(main())
