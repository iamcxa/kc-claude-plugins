## Stage Report: validation

- DONE: Independent verdict on PR #841 head 6da9a765 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED at 6da9a765ee04e1e2c7836517ba01f75b0ea91d73; all 12 current criteria are mapped to fresh runs and counterexamples in validation-2/README.md and acceptance.json; superseded AC-7 stays withdrawn.
- DONE: Recheck after Feedback Cycle 1: reproduce validation-1 findings F1 and F2 at this head with a normal control; judge the refusal when the native reader fails, the kept Budget behaviour, Captain amendment 6's limits on test edits file by file, and the chief-engineer's stated risk (review/chief-engineer-1.md) that a design written before this release with no Worth questions section is refused after upgrade
  validation-2/worth-probe.json shows both rejected-head false passes becoming refusals and visible-section controls passing; native failure/timeout refuses; legacy-design.json confirms old-design refusal; test-scope-audit.json and README assess all six test files with no deleted negative case.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-2/captain.sh ran unchanged in env -i and bash --noprofile --norc: five steps, exit 0, captain.log; package ADR lint --since e8664a72b0f904e5dda3c391d52ab3abaca876b4 --require 0077 exits 0, 68 records (adr.log); finding disposition below.
- DONE: Complete candidate checks and decisive counterexamples
  validation-2/tests.json and full/*.log: 28 commands passed; mutations.json catches 24 Budget/Worth falsifiers; repair-proof.json catches three rejected-head regressions and four reverse mutants as assertion failures, not errors; removing ADR 0077 exits 1 (adr-falsifier.json).
- DONE: Pinned histories and current consumer boundaries
  validation-2/relay-replay.json holds at 42317d0c before d85ce152 while base does not; archive-replay.json/count-differences.json explain every fixed-form difference; message-counts-40cfa1ae.json and message-counts-497b9f32.json distinguish 7 then 8 dispatches as one added stage record; merge-transition-probe.json proves old-header exemption.
- DONE: Governance checks, retained documents, and artifact identity
  validation-2/required-checks.json records role/design/dispatch/ADR checks; number-fresh.log exits 0 after fresh fetch, comments.log is 12/517=2.3% under 5%; all 14 doc-impact paths carry verdicts; export-identity.json binds tested blobs to the candidate, and pr.json confirms the remote draft head.
- DONE: Goal sufficiency and minimum necessary scope
  validation-2/README.md ties retained changes to the accepted criteria, amendment 3 total cap, amendment 5 repair-message rule, and required ADR/word-budget boundaries; repair-scope-audit.json shows Budget and consumer logic unchanged in the repair; no new finding rule, minute meter or old-design backfill.
- SKIPPED: Repair or decline the implementation's 15 sibling findings outside the new Worth check
  Dispatch explicitly returns these to FO; validation-2/sibling-compare.json independently reproduces nine representative observations unchanged, with source-only risks still unproven; implementation-3/sibling-findings.json remains open and is not silently cleared.
- SKIPPED: Product publication, review disposition, gate approval, merge, release and adopter rollout
  FO/Captain-owned. Local native binary 0.27.2 with plugin test root 0.27.3 differs from CI's paired 0.27.2; hosted reported successes are recorded separately in pr.json; CI configuration unchanged and per-PR cost not measured.

### Summary

Fresh validation recommends PASSED for candidate 6da9a765ee04e1e2c7836517ba01f75b0ea91d73 against the accepted Pilot scope. Prior validation-1 F1/F2 are independently repaired; existing sibling findings and the old-design compatibility consequence remain explicit, with no product or unrelated state edits. Evidence is in budget-overrun-holds-and-findings-meet-non-goals/validation-2/; the validator removes its entire /tmp scratch root after evidence commit and records cleanup.json.

- F1 Deferred risk: upgrading and re-presenting an old design without Worth questions now refuses (validation-2/legacy-design.json: base 0, candidate 1, same bytes). Protected field: none: AC-9 promises no legacy Worth exemption; budget exemption alone is accepted. A later requirement to preserve old presentation or backfill designs needs a Captain compatibility decision, outside this repair.

Captain steps: budget-overrun-holds-and-findings-meet-non-goals/validation-2/captain.sh; exact fresh-shell command and expected observations are in validation-2/README.md, observed output in validation-2/captain.log (exit 0).
