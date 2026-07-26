#!/usr/bin/env python3
"""Fail-closed JSON and file-ingestion primitives for review-runtime.sh."""

from __future__ import annotations

import datetime
import errno
import json
import os
import re
import stat
import sys
from typing import Any, Dict, List, Tuple


MAX_SAFE_INTEGER = 9007199254740991


class DuplicateMember(ValueError):
    """Raised when any JSON object repeats a member name."""


class UnsafeInteger(ValueError):
    """Raised when JSON contains an integer outside jq's exact range."""


def unique_object(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateMember
        result[key] = value
    return result


def reject_nonstandard_constant(_: str) -> None:
    raise ValueError


def safe_integer(value: str) -> int:
    parsed = int(value, 10)
    if parsed < 0 or parsed > MAX_SAFE_INTEGER:
        raise UnsafeInteger
    return parsed


def reject_float(_: str) -> None:
    raise UnsafeInteger


def classify_unique_json(payload: bytes) -> int:
    try:
        json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_nonstandard_constant,
            parse_float=reject_float,
            parse_int=safe_integer,
        )
    except DuplicateMember:
        return 1
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return 2
    return 0


def unique_json() -> int:
    return classify_unique_json(sys.stdin.buffer.read())


def split_jsonl(raw: bytes) -> List[bytes]:
    """Split exactly the way the shell's `read -r` loop does.

    An empty input is zero records; a single trailing newline terminates the
    last record rather than introducing an empty one; a record with no trailing
    newline is still a record.
    """
    if raw == b"":
        return []
    if raw.endswith(b"\n"):
        raw = raw[:-1]
    return raw.split(b"\n")


def unique_json_lines() -> int:
    """Classify a whole JSONL stream in one launch, one status code per line.

    Validating an append re-checks every existing line, so the per-line variant
    above cost one interpreter launch per line per pass. Callers batch a whole
    pass through here instead and read the verdicts back positionally.
    """
    verdicts = [classify_unique_json(line) for line in split_jsonl(sys.stdin.buffer.read())]
    sys.stdout.write("".join("%d\n" % verdict for verdict in verdicts))
    return 0


def rfc3339_utc(value: str) -> int:
    match = re.fullmatch(
        r"([0-9]{4})-([0-9]{2})-([0-9]{2})T"
        r"([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]+))?Z",
        value,
    )
    if match is None:
        return 2
    year, month, day, hour, minute, second = (
        int(part, 10) for part in match.groups()[:6]
    )
    try:
        datetime.datetime(
            year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc
        )
    except ValueError:
        return 2
    return 0


def parse_limit(value: str) -> int:
    if re.fullmatch(r"[1-9][0-9]*", value) is None:
        raise ValueError
    limit = int(value, 10)
    if limit > MAX_SAFE_INTEGER:
        raise ValueError
    return limit


def stat_identity(stat_result: os.stat_result) -> Tuple[int, int, int, int, int]:
    return (
        stat_result.st_dev,
        stat_result.st_ino,
        stat_result.st_size,
        stat_result.st_mtime_ns,
        stat_result.st_ctime_ns,
    )


def publish_snapshot(
    destination: str, content: bytes, nofollow: int, cloexec: int
) -> int:
    destination_fd = -1
    try:
        destination_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow | cloexec
        try:
            destination_fd = os.open(destination, destination_flags, 0o600)
        except OSError:
            return 74
        os.fchmod(destination_fd, 0o600)
        created = os.fstat(destination_fd)
        if not stat.S_ISREG(created.st_mode):
            return 74

        written = 0
        while written < len(content):
            count = os.write(destination_fd, content[written:])
            if count <= 0:
                return 74
            written += count
        os.fsync(destination_fd)
        os.close(destination_fd)
        destination_fd = -1
        return 0
    except OSError:
        return 74
    finally:
        if destination_fd >= 0:
            try:
                os.close(destination_fd)
            except OSError:
                pass


