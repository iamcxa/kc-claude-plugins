# Final implementation evidence — 2026-11-09 UTC

Candidate: 90f43f801be3d03ebd7d98d1a41ad78801aea54d
Base: 82c9e67ae892b80647c3f6a8b6929f993e42dbc2
Branch: spacedock-ensign/counts-name-the-run-that-produced-them

verification.json binds the required producers to this unchanged candidate. Each command has its argv, cwd, start/end time, captured process PID, exit, log and hash in its matching JSON. These are local implementation checks, not independent validation, RoboRev, CI, publication or adoption proof.

- suite.log/suite.json: the complete unittest discover command, with SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock explicitly set as dispatched. The raw summary is Ran 1050 tests; OK (skipped=7), not 1050 non-skipped passes.
- mutations.log: deliberately removed learn join, number-in-file comparison, automatic writer, PR-body scan and POC automatic writer. The selected tests fail with exit 1 and no import errors in disposable copies under the assigned worktree; python3 -B and absent bytecode caches are asserted. The mutation driver exits 0 when those falsifiers work.
- words.log: a separate recount of base and candidate files plus actual gate stdout. Startup is unchanged. The tool writes the disclosure into its input text rather than printing an extra copy to the operator.
- gate-replay.log and learn-replay.log: the final shared pattern against pinned ideation state revisions and completed local learn records. Their headers identify the script bytes, candidate, date and pattern hash. replay-differences.json explains the extra heading-shaped 1 FO line refusal, P1/S1 no longer serving as standalone 1, removed passed/items forms, added checks, and removal of the comma defect. The source issue's adopter record is not on this machine.
- identity.json: the nine delivered files. The additional POC test file is authorized by dispatch/implementation-1-message-2.md; its change is confined to expected forwarded bytes, retaining wrong-summary and failure holds. Removing the automatic write makes that test fail.
- document-verdicts.json: each document reported by doc_impact.py has an updated or unaffected verdict.

The earlier implementation-2 folder contains investigation and superseded hold evidence. Its old full-suite attempts are not accepted final-head proof. Product push, Draft PR creation, RoboRev and CI are delegated to FO and were not run by this worker. CI cost was not measured; no CI workflow changed.
