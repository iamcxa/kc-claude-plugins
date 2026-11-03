---
title: A rewritten acceptance criterion is checked against the Captain's words
status: backlog
variant: kc-dev-flow-2
---

When FO or a worker rewrites an acceptance criterion, the rewrite is compared with the Captain's own words before dispatch, so a requirement he never stated does not reach validation.

Source: the Captain, chat 2026-11-03: 「ABC 都開，不屬於套件的本身也要討論一下」, answering 「決定：A、B、C 三個都開成 dev2 任務，跟 #768 一起發版嗎？要刪哪個直接說。」 He also said 「先不合併，我想要把這些也評估修復後，再一起發版」 about Release PR #768. FO had proposed it as: 「FO 改寫驗收條件後，要和你的原話比對」.

Gap: today the package checks that Scope and Captain amendments are unchanged, but no check reads a rewritten acceptance criterion against his words.

Bite: on this workflow's task for PR #756 (batch 11) FO rewrote 「附上來源」 as "the source's commit or link", which failed one validation round. The agent-observatory reports of 2026-11-03 (sampled, not yet checked by FO) show the relay and web FOs stating verdicts before reading the artifacts and using a worker count measured in another repository.

Consumer: every adopter FO at the ideation gate and the dispatch that follows it.
