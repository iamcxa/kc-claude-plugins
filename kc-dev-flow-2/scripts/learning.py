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


class Blocked(Invalid):
    """A new claim was refused because an in-flight sibling job holds the store."""

    def __init__(self, message, blocking):
        super().__init__(message)
        self.blocking = blocking


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


def sha(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value)


def delivery_plan(value, key, result_digest):
    keys(value, "schema_version result_digest repository branch marker base_branch base_commit candidate_commit source_learning_blob candidate_learning_blob worktree title body")
    require(type(value["schema_version"]) is int and value["schema_version"] == 1, "plan schema")
    require(value["result_digest"] == result_digest, "plan does not bind current completed result")
    require(isinstance(value["repository"], str) and re.fullmatch(r"[a-z0-9][a-z0-9_.-]*/[a-z0-9][a-z0-9_.-]*", value["repository"]), "repository must be lowercase owner/repo")
    require(value["branch"] == "learning/" + key, "branch must derive from job")
    require(value["marker"] == "<!-- kc-dev-flow-2 learning " + key + " -->", "marker must derive from job")
    for name in ("base_branch", "worktree", "title", "body"):
        text(value[name])
    require(Path(value["worktree"]).is_absolute(), "worktree must be absolute")
    require(subprocess.run(["git", "check-ref-format", "--branch", value["base_branch"]],
                           cwd="/", capture_output=True).returncode == 0, "invalid base branch")
    for name in ("base_commit", "candidate_commit", "candidate_learning_blob"):
        require(sha(value[name]), "invalid " + name)
    require(value["source_learning_blob"] == "absent" or sha(value["source_learning_blob"]), "invalid source learning blob")
    require(value["body"].count(value["marker"]) == 1, "body must contain the job marker once")
    return value


def observation(value, plan):
    keys(value, "state repository branch candidate_commit marker pr merge_commit draft evidence")
    require(value["state"] in ("open", "merged", "closed", "absent", "unknown"), "observation state")
    for name in ("repository", "branch", "candidate_commit", "marker"):
        require(value[name] == plan[name], "observation mismatch: " + name)
    strings(value["evidence"])
    require(value["evidence"], "provider observation needs evidence")
    ref = value["pr"]
    require(ref is None or (isinstance(ref, str) and re.fullmatch(re.escape(plan["repository"]) + r"#[1-9][0-9]*", ref)), "invalid repository-qualified PR")
    if value["state"] in ("open", "merged", "closed"):
        require(ref is not None and type(value["draft"]) is bool, "observed PR needs identity and draft state")
    else:
        require(value["draft"] is None, "non-PR observation has no draft state")
        if value["state"] == "absent":
            require(ref is None, "absent lookup cannot name a PR")
    require((sha(value["merge_commit"]) if value["state"] == "merged" else value["merge_commit"] is None), "merge commit does not match observed state")
    return value


def inspect_delivery(directory, result_digest):
    path = directory / "delivery.json"
    raw = path.read_bytes() if path.exists() else None
    digest = hashlib.sha256(b"missing" if raw is None else raw).hexdigest()
    record = None
    if raw is not None:
        try:
            record = strict_json(raw)
            keys(record, "schema_version state owner token plan observation recovery")
            require(type(record["schema_version"]) is int and record["schema_version"] == 1, "delivery schema")
            delivery_plan(record["plan"], directory.name, result_digest)
            text(record["owner"])
            require(isinstance(record["token"], str) and re.fullmatch(r"[0-9a-f]{64}", record["token"]), "delivery token")
            require(record["state"] in ("uncertain", "open", "merged", "closed"), "delivery state")
            if record["observation"] is not None:
                observed = observation(record["observation"], record["plan"])
                expected = observed["state"] if observed["state"] in ("open", "merged", "closed") else "uncertain"
                require(record["state"] == expected, "delivery state disagrees with observation")
            else:
                require(record["state"] == "uncertain", "missing delivery observation")
        except (ValueError, TypeError, KeyError, UnicodeError):
            record = None
    return raw, digest, record


def release_record(value):
    keys(value, "schema_version owner reason result_digest delivery_digest authority")
    require(type(value["schema_version"]) is int and value["schema_version"] == 1, "release schema_version")
    for field in ("owner", "reason", "authority"):
        text(value[field])
    for field in ("result_digest", "delivery_digest"):
        require(isinstance(value[field], str) and re.fullmatch(r"[0-9a-f]{64}", value[field]), f"release {field}")
    return value


def inspect_release(directory):
    path = directory / "release.json"
    raw = path.read_bytes() if path.exists() else None
    digest = hashlib.sha256(b"missing" if raw is None else raw).hexdigest()
    record = None
    if raw is not None:
        try:
            record = release_record(strict_json(raw))
        except (ValueError, TypeError, KeyError, UnicodeError):
            record = None
    return raw, digest, record


def release_valid(release, result_digest, delivery_digest):
    return release is not None and release["result_digest"] == result_digest and release["delivery_digest"] == delivery_digest


