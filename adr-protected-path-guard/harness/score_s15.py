#!/usr/bin/env python3
"""Grades S15 runs (task adr-protected-path-guard) under expectations-s15.json. Needs git and python3; no agent, no network.

  python3 score_s15.py --linter <path to the candidate adr_lint.py>                 # grades ../results/S15-*
  python3 score_s15.py --linter <path> --results <dir> [--run <run id>]             # another results folder / one run
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import world  # noqa: E402

EXP = json.loads((HERE / "expectations-s15.json").read_text())["scenarios"]["S15"]
RESULTS = HERE.parent / "results"
NEW_ADR = re.compile(r"^(mira-app|mira-decisions)/docs/adr/(\d{4})-[a-z0-9-]+\.md$")
PROTECTS = re.compile(r"^\*\*Protects:\*\*", re.M)
ENTRY = re.compile(r"^- `([^`]+)`")


def decision_lines(text):
    found, current = {}, None
    for line in text.split("\n"):
        if line.startswith("## "):
            current = line[3:].strip()
            found[current] = []
        elif current:
            found[current].append(line)
    return found


def listed_paths(text):
    lines = [l.strip() for l in decision_lines(text).get("Decision", [])]
    at = next((i for i, l in enumerate(lines) if PROTECTS.match(l)), None)
    paths = []
    if at is not None:
        for line in lines[at + 1:]:
            if not line.startswith("- "):
                break
            m = ENTRY.match(line)
            if m:
                paths.append(m.group(1))
    return paths


def final_tree(changes, dest):
    """The base world's mira-app (control world) with the run's changes applied; returns the problems that make it unreliable."""
    world.build(dest, control=True)
    app = dest / "mira-app"
    problems = []
    for c in changes:
        if not c["path"].startswith(EXP["app_prefix"]):
            continue
        target = dest / c["path"]
        if c["status"] == "deleted":
            target.unlink(missing_ok=True)
            continue
        if len(c.get("content", "")) >= EXP["max_stored"]:
            problems.append(f"{c['path']} hit the {EXP['max_stored']}-character cut")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(c["content"], encoding="utf-8")
    return app, problems


def run_linter(linter, app, number):
    try:
        p = subprocess.run([sys.executable, "-B", str(linter), EXP["adr_dir"], "--require", f"{number:04d}"], cwd=app, capture_output=True,
                           text=True, timeout=60, stdin=subprocess.DEVNULL)
    except (subprocess.TimeoutExpired, OSError) as e:
        return None, f"linter did not run: {e!r}"
    return p.returncode, (p.stdout + p.stderr).strip()


def grade_s15(run_dir, linter):
    meta = json.loads((run_dir / "meta.json").read_text())
    events = [json.loads(l) for l in (run_dir / "trace.jsonl").read_text().splitlines() if l.strip()]
    final = json.loads((run_dir / "final.json").read_text())
    changes = json.loads((run_dir / "changes.json").read_text())
    g = {"run": meta["run"], "scenario": meta["scenario"], "arm": meta["arm"], "host": meta["host"], "rep": meta["rep"],
         "answered": final is not None, "timed_out": meta.get("timed_out"), "source": run_dir.parent.name,
         "plugin_commit": (meta.get("plugin") or {}).get("commit")}
    calls = [e for e in events if e["t"] == "call"]
    call_text = json.dumps([e["input"] for e in calls])
    g["skill_used"] = "read-adr" in call_text
    g["ran_linter"] = "adr_lint" in call_text
    new_adrs = [c for c in changes if c["status"] == "added" and NEW_ADR.match(c["path"])]
    g["other_files_changed"] = sorted(c["path"] for c in changes if c not in new_adrs and c["path"] != "mira-app/" + EXP["site"])
    reasons, unknown = [], []
    adr = None
    if not new_adrs:
        reasons.append("no new ADR file")
    elif len(new_adrs) > 1:
        reasons.append(f"{len(new_adrs)} new ADR files: " + ", ".join(c["path"] for c in new_adrs))
    else:
        adr = new_adrs[0]
        if not adr["path"].startswith("mira-app/"):
            reasons.append(f"the new ADR {adr['path']} is not in mira-app")
            adr = None
    g.update(adr_number=None, adr_status=None, number_is_guard=None, listed=[], pointer_lines=[], site_lines_removed=None, linter_exit=None)
    if adr:
        number = int(NEW_ADR.match(adr["path"]).group(2))
        g["adr_number"], g["number_is_guard"] = number, number == EXP["guard_number"]
        status = next((l.strip() for l in decision_lines(adr["content"]).get("Status", []) if l.strip()), "")
        g["adr_status"] = status
        with tempfile.TemporaryDirectory() as td:
            app, problems = final_tree(changes, Path(td))
            unknown += problems
            site = app / EXP["site"]
            site_text = site.read_text(encoding="utf-8") if site.is_file() else ""
            base_site = world.REPORT_MAILER_JS
            g["site_lines_removed"] = len([l for l in base_site.split("\n") if l not in site_text.split("\n")])
            cite = re.compile(re.escape(EXP["adr_dir"]) + r"/" + f"{number:04d}" + r"(?!\d)")
            g["pointer_lines"] = [l.strip() for l in site_text.split("\n") if cite.search(l)]
            code, out = run_linter(linter, app, number)
            g["linter_exit"] = code
        if code is None:
            unknown.append(out)
        elif code != 0:
            reasons.append(f"linter exit {code}: " + (out.splitlines() or [""])[0][:200])
        g["listed"] = listed_paths(adr["content"])
        if EXP["site"] not in g["listed"]:
            reasons.append(f"the Decision does not list {EXP['site']}")
        if not g["pointer_lines"]:
            reasons.append(f"{EXP['site']} carries no pointer to ADR {number:04d}")
    verdict = "fail" if reasons else ("ungradable" if unknown else "pass")
    g["verdict"] = verdict
    g["reason"] = "; ".join(reasons or unknown) if verdict != "pass" else "one new ADR lists the site, the linter passes, the site carries the pointer"
    return g


def table(grades):
    f = lambda v: "-" if v is None else ("Y" if v else "N")
    rows = ["| Run | Verdict | Reason | ADR | Listed | Pointer line | Linter exit | Skill used | Ran linter | Other files changed | Run record |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for g in sorted(grades, key=lambda x: (x["source"], x["host"], x["rep"])):
        rows.append(f"| {g['arm']} {g['host']} r{g['rep']} ({g['source']}) | {g['verdict']} | {g['reason']} | {g['adr_number'] or '-'} | {', '.join(g['listed']) or '-'} | "
                    f"{(g['pointer_lines'] or ['-'])[0]} | {g['linter_exit']} | {f(g['skill_used'])} | {f(g['ran_linter'])} | {', '.join(g['other_files_changed']) or '-'} | {g['run']} |")
    return "\n".join(rows)


def main():
    if "--linter" not in sys.argv:
        raise SystemExit("--linter <path to the candidate adr_lint.py> is required")
    linter = Path(sys.argv[sys.argv.index("--linter") + 1]).resolve()
    if not linter.is_file():
        raise SystemExit(f"no linter at {linter}")
    results = Path(sys.argv[sys.argv.index("--results") + 1]).resolve() if "--results" in sys.argv else RESULTS
    grades = [grade_s15(d, linter) for d in sorted(results.glob("S15-*")) if (d / "meta.json").exists()]
    for g in grades:
        g["linter_sha256"] = hashlib.sha256(linter.read_bytes()).hexdigest()
    if "--run" in sys.argv:
        rid = sys.argv[sys.argv.index("--run") + 1]
        print(json.dumps(next(g for g in grades if g["run"] == rid), indent=1))
        return
    tag = f"-{results.name}" if results != RESULTS else ""
    (HERE.parent / f"results-s15{tag}.json").write_text(json.dumps(grades, indent=1))
    md = table(grades)
    (HERE.parent / f"results-s15{tag}.md").write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
