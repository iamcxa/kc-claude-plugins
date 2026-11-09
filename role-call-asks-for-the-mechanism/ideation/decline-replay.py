import subprocess, sys, pathlib, shutil, re
Q, M = sys.argv[1], pathlib.Path(sys.argv[2])
BASE = "/tmp/rcm/proto/role_triggers.base.py"; PROTO = "/tmp/rcm/proto/role_triggers.py"
answers = {
 "A1 impl-4 (verbatim, FO transcript 2026-11-09T07:50:32Z)": "These two bugs are in the booking draft we're delivering. Tests can reproduce them now, and if we deleted those two acceptance criteria, the release would ship data loss.",
 "A2 validation-2 (verbatim, FO transcript 2026-11-09T08:12:15Z)": "The goal is still the original one: an owner picks the car once and can always see how to finish the booking. The remaining gaps can all be tested now.",
 "A3 package-feedback.md quoted form": "the outcome is unchanged; the gap is testable now",
 "C1 control: reasoned form": "unrelated: F1 explicit home exit keeps the draft; F2 late 201 response after Back",
 "C2 control: one finding only": "unrelated: F1 explicit home exit keeps the draft",
 "C3 control: same cause twice": "unrelated: F1 late async write; F2 late async write",
}
rows = []
for rev in ("ee29b0a8", "27f04824", "03829bf0"):
    for label, reason in [("none", None)] + list(answers.items()):
        d = M / "repo"; shutil.rmtree(d, ignore_errors=True); d.mkdir()
        subprocess.run(f"git -C {Q} archive {rev} owner-vehicle-kept-after-name.md owner-vehicle-kept-after-name/dispatch | tar -x -C {d}", shell=True, check=True)
        t = d / "owner-vehicle-kept-after-name.md"; s = t.read_text()
        if reason is not None:
            s = s.replace("\n## Captain amendments", f"\nReviewer: kc-dev-flow-2:chief-engineer not run 2026-11-09: {reason}\n\n## Captain amendments", 1)
            assert "not run 2026-11-09" in s
        t.write_text(s)
        subprocess.run("git init -q && git add -A && git -c user.name=x -c user.email=x@x commit -qm s", shell=True, cwd=d, check=True)
        out = {}
        for name, script in (("current", BASE), ("proto", PROTO)):
            r = subprocess.run([sys.executable, "-B", script, str(d), "owner-vehicle-kept-after-name"], capture_output=True, text=True)
            ce = [l for l in r.stdout.splitlines() if "chief-engineer" in l and l.startswith("next:")]
            out[name] = "CE owed" if ce else "CE clear"
            if name == "proto" and ce and rev == "27f04824" and label == "none":
                (M / "proto-owed-line.txt").write_text(ce[0] + "\n")
            if name == "current" and ce and rev == "27f04824" and label == "none":
                (M / "current-owed-line.txt").write_text(ce[0] + "\n")
        rows.append((rev, label, out["current"], out["proto"]))
print("| state rev | decline reason | 0.36.0 | prototype |\n|---|---|---|---|")
for r in rows: print("| " + " | ".join(r) + " |")
