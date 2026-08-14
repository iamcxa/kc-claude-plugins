#!/usr/bin/env python3
"""Executable contract for the optional RoboRev implementation-exit sensor."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Barrier


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "kc-dev-flow"
FIXTURE = ROOT / "scripts/fixtures/roborev-implementation-exit/outcomes.json"
STATE_BRANCH = "spacedock-state/dev"
STATE_PREREQ = ROOT / "scripts/dev-flow-state-prereq.sh"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"roborev implementation-exit contract: {message}")


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        capture_output=True,
        check=check,
    )


def classify(case: dict[str, object], identity: dict[str, object]) -> tuple[str, str]:
    capability = case.get("capability")
    if capability in {"unavailable", "unsupported", "skipped"}:
        return "UNAVAILABLE", str(capability)

    # Correlation precedes lifecycle interpretation. A stale exact-input binding
    # cannot be promoted to member_incomplete or to retained findings.
    for field in (
        "repository",
        "base",
        "tip",
        "configuration",
        "provider_version",
        "json_contract",
        "agent",
        "model",
        "reasoning",
        "minimum_severity",
        "panel",
    ):
        if case.get(field, identity[field]) != identity[field]:
            return "UNKNOWN", "stale"

    members = case.get("members", [])
    require(isinstance(members, list), "fixture members must be a list")
    member_identities = [member.get("identity") for member in members]
    expected_member_identities = identity["member_identities"]
    require(
        isinstance(expected_member_identities, list),
        "fixture member identities must be a list",
    )
    if (
        any(not isinstance(member_identity, str) for member_identity in member_identities)
        or sorted(member_identities) != sorted(expected_member_identities)
    ):
        return "UNKNOWN", "stale"
    if case.get("json_evidence", True) is not True:
        return "UNKNOWN", "state_unknown"
    if case.get("deadline_reached") and case.get("status") != "done":
        return "UNKNOWN", "timed_out"
    if case.get("status") == "failed":
        return "UNKNOWN", "failed"

    member_statuses = [member.get("status") for member in members]
    if "failed" in member_statuses:
        return "UNKNOWN", "failed"
    if "skipped" in member_statuses:
        return "UNKNOWN", "member_skipped"
    if any(status != "done" for status in member_statuses):
        return "UNKNOWN", "member_incomplete"
    if case.get("status") != "done":
        return "UNKNOWN", "member_incomplete"
    if case.get("verdict") == "findings":
        return "FAIL", "findings"
    if case.get("verdict") == "pass":
        return "PASS", "passed"
    return "UNKNOWN", "state_unknown"


def observation_calls(
    *, declared: bool, reusable_jobs: int, claim: str, jobs_after_claim: int
) -> tuple[tuple[str, str], list[str]]:
    if not declared:
        return ("UNAVAILABLE", "omitted"), []
    calls = ["initial_query"]
    if reusable_jobs == 1:
        return ("UNKNOWN", "pending_reuse"), calls
    if reusable_jobs > 1:
        return ("UNKNOWN", "state_unknown"), calls
    calls.append("state_claim")
    if claim != "winner":
        reason = "claim_lost" if claim == "loser" else "state_unknown"
        return ("UNKNOWN", reason), calls
    calls.append("requery")
    if jobs_after_claim == 1:
        return ("UNKNOWN", "pending_reuse"), calls
    if jobs_after_claim > 1:
        return ("UNKNOWN", "state_unknown"), calls
    calls.append("enqueue")
    return ("UNKNOWN", "pending"), calls


def panel_result(panel: str, daemon_support: bool) -> tuple[str, str]:
    if panel != "none" and not daemon_support:
        return "UNAVAILABLE", "unsupported"
    return "UNKNOWN", "pending"


def cost_receipt(total: float, jobs_with_cost: int, jobs_total: int, complete: bool) -> dict[str, object]:
    return {
        "approximate_total": total,
        "jobs_with_cost": jobs_with_cost,
        "jobs_total": jobs_total,
        "complete": complete,
        "exact_ceiling": None,
    }


def repository_config_complete(text: str) -> bool:
    return all(
        field in text
        for field in [
            "review_agent =",
            "review_model =",
            "review_reasoning =",
            "review_min_severity =",
        ]
    )


def request_allowed(kind: str, completed_for_kind: int) -> bool:
    return kind in {"initial", "confirmation"} and completed_for_kind < 1


def authority_errors(text: str) -> list[str]:
    normalized = " ".join(text.split())
    required = [
        "RoboRev is observation, not authority",
        "all flow to one fresh-context validation decision",
        "cannot push, create a Draft, post to GitHub, mark Ready, merge",
        "Captain keeps delivery, scope, irreversibility, and accepted-red authority",
    ]
    return [phrase for phrase in required if phrase not in normalized]


def resolve_spacedock() -> Path | None:
    configured = os.environ.get("SPACEDOCK_BIN")
    located = configured or shutil.which("spacedock")
    if not located:
        return None
    candidate = Path(located).expanduser()
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        return None
    return candidate.resolve()


def workflow_readme() -> str:
    return """---
