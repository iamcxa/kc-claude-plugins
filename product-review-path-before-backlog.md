---
title: A product review path runs picky-user reviewers on different models and the design director rules what to solve, how and when, before backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:product-review-path-before-backlog:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:product-review-path-before-backlog-backlog-1
              briefing:
                id: briefing:product-review-path-before-backlog:backlog:attempt-1:revision-1
                digest: sha256:8f9d4c151bcc4e5601b416881458c8903d2b588f979ad9bc00fc9fb9ff839091
                room-ref: ./product-review-path-before-backlog/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:product-review-path-before-backlog:backlog:1
                briefing: briefing:product-review-path-before-backlog:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T07:14:50.021254Z"
                decision: hold
                reason: 'Captain 「並進去」 (chat, 2026-10-23), answering the bound question: folded into release-acceptance Captain Amendment 3; this task is closed without its own work.'
---

## Scope

- Source (relayed by the kc-paseo-plugins dev2 FO, Paseo agent 8b2c2fc2, 2026-10-23; the quote is relayed, not a ruling in this session): the Captain 「能不能在 dev2 的自駕路徑之前，多加入一個產品自我改善路徑，做法是由不同模型扮演挑剔的使用者，找出不滿意的地方，讓設計總監（dev2 新角色）來評估是否該解決，要怎麼解決，何時解決」 (2026-10-23). Intake copy: intake/method-notes-for-dev2.md; artifacts in kc-paseo-plugins state branch spacedock-state/dev2, ux-review-a5-polish/ (commit 0f0f552).
- What the hand run showed (peer's reading): two picky users (codex gpt-6-astra, experienced; antigravity gemini-3.8-flash-high, newcomer) on an isolated harness found the same top blocker independently; the director (Claude Opus, fresh context) found few new defect kinds and its value was owning and ranking items five earlier tasks had deferred to the Captain's UAT; a fixture with no field values cost one rerun; the two models disagreed on two items and the director took a side.
- Overlaps already in this workflow (upstream first, 2026-10-23): design-director-runs-ui-design-review (PR #708, the kc-dev-flow-2:design-director role at ideation and validation); release-acceptance Amendment 1 (an operated whole-screen pass over the release walk, run by the design director, with a works-but-unusable class, after the last story is built); gpt-partner-extension-proposal (GPT runs beside the special roles, held for later discussion); dev2-poc design-helper-astra-poc (closed without running). The proposal's trigger (a release's tasks all merged, before UAT) is release-acceptance's trigger.
- Questions the peer left open: whether reviewer personas and scenarios come from the journey map's stories; whether the director also owns the per-task ideation review.
- Non-goals: anything before the Captain admits this task at its backlog gate.

## FO alignment

Alignment: needed before ideation; whether this is a new path or folds into release-acceptance's walk and the design director is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
