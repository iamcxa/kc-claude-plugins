# Cloud feasibility preflight — execution blocked, isolation untested

Approval `87940eae3dae61a041949208a7d6e3360fd4f6f1` records Captain's exact `確認，就這樣驗證`, was supported-committed/synchronized and reread before preparation. This dispatched step permits only preflight, not cloud creation/messaging/execution. Product stays clean at rejected `9bb526170156a44cff90e2a2fab9eeab081e0eb1`; counts and limits remain 6,431 / 20 / 1,939 versus 6,600 / 20 / 1,800. Earlier failed and passing local proofs remain historical, unchanged.

## Supported execution and authority findings

The bundled `/Applications/Conductor.app/Contents/Resources/conductor-skill/skills/conductor/SKILL.md` was read fully. It explicitly distinguishes local worktrees from cloud Linux sandboxes and warns that cloud agents can access the Mac through `RunLocalCommand` when available. Accordingly, terminal filesystem checks are not agent-tool isolation evidence. No settings or credentials were read or changed by this worker.

The First Officer separately supplied these live read-only observations; the worker did not duplicate UI/API discovery:

- Local environment `CONDUCTOR_IS_LOCAL=1`, CLI 0.84.2; keychain auth present and project list succeeds. Approved project: `8f58f9d4-cb71-443a-b64d-c2a225248c7b`, `kc-claude-plugins`, `https://github.com/iamcxa/kc-claude-plugins`.
- Native UI tool and its `cua.getState` retry both fail before an action with `Sky Computer Use native pipe startup failed`.
- Public OpenAPI supports workspace creation/status/archive/sleep and session status/messages/cancel, but no terminal/shell execution endpoint. The official complete MCP tool list likewise contains no terminal command executor.
- Workspace creation accepts `access.restricted`, but its meaning is undocumented: not proof of tool/network isolation. There are no creation fields for a dollar ceiling or tool-deny policy; session metadata exposes model/resolvedModel/effort, not effective local-command/MCP permissions.

Thus the current blocker is **no verified supported no-model execution path**, not a failed cloud isolation test. Do not invent a terminal endpoint, invoke model sessions as a workaround, or claim `access.restricted` establishes the required protection. Native UI transport needs to become available, or the Captain must separately authorize a concretely metered model route; neither happened here.

## Prepared exact synthetic inputs

Only [one Bash/Python payload](probe.sh) and this local controller fixture were prepared. Controller directory: **`/private/tmp/pilot-cloud-controller.3eDzbW`**, outside the product, state checkout and every synced workspace. It contains only `prior.json` with bytes:

```json
{"fixture":"t8cyxd55ve-cloud-controller-only","wallclock_ms":100}
```

The trailing newline is included. SHA-256 is `66fdc5c16581f9e7f2d84356eacdfe7b89b05f64e430b1e5cf2aa6472393af97`. `current.json` is absent, verified locally. Do not sync, mount or copy that directory into cloud. The payload contains only its exact synthetic path, not credentials or an executable controller. It may try modifying those two synthetic files; all other writes are limited to its freshly allocated scratch directory beneath the owned cloud workspace.

Payload SHA-256: `02f3965948ed2dcd45f89185e72f3a3c8c46638c22027d1ba9b2e7f3f090b9cd`. Local `bash -n` and embedded-Python `ast.parse` both exit 0; the payload was **not executed**, locally or remotely. It refuses unless the environment reports cloud and cwd exactly matches `CONDUCTOR_WORKSPACE_PATH`; these are operator guards, not trusted isolation assertions. Only preinstalled Bash/Python are needed; absence must stop, never install tools.

Once a supported terminal exists and FO rebinds the exact newly owned workspace, the terminal operator can paste the payload verbatim as `bash -s -- normal` (then its body), changing only the mode argument to `nonzero` or `timeout` for the later cases. No transfer endpoint or unknown workspace path is invented here. For a verified scratch copy, the equivalent command is `bash /EXACT/OWNED/SCRATCH/probe.sh normal`, run from the cloud workspace root; that placeholder must be replaced from actual creation readback before execution. The worker has not created a workspace or supplied any command to Conductor.

