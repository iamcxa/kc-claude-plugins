#!/usr/bin/env python3
"""Compare the loaded kc-dev-flow-2 package with the release an adopted workflow README was synced from.

Usage: package_version.py <workflow README>
Exit 0 when they match, when the README is behind the package (re-sync it), or when the
README carries no release line. Exit 1 when the loaded package is older than the README:
the session must load the newer package before it dispatches. Exit 2 on a usage error.
"""
import json
import re
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
MARK = re.compile(r"kc-dev-flow-2 (\d+)\.(\d+)\.(\d+) x-release-please-version")


def loaded():
    version = json.loads((PACKAGE / ".claude-plugin/plugin.json").read_text())["version"]
    return tuple(int(n) for n in version.split("."))


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
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
