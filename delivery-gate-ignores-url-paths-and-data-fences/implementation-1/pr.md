fix(kc-dev-flow-2): distinguish gate data from Captain steps

Gate preparation currently treats site URL paths and elided package paths as missing files, XML namespace URIs as links, and data fences in named Markdown cards as commands. This blocks complete gate questions before the Captain can review them.

Limit absolute-path checks to existing top-level filesystem roots, ignore a URI immediately after `{`, and require shell or untagged fences in named cards. Every fence in the message and validation report still requires a recorded step unless it matches observed output; ordinary links, real shell commands, and missing files under existing roots keep their holds.

The Captain approved the recommended card-only fence rule with 「核准（建議）」 at the batch 18 ideation gate on 2026-11-09. The PR-body attribution-link rule remains unchanged; FO tracks it separately in `delivery-gate-pr-body-attribution-link`.

Validation on 2026-11-09, candidate `6f2fe8f33de15cf4e9283bf9dfed185a5691ed57`, base `e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e`:

- The new real-CLI question cases fail on the base for the recorded false positives and pass on the candidate. Seven deliberate mutations are caught with `python3 -B` and caches cleared.
- python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py': 1032 tests, 7 skips, exit 0.
- All five extension test suites, real Spacedock dispatch and observer-recovery checks, repository `lint-skills.py`, ADR lint, number guards, design surfaces and version parity pass.
- `workflow.md` remains byte-identical at 5931 words. Comment ratio is 0.0%, below the 5% maximum.
- RoboRev and hosted CI were not run; FO owns those checks. CI cost per PR was not measured; CI configuration is unchanged.

Only `kc-dev-flow-2/scripts/delivery_gate.py` and `kc-dev-flow-2/scripts/test_delivery_gate.py` change. No version bump or new decision record is included.
