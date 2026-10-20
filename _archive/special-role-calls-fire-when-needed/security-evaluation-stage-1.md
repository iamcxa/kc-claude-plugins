# ADR 0021 D1 evaluation, stage 1: later findings against the 10 saved prod validation security reports

Result: two security-class findings were raised on a later head than a saved report and that report did not name them (both on one PR, #666, the merge-gatekeeper task); two more were raised on the same head as a report that did not name them (one clear, one borderline); the other 8 saved reports have no later security-class finding. Stage 1 therefore does not meet the "no escape keeps D1" stop rule, and does not show that a stronger model would have caught either escape. Stage 2 stays the Captain's call. No model was run.

## What was read, and how

- Reports: the 10 saved prod validation security reports at the design's pins (merge-gatekeeper validation-1 to 4, revoke-ends-access, account-publish-ceiling, production-operations validation-10, check-database-version, move-to-singapore-region, product-analytics-posthog). None records its model, so "Sonnet" rests on ADR 0021 D1.
- Later items: every inline comment from `gh api repos/<repo>/pulls/<N>/comments --paginate --slurp` (read 2026-10-20) on the task's PR, and every roborev High recorded in the task file, each placed on the PR's commit order (`gh pr view <N> --json commits`) against the head each report reviewed (the `validation-N` dispatch record names it).
- Security-class: an authority, access-control or disclosure defect, or a bypass of a merge or approval rule. One reader (the implementation worker), no second reader; the labels are a judgment and are listed so a validator can relabel.
- Named: the report has a finding in the same file whose recommendation, followed, would close the item.
- Escape: security-class, present in the code at a saved report's head, raised on a later head than a preceding saved report, and not named by it. Same-head miss: the same, raised on the report's own head.

## The 10 reports

| Task (PR) | Report head | Later inline findings or roborev Highs on the PR | Escapes |
|---|---|---|---|
| merge-gatekeeper (#666), validation-1 to 4 | 1beabd97, 3fd84178, b97068de, a05b18a0 | 7 Codex comments, 10 roborev runs that raised a High; table below | 2 escapes, 2 same-head misses |
| production-operations (#1287), validation-10 | c81f4762 (the PR's last commit) | 19 Codex comments, all on earlier heads but one; roborev Highs 790, 792, 839 on earlier heads | 0 |
| account-publish-ceiling (#400) | 517e2fb3 | no inline comments; roborev:877 High on 258c5db3 predates the report; 902 and 908 clean | 0 |
| revoke-ends-access (#388) | 8330155b | no inline comments, no roborev run recorded | 0 |
| product-analytics-posthog (no PR at the pin) | bb56c25c | roborev:904 High (raw path in page-view properties) on the report's own head; the report names it (finding 2, LOW) | 0 |
| move-to-singapore-region (no PR at the pin) | 370fe36f | roborev:888 High on an earlier head, fixed; later runs Medium | 0 |
| check-database-version (no PR at the pin) | 454a8064 | roborev Medium only | 0 |

The design's "26 later inline findings" counted every comment on #666 and #1287. By the rule above only comments on a head after a saved report can be later: #1287's 19 comments sit on heads at or before the one report, so no earlier report existed to name them.

## #666 (merge-gatekeeper), item by item

Report times (UTC): validation-1 05:56, validation-2 09:20, validation-3 13:37, validation-4 14:25, on 2026-10-18.

| Item | Head | Security-class | Named by | Verdict |
|---|---|---|---|---|
| Codex 4305855772: a quoted `profile: "prod"` is not read as prod by the gate's own regex, so a prod task can be classed docs-only | 1beabd97 | yes (bypass of "prod is never eligible") | not named by validation-1 (same head); no earlier report | same-head miss |
| Codex 4305855775: instruction directories matched only at shallow depth | 1beabd97 | yes | validation-1 finding 1 (recommendation: allowlist) | not an escape |
| Codex 4305855777: stale trunk ref misses a revert | 1beabd97 | yes | validation-1 finding 2 (stale history without fetch) | not an escape |
| Codex 4306363860: grants resolved from a stale working tree, so a revoked grant still merges | 3fd84178 | yes (revoked authority still honored) | not named by validation-1 (preceding) or validation-2 (same head) | **escape** |
| Codex 4306363862: unreadable historical PR state treated as pending | 3fd84178 | yes | validation-1 finding 2, validation-2 finding 4 | not an escape |
| Codex 4307169171: a non-empty CI rollup passes without the required jobs | b97068de | yes (gate integrity) | validation-3 finding 1 (same head) | not an escape |
| Codex 4307329360 (P2): file list not bound to the recorded head | a05b18a0 | borderline (record corruption, no authority effect) | not named by validation-4 (same head) | same-head miss, borderline |
| roborev:843 and 844 (High, one finding twice): a syntactically valid grant entry enables a merge line though its ADR and calibration are never checked | b28bbcc6 | yes | not named by validation-1 (preceding) or validation-2 (3fd84178, grant code still present: it was deleted in b97068de) | **escape** (FO declined it as the Captain's ADR decision, then the grant half was deleted) |
| roborev:855 (High): documented command omits `--workflow-dir` | b97068de | no (a usage form; disputed, accepted as Polish) | not applicable | not an escape |
| roborev:857 (High): only the newest run per workflow was read | 966b27ea | yes | the flaw is in code written after validation-3's head; validation-4 reviewed the fix | not an escape |
| roborev High runs 810 (two Highs), 826, 829, 832, 835, 837 | heads before 1beabd97 | mixed | no saved report precedes them | not eligible |

## #1287 (production-operations), the two security-class comments

Both predate validation-10 and neither is in the head it reviewed. Codex 4306044737 (a non-`Error` thrown object's `code` reaches Sentry): at c81f4762 `codeOf` returns nothing for a non-`Error`. Codex 4306204414 (staff revocations return after a database restore): the restore procedure was split out of the PR's runbook before c81f4762 (its commit headline); the runbook at that head has no restore step to carry it. The other 17 comments are correctness, operations or reliability items, not security-class. The one comment after the report (4311666873, a curl config quoting fault) fails closed and is not security-class.

## What this does and does not show

- It shows two security-class authority defects on one PR that every Sonnet security report on that PR left unnamed, while Codex and roborev named them. It does not show that Opus or Fable would have named them: no model was run.
- Both escapes are logic errors inside the repository's own merge gate. ADR 0021's reach brief targets outsider-facing exposure (routes, public files, disclosure); the reports on this PR said the change adds no public route. These are not the class that brief was written to find.
- 1 of 7 prod tasks contributed. The other 6 show nothing; three of them had no PR at the pin, so no inline reviewer had read them.
- The labels have one reader. A validator relabelling any row changes the count.

## Decision for the Captain

Run stage 2 (about 40 USD assumed, reruns on the two escaped heads plus controls), or stop here and keep ADR 0021 D1. The design's stop rule says stop on zero escapes; this is not zero, and the evidence is one PR.
