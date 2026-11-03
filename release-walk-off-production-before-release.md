---
title: A release walk runs off production, and production waits for its acceptance
status: backlog
variant: kc-dev-flow-2
gates:
    version: 1
    records:
        - id: gate:release-walk-off-production-before-release:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:release-walk-off-production-before-release-backlog-1
              briefing:
                id: briefing:release-walk-off-production-before-release:backlog:attempt-1:revision-1
                digest: sha256:5105584c0647efba89f916911d52090abacd75cf43789548ff1f8845b5060017
                room-ref: ./release-walk-off-production-before-release/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-03T07:39:09.550832Z"
                reason: The Captain widened the batch 13 sitting to seven tasks (chat, 2026-11-03); the bound question named four.
---

## Scope
- Source: the Captain, chat 2026-11-03: 「可以，都沒有測試或預覽站的人在本機驗收也很好，kc-ship-flow 確實不用了。」, answering 「決定：把這件開成這批的第 4 個任務 D：『release 驗收在正式站以外的環境上走；正式版等驗收通過才發』，跟 A、B、C 一起做嗎？」. Earlier: 「…心態上，在每個slice/batch做完才發布正式版才比較合理」 and 「要注意不是每個人都用 netlify 一類的基礎建設，未必有一樣的部署組合」. Then 「好」, answering 「決定：把『幫 repo 記下自己的部署環境，沒有就問那四個問題』併進任務 D 一起構思，暫時不另開擴充，可以嗎？」; the four questions FO named: which environments exist, how a change reaches each, who approves production, how to roll back.
- Outcome: the release-acceptance walk runs on an environment that is not production (a preview or staging deploy, named by the repository), and the repository's production release waits until that walk is accepted. A repository with no preview or staging environment walks locally and records that limit. The repository's environments are recorded once; when they are absent, adoption asks the four questions.
- Gap, read on origin/main 2026-11-03 with git grep: the release-acceptance extension names its `Environment:` target by name only and says nothing about which environment or about the production release; dev2 tasks end at merge and never deploy.
- Bite: the qnow FO's agent-observatory report of 2026-11-03 (the qnow FO confirmed it against its own work the same day): missing icons on staging and production returned HTTP 200 with HTML and only the Captain noticed, after release. subspace-relay set its own order in AGENTS.md (#441, #447): Deploy Preview, then staging, then production, with a two-merge release.
- Consumer: every adopter that lists the release-acceptance extension.
- Upstream first: `extensions/release-acceptance/EXTENSION.md`, `references/sd/adoption.md`; sibling subspace-relay AGENTS.md and docs/releasing.md; gstack `setup-deploy` detects a production platform only and is not reused.

## Non-goals
- dev2 deploying anything; platform-specific steps; reviving kc-ship-flow; a new deployment extension.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## FO alignment
Alignment: needed before ideation; the scope is the Captain's ruling.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Stop condition
- A release-acceptance task whose environment is production is held, one naming a preview or staging target passes, a repository recording no such environment walks locally with the limit recorded, and the production-release step is reached only after an accepted walk.
