#!/usr/bin/env python3
"""Check the dev2 laws in references/sd/laws.md over a committed state-branch history.

Usage: laws_check.py <state checkout> [--rev REV] [--readme FILE] --anchor L1=<commit> [--anchor L2=<commit>]
Each law judges only events in commits that are strict descendants of its anchor. A law with no --anchor
prints `not judged, no anchor`. Reads committed bytes only; changes nothing.
Exit 0 every anchored law held. Exit 1 some law was violated. Exit 2 something could not be judged
(shallow history, a bad REV or anchor, a missing script, a check that crashed or printed a shape this runner
does not parse), even when another law also failed; both kinds print.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
TRACEBACK = "Traceback (most recent call last)"
SENTINEL = re.compile(r"pr-merge:\d+")
DISPATCH = re.compile(r"^(_archive/)?([^/]+)/dispatch/([^/]+\.md)$")


class Cannot(Exception):
    pass


def run(*argv, cwd=None):
    done = subprocess.run(argv, capture_output=True, cwd=cwd)
    return done.returncode, done.stdout.decode("utf-8", "replace"), done.stderr.decode("utf-8", "replace")


def git(state, *args):
    code, out, err = run("git", "-C", str(state), "-c", "core.quotepath=off", *args)
    if code:
        raise Cannot(f"git {' '.join(args[:2])} failed: {err.strip() or out.strip()}")
    return out


def commit_of(state, name):
    code, out, _ = run("git", "-C", str(state), "rev-parse", "--verify", "--quiet", f"{name}^{{commit}}")
    return out.strip() if code == 0 and out.strip() else None


def script(name):
    path = SCRIPTS / name
    if not path.is_file():
        raise Cannot(f"script missing: {path}")
    return str(path)


def run_check(name, *args):
    code, out, err = run(sys.executable, script(name), *args)
    if TRACEBACK in out or TRACEBACK in err:
        raise Cannot(f"{name} crashed: {(err or out).strip().splitlines()[-1]}")
    if code not in (0, 1):
        first = (out or err).strip().splitlines()
        raise Cannot(f"{name} exited {code}: {first[0] if first else 'no output'}")
    return code, [line for line in out.splitlines() if line.strip()]


def after(state, rev, anchor):
    return set(git(state, "rev-list", "--ancestry-path", f"{anchor}..{rev}").split())


def ledger():
    script("decision_ledger.py")
    sys.path.insert(0, str(SCRIPTS))
    import decision_ledger
    return decision_ledger


def frontmatter_pr(text):
    lines, _ = ledger().split_task(text)
    for line in lines or []:
        if line.startswith("pr:"):
            return ledger().unquote(line[3:])
    return None


def readme_extensions(path):
    try:
        lines, _ = ledger().split_task(Path(path).read_text())
    except OSError as err:
        raise Cannot(f"README unreadable: {err}")
    if lines is None:
        raise Cannot(f"README {path} has no frontmatter, so extensions: cannot be read")
    for i, line in enumerate(lines):
        if line.startswith("extensions:"):
            value = line[len("extensions:"):].strip()
            if value.startswith("[") and value.endswith("]"):
                return set(re.findall(r"[\w-]+", value))
            if not value:
                block = []
                for nxt in lines[i + 1:]:
                    if not nxt.lstrip().startswith("- "):
                        break
                    block.append(nxt.lstrip()[2:].strip())
                return set(block)
            raise Cannot(f"README {path}: extensions: is neither a [list] nor a block list")
    return set()


def task_files(state, rev):  # live and archived task files, one entry per slug
    found = {}
    for prefix in ("", "_archive/"):
        for name in git(state, "ls-tree", "--name-only", rev, prefix or "./").split("\n"):
            base = name.rsplit("/", 1)[-1]
            if name.endswith(".md") and base != "README.md" and (prefix or "/" not in name):
                found.setdefault(base[:-3], []).append(name)
    return sorted(found.items())


def first_sentinel(state, rev, paths):
    candidates = git(state, "log", "--reverse", "--format=%H", "-G^pr: [\"']?pr-merge:", rev, "--", *paths).split()
    for commit in candidates:
        for path in paths:
            code, out, _ = run("git", "-C", str(state), "show", f"{commit}:{path}")
            if code == 0 and SENTINEL.fullmatch(frontmatter_pr(out) or ""):
                return commit
    return None


def l1_observer_before_sentinel(ctx, anchor):
    script("observer_check.py")
    if ctx.readme is None:
        raise Cannot("L1 needs --readme FILE to read extensions:")
    if "learn" not in readme_extensions(ctx.readme):
        return 0, [], "0 events judged (README lists no learn)"
    later = after(ctx.state, ctx.rev, anchor)
    judged, violations = 0, []
    for slug, paths in task_files(ctx.state, ctx.rev):
        commit = first_sentinel(ctx.state, ctx.rev, [f"{slug}.md", f"_archive/{slug}.md"])
        if commit not in later:
            continue
        judged += 1
        code, lines = run_check("observer_check.py", str(ctx.state), slug, "--rev", commit)
        if code == 1:
            if not re.match(r"observer report (?:not committed|blank): ", lines[0] if lines else ""):
                raise Cannot(f"observer_check.py exited 1 with output this runner does not parse: {lines[:1]}")
            violations.append(f"violation: L1 observer-before-sentinel task={slug} commit={commit[:12]} {lines[0]}")
    return judged, violations, None


def newest_additions(state, rev):
    added = {}
    out = git(state, "log", "-M", "--diff-filter=A", "--format=%x00%H", "--name-only", rev, "--", "*/dispatch/*.md")
    for block in out.split("\x00")[1:]:
        commit, *names = block.split("\n")
        for name in names:
            match = DISPATCH.match(name)
            if match:
                added.setdefault((match[2], match[3]), commit)
    return added


def l2_dispatch_record_complete(ctx, anchor):
    script("dispatch_records.py")
    later = after(ctx.state, ctx.rev, anchor)
    added = newest_additions(ctx.state, ctx.rev)
    folders = {}
    for path in git(ctx.state, "ls-tree", "-r", "--name-only", ctx.rev).split("\n"):
        match = DISPATCH.match(path)
        if match:
            folders.setdefault(path.rsplit("/dispatch/", 1)[0], []).append((path, match[2], match[3]))
    judged, hit = 0, {}
    with tempfile.TemporaryDirectory() as tmp:
        for folder, records in sorted(folders.items()):
            mine = {}
            for path, slug, name in records:
                if (slug, name) not in added:
                    raise Cannot(f"no commit found that added {path}")
                (Path(tmp) / path).parent.mkdir(parents=True, exist_ok=True)
                (Path(tmp) / path).write_text(git(ctx.state, "show", f"{ctx.rev}:{path}"))
                if added[(slug, name)] in later:
                    mine[name] = (path, added[(slug, name)])
            if not mine:
                continue
            judged += len(mine)
            code, lines = run_check("dispatch_records.py", str(Path(tmp) / folder))
            for line in lines if code == 1 else []:
                match = re.fullmatch(r"([^/]+\.md): (needs .+)", line)
                if not match:
                    raise Cannot(f"dispatch_records.py exited 1 with output this runner does not parse: {line}")
                if match[1] in mine:
                    hit.setdefault(mine[match[1]], []).append(match[2])
            files = [str(Path(tmp) / path) for path, _ in mine.values()]
            code, lines = run_check("dispatch_records.py", "--names", *files)
            for line in lines if code == 1 else []:
                match = re.fullmatch(r"(.+\.md):(\d+): (bare package script name \S+)", line)
                if not match:
                    raise Cannot(f"dispatch_records.py --names exited 1 with output this runner does not parse: {line}")
                key = next((v for v in mine.values() if str(Path(tmp) / v[0]) == match[1]), None)
                if key:
                    hit.setdefault(key, []).append(f"{match[3]} (line {match[2]})")
    violations = [f"violation: L2 dispatch-record-complete record={path} commit={commit[:12]} {part}"
                  for (path, commit), parts in sorted(hit.items()) for part in parts]
    return judged, violations, None, len(hit)


LAWS = {
    "L1": ("observer-before-sentinel", l1_observer_before_sentinel),
    "L2": ("dispatch-record-complete", l2_dispatch_record_complete),
}


class Context:
    def __init__(self, state, rev, readme):
        self.state, self.rev, self.readme = state, rev, readme


def judge(ctx, law_id, spec, anchors):
    name, fn = spec
    if law_id not in anchors:
        return 0, 0, [f"{law_id} {name}: not judged, no anchor"], []
    anchor = commit_of(ctx.state, anchors[law_id])
    if anchor is None:
        raise Cannot(f"anchor {anchors[law_id]} for {law_id} is not a commit in {ctx.state}")
    if run("git", "-C", str(ctx.state), "merge-base", "--is-ancestor", anchor, ctx.rev)[0]:
        raise Cannot(f"anchor {anchors[law_id]} for {law_id} is not an ancestor of {ctx.rev}, "
                     "so every event would count as after it")
    judged, violations, note, *distinct = fn(ctx, anchor)
    violated = distinct[0] if distinct else len(violations)
    head = note or f"{judged} events judged after {anchors[law_id][:12]}, {violated} violated"
    return violated, judged, [f"{law_id} {name}: {head}"], violations


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state")
    parser.add_argument("--rev", default="HEAD")
    parser.add_argument("--readme")
    parser.add_argument("--anchor", action="append", default=[], metavar="LAW=COMMIT")
    opts = parser.parse_args(sys.argv[1:] if argv is None else argv)
    state = Path(opts.state)
    anchors = {}
    for item in opts.anchor:
        law_id, _, ref = item.partition("=")
        anchors[law_id] = ref
    problems = []
    if not anchors:
        problems.append("no anchor given: pass --anchor L1=<commit> or --anchor L2=<commit>")
    problems += [f"unknown law {law_id} in --anchor" for law_id in anchors if law_id not in LAWS]
    if run("git", "-C", str(state), "rev-parse", "--is-inside-work-tree")[1].strip() != "true":
        problems.append(f"{state} is not a git work tree")
    elif run("git", "-C", str(state), "rev-parse", "--is-shallow-repository")[1].strip() != "false":
        problems.append("history is shallow, so events after an anchor cannot be told from a truncated past")
    else:
        rev = commit_of(state, opts.rev)
        if rev is None:
            problems.append(f"--rev {opts.rev} names no commit in {state}")
    if problems:
        for problem in problems:
            print(f"cannot judge: {problem}")
        return 2
    ctx = Context(state, rev, opts.readme)
    total_violated, cannot = 0, []
    for law_id, spec in LAWS.items():
        try:
            violated, _, heads, violations = judge(ctx, law_id, spec, anchors)
        except Cannot as err:
            cannot.append(f"{law_id} {spec[0]}: cannot judge: {err}")
            continue
        total_violated += violated
        print("\n".join(heads + violations))
    for line in cannot:
        print(line)
    return 2 if cannot else (1 if total_violated else 0)


if __name__ == "__main__":
    sys.exit(main())
