"""Throwaway probe: replay the two trial designs and edge variants through the probe check.
usage: python3 -B cases.py <design_surfaces.py> <run1.md> <run2.md> <out-dir>"""
import json, re, subprocess, sys
from pathlib import Path

checker, run1, run2, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
out.mkdir(parents=True, exist_ok=True)
r1, r2 = run1.read_text(), run2.read_text()
AC1 = re.search(r"^\*\*AC-1\*\*.*$", r2, re.M).group(0)
AC2 = re.search(r"^\*\*AC-2\*\*.*$", r2, re.M).group(0)
no_exit_ac2 = r2.replace(AC2, AC2.replace("exit 0, ", ""))
falsifier_only = r2.replace(AC1, "**AC-1** — The probe refuses an empty record. Evidence: read the design. "
                                 "Falsifier: if the check exits 1 the run writes `evidence/AC-1.log` from command `python3 x.py`.")
heading = "\n### Not provable now\n\n"
APPROVED = """gates:
    version: 1
    records:
        - id: gate:x:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:x-ideation-1
              resolution:
                type: Resolution
                id: resolution:spacedock:x:ideation:1
                by: person:captain
                at: "2026-11-12T00:00:00Z"
                decision: approve
                reason: 'r'
              application:
                target-stage: implementation
                state: pending
"""
cases = [
    ("run1-replay", r1, 1, "Pilot criterion AC-3 "),
    ("run2-replay", r2, 0, None),
    ("run2-AC2-exit-removed", no_exit_ac2, 1, "Pilot criterion AC-2 has no exit"),
    ("run2-AC2-exit-removed-unprovable-with-reason", no_exit_ac2.replace("\n## Acceptance criteria",
        heading + "- AC-2: the live provider is unavailable offline, so no exit was observed.\n\n## Acceptance criteria", 1), 0, None),
    ("run2-AC2-exit-removed-unprovable-bare-id", no_exit_ac2.replace("\n## Acceptance criteria",
        heading + "- AC-2\n\n## Acceptance criteria", 1), 1, "Pilot criterion AC-2 has no exit"),
    ("run2-AC1-record-only-in-falsifier", falsifier_only, 1, "Pilot criterion AC-1 has no command, exit, output path"),
    ("run1-replay-status-implementation", r1.replace("status: ideation", "status: implementation", 1), 0, None),
    ("run1-replay-profile-poc", r1.replace("profile: pilot", "profile: poc", 1), 0, None),
    ("run1-replay-design-approved-status-still-ideation", r1.replace("status: ideation\n", "status: ideation\n" + APPROVED, 1), 0, None),
    ("known-limit-planned-clause-passes", r2.replace(AC1, "**AC-1** — X holds. Evidence: `python3 t.py` must exit 0 and write `out.log`. "
                                                    "Falsifier: removing X."), 0, None),
]
results = []
for name, text, want_exit, want_reason in cases:
    path = out / name / f"{name}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text(text)
    cmd = [sys.executable, "-B", checker, "check", str(path)]
    done = subprocess.run(cmd, capture_output=True, text=True)
    (out / f"{name}.stdout.txt").write_text(done.stdout)
    proof_lines = [l for l in done.stdout.splitlines() if "Pilot criterion" in l]
    ok = done.returncode == want_exit and (want_reason is None and not proof_lines or
                                           want_reason is not None and any(want_reason in l for l in proof_lines))
    results.append(dict(case=name, command=" ".join(cmd), exit=done.returncode, want_exit=want_exit,
                        proof_lines=proof_lines, output=str(out / f"{name}.stdout.txt"), ok=ok))
(out / "cases.json").write_text(json.dumps(results, indent=1))
for r in results:
    print(("PASS " if r["ok"] else "FAIL ") + r["case"], r["exit"], r["proof_lines"][:1])
sys.exit(0 if all(r["ok"] for r in results) else 1)
