#!/usr/bin/env python3
"""Fail-closed JSON and file-ingestion primitives for review-runtime.sh."""

from __future__ import annotations

import datetime
import errno
import json
import os
import re
import secrets
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


def read_stdin_bounded(limit: int) -> Tuple[int, bytes]:
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
        return 74, b""
    if len(content) > limit:
        return 73, b""
    return 0, content


def open_parent_directory(
    destination: str, expected_identity: str = ""
) -> Tuple[int, int, str]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    cloexec = getattr(os, "O_CLOEXEC", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or cloexec is None or directory is None:
        return 69, -1, ""
    parent = os.path.dirname(destination) or "."
    name = os.path.basename(destination)
    if name in ("", ".", "..") or "/" in name:
        return 2, -1, ""
    try:
        before = os.lstat(parent)
        if not stat.S_ISDIR(before.st_mode):
            return 2, -1, ""
        parent_fd = os.open(parent, os.O_RDONLY | directory | nofollow | cloexec)
        bound = os.fstat(parent_fd)
        if not stat.S_ISDIR(bound.st_mode):
            os.close(parent_fd)
            return 74, -1, ""
        if (before.st_dev, before.st_ino) != (bound.st_dev, bound.st_ino):
            os.close(parent_fd)
            return 74, -1, ""
        actual_identity = "%d:%d" % (bound.st_dev, bound.st_ino)
        if expected_identity and actual_identity != expected_identity:
            os.close(parent_fd)
            return 74, -1, ""
        return 0, parent_fd, name
    except OSError as error:
        if error.errno in (errno.EACCES, errno.ENOENT, errno.ENOTDIR, errno.ELOOP):
            return 2, -1, ""
        return 74, -1, ""


def create_private_temp(parent_fd: int, content: bytes) -> Tuple[int, str]:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    cloexec = getattr(os, "O_CLOEXEC", 0)
    for _ in range(32):
        name = ".review-timing.%s.%s" % (os.getpid(), secrets.token_hex(8))
        try:
            fd = os.open(
                name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow | cloexec,
                0o600,
                dir_fd=parent_fd,
            )
        except FileExistsError:
            continue
        except OSError:
            return 74, ""
        try:
            os.fchmod(fd, 0o600)
            written = 0
            while written < len(content):
                count = os.write(fd, content[written:])
                if count <= 0:
                    return 74, name
                written += count
            os.fsync(fd)
        except OSError:
            return 74, name
        finally:
            try:
                os.close(fd)
            except OSError:
                pass
        return 0, name
    return 74, ""


def read_bound_regular(parent_fd: int, name: str, limit: int) -> Tuple[int, bytes]:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    cloexec = getattr(os, "O_CLOEXEC", 0)
    flags = os.O_RDONLY | nofollow | cloexec
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    fd = -1
    try:
        classified = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if not stat.S_ISREG(classified.st_mode):
            return 74, b""
        fd = os.open(name, flags, dir_fd=parent_fd)
        before = os.fstat(fd)
        if stat_identity(classified) != stat_identity(before):
            return 74, b""
        chunks = []  # type: List[bytes]
        remaining = limit + 1
        while remaining > 0:
            chunk = os.read(fd, min(remaining, 1024 * 1024))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        content = b"".join(chunks)
        if len(content) > limit:
            return 73, b""
        after = os.fstat(fd)
        if stat_identity(before) != stat_identity(after):
            return 74, b""
        return 0, content
    except OSError:
        return 74, b""
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass


def publish_private(destination: str, parent_identity: str, content: bytes) -> int:
    rc, parent_fd, name = open_parent_directory(destination, parent_identity)
    if rc != 0:
        return rc
    temp_name = ""
    published = False
    try:
        rc, temp_name = create_private_temp(parent_fd, content)
        if rc != 0:
            return rc
        try:
            os.link(
                temp_name,
                name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except OSError:
            return 74
        published = True
        os.fsync(parent_fd)
        published = False
        return 0
    except OSError:
        return 74
    finally:
        if published and temp_name:
            try:
                temporary = os.stat(temp_name, dir_fd=parent_fd, follow_symlinks=False)
                destination_stat = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                if (temporary.st_dev, temporary.st_ino) == (
                    destination_stat.st_dev,
                    destination_stat.st_ino,
                ):
                    os.unlink(name, dir_fd=parent_fd)
            except OSError:
                pass
        if temp_name:
            try:
                os.unlink(temp_name, dir_fd=parent_fd)
            except OSError:
                pass
        try:
            os.close(parent_fd)
        except OSError:
            pass


def replace_private(
    destination: str,
    expected: str,
    parent_identity: str,
    content: bytes,
    limit: int,
) -> int:
    expected_rc, expected_content = snapshot_bytes(expected, limit)
    if expected_rc != 0:
        return expected_rc
    rc, parent_fd, name = open_parent_directory(destination, parent_identity)
    if rc != 0:
        return rc
    temp_name = ""
    try:
        rc, current = read_bound_regular(parent_fd, name, limit)
        if rc != 0 or current != expected_content:
            return 74
        rc, temp_name = create_private_temp(parent_fd, content)
        if rc != 0:
            return rc
        rc, current = read_bound_regular(parent_fd, name, limit)
        if rc != 0 or current != expected_content:
            return 74
        os.replace(temp_name, name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        temp_name = ""
        os.fsync(parent_fd)
        return 0
    except OSError:
        return 74
    finally:
        if temp_name:
            try:
                os.unlink(temp_name, dir_fd=parent_fd)
            except OSError:
                pass
        try:
            os.close(parent_fd)
        except OSError:
            pass


def snapshot_bytes(source: str, limit: int) -> Tuple[int, bytes]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    cloexec = getattr(os, "O_CLOEXEC", None)
    if nofollow is None or cloexec is None:
        return 69, b""
    fd = -1
    try:
        classified = os.lstat(source)
        if not stat.S_ISREG(classified.st_mode):
            return 2, b""
        flags = os.O_RDONLY | nofollow | cloexec
        if hasattr(os, "O_NONBLOCK"):
            flags |= os.O_NONBLOCK
        fd = os.open(source, flags)
        before = os.fstat(fd)
        if stat_identity(classified) != stat_identity(before):
            return 74, b""
        chunks = []  # type: List[bytes]
        remaining = limit + 1
        while remaining > 0:
            chunk = os.read(fd, min(remaining, 1024 * 1024))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        content = b"".join(chunks)
        if len(content) > limit:
            return 73, b""
        after = os.fstat(fd)
        if stat_identity(before) != stat_identity(after):
            return 74, b""
        return 0, content
    except OSError:
        return 74, b""
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass


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


def parent_identity_command(argv: List[str]) -> int:
    if len(argv) != 2 or argv[0] != "--destination":
        return 73
    rc, parent_fd, _ = open_parent_directory(argv[1])
    if rc != 0:
        return rc
    try:
        bound = os.fstat(parent_fd)
        print("%d:%d" % (bound.st_dev, bound.st_ino))
        return 0
    except OSError:
        return 74
    finally:
        try:
            os.close(parent_fd)
        except OSError:
            pass


def parse_descriptor(value: str) -> int:
    if re.fullmatch(r"[3-9]|[1-9][0-9]+", value) is None:
        raise ValueError
    return int(value, 10)


def validate_bound_parent(parent_path: str, parent_fd: int) -> int:
    try:
        path_stat = os.lstat(parent_path)
        bound = os.fstat(parent_fd)
        if not stat.S_ISDIR(path_stat.st_mode) or not stat.S_ISDIR(bound.st_mode):
            return 74
        if (path_stat.st_dev, path_stat.st_ino) != (bound.st_dev, bound.st_ino):
            return 74
        return 0
    except OSError:
        return 74


def open_lock_directory(parent_fd: int, lock_name: str) -> Tuple[int, int]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    cloexec = getattr(os, "O_CLOEXEC", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if nofollow is None or cloexec is None or directory is None:
        return 69, -1
    try:
        classified = os.stat(lock_name, dir_fd=parent_fd, follow_symlinks=False)
        if not stat.S_ISDIR(classified.st_mode):
            return 75, -1
        lock_fd = os.open(
            lock_name,
            os.O_RDONLY | directory | nofollow | cloexec,
            dir_fd=parent_fd,
        )
        bound = os.fstat(lock_fd)
        if (classified.st_dev, classified.st_ino) != (bound.st_dev, bound.st_ino):
            os.close(lock_fd)
            return 75, -1
        return 0, lock_fd
    except OSError:
        return 75, -1


def read_lock_owner(lock_fd: int) -> Tuple[int, str]:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    cloexec = getattr(os, "O_CLOEXEC", 0)
    owner_fd = -1
    try:
        if os.listdir(lock_fd) != ["owner.pid"]:
            return 75, ""
        owner_fd = os.open(
            "owner.pid", os.O_RDONLY | nofollow | cloexec, dir_fd=lock_fd
        )
        owner_stat = os.fstat(owner_fd)
        if not stat.S_ISREG(owner_stat.st_mode) or owner_stat.st_size > 32:
            return 75, ""
        payload = os.read(owner_fd, 33)
        if stat_identity(os.fstat(owner_fd)) != stat_identity(owner_stat):
            return 75, ""
        try:
            owner = payload.decode("ascii").strip()
        except UnicodeDecodeError:
            return 75, ""
        if re.fullmatch(r"[1-9][0-9]*", owner) is None:
            return 75, ""
        return 0, owner
    except OSError:
        return 75, ""
    finally:
        if owner_fd >= 0:
            try:
                os.close(owner_fd)
            except OSError:
                pass


def process_is_live(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True


def timing_lock_acquire(
    parent_path: str, parent_fd: int, lock_name: str, owner_pid: str
) -> int:
    if (
        lock_name in ("", ".", "..")
        or "/" in lock_name
        or re.fullmatch(r"[1-9][0-9]*", owner_pid) is None
    ):
        return 75
    if validate_bound_parent(parent_path, parent_fd) != 0:
        return 75
    for attempt in range(2):
        try:
            os.mkdir(lock_name, 0o700, dir_fd=parent_fd)
        except FileExistsError:
            if attempt != 0:
                return 75
            rc, lock_fd = open_lock_directory(parent_fd, lock_name)
            if rc != 0:
                return 75
            try:
                rc, stale_owner = read_lock_owner(lock_fd)
                if rc != 0 or process_is_live(int(stale_owner, 10)):
                    return 75
                os.unlink("owner.pid", dir_fd=lock_fd)
            except OSError:
                return 75
            finally:
                try:
                    os.close(lock_fd)
                except OSError:
                    pass
            try:
                os.rmdir(lock_name, dir_fd=parent_fd)
            except OSError:
                return 75
            continue
        except OSError:
            return 75

        rc, lock_fd = open_lock_directory(parent_fd, lock_name)
        if rc != 0:
            try:
                os.rmdir(lock_name, dir_fd=parent_fd)
            except OSError:
                pass
            return 75
        try:
            os.fchmod(lock_fd, 0o700)
            owner_fd = os.open(
                "owner.pid",
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                0o600,
                dir_fd=lock_fd,
            )
            try:
                os.fchmod(owner_fd, 0o600)
                os.write(owner_fd, (owner_pid + "\n").encode("ascii"))
                os.fsync(owner_fd)
            finally:
                os.close(owner_fd)
            lock_stat = os.fstat(lock_fd)
            os.fsync(lock_fd)
            print("%s:%d:%d" % (owner_pid, lock_stat.st_dev, lock_stat.st_ino))
            return 0
        except OSError:
            try:
                os.unlink("owner.pid", dir_fd=lock_fd)
            except OSError:
                pass
            try:
                os.rmdir(lock_name, dir_fd=parent_fd)
            except OSError:
                pass
            return 75
        finally:
            try:
                os.close(lock_fd)
            except OSError:
                pass
    return 75


def timing_lock_release(parent_fd: int, lock_name: str, token: str) -> int:
    match = re.fullmatch(r"([1-9][0-9]*):([0-9]+):([0-9]+)", token)
    if match is None or lock_name in ("", ".", "..") or "/" in lock_name:
        return 74
    expected_pid, expected_dev, expected_ino = match.groups()
    rc, lock_fd = open_lock_directory(parent_fd, lock_name)
    if rc != 0:
        return 74
    try:
        lock_stat = os.fstat(lock_fd)
        if (lock_stat.st_dev, lock_stat.st_ino) != (
            int(expected_dev, 10),
            int(expected_ino, 10),
        ):
            return 74
        rc, actual_pid = read_lock_owner(lock_fd)
        if rc != 0 or actual_pid != expected_pid:
            return 74
        os.unlink("owner.pid", dir_fd=lock_fd)
    except OSError:
        return 74
    finally:
        try:
            os.close(lock_fd)
        except OSError:
            pass
    try:
        os.rmdir(lock_name, dir_fd=parent_fd)
        os.fsync(parent_fd)
        return 0
    except OSError:
        return 74


def timing_lock_command(argv: List[str], release: bool) -> int:
    required = {"--parent-fd", "--lock-name"}
    if release:
        required.add("--token")
    else:
        required.update({"--parent-path", "--owner-pid"})
    if len(argv) != len(required) * 2:
        return 73
    values = {}  # type: Dict[str, str]
    for index in range(0, len(argv), 2):
        option = argv[index]
        if option not in required or option in values:
            return 73
        values[option] = argv[index + 1]
    if set(values) != required:
        return 73
    try:
        parent_fd = parse_descriptor(values["--parent-fd"])
    except ValueError:
        return 73
    if release:
        return timing_lock_release(parent_fd, values["--lock-name"], values["--token"])
    return timing_lock_acquire(
        values["--parent-path"],
        parent_fd,
        values["--lock-name"],
        values["--owner-pid"],
    )


def private_json_command(argv: List[str], replace: bool) -> int:
    expected_options = (
        {"--destination", "--expected", "--parent-identity"}
        if replace
        else {"--destination", "--parent-identity"}
    )
    if len(argv) != len(expected_options) * 2:
        return 73
    values = {}  # type: Dict[str, str]
    index = 0
    while index < len(argv):
        option = argv[index]
        if option not in expected_options or option in values or index + 1 >= len(argv):
            return 73
        values[option] = argv[index + 1]
        index += 2
    if set(values) != expected_options:
        return 73
    rc, content = read_stdin_bounded(1048576)
    if rc != 0:
        return rc
    if replace:
        return replace_private(
            values["--destination"],
            values["--expected"],
            values["--parent-identity"],
            content,
            1048576,
        )
    return publish_private(
        values["--destination"], values["--parent-identity"], content
    )


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
    if argv[:1] == ["private-parent-identity"]:
        return parent_identity_command(argv[1:])
    if argv[:1] == ["publish-private-json"]:
        return private_json_command(argv[1:], False)
    if argv[:1] == ["replace-private-json"]:
        return private_json_command(argv[1:], True)
    if argv[:1] == ["timing-lock-acquire"]:
        return timing_lock_command(argv[1:], False)
    if argv[:1] == ["timing-lock-release"]:
        return timing_lock_command(argv[1:], True)
    print(
        "usage: review-runtime-safe-io.py unique-json | unique-json-lines | "
        "rfc3339-utc VALUE | "
        "snapshot --source SOURCE --destination DEST --limit-bytes LIMIT | "
        "snapshot-stdin --destination DEST --limit-bytes LIMIT | "
        "private-parent-identity --destination DEST | "
        "publish-private-json --destination DEST --parent-identity DEV:INO | "
        "replace-private-json --destination DEST --expected SNAPSHOT "
        "--parent-identity DEV:INO | timing-lock-acquire ... | "
        "timing-lock-release ...",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
