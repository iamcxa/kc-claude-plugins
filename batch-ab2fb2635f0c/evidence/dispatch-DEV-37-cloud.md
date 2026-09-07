# DEV-37 dispatch brief (Conductor cloud worker) — prepared 2026-09-07, dispatch after #1177, #1175, #1174 merge

Workspace: one Conductor cloud workspace on iamcxa/qnow main at the merge head of #1174 (record the SHA). Environment carries the six production/functions secrets (Captain confirmed).
Order inside the run (one run, one deploy, no retry; first failure → cleanup only):
1. `cd experiments/netlify-refine-poc/qnow-next && npm ci`
2. DEV-35 AC-2 evidence: `env -u DISPLAY npm run diagnose:headed-browser` → record the receipt (browserSource, contexts: 3, isolatedReadbacks) and exit 0.
3. DEV-36 AC-2 evidence: `npm run acceptance:hosted:full-run:self-check` → providerCalls 0, exit 0.
4. DEV-37: `npm run acceptance:hosted:full-run` per the ticket's 單次執行範圍; deploy must finish under the 15-minute bootstrap window (residual from #1174 r1). Receipt to `docs/evidence/qnow-poc-acceptance-receipt.json` (committed by the run) and a copy to this batch's evidence/.
5. 清理驗收 six steps; census 0 logged; stale token 401 logged.
6. Evidence block per the batch template; the accept station will refuse on AC-3 (S43) — FO verifies by script.
Executor: cloud worker (not a local subagent). The Captain's approval covers exactly this one workspace.

## Amendments from DEV-136/137 (2026-09-07)

- main now carries native migrations 0000–0009 (10). 0008 revokes and 0009 re-grants `qnow_app` SELECT on `qnow_staff_assignments` (PoC ruling; production scoped read = DEV-140). The preflight and every hosted manifest check expect 10; a staging database that already applied 0000–0007 will receive 0008 and 0009 on this deploy — say so in the run log.
- `deployOnce()` now throws `ACCEPTANCE_DEPLOY_LIMIT_EXCEEDED` on a second call within one session; the run is one deploy by construction, not by discipline. If the run needs a retry, it is a new session and the Captain says so.
- @netlify/open-api must resolve 2.57.0 (lock restored to the qualification branch's); `acceptance:hosted:self-check` refuses otherwise. Run it before the full run and quote the line.
- The full-run entrypoint comes from DEV-36 (#1174 rebased onto main); use the script name the merged package.json carries, and quote it.
- Run `npm run test:headed-browser` first in the Linux workspace and quote its exit: on macOS it fails with HEADED_BROWSER_ENVIRONMENT_UNAVAILABLE:NO_PROC_PROCESS_TABLE at main and at the DEV-36 head alike, so the cloud run is the only place it is measured.
- The verbose-deploy diagnostic redacts JSON-quoted secrets as of #1182; still treat its output as sensitive and keep it in the run receipt, not in chat.
