#!/usr/bin/env python3
"""Live multi-profile route gate for kc-dev-flow.

Drives one Spacedock workflow that holds a POC, a Pilot, and a Production work
item at the same time, and asserts the three claims that make profile-native
routing safe to ship:

1. Concurrency — three items in one workflow, each at a different state, each
   loading only its own profile's contracts.
2. Fail-closed routing — a state outside a selected route is refused by the
   loader instead of silently loading another profile's stage.
3. One terminal path — every profile reaches `done` through the same states,
   with Production's release authorization applied as a terminal-approval
   boundary (`route=approved-awaiting-merge` then `merge guard --verdict`)
   rather than as a state the other profiles skip.
4. Proportional load — a lighter profile's whole route loads strictly less
   than a heavier one's, and no single stage load exceeds a declared share of
   the reference tree. This is the only automated evidence behind "POC does
   not pay for Production policy"; without it a POC contract can grow past
   Production's and the claim silently becomes false.

Claims 1-2 are asserted against the packaged contracts and the self-adopted
`docs/dev/_mods` copy. Claim 3 needs the real runtime, so it runs against the
installed Spacedock binary.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "kc-dev-flow"
ADOPTED = ROOT / "docs/dev/_mods"

# The shared graph every profile routes through. It is written out, not derived
# from the loader, so a profile that reintroduces a state of its own — the
# defect that stranded a Pilot item at `status: release` — has nowhere to put
# it: the runtime refuses a state this graph does not declare.
GRAPH_STATES = ["backlog", "ideation", "implementation", "validation", "done"]

# Lightest route first. The order is the product claim: the smallest sufficient
# route must stay the cheapest one to load.
LOAD_ORDER = ["poc-exploration", "pilot-product-slice", "production"]

# Ceiling on one stage's loaded bytes as a share of the whole reference tree.
# Measured high-water mark when this was set: 15.7% (Pilot `shape`). The
# headroom is for a contract that grows with its subject; the ceiling is for a
# stage that quietly absorbs a conditional reference it should have left unread.
STAGE_LOAD_CEILING = 0.20

WORKFLOW_README = """---
commissioned-by: spacedock@0.27.0
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
trunk: main
stages:
  defaults:
    worktree: false
    concurrency: 3
  states:
    - name: backlog
      initial: true
      gate: true
    - name: ideation
      gate: true
    - name: implementation
    - name: validation
      feedback-to: implementation
      gate: true
    - name: done
      terminal: true
---

# Multi-profile route gate fixture

One superset state graph shared by every profile.
"""


class GateError(RuntimeError):
    """The multi-profile claim is not currently true."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def profile_states(loader) -> dict[str, list[str]]:
    """Each profile's runtime states, taken from the loader's own routes."""
    states = {}
    for profile, route in loader.ROUTES.items():
        states[profile] = ["backlog", *route.keys(), "done"]
    return states


def route_load(loader, contracts_root: Path, item: Path) -> int:
    """Bytes a single stage load puts in front of the worker."""
    contract = loader.load_contracts(contracts_root, item)
    return sum(entry["bytes"] for entry in contract["loaded"])


def reference_tree_bytes(contracts_root: Path) -> int:
    return sum(path.stat().st_size for path in contracts_root.rglob("*.md"))


