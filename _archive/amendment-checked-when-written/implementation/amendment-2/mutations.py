import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

wt = Path(sys.argv[1]).resolve()
out = Path(__file__).resolve().parent
cases = [
    ("reuse", "scripts/design_surfaces.py", "reused = tuple(sorted(held & declared))", "reused = ()",
     ["test_laws_check.L4Test.test_reused_id_and_unmarked_replacement_each_have_their_own_line"]),
    ("marker", "scripts/design_surfaces.py", "if named and not waiver and not any", "if False and not any",
     ["test_laws_check.L4Test.test_reused_id_and_unmarked_replacement_each_have_their_own_line",
      "test_design_surfaces.AmendmentTests.test_superseding_entries_need_a_criterion_with_the_amendment_phrase"]),
    ("payload", "scripts/design_surfaces.py", "        if entry.payload is None:\n            continue\n        held =",
     "        if False:\n            continue\n        held =",
     ["test_laws_check.L4Test.test_record_only_marked_move_and_waived_move_are_green"]),
    ("parent", "scripts/laws_check.py", "previous = set(move_defects(before))", "previous = set()",
     ["test_laws_check.L4Test.test_defect_is_reported_at_introduction_not_later_edits_or_repair"]),
    ("heading", "references/sd/laws.md", "## L4 amendment-moves-use-fresh-ids", "### L4 amendment-moves-use-fresh-ids",
     ["test_laws_check.RegistryTest.test_laws_file_matches_registry"]),
]
cases += [
    ("whole-file-entry-skip", "scripts/design_surfaces.py",
     "    entries = [entry for entry in entries\n               if not any(entry.start < line <= entry.end for line, _ in issues)]",
     "    if issues:\n        return []",
     ["test_laws_check.L4Test.test_unrelated_broken_entry_does_not_hide_valid_move"]),
    ("whole-file-parent-skip", "scripts/laws_check.py",
     "            previous = set(move_defects(before))",
     '            if __import__("design_surfaces").parse_amendments(before)[1] or __import__("design_surfaces").parse_amendments(after)[1]:\n                continue\n            previous = set(move_defects(before))',
     ["test_laws_check.L4Test.test_repaired_heading_reports_previously_unjudged_defect"]),
    ("judge-broken-entry", "scripts/design_surfaces.py",
     "    entries = [entry for entry in entries\n               if not any(entry.start < line <= entry.end for line, _ in issues)]",
     "    entries = entries",
     ["test_laws_check.L4Test.test_structural_issues_are_left_to_existing_laws"]),
]
rows = []
for name, file, old, new, tests in cases:
    with tempfile.TemporaryDirectory(prefix="amendment-mutation-") as tmp:
        pkg = Path(tmp)
        shutil.copytree(wt / "kc-dev-flow-2/scripts", pkg / "scripts", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (pkg / "references/sd").mkdir(parents=True)
        shutil.copy(wt / "kc-dev-flow-2/references/sd/laws.md", pkg / "references/sd/laws.md")
        path = pkg / file
        source = path.read_text()
        assert source.count(old) == 1, (name, source.count(old))
        path.write_text(source.replace(old, new))
        assert not list(pkg.rglob("*.pyc"))
        for n, test in enumerate(tests):
            log = out / f"mutation-{name}-{n}.log"
            with log.open("w") as stream:
                result = subprocess.run([sys.executable, "-B", "-m", "unittest", test], cwd=pkg / "scripts",
                                        stdout=stream, stderr=subprocess.STDOUT,
                                        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            text = log.read_text()
            assert result.returncode == 1 and "FAIL:" in text and "ERROR:" not in text, (name, text)
            rows.append({"name": name, "test": test, "exit": result.returncode, "status": "passed", "log": str(log)})
        if name in ("reuse", "marker"):
            state = "/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state"
            readme = str(Path(state).parent / "README.md")
            result = subprocess.run([sys.executable, "-B", str(pkg / "scripts/laws_check.py"), state,
                                     "--before", "b91e7434adde", "--after", "a113aa3e9", "--readme", readme],
                                    capture_output=True, text=True)
            (out / f"mutation-{name}-bite.log").write_text(result.stdout + result.stderr)
            defect = "reused ids:" if name == "reuse" else "unmarked replacement"
            other = "unmarked replacement" if name == "reuse" else "reused ids:"
            assert defect not in result.stdout and other in result.stdout, result.stdout
(out / "mutations.json").write_text(json.dumps(rows, indent=2) + "\n")
print(f"{len(rows)} mutation checks rejected the injected regression")
