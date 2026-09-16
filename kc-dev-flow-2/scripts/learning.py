#!/usr/bin/env python3
"""Record caller-supplied learning evidence locally; never verify or alter SD state."""

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import tempfile


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def keys(value, expected):
    require(isinstance(value, dict) and set(value) == set(expected.split()),
            "unexpected or missing object fields")


def text(value):
    require(isinstance(value, str) and bool(value.strip()), "expected nonempty string")


def strings(value):
    require(isinstance(value, list), "expected string list")
    for item in value:
        text(item)


def entry(value):
    keys(value, "Applicability Practice Evidence")
    for item in value.values():
        text(item)


def pack(value):
    keys(value, "schema_version workflow task_id variant profile closed merged verdict learning_task closure_revision landed_revision pr evidence learning project_rules")
    require(type(value["schema_version"]) is int and value["schema_version"] == 1,
            "unsupported schema_version")
    for field in ("workflow", "task_id", "variant", "profile", "verdict"):
        text(value[field])
    for field in ("closed", "merged", "learning_task"):
        require(type(value[field]) is bool, f"{field} must be boolean")
    for field in ("closure_revision", "landed_revision", "pr"):
        require(isinstance(value[field], str), f"{field} must be a string")
    strings(value["evidence"])
    strings(value["project_rules"])
    require(isinstance(value["learning"], list), "learning must be a list")
    for item in value["learning"]:
        entry(item)
    return value


def eligibility(value):
    return [name for name, allowed in {
        "variant": value["variant"] == "kc-dev-flow-2",
        "profile": value["profile"] in ("poc", "pilot", "prod"),
        "closed": value["closed"], "merged": value["merged"],
        "verdict": value["verdict"] == "passed", "learning_task": not value["learning_task"],
        "closure_revision": bool(value["closure_revision"].strip()),
        "landed_revision": bool(value["landed_revision"].strip()),
        "pr": bool(value["pr"].strip()), "evidence": bool(value["evidence"]),
    }.items() if not allowed]


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()


def job_key(value):
    return hashlib.sha256(encoded([value["workflow"], value["task_id"]])).hexdigest()


def evaluation(value, evidence):
    keys(value, "schema_version decisions")
    require(type(value["schema_version"]) is int and value["schema_version"] == 1,
            "unsupported evaluation schema_version")
    require(isinstance(value["decisions"], list) and value["decisions"], "decisions must be nonempty")
    proposal = {"add": [], "remove": []}
    for decision in value["decisions"]:
        keys(decision, "action entry reason evidence")
        action = decision["action"]
        require(action in ("add", "remove", "no-change"), "unsupported action")
        text(decision["reason"])
        strings(decision["evidence"])
        require(all(ref in evidence["evidence"] for ref in decision["evidence"]),
                "decision evidence must reference supplied pack evidence")
        if action == "no-change":
            require(decision["entry"] is None, "no-change entry must be null")
            continue
        item = decision["entry"]
        entry(item)
        require(decision["evidence"], "changes require evidence references")
        require(item not in proposal[action], "duplicate decision")
        require((item in evidence["learning"]) == (action == "remove"),
                "remove must match existing learning; add must not duplicate it")
        proposal[action].append(item)
    return proposal if any(proposal.values()) else None


def strict_json(raw):
    def pairs(items):
        result = {}
        for name, value in items:
            require(name not in result, "duplicate JSON field")
            result[name] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(Invalid("nonfinite JSON value")))


def read_json(path):
    return strict_json(Path(path).read_bytes())


def atomic_write(path, data):
    """All record publication is serialized by the job's flock."""
    fd, temporary = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def inspect(directory):
    path = directory / "record.json"
    raw = path.read_bytes() if path.exists() else None
    digest = hashlib.sha256(b"missing" if raw is None else raw).hexdigest()
    record = None
    try:
        record = strict_json(raw) if raw is not None else None
        keys(record, "schema_version state input owner token evaluation proposal recovery")
        require(type(record["schema_version"]) is int and record["schema_version"] == 1, "record schema")
        pack(record["input"])
        require(not eligibility(record["input"]), "record eligibility")
        require(job_key(record["input"]) == directory.name, "record identity")
        text(record["owner"])
        require(isinstance(record["token"], str) and re.fullmatch(r"[0-9a-f]{64}", record["token"]), "record token")
        require(record["state"] in ("pending", "completed"), "record state")
        if record["state"] == "pending":
            require(record["evaluation"] is None and record["proposal"] is None, "pending result")
        else:
            require(evaluation(record["evaluation"], record["input"]) == record["proposal"], "result mismatch")
    except (ValueError, TypeError, KeyError, UnicodeError):
        record = None
    return raw, digest, record


