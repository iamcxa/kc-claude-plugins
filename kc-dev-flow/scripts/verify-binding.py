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
shape it exists to detect. The binding file remains caller-supplied, so a caller
naming the wrong file is a misconfiguration this cannot detect; what it does
close is the file being read as a binding when it is not one.

Five revisions of this checker returned PASS for repositories that had no
binding: fields collected across Markdown blocks, an unclosed fence, an indented
example, a shape filter admitting any `Word: sentence` line, and prose carried
where the scan does not look. Three mechanisms now refuse a document, and it is
worth being exact about which one carries the weight, because a maintainer who
believes the wrong one will delete the load-bearing check:

  * `PROSE_SUFFIXES` refuses a prose *filename*, resolved through symlinks. It
    is a shape filter -- the mechanism the fourth variant discredited -- and it
    is nonetheless the primary defense against the historical failure, because
    every one of those variants arrived as a Markdown file. It is load-bearing,
    not belt-and-braces. Do not remove it on the belief that the allowlist
    subsumes it.
  * `BINDING_KEYS` refuses an unrecognised key, but only an *unindented,
    uncommented* one. Markdown headings are YAML comments and are skipped.
  * An indented line must have a block-opening key above it, so prose indented
    under a heading is refused as having no parent.

What none of them can refuse is a document that is a well-formed binding record
carrying odd values -- prose parked under `authority:`, for instance. That file
is semantically a binding, and no parser distinguishes it from one. Naming the
right file remains the caller's responsibility.

The digest covers the release's whole `references/` set, and the entrypoint must
resolve to a regular file inside that same set. The kernel names the Work
Control Profile as an independent declaration and the reverse-recovery audit as
a normative procedure, so a release that moved either moved an invariant an
adopter is bound to. Tying the entrypoint to the digested set keeps the two from
drifting apart: an entrypoint outside it could be rewritten while this reported
that nothing changed.

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
# The unindented, uncommented top level carries these and nothing else. Widening
# this set widens what counts as a binding, so `kc-dev-flow-contract-test.py`
# requires it to equal the shipped template's top-level keys exactly.
BINDING_KEYS = frozenset(
    (
        "kernel_source",
        "kernel_version",
        "kernel_entrypoint",
        "kernel_digest",
        "authority",
        "upstream_contribution",
        "adopted_controls",
        "local_routes",
        "local_exceptions",
    )
)
# release-please cuts semver directories; anything else in the cache root is an
# installer artifact rather than a release, and ranking it would invent a newest.
VERSION_DIR = re.compile(r"^\d+(?:\.\d+)*(?:-[0-9A-Za-z.\-]+)?(?:\+[0-9A-Za-z.\-]+)?$")
TOP_LEVEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_.\-]*):(?:[ \t]+(.*?))?[ \t]*$")
IGNORABLE = re.compile(r"^(?:#.*|---|\.\.\.)?[ \t]*$")
# Column zero only: a nested or indented key belongs to some other mapping.
FIELD = r"^{name}:[ \t]*(?P<value>[^\s#]+)[ \t]*(?:#.*)?$"


def emit(outcome: str, detail: str, *lines: str) -> int:
    print(f"verify-binding:{outcome}:{detail}")
    for line in lines:
        print(line)
    return 0 if outcome == "PASS" else 1


def read_binding(path: Path) -> tuple[dict[str, str] | None, str | None]:
    """Return (binding, error) from a file whose top level is binding keys only.

    Each field must appear exactly once at column zero. A repeated field is
    refused rather than resolved: choosing between two values would verify a
    binding the repository does not operate under.
    """
    # Resolved, so that naming a prose document through a symlink is refused for
    # the same reason as naming it directly.
    target = path.resolve() if path.exists() else path
    if target.suffix.lower() in PROSE_SUFFIXES:
        return None, (
            f"{target.name} is a prose document; the binding is read from a file "
            "whose top level carries binding keys and nothing else"
        )
    if not path.is_file():
        return None, f"{path} is not a readable file"

    text = path.read_text(encoding="utf-8", errors="replace")
    open_block = False
    for number, line in enumerate(text.splitlines(), start=1):
        if IGNORABLE.match(line):
            continue
        if line[:1] in (" ", "\t"):
            # Indentation nests under the key above it. Prose indented beneath a
            # heading has no such key, and is not a value of anything.
            if not open_block:
                return None, f"{path.name}:{number} is indented under no binding key: {line.strip()[:48]!r}"
            continue
        match = TOP_LEVEL.match(line)
        if match is None:
            return None, f"{path.name}:{number} is not a binding line: {line.strip()[:48]!r}"
        if match.group(1) not in BINDING_KEYS:
            return None, f"{path.name}:{number} declares {match.group(1)!r}, which is not a binding key"
        inline = match.group(2)
        open_block = inline is None or inline.startswith("#")

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


def reference_digest(release: Path) -> tuple[str | None, str | None]:
    """Digest every regular file under the release's `references/`, path-ordered.

    A symlink is refused rather than followed -- the release directory, the
    `references/` root, and every entry beneath it. Bytes reached through a link
    are not the release's bytes, and the link's target can be replaced without
    the release changing at all.
    """
    if release.is_symlink():
        return None, f"release {release.name} is a symlink, not an installed release"
    root = release / "references"
    if root.is_symlink():
        return None, f"release {release.name} reaches references/ through a symlink"
    if not root.is_dir():
        return None, f"release {release.name} ships no references/ to digest"
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            return None, f"release {release.name} carries a symlink under references/: {path.name}"
        if not path.is_file():
            continue
        entries.append(
            (path.relative_to(release).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
        )
    if not entries:
        return None, f"release {release.name} has an empty references/"
    manifest = "".join(f"{name}\n{digest}\n" for name, digest in sorted(entries))
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest(), None


def entrypoint_in(release: Path, relative: str) -> Path | None:
    """Resolve to a regular file inside the release's digested reference set."""
    try:
        root = (release / "references").resolve(strict=True)
        resolved = (release / relative).resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError):
        return None
    return resolved if resolved.is_file() else None


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
    source = binding["kernel_source"]
    parts = source.strip("/").split("/")
    if len(parts) < 2 or any(part in ("", ".", "..") for part in parts):
        return emit("UNRESOLVABLE", f"kernel_source {source} is not <owner>/<marketplace>/<plugin>")
    plugin_root = args.cache_root / parts[-2] / parts[-1]
    if not plugin_root.is_dir():
        return emit("UNRESOLVABLE", f"no installed releases for {source} under {args.cache_root}")

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

    # The set is digested before the entrypoint is resolved, so a release with no
    # usable reference set says so, rather than reporting the entrypoint missing
    # from a set that does not exist.
    pinned_digest, digest_error = reference_digest(pinned)
    if pinned_digest is None:
        return emit("UNRESOLVABLE", digest_error or "reference set could not be digested")

    pinned_entry = entrypoint_in(pinned, binding["kernel_entrypoint"])
    if pinned_entry is None:
        return emit(
            "UNRESOLVABLE",
            f"entrypoint {binding['kernel_entrypoint']} is not a file inside {pinned_version}/references/",
        )

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
            f"{source}@{pinned_version} is the newest installed",
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

    newest_digest, digest_error = reference_digest(newest)
    if newest_digest is None:
        return emit("UNRESOLVABLE", digest_error or "reference set could not be digested")

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
