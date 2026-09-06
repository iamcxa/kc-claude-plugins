#!/usr/bin/env python3
"""Compute and verify a kc-ship-flow-batch-pin/v1 record for one batch station."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
RESOURCES_PATH = PACKAGE_ROOT / "schemas" / "resources.json"
PLUGIN_JSON_PATH = PACKAGE_ROOT / ".claude-plugin" / "plugin.json"
RESOURCES_SCHEMA = "kc-ship-flow-resources/v1"
PIN_SCHEMA = "kc-ship-flow-batch-pin/v1"
STATIONS = ["dispatched", "accepted", "reviewed", "uat", "merged", "closed"]


class PinError(RuntimeError):
    pass


def load_declared_resources() -> list[str]:
    try:
        raw = RESOURCES_PATH.read_bytes()
    except OSError as exc:
        raise PinError(f"cannot read {RESOURCES_PATH}: {exc}") from exc
    try:
        declared = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PinError(f"{RESOURCES_PATH} is not valid JSON: {exc}") from exc
    if not isinstance(declared, dict) or declared.get("schema") != RESOURCES_SCHEMA:
        raise PinError(f"{RESOURCES_PATH} schema must be {RESOURCES_SCHEMA}")
    resources = declared.get("resources")
    if (
        not isinstance(resources, list)
        or not resources
        or any(not isinstance(item, str) or not item for item in resources)
        or len(resources) != len(set(resources))
    ):
        raise PinError("declared resources must be a non-empty list of unique paths")
    return resources


def read_plugin_version() -> str:
    try:
        raw = PLUGIN_JSON_PATH.read_bytes()
    except OSError as exc:
        raise PinError(f"cannot read {PLUGIN_JSON_PATH}: {exc}") from exc
    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PinError(f"{PLUGIN_JSON_PATH} is not valid JSON: {exc}") from exc
    version = manifest.get("version") if isinstance(manifest, dict) else None
    if not isinstance(version, str) or not version:
        raise PinError(f"{PLUGIN_JSON_PATH} is missing a version string")
    return version


def compute_contract_digest(
    resources: list[str],
) -> tuple[str, list[dict[str, str]]]:
    digest = hashlib.sha256()
    resource_hashes: list[dict[str, str]] = []
    for declared in sorted(resources):
        relative = Path(declared)
        if relative.is_absolute() or ".." in relative.parts:
            raise PinError(f"declared resource escapes the package: {declared!r}")
        path = (PACKAGE_ROOT / relative).resolve()
        if not path.is_relative_to(PACKAGE_ROOT) or not path.is_file():
            raise PinError(f"declared resource missing: {declared}")
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise PinError(f"declared resource unreadable: {declared}: {exc}") from exc
        path_bytes = declared.encode("utf-8")
        digest.update(len(path_bytes).to_bytes(8, "big"))
        digest.update(path_bytes)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
        resource_hashes.append({"path": declared, "sha256": hashlib.sha256(raw).hexdigest()})
    return digest.hexdigest(), resource_hashes


def expected_previous_station(station: str) -> str | None:
    if station not in STATIONS:
        raise PinError(f"unknown station: {station!r}")
    index = STATIONS.index(station)
    return STATIONS[index - 1] if index > 0 else None


def build_record(batch: str, station: str) -> dict[str, object]:
    resources = load_declared_resources()
    contract_digest, resource_hashes = compute_contract_digest(resources)
    return {
        "schema": PIN_SCHEMA,
        "batch": batch,
        "station": station,
        "plugin_version": read_plugin_version(),
        "contract_digest": contract_digest,
        "previous_station": expected_previous_station(station),
        "written_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "resources": resource_hashes,
    }


def check_no_station_regression(pin_path: Path, batch: str, station: str) -> None:
    if not pin_path.exists():
        return
    try:
        existing = json.loads(pin_path.read_bytes())
    except (OSError, ValueError) as exc:
        raise PinError(f"PIN_UNREADABLE: cannot read {pin_path}: {exc}") from exc
    if not isinstance(existing, dict) or existing.get("schema") != PIN_SCHEMA:
        raise PinError(f"PIN_UNREADABLE: {pin_path} is not a {PIN_SCHEMA} record")
    if existing.get("batch") != batch:
        raise PinError(
            f"PIN_BATCH_MISMATCH: {pin_path} records batch {existing.get('batch')!r}, "
            f"requested {batch!r}"
        )
    existing_station = existing.get("station")
    if existing_station not in STATIONS or station not in STATIONS:
        raise PinError(f"PIN_UNREADABLE: {pin_path} records an unrecognized station")
    if STATIONS.index(existing_station) > STATIONS.index(station):
        raise PinError(
            f"PIN_REGRESSION_REFUSED: existing {existing_station!r} is later than {station!r}"
        )


def cmd_write(args: argparse.Namespace) -> int:
    pin_path = Path(args.pin).expanduser().resolve() if args.pin else None
    if pin_path is not None:
        check_no_station_regression(pin_path, args.batch, args.station)
    record = build_record(args.batch, args.station)
    text = json.dumps(record, indent=2, sort_keys=True)
    print(text)
    if pin_path is not None:
        pin_path.parent.mkdir(parents=True, exist_ok=True)
        pin_path.write_text(text + "\n", encoding="utf-8")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    pin_path = Path(args.pin).expanduser().resolve()
    try:
        raw = pin_path.read_bytes()
    except OSError as exc:
        raise PinError(f"cannot read pin {pin_path}: {exc}") from exc
    try:
        record = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PinError(f"pin {pin_path} is not valid JSON: {exc}") from exc
    if not isinstance(record, dict) or record.get("schema") != PIN_SCHEMA:
        raise PinError(f"pin {pin_path} schema must be {PIN_SCHEMA}")
    if record.get("station") != args.station:
        raise PinError(
            f"STATION_MISMATCH: pin is for {record.get('station')!r}, "
            f"expected {args.station!r}"
        )

    resources = load_declared_resources()
    contract_digest, resource_hashes = compute_contract_digest(resources)
    if contract_digest != record.get("contract_digest"):
        recorded = {
            item.get("path"): item.get("sha256")
            for item in record.get("resources", [])
            if isinstance(item, dict)
        }
        changed = [
            item["path"] for item in resource_hashes if recorded.get(item["path"]) != item["sha256"]
        ]
        detail = ", ".join(changed) if changed else "the declared resource set itself"
        raise PinError(f"CONTRACT_DIGEST_MISMATCH: changed resource: {detail}")

    expected = expected_previous_station(args.station)
    if record.get("previous_station") != expected:
        raise PinError(
            "PREVIOUS_STATION_MISMATCH: recorded previous_station is "
            f"{record.get('previous_station')!r}, expected {expected!r}"
        )

    print(f"PIN_CHECK_OK: batch={record.get('batch')!r} station={args.station!r}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pin.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    write_parser = subparsers.add_parser("write")
    write_parser.add_argument("--batch", required=True)
    write_parser.add_argument("--station", required=True, choices=STATIONS)
    write_parser.add_argument("--pin", default=None)
    write_parser.set_defaults(func=cmd_write)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--pin", required=True)
    check_parser.add_argument("--station", required=True, choices=STATIONS)
    check_parser.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except PinError as exc:
        print(f"PIN_REFUSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
