# Implementation evidence

The two candidate SHAs and per-file SHA-256 values are in candidates.json. Both
branches start at e8664a72b0f904e5dda3c391d52ab3abaca876b4. The combined consumer
run compares bytes from these exact candidate trees; no test assertion or
consumer contract registry changed. The approved choices are the report without
redraw, derived task refs, and filed counts beside unchanged declared progress.

## Replay inputs

Scratch copies: /tmp/opencode-story-done/replays/{relay,qnow,local}.
Relay code 0fce82296710d7bf3b89c2871adefd71db2e2957, state
77f5bb4e0e286467ec7078038e8bb9d680baddde; qnow code
ebc59cf96fdd5303e0dfccb1559d6048724e33ae, state
03838f912be5a74c972750128955524d03b5a6b6; local state 10149f1c5.
Only the scratch relay inbox-home is set done with pr-merge:999. Local originals
were fetched and otherwise read only; remote config writes are in scratch clones.

seed-replay.json compares both checker modes with the base over every task file,
excluding review-room index files. Its 298 changed verdicts add only the intended
Story refusal (135 relay, 163 qnow); local has no changed verdict. Native idle
readiness yields 31 relay and 11 qnow names. Both existing relay Story records
agree with journey-story in the default check.

progress-replay-result.json and AC1-before/after.stdout show the status control,
release-only work and report bounds. Old-field projections and release-walk due
output are equal to the pinned base for both maps. The successful CLI snapshots
were retained while the comparison harness was corrected to allow absent release
keys; the rest of the driver ran with REUSE_OBSERVATION=1. Product bytes did not
change between observation and commit.

Earlier relay reads hit the unchanged 30-second deadline while other work ran.
The later sequential baseline and candidate traces both read successfully; no
limit was raised. The isolated canvas initially hit sandbox EPERM and passed
when its local socket bind was allowed. Neither environment failure is product
acceptance evidence; final successful outputs are retained separately.

## Mutations and tests

mutations.json records 11 rejected reverse mutations, remaining-mutations.json
adds three (unchanged consumer assertion, missing ADR and workflow edit), and
AC12-force-all-workflows.json records the 230-task counterexample. The archive
status change is a separate native fixture control. replay-falsifiers.json also
shows the real relay mutant changing continuity-latest acceptance and counting
agent-reviews-from-link as 3 declared tasks rather than 6 filed tasks. All Python mutant runs use
python3 -B and fresh copies with cache directories omitted/cleared.

The consumer sample was wrong to be called unchanged in the design: its existing
whole-document assertion rejects additive producer fields. Captain amendment 1
allowed only the sample update; the unchanged 122-test suite passes against the
pair. An extra unrecorded producer field still fails that same assertion.

The logs show 21 producer tests, 222 design tests (4 pre-existing conditional
skips), 136 watch tests, 125 dispatch-record tests (1 conditional skip), and 122
consumer tests. Skill lint, ADR lint, fresh-reservation number guards and comment
ratio passed. AC-10 is future acceptance after release and rollout, not claimed
passed. RoboRev, product push, PR creation and hosted CI were delegated and not run.
CI cost was not measured; workflow definitions did not change.

## Reproduction entry

verify.sh takes five explicit paths: producer worktree, dev2 worktree, local relay
clone, local qnow clone, and the dispatched kc-dev-flow-2 0.38.1 package. It checks
both exact heads and clean trees, creates new scratch clones, then uses the
included scripts. Requires Node >=22.13, the producer's npm-ci dependencies,
Spacedock 0.27.2 on PATH, Python >=3.12, Git and a permitted loopback socket for
the existing canvas test. It never pushes. The wrapper was syntax checked;
its component tests/replays/mutations were run as recorded, but the assembled
wrapper was not run end to end.
