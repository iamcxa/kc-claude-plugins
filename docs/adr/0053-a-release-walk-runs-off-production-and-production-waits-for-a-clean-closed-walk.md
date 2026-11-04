# 0053. A release walk runs off production and production waits for a clean closed walk

Date: 2026-11-03

## Status

Accepted

## Context

ADR 0031 accepts a release through an operated walk. ADR 0034 closes an acceptance
task locally, including a walk with complaints, so closure alone cannot establish
production readiness. The prior check accepted a target named production, and
adopters have different deployment arrangements, including no deployed test site.
The task release-walk-off-production-before-release records the design and gates.

## Decision

**Words:** 「可以，都沒有測試或預覽站的人在本機驗收也很好，kc-ship-flow 確實不用了。」
— Captain, chat, 2026-11-03, answering 「決定：把這件開成這批的第 4 個任務 D：『release 驗收在正式站以外的環境上走；正式版等驗收通過才發』，跟 A、B、C 一起做嗎？」.

「好」 — Captain, chat, 2026-11-03, answering 「決定：把『幫 repo 記下自己的部署環境，沒有就問那四個問題』併進任務 D 一起構思，暫時不另開擴充，可以嗎？」.

「可以」 — Captain, chat, 2026-11-03, at the ideation gate, answering
「決定：七張設計照建議進實作，但驗收到期提醒的 D7 改成『在 kc-journey-map 登記 journey-progress/v1，預算放寬為兩個 PR，kc-journey-map 那個先合併』，可以嗎？」.
That approval accepts this task's three recommendations: production waits through
FO's word plus `ra accepted`; release instructions live in the document named by
`release-doc`, with `docs/releasing.md` created when absent; accepted means the
newest closed walk is clean.

**Options considered:**
- Record three adopter-owned README keys, refuse walks on production or another
  target, require a local deployment-limit entry, and let FO announce readiness
  after the newest archived walk has `local-merge:` and an `is_clean` report (chosen).
- Wire a refusal into each adopter's production pipeline, taking platform-specific
  release ownership outside this task's scope.
- Keep deployment answers in the workflow README body, adding README re-sync conflicts.
- Accept any closed walk, allowing unresolved work from a newer walk into production.

**Recommended:** The first option, with the repository's own release document and
a clean newest walk, as the Captain accepted at ideation.

**Protects:**
- `kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py` — `check_environment` refuses unsafe targets; `cmd_accepted` requires the newest walk to be archived, locally closed and clean.

README frontmatter records `walk-environment`, `production-environment` and
`release-doc`. Missing keys hold a walk and point to adoption's four questions:
which environments exist, how a change reaches each, who approves production and
how to roll back. A local walk records a `not_tested` entry starting `not deployed:`.
The `Prior walk:` chain determines the newest acceptance task; parallel unnamed
walks hold readiness. The report schema and workflow word budget do not change.

## Consequences

dev2 deploys nothing and cannot stop a pipeline or Captain releasing without FO.
The environment name is declared evidence, not verification of the running site;
the release document's contents are not checked by the command. An explicit
Captain override can authorize shipping with known complaints, but the script
still says not accepted. Revisit if an adopter needs mechanical production gating
or a real walk exposes a gap in the recorded environment or chain.
