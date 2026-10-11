#!/usr/bin/env python3
"""Rebuild a closed task's worker dispatch against a chosen package version, for a behaviour replay.

  replay_dispatch.py build --run-dir DIR --package-repo PATH --package-ref REF
      --adopter-readme FILE --readme-base-ref REF --state-repo PATH --state-commit SHA
      --task SLUG --code-repo PATH --code-commit SHA --stage STAGE
      --checklist FILE [--scope FILE] [--inject FILE] [--spacedock BIN]
  replay_dispatch.py cleanup --run-dir DIR

build exports the package at REF, merges the adopter README from the package version it was
synced to (--readme-base-ref) onto REF, checks out the task's state and code at the given
commits, appends --inject to the task file when given, and runs `spacedock dispatch build`.
The dispatch file is copied to DIR/dispatch.md, since every build writes the same shared path.
Exit 1 on a failed step, 2 on bad arguments.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

HARNESS = ("TEST HARNESS (isolated replay): do not invoke the kc-dev-flow-2 skill through the Skill tool; "
           "read {pkg}/skills/{stage}/SKILL.md and follow it, resolving every package path against {pkg}. "
           "Do not run the application unit, integration or e2e suites and do not start servers, databases "
           "or browsers; say in the report they were not run. Run the package's own scripts as your "
           "instructions require. Do not push, merge or commit to any remote. The state checkout is "
           "{state}; write your stage report there only. Never git stash.")


def git(repo, *args):
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def export(repo, ref, inner, dest):
    archive = subprocess.run(["git", "-C", str(repo), "archive", ref, inner], capture_output=True)
    if archive.returncode:
        raise RuntimeError(f"git archive {ref} {inner}: {archive.stderr.decode().strip()}")
    dest.mkdir(parents=True)
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)
    return dest / inner


def entity(state, slug):
    for path in (state / f"{slug}.md", state / slug / "index.md"):
        if path.exists():
            return path
    raise RuntimeError(f"task {slug} not found in {state}")


def build(a):
    run = Path(a.run_dir).resolve()
    if run.exists():
        raise RuntimeError(f"{run} exists; clean it up first")
    pkg = export(a.package_repo, a.package_ref, "kc-dev-flow-2", run / "package")
    base = git(a.package_repo, "show", f"{a.readme_base_ref}:kc-dev-flow-2/references/sd/workflow.md")
    (run / "base.md").write_text(base)
    wf = run / "wf"
    wf.mkdir()
    merged = subprocess.run(["git", "merge-file", "-p", a.adopter_readme, str(run / "base.md"),
                             str(pkg / "references/sd/workflow.md")], capture_output=True, text=True)
    if merged.returncode:
        raise RuntimeError("README merge conflicted; the adopter README is not from --readme-base-ref")
    (wf / "README.md").write_text(merged.stdout)
    state = wf / ".spacedock-state"
    git(a.state_repo, "worktree", "add", "--detach", str(state), a.state_commit)
    task = entity(state, a.task)
    if a.inject:
        task.write_text(task.read_text() + Path(a.inject).read_text())
        git(state, "-c", "user.name=replay", "-c", "user.email=replay@localhost", "commit", "-qam", "replay: inject")
    code = run / "code"
    git(a.code_repo, "worktree", "add", "--detach", str(code), a.code_commit)
    (wf / ".worktrees").mkdir()
    (wf / ".worktrees" / f"spacedock-ensign-{a.task}").symlink_to(code)
    scope = [f"Package root: {pkg}"]
    if a.scope:
        scope.append(Path(a.scope).read_text().strip())
    scope.append(HARNESS.format(pkg=pkg, stage=a.stage, state=state))
    (run / "scope.txt").write_text("\n".join(scope) + "\n")
    shutil.copy(a.checklist, run / "checklist.txt")
    done = subprocess.run([a.spacedock, "dispatch", "build", "--workflow-dir", str(wf), "--entity-path", str(task),
                           "--stage", a.stage, "--checklist-file", str(run / "checklist.txt"),
                           "--scope-notes-file", str(run / "scope.txt")], capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(f"dispatch build: {done.stderr.strip()[:300]}")
    shutil.copy(json.loads(done.stdout)["dispatch_file_path"], run / "dispatch.md")
    (run / "replay.json").write_text(json.dumps({"state_repo": str(Path(a.state_repo).resolve()), "state": str(state),
                                                 "code_repo": str(Path(a.code_repo).resolve()), "code": str(code)}))
    print(f"{run / 'dispatch.md'}")


def cleanup(a):
    run = Path(a.run_dir).resolve()
    meta = json.loads((run / "replay.json").read_text()) if (run / "replay.json").exists() else {}
    for repo, tree in ((meta.get("state_repo"), meta.get("state")), (meta.get("code_repo"), meta.get("code"))):
        if repo and tree and Path(tree).exists():
            git(repo, "worktree", "remove", "--force", tree)
    shutil.rmtree(run, ignore_errors=True)
    print(f"removed {run}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    for flag in ("run-dir", "package-repo", "package-ref", "adopter-readme", "readme-base-ref", "state-repo",
                 "state-commit", "task", "code-repo", "code-commit", "stage", "checklist"):
        b.add_argument(f"--{flag}", required=True)
    b.add_argument("--scope")
    b.add_argument("--inject")
    b.add_argument("--spacedock", default="spacedock")
    c = sub.add_parser("cleanup")
    c.add_argument("--run-dir", required=True)
    try:
        a = parser.parse_args(argv)
    except SystemExit as stop:
        return 0 if stop.code == 0 else 2
    try:
        build(a) if a.command == "build" else cleanup(a)
    except (RuntimeError, OSError, KeyError, ValueError, subprocess.CalledProcessError) as error:
        print(f"replay_dispatch: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
