#!/usr/bin/env python3
"""Behavior contract for adoption-parity.py."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
GUARD = PACKAGE / "scripts/adoption-parity.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"adoption parity test: {message}")


with tempfile.TemporaryDirectory(prefix="kc-dev-flow-adoption-parity-") as temporary:
    root = Path(temporary)
    contracts = root / "contracts"
    tools = root / "tools"
    shutil.copytree(PACKAGE / "references", contracts)
    (contracts / "repository-local-policy.md").write_text(
        "This file is owned by the adopter.\n", encoding="utf-8"
    )
    tools.mkdir()
    loader = tools / "profile-contract-loader.py"
    close_guard = tools / "poc-close-guard.py"
    shutil.copy2(PACKAGE / "scripts/profile-contract-loader.py", loader)
    shutil.copy2(PACKAGE / "scripts/poc-close-guard.py", close_guard)

    base_command = [
        sys.executable,
        str(GUARD),
        "--adopter-root",
        str(root),
        "--contracts-root",
        str(contracts),
        "--profile-loader",
        str(loader),
        "--poc-close-guard",
        str(close_guard),
    ]
    command = base_command + ["--planning-mode", "standalone"]
    result = subprocess.run(command, text=True, capture_output=True)
    require(result.returncode == 0, f"matching adoption refused: {result.stderr}")
    envelope = json.loads(result.stdout)
    package_version = json.loads(
        (PACKAGE / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
    )["version"]
    expected_file_count = sum(
        1 for path in (PACKAGE / "references").rglob("*") if path.is_file()
    ) + 2
    require(
        envelope["schema"] == "kc-dev-flow-adoption-parity/v1"
        and envelope["package_version"] == package_version
        and envelope["planning_mode"] == "standalone"
        and envelope["status"] == "clean"
        and envelope["canonical_file_count"] == expected_file_count
        and len(envelope["canonical_set_sha256"]) == 64,
        f"wrong clean envelope: {envelope}",
    )

    linked_tools = root / "linked-tools"
    linked_contracts = root / "linked-contracts"
    linked_contracts.symlink_to(PACKAGE / "references", target_is_directory=True)
    linked_tools.symlink_to(PACKAGE / "scripts", target_is_directory=True)
    linked_root = root / "linked-root"
    linked_root.symlink_to(root, target_is_directory=True)
    linked_root_command = [
        sys.executable,
        str(GUARD),
        "--adopter-root",
        str(linked_root),
        "--contracts-root",
        str(linked_root / "contracts"),
        "--profile-loader",
        str(linked_root / "tools/profile-contract-loader.py"),
        "--poc-close-guard",
        str(linked_root / "tools/poc-close-guard.py"),
        "--planning-mode",
        "standalone",
    ]
    linked_root_result = subprocess.run(
        linked_root_command, text=True, capture_output=True
    )
    require(
        linked_root_result.returncode == 2
        and not linked_root_result.stdout
        and "adopter root" in linked_root_result.stderr
        and "symbolic link" in linked_root_result.stderr,
        "symlinked adopter root did not fail closed",
    )
    for label, replacements in (
        ("contracts root", {str(contracts): str(linked_contracts)}),
        (
            "profile loader parent",
            {str(loader): str(linked_tools / "profile-contract-loader.py")},
        ),
        (
            "POC close guard parent",
            {str(close_guard): str(linked_tools / "poc-close-guard.py")},
        ),
    ):
        linked_command = [replacements.get(value, value) for value in command]
        linked = subprocess.run(linked_command, text=True, capture_output=True)
        require(
            linked.returncode == 2
            and not linked.stdout
            and "symbolic link" in linked.stderr,
            f"symlinked {label} did not fail closed: {linked.stdout}{linked.stderr}",
        )

    direct_package = subprocess.run(
        [
            sys.executable,
            str(GUARD),
            "--adopter-root",
            str(PACKAGE.parent),
            "--contracts-root",
            str(PACKAGE / "references"),
            "--profile-loader",
            str(PACKAGE / "scripts/profile-contract-loader.py"),
            "--poc-close-guard",
            str(PACKAGE / "scripts/poc-close-guard.py"),
            "--planning-mode",
            "standalone",
        ],
        text=True,
        capture_output=True,
    )
    require(
        direct_package.returncode == 2
        and not direct_package.stdout
        and "inside installed package" in direct_package.stderr,
        "direct installed-package paths did not fail closed",
    )

    kernel = contracts / "kernel.md"
    kernel.unlink()
    kernel.hardlink_to(PACKAGE / "references/kernel.md")
    hardlinked_reference = subprocess.run(command, text=True, capture_output=True)
    require(
        hardlinked_reference.returncode == 2
        and not hardlinked_reference.stdout
        and "same installed package file" in hardlinked_reference.stderr,
        "hard-linked canonical reference did not fail closed",
    )
    kernel.unlink()
    shutil.copy2(PACKAGE / "references/kernel.md", kernel)

    loader.unlink()
    loader.hardlink_to(PACKAGE / "scripts/profile-contract-loader.py")
    hardlinked_helper = subprocess.run(command, text=True, capture_output=True)
    require(
        hardlinked_helper.returncode == 2
        and not hardlinked_helper.stdout
        and "same installed package file" in hardlinked_helper.stderr,
        "hard-linked runtime helper did not fail closed",
    )
    loader.unlink()
    shutil.copy2(PACKAGE / "scripts/profile-contract-loader.py", loader)

    for adopted, label in (
        (loader, "scripts/profile-contract-loader.py"),
        (close_guard, "scripts/poc-close-guard.py"),
    ):
        original = adopted.read_bytes()
        adopted.write_bytes(original + b"\nlocal drift\n")
        helper_drift = subprocess.run(command, text=True, capture_output=True)
        require(
            helper_drift.returncode == 2
            and not helper_drift.stdout
            and label in helper_drift.stderr,
            f"{label} drift did not fail closed: "
            f"{helper_drift.stdout}{helper_drift.stderr}",
        )
        adopted.write_bytes(original)

    kernel_bytes = kernel.read_bytes()
    kernel.write_bytes(kernel_bytes + b"\nlocal drift\n")
    drifted = subprocess.run(command, text=True, capture_output=True)
    require(
        drifted.returncode == 2
        and not drifted.stdout
        and "references/kernel.md" in drifted.stderr,
        f"canonical drift did not fail closed: {drifted.stdout}{drifted.stderr}",
    )
    kernel.write_bytes(kernel_bytes)

    comparator = tools / "engage-reconcile.py"
    shutil.copy2(PACKAGE / "scripts/engage-reconcile.py", comparator)
    provider_command = base_command + [
        "--planning-mode",
        "provider-capable",
        "--engage-comparator",
        str(comparator),
    ]
    provider_clean = subprocess.run(provider_command, text=True, capture_output=True)
    require(provider_clean.returncode == 0, provider_clean.stderr)
    provider_envelope = json.loads(provider_clean.stdout)
    require(
        provider_envelope["canonical_file_count"]
        == envelope["canonical_file_count"] + 1,
        f"provider comparator was not added to the canonical set: {provider_envelope}",
    )
    require(
        provider_envelope["planning_mode"] == "provider-capable"
        and provider_envelope["canonical_set_sha256"]
        != envelope["canonical_set_sha256"],
        f"provider mode was not bound into the result: {provider_envelope}",
    )
    missing_comparator = subprocess.run(
        base_command + ["--planning-mode", "provider-capable"],
        text=True,
        capture_output=True,
    )
    require(
        missing_comparator.returncode == 2
        and not missing_comparator.stdout
        and "requires --engage-comparator" in missing_comparator.stderr,
        "provider-capable mode accepted no comparator",
    )
    standalone_comparator = subprocess.run(
        command + ["--engage-comparator", str(comparator)],
        text=True,
        capture_output=True,
    )
    require(
        standalone_comparator.returncode == 2
        and not standalone_comparator.stdout
        and "standalone mode refuses --engage-comparator"
        in standalone_comparator.stderr,
        "standalone mode accepted a comparator",
    )
    linked_comparator_command = [
        str(linked_tools / "engage-reconcile.py")
        if value == str(comparator)
        else value
        for value in provider_command
    ]
    linked_comparator = subprocess.run(
        linked_comparator_command, text=True, capture_output=True
    )
    require(
        linked_comparator.returncode == 2
        and not linked_comparator.stdout
        and "symbolic link" in linked_comparator.stderr,
        "symlinked comparator parent did not fail closed",
    )
    comparator.write_bytes(comparator.read_bytes() + b"\nprovider drift\n")
    provider_drift = subprocess.run(provider_command, text=True, capture_output=True)
    require(
        provider_drift.returncode == 2
        and not provider_drift.stdout
        and "scripts/engage-reconcile.py" in provider_drift.stderr,
        f"provider comparator drift did not fail closed: {provider_drift.stdout}{provider_drift.stderr}",
    )

print("adoption parity test: PASS")
