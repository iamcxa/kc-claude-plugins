# Implementation evidence for Captain amendments 1 and 2

Read `artifact.json` for the exact product revision, `acceptance.json` for criterion status, and `stage-report.md` for claims and named falsifiers. `corpus-inputs.json` pins the three local state histories and README paths; `corpus-*-exit.json` records the full commands and exit codes. The complete historical laws runs exit 2 for existing L3 history debt; `corpus-reconciliation.json` separates the seven expected L4 events from that debt.

To verify the stored corpus outputs, run `python3 -B verify-corpus.py` from this directory. To reproduce execution without overwriting these records, copy this directory to scratch, then run `python3 -B run-corpus.py <candidate-worktree> <scratch>/corpus-inputs.json <dev2|qnow|relay>` for each named history. The script refuses a worktree at a different candidate. Run `python3 -B mutations.py <candidate-worktree>` in the scratch copy to repeat the named mutation controls; temporary package copies are used with caches absent.

The product repository owns the named unit tests. `red.log` demonstrates the prior candidate fails the three added regressions. `criterion-move.json` and `superseded-ac-4.md` record the verbatim criterion move. No hosted activation, RoboRev, product push or PR creation is claimed here.