def sibling_status(path):
    """Blocking classification for one sibling job directory against the hold predicate table."""
    _, result_digest, record = inspect(path)
    if record is None:
        return True, {"job": path.name, "record": "uncertain", "delivery": None, "released": False}
    if record["state"] == "pending":
        return True, {"job": path.name, "record": "pending", "delivery": None, "released": False}
    if record["proposal"] is None:
        return False, None
    delivery_raw, delivery_digest, delivery = inspect_delivery(path, result_digest)
    release_raw, _, release = inspect_release(path)
    released = release_raw is not None
    valid_release = release_valid(release, result_digest, delivery_digest)
    if delivery is not None:
        if delivery["state"] == "open":
            return True, {"job": path.name, "record": "completed", "delivery": "open", "released": released}
        if delivery["state"] in ("merged", "closed"):
            return False, None
        observed_state = delivery["observation"]["state"] if delivery["observation"] else None
        if observed_state == "absent" and valid_release:
            return False, None
        return True, {"job": path.name, "record": "completed", "delivery": "uncertain", "released": released}
    delivery_state = "missing" if delivery_raw is None else "uncertain"
    if delivery_state == "missing" and valid_release:
        return False, None
    return True, {"job": path.name, "record": "completed", "delivery": delivery_state, "released": released}


def blocking_siblings(home, key):
    return [info for path in sorted(home.glob("*"))
            if path.is_dir() and path.name != key and re.fullmatch(r"[0-9a-f]{64}", path.name)
            for blocks, info in [sibling_status(path)] if blocks]


def notice(directory):
    result = view(directory)
    if result["state"] == "missing":
        return result
    raw, digest, delivery = inspect_delivery(directory, result["digest"])
    shown = {"state": "missing" if raw is None else "uncertain", "digest": digest}
    if delivery:
        shown.update({k: v for k, v in delivery.items() if k != "token"})
    result["delivery"] = shown
    release_raw, release_digest, release = inspect_release(directory)
    digest_parts = [result["digest"], digest]
    if release_raw is not None:
        release_shown = {"state": "uncertain" if release is None else "released", "digest": release_digest}
        if release is not None:
            release_shown.update(release)
        result["release"] = release_shown
        digest_parts.append(release_digest)
    result["notice_digest"] = hashlib.sha256(encoded(digest_parts)).hexdigest()
    try:
        acknowledged = read_json(directory / "acknowledgement.json")
        keys(acknowledged, "digest")
        result["unread"] = acknowledged["digest"] != result["notice_digest"]
    except (OSError, ValueError, TypeError):
        result["unread"] = True
    return result


def delivery_operation(args, directory):
    require(directory.is_dir(), "job missing")
    with locked(directory):
        _, result_digest, result = inspect(directory)
        if args.command == "ack":
            current = notice(directory)
            require(args.expected == current["notice_digest"], "notice changed since presentation")
            atomic_write(directory / "acknowledgement.json", encoded({"digest": args.expected}))
            return {"job": directory.name, "acknowledged": args.expected}
        require(result is not None and result["state"] == "completed" and result["proposal"] is not None,
                "delivery requires a completed result with changes")
        raw, digest, record = inspect_delivery(directory, result_digest)
        if args.command == "delivery-claim":
            release_raw, _, _ = inspect_release(directory)
            require(release_raw is None, "job is released; released jobs gain no delivery authority")
            plan = delivery_plan(read_json(args.plan), directory.name, result_digest)
            text(args.owner)
            if raw is not None:
                if record:
                    require(record["plan"] == plan, "existing delivery plan differs")
                return notice(directory)
            record = {"schema_version": 1, "state": "uncertain", "owner": args.owner,
                      "token": secrets.token_hex(32), "plan": plan, "observation": None, "recovery": None}
        elif args.command == "delivery-record":
            require(record is not None, "delivery missing or uncertain; reconcile explicitly")
            require(secrets.compare_digest(record["token"], args.token), "stale or foreign delivery token")
            observed = observation(read_json(args.observation), record["plan"])
            require(observed["state"] != "absent", "absence requires explicit recovery")
            previous = record["observation"]
            if previous and previous["pr"]:
                require(observed["pr"] == previous["pr"], "cannot replace or forget observed PR")
            require(record["state"] != "merged" or observed["state"] == "merged", "merged delivery cannot regress")
            if previous and previous["state"] == "merged":
                require(observed["merge_commit"] == previous["merge_commit"], "merged identity changed")
            record = {**record, "state": observed["state"] if observed["state"] != "unknown" else "uncertain",
                      "observation": observed}
        else:
            require(args.owner_state == "stopped", "verify delivery owner stopped before recovery")
            require(args.expected == digest, "delivery changed since observation")
            text(args.reason)
            text(args.owner)
            plan = delivery_plan(read_json(args.plan), directory.name, result_digest)
            observed = observation(read_json(args.observation), plan)
            require(observed["state"] != "unknown", "unknown provider result cannot authorize recovery")
            if observed["state"] == "absent":
                release_raw, _, _ = inspect_release(directory)
                require(release_raw is None, "job is released; absent reconciliation refused")
            if record:
                require(record["plan"] == plan, "recovery cannot change reviewed plan")
                previous = record["observation"]
                if previous and previous["pr"]:
                    require(observed["pr"] == previous["pr"], "cannot replace or forget observed PR")
                require(record["state"] != "merged" or observed["state"] == "merged", "merged delivery cannot regress")
                if previous and previous["state"] == "merged":
                    require(observed["merge_commit"] == previous["merge_commit"], "merged identity changed")
            archive = directory / ("prior-delivery-" + digest + ".json")
            prior = raw if raw is not None else b"null\n"
            if archive.exists():
                require(archive.read_bytes() == prior, "delivery recovery archive conflict")
            else:
                atomic_write(archive, prior)
            record = {"schema_version": 1, "state": observed["state"] if observed["state"] != "absent" else "uncertain",
                      "owner": args.owner, "token": secrets.token_hex(32), "plan": plan, "observation": observed,
                      "recovery": {"prior_digest": digest, "reason": args.reason, "owner_state": "stopped (caller attestation)"}}
        atomic_write(directory / "delivery.json", encoded(record))
        output = notice(directory)
        if args.command in ("delivery-claim", "delivery-recover"):
            output["delivery_token"] = record["token"]
            output["delivery_claimed"] = args.command == "delivery-claim" or observed["state"] == "absent"
        return output


