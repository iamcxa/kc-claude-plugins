import shutil, subprocess, sys
from pathlib import Path
SRC = Path("/tmp/val643c6/pr/kc-dev-flow-2"); W = Path("/tmp/val643c6/mut"); 
M = [
 ("CLOSED filter removed", 'p["state"] in ("OPEN", "MERGED")', 'p["state"] in ("OPEN", "MERGED", "CLOSED")'),
 ("extensions: read removed (every reviewer read)", '"codex" in listed, "copilot" in listed', 'True, True'),
 ("settle window 60 -> 0", "SETTLE_SECONDS = 60", "SETTLE_SECONDS = 0"),
 ("BLOCKED guard removed", ' and snap.get("merge-state") != "BLOCKED"', ''),
 ("settled-unchecked not treated as green", '(snap.get("checks") == "none" and snap.get("unchecked") == "settled")', 'False'),
 ("green draft: mark-ready line removed", 'if green and snap.get("draft") else []', 'if False else []'),
 ("keep-one-wait lines removed", 'out += already + [f"next: run `{wait} wait` in the background, unless one is running.",\n                          "next: when it exits, do the next: lines it prints."]', 'out += already'),
 ("observer keep-out line removed", 'out += [f"next: keep {slug} out of pr-merge\'s scan in this pass.", *done.stdout.splitlines()]', 'out += done.stdout.splitlines()'),
 ("after pr-merge lines removed", '''out += [f"next: let pr-merge record {slug}.", f"after pr-merge: run `{check}`.",
                        "after pr-merge: do each next: line it prints."]''', 'out += [f"next: let pr-merge record {slug}."]'),
 ("record-a-PR lines removed", '''                    out += [f"next: run `spacedock status --workflow-dir {shlex.quote(str(workflow))} --set {slug} pr={ref}`.",
                            f"next: run `spacedock state commit {slug} --workflow-dir {shlex.quote(str(workflow))}`."]''', '                    pass'),
 ("worktree-absent reminder removed", 'out.append(f"next: record {slug}\'s PR with status --set {slug} pr=<owner/repo>#<N>; its worktree is not on this machine.")', 'pass'),
 ("unchecked not a wake-up outcome", '"unchecked": {"settled"}', '"unchecked": set()'),
 ("wait: idle-hooks line removed", 'return ["next: run the idle hooks now."]', 'return []'),
 ("facts line: reviewer outcome dropped", 'parts.append(f"{name}={snap.get(name, \'-\')}" + ("" if evidence in ("-", None) else f" {evidence}"))', 'pass'),
 ("merge-ask line re-added on green ready PR", 'return [f"next: mark {ref} ready if Delivery authority allows."] if green and snap.get("draft") else []', 'return [f"next: mark {ref} ready if Delivery authority allows."] if green and snap.get("draft") else ([f"next: ask for merge: run delivery_gate.py check for {ref}."] if green else [])'),
 ("hold line re-added while a reviewer is unsettled", 'def next_for(ref, snap):\n', 'def next_for(ref, snap):\n    if snap.get("codex") in ("running", "not-reviewed"):\n        return [f"next: do not ask to merge {ref}; reviewers not read."]\n'),
]
only = sys.argv[1:]
for i, (name, old, new) in enumerate(M, 1):
    if only and str(i) not in only: continue
    shutil.rmtree(W, ignore_errors=True); shutil.copytree(SRC, W, ignore=shutil.ignore_patterns("__pycache__"))
    f = W / "scripts/pr_watch.py"; t = f.read_text()
    if old not in t: print(f"M{i} {name}: PATTERN NOT FOUND"); continue
    f.write_text(t.replace(old, new, 1))
    try:
        d = subprocess.run([sys.executable, "-B", str(W / "scripts/test_pr_watch.py")], capture_output=True, text=True, timeout=150)
        bad = sorted({l.split()[1] for l in (d.stderr + d.stdout).splitlines() if l.startswith(("FAIL:", "ERROR:"))})
        print(f"M{i} {name}: exit {d.returncode}; red: {', '.join(bad) or '-'}")
    except subprocess.TimeoutExpired:
        print(f"M{i} {name}: TIMEOUT 150 s (hang counts as red)")
