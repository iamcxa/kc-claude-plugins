#!/usr/bin/env python3
"""Behavior and packaging contract for kc-ship-flow."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "kc-ship-flow"
SCRIPTS = PLUGIN / "scripts"
FIXTURES = SCRIPTS / "fixtures"

if sys.argv[1:]:
    raise SystemExit("usage: contract-test.py")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"kc-ship-flow contract: {message}")


def run(command: list[str], label: str) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    require(
        result.returncode == 0,
        f"{label} failed:\n{result.stdout}{result.stderr}",
    )


STATIONS = [
    "accept-evidence.sh",
    "without-it.sh",
    "intent.sh",
    "holder.sh",
    "fenced-dispatch.sh",
    "worker-transcript.sh",
    "open-pr.sh",
    "disposition.py",
    "e2e-cli.sh",
    "e2e-gate.py",
    "parse-execute-external.py",
    "uat-doc.py",
    "notify.sh",
    "dev-debrief.py",
    "ship-debrief.py",
    "ci-covers.sh",
]
for station in STATIONS:
    require((SCRIPTS / station).is_file(), f"missing station script: {station}")
    print(f"kc-ship-flow contract: station present: {station}")

STATION_TESTS = [
    ("uat-doc.test.py", [sys.executable, str(SCRIPTS / "uat-doc.test.py")]),
    ("notify.test.sh", ["bash", str(SCRIPTS / "notify.test.sh")]),
    ("dev-debrief.test.py", [sys.executable, str(SCRIPTS / "dev-debrief.test.py")]),
    ("ship-debrief.test.py", [sys.executable, str(SCRIPTS / "ship-debrief.test.py")]),
    ("pin.test.py", [sys.executable, str(SCRIPTS / "pin.test.py")]),
]
for test_name, test_command in STATION_TESTS:
    require((SCRIPTS / test_name).is_file(), f"missing station test: {test_name}")
    run(test_command, f"kc-ship-flow {test_name}")

run(["bash", str(SCRIPTS / "merge-station.test.sh")], "kc-ship-flow merge-station.test.sh")
run(["bash", str(SCRIPTS / "ci-covers.test.sh")], "kc-ship-flow ci-covers.test.sh")

# --- ci-covers.sh: DEV-149's two named fixtures, registered directly (not
# only through ci-covers.test.sh) -- a workflow naming the check but never
# entering the package must be refused, and one that enters it must pass.
ci_covers_script = SCRIPTS / "ci-covers.sh"
ci_covers_uncovered = FIXTURES / "monorepo-uncovered"
ci_covers_covered = FIXTURES / "monorepo-covered"
require(ci_covers_uncovered.is_dir(), f"missing fixture: {ci_covers_uncovered}")
require(ci_covers_covered.is_dir(), f"missing fixture: {ci_covers_covered}")

ci_covers_uncovered_result = subprocess.run(
    ["bash", str(ci_covers_script), str(ci_covers_uncovered), "experiments/island", "pr-test"],
    capture_output=True, text=True,
)
require(
    ci_covers_uncovered_result.returncode == 1
    and "experiments/island not run by pr-test" in ci_covers_uncovered_result.stderr,
    "ci-covers.sh did not refuse the monorepo-uncovered fixture (check named, package never "
    f"entered): exit={ci_covers_uncovered_result.returncode} stderr={ci_covers_uncovered_result.stderr!r}",
)

ci_covers_covered_result = subprocess.run(
    ["bash", str(ci_covers_script), str(ci_covers_covered), "experiments/island", "pr-test"],
    capture_output=True, text=True,
)
require(
    ci_covers_covered_result.returncode == 0,
    "ci-covers.sh did not accept the monorepo-covered fixture (check named, package entered via "
    f"working-directory:): exit={ci_covers_covered_result.returncode} stderr={ci_covers_covered_result.stderr!r}",
)

for py_station in [
    "disposition.py",
    "e2e-gate.py",
    "parse-execute-external.py",
    "uat-doc.py",
    "dev-debrief.py",
    "ship-debrief.py",
]:
    run([sys.executable, "-m", "py_compile", str(SCRIPTS / py_station)], f"{py_station} compile")

CLOSE_RECEIPT_SCHEMA = PLUGIN / "schemas" / "kc-ship-close-receipt.v1.schema.json"
require(CLOSE_RECEIPT_SCHEMA.is_file(), f"missing {CLOSE_RECEIPT_SCHEMA}")

with tempfile.TemporaryDirectory(prefix="kc-ship-flow-intent-lock-") as intent_lock_root_name:
    # DEV-93: a split-root state checkout (`git worktree add`) has `.git` as a FILE, not a
    # directory; a lock path hardcoded as `<state>/.git/...` can never `mkdir` there. This
    # case fails on the pre-fix script (SystemExit-worthy `lock timeout`, exit 6) and only
    # passes once the lock path is resolved through `git rev-parse --git-dir`.
    intent_lock_root = Path(intent_lock_root_name)
    intent_lock_origin = intent_lock_root / "origin.git"
    intent_lock_seed = intent_lock_root / "seed"
    intent_lock_bare = intent_lock_root / "bare-clone"
    intent_lock_state_wt = intent_lock_root / "state-wt"
    git_user = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.test"]
    subprocess.run(["git", "init", "-q", "--bare", str(intent_lock_origin)], check=True, capture_output=True)
    subprocess.run(["git", "clone", "-q", str(intent_lock_origin), str(intent_lock_seed)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(intent_lock_seed), *git_user, "checkout", "-q", "-b", "spacedock-state/dev"], check=True, capture_output=True)
    (intent_lock_seed / "_holder.json").write_text(json.dumps({"writer": 1, "holder": "laptop", "at": "x"}), encoding="utf-8")
    subprocess.run(["git", "-C", str(intent_lock_seed), "add", "_holder.json"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(intent_lock_seed), *git_user, "commit", "-q", "-m", "seed holder"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(intent_lock_seed), "push", "-q", "origin", "spacedock-state/dev"], check=True, capture_output=True)
    subprocess.run(["git", "clone", "-q", str(intent_lock_origin), str(intent_lock_bare)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(intent_lock_bare), "worktree", "add", "-q", str(intent_lock_state_wt), "spacedock-state/dev"],
        check=True, capture_output=True,
    )
    require((intent_lock_state_wt / ".git").is_file(), "DEV-93 fixture: worktree .git is not a file")

    def run_intent_commit(script: Path, claim: str) -> subprocess.CompletedProcess:
        env = dict(os.environ, SHIP_LOCK_STALE_S="3")
        return subprocess.run(
            [
                str(script), "commit", str(intent_lock_state_wt), "laptop", "1", claim,
                "0123456789abcdef0123456789abcdef",
                "11111111-1111-1111-1111-111111111111",
                "d98f40b5e2080cb884facf1734fc66052eff998",
                hashlib.sha256(claim.encode()).hexdigest(),
            ],
            capture_output=True, text=True, env=env, timeout=60,
        )

    fixed_result = run_intent_commit(SCRIPTS / "intent.sh", "dev-93-contract-case")
    require(
        fixed_result.returncode == 0,
        "intent.sh commit did not succeed on a worktree-style state checkout (`.git` is a file): "
        f"exit={fixed_result.returncode} stdout={fixed_result.stdout!r} stderr={fixed_result.stderr!r}",
    )
    intent_lock_git_dir_raw = subprocess.run(
        ["git", "-C", str(intent_lock_state_wt), "rev-parse", "--git-dir"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    intent_lock_git_dir = Path(intent_lock_git_dir_raw)
    if not intent_lock_git_dir.is_absolute():
        intent_lock_git_dir = intent_lock_state_wt / intent_lock_git_dir
    require(
        not list(intent_lock_git_dir.glob("ship-lock.d*")),
        "intent.sh left lock residue under the worktree's git dir",
    )

e2e_gate = SCRIPTS / "e2e-gate.py"
e2e_gate_fixtures = FIXTURES / "e2e-gate"


def run_e2e_gate(
    plan_fixture: str,
    close_fixture: str,
    *,
    offline: bool = False,
    close_receipt_override: dict | None = None,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if offline:
        env["https_proxy"] = "http://127.0.0.1:9"
        env["http_proxy"] = "http://127.0.0.1:9"
    close_path = e2e_gate_fixtures / close_fixture
    override_path: Path | None = None
    if close_receipt_override is not None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(close_receipt_override, handle)
            override_path = Path(handle.name)
        close_path = override_path
    try:
        return subprocess.run(
            [sys.executable, str(e2e_gate), str(e2e_gate_fixtures / plan_fixture), str(close_path)],
            cwd=ROOT, text=True, capture_output=True, env=env, timeout=30,
        )
    finally:
        if override_path is not None:
            override_path.unlink(missing_ok=True)


# The committed ac2 fixture carries a placeholder candidate (a real SHA
# would go unreachable under a shallow CI checkout); this is the only
# gate scenario that runs e2e-cli.sh, so it needs a commit that both
# resolves and contains the fixtures its flow's own steps reference --
# this checkout's own HEAD always satisfies both.
current_head = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True,
).stdout.strip()
ac2_close_receipt = json.loads((e2e_gate_fixtures / "close-receipt.ac2.json").read_text(encoding="utf-8"))
ac2_issue_key = next(iter(ac2_close_receipt["issues"]))
ac2_close_receipt["issues"][ac2_issue_key]["candidate"] = current_head

e2e_gate_ac2 = run_e2e_gate(
    "plan-receipt.ac2.json", "close-receipt.ac2.json", offline=True, close_receipt_override=ac2_close_receipt,
)
require(
    e2e_gate_ac2.returncode == 0 and re.search(r"CLI e2e:.*at [0-9a-f]{40},", e2e_gate_ac2.stdout),
    f"e2e-gate ac2 (run branch) did not exit 0 with a resolved-SHA report line: "
    f"exit {e2e_gate_ac2.returncode}, stdout {e2e_gate_ac2.stdout!r}, stderr {e2e_gate_ac2.stderr!r}",
)

e2e_gate_ac3 = run_e2e_gate("plan-receipt.ac3.json", "close-receipt.ac3.json")
require(
    e2e_gate_ac3.returncode == 0 and "e2e: not applicable" in e2e_gate_ac3.stdout,
    f"e2e-gate ac3 (not-applicable branch) failed: exit {e2e_gate_ac3.returncode}, stdout {e2e_gate_ac3.stdout!r}",
)

e2e_gate_ac4 = run_e2e_gate("plan-receipt.ac4.json", "close-receipt.ac4.json")
require(
    e2e_gate_ac4.returncode == 1,
    f"e2e-gate ac4 (no milestone named) should exit 1: exit {e2e_gate_ac4.returncode}, stderr {e2e_gate_ac4.stderr!r}",
)

e2e_gate_dangling = run_e2e_gate("plan-receipt.dangling-milestone.json", "close-receipt.dangling-milestone.json")
require(
    e2e_gate_dangling.returncode == 2,
    f"e2e-gate dangling milestone id should exit 2: exit {e2e_gate_dangling.returncode}, stderr {e2e_gate_dangling.stderr!r}",
)

e2e_gate_empty_slug = run_e2e_gate("plan-receipt.empty-slug.json", "close-receipt.empty-slug.json")
require(
    e2e_gate_empty_slug.returncode == 2,
    f"e2e-gate punctuation-only milestone name should exit 2 (empty slug): "
    f"exit {e2e_gate_empty_slug.returncode}, stderr {e2e_gate_empty_slug.stderr!r}",
)

e2e_gate_chinese = run_e2e_gate("plan-receipt.chinese-milestone.json", "close-receipt.chinese-milestone.json")
require(
    e2e_gate_chinese.returncode == 0
    and "docs/ship-flow/flows/从派工到一条-slack-消息.yaml" in e2e_gate_chinese.stdout,
    f"e2e-gate Chinese milestone name should derive its Unicode flow path: "
    f"exit {e2e_gate_chinese.returncode}, stdout {e2e_gate_chinese.stdout!r}",
)

# --- review station: open-pr.sh BRANCH binding + disposition.py category handling ---
ship_flow_fixtures = FIXTURES
open_pr_script = SCRIPTS / "open-pr.sh"
disposition_script = SCRIPTS / "disposition.py"


def run_disposition(fixture: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(disposition_script), str(fixture)], capture_output=True, text=True,
    )


disposition_security_cased = run_disposition(ship_flow_fixtures / "findings-security-cased.json")
require(
    disposition_security_cased.returncode == 0 and '"disposition": "block"' in disposition_security_cased.stdout,
    "disposition.py did not block a case-varied 'Security' category after normalization: "
    f"exit={disposition_security_cased.returncode} stdout={disposition_security_cased.stdout!r}",
)

disposition_unrecognized = run_disposition(ship_flow_fixtures / "findings-unrecognized-category.json")
require(
    disposition_unrecognized.returncode == 0
    and '"disposition": "block"' in disposition_unrecognized.stdout
    and "unrecognized-category" in disposition_unrecognized.stdout,
    "disposition.py did not fail closed (block) on an unrecognized category: "
    f"exit={disposition_unrecognized.returncode} stdout={disposition_unrecognized.stdout!r}",
)

disposition_malformed = run_disposition(ship_flow_fixtures / "findings-malformed-entry.json")
require(
    disposition_malformed.returncode == 2,
    "disposition.py did not refuse a findings list with a non-dict entry: "
    f"exit={disposition_malformed.returncode} stdout={disposition_malformed.stdout!r} stderr={disposition_malformed.stderr!r}",
)

disposition_deps_no_supply = run_disposition(ship_flow_fixtures / "deps-diff-no-supply")
require(
    disposition_deps_no_supply.returncode == 2
    and "supply-chain findings required" in (disposition_deps_no_supply.stdout + disposition_deps_no_supply.stderr),
    "disposition.py did not refuse a dependency-manifest diff missing its supply-chain findings file: "
    f"exit={disposition_deps_no_supply.returncode} stdout={disposition_deps_no_supply.stdout!r} "
    f"stderr={disposition_deps_no_supply.stderr!r}",
)

disposition_deps_with_supply = run_disposition(ship_flow_fixtures / "deps-diff-with-supply")
require(
    disposition_deps_with_supply.returncode == 0 and '"disposition": "listed"' in disposition_deps_with_supply.stdout,
    "disposition.py refused a dependency-manifest diff whose supply-chain findings file is present: "
    f"exit={disposition_deps_with_supply.returncode} stdout={disposition_deps_with_supply.stdout!r} "
    f"stderr={disposition_deps_with_supply.stderr!r}",
)

disposition_deps_no_changed_files = run_disposition(ship_flow_fixtures / "deps-diff-no-changed-files")
require(
    disposition_deps_no_changed_files.returncode == 2
    and "changed-files.txt required" in (disposition_deps_no_changed_files.stdout + disposition_deps_no_changed_files.stderr),
    "disposition.py did not refuse a bundle missing changed-files.txt: "
    f"exit={disposition_deps_no_changed_files.returncode} stdout={disposition_deps_no_changed_files.stdout!r} "
    f"stderr={disposition_deps_no_changed_files.stderr!r}",
)

open_pr_fork_branch = subprocess.run(
    ["bash", str(open_pr_script), str(ship_flow_fixtures / "open-pr-evidence-fork-branch.md")],
    cwd=ROOT, capture_output=True, text=True,
)
require(
    open_pr_fork_branch.returncode == 2 and "fork syntax refused" in open_pr_fork_branch.stderr,
    "open-pr.sh did not refuse a BRANCH containing ':' (fork syntax): "
    f"exit={open_pr_fork_branch.returncode} stderr={open_pr_fork_branch.stderr!r}",
)

open_pr_double_block = subprocess.run(
    ["bash", str(open_pr_script), str(ship_flow_fixtures / "open-pr-evidence-double-block.md")],
    cwd=ROOT, capture_output=True, text=True,
)
require(
    open_pr_double_block.returncode == 2 and "'## Evidence' headings" in open_pr_double_block.stderr,
    "open-pr.sh did not refuse an evidence file with more than one '## Evidence' heading: "
    f"exit={open_pr_double_block.returncode} stderr={open_pr_double_block.stderr!r}",
)

with tempfile.TemporaryDirectory(prefix="kc-ship-flow-open-pr-") as open_pr_dir_name:
    open_pr_dir = Path(open_pr_dir_name)
    open_pr_origin = open_pr_dir / "origin.git"
    open_pr_repo = open_pr_dir / "repo"
    git_user = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.test"]
    subprocess.run(["git", "init", "-q", "--bare", str(open_pr_origin)], check=True, capture_output=True)
    subprocess.run(["git", "clone", "-q", str(open_pr_origin), str(open_pr_repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(open_pr_repo), *git_user, "commit", "-q", "--allow-empty", "-m", "feat(fixture): seed"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(open_pr_repo), "push", "-q", "origin", "HEAD:refs/heads/main"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(open_pr_repo), *git_user, "checkout", "-q", "-b", "feature/fixture-branch"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(open_pr_repo), "push", "-q", "origin", "feature/fixture-branch"],
        check=True, capture_output=True,
    )
    open_pr_sha = subprocess.check_output(
        ["git", "-C", str(open_pr_repo), "rev-parse", "HEAD"], text=True,
    ).strip()

    def write_open_pr_evidence(name: str, branch: str) -> Path:
        evidence = open_pr_dir / name
        evidence.write_text(
            "## Evidence\n"
            f"CANDIDATE_SHA: {open_pr_sha}\n"
            f"BRANCH: {branch}\n"
            f"BASE_SHA: {open_pr_sha}\n"
            "SELF_CHECK: fixture accept-evidence: ACCEPT\n"
            "WITHOUT_IT_COMMAND: true\n"
            "WITHOUT_IT_REMOVED_VARIANT: rm -f candidate-only.ts\n",
            encoding="utf-8",
        )
        return evidence

    open_pr_bound_evidence = write_open_pr_evidence("bound-evidence.md", "feature/fixture-branch")
    open_pr_unbound_evidence = write_open_pr_evidence("unbound-evidence.md", "feature/does-not-exist-on-origin")

    fake_gh_dir = open_pr_dir / "fake-gh"
    fake_gh_dir.mkdir()
    fake_gh_sentinel = open_pr_dir / "gh-called"
    fake_gh_path = fake_gh_dir / "gh"
    fake_gh_path.write_text(
        "#!/usr/bin/env bash\n"
        f"touch '{fake_gh_sentinel}'\n"
        "echo 'warning: 999 deprecation notice' >&2\n"
        "echo 'https://github.com/example/example/pull/777'\n",
        encoding="utf-8",
    )
    fake_gh_path.chmod(0o755)

    def run_open_pr(evidence: Path) -> subprocess.CompletedProcess[str]:
        if fake_gh_sentinel.exists():
            fake_gh_sentinel.unlink()
        open_pr_env = dict(os.environ)
        open_pr_env["PATH"] = f"{fake_gh_dir}:{open_pr_env.get('PATH', '')}"
        return subprocess.run(
            ["bash", str(open_pr_script), str(evidence)],
            cwd=open_pr_repo, capture_output=True, text=True, env=open_pr_env,
        )

    open_pr_bound = run_open_pr(open_pr_bound_evidence)
    require(
        open_pr_bound.returncode == 0
        and open_pr_bound.stdout.strip() == "777"
        and fake_gh_sentinel.exists(),
        "open-pr.sh did not open a PR (parsing 777 from stdout only, ignoring stderr's 999) "
        f"for a BRANCH whose remote head matches CANDIDATE_SHA: exit={open_pr_bound.returncode} "
        f"stdout={open_pr_bound.stdout!r} stderr={open_pr_bound.stderr!r}",
    )

    open_pr_unbound = run_open_pr(open_pr_unbound_evidence)
    require(
        open_pr_unbound.returncode == 2 and not fake_gh_sentinel.exists(),
        "open-pr.sh did not refuse a BRANCH absent from origin before calling gh: "
        f"exit={open_pr_unbound.returncode} stderr={open_pr_unbound.stderr!r}",
    )

run([sys.executable, str(SCRIPTS / "prose-placement-check.py")], "kc-ship-flow prose-placement-check.py")

run(
    [sys.executable, str(SCRIPTS / "local-profile-check.py"), str(ROOT / "docs" / "ship" / "README.md")],
    "kc-ship-flow local-profile-check.py",
)

# DEV-119 repair round 1: local-profile-check.py must refuse a Local Profile table
# missing a required row, and refuse (rather than silently pick) a duplicated
# marker pair, naming which failure it hit. Both run against a temporary copy of
# the real README, never the tracked file itself.
local_profile_check = SCRIPTS / "local-profile-check.py"
ship_readme_path = ROOT / "docs" / "ship" / "README.md"
ship_readme_text = ship_readme_path.read_text(encoding="utf-8")


def run_local_profile_check(contents: str) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(contents)
        temp_readme = Path(handle.name)
    try:
        return subprocess.run(
            [sys.executable, str(local_profile_check), str(temp_readme)],
            cwd=ROOT, text=True, capture_output=True,
        )
    finally:
        temp_readme.unlink(missing_ok=True)


missing_runtime_text = "\n".join(
    line for line in ship_readme_text.splitlines() if "| Runtime |" not in line
) + "\n"
require(
    missing_runtime_text != ship_readme_text,
    "local-profile-check mutation fixture: no '| Runtime |' row found in docs/ship/README.md",
)
missing_runtime_result = run_local_profile_check(missing_runtime_text)
require(
    missing_runtime_result.returncode != 0
    and "LOCAL_PROFILE_MISSING_ROW: Runtime" in missing_runtime_result.stderr,
    "local-profile-check.py did not refuse a Local Profile table missing the Runtime row, "
    f"naming it: exit={missing_runtime_result.returncode} stderr={missing_runtime_result.stderr!r}",
)

duplicated_marker_text = ship_readme_text + "\n" + ship_readme_text
duplicated_marker_result = run_local_profile_check(duplicated_marker_text)
require(
    duplicated_marker_result.returncode != 0
    and "LOCAL_PROFILE_MARKER_COUNT" in duplicated_marker_result.stderr,
    "local-profile-check.py did not refuse a Local Profile block whose start/end markers are "
    f"duplicated, naming the marker error: exit={duplicated_marker_result.returncode} "
    f"stderr={duplicated_marker_result.stderr!r}",
)

# DEV-154: station scripts were named by a plugin-relative path that only resolves
# inside a checkout named kc-claude-plugins. SKILL.md must not reintroduce it; the
# adopter fixture must resolve from a plugin copy installed somewhere else entirely.
first_officer_skill = PLUGIN / "skills" / "first-officer" / "SKILL.md"
require(
    "kc-ship-flow/scripts/" not in first_officer_skill.read_text(encoding="utf-8"),
    f"{first_officer_skill} still names a station script by the repo-relative "
    "'kc-ship-flow/scripts/' path (AC-2 regression)",
)

adopter_readme = FIXTURES / "adopter" / "docs" / "ship" / "README.md"
require(adopter_readme.is_file(), f"missing fixture: {adopter_readme}")

adopter_in_tree_result = subprocess.run(
    [sys.executable, str(local_profile_check), str(adopter_readme)],
    cwd=ROOT, text=True, capture_output=True,
)
require(
    adopter_in_tree_result.returncode == 0
    and "LOCAL_PROFILE_SCRIPT_OK" in adopter_in_tree_result.stdout
    and "fenced-dispatch.sh" in adopter_in_tree_result.stdout,
    "local-profile-check.py did not resolve the adopter fixture's station scripts: "
    f"exit={adopter_in_tree_result.returncode} stdout={adopter_in_tree_result.stdout!r} "
    f"stderr={adopter_in_tree_result.stderr!r}",
)

with tempfile.TemporaryDirectory(prefix="kc-ship-flow-adopter-install-") as adopter_install_root_name:
    # Falsifier: plugin copy under an unrelated tree, CLAUDE_PLUGIN_ROOT unset, cwd
    # elsewhere -- only the script's own file location can resolve its siblings here.
    adopter_install_dir = Path(adopter_install_root_name) / "plugins" / "local" / "kc-ship-flow"
    shutil.copytree(PLUGIN, adopter_install_dir)
    adopter_install_check = adopter_install_dir / "scripts" / "local-profile-check.py"
    adopter_install_readme = adopter_install_dir / "scripts" / "fixtures" / "adopter" / "docs" / "ship" / "README.md"
    require(adopter_install_readme.is_file(), "adopter install copy is missing its own fixture")
    with tempfile.TemporaryDirectory(prefix="kc-ship-flow-adopter-cwd-") as adopter_cwd_name:
        adopter_env = dict(os.environ)
        adopter_env.pop("CLAUDE_PLUGIN_ROOT", None)
        adopter_install_result = subprocess.run(
            [sys.executable, str(adopter_install_check), str(adopter_install_readme)],
            cwd=adopter_cwd_name, text=True, capture_output=True, env=adopter_env,
        )
    require(
        adopter_install_result.returncode == 0
        and "LOCAL_PROFILE_SCRIPT_OK" in adopter_install_result.stdout
        and str(adopter_install_dir) in adopter_install_result.stdout,
        "local-profile-check.py did not resolve station scripts from a plugin copy "
        "installed outside kc-claude-plugins, run from an unrelated cwd without "
        f"CLAUDE_PLUGIN_ROOT set: exit={adopter_install_result.returncode} "
        f"stdout={adopter_install_result.stdout!r} stderr={adopter_install_result.stderr!r}",
    )

# DEV-117 repair round 1: a placement.tsv row is not "placed" just because its
# destination file exists -- it must also carry that segment's hash marker.
# Repoint one real row to a different real destination that lacks its hash
# and confirm the check refuses (before the fix this mutation stayed exit 0).
prose_placement_check = SCRIPTS / "prose-placement-check.py"
placement_tsv = PLUGIN / "references" / "placement.tsv"
original_placement = placement_tsv.read_text(encoding="utf-8")
mutated_placement = original_placement.replace(
    "97b2ae0b2cc8\tkc-ship-flow/references/stations/notify.md",
    "97b2ae0b2cc8\tkc-ship-flow/references/stations/uat-doc.md",
)
require(mutated_placement != original_placement, "prose-placement-check mutation fixture: target row not found in placement.tsv")
try:
    placement_tsv.write_text(mutated_placement, encoding="utf-8")
    mutated_result = subprocess.run(
        [sys.executable, str(prose_placement_check)], cwd=ROOT, text=True, capture_output=True,
    )
finally:
    placement_tsv.write_text(original_placement, encoding="utf-8")
require(
    mutated_result.returncode != 0,
    "prose-placement-check.py did not refuse a row repointed to an unrelated existing "
    f"destination lacking the segment's hash marker: exit={mutated_result.returncode} "
    f"stdout={mutated_result.stdout!r}",
)

accept_evidence_script = SCRIPTS / "accept-evidence.sh"

ts_read_path_result = subprocess.run(
    ["bash", str(accept_evidence_script), str(FIXTURES / "ts-read-path.md")],
    cwd=ROOT, text=True, capture_output=True,
)
require(
    ts_read_path_result.returncode == 0
    and "accept-evidence: ACCEPT" in ts_read_path_result.stdout,
    "accept-evidence.sh did not accept a WITHOUT_IT_COMMAND reading tracked .ts/.mts paths: "
    f"exit={ts_read_path_result.returncode} stdout={ts_read_path_result.stdout!r} "
    f"stderr={ts_read_path_result.stderr!r}",
)

mutant_untracked_path_result = subprocess.run(
    ["bash", str(accept_evidence_script), str(FIXTURES / "mutant-untracked-path.md")],
    cwd=ROOT, text=True, capture_output=True,
)
require(
    mutant_untracked_path_result.returncode == 1
    and "accept-evidence-does-not-exist.xyz" in mutant_untracked_path_result.stdout,
    "accept-evidence.sh did not refuse a WITHOUT_IT_COMMAND reading only an untracked path, "
    f"naming it: exit={mutant_untracked_path_result.returncode} "
    f"stdout={mutant_untracked_path_result.stdout!r}",
)

with tempfile.TemporaryDirectory(prefix="kc-ship-flow-accept-evidence-candidate-tree-") as candidate_tree_dir_name:
    candidate_tree_dir = Path(candidate_tree_dir_name)
    candidate_tree_repo = candidate_tree_dir / "repo"
    git_user = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.test"]
    subprocess.run(["git", "init", "-q", str(candidate_tree_repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(candidate_tree_repo), *git_user, "commit", "-q", "--allow-empty", "-m", "feat(fixture): base"],
        check=True, capture_output=True,
    )
    checkout_sha = subprocess.check_output(
        ["git", "-C", str(candidate_tree_repo), "rev-parse", "HEAD"], text=True,
    ).strip()

    only_in_candidate = candidate_tree_repo / "candidate-only.ts"
    only_in_candidate.write_text("export const marker = \"only-in-candidate\";\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(candidate_tree_repo), "add", "candidate-only.ts"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(candidate_tree_repo), *git_user, "commit", "-q", "-m", "feat(fixture): add candidate-only path"],
        check=True, capture_output=True,
    )
    candidate_sha = subprocess.check_output(
        ["git", "-C", str(candidate_tree_repo), "rev-parse", "HEAD"], text=True,
    ).strip()

    subprocess.run(
        ["git", "-C", str(candidate_tree_repo), "checkout", "-q", "--detach", checkout_sha],
        check=True, capture_output=True,
    )

    candidate_tree_evidence = candidate_tree_dir / "evidence.md"
    candidate_tree_evidence.write_text(
        "## Evidence\n"
        f"CANDIDATE_SHA: {candidate_sha}\n"
        f"BASE_SHA: {checkout_sha}\n"
        "WITHOUT_IT_COMMAND: grep -q only-in-candidate candidate-only.ts\n"
        "WITHOUT_IT_REMOVED_VARIANT: rm -f candidate-only.ts\n",
        encoding="utf-8",
    )

    candidate_tree_result = subprocess.run(
        ["bash", str(accept_evidence_script), str(candidate_tree_evidence), "--repo", str(candidate_tree_repo)],
        cwd=ROOT, text=True, capture_output=True,
    )
    require(
        candidate_tree_result.returncode == 0
        and "accept-evidence: ACCEPT" in candidate_tree_result.stdout,
        "accept-evidence.sh did not accept a WITHOUT_IT_COMMAND reading a path that exists only "
        "at CANDIDATE_SHA on a --repo checkout sitting at an earlier commit: "
        f"exit={candidate_tree_result.returncode} stdout={candidate_tree_result.stdout!r} "
        f"stderr={candidate_tree_result.stderr!r}",
    )

# --- DEV-147/DEV-135: dev-debrief.py's real not-dispatched output (the
# --- `note` field) embeds into a close receipt that validate-receipt.py
# --- accepts -- the close-receipt schema admits `note` on a per_issue
# --- entry, it is not a shape only the writer's own stdout can produce ----
dev_debrief_script = SCRIPTS / "dev-debrief.py"
carried_batch = FIXTURES / "batch-carried-issue"
carried_result = subprocess.run(
    [sys.executable, str(dev_debrief_script), str(carried_batch)], capture_output=True, text=True,
)
require(
    carried_result.returncode == 0,
    f"dev-debrief.py on {carried_batch} must exit 0: exit={carried_result.returncode} stderr={carried_result.stderr!r}",
)
carried_dev_debrief = json.loads(carried_result.stdout)
(carried_issue_id,) = carried_dev_debrief["per_issue"]
require(
    carried_dev_debrief["per_issue"][carried_issue_id].get("note") == "not dispatched",
    f"batch-carried-issue's writer output must carry a not-dispatched note: {carried_dev_debrief}",
)


def canon(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


carried_body = "## The problem\n\nFixture body.\n\n## Accepted outcome\n\nFixture only.\n"
carried_plan_receipt = {
    "schema": "kc-plan-receipt/v1",
    "code_repo": "example-org/example-repo",
    "base_branch": "main",
    "project": {
        "id": "00000000-0000-0000-0000-0000000000a1",
        "name": "Synthetic carried-note contract fixture",
        "user_value": "A writer-produced not-dispatched entry embeds into a close receipt that validates.",
        "hypothesis": "If we let the schema admit `note` then a real dev-debrief.py output validates unchanged.",
        "wedge": "Fixture only; exercises validate-receipt.py's close-receipt path end to end.",
        "outcome": "One issue closes carried, with a not-dispatched dev_debrief entry.",
        "exit": ["Fixture validates."],
        "outcome_hash": f"sha256:{sha('carried-note-fixture-outcome')}",
    },
    "cycle": "00000000-0000-0000-0000-0000000000a2",
    "milestones": [],
    "issues": {
        carried_issue_id: {
            "id": "00000000-0000-0000-0000-0000000000a3",
            "url": f"https://example.test/issue/{carried_issue_id}",
            "title": carried_issue_id,
            "branch": f"feature/{carried_issue_id.lower()}-synthetic-fixture",
            "close_line": f"Fixes {carried_issue_id}",
            "profile": "pilot-product-slice",
            "milestone": None,
            "body": carried_body,
            "body_sha256": sha(carried_body),
        },
    },
    "edges": [],
    "dispatch_order": [carried_issue_id],
    "lint": {"schema": "kc-plan-lint/v1", "pass": True, "digest": sha("carried-note-fixture-lint")},
    "premises": [
        {"id": "P1", "statement": "Fixture premise: a real not-dispatched dev-debrief entry validates.", "agreed": True},
    ],
    "rationale_sha256": sha("carried-note-fixture-rationale"),
}
carried_plan_receipt["receipt_sha256"] = sha(canon(carried_plan_receipt).decode())

carried_plan_approval = {
    "schema": "kc-plan-approval/v1",
    "receipt_sha256": carried_plan_receipt["receipt_sha256"],
    "approver": "person:captain",
    "approved_at": "2026-09-09T00:00:00Z",
    "decision": "go",
    "max_workspaces": 1,
    "concurrency": 1,
    "repair_rounds": 0,
    "quote": "go, synthetic fixture approval",
    "quote_source": "fixture, not a real approval",
    "defaults": {
        "findings_outside_brief": ["security", "data-loss", "compatibility"],
        "minimal_necessity_fail": "accepted_no_pr",
        "moved_base": "rebase_and_accept",
        "worker_blocker": "skip_issue_continue_batch",
        "empty_reviewer": "fallback_to_fo_diff_read",
        "pr_creation": "batch_approve_draft",
    },
}

carried_close_receipt = {
    "schema": "kc-ship-close-receipt/v1",
    "plan_receipt_sha256": carried_plan_receipt["receipt_sha256"],
    "approval_receipt_sha256": sha(canon(carried_plan_approval).decode()),
    "batch": {
        "entity": "batch-carried-note-contract",
        "started_at": "2026-09-09T00:00:00Z",
        "closed_at": "2026-09-09T00:05:00Z",
        "holder": "laptop",
    },
    "issues": {
        carried_issue_id: {
            "outcome": "carried",
            "candidate": None,
            "pr": None,
            "rounds": 0,
            "minutes": {"dispatch": 0},
        },
    },
    "defects_returned": [],
    "totals": {"workspaces_created": 0, "workspaces_orphaned": 0, "fix_rounds": 0, "captain_gates": 0},
    "dev_debrief": carried_dev_debrief,
    "ship_debrief": {
        "defaults_decisions": [],
        "defects_disposition": [],
        "minutes_per_station": {"dispatch": 0},
        "candidate_correction": "TBD (FO): one candidate correction to ship-flow from this batch.",
    },
}
carried_close_receipt["close_sha256"] = sha(canon(carried_close_receipt).decode())

validate_receipt_script = ROOT / "docs" / "plan-flow" / "schema" / "validate-receipt.py"

with tempfile.TemporaryDirectory(prefix="kc-ship-flow-carried-note-") as carried_dir_name:
    carried_dir = Path(carried_dir_name)
    (carried_dir / "plan-receipt.json").write_text(json.dumps(carried_plan_receipt), encoding="utf-8")
    (carried_dir / "plan-approval.json").write_text(json.dumps(carried_plan_approval), encoding="utf-8")
    (carried_dir / "close-receipt.json").write_text(json.dumps(carried_close_receipt), encoding="utf-8")
    carried_note_result = subprocess.run(
        [
            sys.executable, str(validate_receipt_script),
            str(carried_dir / "plan-receipt.json"),
            str(carried_dir / "plan-approval.json"),
            str(carried_dir / "close-receipt.json"),
        ],
        capture_output=True, text=True,
    )
    require(
        carried_note_result.returncode == 0 and "CLOSE OK" in carried_note_result.stdout,
        "validate-receipt.py did not accept a close receipt embedding dev-debrief.py's real "
        f"not-dispatched output: exit={carried_note_result.returncode} "
        f"stdout={carried_note_result.stdout!r} stderr={carried_note_result.stderr!r}",
    )
close_receipt_fixtures = FIXTURES / "close-receipt"
forbidden_embed_result = subprocess.run(
    [
        sys.executable, str(validate_receipt_script),
        str(close_receipt_fixtures / "plan-receipt.json"),
        str(close_receipt_fixtures / "plan-approval.json"),
        str(close_receipt_fixtures / "close-receipt.dev-debrief-wrapper-embedded.json"),
    ],
    capture_output=True, text=True,
)
require(
    forbidden_embed_result.returncode == 1 and "dev_debrief" in forbidden_embed_result.stdout,
    "validate-receipt.py did not refuse a close receipt whose dev_debrief embeds the writer's own "
    f"wrapper keys: exit={forbidden_embed_result.returncode} stdout={forbidden_embed_result.stdout!r}",
)

print("kc-ship-flow contract: PASS")
