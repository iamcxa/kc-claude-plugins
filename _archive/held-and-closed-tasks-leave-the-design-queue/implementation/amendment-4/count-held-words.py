#!/usr/bin/env python3
"""Measure the unchanged held-task formatter under Captain amendment 4.

Requires Python 3.11, PyYAML and Spacedock 0.27.2. --case is one, current or
larger. Current rows come from the native query; larger rows are explicitly
fabricated formatter inputs covering every configured workflow stage.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml

parser = argparse.ArgumentParser(description=__doc__)
for key in ("candidate", "state", "scratch", "output", "spacedock"):
    parser.add_argument("--" + key, type=Path, required=True)
parser.add_argument("--case", choices=("one", "current", "larger"), required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.candidate / "kc-dev-flow-2/scripts"))
import pr_watch
from decision_ledger import split_task, gate_entries

native = subprocess.run([str(args.spacedock), "status", "--workflow-dir", str(args.state.parent),
                        "--where", "gate-readiness=not-applicable", "--fields", "slug,status", "--json", "--limit", "0"],
                       capture_output=True, text=True, check=True)
data = json.loads(native.stdout)
rows = data["entities"]
assert data["pagination"]["has_next"] == "false" and int(data["pagination"]["total"]) == len(rows)
stages = yaml.safe_load(args.state.parent.joinpath("README.md").read_text().split("\n---\n", 1)[0].lstrip("-\n"))["stages"]["states"]
stages = [stage["name"] for stage in stages]
if args.case == "one":
    rows = sorted(rows, key=lambda row: row["slug"])[:1]
elif args.case == "larger":
    rows = [{"slug": f"fabricated-{stage}-{i:03d}", "status": stage} for stage in stages for i in range(20)]
    assert len(rows) > int(data["pagination"]["total"])
scratch = args.scratch / args.case
scratch.mkdir()
found = {}
for row in rows:
    slug = row["slug"]
    target = scratch / (slug + ".md")
    if args.case == "larger":
        target.write_text(f"---\ntitle: {slug}\nstatus: {row['status']}\n---\n"
                          "## Held\nClosed: fabricated formatter input\n"
                          "## Captain amendments\nCaptain: fabricated formatter input\n")
    else:
        source = args.state / (slug + ".md")
        if not source.exists():
            source = args.state / slug / "index.md"
        text = source.read_text()
        fm, _ = split_task(text)
        reasons = [r.get("reason", "") for r in gate_entries(fm) if r.get("decision") == "hold"]
        target.write_text(text + "\n## Held\nReopen when: " + reasons[-1].splitlines()[0] + "\n")
        assert split_task(target.read_text())[0] == fm
    found[slug] = target
lines = pr_watch.held_lines(rows, found)
assert len(lines) == 1 and lines[0].startswith("fact: held by the Captain, not waiting:")
line = lines[0] + "\n"
text_path = args.output / (args.case + "-fact.txt")
text_path.write_text(line)
wc = subprocess.run(["wc", "-w", str(text_path)], capture_output=True, text=True, check=True)
words = int(wc.stdout.split()[0])
assert words == len(line.split())
count = len(rows)
result = {"case": args.case, "held_tasks": count, "stages_present": sorted({r["status"] for r in rows}),
          "configured_stages": stages, "all_stages_present": set(r["status"] for r in rows) == set(stages),
          "measured_words": words, "maximum_words": count + 20, "passed": words <= count + 20,
          "measured_fixed_words": words - count - len({r["status"] for r in rows}),
          "bound_from_approved_asked": "每張擱置的任務最多多 1 個字，另加固定 20 個字",
          "captain_answer": "可以，照列名稱（建議）", "synthetic_rows": args.case == "larger",
          "fact_line": line.strip(), "wc_command": ["wc", "-w", str(text_path)], "wc_output": wc.stdout.strip(),
          "candidate": subprocess.check_output(["git", "-C", str(args.candidate), "rev-parse", "HEAD"], text=True).strip(),
          "formatter_sha256": hashlib.sha256((args.candidate / "kc-dev-flow-2/scripts/pr_watch.py").read_bytes()).hexdigest()}
(args.output / (args.case + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result["passed"] else 1)
