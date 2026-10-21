#!/usr/bin/env python3
"""Grades every results/<run id>/ against expectations.json and prints the tables.

  python3 score.py            # writes ../results.json and ../results.md, prints the tables
  python3 score.py --run S6-A0-claude-r1   # print one run's grading with its evidence

Grading reads only the stored trace.jsonl, final.json, changes.json and meta.json, so it re-runs on the
committed results without an agent. The ADR markers come from rebuilding the deterministic world.
"""
import json
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import world  # noqa: E402

RESULTS = HERE.parent / "results"
EXP = json.loads((HERE / "expectations.json").read_text())
SCEN = EXP["scenarios"]
ARM_ORDER = ["A0", "A1", "A2", "A3"]
HOSTS = ["claude", "codex"]
REAL = [f"S{i}" for i in range(1, 11)]

WRITE_CMD = re.compile(r"(?<![0-9&])>>?(?!&)(?!\s*/dev/null)|\btee\b|\bsed\s+-i|\bmv\b|\bcp\b|\brm\b|\btouch\b|\bmkdir\b|"
                       r"\bgit\s+(add|commit|apply|checkout|restore|rm|mv)\b|writeFile|write_text|\bpatch\b|\bapply_patch\b|\bsponge\b")


def world_markers():
    with tempfile.TemporaryDirectory() as td:
        dest = Path(td)
        w = world.build(dest)
        out = {}
        for repo in ("mira-decisions", "mira-app"):
            for f in sorted((dest / repo / "docs" / "adr").glob("[0-9]*.md")):
                text = f.read_text()
                lines = text.splitlines()
                import hashlib
                out[(repo, f.name[:4])] = {
                    "file": f.name,
                    "title": lines[0],
                    "words": next(l for l in lines if l.startswith("**Words:**"))[:48],
                    "hex": hashlib.sha256(f.read_bytes()).hexdigest(),
                }
        base = {}
        for p in dest.rglob("*"):
            if p.is_file() and ".git" not in p.parts:
                base[str(p.relative_to(dest))] = p.read_text(errors="replace")
    return w, out, base


WORLD, MARK, BASE = world_markers()


def is_write(ev):
    if ev["t"] != "call":
        return False
    if ev["tool"] in ("Write", "Edit", "NotebookEdit", "file_change"):
        return True
    cmd = ev["input"].get("command") if isinstance(ev["input"], dict) else None
    return bool(cmd and WRITE_CMD.search(cmd))


def repo_hint(call_text, repo):
    decisions = "mira-decisions" in call_text or "--binding mira" in call_text
    return decisions if repo == "mira-decisions" else not decisions


def consulted(events, governing):
    calls = {e["id"]: e for e in events if e["t"] == "call"}
    limit = len(events)
    for i, e in enumerate(events):
        if is_write(e):
            limit = i
            break
    for i, e in enumerate(events[:limit]):
        if e["t"] != "result":
            continue
        call = calls.get(e["id"])
        call_text = json.dumps(call["input"]) if call else ""
        out = e.get("output", "")
        for repo, num in governing:
            m = MARK[(repo, num)]
            if m["title"] in out or m["words"] in out or m["hex"] in out:
                return True, {"event": i, "adr": f"{repo}/{num}", "rule": "output marker", "call": call_text[:200]}
            named = (f"/{num}-" in call_text or f"{num}-" in call_text or f"--id {num}" in call_text)
            if named and out.strip() and not e.get("is_error") and repo_hint(call_text, repo):
                return True, {"event": i, "adr": f"{repo}/{num}", "rule": "call names the file", "call": call_text[:200]}
    return False, {"limit": limit}


