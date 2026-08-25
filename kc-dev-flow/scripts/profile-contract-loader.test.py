#!/usr/bin/env python3
"""Behavior contract for profile-contract-loader.py."""

from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import os
import re
import shutil
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
        "production": ("shape", "build", "verify"),
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
    schema: str = "kc-dev-flow-work-profile/v3",
    route: list[str] | None = None,
    sprint: str | None = "kc-dev-flow/S2",
    sprint_readiness: str | None = "ready",
    poc_fields: dict[str, str] | None = None,
) -> Path:
    if route is None:
        route = [logical for logical, _next in MODULE.ROUTES[profile].values()]
    if poc_fields is None and profile == "poc-exploration" and schema.endswith("/v3"):
        poc_fields = {
            "poc_decision": "Choose whether to fund the delivery slice",
            "poc_falsifier": "The integrated probe loses the accepted state",
            "poc_budget": "One local run and one review",
            "poc_stop_when": "Stop after the first integrated result",
        }
    path = root / "work-items" / f"{name}.md"
    path.parent.mkdir(exist_ok=True)
    frontmatter = ["---", f"status: {workflow_stage}"]
    if sprint is not None:
        frontmatter.append(f"sprint: {sprint}")
    if sprint_readiness is not None:
        frontmatter.append(f"sprint-readiness: {sprint_readiness}")
    receipt = [
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
    ]
    if poc_fields is not None:
        receipt.extend(f"  {field}: {value}" for field, value in poc_fields.items())
    receipt.extend(
        [
            "```",
            "",
            "## Problem",
            "",
            "Fixture work item.",
            "",
        ]
    )
    path.write_text("\n".join(frontmatter + receipt), encoding="utf-8")
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
            "validation": ("verify", "done"),
        },
    }
    require(MODULE.ROUTES == expected_routes, "route topology drifted")

    scheduling_refusals = [
        (
            "pilot-product-slice", "ideation", {"sprint": None},
            "frontmatter sprint", "an item with no scheduled sprint",
        ),
        (
            "pilot-product-slice", "ideation", {"sprint": "null"},
            "must name an iteration", "an item with a YAML null sprint",
        ),
        (
            "production", "ideation", {"sprint": "~"},
            "must name an iteration", "an item with a shorthand YAML null sprint",
        ),
        (
            "production", "ideation", {"sprint": "false"},
            "must name an iteration", "an item with a YAML boolean sprint",
        ),
        (
            "production", "ideation", {"sprint": "[S2]"},
            "must name an iteration", "an item with a YAML collection sprint",
        ),
        (
            "production", "ideation", {"sprint": "'   '"},
            "must name an iteration", "an item with a quoted blank sprint",
        ),
        (
            "production", "ideation", {"sprint_readiness": None},
            "frontmatter sprint-readiness", "an item with no sprint readiness",
        ),
        (
            "poc-exploration", "implementation", {"sprint_readiness": "defer"},
            "must be 'ready'", "an item that remains deferred",
        ),
    ]
    for profile, stage, fields, error, description in scheduling_refusals:
        work_item = write_work_item(
            root, profile, stage, f"first-stage-{profile}", **fields
        )
        rejected = subprocess.run(
            [
                sys.executable,
                str(LOADER),
                "--contracts-root",
                str(root),
                "--work-item",
                str(work_item),
            ],
            text=True,
            capture_output=True,
        )
        require(
            rejected.returncode == 2 and error in rejected.stderr,
            f"first working stage accepted {description}",
        )

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
                and document["receipt_schema"] == "kc-dev-flow-work-profile/v3",
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
            root, "production", "ideation", "concurrent-production"
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

    required_poc_fields = (
        "poc_decision",
        "poc_falsifier",
        "poc_budget",
        "poc_stop_when",
    )
    valid_poc_fields = {
        "poc_decision": "Choose whether to fund the delivery slice",
        "poc_falsifier": "The integrated probe loses the accepted state",
        "poc_budget": "One local run and one review",
        "poc_stop_when": "Stop after the first integrated result",
    }
    for missing_field in required_poc_fields:
        missing_fields = {
            field: value
            for field, value in valid_poc_fields.items()
            if field != missing_field
        }
        missing_poc_field = write_work_item(
            root,
            "poc-exploration",
            "implementation",
            f"missing-{missing_field}",
            poc_fields=missing_fields,
        )
        rejected = subprocess.run(
            [
                sys.executable,
                str(LOADER),
                "--contracts-root",
                str(root),
                "--work-item",
                str(missing_poc_field),
            ],
            text=True,
            capture_output=True,
        )
        require(
            rejected.returncode == 2
            and f"exactly one {missing_field}" in rejected.stderr,
            f"v3 POC accepted a missing {missing_field}",
        )

    invalid_values = (
        "''",
        "'   '",
        "null",
        "~",
        "TBD",
        "TODO",
        "<the next commitment this evidence decides>",
    )
    for index, invalid_value in enumerate(invalid_values):
        invalid_fields = dict(valid_poc_fields)
        invalid_fields["poc_decision"] = invalid_value
        invalid_poc_field = write_work_item(
            root,
            "poc-exploration",
            "implementation",
            f"invalid-poc-decision-{index}",
            poc_fields=invalid_fields,
        )
        rejected = subprocess.run(
            [
                sys.executable,
                str(LOADER),
                "--contracts-root",
                str(root),
                "--work-item",
                str(invalid_poc_field),
            ],
            text=True,
            capture_output=True,
        )
        require(
            rejected.returncode == 2
            and "poc_decision must be a concrete scalar" in rejected.stderr,
            f"v3 POC accepted placeholder {invalid_value!r}",
        )

    duplicate_poc_field = write_work_item(
        root,
        "poc-exploration",
        "implementation",
        "duplicate-poc-decision",
    )
    duplicate_text = duplicate_poc_field.read_text(encoding="utf-8")
    duplicate_poc_field.write_text(
        duplicate_text.replace(
            "  poc_decision: Choose whether to fund the delivery slice",
            "  poc_decision: First decision\n  poc_decision: Second decision",
            1,
        ),
        encoding="utf-8",
    )
    rejected = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(duplicate_poc_field),
        ],
        text=True,
        capture_output=True,
    )
    require(
        rejected.returncode == 2
        and "exactly one poc_decision" in rejected.stderr,
        "v3 POC accepted duplicate poc_decision fields",
    )

    active_v2_poc = write_work_item(
        root,
        "poc-exploration",
        "implementation",
        "active-v2-poc",
        schema="kc-dev-flow-work-profile/v2",
    )
    rejected = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(active_v2_poc),
        ],
        text=True,
        capture_output=True,
    )
    require(
        rejected.returncode == 2
        and "active v2 POC must finish on v3.x or be Captain re-recorded as v3"
        in rejected.stderr,
        "active v2 POC did not fail closed",
    )

    for compatible_profile, compatible_stage in (
        ("pilot-product-slice", "ideation"),
        ("production", "ideation"),
    ):
        compatible_v2 = write_work_item(
            root,
            compatible_profile,
            compatible_stage,
            f"compatible-v2-{compatible_profile}",
            schema="kc-dev-flow-work-profile/v2",
        )
        compatible = MODULE.load_contracts(root, compatible_v2)
        require(
            compatible["receipt_schema"] == "kc-dev-flow-work-profile/v2",
            f"compatible v2 {compatible_profile} receipt was not retained",
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

    missing = root / "profiles" / "production" / "verify.md"
    missing.unlink()
    production_validation = write_work_item(
        root, "production", "validation", "missing-production-verify"
    )
    rejected = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(production_validation),
        ],
        text=True,
        capture_output=True,
    )
    require(
        rejected.returncode == 2 and "cannot load selected contract" in rejected.stderr,
        "missing selected stage did not fail closed",
    )
    missing.write_text("STAGE-production-verify\n", encoding="utf-8")

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

    # Presence is not enough: a path that escapes the contracts root must be
    # refused even when a real file sits at the resolved location.
    outside = root.parent / "outside-contracts-root.md"
    outside.write_text("OUTSIDE\n", encoding="utf-8")
    for escaping_path, label in [
        ("../../../outside-contracts-root.md", "traversal"),
        (str(outside), "absolute"),
    ]:
        declaring_stage.write_text(
            "STAGE-poc-exploration-prove\n\n"
            "```json\n"
            '{"schema": "kc-dev-flow-conditional-references/v1", '
            '"references": [{"path": "' + escaping_path + '", '
            '"trigger": "example", "receipt": null}]}\n'
            "```\n",
            encoding="utf-8",
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
            rejected.returncode == 2 and "OUTSIDE" not in rejected.stdout,
            f"{label} conditional reference escaped the contracts root",
        )

    # An absolute path is refused even when it resolves inside the root: a
    # vendored contract carrying one is unportable, which containment misses.
    declaring_stage.write_text(
        "STAGE-poc-exploration-prove\n\n"
        "```json\n"
        '{"schema": "kc-dev-flow-conditional-references/v1", '
        '"references": [{"path": "' + str(root / "never-vendored.md") + '", '
        '"trigger": "example", "receipt": null}]}\n'
        "```\n",
        encoding="utf-8",
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
        rejected.returncode == 2 and "absolute" in rejected.stderr,
        "in-root absolute conditional reference was accepted",
    )

    # A non-object or malformed JSON block must not escape as a traceback: an
    # unrelated array is ignored, a malformed reference set is a ContractError.
    for block, expect_rc, label in [
        ('["not", "an", "object"]', 0, "unrelated JSON array"),
        ('{"schema": "kc-dev-flow-conditional-references/v1", "references": {}}',
         2, "non-list reference set"),
        ('{"schema": "kc-dev-flow-conditional-references/v1", "references": [1]}',
         2, "reference entry without a path"),
    ]:
        declaring_stage.write_text(
            "STAGE-poc-exploration-prove\n\n```json\n" + block + "\n```\n",
            encoding="utf-8",
        )
        result = subprocess.run(
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
            result.returncode == expect_rc and "Traceback" not in result.stderr,
            f"{label} did not resolve to a clean rc={expect_rc}: {result.returncode} {result.stderr[:120]}",
        )

    # declared_receipts surfaces the selected stage contract's own receipt
    # name in the loader's JSON output.
    declaring_stage.write_text(
        "STAGE-poc-exploration-prove\n\n"
        "```json\n"
        '{"schema": "kc-dev-flow-conditional-references/v1", '
        '"references": [{"path": "../../kernel.md", '
        '"trigger": "example", "receipt": "example_receipt"}]}\n'
        "```\n",
        encoding="utf-8",
    )
    presence = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(unvendored_item),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
    )
    require(presence.returncode == 0, presence.stderr)
    presence_document = json.loads(presence.stdout)
    require(
        presence_document.get("declared_receipts") == ["example_receipt"],
        "declared_receipts did not surface the stage's own receipt name: "
        f"{presence_document.get('declared_receipts')!r}",
    )

    # declared_receipts derives only from the selected stage contract's own
    # block: kernel.md and base.md may declare the same schema (an adopter
    # mistake, not a supported input), but their receipts must not flatten
    # into the output, and a null receipt in the stage's own block must not
    # leak through either.
    kernel_path = root / "kernel.md"
    base_path = root / "profiles" / "poc-exploration" / "base.md"
    kernel_original = kernel_path.read_text(encoding="utf-8")
    base_original = base_path.read_text(encoding="utf-8")
    kernel_path.write_text(
        kernel_original.rstrip("\n") + "\n\n"
        "```json\n"
        '{"schema": "kc-dev-flow-conditional-references/v1", '
        '"references": [{"path": "profiles/poc-exploration/build.md", '
        '"trigger": "example", "receipt": "kernel_receipt"}]}\n'
        "```\n",
        encoding="utf-8",
    )
    base_path.write_text(
        base_original.rstrip("\n") + "\n\n"
        "```json\n"
        '{"schema": "kc-dev-flow-conditional-references/v1", '
        '"references": [{"path": "build.md", '
        '"trigger": "example", "receipt": "base_receipt"}]}\n'
        "```\n",
        encoding="utf-8",
    )
    declaring_stage.write_text(
        "STAGE-poc-exploration-prove\n\n"
        "```json\n"
        '{"schema": "kc-dev-flow-conditional-references/v1", '
        '"references": ['
        '{"path": "../../kernel.md", "trigger": "example", "receipt": "stage_receipt"}, '
        '{"path": "../../kernel.md", "trigger": "example_untriggered", "receipt": null}'
        "]}\n"
        "```\n",
        encoding="utf-8",
    )
    isolation = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(unvendored_item),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
    )
    require(isolation.returncode == 0, isolation.stderr)
    isolation_document = json.loads(isolation.stdout)
    require(
        isolation_document.get("declared_receipts") == ["stage_receipt"],
        "declared_receipts leaked a null receipt or a kernel/base receipt, or "
        f"missed the stage's own receipt: {isolation_document.get('declared_receipts')!r}",
    )
    kernel_path.write_text(kernel_original, encoding="utf-8")
    base_path.write_text(base_original, encoding="utf-8")

    # declared_receipts preserves exact document order across MULTIPLE
    # conditional-references blocks in the same stage contract, including a
    # receipt name that repeats. This is the normal shape for a third of the
    # shipped contracts (production/shape.md, pilot-product-slice/shape.md,
    # poc-exploration/build.md each declare more than one non-null receipt);
    # a reader that returned only the first receipt, a sorted list, or a set
    # would still pass a single-block/single-receipt test but must fail this
    # one. The two blocks also interleave TWO distinct valid vendored paths
    # (../../kernel.md and the sibling base.md) so that a reader that grouped
    # entries by resolved path before returning — instead of appending each
    # entry in document order — would reorder receipt_b ahead of the second
    # receipt_a and fail this assertion too; with a single shared path that
    # mutation shape is indistinguishable from a correct reader.
    declaring_stage.write_text(
        "STAGE-poc-exploration-prove\n\n"
        "```json\n"
        '{"schema": "kc-dev-flow-conditional-references/v1", '
        '"references": ['
        '{"path": "../../kernel.md", "trigger": "first", "receipt": "receipt_a"}, '
        '{"path": "base.md", "trigger": "second", "receipt": "receipt_b"}'
        "]}\n"
        "```\n\n"
        "some prose between the two blocks\n\n"
        "```json\n"
        '{"schema": "kc-dev-flow-conditional-references/v1", '
        '"references": ['
        '{"path": "../../kernel.md", "trigger": "third", "receipt": "receipt_a"}, '
        '{"path": "base.md", "trigger": "fourth", "receipt": "receipt_c"}'
        "]}\n"
        "```\n",
        encoding="utf-8",
    )
    multi_block = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(unvendored_item),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
    )
    require(multi_block.returncode == 0, multi_block.stderr)
    multi_block_document = json.loads(multi_block.stdout)
    require(
        multi_block_document.get("declared_receipts")
        == ["receipt_a", "receipt_b", "receipt_a", "receipt_c"],
        "declared_receipts did not preserve exact document order across "
        "multiple conditional-references blocks, or dropped the repeated "
        f"name: {multi_block_document.get('declared_receipts')!r}",
    )

    # The text-format default output (no --format flag — the invocation
    # docs/dev/README.md documents) embeds the header as its first line;
    # declared_receipts must be visible there too, not only under
    # --format json. A single default-only run cannot discriminate render_text
    # from render_text's own output shape leaking a header key: if the
    # loader's default changed to json, the whole output would collapse to a
    # single-line JSON document that still carries declared_receipts, and
    # splitlines()[0] would still parse. Comparing the no-flag run against an
    # explicit --format text run on the same fixture closes that gap — the
    # two only match when the no-flag path actually goes through
    # render_text().
    declaring_stage.write_text(
        "STAGE-poc-exploration-prove\n\n"
        "```json\n"
        '{"schema": "kc-dev-flow-conditional-references/v1", '
        '"references": [{"path": "../../kernel.md", '
        '"trigger": "example", "receipt": "text_format_receipt"}]}\n'
        "```\n",
        encoding="utf-8",
    )
    text_format = subprocess.run(
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
    require(text_format.returncode == 0, text_format.stderr)
    explicit_text_format = subprocess.run(
        [
            sys.executable,
            str(LOADER),
            "--contracts-root",
            str(root),
            "--work-item",
            str(unvendored_item),
            "--format",
            "text",
        ],
        text=True,
        capture_output=True,
    )
    require(explicit_text_format.returncode == 0, explicit_text_format.stderr)
    require(
        text_format.stdout == explicit_text_format.stdout,
        "the no-flag default output diverged from an explicit --format text "
        "run on the same fixture, so the default is not provably rendered by "
        f"render_text(): {text_format.stdout[:80]!r} vs "
        f"{explicit_text_format.stdout[:80]!r}",
    )
    header_line = text_format.stdout.splitlines()[0]
    header_document = json.loads(header_line)
    require(
        header_document.get("declared_receipts") == ["text_format_receipt"],
        "text-format default output's header line did not carry "
        f"declared_receipts: {header_document.get('declared_receipts')!r}",
    )

# --- Live Spacedock route mechanism: the production release-authorization
# residual, and the two `build`-owed checks from the work-profile receipt's
# testing obligations.
#
# 1. Drive a POC and a Pilot item through the REAL gate lifecycle
#    (`gate prepare` / `gate record --consume`, no forced `--set status=done`)
#    to `done` against the committed 5-state graph and assert no status was
#    ever outside the declared route. Against the pre-fix 6-state graph (with
#    `release`) this is RED: the Pilot item's validation-approval consume
#    lands at `status: release`, outside `pilot-product-slice`'s declared
#    route `[ideation, implementation, validation]` — reproducing the
#    `declared-receipts-need-a-reader` incident. See the stage report for the
#    captured RED transcript from that pre-fix run.
# 2. At every real `gate record --consume`, assert the loader's computed
#    `next_workflow_stage` for that (profile, workflow_stage) pair equals the
#    runtime's own `target-stage`, so the two cannot silently diverge again.
#    Pilot's route already diverges pre-fix (loader said `done`, the runtime
#    said `release`) even though only `production`'s ROUTES entry changes in
#    this fix — that divergence is exactly what stranded the incident item.
# 3. The Production release-authorization mechanism: `merge guard --verdict`
#    is refused with no pending terminal-target approval; a non-forced
#    `status --set status=done` is refused while that approval is pending;
#    only `merge guard --verdict passed` finalizes, recording a verdict and
#    completed time distinct from the validation gate's own resolution time.
#
# Skips (does not fail) when no `spacedock` binary is available, matching
# `profile-spacedock-route.test.py`'s convention — this is a live-CLI check,
# not a property of the loader module alone.

STATE_BRANCH = "spacedock-state/dev"

# Mirrors docs/dev/README.md's committed `stages:` block exactly. Kept as a
# literal string (not read from the README) so this test exercises the same
# graph shape docs/dev/README.md declares without coupling to its file layout;
# a drifted README is caught separately by scripts/kc-dev-flow-contract-test.py's
# `expected_stage_order` assertion.
WORKFLOW_STATES_BLOCK = """  states:
    - name: backlog
      initial: true
      gate: true
    - name: ideation
      gate: true
    - name: implementation
    - name: validation
      gate: true
    - name: done
      terminal: true
"""


def resolve_spacedock() -> Path | None:
    configured = os.environ.get("SPACEDOCK_BIN")
    located = configured or shutil.which("spacedock")
    if not located:
        return None
    candidate = Path(located).expanduser()
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        return None
    return candidate.resolve()


def sd_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], text=True, capture_output=True, check=True
    )


