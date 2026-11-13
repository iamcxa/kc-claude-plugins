#!/usr/bin/env python3
"""Measure the changed FO reading surface; retain unchanged text as a common term."""
import json
from pathlib import Path
import subprocess
import sys

code = Path(sys.argv[1])
evidence = Path(__file__).parent
rows = json.loads((evidence / "fixtures.json").read_text())["cases"]
moments = []
for prefix, label in [("absent/", "no learn"), ("inline/", "learn")]:
    for report in ["present", "missing"]:
        item = next(r for r in rows if r["case"] == prefix + report)
        moments.append({"moment": f"after archive: {label}, report {report}",
                        "base": item["base_words"], "probe": item["probe_words"],
                        "delta": item["probe_words"] - item["base_words"]})
paths = ["kc-dev-flow-2/references/sd/workflow.md", "kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md",
         "kc-dev-flow-2/extensions/learn/EXTENSION.md"]
for path in paths:
    before = subprocess.run(["git", "-C", str(code), "show",
                             "c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694:" + path],
                            capture_output=True, check=True).stdout
    assert before == (code / path).read_bytes()
for moment in ["startup", "idle on open PR", "merge ask"]:
    moments.append({"moment": moment, "common_passages": "byte-identical", "delta": 0})
# The merged-PR path retains its three existing lines and makes the README argument explicit.
before = ["next: let pr-merge record example.",
          "after pr-merge: run `python3 /package/scripts/observer_check.py /state example`.",
          "after pr-merge: do each next: line it prints."]
after = [before[0], before[1].replace("example`", "example --readme /workflow/README.md`"), before[2]]
assert "--readme" in (code / "kc-dev-flow-2/scripts/pr_watch.py").read_text()
moments.append({"moment": "idle on merged PR with report before archive", "common_passages": "byte-identical",
                "base_output": len(" ".join(before).split()), "probe_output": len(" ".join(after).split()),
                "delta": len(" ".join(after).split()) - len(" ".join(before).split())})
print(json.dumps({"unit": "whitespace-separated words; fixed one-word paths and example slug",
                  "scope": "per-moment changed output plus identical governing passages as a common term; no unrelated provider-output or total workload claim",
                  "moments": moments}, indent=2))
