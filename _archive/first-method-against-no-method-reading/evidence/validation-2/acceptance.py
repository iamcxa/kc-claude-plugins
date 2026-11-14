#!/usr/bin/env python3
"""Reproduce the second reading locally without changing its repository or grades.

Run this file with Python 3. It prompts for the private repository, the blind
packet and its separate key. Optional positional arguments supply those paths.
Exit 1 is expected for this candidate: the blind grade disagreement is reproduced.
No network, credential, model run, or private output is written to the state tree.
"""
import argparse
import ast
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

CANDIDATE = "42ea38dcae91b045c116b60cba221d3883b1f8bf"
READING = "ad5755c8e9ad47f6f932029853d93851aa79ed99"
RECORD_SHA256 = "4c05f4729e16c910d7cf5d3e7b12dfd62e904fb670406470e0fddc79af2ba623"
CELL = "method-against-no-method-2"
BLIND = dict(A="FAIL", B="FAIL", C="FAIL", D="PASS", E="FAIL", F="PASS")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?")
    parser.add_argument("packet", nargs="?")
    parser.add_argument("key", nargs="?")
    parser.add_argument("--report", help="Write the sanitized JSON result here")
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
            ("table_rule", [str(source / "behaviour/table_rule_check.py")]),
        ):
            run = subprocess.run([sys.executable, "-B", *command], env=env, capture_output=True, text=True)
            checks[label] = run.returncode
            assert run.returncode == 0, label
        rows = []
        times = {}
        agents = {}
        for letter in sorted(BLIND):
            run = results / key[letter]
            manifest = module.load_json(run / "manifest.json")
            grade = module.grade_run(run, cell)
            events = list(module.events(module.stream_of(run)))
            first = min(datetime.fromisoformat(e["timestamp"]) for _, e in events if e.get("timestamp"))
            assert committed_at < first
            assert manifest["reading_commit"] == READING
            times[letter] = first.isoformat()
            agents[letter] = []
            for agent in module.started_agents(run):
                info = module.qualify(agent, run)
                child_events = list(module.events(agent["transcript"]))
                tools = [b.get("name") for _, e in child_events for b in module.tool_uses(e)]
                agents[letter].append(dict(joined_transcript=True, tools=tools,
                    qualified=info["ok"], stored_files=len(info["written"]), final_characters=len(info["final"])))
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
        first_path = "behaviour/results/method-against-no-method/table.md"
        first_original = git("show", "fe2a94c5fdd26b3328f29fa81f1f8d9cb6513fb5:" + first_path).decode()
        first_current = (source / first_path).read_text()
        def projection(text):
            projected, keep = [], []
            for line in text.splitlines():
                if line.startswith(("| arm |", "| run |")):
                    columns = [x.strip() for x in line.strip("|").split("|")]
                    added = {"blind k/n", "blind grade", "their tokens in / out / cache", "their minutes (summed)", "their tool calls"}
                    keep = [i for i, c in enumerate(columns) if c not in added]
                if line.startswith("|"):
                    cells = [x.strip() for x in line.strip("|").split("|")]
                    projected.append([cells[i] for i in keep])
            return projected
        assert projection(first_original) == projection(first_current)
        def unchanged_lines(text):
            lines = []
            for line in text.splitlines():
                if line.startswith("## Safety scans"):
                    break
                if line.strip() and not line.startswith(("|", "reading, blind", "verdict:")):
                    lines.append(line)
            return lines
        assert unchanged_lines(first_original) == unchanged_lines(first_current)
        assert first_original.split("## Safety scans", 1)[1].split("## Limits", 1)[0] == first_current.split("## Safety scans", 1)[1].split("## Limits", 1)[0]
        first_cell = module.load_cell(source / "behaviour/cells/method-against-no-method")
        assert module.build_table_v3(first_cell, source / "behaviour/results/method-against-no-method") == first_current
        def definitions(data):
            return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(data).body
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        before = definitions(git("show", READING + ":behaviour/run_cell.py"))
        after = definitions(script.read_bytes())
        changed = sorted(n for n in before.keys() | after.keys() if before.get(n) != after.get(n))
        assert changed == ["build_table_v3", "final_verdict"]
        assert not git("diff", "--name-only", READING, CANDIDATE, "--", "behaviour/cells/" + CELL).strip()
        mutant = work / "old-table-behaviour"
        mutant.mkdir()
        mutant_source = script.read_text().replace("if disagreements:\n", "if disagreements and blinded != every:\n", 1)
        (mutant / "run_cell.py").write_text(mutant_source)
        (mutant / "table_rule_check.py").write_bytes((source / "behaviour/table_rule_check.py").read_bytes())
        mutation = subprocess.run([sys.executable, "-B", str(mutant / "table_rule_check.py")],
                                  env=env, capture_output=True, text=True)
        assert mutation.returncode == 1
        disagreement = [r["packet"] for r in rows if r["blind"] != r["script"]]
        report = dict(candidate=CANDIDATE, record_unchanged=True, reading_precedes_every_run=True,
                      checks=checks, stored_table_byte_match=True, runs=rows,
                      reading_committed_at=committed_at.isoformat(), first_events=times, agents=agents,
                      blind_disagreements=disagreement,
                      blind_packet_coverage_complete=False,
                      hidden_files_first_read_after_unblinding=["C", "D"],
                      first_table_original_columns_unchanged=True, first_table_regenerated_byte_match=True,
                      second_reading_files_unchanged=True, post_reading_functions_changed=changed,
                      old_disagreement_mutation_exit=mutation.returncode,
                      script_with_blind=[line for line in table.splitlines() if line.startswith(("reading,", "verdict:"))],
                      committed_prose_result="cannot discriminate: blind grades disagree" if disagreement else "no blind disagreement")
        if args.report:
            Path(args.report).write_text(json.dumps(report, indent=2)+"\n")
        print(json.dumps(report, indent=2))
        return 1 if disagreement else 0


if __name__ == "__main__":
    sys.exit(main())
