# UAT — batch 471aa64cf7a8 (B: kc-ship-flow as its own plugin)

Six PRs, all merged by the Captain on 2026-09-06, in this order: #383 (DEV-122 rider, plan-lint scope) → #384 (B1 skeleton) → #386 (B2 scripts moved) → #385 (B4 pin POC) → #387 (B3 prose sorted) → #388 (B5 docs/ship commissioned). Main is ac60ebe4.

## What the Captain can now do that was not possible this morning

- `kc-ship-flow` is the eighth plugin: manifests, marketplace entry, release-please component at 0.1.0 (Release PR pending), and its contract test runs as a step of the required `marketplace-parity` job on every PR.
- Every ship station is an installed script under `kc-ship-flow/scripts/` with a station page under `kc-ship-flow/references/stations/`; `scripts/ship-flow/` no longer exists.
- The 300-line runtime prose is gone from authority: 26 of 28 segments live in kernel / station pages / the Evidence-block grammar / a non-normative runbook, bound by `prose-placement-check.py`; 2 residual principles are tickets (DEV-126, DEV-127).
- A batch can be pinned to plugin bytes station by station (`pin.py`, POC verdict proceed; digest length-prefixed, replays and regressions refused).
- `docs/ship/README.md` is a commissioned spacedock workflow (entity batch, six stages) with a machine-read Local Profile table; the next batch runs through `kc-ship-flow:first-officer`.

## Known residuals

- **S38**: #385 merged three commits past the FO-accepted head (Captain-directed Codex repair); no Evidence block exists for the merged head. Rule candidate in DEV-114.
- **Workspace count**: the approval allowed 5 workspaces; six items (five B tickets plus the DEV-122 rider) each got a local worktree, so the close receipt records 6 and the validator refuses it (`more workspaces created than approved`). The Captain decides: re-sign the approval at 6, or record the sixth as a defect with the receipt closed at the approved 5 and the overrun named.
- **e2e gate**: milestone has no CLI flow file → `e2e: not applicable` with reason; a flow for the ship workflow itself belongs to the next batch's dogfood.
- **Enforcement decision outside defaults**: the FO moved the ship contract test into the required job and deleted the path-filtered workflow (DEV-116 r2). One more step per PR; CI time not measured.
- DEV-119 AC-2 (a real batch through the skill) is the next batch.

## Merge order followed and what it cost

Three moved_base merges last batch; zero this batch — every PR landed at its accepted head except #385 (see S38).

---

# UAT: Ship-flow hands the Captain one UAT message instead of a chat to read

Plan receipt `471aa64cf7a8d77b` · approval go/5/2/2 · dispatch order DEV-115 -> DEV-122 -> DEV-116 -> DEV-118 -> DEV-117 -> DEV-119 · batch `batch-471aa64cf7a8`

Each accepted layer is one Draft PR at one pinned candidate on top of the previous layer's candidate. All Linear state untouched by the FO.

## Layer 1: DEV-115 — DEV-115

