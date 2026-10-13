#!/usr/bin/env python3
"""Archive a task without observer.md in a disposable split-root workflow, then repair it the way the learn
extension says, on the installed Spacedock. Runs no model and no delivery hook."""

import argparse
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts/observer_check.py"
TEMPLATE = ROOT / "references/sd/workflow.md"
SLUG = "recovery-fixture"
REPORT = "ok | rule: \"FO records\" (Stage Report) | evidence: \"present\" (abc1234)\n"


def exercise(base, binary):
    env = {key: value for key, value in os.environ.items() if key not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    env["SPACEDOCK_BIN"] = binary

    def run(args, cwd=base, expected=0):
        done = subprocess.run([str(a) for a in args], cwd=cwd, env=env, text=True, capture_output=True, timeout=60)
        if expected is not None and done.returncode != expected:
            raise AssertionError(f"{args}: exit {done.returncode}\n{done.stdout}\n{done.stderr}")
        return done

    origin = base / "origin.git"
    run(["git", "init", "--bare", "--initial-branch=main", origin])
    repo = base / "repo"
    workflow = repo / "docs/dev2"
    workflow.mkdir(parents=True)
    definition = TEMPLATE.read_text()
    definition = re.sub(r"    - name: ideation\n.*?(?=    - name: implementation)", "", definition, flags=re.DOTALL)
    definition = re.sub(r"### `ideation`\n.*?(?=### `implementation`)", "", definition, flags=re.DOTALL)
    (workflow / "README.md").write_text(definition)
    (repo / ".gitignore").write_text(".worktrees/\n**/.spacedock-state/\n")
    run(["git", "init", "--initial-branch=main", repo])
    for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                       ("commit.gpgsign", "false"), ("core.hooksPath", "/dev/null")):
        run(["git", "-C", repo, "config", key, value])
    run(["git", "-C", repo, "remote", "add", "origin", origin])
    run(["git", "-C", repo, "add", "--", ".gitignore", "docs/dev2/README.md"])
    run(["git", "-C", repo, "commit", "-m", "test: seed workflow"])
    run(["git", "-C", repo, "push", "origin", "main"])
    state = workflow / ".spacedock-state"
    run(["git", "-C", repo, "worktree", "add", "--detach", state])
    run(["git", "-C", state, "checkout", "--orphan", "spacedock-state/dev2"])
    run(["git", "-C", state, "rm", "-rf", "."])
    entity = state / f"{SLUG}.md"
    entity.write_text(definition.split("```markdown\n", 1)[1].split("```", 1)[0]
                      .replace("<task-id>", SLUG).replace("<selected-profile>", "poc")
                      .replace("<bounded outcome>", "Synthetic fixture, not product acceptance")
                      .replace("status: backlog", "status: validation"))
    (state / SLUG).mkdir()
    (state / SLUG / "dispatch.md").write_text("synthetic dispatch record\n")
    run(["git", "-C", state, "add", "--", entity.name, SLUG])
    run(["git", "-C", state, "commit", "-m", "test: seed task state"])
    run(["git", "-C", state, "push", "origin", "spacedock-state/dev2"])

    def check(*extra):
        return run(["python3", CHECK, state, SLUG, *extra], expected=None)

    run([binary, "gate", "prepare", SLUG, "--workflow-dir", workflow, "--question", "Synthetic?", "--artifact", entity,
         "--summary", "SYNTHETIC fixture; no human acceptance."], workflow)
    run([binary, "gate", "record", SLUG, "--workflow-dir", workflow, "--decision", "approve", "--actor",
         "person:captain", "--reason", "SYNTHETIC TEST ONLY; no real approval."], workflow)
    run([binary, "gate", "consume", SLUG, "--workflow-dir", workflow], workflow)
    run([binary, "status", "--workflow-dir", workflow, "--set", SLUG, "pr=pr-merge:7"], workflow)
    run([binary, "state", "commit", SLUG, "--workflow-dir", workflow], workflow)

    before = check()
    assert before.returncode == 1 and f"{SLUG}/observer.md" in before.stdout, before
    run([binary, "merge", "guard", SLUG, "--workflow-dir", workflow, "--verdict", "passed"], workflow)
    archived = state / "_archive" / f"{SLUG}.md"
    assert archived.is_file() and not entity.exists(), "the task was not archived"
    missed = check()
    assert missed.returncode == 1 and f"_archive/{SLUG}/observer.md" in missed.stdout, missed

    folder = state / "_archive" / SLUG
    folder.mkdir(exist_ok=True)
    (folder / "observer.md").write_text(REPORT)
    refused = run([binary, "state", "commit", SLUG, "--workflow-dir", workflow], workflow, expected=1)
    assert "archived scope is publish-only" in refused.stdout + refused.stderr, refused
    assert check().returncode == 1, "an uncommitted late report must not pass"

    path = f"_archive/{SLUG}/observer.md"
    run(["git", "-C", state, "add", path])
    run(["git", "-C", state, "commit", "-m", "docs: late observer report", "--", path])
    published = run([binary, "state", "commit", SLUG, "--workflow-dir", workflow], workflow)
    if "Published existing archived state" not in published.stdout + published.stderr:
        raise AssertionError(f"publication not reported: {published.stdout}{published.stderr}")
    local = run(["git", "-C", state, "rev-parse", "HEAD"]).stdout.strip()
    remote = run(["git", "-C", origin, "rev-parse", "spacedock-state/dev2"]).stdout.strip()
    assert local == remote, (local, remote)

    valid = run([binary, "status", "--workflow-dir", workflow, "--validate"], workflow)
    assert "VALID" in valid.stdout, valid.stdout
    repaired = check()
    assert repaired.returncode == 0, repaired
    assert not run(["git", "-C", state, "status", "--porcelain", "--", f"_archive/{SLUG}.md"]).stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    binary = shutil.which(os.environ.get("SPACEDOCK_BIN") or "spacedock")
    if not binary:
        parser.error("set SPACEDOCK_BIN to the installed Spacedock executable")
    base = Path(tempfile.mkdtemp(prefix="observer-recovery-")).resolve()
    try:
        exercise(base, str(Path(binary).resolve()))
    except Exception:
        print(f"FAIL: fixture retained at {base}")
        raise
    shutil.rmtree(base)
    print("PASS: archive without observer.md detected; state commit refused for the late report; "
          "path-scoped commit then state commit published it; validate VALID; check exits 0")


if __name__ == "__main__":
    main()
