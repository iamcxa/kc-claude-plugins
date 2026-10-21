#!/usr/bin/env python3
"""Secondary tables from the stored results: effort per arm, repeat runs, and a post hoc lenient placement reading.

  python3 extras.py      # prints the tables and writes ../extras.md
Run score.py first (it writes ../results.json).
"""
import gzip
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
grades = json.loads((ROOT / "results.json").read_text())
exp = json.loads((HERE / "expectations.json").read_text())["scenarios"]
ARMS, HOSTS = ["A0", "A1", "A2", "A3"], ["claude", "codex"]


def usage(run):
    meta = json.loads((ROOT / "results" / run / "meta.json").read_text())
    tokens = 0
    with gzip.open(ROOT / "results" / run / "raw.jsonl.gz", "rt") as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") == "result" and d.get("usage"):
                u = d["usage"]
                tokens = sum(u.get(k, 0) or 0 for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
            if d.get("type") == "turn.completed" and d.get("usage"):
                u = d["usage"]
                tokens += (u.get("input_tokens", 0) or 0) + (u.get("output_tokens", 0) or 0)
    return meta["elapsed_s"], tokens


out = []
out.append("Effort and tool use per arm and host (rep 1 only; tokens are the host's own usage counters, cache reads included for Claude, input plus output for Codex).")
out.append("")
out.append("| Arm | Host | Runs | Mean tool calls | Mean seconds | Mean tokens | Skill opened | CLI used | git show used | Hook text in context |")
out.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
for arm in ARMS:
    for host in HOSTS:
        rows = [g for g in grades if g["arm"] == arm and g["host"] == host and g["rep"] == 1]
        if not rows:
            continue
        us = [usage(g["run"]) for g in rows]
        n = len(rows)
        out.append(f"| {arm} | {host} | {n} | {sum(g['diag']['tool_calls'] for g in rows)/n:.1f} | {sum(u[0] for u in us)/n:.0f} | {sum(u[1] for u in us)/n:.0f} | "
                   f"{sum(g['diag']['skill_used'] for g in rows)}/{n} | {sum(g['diag']['used_cli'] for g in rows)}/{n} | "
                   f"{sum(g['diag']['used_git_show'] for g in rows)}/{n} | {sum(g['diag']['hook_seen'] for g in rows)}/{n} |")

out.append("")
out.append("Homes written (rep 1, count of runs that wrote each home), by arm and host.")
out.append("")
homes = ["decision_space_new", "app_adr_new", "task_file", "story_map", "instructions", "agent_notes", "other", "ruling_edit"]
out.append("| Arm | Host | " + " | ".join(homes) + " |")
out.append("| --- | --- | " + " | ".join("---" for _ in homes) + " |")
for arm in ARMS:
    for host in HOSTS:
        rows = [g for g in grades if g["arm"] == arm and g["host"] == host and g["rep"] == 1]
        if rows:
            out.append(f"| {arm} | {host} | " + " | ".join(str(sum(h in g["placement"]["written"] for g in rows)) for h in homes) + " |")

out.append("")
out.append("Post hoc, not pre-registered: placement if S2 and S7 also accept the story map as a home. Both scenarios mention work that is put off (non-ASCII file names 'after Friday'; an XLSX request), so a deferred-feature reading is defensible.")
out.append("")
out.append("| Arm | Host | Placement as pre-registered | With story map allowed in S2 and S7 |")
out.append("| --- | --- | --- | --- |")
for arm in ARMS:
    for host in HOSTS:
        rows = [g for g in grades if g["arm"] == arm and g["host"] == host and g["rep"] == 1]
        if not rows:
            continue
        strict = sum(g["placement"]["ok"] for g in rows)
        lenient = 0
        for g in rows:
            p = g["placement"]
            ok = p["ok"]
            if not ok and g["scenario"] in ("S2", "S7") and not p["missing"] and set(p["forbidden"]) <= {"story_map"}:
                ok = True
            lenient += ok
        out.append(f"| {arm} | {host} | {strict}/{len(rows)} | {lenient}/{len(rows)} |")

reps = [g for g in grades if g["rep"] > 1]
if reps:
    out.append("")
    out.append("Repeat runs (rep 2) against rep 1 of the same cell. Flipped = the measure came out differently.")
    out.append("")
    out.append("| Cell | Measure | Rep 1 | Rep 2 | Flipped |")
    out.append("| --- | --- | --- | --- | --- |")
    flips = total = 0
    for r in reps:
        base = next(g for g in grades if g["scenario"] == r["scenario"] and g["arm"] == r["arm"] and g["host"] == r["host"] and g["rep"] == 1)
        for name, pick in (("consulted", lambda g: g.get("consulted")), ("handoff", lambda g: g["handoff"]["ok"] if "handoff" in g else None),
                           ("placement", lambda g: g["placement"]["ok"]), ("choice", lambda g: g["choice_ok"])):
            a, b = pick(base), pick(r)
            if a is None and b is None:
                continue
            total += 1
            flips += a != b
            out.append(f"| {r['scenario']} {r['arm']} {r['host']} | {name} | {a} | {b} | {'yes' if a != b else 'no'} |")
    out.append("")
    out.append(f"{flips} of {total} scored measures flipped between rep 1 and rep 2 ({len(reps)} repeat runs).")

text = "\n".join(out)
(ROOT / "extras.md").write_text(text + "\n")
print(text)
