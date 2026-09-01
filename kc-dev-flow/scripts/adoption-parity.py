#!/usr/bin/env python3
"""Refuse dispatch when an adopter's canonical files differ from this package."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


class ParityError(RuntimeError):
    """The installed package cannot prove the adopter uses its contract set."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adopter-root", type=Path, required=True)
    parser.add_argument("--contracts-root", type=Path, required=True)
    parser.add_argument("--profile-loader", type=Path, required=True)
    parser.add_argument("--poc-close-guard", type=Path, required=True)
    parser.add_argument(
        "--planning-mode",
        choices=("standalone", "provider-capable"),
        required=True,
    )
    parser.add_argument("--engage-comparator", type=Path)
    return parser.parse_args()


def read_regular(path: Path, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ParityError(f"canonical file is missing or not regular: {label}")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ParityError(f"canonical file is unreadable: {label}") from exc


def require_adopter_path(path: Path, root: Path, package: Path, label: str) -> None:
    absolute_root = root.absolute()
    absolute_path = path.absolute()
    if absolute_root.is_symlink() or not absolute_root.is_dir():
        raise ParityError("adopter root is missing, not a directory, or a symbolic link")
    try:
        relative = absolute_path.relative_to(absolute_root)
    except ValueError as exc:
        raise ParityError(f"canonical path is outside adopter root: {label}") from exc
    current = absolute_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ParityError(f"canonical path contains a symbolic link: {label}")
    try:
        absolute_path.resolve(strict=False).relative_to(package)
    except ValueError:
        return
    raise ParityError(f"canonical path resolves inside installed package: {label}")


def package_version(package: Path) -> str:
    manifests = (
        package / ".claude-plugin/plugin.json",
        package / ".codex-plugin/plugin.json",
        package / "plugin.json",
    )
    versions: set[str] = set()
    for manifest in manifests:
        try:
            value = json.loads(read_regular(manifest, manifest.name))["version"]
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ParityError("installed package manifest is invalid") from exc
        if not isinstance(value, str) or not value:
            raise ParityError("installed package version is invalid")
        versions.add(value)
    if len(versions) != 1:
        raise ParityError("installed package manifests disagree")
    return versions.pop()


def compare(
    source: Path,
    adopted: Path,
    adopter_root: Path,
    package: Path,
    label: str,
) -> dict[str, str]:
    require_adopter_path(adopted, adopter_root, package, label)
    source_bytes = read_regular(source, f"package/{label}")
    adopted_bytes = read_regular(adopted, label)
    if source.samefile(adopted):
        raise ParityError(f"canonical path is the same installed package file: {label}")
    if source_bytes != adopted_bytes:
        raise ParityError(f"canonical file differs from installed package: {label}")
    return {"path": label, "sha256": hashlib.sha256(source_bytes).hexdigest()}


def verify(args: argparse.Namespace) -> dict[str, object]:
    package = Path(__file__).resolve().parents[1]
    adopter_root = args.adopter_root.absolute()
    if args.planning_mode == "provider-capable" and args.engage_comparator is None:
        raise ParityError("provider-capable mode requires --engage-comparator")
    if args.planning_mode == "standalone" and args.engage_comparator is not None:
        raise ParityError("standalone mode refuses --engage-comparator")
    package_references = package / "references"
    if package_references.is_symlink() or not package_references.is_dir():
        raise ParityError("installed package references are unavailable")
    records: list[dict[str, str]] = []
    reference_files = sorted(
        path for path in package_references.rglob("*") if path.is_file() or path.is_symlink()
    )
    if not reference_files:
        raise ParityError("installed package has no canonical references")
    for source in reference_files:
        relative = source.relative_to(package_references)
        records.append(
            compare(
                source,
                args.contracts_root / relative,
                adopter_root,
                package,
                f"references/{relative.as_posix()}",
            )
        )

    for source_name, adopted, label in (
        ("profile-contract-loader.py", args.profile_loader, "scripts/profile-contract-loader.py"),
        ("poc-close-guard.py", args.poc_close_guard, "scripts/poc-close-guard.py"),
    ):
        records.append(
            compare(package / "scripts" / source_name, adopted, adopter_root, package, label)
        )
    if args.engage_comparator is not None:
        records.append(
            compare(
                package / "scripts/engage-reconcile.py",
                args.engage_comparator,
                adopter_root,
                package,
                "scripts/engage-reconcile.py",
            )
        )

    canonical_set = {
        "schema": "kc-dev-flow-canonical-set/v1",
        "planning_mode": args.planning_mode,
        "files": sorted(records, key=lambda record: record["path"]),
    }
    encoded = json.dumps(canonical_set, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return {
        "schema": "kc-dev-flow-adoption-parity/v1",
        "status": "clean",
        "package_version": package_version(package),
        "planning_mode": args.planning_mode,
        "canonical_file_count": len(records),
        "canonical_set_sha256": hashlib.sha256(encoded).hexdigest(),
    }


def main() -> int:
    try:
        envelope = verify(parse_args())
    except ParityError as exc:
        print(f"adoption parity: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"adoption parity: unexpected refusal ({type(exc).__name__})", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
