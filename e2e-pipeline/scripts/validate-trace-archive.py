#!/usr/bin/env python3
"""Validate and safely materialize the subset of a Playwright trace we consume."""

from __future__ import annotations

import os
import re
import shutil
import stat
import sys
import zipfile
from pathlib import PurePosixPath

INVALID_ZIP = 2
UNSAFE_ARCHIVE = 3
MISSING_PLAYWRIGHT_CONTENT = 4
RESOURCE_NOT_FOUND = 5
ARCHIVE_LIMIT_EXCEEDED = 6
USAGE = 64
RESOURCE_ID_RE = re.compile(r"[0-9a-f]{40}")
DEFAULT_MAX_ENTRIES = 50_000
DEFAULT_MAX_TOTAL_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
DEFAULT_MAX_ENTRY_UNCOMPRESSED_BYTES = 512 * 1024 * 1024
DEFAULT_MAX_COMPRESSION_RATIO = 1_000


class UnsafeArchiveError(Exception):
    pass


class ResourceNotFoundError(Exception):
    pass


class ArchiveLimitError(Exception):
    pass


class MissingPlaywrightContentError(Exception):
    pass


def positive_integer_environment(name: str, default: int) -> int:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value, 10)
    except ValueError as error:
        raise ArchiveLimitError(f"{name} must be a positive integer") from error
    if value <= 0:
        raise ArchiveLimitError(f"{name} must be a positive integer")
    return value


def archive_limits() -> dict[str, int]:
    return {
        "max_entries": positive_integer_environment(
            "E2E_TRACE_MAX_ENTRIES", DEFAULT_MAX_ENTRIES
        ),
        "max_total_uncompressed_bytes": positive_integer_environment(
            "E2E_TRACE_MAX_TOTAL_UNCOMPRESSED_BYTES",
            DEFAULT_MAX_TOTAL_UNCOMPRESSED_BYTES,
        ),
        "max_entry_uncompressed_bytes": positive_integer_environment(
            "E2E_TRACE_MAX_ENTRY_UNCOMPRESSED_BYTES",
            DEFAULT_MAX_ENTRY_UNCOMPRESSED_BYTES,
        ),
        "max_compression_ratio": positive_integer_environment(
            "E2E_TRACE_MAX_COMPRESSION_RATIO", DEFAULT_MAX_COMPRESSION_RATIO
        ),
    }


def safe_entry_name(name: str) -> bool:
    if not name or "\\" in name or name.startswith("/"):
        return False
    raw_parts = name.split("/")
    if name.endswith("/"):
        raw_parts = raw_parts[:-1]
    if not raw_parts or any(part in ("", ".", "..") for part in raw_parts):
        return False
    path = PurePosixPath(name)
    return not path.is_absolute() and all(part not in (".", "..") for part in path.parts)


def entry_kind(info: zipfile.ZipInfo) -> int:
    return stat.S_IFMT((info.external_attr >> 16) & 0xFFFF)


def validate_info(info: zipfile.ZipInfo) -> None:
    if not safe_entry_name(info.filename):
        raise UnsafeArchiveError(f"unsafe entry name: {info.filename!r}")
    if info.flag_bits & 0x1:
        raise UnsafeArchiveError(f"encrypted entry: {info.filename!r}")

    kind = entry_kind(info)
    if info.is_dir():
        if kind not in (0, stat.S_IFDIR):
            raise UnsafeArchiveError(f"directory has unsafe type: {info.filename!r}")
    elif kind not in (0, stat.S_IFREG):
        raise UnsafeArchiveError(f"non-regular entry: {info.filename!r}")


def validate_metadata_limits(
    infos: list[zipfile.ZipInfo], archive_size: int, limits: dict[str, int]
) -> None:
    if len(infos) > limits["max_entries"]:
        raise ArchiveLimitError(
            f"max_entries exceeded: {len(infos)} > {limits['max_entries']}"
        )

    total_uncompressed = 0
    for info in infos:
        if info.file_size < 0 or info.compress_size < 0 or info.header_offset < 0:
            raise UnsafeArchiveError(f"negative ZIP metadata: {info.filename!r}")
        if info.header_offset >= archive_size:
            raise UnsafeArchiveError(
                f"entry header offset exceeds archive: {info.filename!r}"
            )
        if info.compress_size > archive_size:
            raise UnsafeArchiveError(
                f"compressed size exceeds archive: {info.filename!r}"
            )
        if info.is_dir():
            continue
        if info.file_size > limits["max_entry_uncompressed_bytes"]:
            raise ArchiveLimitError(
                "max_entry_uncompressed_bytes exceeded: "
                f"{info.filename!r} {info.file_size} > "
                f"{limits['max_entry_uncompressed_bytes']}"
            )

        total_uncompressed += info.file_size
        if total_uncompressed > limits["max_total_uncompressed_bytes"]:
            raise ArchiveLimitError(
                "max_total_uncompressed_bytes exceeded: "
                f"{total_uncompressed} > {limits['max_total_uncompressed_bytes']}"
            )

        if info.file_size > 0 and info.compress_size == 0:
            raise ArchiveLimitError(
                f"max_compression_ratio exceeded: {info.filename!r} has zero compressed bytes"
            )
        if (
            info.compress_size > 0
            and info.file_size
            > limits["max_compression_ratio"] * info.compress_size
        ):
            raise ArchiveLimitError(
                "max_compression_ratio exceeded: "
                f"{info.filename!r} {info.file_size}/{info.compress_size} > "
                f"{limits['max_compression_ratio']}"
            )