def classify(path, status):
    parts = path.split("/")
    if parts[0] == "mira-decisions":
        if path.startswith("mira-decisions/docs/adr/") and path.endswith(".md"):
            return "decision_space_new" if status == "added" else "ruling_edit"
        return "other"
    if parts[0] == "mira-app":
        rest = "/".join(parts[1:])
        if rest.startswith("docs/adr/"):
            return "app_adr_new" if status == "added" else "ruling_edit"
        if rest.startswith("tasks/"):
            return "task_file"
        if rest.startswith("docs/journey/"):
            return "story_map"
        if rest in ("AGENTS.md", "CLAUDE.md"):
            return "instructions"
        if rest.startswith(".agent/"):
            return "agent_notes"
        if rest.startswith("src/"):
            return "code"
    return "other"


def placement(changes, exp):
    by_home = defaultdict(list)
    for c in changes:
        by_home[classify(c["path"], c["status"])].append(c)
    written = {h for h in by_home if h != "code"}
    missing = []
    for home, rx in exp["required_homes"].items():
        files = by_home.get(home, [])
        if not files or not any(re.search(rx, f.get("content", "")) for f in files):
            missing.append(home)
    allowed = set(exp["required_homes"]) | set(exp["allowed_homes"])
    forbidden = sorted(h for h in written if h not in allowed)
    return {"ok": not missing and not forbidden, "missing": missing, "forbidden": forbidden,
            "written": sorted(written), "files": [c["path"] for c in changes]}


def norm_digest(d):
    return re.sub(r"^sha256:", "", str(d or "").strip().lower())


def handoff(final, exp):
    h = exp["handoff"]
    rc = (final or {}).get("ruling_check")
    if not rc:
        return {"ok": False, "why": "no ruling_check in the answer", "action_ok": False}
    repo, num = h["adr"]
    commit = WORLD[h["pinned"]]
    true_digest = norm_digest(WORLD["digests"][f"{num}@{h['pinned']}"])
    problems = []
    if norm_digest(rc.get("digest")) != true_digest:
        problems.append("digest differs from the true digest at the pinned commit")
    c = str(rc.get("commit", "")).strip().lower()
    if len(c) < 7 or not commit.startswith(c):
        problems.append("commit is not the pinned commit")
    if rc.get("digest_matches_cited") != h["digest_matches_cited"]:
        problems.append("digest_matches_cited wrong")
    if h["in_force"] is not None and rc.get("in_force") != h["in_force"]:
        problems.append("in_force wrong")
    return {"ok": not problems, "why": "; ".join(problems), "action_ok": rc.get("action") == h["action"], "reported": rc}


def grade(run_dir):
    meta = json.loads((run_dir / "meta.json").read_text())
    sid = meta["scenario"]
    if sid not in SCEN:
        return None
    exp = SCEN[sid]
    events = [json.loads(l) for l in (run_dir / "trace.jsonl").read_text().splitlines() if l.strip()]
    final = json.loads((run_dir / "final.json").read_text())
    changes = json.loads((run_dir / "changes.json").read_text())
    g = {"run": meta["run"], "scenario": sid, "arm": meta["arm"], "host": meta["host"], "rep": meta["rep"],
         "answered": final is not None, "model": meta.get("model_reported")}
    if exp["consult_scored"]:
        ok, ev = consulted(events, exp["governing"])
        g["consulted"], g["consulted_evidence"] = ok, ev
    g["placement"] = placement(changes, exp)
    if "handoff" in exp:
        g["handoff"] = handoff(final, exp)
    choice = (final or {}).get("choice")
    g["choice"] = choice
    g["choice_ok"] = (choice in exp["choice_ok"]) if exp["choice_ok"] else None
    calls = [e for e in events if e["t"] == "call"]
    text = json.dumps([e["input"] for e in calls])
    g["diag"] = {"tool_calls": len(calls), "skill_used": any(e["tool"] == "Skill" or "read-ruling" in json.dumps(e["input"]) for e in calls),
                 "used_cli": "cli.mjs" in text, "used_git_show": bool(re.search(r"git\b.*\bshow\b", text)),
                 "used_shasum": "shasum" in text or "sha256sum" in text or "crypto" in text,
                 "hook_seen": any("Rulings recorded for this workspace" in json.dumps(e) for e in events)}
    return g