def seed_split_root_workflow(root: Path) -> tuple[Path, Path]:
    """Real split-root Spacedock workflow: a bare origin, a repo with
    docs/dev/README.md committed and pushed, and the state checkout as its
    own linked-worktree Git toplevel on `spacedock-state/dev` — the shape
    `gate record`'s state-publication step requires (an unlinked directory is
    refused with "state checkout must be the exact Git toplevel")."""
    remote = root / "remote.git"
    repo = root / "repo"
    state_seed = root / "state-seed"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
    sd_git(repo, "config", "user.name", "route-fixture")
    sd_git(repo, "config", "user.email", "route-fixture@example.test")
    sd_git(repo, "remote", "add", "origin", str(remote))
    (repo / ".gitignore").write_text("docs/dev/.spacedock-state/\n", encoding="utf-8")
    workflow = repo / "docs/dev"
    workflow.mkdir(parents=True)
    (workflow / "README.md").write_text(
        "---\n"
        "commissioned-by: spacedock@0.27.0\n"
        "entity-type: task\n"
        "entity-label: task\n"
        "entity-label-plural: tasks\n"
        "id-style: sd-b32\n"
        "state: .spacedock-state\n"
        "trunk: main\n"
        "stages:\n"
        "  defaults:\n"
        "    worktree: false\n"
        f"{WORKFLOW_STATES_BLOCK}"
        "---\n\n# route fixture\n",
        encoding="utf-8",
    )
    sd_git(repo, "add", ".gitignore", "docs/dev/README.md")
    sd_git(repo, "commit", "-m", "seed product")
    sd_git(repo, "push", "-u", "origin", "main")
    sd_git(repo, "worktree", "add", "--detach", str(state_seed), "HEAD")
    sd_git(state_seed, "switch", "--orphan", STATE_BRANCH)
    subprocess.run(["git", "-C", str(state_seed), "rm", "-rf", "."], capture_output=True)
    (state_seed / ".gitignore").unlink(missing_ok=True)
    shutil.rmtree(state_seed / "docs", ignore_errors=True)
    (state_seed / ".keep").write_text("", encoding="utf-8")
    sd_git(state_seed, "add", ".keep")
    sd_git(state_seed, "commit", "-m", "seed state")
    sd_git(state_seed, "push", "-u", "origin", STATE_BRANCH)
    sd_git(repo, "worktree", "remove", str(state_seed))
    holder = workflow / ".spacedock-state"
    sd_git(repo, "worktree", "add", str(holder), STATE_BRANCH)
    sd_git(holder, "branch", "--set-upstream-to", f"origin/{STATE_BRANCH}")
    return repo, workflow