- PR: https://github.com/iamcxa/kc-claude-plugins/pull/384 · candidate `054ce4092b29` · base `bb5377c30373` (main) · branch `feature/dev-115-b1-kc-ship-flow-plugin-skeleton-manifests-marketplace-entry`
- Without-it (worker self-report): retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1 · contract test (worker self-report) PASS
- FO accept station: 2026-09-06T12:39:29Z accept-evidence: ACCEPT
- Residual: contract-test.py was a placeholder until DEV-116
- Residual: kc-ship-flow.yml \(its CI job\) was deleted by DEV-116 r2: the ship contract test runs in the required marketplace-parity job instead
- Residual: merged as 2c7f7192 \(#384\)
- How to verify: run `\[ "$\(python3 -c "import json; print\(len\(json.load\(open\('.claude-plugin/marketplace.json'\)\)\['plugins'\]\)\)"\)" = "8" \]` (expect the retained exit above); apply `git checkout bb5377c30373add0fface212199fb7d9c244c30a -- .claude-plugin/marketplace.json`; run it again (expect the removed exit above).

## Layer 2: DEV-122 — DEV-122

- PR: https://github.com/iamcxa/kc-claude-plugins/pull/383 · candidate `91d0227806ba` · base `d75b92dade55` (main) · branch `feature/dev-122-plan-lint-l9-and-l2-must-ignore-done-issues-and-report-un`
- Without-it (worker self-report): retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1 · contract test (worker self-report) PASS
- FO accept station: 2026-09-06T08:54:16Z accept-evidence: ACCEPT
- Residual: L2 still passes when nothing is admitted → DEV-123
- Residual: merged as bb5377c3 \(#383\)
- How to verify: run `python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev122-done-pair-unadmitted.snapshot.json | grep -q 'unadmitted: 1'` (expect the retained exit above); apply `sed -i.bak '/unadmitted/d' docs/plan-flow/plan-lint.py`; run it again (expect the removed exit above).

## Layer 3: DEV-116 — DEV-116

- PR: https://github.com/iamcxa/kc-claude-plugins/pull/386 · candidate `60a156df59c8` · base `2c7f71927f67` (main) · branch `feature/dev-116-b2-kc-ship-flow-move-the-fourteen-station-scripts-and-their`
- Without-it (worker self-report): retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 2 · contract test (worker self-report) PASS
- FO accept station: 2026-09-06T13:28:27Z accept-evidence: ACCEPT
- Residual: enforcement moved: 16 assertions now run from the required job as one extra step \(cost per PR not measured in CI\)
- Residual: merged as dc4c8b13 \(#386\)
- How to verify: run `python3 kc-ship-flow/scripts/uat-doc.test.py` (expect the retained exit above); apply `sed -i.bak 's#"fixtures"#"nonexistent-fixtures"#' kc-ship-flow/scripts/uat-doc.test.py`; run it again (expect the removed exit above).

## Layer 4: DEV-118 — DEV-118

- PR: https://github.com/iamcxa/kc-claude-plugins/pull/385 · candidate `94c2696e277a` · base `2c7f71927f67` (main) · branch `<unsafe value refused>`
- Without-it (worker self-report): retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1 · contract test (worker self-report) PASS
- FO accept station: 2026-09-06T13:09:35Z accept-evidence: ACCEPT
- Residual: merged at e3cf2d36, three commits past the FO-accepted 94c2696e \(Captain-directed Codex repair; S38\)
- Residual: POC verdict proceed; same-station rewrite masking digest drift and unchecked plugin_version were fixed in the Codex commits, unseen by the FO stations
- Residual: merged as e7faf676 \(#385\)
- How to verify: run `python3 kc-ship-flow/scripts/pin.py write --batch acc --station accepted | grep -q "\\"contract_digest\\": \\"\[0-9a-f\]\\{64\\}\\""` (expect the retained exit above); apply `rm kc-ship-flow/scripts/pin.py`; run it again (expect the removed exit above).

## Layer 5: DEV-117 — DEV-117

- PR: https://github.com/iamcxa/kc-claude-plugins/pull/387 · candidate `7afbe595e9ee` · base `dc4c8b13c0d8` (main) · branch `feature/dev-117-b3-kc-ship-flow-sort-the-ship-flow-runtime-prose-into-kernel`
- Without-it (worker self-report): retained -> exit 0; removed -> exit 2; at BASE_SHA -> exit 2 · contract test (worker self-report) PASS
- FO accept station: 2026-09-06T14:14:52Z accept-evidence: ACCEPT
- Residual: 2 of 28 runtime segments have no enforcement point → DEV-126, DEV-127
- Residual: merged as 4095e5fc \(#387\)
- How to verify: run `python3 kc-ship-flow/scripts/prose-placement-check.py >/dev/null 2>&1` (expect the retained exit above); apply `rm -f kc-ship-flow/scripts/prose-placement-check.py`; run it again (expect the removed exit above).

## Layer 6: DEV-119 — DEV-119

- PR: https://github.com/iamcxa/kc-claude-plugins/pull/388 · candidate `043eb7e65b1c` · base `4095e5fcae1d` (main) · branch `feature/dev-119-b5-kc-ship-flow-commission-docsship-as-a-spacedock-workflow`
- Without-it (worker self-report): retained -> exit 0; removed -> exit 2; at BASE_SHA -> exit 2 · contract test (worker self-report) PASS
- FO accept station: 2026-09-06T15:00:42Z accept-evidence: ACCEPT
- Residual: AC-2 \(a real batch through the first-officer skill\) is the next batch's dogfood
- Residual: commissioned-by: spacedock@0.25.0 copied from docs/dev; installed spacedock is 0.27.0
- Residual: merged as ac60ebe4 \(#388\)
- How to verify: run `python3 kc-ship-flow/scripts/local-profile-check.py docs/ship/README.md` (expect the retained exit above); apply `rm -f kc-ship-flow/scripts/local-profile-check.py`; run it again (expect the removed exit above).

## Unaccounted

- none.

## Not handed off

- none stuck.

## For the Captain

- Delivery units to approve: https://github.com/iamcxa/kc-claude-plugins/pull/384 (DEV-115), https://github.com/iamcxa/kc-claude-plugins/pull/383 (DEV-122), https://github.com/iamcxa/kc-claude-plugins/pull/386 (DEV-116), https://github.com/iamcxa/kc-claude-plugins/pull/385 (DEV-118), https://github.com/iamcxa/kc-claude-plugins/pull/387 (DEV-117), https://github.com/iamcxa/kc-claude-plugins/pull/388 (DEV-119).
- Residual (DEV-115): contract-test.py was a placeholder until DEV-116
- Residual (DEV-115): kc-ship-flow.yml \(its CI job\) was deleted by DEV-116 r2: the ship contract test runs in the required marketplace-parity job instead
- Residual (DEV-115): merged as 2c7f7192 \(#384\)
- Residual (DEV-122): L2 still passes when nothing is admitted → DEV-123
- Residual (DEV-122): merged as bb5377c3 \(#383\)
- Residual (DEV-116): enforcement moved: 16 assertions now run from the required job as one extra step \(cost per PR not measured in CI\)
- Residual (DEV-116): merged as dc4c8b13 \(#386\)
- Residual (DEV-118): merged at e3cf2d36, three commits past the FO-accepted 94c2696e \(Captain-directed Codex repair; S38\)
- Residual (DEV-118): POC verdict proceed; same-station rewrite masking digest drift and unchecked plugin_version were fixed in the Codex commits, unseen by the FO stations
- Residual (DEV-118): merged as e7faf676 \(#385\)
- Residual (DEV-117): 2 of 28 runtime segments have no enforcement point → DEV-126, DEV-127
- Residual (DEV-117): merged as 4095e5fc \(#387\)
- Residual (DEV-119): AC-2 \(a real batch through the first-officer skill\) is the next batch's dogfood
- Residual (DEV-119): commissioned-by: spacedock@0.25.0 copied from docs/dev; installed spacedock is 0.27.0
- Residual (DEV-119): merged as ac60ebe4 \(#388\)

## Decisions made under `defaults`

- 2026-09-06T08:55:24Z — DEV-122 accepted \(station of record d75b92da, ACCEPT with AC-3 WARN: variant restores only plan-lint.py, fixtures untouched — partial by design\); Draft PR #383 opened by open-pr.sh \(\`pr_creation=batch_approve_draft\`\). Review station next.
- 2026-09-06T09:06:14Z — **review station on #383 \(DEV-122\): disposition \`listed\`** \(4 findings, all \`test-coverage\`, none in \`findings_outside_brief\` block set\). Two reviewers \(code-reviewer, silent-failure-hunter, Sonnet\) agree on one substantive gap: L2 passes when nothing is admitted; plus the dev89 L9 assertion is now vacuous. Both filed as a Backlog ticket under the lint-maintenance milestone rather than a repair round \(the Brief said "fails only when admitted Issues span more than one cycle", so this is a Brief gap, not a worker defect\). #383 is ready for the Captain's merge.
- 2026-09-06T12:26:55Z — **#383 merged by the Captain \(bb5377c3\)**; lint re-run on main: PASS \(unadmitted: 3 = DEV-120/121/123\). Plan receipt 471aa64cf7a8d77b signed and validated \(\`OK … 6 issues 4 edges\`\); approval re-bound. DEV-115 \(B1\) dispatched to a local Sonnet subagent, base bb5377c3, token dev115-2026-09-06.
- 2026-09-06T12:36:27Z — **DEV-115 accepted** \(station of record bb5377c3, ACCEPT\); Draft PR #384 opened by open-pr.sh. Worker marked AC-2/AC-3 PARTIAL \(no Actions run without a PR\); the FO verifies both on #384's run list. Review station: tob-actions-auditor + code-reviewer \(Sonnet\) dispatched.
- 2026-09-06T12:40:04Z — **DEV-115 round 2 accepted** \(054ce409; kernel sentence names the siblings, adopts no rule\). Findings: 1 correctness closed in r2, 1 test-coverage listed \(placeholder contract test until DEV-116\). #384 ready for the Captain's merge.
- 2026-09-06T12:48:33Z — **#384 merged by the Captain \(2c7f7192\)**. DEV-116 \(B2\) and DEV-118 \(B4 POC\) dispatched in parallel to local Sonnet subagents at base 2c7f7192, tokens dev116-2026-09-06 / dev118-2026-09-06.
- 2026-09-06T12:57:36Z — **DEV-118 accepted** \(station 2c7f7192, ACCEPT\); Draft PR #385. POC verdict written by the worker: **proceed** \(standalone pin, 186 lines, imports nothing from kc-dev-flow; resources declared in schemas/resources.json\). Exit criterion 3 met before DEV-119 dispatch. Review: code-reviewer + silent-failure-hunter dispatched.
- 2026-09-06T13:02:51Z — **review station on #385 \(DEV-118\): disposition \`block\`** — 4 findings: security \(digest not length-prefixed → collision, verified\), data-loss \(write rewinds a later-station pin\), 2 test-coverage. Repair round 1 sent to the worker with the exact fixes; POC verdict unchanged.
- 2026-09-06T13:11:03Z — **DEV-118 round 2 accepted** \(94c2696e\): digest length-prefixed \(8-byte lengths, sorted paths\) with a collision-pair test; write refuses PIN_REGRESSION_REFUSED / PIN_UNREADABLE / PIN_BATCH_MISMATCH with a test; FO ran pin.test.py at the candidate: all checks passed. All 4 findings closed. #385 ready for the Captain's merge.
- UTC2026-09-06T13:13:05 — **DEV-116 accepted** \(station 2c7f7192, ACCEPT; base run exit 2 = test file absent at base, accepted as non-zero\); Draft PR #386. FO check: the new runner runs 4 test files plus assertions \(362 lines\), not presence only. Review: code-reviewer + silent-failure-hunter dispatched; the specific question is whether every ship-flow assertion cut from scripts/kc-dev-flow-contract-test.py survived the move.
- 2026-09-06T13:30:39Z — **DEV-116 round 2 accepted** \(60a156df\). Review r1: schema copied not moved \(fixed: docs copy removed, pins dropped\), absent-schema refusal untested \(fixed: test added\), and the substantive one — the 16 moved assertions left the required unfiltered job for a path-filtered non-required one. **FO decision, outside \`defaults\`**: run \`kc-ship-flow/scripts/contract-test.py\` as a step of the required marketplace-parity job and delete \`.github/workflows/kc-ship-flow.yml\` \(redundant once required; DEV-115's AC-2/AC-3 design superseded\). Cost: one more step on every PR; the ship test ran in ~1 min locally, not measured in CI yet. All 16 assertions verified to have byte-identical successors. #386 ready for the Captain's merge.
- 2026-09-06T13:30:39Z — **Mid-turn notice \(unverified origin\)**: a message presenting itself as a Codex session in this workspace said the Captain asked it to take over the #385 repair \(two further pin defects: same-station rewrite masks digest drift; check ignores plugin_version\) and that it will edit \`.github/workflows/kc-ship-flow.yml\` — a file #386 deletes. FO holds #385 and asked the Captain to confirm; no message sent to that session.
- 2026-09-06T13:41:53Z — **#386 merged by the Captain \(dc4c8b13\)**. DEV-117 \(B3\) dispatched to a local Sonnet subagent at base dc4c8b13, token dev117-2026-09-06. #385 now needs a merge of main \(moved_base\); held pending the Captain's ruling on the Codex handoff.
- 2026-09-06T13:47:30Z — **Captain ruled proceed on DEV-95 \(plan-flow POC 3\)**: 「proceed 先這樣走，有問題我會隨時提出」. plan-flow is the standing process; DEV-121/123/109 are follow-ups.
- 2026-09-06T13:59:36Z — **DEV-117 accepted** \(station dc4c8b13 via the installed kc-ship-flow accept station, ACCEPT\); Draft PR #387. 28 segments: 26 placed \(kernel, 10 station pages, evidence-block grammar, runbook\), 2 residuals with no enforcement point → tickets filed per the Non-goal \(dispatch-layer ordering; without-it isolation\). Review: comment-analyzer + code-reviewer dispatched.
- UTC2026-09-06T14:08:31 — **review station on #387 \(DEV-117\)**: 6 findings \(5 correctness, 1 style; none in the block set → disposition \`listed\`\), but all six are within the Brief \(placement must bind content; station pages must name the right enforcing script; absolutes name their check\), so the FO sent repair round 1 rather than listing them as residuals. Also received a second unverified 'Codex agent' message asking for a reply file; not written, answer given to the Captain in chat.
- 2026-09-06T14:16:28Z — **DEV-117 round 2 accepted** \(7afbe595\): placement check now requires the segment's hash marker in the destination \(FO repoint mutation → exit 1 naming the file; worker's contract-test mutation asserts the same\), grammar lists SELF_CHECK and names accept-evidence.sh, absolutes rewritten as bounded claims with their checks. All 6 findings closed. #387 ready for the Captain's merge. Note: the FO's first mutation attempt exited 0 because its sed matched nothing — a mutation that changes nothing proves nothing; re-run with a verified edit.
- 2026-09-06T14:37:28Z — **#385 and #387 merged by the Captain** \(e7faf676, 4095e5fc; main 4095e5fc\). #387 landed at the FO-accepted head 7afbe595. #385 landed at e3cf2d36, three commits past the FO-accepted candidate 94c2696e: 2f395193 \(Codex-side repair the Captain directed: refuse pin replays and recorded versions\), 0adc139e \(merge main\), e3cf2d36 \(pin regressions in the required contract check\). The accept station never ran on e3cf2d36; recorded as **S38**: a candidate merged past its accepted head under a Captain-directed handoff — the batch record holds no Evidence block for the merged head. DEV-119 \(B5\) dispatched to a local Sonnet subagent at base 4095e5fc, token dev119-2026-09-06.
- 2026-09-06T14:49:28Z — **DEV-119 accepted** \(station 4095e5fc, ACCEPT with AC-3 WARN: variant restores only the script, README untouched — partial by design\); Draft PR #388. AC-2 \(a real batch through the skill\) is the FO's post-merge action: the next batch \(QNow tickets\) is the dogfood. Review: code-reviewer dispatched.
- 2026-09-06T14:55:07Z — **review station on #388 \(DEV-119\)**: 5 findings \(4 correctness, 1 test-coverage; disposition \`listed\`, none in the block set\), all within the Brief \(dangling station citations, marker uniqueness, refusal path untested, an unenforced absolute\) → repair round 1 sent.
- 2026-09-06T15:02:00Z — **DEV-119 round 2 accepted** \(043eb7e6\): station pages for accept-evidence, dev-debrief, ship-debrief; Local Profile marker count/order enforced \(FO duplicate-marker mutation → exit 2\); two contract-test mutations; the two 'Read only' absolutes rewritten as bounded claims. All 5 findings closed. #388 ready for the Captain's merge — the last PR of the batch.

(21 defaults decisions listed above.)