def snapshot(source: str, destination: str, limit: int) -> int:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    cloexec = getattr(os, "O_CLOEXEC", None)
    if nofollow is None or cloexec is None:
        return 69

    source_fd = -1
    try:
        try:
            preclassified = os.lstat(source)
        except OSError as error:
            if error.errno in (errno.EACCES, errno.ENOENT, errno.ENOTDIR):
                return 2
            return 74
        if not stat.S_ISREG(preclassified.st_mode):
            return 2

        source_flags = os.O_RDONLY | nofollow | cloexec
        if hasattr(os, "O_NONBLOCK"):
            source_flags |= os.O_NONBLOCK
        try:
            source_fd = os.open(source, source_flags)
        except OSError as error:
            if error.errno == errno.EOPNOTSUPP:
                return 69
            return 74

        before = os.fstat(source_fd)
        if not stat.S_ISREG(before.st_mode):
            return 74
        if stat_identity(preclassified) != stat_identity(before):
            return 74

        chunks = []  # type: List[bytes]
        remaining = limit + 1
        while remaining > 0:
            chunk = os.read(source_fd, min(remaining, 1024 * 1024))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        content = b"".join(chunks)
        if len(content) > limit:
            return 73

        after = os.fstat(source_fd)
        if stat_identity(before) != stat_identity(after):
            return 74

        return publish_snapshot(destination, content, nofollow, cloexec)
    except OSError:
        return 74
    finally:
        if source_fd >= 0:
            try:
                os.close(source_fd)
            except OSError:
                pass


def snapshot_stdin(destination: str, limit: int) -> int:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    cloexec = getattr(os, "O_CLOEXEC", None)
    if nofollow is None or cloexec is None:
        return 69
    try:
        chunks = []  # type: List[bytes]
        remaining = limit + 1
        while remaining > 0:
            chunk = sys.stdin.buffer.read(min(remaining, 1024 * 1024))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        content = b"".join(chunks)
    except OSError:
        return 74
    if len(content) > limit:
        return 73
    return publish_snapshot(destination, content, nofollow, cloexec)


def snapshot_command(argv: List[str]) -> int:
    if len(argv) != 6:
        return 73
    values = {}  # type: Dict[str, str]
    index = 0
    while index < len(argv):
        option = argv[index]
        if option not in ("--source", "--destination", "--limit-bytes"):
            return 73
        if option in values or index + 1 >= len(argv):
            return 73
        values[option] = argv[index + 1]
        index += 2
    if set(values) != {"--source", "--destination", "--limit-bytes"}:
        return 73
    try:
        limit = parse_limit(values["--limit-bytes"])
    except ValueError:
        return 73
    return snapshot(values["--source"], values["--destination"], limit)


def snapshot_stdin_command(argv: List[str]) -> int:
    if len(argv) != 4:
        return 73
    values = {}  # type: Dict[str, str]
    index = 0
    while index < len(argv):
        option = argv[index]
        if option not in ("--destination", "--limit-bytes"):
            return 73
        if option in values or index + 1 >= len(argv):
            return 73
        values[option] = argv[index + 1]
        index += 2
    if set(values) != {"--destination", "--limit-bytes"}:
        return 73
    try:
        limit = parse_limit(values["--limit-bytes"])
    except ValueError:
        return 73
    return snapshot_stdin(values["--destination"], limit)


def main(argv: List[str]) -> int:
    if argv == ["unique-json"]:
        return unique_json()
    if argv == ["unique-json-lines"]:
        return unique_json_lines()
    if len(argv) == 2 and argv[0] == "rfc3339-utc":
        return rfc3339_utc(argv[1])
    if argv[:1] == ["snapshot"]:
        return snapshot_command(argv[1:])
    if argv[:1] == ["snapshot-stdin"]:
        return snapshot_stdin_command(argv[1:])
    print(
        "usage: review-runtime-safe-io.py unique-json | unique-json-lines | "
        "rfc3339-utc VALUE | "
        "snapshot --source SOURCE --destination DEST --limit-bytes LIMIT | "
        "snapshot-stdin --destination DEST --limit-bytes LIMIT",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
