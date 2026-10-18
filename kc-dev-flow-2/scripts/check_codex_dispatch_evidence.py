#!/usr/bin/env python3
"""Reconcile a local candidate, protected baseline and FO's real pilot host evidence.

This reads machine-local raw host logs; it neither dispatches nor authenticates a
provider. Missing results or opaque native messages hold; requested payloads and
child acknowledgements cannot substitute for exact host request/result evidence.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from codex_dispatch import convert, resolve


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def records(path):
    with Path(path).open() as source:
        for line in source:
            yield json.loads(line)


def event_time(value, label):
    try:
        require(isinstance(value, str), "missing time")
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(moment.utcoffset() is not None, "missing timezone")
        return moment
    except ValueError as error:
        raise ValueError(f"{label} needs an unambiguous timestamp with timezone") from error


def native_call(ledger_path, name, expected, expected_handle=None):
    ledger = read(ledger_path)
    calls = [r["payload"] for r in ledger["calls"] if r["payload"].get("name") == name]
    require(len(calls) == 1, f"expected one {name} in {ledger_path}")
    call = calls[0]
    raw_records = [r for r in records(ledger["source_session"])
                   if r.get("type") == "response_item" and r["payload"].get("call_id") == call["call_id"]]
    raw = [r["payload"] for r in raw_records]
    requests = [r for r in raw if r.get("type") == "function_call"]
    require(requests == [call], f"native call absent/altered or ambiguous in raw host log: {name}")
    require(call.get("namespace") == "collaboration", f"unsupported native namespace: {name}")
    results = [r for r in raw if r.get("type") == "function_call_output"]
    require(len(results) == 1 and raw.index(call) < raw.index(results[0]), f"native {name} requires one raw result after its call_id")
    result = results[0]
    require(set(result).issubset({"type", "call_id", "id", "output", "internal_chat_message_metadata_passthrough"}), f"native {name} error or unsupported result fields")
    returned = None
    if name == "spawn_agent":
        try:
            output = json.loads(result["output"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("native spawn_agent result is missing or unreadable") from error
        require(isinstance(output, dict) and set(output) == {"task_name"}, "native spawn_agent result is not a successful handle")
        returned = output["task_name"]
        require(isinstance(returned, str) and returned and returned == expected_handle, "native spawn_agent returned handle mismatch")
    else:
        require(name == "followup_task" and result.get("output") == "", "native followup_task result is not the successful empty host output")
    arguments = json.loads(call["arguments"])
    require(isinstance(arguments, dict), f"native {name} arguments must be an object")
    message = arguments.get("message")
    if not isinstance(message, str) or message.startswith("gAAAA"):
        raise ValueError(f"native {name} message encrypted or unavailable; raw result checked, exact payload equality unverified. Obtain host plaintext bound to call_id {call['call_id']}; requested receipts are not execution proof")
    require(arguments == expected, f"native {name} complete arguments mismatch")
    return returned, raw_records[raw.index(call)].get("timestamp")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for flag in ("repo", "base", "candidate", "baseline", "initial-wrapper", "host-receipt", "observed",
                 "native-calls", "followup-wrapper", "followup-receipt", "followup-native-calls", "entity", "marker", "policy", "capabilities"):
        parser.add_argument("--" + flag, required=True)
    args = parser.parse_args(argv)
    try:
        require(bool(args.marker.strip()), "acknowledgement marker must be nonblank")
        repo = Path(args.repo).resolve()
        candidate = git(repo, "rev-parse", args.candidate)
        require(git(repo, "rev-parse", "HEAD") == candidate and not git(repo, "status", "--porcelain"), "candidate must be checked out and clean")
        baseline = read(args.baseline)
        require(baseline["base"] == git(repo, "rev-parse", args.base), "baseline base mismatch")
        changed = git(repo, "diff", "--name-only", args.base, candidate).splitlines()
        require(changed and all(p.startswith("kc-dev-flow-2/") for p in changed), "product changes escape dev2")
        for path, objects in baseline["protected_base_git_objects"].items():
            require(git(repo, "ls-tree", "-r", candidate, "--", path) == objects.strip(), f"protected git objects changed: {path}")
        for item in baseline["stock_files"]:
            require(hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() == item["sha256"], f"protected stock bytes changed: {item['path']}")
        initial, host = read(args.initial_wrapper), read(args.host_receipt)
        binding = initial["binding"]
        require(resolve(args.policy, args.capabilities, "implementation", binding["requested_model"], binding["requested_reasoning"]) == binding, "current policy/capabilities differ from bound input")
        require((binding["model"], binding["reasoning_effort"]) == ("gpt-6.1-sol", "high"), "pilot requires Sol/high")
        require(host["binding"] == binding and host["requested_spawn_args"] == initial["spawn_args"], "initial requested receipt mismatch")
        require(initial["helper_name"] == initial["stock_helper"]["name"], "stock helper name changed")
        require(initial["spawn_args"] == convert(initial["stock_helper"], binding)["spawn_args"], "initial spawn arguments differ from verified binding/stock helper")
        producer, _ = native_call(args.native_calls, "spawn_agent", initial["spawn_args"], host["returned_handle"])
        observed = [r for r in read(args.observed) if r["handle"] == producer]
        require(len(observed) == 1, "missing/ambiguous producer metadata")
        observed = observed[0]
        raw = list(records(observed["session_path"]))
        metas = [r["payload"] for r in raw if r["type"] == "session_meta"]
        require(len(metas) == 1 and metas[0]["id"] == observed["session_id"], "raw session identity mismatch")
        source = metas[0]["source"]["subagent"]["thread_spawn"]
        require(source["agent_path"] == producer, "raw session producer mismatch")
        parent = [r["payload"] for r in records(read(args.native_calls)["source_session"]) if r["type"] == "session_meta"]
        require(len(parent) == 1 and source.get("parent_thread_id") == parent[0]["id"], "raw child belongs to a different parent session")
        turns = {}
        for record in raw:
            if record["type"] == "turn_context":
                context = record["payload"]
                turns.setdefault(context["turn_id"], []).append(context)
        require(observed["turns"], "no observed turns")
        for turn in observed["turns"]:
            for actual in turns[turn["turn_id"]]:
                require(actual["model"] == turn["model"] == binding["model"] and actual["effort"] == turn["reasoning_effort"] == binding["reasoning_effort"], "raw observed settings mismatch")
        followup, receipt = read(args.followup_wrapper), read(args.followup_receipt)
        require("spawn_args" not in followup and followup["binding"] == binding and followup["reuse"] is True, "followup binding/transport mismatch")
        require(followup["followup_args"] == {"target": producer, "message": followup["stock_helper"]["prompt"]}, "followup pointer/target changed")
        require(receipt["candidate"] == candidate and receipt["handle"] == producer and receipt["binding"] == binding, "followup candidate/producer/binding mismatch")
        wrapper = repo / "kc-dev-flow-2/scripts/codex_dispatch.py"
        require(receipt["wrapper_sha256"] == hashlib.sha256(wrapper.read_bytes()).hexdigest(), "followup used a different wrapper")
        entity = Path(args.entity).resolve()
        require(Path(receipt["entity_file"]).resolve() == entity and receipt["stage"] == "implementation", "followup entity/stage mismatch")
        require(Path(receipt["code_worktree"]).resolve() == repo and receipt["branch"] == git(repo, "branch", "--show-current"), "followup worktree/branch mismatch")
        require(receipt["before"] == receipt["after"], "followup ownership/state changed")
        for key in ("entity_file", "stage", "code_worktree", "branch", "handle"):
            require(receipt["after"][key] == receipt[key], f"followup ownership snapshot mismatch: {key}")
        require(f"worktree {repo}\n" in git(repo, "worktree", "list", "--porcelain") + "\n", "code worktree not registered")
        require(entity.is_file(), "canonical task is missing")
        for phase in ("before", "after"):
            state = Path(receipt[phase + "_entity_snapshot"]).read_text().split("---", 2)[1]
            require(receipt[phase]["frontmatter_sha256"] == hashlib.sha256(state.encode()).hexdigest(), f"{phase} raw entity frontmatter differs from receipt")
            require("status: implementation\n" in state and f"worktree: {repo.parent.name}/{repo.name}\n" in state, f"{phase} entity was not registered in implementation")
        require(receipt["marker"] == args.marker and receipt["completion_turn_id"] in turns, "missing followup marker/turn")
        _, requested_at = native_call(args.followup_native_calls, "followup_task", followup["followup_args"])
        request_time = event_time(requested_at, "native followup request")
        context_times = [event_time(r.get("timestamp"), "claimed completion context") for r in raw
                         if r["type"] == "turn_context" and r["payload"]["turn_id"] == receipt["completion_turn_id"]]
        require(context_times and context_times == sorted(context_times), "claimed completion context timing is ambiguous")
        require(context_times[0] > request_time, "claimed completion turn must begin after the native followup request")
        for actual in turns[receipt["completion_turn_id"]]:
            require((actual["model"], actual["effort"]) == (binding["model"], binding["reasoning_effort"]), "followup host settings changed")
        messages = [r["payload"] for r in raw if r["type"] == "response_item" and r["payload"].get("type") == "message" and r["payload"].get("role") == "assistant"]
        require(any(isinstance(m.get("internal_chat_message_metadata_passthrough"), dict)
                    and m["internal_chat_message_metadata_passthrough"].get("turn_id") == receipt["completion_turn_id"]
                    and any(args.marker in part.get("text", "") for part in m.get("content", [])) for m in messages),
                "unique reply absent from the claimed completion turn")
        print(f"PASS candidate={candidate}; protected bytes, requested/observed Sol/high, complete native arguments/results and real producer followup marker match")
        print("Limit: local evidence consistency only; independent validation/approval remain separate.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, IndexError, subprocess.CalledProcessError) as error:
        print(f"HOLD: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
