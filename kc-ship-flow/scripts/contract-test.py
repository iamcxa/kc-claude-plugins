#!/usr/bin/env python3
"""Behavior and packaging contract for kc-ship-flow."""

from __future__ import annotations

import hashlib
import json
import os
import re
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
            "WITHOUT_IT_REMOVED_VARIANT: true\n",
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

print("kc-ship-flow contract: PASS")
