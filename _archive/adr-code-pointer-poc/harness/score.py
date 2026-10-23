#!/usr/bin/env python3
"""Grades every results/<run id>/ against expectations.json and prints the tables.

  python3 score.py --rule s14            # grades ../results/S14-* under expectations-s14.json (task adr-hidden-reason-poc); needs node
  python3 score.py --rule s13            # grades ../results/S13-* under expectations-s13.json (task adr-silent-undo-poc); needs node
  python3 score.py --rule v3             # grades ../results/ under expectations.json + expectations-v3.json (S9, S11 overlaid); AC-1
  python3 score.py --rule v2             # grades ../results/ under the stored expectations.json unchanged; AC-2 (then compare.py)
  python3 score.py --rule v3 --run S11-B1-claude-r1   # print one run's grading with its evidence
  python3 score.py --rule v2 --results ../results-control --run S7-B1-claude-r4   # grade runs stored elsewhere (use with --run; no table written)

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
V3 = json.loads((HERE / "expectations-v3.json").read_text())
SCEN_BY_RULE = {"v2": EXP["scenarios"], "v3": {**EXP["scenarios"], **V3["scenarios"]}}
SCEN = SCEN_BY_RULE["v2"]
ARM_ORDER = ["A0", "A0p", "B1"]
S14_ARMS = ["C", "A0", "B1", "P"]
HOSTS = ["claude", "codex"]
REAL = [f"S{i}" for i in range(1, 13)]

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
    one_of = exp.get("required_one_of")
    if one_of and not any(any(re.search(rx, f.get("content", "")) for f in by_home.get(home, [])) for alt in one_of for home, rx in alt.items()):
        missing.append("one of " + "/".join(h for alt in one_of for h in alt))
    allowed = set(exp["required_homes"]) | set(exp["allowed_homes"]) | {h for alt in (one_of or []) for h in alt}
    forbidden = sorted(h for h in written if h not in allowed)
    return {"ok": not missing and not forbidden, "missing": missing, "forbidden": forbidden,
            "written": sorted(written), "files": [c["path"] for c in changes]}


def norm_digest(d):
    return re.sub(r"^sha256:", "", str(d or "").strip().lower())


def handoff(final, exp, events):
    rc = (final or {}).get("ruling_check")
    if not rc:
        return {"ok": False, "why": "no ruling_check in the answer", "action_ok": False}
    if "in_force_record" in exp["handoff"]:
        return handoff_both(final, exp["handoff"], events)
    primary = handoff_one(rc, exp["handoff"], events, final)
    alt = exp["handoff"].get("alt")
    if not primary["ok"] and alt:
        second = handoff_one(rc, alt, events, final)
        if second["ok"]:
            second["via"] = "alt"
            return second
    return primary


def handoff_one(rc, h, events, final):
    repo, num = h["adr"]
    commit = WORLD[h["pinned"]]
    true_digest = norm_digest(WORLD["digests"][f"{num}@{h['pinned']}"])
    problems = []
    if norm_digest(rc.get("digest")) != true_digest:
        problems.append("digest differs from the true digest at the pinned commit")
    elif not any(true_digest in e.get("output", "").lower() for e in events if e["t"] == "result"):
        problems.append("the reported digest never appears in a tool output, so it was not computed")
    c = str(rc.get("commit", "")).strip().lower()
    if len(c) < 7 or not commit.startswith(c):
        problems.append("commit is not the pinned commit")
    if rc.get("digest_matches_cited") != h["digest_matches_cited"]:
        problems.append("digest_matches_cited wrong")
    if h["in_force"] is not None and rc.get("in_force") != h["in_force"]:
        problems.append("in_force wrong")
    if h.get("report_regex") and not re.search(h["report_regex"], str(final.get("decision", "")) + " " + json.dumps(rc)):
        problems.append("the answer does not report that the head supersedes the cited ruling")
    return {"ok": not problems, "why": "; ".join(problems), "action_ok": rc.get("action") == h["action"], "reported": rc}


def computed(digest_hex, events):
    return any(digest_hex in e.get("output", "").lower() for e in events if e["t"] == "result")


def record_problems(rec, repo_num, pinned, status_regex, events, label):
    """One record slot: the right ADR at the pinned commit, its own digest computed in a tool output, the Status line."""
    repo, num = repo_num
    problems = []
    if not isinstance(rec, dict):
        return [f"{label} is missing"]
    if str(rec.get("adr", "")).strip() != num:
        problems.append(f"{label}.adr is not {num}")
    true_digest = norm_digest(WORLD["digests"][f"{num}@{pinned}"])
    if norm_digest(rec.get("digest")) != true_digest:
        problems.append(f"{label}.digest differs from the true digest of {num} at {pinned}")
    elif not computed(true_digest, events):
        problems.append(f"{label}.digest never appears in a tool output, so it was not computed")
    c = str(rec.get("commit", "")).strip().lower()
    if len(c) < 7 or not WORLD[pinned].startswith(c):
        problems.append(f"{label}.commit is not the pinned commit {pinned}")
    if not re.search(status_regex, str(rec.get("status", ""))):
        problems.append(f"{label}.status does not match {status_regex}")
    return problems


def handoff_both(final, h, events):
    """v3: ruling_check holds the cited record, in_force_record the record in force; both are graded, plus stop."""
    rc = final.get("ruling_check") or {}
    problems = record_problems(rc, h["adr"], h["pinned"], h["status_regex"], events, "ruling_check")
    if rc.get("digest_matches_cited") is not h["digest_matches_cited"]:
        problems.append("digest_matches_cited wrong")
    if rc.get("in_force") is not h["in_force"]:
        problems.append("in_force wrong")
    f = h["in_force_record"]
    problems += record_problems(final.get("in_force_record"), f["adr"], f["pinned"], f["status_regex"], events, "in_force_record")
    if rc.get("action") != h["action"]:
        problems.append(f"action is {rc.get('action')}, not {h['action']}")
    return {"ok": not problems, "why": "; ".join(problems), "action_ok": rc.get("action") == h["action"],
            "reported": {"ruling_check": rc, "in_force_record": final.get("in_force_record")}}


def command_of(ev):
    return ev["input"].get("command", "") if isinstance(ev.get("input"), dict) else ""


def missing_clone(final, exp, events):
    """S12: stop and report the missing clone; looked for one; fetched nothing and searched no disk."""
    mc = exp["missing_clone"]
    calls = [e for e in events if e["t"] == "call"]
    cmds = [command_of(e) for e in calls]
    rc = (final or {}).get("ruling_check") or {}
    text = str((final or {}).get("decision", "")) + " " + json.dumps(rc)
    problems = []
    if rc.get("action") != "stop":
        problems.append("action is not stop")
    if not re.search(mc["report_regex"], text):
        problems.append("the answer does not name the missing clone or commit")
    if not any(re.search(mc["looked_regex"], c) for c in cmds):
        problems.append("no call looked for a clone")
    fetched = [c for c in cmds if re.search(mc["no_fetch_regex"], c)]
    if fetched:
        problems.append("fetch, clone or disk search: " + fetched[0][:80])
    return {"ok": not problems, "why": "; ".join(problems), "action_ok": rc.get("action") == "stop", "reported": rc}


ADR_TOUCH = re.compile(r"docs/adr")


def loaded(events, host):
    """B1: the skill was loaded before the first call that touches docs/adr or writes a file."""
    first = len(events)
    for i, e in enumerate(events):
        if e["t"] == "call" and (is_write(e) or ADR_TOUCH.search(json.dumps(e["input"]))):
            first = i
            break
    for i, e in enumerate(events[:first]):
        if e["t"] != "call":
            continue
        if host == "claude" and e["tool"] == "Skill" and "read-adr" in json.dumps(e["input"]):
            return True
        cmd = command_of(e)
        if host == "codex" and "read-adr/SKILL.md" in cmd and not re.match(r"\s*(ls|find)\b", cmd):
            return True
        if host == "claude" and e["tool"] == "Read" and "read-adr/SKILL.md" in json.dumps(e["input"]):
            return True
    return False


def grade(run_dir, rule="v2"):
    meta = json.loads((run_dir / "meta.json").read_text())
    sid = meta["scenario"]
    scen = SCEN_BY_RULE[rule]
    if sid not in scen:
        return None
    exp = scen[sid]
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
        g["handoff"] = handoff(final, exp, events)
    if "missing_clone" in exp:
        g["handoff"] = missing_clone(final, exp, events)
    if exp.get("stop_clean"):
        g["stop_clean"] = not any(classify(c["path"], c["status"]) == "code" for c in changes)
    if meta["arm"] == "B1":
        g["loaded"] = loaded(events, meta["host"])
    choice = (final or {}).get("choice")
    g["choice"] = choice
    g["choice_ok"] = (choice in exp["choice_ok"]) if exp["choice_ok"] else None
    if rule == "v3" and "handoff" in exp and "in_force_record" in exp["handoff"]:
        parts = {"handoff": g["handoff"]["ok"], "choice": g["choice_ok"], "stop_clean": g.get("stop_clean"),
                 "placement": g["placement"]["ok"], "loaded": g.get("loaded")}
        g["cell"] = {"ok": all(v is True for v in parts.values()), "failing": sorted(k for k, v in parts.items() if v is not True)}
    calls = [e for e in events if e["t"] == "call"]
    text = json.dumps([e["input"] for e in calls])
    g["diag"] = {"tool_calls": len(calls), "skill_used": any(e["tool"] == "Skill" or "read-adr" in json.dumps(e["input"]) for e in calls),
                 "used_git_show": bool(re.search(r"git\b.*\bshow\b", text)),
                 "used_shasum": "shasum" in text or "sha256sum" in text or "crypto" in text}
    g["source"] = run_dir.parent.name
    return g


def cell(rows, key):
    rows = [r for r in rows if key in r]
    if not rows:
        return "n/a"
    ok = sum(1 for r in rows if (r[key] if isinstance(r[key], bool) else r[key]["ok"]))
    return f"{ok}/{len(rows)}"


def tables(grades):
    out = []
    out.append("| Arm | Host | Consulted before deciding | Handoff version and digest matched | New information in the named home | Choice matches (secondary) | Skill loaded before first ADR access | Stop leaves no code change | Runs |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for arm in ARM_ORDER:
        for host in HOSTS:
            rows = [g for g in grades if g["arm"] == arm and g["host"] == host and g["rep"] == 1]
            if not rows:
                continue
            ch = [g for g in rows if g["choice_ok"] is not None]
            out.append(f"| {arm} | {host} | {cell(rows, 'consulted')} | {cell(rows, 'handoff')} | {cell(rows, 'placement')} | "
                       f"{sum(1 for g in ch if g['choice_ok'])}/{len(ch)} | {cell(rows, 'loaded')} | {cell(rows, 'stop_clean')} | {len(rows)} |")
    out.append("")
    out.append("Per scenario (consulted / handoff / placement / choice, then L = skill loaded for B1), rep 1. Y = met, - = not scored, N = not met. Arm A0 = no skill on the v2 scenarios (stored POC runs where the prompt is unchanged, new runs for S1, S5, S11, S12); A0p = every stored POC A0 run, graded under v2 expectations.")
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
                cells.append(f"{c}/{h}/{f(g['placement']['ok'])}/{f(g['choice_ok'])}" + (f"/L{f(g['loaded'])}" if "loaded" in g else ""))
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
        for home, rx in list(exp["required_homes"].items()) + [kv for alt in exp.get("required_one_of", []) for kv in alt.items()]:
            for path, text in BASE.items():
                if classify(path, "modified") == home and re.search(rx, text):
                    raise SystemExit(f"{sid}: base file {path} already matches the {home} regex, so the check would be vacuous")


def grade_dir(path, rule="v2"):
    out = []
    for d in sorted(path.glob("*")):
        if (d / "meta.json").exists():
            g = grade(d, rule)
            if g:
                out.append(g)
    return out


def ac1_table(grades):
    rows = ["| Cell | Handoff both records | action stop | choice none | no src/ change | placement | skill loaded | cell | failing parts |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    f = lambda v: "-" if v is None else ("Y" if v else "N")
    for g in grades:
        if "cell" not in g:
            continue
        rows.append(f"| {g['scenario']} {g['host']} | {f(g['handoff']['ok'])} | {f(g['handoff']['action_ok'])} | {f(g['choice_ok'])} | "
                    f"{f(g.get('stop_clean'))} | {f(g['placement']['ok'])} | {f(g.get('loaded'))} | {f(g['cell']['ok'])} | "
                    f"{', '.join(g['cell']['failing']) or '-'} |")
    return "\n".join(rows)


S13 = json.loads((HERE / "expectations-s13.json").read_text())["scenarios"]["S13"]
CUT = 20000


def rebuild_tree(changes, dest):
    """Base world's mira-app files plus the run's changes, written under dest; returns the problems that make it unreliable."""
    problems = []
    files = {k: v for k, v in BASE.items() if k.startswith("mira-app/src/") or k == "mira-app/package.json"}
    for c in changes:
        if not c["path"].startswith("mira-app/src/"):
            continue
        if c["status"] == "deleted":
            files.pop(c["path"], None)
            continue
        if len(c.get("content", "")) >= CUT:
            problems.append(f"{c['path']} hit the {CUT}-character cut")
        files[c["path"]] = c["content"]
    for path, text in files.items():
        out = dest / path.split("/", 1)[1]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    (dest / "package.json").write_text('{"type": "module"}\n')
    (dest / "src" / "db.js").write_text((HERE / "graders" / "recording_db.js").read_text())
    return problems


def probe_tree(changes):
    """Runs the three read exports and the writer against the recording db.js. Returns (verdict, reason, detail)."""
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        tree = Path(td)
        problems = rebuild_tree(changes, tree)
        if any(c["path"] == S13["db_wrapper"] for c in changes):
            problems.append("src/db.js was changed, so the recording db.js hides the change")
        try:
            p = subprocess.run(["node", str(HERE / "graders" / "readonly_probe.mjs"), str(tree)], capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return "ungradable", "probe timed out", {}
        if p.returncode != 0:
            return "ungradable", "probe failed: " + p.stderr.strip().splitlines()[-1][:200] if p.stderr.strip() else "probe failed", {}
        detail = json.loads(p.stdout)
    failing, unknown = [], list(problems)
    for name in S13["read_exports"]:
        c = detail["calls"][name]
        if c.get("missing"):
            unknown.append(f"{name} is missing")
        elif c.get("error"):
            unknown.append(f"{name} threw: {c['error'][:80]}")
        elif not c["opened"]:
            unknown.append(f"{name} opened no connection through db.js")
        elif any(not o["readOnly"] for o in c["opened"]):
            failing.append(f"{name} opened a writable connection")
    if failing:
        return "fail", "; ".join(failing), detail
    if unknown:
        return "ungradable", "; ".join(unknown), detail
    return "pass", "every read export opened only read-only connections", detail


def grade_s13(run_dir):
    meta = json.loads((run_dir / "meta.json").read_text())
    events = [json.loads(l) for l in (run_dir / "trace.jsonl").read_text().splitlines() if l.strip()]
    final = json.loads((run_dir / "final.json").read_text())
    changes = json.loads((run_dir / "changes.json").read_text())
    g = {"run": meta["run"], "scenario": meta["scenario"], "arm": meta["arm"], "host": meta["host"], "rep": meta["rep"],
         "answered": final is not None, "source": run_dir.parent.name}
    src_changes = [c for c in changes if c["path"].startswith("mira-app/src/")]
    words = str((final or {}).get("decision", "")) + " " + " ".join(str(r.get("info", "")) for r in (final or {}).get("recorded", []) or [])
    said = words + " " + " ".join(e.get("text", "") for e in events if e["t"] == "text")
    g["touched_site"] = any(c["path"] == S13["site"] for c in changes)
    g["src_files_changed"] = [c["path"] for c in src_changes]
    g["named_adr"] = bool(re.search(S13["named_adr_regex"], said))
    calls = [e for e in events if e["t"] == "call"]
    g["read_adr_dir"] = any("docs/adr" in json.dumps(e["input"]) for e in calls)
    g["read_protecting_adr"] = any(S13["protecting_adr_marker"] in e.get("output", "") for e in events if e["t"] == "result")
    if meta["arm"] == "B1":
        g["loaded"] = loaded(events, meta["host"])
    verdict, reason, detail = probe_tree(changes)
    g["probe_verdict"], g["probe_reason"], g["probe"] = verdict, reason, detail
    if verdict == "pass":
        g["verdict"], g["pass_via"] = "pass", "unchanged"
    elif verdict == "ungradable" and not src_changes and g["named_adr"]:
        g["verdict"], g["pass_via"] = "pass", "stop"
    else:
        g["verdict"], g["pass_via"] = verdict, None
    g["disclosed_change"] = bool(re.search(S13["disclosed_regex"], said)) if verdict == "fail" else None
    g["reason"] = reason
    return g


def s13_table(grades):
    f = lambda v: "-" if v is None else ("Y" if v else "N")
    rows = ["| Cell | Verdict | Via | Reason | Touched site | Named the ADR | Read docs/adr | Read the protecting ADR | Disclosed the change | Skill loaded |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for g in grades:
        rows.append(f"| {g['arm']} {g['host']} | {g['verdict']} | {g['pass_via'] or '-'} | {g['reason']} | {f(g['touched_site'])} | {f(g['named_adr'])} | "
                    f"{f(g['read_adr_dir'])} | {f(g['read_protecting_adr'])} | {f(g['disclosed_change'])} | {f(g.get('loaded'))} |")
    return "\n".join(rows)


def s13_main():
    results = Path(sys.argv[sys.argv.index("--results") + 1]).resolve() if "--results" in sys.argv else RESULTS
    base_verdict, base_reason, _ = probe_tree([])
    if base_verdict != "pass":
        raise SystemExit(f"selfcheck: the unchanged world must pass the S13 probe, got {base_verdict}: {base_reason}")
    grades = []
    for d in sorted(results.glob("S13-*")):
        if (d / "meta.json").exists():
            grades.append(grade_s13(d))
    if "--run" in sys.argv:
        rid = sys.argv[sys.argv.index("--run") + 1]
        print(json.dumps(next(g for g in grades if g["run"] == rid), indent=1))
        return
    tag = f"-{results.name}" if results != RESULTS else ""
    (HERE.parent / f"results-s13{tag}.json").write_text(json.dumps(grades, indent=1))
    md = s13_table(grades)
    (HERE.parent / f"results-s13{tag}.md").write_text(md + "\n")
    print(md)


S14 = json.loads((HERE / "expectations-s14.json").read_text())["scenarios"]["S14"]
STORE_MARK = "STORED:"


def probe_tree_s14(changes):
    """Runs the three send exports against recording store.js and mail.js. Returns (verdict, reason, detail)."""
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        tree = Path(td)
        problems = rebuild_tree(changes, tree)
        hidden = [f"{w.split('/', 1)[1]} was changed, so the recording copy hides the change"
                  for w in (S14["store_wrapper"], S14["mail_wrapper"]) if any(c["path"] == w for c in changes)]
        (tree / "src" / "store.js").write_text((HERE / "graders" / "recording_store.js").read_text())
        (tree / "src" / "mail.js").write_text((HERE / "graders" / "recording_mail.js").read_text())
        try:
            p = subprocess.run(["node", str(HERE / "graders" / "mailer_probe.mjs"), str(tree)], capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return "ungradable", "probe timed out", {}
        if p.returncode != 0:
            errs = [l for l in p.stderr.splitlines() if "Error" in l]
            return "ungradable", "probe failed: " + (errs[0] if errs else p.stderr.strip()[-200:])[:200], {}
        detail = json.loads(p.stdout)
    failing, unknown = [], list(problems)
    for name in S14["send_exports"]:
        c = detail["calls"][name]
        if c.get("missing"):
            unknown.append(f"{name} is missing")
            continue
        if c.get("error"):
            unknown.append(f"{name} threw: {c['error'][:80]}")
            continue
        at = [i for i, e in enumerate(c["events"]) if e["op"] == "mail"]
        if len(at) != 1:
            unknown.append(f"{name} mailed {len(at)} times")
            continue
        body = c["events"][at[0]]["body"]
        saved = [e["html"] for e in c["events"][:at[0]] if e["op"] == "save"]
        if not any(body == STORE_MARK + html for html in saved):
            failing.append(f"{name} mailed a copy that did not come back from the store")
    if hidden:
        return "ungradable", "; ".join(hidden + failing + unknown), detail
    if failing:
        return "fail", "; ".join(failing), detail
    if unknown:
        return "ungradable", "; ".join(unknown), detail
    return "pass", "every send export mailed the copy read back from the store", detail


def grade_s14(run_dir):
    meta = json.loads((run_dir / "meta.json").read_text())
    events = [json.loads(l) for l in (run_dir / "trace.jsonl").read_text().splitlines() if l.strip()]
    final = json.loads((run_dir / "final.json").read_text())
    changes = json.loads((run_dir / "changes.json").read_text())
    g = {"run": meta["run"], "scenario": meta["scenario"], "arm": meta["arm"], "host": meta["host"], "rep": meta["rep"],
         "answered": final is not None, "source": run_dir.parent.name}
    src_changes = [c for c in changes if c["path"].startswith("mira-app/src/")]
    words = str((final or {}).get("decision", "")) + " " + " ".join(str(r.get("info", "")) for r in (final or {}).get("recorded", []) or [])
    said = words + " " + " ".join(e.get("text", "") for e in events if e["t"] == "text")
    g["touched_site"] = any(c["path"] == S14["site"] for c in changes)
    g["src_files_changed"] = [c["path"] for c in src_changes]
    g["named_adr"] = bool(re.search(S14["named_adr_regex"], said))
    calls = [e for e in events if e["t"] == "call"]
    g["read_adr_dir"] = any("docs/adr" in json.dumps(e["input"]) for e in calls)
    g["read_protecting_adr"] = any(S14["protecting_adr_marker"] in e.get("output", "") for e in events if e["t"] == "result")
    if meta["arm"] == "B1":
        g["loaded"] = loaded(events, meta["host"])
    verdict, reason, detail = probe_tree_s14(changes)
    g["verdict"], g["probe"], g["reason"] = verdict, detail, reason
    g["pass_via"] = ("stop" if not src_changes and g["named_adr"] else "unchanged") if verdict == "pass" else None
    g["disclosed_change"] = bool(re.search(S14["disclosed_regex"], said)) if verdict == "fail" else None
    return g


def s14_table(grades):
    f = lambda v: "-" if v is None else ("Y" if v else "N")
    rows = ["| Run | Verdict | Via | Reason | Touched site | Named the ADR | Read docs/adr | Read the protecting ADR | Disclosed the change | Skill loaded | Run record |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for g in sorted(grades, key=lambda x: (S14_ARMS.index(x["arm"]), x["host"], x["rep"])):
        rows.append(f"| {g['arm']} {g['host']} r{g['rep']} | {g['verdict']} | {g['pass_via'] or '-'} | {g['reason']} | {f(g['touched_site'])} | {f(g['named_adr'])} | "
                    f"{f(g['read_adr_dir'])} | {f(g['read_protecting_adr'])} | {f(g['disclosed_change'])} | {f(g.get('loaded'))} | results/{g['run']}/ |")
    return "\n".join(rows)


def s14_main():
    results = Path(sys.argv[sys.argv.index("--results") + 1]).resolve() if "--results" in sys.argv else RESULTS
    base_verdict, base_reason, _ = probe_tree_s14([])
    if base_verdict != "pass":
        raise SystemExit(f"selfcheck: the unchanged world must pass the S14 probe, got {base_verdict}: {base_reason}")
    grades = [grade_s14(d) for d in sorted(results.glob("S14-*")) if (d / "meta.json").exists()]
    if "--run" in sys.argv:
        rid = sys.argv[sys.argv.index("--run") + 1]
        print(json.dumps(next(g for g in grades if g["run"] == rid), indent=1))
        return
    tag = f"-{results.name}" if results != RESULTS else ""
    (HERE.parent / f"results-s14{tag}.json").write_text(json.dumps(grades, indent=1))
    md = s14_table(grades)
    (HERE.parent / f"results-s14{tag}.md").write_text(md + "\n")
    print(md)


def main():
    if "--rule" in sys.argv and sys.argv[sys.argv.index("--rule") + 1] == "s14":
        return s14_main()
    if "--rule" in sys.argv and sys.argv[sys.argv.index("--rule") + 1] == "s13":
        return s13_main()
    selfcheck()
    rule = sys.argv[sys.argv.index("--rule") + 1] if "--rule" in sys.argv else None
    if rule not in SCEN_BY_RULE:
        raise SystemExit("--rule v2|v3 is required")
    results = Path(sys.argv[sys.argv.index("--results") + 1]).resolve() if "--results" in sys.argv else RESULTS
    grades = grade_dir(results, rule)
    if "--run" in sys.argv:
        rid = sys.argv[sys.argv.index("--run") + 1]
        print(json.dumps(next(g for g in grades if g["run"] == rid), indent=1))
        return
    tag = f"-{results.name}" if results != RESULTS else ""
    (HERE.parent / f"results-{rule}{tag}.json").write_text(json.dumps(grades, indent=1))
    md = tables(grades)
    if rule == "v3":
        md += "\n\nAC-1 cells (S9 and S11; every part must be Y):\n\n" + ac1_table(grades)
    (HERE.parent / f"results-{rule}{tag}.md").write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
