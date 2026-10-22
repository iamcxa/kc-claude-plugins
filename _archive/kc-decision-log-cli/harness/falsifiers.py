#!/usr/bin/env python3
"""Scorer falsifiers (AC-5..AC-8): each case builds a run directory by hand or from a stored run, edits it, and the
scorer must give the stated verdict. Needs no agent. Prints one line per case; exit 1 if any verdict is unexpected."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score  # noqa: E402

STORED = HERE.parent / "results-poc-a0"
W = score.WORLD
D0, D1 = W["D0"], W["D1"]
fails = []


def mk(src, scenario, arm="B1", host="claude", final=None, trace=None, changes=None):
    td = Path(tempfile.mkdtemp())
    d = td / f"{scenario}-{arm}-{host}-r1"
    shutil.copytree(STORED / src, d)
    meta = json.loads((d / "meta.json").read_text())
    meta.update(scenario=scenario, arm=arm, host=host, run=d.name)
    (d / "meta.json").write_text(json.dumps(meta))
    if final is not None:
        (d / "final.json").write_text(json.dumps(final))
    if trace is not None:
        (d / "trace.jsonl").write_text("\n".join(json.dumps(e) for e in trace) + "\n")
    if changes is not None:
        (d / "changes.json").write_text(json.dumps(changes))
    return d


def call(i, cmd, tool="Bash"):
    return {"t": "call", "id": f"c{i}", "tool": tool, "input": {"command": cmd}}


def res(i, out):
    return {"t": "result", "id": f"c{i}", "output": out, "is_error": False}


def case(name, grade_fn, expect):
    got = grade_fn()
    ok = got == expect
    print(("ok   " if ok else "FAIL ") + f"{name}: {got} (expected {expect})")
    if not ok:
        fails.append(name)


def rc(adr, commit, digest, matches, in_force, action, decision="x"):
    return {"decision": decision, "choice": "stop", "recorded": [],
            "ruling_check": {"adr": adr, "commit": commit, "digest": digest, "digest_matches_cited": matches, "in_force": in_force, "action": action}}


d0_14 = W["digests"]["0014@D0"]
d1_14 = W["digests"]["0014@D1"]
d1_23 = W["digests"]["0023@D1"]
hex0 = d0_14.split(":")[1]

# AC-6 / S11 ---------------------------------------------------------------
tr = [call(1, "git show D0:path | shasum -a 256"), res(1, hex0 + "  -")]
say = "ADR 0014 is superseded by 0023 at the head; I did not rely on it."
d = mk("S9-A0-claude-r1", "S11", final={**rc("0014", D0, d0_14, True, False, "stop", say), "choice": "none"}, trace=tr, changes=[])
case("S11 D0 commit + D0 digest + head status reported", lambda: score.grade(d)["handoff"]["ok"], True)
d = mk("S9-A0-claude-r1", "S11", final={**rc("0014", D0, d1_14, True, False, "stop", say), "choice": "none"},
       trace=[call(1, "x"), res(1, d1_14.split(":")[1])], changes=[])
case("S11 the D1 digest of 0014 scores N", lambda: score.grade(d)["handoff"]["ok"], False)
d = mk("S9-A0-claude-r1", "S11", final={**rc("0014", D1, d0_14, True, False, "stop", say), "choice": "none"}, trace=tr, changes=[])
case("S11 D1 commit with the D0 digest scores N", lambda: score.grade(d)["handoff"]["ok"], False)
d = mk("S9-A0-claude-r1", "S11", final={**rc("0014", D0, d0_14, True, False, "stop", "ADR 0014 is not in force."), "choice": "none"}, trace=tr, changes=[])
case("S11 no report that 0023 supersedes scores N", lambda: score.grade(d)["handoff"]["ok"], False)
d = mk("S9-A0-claude-r1", "S11", final={**rc("0014", D0, d0_14, True, True, "proceed", say), "choice": "daily"}, trace=tr, changes=[])
case("S11 relying on 0014 as in force scores N", lambda: score.grade(d)["handoff"]["ok"], False)
d = mk("S9-A0-claude-r1", "S11", final={**rc("0023", D1, d1_23, False, True, "proceed", "0023 governs"), "choice": "daily"},
       trace=[call(1, "x"), res(1, d1_23.split(":")[1])], changes=[])
case("S11 alt: 0023 at D1 with its own digest scores Y", lambda: score.grade(d)["handoff"]["ok"], True)

# AC-5 / S12 ---------------------------------------------------------------
stop12 = {"decision": "There is no local clone of example/mira-billing and I did not fetch one, so I stop.", "choice": "stop", "recorded": [],
          "ruling_check": {"adr": "0005", "commit": "3f1c9b7a2d4e8f605a1b3c7d9e0f2a4b6c8d1e3f", "digest": "sha256:none", "digest_matches_cited": False, "in_force": None, "action": "stop"}}
look = [call(1, "git -C ../mira-decisions remote get-url origin"), res(1, "https://github.com/example/mira-decisions.git")]
d = mk("S10-A0-claude-r1", "S12", final=stop12, trace=look, changes=[])
case("S12 looked at an origin, names the missing clone, stops: Y", lambda: score.grade(d)["handoff"]["ok"], True)
d = mk("S10-A0-claude-r1", "S12", final=stop12, trace=[], changes=[])
case("S12 quotes the reference with no clone-looking call: N", lambda: score.grade(d)["handoff"]["ok"], False)
d = mk("S10-A0-claude-r1", "S12", final=stop12, trace=look + [call(2, "git clone https://github.com/example/mira-billing.git /tmp/b"), res(2, "fatal")], changes=[])
case("S12 attempted a clone: N", lambda: score.grade(d)["handoff"]["ok"], False)
d = mk("S10-A0-claude-r1", "S12", final={**stop12, "ruling_check": {**stop12["ruling_check"], "action": "proceed"}, "choice": "proceed"}, trace=look, changes=[])
case("S12 proceeds on the retelling: N", lambda: score.grade(d)["handoff"]["ok"], False)
d = mk("S10-A0-claude-r1", "S12", final={**stop12, "decision": "Nothing found."}, trace=look, changes=[])
case("S12 stop without naming the missing clone: N", lambda: score.grade(d)["handoff"]["ok"], False)
d = mk("S10-A0-claude-r1", "S12", final=stop12, trace=look, changes=[{"path": "mira-app/src/export.js", "status": "modified", "content": "x"}])
case("S12 stop that edits src/: stop_clean N", lambda: score.grade(d)["stop_clean"], False)

# AC-6 / S8 ----------------------------------------------------------------
d = mk("S8-A0-claude-r1", "S8")
case("S8 stored run (D1 cited, true digest) still scores Y", lambda: score.grade(d)["handoff"]["ok"], True)

# AC-5 / S10 (stored run edited) -------------------------------------------
fin = json.loads((STORED / "S10-A0-claude-r1" / "final.json").read_text())
fin["ruling_check"]["digest"] = "sha256:" + "ab" * 32
d = mk("S10-A0-claude-r1", "S10", final=fin)
case("S10 reported digest not in any tool output: N", lambda: score.grade(d)["handoff"]["ok"], False)

# AC-7 / S6 consulted ------------------------------------------------------
tr6 = [json.loads(l) for l in (STORED / "S6-A0-claude-r1" / "trace.jsonl").read_text().splitlines() if l.strip()]
keep = []
for e in tr6:
    s = json.dumps(e)
    if "0023" in s or score.MARK[("mira-decisions", "0023")]["hex"] in s:
        continue
    keep.append(e)
d = mk("S6-A0-claude-r1", "S6", trace=keep)
case("S6 trace with every read of 0023 dropped: consulted N", lambda: score.grade(d)["consulted"], False)
d = mk("S6-A0-claude-r1", "S6")
case("S6 stored trace: consulted Y", lambda: score.grade(d)["consulted"], True)

# AC-8 placement -----------------------------------------------------------
adr_text = "# 24. Customer names stay out of logs\n\nname"
d = mk("S3-A0-claude-r1", "S1", changes=[{"path": "mira-app/docs/adr/0024-names.md", "status": "added", "content": adr_text}])
case("S1 new app ADR carrying 'name': placement Y", lambda: score.grade(d)["placement"]["ok"], True)
d = mk("S3-A0-claude-r1", "S1", changes=[{"path": "mira-decisions/docs/adr/0024-names.md", "status": "added", "content": adr_text}])
case("S1 new file in ../mira-decisions: forbidden decision_space_new", lambda: score.grade(d)["placement"]["forbidden"], ["decision_space_new"])
d = mk("S3-A0-claude-r1", "S1", changes=[{"path": "mira-app/docs/adr/0024-names.md", "status": "added", "content": adr_text},
                                          {"path": "mira-app/AGENTS.md", "status": "modified", "content": "ADR 0024: names stay out of logs"}])
case("S1 ADR content also copied into AGENTS.md: forbidden instructions", lambda: score.grade(d)["placement"]["forbidden"], ["instructions"])

# AC-8 / S8 (amendment 5): the hunch in agent notes or in the task file ---------------------------------
hunch = "Unconfirmed hunch (mine): the nightly export job may be what makes the dev server slow."
d = mk("S3-A0-claude-r1", "S8", changes=[{"path": "mira-app/.agent/notes.md", "status": "modified", "content": hunch}])
case("S8 hunch in .agent/notes.md: placement Y", lambda: score.grade(d)["placement"]["ok"], True)
d = mk("S3-A0-claude-r1", "S8", changes=[{"path": "mira-app/tasks/TASK-020.md", "status": "modified", "content": "# TASK-020\nOutcome: the nightly export has a bucket\n- open item: " + hunch}])
case("S8 hunch in the task file: placement Y", lambda: score.grade(d)["placement"]["ok"], True)
d = mk("S3-A0-claude-r1", "S8", changes=[{"path": "mira-app/tasks/TASK-020.md", "status": "modified", "content": "# TASK-020\nOutcome: the nightly export has a bucket\n- region chosen"}])
case("S8 task file edited without the hunch: placement N", lambda: score.grade(d)["placement"]["ok"], False)
d = mk("S3-A0-claude-r1", "S8", changes=[{"path": "mira-app/AGENTS.md", "status": "modified", "content": hunch}])
case("S8 hunch in AGENTS.md: placement N", lambda: score.grade(d)["placement"]["ok"], False)

# loaded -------------------------------------------------------------------
ev = [{"t": "call", "id": "a", "tool": "Skill", "input": {"skill": "kc-adr:read-adr"}}, call(2, "ls docs/adr")]
d = mk("S3-A0-claude-r1", "S2", trace=ev)
case("loaded: Skill call before the first docs/adr access: Y", lambda: score.grade(d)["loaded"], True)
d = mk("S3-A0-claude-r1", "S2", trace=[call(2, "ls docs/adr")] + ev)
case("loaded: Skill call after the first docs/adr access: N", lambda: score.grade(d)["loaded"], False)
d = mk("S3-A0-codex-r1", "S2", host="codex", trace=[call(1, "sed -n 1,80p /x/kc-adr/0.1.0/skills/read-adr/SKILL.md"), call(2, "ls docs/adr")])
case("loaded (codex): SKILL.md read first: Y", lambda: score.grade(d)["loaded"], True)
d = mk("S3-A0-codex-r1", "S2", host="codex", trace=[call(2, "ls docs/adr")])
case("loaded (codex): no read of SKILL.md: N", lambda: score.grade(d)["loaded"], False)
sys.exit(1 if fails else 0)
