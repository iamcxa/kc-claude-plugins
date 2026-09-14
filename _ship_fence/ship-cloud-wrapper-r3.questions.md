# ship-cloud-wrapper-r3 — dispatch log, questions and answers

## 2026-09-14 dispatch (degraded)
Captain: 「派」 (assemble) then 「准」 (batch of five, pilot profile). Conductor SQL still 503 (re-probed at filing); dispatched with the scratch copy of dispatch.sh 0.2.0 whose sql probe line is a stderr note; watch is by hand (state branch + `session status` + `session message`). Follow-up sent to all five sessions: runtime check (kc-dev-flow >= 4.4.0, spacedock 0.27.2), pilot profile, degraded observability, gate decisions by the ship FO only, shared-file warning for the two tasks that edit `pins/conductor-cli.contract`, PR body shape.
Workspaces: see `ship-cloud-wrapper-r3.json` (five). Deferred, not in this batch: `pr-merge-extension-text-matches-spacedock-0-27`, `pr-merge-extension-separates-canonical-from-local-policy`, `direct-path-below-poc-admission-rule`.
