#!/usr/bin/env python3
"""Append the complete repair report after the exact-candidate checks finish."""
import json
from pathlib import Path
import subprocess

here = Path(__file__).resolve().parent
task_dir = here.parents[1]
entity = task_dir.parent / "dispatch-build-writes-the-dispatch-record.md"
candidate = (here / "fresh/candidate.txt").read_text().strip()
package = json.loads((here / "package-tests/results.json").read_text())
assert len(package) == 28 and all(row["exit"] == 0 for row in package)
assert all(row["status"] == "passed" for row in json.loads((here / "preservation-falsifiers-committed/results.json").read_text()))
assert all(row["status"] == "passed" for row in json.loads((here / "fresh/falsifiers/results.json").read_text()))
seam = json.loads((here / "fresh/dispatch-stage.json").read_text())
assert len(seam) == 12 and all(row["status"] == "passed" for row in seam)
initial = Path("/tmp/spacedock-dispatch/5c030106-8d82-4542-855e-1498b2563c69-spacedock-ensign-dispatch-build-writes-the-implementation.md").read_text()
original = [line for line in initial.split("### Completion checklist\n", 1)[1].split("### Summary", 1)[0].splitlines() if line.strip()]
followup = (task_dir / "dispatch/implementation-1-message-3.md").read_text()
repair = [line.split(". ", 1)[1] for line in followup.split("## Checklist\n", 1)[1].split("## Scope notes", 1)[0].splitlines() if line[:1].isdigit()]
assert len(original) == 4 and len(repair) == 3
rows = []
def item(status, title, evidence):
    rows.extend([f"- {status}: {title}", f"  {evidence}"])
item("SKIPPED", original[0], f"PR #812 exists on the earlier head; repaired candidate {candidate} is committed locally on spacedock-ensign/dispatch-build-writes-the-dispatch-record, parent afa4523468a2e86e6c6e0467591df00bf8e51d35, base 334d91e3165953b2ca7191e3308d80b6c02c4a99. FO owns pushing the new head and the review reply; no product push or PR write performed.")
item("DONE", original[1], "ADR 0070 and its protected pointer are unchanged; the candidate's ADR linter passes. The repair changes the writer and its seam test only; follow-up 1's observer correction and follow-up 2's linter substitution remain intact.")
item("SKIPPED", original[2], "All local acceptance checks and original thirteen falsifiers pass at the new head; three preservation falsifiers also fail as intended. Hosted AC-8 and independent validation on this repaired head are not run; the earlier validation/CI evidence applies to afa4523468a2e86e6c6e0467591df00bf8e51d35 only.")
item("SKIPPED", original[3], "Installed 0.35.0 ADR lint retains the known pre-#806 false positive; the previously authorized candidate linter passes. New-head publication, RoboRev and hosted CI remain FO-owned; CI cost per PR is not measured, and its configuration/triggers did not change.")
item("DONE", repair[0], f"Reproduced all three data-loss cases against the reviewed writer (repair-1/regressions-before.log), then committed {candidate}; repair-1/preservation-falsifiers-committed restores that old writer and rejects it separately for each regression.")
item("DONE", repair[1], "select_record checks the index, then opens the target with exclusive creation; main reports FileExistsError and the path before checking/building. The existing wrote flag now marks a newly created file, so cleanup does not own a pre-existing file; committed identical retry reuse remains unchanged.")
item("DONE", repair[2], f"repair-1/fresh/dispatch-stage.json: 12 passes, including different staged/worktree bytes and an index-only path. All 28 checked-in CI Python commands exit 0 ({sum(row['tests'] or 0 for row in package)} tests reported, {sum(row['skipped'] for row in package)} skipped); repair-1/package-tests/results.json and per-command logs. The final seam file also passes dispatch-stage-final.log. Original acceptance.sh rerun in a fresh bash shell exits 0 at {candidate}; no PR reply or product push.")
item("DONE", "AC-1 through AC-4: complete committed records still carry received input, and malformed dispatches still hold before build.", "repair-1/fresh/dispatch-stage.json and original no-stamp/no-model/dropped-line/no-cleanup/build-before-check/ignored-checker mutants pass their rejection controls; pre-existing records now hold before the checker too.")
item("DONE", "AC-5 and AC-6: owned failure cleanup, committed retry numbering, later rounds and advance envelope/commit boundaries remain covered.", "The seam suite and original failure/reuse/commit mutants pass. Per follow-up 3, a pending record after advance commit failure is now preserved and refused; the test commits it via real spacedock state commit, then verifies identical committed reuse succeeds.")
item("DONE", "AC-7: approved README passages, delta=-2 budget and existing dispatch consumers remain valid.", "repair-1/fresh/: lint-skills.log 5931/5931; 47 lint tests and 115 record tests pass without skips; test_sd_dispatch.py exits 0; restored-base-passages falsifier still fails. Workflow prose is unchanged by this repair.")
item("DONE", "AC-8 local wiring: real-binary step and missing-binary hold are preserved.", "repair-1/fresh/falsifiers retains CI-step deletion and unset-SPACEDOCK_BIN controls; real 0.27.2 seam/integration tests pass locally. The new head's hosted CI is not run by this worker.")
ratio = (here / "fresh/comment-ratio.log").read_text().splitlines()[0]
item("DONE", "Required local gates, candidate preservation and document dispositions.", f"repair-1/fresh/: candidate ADR lint, number guards and diff check exit 0; comment ratio: {ratio}, below 5%. Design surfaces are presentable (scope scan not run at validation); doc_impact exits 0. repair-1/doc-impact-verdicts.json covers every listed document against the original base; this repair edits no document, ADR or version and changes no diagram.")
item("SKIPPED", "RoboRev and new-head external review/CI/independent validation.", "roborev not run: FO owns the review and publication handoff. This worker leaves the product branch local and posts nothing to PR #812; prior-head validation is not claimed for the repaired head.")
report = "\n## Stage Report: implementation\n\n" + "\n".join(rows) + "\n\n### Document dispositions\n\n"
docs = json.loads((here / "doc-impact-verdicts.json").read_text())
report += "\n".join(f"- `{row['doc']}` — {row['verdict']}: {row['reason']}" for row in docs)
report += ("\n\n### Summary\n\n"
           f"Repaired the existing-record data-loss finding at {candidate}; untracked, staged and index-only records are refused without changing file bytes, index entries, task bytes or state HEAD. "
           "This complete implementation report supersedes the earlier implementation report, including its automatic retry over a pending uncommitted record; new-head CI, review response and independent validation remain FO-owned.\n")
(here / "stage-report.md").write_text(report)
assert f"Repaired the existing-record data-loss finding at {candidate}" not in entity.read_text()
with entity.open("a") as output:
    output.write(report)
print(json.dumps(dict(candidate=candidate, lines=len(report.splitlines()))))
