#!/usr/bin/env python3
"""Compare the loaded kc-dev-flow-2 package with the release an adopted workflow README was synced from.

Usage: package_version.py <workflow README>
Exit 0 when they match, when the README is behind the package (re-sync it), or when the
README carries no release line. Exit 1 when the loaded package is older than the README:
the session must load the newer package before it dispatches. Exit 2 on a usage error.
"""
import base64
import json
import re
import subprocess
import sys
from urllib.parse import quote
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
MARK = re.compile(r"kc-dev-flow-2 (\d+)\.(\d+)\.(\d+) x-release-please-version")


def loaded():
    version = json.loads((PACKAGE / ".claude-plugin/plugin.json").read_text())["version"]
    return tuple(int(n) for n in version.split("."))


UPSTREAM = "iamcxa/kc-claude-plugins"
LAWS = ("kc-dev-flow-2/scripts/laws_check.py", "kc-dev-flow-2/references/sd/laws.md",
        "kc-dev-flow-2/references/sd/state-laws.workflow.yml")
WORKFLOW = "kc-dev-flow-2/references/sd/workflow.md"


class Unreadable(Exception):
    pass


class Github:
    def __init__(self):
        self.cache = {}

    def run(self, *args):
        if args not in self.cache:
            try:
                run = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=45)
            except (OSError, subprocess.TimeoutExpired) as error:
                raise Unreadable(str(error)) from error
            if run.returncode:
                raise Unreadable(run.stderr.strip() or run.stdout.strip() or f"gh exit {run.returncode}")
            try:
                self.cache[args] = json.loads(run.stdout)
            except ValueError as error:
                raise Unreadable("gh returned invalid JSON") from error
        return self.cache[args]

    def content(self, repo, path, ref):
        data = self.run("api", f"repos/{repo}/contents/{quote(path, safe='/')}?ref={quote(ref, safe='')}")
        try:
            return base64.b64decode(data["content"]).decode("utf-8")
        except (KeyError, TypeError, ValueError, UnicodeError) as error:
            raise Unreadable(f"cannot decode {path}") from error

    def readme(self, repo, directory):
        default = self.run("api", f"repos/{repo}")["default_branch"]
        path = directory + "/README.md"
        text = self.content(repo, path, default)
        front = re.match(r"---\s*\n(.*?)\n---(?:\n|$)", text, re.S)
        trunk = re.search(r"^trunk:\s*(.+?)\s*$", front[1], re.M) if front else None
        if trunk:
            ref = trunk[1].split(" #", 1)[0].strip().strip("\"'")
            if ref != default:
                text = self.content(repo, path, ref)
        return text

    def releases(self):
        refs = self.run("api", f"repos/{UPSTREAM}/git/matching-refs/tags/kc-dev-flow-2-v")
        tags = {}
        for ref in refs:
            match = re.fullmatch(r"refs/tags/kc-dev-flow-2-v(\d+)\.(\d+)\.(\d+)", ref["ref"])
            if match:
                obj = ref["object"]
                seen = set()
                while obj["type"] == "tag":
                    if obj["sha"] in seen:
                        raise Unreadable("tag cycle")
                    seen.add(obj["sha"])
                    obj = self.run("api", f"repos/{UPSTREAM}/git/tags/{obj['sha']}")["object"]
                if obj["type"] != "commit":
                    raise Unreadable("release tag does not name a commit")
                tags[tuple(map(int, match.groups()))] = obj["sha"]
        if not tags:
            raise Unreadable("no published kc-dev-flow-2 tag")
        return tags


def diagnostic(error):
    return json.dumps(" ".join(str(error).split()), ensure_ascii=False)


def workflow_text(text):
    return "".join(line for line in text.splitlines(keepends=True) if not MARK.search(line))