def assert_proportional_load(loader, contracts_root: Path) -> dict[str, int]:
    """Every profile's whole-route load, ordered lightest first."""
    tree = reference_tree_bytes(contracts_root)
    require(tree > 0, f"no contracts found under {contracts_root}")
    totals: dict[str, int] = {}
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-load-") as temporary:
        scratch = Path(temporary)
        for profile, route in loader.ROUTES.items():
            logical = [stage for stage, _next in route.values()]
            total = 0
            for state in route:
                item = scratch / f"{profile}-{state}.md"
                item.write_text(entity_body(f"{profile}-{state}", profile, logical), encoding="utf-8")
                item.write_text(
                    item.read_text(encoding="utf-8").replace("status: backlog", f"status: {state}", 1),
                    encoding="utf-8",
                )
                stage_bytes = route_load(loader, contracts_root, item)
                require(
                    stage_bytes <= tree * STAGE_LOAD_CEILING,
                    f"{profile} {state} loads {stage_bytes} bytes, over the "
                    f"{STAGE_LOAD_CEILING:.0%} share of the {tree}-byte reference tree",
                )
                total += stage_bytes
            totals[profile] = total
    ordered = [totals[profile] for profile in LOAD_ORDER if profile in totals]
    require(
        ordered == sorted(ordered) and len(set(ordered)) == len(ordered),
        f"route load is not strictly ordered lightest-first under {contracts_root}: "
        + ", ".join(f"{profile}={totals[profile]}" for profile in LOAD_ORDER if profile in totals),
    )
    return totals


def load_loader():
    spec = importlib.util.spec_from_file_location(
        "kc_dev_flow_profile_loader",
        PLUGIN / "scripts/profile-contract-loader.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(command: list[str], label: str, cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    require(
        result.returncode == 0,
        f"{label} failed ({result.returncode}):\n{result.stdout}{result.stderr}",
    )
    return result.stdout + result.stderr


def entity_body(slug: str, profile: str, route: list[str]) -> str:
    return "\n".join(
        [
            "---",
            "status: backlog",
            f"title: {slug}",
            "---",
            "",
            f"# {slug}",
            "",
            "One sentence: a fixture item that exercises the selected route.",
            "",
            "## Work profile receipt",
            "",
            "```yaml",
            "work_profile:",
            "  schema: kc-dev-flow-work-profile/v2",
            f"  selected: {profile}",
            f"  recommended: {profile}",
            f"  route: [{', '.join(route)}]",
            "  basis: multi-profile gate fixture",
            "```",
            "",
        ]
    )


def set_status(spacedock: str, workflow: Path, slug: str, status: str) -> None:
    run(
        [spacedock, "status", "--workflow-dir", str(workflow), "--set", slug, f"status={status}"],
        f"{slug} -> {status}",
        workflow,
    )


def assert_loads_own_route(
    loader, contracts_root: Path, item: Path, profile: str, status: str
) -> None:
    contract = loader.load_contracts(contracts_root, item)
    logical, next_stage = loader.ROUTES[profile][status]
    paths = [entry["path"] for entry in contract["loaded"]]
    require(
        paths
        == ["kernel.md", f"profiles/{profile}/base.md", f"profiles/{profile}/{logical}.md"],
        f"{item.name} at {status} loaded {paths} under {contracts_root}",
    )
    require(
        contract["next_workflow_stage"] == next_stage
        and contract["profile"] == profile
        and contract["receipt_schema"] == "kc-dev-flow-work-profile/v2",
        f"{item.name} at {status} bound the wrong route: {contract['profile']}"
        f" -> {contract['next_workflow_stage']}",
    )
    for other in loader.ROUTES:
        if other != profile:
            require(
                all(f"profiles/{other}/" not in path for path in paths),
                f"{item.name} leaked {other} contracts while at {status}",
            )
    require(
        contract["work_item_sha256"] == hashlib.sha256(item.read_bytes()).hexdigest(),
        f"{item.name} contract is not bound to the exact work-item bytes",
    )


def assert_refuses(loader, contracts_root: Path, item: Path, status: str) -> None:
    try:
        loader.load_contracts(contracts_root, item)
    except loader.ContractError as error:
        require(
            status in str(error),
            f"{item.name} refusal at {status} does not name the offending state: {error}",
        )
        return
    raise GateError(f"{item.name} loaded a contract at off-route state {status}")


