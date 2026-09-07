
## Amendments from DEV-136/137 (2026-09-07)

- main now carries native migrations 0000–0009 (10). 0008 revokes and 0009 re-grants `qnow_app` SELECT on `qnow_staff_assignments` (PoC ruling; production scoped read = DEV-140). The preflight and every hosted manifest check expect 10; a staging database that already applied 0000–0007 will receive 0008 and 0009 on this deploy — say so in the run log.
- `deployOnce()` now throws `ACCEPTANCE_DEPLOY_LIMIT_EXCEEDED` on a second call within one session; the run is one deploy by construction, not by discipline. If the run needs a retry, it is a new session and the Captain says so.
- @netlify/open-api must resolve 2.57.0 (lock restored to the qualification branch's); `acceptance:hosted:self-check` refuses otherwise. Run it before the full run and quote the line.
- The full-run entrypoint comes from DEV-36 (#1174 rebased onto main); use the script name the merged package.json carries, and quote it.
- The verbose-deploy diagnostic redacts JSON-quoted secrets as of #1182; still treat its output as sensitive and keep it in the run receipt, not in chat.
