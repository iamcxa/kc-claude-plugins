# Validation-1 raw results (scratch exports of merge commits via git archive; python3 -B)

Independent count (count.py: ast diff of test methods, merge^ vs merge): N 858=1 (1 added, 0 mod; the implementation counts the rename as modified), 860=6, 859=0, 861=8, 870=22; total 37.
Flagged test (870) run alone: OK (passes). Probe 1 `ask '  '` no --by: stderr "ask needs --by ..." exit 2. Probe 2 with --holds task --by x: "question needs nonempty asked and holds ...".
Executed mutation, scratch copy only: validate_revision blank-question raise replaced by `pass`: the flagged test still OK; the blank ask is recorded ("Recorded ask demo#1").
Falsifiable-sample mutations: revision +1 check removed -> test FAILED; unknown-event raise removed -> FAILED; missing-owner branch disabled -> FAILED; 860 sibling-name resolution removed -> 4 TaskArgumentTests failures.
Unflagged sample run (all OK): 6 task_timeline, 3 observer_check, 5 design_surfaces tests.
adr_lint.py <export>/docs/adr --root <export>: exit 0 (79 ADR files, no changes expected).
Evidence checksums of implementation-1 re-verified: shasum -a 256 -c SHA256SUMS, 0 mismatches.
