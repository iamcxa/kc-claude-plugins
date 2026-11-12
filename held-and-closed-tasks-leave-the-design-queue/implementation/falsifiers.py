#!/usr/bin/env python3
"""Run each acceptance predicate in a fresh -B process on real and mutated evidence.

Generate cases with: python3 -B falsifiers.py --build EVIDENCE SCRATCH
The SCRATCH argument is the origin-less copy made by acceptance.py.
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import yaml


def accepts(name, data):
    if name == "AC-1":
        return sorted(r["slug"] for r in data["rows"]) == sorted(data["expected"])
    if name == "AC-2":
        slugs = {r["slug"] for r in data["rows"]["ready_gates"] + data["rows"]["dispatchable"]}
        return not slugs.intersection(data["held"])
    if name == "AC-3":
        return not any(slug in data["output"] for slug in data["held"])
    if name == "AC-4":
        return data["exit"] == 0
    if name == "AC-5":
        return all(code == 1 for code in data["exits"])
    if name == "AC-6":
        return any(a.get("resolution", {}).get("decision") == "hold" and i + 1 < len(record["attempts"])
                   for record in data["gates"]["records"] for i, a in enumerate(record["attempts"]))
    if name == "AC-7":
        return all(quote in reason for quote, reason in data["quotes"])
    if name == "NP-1":
        return len(data["slugs"]) == len(set(data["slugs"])) and set(data["slugs"]) == set(data["expected"])
    if name == "NP-3":
        return data["added"] <= 30
    if name == "NP-4 projection":
        return data["unchanged_frontmatter"] and not any(line.startswith("next: write ## Held") for line in data["lines"])
    raise ValueError(name)


if sys.argv[1] != "--build":
    name, data = json.loads(Path(sys.argv[1]).read_text())
    good = accepts(name, data)
    print(name, "accepted" if good else "REJECTED")
    raise SystemExit(0 if good else 1)

ev, scratch = map(Path, sys.argv[2:])
state = scratch / "candidate/docs/dev2/.spacedock-state"
held = (ev.parent / "ideation/held-ten.txt").read_text().split()
commands = json.loads((ev / "commands.json").read_text())
codes = {r["name"]: r["exit"] for r in commands if "exit" in r}
fm = lambda path: yaml.safe_load(path.read_text()[4:].split("\n---\n", 1)[0])
reason = lambda slug: [a["resolution"]["reason"] for r in fm(state / (slug + ".md"))["gates"]["records"]
                       for a in r["attempts"] if a.get("resolution", {}).get("decision") == "hold"][-1]
quotes = []
for line in (ev.parent / "ideation/ac7-proposed-held-lines.tsv").read_text().splitlines():
    slug, _, quote = line.split("\t")
    if quote:
        quotes.append([quote, reason(slug)])
expected = [r["slug"] for r in json.loads((ev / "np1-query.log").read_text())["entities"]]
unchanged = all((state / (slug + ".md")).read_bytes().split(b"\n---\n", 1)[0] ==
                (scratch / "base/docs/dev2/.spacedock-state" / (slug + ".md")).read_bytes().split(b"\n---\n", 1)[0]
                for slug in held)
cases = {
    "AC-1": {"rows": json.loads((ev / "ac1-query.log").read_text())["entities"], "expected": held},
    "AC-2": {"rows": json.loads((ev / "ac2-next.log").read_text()), "held": held},
    "AC-3": {"output": (ev / "ac3-legacy.log").read_text(), "held": held},
    "AC-4": {"exit": codes["ac4-dispatch"]},
    "AC-5": {"exits": [codes["ac5-" + name] for name in ("merge-guard", "terminal-status", "archive")]},
    "AC-6": fm(state / "_archive/fo-interviews-extension.md"),
    "AC-7": {"quotes": quotes},
    "NP-1": {"slugs": expected[:], "expected": expected},
    "NP-3": {"added": json.loads((ev / "words.json").read_text())["held_line_added"]},
    "NP-4 projection": {"unchanged_frontmatter": unchanged, "lines": (ev / "np3-all-held-projection.log").read_text().splitlines()},
}
results = []
for name, data in cases.items():
    mutated = copy.deepcopy(data)
    if name == "AC-1": mutated["rows"].pop()
    elif name == "AC-2": mutated["rows"]["ready_gates"].append({"slug": held[0]})
    elif name == "AC-3": mutated["output"] += "\nfact: " + held[0]
    elif name == "AC-4": mutated["exit"] = 1
    elif name == "AC-5": mutated["exits"][1] = 0
    elif name == "AC-6":
        for record in mutated["gates"]["records"]:
            for i, attempt in enumerate(record["attempts"]):
                if attempt.get("resolution", {}).get("decision") == "hold":
                    record["attempts"] = record["attempts"][:i + 1]
                    break
    elif name == "AC-7": mutated["quotes"][0][0] += "X"
    elif name == "NP-1": mutated["slugs"].append(expected[0])
    elif name == "NP-3": mutated["added"] += 31
    elif name == "NP-4 projection": mutated["unchanged_frontmatter"] = False
    for label, case in (("real", data), ("mutated", mutated)):
        path = ev / (name.replace(" ", "-") + "-" + label + ".json")
        path.write_text(json.dumps([name, case], ensure_ascii=False, default=str))
        done = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), str(path)], capture_output=True, text=True)
        expected_exit = 1 if label == "mutated" or name == "NP-3" else 0
        results.append({"name": name + " " + label, "status": "passed" if done.returncode == expected_exit else "failed",
                        "exit": done.returncode, "expected": expected_exit, "message": done.stdout.strip(),
                        "command": [sys.executable, "-B", str(Path(__file__).resolve()), str(path)]})
(ev / "falsifiers.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
raise SystemExit(int(any(r["status"] == "failed" for r in results)))
