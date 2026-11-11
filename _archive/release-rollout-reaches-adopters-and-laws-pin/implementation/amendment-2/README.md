# Captain amendment 2

Candidate: `ba98f3ca95c1f879bf460fbb08976f337e18c4c8`.
Previous candidate: `a1a35a714510683a44a2ac5ec02241e7cb354f80`.
Original base: `e8664a72b0f904e5dda3c391d52ab3abaca876b4`.

The Captain's recorded choice is in task amendment 2. It leaves AC-4 unchanged
and adds only AC-12: a row owing both updates says the merge order itself.
`criteria-before.json` and `criteria-check.json` record that every earlier
criterion block, including superseded blocks, is byte-identical.

`tests-before.log` records exactly one failure: the missing order in the new
both-owed fixture. `tests.log` records 18 passing package_version tests.
`proof-results.json` covers the missing-order mutation, five literal byte/exit
comparisons with the previous candidate and the both-owed example (16 words).
The suffix adds six words only to a both-owed row; documents and other lifecycle
moments are unchanged from the earlier candidate. The actual 11-row live output
is byte-identical for listed rows and remains 112 words; the full output is kept
at the private /tmp path in `live-summary.json` rather than committed here.

Reproduce this round's fixture and mutation controls:

```sh
python3 -B prove.py /absolute/path/to/the/candidate-worktree
```

The original eight mutations and eight legacy stdout comparisons were rerun at
this candidate. Their runner and rejection logs are in `original-proofs/`:

```sh
python3 -B original-proofs/prove.py /absolute/path/to/the/candidate-worktree
```

`checks.json` records current check exits and delegated checks not run here.
`docs.json` lists ADR 0075 and maintain-flow; both are unaffected by this follow-up:
the existing reporting comparison and post-merge execution rule remain intact,
and the new line makes that existing sequence explicit. No new ADR decision,
package document, list file, law, CI workflow or version was introduced.
The earlier review's real-checker version-skew probe remains under review-1725;
this round does not repeat it or claim model/hosted behavior verification.
