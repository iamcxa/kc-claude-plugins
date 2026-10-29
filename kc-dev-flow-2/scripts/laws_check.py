#!/usr/bin/env python3
"""Check the dev2 laws in references/sd/laws.md over the events one push adds to a committed state-branch history.

Usage: laws_check.py <state checkout> --before <commit> [--after <commit>] [--readme FILE]
Judges only the events of the commits in before..after (--after defaults to HEAD), each read at its own commit,
so a violation is reported in the run of the push that added it and not again. Reads committed bytes only;
changes nothing.
Exit 0 every law held. Exit 1 some law was violated. Exit 2 something could not be judged (before or after not a
commit, a range commit with no parent in this clone, a missing script, a check that crashed or printed a shape
this runner does not parse), even when another law also failed; both kinds print.
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
TASK = re.compile(r"^(?:_archive/)?([^/]+)\.md$")
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
    lines = [line for line in out.splitlines() if line.strip()]
    if code == 1 and not lines:
        note = (err.strip().splitlines() or ["stderr empty"])[-1]
        raise Cannot(f"{name} exited 1 with no output: {note}")
    return code, lines


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


def walk(state, before, after):
    span = f"{before}..{after}"
    for line in git(state, "rev-list", "--no-merges", "--parents", span).splitlines():
        sha, *parents = line.split()
        if not parents:
            raise Cannot(f"{sha[:12]} has no parent here, so what it adds cannot be told from a truncated past")
    commits = []
    for line in git(state, "log", "--no-merges", "--reverse", "-M", "--name-status", "--format=%x01%H", span).splitlines():
        if line.startswith("\x01"):
            commits.append((line[1:], []))
        elif line:
            status, *paths = line.split("\t")
            commits[-1][1].append((status[0], paths[0], paths[-1]))
    return commits


def sentinel_at(state, rev, path):
    code, out, _ = run("git", "-C", str(state), "show", f"{rev}:{path}")
    return code == 0 and SENTINEL.fullmatch(frontmatter_pr(out) or "") is not None


def l1_observer_before_sentinel(ctx):
    script("observer_check.py")
    if ctx.readme is None:
        raise Cannot("L1 needs --readme FILE to read extensions:")
    if "learn" not in readme_extensions(ctx.readme):
        return 0, [], "0 events judged (README lists no learn)"
    judged, violations = 0, []
    for commit, changes in ctx.commits:
        for status, old, new in changes:
            task = TASK.match(new)
            if status not in "AMR" or not task or task[1] == "README":
                continue
            if not sentinel_at(ctx.state, commit, new) or (status != "A" and sentinel_at(ctx.state, f"{commit}^", old)):
                continue
            judged += 1
            code, lines = run_check("observer_check.py", str(ctx.state), task[1], "--rev", commit)
            if code == 1:
                if not re.match(r"observer report (?:not committed|blank): ", lines[0] if lines else ""):
                    raise Cannot(f"observer_check.py exited 1 with output this runner does not parse: {lines[:1]}")
                violations.append(f"violation: L1 observer-before-sentinel task={task[1]} commit={commit[:12]} {lines[0]}")
    return judged, violations, None


def l2_dispatch_record_complete(ctx):
    script("dispatch_records.py")
    groups = {}
    for commit, changes in ctx.commits:
        for status, old, new in changes:
            if status in "AR" and DISPATCH.match(new) and (status == "A" or not DISPATCH.match(old)):
                groups.setdefault((commit, new.rsplit("/dispatch/", 1)[0]), []).append(new)
    judged, hit = 0, {}
    for (commit, folder), paths in groups.items():
        with tempfile.TemporaryDirectory() as tmp:
            for path in git(ctx.state, "ls-tree", "--name-only", commit, f"{folder}/dispatch/").split("\n"):
                if DISPATCH.match(path):
                    (Path(tmp) / path).parent.mkdir(parents=True, exist_ok=True)
                    (Path(tmp) / path).write_text(git(ctx.state, "show", f"{commit}:{path}"))
            code, task_text, _ = run("git", "-C", str(ctx.state), "show", f"{commit}:{folder}.md")
            if code == 0:
                (Path(tmp) / f"{folder}.md").write_text(task_text)
            code, index_text, _ = run("git", "-C", str(ctx.state), "show", f"{commit}:{folder}/index.md")
            if code == 0:
                (Path(tmp) / folder / "index.md").write_text(index_text)
            mine = {path.rsplit("/", 1)[1]: (path, commit) for path in paths}
            judged += len(mine)
            readme = ["--readme", str(ctx.readme)] if ctx.readme else []
            code, lines = run_check("dispatch_records.py", *readme, str(Path(tmp) / folder))
            for line in lines if code == 1 else []:
                if not ctx.readme and line.startswith("extensions not checked: "):
                    continue
                match = re.fullmatch(r"([^/]+\.md): (needs .+|[\w-]+ worker instruction .+)", line)
                if not match:
                    raise Cannot(f"dispatch_records.py exited 1 with output this runner does not parse: {line}")
                if match[1] in mine:
                    hit.setdefault(mine[match[1]], []).append(match[2])
            files = [str(Path(tmp) / path) for path in paths]
            code, lines = run_check("dispatch_records.py", "--names", *files)
            for line in lines if code == 1 else []:
                match = re.fullmatch(r"(.+\.md):(\d+): (bare package script name \S+|no 'Candidate: <40-hex head>' line|"
                                     r"design ADR placeholder has no reserved ADR|"
                                     r"reserved line '[^']+' missing from scope notes|"
                                     r"Captain amendment \d+ named in no dispatch checklist|"
                                     r"Captain amendment form at [^:]+:\d+: .+|"
                                     r"'## FO alignment' records alignment as needed with no 'Result:' line|"
                                     r"Captain amendment \d+ (?:Captain|Asked) line holds a backslash-quote copied from JSON)(?:;.*)?", line)
                if not match:
                    raise Cannot(f"dispatch_records.py --names exited 1 with output this runner does not parse: {line}")
                key = next((v for v in mine.values() if str(Path(tmp) / v[0]) == match[1]), None)
                if key:
                    hit.setdefault(key, []).append(f"{match[3]} (line {match[2]})")
    violations = [f"violation: L2 dispatch-record-complete record={path} commit={commit[:12]} {part}"
                  for (path, commit), parts in sorted(hit.items()) for part in parts]
    return judged, violations, None, len(hit)


AMENDMENT_TASK = re.compile(r"^(?:_archive/)?(?:([^/]+)\.md|([^/]+)/index\.md)$")


def amendment_slug(path):
    match = AMENDMENT_TASK.fullmatch(path)
    slug = (match[1] or match[2]) if match else None
    return slug if slug != "README" else None


def amendment_pairs(changes):
    pairs, deleted, added = [], [], []
    for status, old, new in changes:
        if status == "D" and amendment_slug(old):
            deleted.append(old)
        elif status == "A" and amendment_slug(new):
            added.append(new)
        elif status in "MR" and amendment_slug(old):
            pairs.append((old, new if amendment_slug(new) else None))
        elif status == "R" and amendment_slug(new):
            added.append(new)
    for old in deleted:
        matches = [new for new in added if amendment_slug(new) == amendment_slug(old)]
        sources = [path for path in deleted if amendment_slug(path) == amendment_slug(old)]
        if matches and (len(matches) != 1 or len(sources) != 1):
            raise Cannot(f"ambiguous task correspondence: {old} -> {', '.join(matches)}")
        new = matches[0] if matches else None
        pairs.append((old, new))
        if new:
            added.remove(new)
    return pairs + [(None, new) for new in added]


def amendment_blob(ctx, rev, path):
    from design_surfaces import parse_amendments
    if path is None:
        return []
    blob = subprocess.run(["git", "-C", str(ctx.state), "show", f"{rev}:{path}"], capture_output=True)
    if blob.returncode:
        raise Cannot(f"git show {rev}:{path} failed: {blob.stderr.decode('utf-8', 'replace').strip()}")
    try:
        text = blob.stdout.decode("utf-8")
    except UnicodeDecodeError as err:
        raise Cannot(f"{rev}:{path}: unreadable UTF-8 blob: {err}") from err
    entries, issues = parse_amendments(text.split("\n"))
    ambiguous = [f"line {line}: {message}" for line, message in issues
                 if any(word in message for word in ("duplicate", "malformed"))]
    if ambiguous:
        raise Cannot(f"{rev}:{path}: ambiguous protected spans: {'; '.join(ambiguous)}")
    return entries


def payload_append_allowed(old, new):
    from design_surfaces import DECLARATION_LINE
    if new == old:
        return True
    if new is None:
        return False
    if old is None:
        marker = re.match(r"Superseded text:\r?\n", new)
        if not marker:
            return False
        suffix = new[marker.end():]
    else:
        if not new.startswith(old + "\n"):
            return False
        suffix = new[len(old):]
    first = next((line for line in suffix.split("\n") if line.strip()), "")
    return bool(DECLARATION_LINE.match(first))


def l3_amendment_append_only(ctx):
    script("design_surfaces.py")
    script("decision_ledger.py")
    judged, violations, unavailable, hit = 0, [], [], set()
    for commit, changes in ctx.commits:
        try:
            pairs = amendment_pairs(changes)
        except Cannot as err:
            unavailable.append(f"commit={commit[:12]} {err}")
            continue
        for old, new in pairs:
            try:
                before = amendment_blob(ctx, f"{commit}^", old)
                after = amendment_blob(ctx, commit, new)
            except Cannot as err:
                unavailable.append(f"commit={commit[:12]} old={old} new={new} {err}")
                continue
            if not before:
                continue
            judged += 1
            for index, entry in enumerate(before):
                current = after[index] if index < len(after) else None
                field = None
                if current is None:
                    field = "entry removed" if new else "task deleted"
                elif entry.number != current.number:
                    field = "number/order changed"
                elif entry.header != current.header:
                    field = "header changed"
                elif entry.ambiguous_from is not None or current.ambiguous_from is not None:
                    limit = min(n for n in (entry.ambiguous_from, current.ambiguous_from) if n is not None)
                    if entry.raw.split("\n")[:limit] != current.raw.split("\n")[:limit]:
                        field = "metadata changed before unmatched fence"
                    else:
                        unavailable.append(f"commit={commit[:12]} old={old} new={new} amendment={entry.number}: ambiguous protected spans at unmatched fence")
                elif entry.metadata != current.metadata:
                    field = "metadata changed"
                elif not payload_append_allowed(entry.payload, current.payload):
                    field = "Superseded text changed or invalid append"
                if field:
                    hit.add((commit, old, new))
                    violations.append(f"violation: L3 amendment-append-only old={old} new={new or '(deleted)'} "
                                      f"amendment={entry.number} commit={commit[:12]} {field} "
                                      f"(old lines {entry.start + 1}-{entry.end})")
    if unavailable:
        raise Cannot("; ".join(unavailable) + ("\n" + "\n".join(violations) if violations else ""))
    return judged, violations, None, len(hit)


LAWS = {
    "L1": ("observer-before-sentinel", l1_observer_before_sentinel),
    "L2": ("dispatch-record-complete", l2_dispatch_record_complete),
    "L3": ("amendment-append-only", l3_amendment_append_only),
}


class Context:
    def __init__(self, state, span, commits, readme):
        self.state, self.span, self.commits, self.readme = state, span, commits, readme


def judge(ctx, law_id, spec):
    name, fn = spec
    judged, violations, note, *distinct = fn(ctx)
    violated = distinct[0] if distinct else len(violations)
    head = note or f"{judged} events judged in {ctx.span}, {violated} violated"
    return violated, [f"{law_id} {name}: {head}"], violations


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state")
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", default="HEAD")
    parser.add_argument("--readme")
    opts = parser.parse_args(sys.argv[1:] if argv is None else argv)
    state = Path(opts.state)
    problems = []
    if run("git", "-C", str(state), "rev-parse", "--is-inside-work-tree")[1].strip() != "true":
        problems.append(f"{state} is not a git work tree")
    else:
        before, after = commit_of(state, opts.before), commit_of(state, opts.after)
        problems += [f"{flag} {given} names no commit in {state}"
                     for flag, given, found in (("--before", opts.before, before), ("--after", opts.after, after)) if found is None]
    if not problems:
        try:
            commits = walk(state, before, after)
        except Cannot as err:
            problems.append(str(err))
    if problems:
        for problem in problems:
            print(f"cannot judge: {problem}")
        return 2
    ctx = Context(state, f"{before[:12]}..{after[:12]}", commits, opts.readme)
    total_violated, cannot = 0, []
    for law_id, spec in LAWS.items():
        try:
            violated, heads, violations = judge(ctx, law_id, spec)
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
