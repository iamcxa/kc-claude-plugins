"""Throwaway probe: count Pilot task files the probe proof-record rule refuses under each exemption option.
usage: python3 -B corpus.py <design_surfaces.py> <out.json> <label>=<state-root> ...   (task files: <root>/*.md, <root>/_archive/*.md)"""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

checker, out = sys.argv[1], Path(sys.argv[2])
CUTOFF = "2026-11-13T09:27:23Z"  # PR 864 merge time; the probe stands in for a release date
modes = {
    "as-is (stage+profile)": ("stage", None),
    "forced ideation, no exemption": ("stage", "ideation"),
    "forced ideation, Probe line required": ("probe-line", "ideation"),
    "forced ideation, started>=PR864 merge": (f"started>={CUTOFF}", "ideation"),
}
report = {}
for arg in sys.argv[3:]:
    label, root = arg.split("=", 1)
    root = Path(root)
    files = [p for p in sorted(list(root.glob("*.md")) + list(root.glob("_archive/*.md")))
             if re.search(r"\A---\n(?:.*\n)*?profile:[ \t]*pilot[ \t]*\n(?:.*\n)*?---\n", p.read_text(errors="replace"))]
    counts = {"pilot task files": len(files),
              "in ideation now": sum(bool(re.search(r"^status:[ \t]*ideation\b", p.read_text(), re.M)) for p in files),
              "with Probe line": sum(bool(re.search(r"^(?:#{1,4}[ \t]*)?Probe\b", p.read_text(), re.M)) for p in files)}
    for mode, (env, force) in modes.items():
        refused = clean_with_criteria = 0
        with tempfile.TemporaryDirectory() as tmp:
            for p in files:
                text = p.read_text()
                if force:  # an ideation briefing copy: status ideation, no gate resolution yet
                    text = re.sub(r"^status:.*$", f"status: {force}", text, count=1, flags=re.M)
                    text = re.sub(r"^gates:\n(?:[ \t]+.*\n|\n)*", "", text, count=1, flags=re.M)
                copy = Path(tmp) / p.name
                copy.write_text(text)
                done = subprocess.run([sys.executable, "-B", checker, "check", str(copy)], capture_output=True, text=True,
                                      env={**os.environ, "PROBE_EXEMPT": env})
                hit = any("Pilot criterion" in l for l in done.stdout.splitlines())
                refused += hit
                clean_with_criteria += (not hit) and bool(re.search(r"^[ \t]*(?:[-*+][ \t]+)?\*\*AC-", text, re.M))
        counts[f"refused: {mode}"] = refused
        counts[f"declared criteria, none refused: {mode}"] = clean_with_criteria
    report[label] = counts
out.write_text(json.dumps(report, indent=1))
print(json.dumps(report, indent=1))
