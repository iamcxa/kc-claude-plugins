#!/usr/bin/env python3
"""Create and validate the non-authoritative kc-dev-flow PR-review evidence index."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

SCHEMA = "kc-dev-flow-pr-review-handoff/v1"
VALIDATION_SCHEMA = "kc-dev-flow-pr-review-handoff-validation/v1"
SHA = re.compile(r"^[0-9a-f]{40}$")
PROFILE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")
FORBIDDEN_KEYS = {"authority", "authorization", "credential", "credentials", "cookie", "cookies", "browser_profile", "raw_log", "raw_logs", "prompt", "prompts"}
TOP_LEVEL_KEYS = {
    "schema", "work_item_ref", "selected_profile", "base_sha", "candidate_sha", "pr",
    "accepted_outcome", "acceptance_criteria", "falsifiers", "evidence_refs", "changed_files",
    "scope_exclusions", "residuals",
}
PR_KEYS = {"repository", "number", "head_sha"}


def fail(message: str) -> None:
    raise ValueError(message)


def text(value: Any, name: str, *, limit: int = 4096) -> str:
    if not isinstance(value, str) or not value or len(value) > limit or "\x00" in value or "\n" in value or "\r" in value:
        fail(f"invalid {name}")
    return value


def text_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or len(value) > 200:
        fail(f"invalid {name}")
    return [text(item, name) for item in value]


def sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        fail(f"invalid {name}")
    return value


def validate_handoff(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict) or set(document) != TOP_LEVEL_KEYS:
        fail("invalid handoff shape")
    if document.get("schema") != SCHEMA:
        fail("invalid handoff schema")
    if any(key in FORBIDDEN_KEYS for key in document):
        fail("invalid handoff forbidden field")
    work_item_ref = text(document["work_item_ref"], "work_item_ref", limit=256)
    selected_profile = text(document["selected_profile"], "selected_profile", limit=64)
    if not PROFILE.fullmatch(selected_profile):
        fail("invalid selected_profile")
    base_sha = sha(document["base_sha"], "base_sha")
    candidate_sha = sha(document["candidate_sha"], "candidate_sha")
    pr = document["pr"]
    if not isinstance(pr, dict) or set(pr) != PR_KEYS:
        fail("invalid pr")
    repository = text(pr["repository"], "pr.repository", limit=256)
    if not REPOSITORY.fullmatch(repository):
        fail("invalid pr.repository")
    number = pr["number"]
    if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
        fail("invalid pr.number")
    head_sha = sha(pr["head_sha"], "pr.head_sha")
    if candidate_sha != head_sha:
        fail("invalid candidate/head binding")
    return {
        "schema": SCHEMA,
        "work_item_ref": work_item_ref,
        "selected_profile": selected_profile,
        "base_sha": base_sha,
        "candidate_sha": candidate_sha,
        "pr": {"repository": repository, "number": number, "head_sha": head_sha},
        "accepted_outcome": text(document["accepted_outcome"], "accepted_outcome"),
        "acceptance_criteria": text_list(document["acceptance_criteria"], "acceptance_criteria"),
        "falsifiers": text_list(document["falsifiers"], "falsifiers"),
        "evidence_refs": text_list(document["evidence_refs"], "evidence_refs"),
        "changed_files": text_list(document["changed_files"], "changed_files"),
        "scope_exclusions": text_list(document["scope_exclusions"], "scope_exclusions"),
        "residuals": text_list(document["residuals"], "residuals"),
    }


def write_private_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def create(args: argparse.Namespace) -> int:
    document = validate_handoff({
        "schema": SCHEMA,
        "work_item_ref": args.work_item_ref,
        "selected_profile": args.profile,
        "base_sha": args.base_sha,
        "candidate_sha": args.candidate_sha,
        "pr": {"repository": args.repo, "number": args.pr, "head_sha": args.head_sha},
        "accepted_outcome": args.accepted_outcome,
        "acceptance_criteria": args.acceptance_criterion,
        "falsifiers": args.falsifier,
        "evidence_refs": args.evidence_ref,
        "changed_files": args.changed_file,
        "scope_exclusions": args.scope_exclusion,
        "residuals": args.residual,
    })
    write_private_json(Path(args.output), document)
    return 0


def consume(args: argparse.Namespace) -> int:
    try:
        raw = Path(args.handoff).read_text(encoding="utf-8")
        document = validate_handoff(json.loads(raw))
        expected_base_sha = sha(args.expected_base_sha, "expected_base_sha")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"invalid handoff: {error}", file=sys.stderr)
        return 3
    if (document["pr"]["repository"] != args.repo or document["pr"]["number"] != args.pr
            or document["pr"]["head_sha"] != args.head_sha or document["candidate_sha"] != args.candidate_sha
            or document["base_sha"] != expected_base_sha):
        print("identity mismatch: handoff is not evidence for this exact candidate", file=sys.stderr)
        return 3
    context = {key: document[key] for key in (
        "work_item_ref", "selected_profile", "base_sha", "candidate_sha", "pr", "accepted_outcome",
        "acceptance_criteria", "falsifiers", "evidence_refs", "changed_files", "scope_exclusions", "residuals",
    )}
    print(json.dumps({"schema": VALIDATION_SCHEMA, "evidence_valid": True, "review_context": context}, sort_keys=True, separators=(",", ":")))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    create_parser = commands.add_parser("create")
    create_parser.add_argument("--output", required=True)
    create_parser.add_argument("--work-item-ref", required=True)
    create_parser.add_argument("--profile", required=True)
    create_parser.add_argument("--base-sha", required=True)
    create_parser.add_argument("--candidate-sha", required=True)
    create_parser.add_argument("--repo", required=True)
    create_parser.add_argument("--pr", required=True, type=int)
    create_parser.add_argument("--head-sha", required=True)
    create_parser.add_argument("--accepted-outcome", required=True)
    for option, destination in (("--acceptance-criterion", "acceptance_criterion"), ("--falsifier", "falsifier"), ("--evidence-ref", "evidence_ref"), ("--changed-file", "changed_file"), ("--scope-exclusion", "scope_exclusion"), ("--residual", "residual")):
        create_parser.add_argument(option, dest=destination, action="append", default=[])
    validate_parser = commands.add_parser("validate")
    validate_parser.add_argument("--handoff", required=True)
    validate_parser.add_argument("--repo", required=True)
    validate_parser.add_argument("--pr", required=True, type=int)
    validate_parser.add_argument("--head-sha", required=True)
    validate_parser.add_argument("--candidate-sha", required=True)
    validate_parser.add_argument("--expected-base-sha", required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        return create(args) if args.command == "create" else consume(args)
    except ValueError as error:
        print(f"invalid handoff: {error}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
