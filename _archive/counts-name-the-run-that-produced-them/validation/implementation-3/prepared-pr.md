feat(kc-dev-flow-2): disclose unchecked counts and validate learn evidence

Automatically write the computed Unchecked counts line into validation summaries and merge-ask text, including counts in the PR body. Reject new learn add completions when Evidence counts are absent from the pack items their decisions reference, while leaving rejected claims pending and correctable.

The source reminder, existing gate holds and historical completed-record reads remain. ADR 0072 records the decision, and the POC route's byte expectation now includes the tool-written disclosure. Startup budget and versions are unchanged.

Validation (2026-11-09 UTC):
- validation/implementation-3/suite.log records Ran 1050 tests and OK (skipped=7) from python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py', with the dispatched Spacedock executable explicitly set in SPACEDOCK_BIN. suite.json records the exact command and candidate.
- Repository skill lint and package ADR, fresh number-reservation and comment-ratio checks exit 0 at the candidate, with their producer records in validation/implementation-3/verification.json.
- validation/implementation-3/mutations.log confirms the tests fail when the evidence join, number comparison, writer or PR-body scan is removed, including the POC forwarding test. The checks use python3 -B with caches absent.
- Final-pattern gate/learn replays and a separate reading-cost recount are in validation/implementation-3/gate-replay.log, learn-replay.log and words.log.

Limits: presence in a referenced file does not establish truth or identify the producing command. A heading-shaped 1 FO line can be refused as a count, as validation/implementation-3/replay-differences.json records. The original issue's adopter record was unavailable; replay uses local records. No CI workflow changed, and CI cost was not measured.

Product push, Draft PR creation, RoboRev and CI are delegated to FO and have not been run by this worker. No PR opened: no push grant.

Evidence: https://github.com/iamcxa/kc-claude-plugins/tree/spacedock-state/dev2/counts-name-the-run-that-produced-them/validation/implementation-3
