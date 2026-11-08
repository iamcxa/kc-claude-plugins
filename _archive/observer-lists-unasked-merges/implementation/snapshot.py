"""Replay the approved saved GitHub window against committed local state refs.
Usage: python3 -B snapshot.py CODE_ROOT STATE_ROOT OUT
The separate replay-live.log records the actual network run.
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile
code, state, out = map(pathlib.Path, sys.argv[1:])
out.mkdir(parents=True, exist_ok=True)
prs = json.loads((state / "observer-lists-unasked-merges/poc/merged-window.json").read_text())
with tempfile.TemporaryDirectory(prefix="merge-audit-snapshot-") as tmp:
    tmp = pathlib.Path(tmp)
    fixture = tmp / "prs.json"
    bindir = tmp / "bin"
    bindir.mkdir()
    (bindir / "gh").write_text("#!" + sys.executable + "\nimport pathlib\nprint(pathlib.Path(" + repr(str(fixture)) + ").read_text())\n")
    native_git = shutil.which("git")
    (bindir / "git").write_text("#!" + sys.executable + "\nimport os,sys\n"
        "if 'fetch' in sys.argv[1:]: sys.exit(0)\n"
        "os.execv(" + repr(native_git) + ", [" + repr(native_git) + "] + sys.argv[1:])\n")
    for p in bindir.iterdir(): p.chmod(0o755)
    def replay(name, selected, expected):
        fixture.write_text(json.dumps(selected))
        p = subprocess.run([sys.executable, "-B", str(code / "kc-dev-flow-2/scripts/merge_audit.py"),
                            str(state), "merge-check-reads-two-pr-tasks", "--rev",
                            "8ffd6dfa3e021c1967aeaeabd7cf0cb61db48aae"], capture_output=True, text=True,
                           env={**os.environ, "PATH": str(bindir) + os.pathsep + os.environ["PATH"]})
        (out / (name + ".log")).write_text(p.stdout + p.stderr)
        assert p.returncode == expected, p.stdout + p.stderr
        return p.stdout
    whole = replay("window", prs, 1)
    assert "carried: 54 of 82\n" in whole
    expected = {
        "release": [707,717,723,731,739,746,752,760,768],
        "sync": [715,718,725,733,741,747,753,761,781],
        "learning": [726,782]}
    for kind, numbers in expected.items():
        assert kind + ": " + " ".join("#" + str(n) for n in numbers) + "\n" in whole
    import re
    assert [int(n) for n in re.findall(r"^no ask record: #(\d+)", whole, re.M)] == [704,762,774,776,778,784,785,789]
    assert "no ask record: #785 head 0c38dd60b562" in whole
    carried = [p for p in prs if p["number"] == 727]
    assert "carried: 1 of 1" in replay("727-carried", carried, 0)
    changed = [{**p, "headRefOid": "0" * 40} for p in carried]
    assert "head differs: #727 head 000000000000" in replay("727-wrong-head", changed, 1)
print("Saved window matches all AC-1 sets; #727 is carried, and changing its head produces a violation.")
