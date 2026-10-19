#!/usr/bin/env python3
"""Resolve the Codex model and reasoning effort a dev2 stage or agent should get."""
import argparse
import json
from pathlib import Path
import re
import sys

from number_guards import Misconfigured, frontmatter


def scalar(value):
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    if not re.fullmatch(r"[\w.-]+|'[\w.-]+'|\"[\w.-]+\"", value):
        raise ValueError(f"unsupported model/reasoning scalar: {value!r}")
    return value.strip("'\"")


def stage_declaration(workflow_dir, stage):
    text = (Path(workflow_dir) / "README.md").read_text()
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("workflow requires fenced frontmatter")
    defaults, states, current, section, inside = {}, {}, None, None, False
    for line in text.split("\n---\n", 1)[0].splitlines()[1:]:
        if line and not line.startswith((" ", "#")):
            inside, section = line == "stages:", None
        if not inside:
            continue
        if line == "  defaults:":
            section, current = "defaults", defaults
        elif line == "  states:":
            section, current = "states", None
        elif section == "states" and (name := re.match(r"^    - name:\s*(.*)", line)):
            if scalar(name[1]) in states:
                raise ValueError(f"duplicate stage {scalar(name[1])!r} in {workflow_dir}/README.md")
            current = states[scalar(name[1])] = {}
        elif current is not None and (field := re.fullmatch(
                ("    " if section == "defaults" else "      ") + r"(model|reasoning):\s*(.*)", line)):
            if field[1] in current:
                raise ValueError(f"duplicate {field[1]} declaration in {section} block of {workflow_dir}/README.md")
            current[field[1]] = scalar(field[2])
    if stage not in states:
        raise ValueError(f"stage {stage!r} not found in {workflow_dir}/README.md")
    fields = {**defaults, **states[stage]}
    if "model" not in fields:
        raise ValueError(f"stage {stage!r} declares no model")
    return fields["model"], fields.get("reasoning")


def agent_declaration(agent_file):
    fields = frontmatter(Path(agent_file))
    if "model" not in fields:
        raise ValueError(f"{agent_file}: no model declared")
    return scalar(fields["model"]), scalar(fields["reasoning"]) if "reasoning" in fields else None


def resolve(policy_path, name, model, reasoning):
    policy = json.loads(Path(policy_path).read_text())
    mapped = policy["models"].get(model)
    effort = reasoning or policy["reasoning_defaults"].get(name)
    if not mapped:
        raise ValueError(f"{name}: declared model {model!r} has no mapping in {policy_path}")
    if not effort:
        raise ValueError(f"{name}: no declared reasoning and no reasoning_defaults entry in {policy_path}")
    return {"model": mapped, "reasoning_effort": effort}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--workflow-dir")
    parser.add_argument("--stage")
    parser.add_argument("--agent-file")
    parser.add_argument("--flags", action="store_true", help="print --model X --reasoning-effort Y instead of JSON")
    args = parser.parse_args(argv)
    try:
        if args.agent_file and not (args.workflow_dir or args.stage):
            name = Path(args.agent_file).stem
            model, reasoning = agent_declaration(args.agent_file)
        elif args.workflow_dir and args.stage and not args.agent_file:
            name = args.stage
            model, reasoning = stage_declaration(args.workflow_dir, args.stage)
        else:
            parser.error("give either --agent-file or both --workflow-dir and --stage")
        result = resolve(args.policy, name, model, reasoning)
    except (OSError, ValueError, KeyError, AttributeError, Misconfigured) as error:
        print(f"codex_model_policy: {error}", file=sys.stderr)
        return 1
    print(f"--model {result['model']} --reasoning-effort {result['reasoning_effort']}"
          if args.flags else json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
