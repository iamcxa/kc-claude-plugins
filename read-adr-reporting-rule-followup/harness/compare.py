#!/usr/bin/env python3
"""AC-2: prints the 24 cells (S6, S7, S9 x host x consulted-or-handoff, placement, choice, loaded) as stored value, new value.

  python3 compare.py [--new DIR] [--stored DIR]

Both sides are graded under the stored expectations (score rule v2). A cell that is Y in the stored run and N in the new run
is a regression; exit 1 if there is one. The stored runs are the arm-B1 runs of the archived kc-decision-log-cli task.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score  # noqa: E402

STORED = HERE.parent.parent / "_archive" / "kc-decision-log-cli" / "results"
SCENARIOS = ["S6", "S7", "S9"]
HOSTS = ["claude", "codex"]
MEASURES = ["consulted-or-handoff", "placement", "choice", "loaded"]


def cell_value(g, measure):
    if g is None:
        return "-"
    if measure == "consulted-or-handoff":
        v = g["consulted"] if "consulted" in g else g["handoff"]["ok"]
    elif measure == "placement":
        v = g["placement"]["ok"]
    elif measure == "choice":
        v = g["choice_ok"]
    else:
        v = g.get("loaded")
    return "-" if v is None else ("Y" if v else "N")


def graded(path):
    return {(g["scenario"], g["host"]): g for g in score.grade_dir(Path(path), "v2") if g["arm"] == "B1" and g["rep"] == 1}


def compare(stored_dir, new_dir):
    stored, new = graded(stored_dir), graded(new_dir)
    rows = []
    for sid in SCENARIOS:
        for host in HOSTS:
            for m in MEASURES:
                s, n = cell_value(stored.get((sid, host)), m), cell_value(new.get((sid, host)), m)
                rows.append({"scenario": sid, "host": host, "measure": m, "stored": s, "new": n,
                             "regression": s == "Y" and n == "N"})
    return rows


def render(rows):
    out = ["| Scenario | Host | Measure | Stored | New | |", "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        out.append(f"| {r['scenario']} | {r['host']} | {r['measure']} | {r['stored']} | {r['new']} | {'REGRESSION' if r['regression'] else ''} |")
    stored_y = sum(r["stored"] == "Y" for r in rows)
    new_y = sum(r["new"] == "Y" for r in rows)
    out.append("")
    out.append(f"{len(rows)} cells; stored Y {stored_y}, new Y {new_y}, regressions {sum(r['regression'] for r in rows)}.")
    return "\n".join(out)


def main():
    arg = lambda k, d: Path(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
    rows = compare(arg("--stored", STORED), arg("--new", HERE.parent / "results"))
    print(render(rows))
    sys.exit(1 if any(r["regression"] for r in rows) else 0)


if __name__ == "__main__":
    main()
