# Implementation 3 evidence

Product branch: spacedock-ensign/merge-ask-is-produced-from-records.
Candidate: 5e9afd496a6901cc788252a77d84f355acbf0015.
Base: c2f035b6612f5edb42220576b3414e993531ffd6.
Merge commit: 57f796175985d1f5e0bab90cbffe96614ead17c6 (parents preserve the pushed candidate and origin/main; no rebase).

All retained sources are public repository metadata or synthetic/local fixture observations. Product, state, package and scratch paths are normalized in logs. No private task body, reviewer prose, credential or personal data is retained. Public archived input bodies remain in the state checkout identified by provenance.json; scripts name those inputs rather than copying them here.

## Main checks

- ci-tests-final.json joins every CI-listed direct Python command to its exact candidate, exit and log. run_ci.py reads the repository workflow rather than maintaining a second command list. All commands use python3 -B, PYTHONDONTWRITEBYTECODE=1, and task-owned TMPDIR. Native scripts use Spacedock 0.27.2 and unmodified mods/pr-merge.md from the workflow's pinned public commit. This is local macOS evidence, not hosted Linux CI.
- shared_guards.py runs passing producer controls, then eight question-only counterexamples through both readers. It refreshes facts digests to isolate the selected guard. Disabling that one shared guard makes both unsafe inputs pass; shared-guard-mutations.json retains both exits and diagnostics. No product bytes are mutated.
- parity-final-3.log runs the six existing confirmed regression classes through text and record inputs. Legacy summary fields/refusal placement and facts-record digests remain explicit format differences; the record-only unread decision is not asserted as a new legacy requirement.
- question-shape.json records the one final return and the single calls to the common guards. This is structural evidence, supplementary to the behavioral mutations.

## Acceptance and falsifiers

round2_probe.py replay joins two real public archived task/report/dispatch inputs to controlled provider observations, unchanged FO question bytes and native local gate preparation. A fresh-shell fixture reads the report; historical acceptance commands are not executed. replays.json records equal bound-summary and record digests. The current-main question-only control holds because it still requires a factual summary (goal-check.json).

round2_probe.py live performs actual read-only public GitHub queries. The saved observation is held; check and question both exit 1. Direct native preparation is a separate local JSON transport experiment, not a passing delivery preflight or approval. The first sandbox network failure and the authorized retry are retained.

candidate_mutations.py restores manual-summary requirements, writes a held observation as ask-N.json, and replaces each dispatched head after a passing control. Each mutation is detected. goal_and_mutation.py restores local-job round counting; all three real inventories fail. round2_probe.py rounds retains the corrected counts and duplicate-read control. Historical reviewer identities remain FO-recorded inputs, not authenticated event-time history.

## Earlier attempts and boundaries

delivery-first.log retains the initial complete delivery test attempt: two stale source-mutation anchors failed after the refactor. Those mutation checks were retargeted, not deleted. Focused parity attempts retain the legacy refusal-fixture location correction. ci-before-pointer-finalization.json/log retain the preliminary CI run stopped to restore two required ADR pointers and rerun at the final commit; it is not a complete suite claim. adr-lint.log retains the initial pointer failure; adr-lint-final.log is the corrected final check.

The requested post-merge FO progress send was attempted once and rejected by the tool with "user rejected MCP tool call"; there was no retry or alternate tool send. No product/state push, PR write, review request, ready transition, merge, version bump or new ADR was performed. FO owns publication, RoboRev, hosted CI and independent validation. Question-time live PR freshness remains deferred under the recorded Chief Engineer/FO disposition. The earlier pin-deletion experiment remains separate in implementation/pr.md for the Captain's ruling.

## Reproduction

Set PRODUCT_WORKTREE to a checkout of the candidate and SPACEDOCK_BIN to the workflow-pinned Spacedock 0.27.2 binary. Place this folder's scripts in a task-owned scratch directory; provide sd-plugin/mods/pr-merge.md from public commit 4d158a484ec73e184861067f8ed1e20087fdc26a and sd-bin/spacedock for run_ci.py. The source workflow names the Linux asset and checksum; provenance.json identifies the macOS binary and mod used here.

Run with python3 -B and PYTHONDONTWRITEBYTECODE=1, assigning TMPDIR to that scratch. Run run_ci.py, shared_guards.py, round2_probe.py replay, round2_probe.py rounds, round2_probe.py live, goal_and_mutation.py, then candidate_mutations.py. The replay/mutation scripts require the public archived state inputs at the state commit in provenance.json and PROBE_RUN=repair-final- for the replay. Live requires authorized read-only GitHub access. Package checks and exits are listed in commands.json; doc-impact-dispositions.json records every affected document.
