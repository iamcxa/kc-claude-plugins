#!/usr/bin/env bash
# Validate release-please extra-file resolution and JSONPath targets.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="${REPO_DIR_OVERRIDE:-$(cd "$SCRIPT_DIR/.." && pwd)}"
CONFIG_JSON="$REPO_DIR/release-please-config.json"

python3 - "$REPO_DIR" "$CONFIG_JSON" <<'PY'
import json
import os
import re
import sys

repo_dir = os.path.realpath(sys.argv[1])
config_path = sys.argv[2]

try:
    with open(config_path, encoding="utf-8") as handle:
        config = json.load(handle)
except (OSError, json.JSONDecodeError) as exc:
    print(f"release-please config check failed: {exc}", file=sys.stderr)
    raise SystemExit(1)

packages = config.get("packages")
if not isinstance(packages, dict) or not packages:
    print("release-please config check failed: packages must be a non-empty object", file=sys.stderr)
    raise SystemExit(1)

marketplace_selector = re.compile(
    r'^\$\.plugins\[\?\(@\.name=="([^"]+)"\)\]\.version$'
)
failures = []
rows = []

for package, package_config in packages.items():
    extra_files = package_config.get("extra-files", [])
    if not isinstance(extra_files, list) or not extra_files:
        failures.append(f"{package}: extra-files must be a non-empty array")
        continue

    for extra_file in extra_files:
        if not isinstance(extra_file, dict):
            failures.append(f"{package}: every extra-file must be an object")
            continue

        configured_path = extra_file.get("path")
        if not isinstance(configured_path, str) or not configured_path:
            failures.append(f"{package}: extra-file path must be a non-empty string")
            continue

        if configured_path.startswith("/"):
            effective_path = configured_path.lstrip("/")
        else:
            effective_path = os.path.join(package, configured_path)

        absolute_path = os.path.realpath(os.path.join(repo_dir, effective_path))
        try:
            inside_repo = os.path.commonpath([repo_dir, absolute_path]) == repo_dir
        except ValueError:
            inside_repo = False
        if not inside_repo:
            failures.append(
                f"{package}: resolved path escapes repository: {configured_path} -> {effective_path}"
            )
            rows.append((package, configured_path, effective_path, "INVALID"))
            continue

        if not os.path.isfile(absolute_path):
            failures.append(
                f"{package}: resolved path does not exist: {configured_path} -> {effective_path}"
            )
            rows.append((package, configured_path, effective_path, "MISSING"))
            continue

        if extra_file.get("type") == "json":
            try:
                with open(absolute_path, encoding="utf-8") as handle:
                    document = json.load(handle)
            except (OSError, json.JSONDecodeError) as exc:
                failures.append(f"{package}: invalid JSON at {effective_path}: {exc}")
                rows.append((package, configured_path, effective_path, "INVALID"))
                continue

            jsonpath = extra_file.get("jsonpath")
            match_count = 0
            if jsonpath == "$.version":
                match_count = int(isinstance(document, dict) and "version" in document)
            elif isinstance(jsonpath, str):
                selector_match = marketplace_selector.fullmatch(jsonpath)
                if selector_match and isinstance(document, dict):
                    plugin_name = selector_match.group(1)
                    plugins = document.get("plugins", [])
                    if isinstance(plugins, list):
                        match_count = sum(
                            1
                            for plugin in plugins
                            if isinstance(plugin, dict)
                            and plugin.get("name") == plugin_name
                            and "version" in plugin
                        )

            if match_count != 1:
                failures.append(
                    f"{package}: JSONPath {jsonpath!r} matches {match_count} fields in {effective_path}; expected 1"
                )
                rows.append((package, configured_path, effective_path, "NO MATCH"))
                continue

        rows.append((package, configured_path, effective_path, "ok"))

print(f"{'PACKAGE':18} {'CONFIGURED PATH':52} {'RESULT':9} EFFECTIVE PATH")
for package, configured_path, effective_path, result in rows:
    print(f"{package:18} {configured_path:52} {result:9} {effective_path}")

if failures:
    print("", file=sys.stderr)
    for failure in failures:
        print(f"release-please config check failed: {failure}", file=sys.stderr)
    raise SystemExit(1)

print("\nRelease-please config: all extra-file paths and JSONPath selectors are valid")
PY