commissioned-by: spacedock@0.26.0
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
state: .spacedock-state
trunk: main
stages:
  defaults:
    worktree: false
  states:
    - name: backlog
      initial: true
    - name: implementation
      worktree: true
    - name: validation
      worktree: true
---

# Fixture workflow
"""


def task_text() -> str:
    return """---
id: fixture-task
title: "Fixture task"
status: implementation
source: contract-test
product: kc-dev-flow
sprint: S2
started: 2026-08-14T00:00:00Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane: main
---

# Fixture task

## Implementation evidence
"""


def configure_repository(repo: Path) -> None:
    git(repo, "config", "user.name", "RoboRev Contract")
    git(repo, "config", "user.email", "roborev-contract@example.test")


def seed_repository(root: Path) -> tuple[Path, Path, Path, Path]:
    root = root.resolve()
    remote = root / "remote.git"
    repo = root / "repo"
    state_seed = root / "state-seed"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
    configure_repository(repo)
    git(repo, "remote", "add", "origin", str(remote))
    (repo / ".gitignore").write_text("docs/dev/.spacedock-state/\n", encoding="utf-8")
    workflow = repo / "docs/dev"
    workflow.mkdir(parents=True)
    (workflow / "README.md").write_text(workflow_readme(), encoding="utf-8")
    git(repo, "add", ".gitignore", "docs/dev/README.md")
    git(repo, "commit", "-m", "seed product")
    git(repo, "push", "-u", "origin", "main")

    git(repo, "worktree", "add", "--detach", str(state_seed), "HEAD")
    git(state_seed, "switch", "--orphan", STATE_BRANCH)
    git(state_seed, "rm", "-rf", ".", check=False)
    (state_seed / ".gitignore").unlink(missing_ok=True)
    shutil.rmtree(state_seed / "docs", ignore_errors=True)
    (state_seed / "task.md").write_text(task_text(), encoding="utf-8")
    git(state_seed, "add", "task.md")
    git(state_seed, "commit", "-m", "seed state")
    git(state_seed, "push", "-u", "origin", STATE_BRANCH)
    git(repo, "worktree", "remove", str(state_seed))

    holder = workflow / ".spacedock-state"
    git(repo, "worktree", "add", str(holder), STATE_BRANCH)
    git(holder, "branch", "--set-upstream-to", f"origin/{STATE_BRANCH}")
    return remote, repo, workflow, holder


def clone_repository(remote: Path, destination: Path, *, with_holder: bool = True) -> tuple[Path, Path, Path | None]:
    destination = destination.parent.resolve() / destination.name
    subprocess.run(
        ["git", "clone", "--branch", "main", str(remote), str(destination)],
        check=True,
        capture_output=True,
    )
    configure_repository(destination)
    workflow = destination / "docs/dev"
    if not with_holder:
        return destination, workflow, None
    holder = workflow / ".spacedock-state"
    git(
        destination,
        "worktree",
        "add",
        "-b",
        STATE_BRANCH,
        str(holder),
        f"origin/{STATE_BRANCH}",
    )
    git(holder, "branch", "--set-upstream-to", f"origin/{STATE_BRANCH}")
    return destination, workflow, holder


def claim_text(identity: str, claimant: str, state_revision: str) -> str:
    return (
        "\n### RoboRev observation claim\n\n"
        f"- identity: `{identity}`\n"
        f"- claimant: `{claimant}`\n"
        f"- observed-state-revision: `{state_revision}`\n"
        "- state: `claimed`\n"
    )


@dataclass(frozen=True)
class ClaimPreparation:
    repository: Path
    workflow: Path
    holder: Path
    slug: str
    identity: str
    claimant: str
    state_revision: str
    entity_path: Path


def prepare_supported_claim(
    repository: Path,
    workflow: Path,
    identity: str,
    claimant: str,
    spacedock_binary: Path | None,
) -> tuple[tuple[str, str], ClaimPreparation | None]:
    if spacedock_binary is None or not STATE_PREREQ.is_file():
        return ("UNAVAILABLE", "unavailable"), None
    prerequisite = subprocess.run(
        [str(STATE_PREREQ), str(workflow)],
        cwd=repository,
        text=True,
        capture_output=True,
        check=False,
    )
    if prerequisite.returncode != 0:
        return ("UNKNOWN", "state_unknown"), None

    holder = workflow / ".spacedock-state"
    state_revision = git(holder, "rev-parse", "HEAD^{commit}").stdout.strip()
    entity_path = holder / "task.md"
    current = entity_path.read_text(encoding="utf-8")
    if f"- identity: `{identity}`" in current:
        return ("UNKNOWN", "claim_lost"), None
    entity_path.write_text(
        current + claim_text(identity, claimant, state_revision),
        encoding="utf-8",
    )
    changed_paths = [line[3:] for line in git(holder, "status", "--porcelain").stdout.splitlines()]
    if changed_paths != ["task.md"]:
        return ("UNKNOWN", "state_unknown"), None
    return (
        ("UNKNOWN", "pending_claim"),
        ClaimPreparation(
            repository=repository,
            workflow=workflow,
            holder=holder,
            slug="task",
            identity=identity,
            claimant=claimant,
            state_revision=state_revision,
            entity_path=entity_path,
        ),
    )


def validate_prepared_claim(preparation: ClaimPreparation | None) -> tuple[str, str]:
    if preparation is None:
        return "UNKNOWN", "state_unknown"
    if git(preparation.holder, "rev-parse", "HEAD^{commit}").stdout.strip() != preparation.state_revision:
        return "UNKNOWN", "stale"
    changed_paths = [
        line[3:]
        for line in git(preparation.holder, "status", "--porcelain").stdout.splitlines()
    ]
    if changed_paths != [preparation.entity_path.name]:
        return "UNKNOWN", "state_unknown"
    git(preparation.holder, "fetch", "--no-tags", "origin", STATE_BRANCH)
    remote_revision = git(preparation.holder, "rev-parse", "FETCH_HEAD^{commit}").stdout.strip()
    if remote_revision != preparation.state_revision:
        return "UNKNOWN", "stale"
    current = preparation.entity_path.read_text(encoding="utf-8")
    if (
        current.count(f"- identity: `{preparation.identity}`") != 1
        or f"- claimant: `{preparation.claimant}`" not in current
    ):
        return "UNKNOWN", "state_unknown"
    return "UNKNOWN", "pending_claim"


def reread_remote_claim(preparation: ClaimPreparation) -> str:
    git(preparation.holder, "fetch", "--no-tags", "origin", STATE_BRANCH)
    return git(preparation.holder, "show", f"FETCH_HEAD:{preparation.slug}.md").stdout


def commit_supported_claim(
    preparation: ClaimPreparation | None,
    spacedock_binary: Path | None,
    barrier: Barrier | None = None,
) -> tuple[str, str]:
    if spacedock_binary is None:
        return "UNAVAILABLE", "unavailable"
    validated = validate_prepared_claim(preparation)
    if validated != ("UNKNOWN", "pending_claim") or preparation is None:
        return validated
    if barrier is not None:
        barrier.wait(timeout=10)
    committed = subprocess.run(
        [
            str(spacedock_binary),
            "state",
            "commit",
            "--workflow-dir",
            str(preparation.workflow),
            preparation.slug,
        ],
        cwd=preparation.repository,
        text=True,
        capture_output=True,
        check=False,
    )
    remote_state = reread_remote_claim(preparation)
    if committed.returncode != 0:
        if (
            remote_state.count(f"- identity: `{preparation.identity}`") == 1
            and f"- claimant: `{preparation.claimant}`" not in remote_state
        ):
            return "UNKNOWN", "claim_lost"
        return "UNKNOWN", "state_unknown"
    if (
        remote_state.count(f"- identity: `{preparation.identity}`") == 1
        and f"- claimant: `{preparation.claimant}`" in remote_state
    ):
        return "UNKNOWN", "pending"
    return "UNKNOWN", "state_unknown"


def assert_independent_clone_single_flight(spacedock_binary: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="roborev-claim-independent-") as tmp:
        remote, _, _, _ = seed_repository(Path(tmp))
        first_repo, first_workflow, _ = clone_repository(remote, Path(tmp) / "first")
        second_repo, second_workflow, _ = clone_repository(remote, Path(tmp) / "second")
        identity = "complete-exact-input-identity"
        first_result, first_preparation = prepare_supported_claim(
            first_repo, first_workflow, identity, "first", spacedock_binary
        )
        second_result, second_preparation = prepare_supported_claim(
            second_repo, second_workflow, identity, "second", spacedock_binary
        )
        require(first_result[1] == "pending_claim", f"first independent claimant did not prepare: {first_result}")
        require(second_result[1] == "pending_claim", f"second independent claimant did not prepare: {second_result}")
        require(first_preparation is not None and second_preparation is not None, "claim preparation disappeared")

        barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as executor:
            first_future = executor.submit(
                commit_supported_claim, first_preparation, spacedock_binary, barrier
            )
            second_future = executor.submit(
                commit_supported_claim, second_preparation, spacedock_binary, barrier
            )
            results = {"first": first_future.result(), "second": second_future.result()}
        require(
            [result[1] for result in results.values()].count("pending") == 1,
            f"supported independent transaction produced other than one winner: {results}",
        )
        winner = next(claimant for claimant, result in results.items() if result[1] == "pending")
        loser = "second" if winner == "first" else "first"
        require(results[loser][1] == "claim_lost", f"independent loser was not claim_lost: {results}")

        first_remote = reread_remote_claim(first_preparation)
        second_remote = reread_remote_claim(second_preparation)
        require(first_remote == second_remote, "independent clones did not agree after post-push re-read")
        require(first_remote.count(f"- identity: `{identity}`") == 1, "remote state does not contain one claim")
        require(f"- claimant: `{winner}`" in first_remote, "remote claimant is not the transaction winner")


def assert_shared_parent_single_flight(spacedock_binary: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="roborev-claim-shared-") as tmp:
        _, repo, workflow, holder = seed_repository(Path(tmp))
        identity = "complete-exact-input-identity"
        first_result, first_preparation = prepare_supported_claim(
            repo, workflow, identity, "first", spacedock_binary
        )
        require(first_result[1] == "pending_claim" and first_preparation is not None, "first shared claim refused")
        require(
            commit_supported_claim(first_preparation, spacedock_binary)[1] == "pending",
            "first shared claim did not commit through Spacedock",
        )
        second_result, second_preparation = prepare_supported_claim(
            repo, workflow, identity, "second", spacedock_binary
        )
        require(second_result == ("UNKNOWN", "claim_lost"), "shared parent accepted duplicate identity")
        require(second_preparation is None, "shared-parent loser retained a claim preparation")
        remote_state = reread_remote_claim(first_preparation)
        require(remote_state.count(f"- identity: `{identity}`") == 1, "shared remote has duplicate claims")
        require("- claimant: `first`" in remote_state, "shared-parent claimant changed")
        require(not git(holder, "status", "--porcelain").stdout, "shared holder was not clean after durability")


def assert_state_boundary_refusals(spacedock_binary: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="roborev-state-boundary-") as tmp:
        root = Path(tmp)
        remote, repo, workflow, holder = seed_repository(root / "missing-tool")
        missing_result, missing_preparation = prepare_supported_claim(
            repo, workflow, "missing-tool", "observer", None
        )
        require(missing_result == ("UNAVAILABLE", "unavailable"), "missing Spacedock path was not non-green")
        require(missing_preparation is None and not git(holder, "status", "--porcelain").stdout, "missing tool mutated state")

        nonholder_repo, nonholder_workflow, _ = clone_repository(
            remote, root / "nonholder", with_holder=False
        )
        nonholder_result, _ = prepare_supported_claim(
            nonholder_repo, nonholder_workflow, "nonholder", "observer", spacedock_binary
        )
        require(nonholder_result == ("UNKNOWN", "state_unknown"), "non-holder could prepare a claim")

        _, dirty_repo, dirty_workflow, dirty_holder = seed_repository(root / "dirty")
        (dirty_holder / "unrelated.md").write_text("dirty\n", encoding="utf-8")
        dirty_result, _ = prepare_supported_claim(
            dirty_repo, dirty_workflow, "dirty", "observer", spacedock_binary
        )
        require(dirty_result == ("UNKNOWN", "state_unknown"), "dirty holder could prepare a claim")

        _, ahead_repo, ahead_workflow, ahead_holder = seed_repository(root / "ahead")
        git(ahead_holder, "commit", "--allow-empty", "-m", "local ahead")
        ahead_result, _ = prepare_supported_claim(
            ahead_repo, ahead_workflow, "ahead", "observer", spacedock_binary
        )
        require(ahead_result == ("UNKNOWN", "state_unknown"), "ahead holder could prepare a claim")

        divergent_remote, divergent_repo, divergent_workflow, divergent_holder = seed_repository(
            root / "divergent"
        )
        _, _, divergent_peer_holder = clone_repository(
            divergent_remote, root / "divergent-peer"
        )
        require(divergent_peer_holder is not None, "divergent peer has no holder")
        git(divergent_holder, "commit", "--allow-empty", "-m", "local side")
        git(divergent_peer_holder, "commit", "--allow-empty", "-m", "remote side")
        git(divergent_peer_holder, "push", "origin", STATE_BRANCH)
        divergent_result, _ = prepare_supported_claim(
            divergent_repo, divergent_workflow, "divergent", "observer", spacedock_binary
        )
        require(divergent_result == ("UNKNOWN", "state_unknown"), "divergent holder could prepare a claim")

        stale_remote, stale_repo, stale_workflow, _ = seed_repository(root / "stale")
        stale_result, stale_preparation = prepare_supported_claim(
            stale_repo, stale_workflow, "stale-observer", "observer", spacedock_binary
        )
        require(stale_result[1] == "pending_claim" and stale_preparation is not None, "stale fixture did not prepare")
        peer_repo, peer_workflow, _ = clone_repository(stale_remote, root / "stale-peer")
        peer_result, peer_preparation = prepare_supported_claim(
            peer_repo, peer_workflow, "peer-advance", "peer", spacedock_binary
        )
        require(peer_result[1] == "pending_claim" and peer_preparation is not None, "peer did not prepare")
        require(commit_supported_claim(peer_preparation, spacedock_binary)[1] == "pending", "peer did not advance state")
        require(
            commit_supported_claim(stale_preparation, spacedock_binary) == ("UNKNOWN", "stale"),
            "stale observed state revision could earn a claim winner",
        )
        require(
            commit_supported_claim(None, spacedock_binary) == ("UNKNOWN", "state_unknown"),
            "bypassed prerequisite could reach the supported transaction",
        )


fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
identity = fixture["identity"]
required_stale_mutations = {
    "stale_repository",
    "stale_base",
    "stale_tip",
    "stale_configuration",
    "stale_provider_version",
    "stale_json_contract",
    "stale_agent",
    "stale_model",
    "stale_reasoning",
    "stale_minimum_severity",
    "stale_panel",
    "stale_member_identity",
    "stale_member_population_missing",
    "stale_member_population_extra",
}
fixture_case_names = {case["name"] for case in fixture["cases"]}
require(
    required_stale_mutations <= fixture_case_names,
    "fixture lost exact-input mutations: "
    + ", ".join(sorted(required_stale_mutations - fixture_case_names)),
)
for case in fixture["cases"]:
    actual = classify(case, identity)
    expected = tuple(case["expected"])
    require(actual == expected, f"{case['name']} mapped to {actual}, expected {expected}")

omitted_result, omitted_calls = observation_calls(
    declared=False, reusable_jobs=0, claim="winner", jobs_after_claim=0
)
require(omitted_calls == [], "omitted control performed provider or state work")
require(omitted_result == ("UNAVAILABLE", "omitted"), "omitted control did not stay inactive")

reuse_result, reuse_calls = observation_calls(
    declared=True, reusable_jobs=1, claim="winner", jobs_after_claim=0
)
require(reuse_result[1] == "pending_reuse", "matching evidence was not reused")
require(reuse_calls == ["initial_query"], "reuse path claimed or enqueued")

loser_result, loser_calls = observation_calls(
    declared=True, reusable_jobs=0, claim="loser", jobs_after_claim=0
)
require(loser_result == ("UNKNOWN", "claim_lost"), "claim loser was not conservative")
require("requery" not in loser_calls and "enqueue" not in loser_calls, "claim loser reached provider")

winner_result, winner_calls = observation_calls(
    declared=True, reusable_jobs=0, claim="winner", jobs_after_claim=0
)
require(winner_result[1] == "pending", "claim winner did not reach bounded request")
require(winner_calls.count("enqueue") == 1, "claim winner did not enqueue once")

require(panel_result("none", daemon_support=False)[1] == "pending", "single reviewer incorrectly requires panel support")
require(
    panel_result("branch_final", daemon_support=False) == ("UNAVAILABLE", "unsupported"),
    "named panel silently downgraded without daemon support",
)

incomplete_cost = cost_receipt(12.38, 4, 22, False)
require(incomplete_cost["complete"] is False, "incomplete cost coverage was hidden")
require(incomplete_cost["exact_ceiling"] is None, "approximate cost became an exact ceiling")
require(request_allowed("initial", 0), "initial request allowance is missing")
require(not request_allowed("initial", 1), "second initial request survived the cap")
require(request_allowed("confirmation", 0), "repair confirmation allowance is missing")
require(not request_allowed("confirmation", 1), "second repair confirmation survived the cap")

reference = PLUGIN / "references/roborev-implementation-exit.md"
adopted = ROOT / "docs/dev/runbooks/roborev-implementation-exit.md"
require(reference.is_file(), "missing packaged provider reference")
require(adopted.is_file(), "missing self-adopted provider runbook")
require(reference.read_bytes() == adopted.read_bytes(), "package and self-adopted provider contracts differ")

reference_text = reference.read_text(encoding="utf-8")
normalized_reference = " ".join(reference_text.split())
for phrase in [
    "Correlation precedence",
    "stale` wins over `member_incomplete",
    "scripts/dev-flow-state-prereq.sh",
    "registered state holder",
    "spacedock state commit",
    "supported Spacedock state transaction",
    "post-push re-read",
    "no provider re-query, enqueue, or retry",
    "one repair confirmation",
    "RoboRev is observation, not authority",
]:
    require(phrase in normalized_reference, f"provider reference is missing: {phrase}")
require(not authority_errors(reference_text), "provider reference weakens authority: " + ", ".join(authority_errors(reference_text)))
for phrase in [
    "RoboRev is observation, not authority",
    "all flow to one fresh-context validation decision",
    "cannot push, create a Draft, post to GitHub, mark Ready, merge",
]:
    mutant = reference_text.replace(phrase, "provider decides", 1)
    require(authority_errors(mutant), f"authority mutant survived: {phrase}")

continue_skill = (PLUGIN / "skills/continue-dev-flow/SKILL.md").read_text(encoding="utf-8")
normalized_continue_skill = " ".join(continue_skill.split())
require(
    "references/roborev-implementation-exit.md" in normalized_continue_skill,
    "continue skill has no conditional RoboRev locator",
)
require(
    "performs no RoboRev probe or invocation" in normalized_continue_skill,
    "omitted declaration is not a zero-provider-work path",
)

repo_config = (ROOT / ".roborev.toml").read_text(encoding="utf-8")
for phrase in [
    'review_agent = "codex"',
    'review_model = "gpt-5.6-terra"',
    'review_reasoning = "thorough"',
    'review_min_severity = "medium"',
]:
    require(phrase in repo_config, f"repository config is missing: {phrase}")
for forbidden in ["default_panel", "hook_review_panel", "[[hooks]]"]:
    require(forbidden not in repo_config, f"repository config enables unapproved automation: {forbidden}")

local_profile = (ROOT / "docs/dev/README.md").read_text(encoding="utf-8")
for phrase in [
    "`review_convergence` in `observe` mode at implementation exit",
    "provider RoboRev",
    "`.roborev.toml`",
    "`panel: none`",
    "one exact-tip request",
    "one changed-tip repair confirmation",
]:
    require(phrase in local_profile, f"Local Profile is missing ownership/cap: {phrase}")
for field in ["review_agent", "review_model", "review_reasoning", "review_min_severity"]:
    mutated = "\n".join(line for line in repo_config.splitlines() if not line.startswith(f"{field} ="))
    require(
        not repository_config_complete(mutated),
        "ambient/global configuration could satisfy a missing repository field",
    )

spacedock_binary = resolve_spacedock()
missing_result, missing_preparation = prepare_supported_claim(
    ROOT,
    ROOT / "docs/dev",
    "missing-spacedock",
    "observer",
    None,
)
require(missing_result == ("UNAVAILABLE", "unavailable"), "missing Spacedock path was not non-green")
require(missing_preparation is None, "missing Spacedock path created a claim preparation")
if spacedock_binary is not None:
    assert_independent_clone_single_flight(spacedock_binary)
    assert_shared_parent_single_flight(spacedock_binary)
    assert_state_boundary_refusals(spacedock_binary)

print("roborev implementation-exit contract: PASS")
