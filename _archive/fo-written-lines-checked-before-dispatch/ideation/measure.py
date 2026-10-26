"""Replay the four new FO-write checks over four dev2 state checkouts, read only.
usage: python3 -B -I fwl_measure.py <candidate scripts dir>
Reads each checkout with git, never writes. Prints one block per check."""
import collections, importlib.util, json, re, subprocess, sys
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
    spec = importlib.util.spec_from_file_location(name, Path(path) / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(state, *args):
    return subprocess.run(["git", "-C", str(state), *args], capture_output=True, text=True).stdout


def task_files(state):
    return [f for f in git(state, "ls-files", "*.md").split() if "/" not in f.replace("_archive/", "", 1) and f != "README.md"]


def main(cand):
    ds, dg = load(cand, "design_surfaces"), load(cand, "delivery_gate")
    print("candidate scripts:", cand)
    for name, rel in CHECKOUTS.items():
        print(f"{name} head {git(HOME/rel, 'rev-parse', '--short=12', 'HEAD').strip()}, {len(task_files(HOME/rel))} task files")

    print("\n[1] Result line owed at the commit that added each ideation dispatch record")
    for name, rel in CHECKOUTS.items():
        state, total, needed, owing, rows, seen = HOME/rel, 0, 0, 0, [], set()
        added = git(state, "log", "--diff-filter=A", "--no-renames", "--name-only", "--format=@%H %cI", "--reverse", "--", "*/dispatch/ideation-*.md")
        sha = date = None
        for line in added.splitlines():
            if line.startswith("@"):
                sha, date = line[1:].split()[0], line.split()[1]
            elif re.search(r"(?:^|/)([^/]+)/dispatch/ideation-\d+\.md$", line):
                slug = re.search(r"([^/]+)/dispatch/ideation-(\d+)\.md$", line)
                prefix = line[:line.index(slug.group(1))]
                key = (slug.group(1), slug.group(2))
                if key in seen:
                    continue
                seen.add(key)
                text = git(state, "show", f"{sha}:{prefix}{slug.group(1)}.md")
                if not text:
                    continue
                total += 1
                if ds.ALIGN_NEEDED.search(ds.split_fo("\n".join(ds.unfenced(text.split("\n"))))[0]):
                    needed += 1
                    if ds.alignment_owes_result(text):
                        owing += 1
                        rows.append(f"{slug.group(1)} ideation-{slug.group(2)} {date[:10]}")
        print(f"  {name}: {total} ideation records, {needed} with alignment needed, {owing} would be refused")
        for r in rows:
            print("    ", r)

    print("\n[2] backslash-quote on an amendment line, task files at head")
    hits = 0
    for name, rel in CHECKOUTS.items():
        state = HOME/rel
        for f in task_files(state):
            for title, key in ds.escaped_amendment_lines((state/f).read_text(errors="replace").split("\n")):
                hits += 1
                print(f"  {name}/{f}: {title} {key}")
    print("  total:", hits)

    print("\n[3] validation gate questions: merge named with --match-head-commit and no hold-out clause")
    for name, rel in CHECKOUTS.items():
        state, total, grants, missing, rows = HOME/rel, 0, 0, 0, []
        for f in git(state, "ls-files", "*/review/validation/briefing-*/index.json").split():
            try:
                q = json.loads((state/f).read_text())["question"]
            except (OSError, ValueError, KeyError):
                continue
            total += 1
            grants += bool(dg.GRANT.search(q))
            if dg.grant_without_hold_out(q):
                missing += 1
                first = git(state, "log", "--diff-filter=A", "--format=%cI", "-1", "--", f).strip()[:10]
                rows.append(f"{f.split('/review')[0]} {first}")
        print(f"  {name}: {total} questions, {grants} name the merge, {missing} lack the clause")
        for r in rows:
            print("    ", r)

    print("\n[4] Override: recommended line in a task body and in no gate resolution reason, task files at head")
    hits = 0
    for name, rel in CHECKOUTS.items():
        state = HOME/rel
        for f in task_files(state):
            for line in ds.owed_overrides((state/f).read_text(errors="replace")):
                hits += 1
                print(f"  {name}/{f}: {line[:100]}")
    print("  total:", hits)


if __name__ == "__main__":
    main(sys.argv[1])