def release_operation(args, directory):
    require(directory.is_dir(), "job missing")
    with locked(directory):
        text(args.owner)
        text(args.reason)
        _, result_digest, record = inspect(directory)
        require(record is not None and record["state"] == "completed" and record["proposal"] is not None,
                "release requires a completed result with changes")
        delivery_raw, delivery_digest, delivery = inspect_delivery(directory, result_digest)
        release_raw, _, _ = inspect_release(directory)
        if release_raw is not None:
            return notice(directory)
        require(args.expected == notice(directory)["notice_digest"], "notice changed since presentation")
        if delivery is not None:
            require(delivery["state"] not in ("open", "merged", "closed"),
                    "delivery is open, merged or closed; release refused")
            observed_state = delivery["observation"]["state"] if delivery["observation"] else None
            require(observed_state == "absent",
                    "delivery uncertain and not reconciled to absent; use delivery-recover first")
        else:
            require(delivery_raw is None, "delivery record is torn; reconcile before release")
        payload = {"schema_version": 1, "owner": args.owner, "reason": args.reason,
                   "result_digest": result_digest, "delivery_digest": delivery_digest,
                   "authority": "caller attestation"}
        atomic_write(directory / "release.json", encoded(payload))
        return notice(directory)


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
    if args.command == "notices":
        return {"notices": [item for path in sorted(home.glob("*"))
                            if path.is_dir() and re.fullmatch(r"[0-9a-f]{64}", path.name)
                            for item in [notice(path)] if args.all or item.get("unread")]}
    if args.command.startswith("delivery-") or args.command == "ack":
        require(re.fullmatch(r"[0-9a-f]{64}", args.job), "invalid job identifier")
        return delivery_operation(args, home / args.job)
    if args.command == "release":
        require(re.fullmatch(r"[0-9a-f]{64}", args.job), "invalid job identifier")
        return release_operation(args, home / args.job)
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
        if not directory.is_dir():
            # Sibling of home, not inside it: test_linked_worktree_multiprocess_claim_race
            # counts raw home.iterdir() results, which a lock file inside home would perturb;
            # notices already filters to 64-hex names regardless.
            with (home.parent / "learning.lock").open("a") as store:
                fcntl.flock(store, fcntl.LOCK_EX)
                try:
                    if not directory.is_dir():
                        if blocking := blocking_siblings(home, key):
                            raise Blocked("learning job in flight; settle or release the blocking job first",
                                          blocking)
                        directory.mkdir()
                        created = True
                finally:
                    fcntl.flock(store, fcntl.LOCK_UN)
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
    notices = commands.add_parser("notices")
    notices.add_argument("--all", action="store_true", help="include acknowledged jobs for explicit inspection/recovery")
    ack = commands.add_parser("ack")
    ack.add_argument("--job", required=True)
    ack.add_argument("--expected", required=True)
    deliver = commands.add_parser("delivery-claim")
    observe = commands.add_parser("delivery-record")
    resume = commands.add_parser("delivery-recover")
    for command in (deliver, observe, resume):
        command.add_argument("--job", required=True)
    for command in (deliver, resume):
        command.add_argument("--plan", required=True)
        command.add_argument("--owner", required=True)
    for command in (observe, resume):
        command.add_argument("--observation", required=True)
    observe.add_argument("--token", required=True)
    resume.add_argument("--expected", required=True)
    resume.add_argument("--owner-state", choices=("running", "unknown", "stopped"), required=True)
    resume.add_argument("--reason", required=True)
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
    release = commands.add_parser("release")
    for name in ("job", "expected", "owner", "reason"):
        release.add_argument("--" + name, required=True)
    try:
        result = operate(parser.parse_args())
    except (Invalid, OSError, ValueError, subprocess.CalledProcessError) as error:
        payload = {"state": "error", "error": str(error)}
        if isinstance(error, Blocked):
            payload["blocking"] = error.blocking
        print(json.dumps(payload, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