@contextmanager
def locked(directory):
    with (directory / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Invalid("job busy; observe later, do not dispatch another evaluator")
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def view(directory):
    if not directory.is_dir():
        return {"job": directory.name, "state": "missing"}
    _, digest, record = inspect(directory)
    result = {"job": directory.name, "digest": digest, "state": "uncertain"}
    if record:
        result.update({key: value for key, value in record.items() if key != "token"})
        if record["state"] == "pending":
            result["owner_status"] = "unverified; check session before explicit recovery"
    return result


def pending(value, owner, recovery=None):
    text(owner)
    return {"schema_version": 1, "state": "pending", "input": value, "owner": owner,
            "token": secrets.token_hex(32), "evaluation": None, "proposal": None,
            "recovery": recovery}


def operate(args):
    common = subprocess.check_output(
        ["git", "-C", args.repo, "rev-parse", "--path-format=absolute", "--git-common-dir"],
        text=True, stderr=subprocess.PIPE).strip()
    home = Path(common) / "kc-dev-flow-2" / "learning"
    value = pack(read_json(args.input)) if args.command in ("claim", "recover") else None
    if value is not None:
        if reasons := eligibility(value):
            return {"state": "ineligible", "reasons": reasons}
    if args.command in ("claim", "recover"):
        text(args.owner)
    key = job_key(value) if args.command == "claim" else args.job
    require(re.fullmatch(r"[0-9a-f]{64}", key), "invalid job identifier")
    directory = home / key
    if args.command == "read":
        return view(directory)
    created = False
    if args.command == "claim":
        home.mkdir(parents=True, exist_ok=True)
        try:
            directory.mkdir()
            created = True
        except FileExistsError:
            pass
    require(directory.is_dir(), "job missing; claim it explicitly")
    with locked(directory):
        raw, digest, record = inspect(directory)
        if args.command == "claim":
            if not created or raw is not None:
                if record:
                    require(record["input"] == value, "existing task evidence differs; no automatic re-evaluation")
                return view(directory)
            record = pending(value, args.owner)
        elif args.command == "complete":
            # Validate the whole result before changing the pending claim.
            require(record is not None and record["state"] == "pending", "job is not pending")
            require(secrets.compare_digest(record["token"], args.token), "stale or foreign claim token")
            result = read_json(args.result)
            proposal = evaluation(result, record["input"])
            record = {**record, "state": "completed", "evaluation": result, "proposal": proposal}
        elif args.command == "recover":
            require(args.owner_state == "stopped", "verify the owner stopped; running or unknown is not recoverable")
            text(args.reason)
            require(args.expected == digest, "record changed since observation")
            require(record is None or record["state"] != "completed", "completed results are immutable")
            require(job_key(value) == key, "recovery input names another job")
            if record:
                require(record["input"] == value, "recovery cannot change the claimed evidence")
            archive = directory / ("prior-" + digest + ".json")
            prior = raw if raw is not None else b"null\n"
            if archive.exists():
                require(archive.read_bytes() == prior, "recovery archive conflict")
            else:
                atomic_write(archive, prior)
            record = pending(value, args.owner, {"prior_digest": digest, "reason": args.reason,
                                               "owner_state": "stopped (caller attestation)"})
        atomic_write(directory / "record.json", encoded(record))
        output = view(directory)
        if args.command in ("claim", "recover"):
            output["token"] = record["token"]
            output["claimed"] = True
        return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    claim = commands.add_parser("claim")
    claim.add_argument("--input", required=True)
    claim.add_argument("--owner", required=True)
    read = commands.add_parser("read")
    complete = commands.add_parser("complete")
    recover = commands.add_parser("recover")
    for command in (read, complete, recover):
        command.add_argument("--job", required=True)
    complete.add_argument("--token", required=True)
    complete.add_argument("--result", required=True)
    for name in ("expected", "reason", "input", "owner"):
        recover.add_argument("--" + name, required=True)
    recover.add_argument("--owner-state", choices=("running", "unknown", "stopped"), required=True)
    try:
        result = operate(parser.parse_args())
    except (Invalid, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(json.dumps({"state": "error", "error": str(error)}))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
