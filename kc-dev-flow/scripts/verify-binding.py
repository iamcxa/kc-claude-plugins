#!/usr/bin/env python3
"""Resolve an adopter's kernel binding against the installed releases, and report drift.

A binding names a kernel by source, version, entrypoint, and digest. The version
states compatibility intent; the digest identifies the exact bytes agreed to.
Neither alone is enough:

  * version alone cannot see that the text moved under a reused version;
  * digest alone cannot see that a newer release exists.

So this resolves `kernel_source` itself rather than accepting a package path from
the caller. A checker told where to look verifies only that the binding agrees
with whatever it was handed, which is the same internally-consistent-but-stale
shape it exists to detect.

The binding is read from a machine-readable file that holds nothing else. Two
earlier revisions tried to locate it inside a Markdown document instead, and both
returned PASS for repositories that had no binding at all -- once by collecting
fields from unrelated blocks, once because an unclosed fence and an indented
example both read as real blocks. Prose documents are refused here rather than
parsed, so that failure class has nowhere left to live.

The digest covers the release's whole `references/` set, not the entrypoint
alone. The kernel names the Work Control Profile as an independent declaration
and the reverse-recovery audit as a normative procedure, so a release that moved
either of those moved an invariant an adopter is bound to -- and an
entrypoint-only digest would have called that release unchanged.

Outcomes are closed:

  PASS              pinned version is the newest installed, and its bytes match
  STALE_COMPATIBLE  a newer release is installed, but no reference text changed
  REBIND_REQUIRED   the pinned bytes are wrong, or a newer release changed them
  UNRESOLVABLE      binding, release, or entrypoint could not be established

Every outcome except PASS exits non-zero. Absence of proof is never a pass.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

REQUIRED = ("kernel_source", "kernel_version", "kernel_entrypoint")
DEFAULT_CACHE = Path.home() / ".claude" / "plugins" / "cache"
PROSE_SUFFIXES = {".md", ".markdown", ".mdx", ".rst", ".txt"}
# release-please cuts semver directories; anything else in the cache root is an
# installer artifact rather than a release, and ranking it would invent a newest.
VERSION_DIR = re.compile(r"^\d+(?:\.\d+)*(?:-[0-9A-Za-z.\-]+)?(?:\+[0-9A-Za-z.\-]+)?$")
# Column zero only: a nested or indented key belongs to some other mapping.
FIELD = r"^{name}:[ \t]*(?P<value>[^\s#]+)[ \t]*(?:#.*)?$"
# Every unindented line of a binding file is a key, a list item, a comment, or
# blank. A Markdown fence, heading underline, or sentence is none of those, so a
# prose document renamed to a data suffix is refused structurally rather than by
# its name.
RECORD_LINE = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_.\-]*:(?:[ \t].*)?|-[ \t].*|#.*|---|\.\.\.)?[ \t]*$")


def emit(outcome: str, detail: str, *lines: str) -> int:
    print(f"verify-binding:{outcome}:{detail}")
    for line in lines:
        print(line)
    return 0 if outcome == "PASS" else 1


def read_binding(path: Path) -> tuple[dict[str, str] | None, str | None]:
    """Return (binding, error) from a file whose whole content is the binding.

    Each field must appear exactly once at column zero. A repeated field is
    refused rather than resolved: choosing between two values would verify a
    binding the repository does not operate under.
    """
    if path.suffix.lower() in PROSE_SUFFIXES:
        return None, (
            f"{path.name} is a prose document; the binding is read from a "
            "machine-readable file that holds nothing else"
        )
    if not path.is_file():
        return None, f"{path} is not a readable file"

    text = path.read_text(encoding="utf-8", errors="replace")
    for number, line in enumerate(text.splitlines(), start=1):
        if line[:1] not in (" ", "\t") and not RECORD_LINE.match(line):
            return None, f"{path.name}:{number} is not a record line: {line.strip()[:48]!r}"

    binding: dict[str, str] = {}
    for name in (*REQUIRED, "kernel_digest"):
        matches = re.findall(FIELD.format(name=name), text, re.MULTILINE)
        if len(matches) > 1:
            return None, f"{name} is declared {len(matches)} times; exactly one must"
        if matches:
            binding[name] = matches[0].strip("\"'")

    missing = [name for name in REQUIRED if name not in binding]
    if missing:
        return None, f"binding omits {','.join(missing)}"
    return binding, None


def version_key(name: str) -> tuple:
    """Order releases so a pre-release ranks below the version it precedes."""
    core, _, pre = name.partition("+")[0].partition("-")
    parts = tuple(int(p) if p.isdigit() else -1 for p in core.split("."))
    return (parts, 0 if pre else 1, pre)


def reference_digest(release: Path) -> str | None:
    """Digest every regular file under the release's `references/`, path-ordered."""
    root = release / "references"
    if not root.is_dir():
        return None
    entries = []
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        entries.append(
            (path.relative_to(release).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
        )
    if not entries:
        return None
    manifest = "".join(f"{name}\n{digest}\n" for name, digest in sorted(entries))
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()


def entrypoint_in(release: Path, relative: str) -> Path | None:
    """Resolve inside the release, refusing anything that escapes it."""
    try:
        resolved = (release / relative).resolve(strict=True)
        resolved.relative_to(release.resolve())
        return resolved
    except (OSError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binding", type=Path, help="the adopter's kernel binding file")
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=DEFAULT_CACHE,
        help="installed-plugin cache root; override exists for tests, not for callers",
    )
    args = parser.parse_args()

    binding, error = read_binding(args.binding)
    if binding is None:
        return emit("UNRESOLVABLE", error or "unreadable binding")

    # kernel_source is <owner>/<marketplace>/<plugin>; the cache is addressed by
    # the trailing two, and every installed release sits in its own version dir.
    parts = binding["kernel_source"].strip("/").split("/")
    if len(parts) < 2:
        return emit("UNRESOLVABLE", f"kernel_source {binding['kernel_source']} is not <owner>/<marketplace>/<plugin>")
    plugin_root = args.cache_root / parts[-2] / parts[-1]
    if not plugin_root.is_dir():
        return emit("UNRESOLVABLE", f"no installed releases for {binding['kernel_source']} under {args.cache_root}")

    installed = sorted(
        (d for d in plugin_root.iterdir() if d.is_dir() and VERSION_DIR.match(d.name)),
        key=lambda d: version_key(d.name),
    )
    if not installed:
        return emit("UNRESOLVABLE", f"{plugin_root} holds no versioned release")

    pinned_version = binding["kernel_version"]
    pinned = plugin_root / pinned_version
    if not pinned.is_dir() or not VERSION_DIR.match(pinned_version):
        # The pinned release is not on this machine, so the pin cannot be checked
        # at all — which is different from being out of date and must not read
        # the same.
        return emit("UNRESOLVABLE", f"pinned {pinned_version} is not installed; have {', '.join(d.name for d in installed)}")

    pinned_entry = entrypoint_in(pinned, binding["kernel_entrypoint"])
    if pinned_entry is None:
        return emit("UNRESOLVABLE", f"entrypoint {binding['kernel_entrypoint']} does not resolve inside {pinned_version}")

    pinned_digest = reference_digest(pinned)
    if pinned_digest is None:
        return emit("UNRESOLVABLE", f"release {pinned_version} ships no references/ to digest")

    # Printed whenever a release resolves, so a rebind — and a first adoption,
    # which starts with no digest to state — is mechanical rather than computed
    # by hand over a set of files.
    expected = f"verify-binding:expected-digest:{pinned_digest}"

    declared = binding.get("kernel_digest")
    if declared is None:
        return emit("UNRESOLVABLE", f"binding omits kernel_digest for {pinned_version}", expected)
    if declared.lower() != pinned_digest:
        # The binding disagrees with the very release it names. Nothing about a
        # newer version matters until this is repaired.
        return emit(
            "REBIND_REQUIRED",
            f"binding claims {declared[:12].lower()} for {pinned_version}, but that release is {pinned_digest[:12]}",
            f"verify-binding:entrypoint:{pinned_entry}",
            expected,
        )

    newest = installed[-1]
    if newest.name == pinned_version:
        return emit(
            "PASS",
            f"{binding['kernel_source']}@{pinned_version} is the newest installed",
            # The agent's read path. A stale pin answers "which file do I read"
            # wrongly and silently, so it is answered out loud on every pass.
            f"verify-binding:entrypoint:{pinned_entry}",
        )

    newest_entry = entrypoint_in(newest, binding["kernel_entrypoint"])
    if newest_entry is None:
        return emit(
            "REBIND_REQUIRED",
            f"{newest.name} is installed and no longer carries {binding['kernel_entrypoint']}",
            f"verify-binding:entrypoint:{pinned_entry}",
        )

    newest_digest = reference_digest(newest)
    if newest_digest is None:
        return emit("UNRESOLVABLE", f"release {newest.name} ships no references/ to digest")

    newer = f"verify-binding:expected-digest:{newest_digest}"
    if newest_digest == pinned_digest:
        return emit(
            "STALE_COMPATIBLE",
            f"pinned {pinned_version}, {newest.name} installed; no reference text changed",
            f"verify-binding:entrypoint:{newest_entry}",
            newer,
        )

    return emit(
        "REBIND_REQUIRED",
        f"pinned {pinned_version}, {newest.name} installed and its references differ",
        f"verify-binding:entrypoint:{newest_entry}",
        newer,
    )


if __name__ == "__main__":
    sys.exit(main())
