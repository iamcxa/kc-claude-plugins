#!/usr/bin/env python3
"""Boundedly validate and summarize Chrome Trace Event JSON."""

from __future__ import annotations

import collections
import heapq
import json
import os
import re
import stat
import sys
import time
from dataclasses import dataclass, field
from typing import Any

FORMAT_CHROME = "chrome-trace-json"
FORMAT_PLAYWRIGHT = "playwright-trace-zip"
FORMAT_UNKNOWN = "unknown"


class InvalidJsonError(Exception):
    """The artifact is not valid JSON."""


class WrongFormatError(Exception):
    """The artifact is valid data but not Chrome Trace Event JSON."""


class ResourceLimitError(Exception):
    """The artifact exceeds a configured validation budget."""


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


class JsonStream:
    """Incrementally decode JSON values without retaining the complete trace."""

    def __init__(self, file_path: str, max_value_bytes: int):
        self.handle = open(file_path, encoding="utf-8")
        self.decoder = json.JSONDecoder()
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
            while self.position < len(self.buffer) and self.buffer[
                self.position
            ].isspace():
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
                value, end = self.decoder.raw_decode(self.buffer, self.position)
                self.position = end
                return value
            except json.JSONDecodeError as error:
                remaining = len(self.buffer) - self.position
                if remaining > budget:
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
        self.longest: list[tuple[float, int, dict[str, Any]]] = []

    def add(self, event: Any) -> None:
        if not isinstance(event, dict):
            raise WrongFormatError("traceEvents entries must be JSON objects")
        name = event.get("name")
        phase = event.get("ph")
        if not isinstance(name, str) or not name or not isinstance(phase, str) or not phase:
            raise WrongFormatError("traceEvents entries require string name and ph")

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

        category = event.get("cat", "(uncategorized)")
        if not isinstance(category, str):
            category = "(uncategorized)"
        if category in self.categories or len(self.categories) < self.limits.max_categories:
            self.categories[category] += 1
        else:
            self.categories["(other)"] += 1

        duration = event.get("dur")
        if (
            phase == "X"
            and isinstance(duration, (int, float))
            and not isinstance(duration, bool)
            and duration >= 0
        ):
            self.duration_event_count += 1
            item = {
                "name": name,
                "category": category,
                "duration_us": duration,
                "pid": pid,
                "tid": tid,
            }
            ranked = (float(duration), self.event_count, item)
            if len(self.longest) < 20:
                heapq.heappush(self.longest, ranked)
            elif ranked[:2] > self.longest[0][:2]:
                heapq.heapreplace(self.longest, ranked)

    def result(self) -> dict[str, Any]:
        longest = [
            item
            for _, _, item in sorted(
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


def assert_regular_file(file_path: str, limits: Limits) -> None:
    file_stat = os.lstat(file_path)
    if not stat.S_ISREG(file_stat.st_mode):
        raise WrongFormatError("trace artifact must be a regular file")
    if file_stat.st_size <= 0:
        raise InvalidJsonError("invalid JSON: trace artifact is empty")
    if file_stat.st_size > limits.max_file_bytes:
        raise ResourceLimitError("max_file_bytes exceeded")


def detect(file_path: str) -> str:
    with open(file_path, "rb") as artifact:
        prefix = artifact.read(64 * 1024)
    if prefix.startswith(b"PK\x03\x04"):
        return FORMAT_PLAYWRIGHT
    try:
        text = prefix.decode("utf-8")
    except UnicodeDecodeError:
        return FORMAT_UNKNOWN
    if re.match(r'^\s*\{\s*"traceEvents"\s*:', text):
        return FORMAT_CHROME
    return FORMAT_UNKNOWN


def parse_trace(file_path: str, limits: Limits) -> TraceSummary:
    started = time.monotonic()
    stream = JsonStream(file_path, limits.max_event_bytes)
    summary = TraceSummary(limits)
    found_trace_events = False
    try:
        stream.expect("{")
        if stream.peek() == "}":
            raise WrongFormatError("Chrome trace requires a traceEvents array")
        while True:
            key = stream.value(64 * 1024)
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
                        if time.monotonic() - started > limits.timeout_seconds:
                            raise ResourceLimitError("timeout_seconds exceeded")
                        summary.add(stream.value())
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
            separator = stream.peek()
            if separator == ",":
                stream.position += 1
                continue
            if separator == "}":
                stream.position += 1
                break
            raise InvalidJsonError("invalid JSON: expected comma or object end")
        if stream.peek():
            raise InvalidJsonError("invalid JSON: trailing content")
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
        limits = Limits()
        assert_regular_file(file_path, limits)
        detected = detect(file_path)
        if command == "detect":
            print(detected)
            return 0
        if detected != FORMAT_CHROME:
            raise WrongFormatError(
                f"expected Chrome trace JSON with traceEvents, detected {detected}"
            )
        summary = parse_trace(file_path, limits)
        if command == "validate":
            print(FORMAT_CHROME)
        else:
            print(json.dumps(summary.result(), separators=(",", ":"), sort_keys=True))
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
