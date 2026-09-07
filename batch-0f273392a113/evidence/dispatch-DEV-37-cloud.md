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
