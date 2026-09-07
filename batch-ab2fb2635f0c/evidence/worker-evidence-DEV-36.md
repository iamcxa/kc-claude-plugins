## Evidence (rebase)
DISPATCH_TOKEN: dev36-2026-09-07
CANDIDATE_SHA: 65c0143a46dea4c2baab50343b180c1ef22b0b39
BASE_SHA: ac59c26adffad4e942493c192adeabf040142a94
PR: #1174 base retargeted to main (was spacedock-ensign/qnow-next-hosted-staging-qualification); force-pushed with --force-with-lease
COMMITS: brief said 10; PR had 15 — 4 DEV-35 "headed Playwright display" commits dropped (main's #1180 supersedes them by 558 lines; one touched scripts/conductor-cloud-setup.sh); 11 kept, 18 files, +3090/−9 vs main
DROPPED: qualification-only AGENTS.md "Hosted migration ownership" prose; LOCAL_STACK.md branch prose; DEV-35 headed-browser files (main's kept)
CONFLICTS: AGENTS.md ×2 (kept #1174's hunks under new heading "Hosted acceptance full run"); acceptance-netlify-session.ts + test ×2 — main's deployCount limit guard and #1174's deployAttempted cleanup latch kept as two independent mechanisms with both test sets; four files auto-merged
HIDDEN BUG FIXED: hosted/acceptance-full-run-dependencies.mjs EXPECTED_MIGRATIONS 8→10 plus five fixture/assertion sites (only the tip commit passes the run-mode test; intermediate commits not claimed)
TESTS (worker): npm ci 0 (lock untouched); npm test 0 (all 9 stages); acceptance:hosted:full-run:self-check 0 — {"status":"admitted","providerCalls":0,"browserLaunches":0,"deploys":0,"netlifyOpenApiVersion":"2.57.0",...,"exactRevisionEnforced":true,"valuesExposed":false}
RESIDUAL (worker): npm run test:headed-browser not in npm test's chain, not run — compatibility of #1174's browser adapter with main's DEV-35 planner unmeasured
FO: running full npm test + full-run self-check + test:headed-browser at 65c0143a (log /tmp/npmtest36.log, /tmp/headed36.log); rebase-reconciliation review dispatched
