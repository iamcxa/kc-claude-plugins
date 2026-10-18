#!/usr/bin/env python3
"""Reconcile a local candidate, protected baseline and FO's real pilot host evidence.

This reads machine-local raw host logs; it neither dispatches nor authenticates a
provider. Missing evidence fails closed. Native message ciphertext is not decoded:
compare wrapper prompt bytes locally and check the child's unique acknowledgement.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from codex_dispatch import resolve


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


def native_call(ledger_path, name, expected):
    ledger = read(ledger_path)
    calls = [r["payload"] for r in ledger["calls"] if r["payload"].get("name") == name]
    require(len(calls) == 1, f"expected one {name} in {ledger_path}")
    call = calls[0]
    raw = [r["payload"] for r in records(ledger["source_session"])
           if r.get("type") == "response_item" and r["payload"].get("call_id") == call["call_id"]]
    require(call in raw, f"native call absent/altered in raw host log: {name}")
    arguments = json.loads(call["arguments"])
    require(all(arguments.get(k) == v for k, v in expected.items()), f"native {name} arguments mismatch")
    return call


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for flag in ("repo", "base", "candidate", "baseline", "initial-wrapper", "host-receipt", "observed",
                 "native-calls", "followup-wrapper", "followup-receipt", "followup-native-calls", "entity", "marker", "policy", "capabilities"):
        parser.add_argument("--" + flag, required=True)
    args = parser.parse_args(argv)
    try:
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
        require(initial["spawn_args"]["message"] == initial["stock_helper"]["prompt"] and initial["helper_name"] == initial["stock_helper"]["name"], "stock prompt/name changed")
        producer = host["returned_handle"]
        native_call(args.native_calls, "spawn_agent", {k: initial["spawn_args"][k] for k in ("task_name", "fork_turns", "model", "reasoning_effort")})
        observed = [r for r in read(args.observed) if r["handle"] == producer]
        require(len(observed) == 1, "missing/ambiguous producer metadata")
        observed = observed[0]
        raw = list(records(observed["session_path"]))
        metas = [r["payload"] for r in raw if r["type"] == "session_meta"]
        require(len(metas) == 1 and metas[0]["id"] == observed["session_id"], "raw session identity mismatch")
        source = metas[0]["source"]["subagent"]["thread_spawn"]
        require(source["agent_path"] == producer, "raw session producer mismatch")
        turns = {r["payload"]["turn_id"]: r["payload"] for r in raw if r["type"] == "turn_context"}
        require(observed["turns"], "no observed turns")
        for turn in observed["turns"]:
            actual = turns[turn["turn_id"]]
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
        require(receipt["completion_turn_id"] != observed["turns"][0]["turn_id"], "followup has no new host turn")
        actual = turns[receipt["completion_turn_id"]]
        require((actual["model"], actual["effort"]) == (binding["model"], binding["reasoning_effort"]), "followup host settings changed")
        messages = [r["payload"] for r in raw if r["type"] == "response_item" and r["payload"].get("type") == "message" and r["payload"].get("role") == "assistant"]
        require(any(args.marker in part.get("text", "") for m in messages for part in m.get("content", [])), "unique reply absent from raw child output")
        native_call(args.followup_native_calls, "followup_task", {"target": producer})
        print(f"PASS candidate={candidate}; protected bytes, requested/observed Sol/high, real producer followup marker and raw host records match")
        print("Limit: local evidence consistency only; encrypted native message bodies are not decoded; independent validation/approval remain separate.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, IndexError, subprocess.CalledProcessError) as error:
        print(f"HOLD: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