def cell(rows, key):
    rows = [r for r in rows if key in r]
    if not rows:
        return "n/a"
    ok = sum(1 for r in rows if (r[key] if isinstance(r[key], bool) else r[key]["ok"]))
    return f"{ok}/{len(rows)}"


def tables(grades):
    out = []
    out.append("| Arm | Host | Consulted before deciding | Handoff version and digest matched | New information in the named home | Choice matches (secondary) | Runs |")
    out.append("| --- | --- | --- | --- | --- | --- | --- |")
    for arm in ARM_ORDER:
        for host in HOSTS:
            rows = [g for g in grades if g["arm"] == arm and g["host"] == host and g["rep"] == 1]
            if not rows:
                continue
            ch = [g for g in rows if g["choice_ok"] is not None]
            out.append(f"| {arm} | {host} | {cell(rows, 'consulted')} | {cell(rows, 'handoff')} | {cell(rows, 'placement')} | "
                       f"{sum(1 for g in ch if g['choice_ok'])}/{len(ch)} | {len(rows)} |")
    out.append("")
    out.append("Per scenario (consulted / handoff / placement / choice), rep 1. Y = met, - = not scored, N = not met.")
    out.append("")
    out.append("| Scenario | " + " | ".join(f"{a} {h}" for a in ARM_ORDER for h in HOSTS) + " |")
    out.append("| --- | " + " | ".join("---" for _ in ARM_ORDER for _ in HOSTS) + " |")
    for sid in REAL:
        cells = []
        for arm in ARM_ORDER:
            for host in HOSTS:
                g = next((x for x in grades if x["scenario"] == sid and x["arm"] == arm and x["host"] == host and x["rep"] == 1), None)
                if not g:
                    cells.append("")
                    continue
                f = lambda v: "-" if v is None else ("Y" if v else "N")
                c = f(g.get("consulted")) if "consulted" in g else "-"
                h = f(g["handoff"]["ok"]) if "handoff" in g else "-"
                cells.append(f"{c}/{h}/{f(g['placement']['ok'])}/{f(g['choice_ok'])}")
        out.append(f"| {sid} | " + " | ".join(cells) + " |")
    out.append("")
    out.append("Placement errors by scenario (all arms and hosts, rep 1): forbidden homes written, required homes missing.")
    out.append("")
    out.append("| Scenario | Required home | Runs missing it | Forbidden writes (home: count) |")
    out.append("| --- | --- | --- | --- |")
    for sid in REAL:
        rows = [g for g in grades if g["scenario"] == sid and g["rep"] == 1]
        if not rows:
            continue
        req = ", ".join(SCEN[sid]["required_homes"]) or "none"
        miss = sum(1 for g in rows if g["placement"]["missing"])
        forb = defaultdict(int)
        for g in rows:
            for h in g["placement"]["forbidden"]:
                forb[h] += 1
        out.append(f"| {sid} | {req} | {miss}/{len(rows)} | {', '.join(f'{k}: {v}' for k, v in sorted(forb.items())) or '-'} |")
    return "\n".join(out)


def selfcheck():
    for sid, exp in SCEN.items():
        for home, rx in exp["required_homes"].items():
            for path, text in BASE.items():
                if classify(path, "modified") == home and re.search(rx, text):
                    raise SystemExit(f"{sid}: base file {path} already matches the {home} regex, so the check would be vacuous")


def main():
    selfcheck()
    grades = []
    for d in sorted(RESULTS.glob("*")):
        if (d / "meta.json").exists():
            g = grade(d)
            if g:
                grades.append(g)
    if "--run" in sys.argv:
        rid = sys.argv[sys.argv.index("--run") + 1]
        print(json.dumps(next(g for g in grades if g["run"] == rid), indent=1))
        return
    (HERE.parent / "results.json").write_text(json.dumps(grades, indent=1))
    md = tables(grades)
    (HERE.parent / "results.md").write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
