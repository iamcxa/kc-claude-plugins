"""Run fresh, bytecode-free behavioral checks and reverse mutations.
Usage: python3 -B mutate.py CODE_ROOT STATE_ROOT OUT
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile
code, state, out = map(pathlib.Path, sys.argv[1:])
out.mkdir(parents=True, exist_ok=True)
source = (code / "kc-dev-flow-2/scripts/merge_audit.py").read_text()
tests = (code / "kc-dev-flow-2/scripts/test_merge_audit.py").read_text()
mutations = [
 ("release-removed", [('if pr["headRefName"].startswith("release-please--branches--"):', 'if False:')],
  "test_producer_names_and_a_renamed_release"),
 ("pr-number-only", [('if any(head.startswith(h) for h, source in recs):', 'if recs:')],
  "test_matching_head_is_carried_and_different_head_is_a_finding"),
 ("kind-before-record", [('if any(head.startswith(h) for h, source in recs):', 'if named_kind(pr) is None and any(head.startswith(h) for h, source in recs):')],
  "test_recorded_release_reads_carried_before_kind"),
 ("records-at-to", [('def read_state(state, repo):', 'def read_state(state, repo, end):'),
                    ('read_state(state, repo)', 'read_state(state, repo, end)'),
                    ('tree(state, sha)', 'tree(state, end)')],
  "test_record_committed_after_to_is_carried_but_uncommitted_record_is_not"),
 ("collapse-removed", [('if any(token in text for text in reports):', 'if False:')],
  "test_repeats_collapse_only_from_another_committed_report_at_to")
]
results = []
for name, edits, case in [("baseline", [], None), *mutations]:
    mutated = source
    for old, new in edits:
        assert old in mutated, (name, old)
        mutated = mutated.replace(old, new)
    with tempfile.TemporaryDirectory(prefix="merge-audit-fresh-") as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / "merge_audit.py").write_text(mutated)
        (tmp / "test_merge_audit.py").write_text(tests)
        command = [sys.executable, "-B", str(tmp / "test_merge_audit.py")]
        if case:
            command.append("MergeAuditTest." + case)
        proc = subprocess.run(command, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        (out / (name + ".log")).write_text(proc.stdout + proc.stderr)
        expected = 0 if not case else 1
        assert proc.returncode == expected and (not case or "FAIL:" in proc.stderr), (name, proc.returncode, proc.stderr)
        if name == "release-removed":
            bindir = tmp / "bin"
            bindir.mkdir()
            fixture = state / "observer-lists-unasked-merges/poc/merged-window.json"
            (bindir / "gh").write_text("#!" + sys.executable + "\nimport pathlib\nprint(pathlib.Path(" + repr(str(fixture)) + ").read_text())\n")
            native_git = shutil.which("git")
            (bindir / "git").write_text("#!" + sys.executable + "\nimport os,sys\n"
                "if 'fetch' in sys.argv[1:]: sys.exit(0)\n"
                "os.execv(" + repr(native_git) + ", [" + repr(native_git) + "] + sys.argv[1:])\n")
            for executable in bindir.iterdir():
                executable.chmod(0o755)
            replay = subprocess.run([sys.executable, "-B", str(tmp / "merge_audit.py"), str(state),
                                     "merge-check-reads-two-pr-tasks", "--rev", "8ffd6dfa3e021c1967aeaeabd7cf0cb61db48aae"],
                                    capture_output=True, text=True,
                                    env={**os.environ, "PATH": str(bindir) + os.pathsep + os.environ["PATH"],
                                         "PYTHONDONTWRITEBYTECODE": "1"})
            (out / "release-removed-snapshot-replay.log").write_text(replay.stdout + replay.stderr)
            assert replay.returncode == 1 and "no ask record: #707 head " in replay.stdout, replay.stdout
        results.append({"name":name, "status":"passed", "message": "All behavioral checks passed" if not case else "Mutation rejected by " + case})
(out / "results.json").write_text(json.dumps(results, indent=2))
print("Fresh baseline (17 tests) and all five reverse mutations passed; release removal exposes #707 in the saved PR snapshot.")
