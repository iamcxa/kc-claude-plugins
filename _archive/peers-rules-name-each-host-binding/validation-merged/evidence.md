# Merged-head independent validation

Candidate: f7516476989b59fb45e4e5cb520d41ed9bc563ce (PR #730).
Merged base: b8ce84e584cf5c5cb482009d9d08d7316ce2a6ac.
Prior validated candidate: dc3916fbb4ce9655dc37c5e4185653694e029de4.
Verdict: **PASSED at the accepted local/prose/manual-replay boundary.** No product-code repair finding remains.

## Merge identity and preservation

merge-proof.py independently reconstructed lint-skills.py with git merge-file from the two parents and their common ancestor. It returned 0, without conflict, and reproduced the candidate byte-for-byte.
The merge has exactly the expected parents. Each PR-owned file other than lint matches the prior candidate, and every other incoming file matches main.
Removing the three-line document-presence addition from candidate lint yields the entire main lint file exactly. Main's budget-step list, including +144, is byte-identical; the removed dependency helper remains absent.
Thus this was an automatic merge, not an additional repair or scope change. Dropping the +144 budget step makes budget_errors(5565) refuse the file; removing the document guard makes its existing mutation test fail.
ADR 0037 records the Captain's approval of the +144 worker-collaboration instruction and protects that budget step. The head retains it; this PR introduces no further workflow budget increase.

## Criteria and exercised falsifiers

| Criterion | Independent result | Falsifier and evidence boundary |
| --- | --- | --- |
| AC-1 transport | Native Claude, Claude/Codex inside Paseo, bare Codex, unavailable tools/skill and ambiguous transport retain the previously reviewed policy. Incoming Paseo reply does not read unlisted paseo; native questions keep identity checks. | Vendor-selected route, unlisted read, missing probe/opening rejected by the rerun manual-event auditor. |
| AC-2 exchange | At fake times 0/299/300/301, busy new asks send zero, idle-before-deadline can send, expiration/no work/still-busy recheck stops deferral. Explicit steer and callback settings, worker exception and interrupt-fallback limits retained. Current CLI help checked. | Missing behavior, explicit interrupt, busy send, polling/reset/late send, blocked worker, receipt-as-answer and duplicate sends rejected. |
| AC-3 collaboration | Both interview rounds remain covered: taskless records, bound-briefing preservation, backlog reuse and unverified inaccessible originals. Real SD discovery and pr_watch separately executed on base/candidate omit the task-shaped hidden note. | Duplicate task, lost record, briefing edit and relayed-authority acceptance rejected. |
| AC-7 optional activation | Default package passes; optional-paseo template refused; three adopter lists do not affect the package result; three-way merges preserve default/custom/opt-in values. Installation refusal remains an instruction to FO, without an adopter-list enforcement script. | Mandatory-paseo tier mutant and unlisted-read trace rejected. Retained document check refuses a missing EXTENSION.md. |
| AC-6 reading/integration | Separately executed base/candidate fixture outputs, full input hashes, all route totals and independent line-index/regex recount match the implementation manifest exactly. All retained test files run. | Omitted upstream and inbound bundles rejected; removed +144 budget step refused; removed document guard fails its named test. |

replay.txt records 37 manual traces and 17 rejected bad-event mutations. The scratch auditor does not read the policy; these are counterexamples to its event predicates, not proof of a shipped policy engine.
Policy files are byte-identical to the earlier independently inspected reader traces. Those model runs were not repeated. No real peer was messaged, no host interruption prevention claimed, and no original Captain source authenticated.
AC-4 and source migration remain withdrawn by amendment 1.

## Complete reading recount

| Moment | Merged base | Candidate |
| --- | ---: | ---: |
| Startup, no exchange | 5775 | 5775 |
| Idle open | 1045 | 1045 |
| Idle merged | 1318 | 1318 |
| After archive | 3276 | 3276 |
| Merge ask | 742 | 742 |
| First native / unsupported | 742 | 805 |
| First task opening | 0 | 805 |
| First proactive Paseo | 742, unsupported | 2475 |
| Incoming / gate reply | 742, unsupported | 2185 |
| Warm exchange / withdrawn source repair | 0 | 0 |

The previous startup was 5631: both arms rise exactly 144 with main. Workflow words rise 5421 to 5565.
Peers remains 805, paseo 290, and the complete upstream Paseo skill 1380; peer ceilings remain 811/2481/2191.
Both-arm raw outputs and input hashes are saved under base/, candidate/ and reading-manifest.json. The independent recount verifies every route sum and input hash.
These counts measure text volume, not model attention or live compliance.

## Tests and retained guards

All 25 test files exit 0: 883 unittest cases, **882 passed and 1 skipped**, plus SD dispatch and observer-recovery assertion runners.
Changed counts reproduce implementation: Codex-review cases 29 to 35; POC README cases 6 to 7; lint remains 44.
The unchanged optional release-acceptance integration reports node, journey-accept.mjs or its YAML dependency unavailable; its probe does not identify which. This seam is not verified.
Repository lint passes at 5565/5565. ADR lint --since b8ce84e5 --require 0038 checks 38 records, 0 legacy, exit 0.
Number guards, dispatch records (9 complete) and design surfaces pass; migration checking is inapplicable and scope checking is not run outside ideation.
Comments: 6 added code lines, 0 comments, 0%; maximum 5% is not enforced below 20 added lines.
doc_impact lists five documents: package README updated by the existing peer change; ADR 0020 unaffected (budget equality retained), ADR 0037 unaffected (its exact protected step retained), maintain-flow unaffected (same replay/checking duties), learning.md unaffected (same learned practice).
No CI trigger changed; cost per PR was not measured.

## Findings and external evidence

FO supplied clean RoboRev roborev:1243 and CI 5/5 on this exact head, dated 2026-10-27. These remain attributed provider evidence, not validator executions.
A successful API read confirmed the exact head, OPEN state and isDraft=false; validation did not change readiness or any PR data.
F1, unused dependency automation, remains resolved.
- F2 Polish (remaining part): PR-body comment measurement still says 0/25 and maximum 5%, whereas this head reports 0/6 and a maximum not enforced below 20 lines. Reviewer/normal workflow: read PR #730; observed harm: inaccurate review evidence; protected criterion: none, review clarity only; trigger: the successful current-head API response. Refresh the PR description with this head's counts/limits before delivery. Its prior-head validation/review paragraphs also need the ordinary merged-head update; no product-code repair is required.

Sufficiency: all active criteria remain supported at their accepted boundary.
Necessity: the prior redundant dependency code remains removed; the surviving policy, adoption guidance, decision record and document guard map to accepted outcomes or observed negative cases. The merge adds only approved main changes.

## Minimal acceptance and limits

Run the five steps exactly in fresh Bash:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/peers-rules-name-each-host-binding/validation-merged/acceptance.sh
```

acceptance.sh includes exact commands, prerequisites and expected outputs. It ran unchanged, exit 0; acceptance-output.txt contains complete output.
Observed: pinned f7516476; lint 5565/5565 and 44 tests OK; 38 ADR records; both parents/+144 budget/document guard preserved; peer counts 805/290/1380, totals 2475/2185; clean candidate diff.
The script creates/removes its own detached checkout. No visible UI changed.
Live messaging, agent compliance, human authority, adopted configuration enforcement, release/adoption and merge authorization remain unverified or outside this assignment.

This report supersedes earlier candidate conclusions while preserving their historical evidence.
