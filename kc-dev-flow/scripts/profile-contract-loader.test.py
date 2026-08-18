#!/usr/bin/env python3
"""Behavior contract for profile-contract-loader.py."""

from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
LOADER = HERE / "profile-contract-loader.py"
SPEC = importlib.util.spec_from_file_location("profile_contract_loader", LOADER)
if SPEC is None or SPEC.loader is None:
    raise SystemExit("cannot import profile contract loader")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"profile contract loader test: {message}")


def write_fixture(root: Path) -> None:
    (root / "kernel.md").write_text("CORE-MARKER\n", encoding="utf-8")
    for profile, stages in {
        "poc-exploration": ("build", "prove"),
        "pilot-product-slice": ("shape", "build", "verify-deliver"),
        "production": ("shape", "build", "verify", "release"),
    }.items():
        profile_root = root / "profiles" / profile
        profile_root.mkdir(parents=True)
        (profile_root / "base.md").write_text(
            f"BASE-{profile}\n", encoding="utf-8"
        )
        for stage in stages:
            (profile_root / f"{stage}.md").write_text(
                f"STAGE-{profile}-{stage}\n", encoding="utf-8"
            )


def write_work_item(
    root: Path,
    profile: str,
    workflow_stage: str,
    name: str,
    *,
    schema: str = "kc-dev-flow-work-profile/v2",
    route: list[str] | None = None,
) -> Path:
    if route is None:
        route = [logical for logical, _next in MODULE.ROUTES[profile].values()]
    path = root / "work-items" / f"{name}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                f"status: {workflow_stage}",
                "---",
                "",
                "## Work profile receipt",
                "",
                "```yaml",
                "work_profile:",
                f"  schema: {schema}",
                f"  selected: {profile}",
                f"  recommended: {profile}",
                f"  route: [{', '.join(route)}]",
                "  basis: fixture",
                "```",
                "",
                "## Problem",
                "",
                "Fixture work item.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


