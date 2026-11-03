---
title: A release walk runs off production, and production waits for its acceptance
status: backlog
variant: kc-dev-flow-2
---

The release-acceptance walk runs on an environment that is not production (a preview or staging deploy, named by the repository), and the repository's production release waits until that walk is accepted. A repository with no preview or staging environment walks locally and records that limit.

Source: the Captain, chat 2026-11-03: 「可以，都沒有測試或預覽站的人在本機驗收也很好，kc-ship-flow 確實不用了。」, answering 「決定：把這件開成這批的第 4 個任務 D：『release 驗收在正式站以外的環境上走；正式版等驗收通過才發』，跟 A、B、C 一起做嗎？」. Earlier the same day: 「…心態上，在每個slice/batch做完才發布正式版才比較合理」, and 「要注意不是每個人都用 netlify 一類的基礎建設，未必有一樣的部署組合」.

Gap, read on origin/main 2026-11-03 with git grep: the release-acceptance extension names its `Environment:` target by name only and says nothing about which environment or about the production release; dev2 tasks end at merge and never deploy.

Bite: the qnow FO's agent-observatory report of 2026-11-03 (sampled; the qnow FO confirmed it against its own work the same day): missing icons on staging and production returned HTTP 200 with HTML and only the Captain noticed, after release. subspace-relay set its own order in AGENTS.md (#441, #447): Deploy Preview, then staging, then production, with a two-merge release.

Consumer: every adopter that lists the release-acceptance extension, through the walk's environment line and the release that follows it.
