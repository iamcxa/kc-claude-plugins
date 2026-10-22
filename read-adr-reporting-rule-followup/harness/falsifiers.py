#!/usr/bin/env python3
"""Scorer and comparer falsifiers for AC-1 and AC-2. Needs no agent. Prints one line per case; exit 1 if a verdict is unexpected.

Stored runs read here are the archived kc-decision-log-cli results (arm B1 = the shipped skill; arm A0 = no skill)."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compare  # noqa: E402
import score  # noqa: E402

STORED = compare.STORED
W = score.WORLD
D0, D1 = W["D0"], W["D1"]
DG = W["digests"]
fails = []


def mk(scenario, host="claude", final=None, trace=None, changes=None, src="S11-B1-claude-r1"):
    td = Path(tempfile.mkdtemp())
    d = td / f"{scenario}-B1-{host}-r1"
    shutil.copytree(STORED / src, d)
    meta = json.loads((d / "meta.json").read_text())
    meta.update(scenario=scenario, arm="B1", host=host, run=d.name)
    (d / "meta.json").write_text(json.dumps(meta))
    (d / "final.json").write_text(json.dumps(final))
    (d / "trace.jsonl").write_text("\n".join(json.dumps(e) for e in trace) + "\n")
    (d / "changes.json").write_text(json.dumps(changes if changes is not None else []))
    return d


def case(name, got, expect):
    ok = got == expect
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (expected {expect})")
    if not ok:
        fails.append(name)


def hex_of(key):
    return DG[key].split(":")[1]


def trace_for(*keys):
    ev = [{"t": "call", "id": "s", "tool": "Skill", "input": {"skill": "kc-adr:read-adr"}}, {"t": "result", "id": "s", "output": "ok", "is_error": False}]
    for i, k in enumerate(keys):
        ev += [{"t": "call", "id": f"c{i}", "tool": "Bash", "input": {"command": f"git show X:{k} | shasum -a 256"}},
               {"t": "result", "id": f"c{i}", "output": hex_of(k) + "  -", "is_error": False}]
    return ev


def answer(sid, **over):
    """The hand-built answer that holds both records."""
    cited = {"S9": ("0002", D1, "0002@D1", "Superseded by 0014"), "S11": ("0014", D0, "0014@D0", "Accepted")}[sid]
    a = {"decision": f"The cited ADR {cited[0]} is superseded by 0023, which is in force; I stop and wait for a person.", "recorded": [], "choice": "none",
         "ruling_check": {"adr": cited[0], "commit": cited[1], "digest": DG[cited[2]], "status": cited[3], "digest_matches_cited": True,
                          "in_force": False, "action": "stop"},
         "in_force_record": {"adr": "0023", "commit": D1, "digest": DG["0023@D1"], "status": "Accepted"}}
    for k, v in over.items():
        if k in ("choice",):
            a[k] = v
        elif k == "in_force_record":
            a[k] = v
        else:
            a["ruling_check"][k] = v
    return a


def v3(d):
    g = score.grade(d, "v3")
    return g["cell"]["ok"]


def why(d):
    """The failing parts and the handoff reason: a mutation must fail for its own reason, not for another one."""
    g = score.grade(d, "v3")
    return g["cell"]["failing"], g["handoff"]["why"]


def case_why(name, d, parts, text):
    failing, reason = why(d)
    ok = failing == parts and text in reason
    print(("ok   " if ok else "FAIL ") + f"{name}: failing {failing}, handoff reason '{reason}' (expected {parts} containing '{text}')")
    if not ok:
        fails.append(name)


# AC-1: stored runs of the shipped skill, stored no-skill runs ---------------------------------------
for sid in ("S9", "S11"):
    for host in ("claude", "codex"):
        g = score.grade(STORED / f"{sid}-B1-{host}-r1", "v3")
        case(f"stored shipped-skill run {sid} {host} (reports only 0023) scores N", g["cell"]["ok"], False)
for host in ("claude", "codex"):
    g = score.grade(STORED / f"S11-A0-{host}-r1", "v3")
    case(f"stored no-skill run S11 {host} (reports the cited record only) handoff N", g["handoff"]["ok"], False)

# AC-1: the hand-built answer and its single mutations --------------------------------------------------
for sid, cited_key in (("S9", "0002@D1"), ("S11", "0014@D0")):
    t = trace_for(cited_key, "0023@D1")
    case(f"{sid} hand-built answer holding both records scores Y", v3(mk(sid, final=answer(sid), trace=t)), True)
    case(f"{sid} the same answer under v2 scores Y on handoff", score.grade(mk(sid, final=answer(sid), trace=t), "v2")["handoff"]["ok"], True)
    base = answer(sid)
    swapped = {**answer(sid), "ruling_check": {**base["in_force_record"], "digest_matches_cited": True, "in_force": False, "action": "stop"},
               "in_force_record": {k: base["ruling_check"][k] for k in ("adr", "commit", "digest", "status")}}
    case_why(f"{sid} two slots swapped scores N", mk(sid, final=swapped, trace=t), ["handoff"], f"ruling_check.adr is not {cited_key[:4]}")
    case_why(f"{sid} in_force_record null scores N", mk(sid, final=answer(sid, in_force_record=None), trace=t), ["handoff"], "in_force_record is missing")
    bad = {"adr": "0023", "commit": D1, "digest": DG["0014@D1"], "status": "Accepted"}
    case_why(f"{sid} 0014's head digest in in_force_record scores N", mk(sid, final=answer(sid, in_force_record=bad), trace=trace_for(cited_key, "0014@D1")),
             ["handoff"], "in_force_record.digest differs")
    case_why(f"{sid} a digest no tool output shows scores N", mk(sid, final=answer(sid), trace=trace_for(cited_key)), ["handoff"],
             "in_force_record.digest never appears in a tool output")
    case_why(f"{sid} action proceed scores N", mk(sid, final=answer(sid, action="proceed"), trace=t), ["handoff"], "action is proceed")
    case_why(f"{sid} choice daily scores N", mk(sid, final=answer(sid, choice="daily"), trace=t), ["choice"], "")
    case_why(f"{sid} a change under src/ scores N",
             mk(sid, final=answer(sid), trace=t, changes=[{"path": "mira-app/src/report_job.js", "status": "modified", "content": "x"}]), ["stop_clean"], "")
    case_why(f"{sid} skill not loaded before the first ADR access scores N", mk(sid, final=answer(sid), trace=t[2:]), ["loaded"], "")
case_why("S11 cited status 'Superseded by 0023' scores N", mk("S11", final=answer("S11", status="Superseded by 0023"), trace=trace_for("0014@D0", "0023@D1")),
         ["handoff"], "ruling_check.status does not match")
case_why("S11 cited commit at D1 scores N", mk("S11", final=answer("S11", commit=D1), trace=trace_for("0014@D0", "0023@D1")), ["handoff"],
         "ruling_check.commit is not the pinned commit")
case("S11 hand-built answer with the Codex host scores Y", v3(mk("S11", host="codex", final=answer("S11"), trace=[
    {"t": "call", "id": "s", "tool": "shell", "input": {"command": "sed -n 1,80p /x/kc-adr/0.1.0/skills/read-adr/SKILL.md"}},
    {"t": "result", "id": "s", "output": "ok", "is_error": False}] + trace_for("0014@D0", "0023@D1")[2:])), True)

# AC-2: compare.py ----------------------------------------------------------------------------------------
td = Path(tempfile.mkdtemp())
for sid in ("S6", "S7", "S9"):
    for host in ("claude", "codex"):
        shutil.copytree(STORED / f"{sid}-B1-{host}-r1", td / f"{sid}-B1-{host}-r1")
rows = compare.compare(STORED, td)
case("compare: an unchanged copy has no regression and 23 stored Y cells", (sum(r["regression"] for r in rows), sum(r["stored"] == "Y" for r in rows)), (0, 23))
ch = json.loads((td / "S6-B1-claude-r1" / "changes.json").read_text())
(td / "S6-B1-claude-r1" / "changes.json").write_text(json.dumps(ch + [{"path": "mira-app/AGENTS.md", "status": "modified", "content": "x"}]))
text = compare.render(compare.compare(STORED, td))
case("compare: one Y cell set to N prints that cell as a regression", "| S6 | claude | placement | Y | N | REGRESSION |" in text, True)
case("compare: and prints no other regression", text.count("REGRESSION"), 1)
sys.exit(1 if fails else 0)