def validate_archive(archive: str) -> list[zipfile.ZipInfo]:
    try:
        archive_size = os.path.getsize(archive)
        with zipfile.ZipFile(archive) as trace_zip:
            infos = trace_zip.infolist()
            limits = archive_limits()

            seen: set[str] = set()
            has_trace_content = False
            for info in infos:
                validate_info(info)
                if info.filename in seen:
                    raise UnsafeArchiveError(f"duplicate entry: {info.filename!r}")
                seen.add(info.filename)
                if not info.is_dir() and info.filename in ("trace.trace", "trace.network"):
                    has_trace_content = True

            validate_metadata_limits(infos, archive_size, limits)
            if not has_trace_content:
                raise MissingPlaywrightContentError(
                    "missing root-level trace.trace or trace.network"
                )

            # Metadata and resource limits are deliberately checked before this
            # full read so a declared zip bomb never reaches decompression.
            bad_member = trace_zip.testzip()
            if bad_member is not None:
                raise zipfile.BadZipFile(f"CRC failure: {bad_member}")
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as error:
        raise zipfile.BadZipFile(str(error)) from error
    return infos


def should_materialize(info: zipfile.ZipInfo) -> bool:
    return (
        info.filename in ("trace.trace", "trace.network")
        or info.filename == "resources/"
        or info.filename.startswith("resources/")
    )


def materialize(archive: str, destination: str) -> None:
    infos = validate_archive(archive)
    os.mkdir(destination, 0o700)
    destination_real = os.path.realpath(destination)

    try:
        with zipfile.ZipFile(archive) as trace_zip:
            for info in infos:
                if not should_materialize(info):
                    continue
                target = os.path.join(destination, *PurePosixPath(info.filename).parts)
                target_real = os.path.realpath(target)
                if os.path.commonpath((destination_real, target_real)) != destination_real:
                    raise UnsafeArchiveError(f"entry escapes destination: {info.filename!r}")
                if info.is_dir():
                    os.makedirs(target, mode=0o700, exist_ok=True)
                    continue
                os.makedirs(os.path.dirname(target), mode=0o700, exist_ok=True)
                flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
                if hasattr(os, "O_NOFOLLOW"):
                    flags |= os.O_NOFOLLOW
                descriptor = os.open(target, flags, 0o600)
                with os.fdopen(descriptor, "wb") as output, trace_zip.open(info, "r") as source:
                    shutil.copyfileobj(source, output)
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def resolve_resource_path(materialized: str, resource_id: str) -> str:
    if RESOURCE_ID_RE.fullmatch(resource_id) is None:
        raise UnsafeArchiveError(
            "resource identifier must be exactly 40 lowercase hexadecimal characters"
        )

    materialized_real = os.path.realpath(materialized)
    resources_real = os.path.realpath(os.path.join(materialized_real, "resources"))
    if not os.path.isdir(materialized_real) or not os.path.isdir(resources_real):
        raise ResourceNotFoundError("materialized resources directory is missing")
    if os.path.commonpath((materialized_real, resources_real)) != materialized_real:
        raise UnsafeArchiveError("resources directory escapes materialized trace")

    target = os.path.join(resources_real, resource_id)
    target_real = os.path.realpath(target)
    if os.path.commonpath((resources_real, target_real)) != resources_real:
        raise UnsafeArchiveError("resource path escapes resources directory")
    try:
        target_stat = os.lstat(target)
    except FileNotFoundError as error:
        raise ResourceNotFoundError(f"resource is missing: {resource_id}") from error
    if stat.S_ISLNK(target_stat.st_mode) or not stat.S_ISREG(target_stat.st_mode):
        raise UnsafeArchiveError(f"resource is not a regular file: {resource_id}")
    return target_real


def main() -> int:
    if len(sys.argv) not in (3, 4) or sys.argv[1] not in (
        "validate",
        "extract",
        "resource-path",
    ):
        print(
            "usage: validate-trace-archive.py validate <archive> | "
            "extract <archive> <fresh-destination> | "
            "resource-path <materialized-trace> <sha1>",
            file=sys.stderr,
        )
        return USAGE

    command = sys.argv[1]
    try:
        if command == "validate":
            if len(sys.argv) != 3:
                return USAGE
            validate_archive(sys.argv[2])
        elif command == "extract":
            if len(sys.argv) != 4:
                return USAGE
            materialize(sys.argv[2], sys.argv[3])
        else:
            if len(sys.argv) != 4:
                return USAGE
            print(resolve_resource_path(sys.argv[2], sys.argv[3]))
            return 0
    except zipfile.BadZipFile as error:
        print(f"invalid_zip: {error}", file=sys.stderr)
        return INVALID_ZIP
    except UnsafeArchiveError as error:
        print(f"unsafe_archive: {error}", file=sys.stderr)
        return UNSAFE_ARCHIVE
    except MissingPlaywrightContentError as error:
        print(f"missing_playwright_content: {error}", file=sys.stderr)
        return MISSING_PLAYWRIGHT_CONTENT
    except ResourceNotFoundError as error:
        print(f"resource_not_found: {error}", file=sys.stderr)
        return RESOURCE_NOT_FOUND
    except ArchiveLimitError as error:
        print(f"archive_limit_exceeded: {error}", file=sys.stderr)
        return ARCHIVE_LIMIT_EXCEEDED
    except OSError as error:
        print(f"unsafe_archive: {error}", file=sys.stderr)
        return UNSAFE_ARCHIVE

    print("valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