def sd_new_entity(
    spacedock: Path, repo: Path, workflow: Path, slug: str, profile: str, route: list[str]
) -> None:
    body = (
        "---\nstatus: backlog\nsprint: kc-dev-flow/S2\n"
        "sprint-readiness: ready\n---\n\n"
        f"# {slug}\n\n## Work profile receipt\n\n```yaml\nwork_profile:\n"
        "  schema: kc-dev-flow-work-profile/v2\n"
        f"  selected: {profile}\n"
        f"  route: [{', '.join(route)}]\n```\n"
    )
    result = subprocess.run(
        [
            str(spacedock), "new", slug, "--workflow-dir", str(workflow),
            "--id-seed", slug, "--id-actor", "fixture",
        ],
        cwd=repo, input=body, text=True, capture_output=True,
    )
    require(result.returncode == 0, f"spacedock new {slug} failed: {result.stdout}{result.stderr}")


def sd_gate_consume(
    spacedock: Path, repo: Path, workflow: Path, slug: str, artifact: Path, label: str
) -> str:
    """Prepare and record-approve-consume the gate at the entity's current
    stage; returns the real runtime `target-stage`."""
    prep = subprocess.run(
        [
            str(spacedock), "gate", "prepare", slug, "--workflow-dir", str(workflow),
            "--question", f"{label}?", "--artifact",
            str(artifact.relative_to(workflow / ".spacedock-state")),
            "--summary", label,
        ],
        cwd=repo, text=True, capture_output=True,
    )
    require(prep.returncode == 0, f"gate prepare {slug}/{label} failed: {prep.stdout}{prep.stderr}")
    rec = subprocess.run(
        [
            str(spacedock), "gate", "record", slug, "--workflow-dir", str(workflow),
            "--decision", "approve", "--actor", "person:captain", "--consume",
        ],
        cwd=repo, text=True, capture_output=True,
    )
    require(rec.returncode == 0, f"gate record {slug}/{label} failed: {rec.stdout}{rec.stderr}")
    match = re.search(r"target-stage=(\S+)", rec.stdout)
    require(match is not None, f"gate record {slug}/{label} did not report target-stage: {rec.stdout}")
    return match.group(1)


