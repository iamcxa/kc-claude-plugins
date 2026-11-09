fix(kc-dev-flow-2): distinguish gate data from Captain steps

Gate preparation treats site URL paths and elided package paths as missing files, XML namespace URIs as links, and data fences in named Markdown cards as commands. This blocks complete gate questions before the Captain can review them.

Limit absolute-path checks to existing top-level filesystem roots, ignore a URI immediately after `{`, and require shell or untagged fences in named cards. Every fence in the message and validation report still requires a recorded step unless it matches observed output; ordinary links, real shell commands, and missing files under existing roots keep their holds.

The Captain approved the recommended card-only fence rule with 「核准（建議）」 at the batch 18 ideation gate on 2026-11-09. The PR-body attribution-link rule remains unchanged; FO tracks it separately in `delivery-gate-pr-body-attribution-link`.

Candidate `b8362fb901cd27bd367be1cd5b826f21fefad70e` merges main `8c8313823f353f631e2b7cca4559dd3e643f30a5` (#817) into the original candidate with a merge commit. The test fixture prepares #817's matching delivery record before executing this task's real CLI branch. Runtime functions for both changes remain identical to their respective parents.

Validation on 2026-11-09 at the merged candidate:

- Existing acceptance runner passes; its merged-head copy changes only the candidate/base pins. All five inputs also pass real merge-naming questions with a matching delivery record; missing or mismatched records still hold.
- `test_delivery_gate.py`: 192 tests, 1 skip, exit 0. All eight delivery-record cases pass. Seven reverse mutations remain caught with `python3 -B` and caches cleared.
- full discovery: 1040 tests, 7 skips, exit 0.
- All five extension suites, native local Spacedock dispatch/recovery, repository lint, ADR lint, number guards, design surfaces and version parity exit 0. Four release-acceptance dependency skips remain unproven.
- Relative to main, only the two approved script/test files differ. Workflow bytes remain unchanged at 5931 words; comment ratio is 0.0%, maximum 5%.
- RoboRev and hosted CI were not run by this worker; FO owns those checks and publication. CI cost per PR was not measured; CI configuration is unchanged.