def terminalize(spacedock: str, workflow: Path, slug: str) -> None:
    """Approve at validation, then terminalize through the merge ceremony."""
    review = workflow / f"{slug}-review.md"
    review.write_text(f"# {slug} validation review\n", encoding="utf-8")
    run(["git", "add", "--", review.name], f"{slug} stage artifact", workflow)
    run(
        ["git", "commit", "-qm", f"{slug} review"],
        f"{slug} artifact commit",
        workflow,
    )
    run(
        [
            spacedock, "gate", "prepare", slug,
            "--workflow-dir", str(workflow),
            "--question", "Is this item releasable?",
            "--artifact", review.name,
            "--summary", f"{slug} validation",
        ],
        f"{slug} gate prepare",
        workflow,
    )
    recorded = run(
        [
            spacedock, "gate", "record", slug,
            "--workflow-dir", str(workflow),
            "--decision", "approve",
            "--actor", "person:captain",
            "--consume",
        ],
        f"{slug} gate approve",
        workflow,
    )
    require(
        "target-stage=done" in recorded and "route=approved-awaiting-merge" in recorded,
        f"{slug} validation approval did not stop at the terminal-approval boundary:\n{recorded}",
    )
    require(
        "consumed=false" in recorded,
        f"{slug} approval consumed the terminal transition without a merge verdict:\n{recorded}",
    )
    finalized = run(
        [spacedock, "merge", "guard", slug, "--workflow-dir", str(workflow), "--verdict", "passed"],
        f"{slug} merge guard",
        workflow,
    )
    require(
        f"{slug} -> done" in finalized,
        f"{slug} did not terminalize through the merge ceremony:\n{finalized}",
    )


