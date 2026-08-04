#!/usr/bin/env python3
"""Resolve an adopter's kernel binding and report whether it is still the text they pinned.

A binding names a kernel by version *and* by digest. The version expresses
compatibility intent; the digest identifies the exact bytes the adopter agreed to.
Only the digest can tell a stale pin from a current one, because an adopter that
holds a verbatim or condensed copy of kernel text stays internally consistent
while the upstream text moves underneath it.

Outcomes are closed:

  PASS              the pinned digest is the installed entrypoint's digest
  STALE_COMPATIBLE  digest matches but the declared version is behind the package
  REBIND_REQUIRED   the installed entrypoint is not the text this binding pinned
  UNRESOLVABLE      binding, package, or entrypoint could not be established

Absence of proof is never PASS: every failure to resolve is UNRESOLVABLE, and a
non-PASS exits non-zero so a caller cannot read silence as agreement.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

FIELDS = ("kernel_source", "kernel_version", "kernel_digest", "kernel_entrypoint")


def emit(outcome: str, detail: str, entrypoint: Path | None = None) -> int:
    print(f"verify-binding:{outcome}:{detail}")
    if entrypoint is not None:
        # The agent's read path. Printed on every outcome that resolved a file,
        # because "which file do I actually read" is the question a stale pin
        # answers wrongly and silently.
        print(f"verify-binding:entrypoint:{entrypoint}")
    return 0 if outcome == "PASS" else 1


def read_binding(readme: Path) -> dict[str, str] | None:
    if not readme.is_file():
        return None
    text = readme.read_text(encoding="utf-8", errors="replace")
    found: dict[str, str] = {}
    for field in FIELDS:
        # Bindings live in a fenced yaml block inside Markdown; a line-anchored
        # scalar read is deliberate rather than a YAML parse, because a general
        # parser would also accept the field from an unrelated block.
        match = re.search(rf"^\s*{field}:\s*(\S+)\s*$", text, re.MULTILINE)
        if match:
            found[field] = match.group(1).strip().strip('"\'')
    return found or None


def package_version(package: Path) -> str | None:
    manifest = package / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        return None
    match = re.search(r'"version"\s*:\s*"([^"]+)"', manifest.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readme", type=Path, help="adopter workflow README carrying the binding")
    parser.add_argument("--package", type=Path, required=True, help="installed kc-dev-flow package root")
    args = parser.parse_args()

    binding = read_binding(args.readme)
    if binding is None:
        return emit("UNRESOLVABLE", f"no binding fields in {args.readme}")
    missing = [f for f in FIELDS if f not in binding]
    if missing:
        return emit("UNRESOLVABLE", f"binding omits {','.join(missing)}")

    if not args.package.is_dir():
        return emit("UNRESOLVABLE", f"package root {args.package} is not a directory")

    entrypoint = args.package / binding["kernel_entrypoint"]
    try:
        entrypoint = entrypoint.resolve(strict=True)
        entrypoint.relative_to(args.package.resolve())
    except (OSError, ValueError):
        # A traversing or absent entrypoint resolves to something outside the
        # package; refusing is the point, since the alternative is verifying a
        # file the package does not own.
        return emit("UNRESOLVABLE", f"entrypoint {binding['kernel_entrypoint']} does not resolve inside the package")

    actual = hashlib.sha256(entrypoint.read_bytes()).hexdigest()
    declared = binding["kernel_digest"]
    if actual != declared:
        return emit("REBIND_REQUIRED", f"declared {declared[:12]} but installed is {actual[:12]}", entrypoint)

    installed = package_version(args.package)
    if installed is None:
        return emit("UNRESOLVABLE", "package manifest has no version", entrypoint)
    if installed != binding["kernel_version"]:
        return emit("STALE_COMPATIBLE", f"pinned {binding['kernel_version']} but package is {installed}; entrypoint text unchanged", entrypoint)

    return emit("PASS", f"{binding['kernel_source']}@{installed}", entrypoint)


if __name__ == "__main__":
    sys.exit(main())
