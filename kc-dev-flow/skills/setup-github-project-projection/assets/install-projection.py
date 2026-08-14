#!/usr/bin/env python3
"""Plan, install, or audit reviewable Spacedock projection files."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any


ASSET_DIR = pathlib.Path(__file__).resolve().parent
TARGETS = {
    ".github/workflows/spacedock-project-sync.yml": "spacedock-project-sync.yml",
    ".github/scripts/project-spacedock-state.py": "project-spacedock-state.py",
}


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def build_config(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": "spacedock-project-config/v1",
        "repository": args.repository,
        "trunk_ref": args.trunk_ref,
        "state_ref": args.state_ref,
        "workflow_dir": args.workflow_dir,
        "profile": args.profile,
        "entity_selection": sorted(set(args.entity or [])),
        "project": {
            "owner_type": args.project_owner_type,
            "owner": args.project_owner,
            "number": args.project_number,
            "node_id": args.project_id,
        },
        "project_secret_name": args.project_secret_name,
        "credential": {
            "token_type": args.project_token_type,
            "permissions": args.project_token_permissions,
            "expiry": args.credential_expiry,
            "rotation_owner": args.rotation_owner,
            "fallback_blast_radius": args.fallback_blast_radius,
        },
        "schedule_interval_minutes": args.schedule_interval_minutes,
        "external_apply_enabled": bool(args.enable_external_apply),
    }


def desired_files(config: dict[str, Any]) -> dict[str, bytes]:
    files = {
        target: (ASSET_DIR / source).read_bytes() for target, source in TARGETS.items()
    }
    workflow_path = ".github/workflows/spacedock-project-sync.yml"
    interval = config["schedule_interval_minutes"]
    cron = "0 * * * *" if interval == 60 else f"*/{interval} * * * *"
    secret_name = config["project_secret_name"]
    if not secret_name.replace("_", "").isalnum() or not secret_name[0].isalpha():
        raise ValueError("project secret name must be an Actions-compatible identifier")
    workflow = (
        files[workflow_path]
        .decode()
        .replace("__SCHEDULE_CRON__", cron)
        .replace("__PROJECT_SECRET_NAME__", secret_name)
    )
    files[workflow_path] = workflow.encode()
    files[".github/spacedock-project.json"] = _canonical_json(config)
    return files


def installation_plan(target: pathlib.Path, config: dict[str, Any]) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    for relative, desired in sorted(desired_files(config).items()):
        path = target / relative
        current = path.read_bytes() if path.exists() else None
        changes.append(
            {
                "path": relative,
                "action": "NO_CHANGE" if current == desired else "CREATE" if current is None else "UPDATE",
                "current_digest": _digest(current) if current is not None else None,
                "desired_digest": _digest(desired),
            }
        )
    return {
        "schema": "spacedock-project-install-plan/v1",
        "target": str(target.resolve()),
        "external_mutations": [],
        "files": changes,
    }


def write_installation(target: pathlib.Path, config: dict[str, Any]) -> dict[str, Any]:
    plan = installation_plan(target, config)
    for relative, desired in desired_files(config).items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(desired)
    return plan


def audit_installation(target: pathlib.Path, config: dict[str, Any]) -> dict[str, Any]:
    plan = installation_plan(target, config)
    plan["clean"] = all(item["action"] == "NO_CHANGE" for item in plan["files"])
    return plan


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("plan", "install", "audit"))
    parser.add_argument("--target", type=pathlib.Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--workflow-dir", required=True)
    parser.add_argument("--trunk-ref", default="main")
    parser.add_argument("--state-ref", required=True)
    parser.add_argument("--profile", choices=("generic", "kc-dev-flow"), default="generic")
    parser.add_argument(
        "--entity",
        action="append",
        help="project only this entity slug; repeat for a bounded subset",
    )
    parser.add_argument("--project-owner-type", choices=("user", "organization"), required=True)
    parser.add_argument("--project-owner", required=True)
    parser.add_argument("--project-number", type=int, required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--project-secret-name", default="SPACEDOCK_PROJECT_TOKEN")
    parser.add_argument(
        "--project-token-type",
        choices=("unresolved", "classic-pat", "fine-grained-pat", "github-app"),
        default="unresolved",
    )
    parser.add_argument("--credential-expiry")
    parser.add_argument("--project-token-permissions")
    parser.add_argument("--rotation-owner")
    parser.add_argument("--fallback-blast-radius")
    parser.add_argument("--schedule-interval-minutes", type=int, default=15)
    parser.add_argument("--enable-external-apply", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.schedule_interval_minutes not in {5, 10, 15, 20, 30, 60}:
        raise SystemExit("schedule interval must be one of 5, 10, 15, 20, 30, or 60 minutes")
    if args.enable_external_apply:
        if (
            args.project_token_type == "unresolved"
            or not args.project_token_permissions
            or not args.credential_expiry
            or not args.rotation_owner
            or not args.fallback_blast_radius
        ):
            raise SystemExit(
                "external apply requires token type, permissions, expiry, rotation owner, "
                "and fallback blast radius"
            )
        if args.project_owner_type == "user" and args.project_token_type != "classic-pat":
            raise SystemExit("the REST adapter for a user-owned Project requires classic-pat")
    config = build_config(args)
    if args.mode == "install":
        result = write_installation(args.target, config)
    elif args.mode == "audit":
        result = audit_installation(args.target, config)
    else:
        result = installation_plan(args.target, config)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if args.mode != "audit" or result["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