def resolve_spacedock(allow_skip: bool) -> str | None:
    configured = os.environ.get("SPACEDOCK_BIN")
    located = configured or shutil.which("spacedock")
    if located is None:
        if allow_skip:
            return None
        raise GateError(
            "spacedock is required for the runtime claim; install it or pass --allow-skip-runtime"
        )
    path = Path(located).resolve()
    require(path.is_file(), f"spacedock executable does not exist: {path}")
    return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-skip-runtime",
        action="store_true",
        help="report the runtime claim as skipped instead of failing when spacedock is absent",
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable receipt")
    args = parser.parse_args()

    loader = load_loader()
    states = profile_states(loader)
    for profile, route in states.items():
        require(
            [state for state in GRAPH_STATES if state in route] == route,
            f"{profile} declares states outside the shared graph: {route}",
        )
    spacedock = resolve_spacedock(args.allow_skip_runtime)
    contracts_roots = [PLUGIN / "references", ADOPTED]
    route_bytes = {
        str(root.relative_to(ROOT)): assert_proportional_load(loader, root)
        for root in contracts_roots
    }
    results: dict[str, object] = {
        "schema": "kc-dev-flow-multi-profile-gate/v1",
        "contracts_roots": [str(root.relative_to(ROOT)) for root in contracts_roots],
        "runtime": "skipped" if spacedock is None else "spacedock",
        "profiles": sorted(states),
        "route_bytes": route_bytes,
    }

    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-multi-profile-") as temporary:
        workflow = Path(temporary) / "workflow"
        workflow.mkdir()
        (workflow / "README.md").write_text(WORKFLOW_README, encoding="utf-8")
        run(["git", "init", "-q", "-b", "main", "."], "fixture git init", workflow)
        # Repository-scoped identity: Spacedock commits the archive move
        # itself, so a runner with no global git identity must still work.
        run(["git", "config", "user.email", "gate@example.invalid"], "fixture git email", workflow)
        run(["git", "config", "user.name", "kc-dev-flow gate"], "fixture git name", workflow)
        run(["git", "add", "--", "README.md"], "fixture stage", workflow)
        run(
            ["git", "commit", "-qm", "fixture"],
            "fixture commit",
            workflow,
        )

        items: dict[str, Path] = {}
        for profile in sorted(states):
            slug = profile.split("-")[0] + "-item"
            route = [logical for logical, _next in loader.ROUTES[profile].values()]
            body = entity_body(slug, profile, route)
            if spacedock is None:
                path = workflow / f"{slug}.md"
                path.write_text(body, encoding="utf-8")
            else:
                created = subprocess.run(
                    [spacedock, "new", slug, "--workflow-dir", str(workflow)],
                    cwd=workflow,
                    input=body,
                    text=True,
                    capture_output=True,
                )
                require(
                    created.returncode == 0,
                    f"could not create {slug}:\n{created.stdout}{created.stderr}",
                )
                path = workflow / f"{slug}.md"
            items[profile] = path

        # The archive move at terminalization is a tracked-file operation, so
        # the fixture entities must exist in git before any route advances.
        run(["git", "add", "--all", "--", "."], "fixture entities stage", workflow)
        run(
            ["git", "commit", "-qm", "entities"],
            "fixture entities commit",
            workflow,
        )

        # Interleave the routes so the three items sit at different states at
        # the same time. Loading is asserted for every live item at every step,
        # which is what makes this a concurrency claim rather than three
        # independent single-profile runs.
        cursors = {profile: 0 for profile in items}
        while any(
            cursors[profile] < len(states[profile]) - 1 for profile in items
        ):
            for profile, path in items.items():
                route = states[profile]
                if cursors[profile] >= len(route) - 1:
                    continue
                cursors[profile] += 1
                target = route[cursors[profile]]
                if target == "done":
                    cursors[profile] = len(route) - 1
                    continue
                if spacedock is None:
                    text = path.read_text(encoding="utf-8")
                    current = route[cursors[profile] - 1]
                    path.write_text(
                        text.replace(f"status: {current}", f"status: {target}", 1),
                        encoding="utf-8",
                    )
                else:
                    set_status(spacedock, workflow, path.stem, target)
                for live_profile, live_path in items.items():
                    live_state = states[live_profile][cursors[live_profile]]
                    if live_state in ("backlog", "done"):
                        continue
                    for contracts_root in contracts_roots:
                        assert_loads_own_route(
                            loader, contracts_root, live_path, live_profile, live_state
                        )

        # The shared graph is a runtime fact, not a comment: a state no profile
        # declares must be refused by the runtime, which is what makes
        # "no profile owns its own state" enforceable rather than aspirational.
        if spacedock is not None:
            probe = subprocess.run(
                [
                    spacedock, "status", "--workflow-dir", str(workflow),
                    "--set", items["production"].stem, "status=release",
                ],
                cwd=workflow,
                text=True,
                capture_output=True,
            )
            require(
                probe.returncode != 0,
                "the runtime accepted a state the shared graph does not declare",
            )

        # Fail-closed: force the POC item onto Pilot's ideation state and prove
        # the loader refuses rather than borrowing another profile's stage.
        poc = items["poc-exploration"]
        original = poc.read_text(encoding="utf-8")
        poc.write_text(original.replace("status: validation", "status: ideation", 1), encoding="utf-8")
        for contracts_root in contracts_roots:
            assert_refuses(loader, contracts_root, poc, "ideation")
        poc.write_text(original, encoding="utf-8")

        if spacedock is None:
            results["terminal"] = "skipped"
        else:
            for profile, path in items.items():
                terminalize(spacedock, workflow, path.stem)
            remaining = run(
                [spacedock, "status", "--workflow-dir", str(workflow)],
                "final status",
                workflow,
            )
            for path in items.values():
                require(
                    path.stem not in remaining,
                    f"{path.stem} is still active after its route completed:\n{remaining}",
                )
            results["terminal"] = "all profiles reached done"

    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print(
            "kc-dev-flow multi-profile gate: PASS "
            f"(runtime={results['runtime']}, terminal={results['terminal']}, "
            f"route bytes={route_bytes[str(contracts_roots[0].relative_to(ROOT))]})"
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GateError as error:
        print(f"kc-dev-flow multi-profile gate: FAIL\n{error}", file=sys.stderr)
        sys.exit(1)