def sd_status(workflow: Path, slug: str) -> str:
    text = (workflow / ".spacedock-state" / f"{slug}.md").read_text(encoding="utf-8")
    match = re.search(r"^status:\s*(\S+)\s*$", text, re.MULTILINE)
    require(match is not None, f"{slug} has no status field: {text}")
    return match.group(1)


def sd_set(spacedock: Path, repo: Path, workflow: Path, slug: str, field_value: str) -> None:
    result = subprocess.run(
        [str(spacedock), "status", "--workflow-dir", str(workflow), "--set", slug, field_value],
        cwd=repo, text=True, capture_output=True,
    )
    require(result.returncode == 0, f"status --set {slug} {field_value} failed: {result.stdout}{result.stderr}")


spacedock_binary = resolve_spacedock()
if spacedock_binary is None:
    print("profile contract loader test: route mechanism SKIP (spacedock unavailable)")
else:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-route-mechanism-") as route_tmp:
        route_root = Path(route_tmp)
        route_repo, route_workflow = seed_split_root_workflow(route_root)
        route_artifact = route_workflow / ".spacedock-state" / "review.md"
        route_artifact.write_text("route fixture review\n", encoding="utf-8")
        sd_git(route_workflow / ".spacedock-state", "add", "review.md")
        sd_git(route_workflow / ".spacedock-state", "commit", "-m", "add review artifact")

        # POC: backlog's gate lands ideation regardless of profile (the
        # runtime advances by declared graph order, not by ROUTES); the FO's
        # manual nudge past ideation is POC's documented, harmless skip —
        # unchanged by this task — because no gate record is ever created at
        # POC's ideation visit.
        sd_new_entity(spacedock_binary, route_repo, route_workflow, "poc-item", "poc-exploration", ["build", "prove"])
        poc_target_backlog = sd_gate_consume(spacedock_binary, route_repo, route_workflow, "poc-item", route_artifact, "backlog")
        require(poc_target_backlog == "ideation", f"POC backlog gate target drifted: {poc_target_backlog}")
        sd_set(spacedock_binary, route_repo, route_workflow, "poc-item", "status=implementation")
        sd_set(spacedock_binary, route_repo, route_workflow, "poc-item", "status=validation")
        poc_target_validation = sd_gate_consume(spacedock_binary, route_repo, route_workflow, "poc-item", route_artifact, "validation")
        require(
            poc_target_validation == "done" == MODULE.ROUTES["poc-exploration"]["validation"][1],
            f"POC validation did not terminalize at done: runtime={poc_target_validation}",
        )
        require(
            sd_status(route_workflow, "poc-item") == "validation",
            "POC validation-approval-consume should stay pending at validation (terminal-target approved-awaiting-merge)",
        )
        poc_finalize = subprocess.run(
            [str(spacedock_binary), "merge", "guard", "poc-item", "--workflow-dir", str(route_workflow), "--verdict", "passed"],
            cwd=route_repo, text=True, capture_output=True,
        )
        require(poc_finalize.returncode == 0, f"POC merge guard finalize failed: {poc_finalize.stdout}{poc_finalize.stderr}")
        require(
            "done" in poc_finalize.stdout and "verdict passed" in poc_finalize.stdout,
            f"POC did not terminalize via merge guard: {poc_finalize.stdout}",
        )

        # Pilot: real gate lifecycle end to end, no forced status writes.
        # This is the Fixture A shape from the accepted outcome: assert every
        # visited status stays inside pilot-product-slice's declared route,
        # and assert the loader's next_workflow_stage never disagrees with
        # the runtime's own target-stage.
        sd_new_entity(spacedock_binary, route_repo, route_workflow, "pilot-item", "pilot-product-slice", ["shape", "build", "verify-deliver"])
        pilot_route = MODULE.ROUTES["pilot-product-slice"]
        pilot_target_backlog = sd_gate_consume(spacedock_binary, route_repo, route_workflow, "pilot-item", route_artifact, "backlog")
        require(pilot_target_backlog == "ideation", f"pilot backlog gate target drifted: {pilot_target_backlog}")
        pilot_target_ideation = sd_gate_consume(spacedock_binary, route_repo, route_workflow, "pilot-item", route_artifact, "ideation")
        require(
            pilot_target_ideation == pilot_route["ideation"][1] == "implementation",
            f"loader/runtime disagree at pilot ideation: loader={pilot_route['ideation'][1]} runtime={pilot_target_ideation}",
        )
        require(sd_status(route_workflow, "pilot-item") in pilot_route, "pilot status left its declared route before validation")
        sd_set(spacedock_binary, route_repo, route_workflow, "pilot-item", "status=validation")
        pilot_target_validation = sd_gate_consume(spacedock_binary, route_repo, route_workflow, "pilot-item", route_artifact, "validation")
        require(
            pilot_target_validation == pilot_route["validation"][1] == "done",
            "loader/runtime disagree at pilot validation (the exact divergence that stranded "
            f"declared-receipts-need-a-reader): loader={pilot_route['validation'][1]} runtime={pilot_target_validation}",
        )
        require(
            sd_status(route_workflow, "pilot-item") == "validation",
            f"pilot landed outside its declared route {list(pilot_route)} after validation-approval-consume: "
            f"status={sd_status(route_workflow, 'pilot-item')!r} (this is the incident this task closes)",
        )
        sd_finalize = subprocess.run(
            [str(spacedock_binary), "merge", "guard", "pilot-item", "--workflow-dir", str(route_workflow), "--verdict", "passed"],
            cwd=route_repo, text=True, capture_output=True,
        )
        require(sd_finalize.returncode == 0, f"pilot merge guard finalize failed: {sd_finalize.stdout}{sd_finalize.stderr}")
        require(
            "done" in sd_finalize.stdout and "verdict passed" in sd_finalize.stdout,
            f"pilot did not terminalize via merge guard: {sd_finalize.stdout}",
        )

        # Production: the release-authorization residual. No graph state
        # named `release` exists; the two rulings ("verified" / "may be
        # released") are recorded as the validation gate's own resolution and
        # a later, separate merge-guard verdict — and both refusals below are
        # exercised, not asserted from prose.
        sd_new_entity(spacedock_binary, route_repo, route_workflow, "prod-item", "production", ["shape", "build", "verify"])
        prod_route = MODULE.ROUTES["production"]
        sd_gate_consume(spacedock_binary, route_repo, route_workflow, "prod-item", route_artifact, "backlog")
        sd_gate_consume(spacedock_binary, route_repo, route_workflow, "prod-item", route_artifact, "ideation")
        sd_set(spacedock_binary, route_repo, route_workflow, "prod-item", "status=validation")

        # Mechanism 1: merge guard refuses with no pending terminal approval —
        # release cannot be authorized before verification has even started.
        premature_guard = subprocess.run(
            [str(spacedock_binary), "merge", "guard", "prod-item", "--workflow-dir", str(route_workflow), "--verdict", "passed"],
            cwd=route_repo, text=True, capture_output=True,
        )
        require(
            premature_guard.returncode != 0 and "no binding pending terminal-target approval" in premature_guard.stderr,
            f"merge guard did not refuse without a pending approval: rc={premature_guard.returncode} {premature_guard.stderr}",
        )

        prod_target_validation = sd_gate_consume(spacedock_binary, route_repo, route_workflow, "prod-item", route_artifact, "validation")
        require(
            prod_target_validation == prod_route["validation"][1] == "done",
            f"loader/runtime disagree at production validation: loader={prod_route['validation'][1]} runtime={prod_target_validation}",
        )
        require(
            "validation" not in prod_route or sd_status(route_workflow, "prod-item") == "validation",
            "production's validation-approval-consume should stay pending (approved-awaiting-merge), not land at an excluded stage",
        )

        # Mechanism 2: a non-forced status --set cannot bypass the merge-guard
        # ceremony while the terminal approval is pending — this is the
        # "fails when authorization is absent" behavior the residual asked for.
        bypass = subprocess.run(
            [str(spacedock_binary), "status", "--workflow-dir", str(route_workflow), "--set", "prod-item", "status=done"],
            cwd=route_repo, text=True, capture_output=True,
        )
        require(
            bypass.returncode != 0 and "merge guard prod-item is the sole terminal consumer" in bypass.stderr,
            f"status --set status=done was not refused while a terminal approval was pending: rc={bypass.returncode} {bypass.stderr}",
        )
        require(
            sd_status(route_workflow, "prod-item") == "validation",
            "prod-item's status changed despite the refused bypass attempt",
        )

        pre_guard_prod_item = (route_workflow / ".spacedock-state" / "prod-item.md").read_text(encoding="utf-8")
        validation_resolution_at = re.search(
            r"stage: validation.*?at: \"([^\"]+)\"", pre_guard_prod_item, re.DOTALL,
        )
        require(validation_resolution_at is not None, "could not read the validation gate's own resolution timestamp")
        # The "may be released" field does not exist yet: it is not written by
        # the validation gate's own resolution, only by a later merge guard.
        require(
            "completed:" not in pre_guard_prod_item,
            f"completed was already set before merge guard ran — the two rulings are not distinct steps: {pre_guard_prod_item}",
        )

        # The actual release ruling: merge guard --verdict is the only path
        # to done, and it is the sole writer of `completed` — a distinct
        # field, populated by a distinct, later step, from the validation
        # gate's own resolution time above. Two separately rendered rulings,
        # not one collapsed into the other.
        release_guard = subprocess.run(
            [str(spacedock_binary), "merge", "guard", "prod-item", "--workflow-dir", str(route_workflow), "--verdict", "passed"],
            cwd=route_repo, text=True, capture_output=True,
        )
        require(release_guard.returncode == 0, f"authorized merge guard finalize failed: {release_guard.stdout}{release_guard.stderr}")
        archived_prod = (route_workflow / ".spacedock-state" / "_archive" / "prod-item.md").read_text(encoding="utf-8")
        require("status: done" in archived_prod and "verdict: PASSED" in archived_prod, f"production item did not terminalize via merge guard: {archived_prod}")
        require(
            re.search(r"^completed:\s*$", archived_prod, re.MULTILINE) is None
            and re.search(r"^completed: \S+", archived_prod, re.MULTILINE) is not None,
            f"merge guard did not populate completed on finalize: {archived_prod}",
        )
        print("profile contract loader test: route mechanism PASS")

print("profile contract loader test: PASS")