with tempfile.TemporaryDirectory(prefix="profile-contract-loader-") as temporary:
    root = Path(temporary)
    write_fixture(root)

    expected_routes = {
        "poc-exploration": {
            "implementation": ("build", "validation"),
            "validation": ("prove", "done"),
        },
        "pilot-product-slice": {
            "ideation": ("shape", "implementation"),
            "implementation": ("build", "validation"),
            "validation": ("verify-deliver", "done"),
        },
        "production": {
            "ideation": ("shape", "implementation"),
            "implementation": ("build", "validation"),
            "validation": ("verify", "release"),
            "release": ("release", "done"),
        },
    }
    require(MODULE.ROUTES == expected_routes, "route topology drifted")

    all_markers = {
        f"BASE-{profile}" for profile in expected_routes
    } | {
        f"STAGE-{profile}-{logical}"
        for profile, stages in expected_routes.items()
        for logical, _ in stages.values()
    }

    for profile, stages in expected_routes.items():
        for workflow_stage, (logical_stage, next_stage) in stages.items():
            work_item = write_work_item(
                root, profile, workflow_stage, f"{profile}-{workflow_stage}"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(LOADER),
                    "--contracts-root",
                    str(root),
                    "--work-item",
                    str(work_item),
                    "--format",
                    "json",
                ],
                text=True,
                capture_output=True,
            )
            require(result.returncode == 0, result.stderr)
            document = json.loads(result.stdout)
            require(
                document["profile"] == profile
                and document["logical_stage"] == logical_stage
                and document["next_workflow_stage"] == next_stage,
                f"wrong route result: {document}",
            )
            require(
                document["work_item"] == work_item.resolve().as_posix()
                and document["receipt_schema"] == "kc-dev-flow-work-profile/v2",
                f"work-item binding is missing: {document}",
            )
            paths = [item["path"] for item in document["loaded"]]
            require(
                paths
                == [
                    "kernel.md",
                    f"profiles/{profile}/base.md",
                    f"profiles/{profile}/{logical_stage}.md",
                ],
                f"wrong loaded paths: {paths}",
            )
            content = "".join(item["content"] for item in document["loaded"])
            selected = {"CORE-MARKER", f"BASE-{profile}", f"STAGE-{profile}-{logical_stage}"}
            require(selected <= set(content.splitlines()), "selected contract is incomplete")
            require(
                not (all_markers - selected).intersection(content.splitlines()),
                "an unselected profile or stage leaked into the contract",
            )

    concurrent_items = {
        "poc-exploration": write_work_item(
            root, "poc-exploration", "implementation", "concurrent-poc"
        ),
        "pilot-product-slice": write_work_item(
            root, "pilot-product-slice", "validation", "concurrent-pilot"
        ),
        "production": write_work_item(
            root, "production", "release", "concurrent-production"
        ),
    }

    def load_concurrently(item: tuple[str, Path]) -> tuple[str, subprocess.CompletedProcess[str]]:
        profile, work_item = item
        return profile, subprocess.run(
            [
                sys.executable,
                str(LOADER),
                "--contracts-root",
                str(root),
                "--work-item",
                str(work_item),
                "--format",
                "json",
            ],
            text=True,
            capture_output=True,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        concurrent_results = dict(executor.map(load_concurrently, concurrent_items.items()))
    for profile, result in concurrent_results.items():
        require(result.returncode == 0, f"concurrent {profile}: {result.stderr}")
        document = json.loads(result.stdout)
        require(document["profile"] == profile, f"concurrent profile crossed: {document}")
        loaded_paths = "\n".join(item["path"] for item in document["loaded"])
        require(
            all(
                f"profiles/{other}/" not in loaded_paths
                for other in concurrent_items
                if other != profile
            ),
            f"concurrent unselected profile leaked: {document}",
        )

    poc_ideation = write_work_item(
        root, "poc-exploration", "ideation", "rejected-poc-ideation"
    )
    rejected = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(poc_ideation),
        ],
        text=True,
        capture_output=True,
    )
    require(
        rejected.returncode == 2 and "outside poc-exploration" in rejected.stderr,
        "POC accepted an inactive ideation stage",
    )

    legacy_item = write_work_item(
        root,
        "poc-exploration",
        "implementation",
        "legacy-receipt",
        schema="kc-dev-flow-work-profile/v1",
    )
    rejected = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(legacy_item),
        ],
        text=True,
        capture_output=True,
    )
    require(
        rejected.returncode == 2 and "unsupported work profile schema" in rejected.stderr,
        "legacy receipt did not fail closed",
    )

    stale_item = write_work_item(
        root,
        "pilot-product-slice",
        "implementation",
        "stale-route",
        route=["shape", "build"],
    )
    rejected = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(stale_item),
        ],
        text=True,
        capture_output=True,
    )
    require(
        rejected.returncode == 2 and "stale route" in rejected.stderr,
        "stale profile route did not fail closed",
    )

    missing = root / "profiles" / "production" / "release.md"
    missing.unlink()
    production_release = write_work_item(
        root, "production", "release", "missing-production-release"
    )
    rejected = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(production_release),
        ],
        text=True,
        capture_output=True,
    )
    require(
        rejected.returncode == 2 and "cannot load selected contract" in rejected.stderr,
        "missing selected stage did not fail closed",
    )

    # A stage that declares a conditional reference the adopter never vendored
    # must fail at load, not silently drop the capability the stage declares.
    declaring_stage = root / "profiles" / "poc-exploration" / "prove.md"
    declaring_stage.write_text(
        "STAGE-poc-exploration-prove\n\n"
        "```json\n"
        '{"schema": "kc-dev-flow-conditional-references/v1", '
        '"references": [{"path": "../../never-vendored.md", '
        '"trigger": "example", "receipt": null}]}\n'
        "```\n",
        encoding="utf-8",
    )
    unvendored_item = write_work_item(
        root, "poc-exploration", "validation", "unvendored-conditional-reference"
    )
    rejected = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(unvendored_item),
        ],
        text=True,
        capture_output=True,
    )
    require(
        rejected.returncode == 2
        and "never-vendored.md" in rejected.stderr
        and "not vendored" in rejected.stderr,
        "unvendored conditional reference did not fail closed",
    )

    # The same stage passes once the reference exists, so the check gates on
    # presence rather than on declaring a conditional reference at all.
    (root / "never-vendored.md").write_text("VENDORED\n", encoding="utf-8")
    accepted = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(unvendored_item),
        ],
        text=True,
        capture_output=True,
    )
    require(
        accepted.returncode == 0
        and "STAGE-poc-exploration-prove" in accepted.stdout
        and "VENDORED" not in accepted.stdout,
        "vendored conditional reference did not load, or was read eagerly",
    )

print("profile contract loader test: PASS")
