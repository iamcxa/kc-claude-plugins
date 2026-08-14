#!/usr/bin/env python3
"""Executable contract for the optional RoboRev implementation-exit sensor."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "kc-dev-flow"
FIXTURE = ROOT / "scripts/fixtures/roborev-implementation-exit/outcomes.json"
STATE_BRANCH = "spacedock-state/dev"


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


def classify(case: dict[str, object], identity: dict[str, str]) -> tuple[str, str]:
    capability = case.get("capability")
    if capability in {"unavailable", "unsupported", "skipped"}:
        return "UNAVAILABLE", str(capability)

    # Correlation precedes lifecycle interpretation. A stale exact-input binding
    # cannot be promoted to member_incomplete or to retained findings.
    for field in ("repository", "base", "tip", "configuration"):
        if case.get(field, identity[field]) != identity[field]:
            return "UNKNOWN", "stale"
    if case.get("json_evidence", True) is not True:
        return "UNKNOWN", "state_unknown"
    if case.get("deadline_reached") and case.get("status") != "done":
        return "UNKNOWN", "timed_out"
    if case.get("status") == "failed":
        return "UNKNOWN", "failed"

    members = case.get("members", [])
    require(isinstance(members, list), "fixture members must be a list")
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


def seed_remote(root: Path) -> tuple[Path, Path]:
    remote = root / "state.git"
    seed = root / "seed"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    subprocess.run(["git", "clone", str(remote), str(seed)], check=True, capture_output=True)
    git(seed, "switch", "-c", STATE_BRANCH)
    (seed / "task.md").write_text("# Task\n\n## Implementation evidence\n", encoding="utf-8")
    git(seed, "add", "task.md")
    git(seed, "-c", "user.name=Seed", "-c", "user.email=seed@example.test", "commit", "-m", "seed state")
    git(seed, "push", "-u", "origin", STATE_BRANCH)
    return remote, seed


def clone_state(remote: Path, destination: Path) -> Path:
    subprocess.run(
        ["git", "clone", "--branch", STATE_BRANCH, str(remote), str(destination)],
        check=True,
        capture_output=True,
    )
    return destination


def claim_text(identity: str, owner: str) -> str:
    return (
        "\n### RoboRev observation claim\n\n"
        f"- identity: `{identity}`\n"
        f"- owner: `{owner}`\n"
        "- state: `claimed`\n"
    )


def prepare_claim(clone: Path, identity: str, owner: str) -> bool:
    task = clone / "task.md"
    current = task.read_text(encoding="utf-8")
    if f"- identity: `{identity}`" in current:
        return False
    task.write_text(current + claim_text(identity, owner), encoding="utf-8")
    git(clone, "add", "task.md")
    git(
        clone,
        "-c",
        f"user.name={owner}",
        "-c",
        f"user.email={owner}@example.test",
        "commit",
        "-m",
        f"claim {identity} for {owner}",
    )
    return True


def push_claim(clone: Path) -> bool:
    return git(clone, "push", "origin", STATE_BRANCH, check=False).returncode == 0


def reread_remote_claim(clone: Path) -> str:
    git(clone, "fetch", "origin", STATE_BRANCH)
    return git(clone, "show", f"origin/{STATE_BRANCH}:task.md").stdout


def assert_independent_clone_single_flight() -> None:
    with tempfile.TemporaryDirectory(prefix="roborev-claim-independent-") as tmp:
        remote, _ = seed_remote(Path(tmp))
        first = clone_state(remote, Path(tmp) / "first")
        second = clone_state(remote, Path(tmp) / "second")
        identity = "repo-base-tip-config"
        require(prepare_claim(first, identity, "first"), "first independent claimant did not prepare")
        require(prepare_claim(second, identity, "second"), "second independent claimant did not observe the same initial miss")

        first_won = push_claim(first)
        second_won = push_claim(second)
        require([first_won, second_won].count(True) == 1, "independent clones produced other than one push winner")

        provider_calls = {"first": [], "second": []}
        winner = "first" if first_won else "second"
        loser = "second" if first_won else "first"
        provider_calls[winner].extend(["requery", "enqueue"])
        first_remote = reread_remote_claim(first)
        second_remote = reread_remote_claim(second)
        require(first_remote == second_remote, "independent clones did not agree after post-push re-read")
        require(first_remote.count(f"- identity: `{identity}`") == 1, "remote state does not contain exactly one claim")
        require(f"- owner: `{winner}`" in first_remote, "remote claim owner is not the push winner")
        require(provider_calls[loser] == [], "independent-clone loser reached provider re-query or enqueue")


def assert_shared_parent_single_flight() -> None:
    with tempfile.TemporaryDirectory(prefix="roborev-claim-shared-") as tmp:
        remote, _ = seed_remote(Path(tmp))
        shared = clone_state(remote, Path(tmp) / "shared")
        identity = "repo-base-tip-config"
        provider_calls = {"first": [], "second": []}

        require(prepare_claim(shared, identity, "first"), "first shared-parent claim was refused")
        require(push_claim(shared), "first shared-parent claim did not push")
        provider_calls["first"].extend(["requery", "enqueue"])
        require(not prepare_claim(shared, identity, "second"), "shared parent accepted a duplicate identity")

        remote_state = reread_remote_claim(shared)
        require(remote_state.count(f"- identity: `{identity}`") == 1, "shared-parent remote state does not contain one claim")
        require("- owner: `first`" in remote_state, "shared-parent claim owner changed")
        require(provider_calls["second"] == [], "shared-parent loser reached provider re-query or enqueue")


fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
identity = fixture["identity"]
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

assert_independent_clone_single_flight()
assert_shared_parent_single_flight()

print("roborev implementation-exit contract: PASS")