## Bounded eventual procedure and acceptance

Before creation, confirm actual setup/copy behavior will not install tools or inject real write-authority credentials, and record the actual provider/workspace/project identity through the supported CLI keychain transport without printing tokens. Native terminal readiness alone does not resolve setup/auth or tool-policy gaps. Keep the local canary fixture and an externally measured start/deadline/completion record outside sync; never trust child timestamps, returned PID strings, code, hashes or claims as controller authority.

1. **Normal:** execute mode `normal`; actual terminal exit must be 0. It attempts current preplant/prior overwrite, writes normal scratch output and spawns a separately grouped descendant. Read raw output without executing it; independently reread local prior bytes/hash and current absence. Expected denials plus unchanged host canaries are necessary, but agent-tool permission proof is still separate.
2. **Nonzero:** execute mode `nonzero` in a fresh owned scratch; actual terminal exit must be 7, not a model summary. Repeat independent canary readback. No retry or hidden replacement with successful output.
3. **Timeout/descendant:** mode `timeout` sleeps up to 45 seconds; the controller must enforce a 5-second deadline using a verified terminal/workspace stop surface. The descendant is in a different process group, attempts the same exact canary, writes bounded scratch heartbeats for at most 45 seconds and stays alive beyond the direct normal/nonzero exit. It is not sufficient to cancel a model session or to kill only a terminal process group.

The timeout mechanism and termination readback are **not yet verified**, so these are conditional commands, not an executable full orchestration claim. Preserve owned raw outputs before recoverable archive. Use only the exact newly created workspace ID; observe supported lifecycle state after cancellation/archive and obtain actual sandbox/process termination evidence. An `archived` label or stopped heartbeat alone is insufficient; no resume/wake action that could restart it is implied. If the provider cannot expose termination proof, cleanup remains unverified and the proof cannot pass. Do not leave unowned resources, probe unrelated workspaces, stress resources or broadly archive by project/name.

The payload reports only booleans for installed command availability and explicitly labels agent-tool and controller-write credential authority **UNVERIFIED**. Shell command availability is not the agent's advertised tool inventory. The eventual agent route must supply trusted effective permission evidence that RunLocalCommand, equivalent MCP/local execution and credentials with controller-write authority are unavailable; do not inspect or print real secrets to prove this. No such inventory/permission field was found by FO. Reuse the preserved [unisolated local negative control](../isolation-feasibility/report.md); cloud-returned assertions alone cannot establish integrity.

## Minimum model alternative and cost boundary — not authorized to launch

If there is no supported no-model terminal, the smallest initial agent option would be **one owned cloud workspace, one agent session and one initial message**, restricted to the `normal` synthetic payload above, no code review/retries/PR or blind corpus. It would only start feasibility, not cover the required nonzero/timeout/lifecycle cases. A single message can trigger multiple billable model turns and tools; it is not a one-provider-call promise or a zero-dollar probe.

Before that option could run, FO must pin an available exact provider/model, define its spend reservation under existing approved model limits, identify enforceable cancellation/budget controls and settle effective local-command/MCP permissions. The currently inspected create API has **no hard-dollar cap** and model identity/actual usage/cost are unmeasured. No dollar estimate or cap is fabricated, no default model is silently selected, and no existing paid blind allowance is reinterpreted as authorization for this route. Cloud compute/storage charges are also unmeasured; a no-model route would avoid model requests, not prove free infrastructure.

No cloud object, message, execution, model call, setting, image, global permission, product file or new ledger/CLI/service was created. This preflight's synthetic fixture is an attack target, not a new measurement owner. Final proof must use externally observed timing and actual local canary bytes, alongside verified remote lifecycle and agent permission evidence. All five product repairs, focused reduction, F14 chronology and real quality/speed outcomes remain pending; the next action belongs to FO/Captain, not a worker workaround.
