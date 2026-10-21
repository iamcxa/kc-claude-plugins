#!/usr/bin/env python3
"""Prototype of the R3 check (cycle 2: baseline at the newest amendment's commit, stage-gated, FO-addressed hold line).

Usage: python3 -I -B proto_scope.py <package scripts dir> <state checkout> [--fixtures] [task.md ...]
  census (default): judge every task file of a state checkout, ignoring the stage gate (a replay of what the check
    would have said at the ideation gate), and print held / amended / clean / not judged counts. Writes nothing.
  --fixtures: the cycle-2 cases of AC-6 on real tasks of the checkout, which must be a LINKED worktree (its `.git` is a file),
    as the state checkout is. It edits one task file in the working tree for each case and restores it with `git checkout`, so run it in a scratch
    clone (the design's runs used /tmp/fwrc-work/state-wt at 8eda9070), never in the live state checkout.

The functions below are what the implementation would add to design_surfaces.py. For a task with a closed backlog approval:
  baseline = the task file at the sha the backlog briefing binds (`git-root://state/<sha>/<path>`);
  if an `### Amendment N — <date>` dated on or after the approval day exists, the baseline is the file at the commit that
  introduced the NEWEST such amendment (`git log --follow -G'^### Amendment N — '`, oldest commit), or the working tree when that
  heading is not committed yet, so a Scope edit made before or with the newest amendment is covered and one made after it is not;
  held = `## Scope` lines added or removed against the baseline, except lines that open with Non-goals, Budget, Stop condition or Follow-up:.
The check runs only while the task's frontmatter says `status: ideation` (the stage in which FO runs it before the gate).
"""
import json, re, subprocess, sys
from pathlib import Path

NONGOAL = re.compile(r"\s*(?:[-*]\s*)?(?:Non-goals?\b|Budget\b|Stop condition\b|Follow-up:)", re.I)
AMD = re.compile(r"^### Amendment (\d+) — (\d{4}-\d{2}-\d{2})", re.M)
STATUS = re.compile(r"""^status:[ \t]*["']?([^\s"']+)["']?[ \t]*$""", re.M)
HOLD = ('Scope changed after {what} ({sha}): "{line}". FO: restore the line; add an \'### Amendment N\' with \'Supersedes: none\' only if '
        'the Captain asked for it, with his words verbatim and where he said them. A worker that sees this line reports it to FO and edits neither Scope nor amendments.')


def scope(text):
    m = re.search(r"^## Scope\b[^\n]*\n(.*?)(?=^## |\Z)", text or "", re.M | re.S)
    return (m.group(1) if m else "").splitlines()


def git(task, *args):
    return subprocess.run(["git", "-C", str(task.parent), *args], capture_output=True)


def show(task, commit, rel):
    for path in (rel, rel.replace("_archive/", "", 1) if rel.startswith("_archive/") else "_archive/" + rel):
        done = git(task, "show", f"{commit}:{path}")
        if done.returncode == 0:
            return done.stdout.decode("utf-8", "replace")
    return None


def introducing_commit(task, number):
    """the oldest commit whose diff adds the `### Amendment <number> — ` heading line; None when it is not committed"""
    done = git(task, "log", "--follow", "--format=%H", f"-G^### Amendment {number} — ", "--", task.name)
    commits = done.stdout.decode().split()
    return commits[-1] if commits else None


def judge(task, stage_gate=True, rule="newest"):
    import decision_ledger as dl
    text = task.read_text()
    fm, body = dl.split_task(text)
    if fm is None:
        return "not run", "no frontmatter"
    if stage_gate:
        status = STATUS.search("\n".join(fm))
        if not status or status.group(1) != "ideation":
            return "not run", f"stage is {status.group(1) if status else 'unknown'}, not ideation"
    closed = [e for e in dl.gate_entries(fm) if e["stage"] == "backlog" and e["kind"] == "resolution" and e.get("decision") == "approve"]
    if not closed:
        return "not run", "no closed backlog approval"
    gate = closed[-1]
    try:
        uri = json.loads((task.parent / gate["room"] / "index.json").read_text())["artifacts"][0]["uri"]
    except (OSError, ValueError, KeyError, IndexError):
        return "not run", "backlog briefing unreadable"
    m = re.fullmatch(r"git-root://state/([0-9a-f]{40})/(.+)", uri)
    if not m:
        return "not run", "artifact uri has no sha"
    if git(task, "rev-parse", "--git-dir").returncode:
        return "not run", "not in a git checkout"
    old_text = show(task, m[1], m[2])
    if old_text is None:
        return "not run", "baseline not readable by git"
    day = (gate.get("at") or "")[:10]
    after = [int(n) for n, d in AMD.findall(body) if d >= day]
    baseline, via = old_text, f"backlog {m[1][:8]}"
    if after and rule == "any":
        return "amended", f"amendment(s) {after} exist (the first-cycle rule: any amendment exempts every later edit)"
    if after and rule == "newest":
        newest = max(after)
        commit = introducing_commit(task, newest)
        if commit is None:
            baseline, via = text, f"amendment {newest} (uncommitted)"
        else:
            rel = git(task, "ls-files", "--full-name", "--", task.name).stdout.decode().strip() or task.name
            at_amd = show(task, commit, rel)
            if at_amd is None:
                return "not run", f"amendment {newest} commit {commit[:8]} unreadable"
            baseline, via = at_amd, f"amendment {newest} {commit[:8]}"
    old, new = scope(baseline), scope(text)
    add = [l for l in new if l not in old and l.strip() and not NONGOAL.match(l)]
    rem = [l for l in old if l not in new and l.strip() and not NONGOAL.match(l)]
    if not add and not rem:
        return "clean", via
    what = "the backlog gate" if via.startswith("backlog") else "the newest amendment"
    return "HOLD", HOLD.format(what=what, sha=via.split()[-1][:8], line=(add or rem)[0].strip()[:80])