def laws_status(gh, repo, branch, released, commits):
    try:
        text = gh.content(repo, ".github/workflows/dev2-laws.yml", branch)
    except Unreadable as error:
        if "HTTP 404" not in str(error):
            raise
        gh.run("api", f"repos/{repo}/branches/{quote(branch, safe='')}")
        # see docs/adr/0075-release-rollout-reports-adopters-and-laws-pin.md
        return "not installed", False
    checkout = re.search(r"repository:\s*['\"]?iamcxa/kc-claude-plugins['\"]?\s*\n(.*?)(?=\n\s*- |\Z)", text, re.S)
    pin = re.search(r"^\s*ref:\s*['\"]?([^'\"\s#]+)['\"]?\s*(?:#.*)?$", checkout[1], re.M) if checkout else None
    if not pin or pin[1].lower() not in commits:
        return (pin[1] if pin else "missing") + " pin unrecognised", True
    sha = pin[1].lower()
    owed = any(gh.content(UPSTREAM, path, sha) != gh.content(UPSTREAM, path, released) for path in LAWS)
    return sha + (" pin owed" if owed else " no pin owed"), owed


def rollout(listing):
    try:
        rows = []
        for number, line in enumerate(Path(listing).read_text().splitlines(), 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            fields = line.split()
            if (len(fields) not in (2, 3) or not re.fullmatch(r"[\w.-]+/[\w.-]+", fields[0])
                    or fields[1].startswith("/") or ".." in fields[1].split("/")):
                raise ValueError(f"invalid adopter row {number}: expected owner/repo workflow-dir [state-branch]")
            rows.append(fields)
        if not rows:
            raise ValueError("adopter list has no rows")
    except (OSError, ValueError) as error:
        print(f"rollout: unreadable {diagnostic(error)}")
        return 1
    gh = Github()
    try:
        tags = gh.releases()
        version = max(tags)
        released = tags[version]
    except (Unreadable, KeyError, TypeError) as error:
        for repo, directory, *_ in rows:
            print(f"{repo} {directory} unreadable: {diagnostic(error)}")
        return 1
    failed = False
    known = {(row[0], row[1] + "/README.md") for row in rows}
    for repo, directory, *state in rows:
        try:
            text = gh.readme(repo, directory)
            marker = MARK.search(text)
            if not marker:
                raise Unreadable("README carries no kc-dev-flow-2 release line")
            have = tuple(map(int, marker.groups()))
            if have not in tags:
                raise Unreadable("README release has no published tag")
            owed = workflow_text(gh.content(UPSTREAM, WORKFLOW, tags[have])) != workflow_text(gh.content(UPSTREAM, WORKFLOW, released))
            branch = state[0] if state else "spacedock-state/" + Path(directory).name
            laws, pin_owed = laws_status(gh, repo, branch, released, set(tags.values()))
            order = "; sync README, merge, then move pin" if owed and pin_owed else ""
            print(f"{repo} {directory} README:{'.'.join(marker.groups())} released:{'.'.join(map(str, version))} "
                  f"{'sync owed' if owed else 'no sync owed'}; laws: {laws}{order}")
            failed |= owed or pin_owed
        except (Unreadable, KeyError, TypeError) as error:
            print(f"{repo} {directory} unreadable: {diagnostic(error)}")
            failed = True
    try:
        found = gh.run("search", "code", "x-release-please-version", "--owner", "iamcxa", "--owner", "spacedock-dev",
                       "--filename", "README.md", "--limit", "1000", "--json", "repository,path")
        seen = set(known)
        for item in found:
            repo, path = item["repository"]["nameWithOwner"], item["path"]
            if (repo, path) not in seen and path.endswith("/README.md"):
                if MARK.search(gh.readme(repo, path.rsplit("/", 1)[0])):
                    print(f"unlisted: {repo} {path}")
                    seen.add((repo, path))
    except (Unreadable, KeyError, TypeError) as error:
        print(f"search: unavailable {diagnostic(error)}")
    return int(failed)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) == 2 and args[0] == "rollout":
        return rollout(args[1])
    if len(args) != 1 or not Path(args[0]).is_file():
        print(__doc__.strip())
        return 2
    package = loaded()
    found = MARK.search(Path(args[0]).read_text())
    have = ".".join(map(str, package))
    if not found:
        print(f"package {have}; the README carries no kc-dev-flow-2 release line (synced before 0.18.1)")
        return 0
    readme = tuple(int(n) for n in found.groups())
    want = ".".join(map(str, readme))
    if package < readme:
        print(f"loaded package {have} is older than the README's {want}: load {want} or later before dispatching")
        return 1
    if package > readme:
        print(f"README synced from {want} is behind the loaded package {have}: re-sync it")
        return 0
    print(f"package {have} matches the README")
    return 0


if __name__ == "__main__":
    sys.exit(main())
