#!/usr/bin/env python3
"""Boundedly validate and summarize Chrome Trace Event JSON."""

from __future__ import annotations

import collections
import heapq
import json
import math
import os
import stat
import sys
import time
from dataclasses import dataclass, field
from typing import Any

FORMAT_CHROME = "chrome-trace-json"
FORMAT_PLAYWRIGHT = "playwright-trace-zip"
FORMAT_UNKNOWN = "unknown"
TRACE_EVENT_PHASES = frozenset(
    {
        "(",
        ")",
        "=",
        "B",
        "C",
        "D",
        "E",
        "F",
        "I",
        "M",
        "N",
        "O",
        "P",
        "R",
        "S",
        "T",
        "V",
        "X",
        "b",
        "c",
        "e",
        "f",
        "i",
        "n",
        "p",
        "s",
        "t",
        "v",
    }
)


class InvalidJsonError(Exception):
    """The artifact is not valid JSON."""


class WrongFormatError(Exception):
    """The artifact is valid data but not Chrome Trace Event JSON."""


class ResourceLimitError(Exception):
    """The artifact exceeds a configured validation budget."""


def reject_non_finite_constant(value: str) -> None:
    raise InvalidJsonError(f"invalid JSON: non-finite constant {value}")


def parse_finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise InvalidJsonError(f"invalid JSON: numeric value must be finite: {value}")
    return parsed