def census(state, only):
    import decision_ledger  # noqa: F401
    tasks = only or sorted(p for p in list(state.glob("*.md")) + list((state / "_archive").glob("*.md")) if p.name != "README.md")
    tally = {}
    for t in tasks:
        verdict, why = judge(t, stage_gate=False)
        tally.setdefault(verdict, []).append((t.stem, why))
        if verdict == "HOLD":
            print(f"HOLD     {t.stem[:46]:46s} {why[:140]}")
    print({k: len(v) for k, v in tally.items()})
    print("not run:", sorted({w for _, w in tally.get("not run", [])}))
    print("clean via:", {k: sum(1 for _, w in tally.get("clean", []) if w.startswith(k)) for k in ("backlog", "amendment")})


def fixtures(state):
    def edit(rel, fn):
        p = state / rel
        p.write_text(fn(p.read_text()))
        return p

    def restore(rel):
        subprocess.run(["git", "-C", str(state), "checkout", "--", rel], check=True)

    def case(label, rel, fn, stage_gate=False, rule="newest"):
        p = edit(rel, fn) if fn else state / rel
        try:
            verdict, why = judge(p, stage_gate, rule)
        finally:
            if fn:
                restore(rel)
        print(f"  {label:78s} -> {verdict}: {why[:150]}")
        return verdict

    add_scope = lambda line: (lambda t: t.replace("## Scope\n", "## Scope\n\n" + line + "\n", 1))
    amd = "ideation-gaps"
    rel = f"_archive/{amd}.md"
    print("-- AC-6 cases on real tasks (run at the ideation stage by --stage-gate off; the stage gate is its own case below)")
    case("real: special-role-calls (Captain scope addition after the backlog gate, no amendment)", "_archive/special-role-calls-fire-when-needed.md", None)
    case("real: ideation-gaps (Scope changed, newest amendment 1 committed with it)", rel, None)
    case("edit AFTER the newest amendment: ideation-gaps + a new Scope line, uncommitted", rel, add_scope("- Captain asked for one more thing, added after amendment 1."))
    def drop_first_scope_line(t):
        head, rest = t.split("## Scope\n", 1)
        lines = rest.split("\n")
        first = next(i for i, l in enumerate(lines) if l.strip() and not l.startswith("## "))
        return head + "## Scope\n" + "\n".join(lines[:first] + lines[first + 1:])
    case("edit AFTER the amendment, a Scope line removed instead", rel, drop_first_scope_line)
    case("exempt fill only: ideation-gaps + a Non-goals line after the amendment", rel, add_scope("- Non-goals: nothing else."))
    case("an edit outside Scope only (a line appended to the last section of ideation-gaps)", rel, lambda t: t.rstrip("\n") + "\nAn added line outside Scope.\n")
    case("uncommitted newest amendment covers the uncommitted Scope line", rel,
         lambda t: add_scope("- Captain asked for one more thing, added with amendment 2.")(t).rstrip("\n") + "\n\n### Amendment 2 — 2026-10-20, chat\nCaptain: 「加」\nSupersedes: none\n")
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="proto-scope-"))
    subprocess.run(f"git -C '{state}' archive HEAD _archive/special-role-calls-fire-when-needed.md _archive/special-role-calls-fire-when-needed | tar -x -C '{tmp}'", shell=True, check=True)
    print("-- observer replay shape (ADR 0024): the task and its folder extracted with git archive into a temp directory, no .git")
    print("  ", judge(tmp / "_archive/special-role-calls-fire-when-needed.md", stage_gate=False))
    subprocess.run(["rm", "-r", str(tmp)], check=True)
    print("-- mutations: each changes the baseline rule and must turn exactly the case named")
    case("MUTATION any-amendment (first-cycle rule): edit AFTER amendment 1 passes", rel, add_scope("- Captain asked for one more thing, added after amendment 1."), rule="any")
    case("MUTATION bound-sha only: ideation-gaps, whose Scope change amendment 1 records, is held", rel, None, rule="bound")
    stage = state / "_archive/ideation-gaps.md"
    print("-- stage gate: the same real file, status done / ideation")
    print("  ", judge(stage, True))
    edit(rel, lambda t: re.sub(r"^status: .*$", "status: ideation", t, count=1, flags=re.M))
    try:
        print("  ", judge(stage, True))
    finally:
        restore(rel)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--fixtures"]
    sys.path.insert(0, args[0])
    state = Path(args[1])
    if "--fixtures" in sys.argv:
        fixtures(state)
    else:
        census(state, [Path(a) for a in args[2:]])
