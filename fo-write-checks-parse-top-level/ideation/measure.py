"""Base-versus-candidate verdicts over every task file in four dev2 state checkouts.
usage: python3 -B -I measure.py <base-scripts-dir> <candidate-scripts-dir> [--gate-only]
--gate-only skips the design_surfaces runs (about 8 minutes on this machine for all of them)."""
import importlib.util, json, subprocess, sys, io, contextlib
from pathlib import Path

HOME = Path.home() / "conductor"
CHECKOUTS = {
    "kc-claude-plugins": "workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state",
    "qnow": "repos/qnow-adopt-dev2/docs/dev2/.spacedock-state",
    "subspace-relay": "workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state",
    "subspace-web": "workspaces/subspace-web/dev2-fo/docs/dev2/.spacedock-state",
}

def load(path, name):
    sys.path.insert(0, str(path))
    spec = importlib.util.spec_from_file_location(name, path / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.path.pop(0)
    return mod

def mods(root):
    root = Path(root)
    for n in ("decision_ledger", "number_guards", "validation_security", "design_surfaces", "delivery_gate"):
        sys.modules.pop(n, None)
    ds = load(root, "design_surfaces")
    dg = load(root, "delivery_gate")
    return ds, dg

def run_check(ds, task, seed):
    out = io.StringIO()
    argv = ["check", *(["--seed"] if seed else []), str(task)]
    with contextlib.redirect_stdout(out):
        code = ds.main(argv)
    return code, out.getvalue().replace(str(task.name), "T")

def tasks(state):
    files = subprocess.run(["git", "-C", str(state), "ls-files", "*.md"], capture_output=True, text=True).stdout.split()
    return [f for f in files if "/" not in f.replace("_archive/", "", 1) and f != "README.md"]

def revisions(state, rel):
    log = subprocess.run(["git", "-C", str(state), "log", "--format=%H", "--follow", "--", rel], capture_output=True, text=True).stdout.split()
    for sha in log:
        show = subprocess.run(["git", "-C", str(state), "show", f"{sha}:{rel}"], capture_output=True)
        if show.returncode == 0:
            yield show.stdout.decode("utf-8", "replace")

def gate_texts(state):
    for f in subprocess.run(["git", "-C", str(state), "ls-files", "*/briefing-*/index.json"], capture_output=True, text=True).stdout.split():
        try:
            yield f, json.loads((state / f).read_text()).get("question", "")
        except (OSError, ValueError):
            pass

def main(base_dir, cand_dir, flag=""):
    skip = flag == "--gate-only"
    (bds, bdg), (cds, cdg) = mods(base_dir), mods(cand_dir)
    total = {"files": 0, "revisions": 0, "gate texts": 0, "gate text bodies": 0}
    changed = []
    for label, rel in CHECKOUTS.items():
        state = HOME / rel
        for f in tasks(state):
            total["files"] += 1
            text = (state / f).read_text(errors="replace")
            for mode in () if skip else (False, True):
                b, c = run_check(bds, state / f, mode), run_check(cds, state / f, mode)
                if b != c:
                    changed.append((label, f, "check --seed" if mode else "check", b, c))
            for rev in () if skip else revisions(state, f):
                total["revisions"] += 1
                if bds.scope_lines(rev) != cds.scope_lines(rev):
                    changed.append((label, f, "scope_lines at a committed revision", len(bds.scope_lines(rev)), len(cds.scope_lines(rev))))
                    break
            total["gate text bodies"] += 1
            for name, fn in (("declined_items", "declined_items"), ("unreasoned_items", "unreasoned_items")):
                if getattr(bdg, fn)(text) != getattr(cdg, fn)(text):
                    changed.append((label, f, f"{name} over the task body", getattr(bdg, fn)(text)[:3], getattr(cdg, fn)(text)[:3]))
        for name, q in gate_texts(state):
            total["gate texts"] += 1
            for fn in ("declined_items", "unreasoned_items"):
                if getattr(bdg, fn)(q) != getattr(cdg, fn)(q):
                    changed.append((label, name, f"{fn} over the gate question", getattr(bdg, fn)(q)[:3], getattr(cdg, fn)(q)[:3]))
    print(total)
    print(len(changed), "verdict changes")
    for row in changed:
        print(row)

main(*sys.argv[1:4])
