#!/usr/bin/env python3
"""Execute named falsifiers against the unchanged committed candidate."""
import argparse
import atexit
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import types

HERE = Path(__file__).resolve().parent
FACT = 'out.append(f"fact: {slug} has no recorded PR; its worktree is not on this machine.")'
OLD = 'out.append(f"next: record {slug}\'s PR with status --set {slug} pr=<owner/repo>#<N>; its worktree is not on this machine.")'
MUTATIONS = {
    "ac1-old-action": ("AC-1", FACT, OLD),
    "ac1-remove-fact": ("AC-1", FACT, "pass"),
    "ac1-create-watch": ("AC-1", FACT, FACT + '\n                opts.state.write_text("{}")'),
    "ac2-guard-recorded-pr": ("AC-2", 'if not pr and meta.get("worktree") else None', 'if meta.get("worktree") else None'),
    "ac2-suppress-local-lookup": ("AC-2", "elif where:\n                ref = opened_pr(where, ask)", "elif False:\n                ref = opened_pr(where, ask)"),
    "ac2-remove-status-step": ("AC-2", 'f"next: run `spacedock status --workflow-dir {shlex.quote(str(workflow))} --set {slug} pr={ref}`.",\n                            ', ""),
    "ac2-remove-commit-step": ("AC-2", ',\n                            f"next: run `spacedock state commit {slug} --workflow-dir {shlex.quote(str(workflow))}`."', ""),
    "ac3-revert-first-case": ("AC-3", FACT, 'out.append(f"next: record {slug}\'s PR with status --set {slug} pr=<owner/repo>#<N>; its worktree is not on this machine." if slug == "journey-server-host-pilot" else f"fact: {slug} has no recorded PR; its worktree is not on this machine.")'),
    "ac3-revert-second-case": ("AC-3", FACT, 'out.append(f"next: record {slug}\'s PR with status --set {slug} pr=<owner/repo>#<N>; its worktree is not on this machine." if slug == "pr-review-lite-value-pilot" else f"fact: {slug} has no recorded PR; its worktree is not on this machine.")'),
    "ac3-add-lookup": ("AC-3", FACT, FACT + "\n                opened_pr(where, ask)"),
    "ac3-add-record-command": ("AC-3", FACT, FACT + '\n                out.append(f"next: run `spacedock status --set {slug} pr=o/r#999`.")'),
    "ac4-grow-output": ("AC-4", FACT, FACT.replace("machine.", "machine. " + "more " * 30)),
}
COMMON = {"ac4-change-workflow": "kc-dev-flow-2/references/sd/workflow.md",
          "ac4-change-mod": "kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md"}
TEMPORARY = []


def audit(event, args):
    if event == "tempfile.mkdtemp":
        TEMPORARY.append(str(args[0]))


sys.addaudithook(audit)


def mutate(repo, key):
    criterion, old, new = MUTATIONS[key]
    source = (repo / "kc-dev-flow-2/scripts/pr_watch.py").read_text()
    assert source.count(old) == 1, "mutation target must match exactly once"
    return criterion, source.replace(old, new, 1)


def execute(args):
    spec = importlib.util.spec_from_file_location("checks", HERE / "probe_checks.py")
    checks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checks)
    original_load = checks.load
    if args.one in COMMON:
        target = args.repo / ".context/pr-watch-mutations" / args.one
        target.mkdir(parents=True, exist_ok=False)
        archive = subprocess.check_output(["git", "-C", str(args.repo), "archive", "HEAD"])
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(target, filter="data")
        document = target / COMMON[args.one]
        document.write_text(document.read_text() + "\nInjected extra lifecycle passage.\n")
        print("MUTATION", args.one, "actual changed copy:", document, flush=True)
        checks.words(target)
        return 0
    criterion, source = mutate(args.repo, args.one)
    # Compile before the evidence call: syntax/import failures are not killed mutants.
    code = compile(source, str(args.repo / "kc-dev-flow-2/scripts/pr_watch.py"), "exec")
    module = types.ModuleType("mutated_pr_watch")
    module.__file__ = str(args.repo / "kc-dev-flow-2/scripts/pr_watch.py")
    original_load(args.repo)
    exec(code, module.__dict__)

    def load(repo, base=False):
        tests = original_load(repo, base)
        if not base:
            tests.watch = module
        return tests

    checks.load = load
    tests = load(args.repo)
    print("MUTATION", args.one, "criterion", criterion, flush=True)
    if criterion == "AC-1":
        return checks.unit(tests, ["test_an_empty_pr_whose_worktree_is_gone_is_a_fact_and_one_with_no_worktree_field_stays_silent"])
    if criterion == "AC-2":
        return checks.unit(tests, ["test_a_pr_a_worker_opened_is_recorded_with_two_commands_and_then_watched",
            "test_a_branch_whose_only_pr_is_closed_records_nothing",
            "test_a_bare_pr_is_resolved_from_the_workflow_checkout_when_its_worktree_is_gone"])
    if criterion == "AC-3":
        checks.real_cases(tests, args.workflow, False, args.sd_bin)
    else:
        checks.words(args.repo)
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--workflow", type=Path, required=True)
    parser.add_argument("--sd-bin", required=True)
    parser.add_argument("--one", choices=[*MUTATIONS, *COMMON])
    args = parser.parse_args()
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    if args.one:
        def save_cleanup():
            directory = HERE / "mutations"
            directory.mkdir(exist_ok=True)
            rows = [{"path": path, "exists_after_command": Path(path).exists()} for path in TEMPORARY]
            (directory / (args.one + "-cleanup.json")).write_text(json.dumps(rows, indent=2) + "\n")
        atexit.register(save_cleanup)
        try:
            result = execute(args)
        except AssertionError:
            import traceback
            traceback.print_exc()
            result = 1
        return result
    rows = []
    directory = HERE / "mutations"
    directory.mkdir(exist_ok=True)
    for key in [*MUTATIONS, *COMMON]:
        argv = [sys.executable, "-B", str(Path(__file__).resolve()), "--repo", str(args.repo),
                "--workflow", str(args.workflow), "--sd-bin", args.sd_bin, "--one", key]
        done = subprocess.run(argv, text=True, capture_output=True, timeout=120)
        output = directory / (key + ".log")
        output.write_text(done.stdout + done.stderr)
        assert "SyntaxError" not in done.stderr and "ModuleNotFoundError" not in done.stderr, done.stderr
        assert done.stdout.startswith("MUTATION " + key), "mutation never reached its evidence call"
        assert "FAILED (" in done.stderr or "AssertionError" in done.stderr, "no behavioral evidence failure observed"
        row = {"name": key, "criterion": MUTATIONS[key][0] if key in MUTATIONS else "AC-4",
               "command": argv, "exit": done.returncode, "status": "passed" if done.returncode == 1 else "failed",
               "meaning": "falsifier rejected" if done.returncode == 1 else "unexpected survival or harness error",
               "output": str(output.relative_to(HERE))}
        rows.append(row)
        print(json.dumps(row), flush=True)
    (HERE / "mutation-results.json").write_text(json.dumps(rows, indent=2) + "\n")
    return 0 if all(row["exit"] == 1 for row in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
