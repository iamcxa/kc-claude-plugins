# Implementation evidence

Candidate `455846c6d30d4ab650c1c4503bc591722231586d`, stacked on
`77e240d46ced4980ec1f6f2dc61a692f27857af1` (PR #854).
Only the two named Python files and ADR 0081 changed. No versions or CI
configuration changed. Product publication, RoboRev and hosted CI are not run.

## Result and decision needed

NP-3 fails: the exact approved fact-line shape adds **32 words**, above the
**30-word** increase bound. The frozen state has 14 held tasks across three
stages; the design's ten ideation tasks are a subset. `held-fact-word-count.json`
records every counted token. `words.json` records the observed full totals;
those runs include retained environment diagnostics, so they are not a clean
comparison. The one-line count itself is independent of those diagnostics.
No shortening or increased bound was implemented. FO must return the bound or
wording decision through the workflow before a repair.

The real workflow entrance was also exercised with public GitHub read access:
`real-workflow-tasks.log`, exit 0. It prints the same 14-task held fact and the
missing-Held prompt. `actual-state-counts.json` records counts only: 0 valid of
14 Held sections, including the ten ideation tasks. These body edits remain
FO-owned; the journey-canvas task is left untouched under its own ruling.
NP-4 is only a scratch projection, not completed live-state acceptance. NP-5
(the plain upstream status display) is intentionally not implemented under D2.

## Tests and falsifiers

`unit-tests.log` records 164 pytest items passed. `unit-tests.xml` expands
subtests into 250 JUnit entries, with zero failures or errors. The test scope
is `test_pr_watch.py` plus `test_scratch.py`, not the whole package suite.
`mutation-tests.json` and `mutation-*.log` record five behavior mutations plus
removal of the candidate, each rejected by the tests with exit 1. The runs use
Python `-B`, disable bytecode writes and clear scratch `__pycache__` directories.

`acceptance.py` rebuilds origin-less snapshots and runs AC-1 through AC-7 and
the candidate checks. Requirements: git, Python 3.11 with PyYAML and pytest,
Spacedock 0.27.2 and gh for read-only public PR queries. The explicit arguments
are in `commands.json`; checkout paths and the scratch path are caller inputs.
For another run, choose an empty scratch path and an evidence directory next
to the retained `ideation/` directory. It returns 1 here because NP-3 fails and
the full origin-less tasks runs return 2. Their output retains both the
inherited scratch sweep's missing-origin diagnostic when `/tmp/dev2` exists,
and the sandbox GitHub connectivity diagnostic. Neither is repaired here.
The new held-line predicates pass; a clean full entrance is separately proven
by the real-workflow run above.

`falsifiers.py --build EVIDENCE SCRATCH` records the observed data and mutated
data, then starts a fresh Python `-B` checker process for each. Each mutated
case exits 1; the unmodified NP-3 case also exits 1, exposing the actual defect.
`falsifiers.json` records all 20 process outcomes. AC-4/AC-5 mutations change
the recorded exit observations, not the Spacedock binary; AC-6 removes the
actual successor attempts, and AC-7 changes an actual quote by one character.
The script's rejection checks are acceptance-oracle sensitivity, not new
claims about upstream behavior. Candidate behavior mutations are separate.

## Other checks

Skill lint, design-surfaces, ADR lint requiring 0081, number guards and comment
ratio pass. `number-guards.log` retains the first sandbox fetch warning;
`number-guards-fresh.log` is the successful rerun with refreshed state refs.
`adr-quote-check.json` verifies the ADR's relevant passage against the bound
ideation ruling. `doc-impact.json` lists only ADR 0081, disposition `updated`.
The added-comment ratio is 0.7%, below 5%. CI cost is not measured.

`open-pr-fresh.json` is an empty open-PR lookup for this task branch. The first
sandbox API failure is retained in `open-pr-error.log`. No product branch was
pushed and no PR was opened. `prepared-pr.md` is the prepared title and body;
FO's retained copy is `/tmp/impl-held-and-closed-tasks-leave-the-design-queue-pr.md`.

`identity.json` pins the candidate and source hashes. `cleanup.json` records
the exact removed scratch root and generated dispatch path after evidence was
committed. That file and the final stage report are committed separately from
the evidence so scratch removal follows evidence retention.
