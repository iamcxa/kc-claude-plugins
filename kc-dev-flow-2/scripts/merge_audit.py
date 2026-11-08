#!/usr/bin/env python3
"""List merges against saved asks in committed spacedock-state/* tips.

Usage: merge_audit.py STATE TASK [--from FROM] [--rev TO]
Exit 0: carried or named kinds; 1: findings; 2: incomplete evidence.
Only the state-ref fetch writes; approval in chat or another repository is outside this audit.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ASK = re.compile(r"(?:^|/)merge/ask-[0-9]+\.json$")
HEAD = re.compile(r"[0-9a-f]{7,40}")
PR = re.compile(r"([\w.-]+/[\w.-]+)#([1-9][0-9]*)")
SYNC = re.compile(r"^chore\([\w.-]+\): sync workflow to kc-dev-flow-2 v")


class CannotTell(Exception):
    pass


def run(command, data=None, allowed=(0,)):
    done = subprocess.run(command, input=data, capture_output=True)
    if done.returncode not in allowed:
        raise CannotTell(f"{' '.join(command)}: {done.stderr.decode(errors='replace').strip()}")
    return done.stdout


def git(state, *args):
    return run(["git", "-C", str(state), *args]).decode()


def field(text, key):
    front = text.split("\n---", 1)[0] if text.startswith("---\n") else ""
    match = re.search(rf"^{key}:[ \t]*(.*)$", front, re.M)
    if not match:
        return ""
    raw = match[1].strip()
    quoted = re.fullmatch(r"""(['"])(.*?)\1(?:\s+#.*)?""", raw)
    return quoted[2] if quoted else re.split(r"\s+#", raw, 1)[0].strip()


def stamp(text):
    value = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("timestamp has no timezone")
    return value


def window(state, task, start, end):
    end = git(state, "rev-parse", "--verify", f"{end}^{{commit}}").strip()
    paths = [f"{task}.md", f"{task}/index.md", f"_archive/{task}.md", f"_archive/{task}/index.md"]
    names = git(state, "ls-tree", "-r", "--name-only", end, "--", *paths).splitlines()
    if not names:
        raise CannotTell(f"no task {task} at {end}")
    if start is None:
        history = git(state, "log", "--reverse", "--diff-filter=A", "--format=%H", end, "--", *paths[:2])
        if not history.strip():
            raise CannotTell(f"cannot find the commit that added {task}")
        start = history.splitlines()[0]
    start = git(state, "rev-parse", "--verify", f"{start}^{{commit}}").strip()
    lo, hi = (stamp(git(state, "show", "-s", "--format=%cI", ref).strip()) for ref in (start, end))
    if lo > hi:
        raise CannotTell("FROM is later than TO")
    return start, end, lo, hi


def blobs(state, ids):
    ids = list(dict.fromkeys(ids))
    raw = run(["git", "-C", str(state), "cat-file", "--batch"], "".join(f"{oid}\n" for oid in ids).encode())
    found, offset = {}, 0
    for oid in ids:
        line_end = raw.index(b"\n", offset)
        header = raw[offset:line_end].decode().split()
        if len(header) != 3 or header[1] != "blob":
            raise CannotTell(f"cannot read blob {oid}")
        size = int(header[2])
        offset = line_end + 1
        found[oid] = raw[offset:offset + size].decode()
        offset += size + 1
    return found


def tree(state, rev):
    entries = []
    for entry in git(state, "ls-tree", "-r", "-z", rev).split("\0"):
        if entry:
            meta, path = entry.split("\t", 1)
            mode, kind, oid = meta.split()
            if kind == "blob":
                entries.append((path, oid))
    return entries


def task_path(path):
    parts = path.removeprefix("_archive/").split("/")
    return (len(parts) == 1 and parts[0].endswith(".md") and not parts[0].startswith((".", "_"))
            or len(parts) == 2 and parts[1] == "index.md" and not parts[0].startswith((".", "_")))


def read_state(state, repo):
    fetched = subprocess.run(["git", "-C", str(state), "fetch", "--quiet", "--prune", "origin",
                              "+refs/heads/spacedock-state/*:refs/remotes/origin/spacedock-state/*"],
                             capture_output=True)
    if fetched.returncode:
        print("warning: state fetch failed; reading local refs; records may be stale or invisible", file=sys.stderr)
    refs = git(state, "for-each-ref", "--format=%(refname) %(objectname) %(committerdate:iso-strict)",
               "refs/remotes/origin/spacedock-state/", "refs/heads/spacedock-state/").splitlines()
    if not refs:
        raise CannotTell("no readable spacedock-state/* refs")
    entries = []
    for line in refs:
        ref, sha, time = line.split()
        print(f"read: {ref} {sha} {time}")
        entries.extend((ref, path, oid) for path, oid in tree(state, sha) if ASK.search(path) or task_path(path))
    contents = blobs(state, (oid for _, _, oid in entries))
    records, owners = {}, {}
    for ref, path, oid in entries:
        text, source = contents[oid], f"{ref.split('/', 2)[2]}:{path}"
        if ASK.search(path):
            record = json.loads(text)
            if not isinstance(record, dict) or not PR.fullmatch(str(record.get("pr", ""))):
                raise CannotTell(f"invalid ask PR in {source}")
            head = str(record.get("head", "")).lower()
            if not HEAD.fullmatch(head):
                raise CannotTell(f"invalid ask head in {source}")
            records.setdefault(record["pr"], []).append((head, source))
        else:
            owner = field(text, "pr")
            match = re.fullmatch(r"(?:pr-merge:)?#?([1-9][0-9]*)", owner)
            if match:
                owners.setdefault(f"{repo}#{match[1]}", source)
            elif PR.fullmatch(owner):
                owners.setdefault(owner, source)
    return records, owners


def merged_prs(repo, trunk, lo, hi):
    raw = run(["gh", "pr", "list", "--repo", repo, "--state", "merged", "--base", trunk,
               "--search", f"merged:{lo.astimezone(dt.timezone.utc).date()}..{hi.astimezone(dt.timezone.utc).date()}",
               "--limit", "1000", "--json", "number,title,headRefName,headRefOid,mergedAt"])
    prs = json.loads(raw)
    if not isinstance(prs, list) or len(prs) >= 1000:
        raise CannotTell("gh returned 1000 results or an invalid PR list; narrow the window")
    selected, seen = [], set()
    for pr in prs:
        if (not isinstance(pr, dict) or type(pr.get("number")) is not int or pr["number"] <= 0
                or not re.fullmatch(r"[0-9a-fA-F]{40}", str(pr.get("headRefOid", "")))
                or not all(isinstance(pr.get(k), str) for k in ("title", "headRefName", "mergedAt"))):
            raise CannotTell("gh returned an incomplete merged PR")
        if pr["number"] in seen:
            raise CannotTell(f"gh returned duplicate PR #{pr['number']}")
        seen.add(pr["number"])
        if lo < stamp(pr["mergedAt"]) <= hi:
            selected.append(pr)
    return sorted(selected, key=lambda pr: pr["number"])


def named_kind(pr):
    if pr["headRefName"].startswith("release-please--branches--"):
        return "release"
    if SYNC.match(pr["title"]):
        return "sync"
    if re.fullmatch(r"learning/[0-9a-f]{64}", pr["headRefName"]):
        return "learning"
    return None


def audit(state, task, start, end):
    origin = git(state, "remote", "get-url", "origin").strip()
    match = re.search(r"[:/]([\w.-]+/[\w.-]+?)(?:\.git)?/?$", origin)
    if not match:
        raise CannotTell(f"cannot read owner/repo from origin {origin}")
    repo = match[1]
    readme = state.parent / "README.md"
    trunk = field(readme.read_text(), "trunk")
    if not trunk:
        raise CannotTell(f"no trunk in {readme}")
    start, end, lo, hi = window(state, task, start, end)
    print(f"window: {start}..{end} ({lo.isoformat()}, {hi.isoformat()}]")
    records, owners = read_state(state, repo)
    prs = merged_prs(repo, trunk, lo, hi)
    earlier = [(p, oid) for p, oid in tree(state, end)
               if p.endswith("/observer.md") and p not in (f"{task}/observer.md", f"_archive/{task}/observer.md")]
    reports = blobs(state, (oid for _, oid in earlier)).values()
    carried, kinds, findings, repeated = 0, {k: [] for k in ("release", "sync", "learning")}, [], []
    for pr in prs:
        number, head = pr["number"], pr["headRefOid"].lower()
        key = f"{repo}#{number}"
        recs = records.get(key, [])
        if any(head.startswith(h) for h, source in recs):
            carried += 1
            continue
        kind = named_kind(pr)
        if kind:
            kinds[kind].append(number)
            continue
        kind = "head differs" if recs else "no ask record"
        token = f"{kind}: #{number} head {head[:12]}"
        if any(token in text for text in reports):
            repeated.append(number)
            continue
        note = "; ".join(f"{h[:12]} in {source}" for h, source in recs) if recs else owners.get(key, "no task in readable state")
        findings.append(f"{token} merged {pr['mergedAt']} ({note})")
    print(f"carried: {carried} of {len(prs)}")
    for kind, numbers in kinds.items():
        print(f"{kind}: " + (" ".join(f"#{n}" for n in numbers) or "none"))
    for line in findings:
        print(line)
    print("already reported: " + (" ".join(f"#{n}" for n in repeated) or "none"))
    return int(bool(findings))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("task")
    parser.add_argument("--from", dest="start")
    parser.add_argument("--rev", default="HEAD")
    args = parser.parse_args()
    if not re.fullmatch(r"[\w.-]+", args.task) or args.task in (".", ".."):
        parser.error("TASK must be a task slug")
    try:
        return audit(args.state.resolve(), args.task, args.start, args.rev)
    except (CannotTell, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"can't tell: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
