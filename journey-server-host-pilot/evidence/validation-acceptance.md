# Four-step local acceptance

This checks the candidate's private local/emulated transport and recovery boundaries. A pass is **not deployment approval**, hosted Node/Cloudflare evidence, actual provider hibernation, billing proof or formal license acceptance. The full task-aware number guard remains unavailable/NOT PASS as separately reported.

Prerequisites: the absolute product checkout and state-task directory embedded in [validation-acceptance.sh](validation-acceptance.sh); candidate `4f678cd88eddbcc171df7e2037dd19d2fbf4065b`; Node >=22.13, Python 3, Git and RTK; packages already installed from `kc-journey-map/package-lock.json` with install scripts disabled, as described in `kc-journey-map/docs/private-host.md`; permission for temporary loopback listeners, workerd execution and read-only process inventory. No browser launch, production credential, cloud account, sign-in, provider provisioning or neighboring data is required. Dependency installation is a setup prerequisite, not part of the five-minute script.

Run this ordered block unchanged in one fresh shell:

```sh
rtk proxy bash '/Users/kent/Documents/Codex/2026-10-11/tldraw-tldraw-gpt-plugin/work/kc-jmap-host-pilot/docs/dev2/.spacedock-state/journey-server-host-pilot/evidence/validation-acceptance.sh'
```

The shell file contains these four exact steps in full, with all absolute paths set once. FO must display the full script and each actual output at the gate.

1. Confirm candidate and installed prerequisites. Expected: `PASS candidate 4f678cd88 clean; v...; locked runtime dependencies present`.
2. Run the Node probe. Expected: four readable PASS lines for isolation, recovery, revocation and expiry; LOCAL ONLY; a new synthetic evidence path.
3. Run the Cloudflare-local probe with the same client contract. Expected: the same four PASS lines, LOCAL ONLY and a new evidence path. The idle close control may take approximately 30 seconds.
4. Confirm unchanged product and stopped test processes. Expected: `PASS product unchanged; no validation server/emulator remains`, then the local-evidence limit.

Observed focused group durations: Node approximately 17 seconds; Cloudflare-local approximately 36 seconds, plus startup/preflight. Allow two minutes; each close-event wait is bounded at 35 seconds and setup at 10 seconds. Each adapter invocation also has a 110-second overall limit and stops its owned process group on timeout, keeping the two runs below four minutes plus short preflight/cleanup. The script creates only separate synthetic data and generated probe code under ignored `kc-journey-map/.host-check`; each runner closes its own processes. Existing implementation evidence and product bytes remain unchanged.