def positive_limit(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as error:
        raise ResourceLimitError(f"{name.lower()} must be a positive integer") from error
    if value <= 0:
        raise ResourceLimitError(f"{name.lower()} must be a positive integer")
    return value


@dataclass
class Limits:
    max_file_bytes: int = field(
        default_factory=lambda: positive_limit(
            "E2E_CHROME_TRACE_MAX_FILE_BYTES", 512 * 1024 * 1024
        )
    )
    max_events: int = field(
        default_factory=lambda: positive_limit("E2E_CHROME_TRACE_MAX_EVENTS", 2_000_000)
    )
    max_event_bytes: int = field(
        default_factory=lambda: positive_limit(
            "E2E_CHROME_TRACE_MAX_EVENT_BYTES", 1024 * 1024
        )
    )
    timeout_seconds: int = field(
        default_factory=lambda: positive_limit(
            "E2E_CHROME_TRACE_TIMEOUT_SECONDS", 60
        )
    )
    max_identities: int = field(
        default_factory=lambda: positive_limit(
            "E2E_CHROME_TRACE_MAX_IDENTITIES", 100_000
        )
    )
    max_categories: int = field(
        default_factory=lambda: positive_limit(
            "E2E_CHROME_TRACE_MAX_CATEGORIES", 10_000
        )
    )
    max_string_bytes: int = field(
        default_factory=lambda: positive_limit(
            "E2E_CHROME_TRACE_MAX_STRING_BYTES", 4 * 1024
        )
    )
    max_summary_string_bytes: int = field(
        default_factory=lambda: positive_limit(
            "E2E_CHROME_TRACE_MAX_SUMMARY_STRING_BYTES", 1024 * 1024
        )
    )


class JsonStream:
    """Incrementally decode JSON values without retaining the complete trace."""

    def __init__(self, file_path: str, max_value_bytes: int):
        self.handle = open(file_path, encoding="utf-8")
        self.decoder = json.JSONDecoder(
            parse_constant=reject_non_finite_constant,
            parse_float=parse_finite_float,
        )
        self.buffer = ""
        self.position = 0
        self.eof = False
        self.max_value_bytes = max_value_bytes

    def close(self) -> None:
        self.handle.close()

    def compact(self) -> None:
        if self.position:
            self.buffer = self.buffer[self.position :]
            self.position = 0

    def fill(self) -> bool:
        self.compact()
        chunk = self.handle.read(64 * 1024)
        if not chunk:
            self.eof = True
            return False
        self.buffer += chunk
        return True

    def skip_whitespace(self) -> None:
        while True:
            while (
                self.position < len(self.buffer)
                and self.buffer[self.position] in " \t\r\n"
            ):
                self.position += 1
            if self.position < len(self.buffer) or self.eof:
                return
            self.fill()

    def peek(self) -> str:
        self.skip_whitespace()
        while self.position >= len(self.buffer) and not self.eof:
            self.fill()
            self.skip_whitespace()
        return self.buffer[self.position] if self.position < len(self.buffer) else ""

    def expect(self, character: str) -> None:
        actual = self.peek()
        if actual != character:
            raise InvalidJsonError(
                f"invalid JSON: expected {character!r}, found {actual!r}"
            )
        self.position += 1

    def value(self, limit: int | None = None) -> Any:
        budget = limit or self.max_value_bytes
        self.skip_whitespace()
        while True:
            try:
                start = self.position
                value, end = self.decoder.raw_decode(self.buffer, start)
                if len(self.buffer[start:end].encode("utf-8")) > budget:
                    raise ResourceLimitError("max_event_bytes exceeded")
                self.position = end
                return value
            except json.JSONDecodeError as error:
                remaining = self.buffer[self.position :].encode("utf-8")
                if len(remaining) > budget:
                    raise ResourceLimitError("max_event_bytes exceeded") from error
                if self.eof or not self.fill():
                    raise InvalidJsonError(f"invalid JSON: {error.msg}") from error


class TraceSummary:
    def __init__(self, limits: Limits):
        self.limits = limits
        self.event_count = 0
        self.metadata_event_count = 0
        self.duration_event_count = 0
        self.processes: set[int] = set()
        self.threads: set[tuple[int, int]] = set()
        self.categories: collections.Counter[str] = collections.Counter()
        self.longest: list[
            tuple[int | float, int, int, int, dict[str, Any]]
        ] = []
        self.retained_string_bytes = 0

    def string_size(self, value: str) -> int:
        size = len(value.encode("utf-8"))
        if size > self.limits.max_string_bytes:
            raise ResourceLimitError("max_string_bytes exceeded")
        return size

    def reserve_strings(self, added_bytes: int, removed_bytes: int = 0) -> None:
        retained = self.retained_string_bytes - removed_bytes + added_bytes
        if retained > self.limits.max_summary_string_bytes:
            raise ResourceLimitError("max_summary_string_bytes exceeded")
        self.retained_string_bytes = retained

    def add(self, event: Any) -> None:
        if not isinstance(event, dict):
            raise WrongFormatError("traceEvents entries must be JSON objects")
        name = event.get("name")
        phase = event.get("ph")
        if not isinstance(name, str) or not name or not isinstance(phase, str):
            raise WrongFormatError("traceEvents entries require string name and ph")
        if phase not in TRACE_EVENT_PHASES:
            raise WrongFormatError(f"unsupported trace event phase: {phase!r}")
        name_size = self.string_size(name)

        self.event_count += 1
        if self.event_count > self.limits.max_events:
            raise ResourceLimitError("max_events exceeded")
        if phase == "M":
            self.metadata_event_count += 1

        pid = event.get("pid")
        tid = event.get("tid")
        if isinstance(pid, int) and not isinstance(pid, bool):
            self.processes.add(pid)
            if isinstance(tid, int) and not isinstance(tid, bool):
                self.threads.add((pid, tid))
        if (
            len(self.processes) > self.limits.max_identities
            or len(self.threads) > self.limits.max_identities
        ):
            raise ResourceLimitError("max_identities exceeded")

        raw_category = event.get("cat", "(uncategorized)")
        if isinstance(raw_category, str):
            categories = [
                category.strip()
                for category in raw_category.split(",")
                if category.strip()
            ]
        else:
            categories = []
        if not categories:
            categories = ["(uncategorized)"]
        bounded_categories = []
        has_category_overflow = False
        for category in categories:
            if (
                category not in self.categories
                and len(self.categories) >= self.limits.max_categories
            ):
                self.categories["(other)"] += 1
                bounded_categories.append("(other)")
                has_category_overflow = True
            else:
                if category not in self.categories:
                    self.reserve_strings(self.string_size(category))
                self.categories[category] += 1
                bounded_categories.append(category)

        duration = event.get("dur")
        if phase == "X":
            if (
                not isinstance(duration, (int, float))
                or isinstance(duration, bool)
                or (isinstance(duration, float) and not math.isfinite(duration))
                or duration < 0
            ):
                raise WrongFormatError(
                    "complete trace events require a finite non-negative dur"
                )
            self.duration_event_count += 1
            if has_category_overflow:
                event_category = "(other)"
                event_category_size = 0
            elif len(bounded_categories) == 1:
                event_category = bounded_categories[0]
                event_category_size = 0
            else:
                event_category = ",".join(bounded_categories)
                event_category_size = self.string_size(event_category)
            item = {
                "name": name,
                "category": event_category,
                "duration_us": duration,
                "pid": pid,
                "tid": tid,
            }
            ranked = (
                duration,
                self.event_count,
                name_size,
                event_category_size,
                item,
            )
            if len(self.longest) < 20:
                self.reserve_strings(name_size + event_category_size)
                heapq.heappush(self.longest, ranked)
            elif ranked[:2] > self.longest[0][:2]:
                replaced_name_size = self.longest[0][2]
                replaced_category_size = self.longest[0][3]
                self.reserve_strings(
                    name_size + event_category_size,
                    removed_bytes=replaced_name_size + replaced_category_size,
                )
                heapq.heapreplace(self.longest, ranked)

    def result(self) -> dict[str, Any]:
        longest = [
            item
            for _, _, _, _, item in sorted(
                self.longest, key=lambda entry: (entry[0], entry[1]), reverse=True
            )
        ]
        categories = [
            {"name": name, "count": count}
            for name, count in sorted(
                self.categories.items(), key=lambda entry: (-entry[1], entry[0])
            )[:20]
        ]
        return {
            "format": FORMAT_CHROME,
            "trace_event_count": self.event_count,
            "metadata_event_count": self.metadata_event_count,
            "duration_event_count": self.duration_event_count,
            "process_count": len(self.processes),
            "thread_count": len(self.threads),
            "categories": categories,
            "longest_events": longest,
        }


def assert_regular_file(file_path: str) -> int:
    file_stat = os.lstat(file_path)
    if not stat.S_ISREG(file_stat.st_mode):
        raise WrongFormatError("trace artifact must be a regular file")
    if file_stat.st_size <= 0:
        raise InvalidJsonError("invalid JSON: trace artifact is empty")
    return file_stat.st_size


def assert_chrome_file_limit(file_size: int, limits: Limits) -> None:
    if file_size > limits.max_file_bytes:
        raise ResourceLimitError("max_file_bytes exceeded")


def assert_before_deadline(deadline: float) -> None:
    if time.monotonic() > deadline:
        raise ResourceLimitError("timeout_seconds exceeded")


def has_top_level_trace_events(
    file_path: str, max_value_bytes: int, deadline: float
) -> bool:
    stream = JsonStream(file_path, max_value_bytes)
    try:
        assert_before_deadline(deadline)
        stream.expect("{")
        if stream.peek() == "}":
            return False
        while True:
            assert_before_deadline(deadline)
            key = stream.value(64 * 1024)
            assert_before_deadline(deadline)
            if not isinstance(key, str):
                raise InvalidJsonError("invalid JSON: object key must be a string")
            stream.expect(":")
            if key == "traceEvents":
                return True
            stream.value()
            assert_before_deadline(deadline)
            separator = stream.peek()
            if separator == ",":
                stream.position += 1
                continue
            if separator == "}":
                return False
            raise InvalidJsonError("invalid JSON: expected comma or object end")
    finally:
        stream.close()


def detect(file_path: str, max_value_bytes: int, deadline: float) -> str:
    assert_before_deadline(deadline)
    with open(file_path, "rb") as artifact:
        prefix = artifact.read(4)
    if prefix.startswith(b"PK\x03\x04"):
        return FORMAT_PLAYWRIGHT
    try:
        if has_top_level_trace_events(file_path, max_value_bytes, deadline):
            return FORMAT_CHROME
    except (InvalidJsonError, UnicodeDecodeError):
        return FORMAT_UNKNOWN
    return FORMAT_UNKNOWN


def parse_trace(file_path: str, limits: Limits, deadline: float) -> TraceSummary:
    stream = JsonStream(file_path, limits.max_event_bytes)
    summary = TraceSummary(limits)
    found_trace_events = False
    try:
        assert_before_deadline(deadline)
        stream.expect("{")
        if stream.peek() == "}":
            raise WrongFormatError("Chrome trace requires a traceEvents array")
        while True:
            assert_before_deadline(deadline)
            key = stream.value(64 * 1024)
            assert_before_deadline(deadline)
            if not isinstance(key, str):
                raise InvalidJsonError("invalid JSON: object key must be a string")
            stream.expect(":")
            if key == "traceEvents":
                if found_trace_events:
                    raise WrongFormatError("duplicate traceEvents field")
                found_trace_events = True
                stream.expect("[")
                if stream.peek() != "]":
                    while True:
                        assert_before_deadline(deadline)
                        summary.add(stream.value())
                        assert_before_deadline(deadline)
                        separator = stream.peek()
                        if separator == ",":
                            stream.position += 1
                            continue
                        if separator == "]":
                            break
                        raise InvalidJsonError(
                            "invalid JSON: expected comma or traceEvents array end"
                        )
                stream.expect("]")
            else:
                stream.value()
                assert_before_deadline(deadline)
            separator = stream.peek()
            if separator == ",":
                stream.position += 1
                continue
            if separator == "}":
                stream.position += 1
                break
            raise InvalidJsonError("invalid JSON: expected comma or object end")
        assert_before_deadline(deadline)
        if stream.peek():
            raise InvalidJsonError("invalid JSON: trailing content")
        assert_before_deadline(deadline)
    except UnicodeDecodeError as error:
        raise InvalidJsonError("invalid JSON: artifact is not UTF-8") from error
    finally:
        stream.close()
    if not found_trace_events:
        raise WrongFormatError("Chrome trace requires a traceEvents array")
    if summary.event_count == 0:
        raise WrongFormatError("Chrome trace requires at least one traceEvents entry")
    return summary


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] not in {"detect", "validate", "summarize"}:
        print(
            "usage: validate-chrome-trace.py detect|validate|summarize <trace-path>",
            file=sys.stderr,
        )
        return 64
    command, file_path = argv
    try:
        file_size = assert_regular_file(file_path)
        with open(file_path, "rb") as artifact:
            is_playwright = artifact.read(4).startswith(b"PK\x03\x04")
        if is_playwright:
            if command == "detect":
                print(FORMAT_PLAYWRIGHT)
                return 0
            raise WrongFormatError(
                f"expected Chrome trace JSON with traceEvents, detected {FORMAT_PLAYWRIGHT}"
            )

        limits = Limits()
        assert_chrome_file_limit(file_size, limits)
        deadline = time.monotonic() + limits.timeout_seconds
        detected = detect(
            file_path,
            limits.max_event_bytes,
            deadline,
        )
        if command == "detect":
            print(detected)
            return 0
        if detected != FORMAT_CHROME:
            raise WrongFormatError(
                f"expected Chrome trace JSON with traceEvents, detected {detected}"
            )
        summary = parse_trace(file_path, limits, deadline)
        if command == "validate":
            print(FORMAT_CHROME)
        else:
            print(
                json.dumps(
                    summary.result(),
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
            )
        return 0
    except InvalidJsonError as error:
        print(str(error), file=sys.stderr)
        return 2
    except WrongFormatError as error:
        print(str(error), file=sys.stderr)
        return 3
    except ResourceLimitError as error:
        print(str(error), file=sys.stderr)
        return 4
    except (OSError, ValueError) as error:
        print(f"trace validation unavailable: {error}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
