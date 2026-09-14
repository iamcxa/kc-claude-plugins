#!/usr/bin/env python3
"""Read-only adopter conformance check shipped by the kc-dev-flow package itself.

An adopter that has refit onto the installed `kc-dev-flow` contracts (see
`MIGRATION.md` and `skills/adopt-dev-flow/SKILL.md`) runs this script from its own
CI, pointed at the installed package, to prove four things without maintaining a
repository-local copy of any of these checks:

1. The adopter's marked `## Local Profile` block carries every row the installed
   `kc-dev-flow-local-profile/v1` interface requires.
2. If the adopter's `Local mods` bind a `pr-merge.md` local mod, its
   `<!-- kc-dev-flow runtime extension:start -->` .. `:end -->` block matches this
   package's `references/pr-merge-extension.md` byte-for-byte.
3. That same mod's released body (everything before the extension's start
   marker, trailing newlines stripped) matches the pin recorded for the mod's
   own declared `version:` in `contract-manifest.json`'s
   `pr_merge_released_body_pin_per_mod_version` table.
4. The adopter's `docs/dev` tree carries no file whose bytes are byte-identical
   to a canonical resource this package ships -- a leftover vendored copy that
   `MIGRATION.md` says to delete once the installed route is proven.

This script does not write anything. A conforming adopter exits 0; any other
result names the specific row, block, body, or leftover path that diverged.

usage: adopter-contract-test.py --repo <adopter-repo-root>
                                 [--local-profile <path, default docs/dev/README.md>]
                                 [--package-root <path, default: this script's installed package>]
exit 0: the adopter conforms.
exit 1: at least one conformance check failed; stderr names the diverged row, block, or body.
exit 2: usage error, an unreadable input, or a malformed installed package/manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOADER_PATH = HERE / "profile-contract-loader.py"

EXTENSION_START_MARKER = "<!-- kc-dev-flow runtime extension:start -->\n"
EXTENSION_END_MARKER = "<!-- kc-dev-flow runtime extension:end -->\n"


class CheckError(RuntimeError):
    """A conformance divergence -- reported on stderr, exit 1."""


class UsageError(RuntimeError):
    """A usage, read, or installed-package defect -- reported on stderr, exit 2."""


def load_profile_loader():
    spec = importlib.util.spec_from_file_location("profile_contract_loader", LOADER_PATH)
    if spec is None or spec.loader is None:
        raise UsageError(f"cannot import profile loader at {LOADER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_manifest(package_root: Path) -> dict[str, object]:
    manifest_path = package_root / "contract-manifest.json"
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise UsageError(f"cannot read installed manifest {manifest_path}: {exc}") from exc
    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UsageError(f"installed manifest {manifest_path} is not valid JSON: {exc}") from exc
    if manifest.get("schema") != "kc-dev-flow-contract-manifest/v1":
        raise UsageError(f"{manifest_path} does not declare kc-dev-flow-contract-manifest/v1")
    return manifest


def check_local_profile(loader, local_profile_path: Path, manifest: dict[str, object]) -> dict[str, object]:
    """Row check: reuses the installed loader's own `read_local_profile`, the same
    reader that gates every dispatch, so this cannot drift from what actually binds."""
    interface = manifest["local_profile_interface"]
    try:
        return loader.read_local_profile(local_profile_path, interface)
    except loader.ContractError as exc:
        raise CheckError(f"LOCAL_PROFILE: {exc}") from exc


def resolve_pr_merge_mod_path(local_mods_row: str) -> Path | None:
    """`Local mods` names paths relative to the adopter repository root, matching
    how the row is written throughout this package's own README and MIGRATION.md
    (e.g. `docs/dev/_mods/pr-merge.md`); the caller resolves against `--repo`."""
    candidates = [part.strip(" `") for part in local_mods_row.split(",")]
    for candidate in candidates:
        if candidate and Path(candidate).name == "pr-merge.md":
            return Path(candidate)
    return None


def read_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise UsageError(f"cannot read {label} {path}: {exc}") from exc


def extract_mod_version(mod_text: str, mod_path: Path) -> str:
    if not mod_text.startswith("---\n"):
        raise CheckError(f"PR_MERGE_MOD: {mod_path} is missing leading frontmatter")
    frontmatter_end = mod_text.find("\n---\n", 4)
    if frontmatter_end < 0:
        raise CheckError(f"PR_MERGE_MOD: {mod_path} frontmatter is unterminated")
    frontmatter = mod_text[4:frontmatter_end]
    match = re.search(r"^version:[ \t]*([^\n#]+?)[ \t]*$", frontmatter, re.MULTILINE)
    if not match:
        raise CheckError(f"PR_MERGE_MOD: {mod_path} frontmatter is missing a version field")
    return match.group(1).strip()


def check_pr_merge_extension_block(mod_path: Path, mod_text: str, resource_path: Path) -> str:
    """Block check: the adopter's synced extension must match this package's
    `references/pr-merge-extension.md` byte-for-byte, mirroring the same
    comparison `scripts/kc-dev-flow-contract-test.py` runs for this repository's
    own copy."""
    if mod_text.count(EXTENSION_START_MARKER) != 1:
        raise CheckError(f"PR_MERGE_BLOCK: {mod_path} runtime extension start marker is not unique")
    if mod_text.count(EXTENSION_END_MARKER) != 1:
        raise CheckError(f"PR_MERGE_BLOCK: {mod_path} runtime extension end marker is not unique")
    start = mod_text.index(EXTENSION_START_MARKER)
    end = mod_text.index(EXTENSION_END_MARKER) + len(EXTENSION_END_MARKER)
    if end <= start:
        raise CheckError(f"PR_MERGE_BLOCK: {mod_path} runtime extension end marker precedes its start marker")
    if mod_text[:end].count(EXTENSION_END_MARKER.rstrip("\n")) != 1:
        raise CheckError(
            f"PR_MERGE_BLOCK: {mod_path} quotes its own runtime extension end marker "
            "somewhere other than the marker line itself, within the extension's own block"
        )
    mod_extension = mod_text[start:end]
    resource_text = read_text(resource_path, "pr-merge-extension.md resource")
    if not resource_text.endswith(EXTENSION_END_MARKER):
        raise UsageError(f"{resource_path} does not end at its own runtime extension end marker")
    if mod_extension != resource_text:
        first_diff = next(
            (
                index
                for index, (mod_char, resource_char) in enumerate(zip(mod_extension, resource_text))
                if mod_char != resource_char
            ),
            min(len(mod_extension), len(resource_text)),
        )
        context_start = max(0, first_diff - 20)
        raise CheckError(
            f"PR_MERGE_BLOCK: {mod_path} runtime extension block drifted from {resource_path} "
            f"at byte {first_diff}: mod={mod_extension[context_start:first_diff + 20]!r} "
            f"resource={resource_text[context_start:first_diff + 20]!r}"
        )
    return mod_extension


def check_pr_merge_released_body(mod_path: Path, mod_text: str, manifest: dict[str, object]) -> None:
    """Body check: the released body pin is keyed by the mod's own declared
    `version:`, so a mod-version bump that silently changes the released body
    (or a body edit that keeps the old version number) is caught either way."""
    released_body = mod_text.split(EXTENSION_START_MARKER, 1)[0].rstrip("\n")
    released_bytes = released_body.encode("utf-8")
    actual_sha256 = hashlib.sha256(released_bytes).hexdigest()
    mod_version = extract_mod_version(mod_text, mod_path)
    pin_table = manifest.get("pr_merge_released_body_pin_per_mod_version", {})
    if not isinstance(pin_table, dict) or mod_version not in pin_table:
        raise CheckError(
            f"PR_MERGE_BODY: {mod_path} declares pr-merge version {mod_version!r}, which has no "
            "entry in contract-manifest.json pr_merge_released_body_pin_per_mod_version"
        )
    pin = pin_table[mod_version]
    expected_sha256 = pin.get("sha256")
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise UsageError(
            f"contract-manifest.json pr_merge_released_body_pin_per_mod_version[{mod_version!r}] "
            "is missing a valid sha256"
        )
    if actual_sha256 != expected_sha256:
        raise CheckError(
            f"PR_MERGE_BODY: {mod_path} released body (version {mod_version!r}, everything before "
            f"'{EXTENSION_START_MARKER.strip()}') drifted from its pin: "
            f"expected sha256:{expected_sha256} got sha256:{actual_sha256} "
            f"(expected {pin.get('bytes')} bytes, got {len(released_bytes)})"
        )


def iter_docs_dev_files(docs_dev: Path):
    for path in sorted(docs_dev.rglob("*")):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(docs_dev).parts):
            continue
        yield path


def check_no_leftover_canonical_copies(
    repo: Path, package_root: Path, manifest: dict[str, object]
) -> None:
    """Leftover check: MIGRATION.md's cutover only deletes a canonical repository
    copy after the installed route is proven; a byte-identical copy left under
    `docs/dev` means that step never ran."""
    docs_dev = repo / "docs" / "dev"
    if not docs_dev.is_dir():
        return
    resource_hashes: dict[str, str] = {}
    for relative in manifest.get("resources", []):
        resource_path = package_root / relative
        try:
            resource_bytes = resource_path.read_bytes()
        except OSError as exc:
            raise UsageError(f"installed resource {relative} is unreadable: {exc}") from exc
        resource_hashes[hashlib.sha256(resource_bytes).hexdigest()] = relative
    if not resource_hashes:
        return
    for path in iter_docs_dev_files(docs_dev):
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            raise UsageError(f"cannot read {path}: {exc}") from exc
        if digest in resource_hashes:
            raise CheckError(
                f"LEFTOVER_COPY: {path.relative_to(repo)} is byte-identical to the installed "
                f"canonical resource {resource_hashes[digest]!r}; delete the repository copy "
                "per MIGRATION.md's cutover instead of keeping it alongside the installed package"
            )


def run(repo: Path, local_profile_path: Path, package_root: Path) -> None:
    manifest = load_manifest(package_root)
    loader = load_profile_loader()
    profile = check_local_profile(loader, local_profile_path, manifest)
    local_mods_row = profile.get("local_mods", "none")
    mod_path = resolve_pr_merge_mod_path(str(local_mods_row))
    if mod_path is not None:
        resolved_mod_path = mod_path if mod_path.is_absolute() else repo / mod_path
        mod_text = read_text(resolved_mod_path, "pr-merge local mod")
        check_pr_merge_extension_block(
            resolved_mod_path, mod_text, package_root / "references" / "pr-merge-extension.md"
        )
        check_pr_merge_released_body(resolved_mod_path, mod_text, manifest)
    check_no_leftover_canonical_copies(repo, package_root, manifest)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="adopter repository root")
    parser.add_argument(
        "--local-profile",
        type=Path,
        default=None,
        help="path to the marked Local Profile README (default: <repo>/docs/dev/README.md)",
    )
    parser.add_argument(
        "--package-root",
        type=Path,
        default=HERE.parent,
        help="installed kc-dev-flow package root (default: this script's own package)",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    repo = args.repo.expanduser().resolve()
    package_root = args.package_root.expanduser().resolve()
    local_profile_path = (
        args.local_profile.expanduser().resolve()
        if args.local_profile is not None
        else repo / "docs" / "dev" / "README.md"
    )
    try:
        run(repo, local_profile_path, package_root)
    except UsageError as exc:
        print(f"ADOPTER_CONTRACT_USAGE: {exc}", file=sys.stderr)
        return 2
    except CheckError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"ADOPTER_CONTRACT_OK: {repo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
