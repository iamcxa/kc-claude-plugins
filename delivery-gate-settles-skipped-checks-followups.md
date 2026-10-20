---
title: delivery-gate-settles-skipped-checks follow-ups accepted at the #680 delivery gate
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Residuals the engineering-reviewer named (reviews/engineering-reviewer-1.md in the archived task, 2026-10-20), accepted at the #680 delivery gate; build only when the trigger below is seen.

- Shape A: a fan-in job without `always()` is skipped together with the test job it needs while a sibling succeeds; ci_problem now settles it, and a carried merge (ADR 0023) can follow. Not reachable on relay or qnow PRs (their ci-gate is `always()` and checks skips both ways).
- Shape B on subspace-web: a Release Please PR whose `release-pair` or `resolve-release-relay` job is skipped by mistake passes beside a succeeded `review-gate` (web has no fan-in). Unverified whether a web release PR ever goes through a dev2 delivery ask.
- Fix sketched by the reviewer: an optional workflow README key naming the one check that must finish SUCCESS (relay's ci-gate header already calls it the only job the merge path should know). Trigger: an adopter without an `always()` fan-in, or a web release PR, reaching a delivery ask.

## Closed

Closed by the Captain 2026-10-20 (「照建議關掉 19 張。」) on FO's follow-up triage against origin/main ad44f0cb: #680 shipped; shapes A and B have no adopter on the trigger; the sketched README key stays a note in the archived engineering-reviewer report.
