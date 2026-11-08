#!/usr/bin/env python3
import json
from pathlib import Path

here = Path(__file__).resolve().parent
entity = here.parent.parent / "dispatch-build-writes-the-dispatch-record.md"
dispatch = Path("/tmp/spacedock-dispatch/5c030106-8d82-4542-855e-1498b2563c69-spacedock-ensign-dispatch-build-writes-the-implementation.md").read_text()
items = [line for line in dispatch.split("### Completion checklist\n", 1)[1].split("### Summary", 1)[0].splitlines() if line.strip()]
assert len(items) == 4
candidate = (here / "fresh/candidate.txt").read_text().strip()
rows = []
def item(status, title, evidence):
    rows.extend([f"- {status}: {title}", f"  {evidence}"])
item("DONE", "Bounded integrated implementation committed locally on the assigned branch, based on origin/main.",
     f"Candidate {candidate}; base 334d91e3165953b2ca7191e3308d80b6c02c4a99; branch spacedock-ensign/dispatch-build-writes-the-dispatch-record; nine authorized files; clean code worktree; implementation/candidate-tree.txt.")
item("SKIPPED", items[0], "No PR opened: no push grant. Product push and Draft PR are FO-owned; /tmp/impl-dispatch-build-writes-the-dispatch-record-pr.md is ready, also saved as implementation/prepared-pr.md; no version edits.")
item("DONE", items[1], "ADR 0070 quotes 「核准（建議）」 and the task gate's D1/D2/D3 question excerpt, recorded 2026-11-07T15:37:23.875685Z; it protects dispatch_stage.py main with its ADR pointer.")
item("SKIPPED", items[2], "AC-1 through AC-7 and AC-8 local wiring/binary checks pass; hosted AC-8 PR run is not run, delegated to FO. All thirteen local counterexamples are caught; implementation/fresh/falsifiers/results.json and adjacent mutation patches/logs.")
item("DONE", "AC-1 through AC-4: stamp commits a complete record with received inputs; incomplete records and invalid/missing candidates hold before building.",
     "implementation/fresh/dispatch-stage.json: real 0.27.2 split-root seam tests; no-stamp, no-model, dropped-scope-line, skipped-removal, build-before-check and ignored-checker mutants fail their corresponding assertions.")
item("DONE", "AC-5 and AC-6: failed/repeated builds and reuse-advance dispatches preserve the intended record/commit boundary.",
     "The same real-binary suite checks immediate reuse, changed checklist, intervening state commit, staged-record cleanup, advance commit and withheld envelope on commit failure; no-removal, no-reuse, bytes-only reuse and no-state-commit mutants fail.")
item("DONE", "AC-7: three README passages match the approved text, delta=-2, and the updated consumers pass.",
     "implementation/fresh/: lint-skills.log 5931/5931, test-lint-skills.json 47 passes, dispatch-records.json 115 passes, sd-dispatch.log exit 0; restored-base-passages mutant fails at 5933 versus 5931. lifecycle-words.json: startup 5933→5931, fresh dispatch 116→101, follow-up 147→87.")
item("DONE", "AC-8 local source and binary checks: CI runs the real seam test after installing the pinned binary and an unset SPACEDOCK_BIN fails.",
     "implementation/fresh/falsifiers/: deleting the step removes the seam command; missing-binary log exits 1 naming SPACEDOCK_BIN. Existing package/workflow path triggers retained; CI cost per PR not measured; hosted run not run.")
item("SKIPPED", items[3], "The installed 0.35.0 ADR command exits 1 on the base's known pre-#806 historical-assertion false positive (adr-lint.log, base-adr-lint.log). Follow-up 2 substitutes the candidate's corrected ADR linter; product publication, RoboRev and hosted CI remain FO-owned.")
item("DONE", "Required local gates and fresh-shell exact-candidate acceptance.",
     "SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock SD_PLUGIN_ROOT=/tmp/spacedock-0272-source bash --noprofile --norc implementation/acceptance.sh <code-root> <candidate> <output> exited 0; fresh/adr-lint.log, number-guards.log and diff-check.log pass; comment-ratio.log 0.9% ≤ 5%. The runner uses git archive, python3 -B and no exported caches; goal-without-change.log shows the missing base writer.")
item("DONE", "Implementation follow-up 1: change only the observer chat-only command entry forced by the shortened README command.",
     "Extra file kc-dev-flow-2/skills/observer/SKILL.md authorized in dispatch/implementation-1-message-1.md; lint-skills.log exit 1 before, lint-skills-after-observer.log exit 0 after. No additional observer test pin names that entry.")
item("DONE", "Implementation follow-up 2: keep the historical ADR 0047 assertion unchanged and use the candidate ADR linter.",
     "dispatch/implementation-1-message-2.md names merged #806 and its linter correction; `python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since <base> --require 0070` exits 0; the installed command's exit 1 is retained, not called clean.")
item("SKIPPED", "RoboRev review before publication.", "roborev not run: FO runs RoboRev after this report because the worker sandbox cannot reach the local daemon; no review, PR comment, ready action or merge performed.")
item("DONE", "Affected documents checked with doc_impact.py <base> <candidate> --repo <code-root> --json.", "implementation/doc-impact.json and doc-impact-verdicts.json cover every listed document; dispositions follow. Workflow prose and the observer entry are updated; no affected diagram changes.")
docs = json.loads((here / "doc-impact-verdicts.json").read_text())
report = "\n## Stage Report: implementation\n\n" + "\n".join(rows) + "\n\n### Document dispositions\n\n"
report += "\n".join(f"- `{row['doc']}` — {row['verdict']}: {row['reason']}" for row in docs)
report += ("\n\n### Summary\n\n"
           f"Implemented and locally committed {candidate}, with a fresh export acceptance run and thirteen caught falsifiers. "
           "The approved package wrapper owns record writing/checking/build order; model/roster flags and the two preflights retain their existing ownership. "
           "Prepared PR text and all local evidence are ready for FO; product publication, hosted CI, RoboRev and independent validation are not run by this worker.\n")
(here / "stage-report.md").write_text(report)
assert "## Stage Report: implementation" not in entity.read_text()
with entity.open("a") as output:
    output.write(report)
print(json.dumps(dict(report_lines=len(report.splitlines()), entity_lines=len(entity.read_text().splitlines()), candidate=candidate)))
