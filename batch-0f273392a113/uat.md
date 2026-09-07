# UAT: 架構收斂與 POC 瘦身

Plan receipt `0f273392a11371be` · approval go/3/1/2 · dispatch order DEV-25 -> DEV-35 -> DEV-36 -> DEV-37 · batch `batch-0f273392a113`

Each accepted layer is one Draft PR at one pinned candidate on top of the previous layer's candidate. All Linear state untouched by the FO.

## Layer 1: DEV-25 — DEV-25

- PR: https://github.com/iamcxa/qnow/pull/1177 · candidate `2c79489203b3` · base `eeb7d4f83e5e` (main) · branch `conductor/dev-25-netlify-tenancy-and-otp-validation`
- Without-it (worker self-report): retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1 · contract test (worker self-report) PASS
- FO accept station: 2026-09-07T02:25:58Z accept-evidence: REFUSE: AC-3: cannot extract paths from WITHOUT_IT_COMMAND - command may be unparseable
- Residual: merged as c7a905a9 after a moved_base merge \(qnow ruleset: head up to date\)
- Residual: hosted Neon behaviour unproven \(PR's own 'Not proven'\)
- Residual: customer identity provider undecided → DEV-132; revoke-by-subject → DEV-133
- Residual: accept station S43 override \(FO re-ran the pair\)
- How to verify: run `npx vitest run --config vitest.config.ts test/phone-identity-conformance.test.ts 2>&1 | grep -q "22 passed"` (expect the retained exit above); apply `sed -i.bak '159d' experiments/netlify-refine-poc/qnow-next/identity/reference-phone-identity.ts`; run it again (expect the removed exit above).

## Layer 2: DEV-35 — DEV-35

- PR: https://github.com/iamcxa/qnow/pull/1180 · candidate `c6c4fe19b3a6` · base `c0c314597f4c` (main) · branch `conductor/dev-35-cloud-headed-playwright`
- Without-it (worker self-report): worker: retained 0; removed 1; base 1. FO: see README entry \(script-based re-run\) · contract test (worker self-report) FAIL
- FO accept station: accept-evidence: REFUSE: AC-3: cannot extract paths \(extension list — S43/DEV-134\)
- Residual: first merged into the wrong base \(S45\), reverted; re-landed on main via #1180 as 820f6fb5 \(cherry-picks\)
- Residual: display-dependent journey evidence pending the DEV-37 cloud run
- Residual: accept station S43 override
- How to verify: run `node /tmp/wi-1175.mjs <abs path to local/headed-browser-environment.mjs>  \(asserts NO_PROC_PROCESS_TABLE is raised when the /proc probe returns false\)` (expect the retained exit above); apply `sed -i.bak "s/if \(!hasProcDirectory\(\)\) throw unavailable\('NO_PROC_PROCESS_TABLE'\);/if \(false\) throw unavailable\('NO_PROC_PROCESS_TABLE'\);/" experiments/netlify-refine-poc/qnow-next/local/headed-browser-environment.mjs`; run it again (expect the removed exit above).

## Layer 3: DEV-36 — DEV-36

- PR: https://github.com/iamcxa/qnow/pull/1174 · candidate `b5d87ed862a9` · base `3c65da1e99ee` (main) · branch `conductor/dev-36-qnow-esm-runner`
- Without-it (worker self-report): worker: retained 0; removed 1; base 1. FO: retained 0; removed 1 \(variant applied 1 line\); type-check 0; test:unit 180; netlify-package 106; self-check 0 · contract test (worker self-report) PASS
- FO accept station: accept-evidence: REFUSE: AC-3 extension list \(S43/DEV-134\)
- Residual: cannot land on main alone: the whole hosted/ runner \(26 files\) exists only on the staging-qualification branch; waits for that task's delivery to main \(Captain ruling b\)
- Residual: bootstrap window is the 15-minute ceiling, not re-stamped after deploy
- Residual: accept station S43 override
- How to verify: run `cd experiments/netlify-refine-poc/qnow-next && npx vitest run --config vitest.config.ts test/identity-bootstrap.test.ts -t "admits create-users after a 12-minute deploy" 2>&1 | grep -c "Tests  1 passed"` (expect the retained exit above); apply `sed -i '' 's/BOOTSTRAP_WINDOW_MS = 15 \\* 60_000/BOOTSTRAP_WINDOW_MS = 10 * 60_000/' experiments/netlify-refine-poc/qnow-next/hosted/acceptance-full-run-dependencies.mjs`; run it again (expect the removed exit above).

## Layer 4: DEV-37 — DEV-37

- Residual: not dispatched: prerequisites DEV-36 and the hosted runner are not on main; cloud brief prepared \(evidence/dispatch-DEV-37-cloud.md\)

## Unaccounted

- none.

## Not handed off

- DEV-37: carried

## For the Captain

- Delivery units to approve: https://github.com/iamcxa/qnow/pull/1177 (DEV-25), https://github.com/iamcxa/qnow/pull/1180 (DEV-35), https://github.com/iamcxa/qnow/pull/1174 (DEV-36).
- Residual (DEV-25): merged as c7a905a9 after a moved_base merge \(qnow ruleset: head up to date\)
- Residual (DEV-25): hosted Neon behaviour unproven \(PR's own 'Not proven'\)
- Residual (DEV-25): customer identity provider undecided → DEV-132; revoke-by-subject → DEV-133
- Residual (DEV-25): accept station S43 override \(FO re-ran the pair\)
- Residual (DEV-35): first merged into the wrong base \(S45\), reverted; re-landed on main via #1180 as 820f6fb5 \(cherry-picks\)
- Residual (DEV-35): display-dependent journey evidence pending the DEV-37 cloud run
- Residual (DEV-35): accept station S43 override
- Residual (DEV-36): cannot land on main alone: the whole hosted/ runner \(26 files\) exists only on the staging-qualification branch; waits for that task's delivery to main \(Captain ruling b\)
- Residual (DEV-36): bootstrap window is the 15-minute ceiling, not re-stamped after deploy
- Residual (DEV-36): accept station S43 override
- Residual (DEV-37): not dispatched: prerequisites DEV-36 and the hosted runner are not on main; cloud brief prepared \(evidence/dispatch-DEV-37-cloud.md\)

## Decisions made under `defaults`

- 2026-09-07T01:45:15Z — **DEV-25 \(#1177, base 038222ea head eeb7d4f8\)**: accept station not applicable \(pre-built PR, no worker Evidence block\); review station started — code-reviewer, tob-security-reviewer, silent-failure-hunter \(Sonnet\) on the diff in the local qnow clone.
- 2026-09-07T01:47:42Z — #1177: silent-failure-hunter returned no findings \(no skips, no swallowed errors, tests wired into \`npm test\`\). e2e station first pass \(zsh dropped exit codes — rerun under bash in flight\): type-check clean, cleanup and web-artifact node tests pass, probe 4/4 HOLDS against netlify/gotrue master \(pushed 2026-09-02\).
- 2026-09-07T01:48:25Z — **#1177 e2e station \(PR's own verification at head eeb7d4f8, local Docker PostgreSQL\)**: type-check exit 0; \`npm test\` exit 0 — vitest 2 + 104 + 65 = 171 cases, node --test 2 + 1, exactly the counts the PR body claims; probe exit 0, 4/4 HOLDS. Logs in evidence/.
- 2026-09-07T01:53:48Z — **review station on #1177: disposition \`block\`** — 8 findings \(2 security: otp-verify attempt bound absent from the contract/reference/conformance; refusal reason not collapsed at the boundary; 3 correctness; 2 test-coverage; 1 accounting\). Revoke-by-subject and matrix scoring → DEV-133 \(port design beyond this PR\). Repair round 1 dispatched to a local Sonnet worker on the PR branch.
- 2026-09-07T01:55:47Z — **DEV-35 \(#1175, base 36a8bef4 head c0c31459\)**: review station started ahead of its merge slot \(FO stations use no worker workspace, so concurrency 1 is untouched\): code-reviewer, silent-failure-hunter, tob-security-reviewer; e2e station running the PR's own commands at the head on the macOS host \(the Conductor-image proof stays the PR's own table; recorded as such\).
- 2026-09-07T01:56:41Z — **#1175 e2e station on the macOS host**: npm ci 0, type-check 0; \`test:headed-browser\` 6/18 pass \(the 12 failures are the display-dependent cases\); \`diagnose:headed-browser\` exits 1 with \`HEADED_BROWSER_ENVIRONMENT_UNAVAILABLE:NO_DISPLAY_SERVER\` — the exact blocker the planner is specified to report on a host with no X server. The PR targets the Conductor Cloud Linux image; its own table is the image evidence. **Decision under defaults \(FO\)**: the cloud run of \`diagnose:headed-browser\` at the merge head is folded into the DEV-37 cloud workspace \(it is DEV-37's stated 前置 and uses the one approved workspace\), recorded then as DEV-35's AC-2 evidence.
- 2026-09-07T02:04:46Z — **review station on #1175: disposition \`block\`** — 8 findings \(1 compatibility: /proc read unguarded; 5 correctness: receipts drop stderr/launch error text, finally without try, bare catch on executablePath, spawn pid recorded before the error event, LOCAL_STACK fallback order backwards; 1 test-coverage: SIGINT not exercised; 1 accounting\). Repair round queued **after** #1177's repair worker finishes: repair worktrees count against the approval's 1 workspace \(S39 lesson\), so repairs run one at a time.
- 2026-09-07T02:05:38Z — **DEV-36 \(#1174, base 073fee11 head 3c65da1e\)**: review station started ahead of its slot — code-reviewer, tob-security-reviewer, silent-failure-hunter. Its e2e \(runner npm script, zero provider gates\) needs hosted credentials; it is folded into the DEV-37 cloud workspace run like #1175's preflight.
- 2026-09-07T02:24:53Z — Two background agents stalled at the same moment \(harness stream watchdog, 600 s no progress\): the #1177 repair worker \(after verifying its without-it exits, before commit\) and the #1174 silent-failure reviewer \(mid-file\). Both resumed by message with the same agent, not re-dispatched \(no double-writing of the repair worktree\). Recorded as **S42**: a stall is not a failure; resume the same agent first.
- 2026-09-07T02:29:11Z — **#1177 repair round 1 returned** \(2c794892, fast-forward on the PR branch; 5 findings fixed; conformance 22 passed, tenancy 13 passed, npm test exit 0 per worker\). Accept station REFUSED on AC-3: its path extractor knows only py/md/sh/json/yaml/yml/txt and this repo is TypeScript — **S43**, ticket filed. FO is re-running the without-it pair and npm test at the candidate itself; acceptance will be recorded as an FO override with that log if the pair holds. Repair worker's worktree removed; #1175 repair dispatched next \(one worker at a time\).
- 2026-09-07T02:29:51Z — **#1177 round 1 accepted by FO override** \(2c794892\): station refused only on the AC-3 extension list \(S43/DEV-134\); FO re-ran the pair at the candidate \(retained 0 / removed 1\) and \`npm test\` \(exit 0; vitest 106+66+2, node 2+1\). Both security findings closed; DEV-133 holds the port-design items. **#1177 ready for the Captain's merge** once its CI is green on the new head. #1174 code-reviewer: no findings; single-deploy/no-retry and secret zeroization verified with tests.
- 2026-09-07T02:33:25Z — **review station on #1174: disposition \`block\`** — 8 findings \(1 security: secret-classified run id in a /tmp directory name; 6 correctness incl. one that would sink DEV-37's single deploy — the 10-minute bootstrap window is stamped before a deploy allowed 20 minutes; 1 test-coverage\). Repair round queued behind #1175's worker \(one at a time\).
- 2026-09-07T02:48:10Z — **#1175 round 1 accepted by FO override** \(c6c4fe19; station refused only on the AC-3 extension list\). FO re-ran the pair by script: retained 0 / mutated 1 / base 1; type-check 0; macOS run 21 tests: 8 pass, 1 skipped \(SIGINT, no display\), 12 display/proc-dependent fail as at base. All 8 findings closed. **#1175 ready for the Captain's merge after #1177.** #1174 repair worker dispatched.
- 2026-09-07T03:26:02Z — **#1174 round 1 accepted by FO override** \(b5d87ed8; station S43\). FO verified: pair 0/1, type-check 0, test:unit 180, netlify-package 106, self-check 0. All 8 findings closed. Residual: bootstrap window is now the 15-minute ceiling, not re-stamped after deploy — DEV-37's single deploy must finish under 15 min. All three prerequisite PRs are now accepted; merge order #1177 → #1175 → #1174. DEV-37 cloud dispatch brief prepared \(evidence/dispatch-DEV-37-cloud.md\).
- 2026-09-07T03:35:29Z — **S44 \(FO conduct\)**: the FO handed the Captain an \(a\)/\(b\) choice on whether to merge #1175/#1174 before their cloud-image journey run, instead of deciding it at the station. Ship kernel: the FO decides station questions under \`defaults\` and records them; the Captain gets a verdict with the checks named. Decision taken now: merge all three; the exact-revision journey evidence for #1175/#1174 is produced by the DEV-37 workspace run at the merge head \(its first two steps\), recorded as each ticket's AC-2. The Captain's merge authority is unchanged.
- 2026-09-07T03:38:57Z — **merge station**: #1177 required a main merge first \(qnow ruleset: head must be up to date; moved_base 8b130a0b\), then squash-merged as c7a905a9. DEV-25 Done. #1175 next \(same path\).
- 2026-09-07T03:43:53Z — **S45 \(merge station, FO error\)**: the FO merged #1177 \(base main → c7a905a9, correct\) and then #1175 **without verifying its base**: #1175 and #1174 are based on \`spacedock-ensign/qnow-next-hosted-staging-qualification\`, not main. #1175 squash-merged into that branch \(dbdc8378\) with a merge resolution whose \`scripts/conductor-cloud-setup.sh\` failed \`bash -n\` \(my keep-both lost the Xvfb block's closing \`fi\`; my script printed the check but did not gate on it\). Containment: script repaired on the branch \(88796809, bash -n 0\); #1174, auto-closed at the moment of that merge, reopened. main is untouched by #1175. Rule for DEV-114: verify \`baseRefName == trunk\` before merging and gate every merge-resolution on the repo's syntax/type checks. DEV-35 AC-3 \(\`git log origin/main | grep '#1175'\`\) is NOT met; the receipt's base_branch is main.
- 2026-09-07 — **Captain ruled B** \(「CI 是 main → staging → prod，從來不會反過來」\): work lands on main only. Actions: my two commits on \`spacedock-ensign/qnow-next-hosted-staging-qualification\` reverted with \`git revert\` \(aeb08633; no force-push\); #1175 re-landed on main as PR #1180 → 820f6fb5 \(cherry-picks of its six commits; package.json kept only scripts whose targets exist on main\). **S46 \(FO\)**: three regex-based attempts left \`scripts/conductor-cloud-setup.sh\` syntax-broken because the printed \`bash -n\` was never a gate; stopped at the circuit breaker and rebuilt the file as main's version + the Xvfb block, gated on the exit code. DEV-35 Done.
- 2026-09-07T04:03:07Z — **Captain ruled \(b\)**: the staging-qualification task delivers to main itself; this batch closes with DEV-25 and DEV-35 on main; DEV-36 \(#1174, open, base = that branch, accepted candidate b5d87ed8\) and DEV-37 wait for that delivery. Fact for the record: \`experiments/netlify-refine-poc/qnow-next/hosted/\` \(26 files, the entire hosted acceptance runner\) exists only on \`spacedock-ensign/qnow-next-hosted-staging-qualification\` \(48 ahead of main, last real commit 2026-08-31; entity r33jtp5370kxngzbr6cd7rej 'Qualify QNow Next claim/readback on isolated hosted staging', Pilot, status implementation since 2026-08-23, no PR\).
- 2026-09-07T04:06:04Z — Correction: the previous state commit said 'receipt validated' while the validator had refused \(S47 was appended after the ship writer ran — the same slip as batch 471aa64c\). Writers re-run with S47 present; result in this commit's message.
- 2026-09-07T04:06:32Z — **Batch 0f273392a113 close: still DRAFT.** DEV-25, DEV-35 merged on main; DEV-36 pr_open \(#1174, waits for the staging-qualification task's delivery\); DEV-37 carried. Defects S42–S47 → DEV-114, DEV-134, DEV-135. UAT document: uat.md.
- 2026-09-07T04:06:53Z — Close receipt refused: workspaces_created 3 > approved 1. The approval counted only the DEV-37 cloud worker; the three local repair workers \(one per PR\) are workspaces too. **S48** \(second occurrence of the S39 class\): the FO's approval recommendation must count repair workers \(up to repair_rounds × items\) plus build workers. Captain to re-sign at 3 or close with the overrun as a defect.
- 2026-09-07 — **Provenance of \`spacedock-ensign/qnow-next-hosted-staging-qualification\`** \(Captain asked\): no local Claude session owns it \(barcelona-8e answered "not mine"; project-65 asked, pending\); Conductor transcripts mention it only from the two child workspaces "DEV-35 Cloud headed Playwright" \(3f53345e\) and "DEV-36 QNow ESM runner" \(64d00bbd\), both sleeping since 2026-09-01. The 48-commit parent work was done in a local spacedock-ensign worktree by a session that is gone; its record is qnow's state branch: entity r33jtp5370kxngzbr6cd7rej, Pilot, ideation approved 2026-08-23 with the rule "implementation may prepare code and zero-mutation preflight only; the first hosted mutation must stop for an exact resource, operation, cleanup-owner and spend authorization". Child reports: DEV-35 gates at c0c31459 all green incl. \`diagnose:headed-browser\` admitted \(3 contexts, remainders 0\); DEV-36 gates at 3c65da1e green \(unit 175, netlify-package 99/100 with one baseline-only failure, headed 29/29 under Xvfb, hosted-gates 18/18\), with the stated open risk: "the package-default provider path has never been rehearsed against the real provider — the first real run must be watched."
- 2026-09-07T04:16:47Z — Captain linked Conductor workspace ea1c7833-459b-4fa9-8879-6ec00b64d3b2; it is not visible to this session's Conductor account \(77 workspaces across subspace-relay / qnow / kc-claude-plugins, no carlove project, no match\) — HTTP 404 on get and no transcript rows. The only 2026-08-31 qnow workspace \(b14043f1 'QNow Cloud Playwright preflight', codex\) was a read-only preflight probe at 36a8bef4, not the author of the 48 commits. Provenance of the parent branch remains: qnow state-branch entity r33jtp5370kxngzbr6cd7rej + the two child workspaces' reports.

(24 defaults decisions listed above.)
