fix(kc-dev-flow-2): settle skipped runs when required checks pass

Delivery checks held qnow feature PRs when Release Gate was intentionally skipped. Read GitHub's required checks once per `check`, group duplicate names, and settle completed skipped workflow runs when the required list is non-empty and every required name has a pass entry.

Failed, pending, cancelled and neutral runs still hold. A required name with only skipped entries still holds, repositories reporting no required checks retain the skipped-run hold, and unreadable or malformed required-check responses hold with exit 2. This follows the approved design's one additional read-only `gh pr checks --required` call.

Validation on 2026-11-07 (Asia/Taipei):
- Five suites: 637 test cases, no failures, 6 existing skips; the delivery suite includes 170 cases.
- qnow #1338 fixture: exit 1 on base, exit 0 on candidate; failure, pending, required-only-skip and no-required-check rows still exit 1.
- Ten behavior mutations rejected by assertions; a changed workflow-text fixture is detected separately.
- Repository skill lint, ADR lint, number guards, comment ratio and design-surfaces checks pass. No workflow, skill, extension, version or CI trigger changes.
- Live read-only gh 2.103.0 contract: relay #477 reports no required checks; qnow #1338 returns duplicate required names with pass/skipping entries; qnow #1316 returns failed required checks as JSON.

CI cost per PR: not measured. RoboRev and hosted CI are not run by this worker; FO owns publication, local review and CI verification.
