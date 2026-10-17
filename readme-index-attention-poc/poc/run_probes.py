#!/usr/bin/env python3
"""Run the pre-registered probe matrix: 5 probes x 2 arms x 3 reps, in a seeded shuffled order.

Usage: run_probes.py run [--only ARM-PROBE-REP ...]   run the matrix (skips runs whose raw file exists)
       run_probes.py report                           score runs/*.jsonl into results.md and results.json
Raw stream-json for each run goes to runs/<arm>-<probe>-<rep>.jsonl; nothing here edits it afterwards.
Isolation: only the system prompt differs between arms. Tools, cwd contents (arm B has rules/), flags are fixed.
"""
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from probes import DECIDERS, SITUATIONS  # noqa: E402

HERE = Path(__file__).resolve().parent
RUNS = Path(os.environ.get("POC_RUNS_DIR", HERE / "runs"))
SEED = 20261017
ARMS = ("A", "B")
PROBES = tuple(SITUATIONS)
REPS = (1, 2, 3)
MODEL = "sonnet"

COMMON = ("You are the first officer (FO) of a development workflow: you coordinate workers and record state, and "
          "you cannot run commands in this session. When a situation asks for an action, answer with the exact "
          "text or commands FO would produce, in the layout the situation asks for, and nothing else. Do not ask "
          "questions. You have a Read tool for workflow files.")
ARM_INTRO = {
    "A": "\n\nYour startup load is the workflow README below. It is the whole workflow definition.\n\n",
    "B": ("\n\nYour startup load is the workflow README below. It is an index: the rule files it lists are under "
          "`rules/` in your working directory.\n\n"),
}


def arm_dir(arm):
    return HERE / ("arm-a-cwd" if arm == "A" else "arm-b")


def startup_text(arm):
    return (HERE / ("arm-a/README.md" if arm == "A" else "arm-b/README.md")).read_text()


def words(text):
    return len(text.split())


def matrix():
    cells = [(a, p, r) for a in ARMS for p in PROBES for r in REPS]
    random.Random(SEED).shuffle(cells)
    return cells


def name(cell):
    return "{}-{}-{}".format(*cell)


def run_one(cell):
    arm, probe, rep = cell
    out = RUNS / f"{name(cell)}.jsonl"
    if out.exists():
        return
    cwd = arm_dir(arm)
    cwd.mkdir(exist_ok=True)
    sysfile = RUNS / f"{name(cell)}.system.txt"
    sysfile.write_text(COMMON + ARM_INTRO[arm] + startup_text(arm))
    argv = ["claude", "-p", "--model", MODEL, "--system-prompt-file", str(sysfile), "--tools", "Read",
            "--setting-sources", "", "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence",
            "--max-budget-usd", "1", "--output-format", "stream-json", "--verbose"]
    started = time.time()
    done = subprocess.run(argv, input="Situation:\n\n" + SITUATIONS[probe], cwd=cwd, capture_output=True, text=True,
                          timeout=600)
    out.write_text(done.stdout)
    (RUNS / f"{name(cell)}.meta.json").write_text(json.dumps(
        {"argv": argv, "exit": done.returncode, "seconds_wall": round(time.time() - started, 1),
         "stderr_tail": done.stderr[-500:]}))


def parse(cell):
    path = RUNS / f"{name(cell)}.jsonl"
    reads, other_tools, result = [], [], None
    for line in path.read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") == "tool_use":
                    if block["name"] == "Read":
                        reads.append(block["input"].get("file_path", ""))
                    else:
                        other_tools.append(block["name"])
        if event.get("type") == "result":
            result = event
    return reads, other_tools, result


def report():
    rows = []
    for cell in matrix():
        arm, probe, rep = cell
        if not (RUNS / f"{name(cell)}.jsonl").exists():
            continue
        reads, other, result = parse(cell)
        answer = (result or {}).get("result", "") or ""
        followed, decider = DECIDERS[probe](answer)
        usage = (result or {}).get("usage", {})
        tokens = sum(usage.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens",
                                               "cache_read_input_tokens", "output_tokens"))
        startup = words(startup_text(arm))
        read_words = 0
        for rel in dict.fromkeys(reads):
            p = Path(rel) if Path(rel).is_absolute() else arm_dir(arm) / rel
            read_words += words(p.read_text()) if p.exists() else 0
        rows.append({"run": name(cell), "arm": arm, "probe": probe, "rep": rep, "followed": followed,
                     "decider": decider, "startup_words": startup, "moment_words": startup + read_words,
                     "files_read": [Path(r).name for r in dict.fromkeys(reads)], "other_tools": other,
                     "tokens": tokens, "seconds": round((result or {}).get("duration_ms", 0) / 1000, 1),
                     "cost_usd_imputed": (result or {}).get("total_cost_usd"),
                     "is_error": (result or {}).get("is_error"), "model": list((result or {}).get("modelUsage", {}))})
    rows.sort(key=lambda r: (r["probe"], r["arm"], r["rep"]))
    (HERE / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    lines = ["| run | followed | decider | startup words | moment words | files read | tokens | s | cost (imputed) |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append("| {run} | {f} | {decider} | {startup_words} | {moment_words} | {files} | {tokens} | {seconds} | {cost_usd_imputed} |".format(
            f="yes" if r["followed"] else "NO", files=", ".join(r["files_read"]) or "-", **{**r, "decider": r["decider"].replace("|", "/")[:160]}))
    (HERE / "results.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    for arm in ARMS:
        mine = [r for r in rows if r["arm"] == arm]
        print(arm, sum(r["followed"] for r in mine), "/", len(mine))


if __name__ == "__main__":
    RUNS.mkdir(exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        only = set(sys.argv[3:]) if len(sys.argv) > 2 and sys.argv[2] == "--only" else None
        for cell in matrix():
            if only is None or name(cell) in only:
                run_one(cell)
                print("done", name(cell), flush=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "report":
        report()
    else:
        print(__doc__)
        sys.exit(2)
