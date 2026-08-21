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

print("profile contract loader test: PASS")
