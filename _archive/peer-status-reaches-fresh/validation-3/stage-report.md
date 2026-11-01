
## Stage Report: validation

- DONE: Independent verdict on PR #756 head 39fdbb28 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Third run: PASSED at 39fdbb28b411d44a323741f645c7c1d75c653be1, stacked base 422caef5a9b115a14f8391836499520d9fba6d91. Per the dispatch's narrower instruction, only F5 is reassessed; unchanged AC-2/AC-3/AC-5/AC-6 exercises and falsifiers are explicitly carried forward from validation-2, not claimed as newly run. AC-4 remains post-delivery/not run.
- DONE: This PR is stacked on PR #754: re-judge only finding F5 against corrected AC-9 and carry forward other judgements if product head and inputs are unchanged
  validation-3/details.md records product/harness/eight cold-log hash equality and unchanged prior evidence since state 9e4564aec. Both no-notice outputs include the repository and PR 186, satisfying the restored source duty; F5 clears. Actual-output mutations removing repository or PR, plus a missing-query mutation, are detected. Prior F5/REJECTED history remains intact.
- DONE: Judge every active acceptance criterion and implementation limit at the accepted Pilot boundary
  AC-9 cold core/source attribution passes within existing g-* records; AC-2 synthetic originals and AC-3 recording stay bounded/partial. AC-5 counts and orchestration checks and AC-6 design/preservation remain carried passes. Direct resumes, long sessions, historical originals, native delivery and complete launch sealing remain unverified; no new cold/native run is claimed.
- SKIPPED: AC-4 post-delivery natural adopted transition and its natural-use falsifier
  No normally adopted post-delivery event is available. FO retains the observation obligation; this explicitly does not block validation or delivery.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; adr_lint.py docs/adr --since <base> with its exit code; verdict naming the head with workflow finding dispositions
  validation-3/acceptance.sh has three exact groups; fresh bash output in acceptance-output.log, exit 0: exact head, 45 ADR files/0 legacy, four attribution passes, three detected falsifiers, bounded PASSED. Detached-candidate ADR lint also exits 0; dispatch-records exits 0 with 12 complete. Script exclusions are explicit in details.md.
- DONE: Assess supplied exact-head review/CI receipts without claiming validator execution
  FO supplied RoboRev clean evidence=roborev:1378 and review/ci-39fdbb28.txt at 39fdbb28b; read as supplied receipts only. No hosted API verification, PR mutation, merge, adopter enablement or CI trigger change; CI cost per PR unmeasured.
- F3 Deferred risk: bounded authorization/recording does not prove historical authority/native delivery; a forbidden send, release overclaim, hidden real error or supported-path stale action would make it Material.
- F4 Deferred risk: all package/project/config bytes at cold launch are not sealed; evidence of changed execution bytes or injected rules would reopen acceptance. F1 stays superseded, F2 resolved and F5 cleared; no Material or Needs decision remains in this scoped review.

### Summary

This third validation supersedes validation-2's verdict for the unchanged candidate under corrected AC-9: 39fdbb28b411d44a323741f645c7c1d75c653be1 is PASSED within the recorded bounded Pilot evidence. Only F5 is re-judged; the repository-plus-PR source attribution satisfies the restored duty, while all other prior judgements and evidence limits carry forward. FO retains the Captain gate, delivery and post-delivery natural observation; this report grants no delivery authority.
