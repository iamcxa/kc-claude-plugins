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

Outcomes are closed:

  PASS              pinned version is the newest installed, and its bytes match
  STALE_COMPATIBLE  a newer release is installed, but the entrypoint is unchanged
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

FIELDS = ("kernel_source", "kernel_version", "kernel_digest", "kernel_entrypoint")
IDENTIFYING = ("kernel_source", "kernel_version")
DEFAULT_CACHE = Path.home() / ".claude" / "plugins" / "cache"
FENCE = re.compile(r"^[ \t]*(?:```+|~~~+)", re.MULTILINE)


def emit(outcome: str, detail: str, entrypoint: Path | None = None) -> int:
    print(f"verify-binding:{outcome}:{detail}")
    if entrypoint is not None:
        # The agent's read path. A stale pin answers "which file do I read"
        # wrongly and silently, so it is answered out loud on every resolution.
        print(f"verify-binding:entrypoint:{entrypoint}")
    return 0 if outcome == "PASS" else 1


def fenced_blocks(text: str) -> list[str]:
    """Split on fence lines and keep the odd segments, which are block bodies."""
    parts = FENCE.split(text)
    return parts[1::2]


def read_binding(readme: Path) -> tuple[dict[str, str] | None, str | None]:
    """Return (binding, error). A binding is read from ONE block, never assembled.

    Fields scattered across a document — a quoted example, an appendix, a
    changelog line — are not a binding, and treating them as one lets a
    repository with no binding at all report success.
    """
    if not readme.is_file():
        return None, f"{readme} is not a readable file"

    candidates: list[dict[str, str]] = []
    for block in fenced_blocks(readme.read_text(encoding="utf-8", errors="replace")):
        found = {}
        for field in FIELDS:
            match = re.search(rf"^[ \t]*{field}:[ \t]*(\S+)[ \t]*$", block, re.MULTILINE)
            if match:
                found[field] = match.group(1).strip().strip("\"'")
        if all(key in found for key in IDENTIFYING):
            candidates.append(found)

    if not candidates:
        return None, "no fenced block declares both kernel_source and kernel_version"
    if len(candidates) > 1:
        # Choosing between them would be a guess, and a wrong guess verifies a
        # binding the repository does not operate under.
        return None, f"{len(candidates)} blocks declare a binding; exactly one must"

    binding = candidates[0]
    missing = [f for f in FIELDS if f not in binding]
    if missing:
        return None, f"binding omits {','.join(missing)}"
    return binding, None


def version_key(name: str) -> tuple:
    return tuple(int(p) if p.isdigit() else -1 for p in re.split(r"[.\-+]", name))


def digest_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    parser.add_argument("readme", type=Path, help="adopter workflow README carrying the binding")
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=DEFAULT_CACHE,
        help="installed-plugin cache root; override exists for tests, not for callers",
    )
    args = parser.parse_args()

    binding, error = read_binding(args.readme)
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

    installed = sorted((d for d in plugin_root.iterdir() if d.is_dir()), key=lambda d: version_key(d.name))
    if not installed:
        return emit("UNRESOLVABLE", f"{plugin_root} holds no versioned release")

    pinned_version = binding["kernel_version"]
    pinned = plugin_root / pinned_version
    if not pinned.is_dir():
        # The pinned release is not on this machine, so the pin cannot be checked
        # at all — which is different from being out of date and must not read
        # the same.
        return emit("UNRESOLVABLE", f"pinned {pinned_version} is not installed; have {', '.join(d.name for d in installed)}")

    pinned_entry = entrypoint_in(pinned, binding["kernel_entrypoint"])
    if pinned_entry is None:
        return emit("UNRESOLVABLE", f"entrypoint {binding['kernel_entrypoint']} does not resolve inside {pinned_version}")

    pinned_digest = digest_of(pinned_entry)
    if pinned_digest != binding["kernel_digest"]:
        # The binding disagrees with the very release it names. Nothing about a
        # newer version matters until this is repaired.
        return emit(
            "REBIND_REQUIRED",
            f"binding claims {binding['kernel_digest'][:12]} for {pinned_version}, but that release is {pinned_digest[:12]}",
            pinned_entry,
        )

    newest = installed[-1]
    if newest.name == pinned_version:
        return emit("PASS", f"{binding['kernel_source']}@{pinned_version} is the newest installed", pinned_entry)

    newest_entry = entrypoint_in(newest, binding["kernel_entrypoint"])
    if newest_entry is None:
        return emit("REBIND_REQUIRED", f"{newest.name} is installed and no longer carries {binding['kernel_entrypoint']}", pinned_entry)

    if digest_of(newest_entry) == pinned_digest:
        return emit("STALE_COMPATIBLE", f"pinned {pinned_version}, {newest.name} installed; entrypoint unchanged", newest_entry)

    return emit("REBIND_REQUIRED", f"pinned {pinned_version}, {newest.name} installed and the entrypoint differs", newest_entry)


if __name__ == "__main__":
    sys.exit(main())
