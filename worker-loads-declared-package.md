---
title: Workers load the newest installed kc-dev-flow-2, not the version the workflow README declares
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:worker-loads-declared-package:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:worker-loads-declared-package-backlog-1
              briefing:
                id: briefing:worker-loads-declared-package:backlog:attempt-1:revision-1
                digest: sha256:846e2a9935ad5f8124c30d59e6aa5d33843c40eb0830901c017df4823325f90b
                room-ref: ./worker-loads-declared-package/review/backlog/briefing-1
---

Filed on the Captain's 「兩問題照這樣做」 (chat, 2026-10-17), to FO's question whether to file the subspace-relay FO's report as a kc-dev-flow-2 task.

## Scope

- Reported by the relay FO (dhaka-70, 2026-10-17), task `owner-link-sign-in-to-claim` (relay PR spacedock-dev/subspace-relay#381): relay's `docs/dev2/README.md` declares 0.22.1 and dispatch scope notes name `Package root: .../kc-dev-flow-2/0.22.1`, yet its cycle-2 and cycle-3 validators reported "the loaded skill is 0.23.0" and ran 0.23.0 scripts. Evidence on relay's spacedock-state/dev2: `_archive/owner-link-sign-in-to-claim/dispatch/validation-{1,2,3}.md` and the cycle-2/3 stage reports.
- Cause (FO, 2026-10-17): the Claude plugin install is per user, not per workflow. The Captain's machine moved to 0.23.0 on 2026-10-16 (`claude plugin update kc-dev-flow-2@kc-claude-plugins`), so every repository's workers load 0.23.0 whatever its README declares. `package_version.py` checks FO's own load only.
- Effect: 0.23.0's `delivery_gate.py` requires a `Candidate: <40-hex head>` line in the latest validation dispatch record; 0.22.1 records have none, so in-flight tasks in a 0.22.1 workflow hold at the merge ask. Relay's FO now adds the line by hand.
- Candidate routes for ideation: workers load the Package root the dispatch names (the skill already states one), a check that a worker's loaded version equals the README's, or upgrade notes plus a `dispatch_records.py` part that require the Candidate line before release; and whether FO's "sync later" for an adopter is meaningful at all while installs are per user.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it (his words are at the top of this file).
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
