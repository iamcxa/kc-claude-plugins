# Repair evidence

Candidate ad41870b72f19d8ad141efaa67cda3afb23f1d4d; local commits only.
commands.json joins commands, exits and saved output. ci-tests-final.json contains
all 29 passing file entrypoints; test-summary-final.json separates unit cases,
optional skips and native scripts. The CI file invocations came from the product
worktree; independent files ran in up to four processes and native tests in order.

Six new regression methods reject the original checker; six isolated in-memory
guard mutations fail their owning test. A mutation harness exit 0 means expected
rejection, not a repaired-candidate test failure. Initial CI/fixture and evidence
collection failures remain: the first suite stopped after 13 completed commands;
the intermediate POC retry also failed until empty-observation configuration was
made consistent. The original baseline grouping counted two subcases separately;
final grouping verifies six failing methods, seven subcases, and zero errors.

Reproducers use PRODUCT_WORKTREE and task-owned TMPDIR. Set SPACEDOCK_BIN to the
assigned 0.27.2 binary; obtain mods/pr-merge.md from the workflow's pinned Spacedock
commit (native-provenance.json gives its digest) under <scratch>/sd-plugin/mods.
Run the direct Python entrypoints in commands.json from the clean candidate.
The archived replay/round probes require the task's public state/archive inputs;
their limits are recorded in replays.json and live.json. No real merge or gate
approval occurred. Live API reads first failed under the sandbox, then succeeded
with authorized network access; check/question still held. No review was requested.

Counts use git object bytes. No dynamic lifecycle, speedup or CI cost measurement
is claimed. normalization.json maps raw hashes to path-normalized retained bytes.
