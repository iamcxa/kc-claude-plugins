#!/usr/bin/env python3
"""Bind an explicitly selected dev2 Codex policy around stock Spacedock transport."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from number_guards import Misconfigured, frontmatter


def read_json(path, category, raw=None):
    try:
        value = json.loads(Path(path).read_bytes() if raw is None else raw)
        if not isinstance(value, dict):
            raise ValueError("expected a JSON object")
        return value
    except (OSError, ValueError) as error:
        raise ValueError(f"{category} {str(path)!r}: {error}") from error


def scalar(value):
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    if not re.fullmatch(r"[\w.-]+|'[\w.-]+'|\"[\w.-]+\"", value):
        raise ValueError(f"unsupported model/reasoning scalar: {value!r}")
    return value.strip("'\"")


def declaration(workflow, agent, stage):
    if agent:
        fields = frontmatter(Path(agent))
        return scalar(fields.get("model", "")), scalar(fields["reasoning"]) if "reasoning" in fields else None
    path = Path(workflow) / "README.md"
    text = path.read_text()
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("workflow requires fenced frontmatter")
    lines = text.split("\n---\n", 1)[0].splitlines()[1:]
    defaults, states, current = {}, {}, None
    section = None
    inside = False
    for line in lines:
        if line and not line.startswith(" ") and not line.startswith("#"):
            inside = line == "stages:"
            section = None
        if not inside:
            continue
        if line == "  defaults:":
            section, current = "defaults", defaults
        elif line == "  states:":
            section, current = "states", None
        elif section == "states" and re.match(r"^    - name:\s*", line):
            name = scalar(line.split(":", 1)[1])
            if name in states:
                raise ValueError(f"duplicate stage {name}")
            states[name] = current = {}
        else:
            indent = "    " if section == "defaults" else "      "
            match = re.fullmatch(indent + r"(model|reasoning):\s*(.*)", line)
            if match and current is not None:
                if match[1] in current:
                    raise ValueError(f"duplicate {match[1]} declaration")
                current[match[1]] = scalar(match[2])
    if stage not in states:
        raise ValueError(f"stage {stage!r} not found in adopted block declarations")
    fields = dict(defaults, **states[stage])
    if "model" not in fields:
        raise ValueError("missing declared model")
    return fields["model"], fields.get("reasoning")


def resolve(policy_path, capabilities_path, stage, model, reasoning):
    try:
        raw = Path(policy_path).read_bytes()
    except OSError as error:
        raise ValueError(f"policy {str(policy_path)!r}: {error}") from error
    policy = read_json(policy_path, "policy", raw)
    if not isinstance(policy, dict) or type(policy.get("version")) is not int or policy["version"] != 1 or not isinstance(policy.get("id"), str) or not policy["id"]:
        raise ValueError("unsupported or unnamed Codex policy")
    if not isinstance(policy.get("models"), dict) or not isinstance(policy.get("reasoning_defaults"), dict):
        raise ValueError("invalid Codex policy mappings")
    mapped = policy["models"].get(model)
    effort = reasoning if reasoning is not None else policy["reasoning_defaults"].get(stage)
    capabilities = read_json(capabilities_path, "capabilities")
    if not isinstance(capabilities, dict) or not isinstance(capabilities.get("arguments"), list) or not isinstance(capabilities.get("supported_models"), dict):
        raise ValueError("invalid host capability snapshot")
    required = {"task_name", "message", "fork_turns", "model", "reasoning_effort"}
    if not required.issubset(capabilities.get("arguments", [])):
        raise ValueError("host lacks explicit native spawn arguments")
    supported = capabilities["supported_models"].get(mapped, [])
    if not isinstance(mapped, str) or not isinstance(effort, str) or not isinstance(supported, list) or not effort or effort not in supported:
        raise ValueError(f"unmapped or unsupported binding {model!r}/{effort!r}")
    return {"policy_id": policy["id"], "policy_sha256": hashlib.sha256(raw).hexdigest(),
            "requested_model": model, "requested_reasoning": reasoning,
            "model": mapped, "reasoning_effort": effort}


def reusable(binding, previous, fresh=False):
    return not fresh and bool(previous) and all(previous.get(key) == binding[key] for key in
                                               ("model", "reasoning_effort", "policy_id", "policy_sha256"))


def convert(helper, binding, previous=None, fresh=False, target=None):
    name, prompt = helper.get("name"), helper.get("prompt")
    if not isinstance(prompt, str) or not prompt:
        raise ValueError("stock helper requires a non-empty prompt string")
    if name is None:
        if not target or not reusable(binding, previous, fresh):
            raise ValueError("advance requires a matching prior binding and target; otherwise build fresh")
        return {"followup_args": {"target": target, "message": prompt}, "binding": binding,
                "reuse": True, "reuse_reason": "binding matches; shared lifecycle/freshness checks still required"}
    if not isinstance(name, str) or not name or target:
        raise ValueError("fresh helper requires name and no reused target")
    task_name = re.sub(r"[^a-z0-9_]+", "_", name.lower()).strip("_") or "spacedock_worker"
    reuse = reusable(binding, previous, fresh)
    reason = "binding matches; shared lifecycle/freshness checks still required" if reuse else "spawn fresh: absent or mismatched binding"
    if fresh:
        reuse, reason = False, "independent fresh context required"
    return {"spawn_args": {"task_name": task_name, "message": prompt, "fork_turns": "none",
                           "model": binding["model"], "reasoning_effort": binding["reasoning_effort"]},
            "helper_name": name, "binding": binding, "reuse": reuse, "reuse_reason": reason}


def flag_value(args, name):
    values = [arg.split("=", 1)[1] for arg in args if arg.startswith(name + "=")]
    for index, arg in enumerate(args):
        if arg == name:
            if index + 1 == len(args):
                raise ValueError(f"missing {name} value")
            values.append(args[index + 1])
    if len(values) != 1:
        raise ValueError(f"require exactly one {name}")
    return values[0]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "convert"))
    parser.add_argument("--spacedock", default="spacedock")
    parser.add_argument("--policy")
    parser.add_argument("--capabilities")
    parser.add_argument("--stage")
    parser.add_argument("--workflow-dir")
    parser.add_argument("--agent-file")
    parser.add_argument("--previous-binding")
    parser.add_argument("--stock-output", help="retain raw stock stdout at this explicit evidence path")
    parser.add_argument("--target")
    parser.add_argument("--fresh", action="store_true")
    supplied = list(sys.argv[1:] if argv is None else argv)
    split = supplied.index("--") if "--" in supplied else len(supplied)
    args = parser.parse_args(supplied[:split])
    forwarded = supplied[split + 1:]
    phase = "preflight"
    recovery = "Correct the named input and rerun preflight; do not substitute or dispatch an older payload."
    try:
        if args.command == "build" and args.policy is None:
            return subprocess.run([args.spacedock, "dispatch", "build", *forwarded]).returncode
        if not args.policy or not args.capabilities:
            raise ValueError("selected conversion requires --policy and --capabilities")
        workflow, stage = args.workflow_dir, args.stage
        if args.command == "build":
            if any(arg == "--host" or arg.startswith("--host=") for arg in forwarded):
                if flag_value(forwarded, "--host") != "codex":
                    raise ValueError("selected policy applies only to Codex")
            else:
                forwarded += ["--host", "codex"]
            workflow, stage = flag_value(forwarded, "--workflow-dir"), flag_value(forwarded, "--stage")
        if not stage or bool(workflow) == bool(args.agent_file):
            raise ValueError("require --stage and exactly one workflow or agent declaration")
        binding = resolve(args.policy, args.capabilities, stage, *declaration(workflow, args.agent_file, stage))
        previous = read_json(args.previous_binding, "previous binding") if args.previous_binding else None
        if args.command == "build":
            if "--advance" in forwarded and (not args.target or not reusable(binding, previous, args.fresh)):
                recovery = "After FO confirms fresh-worker eligibility, build fresh without --advance and without --target."
                raise ValueError("advance requires matching policy/model/effort, a target and no --fresh; stock was not called")
            phase = "stock build"
            recovery = "Inspect stock state and dispatch artifacts before retry; stock may have written partial state. Do not resend automatically."
            done = subprocess.run([args.spacedock, "dispatch", "build", *forwarded],
                                  text=True, capture_output=True)
            sys.stderr.write(done.stderr)
            if args.stock_output:
                Path(args.stock_output).write_text(done.stdout)
            if done.returncode:
                print(f"codex_dispatch: stock build exited {done.returncode}. {recovery}", file=sys.stderr)
                return done.returncode
            phase = "stock conversion"
            helper = json.loads(done.stdout)
        else:
            if forwarded:
                raise ValueError("convert does not accept stock build arguments")
            helper = json.load(sys.stdin)
        if not isinstance(helper, dict):
            raise ValueError("stock helper must be a JSON object")
        result = convert(helper, binding, previous, args.fresh, args.target)
        result["stock_helper"] = helper
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, Misconfigured) as error:
        print(f"codex_dispatch: {phase}: {error}. {recovery}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
