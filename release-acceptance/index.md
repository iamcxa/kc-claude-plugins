---
title: Every release is walked end to end as a whole after its last story is built, and the pre-implementation release review is enforced at dispatch
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
---

Issue iamcxa/kc-claude-plugins#571: a release is reviewed as one journey before its tasks are split, but nothing enforces that review, and nothing walks a release as a whole after its stories are built.

## Scope

Captain 2026-10-09 (qnow session), asking where the release-scale acceptance he had discussed lives: 「我們有討論過一個改進是，每個 release 應該要在故事都完成後，立一張票做 release scale 的驗收，目的是發現單獨故事做完之後是否仍有不可用的狀況，例如沒想到的問題，或是功能做完但流程不能走，沒有進入點...諸如此類，目前這個在哪裡？」; then 「可以」 to filing #571 and running the acceptance by hand on R3; 「照這樣核准。此外release 整版驗收要加入成為 workflow 的標準機制，應該加到哪個套件？」 (2026-10-10); then 「現在開」 to the FO's recommendation: the mechanism's main body in kc-dev-flow-2 (when the task opens, who walks, what the report carries, how failures route back to release review) paired with a kc-journey-map mode that produces the walk list from the map and takes the result back, joined by a declared contract, not shared code.
Evidence (copied into this task's folder): r3-acceptance.md (RELEASE 3 walk, 2026-10-09: found the office 確認 action off-screen at common laptop widths, which no single task's validation saw) and r4-acceptance.md (RELEASE 4 walk, 2026-10-10: R4's proof line could not be performed on staging until the opt-in operator secret was found; found the owner tab-bar icon font served as HTML).
Non-goals: rewriting the existing review-release mode; adopter-specific environments.
Budget and stop condition: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Release: none (package workflow change; kc-claude-plugins has no journey map).
Release review: not needed: no release.
Needed at ideation: the design of both halves (the kc-dev-flow-2 rule and task, the kc-journey-map mode) and the contract between them, against the existing Release review rule in kc-dev-flow-2 references/sd/workflow.md and kc-journey-map's review-release mode.
Surfaces: none
Visible change: none
