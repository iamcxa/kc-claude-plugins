# Local monitor/exit repair — no cloud execution

The revised monitor passes **19 local tests**. The preserved old behavior fails **four regression assertions** as expected. These are local control-flow/exit-code fixes, not new cloud isolation, remote-stop or product evidence. Approval `dec0f52dff489381da1dc5c6f6b71677931ff7cd` was supported-committed/synced/reread before edits; no real Conductor/API/model command was run.

## Delivered scope and safety

[monitor.py](monitor.py) is one revised monitor core with a minimal dormant `CommandTransport`. First Officer clarified that fake-only means **test execution**, not a parallel simulation replacing the requested monitor: tests now inject their fake subprocess and clock into the exact same command/timeout/parse path. No production core is duplicated in the fake. Default live construction refuses unless explicitly enabled; module execution always refuses; there is no workspace-create/message-create/retry entrypoint. The transport allowlist is limited to the previously observed read/cancel/archive commands. Live use remains unauthorized this turn and would need exact owned identity binding and a separately approved run.

Tests structurally patch real `subprocess.run` to raise while exercising the monitor; the injected runner is a closed synthetic response table. Clock advancement is synthetic. Only the explicitly local Bash/Python exit tests launch actual subprocesses, against fixed owned commands and temporary fixtures. Original `cloud-once/monitor-once.py` is never imported: the RED harness parses its AST and runs either extracted definitions/cleanup or the original body with all imports removed and subprocess replaced by the closed fake. Thus no original top-level submission can reach a real transport. No network, credentials, cloud lifecycle action, tool-inventory exploration, install, settings, CI or reviewer was used.

## Repairs exercised

| Boundary | Repaired behavior and falsifier |
|---|---|
| Malformed/truncated output | Raw synthetic response remains in call evidence; invalid JSON raises classified `malformed_json`, never missing-response KeyError or success. Both monitoring and final capture failures persist a nonzero final result. |
| Nested JSON | Null/list `content` or `rawPayload` is rejected as `invalid_message_shape` before terminal access. All four shapes first reproduced AttributeError and now persist failure plus identity-safe cleanup. |
| Cleanup independence | Cancel, status, fresh archive identity, archive, bounded readbacks, final transcript and canary each retain their own ok/error/unknown/refused state. Transcript collection follows cleanup; its failure cannot suppress archive. Cancellation failure also cannot suppress archive. |
| Unknown mutation outcome | Command timeout remains unknown. Archive timeout followed by archived readback retains both facts independently, performs only one archive attempt and still yields nonzero because an observation failed. Missing archive readback is not success. |
| Exact identity | Structured workspace id/projectId and actual session-row id must match; a target session ID hidden in another row's name does not authorize mutation. Wrong identities refuse cancel/archive. Status/event session bindings are also checked. |
| Transcript/terminal | Limit-10 cursor pages, maximum three per collection; partial events survive malformed/incomplete follow-up and duplicate/foreign records fail closed. Actual matching SDK result plus repeated idle observation is needed; idle without a terminal result reaches the bounded deadline and is nonzero. |
| Exit status | The local conditional shell pattern captures the child status and explicitly exits with it: normal 0, explicit 7, synthetic TERM/error 143 and invalid mode 64. This fixes the original trailing-echo mask; it does not turn SIGTERM into a remote timeout proof. |
| Controller process | `Monitor.run()` returns and persists 1 for failed/incomplete observations, 0 only for verified synthetic terminal plus clean cleanup/readbacks. Actual local controller subprocess tests propagate both values with `SystemExit(code)`; default direct module execution refuses rather than silently running. |
| Frozen start | Caller-supplied submission/deadline and expected prior SHA are required; no baseline is derived after submission and no new 300-second window starts when monitoring starts. Pre-start tampering fails before polling; delayed and already-expired starts retain the original deadline and proceed to bounded cleanup. |

[preserve-exit.sh](preserve-exit.sh) intentionally accepts only the fixed local synthetic modes, not arbitrary commands. Its `if child; then status=0; else status=$?; fi; ...; exit "$status"` pattern is the revision to use around any later authorized cloud payload; the original prompt is unchanged. Local fake deadline tests verify cancellation is attempted before synthetic 300 seconds, but cannot prove a provider will stop by a real deadline.

## Fresh RED/GREEN evidence

Commands actually run with the existing Recce venv activated and `which python` confirmed; paths below are relative to this state-owned directory:

```text
/usr/bin/time -p python -B legacy-red.test.py
/usr/bin/time -p python -B monitor.test.py
```

- [Old-behavior RED](legacy-red.log): exit **1**, 4 tests, **3 failures + 1 error**, unittest **0.090 s**, wall **0.16 s**. Actual symptoms: malformed JSON → KeyError; final transcript failure skips archive; child exit 7 becomes outer 0; old controller failure still exits 0. These are intentionally failing counterfactual assertions, not ignored failures in the repaired suite.
- [Nested-shape RED](nested-json-red.log): exit **1**, one test with **four AttributeErrors**, **0.004 s**, against pre-fix draft monitor SHA-256 `c48a1cecb61f0a522e24cf3d5a40a5cf99b38e66928693f69f29d4bbc0b71707`. FO's additional finding was reproduced before structural validation was added.
- [Frozen-start RED](frozen-start-red.log): exit **1**, two tests with **three failed assertions**, **0.010 s**, against the prior `2101871c…` draft: starts at synthetic 250/310 seconds incorrectly delayed cancellation to 515.6/575.6, and pre-start tampering was accepted as the new baseline. All three assertions pass after requiring frozen caller inputs.
- [Final GREEN](green.log): exit **0**, **19 tests / 0 failures**, unittest **0.333 s**, wall **0.47 s**. Independent temporary-directory cases cover all named failures and actual shell/controller statuses; source imports do not execute the dormant adapter. The earlier 17-test run is retained separately as intermediate evidence, not substituted for the final suite.

Exact final SHA-256: monitor `54d55e640c85b7957173cc3b66a23751fe3be2d515389265669447a82c8f890b`; test `ec9cd1e5425c645df31da245c78e140789fab4941fa380fa0aec993e4ca8b6c0`; exit wrapper `821eec7e49a948c34cc415a0587c45c619f56478c79cd1401971713248924442`. Preserved old monitor hash `860f29a47a8269e76bcb817cdad33013b366b3e7a690908f3badc088308b51a3`; `git diff bcc531470f7238225c696d6a7a8f196bc7bbfd7c -- profiled-pr-review-capability-protocol/cloud-once` is empty, covering all original artifacts, not just that file.

## Remaining authority and handoff

Product remains clean at rejected `9bb526170156a44cff90e2a2fab9eeab081e0eb1`, actual branch `feature/kc-pr-review-capability-protocol-pilot`; product counts **6,431 / 20 / 1,939** versus unchanged **6,600 / 20 / 1,800**. Entity frontmatter, status, rejected checkpoint and validation pin are untouched. Unrelated holder `e2e-pipeline/scripts/measure-prose-load.sh` and `scripts/deliver.sh` were preserved; state changes are confined to this task.

No new cloud/model cost occurred; historical SDK cost remains historical. The old workspace's archived state was **not reread or changed** because this assignment forbids live commands. Effective agent bridge/credential exclusion, real external deadline expiry, descendant termination, complete cloud proof and any product integration remain unverified. All original five repairs, focused reduction, F14 chronology and real quality/speed evidence remain pending. These local fixes are ready for FO inspection only; no cloud retest or stage advancement is authorized.
