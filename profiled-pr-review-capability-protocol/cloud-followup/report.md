# Single cloud follow-up — bounded partial evidence

Approval `1e32bb69a198002f25853d66e56f528e4c8a746c` was supported-committed, synced and reread before launch. Exactly one workspace, initial session and message were used; no retry, follow-up, fallback, subagent, real PR review, installation, permission change or product edit. Checklist: 3 DONE / 0 SKIPPED / 0 FAILED for executing and reporting the bounded experiment; this is **not** a full isolation or successful model-turn result.

## Binding and inputs

- Project `8f58f9d4-cb71-443a-b64d-c2a225248c7b`, repository `https://github.com/iamcxa/kc-claude-plugins`, freshly read remote main `a729caee100e68ec0f39e975680ee0808213e401`. Root setup/copy entries `.conductor`, `conductor.json`, `.worktreeinclude` absent at that revision; organization defaults remain unknown, not disabled.
- Workspace `c5d8ac57-5594-4726-adcf-289159d36f62`; session `81c917e1-f805-4444-b87a-df8a01a66449`; message `0f22551a-814a-44e4-bbc7-f4fc55ae48db`. [Owned workspace](conductor://workspace?id=c5d8ac57-5594-4726-adcf-289159d36f62).
- Requested `claude` / `opus-5-1m` / `medium`, no fast-mode option; resolved `claude-opus-5[1m]`, medium. No independent effective-speed guarantee is inferred.
- External controller `/private/tmp/pilot-cloud-followup.Cjh5w4`; monitor PID 45634, independently armed cleanup PID 45661. Unchanged [monitor core](../cloud-local-repair/monitor.py) SHA-256 `54d55e640c85b7957173cc3b66a23751fe3be2d515389265669447a82c8f890b`; [one-run glue](run-once.py), [prompt](prompt.md), [probe](probe.sh).
- Prior SHA-256 frozen before submission: `6cc61c7395e7719f9738f3076d5efbbd13c7a9eb75743f838cb3698f73fc8608`; current file absent. These are actual local controller checks, not cloud-returned measurements.

## Observed sequence (UTC, local receipt clocks unless stated)

| Observation | Time / evidence |
|---|---|
| Independent cleanup armed; creation requested | 05:55:31.669923; 05:55:31.685698 |
| Ready and model binding observed | 05:55:40.997104; setup 9.311350 seconds, below 180 |
| Frozen submission / deadline | 05:55:40.997316 / 06:00:40.997316; monotonic 1121305.629676333 / 1121605.629676333 |
| First working readback | 05:55:45.932227, provider updatedAt 05:55:42.313 |
| Normal tool result | Provider receivedAt 05:56:06.566, `is_error:false` |
| Actual nonzero tool result | Provider receivedAt 05:56:15.220, `Exit code 7`, `is_error:true` |
| Third foreground Bash requested | Provider receivedAt 05:56:24.965, timeout 600000; finite 360-second payload |
| Last working before cancel | 06:00:05.311092; third tool had no returned result |
| Cancel request / response | 06:00:12.087876 / 06:00:13.126689, exit 0; response still said working |
| First post-cancel idle | 06:00:14.039376, provider updatedAt 06:00:13.097 |
| Archive request / local timeout | 06:00:15.873881 / 06:00:25.881859; response UNKNOWN, not retried |
| Archive confirmed / final idle | 06:00:26.836151 / 06:00:33.830122 |
| Controller finished / watchdog exited | 06:00:33.830761 / 06:00:33.941909; both PIDs absent on subsequent `ps` |

Raw control evidence: [cancel](call-45634-095.json), [archive timeout](call-45634-099.json), [archived readback](call-45634-100.json), [final cleanup](final-cleanup.json), [finished controller](finished.json), [watchdog exit](watchdog-exit.json). Cancellation response alone did not prove stop; the subsequent exact session idle did. All control mutations were exact-identity checked, finite, and one-shot guarded against duplicate primary/watchdog/fallback calls.

## Separate conclusions

- **Real shell exit behavior: verified.** Normal work succeeds; direct `exec` preserves intended exit 7 in the raw tool error. Their actual host-target attempts return ENOENT (2), not permission-denied; local prior stays byte-identical and current absent. This proves these path attempts, not all authority exclusion.
- **External provider lifecycle: verified narrowly.** A pending third Bash and repeated working observations precede external cancellation; exact idle and archived states follow before the frozen 300-second bound. There is no third tool result or process-liveness observation. The payload includes a distinct-process-group descendant, but its actual creation and death are **unverified**; archive/idle do not prove either.
- **Live controller behavior: verified for this path, not universally.** Unchanged core returned `deadline_incomplete`, exit 1; archive timeout stayed `unknown`, while archive readback, final status, transcript and canary steps succeeded. Diagnostic capture did not block cleanup. No malformed-response failure occurred this time; prior local negative tests remain separate evidence. Independent watchdog was armed and exited after primary archive; takeover was not exercised.
- **Authority: incomplete.** SDK initialization advertises no `RunLocalCommand`, but does advertise `RemoteTrigger`, other broad tools and Linear/Netlify/PostHog integrations, with `permissionMode:bypassPermissions`. No concrete local bridge was invoked or observed. Absence of one tool name is not complete tool/credential isolation; organization defaults and effective grants remain unverified.
- **Usage/cost: unknown.** Complete collected transcript has 24 events but no SDK `type:result` event, cost or aggregate usage receipt. No auxiliary usage attribution can be established. Previous SDK list-based US$0.483311 is historical reference only, not this run's fee, invoice, per-PR cost or dollar cap. Neither speed nor review quality is measured.

[Core result](result.json) preserves all per-step outcomes and sanitized raw events. [Manifest](manifest.json) binds 129 original files to durable copies by SHA-256; private thinking/signatures and auth-status text are redacted, original bytes stay outside sync. No returned text was executed by the controller.

Product remains clean at `9bb526170156a44cff90e2a2fab9eeab081e0eb1` on `feature/kc-pr-review-capability-protocol-pilot`; base `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`, actual 6,431 / 20 / 1,939 versus unchanged 6,600 / 20 / 1,800 stops. Earlier evidence and held validation/status/pin are preserved. Original five repairs, focused reduction, CI sequence, fresh review and real blind quality/speed remain open. This one attempt ends here; FO owns the next decision.
