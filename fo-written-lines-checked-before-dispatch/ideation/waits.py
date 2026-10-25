"""Replay 'supersedes AC-N but it is still declared' over every committed revision of every task, read only.
usage: python3 -B -I fwl_waits.py <base scripts dir> <candidate scripts dir>
For each revision with a Captain amendments section, counts the 'still declared' errors the base prints, and the
ones the candidate still prints once an amendment waits until a dispatch checklist names it (read at the same commit)."""
import importlib.util, subprocess, sys
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
    spec = importlib.util.spec_from_file_location(name + str(abs(hash(str(path)))), Path(path) / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.path.pop(0)
    return mod


def git(state, *args):
    return subprocess.run(["git", "-C", str(state), *args], capture_output=True, text=True).stdout


def main(base_dir, cand_dir):
    base, cand = load(base_dir, "design_surfaces"), load(cand_dir, "design_surfaces")
    for name, rel in CHECKOUTS.items():
        state = HOME / rel
        files = [f for f in git(state, "ls-files", "*.md").split() if "/" not in f.replace("_archive/", "", 1) and f != "README.md"]
        revs = held = freed = 0
        rows = []
        for f in files:
            log = git(state, "log", "--follow", "--name-only", "--format=@%H", "--", f).split("\n")
            sha = None
            for line in log:
                if line.startswith("@"):
                    sha = line[1:]
                elif line and sha:
                    text, path, at = git(state, "show", f"{sha}:{line}"), line, sha
                    sha = None
                    if "## Captain amendments" not in text:
                        continue
                    sha = at
                    revs += 1
                    folder = path[:-3]
                    names = [p for p in git(state, "ls-tree", "-r", "--name-only", at, f"{folder}/dispatch/").split() if p.endswith(".md")]
                    texts = [git(state, "show", f"{at}:{p}") for p in names]
                    lines = text.split("\n")
                    declared = base.check_criteria("t", lines, [])
                    e1, e2 = [], []
                    base.check_amendments("t", lines, declared, e1)
                    cand.check_amendments("t", lines, declared, e2, cand.dispatched_amendments(folder, texts))
                    sha = None
                    a = sum("is still declared" in e for e in e1)
                    b = sum("is still declared" in e for e in e2)
                    held += bool(a)
                    freed += bool(a and not b)
                    if a != b:
                        rows.append(f"{path} {at[:8]}: base {a} still-declared error(s), candidate {b}")
        print(f"{name}: {revs} revisions with an amendments section; base prints 'still declared' on {held}; candidate stops it on {freed}")
        for r in rows:
            print("   ", r)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
